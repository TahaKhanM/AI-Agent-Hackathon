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
from agents.watcher import decide_from_reply
from console.app import app
from console.demo_state import STATE
from precedent import console_link, orchestrator
from precedent.contracts import ApprovalDecision, IncidentEvent
from precedent.tools import SimTools
from precedent_memory import audit, db
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


def _expired(req) -> bool:
    """True when a pending ApprovalRequest is past its TTL (or unparseable -> fail-closed)."""
    ts = db.parse_iso(getattr(req, "expires_at", "") or "")
    return ts is None or db.utcnow() >= ts


def _prune_pending() -> None:
    """P0.7(c): drop expired entries from the in-process pending map so a dropped hold never
    lingers past its TTL (the DB `approval` ledger ages it out too — this keeps the map honest)."""
    for inc_id, prepared in list(_PENDING.items()):
        req = getattr(prepared, "approval_request", None)
        if req is None or _expired(req):
            _PENDING.pop(inc_id, None)


def _plan_preview(prepared) -> dict:
    """The diff preview shown on the pending-approval card (P1.7): pre_state vs the planned
    mutation + the rollback anchor — 'you approve exactly this change, with exactly this undo'."""
    ref = prepared.ref or {}
    return {
        "action": (prepared.rule or {}).get("action_type"),
        "object_type": ref.get("object_type"),
        "object_id": ref.get("object_id"),
        "risk_class": prepared.assessment.risk_class if prepared.assessment else None,
        "pre_state": prepared.pre_state or {},
        "planned": [{"tool": s.tool, "args": s.args} for s in prepared.plan.steps],
        "rollback_ref": prepared.plan.pre_state_snapshot_ref,
        "plan_hash": prepared.plan.plan_hash,
    }


@app.post("/api/drive/{n}")
def api_drive(n: int, approve: bool = True, hold: bool = False, flake: bool = False,
              principal: str | None = None):
    """Run the REAL orchestrator for incident n IN this process, streaming every hop to the live
    trace panel. approve=true auto-approves the slow-path (rehearsal); hold=true instead PAUSES at
    the gate — records a pending approval (10-min TTL) for a human to Approve via
    /api/drive/{n}/approve. The fast-path (STANDING) needs no approval and runs straight through,
    zero-LLM. flake=true arms the one-shot verification failure ONLY on a path that will execute
    (P0.7d), so it can never stay armed and poison the next drive.

    P0.4: STATE.conn (one writer, no cross-connection contention) is touched ONLY under STATE._lock,
    and the slow SMART rationale (venice.chat) runs OUTSIDE the lock — so /api/state stays
    responsive and the trace panel streams (prepare hops, then the model 'thinking' window, then
    execution) instead of appearing all-at-once after the drive."""
    principal = principal or STATE.principal
    sim = SimTools(base_url=SIM_URL)
    p = sim.incident(n)                          # sim read — outside the lock
    inc = IncidentEvent(incident_id=p["incident_id"], raw_text=p["raw_text"],
                        source="sim", observed_at=p["observed_at"])
    trace = console_link.in_process_trace(STATE)
    with STATE._lock:                            # brief: deterministic prepare (no LLM under lock)
        prepared = orchestrator.prepare(inc, structured=p["structured"], conn=STATE.conn,
                                        tools=sim, principal=principal, trace=trace,
                                        defer_rationale=True)
    if prepared.outcome in ("refused", "escalated"):
        return _result(n, prepared.result)       # non-executing path -> a flake is NEVER armed
    if prepared.fast:
        if flake:
            sim.arm_flake()                      # armed right before an execution consumes it
        with STATE._lock:
            return _result(n, orchestrator.commit_execution(prepared, conn=STATE.conn,
                                                            tools=sim, trace=trace))
    # slow-path: the SMART rationale prose is a network/LLM call — run it OUTSIDE the lock.
    orchestrator.fill_rationale(prepared)
    if hold:   # pause at the gate — real held approval with TTL (fail-closed)
        with STATE._lock:
            _prune_pending()
            approval.record_pending(STATE.conn, prepared.approval_request, sender_address=principal)
        _PENDING[inc.incident_id] = prepared
        return {"incident": n, "status": "pending_approval",
                "plan_hash": prepared.approval_request.plan_hash,
                "expires_at": prepared.approval_request.expires_at,
                "preview": _plan_preview(prepared)}   # P1.7: the diff the human approves
    decision = _auto_approve("ops-lead")(prepared.approval_request) if approve else None
    if decision is not None and flake:           # only arm when an execution WILL consume it
        sim.arm_flake()
    with STATE._lock:
        return _result(n, orchestrator.commit_execution(prepared, conn=STATE.conn, tools=sim,
                                                        trace=trace, decision=decision))


