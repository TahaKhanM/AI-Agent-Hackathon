"""End-to-end tests for the versioned HTTP Gate API (gate/ — WP-API).

Every gate operation is driven THROUGH the HTTP surface (fastapi.testclient.TestClient on the
standalone gate app) against a freshly-seeded backing world. The world's conn is inspected only
for the final audit-chain assertion (the test owns the world it seeded).

Proves, at the product spine:
  * the full slow path: propose (needs-approval) → decision (pending) → approve+execute-in-sim
    → verify → the hash-chained audit log verifies with expected_len/tail anchors;
  * the Standing-Approval zero-LLM fast path (allow-standing);
  * NO LLM in the decision path — a full propose→decide→outcome cycle makes 0 model-backend
    calls (a spy on the single network seam), and the decision-path source imports no backend.
    Stubbing an LLM into the path trips the spy;
  * fail-closed TTL — a pending approval past its TTL is a non-action via decision AND outcome,
    with a fail-closed audit row and NO execution;
  * deny paths — an unknown class (denied before any extractor LLM branch) and an ACL-restricted
    fix (the principal cannot access the documented remediation).
"""
from __future__ import annotations

import pathlib
from datetime import timedelta
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from console.demo_state import SCHED_CLASS_STANDING
from gate.api import create_gate_app
from gate.world import build_seeded_world
from precedent import venice
from precedent_memory import audit
from precedent_memory import db as memdb

GATE = "/v1/gate"


def _earn_scheduler_standing(c):
    """WP-DEMO §b: the cold-open template NO LONGER pre-promotes the scheduler class (it opens at
    L2/streak-0). Earn STANDING on THIS client's per-cookie session (the ladder's force pre-seed
    path — legitimate test setup) so INC-2 fast-paths to allow-standing on the mounted console."""
    from console.session import COOKIE_NAME, SESSIONS
    from precedent import ladder
    c.get("/api/incidents")  # mint the per-cookie session first
    sess = SESSIONS.get(c.cookies.get(COOKIE_NAME))
    with sess.state._lock:
        ladder.promote(SCHED_CLASS_STANDING, "ops-lead", conn=sess.state.conn, force=True)


# --------------------------------------------------------------------------- fixtures
@pytest.fixture
def make_gate(tmp_path):
    """Factory → a SimpleNamespace(client, world) over a freshly-seeded gate app. Each world is
    torn down (sim TestClient + memory conn closed) at test end — no FD/orphan-db leak."""
    made: list[tuple[TestClient, object]] = []

    def _make(*, standing: tuple[str, ...] = (), sub: str = "world") -> SimpleNamespace:
        d = tmp_path / sub
        d.mkdir(parents=True, exist_ok=True)
        world = build_seeded_world(d, standing_classes=tuple(standing))
        client = TestClient(create_gate_app(world))
        made.append((client, world))
        return SimpleNamespace(client=client, world=world)

    yield _make
    for client, world in made:
        client.close()
        world.close()


def _propose_body(sim_incident: dict, principal: str, **over) -> dict:
    body = {
        "incident_id": sim_incident["incident_id"],
        "principal": principal,
        "raw_text": sim_incident["raw_text"],
        "source": "sim",
        "observed_at": sim_incident["observed_at"],
        "structured": sim_incident["structured"],
    }
    body.update(over)
    return body


def _audit_kinds(world) -> set[str]:
    return {r["event_type"]
            for r in world.conn.execute("SELECT event_type FROM audit_log").fetchall()}


class _Spy:
    """Counts every invocation of the single model-backend network seam (venice._post). If the
    decision path stays LLM-free, the count is 0; a stubbed LLM call trips it."""

    def __init__(self) -> None:
        self.n = 0

    def __call__(self, *_a, **_k) -> dict:
        self.n += 1
        return {"choices": [{"message": {"content": "[[spy]]"}}]}


def _install_model_spy(monkeypatch) -> _Spy:
    """Replace the single model-backend network seam with a counting spy. Clears the response
    cache first so a cached answer can never mask a stubbed LLM call (keeps the mutation-catching
    guarantee: any LLM call in the decision path trips the spy)."""
    spy = _Spy()
    monkeypatch.setattr(venice, "_post", spy)
    venice._MEM_CACHE.clear()
    venice.reset_model_calls()
    return spy


