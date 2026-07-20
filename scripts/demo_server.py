"""Same-process demo server: the judge console + T1's in-process drive.  [owner T1, task T1-10/E]

The resolved-decision design: run T1's orchestrator IN the console's process so trace hops light
the LIVE trace panel, and — the load-bearing reason — so only ONE writer per session ever
touches that session's memory db (no cross-connection SQLite contention).

WP-HOST-SESSION: every drive/gate route resolves the CURRENT browser session from the request
(``_session(request)``) and operates on ITS private world — its own memory db (``sess.state``),
its own held-approval map (``sess.pending``), and its own in-process sim reached through
``sess.sim_tools()`` (a TestClient over that session's sim db copy — no shared ``flake_state``,
no shared MediaCo rows). The old process-wide ``STATE`` singleton + module ``_PENDING`` are
retired in production: ``STATE`` here is an OPT-IN test pin (default None) and ``_PENDING`` is
the pinned/legacy map the pre-session unit tests poke directly.

This EXTENDS the imported console app at runtime (add_api_route). The single background
ACL-freshness tick now lives in console.app's lifespan (one task over ALL live sessions).
RULE 1/2: no model id, no LLM decision here.
"""
from __future__ import annotations

import os

from fastapi import Request

from agents import approval
from agents.watcher import decide_from_reply
from console import session as sessionmod
from console.app import app
from precedent import console_link, orchestrator
from precedent.contracts import ApprovalDecision, IncidentEvent
from precedent.tools import SimTools
from precedent_memory import audit, db

SIM_URL = os.environ.get("PRECEDENT_SIM_URL", "http://127.0.0.1:8100")

# WP-HOST-SESSION test pins (default None => production uses per-cookie sessions). When a test
# sets ``demo_server.STATE`` to a DemoState, the routes run against that ONE pinned world and
# ``_PENDING`` is its held-approval map (matches the pre-session topology exactly).
STATE = None
_PENDING: dict[str, object] = {}   # pinned/legacy held-approval map (INC-n -> Prepared)


class _LegacySession:
    """Single-world view over the module pins — used ONLY when ``STATE`` is pinned in a test."""

    @property
    def state(self):
        return STATE

    @property
    def pending(self) -> dict:
        return _PENDING

    def sim_tools(self) -> SimTools:
        # Honour a monkeypatched ``SimTools`` (tests swap it for an in-process TestClient).
        return SimTools(base_url=SIM_URL)


def _session(request: Request = None):
    """Resolve the world for THIS request: the pinned world in test mode, else the per-cookie
    session. Direct function calls (no request) in pinned tests land on the legacy world."""
    if STATE is not None:
        return _LegacySession()
    return sessionmod.session_from_request(request)


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


def _prune_pending(pending: dict | None = None) -> None:
    """P0.7(c): drop expired entries from the in-process pending map so a dropped hold never
    lingers past its TTL. Defaults to the pinned/legacy ``_PENDING`` (the pre-session prune
    test calls ``_prune_pending()`` bare); production passes the session's ``sess.pending``."""
    pending = _PENDING if pending is None else pending
    for inc_id, prepared in list(pending.items()):
        req = getattr(prepared, "approval_request", None)
        if req is None or _expired(req):
            pending.pop(inc_id, None)


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
              principal: str | None = None, request: Request = None):
    """Run the REAL orchestrator for incident n IN this process against THIS session's world,
    streaming every hop to the live trace panel. approve=true auto-approves the slow-path
    (rehearsal); hold=true instead PAUSES at the gate — records a pending approval (10-min TTL)
    for a human to Approve via /api/drive/{n}/approve. The fast-path (STANDING) runs straight
    through, zero-LLM. flake=true arms the one-shot verification failure ONLY on a path that will
    execute (P0.7d), so it can never stay armed and poison the next drive.

    P0.4: the session's memory conn is touched ONLY under its RLock, and the slow SMART rationale
    (venice.chat) runs OUTSIDE the lock — so /api/state stays responsive and the trace streams."""
    sess = _session(request)
    state = sess.state
    principal = principal or state.principal
    sim = sess.sim_tools()
    p = sim.incident(n)                          # sim read — outside the lock
    inc = IncidentEvent(incident_id=p["incident_id"], raw_text=p["raw_text"],
                        source="sim", observed_at=p["observed_at"])
    trace = console_link.in_process_trace(state)
    with state._lock:                            # brief: deterministic prepare (no LLM under lock)
        prepared = orchestrator.prepare(inc, structured=p["structured"], conn=state.conn,
                                        tools=sim, principal=principal, trace=trace,
                                        defer_rationale=True)
    if prepared.outcome in ("refused", "escalated"):
        return _result(n, prepared.result)       # non-executing path -> a flake is NEVER armed
    if prepared.fast:
        if flake:
            sim.arm_flake()                      # armed right before an execution consumes it
        with state._lock:
            return _result(n, orchestrator.commit_execution(prepared, conn=state.conn,
                                                            tools=sim, trace=trace))
    # slow-path: the SMART rationale prose is a network/LLM call — run it OUTSIDE the lock.
    orchestrator.fill_rationale(prepared)
    if hold:   # pause at the gate — real held approval with TTL (fail-closed)
        with state._lock:
            _prune_pending(sess.pending)
            approval.record_pending(state.conn, prepared.approval_request, sender_address=principal)
        sess.pending[inc.incident_id] = prepared
        return {"incident": n, "status": "pending_approval",
                "plan_hash": prepared.approval_request.plan_hash,
                "expires_at": prepared.approval_request.expires_at,
                "preview": _plan_preview(prepared)}   # P1.7: the diff the human approves
    decision = _auto_approve("ops-lead")(prepared.approval_request) if approve else None
    if decision is not None and flake:           # only arm when an execution WILL consume it
        sim.arm_flake()
    with state._lock:
        return _result(n, orchestrator.commit_execution(prepared, conn=state.conn, tools=sim,
                                                        trace=trace, decision=decision))


