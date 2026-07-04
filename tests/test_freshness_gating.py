"""P0.6 — gate the freshness heartbeat + audit it.

commit 5f29a2e's refresh_cached_freshness re-affirmed cached ACLs as fresh WITHOUT consulting any
source. Sound in airplane mode (the local seeded store IS the source of truth); UNSOUND with a live
Jira configured (the 60s window degenerates to "time since last chat", serving an un-polled upstream
tightening indefinitely). This gates it: heartbeat only when no live source is configured; a real
sync() tick otherwise; and an audit row per path.

Verify:
- airplane: incident-2 (scheduler, authorised) stays readable after a heartbeat; incident-3 (rights)
  stays refused; a freshness_heartbeat audit row is written.
- live-source: a stale window produces DENY until a real sync (a blind restamp never happens); a
  freshness_sync_tick audit row is written, and no heartbeat row.
"""
from __future__ import annotations

from datetime import timedelta

import pytest

from console.demo_state import DemoState
from precedent_memory import db, retrieve, store
from precedent_memory import sync as syncmod

# fp-sched: scheduler|SCH-DUP-002, lineage jira:MEDIA-113 (SCHED) — scheduling-ops authorised.
# fp-rights: rights|RGT-EXCL-009, lineage kb:KB-0004 (RIGHTS) + jira:MEDIA-113 (SCHED).
SCHED_FP = "fp-sched"
RIGHTS_FP = "fp-rights"


def _iso(secs_ago: int) -> str:
    return (db.utcnow() - timedelta(seconds=secs_ago)).isoformat()


@pytest.fixture(autouse=True)
def _no_live_env(monkeypatch):
    # start every test from a clean env (no leaked live-Jira config)
    for k in syncmod.JiraPermissionSource.ENV:
        monkeypatch.delenv(k, raising=False)
    yield


@pytest.fixture
def seeded(tmp_path):
    console = DemoState(db_path=str(tmp_path / "mem.db"))
    conn = db.connect(str(tmp_path / "mem.db"))
    yield conn, console
    conn.close()
    console.conn.close()


def _make_sched_stale(conn):
    """Age jira:MEDIA-113 (the SCHED source behind fp-sched) past the freshness window."""
    sid = store.source_id(conn, "jira:MEDIA-113")
    conn.execute("UPDATE acl_source SET last_verified_at = ? WHERE id = ?", (_iso(120), sid))
    store.recompile_for_source(conn, sid)
    conn.commit()


def _hits(conn, fp, principal="scheduling-ops"):
    return retrieve.retrieve(principal, {"fingerprint": fp}, mode="live", conn=conn).hits


def _count(conn, event_type):
    return conn.execute("SELECT COUNT(*) c FROM audit_log WHERE event_type = ?",
                        (event_type,)).fetchone()["c"]


def test_live_source_configured_env_detection(monkeypatch):
    assert syncmod.live_source_configured() is False
    for k in syncmod.JiraPermissionSource.ENV:
        monkeypatch.setenv(k, "placeholder")
    assert syncmod.live_source_configured() is True


def test_airplane_heartbeat_refreshes_and_audits(seeded):
    conn, _ = seeded
    _make_sched_stale(conn)
    assert _hits(conn, SCHED_FP) == [], "precondition: stale restricted record is denied"

    before = _count(conn, "freshness_heartbeat")
    n = syncmod.refresh_cached_freshness(conn)     # airplane (no live env) -> heartbeat
    assert n >= 1
    assert _count(conn, "freshness_heartbeat") == before + 1

    # the authorised scheduler fix is readable again; the rights fix stays refused (conjunction)
    assert _hits(conn, SCHED_FP), "incident-2 authorised class must resolve after a heartbeat"
    assert _hits(conn, RIGHTS_FP) == [], "incident-3 (rights) must stay refused for scheduling-ops"


def test_live_mode_does_not_blindly_refresh_stale(seeded):
    conn, _ = seeded
    _make_sched_stale(conn)
    unavailable = syncmod.FakePermissionSource()
    unavailable.set_available(False)              # a live source that cannot be reached

    before = _count(conn, "freshness_sync_tick")
    syncmod.refresh_cached_freshness(conn, source=unavailable)   # a REAL sync tick, not a restamp
    assert _count(conn, "freshness_sync_tick") == before + 1
    assert _count(conn, "freshness_heartbeat") == 0, "no blind heartbeat on the live path"

    # the stale restricted record was NOT blindly refreshed -> still denied (fail-closed)
    assert _hits(conn, SCHED_FP) == [], "a live-source outage must keep restricted memory dark"


def test_live_env_auto_selects_sync_tick(seeded, monkeypatch):
    """With the live-Jira env set and NO explicit source, refresh auto-constructs a
    JiraPermissionSource and does a real sync tick — never a blind heartbeat. Kept hermetic by
    making that source's snapshot fail closed (no network)."""
    conn, _ = seeded
    _make_sched_stale(conn)
    for k in syncmod.JiraPermissionSource.ENV:
        monkeypatch.setenv(k, "placeholder")

    def _fail_closed_snapshot(self):
        raise syncmod.PermissionSourceUnavailable("hermetic test — no network")
    monkeypatch.setattr(syncmod.JiraPermissionSource, "snapshot", _fail_closed_snapshot)

    syncmod.refresh_cached_freshness(conn)        # no explicit source -> env -> auto sync tick
    assert _count(conn, "freshness_sync_tick") >= 1
    assert _count(conn, "freshness_heartbeat") == 0
    assert _hits(conn, SCHED_FP) == []            # fail-closed: stays dark
