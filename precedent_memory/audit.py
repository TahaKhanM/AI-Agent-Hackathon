"""Hash-chained audit log.  [STUB — owner T2, task T2-1]

Spec: Idea/refinement/02-architecture-refinement.md §2.3.

Append-only; each row's hash = sha256(prev_hash || canonical_json(row)). Covers
retrievals, denials, sync events, executions, promotions/demotions, redactions — the
SOC 2 five elements live in payload. 100% coverage (every retrieval/denial logged) is a
BasedAI requirement, asserted by tests/ — see test_audit_coverage (T3-7). A README
"Audit posture" line cross-references Jira's own auditing API (two independent logs).
"""
from __future__ import annotations


def audit(event_type: str, **payload) -> int:
    """TODO T2-1: append a hash-chained row; return its seq. Must be called on every
    retrieval, denial, sync, execution, promotion/demotion, redaction."""
    raise NotImplementedError("T2-1: audit() — see 02 §2.3")


def verify_chain() -> bool:
    """TODO T2-1: recompute the chain end-to-end; True iff intact. Exposed as a README
    verification command."""
    raise NotImplementedError("T2-1: chain verification — see 02 §2.3")
