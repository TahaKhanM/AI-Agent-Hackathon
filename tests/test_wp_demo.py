"""WP-DEMO — the graduation-via-real-ladder rewire, the deleted bypass, and the express run.

The pure-Python TestClient is the authoritative gate (Playwright is collection-guarded elsewhere).
These tests lock the load-bearing §b changes:
  * the graduation class opens at L2/streak-0 and is earned to Standing through the REAL ladder
    (ladder.on_verification_result → eligible on EXACTLY the 3rd distinct target → ladder.promote);
  * the raw STANDING-upsert bypass in DemoState.promote is GONE, and demo_reset / the cold-open
    template no longer force-pre-seed STANDING;
  * a scripted EXPRESS run (hold → approve → graduation → reversal → close) hits every beat with
    AI calls: 0 and completes well under four minutes of scripted time.
"""
from __future__ import annotations

import pathlib
import time

import pytest
from fastapi.testclient import TestClient

from console.demo_state import (
    GRADUATION_TARGETS,
    SCHED_CLASS_STANDING,
    DemoState,
)
from precedent import ladder, venice
from precedent.tools import SimTools

REPO = pathlib.Path(__file__).resolve().parent.parent
SCHED = SCHED_CLASS_STANDING


# --------------------------------------------------------------------------- #
# fixtures — the demo server pinned to one world (matches test_seat_demo)
# --------------------------------------------------------------------------- #
@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    monkeypatch.setenv("PRECEDENT_AGENTS_OFFLINE", "1")
    yield


@pytest.fixture
def console_state(tmp_path):
    st = DemoState(db_path=str(tmp_path / "mem.db"))
    yield st
    st.conn.close()


@pytest.fixture
def sim_client(tmp_path, monkeypatch):
    monkeypatch.setenv("PRECEDENT_SIM_DB", str(tmp_path / "sim.db"))
    from sim.app import app
    with TestClient(app) as c:
        c.get("/health")
        yield c


@pytest.fixture
def client(console_state, sim_client, monkeypatch):
    import console.app as capp
    import scripts.demo_server as ds
    monkeypatch.setattr(ds, "STATE", console_state)
    monkeypatch.setattr(capp, "STATE", console_state)
    monkeypatch.setattr(ds, "SimTools", lambda *a, **k: SimTools(client=sim_client))
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    venice.reset_model_calls()
    return TestClient(ds.app)


# --------------------------------------------------------------------------- #
# graduation — the real ladder, distinct targets, eligible ONLY on the 3rd
# --------------------------------------------------------------------------- #
def test_cold_open_graduation_class_is_L2_streak_zero_not_standing(console_state):
    assert ladder.level_of(console_state.conn, SCHED) == "L2"
    assert ladder.consecutive_verified(console_state.conn, SCHED) == 0
    assert ladder.is_standing(SCHED, conn=console_state.conn) is False
    assert ladder.eligible(SCHED, conn=console_state.conn) is False


def test_eligible_flips_only_on_the_third_distinct_recurrence(console_state):
    # 1st and 2nd distinct verified targets do NOT make it eligible…
    r1 = console_state.record_recurrence()
    assert r1["counted"] is True and r1["eligible"] is False
    r2 = console_state.record_recurrence()
    assert r2["eligible"] is False
    # …only the 3rd distinct verified target lights eligibility.
    r3 = console_state.record_recurrence()
    assert r3["eligible"] is True
    assert ladder.eligible(SCHED, conn=console_state.conn) is True


def test_identical_target_within_the_hour_does_not_count(console_state):
    same = GRADUATION_TARGETS[0]
    a = console_state.record_recurrence(target_ref=same)
    assert a["counted"] is True
    b = console_state.record_recurrence(target_ref=same)   # identical (class_key, target_ref)
    assert b.get("counted") is False and b["eligible"] is False


def test_promote_is_a_non_action_until_eligible_then_grants_standing(client, console_state):
    # Not eligible yet → fail-closed non-action (no STANDING, no raw upsert).
    denied = client.post("/api/promote", json={"class_key": SCHED}).json()
    assert denied["ok"] is False and "not_eligible" in denied["reason"]
    assert ladder.is_standing(SCHED, conn=console_state.conn) is False

    for _ in range(3):
        client.post("/api/recur", json={"class_key": SCHED})
    ok = client.post("/api/promote", json={"class_key": SCHED}).json()
    assert ok["ok"] is True and ok["level"] == "STANDING"
    assert ladder.is_standing(SCHED, conn=console_state.conn) is True
    # the real ladder vocabulary is used — a class_promoted event names the promoter.
    rows = [r["event_type"] for r in console_state.conn.execute(
        "SELECT event_type FROM audit_log").fetchall()]
    assert "class_promoted" in rows


def test_revoke_routes_through_ladder_demote_resets_counter(client, console_state):
    for _ in range(3):
        client.post("/api/recur", json={"class_key": SCHED})
    client.post("/api/promote", json={"class_key": SCHED})
    r = client.post("/api/revoke", json={"class_key": SCHED}).json()
    assert r["ok"] is True and r["level"] == "L1"
    assert ladder.consecutive_verified(console_state.conn, SCHED) == 0   # demote resets the counter
    kinds = [r["event_type"] for r in console_state.conn.execute(
        "SELECT event_type FROM audit_log").fetchall()]
    assert "class_demoted" in kinds


