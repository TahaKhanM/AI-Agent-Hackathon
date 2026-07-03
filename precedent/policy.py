"""Deterministic risk-policy engine.  [STUB — owner T1, task T1-4]

Spec: Idea/refinement/02-architecture-refinement.md §3.2-§3.3.

RULE 2: the risk CLASS is decided here by YAML rules keyed on
(system x action type x risk class x autonomy level) — NEVER by an LLM. The SMART
model may write the rationale PROSE, but the class and the gate decision are
deterministic. Evaluation cost is corpus-size-independent (per-tenant YAML trees).
"""
from __future__ import annotations

from precedent.contracts import RiskAssessment, TriageResult


def assess(triage: TriageResult) -> RiskAssessment:
    """TODO T1-4: load the YAML policy pack, evaluate the fingerprint's rule, return
    the risk class + ladder level + policy_rule_id. No LLM in this function."""
    raise NotImplementedError("T1-4: YAML policy engine — see 02 §3.2")
