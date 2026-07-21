"""Per-visitor session world — the hosting-blocker fix (WP-HOST-SESSION CORE).

The hosted demo used to serve EVERY visitor from one process-wide world: a single
``DemoState`` (memory db + ladder + audit chain), a single ``_PENDING`` approval map, a
single ``_TAMPER_BACKUP``, a single latency ring, and a single out-of-process sim db. Two
concurrent visitors trampled each other across all five axes.

This module gives every browser session its OWN world, keyed by an opaque HTTP-only cookie:

  * its OWN memory db — a private file copy of the committed-style COLD-OPEN snapshot, driven
    through a per-session ``DemoState`` (which already carries an RLock => single-writer/§2.9);
  * its OWN sim db — a private file copy of the sim snapshot, driven through an in-process
    ``sim`` FastAPI app (``sim.factory.make_sim_app``) wrapped in a TestClient and handed to
    ``SimTools(client=...)`` — no shared row, no shared ``flake_state``;
  * per-session ``pending`` (held approvals), ``tamper_backup`` (audit round-trip), and
    ``lat_ring`` (latency sparkline) — the other three globals folded onto the session object.

Lifecycle is fail-closed (Rule 3 / §2.3): a request whose cookie names an evicted / expired /
absent session gets a FRESH cold-open session with a NEW id — never another visitor's world and
never a resurrected pending approval. Eviction CLOSES both db connections and the sim TestClient
and DELETES every per-session file (no FD leak, no orphaned db).

RULE 1/2: no model id, no LLM decision anywhere here — this is deterministic session plumbing.
"""
from __future__ import annotations

import contextlib
import os
import secrets
import shutil
import sqlite3
import tempfile
import threading
import time
from collections import deque
from pathlib import Path

from fastapi.testclient import TestClient

from console.demo_state import DemoState
from precedent import venice
from precedent.tools import SimTools
from sim.factory import make_sim_app

# --------------------------------------------------------------------------- #
# Cookie + id
# --------------------------------------------------------------------------- #
COOKIE_NAME = "precedent_sid"
COOKIE_MAX_AGE = 60 * 60  # 1h — matches the eviction TTL ceiling

# Idle TTL: a session untouched for this long is evicted (fail-closed) on the next tick.
DEFAULT_TTL_SECONDS = int(os.environ.get("PRECEDENT_SESSION_TTL", "1800"))  # 30 min

# Hard ceiling on concurrent live sessions. Each session owns two sqlite connections + two db
# files, so unbounded CREATION (not just per-session request rate) is an FD/disk-exhaustion DoS
# vector. At capacity we evict the OLDEST-by-last_seen (LRU) BEFORE minting a new one, so the
# store never grows past this bound. Fail-closed: an over-cap mint sheds the stalest world first.
DEFAULT_MAX_SESSIONS = int(os.environ.get("PRECEDENT_MAX_SESSIONS", "256"))


def new_session_id() -> str:
    """Opaque, unguessable session id (URL-safe, ~256 bits)."""
    return secrets.token_urlsafe(32)


# --------------------------------------------------------------------------- #
# Hand-rolled token-bucket rate limiter (no new dependency — keeps the image slim/offline)
# --------------------------------------------------------------------------- #
# WHY hand-rolled: adding slowapi/limits would pull a dependency into an offline, airplane-mode
# image whose whole pitch is "no closed models, nothing phoning home". A monotonic-clock token
# bucket is ~15 lines, deterministic, and lets the rate-limit test shrink the bucket to force a
# 429 without patching wall-clock time. Over-limit => 429, which is a NON-action (fail-closed):
# the middleware short-circuits before any route/session mutation runs.

# Generous defaults so the guided tour (a burst of polls + drives) never trips; the rate-limit
# test narrows these via ``configure``. Read live from module globals so a test monkeypatch or
# ``configure`` call takes effect immediately.
_RATE_CAPACITY = float(os.environ.get("PRECEDENT_RATE_CAPACITY", "240"))
_RATE_REFILL_PER_S = float(os.environ.get("PRECEDENT_RATE_REFILL_PER_S", "120"))