# --------------------------------------------------------------------------- slow path e2e
def test_needs_approval_cycle_end_to_end(make_gate):
    env = make_gate(sub="slow")
    inc = env.world.tools.incident(1)                       # publisher|PUB-4012 (public runbook)

    r = env.client.post(f"{GATE}/propose", json=_propose_body(inc, "scheduling-ops"))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["decision"] == "needs-approval"
    ref, plan_hash = body["ref"], body["plan_hash"]
    assert ref and plan_hash and body["expires_at"]

    d = env.client.get(f"{GATE}/decision/{ref}")
    assert d.status_code == 200 and d.json()["status"] == "pending"

    o = env.client.post(f"{GATE}/outcome",
                        json={"ref": ref, "decision": "approve", "approver_principal": "ops-lead"})
    assert o.status_code == 200, o.text
    out = o.json()
    assert out["executed"] is True and out["verified"] is True and out["rolled_back"] is False
    assert out["outcome"] == "resolved"

    # After execution the decision reads approved.
    assert env.client.get(f"{GATE}/decision/{ref}").json()["status"] == "approved"

    # The hash-chained audit log verifies with the length + tail anchors (truncation-proof).
    conn = env.world.conn
    rows = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
    tail = conn.execute("SELECT hash FROM audit_log ORDER BY seq DESC LIMIT 1").fetchone()[0]
    assert audit.verify_chain(conn=conn, expected_len=rows, expected_tail_hash=tail) is True

    kinds = _audit_kinds(env.world)
    assert {"gate_needs_approval", "approval_decided", "executed", "verified",
            "memory_stored", "gate_outcome_recorded"} <= kinds


def test_replay_after_outcome_is_non_action(make_gate):
    env = make_gate(sub="replay")
    inc = env.world.tools.incident(1)
    ref = env.client.post(f"{GATE}/propose",
                          json=_propose_body(inc, "scheduling-ops")).json()["ref"]
    env.client.post(f"{GATE}/outcome",
                    json={"ref": ref, "decision": "approve", "approver_principal": "ops-lead"})
    # A second outcome on the SAME ref must NOT re-execute (consumed).
    again = env.client.post(f"{GATE}/outcome",
                            json={"ref": ref, "decision": "approve",
                                  "approver_principal": "ops-lead"}).json()
    assert again["executed"] is False
    assert "already decided" in again["detail"]


def test_two_proposes_same_plan_execute_once(make_gate):
    """Finding 2/6: two propose() calls for the SAME (incident, plan_hash) mint DISTINCT refs;
    approving+outcoming BOTH must execute the plan EXACTLY ONCE. The second outcome is bound to
    the durable (incident, plan) ledger — already-decided ⇒ non-action + an audit row."""
    env = make_gate(sub="double")
    inc = env.world.tools.incident(1)
    body = _propose_body(inc, "scheduling-ops")

    b1 = env.client.post(f"{GATE}/propose", json=body).json()
    b2 = env.client.post(f"{GATE}/propose", json=body).json()
    assert b1["decision"] == b2["decision"] == "needs-approval"
    assert b1["ref"] != b2["ref"], "each propose returns a distinct ref"
    assert b1["plan_hash"] == b2["plan_hash"], "same (incident, plan) ⇒ same durable ledger row"

    o1 = env.client.post(f"{GATE}/outcome",
                         json={"ref": b1["ref"], "decision": "approve",
                               "approver_principal": "ops-lead"}).json()
    assert o1["executed"] is True and o1["outcome"] == "resolved"

    o2 = env.client.post(f"{GATE}/outcome",
                         json={"ref": b2["ref"], "decision": "approve",
                               "approver_principal": "ops-lead"}).json()
    assert o2["executed"] is False, "the duplicate ref must NOT re-execute"
    assert o2["outcome"] == "approved"                     # the prior durable outcome
    assert "already decided" in o2["detail"]

    # EXACTLY ONE execution across the two refs, and the replay wrote its audit row (finding 6).
    conn = env.world.conn
    n_exec = conn.execute(
        "SELECT COUNT(*) FROM audit_log WHERE event_type='executed'").fetchone()[0]
    assert n_exec == 1, "the plan executed once, not twice"
    assert "gate_already_decided" in _audit_kinds(env.world)


