"""WP-BARRIER — five confirmed P0-barrier findings, each pinned by a failing test first (TDD).

Every new failure direction lands on NON-ACTION (fail-closed, Rule 3):

  1. rate-limit fail-open — a cookieless caller mints a FRESH session (+bucket) every request,
     bypassing the per-session limit and flooding session/world creation. A creation-rate limit
     (per-client + a global ceiling) is checked BEFORE minting; over-limit ⇒ 429, NO session.
  2. forged principal    — the state-changing console routes that NAME a principal now reject a
     principal not in gate.world.DEFAULT_PRINCIPALS (403, NO audit row), mirroring /api/ladder/*.
  3. standing double-exec— two propose() calls for the SAME standing (incident, plan) mint two
     refs; outcoming BOTH must execute EXACTLY once (the second ⇒ non-action + an audit row).
  4. reset resurrected ref— a gate pending-decision ref proposed BEFORE /api/demo/reset must be
     GONE (non-action) after the cold-open restart, not a resurrected pending decision.
  5. eviction × in-flight — an LRU cap-eviction must SKIP a session whose world lock is currently
     held; an in-flight op never hits a mid-op closed-conn crash and lands on a coherent state.
"""
from __future__ import annotations

import threading

import pytest
from fastapi.testclient import TestClient

from console import session as sessionmod
from precedent import venice

REGISTERED = "scheduling-ops"      # in gate.world.DEFAULT_PRINCIPALS
FORGED = "mallory"                 # NOT registered out-of-band


@pytest.fixture(autouse=True)
def _airplane(monkeypatch):
    """Never let a slow-path rationale reach a real model; keep drives deterministic + offline."""
    monkeypatch.setenv("PRECEDENT_AGENTS_OFFLINE", "1")
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    venice.reset_model_calls()
    yield


# --------------------------------------------------------------------------- #
# Finding 1 — cookieless session-creation flood is rate-limited (fail-closed)
# --------------------------------------------------------------------------- #
def test_cookieless_creation_flood_is_rate_limited_and_mints_nothing():
    import console.app as capp
    assert capp.STATE is None, "this test exercises the production per-cookie path"

    orig = (sessionmod._CREATION_CAPACITY, sessionmod._CREATION_REFILL_PER_S)
    sessionmod.configure_creation_limit(capacity=3, refill_per_s=0)   # 3 mints, no refill
    sessionmod.reset_creation_state()
    try:
        before = len(sessionmod.SESSIONS)
        codes = []
        for _ in range(10):
            c = TestClient(capp.app)                 # fresh cookie jar => a COOKIELESS request
            codes.append(c.get("/api/state").status_code)
        # The first 3 cookieless requests mint; the rest are 429 (fail-closed, NO session minted).
        assert codes[:3] == [200, 200, 200]
        assert codes[3:] == [429] * 7
        assert (len(sessionmod.SESSIONS) - before) <= 3, \
            "over-limit cookieless requests must mint NO sessions"
    finally:
        sessionmod.configure_creation_limit(*orig)
        sessionmod.reset_creation_state()


def test_creation_limit_does_not_penalise_a_cookie_persisting_visitor():
    """A well-behaved visitor (persisted cookie) mints exactly ONCE, then rides the same session —
    it must never trip the creation limit no matter how many requests it makes."""
    import console.app as capp
    orig = (sessionmod._CREATION_CAPACITY, sessionmod._CREATION_REFILL_PER_S)
    sessionmod.configure_creation_limit(capacity=1, refill_per_s=0)   # only ONE mint allowed
    sessionmod.reset_creation_state()
    try:
        c = TestClient(capp.app)                     # persists cookies across requests
        assert c.get("/api/state").status_code == 200            # the one allowed mint
        for _ in range(5):
            assert c.get("/api/state").status_code == 200, \
                "a cookie-persisting visitor never re-mints, so never trips the creation limit"
    finally:
        sessionmod.configure_creation_limit(*orig)
        sessionmod.reset_creation_state()