def configure_rate_limit(capacity: float, refill_per_s: float) -> None:
    """Reset the token-bucket parameters (used by the rate-limit test; restore after)."""
    global _RATE_CAPACITY, _RATE_REFILL_PER_S
    _RATE_CAPACITY = float(capacity)
    _RATE_REFILL_PER_S = float(refill_per_s)


class TokenBucket:
    """A single monotonic-clock token bucket. ``allow()`` costs one token; empty => False.

    ``capacity_fn``/``refill_fn`` are read LIVE on every ``allow()`` so a test monkeypatch or a
    ``configure_*`` call takes effect immediately (default: the per-session request knobs)."""

    def __init__(self, capacity_fn=None, refill_fn=None) -> None:
        self._lock = threading.Lock()
        self._capacity_fn = capacity_fn or (lambda: _RATE_CAPACITY)
        self._refill_fn = refill_fn or (lambda: _RATE_REFILL_PER_S)
        self._tokens = self._capacity_fn()
        self._last = time.monotonic()

    def allow(self, cost: float = 1.0) -> bool:
        with self._lock:
            cap = self._capacity_fn()
            now = time.monotonic()
            # Refill using the CURRENT (possibly reconfigured) rate, capped at capacity.
            self._tokens = min(cap, self._tokens + (now - self._last) * self._refill_fn())
            self._last = now
            if self._tokens >= cost:
                self._tokens -= cost
                return True
            return False

    def reset(self) -> None:
        with self._lock:
            self._tokens = self._capacity_fn()
            self._last = time.monotonic()


# --------------------------------------------------------------------------- #
# Session-CREATION rate limit (finding 1 — the cookieless fail-open)
# --------------------------------------------------------------------------- #
# The per-session request bucket above only bites a caller that PERSISTS its precedent_sid cookie.
# A caller that drops the cookie mints a FRESH session — and a FRESH full request bucket — on EVERY
# request, bypassing the per-session limit and flooding session/world CREATION (each mint copies two
# sqlite dbs + opens two connections => an FD/disk-exhaustion DoS the MAX_SESSIONS LRU cap only
# bounds the STEADY-STATE of, never the churn rate). So creation itself is rate-limited BEFORE a new
# session is minted, keyed by CLIENT (request.client.host). Over-limit ⇒ 429, NO session minted
# (fail-closed / non-action). Keyed PER-CLIENT (not one global bucket) so a single abuser's flood is
# throttled WITHOUT one shared bucket coupling — and falsely throttling — distinct legitimate
# visitors. The MAX_SESSIONS LRU cap stays as the disk/FD backstop for a distributed multi-IP spray.
# Defaults are generous (mirroring the per-session request bucket) so a real visitor — who mints
# exactly ONE session and then rides its cookie — and the whole test suite never trip it; only a
# deliberate cookieless flood from a single client does. The barrier test shrinks these to force it.
_CREATION_CAPACITY = float(os.environ.get("PRECEDENT_CREATE_CAPACITY", "240"))
_CREATION_REFILL_PER_S = float(os.environ.get("PRECEDENT_CREATE_REFILL_PER_S", "120"))
# Bound the per-client bucket MAP itself so a spray of distinct client keys can't grow it without
# limit (a second-order DoS). Oldest-touched keys are dropped (they refill to full when re-seen).
_CREATION_BUCKETS_MAX = 4096

_CREATION_LOCK = threading.Lock()
_CREATION_BUCKETS: dict[str, TokenBucket] = {}


def _creation_capacity() -> float:
    return _CREATION_CAPACITY


def _creation_refill() -> float:
    return _CREATION_REFILL_PER_S


def configure_creation_limit(capacity: float, refill_per_s: float) -> None:
    """Reset the session-CREATION token-bucket parameters (used by the barrier test; restore
    after). Read live by every creation bucket, so this takes effect immediately."""
    global _CREATION_CAPACITY, _CREATION_REFILL_PER_S
    _CREATION_CAPACITY = float(capacity)
    _CREATION_REFILL_PER_S = float(refill_per_s)


