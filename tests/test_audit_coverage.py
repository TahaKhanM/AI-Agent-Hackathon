"""100% audit-coverage check.  [owner T3, task T3-9]

Spec: Idea/refinement/02-architecture-refinement.md §2.7.

Asserts every retrieval / denial / sync / store path appends a hash-chained audit_log row and
that verify_chain(expected_len=…) holds. Crucially this is a REAL coverage check, not just a
chain-validity check:

  * test_dropped_audit_call_is_detected — with the audit() chokepoint stubbed out, the number
    of rows written falls below the number of decisions, so the coverage assertion FAILS. That
    proves the coverage test would catch a developer who removes an audit() call.
  * test_verify_chain_detects_tail_truncation — deleting the most-recent rows still leaves a
    valid prefix; only verify_chain(expected_len=…) catches the truncation. That proves the
    length anchor is load-bearing (100% is really 100%, not "100% of what survived").
"""
from __future__ import annotations

import precedent_memory.audit as audit_mod
from precedent_memory import audit, db, retrieve, store
from precedent_memory.bench import grade


def _world():
    conn = db.connect(":memory:")
    rights = store.ensure_constraint(conn, "jira", "issue-security:rights", "Rights Ops")
    store.put_principal(conn, "rights_only", [rights])
    store.put_principal(conn, "nobody", [])
    fresh = db.utcnow_iso()
    store.put_source(conn, "kb:RIGHTS", [rights], last_verified_at=fresh)
    rid = store.store({"kind": "executed_fix", "class_key": "svc|A-1|obj"},
                      ["kb:RIGHTS"], conn=conn)
    return conn, rid


def _count(conn) -> int:
    return conn.execute("SELECT COUNT(*) c FROM audit_log").fetchone()["c"]


# --------------------------------------------------------------------------- #
# Coverage: every decision path writes exactly one chained row
# --------------------------------------------------------------------------- #
def test_store_writes_an_audit_row():
    conn, _rid = _world()
    row = conn.execute(
        "SELECT COUNT(*) c FROM audit_log WHERE event_type='memory_stored'").fetchone()["c"]
    assert row == 1
    assert audit.verify_chain(conn=conn)


def test_every_retrieval_decision_is_audited():
    conn, rid = _world()
    before = _count(conn)
    decisions = 0
    # one allow, one deny — both must audit
    for principal in ("rights_only", "nobody"):
        bundle = retrieve.retrieve(principal, {"class_key": "svc|A-1|obj"}, conn=conn)
        decisions += len(bundle.hits) + bundle.denied_count
    after = _count(conn)
    assert decisions == 2
    assert after - before == decisions            # 100% coverage
    types = {r["event_type"] for r in conn.execute(
        "SELECT event_type FROM audit_log WHERE seq > ?", (before,)).fetchall()}
    assert types == {"retrieval_allowed", "retrieval_denied"}
    assert audit.verify_chain(conn=conn, expected_len=after)


def test_sync_applied_and_unavailable_are_audited():
    from precedent_memory import sync
    conn, _rid = _world()
    src = sync.FakePermissionSource()
    src.add("kb:RIGHTS", [("jira", "issue-security:rights", "Rights Ops")])
    src.flip_add("kb:RIGHTS", ("jira", "issue-security:scheduling", "Scheduling Ops"))
    sync.sync(src, conn=conn)   # a real ACL change -> acl_sync_applied
    assert conn.execute(
        "SELECT COUNT(*) c FROM audit_log WHERE event_type='acl_sync_applied'"
    ).fetchone()["c"] >= 1

    src.set_available(False)
    sync.sync(src, conn=conn)   # source down -> fail closed -> sync_unavailable
    assert conn.execute(
        "SELECT COUNT(*) c FROM audit_log WHERE event_type='sync_unavailable'"
    ).fetchone()["c"] >= 1
    assert audit.verify_chain(conn=conn)


# --------------------------------------------------------------------------- #
# Meta-tests: prove the coverage check is REAL
# --------------------------------------------------------------------------- #
def test_dropped_audit_call_is_detected(monkeypatch):
    """If the audit() chokepoint is stubbed out, retrievals stop writing rows and the
    coverage assertion (audited == decisions) FAILS. This is what makes the coverage test a
    coverage test and not merely a chain-validity test."""
    conn, rid = _world()
    before = _count(conn)

    # drop the audit call on the retrieval path
    monkeypatch.setattr(audit_mod, "audit", lambda *a, **k: 0)

    decisions = 0
    for principal in ("rights_only", "nobody"):
        bundle = retrieve.retrieve(principal, {"class_key": "svc|A-1|obj"}, conn=conn)
        decisions += len(bundle.hits) + bundle.denied_count
    audited = _count(conn) - before

    assert decisions == 2
    assert audited < decisions          # the drop is DETECTED (0 rows written for 2 decisions)
    # and therefore a 100%-coverage assertion would fail:
    coverage = audited / decisions
    assert coverage < 1.0


def test_verify_chain_detects_tail_truncation():
    """A bare hash chain cannot detect deletion of the most-recent rows on its own; only the
    expected_len anchor catches it. Proves 100% audit coverage really means 100%."""
    conn, _rid = _world()
    # write a few more rows
    for i in range(5):
        audit.audit("probe", conn=conn, actor="t", i=i)
    full_len = _count(conn)
    assert audit.verify_chain(conn=conn, expected_len=full_len)

    # truncate the tail (simulate someone deleting the last audit rows)
    last_seq = conn.execute("SELECT MAX(seq) m FROM audit_log").fetchone()["m"]
    conn.execute("DELETE FROM audit_log WHERE seq >= ?", (last_seq - 1,))
    conn.commit()

    # the surviving prefix still verifies on its own — the danger a length anchor closes
    assert audit.verify_chain(conn=conn) is True
    # but with the remembered length, truncation is caught
    assert audit.verify_chain(conn=conn, expected_len=full_len) is False


def test_bench_reports_full_coverage():
    """The conformance bench's audit-coverage witness agrees: 100% + chain verified."""
    result = grade.run_audit_coverage()
    assert result["coverage"] >= 1.0
    assert result["chain_verified"] is True
