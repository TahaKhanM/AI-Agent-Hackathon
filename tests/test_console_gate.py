"""P1.7 — the console Approve button is REAL.

Drives the demo server (scripts.demo_server) with the in-process sim and asserts:
- hold=true returns a pending-approval card payload with the DIFF PREVIEW (pre_state vs the
  planned mutation + the rollback anchor + the plan hash);
- Approve resumes the REAL held gate (executes, verified, approver principal recorded in audit);
- Reject leaves state untouched (nothing executes);
- the robustness chip / cumulative-close / per-incident TTR come from committed sources via
  /api/state, byte-for-byte;
- the page has NO inline onclick (the XSS fix — data-* attributes + one delegated handler);
- one-click change-record export returns the audit-derived document.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from console.demo_state import DemoState
from precedent import venice
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


@pytest.fixture
def demo(sim_client, mem, monkeypatch):
    import console.app as capp
    import scripts.demo_server as ds
    _t1, console = mem
    # Both modules bound `from console.demo_state import STATE` at import; in production they are
    # the SAME singleton. In the test, point BOTH at the fixture's DemoState so the drive
    # (demo_server) and the read/export endpoints (console.app) share one connection.
    monkeypatch.setattr(ds, "STATE", console)
    monkeypatch.setattr(capp, "STATE", console)
    monkeypatch.setattr(ds, "SimTools", lambda *a, **k: SimTools(client=sim_client))
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    ds._PENDING.clear()
    client = TestClient(ds.app)
    return ds, console, client


def _audit_types(conn, incident_id):
    rows = conn.execute("SELECT event_type, payload FROM audit_log WHERE payload LIKE ?",
                        (f'%"{incident_id}"%',)).fetchall()
    return [r["event_type"] for r in rows]


def test_hold_returns_diff_preview_with_rollback_anchor(demo):
    _ds, console, client = demo
    r = client.post("/api/drive/1?hold=true").json()
    assert r["status"] == "pending_approval"
    p = r["preview"]
    assert p["pre_state"], "the card must show the BEFORE (pre-state) to diff against"
    assert p["planned"], "the card must show the planned mutation"
    assert p["rollback_ref"], "the card must show the rollback anchor"
    assert p["plan_hash"] and len(p["plan_hash"]) == 64
    assert p["risk_class"]
    # nothing executed yet while the gate is held
    assert "verified" not in _audit_types(console.conn, "INC-1")


def test_approve_resumes_the_real_gate(demo):
    _ds, console, client = demo
    client.post("/api/drive/1?hold=true")
    a = client.post("/api/drive/1/approve?principal=ops-lead").json()
    assert a["outcome"] == "resolved" and a["verified"] is True
    types = _audit_types(console.conn, "INC-1")
    assert "verified" in types and "memory_stored" in types   # the REAL loop ran
    # the approver principal is in the audit (not just an approval_recorded stamp)
    row = console.conn.execute(
        "SELECT payload FROM audit_log WHERE event_type='approval_decided' "
        "AND payload LIKE '%INC-1%' ORDER BY seq DESC LIMIT 1").fetchone()
    assert row is not None and "ops-lead" in row["payload"]


def test_reject_leaves_state_untouched(demo):
    _ds, console, client = demo
    client.post("/api/drive/1?hold=true")
    r = client.post("/api/drive/1/reject?principal=ops-lead").json()
    assert r["status"] == "rejected"
    types = _audit_types(console.conn, "INC-1")
    assert "verified" not in types and "memory_stored" not in types  # nothing executed
    # a second reject is fail-closed non-action (the gate is gone)
    r2 = client.post("/api/drive/1/reject").json()
    assert r2["status"] == "no_live_approval"


def test_state_carries_committed_chip_numbers(demo):
    _ds, _console, client = demo
    st = client.get("/api/state").json()
    rob = st["robustness"]
    assert rob["false_fast_paths"] == 0 and rob["total"] == 100
    assert rob["decoys_resisted"] == 25 and rob["decoys_total"] == 25
    assert st["closed_count"] == 0
    # after a resolved drive, the TTR chip + close count populate from real audit rows
    client.post("/api/drive/2")                 # standing fast-path -> resolved
    st2 = client.get("/api/state").json()
    assert st2["closed_count"] == 1
    inc2 = next(i for i in st2["incidents"] if i["incident_id"] == "INC-2")
    assert inc2["ttr_seconds"] is not None and inc2["ttr_seconds"] >= 0


def test_page_has_no_inline_onclick_xss(demo):
    _ds, _console, client = demo
    page = client.get("/").text
    assert "onclick" not in page, "inline onclick handlers are the XSS vector — must be gone"
    assert "data-act" in page                    # controls are delegated off data-* attributes
    assert "Standing Approval" in page and "autonomous" not in page.lower()


def test_change_record_export_from_audit(demo):
    _ds, _console, client = demo
    client.post("/api/drive/1")                  # produce a real audit trail
    r = client.get("/api/change-record/INC-1")
    assert r.status_code == 200
    assert "attachment" in r.headers.get("content-disposition", "")
    assert "Change record" in r.text and "hash-chained" in r.text
    assert "takedown" not in r.text.lower()      # never leaks restricted content