def reset_creation_state() -> None:
    """Forget every per-client creation bucket — so a test starts from a clean creation-rate state
    (no drained/over-sized bucket leaking across tests)."""
    with _CREATION_LOCK:
        _CREATION_BUCKETS.clear()


def allow_session_creation(client_key: str | None) -> bool:
    """True iff a NEW session may be minted for this client right now. Fail-closed: over the
    per-client creation rate ⇒ False (the caller must NOT mint, and returns 429)."""
    key = client_key or "-"
    with _CREATION_LOCK:
        bucket = _CREATION_BUCKETS.get(key)
        if bucket is None:
            if len(_CREATION_BUCKETS) >= _CREATION_BUCKETS_MAX:
                # Drop an arbitrary existing key (it refills to full if the client returns) so the
                # map can never grow past its bound — the map itself is not a memory DoS vector.
                _CREATION_BUCKETS.pop(next(iter(_CREATION_BUCKETS)), None)
            bucket = TokenBucket(_creation_capacity, _creation_refill)
            _CREATION_BUCKETS[key] = bucket
    return bucket.allow()


# --------------------------------------------------------------------------- #
# Cold-open snapshot — seed ONCE, then COPY the file per session (fast).
# --------------------------------------------------------------------------- #
# The snapshot is the "committed cold-open" both dbs derive from. Rather than re-seed from
# scratch on every request (~seconds for the sim load), we build each template db ONCE
# (memoised, process-wide) and ``shutil.copyfile`` it per session (milliseconds). A checked-in
# template under data/cold-open/ is honoured if present; otherwise it is generated at first use
# so a bare checkout / CI still works offline.
_TEMPLATE_LOCK = threading.RLock()
_MEM_TEMPLATE: str | None = None
_SIM_TEMPLATE: str | None = None

_COMMITTED_DIR = Path(__file__).resolve().parent.parent / "data" / "cold-open"


def _template_dir() -> Path:
    d = Path(tempfile.gettempdir()) / "precedent-cold-open"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _rm_db(path: str) -> None:
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(path + suffix)
        except OSError:
            pass


def _copy_sqlite_db(src: str, dst: str) -> None:
    """Copy a sqlite db to ``dst`` as a COMPLETE, self-contained snapshot — hermetically.

    Plain ``shutil.copyfile`` copies only the named main file; if the source has a live ``-wal``
    sidecar with committed-but-un-checkpointed frames (WAL journal mode), the copy is TORN — it
    silently drops those rows and can even fail an integrity check. That non-hermetic copy is the
    root of the intermittent gate/sim RED (a copy racing a partially-written template).

    The sqlite online backup API reads a CONSISTENT image THROUGH the SQLite engine, so any
    committed WAL frames are included and a fresh, single-file db is produced regardless of the
    source's journal mode or sidecar state. Any stale sidecars at ``dst`` are removed first.
    """
    _rm_db(dst)
    src_conn = sqlite3.connect(src)
    try:
        dst_conn = sqlite3.connect(dst)
        try:
            src_conn.backup(dst_conn)  # consistent snapshot incl. any committed WAL frames
        finally:
            dst_conn.close()
    finally:
        src_conn.close()


