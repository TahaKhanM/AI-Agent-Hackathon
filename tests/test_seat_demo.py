"""The Approver's Seat (v2 demo) — the NEW interactive surfaces are REAL.

Every beat of the redesigned demo drives the real kernel; these tests lock the new
endpoints that back it:
- /api/model-calls        honest counter of successful model calls (0 on the airplane path)
- /api/audit/tamper|restore  a REAL byte-flip that fails the real chain verifier, round-trip
- /api/gate/{n}/decide    the participatory vocabulary guard (ambiguous re-presents; only an
                          explicit 'approve' executes; 'reject' rejects)
- /api/drive/{n}/forge    a forged plan hash is rejected by the tamper check, hold stays open
- /api/gate/pending       held approvals exposed server-side (survive refresh / second tab)

No network, no T1 required — the demo server drives the in-process sim.
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
    monkeypatch.setattr(ds, "STATE", console)
    monkeypatch.setattr(capp, "STATE", console)
    monkeypatch.setattr(ds, "SimTools", lambda *a, **k: SimTools(client=sim_client))
    # airplane-mode: any real model call would come through venice._post; keep it un-mocked
    # here but point rationale at a stub so the slow path completes deterministically.
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    venice.reset_model_calls()
    ds._PENDING.clear()
    capp._TAMPER_BACKUP.clear()
    return ds, console, TestClient(ds.app)


# --------------------------------------------------------------------------- #
# model-call counter
# --------------------------------------------------------------------------- #
def test_model_calls_zero_on_the_airplane_path(demo):
    _ds, _console, client = demo
    assert client.get("/api/model-calls").json()["model_calls"] == 0
    client.post("/api/drive/2")                       # a full drive with venice stubbed
    # no successful venice._post happened, so the honest counter stays at 0
    assert client.get("/api/model-calls").json()["model_calls"] == 0


# --------------------------------------------------------------------------- #
# REAL tamper + restore round-trip against the real verifier
# --------------------------------------------------------------------------- #
def test_real_tamper_fails_the_chain_then_restore_fixes_it(demo):
    _ds, console, client = demo
    client.post("/api/drive/1")                       # produce real audit rows
    assert client.get("/api/audit/verify").json()["verified"] is True

    seq = console.conn.execute(
        "SELECT seq FROM audit_log WHERE event_type='approval_decided' "
        "ORDER BY seq DESC LIMIT 1").fetchone()["seq"]
    t = client.post(f"/api/audit/tamper?seq={seq}").json()
    assert t["ok"] and t["tampered_seq"] == seq and t["verified"] is False
    assert client.get("/api/audit/verify").json()["verified"] is False   # REAL verifier fails

    r = client.post("/api/audit/restore").json()
    assert r["ok"] and r["verified"] is True
    assert client.get("/api/audit/verify").json()["verified"] is True    # round-trip clean


def test_tamper_default_targets_the_newest_row(demo):
    _ds, _console, client = demo
    client.post("/api/drive/1")
    t = client.post("/api/audit/tamper").json()       # no seq -> newest row
    assert t["ok"] and t["verified"] is False
    client.post("/api/audit/restore")
    assert client.get("/api/audit/verify").json()["verified"] is True


# --------------------------------------------------------------------------- #
# participatory vocabulary guard  (agents.watcher.decide_from_reply)
# --------------------------------------------------------------------------- #
def _audit_types(conn, incident_id):
    rows = conn.execute("SELECT event_type FROM audit_log WHERE payload LIKE ?",
                        (f'%"{incident_id}"%',)).fetchall()
    return [r["event_type"] for r in rows]


def test_gate_decide_ambiguous_represents_never_executes(demo):
    _ds, console, client = demo
    client.post("/api/drive/1?hold=true")
    for txt in ("ok go ahead", "yes please", "sounds good, what does this do?", "don't approve"):
        r = client.post(f"/api/gate/1/decide?text={txt}").json()
        assert r["verdict"] == "represent", f"{txt!r} must re-present, not execute"
    assert "verified" not in _audit_types(console.conn, "INC-1")   # nothing ran


def test_gate_decide_explicit_approve_executes_and_names_the_visitor(demo):
    _ds, console, client = demo
    client.post("/api/drive/1?hold=true")
    r = client.post("/api/gate/1/decide?text=approve&principal=Priya").json()
    assert r["verdict"] == "approve" and r["verified"] is True
    row = console.conn.execute(
        "SELECT payload FROM audit_log WHERE event_type='approval_decided' "
        "AND payload LIKE '%INC-1%' ORDER BY seq DESC LIMIT 1").fetchone()
    assert row is not None and "Priya" in row["payload"]    # the visitor is the principal


def test_gate_decide_reject(demo):
    _ds, console, client = demo
    client.post("/api/drive/1?hold=true")
    r = client.post("/api/gate/1/decide?text=no, reject").json()
    assert r["verdict"] == "reject"
    assert "verified" not in _audit_types(console.conn, "INC-1")


# --------------------------------------------------------------------------- #
# forged plan hash is rejected; the honest hold stays open
# --------------------------------------------------------------------------- #
def test_forge_is_rejected_and_leaves_the_hold_open(demo):
    ds, console, client = demo
    hold = client.post("/api/drive/1?hold=true").json()
    real_hash = hold["plan_hash"]
    f = client.post("/api/drive/1/forge?principal=attacker").json()
    assert f["status"] == "rejected"
    assert "verified" not in _audit_types(console.conn, "INC-1")     # nothing executed
    # the tamper check saw a plan hash that does NOT match the prepared plan
    row = console.conn.execute(
        "SELECT payload FROM audit_log WHERE event_type='approval_decided' "
        "ORDER BY seq DESC LIMIT 1").fetchone()
    assert row is not None and real_hash not in row["payload"]       # a forged (non-matching) hash
    # ...and the genuine hold is still approvable afterwards
    a = client.post("/api/gate/1/decide?text=approve&principal=Priya").json()
    assert a["verdict"] == "approve" and a["verified"] is True


# --------------------------------------------------------------------------- #
# server-side pending approvals (survive refresh / second tab)
# --------------------------------------------------------------------------- #
def test_gate_pending_exposes_the_held_card_server_side(demo):
    _ds, _console, client = demo
    assert client.get("/api/gate/pending").json()["pending"] == []
    client.post("/api/drive/1?hold=true")
    pend = client.get("/api/gate/pending").json()["pending"]
    assert len(pend) == 1
    card = pend[0]
    assert card["n"] == 1 and card["plan_hash"] and len(card["plan_hash"]) == 64
    p = card["preview"]
    assert p["pre_state"] and p["planned"] and p["rollback_ref"]
