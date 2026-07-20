"""WP-CONSOLE — the authoritative pure-Python gate for the case-file console.

Drives the product surface exactly as a browser does — over HTTP against the mounted console app
(``/api/*`` read endpoints + ``/v1/gate/*``) with a real per-cookie session — and asserts the
load-bearing product claims:

  * the case-file INDEX + the drivable incident set are served;
  * the PIVOTAL invariant: on a needs-approval record the pre-state snapshot + typed inverse are
    shown BEFORE execution (safety_net present, NO ``executed`` row yet), and AFTER a four-eyes
    approval the armed plan_hash byte-matches the executed plan_hash;
  * four-eyes: the proposer cannot approve its own proposal (self-approval is a non-action);
  * the SEALED pack verifies OFFLINE (byte-identical to verify_pack.py) and the /verify endpoint
    returns a row-by-row chain result; a DENIAL is a complete, valid record that leaks no content;
  * the No-LLM decision path makes zero model calls and lights the scoped badge;
  * the ladder: promote is eligibility-gated + audited + names the principal; revoke demotes +
    audits + names; an unregistered principal is a non-action (fail-closed); an injected
    verification failure auto-demotes a Standing class live.

This is the AUTHORITATIVE gate; tests/e2e/test_product_console_e2e.py is the (collection-guarded)
browser companion.
"""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from console.demo_state import SCHED_CLASS_STANDING
from gate.world import build_seeded_world
from precedent import venice

PUBLISHER_CLASS = "publisher|PUB-4012|schedule_item"   # INC-1's class — cold-open L1 (slow path)


@pytest.fixture
def client():
    from console.app import app
    venice.reset_model_calls()
    with TestClient(app) as c:
        c.get("/api/incidents")          # establish the per-cookie session
        yield c


@pytest.fixture(scope="module")
def bodies(tmp_path_factory):
    """The seeded incident bodies (same cold-open template ⇒ same object_ids as the app session)."""
    d = tmp_path_factory.mktemp("ref")
    world = build_seeded_world(d)
    out = {n: world.tools.incident(n) for n in (1, 2, 3)}
    world.close()
    return out


def _pb(inc: dict, principal: str, **over) -> dict:
    b = {"incident_id": inc["incident_id"], "principal": principal, "raw_text": inc["raw_text"],
         "source": "sim", "observed_at": inc["observed_at"], "structured": inc["structured"]}
    b.update(over)
    return b


def _session(client):
    from console.session import COOKIE_NAME, SESSIONS
    sid = client.cookies.get(COOKIE_NAME)
    return SESSIONS.get(sid)


def _audit_rows(client):
    conn = _session(client).state.conn
    with _session(client).state._lock:
        return [{"event_type": r["event_type"], "actor": r["actor"], "payload": r["payload"]}
                for r in conn.execute(
                    "SELECT event_type, actor, payload FROM audit_log ORDER BY seq").fetchall()]


# --------------------------------------------------------------------------- #
# read surface
# --------------------------------------------------------------------------- #
def test_console_page_and_read_endpoints(client):
    assert client.get("/console").status_code == 200
    incs = client.get("/api/incidents").json()["incidents"]
    assert [i["incident_id"] for i in incs] == ["INC-1", "INC-2", "INC-3"]
    assert all(i["available"] and i["structured"] for i in incs)
    cf = client.get("/api/case-files").json()["case_files"]
    assert [c["incident_id"] for c in cf] == ["INC-1", "INC-2", "INC-3"]
    assert all(c["has_record"] is False for c in cf)   # cold open: nothing filed yet


