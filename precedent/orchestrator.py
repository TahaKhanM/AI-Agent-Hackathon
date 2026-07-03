"""The closed loop.  [owner T1, task T1-10]

Spec: Idea/refinement/02-architecture-refinement.md §3.

DETECT -> TRIAGE -> RETRIEVE (ACL-filtered) -> RISK-CLASSIFY (deterministic) -> GATE
-> EXECUTE (typed tools) -> VERIFY (auto-rollback on failure) -> MEMORISE.

Split into prepare() (up to the gate) + commit_execution() (execute/verify/memorise) so the
same loop drives BOTH the synchronous console path (handle()) and the async Fetch/ASI:One
chat-approval path (Watcher: prepare -> send ApprovalRequest -> resume on the human reply).

Owns the shared memory `conn` and threads it through retrieve/store/audit/ladder. Enforces
the plan_hash tamper check (the SAME hash flows IncidentEvent -> ExecutionPlan ->
ApprovalRequest -> ApprovalDecision -> ExecutionResult) and rollback ordering (capture the
full pre-state snapshot BEFORE any typed call; verify AFTER; on failure restore the snapshot
THEN demote; a FAILED rollback escalates with the snapshot — never swallowed).

RULE 2: the STANDING fast-path makes ZERO venice.chat/venice.embed calls; slow-path LLM
calls (SMART rationale prose) only PROPOSE. RULE 3: denials surface count+owner only.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from precedent import extractor, ladder, policy
from precedent.contracts import (
    ApprovalDecision,
    ApprovalRequest,
    ExecutionPlan,
    ExecutionResult,
    Extracted,
    IncidentEvent,
    MemoryWrite,
    RiskAssessment,
    TriageResult,
    TypedToolCall,
)
from precedent_memory import audit, db, retrieve, store

_APPROVAL_TTL_S = 600


def _noop_trace(step: str, detail: str = "", incident_id: str | None = None) -> None:
    pass


@dataclass
class Prepared:
    """Everything the gate + executor need, carried across the async approval boundary."""
    incident: IncidentEvent
    outcome: str                                   # refused|escalated|ready|fast_ready
    result: ExecutionResult | None = None          # terminal result for refused/escalated
    plan: ExecutionPlan | None = None
    ref: dict | None = None
    pre_state: dict = field(default_factory=dict)
    class_key: str | None = None
    fingerprint: str | None = None
    rule: dict | None = None
    assessment: RiskAssessment | None = None
    approval_request: ApprovalRequest | None = None
    fast: bool = False


def _plan_hash(incident_id: str, object_ref: dict, steps: list[TypedToolCall],
               rollback: list[TypedToolCall]) -> str:
    material = json.dumps({
        "incident_id": incident_id, "object_ref": object_ref,
        "steps": [(s.tool, s.args) for s in steps],
        "rollback": [(s.tool, s.args) for s in rollback],
    }, sort_keys=True)
    return hashlib.sha256(material.encode()).hexdigest()


def _object_ref(extracted: Extracted, structured: dict | None) -> dict | None:
    oid = (structured or {}).get("object_id")
    if oid is None:
        return None
    return {"service": extracted.service, "object_type": extracted.target_object_type,
            "object_id": oid}


def _result(incident: IncidentEvent, plan_hash: str, *, outcome: str, verified: bool = False,
            rolled_back: bool = False, extra: dict | None = None) -> ExecutionResult:
    return ExecutionResult(
        incident_id=incident.incident_id, plan_hash=plan_hash,
        step_results=[{"outcome": outcome, **(extra or {})}], verified=verified,
        rolled_back=rolled_back)


def _emitter(incident, conn, trace, actor):
    def emit(step, detail="", **kw):
        trace(step, detail, incident.incident_id)
        audit.audit(step, conn=conn, actor=actor, incident_id=incident.incident_id, **kw)
        conn.commit()
    return emit


# --------------------------------------------------------------------------- #
# prepare()  — detect -> triage -> retrieve -> assess -> build plan (up to the gate)
# --------------------------------------------------------------------------- #
def prepare(incident: IncidentEvent, *, structured: dict | None = None, conn=None, tools=None,
            principal: str = "scheduling-ops", trace=None, mode: str = "live",
            actor: str | None = None) -> Prepared:
    if conn is None or tools is None:
        raise ValueError("prepare requires the shared conn and a SimTools client")
    trace = trace or _noop_trace
    actor = actor or principal
    emit = _emitter(incident, conn, trace, actor)

    emit("detected", f"{incident.source} incident {incident.incident_id}")

    extracted, method = extractor.extract(incident.raw_text, structured)
    class_key = extractor.class_key_of(extracted) if extracted else None
    triage = TriageResult(incident_id=incident.incident_id, extracted=extracted,
                          extraction_method=method, candidate_class_key=class_key)
    emit("triage", f"method={method} class={class_key or 'unresolved'}", method=method,
         class_key=class_key)
    if extracted is None:
        return Prepared(incident, "escalated",
                        result=_result(incident, "", outcome="escalated",
                                       extra={"reason": "no_class"}))

    bundle = retrieve.retrieve(principal, {"incident_id": incident.incident_id,
                                           "class_key": class_key}, mode, conn=conn, actor=actor)
    trace("retrieval_check", f"{len(bundle.hits)} permitted, {bundle.denied_count} denied",
          incident.incident_id)
    if not bundle.hits:
        emit("refused", f"restricted — {bundle.denied_count} remediation hidden; owner: "
             f"{bundle.denied_owner_team or 'restricted team'}",
             denied_count=bundle.denied_count, denied_owner_team=bundle.denied_owner_team)
        return Prepared(incident, "refused",
                        result=_result(incident, "", outcome="refused",
                                       extra={"denied_count": bundle.denied_count,
                                              "denied_owner_team": bundle.denied_owner_team}))

    assessment = policy.assess(triage)
    rule = policy.rule_for(class_key)
    emit("risk_assessed", f"{assessment.risk_class} rule={assessment.policy_rule_id} "
         f"level={assessment.ladder_level}", risk_class=assessment.risk_class,
         policy_rule_id=assessment.policy_rule_id, ladder_level=assessment.ladder_level)
    if assessment.risk_class == "escalate" or rule.get("action_type") in (None, "none"):
        emit("escalated", "no safe automated fix — routing to human (ladder floor)")
        return Prepared(incident, "escalated",
                        result=_result(incident, "", outcome="escalated",
                                       extra={"policy_rule_id": assessment.policy_rule_id}))

    ref = _object_ref(extracted, structured)
    if ref is None:
        emit("escalated", "no execution target object — L0")
        return Prepared(incident, "escalated",
                        result=_result(incident, "", outcome="escalated",
                                       extra={"reason": "no_object"}))

    snap = tools.snapshot(ref["service"], ref["object_type"], ref["object_id"])
    pre_state = snap.get("fields", {})
    steps = [TypedToolCall(tool=rule["action_type"],
                           args={_id_arg(ref["object_type"]): ref["object_id"]})]
    rollback = [TypedToolCall(tool="restore", args={**ref, "snapshot": pre_state})]
    plan_hash = _plan_hash(incident.incident_id, ref, steps, rollback)
    plan = ExecutionPlan(incident_id=incident.incident_id, steps=steps, rollback_steps=rollback,
                         pre_state_snapshot_ref=f"snapshot:{incident.incident_id}:{plan_hash[:12]}",
                         plan_hash=plan_hash)

    fast = (method == "deterministic" and ladder.is_standing(class_key, conn=conn)
            and assessment.risk_class not in ("restricted_change", "escalate"))
    fingerprint = extractor.fingerprint(extracted)

    if fast:
        return Prepared(incident, "fast_ready", plan=plan, ref=ref, pre_state=pre_state,
                        class_key=class_key, fingerprint=fingerprint, rule=rule,
                        assessment=assessment, fast=True)

    # slow-path: SMART writes rationale PROSE only (rule 2), then request approval.
    assessment.rationale_text = _smart_rationale(assessment) or assessment.rationale_text
    req = ApprovalRequest(incident_id=incident.incident_id, plan_hash=plan_hash,
                          risk_class=assessment.risk_class, ladder_level=assessment.ladder_level,
                          requested_at=db.utcnow_iso(), expires_at=_expiry_iso(), channel="console")
    emit("approval_requested", f"awaiting approval for {assessment.policy_rule_id}",
         plan_hash=plan_hash, risk_class=assessment.risk_class)
    return Prepared(incident, "ready", plan=plan, ref=ref, pre_state=pre_state,
                    class_key=class_key, fingerprint=fingerprint, rule=rule,
                    assessment=assessment, approval_request=req, fast=False)


# --------------------------------------------------------------------------- #
# commit_execution()  — verify decision -> execute -> verify -> memorise / rollback
# --------------------------------------------------------------------------- #
def commit_execution(prepared: Prepared, *, conn, tools, trace=None,
                     actor: str | None = None, decision: ApprovalDecision | None = None,
                     principal: str = "scheduling-ops") -> ExecutionResult:
    trace = trace or _noop_trace
    actor = actor or principal
    inc = prepared.incident
    plan = prepared.plan
    emit = _emitter(inc, conn, trace, actor)

    if prepared.fast:
        emit("approval_decided", "standing approval (pre-approved standard change) — "
             "fast-path, zero LLM; ~15s", decision="standing", plan_hash=plan.plan_hash)
    else:
        # tamper check: the approved hash MUST equal the plan we are about to run.
        ok = decision is not None and decision.decision == "approve" \
            and decision.plan_hash == plan.plan_hash
        if not ok:
            who = decision.approver_principal if decision else "system:no-approver"
            verdict = decision.decision if decision else "reject"
            emit("approval_decided", f"rejected/tampered by {who}", decision=verdict,
                 plan_hash=decision.plan_hash if decision else "", approver=who)
            return _result(inc, plan.plan_hash, outcome="rejected", extra={"decision": verdict})
        emit("approval_decided", f"approved by {decision.approver_principal}",
             decision="approve", approver=decision.approver_principal, plan_hash=plan.plan_hash)

    # EXECUTE typed calls (snapshot already captured in prepare() — rollback ordering holds).
    for step in plan.steps:
        tools.execute(step.tool, step.args)
    emit("executed", f"{plan.steps[0].tool} on {prepared.ref['object_type']} "
         f"{prepared.ref['object_id']}", plan_hash=plan.plan_hash)

    ref = prepared.ref
    verdict = tools.verify(ref["service"], ref["object_type"], ref["object_id"])
    if verdict.get("verified"):
        emit("verified", "post-state healthy", plan_hash=plan.plan_hash)
        ladder.on_verification_result(prepared.class_key, True, False, conn=conn, actor=actor,
                                      target_ref=str(ref["object_id"]), source=inc.source)
        _memorise(inc, ref, prepared.class_key, prepared.fingerprint, prepared.rule,
                  prepared.assessment, conn=conn, actor=actor)
        emit("memory_stored", "executed-fix-with-provenance recorded", class_key=prepared.class_key)
        return _result(inc, plan.plan_hash, outcome="resolved", verified=True)

    # VERIFY FAILED -> restore snapshot FIRST, THEN demote.
    restored = tools.restore(ref["service"], ref["object_type"], ref["object_id"],
                             prepared.pre_state)
    if not restored.get("ok"):
        emit("escalated", "ROLLBACK FAILED — escalating with pre-state snapshot attached",
             plan_hash=plan.plan_hash, snapshot_ref=plan.pre_state_snapshot_ref)
        return _result(inc, plan.plan_hash, outcome="rollback_failed",
                       extra={"snapshot_ref": plan.pre_state_snapshot_ref})
    emit("rolled_back", "verification failed — pre-state snapshot restored",
         plan_hash=plan.plan_hash)
    ladder.on_verification_result(prepared.class_key, False, True, conn=conn, actor=actor,
                                  target_ref=str(ref["object_id"]), source=inc.source)
    trace("class_demoted", f"{prepared.class_key} -> L1 (verification failure)", inc.incident_id)
    return _result(inc, plan.plan_hash, outcome="rolled_back", rolled_back=True)


# --------------------------------------------------------------------------- #
# handle()  — the synchronous composition (console path)
# --------------------------------------------------------------------------- #
def handle(incident: IncidentEvent, *, structured: dict | None = None, conn=None, tools=None,
           principal: str = "scheduling-ops", approve=None, trace=None, mode: str = "live",
           actor: str | None = None) -> ExecutionResult:
    prepared = prepare(incident, structured=structured, conn=conn, tools=tools,
                       principal=principal, trace=trace, mode=mode, actor=actor)
    if prepared.outcome in ("refused", "escalated"):
        return prepared.result
    decision = None
    if not prepared.fast:
        decision = (approve(prepared.approval_request) if approve
                    else _rejected(prepared.approval_request, actor or principal))
    return commit_execution(prepared, conn=conn, tools=tools, trace=trace, actor=actor,
                            decision=decision, principal=principal)


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _memorise(incident, ref, class_key, fingerprint, rule, assessment, *, conn, actor) -> int:
    body = {
        "symptom": incident.raw_text[:280],
        "fix": f"{rule['policy_rule_id']}: {rule['action_type']} on {ref['object_type']}",
        "approver": actor, "risk_class": assessment.risk_class,
        "rollback": "restore pre-state snapshot", "outcome": "verified",
    }
    mw = MemoryWrite(
        record={"kind": "executed_fix", "class_key": class_key, "fingerprint": fingerprint,
                "body": body},
        lineage_source_refs=list(rule.get("lineage_refs") or []), class_key=class_key)
    return store.store_memory_write(mw, principal_ctx={"principal": actor}, conn=conn)


def _smart_rationale(assessment) -> str:
    """LLM-assisted PROSE for the approval card — proposes narrative only, never the
    decision. Lazy import so a missing model never breaks import; canned on any outage."""
    from precedent import venice
    out = venice.chat("SMART", [{"role": "user", "content":
        f"In one sentence, explain the documented fix plan for policy rule "
        f"{assessment.policy_rule_id} (risk class {assessment.risk_class}). "
        "Do not change the risk class or approval level."}], max_tokens=256)
    return out if isinstance(out, str) and out != venice.CANNED_FALLBACK else ""


def _id_arg(object_type: str) -> str:
    return {"schedule_item": "schedule_slot_id", "vod_item": "vod_item_id"}.get(
        object_type, f"{object_type}_id")


def _expiry_iso() -> str:
    from datetime import timedelta
    return (db.utcnow() + timedelta(seconds=_APPROVAL_TTL_S)).isoformat()


def _rejected(req: ApprovalRequest, actor: str) -> ApprovalDecision:
    return ApprovalDecision(incident_id=req.incident_id, plan_hash=req.plan_hash,
                            decision="reject", approver_principal="system:no-approver",
                            channel="console", decided_at=db.utcnow_iso())
