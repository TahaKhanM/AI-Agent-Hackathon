"""B12 (reach) — the change-record artifact renders from REAL audit rows.

Drives incident 1 through the deterministic kernel, then renders the ITIL-style change document
from the committed audit_log and asserts the load-bearing sections came from real audit events
(no LLM, no network). Also covers the refusal case (incident 3 → REFUSED, no restricted body).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from console.demo_state import DemoState
from precedent import orchestrator, venice
from precedent.contracts import ApprovalDecision, IncidentEvent
from precedent.tools import SimTools
from precedent_memory import db
from scripts.render_change_record import render


def _approve(req):
    return ApprovalDecision(incident_id=req.incident_id, plan_hash=req.plan_hash,
                            decision="approve", approver_principal="ops-lead",
                            channel="console", decided_at=db.utcnow_iso())


@pytest.fixture
def mem(tmp_path):
    shared = str(tmp_path / "mem.db")
    console = DemoState(db_path=shared)
    t1 = db.connect(shared)
    yield t1, console
    t1.close()
    console.conn.close()


@pytest.fixture
def sim_client(tmp_path, monkeypatch):
    monkeypatch.setenv("PRECEDENT_SIM_DB", str(tmp_path / "sim.db"))
    from sim.app import app
    with TestClient(app) as c:
        c.get("/health")
        yield c


def _drive(sim, conn, n, approve, principal="scheduling-ops"):
    p = sim.incident(n)
    inc = IncidentEvent(incident_id=p["incident_id"], raw_text=p["raw_text"], source="sim",
                        observed_at=p["observed_at"])
    return orchestrator.handle(inc, structured=p["structured"], conn=conn, tools=sim,
                               principal=principal, approve=approve)


def test_change_record_renders_from_real_audit_rows(sim_client, mem, monkeypatch):
    t1, _ = mem
    sim = SimTools(client=sim_client)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    res = _drive(sim, t1, 1, approve=_approve)
    assert res.verified

    doc = render(t1, "INC-1")
    # the change record is built from REAL audit events, not invented
    assert "# Change record CHG-" in doc
    assert "publisher|PUB-4012|schedule_item" in doc          # class_key from the triage event
    assert "standard_change" in doc                            # risk_class from risk_assessed
    assert "PUB-4012-REPUBLISH" in doc                         # policy rule
    assert "ops-lead" in doc                                   # approver from approval_decided
    assert "IMPLEMENTED — verified successful" in doc          # from executed + verified events
    assert "Chain tail hash:" in doc                           # hash-chained provenance
    assert "detected" in doc and "executed" in doc and "verified" in doc  # the audit event table
    assert res.plan_hash[:8].upper() in doc   # change id derives from the plan hash


def test_change_record_refusal_discloses_no_restricted_body(sim_client, mem, monkeypatch):
    t1, _ = mem
    sim = SimTools(client=sim_client)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    # scheduling-ops lacks the rights constraint → incident 3 is refused
    res = _drive(sim, t1, 3, approve=None, principal="scheduling-ops")
    assert not res.verified

    doc = render(t1, "INC-3")
    assert "REFUSED" in doc
    # RULE 3: the change record must not leak the restricted runbook body
    assert "takedown" not in doc.lower()
    assert "RGT-WIN-014" not in doc
    assert "republish per rights runbook" not in doc
