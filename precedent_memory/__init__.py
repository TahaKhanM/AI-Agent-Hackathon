"""precedent_memory — standalone permission-aware memory governance library.

Precedent imports it; it does not import Precedent. A/B/C lineage semantics
(conjunction over ALL sources), precompiled effective-policy bitmaps (the P99 fast
path), hash-chained audit, fail-closed retrieval. See:
- Idea/refinement/02-architecture-refinement.md §2 (the full design)
- schema.sql (already written from §2.3)
- tests/ (spec skeletons — implement store/retrieve/sync/audit to green)

Public API (frozen at the M-1 merge; keep these signatures stable):
    store(record, lineage, principal_ctx) -> record_id
    retrieve(principal, query, mode) -> list[Hit]        # NO LLM import in retrieve.py (rule 2)
    sync(jira_client) -> None                             # versioned ACL poll, fail-closed
    audit(event_type, **payload) -> None                 # hash-chained
"""
