"""precedent_memory — standalone permission-aware memory governance library.

Precedent imports it; it does not import Precedent. A/B/C lineage semantics
(conjunction over ALL sources), precompiled effective-policy bitmaps (the P99 fast
path), hash-chained audit, fail-closed retrieval. See:
- Idea/refinement/02-architecture-refinement.md §2 (the full design)
- schema.sql (already written from §2.3)
- tests/ (conjunction / fail-closed / concurrency / audit / sync — all green)

Public API (keep these signatures stable — T1 integrates against them). Every
function takes an explicit SQLite connection (open one with db.connect(path); the
caller owns the handle). NO LLM/model import appears in retrieve.py (rule 2).

    db.connect(path=None, *, check_same_thread=True) -> sqlite3.Connection
    store.store(record: dict, lineage: list[str], principal_ctx=None, *, conn) -> int
    store.store_memory_write(mw, principal_ctx=None, *, conn) -> int   # MemoryWrite adapter
    store.compile_effective_policy(record_id, *, conn) -> None
    store.put_source(conn, external_ref, constraint_ids=(), *,
                     last_verified_at=None, revoked=0) -> dict
    store.put_principal(conn, external_id, constraint_ids=(), kind='human') -> int
    store.ensure_constraint(conn, source_system, external_ref, description=None) -> int
    retrieve.retrieve(principal, query, mode='live', *, conn) -> RetrievalBundle
    retrieve.check_access(conn, principal, record_id, mode='live') -> (bool, owner_team)
    sync.sync(source, *, conn) -> dict     # {"available": bool, ...}; fail-closed on outage
    sync.FakePermissionSource / sync.JiraPermissionSource   # offline demo / live Jira
    audit.audit(event_type, *, conn, actor=None, **payload) -> int   # hash-chained
    audit.verify_chain(*, conn, expected_len=None, expected_tail_hash=None) -> bool
"""
