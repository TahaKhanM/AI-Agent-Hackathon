"""CORE hardening — P0.5 (Rule-2 grey zone), P0.7 (tool + gate hardening), P0.4
(demo-server responsiveness). Offline / in-process sim.

Each test encodes a *Verify* line:
- P0.5: an llm_proposed extraction can NEVER reach executable plan construction; deterministic
  extractions still build a plan (the 3 demo incidents replay unchanged).
- P0.7(a): a 404 snapshot raises (no silent empty pre-state); an empty snapshot refuses a plan.
- P0.7(b): a tool step reporting ok=false is treated as a verification failure (rollback + audit).
- P0.7(c): the in-process pending map prunes expired holds.
- P0.7(d): the flake is armed ONLY on a path that executes; a refused incident never arms it.
- P0.4: driving an incident does not hold STATE._lock across venice — /api/state stays responsive
  and the trace streams per hop.
"""
from __future__ import annotations

import threading
import time

import httpx
import pytest
from fastapi.testclient import TestClient

from console.demo_state import DemoState
from precedent import extractor, orchestrator, venice
from precedent.contracts import IncidentEvent
from precedent.tools import SimTools
from precedent_memory import db


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    monkeypatch.setenv("PRECEDENT_AGENTS_OFFLINE", "1")
    yield


@pytest.fixture
def mem(tmp_path):
    shared = str(tmp_path / "mem.db")
    console = DemoState(db_path=shared)
    t1 = db.connect(shared)
    yield t1, console, shared
    t1.close()
    console.conn.close()


@pytest.fixture
def sim_client(tmp_path, monkeypatch):
    monkeypatch.setenv("PRECEDENT_SIM_DB", str(tmp_path / "sim.db"))
    from sim.app import app
    with TestClient(app) as c:
        c.get("/health")
        yield c


def _incident_event(sim, n):
    p = sim.incident(n)
    return IncidentEvent(incident_id=p["incident_id"], raw_text=p["raw_text"],
                         source="sim", observed_at=p["observed_at"]), p["structured"]


# --------------------------------------------------------------------------- #
# P0.5 — Rule-2 grey zone: llm_proposed never builds an executable plan
# --------------------------------------------------------------------------- #
def test_llm_proposed_never_builds_executable_plan(sim_client, mem, monkeypatch):
    t1, _c, _ = mem
    sim = SimTools(client=sim_client)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    inc, structured = _incident_event(sim, 2)   # a permitted, deterministic class...
    real_extract = extractor.extract

    def fake_extract(raw, structured=None):     # ...but force the method to llm_proposed
        ext, _method = real_extract(raw, structured)
        return ext, "llm_proposed"
    monkeypatch.setattr(extractor, "extract", fake_extract)

    prepared = orchestrator.prepare(inc, structured=structured, conn=t1, tools=sim,
                                    principal="scheduling-ops")
    assert prepared.outcome == "escalated", "an LLM-proposed class must not reach plan construction"
    assert prepared.plan is None
    assert prepared.fast is False
    assert prepared.result.step_results[0].get("reason") == "not_deterministic_extraction"


def test_deterministic_extraction_still_builds_plan(sim_client, mem, monkeypatch):
    t1, _c, _ = mem
    sim = SimTools(client=sim_client)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    for n in (1, 2):
        inc, structured = _incident_event(sim, n)
        _ext, method = extractor.extract(inc.raw_text, structured)
        assert method == "deterministic", f"incident {n} must extract deterministically"
        prepared = orchestrator.prepare(inc, structured=structured, conn=t1, tools=sim,
                                        principal="scheduling-ops")
        assert prepared.outcome in ("ready", "fast_ready")
        assert prepared.plan is not None


# --------------------------------------------------------------------------- #
# P0.7(a) — no silent empty pre-state; refuse a plan on an empty snapshot
# --------------------------------------------------------------------------- #
def test_snapshot_404_raises(sim_client):
    sim = SimTools(client=sim_client)
    with pytest.raises(httpx.HTTPStatusError):
        sim.snapshot("publisher", "schedule_item", "does-not-exist-999")


def test_empty_snapshot_refuses_plan(sim_client, mem, monkeypatch):
    t1, _c, _ = mem
    sim = SimTools(client=sim_client)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    inc, structured = _incident_event(sim, 1)
    monkeypatch.setattr(sim, "snapshot", lambda *a, **k: {"fields": {}})  # empty pre-state
    prepared = orchestrator.prepare(inc, structured=structured, conn=t1, tools=sim,
                                    principal="scheduling-ops")
    assert prepared.outcome == "escalated"
    assert prepared.result.step_results[0].get("reason") == "empty_snapshot"
    assert prepared.plan is None


