"""Message contracts — the frozen boundary every agent and loop step imports.

Shapes are from Idea/refinement/02-architecture-refinement.md §3.1. These are pure
data models (pydantic v2), scaffolded so the import graph is stable at the M-1 merge;
the LOGIC that produces/consumes them lives in the stub modules alongside.

Rule reminders that touch these types:
- TriageResult.extracted counts as a class match only when extraction_method ==
  'deterministic' (rule 2 — the LLM may propose, only the extractor confirms).
- ApprovalDecision.approver_principal is the authorising identity (console user, or
  the ASI:One chat sender address) — recorded in the audit log.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Extracted(BaseModel):
    service: str
    error_code: str
    target_object_type: str


class IncidentEvent(BaseModel):
    incident_id: str
    jira_key: str | None = None
    raw_text: str
    source: Literal["sim", "jira", "chat"]
    observed_at: str


class TriageResult(BaseModel):
    incident_id: str
    extracted: Extracted | None = None
    extraction_method: Literal["deterministic", "llm_proposed"]
    candidate_class_key: str | None = None
    confidence: float = 0.0


class Hit(BaseModel):
    record_id: int
    kind: str
    score: float


class RetrievalBundle(BaseModel):
    incident_id: str
    principal_id: str
    hits: list[Hit] = Field(default_factory=list)
    denied_count: int = 0
    denied_owner_team: str | None = None


class RiskAssessment(BaseModel):
    incident_id: str
    risk_class: str
    policy_rule_id: str
    ladder_level: Literal["L0", "L1", "L2", "STANDING", "ESCALATE"]
    rationale_text: str = ""


class TypedToolCall(BaseModel):
    tool: str
    args: dict


class ExecutionPlan(BaseModel):
    incident_id: str
    steps: list[TypedToolCall] = Field(default_factory=list)
    rollback_steps: list[TypedToolCall] = Field(default_factory=list)
    pre_state_snapshot_ref: str | None = None
    plan_hash: str


class ApprovalRequest(BaseModel):
    incident_id: str
    plan_hash: str
    risk_class: str
    ladder_level: str
    requested_at: str
    expires_at: str
    channel: Literal["console", "chat"]


class ApprovalDecision(BaseModel):
    incident_id: str
    plan_hash: str
    decision: Literal["approve", "reject"]
    approver_principal: str
    channel: Literal["console", "chat"]
    decided_at: str


class ExecutionResult(BaseModel):
    incident_id: str
    plan_hash: str
    step_results: list[dict] = Field(default_factory=list)
    verified: bool = False
    rolled_back: bool = False
    elapsed_ms: int = 0


class MemoryWrite(BaseModel):
    record: dict  # executed-fix-with-provenance
    lineage_source_refs: list[str] = Field(default_factory=list)
    class_key: str
