"""The closed loop.  [STUB — owner T1, task T1-5]

Spec: Idea/refinement/02-architecture-refinement.md §3.

DETECT -> TRIAGE -> RETRIEVE (ACL-filtered) -> RISK-CLASSIFY (deterministic) -> GATE
-> EXECUTE (typed tools) -> VERIFY (auto-rollback on failure) -> MEMORISE.

The recovery beat (incident R): a verification failure fires the pre-generated
rollback, restores the pre-state snapshot, demotes the class, and re-escalates to a
human. Every hop appends to the hash-chained audit log.
"""
from __future__ import annotations

from precedent.contracts import IncidentEvent


def handle(incident: IncidentEvent):
    """TODO T1-5: run the loop. On a STANDING fingerprint match, take the zero-LLM
    fast-path (ladder.is_standing). Otherwise triage -> retrieve -> assess -> gate."""
    raise NotImplementedError("T1-5: orchestrator loop — see 02 §3")