def test_self_approval_rejected_four_eyes(make_gate):
    """Finding 5: separation of duties — the PROPOSER cannot approve its own proposal (non-action
    + a gate_self_approval_rejected audit row). A DISTINCT registered approver works."""
    env = make_gate(sub="four-eyes")
    inc = env.world.tools.incident(1)

    ref = env.client.post(f"{GATE}/propose",
                          json=_propose_body(inc, "scheduling-ops")).json()["ref"]
    self_o = env.client.post(f"{GATE}/outcome",
                             json={"ref": ref, "decision": "approve",
                                   "approver_principal": "scheduling-ops"}).json()
    assert self_o["executed"] is False and self_o["outcome"] == "self_approval_rejected"
    kinds = _audit_kinds(env.world)
    assert "gate_self_approval_rejected" in kinds
    assert "executed" not in kinds and "verified" not in kinds   # nothing ran

    # The correct four-eyes pattern: propose as scheduling-ops, approve as a DIFFERENT principal.
    ref2 = env.client.post(f"{GATE}/propose",
                           json=_propose_body(inc, "scheduling-ops")).json()["ref"]
    ok = env.client.post(f"{GATE}/outcome",
                         json={"ref": ref2, "decision": "approve",
                               "approver_principal": "ops-lead"}).json()
    assert ok["executed"] is True and ok["outcome"] == "resolved"


# --------------------------------------------------------------------------- fast path e2e
def test_standing_allow_fast_path_is_zero_llm(make_gate, monkeypatch):
    env = make_gate(standing=(SCHED_CLASS_STANDING,), sub="standing")
    inc = env.world.tools.incident(2)                       # scheduler|SCH-DUP-002 (promoted)

    spy = _install_model_spy(monkeypatch)

    r = env.client.post(f"{GATE}/propose", json=_propose_body(inc, "scheduling-ops"))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["decision"] == "allow-standing"
    ref = body["ref"]
    assert env.client.get(f"{GATE}/decision/{ref}").json()["status"] == "approved"

    o = env.client.post(f"{GATE}/outcome", json={"ref": ref}).json()   # no human decision needed
    assert o["executed"] is True and o["verified"] is True and o["outcome"] == "resolved"

    # The zero-LLM proof: the whole fast-path cycle made no model-backend call.
    assert spy.n == 0
    assert venice.model_call_count() == 0


# --------------------------------------------------------------------------- no-LLM proof
def test_full_cycle_makes_zero_model_calls(make_gate, monkeypatch):
    env = make_gate(sub="nollm")
    inc = env.world.tools.incident(1)

    spy = _install_model_spy(monkeypatch)

    ref = env.client.post(f"{GATE}/propose",
                          json=_propose_body(inc, "scheduling-ops")).json()["ref"]
    env.client.get(f"{GATE}/decision/{ref}")
    env.client.post(f"{GATE}/outcome",
                    json={"ref": ref, "decision": "approve", "approver_principal": "ops-lead"})

    assert spy.n == 0, "an LLM was called inside the gate decision path"
    assert venice.model_call_count() == 0


def test_gate_decision_path_imports_no_model_backend():
    """Mirror tests/test_venice.py's source scan: the gate's decision-path modules import no
    model backend, defer the prose LLM, and never fill it inside a decision (rule 2)."""
    base = pathlib.Path(__file__).resolve().parent.parent / "gate"
    for name in ("service.py", "api.py", "models.py", "world.py", "__init__.py"):
        src = (base / name).read_text().lower()
        assert "venice" not in src, f"gate/{name} references the model backend"
        assert "import" in src
    svc = (base / "service.py").read_text()
    assert "defer_rationale=True" in svc          # the decision never triggers the SMART prose
    assert "fill_rationale" not in svc            # ...and never fills it


# --------------------------------------------------------------------------- fail-closed TTL
def test_pending_past_ttl_is_non_action(make_gate, monkeypatch):
    env = make_gate(sub="ttl")
    inc = env.world.tools.incident(1)
    body = env.client.post(f"{GATE}/propose",
                           json=_propose_body(inc, "scheduling-ops")).json()
    ref = body["ref"]
    assert body["decision"] == "needs-approval"

    # Advance the clock past the 10-minute TTL (the whole system reads db.utcnow).
    real_now = memdb.utcnow()
    monkeypatch.setattr(memdb, "utcnow", lambda: real_now + timedelta(minutes=11))

    d = env.client.get(f"{GATE}/decision/{ref}").json()
    assert d["status"] == "expired"

    o = env.client.post(f"{GATE}/outcome",
                        json={"ref": ref, "decision": "approve",
                              "approver_principal": "ops-lead"}).json()
    assert o["executed"] is False and o["outcome"] == "expired"

    kinds = _audit_kinds(env.world)
    assert "gate_expired_nonaction" in kinds       # the fail-closed audit row
    assert "executed" not in kinds and "verified" not in kinds   # nothing ran


