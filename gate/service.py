"""The gate's decision logic — deterministic, fail-closed, ZERO LLM.

This module is the product spine's decision path. It reuses the EXISTING deterministic
components and adds NO new decision logic:

  propose  → orchestrator.prepare() (extractor/fingerprint → retrieve ACL → policy.assess →
             plan → ladder.is_standing), mapped to deny | needs-approval | allow-standing.
  outcome  → orchestrator.commit_execution() (execute-in-sim → verify → ladder →
             memorise/rollback), recording the verified/rolled_back result + audit rows.

RULE 2 (load-bearing, verified by tests/test_gate_api.py's no-LLM proof): this file imports
NO model backend and calls NO LLM. The decision is computed by policy + ladder; the model may
only produce PROSE elsewhere, never here. prepare() is invoked with defer_rationale=True and the
deferred SMART-prose step is never invoked, so the slow-path prose network call cannot fire
inside a decision. An unknown error_code is denied BEFORE prepare(), so the extractor's
LLM-proposal branch is unreachable from the gate.

RULE 3 (fail-closed): an expired or absent ref is a non-action with a fail-closed audit row and
NO execution. A proposal whose class has no documented inverse (action_type none / escalate) or
whose fix the principal cannot access (ACL-restricted) is denied.
"""
from __future__ import annotations

import secrets

from agents import approval
from gate.models import (
    DecisionStateResponse,
    OutcomeRequest,
    OutcomeResponse,
    ProposeRequest,
    ProposeResponse,
)
from gate.world import GateWorld, PendingEntry
from precedent import extractor, orchestrator
from precedent.contracts import ApprovalDecision, IncidentEvent
from precedent_memory import audit, db

# Mirror orchestrator._APPROVAL_TTL_S — the 10-minute hold both the demo server and the
# agents.approval ledger use. Defined here (not imported from a private name) so the gate's
# standing-path TTL is explicit and stable.
GATE_TTL_S = 600


# --------------------------------------------------------------------------- #
# small helpers
# --------------------------------------------------------------------------- #
def _new_ref() -> str:
    """An opaque, unguessable decision reference."""
    return secrets.token_urlsafe(18)


def _safe_code(code: str | None) -> str:
    """Cap + sanitise an attacker-supplied error_code before it enters the hash-chained audit
    payload on the deny path. An unknown error_code is caller-controlled; logging it raw risks
    log/payload injection and unbounded rows. Keep a sane charset (alnum + ``-_.``) and truncate
    to 64 chars so a garbage/over-long code is neutralised in the audit trail (fail-closed)."""
    kept = "".join(ch for ch in (code or "") if ch.isalnum() or ch in "-_.")
    return kept[:64]


def _expiry_iso() -> str:
    from datetime import timedelta

    return (db.utcnow() + timedelta(seconds=GATE_TTL_S)).isoformat()


def _is_past(iso: str | None) -> bool:
    """True when an ISO horizon has passed OR is unparseable (fail-closed)."""
    ts = db.parse_iso(iso or "")
    return ts is None or db.utcnow() >= ts


def _audit(world: GateWorld, event: str, actor: str | None, **payload) -> None:
    """Append a gate-level hash-chained audit row on the world's conn (caller holds the lock)."""
    audit.audit(event, conn=world.conn, actor=actor, **payload)
    world.conn.commit()


def _approval_row(world: GateWorld, incident_id: str, plan_hash: str):
    """The durable approval-ledger row for (incident, plan), regardless of status, or None."""
    approval.ensure_table(world.conn)
    return world.conn.execute(
        "SELECT incident_id, plan_hash, sender_address, requested_at, expires_at, status "
        "FROM approval WHERE incident_id = ? AND plan_hash = ?",
        (incident_id, plan_hash),
    ).fetchone()