# --------------------------------------------------------------------------- #
# the bypass is GONE (source-level guards — the repo is public, a curl bypass
# would disprove the ladder story)
# --------------------------------------------------------------------------- #
def test_raw_upsert_bypass_and_rival_vocabulary_are_gone():
    src = (REPO / "console" / "demo_state.py").read_text()
    # the two rival audit vocabularies are retired (the actual emit calls are gone)…
    assert 'audit.audit("promoted_standing_approval"' not in src
    assert 'audit.audit("revoked_standing_approval"' not in src
    # …and promote/revoke route through the real ladder, never a raw STANDING upsert.
    assert "ladder.promote(" in src and "ladder.demote(" in src
    assert "_set_ladder(class_key, STANDING" not in src


def test_demo_reset_no_longer_force_preseeds_standing():
    # No ladder.promote() call at all in demo_reset — the graduation class is seeded at L2 by
    # DemoState._seed, never force-promoted to STANDING at boot.
    assert "ladder.promote(" not in (REPO / "scripts" / "demo_reset.py").read_text()


def test_session_template_no_longer_force_preseeds_standing():
    # The cold-open memory template builds the world and checkpoints it — no ladder.promote(force).
    assert "ladder.promote(" not in (REPO / "console" / "session.py").read_text()


# --------------------------------------------------------------------------- #
# the EXPRESS scripted run — every beat, AI calls: 0, under four minutes scripted
# --------------------------------------------------------------------------- #
def test_express_run_hits_every_beat_with_zero_ai_calls(client, console_state):
    t0 = time.monotonic()
    assert client.get("/api/model-calls").json()["model_calls"] == 0

    # BEAT hold — Door-2 cold open: a real held gate card with the 64-char plan hash + inverse.
    hold = client.post("/api/drive/1?hold=true").json()
    assert hold["status"] == "pending_approval" and len(hold["plan_hash"]) == 64
    assert hold["preview"]["rollback_ref"]                       # inverse written BEFORE execution

    # BEAT approve — the visitor's name is sealed verbatim into the hash-chained ledger.
    appr = client.post("/api/gate/1/decide?text=approve&principal=Ada").json()
    assert appr["verdict"] == "approve" and appr["verified"] is True
    sealed = console_state.conn.execute(
        "SELECT payload FROM audit_log WHERE event_type='approval_decided' "
        "AND payload LIKE '%INC-1%' ORDER BY seq DESC LIMIT 1").fetchone()
    assert sealed is not None and "Ada" in sealed["payload"]

    # BEAT graduation — three distinct verified recurrences → eligible → the visitor promotes.
    assert client.post("/api/promote", json={"class_key": SCHED}).json()["ok"] is False
    for _ in range(3):
        client.post("/api/recur", json={"class_key": SCHED})
    assert ladder.eligible(SCHED, conn=console_state.conn) is True
    assert client.post("/api/promote", json={"class_key": SCHED}).json()["level"] == "STANDING"

    # the next recurrence runs the zero-LLM fast path (STANDING) — live-measured, AI calls: 0.
    fast = client.post("/api/drive/2").json()
    assert fast["verified"] is True
    assert client.get("/api/model-calls").json()["model_calls"] == 0

    # BEAT reversal — sabotage the visitor's OWN Standing class: verify fails, pre-state restored,
    # STANDING → L1 demotion in the live ledger.
    flaked = client.post("/api/drive/2/flake").json()
    assert flaked["rolled_back"] is True and flaked["verified"] is False
    assert ladder.level_of(console_state.conn, SCHED) == "L1"     # self-demoted, no human needed
    kinds = [r["event_type"] for r in console_state.conn.execute(
        "SELECT event_type FROM audit_log").fetchall()]
    assert "class_demoted" in kinds

    # BEAT close — the REAL WP-PACK evidence pack for this session's incident verifies offline.
    import verify_pack as vp
    pack = client.get("/api/pack/INC-1").json()
    assert vp.verify_pack(pack) == []                            # zero tamper findings, stdlib only
    assert client.get("/api/pack/INC-1/verify").json()["verified"] is True

    # zero AI calls across the WHOLE express arc; scripted wall-clock well under four minutes.
    assert client.get("/api/model-calls").json()["model_calls"] == 0
    assert time.monotonic() - t0 < 240


# --------------------------------------------------------------------------- #
# SSE — the rail streams real events; the client-side unconditional poll is retired
# --------------------------------------------------------------------------- #
def test_sse_stream_emits_rail_events_then_stops_on_disconnect():
    import asyncio

    from console.app import _rail_event_stream

    class _FakeReq:
        """Connected for the first check, disconnected after — so the generator yields exactly one
        rail event then terminates (mirrors a client that opened the stream then left)."""
        def __init__(self):
            self.checks = 0

        async def is_disconnected(self):
            self.checks += 1
            return self.checks > 1

    async def _collect():
        return [e async for e in _rail_event_stream(_FakeReq(), interval=0)]

    events = asyncio.run(_collect())
    assert events and events[0]["event"] == "rail"     # real SSE rail event, deterministically


def test_sse_endpoint_is_registered():
    from console.app import app as capp
    paths = {getattr(r, "path", None) for r in capp.routes}
    assert "/api/stream" in paths


def test_client_retires_the_unconditional_setinterval_poll():
    src = (REPO / "console" / "static" / "js" / "demo.js").read_text()
    # SSE is the primary mechanism…
    assert "EventSource('/api/stream')" in src
    # …and the old unconditional boot-time poll is gone (setInterval now lives only inside the
    # truthful fallback path, started on SSE failure — recorded as the §9 cut-line-6 fallback).
    assert "refreshRail();\nsetInterval(refreshRail, 2500)" not in src
    assert "startRail();" in src
