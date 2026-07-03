"""The closed loop.  [owner T1, task T1-10]

Spec: Idea/refinement/02-architecture-refinement.md §3.

DETECT -> TRIAGE -> RETRIEVE (ACL-filtered) -> RISK-CLASSIFY (deterministic) -> GATE
-> EXECUTE (typed tools) -> VERIFY (auto-rollback on failure) -> MEMORISE.

Owns the shared memory `conn` and threads it through retrieve/store/audit/ladder in one
process. Enforces the plan_hash tamper check (the SAME hash flows
IncidentEvent -> ExecutionPlan -> ApprovalRequest -> ApprovalDecision -> ExecutionResult;
the approved hash must equal the executed plan) and rollback ordering (capture the full
pre-state snapshot BEFORE any typed call; verify AFTER; on failure restore the snapshot,
THEN demote; a FAILED rollback escalates with the snapshot — never swallowed).

RULE 2: the STANDING fast-path makes ZERO venice.chat/venice.embed calls. The slow-path
LLM calls (SMART rationale prose) only PROPOSE — never set risk_class or ladder_level.
RULE 3: retrieval denials surface only denied_count + denied_owner_team.
"""
from __future__ import annotations

import hashlib
import json

from precedent import extractor, ladder, policy
from precedent.contracts import (
    ApprovalDecision,
    ApprovalRequest,
    ExecutionPlan,
    ExecutionResult,
    Extracted,
    IncidentEvent,
    MemoryWrite,
    TriageResult,
    TypedToolCall,
)
from precedent_memory import audit, db, retrieve, store

_APPROVAL_TTL_S = 600


def _noop_trace(step: str, detail: str = "", incident_id: str | None = None) -> None:
    pass


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
            rolled_back: bool = False, extra: dict | None = None,
            steps: list | None = None) -> ExecutionResult:
    payload = {"outcome": outcome, **(extra or {})}
    return ExecutionResult(
        incident_id=incident.incident_id, plan_hash=plan_hash,
        step_results=[payload, *(steps or [])], verified=verified, rolled_back=rolled_back)