@app.post("/api/drive/{n}/approve")
def api_drive_approve(n: int, principal: str = "ops-lead"):
    """Resume a HELD drive: a human Approve. Fail-closed — an expired/absent pending approval
    NEVER executes (non-action). commit_execution makes no LLM call, so STATE._lock is held only
    for the brief deterministic execute/verify against the local sim."""
    inc_id = f"INC-{n}"
    with STATE._lock:
        approval.expire_stale(STATE.conn)                 # sweep first
        row = approval.lookup_pending(STATE.conn, inc_id)
        prepared = _PENDING.get(inc_id)
        if row is None or prepared is None:
            _PENDING.pop(inc_id, None)                    # P0.7(c): drop a stale in-process entry
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


@app.get("/api/gate/pending")
def api_gate_pending():
    """Expose held approvals SERVER-SIDE so the gate card survives a refresh, a second
    tab, or the visitor's phone — replacing the old client-only `window._gate` that was
    lost on reload. Fail-closed: expired holds are pruned before we answer."""
    with STATE._lock:
        _prune_pending()
        out = []
        for inc_id, prepared in _PENDING.items():
            req = getattr(prepared, "approval_request", None)
            try:
                n = int(inc_id.split("-")[1])
            except (IndexError, ValueError):
                continue
            out.append({"incident_id": inc_id, "n": n,
                        "plan_hash": req.plan_hash if req else None,
                        "expires_at": getattr(req, "expires_at", None),
                        "preview": _plan_preview(prepared)})
        return {"pending": out}


@app.post("/api/gate/{n}/decide")
def api_gate_decide(n: int, text: str = "", principal: str = "visitor"):
    """The participatory 'try to trick the gate' beat, wired to the REAL vocabulary
    guard (agents.watcher.decide_from_reply). Free text in; only an explicit approve
    token executes. A question ('what does this do?'), a bare 'ok'/'yes please', or a
    negation ('don't approve') RE-PRESENTS the card — it never executes. The verdict
    here is the same deterministic function the chat loop and its tests use."""
    verdict = decide_from_reply(text)
    if verdict == "approve":
        res = api_drive_approve(n, principal=principal)
        return {"verdict": "approve", **res}
    if verdict == "reject":
        res = api_drive_reject(n, principal=principal)
        return {"verdict": "reject", **res}
    return {"verdict": "represent", "incident": n,
            "detail": "Ambiguous. Here is the card again — only an explicit approval executes."}


def _mutate_hash(plan_hash: str) -> str:
    """Flip one hex character of a 64-char plan hash to simulate a forged approval."""
    if not plan_hash:
        return "0" * 64
    i = len(plan_hash) - 1
    ch = plan_hash[i]
    return plan_hash[:i] + ("0" if ch != "0" else "1")