@app.post("/api/drive/{n}/approve")
def api_drive_approve(n: int, principal: str = "ops-lead", request: Request = None):
    """Resume a HELD drive: a human Approve. Fail-closed — an expired/absent pending approval
    NEVER executes (non-action). commit_execution makes no LLM call, so the session lock is held
    only for the brief deterministic execute/verify against the session's sim."""
    sess = _session(request)
    state = sess.state
    inc_id = f"INC-{n}"
    with state._lock:
        approval.expire_stale(state.conn)                 # sweep first
        row = approval.lookup_pending(state.conn, inc_id)
        prepared = sess.pending.get(inc_id)
        if row is None or prepared is None:
            sess.pending.pop(inc_id, None)                # P0.7(c): drop a stale in-process entry
            return {"incident": n, "status": "no_live_approval",
                    "detail": "expired or absent — non-action (fail-closed)"}
        decision = ApprovalDecision(incident_id=inc_id, plan_hash=row["plan_hash"],
                                    decision="approve", approver_principal=principal,
                                    channel="console", decided_at=db.utcnow_iso())
        res = orchestrator.commit_execution(prepared, conn=state.conn,
                                            tools=sess.sim_tools(),
                                            trace=console_link.in_process_trace(state),
                                            decision=decision)
        approval.mark(state.conn, inc_id, row["plan_hash"], "approved")
        sess.pending.pop(inc_id, None)
    return _result(n, res)


@app.get("/api/gate/pending")
def api_gate_pending(request: Request = None):
    """Expose THIS session's held approvals SERVER-SIDE so the gate card survives a refresh, a
    second tab, or the visitor's phone. Fail-closed: expired holds are pruned before we answer,
    and one visitor's held card is NEVER shown to another (per-session ``sess.pending``)."""
    sess = _session(request)
    with sess.state._lock:
        _prune_pending(sess.pending)
        out = []
        for inc_id, prepared in sess.pending.items():
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
def api_gate_decide(n: int, text: str = "", principal: str = "visitor", request: Request = None):
    """The participatory 'try to trick the gate' beat, wired to the REAL vocabulary guard
    (agents.watcher.decide_from_reply). Free text in; only an explicit approve token executes.
    The request is threaded through so the decision runs against the SAME session's held gate."""
    verdict = decide_from_reply(text)
    if verdict == "approve":
        res = api_drive_approve(n, principal=principal, request=request)
        return {"verdict": "approve", **res}
    if verdict == "reject":
        res = api_drive_reject(n, principal=principal, request=request)
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
def api_drive_forge(n: int, principal: str = "visitor", request: Request = None):
    """The forgery beat: approve the HELD change with a plan hash that does NOT match the plan
    Precedent prepared. The real tamper check in commit_execution rejects it — nothing executes,
    an 'approval_decided rejected/tampered' row is written, and the genuine hold stays open."""
    sess = _session(request)
    state = sess.state
    inc_id = f"INC-{n}"
    with state._lock:
        row = approval.lookup_pending(state.conn, inc_id)
        prepared = sess.pending.get(inc_id)
        if row is None or prepared is None:
            return {"incident": n, "status": "no_live_approval",
                    "detail": "expired or absent — nothing to forge"}
        forged = _mutate_hash(row["plan_hash"])
        decision = ApprovalDecision(incident_id=inc_id, plan_hash=forged, decision="approve",
                                    approver_principal=principal, channel="console",
                                    decided_at=db.utcnow_iso())
        res = orchestrator.commit_execution(prepared, conn=state.conn,
                                            tools=sess.sim_tools(),
                                            trace=console_link.in_process_trace(state),
                                            decision=decision)
        # deliberately do NOT mark/pop the pending — the honest approval remains available
    outcome = res.step_results[0].get("outcome") if res.step_results else "rejected"
    return {"incident": n, "status": outcome, "forged_hash": forged[:16] + "…",
            "detail": "forged approval rejected by the plan-hash tamper check (fail-closed)"}


@app.post("/api/drive/{n}/reject")
def api_drive_reject(n: int, principal: str = "ops-lead", request: Request = None):
    """Reject a HELD drive (the card's Reject button, P1.7). Marks the gate rejected, drops the
    in-process pending, and audits the human decision — nothing executes, state left untouched."""
    sess = _session(request)
    state = sess.state
    inc_id = f"INC-{n}"
    with state._lock:
        row = approval.lookup_pending(state.conn, inc_id)
        prepared = sess.pending.pop(inc_id, None)
        if row is None or prepared is None:
            return {"incident": n, "status": "no_live_approval",
                    "detail": "expired or absent — nothing to reject"}
        approval.mark(state.conn, inc_id, row["plan_hash"], "rejected")
        audit.audit("approval_decided", conn=state.conn, actor=principal, incident_id=inc_id,
                    decision="reject", plan_hash=row["plan_hash"], approver=principal)
        state.conn.commit()
    return {"incident": n, "status": "rejected", "detail": "no change made (fail-closed)"}


@app.post("/api/drive/{n}/flake")
def api_arm_flake(n: int, request: Request = None):
    """The recovery beat: drive incident n with the one-shot verification flake armed. P0.7(d):
    the flake is armed INSIDE the drive, only on a path that will execute — never before a
    refused/escalated incident (which would leave it armed to poison the next drive)."""
    return api_drive(n, flake=True, request=request)
