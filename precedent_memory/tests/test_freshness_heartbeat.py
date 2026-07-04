"""Freshness heartbeat — refresh_cached_freshness keeps restricted-but-authorised memory
readable in a sync-less process, without ever widening access.

Reproduces the standalone-Watcher bug: a restricted record whose compiled freshness has aged
past the 60s window is fail-closed DENIED even to a cleared principal; the heartbeat re-affirms
the cached ACLs and restores it. Revoked sources must stay dark (fail-closed preserved).
"""
from __future__ import annotations

from datetime import timedelta

from precedent_memory import db, retrieve, store
from precedent_memory.sync import refresh_cached_freshness


def _rec(conn, fp, lineage):
    return store.store({"kind": "kb_summary", "fingerprint": fp, "body": {"fix": "x"}},
                       lineage, conn=conn)


def _age(conn, minutes):
    conn.execute("UPDATE effective_policy SET min_source_freshness = ?",
                 ((db.utcnow() - timedelta(minutes=minutes)).isoformat(),))
    conn.commit()


def test_heartbeat_restores_stale_but_authorised_record(scenario):
    conn = scenario["conn"]
    rec = _rec(conn, "fp-heartbeat", ["kb:KB-0004"])            # requires {rights}
    # fresh -> allowed
    assert retrieve.check_access(conn, "rights_only", rec, mode="live")[0] is True
    _age(conn, 5)                                              # 5 min past -> beyond the 60s window
    # stale -> denied (fail-closed)
    assert retrieve.check_access(conn, "rights_only", rec, mode="live")[0] is False
    refreshed = refresh_cached_freshness(conn)
    assert refreshed >= 1
    # re-affirmed -> allowed
    assert retrieve.check_access(conn, "rights_only", rec, mode="live")[0] is True


def test_heartbeat_does_not_widen_access(scenario):
    """The heartbeat only refreshes the freshness stamp — it never grants a principal a
    constraint it lacks."""
    conn = scenario["conn"]
    rec = _rec(conn, "fp-hb-deny", ["kb:KB-0004"])             # requires {rights}
    _age(conn, 5)
    refresh_cached_freshness(conn)
    # sched-only still lacks the rights constraint -> denied (permission, not freshness)
    assert retrieve.check_access(conn, "sched_only", rec, mode="live")[0] is False
    assert retrieve.check_access(conn, "rights_only", rec, mode="live")[0] is True


def test_heartbeat_leaves_revoked_source_dark(scenario):
    conn = scenario["conn"]
    rec = _rec(conn, "fp-hb-rev", ["kb:KB-0004"])
    store.put_source(conn, "kb:KB-0004", [scenario["rights"]], revoked=1)   # revoke the source
    assert retrieve.check_access(conn, "rights_only", rec, mode="live")[0] is False
    refresh_cached_freshness(conn)                            # must NOT un-revoke
    assert retrieve.check_access(conn, "rights_only", rec, mode="live")[0] is False
