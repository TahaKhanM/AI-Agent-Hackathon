"""PrecedentProtocol — the frozen loop contracts carried as uAgents messages.
[owner T1, task T1-8]

Spec: Idea/refinement/02-architecture-refinement.md §3.4.

The three network agents (Watcher -> Librarian -> Operator) exchange these
`uagents.Model` messages. They are JSON-friendly projections of the pydantic
contracts in precedent/contracts.py — only str/int/bool/list/dict/optional fields,
so they serialise cleanly over Agentverse without importing the whole contract
graph on the wire.

The two converters keep the deterministic loop authoritative: a PlanMsg is built
FROM a `Prepared` (produced by orchestrator.prepare) and rebuilt back INTO a
`Prepared` + optional `ApprovalDecision` on the Operator side, so the SAME
plan_hash flows Watcher -> Operator and commit_execution()'s tamper check still
bites. The Operator never re-plans; it executes exactly the hash it was handed.

RULE 1: no model id here. RULE 2: this module is pure data + pure converters — it
runs no LLM and makes no risk/permission decision (those already happened in
prepare()); it only reshapes typed data across the network boundary.
"""
from __future__ import annotations

from uagents import Model, Protocol

from precedent.contracts import (
    ApprovalDecision,
    ExecutionPlan,
    IncidentEvent,
    RiskAssessment,
    TypedToolCall,
)
from precedent.orchestrator import Prepared

# One protocol object every agent includes; the version pins the wire shape.
PRECEDENT_PROTOCOL = Protocol(name="precedent", version="1.0")


# --------------------------------------------------------------------------- #
# Wire messages (uagents.Model — JSON-friendly fields only)
# --------------------------------------------------------------------------- #
class IncidentMsg(Model):
    """Watcher's inbound incident (from the sim, a Jira poll, or a chat report)."""
    incident_id: str
    raw_text: str
    source: str
    observed_at: str
    structured: dict | None = None
    principal: str = "scheduling-ops"


class TriageMsg(Model):
    """Watcher -> Librarian: the deterministic triage result. `class_key` is None
    when the extractor could not confirm a class (nothing is retrievable then)."""
    incident_id: str
    class_key: str | None
    extraction_method: str
    principal: str


class RetrievalResultMsg(Model):
    """Librarian -> Watcher: the ACL-filtered retrieval verdict. RULE 3 — on a
    denial this carries ONLY the count and the owning team, never any content."""
    incident_id: str
    principal_id: str
    permitted: bool
    hit_count: int
    denied_count: int
    denied_owner_team: str | None = None


class PlanMsg(Model):
    """Watcher -> Operator: the fully-built execution plan + gate decision. Carries
    everything commit_execution() needs to run the plan without re-planning, so the
    plan_hash tamper check still holds end-to-end.

    `decision` is "standing" for the zero-LLM fast-path (no human approval needed),
    or "approve"/"reject" for a human chat decision. `approver_principal` is the
    authorising identity recorded in the audit log (the chat sender address)."""
    incident_id: str
    raw_text: str
    source: str
    observed_at: str
    plan_hash: str
    steps: list
    rollback_steps: list
    pre_state_snapshot_ref: str | None
    ref: dict
    pre_state: dict
    class_key: str
    fingerprint: str
    rule: dict
    risk_class: str
    policy_rule_id: str
    ladder_level: str
    decision: str
    approver_principal: str


class ResultMsg(Model):
    """Operator -> Watcher: the terminal execution outcome. `hop_trail` records the
    Watcher->Librarian->Operator path (for the chat footer); `audit_hash` is the
    tail of the hash-chained audit log after commit (provenance the human can cite)."""
    incident_id: str
    plan_hash: str
    verified: bool
    rolled_back: bool
    outcome: str
    audit_hash: str | None = None
    hop_trail: list