def memory_template() -> str:
    """Path to the cold-open MEMORY db template (records + ACLs + principals + ladder). WP-DEMO §b:
    the graduation (scheduler) class opens at L2 / streak 0 — NOT STANDING. The boot-time
    force=True STANDING pre-seed is RETIRED; the visitor earns Standing live through the real
    ladder, so the zero-LLM fast path fires only AFTER their own promotion. Built once, then copied.
    """
    global _MEM_TEMPLATE
    with _TEMPLATE_LOCK:
        if _MEM_TEMPLATE and os.path.exists(_MEM_TEMPLATE):
            return _MEM_TEMPLATE
        committed = _COMMITTED_DIR / "memory.db"
        if committed.exists():
            _MEM_TEMPLATE = str(committed)
            return _MEM_TEMPLATE

        path = str(_template_dir() / "memory.db")
        _rm_db(path)
        # __init__ -> reset -> _seed seeds records/ACLs/principals, all classes at L1, and the
        # graduation class at L2/streak-0 (console/demo_state._seed). No force-promote here.
        st = DemoState(db_path=path)
        st.conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")  # fold the WAL into the main file
        st.conn.commit()
        st.conn.close()
        # Drop the now-empty WAL/SHM sidecars so a session copies ONE complete file.
        for suffix in ("-wal", "-shm"):
            try:
                os.remove(path + suffix)
            except OSError:
                pass
        _MEM_TEMPLATE = path
        return path


def sim_template() -> str:
    """Path to the cold-open SIM db template (MediaCo loaded + the 3 incidents in their broken
    pre-states + flake_state armed=0). Built once, then copied."""
    global _SIM_TEMPLATE
    with _TEMPLATE_LOCK:
        if _SIM_TEMPLATE and os.path.exists(_SIM_TEMPLATE):
            return _SIM_TEMPLATE
        committed = _COMMITTED_DIR / "sim.db"
        if committed.exists():
            _SIM_TEMPLATE = str(committed)
            return _SIM_TEMPLATE
        from sim import core
        from sim import db as simdb

        path = str(_template_dir() / "sim.db")
        _rm_db(path)
        conn = simdb.connect(path)
        try:
            core.reset(conn)  # DROP+rebuild from committed data/raw + data/kb, seed incidents
            conn.commit()
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")  # fold any WAL into the main file
            conn.commit()
        finally:
            conn.close()
        # Drop any WAL/SHM sidecars so every session copies ONE complete file (hermetic — mirrors
        # memory_template). Belt-and-braces with _copy_sqlite_db, which is torn-copy-safe anyway.
        for suffix in ("-wal", "-shm"):
            try:
                os.remove(path + suffix)
            except OSError:
                pass
        _SIM_TEMPLATE = path
        return path


# --------------------------------------------------------------------------- #
# Cookieless health snapshot — computed ONCE from the cold-open template, cached process-wide.
# --------------------------------------------------------------------------- #
# /health (and any other cookie-less infra probe) needs a status payload but NOT a private
# world. Minting a session per health poll would churn a throwaway memory+sim world on every
# always-on liveness check (FD/disk pressure). Instead we derive the status once from the memory
# template — the cold-open is immutable, so a cached snapshot is correct — and create NO session,
# NO cookie, NO store entry.
_HEALTH_LOCK = threading.Lock()
_HEALTH_CACHE: dict | None = None


def template_status() -> dict:
    """Cold-open ``{"status": {...}, "precedents_count": int}`` for cookieless infra probes.
    Built ONCE from a throwaway copy of the memory template (then closed + deleted) and cached
    process-wide — so /health mints no session, sets no cookie, and adds no store entry."""
    global _HEALTH_CACHE
    with _HEALTH_LOCK:
        if _HEALTH_CACHE is not None:
            return _HEALTH_CACHE
        tmp = Path(tempfile.mkdtemp(prefix="precedent-health-"))
        path = str(tmp / "memory.db")
        try:
            shutil.copyfile(memory_template(), path)
            st = DemoState(db_path=path)
            try:
                snap = st.snapshot()
                _HEALTH_CACHE = {
                    "status": dict(snap["status"]),
                    "precedents_count": snap["precedents_count"],
                }
            finally:
                with st._lock:
                    st.conn.close()
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        return _HEALTH_CACHE