def test_outcome_past_ttl_without_decision_is_non_action(make_gate, monkeypatch):
    """Finding 4: the report_outcome TTL guard is the SUT directly. POST /outcome on a PAST-TTL
    pending ref WITHOUT calling /decision first (the earlier test hit /decision, which consumed
    the ref, so a neutered outcome-side guard still looked green — vacuous). Expect NO execution,
    outcome=='expired', a gate_expired_nonaction row, and nothing executed."""
    env = make_gate(sub="ttl-outcome")
    inc = env.world.tools.incident(1)
    body = env.client.post(f"{GATE}/propose",
                           json=_propose_body(inc, "scheduling-ops")).json()
    assert body["decision"] == "needs-approval"
    ref = body["ref"]

    real_now = memdb.utcnow()
    monkeypatch.setattr(memdb, "utcnow", lambda: real_now + timedelta(minutes=11))

    # Straight to /outcome — no /decision call — so report_outcome's OWN fail-closed TTL is tested.
    o = env.client.post(f"{GATE}/outcome",
                        json={"ref": ref, "decision": "approve",
                              "approver_principal": "ops-lead"}).json()
    assert o["executed"] is False and o["outcome"] == "expired"

    kinds = _audit_kinds(env.world)
    assert "gate_expired_nonaction" in kinds                     # the fail-closed audit row
    assert "executed" not in kinds and "verified" not in kinds   # nothing ran


def test_absent_ref_is_non_action(make_gate):
    env = make_gate(sub="absent")
    d = env.client.get(f"{GATE}/decision/does-not-exist").json()
    assert d["status"] == "expired"
    o = env.client.post(f"{GATE}/outcome", json={"ref": "does-not-exist"}).json()
    assert o["executed"] is False and o["outcome"] == "absent"


# --------------------------------------------------------------------------- deny paths
def test_unknown_class_denied_without_llm(make_gate, monkeypatch):
    env = make_gate(sub="deny-unknown")
    spy = _install_model_spy(monkeypatch)

    body = {
        "incident_id": "INC-X",
        "principal": "scheduling-ops",
        "raw_text": "totally novel incident",
        "structured": {"service": "publisher", "error_code": "ZZZ-000",
                       "target_object_type": "schedule_item", "object_id": "1"},
    }
    r = env.client.post(f"{GATE}/propose", json=body).json()
    assert r["decision"] == "deny" and r["reason"] == "unknown_class"
    assert spy.n == 0          # denied BEFORE the extractor's LLM-proposal branch


def test_unknown_class_error_code_is_sanitised_in_audit(make_gate):
    """Finding 7: the unknown_class deny path logs a caller-supplied error_code into the
    hash-chained audit payload. An over-long / garbage code must be truncated (≤64) and charset-
    restricted before it enters the chain (log-injection + unbounded-payload defence)."""
    env = make_gate(sub="deny-sanitise")
    nasty = "ZZZ" + ("A" * 200) + "\n\t<script>drop;{}|payload injection"
    body = {
        "incident_id": "INC-X",
        "principal": "scheduling-ops",
        "raw_text": "novel",
        "structured": {"service": "publisher", "error_code": nasty,
                       "target_object_type": "schedule_item", "object_id": "1"},
    }
    r = env.client.post(f"{GATE}/propose", json=body).json()
    assert r["decision"] == "deny" and r["reason"] == "unknown_class"

    row = env.world.conn.execute(
        "SELECT payload FROM audit_log WHERE event_type='gate_denied' "
        "ORDER BY seq DESC LIMIT 1").fetchone()
    payload = row["payload"]
    assert "<script>" not in payload and "\n" not in payload and "|" not in payload
    assert "payload injection" not in payload
    # The logged code is the sanitised, capped form (alnum + -_. only, ≤64 chars).
    import json as _json
    logged = _json.loads(payload).get("error_code", "")
    assert len(logged) <= 64 and all(ch.isalnum() or ch in "-_." for ch in logged)


