"""WP-HOST-SESSION — the AUTHORITATIVE per-session isolation gate (pure-Python TestClient).

The hosted demo serves many concurrent visitors from ONE process. This suite proves that two
concurrent sessions (two TestClients => two distinct session cookies) never touch each other's
world across ALL FIVE shared-state axes that used to be process-wide globals:

  1. STATE            — per-session memory db (ladder + audit chain)
  2. _PENDING         — per-session held-approval map
  3. _TAMPER_BACKUP   — per-session audit tamper/restore round-trip
  4. _LAT_RING        — per-session latency ring (view-only)
  5. the SIM world    — per-session sim db copy driven through an in-process TestClient

Docker/Playwright are unavailable in this environment (CLAUDE.md INFRA REALITY), so a
TestClient with two distinct session cookies IS the isolation gate. These run in PRODUCTION
(non-pinned) mode — ``console.app.STATE`` / ``demo_server.STATE`` are None — so every request
resolves its own per-cookie session, exactly as a browser visitor would.
"""
from __future__ import annotations

import os
import sqlite3

import pytest
from fastapi.testclient import TestClient

from console import session as sessionmod
from precedent import venice

PUBLISHER_CLASS = "publisher|PUB-4012|schedule_item"   # INC-1's class (cold-open L1 => slow-path)


@pytest.fixture(autouse=True)
def _airplane(monkeypatch):
    """Airplane mode: never let the slow-path rationale reach a real model (keeps model calls 0
    and the drive deterministic). The fast-path already makes zero model calls."""
    monkeypatch.setenv("PRECEDENT_AGENTS_OFFLINE", "1")
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    venice.reset_model_calls()
    yield


@pytest.fixture(autouse=True)
def _restore_rate_limit():
    """Snapshot + restore the token-bucket knobs so a rate-limit test can never leak a shrunk
    bucket into a sibling test (which would spuriously 429 it)."""
    cap, refill = sessionmod._RATE_CAPACITY, sessionmod._RATE_REFILL_PER_S
    yield
    sessionmod.configure_rate_limit(cap, refill)


@pytest.fixture
def app_mod():
    """The served demo app: console.app extended by scripts.demo_server, in PRODUCTION wiring
    (no pinned STATE) so every request resolves its own per-cookie session."""
    import console.app as capp
    import scripts.demo_server as ds
    assert capp.STATE is None and ds.STATE is None, "these tests exercise the per-cookie path"
    return ds


def _client(app_mod) -> TestClient:
    c = TestClient(app_mod.app)   # no `with` => no background loop; sessions build lazily
    c.get("/")                    # establish a session cookie
    return c


def _sid(client: TestClient) -> str:
    return client.cookies.get(sessionmod.COOKIE_NAME)


def _inc(state_json: dict, incident_id: str) -> dict:
    return next(i for i in state_json["incidents"] if i["incident_id"] == incident_id)


def _slot_healthy(session, n: int) -> bool:
    """Read incident n's target slot health straight from THIS session's in-process sim."""
    oid = session.sim_client().get(f"/sim/incident/{n}").json()["structured"]["object_id"]
    return session.sim_client().get(
        f"/sim/object/publisher/schedule_item/{oid}").json()["healthy"]