# --------------------------------------------------------------------------- #
# Finding 2 — a forged (unregistered) principal is a non-action on a naming route
# --------------------------------------------------------------------------- #
def _fresh_client():
    import console.app as capp
    c = TestClient(capp.app)
    c.post("/api/demo/reset")            # isolate on a cold-open per-cookie world
    return c


def _audit_rows_for(client, actor: str) -> int:
    sess = sessionmod.SESSIONS.get(client.cookies.get(sessionmod.COOKIE_NAME))
    with sess.state._lock:
        return sess.state.conn.execute(
            "SELECT COUNT(*) FROM audit_log WHERE actor = ?", (actor,)).fetchone()[0]


def test_forged_principal_on_approve_is_403_and_writes_no_audit_row():
    c = _fresh_client()
    r = c.post("/api/approve", json={"incident_id": "INC-1", "principal": FORGED})
    assert r.status_code == 403
    assert r.json()["reason"] == "unregistered_principal"
    assert _audit_rows_for(c, FORGED) == 0, "a forged principal must write NO audit row"


def test_registered_principal_on_approve_still_works():
    c = _fresh_client()
    r = c.post("/api/approve", json={"incident_id": "INC-1", "principal": REGISTERED})
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert _audit_rows_for(c, REGISTERED) >= 1, "a registered principal writes its audit row"


def test_forged_principal_on_revoke_is_403():
    c = _fresh_client()
    r = c.post("/api/revoke", json={"class_key": "publisher|PUB-4012|schedule_item",
                                    "principal": FORGED})
    assert r.status_code == 403 and r.json()["reason"] == "unregistered_principal"


# --------------------------------------------------------------------------- #
# Finding 3 — a STANDING ref executes EXACTLY once across two proposes
# --------------------------------------------------------------------------- #
def _standing_gate(tmp_path):
    from console.demo_state import SCHED_CLASS_STANDING
    from gate.api import create_gate_app
    from gate.world import build_seeded_world
    world = build_seeded_world(tmp_path / "standing2", standing_classes=(SCHED_CLASS_STANDING,))
    client = TestClient(create_gate_app(world))
    return client, world


def _propose_body(inc: dict) -> dict:
    return {
        "incident_id": inc["incident_id"],
        "principal": REGISTERED,
        "raw_text": inc["raw_text"],
        "source": "sim",
        "observed_at": inc["observed_at"],
        "structured": inc["structured"],
    }


def test_two_standing_proposes_execute_exactly_once(tmp_path):
    client, world = _standing_gate(tmp_path)
    try:
        inc = world.tools.incident(2)                      # scheduler|SCH-DUP-002 (STANDING)
        body = _propose_body(inc)

        b1 = client.post("/v1/gate/propose", json=body).json()
        b2 = client.post("/v1/gate/propose", json=body).json()
        assert b1["decision"] == b2["decision"] == "allow-standing"
        assert b1["ref"] != b2["ref"], "each propose returns a distinct ref"
        assert b1["plan_hash"] == b2["plan_hash"], "same (incident, plan) ⇒ same plan_hash"

        o1 = client.post("/v1/gate/outcome", json={"ref": b1["ref"]}).json()
        assert o1["executed"] is True and o1["outcome"] == "resolved"

        # The SECOND standing ref for an already-executed plan is a non-action (exactly-once).
        o2 = client.post("/v1/gate/outcome", json={"ref": b2["ref"]}).json()
        assert o2["executed"] is False, "the duplicate standing ref must NOT re-execute"
        assert "already decided" in o2["detail"]

        n_exec = world.conn.execute(
            "SELECT COUNT(*) FROM audit_log WHERE event_type='executed'").fetchone()[0]
        assert n_exec == 1, "the standing plan executed once, not twice"
        kinds = {r["event_type"] for r in world.conn.execute("SELECT event_type FROM audit_log")}
        assert "gate_already_decided" in kinds, "the replay wrote its non-action audit row"
    finally:
        client.close()
        world.close()


