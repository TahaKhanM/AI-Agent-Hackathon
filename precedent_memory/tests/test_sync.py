"""ACL sync: idempotent versioned upserts, revocation/flip fan-out, and
fail-closed on source outage — all without a live Jira (02 §2.5)."""
from __future__ import annotations

from precedent_memory import retrieve, store
from precedent_memory.sync import (
    FakePermissionSource,
    JiraPermissionSource,
    sync,
)

RIGHTS = ("jira", "issue-security:rights", "Rights Ops")
SCHED = ("jira", "issue-security:scheduling", "Scheduling Ops")


def _seed(conn, constraints):
    """Sync a fake source once, then create principals mapped to the constraint
    ids sync just registered, and store a restricted fix derived from the source."""
    src = FakePermissionSource()
    src.add("jira:MEDIA-113", constraints)
    sync(src, conn=conn)
    sched_id = store.ensure_constraint(conn, *SCHED)
    rights_id = store.ensure_constraint(conn, *RIGHTS)
    store.put_principal(conn, "sched_only", [sched_id])
    store.put_principal(conn, "both", [sched_id, rights_id])
    rid = store.store(
        {"fingerprint": "fp-fc", "class_key": "sched|S-1|slot", "body": {"fix": "secret"}},
        ["jira:MEDIA-113"], conn=conn,
    )
    return src, rid


def test_sync_adds_source_constraints(conn):
    src, _ = _seed(conn, [SCHED])
    row = conn.execute("SELECT constraint_ids FROM acl_source WHERE external_ref=?",
                       ("jira:MEDIA-113",)).fetchone()
    assert row is not None and row["constraint_ids"] not in (None, "[]")
    assert retrieve.retrieve("sched_only", {"fingerprint": "fp-fc"}, conn=conn).hits


def test_sync_revocation_denies_previously_visible_memory(conn):
    src, _ = _seed(conn, [SCHED])
    assert retrieve.retrieve("sched_only", {"fingerprint": "fp-fc"}, conn=conn).hits

    src.revoke("jira:MEDIA-113")
    sync(src, conn=conn)
    assert retrieve.retrieve("sched_only", {"fingerprint": "fp-fc"}, conn=conn).hits == []


def test_sync_flip_tightens_access_conjunction(conn):
    """The console demo mechanic: flipping a source to ALSO require RIGHTS makes a
    scheduling-only principal go dark (conjunction), reversibly."""
    src, _ = _seed(conn, [SCHED])
    assert retrieve.retrieve("sched_only", {"fingerprint": "fp-fc"}, conn=conn).hits

    src.flip_add("jira:MEDIA-113", RIGHTS)
    sync(src, conn=conn)
    assert retrieve.retrieve("sched_only", {"fingerprint": "fp-fc"}, conn=conn).hits == []
    assert retrieve.retrieve("both", {"fingerprint": "fp-fc"}, conn=conn).hits  # still ok

    src.flip_remove("jira:MEDIA-113", RIGHTS)   # un-flip restores
    sync(src, conn=conn)
    assert retrieve.retrieve("sched_only", {"fingerprint": "fp-fc"}, conn=conn).hits


def test_sync_outage_denies_restricted_serves_public(conn):
    src, _ = _seed(conn, [SCHED])
    store.put_source(conn, "kb:KB-0001", [])   # public source
    store.store({"fingerprint": "fp-pub", "body": {"fix": "x"}}, ["kb:KB-0001"], conn=conn)
    assert retrieve.retrieve("sched_only", {"fingerprint": "fp-fc"}, conn=conn).hits

    src.set_available(False)
    res = sync(src, conn=conn)
    assert res["available"] is False
    # restricted memory goes dark in live mode; public keeps serving
    assert retrieve.retrieve("sched_only", {"fingerprint": "fp-fc"}, conn=conn).hits == []
    assert retrieve.retrieve("both", {"fingerprint": "fp-fc"}, conn=conn).hits == []
    assert retrieve.retrieve("sched_only", {"fingerprint": "fp-pub"}, conn=conn).hits


def test_sync_is_idempotent(conn):
    src, _ = _seed(conn, [SCHED])
    v1 = conn.execute("SELECT acl_version FROM acl_source WHERE external_ref=?",
                      ("jira:MEDIA-113",)).fetchone()["acl_version"]
    sync(src, conn=conn)
    sync(src, conn=conn)
    rows = conn.execute("SELECT acl_version FROM acl_source WHERE external_ref=?",
                        ("jira:MEDIA-113",)).fetchall()
    assert len(rows) == 1
    assert rows[0]["acl_version"] == v1   # no ACL change -> no version bump


def test_jira_source_unconfigured_fails_closed(conn):
    src = JiraPermissionSource(env={})
    assert src.configured is False
    res = sync(src, conn=conn)
    assert res["available"] is False   # no creds -> fail closed, never open
