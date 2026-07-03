"""Access-control edge hardening regression tests (from the independent checker).

Covers paths that WORK but previously had no dedicated test, so a regression could
pass silently: missing effective_policy row, quarantined/tombstoned deny-on-read,
unknown lineage ref, non-fix empty-lineage, a real retrieve->audit-chain flow, and
the honest tail-truncation limitation.
"""
from __future__ import annotations

from precedent_memory import audit, db, retrieve, store


def _restricted(conn, fp="fp-e"):
    return store.store({"kind": "executed_fix", "fingerprint": fp, "body": {"fix": "secret"}},
                       ["jira:MEDIA-113"], conn=conn)


def test_missing_effective_policy_row_denies(scenario):
    """A record whose effective_policy row is absent must be denied (has_policy
    False -> fail closed), never served on an assumed-public default."""
    conn = scenario["conn"]
    rid = _restricted(conn)
    assert retrieve.retrieve("sched_only", {"fingerprint": "fp-e"}, conn=conn).hits  # baseline
    conn.execute("DELETE FROM effective_policy WHERE record_id = ?", (rid,))
    conn.commit()
    assert retrieve.retrieve("sched_only", {"fingerprint": "fp-e"}, conn=conn).hits == []


def test_quarantined_and_tombstoned_records_deny_on_read(scenario):
    """memory_record.status != 'active' denies retrieval even for an otherwise
    authorised principal."""
    conn = scenario["conn"]
    rid = _restricted(conn)
    for status in ("quarantined", "tombstoned"):
        conn.execute("UPDATE memory_record SET status = ? WHERE id = ?", (status, rid))
        conn.commit()
        got = retrieve.retrieve("sched_only", {"fingerprint": "fp-e"}, conn=conn).hits
        assert got == [], status


def test_unknown_lineage_ref_fails_closed(scenario):
    """A record referencing an UNKNOWN acl_source ref must fail closed — store
    materialises it as an unverified (nobody-satisfies) source, never public."""
    conn = scenario["conn"]
    store.store({"kind": "executed_fix", "fingerprint": "fp-unk", "body": {"fix": "x"}},
                ["kb:DOES-NOT-EXIST-9999"], conn=conn)
    ep = conn.execute("SELECT is_restricted FROM effective_policy ep JOIN memory_record m "
                      "ON m.id = ep.record_id WHERE m.fingerprint = 'fp-unk'").fetchone()
    assert ep["is_restricted"] == 1
    for p in ("nobody", "rights_only", "sched_only", "both"):
        assert retrieve.retrieve(p, {"fingerprint": "fp-unk"}, conn=conn).hits == []


def test_kb_summary_empty_lineage_denied_but_public_lineage_allowed(scenario):
    """Empty lineage fails closed for ALL kinds (not just executed_fix); a record
    with an explicitly PUBLIC lineage source stays readable by everyone."""
    conn = scenario["conn"]
    store.store({"kind": "kb_summary", "fingerprint": "fp-kb", "body": {"x": "y"}}, [], conn=conn)
    store.put_source(conn, "kb:PUBLIC", [])
    store.store({"kind": "kb_summary", "fingerprint": "fp-pub2", "body": {"x": "y"}},
                ["kb:PUBLIC"], conn=conn)
    assert retrieve.retrieve("nobody", {"fingerprint": "fp-kb"}, conn=conn).hits == []   # denied
    assert retrieve.retrieve("nobody", {"fingerprint": "fp-pub2"}, conn=conn).hits        # public


def test_real_retrieve_then_audit_chain_verifies(scenario):
    """Drive the audit log through REAL retrievals (allow + deny), then confirm the
    hash chain still verifies end-to-end."""
    conn = scenario["conn"]
    _restricted(conn)
    retrieve.retrieve("sched_only", {"fingerprint": "fp-e"}, conn=conn)   # allowed -> audits
    retrieve.retrieve("rights_only", {"fingerprint": "fp-e"}, conn=conn)  # denied  -> audits
    kinds = {r["event_type"] for r in conn.execute("SELECT event_type FROM audit_log")}
    assert {"memory_stored", "retrieval_allowed", "retrieval_denied"} <= kinds
    assert audit.verify_chain(conn=conn) is True


def test_tail_truncation_detected_only_with_a_remembered_anchor(conn):
    """Honest limitation: deleting the last row leaves a bare verify() True; passing
    a remembered expected_len / expected_tail_hash detects the truncation."""
    for i in range(3):
        audit.audit(f"e{i}", conn=conn, actor="a")
    good_len = 3
    good_tail = conn.execute(
        "SELECT hash FROM audit_log ORDER BY seq DESC LIMIT 1").fetchone()["hash"]
    conn.execute("DELETE FROM audit_log WHERE seq = (SELECT MAX(seq) FROM audit_log)")
    conn.commit()
    assert audit.verify_chain(conn=conn) is True                         # bare chain: undetected
    assert audit.verify_chain(conn=conn, expected_len=good_len) is False  # anchor catches it
    assert audit.verify_chain(conn=conn, expected_tail_hash=good_tail) is False


def test_unverified_provenance_denies_even_if_sentinel_bit_granted(scenario):
    """Hardening: an unverified-provenance record is denied even to a principal that
    has (wrongly) been granted the reserved sentinel bit — the fail-closed guarantee
    is enforced by permitted(), not just a naming convention."""
    conn = scenario["conn"]
    store.store({"kind": "executed_fix", "fingerprint": "fp-uv", "body": {"fix": "x"}},
                [], conn=conn)                       # empty lineage -> unverified provenance
    unv_id = store.ensure_constraint(conn, db.UNVERIFIED_SOURCE_SYSTEM, db.UNVERIFIED_SOURCE_REF)
    store.put_principal(conn, "attacker", [unv_id])  # attacker granted the sentinel bit
    assert retrieve.retrieve("attacker", {"fingerprint": "fp-uv"}, conn=conn).hits == []


def test_no_provenance_leak_via_owner_team_on_unverified(scenario):
    """An unverified/no-provenance record must not disclose a real owner team (the
    unverified constraint carries only a system label, not a team's identity)."""
    conn = scenario["conn"]
    store.store({"kind": "executed_fix", "fingerprint": "fp-np", "body": {"fix": "x"}},
                [], conn=conn)
    bundle = retrieve.retrieve("nobody", {"fingerprint": "fp-np"}, conn=conn)
    assert bundle.hits == []
    assert bundle.denied_owner_team in (None, "Unverified source — fail closed")
