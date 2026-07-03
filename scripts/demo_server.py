"""Same-process demo server: the judge console + T1's in-process drive.  [owner T1, task T1-10/E]

The resolved-decision design: run T1's orchestrator IN the console's process so POST
/api/trace-equivalent hops (via in_process_trace) light the LIVE trace panel, and — the
load-bearing reason — so only ONE process ever writes the shared memory db (no cross-process
SQLite write contention). The MediaCo sim stays a separate process on its own db (no
shared-db contention), reached over HTTP by the Operator's typed tools.

This EXTENDS the imported console app at runtime (add_api_route / startup hook) — it does
not modify or rebuild console/ (T2). Adds:
  - POST /api/drive/{n}         run the real loop for incident n in-process (streams trace)
  - a periodic ACL re-sync      keeps restricted-record freshness < 60s (models the Jira poll)
RULE 1/2: no model id, no LLM decision here.
"""
from __future__ import annotations

import asyncio
import os

from agents import approval
from console.app import app
from console.demo_state import STATE
from precedent import console_link, orchestrator
from precedent.contracts import ApprovalDecision, IncidentEvent
from precedent.tools import SimTools
from precedent_memory import db
from precedent_memory import sync as syncmod

SIM_URL = os.environ.get("PRECEDENT_SIM_URL", "http://127.0.0.1:8100")
_SYNC_INTERVAL_S = 20   # < the 60s freshness window, so restricted memory stays readable
_PENDING: dict[str, object] = {}   # incident_id -> Prepared (same-process approval handoff)


def _auto_approve(principal: str):
    def approve(req):
        return ApprovalDecision(incident_id=req.incident_id, plan_hash=req.plan_hash,
                                decision="approve", approver_principal=principal,
                                channel="console", decided_at=db.utcnow_iso())
    return approve


def _result(n, res):
    return {"incident": n, "verified": res.verified, "rolled_back": res.rolled_back,
            "outcome": res.step_results[0].get("outcome")}


@app.post("/api/drive/{n}")
def api_drive(n: int, approve: bool = True, hold: bool = False, principal: str | None = None):
    """Run the REAL orchestrator for incident n IN this process, sharing STATE.conn under
    STATE's lock and streaming every hop to the live trace panel. approve=true auto-approves
    the slow-path (rehearsal); hold=true instead PAUSES at the gate — records a pending
    approval (10-min TTL) for a human to Approve via /api/drive/{n}/approve. The fast-path
    (STANDING) needs no approval and runs straight through, zero-LLM."""
    principal = principal or STATE.principal
    with STATE._lock:
        sim = SimTools(base_url=SIM_URL)
        p = sim.incident(n)
        inc = IncidentEvent(incident_id=p["incident_id"], raw_text=p["raw_text"],
                            source="sim", observed_at=p["observed_at"])
        trace = console_link.in_process_trace(STATE)
        prepared = orchestrator.prepare(inc, structured=p["structured"], conn=STATE.conn,
                                        tools=sim, principal=principal, trace=trace)
        if prepared.outcome in ("refused", "escalated"):
            return _result(n, prepared.result)
        if prepared.fast:
            return _result(n, orchestrator.commit_execution(prepared, conn=STATE.conn,
                                                            tools=sim, trace=trace))
        if hold:   # pause at the gate — real held approval with TTL (fail-closed)
            approval.record_pending(STATE.conn, prepared.approval_request, sender_address=principal)
            _PENDING[inc.incident_id] = prepared
            return {"incident": n, "status": "pending_approval",
                    "plan_hash": prepared.approval_request.plan_hash,
                    "expires_at": prepared.approval_request.expires_at}
        decision = _auto_approve("ops-lead")(prepared.approval_request) if approve else None
        return _result(n, orchestrator.commit_execution(prepared, conn=STATE.conn, tools=sim,
                                                        trace=trace, decision=decision))


@app.post("/api/drive/{n}/approve")
def api_drive_approve(n: int, principal: str = "ops-lead"):
    """Resume a HELD drive: a human Approve. Fail-closed — an expired/absent pending
    approval NEVER executes (non-action)."""
    inc_id = f"INC-{n}"
    with STATE._lock:
        approval.expire_stale(STATE.conn)                 # sweep first
        row = approval.lookup_pending(STATE.conn, inc_id)
        prepared = _PENDING.get(inc_id)
        if row is None or prepared is None:
            return {"incident": n, "status": "no_live_approval",
                    "detail": "expired or absent — non-action (fail-closed)"}
        decision = ApprovalDecision(incident_id=inc_id, plan_hash=row["plan_hash"],
                                    decision="approve", approver_principal=principal,
                                    channel="console", decided_at=db.utcnow_iso())
        res = orchestrator.commit_execution(prepared, conn=STATE.conn,
                                            tools=SimTools(base_url=SIM_URL),
                                            trace=console_link.in_process_trace(STATE),
                                            decision=decision)
        approval.mark(STATE.conn, inc_id, row["plan_hash"], "approved")
        _PENDING.pop(inc_id, None)
    return _result(n, res)


@app.post("/api/drive/{n}/flake")
def api_arm_flake(n: int):
    """Arm the one-shot verification flake (the recovery beat), then drive incident n."""
    SimTools(base_url=SIM_URL).arm_flake()
    return api_drive(n, approve=False)


@app.on_event("startup")
async def _start_sync_loop() -> None:
    async def _loop() -> None:
        while True:
            await asyncio.sleep(_SYNC_INTERVAL_S)
            try:
                with STATE._lock:
                    syncmod.sync(STATE.source, conn=STATE.conn)   # refresh ACL freshness
            except Exception:  # noqa: BLE001 — best-effort; a hiccup must not kill the server
                pass
    asyncio.create_task(_loop())