# --------------------------------------------------------------------------- #
# Finding 4 — a gate ref proposed BEFORE /api/demo/reset is GONE after the restart
# --------------------------------------------------------------------------- #
def test_gate_ref_is_gone_after_demo_reset():
    import console.app as capp
    c = TestClient(capp.app)
    incs = c.get("/api/incidents").json()["incidents"]
    inc1 = next(i for i in incs if i["incident_id"] == "INC-1")
    body = {
        "incident_id": "INC-1", "principal": REGISTERED,
        "raw_text": inc1["raw_text"], "source": "sim",
        "observed_at": inc1["observed_at"], "structured": inc1["structured"],
    }
    r = c.post("/v1/gate/propose", json=body).json()
    assert r["decision"] == "needs-approval"
    ref = r["ref"]
    assert c.get(f"/v1/gate/decision/{ref}").json()["status"] == "pending"

    # Cold-open restart: reset_world() must clear the per-session gate pending-decision refs.
    c.post("/api/demo/reset")

    # The pre-reset ref is GONE — an absent ref is a non-action (fail-closed), never resurrected.
    d = c.get(f"/v1/gate/decision/{ref}").json()
    assert d["status"] == "expired", "a ref proposed before reset must not survive the cold open"
    o = c.post("/v1/gate/outcome", json={
        "ref": ref, "decision": "approve", "approver_principal": "ops-lead"}).json()
    assert o["executed"] is False and o["outcome"] == "absent", \
        "outcoming a reset-cleared ref executes NOTHING (non-action)"


# --------------------------------------------------------------------------- #
# Finding 5 — an in-flight op on an evicting session never hits a mid-op closed conn
# --------------------------------------------------------------------------- #
def test_inflight_op_is_not_cap_evicted_midop():
    import console.app as capp
    assert capp.STATE is None
    store = sessionmod.SessionStore(ttl_seconds=1800, max_sessions=2)
    try:
        busy = store.resolve(None)                 # the stalest session (first created)
        started, release, result = threading.Event(), threading.Event(), {}

        def op() -> None:
            # Hold the world's single-writer lock across a conn op — the shape of a gate outcome.
            with busy.state._lock:
                started.set()
                release.wait(3.0)
                try:
                    result["value"] = busy.state.conn.execute("SELECT 1").fetchone()[0]
                    result["ok"] = True
                except Exception as e:               # noqa: BLE001 — record a mid-op closed conn
                    result["ok"] = False
                    result["err"] = repr(e)

        t = threading.Thread(target=op)
        t.start()
        assert started.wait(3.0), "the in-flight op acquired the world lock"

        # Force mints past the cap while `busy` is the stalest AND its lock is held. Cap-eviction
        # must SKIP the in-flight session and shed an idle one instead — never force-close it.
        for _ in range(4):
            store.resolve(None)
        assert store.get(busy.sid) is not None, "an in-flight session must never be cap-evicted"

        release.set()
        t.join(3.0)
        assert result.get("ok") is True, \
            f"the in-flight op saw a live conn (no mid-op close): {result.get('err')}"
    finally:
        store.close_all()


def test_close_does_not_force_close_a_locked_conn():
    """close() must not yank the conn out from under an in-flight op holding the world lock —
    the bounded wait expires into a NON-close (fail-safe), never a mid-op ProgrammingError."""
    store = sessionmod.SessionStore(ttl_seconds=1800)
    try:
        sess = store.resolve(None)
        held = threading.Event()
        proceed = threading.Event()

        def hold() -> None:
            with sess.state._lock:
                held.set()
                proceed.wait(3.0)

        t = threading.Thread(target=hold)
        t.start()
        assert held.wait(3.0)

        sess.close()                                 # bounded lock wait; must NOT close the conn
        # The op's world lock is still held → the conn stays live (no mid-op close).
        assert sess.state.conn.execute("SELECT 1").fetchone()[0] == 1

        proceed.set()
        t.join(3.0)
    finally:
        store.close_all()
