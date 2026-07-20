"""Console endpoint tests — the judge-facing surface, driven through FastAPI's
TestClient. No network, no T1 required; the console runs on the seeded local-demo
state. Proves: endpoints work, Standing-Approval terminology, permission-flip makes
restricted memory go dark, and NO restricted content ever leaks in a denial.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from console.app import app

# The restricted fix body seeded in demo_state — must never appear in a denial.
RESTRICTED_FIX_TEXT = "takedown + republish per rights runbook"


def served_surface(client) -> str:
    """The user-visible demo surface. Post WP-REFACTOR the page shell links an external
    JS bundle (console/static/js/demo.js) that carries the narrative copy, so a copy
    assertion must look at the shell AND the bundle it ships."""
    html = client.get("/").text
    js = client.get("/static/js/demo.js").text
    return html + "\n" + js


@pytest.fixture
def client():
    c = TestClient(app)
    c.post("/api/demo/reset")   # isolate each test
    return c


def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["memory"] == "ready"
    assert body["audit_chain"] == "intact"


def test_index_loads_and_never_says_autonomous(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Precedent" in r.text
    surface = served_surface(client)
    assert "Standing Approval" in surface
    assert "Autonomous" not in surface and "autonomous" not in surface


def test_approve_records_audit_event(client):
    client.post("/api/approve", json={"incident_id": "INC-1"})
    events = client.get("/api/events").json()
    kinds = [a["event_type"] for a in events["audit"]]
    assert "approval_recorded" in kinds
    assert events["audit_chain"] == "intact"


def test_promote_stores_canonical_standing_displays_label(client):
    cls = "publisher|PUB-4012|schedule_item"
    r = client.post("/api/promote", json={"class_key": cls}).json()
    assert r["level"] == "STANDING"                  # canonical DATA token
    assert r["level_label"] == "Standing Approval"   # display text
    state = client.get("/api/state").json()
    inc = {i["class_key"]: i for i in state["incidents"]}[cls]
    assert inc["ladder_level"] == "STANDING"          # API exposes the canonical token
    assert inc["ladder_level_label"] == "Standing Approval"
    surface = served_surface(client)
    assert "Standing Approval" in surface and "Autonomous" not in surface

    r2 = client.post("/api/revoke", json={"class_key": cls}).json()
    assert r2["level"] == "L1"
    state2 = client.get("/api/state").json()
    assert {i["class_key"]: i["ladder_level"] for i in state2["incidents"]}[cls] == "L1"


def test_class_ladder_row_holds_canonical_token_not_display_text(client):
    # WP-HOST-SESSION: the process-wide STATE singleton is retired; read THIS client's
    # per-session memory db (resolved from its session cookie) to inspect the raw ladder row.
    from console.session import COOKIE_NAME, SESSIONS
    cls = "publisher|PUB-4012|schedule_item"
    client.post("/api/promote", json={"class_key": cls})
    conn = SESSIONS.get(client.cookies.get(COOKIE_NAME)).state.conn
    level = conn.execute("SELECT level FROM class_ladder WHERE class_key=?",
                         (cls,)).fetchone()["level"]
    assert level == "STANDING"                        # DB never stores display text
    assert level != "Standing Approval"


def test_console_honours_shared_db_path(tmp_path):
    import os

    from console.demo_state import DemoState
    from precedent_memory import db, retrieve, store
    p = str(tmp_path / "shared.db")
    st = DemoState(db_path=p)                          # console seeds the file db
    t1 = db.connect(p)                                # T1 opens the SAME file
    try:
        rid = store.store({"kind": "executed_fix", "fingerprint": "fp-t1shared",
                           "body": {"fix": "x"}}, ["jira:MEDIA-113"], conn=t1)
        hits = retrieve.retrieve("scheduling-ops", {"fingerprint": "fp-t1shared"},
                                 conn=st.conn).hits
        assert [h.record_id for h in hits] == [rid]   # console sees T1's write
        st.reset()                                    # reset preserves the file + T1 data
        assert os.path.exists(p)
        again = retrieve.retrieve("scheduling-ops", {"fingerprint": "fp-t1shared"},
                                  conn=st.conn).hits
        assert [h.record_id for h in again] == [rid]
    finally:
        t1.close()
        st.conn.close()


def test_live_timer_moves(monkeypatch):
    import datetime

    from console.demo_state import DemoState
    from precedent_memory import db
    st = DemoState()
    e0 = st.snapshot()["elapsed_seconds"]
    base = db.utcnow()
    monkeypatch.setattr(db, "utcnow", lambda: base + datetime.timedelta(seconds=5))
    e1 = st.snapshot()["elapsed_seconds"]
    assert e1 >= e0 + 4                                # elapsed advances with the clock


def test_baseline_caveat_visible_on_screen(client):
    surface = served_surface(client)
    assert "MetricNet" in surface and "business-hours" in surface and "8h 51m" in surface


def test_permission_flip_makes_restricted_memory_go_dark(client):
    # INC-2 (scheduler fix) is readable by the default scheduling-ops principal...
    state = client.get("/api/state").json()
    inc2 = next(i for i in state["incidents"] if i["incident_id"] == "INC-2")
    assert inc2["access"] == "permitted"

    flip = client.post("/api/permission-flip", json={}).json()
    assert flip["scheduler_fix_access"] == "denied"

    state2 = client.get("/api/state").json()
    inc2b = next(i for i in state2["incidents"] if i["incident_id"] == "INC-2")
    assert inc2b["access"] == "denied"
    assert inc2b["denied_owner_team"] == "Rights Ops"

    # ...and un-flipping restores it
    client.post("/api/permission-flip", json={"on": False})
    state3 = client.get("/api/state").json()
    inc2c = next(i for i in state3["incidents"] if i["incident_id"] == "INC-2")
    assert inc2c["access"] == "permitted"


def test_triage_refusal_leaks_no_restricted_content(client):
    r = client.post("/api/triage", json={"incident_id": "INC-3"})
    body = r.json()
    assert body["result"] == "refused"
    assert body["denied_count"] >= 1
    assert body["denied_owner_team"] in ("Rights Ops", "Scheduling Ops")
    assert body["hits"] == []
    assert RESTRICTED_FIX_TEXT not in r.text   # no fix content in the denial


def test_no_endpoint_leaks_restricted_fix_content(client):
    """The restricted fix body must not surface via state, events, or a denied
    triage for an unauthorised principal."""
    client.post("/api/triage", json={"incident_id": "INC-3"})
    for path in ("/api/state", "/api/events", "/health"):
        assert RESTRICTED_FIX_TEXT not in client.get(path).text


def test_permitted_triage_returns_a_hit(client):
    r = client.post("/api/triage", json={"incident_id": "INC-1"}).json()
    assert r["result"] == "permitted"
    assert len(r["hits"]) == 1