# --------------------------------------------------------------------------- #
# 1) Two concurrent sessions are isolated across BOTH dbs (memory + sim explicit)
# --------------------------------------------------------------------------- #
def test_two_sessions_isolated_across_both_dbs(app_mod):
    A, B = _client(app_mod), _client(app_mod)
    sidA, sidB = _sid(A), _sid(B)
    assert sidA and sidB and sidA != sidB

    sessA = sessionmod.SESSIONS.get(sidA)
    sessB = sessionmod.SESSIONS.get(sidB)

    # B's cold open is broken for INC-1 (asserted explicitly BEFORE A touches anything).
    assert _slot_healthy(sessB, 1) is False

    # A drives the tour: Reset, audit-tamper, promote INC-1's class, EPG-repair (execute-in-sim).
    A.post("/api/demo/reset")
    A.post("/api/audit/tamper")                                   # breaks A's audit chain
    A.post("/api/promote", json={"class_key": PUBLISHER_CLASS})   # INC-1 -> STANDING (A only)
    d = A.post("/api/drive/1").json()                             # fast-path repair runs in A's sim
    assert d["verified"] is True and d["outcome"] == "resolved"

    sa, sb = A.get("/api/state").json(), B.get("/api/state").json()

    # ---- MEMORY axis: ladder + audit chain + close count are all A-only ----
    assert _inc(sa, "INC-1")["ladder_level"] == "STANDING"
    assert _inc(sb, "INC-1")["ladder_level"] == "L1", "A's promote must NOT leak to B"
    assert sa["status"]["audit_chain"] == "BROKEN"
    assert sb["status"]["audit_chain"] == "intact", "A's tamper must NOT leak to B"
    assert sa["closed_count"] == 1 and sb["closed_count"] == 0

    # ---- SIM axis (explicit): A's republish_epg fixed A's slot; B's identical slot stays broken.
    assert _slot_healthy(sessA, 1) is True, "A repaired its OWN EPG slot"
    assert _slot_healthy(sessB, 1) is False, "B's cold open stays broken — no sim bleed"

    # B's world was never consumed: B can still drive INC-1 for itself.
    assert B.post("/api/drive/1").json()["verified"] is True
    assert A.get("/api/model-calls").json()["model_calls"] == 0   # airplane path stays at 0


# --------------------------------------------------------------------------- #
# 1b) resolve()'s INLINE TTL-expiry branch is fail-closed (the mutation-surviving gap):
#     an expired cookie is evicted INSIDE resolve() — not only by the background evict_expired()
#     tick — so a request on a stale cookie can never touch its own resurrected world.
# --------------------------------------------------------------------------- #
def test_resolve_inline_expiry_evicts_stale_session(app_mod):
    """Drive resolve()'s inline expiry branch DIRECTLY (no evict_expired() call): register a
    session with a held approval + materialised sim, age it past the TTL, then resolve() its id.
    A fresh cold-open session (new id) must come back, the old pending approval GONE (§2.3
    expired => non-action), and the old memory + sim db files DELETED with the conn closed."""
    store = sessionmod.SessionStore(ttl_seconds=1800)
    try:
        sess = store.resolve(None)                 # fresh session, stored
        sid = sess.sid
        sess.pending["INC-1"] = object()           # a held approval on the stale world
        sess.sim_client()                          # materialise the sim db file
        mem_conn, mem_path, sim_path = sess.state.conn, sess.mem_path, sess.sim_path
        assert os.path.exists(mem_path) and os.path.exists(sim_path)

        # Age it past the TTL WITHOUT calling evict_expired() — the inline branch is the SUT.
        sess.last_seen -= store.ttl + 1

        fresh = store.resolve(sid)
        assert fresh.sid != sid, "inline expiry must hand back a FRESH session, not the stale one"
        assert fresh.pending == {}, "the stale held approval must never be resurrected (§2.3)"
        assert store.get(sid) is None, "the expired session is evicted from the store"
        # conn closed (no FD leak) + both files deleted (no orphan db)
        with pytest.raises(sqlite3.ProgrammingError):
            mem_conn.execute("SELECT 1")
        assert not os.path.exists(mem_path) and not os.path.exists(sim_path)
    finally:
        store.close_all()


