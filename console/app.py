"""Demo console — server-rendered page + JSON polling, NO frontend framework. [owner T2, task T2-3]

Spec: Idea/refinement/02 §4 + 04-demo-and-video-script.md §1.2.

The console is a VIEW/CONTROL surface only. Every access decision is delegated to
precedent_memory (see console/demo_state.py). Terminology: the top ladder level is
"Standing Approval", never "Autonomous". The Revoke control is always visible on a
Standing-Approval class.

WP-HOST-SESSION: this app is served to MANY concurrent visitors. Every route resolves the
CURRENT session from the request cookie and operates on ITS private world (memory db + sim
db + pending/tamper/latency scratch) — no process-wide mutable singleton leaks across
visitors. A ``_session(request)`` helper returns that per-session world; a thin ``STATE``
module attribute (default None) is an OPT-IN test pin that restores the old single-world
behaviour for the pre-session unit tests. Session cookies + the hand-rolled rate limiter +
the single background tick live in console/session.py.
"""
from __future__ import annotations

import asyncio
import contextlib
import os
import time
from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from console import session as sessionmod
from console import showcase
from console.product import make_product_router
from console.read_api import make_read_router
from gate.api import make_gate_router
from gate.world import DEFAULT_PRINCIPALS, gate_world_from_session

# --------------------------------------------------------------------------- #
# Per-session resolution + legacy test pin
# --------------------------------------------------------------------------- #
# Production: STATE is None -> every request resolves its own per-cookie session (full
# isolation). Tests may ``monkeypatch.setattr(console.app, "STATE", some_DemoState)`` to run
# the app against ONE pinned world (the pre-session unit tests do this) — in that mode the
# middleware and per-cookie store are bypassed and these module globals ARE the world.
STATE = None

# Pinned/legacy audit-tamper round-trip store. In production this is unused; each session owns
# its own ``tamper_backup`` (console/session.py). Kept as a module attribute because the
# pre-session tests clear it directly (``console.app._TAMPER_BACKUP.clear()``).
_TAMPER_BACKUP: dict[int, str] = {}

_TICK_INTERVAL_S = 20  # single background tick cadence (< the 60s ACL-freshness window)


class _LegacySession:
    """A single-world view over the module globals — used ONLY when ``STATE`` is pinned in a
    test. Exposes the same surface the routes use so route bodies stay session-agnostic."""

    @property
    def state(self):
        return STATE

    @property
    def tamper_backup(self) -> dict[int, str]:
        return _TAMPER_BACKUP

    @property
    def lat_ring(self):
        return showcase._LAT_RING

    def reset_world(self) -> dict:
        _TAMPER_BACKUP.clear()
        return STATE.reset()


def _session(request: Request | None = None):
    """Resolve the world for THIS request: the pinned world in test mode, else the per-cookie
    session (created fresh + cold-open on first hit / after eviction — fail-closed)."""
    if STATE is not None:
        return _LegacySession()
    return sessionmod.session_from_request(request)


# --------------------------------------------------------------------------- #
# App + lifespan (migrated off the deprecated @app.on_event)
# --------------------------------------------------------------------------- #
@contextlib.asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Own the ONE background tick for ALL sessions (not one task per session) and warm the
    cold-open snapshot so the first visitor doesn't wait. Skipped entirely in pinned test mode."""
    task: asyncio.Task | None = None
    if STATE is None:
        with contextlib.suppress(Exception):
            sessionmod.memory_template()  # warm the cheap template; sim builds lazily on drive

        async def _loop() -> None:
            while True:
                await asyncio.sleep(_TICK_INTERVAL_S)
                with contextlib.suppress(Exception):
                    # Never block the event loop on sqlite: hop to a worker thread.
                    await asyncio.to_thread(sessionmod.registry_tick)

        task = asyncio.create_task(_loop())
    try:
        yield
    finally:
        if task is not None:
            task.cancel()
            with contextlib.suppress(Exception, asyncio.CancelledError):
                await task
        if STATE is None:
            sessionmod.SESSIONS.close_all()


app = FastAPI(title="Precedent Console", lifespan=_lifespan)

_STATIC_DIR = Path(__file__).parent / "static"
if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


