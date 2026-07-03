"""Shared fixtures for the precedent_memory test suite.

Fast + offline: every test runs against a fresh in-memory SQLite db with the
canonical schema applied. No network, no live Jira, no model calls.
"""
from __future__ import annotations

from datetime import timedelta

import pytest

from precedent_memory import db, store


@pytest.fixture
def conn():
    c = db.connect(":memory:")
    try:
        yield c
    finally:
        c.close()


@pytest.fixture
def iso():
    """Helper to produce an ISO timestamp `seconds` in the past (negative = future)."""
    def _iso(seconds_ago: float = 0) -> str:
        return (db.utcnow() - timedelta(seconds=seconds_ago)).isoformat()
    return _iso


@pytest.fixture
def scenario(conn):
    """Seed the canonical two-team conjunction scenario and return handles.

    Constraints: RIGHTS (owner 'Rights Ops'), SCHED (owner 'Scheduling Ops').
    Principals: rights_only, sched_only, both, nobody.
    Sources: kb-public (public), kb-rights (RIGHTS), jira-sched (SCHED).
    """
    rights = store.ensure_constraint(conn, "jira", "issue-security:rights", "Rights Ops")
    sched = store.ensure_constraint(conn, "jira", "issue-security:scheduling", "Scheduling Ops")

    store.put_principal(conn, "rights_only", [rights])
    store.put_principal(conn, "sched_only", [sched])
    store.put_principal(conn, "both", [rights, sched])
    store.put_principal(conn, "nobody", [])

    store.put_source(conn, "kb:KB-0001", [])
    store.put_source(conn, "kb:KB-0004", [rights])
    store.put_source(conn, "jira:MEDIA-113", [sched])

    return {"conn": conn, "rights": rights, "sched": sched}