# --------------------------------------------------------------------------- #
# 2) TTL eviction is fail-closed: closes both connections, deletes both files, forgets pending
# --------------------------------------------------------------------------- #
def test_eviction_closes_conns_deletes_files_and_forgets_pending(app_mod, monkeypatch):
    A = _client(app_mod)
    sidA = _sid(A)

    # Materialise a full world: a HELD approval (pending) + the sim + files on disk.
    assert A.post("/api/drive/1?hold=true").json()["status"] == "pending_approval"
    assert len(A.get("/api/gate/pending").json()["pending"]) == 1
    sess = sessionmod.SESSIONS.get(sidA)
    sess.sim_client()                                            # force the sim to materialise
    mem_conn, mem_path, sim_path = sess.state.conn, sess.mem_path, sess.sim_path
    assert os.path.exists(mem_path) and os.path.exists(sim_path)

    # Force TTL eviction (everything past its TTL).
    monkeypatch.setattr(sessionmod.SESSIONS, "ttl", -1)
    evicted = sessionmod.SESSIONS.evict_expired()
    assert sidA in evicted

    # Memory connection CLOSED — finding 4: close() reliably closes the sqlite handle in its own
    # guarded step, so there is NO usable handle after eviction (no FD leak).
    with pytest.raises(sqlite3.ProgrammingError):
        mem_conn.execute("SELECT 1")
    # close() is idempotent: a second close (e.g. lifespan close_all after an evict) must not
    # raise and must leave the handle just as closed.
    sess.close()
    with pytest.raises(sqlite3.ProgrammingError):
        mem_conn.execute("SELECT 1")
    assert sess._sim_client is None
    # ... files DELETED (no orphans) ...
    assert not os.path.exists(mem_path) and not os.path.exists(sim_path)
    assert sessionmod.SESSIONS.get(sidA) is None

    # A subsequent request on the SAME cookie gets a FRESH cold-open session (new id), and the
    # evicted session's pending approval is GONE — never resurrected (§2.3 expired => non-action).
    monkeypatch.setattr(sessionmod.SESSIONS, "ttl", sessionmod.DEFAULT_TTL_SECONDS)
    assert A.get("/api/gate/pending").json()["pending"] == []
    assert _sid(A) != sidA
    fresh = A.get("/api/state").json()
    assert fresh["closed_count"] == 0 and _inc(fresh, "INC-1")["ladder_level"] == "L1"


# --------------------------------------------------------------------------- #
# 2b) Unbounded session CREATION is capped (FD/disk exhaustion): a global MAX_SESSIONS ceiling
#     evicts the OLDEST-by-last_seen (LRU) BEFORE minting a new one, so the store never grows
#     without bound and every evicted session's files are deleted.
# --------------------------------------------------------------------------- #
def test_session_creation_is_capped_and_evicts_oldest(app_mod):
    cap = 8
    store = sessionmod.SessionStore(ttl_seconds=1800, max_sessions=cap)
    try:
        created = []
        for _ in range(cap + 5):                    # MAX + K creations
            sess = store.resolve(None)              # each mint may force an LRU eviction
            created.append(sess)

        assert len(store) <= cap, "the store must never exceed MAX_SESSIONS"
        # The oldest K+ (first-created, lowest last_seen) were evicted: gone from store + on disk.
        for old in created[:5]:
            assert store.get(old.sid) is None, "oldest sessions evicted at capacity"
            assert not old.dir.exists(), "an evicted session's dir is deleted (no disk leak)"
        # The most-recent `cap` survive.
        for recent in created[-cap:]:
            assert store.get(recent.sid) is not None
    finally:
        store.close_all()


# --------------------------------------------------------------------------- #
# 3) Rate limit: over-limit => 429, and the 429 performs NO action (fail-closed)
# --------------------------------------------------------------------------- #
def test_rate_limit_returns_429_and_performs_no_action(app_mod):
    A = _client(app_mod)
    sess = sessionmod.SESSIONS.get(_sid(A))
    assert A.get("/api/state").json()["closed_count"] == 0

    # Drain this session's bucket to empty with NO refill, then attempt a mutating fast-path drive.
    sessionmod.configure_rate_limit(capacity=0, refill_per_s=0)
    sess.bucket.reset()
    r = A.post("/api/drive/2")                       # would CLOSE a fix if it ran
    assert r.status_code == 429
    assert r.json()["error"] == "rate_limited"

    # Restore a working bucket; the 429'd request must have executed NOTHING.
    sessionmod.configure_rate_limit(240, 120)
    sess.bucket.reset()
    assert A.get("/api/state").json()["closed_count"] == 0, "the rate-limited drive never ran"


# --------------------------------------------------------------------------- #
# 3b) /health is a cookieless infra probe — it must mint NO session (an always-on health poll
#     would otherwise churn a throwaway world per request: FD/disk pressure on the live deploy).
# --------------------------------------------------------------------------- #
def test_health_probe_mints_no_session(app_mod):
    before = len(sessionmod.SESSIONS)
    c = TestClient(app_mod.app)
    for _ in range(6):
        r = c.get("/health")
        assert r.status_code == 200 and r.json()["status"] == "ok"
        assert "set-cookie" not in {k.lower() for k in r.headers}, "no session cookie on /health"
    assert sessionmod.COOKIE_NAME not in c.cookies, "health never sets the session cookie"
    assert len(sessionmod.SESSIONS) == before, "N health polls create ZERO sessions"