def test_acl_restricted_fix_is_denied(make_gate):
    env = make_gate(sub="deny-acl")
    inc = env.world.tools.incident(3)                # rights|RGT-EXCL-009 (RIGHTS-restricted)
    # scheduling-ops lacks the Rights-Ops grant → the documented fix is not accessible.
    r = env.client.post(f"{GATE}/propose", json=_propose_body(inc, "scheduling-ops")).json()
    assert r["decision"] == "deny" and r["reason"] == "restricted"


def test_unregistered_principal_is_denied(make_gate):
    env = make_gate(sub="deny-principal")
    inc = env.world.tools.incident(1)
    r = env.client.post(f"{GATE}/propose", json=_propose_body(inc, "mallory")).json()
    assert r["decision"] == "deny" and r["reason"] == "unregistered_principal"


def test_intended_action_mismatch_is_denied(make_gate):
    env = make_gate(sub="deny-action")
    inc = env.world.tools.incident(1)                       # PUB-4012 → policy action republish_epg
    r = env.client.post(f"{GATE}/propose",
                        json=_propose_body(inc, "scheduling-ops",
                                           intended_action="rights_takedown")).json()
    assert r["decision"] == "deny" and r["reason"] == "action_mismatch"


# --------------------------------------------------------------------------- mounted deploy
def test_mounted_on_console_app_end_to_end(tmp_path):
    """The gate is ONE deploy: mounted into console.app.app at /v1/gate and driven over HTTP
    against the CURRENT browser session's private world (the console dogfoods it). The cold-open
    session template pre-promotes the scheduler class, so INC-2 fast-paths to allow-standing."""
    from console.app import app as console_app

    ref_world = build_seeded_world(tmp_path / "ref")     # same cold-open template → same object_id
    inc2 = ref_world.tools.incident(2)
    ref_world.close()

    with TestClient(console_app) as c:                     # a real per-cookie session (jar reused)
        _earn_scheduler_standing(c)                        # WP-DEMO §b: no cold-open pre-promote
        r = c.post("/v1/gate/propose", json=_propose_body(inc2, "scheduling-ops"))
        assert r.status_code == 200, r.text
        assert r.json()["decision"] == "allow-standing"
        gref = r.json()["ref"]
        assert c.get(f"/v1/gate/decision/{gref}").json()["status"] == "approved"
        o = c.post("/v1/gate/outcome", json={"ref": gref}).json()
        assert o["executed"] is True and o["verified"] is True and o["outcome"] == "resolved"


def test_mounted_gate_enforces_registered_principals(tmp_path):
    """Finding 3: the console mount passes a CONCRETE principals set (DEFAULT_PRINCIPALS), so on
    the DEPLOYED path an unregistered, self-asserted principal is a non-action — proposing OR
    approving. Previously the mount passed principals=None (restriction OFF) → any claimed
    identity was accepted → an auth bypass."""
    from console.app import app as console_app

    ref_world = build_seeded_world(tmp_path / "ref")     # same cold-open template → same object_ids
    inc1 = ref_world.tools.incident(1)                   # publisher L1 → slow path (needs-approval)
    inc2 = ref_world.tools.incident(2)                   # scheduler standing → allow-standing
    ref_world.close()

    with TestClient(console_app) as c:
        _earn_scheduler_standing(c)                        # WP-DEMO §b: no cold-open pre-promote
        # (a) UNREGISTERED proposer → denied up front (fail-closed).
        deny = c.post("/v1/gate/propose", json=_propose_body(inc2, "mallory")).json()
        assert deny["decision"] == "deny" and deny["reason"] == "unregistered_principal"

        # (b) UNREGISTERED approver on a legitimately-held ref → rejected, nothing executes.
        held = c.post("/v1/gate/propose", json=_propose_body(inc1, "scheduling-ops")).json()
        assert held["decision"] == "needs-approval"
        rej = c.post("/v1/gate/outcome",
                     json={"ref": held["ref"], "decision": "approve",
                           "approver_principal": "mallory"}).json()
        assert rej["executed"] is False and rej["outcome"] == "rejected"

        # (c) a REGISTERED principal proposing + a DISTINCT registered approver still works.
        ok_prop = c.post("/v1/gate/propose", json=_propose_body(inc2, "scheduling-ops")).json()
        assert ok_prop["decision"] == "allow-standing"