# --------------------------------------------------------------------------- #
# Session cookie + hand-rolled rate limit — applied to every public request.
# --------------------------------------------------------------------------- #
# Cookieless infra endpoints that need NO private session (no world, no cookie, no store entry).
# /health is polled by the always-on deploy's liveness check; minting a throwaway session per
# poll would churn a memory+sim world every few seconds (FD/disk pressure).
_SESSIONLESS_PATHS = frozenset({"/health"})


@app.middleware("http")
async def _session_and_rate_limit(request: Request, call_next):
    """Resolve/create the per-cookie session, enforce the token-bucket rate limit (over-limit
    => 429, a NON-action), and stamp the session cookie on the response. Bypassed in pinned
    test mode, for /static assets, and for cookieless infra endpoints (/health)."""
    if (STATE is not None
            or request.url.path.startswith("/static")
            or request.url.path in _SESSIONLESS_PATHS):
        return await call_next(request)

    sid = request.cookies.get(sessionmod.COOKIE_NAME)
    session = sessionmod.SESSIONS.resolve(sid)
    request.state.session = session

    if not session.bucket.allow():
        # Fail-closed: short-circuit BEFORE any route/session mutation runs.
        response = JSONResponse(
            {"error": "rate_limited", "detail": "Too many requests — slow down."},
            status_code=429,
        )
    else:
        response = await call_next(request)

    # Secure the session cookie on HTTPS (or when a hosted/HTTPS env flag is set), but NOT on
    # plain-HTTP local/dev/TestClient — else the browser drops the cookie and the suite + local
    # uvicorn break. HttpOnly + SameSite=Lax always. (CSRF-token defense is out of scope; the
    # SameSite=Lax default stands for now.)
    secure = (
        request.url.scheme == "https"
        or bool(os.environ.get("PRECEDENT_HTTPS"))
        or bool(os.environ.get("PRECEDENT_HOSTED"))
    )
    response.set_cookie(
        sessionmod.COOKIE_NAME, session.sid,
        max_age=sessionmod.COOKIE_MAX_AGE, httponly=True, samesite="lax", path="/",
        secure=secure,
    )
    return response


# --------------------------------------------------------------------------- #
# Request bodies
# --------------------------------------------------------------------------- #
class TriageReq(BaseModel):
    incident_id: str


class ApproveReq(BaseModel):
    incident_id: str
    principal: str | None = None


class LadderReq(BaseModel):
    class_key: str
    principal: str | None = None


class FlipReq(BaseModel):
    on: bool | None = None


class TraceReq(BaseModel):
    step: str
    detail: str = ""
    incident_id: str | None = None


# --------------------------------------------------------------------------- #
# JSON API
# --------------------------------------------------------------------------- #
@app.get("/health")
def health(request: Request):
    # Cookieless liveness probe: NO per-session world (see _SESSIONLESS_PATHS). In pinned test
    # mode report the pinned world; in production report the cached cold-open template status so
    # a health poll never mints a session.
    snap = STATE.snapshot() if STATE is not None else sessionmod.template_status()
    return {"status": "ok", **snap["status"], "precedents": snap["precedents_count"]}


@app.get("/api/state")
def api_state(request: Request):
    return _session(request).state.snapshot()


@app.get("/api/events")
def api_events(request: Request):
    return _session(request).state.events()


@app.post("/api/triage")
def api_triage(req: TriageReq, request: Request):
    sess = _session(request)
    t0 = time.perf_counter_ns()
    try:
        return sess.state.triage(req.incident_id)
    finally:
        # Rolling P99 for the BasedAI proof strip. VIEW-ONLY measurement — does not participate
        # in the risk / permission decision. Per-session ring (no cross-visitor bleed).
        showcase.record_latency_ns(time.perf_counter_ns() - t0, sess.lat_ring)


# --------------------------------------------------------------------------- #
# Showcase read-only endpoints (VIEW surface only — no logic branches into these)
# --------------------------------------------------------------------------- #
@app.get("/api/copy")
def api_copy():
    """Static prose bundle for the guided tour + strips. Never fetches at runtime."""
    return showcase.copy_bundle()