# --------------------------------------------------------------------------- #
# propose_action
# --------------------------------------------------------------------------- #
def propose(world: GateWorld, req: ProposeRequest) -> ProposeResponse:
    """Run the deterministic pipeline and return the gate's verdict. No LLM on any path."""
    inc_id = req.incident_id
    structured = req.structured

    with world.lock:
        # (1) Out-of-band identity. An unregistered proposer is a non-action (fail-closed).
        if not world.registered(req.principal):
            _audit(world, "gate_denied", req.principal, incident_id=inc_id,
                   reason="unregistered_principal")
            return ProposeResponse(incident_id=inc_id, decision="deny",
                                   reason="unregistered_principal",
                                   rationale="principal not registered out-of-band")

        # (2) Deterministic class gate. An unknown code has no documented inverse and — crucially —
        #     never reaches the extractor's LLM-proposal branch (kept out of the decision path).
        if (structured.error_code or "").strip().upper() not in extractor.KNOWN_CODES:
            _audit(world, "gate_denied", req.principal, incident_id=inc_id,
                   reason="unknown_class", error_code=_safe_code(structured.error_code))
            return ProposeResponse(incident_id=inc_id, decision="deny", reason="unknown_class",
                                   rationale="error_code is not a known deterministic class")

        # (3) Build the incident + structured payload and run the REAL deterministic pipeline.
        incident = IncidentEvent(incident_id=inc_id, raw_text=req.raw_text, source=req.source,
                                 observed_at=req.observed_at or db.utcnow_iso())
        structured_payload = {
            "service": structured.service,
            "error_code": structured.error_code,
            "target_object_type": structured.target_object_type,
            "object_id": structured.object_id,
        }
        prepared = orchestrator.prepare(
            incident, structured=structured_payload, conn=world.conn, tools=world.tools,
            principal=req.principal, defer_rationale=True,   # RULE 2: no SMART prose in a decision
        )

        assessment = prepared.assessment
        rule = prepared.rule or {}
        risk_class = assessment.risk_class if assessment else None
        policy_rule_id = assessment.policy_rule_id if assessment else None
        ladder_level = assessment.ladder_level if assessment else None
        class_key = prepared.class_key
        rationale = (f"policy {policy_rule_id} → {risk_class}" if policy_rule_id else "")

        # (4) The caller cannot smuggle a different action past the gate: an intended_action that
        #     disagrees with the deterministically-selected policy action is a non-action.
        policy_action = rule.get("action_type")
        if (req.intended_action and prepared.outcome in ("ready", "fast_ready")
                and req.intended_action != policy_action):
            _audit(world, "gate_denied", req.principal, incident_id=inc_id,
                   reason="action_mismatch", intended=req.intended_action, policy=policy_action)
            return ProposeResponse(incident_id=inc_id, decision="deny", reason="action_mismatch",
                                   class_key=class_key, risk_class=risk_class,
                                   policy_rule_id=policy_rule_id, ladder_level=ladder_level,
                                   rationale="intended action ≠ documented policy action")

        # (5) Map the deterministic outcome to the gate verdict.
        if prepared.outcome == "fast_ready":          # Standing Approval → zero-LLM fast path
            ref = _new_ref()
            expires_at = _expiry_iso()
            world.refs[ref] = PendingEntry(
                ref=ref, kind="standing", incident_id=inc_id, plan_hash=prepared.plan.plan_hash,
                expires_at=expires_at, principal=req.principal, prepared=prepared,
                status="approved")
            _audit(world, "gate_allow_standing", req.principal, incident_id=inc_id,
                   plan_hash=prepared.plan.plan_hash, class_key=class_key, ref=ref)
            return ProposeResponse(incident_id=inc_id, decision="allow-standing", ref=ref,
                                   expires_at=expires_at, risk_class=risk_class,
                                   policy_rule_id=policy_rule_id, ladder_level=ladder_level,
                                   class_key=class_key, plan_hash=prepared.plan.plan_hash,
                                   rationale=rationale)

        if prepared.outcome == "ready":               # policy-permitted, non-standing → gate it
            areq = prepared.approval_request
            approval.record_pending(world.conn, areq, sender_address=req.principal)  # 10-min TTL
            ref = _new_ref()
            world.refs[ref] = PendingEntry(
                ref=ref, kind="approval", incident_id=inc_id, plan_hash=areq.plan_hash,
                expires_at=areq.expires_at, principal=req.principal, prepared=prepared,
                status="pending")
            _audit(world, "gate_needs_approval", req.principal, incident_id=inc_id,
                   plan_hash=areq.plan_hash, class_key=class_key, ref=ref)
            return ProposeResponse(incident_id=inc_id, decision="needs-approval", ref=ref,
                                   expires_at=areq.expires_at, risk_class=risk_class,
                                   policy_rule_id=policy_rule_id, ladder_level=ladder_level,
                                   class_key=class_key, plan_hash=areq.plan_hash,
                                   rationale=rationale)

        # refused (ACL-restricted) or escalated (no documented inverse) → deny.
        extra = (prepared.result.step_results[0] if prepared.result
                 and prepared.result.step_results else {})
        reason = "restricted" if prepared.outcome == "refused" else "no_documented_inverse"
        _audit(world, "gate_denied", req.principal, incident_id=inc_id, reason=reason,
               outcome=prepared.outcome)
        return ProposeResponse(incident_id=inc_id, decision="deny", reason=reason,
                               class_key=class_key, risk_class=risk_class,
                               policy_rule_id=policy_rule_id, ladder_level=ladder_level,
                               rationale=f"{prepared.outcome}: {extra.get('reason', reason)}")


