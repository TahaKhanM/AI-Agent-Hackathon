"""Write path: lineage capture + effective-policy compilation.  [STUB — owner T2, task T2-1]

Spec: Idea/refinement/02-architecture-refinement.md §2.3-§2.4.

On write: record the full SET of source lineage constraints, then compile the
effective_policy row = union of constraint-ids across ALL lineage sources (conjunction,
semantic rule A), as a bitmap (implementation B). is_restricted = required_bits nonempty.
"""
from __future__ import annotations


def store(record: dict, lineage: list[str], principal_ctx=None) -> int:
    """TODO T2-1: insert memory_record + lineage rows, compile effective_policy bitmap,
    append an audit event. Return record_id."""
    raise NotImplementedError("T2-1: store() — see 02 §2.4")


def compile_effective_policy(record_id: int) -> None:
    """TODO T2-1: recompute required_bits = union over lineage sources; bump
    policy_version; set min_source_freshness. Called on write and on ACL sync."""
    raise NotImplementedError("T2-1: effective-policy compile — see 02 §2.4")
