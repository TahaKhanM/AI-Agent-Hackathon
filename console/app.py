"""Demo console — server-rendered page + JSON polling, NO frontend framework. [owner T2, task T2-3]

Spec: Idea/refinement/02 §4 + 04-demo-and-video-script.md §1.2.

The console is a VIEW/CONTROL surface only. Every access decision is delegated to
precedent_memory (see console/demo_state.py). Terminology: the top ladder level is
"Standing Approval", never "Autonomous". The Revoke control is always visible on a
Standing-Approval class. The console runs end-to-end on the seeded local-demo
scenario even when the T1 loop is not wired; T1 streams its own steps via POST
/api/trace.
"""
from __future__ import annotations

import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from console import showcase
from console.demo_state import STATE

app = FastAPI(title="Precedent Console")

_STATIC_DIR = Path(__file__).parent / "static"
if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

# Jinja2 templates (WP-REFACTOR): the demo page moved out of a raw Python string into
# console/templates/demo.html. Context today is just {"request": request}; later WPs
# can add variables without touching the route.
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


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
def health():
    snap = STATE.snapshot()
    return {"status": "ok", **snap["status"], "precedents": snap["precedents_count"]}


@app.get("/api/state")
def api_state():
    return STATE.snapshot()


@app.get("/api/events")
def api_events():
    return STATE.events()


@app.post("/api/triage")
def api_triage(req: TriageReq):
    t0 = time.perf_counter_ns()
    try:
        return STATE.triage(req.incident_id)
    finally:
        # Rolling P99 for the BasedAI proof strip. VIEW-ONLY measurement — does
        # not participate in the risk / permission decision.
        showcase.record_latency_ns(time.perf_counter_ns() - t0)


# --------------------------------------------------------------------------- #
# Showcase read-only endpoints (VIEW surface only — no logic branches into these)
# --------------------------------------------------------------------------- #
@app.get("/api/copy")
def api_copy():
    """Static prose bundle for the guided tour + strips. Never fetches at runtime."""
    return showcase.copy_bundle()


@app.get("/api/latency")
def api_latency():
    """Rolling P50/P99 of REAL permission-check calls. Measurement-only.

    If the ring is empty (first call after boot), run a small benchmark of the
    live check_access path to seed it — this way the sparkline is populated
    even before any incident is driven.
    """
    snap = showcase.latency_snapshot()
    if snap["samples"] == 0:
        showcase._bench_permission_check(n=200)
        snap = showcase.latency_snapshot()
    snap["kernel_hash"] = showcase.KERNEL_HASH
    return snap