# --------------------------------------------------------------------------- #
# 4) Cross-session regression (the permanent guard) — would FAIL under the old single-global
#    design: a global _PENDING would show/serve A's held approval to B.
# --------------------------------------------------------------------------- #
def test_cross_session_held_approval_never_leaks(app_mod):
    A, B = _client(app_mod), _client(app_mod)

    # A holds an approval on INC-1.
    assert A.post("/api/drive/1?hold=true").json()["status"] == "pending_approval"
    assert len(A.get("/api/gate/pending").json()["pending"]) == 1

    # B sees NOTHING (old design: this list would be non-empty for B too).
    assert B.get("/api/gate/pending").json()["pending"] == []

    # B trying to approve "INC-1" is a fail-closed non-action — it cannot reach A's held plan.
    rb = B.post("/api/gate/1/decide?text=approve").json()
    assert rb["verdict"] == "approve" and rb["status"] == "no_live_approval"
    assert B.get("/api/state").json()["closed_count"] == 0

    # A's hold is intact and A can still approve its OWN change.
    ra = A.post("/api/gate/1/decide?text=approve&principal=Priya").json()
    assert ra["verdict"] == "approve" and ra["verified"] is True


# --------------------------------------------------------------------------- #
# 4b) The session cookie gets Secure ONLY on HTTPS (or a hosted/HTTPS env flag) — never on
#     plain-HTTP local/dev/TestClient (else the browser drops it and the suite breaks). HttpOnly
#     + SameSite=Lax always. (CSRF-token defense is out of scope; SameSite=Lax stands.)
# --------------------------------------------------------------------------- #
def test_cookie_secure_only_on_https_or_flag(app_mod, monkeypatch):
    monkeypatch.delenv("PRECEDENT_HTTPS", raising=False)
    monkeypatch.delenv("PRECEDENT_HOSTED", raising=False)

    # Plain HTTP (TestClient) — no Secure, but HttpOnly + SameSite=Lax hold.
    setc = TestClient(app_mod.app).get("/").headers.get("set-cookie", "")
    assert sessionmod.COOKIE_NAME in setc
    assert "Secure" not in setc
    assert "HttpOnly" in setc and "SameSite=lax" in setc

    # Hosted flag set — Secure is stamped even over the plain-HTTP TestClient.
    monkeypatch.setenv("PRECEDENT_HOSTED", "1")
    setc_hosted = TestClient(app_mod.app).get("/").headers.get("set-cookie", "")
    assert "Secure" in setc_hosted
    assert "HttpOnly" in setc_hosted and "SameSite=lax" in setc_hosted


# --------------------------------------------------------------------------- #
# 5) ONE background tick over live sessions (not N tasks) + lifespan boot/cleanup
# --------------------------------------------------------------------------- #
def test_single_registry_tick_evicts_expired_and_keeps_live(app_mod, monkeypatch):
    A, B = _client(app_mod), _client(app_mod)
    sidA, sidB = _sid(A), _sid(B)

    # Make A idle-expired while B stays fresh; ttl small so only A ages out.
    sessionmod.SESSIONS.get(sidA).last_seen -= 10_000
    monkeypatch.setattr(sessionmod.SESSIONS, "ttl", 60)

    sessionmod.registry_tick()   # the exact body the single lifespan task runs on an interval

    assert sessionmod.SESSIONS.get(sidA) is None, "expired session evicted by the one tick"
    assert sessionmod.SESSIONS.get(sidB) is not None, "live session retained + ticked"


def test_lifespan_boots_serves_and_cleans_up(app_mod):
    # Entering the context runs the migrated lifespan (warms the snapshot, starts the ONE tick
    # task); exiting cancels the task and closes every session (no orphan files/FDs).
    with TestClient(app_mod.app) as c:
        assert c.get("/api/state").status_code == 200
        assert len(sessionmod.SESSIONS) >= 1
    assert len(sessionmod.SESSIONS) == 0