@app.post("/api/drive/{n}/forge")
def api_drive_forge(n: int, principal: str = "visitor"):
    """The forgery beat: approve the HELD change with a plan hash that does NOT match the
    plan Precedent prepared. The real tamper check in commit_execution rejects it —
    nothing executes, an 'approval_decided rejected/tampered' row is written, and the
    genuine hold stays open so the visitor can still approve for real afterwards."""
    inc_id = f"INC-{n}"
    with STATE._lock:
        row = approval.lookup_pending(STATE.conn, inc_id)
        prepared = _PENDING.get(inc_id)
        if row is None or prepared is None:
            return {"incident": n, "status": "no_live_approval",
                    "detail": "expired or absent — nothing to forge"}
        forged = _mutate_hash(row["plan_hash"])
        decision = ApprovalDecision(incident_id=inc_id, plan_hash=forged, decision="approve",
                                    approver_principal=principal, channel="console",
                                    decided_at=db.utcnow_iso())
        res = orchestrator.commit_execution(prepared, conn=STATE.conn,
                                            tools=SimTools(base_url=SIM_URL),
                                            trace=console_link.in_process_trace(STATE),
                                            decision=decision)
        # deliberately do NOT mark/pop the pending — the honest approval remains available
    outcome = res.step_results[0].get("outcome") if res.step_results else "rejected"
    return {"incident": n, "status": outcome, "forged_hash": forged[:16] + "…",
            "detail": "forged approval rejected by the plan-hash tamper check (fail-closed)"}


@app.post("/api/drive/{n}/reject")
def api_drive_reject(n: int, principal: str = "ops-lead"):
    """Reject a HELD drive (the card's Reject button, P1.7). Marks the gate rejected, drops the
    in-process pending, and audits the human decision — nothing executes, state left untouched."""
    inc_id = f"INC-{n}"
    with STATE._lock:
        row = approval.lookup_pending(STATE.conn, inc_id)
        prepared = _PENDING.pop(inc_id, None)
        if row is None or prepared is None:
            return {"incident": n, "status": "no_live_approval",
                    "detail": "expired or absent — nothing to reject"}
        approval.mark(STATE.conn, inc_id, row["plan_hash"], "rejected")
        audit.audit("approval_decided", conn=STATE.conn, actor=principal, incident_id=inc_id,
                    decision="reject", plan_hash=row["plan_hash"], approver=principal)
        STATE.conn.commit()
    return {"incident": n, "status": "rejected", "detail": "no change made (fail-closed)"}


@app.post("/api/drive/{n}/flake")
def api_arm_flake(n: int):
    """The recovery beat: drive incident n with the one-shot verification flake armed. P0.7(d):
    the flake is armed INSIDE the drive, only on a path that will execute — never before a
    refused/escalated incident (which would leave it armed to poison the next drive)."""
    return api_drive(n, flake=True)


def _sync_tick() -> None:
    """One ACL re-sync / freshness tick (runs in a worker thread — never on the event loop).

    Fixes the freshness footgun: plain sync() of an UNCHANGED source does not re-stamp
    last_verified_at, so a restricted-but-authorised record (e.g. INC-2's scheduler fix)
    silently goes dark ~60s into a demo. When no LIVE Jira is configured (airplane mode —
    the seeded local store IS the source of truth) we run the gated freshness heartbeat,
    which re-affirms every non-revoked source and recompiles — keeping authorised memory
    readable indefinitely without ever masking an un-polled upstream tightening. With a
    real Jira configured, refresh_cached_freshness() instead runs a genuine poll (P0.6)."""
    with STATE._lock:
        if syncmod.live_source_configured():
            syncmod.sync(STATE.source, conn=STATE.conn)
        else:
            syncmod.refresh_cached_freshness(STATE.conn)   # airplane heartbeat
        STATE.conn.commit()


@app.on_event("startup")
async def _start_sync_loop() -> None:
    async def _loop() -> None:
        while True:
            await asyncio.sleep(_SYNC_INTERVAL_S)
            try:
                await asyncio.to_thread(_sync_tick)   # P0.4: never freeze the event loop
            except Exception:  # noqa: BLE001 — best-effort; a hiccup must not kill the server
                pass
    asyncio.create_task(_loop())