# --------------------------------------------------------------------------- #
# get_decision
# --------------------------------------------------------------------------- #
def get_decision(world: GateWorld, ref: str) -> DecisionStateResponse:
    """Current state of a held decision. Expired/absent ⇒ non-action + a fail-closed audit row."""
    with world.lock:
        entry = world.refs.get(ref)
        if entry is None:
            _audit(world, "gate_ref_absent", None, ref=ref)
            return DecisionStateResponse(ref=ref, status="expired",
                                         detail="absent ref — non-action (fail-closed)")

        # Terminal already? Report it (unless the horizon also passed — then it reads expired).
        if entry.status in ("approved", "denied") and entry.prepared is None:
            if _is_past(entry.expires_at):
                return DecisionStateResponse(ref=ref, status="expired",
                                             incident_id=entry.incident_id,
                                             plan_hash=entry.plan_hash,
                                             expires_at=entry.expires_at,
                                             detail="decided, horizon passed")
            return DecisionStateResponse(ref=ref, status=entry.status,
                                         incident_id=entry.incident_id, plan_hash=entry.plan_hash,
                                         expires_at=entry.expires_at, detail="decided")

        # Live ref: the fail-closed TTL check. For a needs-approval ref the durable ledger is the
        # authority (agents.approval.is_expired); the in-process horizon is the belt-and-braces.
        expired = _is_past(entry.expires_at)
        if not expired and entry.kind == "approval":
            row = _approval_row(world, entry.incident_id, entry.plan_hash)
            expired = row is None or approval.is_expired(row)
        if expired:
            entry.status = "expired"
            entry.prepared = None
            if entry.kind == "approval":
                approval.mark(world.conn, entry.incident_id, entry.plan_hash, "expired")
            _audit(world, "gate_expired_nonaction", entry.principal,
                   incident_id=entry.incident_id, plan_hash=entry.plan_hash, ref=ref)
            return DecisionStateResponse(ref=ref, status="expired", incident_id=entry.incident_id,
                                         plan_hash=entry.plan_hash, expires_at=entry.expires_at,
                                         detail="past TTL — non-action (fail-closed)")

        # Standing ⇒ pre-approved and actionable; needs-approval ⇒ still pending a human.
        status = "approved" if entry.kind == "standing" else "pending"
        return DecisionStateResponse(ref=ref, status=status, incident_id=entry.incident_id,
                                     plan_hash=entry.plan_hash, expires_at=entry.expires_at,
                                     detail=("standing (pre-approved)" if entry.kind == "standing"
                                             else "awaiting approval"))


