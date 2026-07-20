"""Gate API wire shapes — thin pydantic models over the frozen precedent/contracts.py.

These add ONLY the request/response envelopes the HTTP surface needs; the load-bearing
domain types (IncidentEvent, Extracted, RiskAssessment, ApprovalRequest/Decision,
ExecutionResult) stay in precedent/contracts.py and are reused verbatim by the service.

RULE 2 reminder: nothing in these models carries a decision an LLM could set. `decision`,
`status` and `outcome` are produced by the deterministic policy engine + ladder ONLY.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# The three terminal verdicts propose() can return. Computed by policy + ladder, never a model.
Decision = Literal["deny", "needs-approval", "allow-standing"]
# The four states a decision reference can be observed in. Expired ⇒ non-action (fail-closed).
DecisionStatus = Literal["pending", "approved", "denied", "expired"]


class StructuredExtraction(BaseModel):
    """The deterministic, already-extracted class fields + the concrete target object.

    The gate does NOT re-run free-text extraction: the caller supplies the confirmed fields
    (an upstream deterministic extractor, or a human). `error_code` MUST be a code the
    deterministic dictionary knows (precedent.extractor.KNOWN_CODES) — an unknown code is
    denied up front (fail-closed), so the extractor's LLM-proposal branch is never reached
    from the gate's decision path.
    """

    service: str
    error_code: str
    target_object_type: str
    object_id: str | int


class ProposeRequest(BaseModel):
    """A typed proposal: an incident + its structured extraction + the intended action.

    `principal` is the authorising identity, registered OUT-OF-BAND (config/API) — the gate
    NEVER derives identity from an MCP client claim (no robust 2026 standard). `intended_action`
    is optional; when present it must equal the deterministically-selected policy action_type,
    else the proposal is denied (the caller cannot smuggle a different action past the gate).
    """

    incident_id: str
    principal: str
    structured: StructuredExtraction
    raw_text: str = ""
    source: Literal["sim", "jira", "chat"] = "sim"
    observed_at: str | None = None
    intended_action: str | None = None


class ProposeResponse(BaseModel):
    incident_id: str
    decision: Decision
    ref: str | None = None
    expires_at: str | None = None
    risk_class: str | None = None
    policy_rule_id: str | None = None
    ladder_level: str | None = None
    class_key: str | None = None
    plan_hash: str | None = None
    reason: str | None = None
    # DETERMINISTIC basis only (policy rule id + risk class). Never LLM-authored prose.
    rationale: str = ""


class DecisionStateResponse(BaseModel):
    ref: str
    status: DecisionStatus
    incident_id: str | None = None
    plan_hash: str | None = None
    expires_at: str | None = None
    detail: str = ""


class OutcomeRequest(BaseModel):
    """Approve (or reject) a held ref and execute-in-sim, recording the verified outcome.

    `decision`/`approver_principal` are REQUIRED for a needs-approval ref and ignored for a
    standing ref (already pre-approved by the human class promotion). `approver_principal`,
    like the proposer, is registered out-of-band.
    """

    ref: str
    decision: Literal["approve", "reject"] | None = None
    approver_principal: str | None = None


class OutcomeResponse(BaseModel):
    ref: str
    incident_id: str | None = None
    outcome: str
    executed: bool = False
    verified: bool = False
    rolled_back: bool = False
    plan_hash: str | None = None
    detail: str = ""


class GateInfo(BaseModel):
    """Served at GET /v1/gate — the honest self-description of the gate's trust posture."""

    name: str = "Precedent Gate API"
    version: str = "v1"
    principal_binding: str = Field(
        default=(
            "Principals are registered OUT-OF-BAND (config/API) and passed explicitly. The "
            "gate never trusts an MCP client's self-asserted identity — there is no robust "
            "MCP client-identity standard in 2026."
        )
    )
    decision_authority: str = Field(
        default=(
            "Decisions are computed by the deterministic policy engine + approval ladder only. "
            "No LLM is called anywhere in the propose/decide/outcome path."
        )
    )
    failure_direction: str = "fail-closed — an expired or absent ref is a non-action"