# --------------------------------------------------------------------------- #
# Session
# --------------------------------------------------------------------------- #
class Session:
    """One visitor's private world: memory db + sim db + the three folded-in scratch stores."""

    def __init__(self, sid: str, root: Path) -> None:
        self.sid = sid
        self.dir = root / sid
        self.dir.mkdir(parents=True, exist_ok=True)
        self.mem_path = str(self.dir / "memory.db")
        self.sim_path = str(self.dir / "sim.db")

        # Memory world: copy the cold-open template, then open a per-session DemoState on it.
        shutil.copyfile(memory_template(), self.mem_path)
        self.state = DemoState(db_path=self.mem_path)

        # The three other globals, folded onto the session (keyed by session, not row/inc id).
        self.pending: dict[str, object] = {}          # was scripts.demo_server._PENDING
        self.tamper_backup: dict[int, str] = {}        # was console.app._TAMPER_BACKUP
        self.lat_ring: deque[int] = deque(maxlen=200)  # was console.showcase._LAT_RING
        # Per-session model-call tally (was the process-global _MODEL_CALLS in precedent.venice).
        # The _session resolvers bind this per request so a model call increments THIS visitor's
        # counter — the §2.6 "model calls THIS session" attestation is now truthful, not a global.
        self.model_counter = venice.new_call_counter()

        # Sim world is built LAZILY (only /api/drive* needs it) so read-only visitors and the
        # DOM/palette tests never pay the sim-load cost.
        self._sim_app = None
        self._sim_client: TestClient | None = None
        self._sim_lock = threading.Lock()

        self.bucket = TokenBucket()
        self.created_at = time.monotonic()
        self.last_seen = self.created_at

    # -- sim (lazy) --------------------------------------------------------- #
    def sim_client(self) -> TestClient:
        with self._sim_lock:
            if self._sim_client is None:
                _copy_sqlite_db(sim_template(), self.sim_path)  # hermetic — never a torn copy
                self._sim_app = make_sim_app(self.sim_path)
                self._sim_client = TestClient(self._sim_app)
            return self._sim_client

    def sim_tools(self) -> SimTools:
        """A SimTools bound to THIS session's in-process sim (no base_url, no HTTP)."""
        return SimTools(client=self.sim_client())

    def reset_sim(self) -> None:
        """Drop this session's sim world so the next drive rebuilds it from the cold-open
        template (broken incidents, flake disarmed). Closes the TestClient first — no FD leak."""
        with self._sim_lock:
            if self._sim_client is not None:
                try:
                    self._sim_client.close()
                except Exception:  # noqa: BLE001
                    pass
                self._sim_client = None
                self._sim_app = None
            _rm_db(self.sim_path)  # next sim_client() re-copies sim_template()

    def reset_world(self) -> dict:
        """Full per-session cold-open restart: re-seed the memory db, clear the three scratch
        stores, and reset the sim to its broken pre-state. Returns the fresh snapshot."""
        snap = self.state.reset()
        self.pending.clear()
        self.tamper_backup.clear()
        self.lat_ring.clear()
        self.model_counter.reset()   # a fresh cold-open starts THIS session's tally back at 0
        # Finding 4: the gate pending-decision refs (and the standing exactly-once ledger) are
        # stashed on the DemoState (gate/world.gate_world_from_session). reset() swaps in a fresh
        # conn but leaves those, so a ref proposed before the cold-open restart would SURVIVE and
        # stay executable. Drop them here so a pre-reset ref becomes a non-action (fail-closed).
        self.state.__dict__.pop("_gate_refs", None)
        self.state.__dict__.pop("_gate_executed", None)
        self.reset_sim()
        return snap

    # -- lifecycle ---------------------------------------------------------- #
    def touch(self, now: float | None = None) -> None:
        self.last_seen = time.monotonic() if now is None else now

    def is_expired(self, ttl: float, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        return (now - self.last_seen) > ttl

    def close(self) -> None:
        """Close the memory sqlite connection, then the per-session sim TestClient, then DELETE
        every per-session file. Fail-closed and idempotent: each resource is torn down in its OWN
        guarded step so one failure never leaves a later resource (or an FD) silently live."""
        # 1) Memory sqlite connection — its OWN step. Acquire the world lock (bounded) BEFORE
        #    closing the conn, and close ONLY when we hold it. Finding 5: if an in-flight op (a
        #    gate outcome) still holds the lock after the bounded wait, we must NOT yank the conn
        #    out from under it — that mid-op close is the crash. So a still-held lock ⇒ we leave the
        #    conn live (the op finishes coherently; the already-unlinked file GCs with its fd). The
        #    LRU cap-eviction additionally SKIPS in-flight sessions, so this timeout is the rare
        #    belt-and-braces path. Catch only the sqlite error a close is expected to raise.
        lock = getattr(self.state, "_lock", None)
        got_lock = True if lock is None else lock.acquire(timeout=1.0)
        try:
            if got_lock:
                try:
                    self.state.conn.close()  # idempotent; the reliably-closed FD
                except sqlite3.Error:  # narrow: the only error a sqlite close is expected to raise
                    pass
        finally:
            if got_lock and lock is not None:
                lock.release()
        # 2) Sim TestClient / app — its OWN guarded step.
        with self._sim_lock:
            if self._sim_client is not None:
                try:
                    self._sim_client.close()
                except Exception:  # noqa: BLE001 — a sim-close hiccup must not orphan the files
                    pass
                self._sim_client = None
                self._sim_app = None
        # 3) Per-session files.
        shutil.rmtree(self.dir, ignore_errors=True)


# --------------------------------------------------------------------------- #
# Store
# --------------------------------------------------------------------------- #
class SessionStore:
    """Registry of live sessions keyed by opaque id, with fail-closed TTL eviction."""

    def __init__(self, ttl_seconds: int = DEFAULT_TTL_SECONDS,
                 max_sessions: int = DEFAULT_MAX_SESSIONS) -> None:
        self._lock = threading.RLock()
        self._sessions: dict[str, Session] = {}
        self.ttl = ttl_seconds
        self.max_sessions = max(1, int(max_sessions))
        self.root = Path(tempfile.mkdtemp(prefix="precedent-sessions-"))

    # -- resolution --------------------------------------------------------- #
    def resolve(self, sid: str | None) -> Session:
        """Return the live session for ``sid``, or a FRESH cold-open session (new id) when the
        cookie is absent / unknown / expired. Never returns another visitor's world."""
        with self._lock:
            now = time.monotonic()
            if sid is not None:
                sess = self._sessions.get(sid)
                if sess is not None:
                    if sess.is_expired(self.ttl, now):
                        self._evict_locked(sid)  # expired => non-action; fall through to fresh
                    else:
                        sess.touch(now)
                        return sess
            # Cap CREATION: shed the stalest world(s) BEFORE minting so the store never grows
            # past max_sessions (FD/disk exhaustion guard). Fail-closed — LRU by last_seen.
            while len(self._sessions) >= self.max_sessions:
                if not self._evict_oldest_locked():
                    break
            new_sid = new_session_id()
            sess = Session(new_sid, self.root)
            sess.touch(now)
            self._sessions[new_sid] = sess
            return sess

    def get(self, sid: str) -> Session | None:
        with self._lock:
            return self._sessions.get(sid)

    def has_live(self, sid: str | None, now: float | None = None) -> bool:
        """True iff ``sid`` names a live, non-expired session — i.e. a request on this cookie would
        REUSE a world rather than MINT one. The creation-rate gate uses this to charge only the
        cookieless / new-session path, never a well-behaved cookie-persisting visitor."""
        if not sid:
            return False
        now = time.monotonic() if now is None else now
        with self._lock:
            sess = self._sessions.get(sid)
            return sess is not None and not sess.is_expired(self.ttl, now)

    def __len__(self) -> int:
        with self._lock:
            return len(self._sessions)

    # -- eviction ----------------------------------------------------------- #
    def _evict_locked(self, sid: str) -> bool:
        sess = self._sessions.pop(sid, None)
        if sess is None:
            return False
        sess.close()
        return True

    @staticmethod
    def _lock_is_free(sess: Session) -> bool:
        """True iff ``sess``'s world lock is NOT currently held by another thread. Non-blocking:
        a successful trylock is released immediately. Used to keep cap-eviction off an in-flight
        session (finding 5)."""
        lock = getattr(sess.state, "_lock", None)
        if lock is None:
            return True
        if lock.acquire(blocking=False):
            lock.release()
            return True
        return False

    def _evict_oldest_locked(self) -> bool:
        """Evict the stalest (oldest ``last_seen``) session whose world lock is NOT currently held.
        Returns False when empty OR when every live session is in-flight. Caller MUST hold
        ``self._lock``. Used by the MAX_SESSIONS creation cap.

        Finding 5: force-closing a session whose lock a gate outcome is holding would yank its conn
        mid-op (closed-conn crash). So an in-flight session is SKIPPED — we shed the next-stalest
        idle world instead. If ALL live sessions are busy, we decline to evict (a brief, bounded
        cap overflow, capped by concurrency) rather than evict an in-flight world."""
        for sid in sorted(self._sessions, key=lambda s: self._sessions[s].last_seen):
            if self._lock_is_free(self._sessions[sid]):
                return self._evict_locked(sid)
        return False

    def evict(self, sid: str) -> bool:
        with self._lock:
            return self._evict_locked(sid)

    def evict_expired(self, now: float | None = None) -> list[str]:
        """Evict every session past its TTL. Returns the evicted ids. Called by the single
        background tick (and directly by the eviction test)."""
        now = time.monotonic() if now is None else now
        with self._lock:
            stale = [sid for sid, s in self._sessions.items() if s.is_expired(self.ttl, now)]
            for sid in stale:
                self._evict_locked(sid)
            return stale

    def live_sessions(self) -> list[Session]:
        """A snapshot list of live sessions (so the tick can iterate without holding the lock)."""
        with self._lock:
            return list(self._sessions.values())

    def close_all(self) -> None:
        with self._lock:
            for sid in list(self._sessions):
                self._evict_locked(sid)
        shutil.rmtree(self.root, ignore_errors=True)


# Process-wide registry the served app uses. In pinned/legacy test mode (module STATE set) the
# routes never touch this — see console.app / scripts.demo_server ``_session`` helpers.
SESSIONS = SessionStore()


def session_from_request(request) -> Session:
    """Resolve the Session for a request. The middleware stashes it on ``request.state.session``;
    for direct calls (no middleware ran) or a bare cookie, fall back to the store. Never returns
    another visitor's world (fail-closed inside ``SessionStore.resolve``)."""
    if request is not None:
        existing = getattr(getattr(request, "state", None), "session", None)
        if existing is not None:
            return existing
    sid = None
    if request is not None:
        with contextlib.suppress(Exception):
            sid = request.cookies.get(COOKIE_NAME)
    return SESSIONS.resolve(sid)


# --------------------------------------------------------------------------- #
# One background tick over live sessions (NOT one asyncio task per session)
# --------------------------------------------------------------------------- #
def tick_session(session: Session) -> None:
    """One ACL re-sync / freshness heartbeat for a single session, under THAT session's lock
    (§2.9 single-writer-per-session). Mirrors the old process-wide ``_sync_tick`` but scoped."""
    from precedent_memory import sync as syncmod

    state = session.state
    with state._lock:
        if syncmod.live_source_configured():
            syncmod.sync(state.source, conn=state.conn)
        else:
            syncmod.refresh_cached_freshness(state.conn)  # airplane heartbeat
        state.conn.commit()


def registry_tick(store: SessionStore | None = None) -> None:
    """Evict expired sessions, then tick each survivor once. This is the body the single
    lifespan-owned async task runs on an interval — one task for ALL sessions."""
    store = store or SESSIONS
    store.evict_expired()
    for session in store.live_sessions():
        try:
            tick_session(session)
        except Exception:  # noqa: BLE001 — a per-session hiccup must not kill the loop
            pass
