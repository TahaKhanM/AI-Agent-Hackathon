"""Jira ACL sync — versioned polling, fail-closed fallback.  [STUB — owner T2, task T2-2]

Spec: Idea/refinement/02-architecture-refinement.md §2.5.

Poll every 2-3s (no webhooks — venue Wi-Fi has no inbound path): project role /
permission-scheme membership on the live scheme, AND the issue-security level on
runbook issues (JSM Standard — enforcement verified <=5s; the dual-enforcement demo).
Each observed ACL state hashes to a digest; digest change -> acl_version += 1,
last_verified_at = now, single transaction (idempotent compare-and-set).

Revocation fan-out: on any acl_source change -> SELECT record_id FROM lineage WHERE
source_id = ? (indexed) -> recompile each effective_policy row -> emit one
acl_sync_applied audit event per record. Source deleted -> derived records quarantined.

Fallback (Jira unreachable): serve reads from cache, queue writes for replay, flip the
degraded banner, and LOCK every restricted record (fail-closed).
"""
from __future__ import annotations


def sync(jira_client) -> None:
    """TODO T2-2: one poll tick — refresh ACL sources, fan out recompiles, emit audit
    events. Anchor drift/TTC timestamps to Jira's own auditing API (external clock)."""
    raise NotImplementedError("T2-2: Jira ACL sync — see 02 §2.5")
