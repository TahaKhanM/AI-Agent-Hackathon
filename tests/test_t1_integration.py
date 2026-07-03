"""T1<->T2 seam over a shared SQLite file, driven by the REAL orchestrator (not an inline
simulation). T1 (the execution loop) runs a real incident against the MediaCo sim while
sharing ONE db file with the console (T2 view):
- the REAL orchestrator writes an executed-fix memory record (contract-shaped) + audits
  every loop hop over the shared db,
- a human promotes the class to the CANONICAL "STANDING" token,
- the console (separate connection, same file) reflects all of it and displays
  "Standing Approval", the audit chain verifies, and no restricted content leaks,
- a permission flip on the shared db makes the T1-written memory go dark.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from console.demo_state import DemoState, level_label
from precedent import ladder, orchestrator, venice
from precedent.contracts import ApprovalDecision, IncidentEvent
from precedent.tools import SimTools
from precedent_memory import audit, db, retrieve
from precedent_memory import sync as syncmod
from precedent_memory.sync import FakePermissionSource

RIGHTS = ("jira", "issue-security:rights", "Rights Ops")
SCHED = ("jira", "issue-security:scheduling", "Scheduling Ops")
CK = "scheduler|SCH-DUP-002|schedule_item"     # canonical class the real loop resolves


def _approve(req):
    return ApprovalDecision(incident_id=req.incident_id, plan_hash=req.plan_hash,
                            decision="approve", approver_principal="ops-lead",
                            channel="console", decided_at=db.utcnow_iso())


def test_t1_plugs_into_t2_over_shared_db(tmp_path, monkeypatch):
    monkeypatch.setenv("PRECEDENT_SIM_DB", str(tmp_path / "sim.db"))
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "documented dedupe fix")  # offline
    from sim.app import app

    shared = str(tmp_path / "precedent.db")
    console = DemoState(db_path=shared)          # console seeds the shared file
    t1 = db.connect(shared)                      # T1 opens the SAME file
    try:
        with TestClient(app) as sc:
            sc.get("/health")
            sim = SimTools(client=sc)
            p = sim.incident(2)                  # scheduler|SCH-DUP-002 (lineage jira:MEDIA-113)
            inc = IncidentEvent(incident_id=p["incident_id"], raw_text=p["raw_text"],
                                source="sim", observed_at=p["observed_at"])

            # 1+2. the REAL orchestrator resolves the incident: retrieve -> gate -> execute
            #      -> verify -> memorise + audit every hop over the shared db.
            res = orchestrator.handle(inc, structured=p["structured"], conn=t1, tools=sim,
                                      principal="scheduling-ops", approve=_approve)
            assert res.verified is True

            # 3. T1 retrieves through the ENFORCED ACL (no bypass): the SCHED-restricted
            #    record is readable by scheduling-ops, denied to rights-ops.
            assert retrieve.retrieve("scheduling-ops", {"class_key": CK}, conn=t1).hits
            denied = retrieve.retrieve("rights-ops", {"class_key": CK}, conn=t1)
            assert denied.hits == [] and "SCH-DUP-002-DEDUPE" not in denied.model_dump_json()

            # 4. a human promotes the class to the CANONICAL token
            ladder.promote(CK, "ops-lead", conn=t1, force=True)
    finally:
        t1.close()

    # 5. Console (its own connection) reflects the shared-db writes
    assert retrieve.retrieve("scheduling-ops", {"class_key": CK}, conn=console.conn).hits
    lvl = console.conn.execute("SELECT level FROM class_ladder WHERE class_key=?",
                               (CK,)).fetchone()["level"]
    assert lvl == "STANDING"                        # canonical token in shared DB
    assert level_label(lvl) == "Standing Approval"  # console displays the label
    kinds = {a["event_type"] for a in console.events()["audit"]}
    assert {"detected", "executed", "memory_stored"} <= kinds   # T1 events visible
    assert audit.verify_chain(conn=console.conn) is True

    # 6. A permission flip on the shared db takes the T1-written memory dark
    src = FakePermissionSource()
    src.add("kb:KB-0001", [])
    src.add("kb:KB-0004", [RIGHTS])
    src.add("jira:MEDIA-113", [SCHED, RIGHTS])       # tighten: now needs both
    syncmod.sync(src, conn=console.conn)
    assert retrieve.retrieve("scheduling-ops", {"class_key": CK},
                             conn=console.conn).hits == []
    console.conn.close()
