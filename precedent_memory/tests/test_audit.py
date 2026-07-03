"""Hash-chained audit log: append produces a verifiable chain; any modification,
removal or reorder breaks verification (02 §2.3)."""
from __future__ import annotations

from precedent_memory import audit


def test_append_produces_valid_chain(conn):
    audit.audit("retrieval_allowed", conn=conn, actor="alice", record_id=1)
    audit.audit("retrieval_denied", conn=conn, actor="bob", record_id=2, reason="acl")
    audit.audit("acl_sync_applied", conn=conn, actor="system", source="jira:MEDIA-113")
    assert audit.verify_chain(conn=conn) is True
    assert conn.execute("SELECT COUNT(*) c FROM audit_log").fetchone()["c"] == 3


def test_tamper_with_payload_breaks_chain(conn):
    audit.audit("e1", conn=conn, actor="a", record_id=1)
    audit.audit("e2", conn=conn, actor="a", record_id=2)
    assert audit.verify_chain(conn=conn) is True
    conn.execute("UPDATE audit_log SET payload = ? WHERE seq = 1", ('{"record_id":999}',))
    assert audit.verify_chain(conn=conn) is False


def test_removing_a_row_breaks_chain(conn):
    audit.audit("e1", conn=conn, actor="a")
    audit.audit("e2", conn=conn, actor="a")
    audit.audit("e3", conn=conn, actor="a")
    conn.execute("DELETE FROM audit_log WHERE seq = 2")  # break the middle link
    assert audit.verify_chain(conn=conn) is False


def test_tamper_with_hash_breaks_chain(conn):
    audit.audit("e1", conn=conn, actor="a")
    audit.audit("e2", conn=conn, actor="a")
    conn.execute("UPDATE audit_log SET hash = ? WHERE seq = 1", ("deadbeef" * 8,))
    assert audit.verify_chain(conn=conn) is False


def test_empty_chain_is_valid(conn):
    assert audit.verify_chain(conn=conn) is True