# --------------------------------------------------------------------------- #
# P0.7(b) — a tool step reporting ok=false is a verification failure (rollback + audit)
# --------------------------------------------------------------------------- #
def test_execute_ok_false_rolls_back_and_audits(sim_client, mem, monkeypatch):
    t1, _c, _ = mem
    sim = SimTools(client=sim_client)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    inc, structured = _incident_event(sim, 1)
    prepared = orchestrator.prepare(inc, structured=structured, conn=t1, tools=sim,
                                    principal="scheduling-ops")
    assert prepared.outcome == "ready"

    calls = {"verify": 0}
    orig_verify = sim.verify
    monkeypatch.setattr(sim, "execute", lambda *a, **k: {"ok": False, "detail": "sim rejected"})

    def counting_verify(*a, **k):
        calls["verify"] += 1
        return orig_verify(*a, **k)
    monkeypatch.setattr(sim, "verify", counting_verify)

    from precedent.contracts import ApprovalDecision
    decision = ApprovalDecision(incident_id=inc.incident_id, plan_hash=prepared.plan.plan_hash,
                                decision="approve", approver_principal="ops-lead",
                                channel="console", decided_at=db.utcnow_iso())
    res = orchestrator.commit_execution(prepared, conn=t1, tools=sim, decision=decision,
                                        actor="ops-lead")
    assert res.verified is False and res.rolled_back is True
    assert calls["verify"] == 0, "verify must be SKIPPED once a step reports ok=false"
    rows = t1.execute("SELECT COUNT(*) c FROM audit_log WHERE event_type='execute_failed'"
                      ).fetchone()["c"]
    assert rows >= 1, "an explicit execute_failed audit row must be written"


# --------------------------------------------------------------------------- #
# P0.7(c) — the in-process pending map prunes expired holds
# --------------------------------------------------------------------------- #
def test_pending_map_prunes_expired(monkeypatch):
    from datetime import timedelta

    import scripts.demo_server as ds

    class _FakePrepared:
        def __init__(self, expires_at):
            self.approval_request = type("R", (), {"expires_at": expires_at})()

    ds._PENDING.clear()
    ds._PENDING["INC-STALE"] = _FakePrepared((db.utcnow() - timedelta(minutes=1)).isoformat())
    ds._PENDING["INC-LIVE"] = _FakePrepared((db.utcnow() + timedelta(minutes=5)).isoformat())
    ds._prune_pending()
    assert "INC-STALE" not in ds._PENDING       # expired -> pruned
    assert "INC-LIVE" in ds._PENDING            # still-live -> kept
    ds._PENDING.clear()


# --------------------------------------------------------------------------- #
# P0.7(d) — flake arms only on an executing path; refused never arms it
# --------------------------------------------------------------------------- #
def _demo_server_client(monkeypatch, sim_client, console):
    """Point the demo server at the fixture's ALREADY-SEEDED DemoState (one connection, committed)
    and route its typed tools through the in-process sim. Creating a second DemoState on the same
    file would re-run sync() (which does not commit) and hold a write lock -> 'database is locked';
    reusing the committed console avoids that and matches the live single-STATE topology."""
    import scripts.demo_server as ds
    monkeypatch.setattr(ds, "STATE", console)
    monkeypatch.setattr(ds, "SimTools", lambda *a, **k: SimTools(client=sim_client))
    ds._PENDING.clear()
    return ds, console


def test_flake_not_armed_on_refused_incident(sim_client, mem, monkeypatch):
    t1, console, _shared = mem
    ds, _state = _demo_server_client(monkeypatch, sim_client, console)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    # incident 3 is refused (rights) -> arming must NOT happen (would poison the next drive)
    out = ds.api_arm_flake(3)
    assert out["outcome"] == "refused"
    # a subsequent normal drive must verify TRUE (flake was never armed)
    res2 = ds.api_drive(2)
    assert res2["outcome"] == "resolved"
    assert res2["verified"] is True and res2["rolled_back"] is False


def test_flake_armed_on_executing_incident_triggers_recovery(sim_client, mem, monkeypatch):
    t1, console, _shared = mem
    ds, state = _demo_server_client(monkeypatch, sim_client, console)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    # incident 2 is the STANDING fast-path -> flake armed -> first verify FAILS -> rollback
    state.promote("scheduler|SCH-DUP-002|schedule_item", "ops-lead")
    out = ds.api_arm_flake(2)
    assert out["rolled_back"] is True and out["verified"] is False


# --------------------------------------------------------------------------- #
# P0.4 — demo-server responsiveness: /api/state stays live during a drive
# --------------------------------------------------------------------------- #
def test_drive_does_not_block_state_reads(sim_client, mem, monkeypatch):
    t1, console, _shared = mem
    ds, state = _demo_server_client(monkeypatch, sim_client, console)

    entered = threading.Event()
    release = threading.Event()

    def slow_chat(*a, **k):
        entered.set()
        release.wait(3.0)
        return "documented fix rationale"
    monkeypatch.setattr(venice, "chat", slow_chat)

    result: dict = {}

    def run_drive():
        result["r"] = ds.api_drive(1)          # slow-path -> parks in venice.chat

    th = threading.Thread(target=run_drive)
    th.start()
    try:
        assert entered.wait(3.0), "drive never reached venice.chat"
        # while the drive is parked in venice, STATE._lock (which /api/state needs) must be FREE —
        # the old code held it across the whole drive, so /api/state would block for seconds.
        t0 = time.monotonic()
        acquired = state._lock.acquire(timeout=0.5)
        dt = time.monotonic() - t0
        assert acquired, f"STATE._lock held across venice.chat ({dt:.2f}s) — /api/state would stall"
        try:
            snap = state.snapshot()            # and a real read returns promptly
            assert snap["title"] == "Precedent"
        finally:
            state._lock.release()
        # the trace streamed several hops BEFORE venice (streams, not one burst at the end)
        assert len(state.trace) >= 3
    finally:
        release.set()
        th.join(4.0)
    assert result["r"]["outcome"] == "resolved"
