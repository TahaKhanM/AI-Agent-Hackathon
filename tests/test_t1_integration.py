"""T1 integration simulator — proves the T1<->T2 seam is real, not theoretical.

Simulates T1 (execution loop) sharing ONE SQLite file with the console (T2 view):
- T1 writes a memory record via the MemoryWrite adapter (contract-shaped),
- T1 audits its loop steps and promotes a class to the CANONICAL "STANDING" token,
- the console (separate connection, same file) reflects all of it and displays
  "Standing Approval", the audit chain verifies, and no restricted content leaks,
- a permission flip on the shared db makes the T1-written memory go dark.
"""
from __future__ import annotations

import json

from console.demo_state import STANDING, DemoState, level_label
from precedent.contracts import MemoryWrite
from precedent_memory import audit, db, retrieve, store
from precedent_memory import sync as syncmod
from precedent_memory.sync import FakePermissionSource

RIGHTS = ("jira", "issue-security:rights", "Rights Ops")
SCHED = ("jira", "issue-security:scheduling", "Scheduling Ops")
SECRET = "T1-SECRET-FIX-CONTENT"


def test_t1_plugs_into_t2_over_shared_db(tmp_path):
    shared = str(tmp_path / "precedent.db")
    console = DemoState(db_path=shared)          # console seeds the shared file

    t1 = db.connect(shared)                      # T1 opens the SAME file
    try:
        # 1. T1 writes via the contract-shaped MemoryWrite adapter
        mw = MemoryWrite(
            record={"kind": "executed_fix", "fingerprint": "fp-t1",
                    "body": {"symptom": "s", "fix": SECRET}},
            lineage_source_refs=["jira:MEDIA-113"], class_key="rights-run|X|obj")
        rid = store.store_memory_write(mw, principal_ctx={"principal": "watcher"}, conn=t1)
        assert rid > 0

        # 2. T1 audits its loop steps
        for ev in ("detected", "retrieved", "approved", "executed", "verified", "memorised"):
            audit.audit(ev, conn=t1, actor="watcher", incident_id="T1-1")
        t1.commit()

        # 3. T1 retrieves through the ENFORCED ACL layer (no bypass)
        assert retrieve.retrieve("scheduling-ops", {"fingerprint": "fp-t1"}, conn=t1).hits
        denied = retrieve.retrieve("rights-ops", {"fingerprint": "fp-t1"}, conn=t1)
        assert denied.hits == [] and SECRET not in denied.model_dump_json()

        # 4. T1 promotes the class to the CANONICAL token (what ladder.py reads)
        t1.execute(
            "INSERT INTO class_ladder(class_key, level, promoted_by, promoted_at) "
            "VALUES(?,?,?,?) ON CONFLICT(class_key) DO UPDATE SET level=excluded.level",
            ("rights-run|X|obj", STANDING, "ops-lead", db.utcnow_iso()))
        t1.commit()
    finally:
        t1.close()

    # 5. Console (its own connection) reflects the shared-db writes
    assert retrieve.retrieve("scheduling-ops", {"fingerprint": "fp-t1"}, conn=console.conn).hits
    lvl = console.conn.execute("SELECT level FROM class_ladder WHERE class_key=?",
                               ("rights-run|X|obj",)).fetchone()["level"]
    assert lvl == "STANDING"                       # canonical token in shared DB
    assert level_label(lvl) == "Standing Approval"  # console displays the label
    kinds = {a["event_type"] for a in console.events()["audit"]}
    assert {"detected", "executed", "memorised"} <= kinds   # T1 events visible to console
    assert audit.verify_chain(conn=console.conn) is True
    assert SECRET not in json.dumps(console.snapshot())      # no leak via console

    # 6. A permission flip on the shared db takes the T1-written memory dark
    src = FakePermissionSource()
    src.add("kb:KB-0001", [])
    src.add("kb:KB-0004", [RIGHTS])
    src.add("jira:MEDIA-113", [SCHED, RIGHTS])      # tighten: now needs both
    syncmod.sync(src, conn=console.conn)
    assert retrieve.retrieve("scheduling-ops", {"fingerprint": "fp-t1"},
                             conn=console.conn).hits == []
    console.conn.close()