@app.get("/api/latency")
def api_latency(request: Request):
    """Rolling P50/P99 of REAL permission-check calls. Measurement-only.

    If the ring is empty (first call after boot), run a small benchmark of the live
    check_access path to seed it — this way the sparkline is populated even before any
    incident is driven.
    """
    sess = _session(request)
    snap = showcase.latency_snapshot(sess.lat_ring)
    if snap["samples"] == 0:
        showcase._bench_permission_check(sess.state.conn, sess.lat_ring, n=200)
        snap = showcase.latency_snapshot(sess.lat_ring)
    snap["kernel_hash"] = showcase.KERNEL_HASH
    return snap


@app.get("/api/kernel-hash")
def api_kernel_hash():
    """Deterministic-surface fingerprint. Compared against MANIFEST.json for external
    attestation — a hash pinned in a committed file the running process cannot forge.
    """
    expected = showcase.manifest_expected_hash()
    return {
        "kernel_hash": showcase.KERNEL_HASH,
        "manifest_expected": expected,
        "matches_manifest": (expected is not None and expected == showcase.KERNEL_HASH),
        "manifest_present": expected is not None,
    }


@app.get("/api/model-calls")
def api_model_calls():
    """Honest counter of REAL network calls to the open-weight model endpoint this session
    (never cache hits). The zero-LLM fast path keeps it at 0, so the number IS the proof.
    """
    from precedent import venice
    return {"model_calls": venice.model_call_count()}


def _tamper_one(payload: str | None) -> str:
    """Return a payload string guaranteed to differ from the input by one byte, so the stored
    row hash no longer matches its recomputed value."""
    p = payload or "{}"
    last = p[-1]
    return p[:-1] + ("0" if last != "0" else "1")


@app.post("/api/audit/tamper")
def api_audit_tamper(request: Request, seq: int | None = None):
    """REAL tamper: flip one byte in one audit row's payload (default: the newest row, or the
    caller's chosen seq). The row's stored hash is left untouched, so the REAL verifier below
    fails at exactly this row. Restore is a true round-trip. Per-session (backup keyed by seq
    within THIS session's audit chain — never another session's)."""
    from precedent_memory import audit
    sess = _session(request)
    state = sess.state
    with state._lock:
        if seq is None:
            row = state.conn.execute(
                "SELECT seq FROM audit_log ORDER BY seq DESC LIMIT 1").fetchone()
            if row is None:
                return {"ok": False, "detail": "audit log is empty"}
            seq = row["seq"]
        row = state.conn.execute(
            "SELECT payload FROM audit_log WHERE seq = ?", (seq,)).fetchone()
        if row is None:
            return {"ok": False, "detail": f"no audit row #{seq}"}
        sess.tamper_backup.setdefault(seq, row["payload"] or "{}")
        state.conn.execute("UPDATE audit_log SET payload = ? WHERE seq = ?",
                           (_tamper_one(row["payload"]), seq))
        state.conn.commit()
        verified = audit.verify_chain(conn=state.conn)
    return {"ok": True, "tampered_seq": seq, "verified": verified,
            "detail": f"flipped one byte of audit row #{seq}"}


@app.post("/api/audit/restore")
def api_audit_restore(request: Request):
    """Undo every real tamper: rewrite each corrupted row's original payload, so the REAL
    verifier passes again. Deterministic, no re-hashing tricks."""
    from precedent_memory import audit
    sess = _session(request)
    state = sess.state
    with state._lock:
        for seq, original in list(sess.tamper_backup.items()):
            state.conn.execute("UPDATE audit_log SET payload = ? WHERE seq = ?",
                               (original, seq))
        state.conn.commit()
        sess.tamper_backup.clear()
        verified = audit.verify_chain(conn=state.conn)
    return {"ok": True, "verified": verified}


@app.get("/api/audit/verify")
def api_audit_verify(request: Request):
    """REAL hash-chain verification over on-disk audit rows. Read-only. This is the endpoint
    the audit-chain proof reflects.
    """
    from precedent_memory import audit
    state = _session(request).state
    with state._lock:
        try:
            ok = audit.verify_chain(conn=state.conn)
            length = state.conn.execute(
                "SELECT COUNT(*) FROM audit_log").fetchone()[0]
            tail = state.conn.execute(
                "SELECT hash FROM audit_log ORDER BY seq DESC LIMIT 1").fetchone()
            return {
                "verified": bool(ok),
                "rows": length,
                "tail_hash": (tail[0][:16] + "…") if tail else None,
            }
        except Exception as e:
            return {"verified": False, "rows": 0, "tail_hash": None,
                    "error": str(e).splitlines()[0][:200]}


