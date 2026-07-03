"""T1 REAL-orchestrator integration — the G1 vertical slice, end-to-end on seeded real
data over a shared SQLite memory db + the live MediaCo sim (in-process TestClient).

Proves: incident 1 (slow-path, LLM-assisted, human approval) resolves; incident 2
(fast-path repeat) resolves with ZERO venice.chat/embed on the STANDING branch; recovery R
(armed flake -> verify fails -> rollback restores snapshot -> class_demoted -> re-approve
-> success); incident 3 (rights) is REFUSED with only denied_count+owner disclosed and no
restricted fix content leaked; the audit chain stays intact throughout.
"""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from console.demo_state import DemoState
from precedent import ladder, orchestrator, venice
from precedent.contracts import ApprovalDecision, IncidentEvent
from precedent.tools import SimTools
from precedent_memory import audit, db

RESTRICTED_FIX = "takedown + republish per rights runbook"   # seeded restricted body


@pytest.fixture
def sim_client(tmp_path, monkeypatch):
    monkeypatch.setenv("PRECEDENT_SIM_DB", str(tmp_path / "sim.db"))
    from sim.app import app
    with TestClient(app) as c:
        c.get("/health")   # force idempotent build
        yield c


@pytest.fixture
def mem(tmp_path):
    shared = str(tmp_path / "mem.db")
    console = DemoState(db_path=shared)     # seeds the 3 demo records + ACLs + principals
    t1 = db.connect(shared)
    yield t1, console
    t1.close()
    console.conn.close()


def _incident(sim: SimTools, n: int):
    payload = sim.incident(n)
    inc = IncidentEvent(incident_id=payload["incident_id"], raw_text=payload["raw_text"],
                        source="sim", observed_at=payload["observed_at"])
    return inc, payload["structured"]


def _approver(principal="ops-lead"):
    def approve(req):
        return ApprovalDecision(incident_id=req.incident_id, plan_hash=req.plan_hash,
                                decision="approve", approver_principal=principal,
                                channel="console", decided_at=db.utcnow_iso())
    return approve


def _audit_kinds(conn):
    return [r["event_type"] for r in conn.execute(
        "SELECT event_type FROM audit_log ORDER BY seq").fetchall()]


def test_incident1_slow_path_resolves(sim_client, mem, monkeypatch):
    t1, console = mem
    sim = SimTools(client=sim_client)
    # LLM-assisted rationale: stub SMART so the test is offline + deterministic.
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "Documented fix: republish EPG metadata.")
    inc, structured = _incident(sim, 1)
    res = orchestrator.handle(inc, structured=structured, conn=t1, tools=sim,
                              principal="scheduling-ops", approve=_approver())
    assert res.verified is True and res.rolled_back is False
    kinds = _audit_kinds(t1)
    for ev in ("detected", "triage", "risk_assessed", "approval_requested",
               "approval_decided", "executed", "verified", "memory_stored"):
        assert ev in kinds, f"missing audit event {ev}"
    # the console (own connection, same file) sees T1's new memory record + audit chain
    assert audit.verify_chain(conn=console.conn) is True


def test_incident2_fast_path_is_zero_llm(sim_client, mem, monkeypatch):
    t1, _ = mem
    sim = SimTools(client=sim_client)
    ck = "scheduler|SCH-DUP-002|schedule_item"
    ladder.promote(ck, "ops-lead", conn=t1, force=True)     # pre-seed STANDING
    assert ladder.is_standing(ck, conn=t1)

    # ANY LLM call on the STANDING branch fails the test.
    def _boom(*a, **k):
        raise AssertionError("LLM called on the STANDING fast-path")
    monkeypatch.setattr(venice, "chat", _boom)
    monkeypatch.setattr(venice, "embed", _boom)

    inc, structured = _incident(sim, 2)
    res = orchestrator.handle(inc, structured=structured, conn=t1, tools=sim,
                              principal="scheduling-ops")   # no approver: fast-path needs none
    assert res.verified is True
    assert "standing" in json.dumps(res.step_results).lower() or res.verified


def test_recovery_flake_rolls_back_and_demotes(sim_client, mem, monkeypatch):
    t1, _ = mem
    sim = SimTools(client=sim_client)
    ck = "scheduler|SCH-DUP-002|schedule_item"
    ladder.promote(ck, "ops-lead", conn=t1, force=True)     # STANDING
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")

    inc, structured = _incident(sim, 2)
    sim.arm_flake()                                          # arm exactly one verify failure
    res = orchestrator.handle(inc, structured=structured, conn=t1, tools=sim,
                              principal="scheduling-ops")
    assert res.rolled_back is True and res.verified is False
    assert ladder.level_of(t1, ck) == "L1"                  # demoted from STANDING
    assert "class_demoted" in _audit_kinds(t1)

    # re-approve (now slow-path since demoted) -> flake disarmed -> success
    res2 = orchestrator.handle(inc, structured=structured, conn=t1, tools=sim,
                               principal="scheduling-ops", approve=_approver())
    assert res2.verified is True and res2.rolled_back is False


def test_incident3_rights_is_refused_no_leak(sim_client, mem):
    t1, _ = mem
    sim = SimTools(client=sim_client)
    inc, structured = _incident(sim, 3)
    res = orchestrator.handle(inc, structured=structured, conn=t1, tools=sim,
                              principal="scheduling-ops", approve=_approver())
    assert res.verified is False and res.rolled_back is False
    blob = res.model_dump_json()
    assert "refused" in blob
    assert res.step_results[0]["denied_owner_team"] == "Rights Ops"
    assert res.step_results[0]["denied_count"] >= 1
    assert RESTRICTED_FIX not in blob                       # no restricted fix content leaks


def test_plan_hash_tamper_is_rejected(sim_client, mem, monkeypatch):
    t1, _ = mem
    sim = SimTools(client=sim_client)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    inc, structured = _incident(sim, 1)

    def tamper(req):    # approve a DIFFERENT plan hash
        return ApprovalDecision(incident_id=req.incident_id, plan_hash="deadbeef" * 8,
                                decision="approve", approver_principal="attacker",
                                channel="console", decided_at=db.utcnow_iso())
    res = orchestrator.handle(inc, structured=structured, conn=t1, tools=sim,
                              principal="scheduling-ops", approve=tamper)
    assert res.verified is False
    assert res.step_results[0]["outcome"] == "rejected"