# --------------------------------------------------------------------------- #
# Pure converters — Prepared <-> PlanMsg (no I/O, no LLM, trivially testable)
# --------------------------------------------------------------------------- #
def _dump_calls(calls: list[TypedToolCall]) -> list[dict]:
    return [{"tool": c.tool, "args": c.args} for c in calls]


def _load_calls(rows: list) -> list[TypedToolCall]:
    return [TypedToolCall(tool=r["tool"], args=r["args"]) for r in rows]


def plan_msg_from_prepared(prepared: Prepared, decision_str: str, approver: str) -> PlanMsg:
    """Project a gate-ready `Prepared` (outcome 'ready' or 'fast_ready') into a
    PlanMsg for the Operator. `decision_str` is 'standing' (fast-path) or
    'approve'/'reject'; `approver` is the authorising principal (chat sender)."""
    plan: ExecutionPlan = prepared.plan
    assessment: RiskAssessment = prepared.assessment
    inc: IncidentEvent = prepared.incident
    return PlanMsg(
        incident_id=inc.incident_id,
        raw_text=inc.raw_text,
        source=inc.source,
        observed_at=inc.observed_at,
        plan_hash=plan.plan_hash,
        steps=_dump_calls(plan.steps),
        rollback_steps=_dump_calls(plan.rollback_steps),
        pre_state_snapshot_ref=plan.pre_state_snapshot_ref,
        ref=dict(prepared.ref or {}),
        pre_state=dict(prepared.pre_state or {}),
        class_key=prepared.class_key,
        fingerprint=prepared.fingerprint,
        rule=dict(prepared.rule or {}),
        risk_class=assessment.risk_class,
        policy_rule_id=assessment.policy_rule_id,
        ladder_level=assessment.ladder_level,
        decision=decision_str,
        approver_principal=approver,
    )


def prepared_from_plan_msg(msg: PlanMsg) -> tuple[Prepared, ApprovalDecision | None]:
    """Rebuild a `Prepared` (+ optional `ApprovalDecision`) from a PlanMsg on the
    Operator side. The reconstructed ExecutionPlan keeps the ORIGINAL plan_hash
    (not recomputed), so commit_execution()'s `decision.plan_hash == plan.plan_hash`
    tamper check still guards the network boundary.

    `decision` is None on the 'standing' fast-path (commit_execution needs none);
    otherwise it is an ApprovalDecision built VERBATIM from the message (approver
    principal = the chat sender address, channel='chat')."""
    incident = IncidentEvent(
        incident_id=msg.incident_id,
        raw_text=msg.raw_text,
        source=msg.source,   # 'sim' | 'jira' | 'chat'
        observed_at=msg.observed_at,
    )
    plan = ExecutionPlan(
        incident_id=msg.incident_id,
        steps=_load_calls(msg.steps),
        rollback_steps=_load_calls(msg.rollback_steps),
        pre_state_snapshot_ref=msg.pre_state_snapshot_ref,
        plan_hash=msg.plan_hash,   # preserved, not recomputed — tamper check anchor
    )
    assessment = RiskAssessment(
        incident_id=msg.incident_id,
        risk_class=msg.risk_class,
        policy_rule_id=msg.policy_rule_id,
        ladder_level=msg.ladder_level,
    )
    is_standing = msg.decision == "standing"
    prepared = Prepared(
        incident=incident,
        outcome="fast_ready" if is_standing else "ready",
        plan=plan,
        ref=dict(msg.ref or {}),
        pre_state=dict(msg.pre_state or {}),
        class_key=msg.class_key,
        fingerprint=msg.fingerprint,
        rule=dict(msg.rule or {}),
        assessment=assessment,
        fast=is_standing,
    )
    if is_standing:
        return prepared, None
    decision = ApprovalDecision(
        incident_id=msg.incident_id,
        plan_hash=msg.plan_hash,
        decision="approve" if msg.decision == "approve" else "reject",
        approver_principal=msg.approver_principal,
        channel="chat",
        decided_at="",
    )
    return prepared, decision