@app.get("/api/kernel-hash")
def api_kernel_hash():
    """Deterministic-surface fingerprint. Compared against MANIFEST.json for
    external attestation — a hash pinned in a committed file the running process
    cannot forge.
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
    """Honest counter of REAL network calls to the open-weight model endpoint this
    session (never cache hits). The demo header renders this as "Model calls this
    session: N" — the zero-LLM fast path keeps it at 0, so the number IS the proof.
    """
    from precedent import venice
    return {"model_calls": venice.model_call_count()}


# The real-tamper affordance keeps the ORIGINAL payload of every row it corrupts so
# Restore is a true round-trip. Session-scoped in spirit (single-writer STATE.conn);
# a tampered byte makes the REAL /api/audit/verify fail at that row — no fake pill.
_TAMPER_BACKUP: dict[int, str] = {}


def _tamper_one(payload: str | None) -> str:
    """Return a payload string guaranteed to differ from the input by one byte, so the
    stored row hash no longer matches its recomputed value."""
    p = payload or "{}"
    last = p[-1]
    return p[:-1] + ("0" if last != "0" else "1")


@app.post("/api/audit/tamper")
def api_audit_tamper(seq: int | None = None):
    """REAL tamper: flip one byte in one audit row's payload (default: the newest row,
    or the caller's chosen seq). The row's stored hash is left untouched, so the REAL
    verifier below fails at exactly this row. Restore is a true round-trip. This
    replaces the old cosmetic "Tamper (visual)" button — nothing is faked."""
    from precedent_memory import audit
    with STATE._lock:
        if seq is None:
            row = STATE.conn.execute(
                "SELECT seq FROM audit_log ORDER BY seq DESC LIMIT 1").fetchone()
            if row is None:
                return {"ok": False, "detail": "audit log is empty"}
            seq = row["seq"]
        row = STATE.conn.execute(
            "SELECT payload FROM audit_log WHERE seq = ?", (seq,)).fetchone()
        if row is None:
            return {"ok": False, "detail": f"no audit row #{seq}"}
        _TAMPER_BACKUP.setdefault(seq, row["payload"] or "{}")
        STATE.conn.execute("UPDATE audit_log SET payload = ? WHERE seq = ?",
                            (_tamper_one(row["payload"]), seq))
        STATE.conn.commit()
        verified = audit.verify_chain(conn=STATE.conn)
    return {"ok": True, "tampered_seq": seq, "verified": verified,
            "detail": f"flipped one byte of audit row #{seq}"}


@app.post("/api/audit/restore")
def api_audit_restore():
    """Undo every real tamper: rewrite each corrupted row's original payload, so the
    REAL verifier passes again. Deterministic, no re-hashing tricks."""
    from precedent_memory import audit
    with STATE._lock:
        for seq, original in list(_TAMPER_BACKUP.items()):
            STATE.conn.execute("UPDATE audit_log SET payload = ? WHERE seq = ?",
                               (original, seq))
        STATE.conn.commit()
        _TAMPER_BACKUP.clear()
        verified = audit.verify_chain(conn=STATE.conn)
    return {"ok": True, "verified": verified}


@app.get("/api/audit/verify")
def api_audit_verify():
    """REAL hash-chain verification over on-disk audit rows. Read-only. This is
    the endpoint the audit-chain proof reflects.
    """
    from precedent_memory import audit
    with STATE._lock:
        try:
            ok = audit.verify_chain(conn=STATE.conn)
            length = STATE.conn.execute(
                "SELECT COUNT(*) FROM audit_log").fetchone()[0]
            tail = STATE.conn.execute(
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
def api_probes_run(n: int = 100):
    """Fire n adversarial permission-check probes against the live memory db.
    Read-only. Returns leak count (should be zero) + P50/P99 latency.
    """
    return showcase.run_adversarial_probes(n=n)


@app.post("/api/approve")
def api_approve(req: ApproveReq):
    return STATE.approve(req.incident_id, req.principal)


@app.post("/api/promote")
def api_promote(req: LadderReq):
    return STATE.promote(req.class_key, req.principal)


@app.post("/api/revoke")
def api_revoke(req: LadderReq):
    return STATE.revoke(req.class_key, req.principal)


@app.post("/api/permission-flip")
def api_permission_flip(req: FlipReq):
    return STATE.permission_flip(req.on)


@app.post("/api/trace")
def api_trace(req: TraceReq):
    """T1 integration seam: the execution loop pushes DETECT/EXECUTE/VERIFY steps."""
    return STATE.push_trace(req.model_dump())


@app.post("/api/demo/reset")
def api_reset():
    from precedent import venice
    _TAMPER_BACKUP.clear()
    venice.reset_model_calls()
    return STATE.reset()


@app.get("/api/change-record/{incident_id}", response_class=PlainTextResponse)
def api_change_record(incident_id: str):
    """P1.7: one-click export of an incident's ITIL change record, rendered deterministically
    from the REAL hash-chained audit rows (no LLM, no network). Downloads as markdown."""
    from scripts.render_change_record import render
    with STATE._lock:
        doc = render(STATE.conn, incident_id)
    safe = "".join(c for c in incident_id if c.isalnum() or c in "-_") or "record"
    return PlainTextResponse(doc, media_type="text/markdown", headers={
        "Content-Disposition": f'attachment; filename="change-record-{safe}.md"'})


# --------------------------------------------------------------------------- #
# The page — "The Approver's Seat" (v2 demo). Server-rendered shell + a self-paced,
# chaptered narrative that drives the REAL kernel at every beat. No frontend
# framework, no inline handlers (one delegated listener off data-* attributes).
# --------------------------------------------------------------------------- #
@app.get("/")
def index(request: Request):
    # Modern Starlette signature (request first); `request` is injected into the
    # template context automatically, and later WPs can pass a context= dict here.
    return templates.TemplateResponse(request=request, name="demo.html")