# --------------------------------------------------------------------------- #
# THE PIVOTAL INVARIANT — safety net armed BEFORE execution
# --------------------------------------------------------------------------- #
def test_safety_net_shown_before_execution_then_binds_to_executed(client, bodies):
    # Propose the slow-path incident: needs a four-eyes approval, nothing has executed yet.
    r = client.post("/v1/gate/propose", json=_pb(bodies[1], "scheduling-ops")).json()
    assert r["decision"] == "needs-approval"
    ref = r["ref"]

    rec = client.get("/api/case-file/INC-1").json()
    sn = rec["safety_net"]
    assert sn is not None, "the rollback must be armed on a needs-approval record"
    assert sn["pre_state_snapshot_ref"].startswith("snapshot:INC-1:")
    assert sn["inverse"]["tool"] == "restore"                     # pre-generated typed inverse
    assert sn["inverse"]["target"]["object_type"]                 # a concrete target object
    assert sn["plan_hash"]
    # BEFORE execution: the armed plan is not yet matched to any executed row, and there is NO
    # `executed` event in the transcript — the undo exists before any typed call runs.
    assert sn["plan_hash_matches_execution"] is None
    events = [e["event_type"] for e in rec["execution_transcript"]]
    assert "executed" not in events
    assert "gate_needs_approval" in events

    # Approve as a DISTINCT registered principal (four-eyes), which executes-in-sim.
    o = client.post("/v1/gate/outcome",
                    json={"ref": ref, "decision": "approve",
                          "approver_principal": "ops-lead"}).json()
    assert o["executed"] and o["verified"]

    rec2 = client.get("/api/case-file/INC-1").json()
    sn2 = rec2["safety_net"]
    assert sn2["plan_hash_matches_execution"] is True             # armed hash == executed hash
    assert sn2["plan_hash"] == sn["plan_hash"]                    # the SAME plan, not a swapped one
    events2 = [e["event_type"] for e in rec2["execution_transcript"]]
    assert "executed" in events2 and "verified" in events2


def test_proposer_cannot_approve_own_proposal(client, bodies):
    r = client.post("/v1/gate/propose", json=_pb(bodies[1], "scheduling-ops")).json()
    # The proposer signs its OWN approval — four-eyes rejects it, nothing executes.
    o = client.post("/v1/gate/outcome",
                    json={"ref": r["ref"], "decision": "approve",
                          "approver_principal": "scheduling-ops"}).json()
    assert o["executed"] is False
    assert o["outcome"] == "self_approval_rejected"


# --------------------------------------------------------------------------- #
# sealed pack + offline verifier + denial-without-leak
# --------------------------------------------------------------------------- #
def test_standing_pack_verifies_offline_and_downloads(client, bodies):
    r = client.post("/v1/gate/propose", json=_pb(bodies[2], "scheduling-ops")).json()
    assert r["decision"] == "allow-standing"
    client.post("/v1/gate/outcome", json={"ref": r["ref"]})

    # sealed canonical bytes verify with the REAL stdlib verifier (byte-identical to the page)
    import verify_pack as vp
    resp = client.get("/api/pack/INC-2")
    assert resp.headers["content-disposition"].endswith('"INC-2.pack.json"')
    pack = json.loads(resp.text)
    assert vp.verify_pack(pack) == []                             # zero tamper findings

    v = client.get("/api/pack/INC-2/verify").json()
    assert v["verified"] is True
    assert v["expected_len"] == len(v["rows"]) > 0
    assert all(row["prev_ok"] and row["hash_ok"] for row in v["rows"])

    html = client.get("/api/pack/INC-2.html")
    assert html.status_code == 200 and "pack-json" in html.text  # self-contained embedded bytes

    rec = client.get("/api/case-file/INC-2").json()
    assert rec["no_llm_badge_lit"] is True
    assert rec["live_model_calls"] == 0                           # zero-LLM decision path


def test_denial_is_a_complete_record_that_leaks_no_content(client, bodies):
    r = client.post("/v1/gate/propose", json=_pb(bodies[3], "scheduling-ops")).json()
    assert r["decision"] == "deny" and r["reason"] == "restricted"

    rec = client.get("/api/case-file/INC-3").json()
    assert rec["decision"]["decision"] == "deny"
    assert rec["decision"]["denied_owner_team"]                   # discloses the owning team...
    assert rec["retrieved_precedent"]["redacted"] is True         # ...content withheld, fail-closed
    # NOTHING of the restricted remediation content — not in the case file, NOR the SEALED pack.
    import verify_pack as vp
    pack = json.loads(client.get("/api/pack/INC-3").text)
    for surface in (json.dumps(rec).lower(), json.dumps(pack).lower()):
        for secret in ("takedown", "republish per rights", "rights runbook", "dedupe"):
            assert secret not in surface, f"denial leaked restricted content: {secret!r}"

    # A denial is still a complete, valid, self-verifying record — the re-sealed pack still
    # verifies OFFLINE with the real stdlib verifier and via the endpoint.
    assert vp.verify_pack(pack) == []
    assert client.get("/api/pack/INC-3/verify").json()["verified"] is True


def test_zero_model_calls_across_the_whole_flow(client, bodies):
    for n in (1, 2, 3):
        client.post("/v1/gate/propose", json=_pb(bodies[n], "scheduling-ops"))
    assert client.get("/api/model-calls").json()["model_calls"] == 0