def handle(incident: IncidentEvent, *, structured: dict | None = None, conn=None, tools=None,
           principal: str = "scheduling-ops", approve=None, trace=None, mode: str = "live",
           actor: str | None = None) -> ExecutionResult:
    """Run the loop for one incident. `conn` = shared memory db; `tools` = SimTools;
    `approve(ApprovalRequest)->ApprovalDecision` gates the slow path (default: fail-closed
    reject); `trace(step, detail, incident_id)` streams to the console."""
    if conn is None:
        raise ValueError("orchestrator.handle requires the shared memory conn")
    if tools is None:
        raise ValueError("orchestrator.handle requires a SimTools client")
    trace = trace or _noop_trace
    actor = actor or principal

    def emit(step, detail="", **kw):
        trace(step, detail, incident.incident_id)
        audit.audit(step, conn=conn, actor=actor, incident_id=incident.incident_id, **kw)
        conn.commit()

    emit("detected", f"{incident.source} incident {incident.incident_id}")

    # ---- TRIAGE (deterministic first; LLM may only propose) -------------------------- #
    extracted, method = extractor.extract(incident.raw_text, structured)
    class_key = extractor.class_key_of(extracted) if extracted else None
    triage = TriageResult(incident_id=incident.incident_id, extracted=extracted,
                          extraction_method=method, candidate_class_key=class_key)
    emit("triage", f"method={method} class={class_key or 'unresolved'}", method=method,
         class_key=class_key)

    if extracted is None:
        emit("escalated", "extraction not resolvable — human classification required")
        return _result(incident, "", outcome="escalated", extra={"reason": "no_class"})

    # ---- RETRIEVE (ACL-enforced; fail-closed; denials disclose count+owner only) ----- #
    bundle = retrieve.retrieve(principal, {"incident_id": incident.incident_id,
                                           "class_key": class_key},
                               mode, conn=conn, actor=actor)
    trace("retrieval_check", f"{len(bundle.hits)} permitted, {bundle.denied_count} denied",
          incident.incident_id)
    if not bundle.hits:
        emit("refused", f"restricted — {bundle.denied_count} remediation hidden; owner: "
             f"{bundle.denied_owner_team or 'restricted team'}",
             denied_count=bundle.denied_count, denied_owner_team=bundle.denied_owner_team)
        return _result(incident, "", outcome="refused",
                       extra={"denied_count": bundle.denied_count,
                              "denied_owner_team": bundle.denied_owner_team})

    # ---- RISK ASSESS (deterministic YAML gate) --------------------------------------- #
    assessment = policy.assess(triage)
    rule = policy.rule_for(class_key)
    emit("risk_assessed", f"{assessment.risk_class} rule={assessment.policy_rule_id} "
         f"level={assessment.ladder_level}", risk_class=assessment.risk_class,
         policy_rule_id=assessment.policy_rule_id, ladder_level=assessment.ladder_level)

    if assessment.risk_class == "escalate" or rule.get("action_type") in (None, "none"):
        emit("escalated", "no safe automated fix — routing to human (ladder floor)")
        return _result(incident, "", outcome="escalated",
                       extra={"policy_rule_id": assessment.policy_rule_id})

    ref = _object_ref(extracted, structured)
    if ref is None:
        emit("escalated", "no execution target object — L0")
        return _result(incident, "", outcome="escalated", extra={"reason": "no_object"})

    # ---- BUILD PLAN + capture pre-state snapshot BEFORE any typed call ---------------- #
    snap = tools.snapshot(ref["service"], ref["object_type"], ref["object_id"])
    pre_state = snap.get("fields", {})
    steps = [TypedToolCall(tool=rule["action_type"],
                           args={_id_arg(ref["object_type"]): ref["object_id"]})]
    rollback = [TypedToolCall(tool="restore", args={**ref, "snapshot": pre_state})]
    plan_hash = _plan_hash(incident.incident_id, ref, steps, rollback)
    snapshot_ref = f"snapshot:{incident.incident_id}:{plan_hash[:12]}"
    plan = ExecutionPlan(incident_id=incident.incident_id, steps=steps, rollback_steps=rollback,
                         pre_state_snapshot_ref=snapshot_ref, plan_hash=plan_hash)

    # ---- GATE: STANDING fast-path (zero LLM) vs slow-path approval -------------------- #
    fast = (method == "deterministic"
            and ladder.is_standing(class_key, conn=conn)
            and assessment.risk_class not in ("restricted_change", "escalate"))

    if fast:
        emit("approval_decided", "standing approval (pre-approved standard change) — "
             "fast-path, zero LLM; ~15s", decision="standing", plan_hash=plan_hash)
    else:
        # SLOW-PATH is LLM-ASSISTED: SMART writes rationale PROSE only (rule 2 — it can
        # touch neither risk_class nor ladder_level). Skipped on the fast-path so the
        # STANDING branch stays provably zero-LLM. Airplane-safe (canned fallback).
        assessment.rationale_text = _smart_rationale(assessment) or assessment.rationale_text
        req = ApprovalRequest(incident_id=incident.incident_id, plan_hash=plan_hash,
                              risk_class=assessment.risk_class,
                              ladder_level=assessment.ladder_level,
                              requested_at=db.utcnow_iso(),
                              expires_at=_expiry_iso(), channel="console")
        emit("approval_requested", f"awaiting approval for {assessment.policy_rule_id}",
             plan_hash=plan_hash, risk_class=assessment.risk_class)
        decision = approve(req) if approve else _rejected(req, actor)
        # tamper check: the approved hash MUST equal the plan we are about to run.
        if decision.decision != "approve" or decision.plan_hash != plan_hash:
            emit("approval_decided", f"rejected/tampered by {decision.approver_principal}",
                 decision=decision.decision, plan_hash=decision.plan_hash,
                 approver=decision.approver_principal)
            return _result(incident, plan_hash, outcome="rejected",
                           extra={"decision": decision.decision})
        emit("approval_decided", f"approved by {decision.approver_principal}",
             decision="approve", approver=decision.approver_principal, plan_hash=plan_hash)

    fingerprint = extractor.fingerprint(extracted)
    return _execute_verify_memorise(incident, plan, ref, pre_state, class_key, fingerprint,
                                    rule, assessment, conn=conn, tools=tools, emit=emit,
                                    trace=trace, actor=actor)