@app.post("/api/probes/run")
def api_probes_run(request: Request, n: int = 100):
    """Fire n adversarial permission-check probes against THIS session's memory db. Read-only.
    Returns leak count (should be zero) + P50/P99 latency.
    """
    sess = _session(request)
    return showcase.run_adversarial_probes(sess.state.conn, sess.lat_ring, n=n)


@app.post("/api/approve")
def api_approve(req: ApproveReq, request: Request):
    return _session(request).state.approve(req.incident_id, req.principal)


@app.post("/api/promote")
def api_promote(req: LadderReq, request: Request):
    return _session(request).state.promote(req.class_key, req.principal)


@app.post("/api/revoke")
def api_revoke(req: LadderReq, request: Request):
    return _session(request).state.revoke(req.class_key, req.principal)


@app.post("/api/permission-flip")
def api_permission_flip(req: FlipReq, request: Request):
    return _session(request).state.permission_flip(req.on)


@app.post("/api/trace")
def api_trace(req: TraceReq, request: Request):
    """T1 integration seam: the execution loop pushes DETECT/EXECUTE/VERIFY steps."""
    return _session(request).state.push_trace(req.model_dump())


@app.post("/api/demo/reset")
def api_reset(request: Request):
    from precedent import venice
    venice.reset_model_calls()
    return _session(request).reset_world()


@app.get("/api/change-record/{incident_id}", response_class=PlainTextResponse)
def api_change_record(incident_id: str, request: Request):
    """P1.7: one-click export of an incident's ITIL change record, rendered deterministically
    from the REAL hash-chained audit rows (no LLM, no network). Downloads as markdown."""
    from scripts.render_change_record import render
    state = _session(request).state
    with state._lock:
        doc = render(state.conn, incident_id)
    safe = "".join(c for c in incident_id if c.isalnum() or c in "-_") or "record"
    return PlainTextResponse(doc, media_type="text/markdown", headers={
        "Content-Disposition": f'attachment; filename="change-record-{safe}.md"'})


# --------------------------------------------------------------------------- #
# The page — "The Approver's Seat" (v2 demo). Server-rendered shell + a self-paced,
# chaptered narrative that drives the REAL kernel at every beat. No frontend framework,
# no inline handlers (one delegated listener off data-* attributes).
# --------------------------------------------------------------------------- #
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request=request, name="demo.html")


# --------------------------------------------------------------------------- #
# Versioned HTTP Gate API (WP-API) — the product spine, mounted into ONE deploy.
# --------------------------------------------------------------------------- #
# Every surface consumes /v1/gate; the console dogfoods it over HTTP. The gate operates on the
# CURRENT session's private world (memory db + in-process sim + a per-session pending registry),
# resolved the same way every other route resolves its world (``_session``). No LLM in the gate's
# decision path; identity is passed in-band but registered out-of-band (see gate/README.md).
def _gate_world(request: Request):
    # Pass a CONCRETE principals set so the mounted gate enforces out-of-band registration: an
    # unregistered, self-asserted principal is a non-action (deny/reject). Without this the gate
    # world defaulted principals=None (restriction OFF) and ANY claimed identity was accepted —
    # a deployed auth bypass. The seeded session registers exactly DEFAULT_PRINCIPALS.
    return gate_world_from_session(_session(request), principals=DEFAULT_PRINCIPALS)


app.include_router(make_gate_router(_gate_world), prefix="/v1/gate")


# --------------------------------------------------------------------------- #
# WP-CONSOLE — the per-incident notarised case-file console.
# --------------------------------------------------------------------------- #
# The kernel-backed read/query + ladder-control endpoints (console/read_api.py) resolve the SAME
# per-session world every other route uses. The kernel-FREE page router (console/product/) renders
# the /console shell that consumes those endpoints (and /v1/gate/*) over HTTP — it imports no
# kernel (CI-guarded by scripts/check_product_imports.sh).
app.include_router(make_read_router(_session))
app.include_router(make_product_router())