# --------------------------------------------------------------------------- #
# ladder — promote (eligibility-gated, audited, named) / revoke / auto-demote
# --------------------------------------------------------------------------- #
def test_ladder_state_served(client):
    lad = client.get("/api/ladder").json()
    keys = {r["class_key"]: r for r in lad["ladder"]}
    assert SCHED_CLASS_STANDING in keys
    assert keys[SCHED_CLASS_STANDING]["level"] == "STANDING"      # cold-open pre-promoted
    assert keys[SCHED_CLASS_STANDING]["promoted_by"]             # names the promoter
    assert lad["standing_label"] == "Standing Approval"          # never "Autonomous"


def test_unregistered_principal_cannot_promote_or_revoke(client):
    for path in ("/api/ladder/promote", "/api/ladder/revoke"):
        r = client.post(path, json={"class_key": SCHED_CLASS_STANDING, "principal": "mallory"})
        assert r.status_code == 403
        assert r.json()["reason"] == "unregistered_principal"


def test_promote_is_eligibility_gated_audited_and_named(client):
    from precedent import ladder
    # Not eligible yet → the endpoint is a fail-closed non-action.
    denied = client.post("/api/ladder/promote",
                         json={"class_key": PUBLISHER_CLASS, "principal": "ops-lead"}).json()
    assert denied["ok"] is False and "not_eligible" in denied["reason"]

    # Seed real eligibility (L2 with 3 consecutive verified) on THIS session's world, then promote.
    sess = _session(client)
    with sess.state._lock:
        ladder._upsert(sess.state.conn, PUBLISHER_CLASS, level="L2", count=3)
        sess.state.conn.commit()
    ok = client.post("/api/ladder/promote",
                     json={"class_key": PUBLISHER_CLASS, "principal": "ops-lead"}).json()
    assert ok["ok"] is True and ok["level"] == "STANDING"

    rows = _audit_rows(client)
    promo = [r for r in rows if r["event_type"] == "class_promoted"
             and PUBLISHER_CLASS in (r["payload"] or "")]
    assert promo and promo[-1]["actor"] == "ops-lead"            # audited + names the principal


def test_revoke_demotes_audited_and_named(client):
    r = client.post("/api/ladder/revoke",
                    json={"class_key": SCHED_CLASS_STANDING, "principal": "ops-lead"}).json()
    assert r["ok"] is True and r["level"] == "L1"
    lad = {x["class_key"]: x for x in client.get("/api/ladder").json()["ladder"]}
    assert lad[SCHED_CLASS_STANDING]["level"] == "L1"
    rows = _audit_rows(client)
    dem = [r for r in rows if r["event_type"] == "class_demoted"
           and SCHED_CLASS_STANDING in (r["payload"] or "")]
    assert dem and dem[-1]["actor"] == "ops-lead"


def test_injected_verification_failure_auto_demotes_a_standing_class(client, bodies):
    from precedent import ladder
    # Promote the publisher class to Standing (seed eligibility, then the real endpoint).
    sess = _session(client)
    with sess.state._lock:
        ladder._upsert(sess.state.conn, PUBLISHER_CLASS, level="L2", count=3)
        sess.state.conn.commit()
    client.post("/api/ladder/promote", json={"class_key": PUBLISHER_CLASS, "principal": "ops-lead"})
    lad = {x["class_key"]: x for x in client.get("/api/ladder").json()["ladder"]}
    assert lad[PUBLISHER_CLASS]["level"] == "STANDING"

    # Inject a verification failure, then drive the (now-standing) incident: it executes on the
    # fast path, verification FAILS, the pre-state snapshot is restored, and the class auto-demotes.
    assert client.post("/api/sim/arm-flake").json()["ok"] is True
    r = client.post("/v1/gate/propose", json=_pb(bodies[1], "scheduling-ops")).json()
    assert r["decision"] == "allow-standing"
    o = client.post("/v1/gate/outcome", json={"ref": r["ref"]}).json()
    assert o["rolled_back"] is True and o["verified"] is False

    lad2 = {x["class_key"]: x for x in client.get("/api/ladder").json()["ladder"]}
    assert lad2[PUBLISHER_CLASS]["level"] == "L1", "a verification failure must auto-demote to L1"
    assert any(r["event_type"] == "class_demoted" for r in _audit_rows(client))

    # The rolled-back record is still a complete, self-verifying case file with a rollback stage.
    rec = client.get("/api/case-file/INC-1").json()
    assert rec["verification"]["outcome"] == "rolled_back"
    assert rec["rollback"] is not None
    assert client.get("/api/pack/INC-1/verify").json()["verified"] is True