# --------------------------------------------------------------------------- #
# report_outcome
# --------------------------------------------------------------------------- #
def report_outcome(world: GateWorld, req: OutcomeRequest) -> OutcomeResponse:
    """Approve (or reject) a held ref, execute-in-sim, and record the verified/rolled_back
    outcome via commit_execution + ladder. Expired/absent ⇒ non-action, NO execution."""
    ref = req.ref
    with world.lock:
        entry = world.refs.get(ref)
        if entry is None:
            _audit(world, "gate_ref_absent", req.approver_principal, ref=ref)
            return OutcomeResponse(ref=ref, outcome="absent", executed=False,
                                   detail="absent ref — non-action (fail-closed)")

        if entry.prepared is None:                    # already consumed — never replay
            return OutcomeResponse(ref=ref, incident_id=entry.incident_id, outcome=entry.status,
                                   executed=False, plan_hash=entry.plan_hash,
                                   detail="already decided — non-action")

        # Fail-closed TTL BEFORE any execution.
        expired = _is_past(entry.expires_at)
        if not expired and entry.kind == "approval":
            row = _approval_row(world, entry.incident_id, entry.plan_hash)
            expired = row is None or approval.is_expired(row)
        if expired:
            entry.status = "expired"
            entry.prepared = None
            if entry.kind == "approval":
                approval.mark(world.conn, entry.incident_id, entry.plan_hash, "expired")
            _audit(world, "gate_expired_nonaction", entry.principal,
                   incident_id=entry.incident_id, plan_hash=entry.plan_hash, ref=ref)
            return OutcomeResponse(ref=ref, incident_id=entry.incident_id, outcome="expired",
                                   executed=False, plan_hash=entry.plan_hash,
                                   detail="past TTL — non-action (fail-closed)")

        # Bind execution to the DURABLE (incident_id, plan_hash) ledger — NOT this per-ref
        # Prepared. Two propose() calls for the same (incident, plan) mint two refs; without this
        # guard, approving+outcoming BOTH would execute the plan TWICE. If the durable ledger for
        # this (incident, plan) is already non-'pending' (approved/rejected/expired), this outcome
        # is an ALREADY-DECIDED replay → non-action, returning the prior outcome + an audit row.
        if entry.kind == "approval":
            row = _approval_row(world, entry.incident_id, entry.plan_hash)
            prior = row["status"] if row is not None else None
            if prior is not None and prior != "pending":
                entry.status = ("approved" if prior == "approved"
                                else "expired" if prior == "expired" else "denied")
                entry.prepared = None
                _audit(world, "gate_already_decided", req.approver_principal,
                       incident_id=entry.incident_id, plan_hash=entry.plan_hash,
                       prior=prior, ref=ref)
                return OutcomeResponse(ref=ref, incident_id=entry.incident_id, outcome=prior,
                                       executed=False, plan_hash=entry.plan_hash,
                                       detail="already decided (durable ledger) — non-action")

        # Resolve the human decision for a needs-approval ref. Standing needs none.
        decision: ApprovalDecision | None = None
        actor = entry.principal
        if entry.kind == "approval":
            approver = req.approver_principal
            # SEPARATION OF DUTIES (four-eyes): the PROPOSER may never approve its own proposal.
            # A self-approval is a non-action + a dedicated audit row (self-rejection is fine — it
            # is a withdrawal, not a four-eyes breach — so this only guards decision == approve).
            if req.decision == "approve" and approver is not None and approver == entry.principal:
                entry.status = "denied"
                entry.prepared = None
                approval.mark(world.conn, entry.incident_id, entry.plan_hash, "rejected")
                _audit(world, "gate_self_approval_rejected", approver,
                       incident_id=entry.incident_id, plan_hash=entry.plan_hash, ref=ref)
                return OutcomeResponse(ref=ref, incident_id=entry.incident_id,
                                       outcome="self_approval_rejected", executed=False,
                                       plan_hash=entry.plan_hash,
                                       detail="four-eyes: proposer cannot approve own proposal")
            if req.decision != "approve" or not world.registered(approver):
                entry.status = "denied"
                entry.prepared = None
                approval.mark(world.conn, entry.incident_id, entry.plan_hash, "rejected")
                reason = ("rejected" if req.decision != "approve" else "unregistered_approver")
                _audit(world, "gate_outcome_rejected", approver, incident_id=entry.incident_id,
                       plan_hash=entry.plan_hash, reason=reason, ref=ref)
                return OutcomeResponse(ref=ref, incident_id=entry.incident_id, outcome="rejected",
                                       executed=False, plan_hash=entry.plan_hash,
                                       detail=f"no change made ({reason}) — fail-closed")
            actor = approver
            decision = ApprovalDecision(
                incident_id=entry.incident_id, plan_hash=entry.plan_hash, decision="approve",
                approver_principal=approver, channel="console", decided_at=db.utcnow_iso())

        # EXECUTE-IN-SIM: commit_execution runs the typed calls, verifies, rolls back on failure,
        # advances/demotes the ladder, memorises on success, and writes every audit row. The
        # plan-hash tamper check inside binds the approved hash to the plan we run.
        res = orchestrator.commit_execution(entry.prepared, conn=world.conn, tools=world.tools,
                                             decision=decision, actor=actor)
        if entry.kind == "approval":
            approval.mark(world.conn, entry.incident_id, entry.plan_hash, "approved")

        outcome = res.step_results[0].get("outcome") if res.step_results else "unknown"
        entry.status = "approved" if outcome != "rejected" else "denied"
        entry.prepared = None                         # consumed — no replay
        _audit(world, "gate_outcome_recorded", actor, incident_id=entry.incident_id,
               plan_hash=entry.plan_hash, outcome=outcome, verified=res.verified,
               rolled_back=res.rolled_back, ref=ref)
        return OutcomeResponse(ref=ref, incident_id=entry.incident_id, outcome=outcome,
                               executed=(outcome not in ("rejected",)), verified=res.verified,
                               rolled_back=res.rolled_back, plan_hash=entry.plan_hash,
                               detail="executed-in-sim; outcome recorded")