def _execute_verify_memorise(incident, plan, ref, pre_state, class_key, fingerprint, rule,
                             assessment, *, conn, tools, emit, trace, actor) -> ExecutionResult:
    # EXECUTE typed calls (snapshot already captured — rollback ordering guaranteed).
    for step in plan.steps:
        tools.execute(step.tool, step.args)
    emit("executed", f"{plan.steps[0].tool} on {ref['object_type']} {ref['object_id']}",
         plan_hash=plan.plan_hash)

    verdict = tools.verify(ref["service"], ref["object_type"], ref["object_id"])
    if verdict.get("verified"):
        emit("verified", "post-state healthy", plan_hash=plan.plan_hash)
        ladder.on_verification_result(class_key, True, False, conn=conn, actor=actor,
                                      target_ref=str(ref["object_id"]), source=incident.source)
        _memorise(incident, ref, class_key, fingerprint, rule, assessment, conn=conn, actor=actor)
        emit("memory_stored", "executed-fix-with-provenance recorded", class_key=class_key)
        return _result(incident, plan.plan_hash, outcome="resolved", verified=True)

    # VERIFY FAILED -> restore snapshot FIRST, THEN demote.
    restored = tools.restore(ref["service"], ref["object_type"], ref["object_id"], pre_state)
    if not restored.get("ok"):
        # A failed rollback is never swallowed: escalate with the snapshot attached.
        emit("escalated", "ROLLBACK FAILED — escalating with pre-state snapshot attached",
             plan_hash=plan.plan_hash, snapshot_ref=plan.pre_state_snapshot_ref)
        return _result(incident, plan.plan_hash, outcome="rollback_failed", rolled_back=False,
                       extra={"snapshot_ref": plan.pre_state_snapshot_ref})
    emit("rolled_back", "verification failed — pre-state snapshot restored",
         plan_hash=plan.plan_hash)
    ladder.on_verification_result(class_key, False, True, conn=conn, actor=actor,
                                  target_ref=str(ref["object_id"]), source=incident.source)
    trace("class_demoted", f"{class_key} -> L1 (verification failure)", incident.incident_id)
    return _result(incident, plan.plan_hash, outcome="rolled_back", verified=False,
                   rolled_back=True)


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
        lineage_source_refs=list(rule.get("lineage_refs") or []),
        class_key=class_key)
    return store.store_memory_write(mw, principal_ctx={"principal": actor}, conn=conn)


def _id_arg(object_type: str) -> str:
    """The sim's execute tools take a typed id arg named for the object."""
    return {"schedule_item": "schedule_slot_id", "vod_item": "vod_item_id"}.get(
        object_type, f"{object_type}_id")


def _expiry_iso() -> str:
    from datetime import timedelta
    return (db.utcnow() + timedelta(seconds=_APPROVAL_TTL_S)).isoformat()


def _smart_rationale(assessment) -> str:
    """LLM-assisted PROSE for the approval card — proposes narrative only, never the
    decision. Lazy import so a missing model never breaks import; canned on any outage."""
    from precedent import venice
    out = venice.chat("SMART", [{"role": "user", "content":
        f"In one sentence, explain the documented fix plan for policy rule "
        f"{assessment.policy_rule_id} (risk class {assessment.risk_class}). "
        "Do not change the risk class or approval level."}], max_tokens=256)
    return out if isinstance(out, str) and out != venice.CANNED_FALLBACK else ""


def _rejected(req: ApprovalRequest, actor: str) -> ApprovalDecision:
    """Fail-closed default when no approver is wired: reject (never auto-approve)."""
    return ApprovalDecision(incident_id=req.incident_id, plan_hash=req.plan_hash,
                            decision="reject", approver_principal="system:no-approver",
                            channel="console", decided_at=db.utcnow_iso())
