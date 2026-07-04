"""Fetch-rails behaviour tests — offline (PRECEDENT_AGENTS_OFFLINE=1, no mailbox/network).

Proves the Watcher->Librarian->Operator rails without a live Agentverse:
- the protocol messages construct and the two converters round-trip a Prepared
  through a PlanMsg with the plan_hash preserved (the tamper-check anchor);
- the Librarian's serve_retrieval permits scheduling-ops on the scheduler class,
  denies rights-ops, and leaks NO restricted body/secret on the denial (RULE 3);
- the Operator's serve_execution drives the REAL commit_execution kernel against a
  live in-process sim and returns verified=True on the STANDING fast-path;
- the chat gate binds the sender address verbatim and maps approve/reject replies;
- the approval TTL table records/looks-up, expires stale rows, and never yields an
  execution for an expired/absent approval;
- the Librarian imports NO model id (RULE 1/2);
- both README badges are present.
"""
from __future__ import annotations

import pathlib

import pytest
from fastapi.testclient import TestClient

from agents import approval
from agents.protocol import (
    PlanMsg,
    RetrievalResultMsg,
    TriageMsg,
    plan_msg_from_prepared,
    prepared_from_plan_msg,
)
from console.demo_state import DemoState
from precedent import ladder, orchestrator, venice
from precedent.contracts import ApprovalRequest, IncidentEvent
from precedent.tools import SimTools
from precedent_memory import db

REPO = pathlib.Path(__file__).resolve().parent.parent
SCHED_CK = "scheduler|SCH-DUP-002|schedule_item"
RIGHTS_CK = "rights|RGT-EXCL-009|vod_item"
RESTRICTED_FIX = "takedown + republish per rights runbook"


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    monkeypatch.setenv("PRECEDENT_AGENTS_OFFLINE", "1")
    yield


@pytest.fixture
def mem(tmp_path):
    """A seeded shared memory db (the 3 demo records + ACLs + principals) + a T1 conn."""
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
        c.get("/health")   # force idempotent build
        yield c


def _prepared_for(sim, mem_conn, n, principal="scheduling-ops"):
    payload = sim.incident(n)
    inc = IncidentEvent(incident_id=payload["incident_id"], raw_text=payload["raw_text"],
                        source="sim", observed_at=payload["observed_at"])
    return orchestrator.prepare(inc, structured=payload["structured"], conn=mem_conn,
                                tools=sim, principal=principal)


# --------------------------------------------------------------------------- #
# protocol messages + the two converters
# --------------------------------------------------------------------------- #
def test_protocol_messages_construct():
    tri = TriageMsg(incident_id="INC-2", class_key=SCHED_CK,
                    extraction_method="deterministic", principal="scheduling-ops")
    assert tri.class_key == SCHED_CK
    rr = RetrievalResultMsg(incident_id="INC-2", principal_id="scheduling-ops",
                            permitted=True, hit_count=1, denied_count=0)
    assert rr.permitted and rr.denied_owner_team is None


def test_converters_round_trip_preserve_plan_hash(sim_client, mem, monkeypatch):
    t1, _ = mem
    sim = SimTools(client=sim_client)
    ladder.promote(SCHED_CK, "ops-lead", conn=t1, force=True)   # STANDING -> fast_ready
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    prepared = _prepared_for(sim, t1, 2)
    assert prepared.outcome == "fast_ready" and prepared.plan is not None
    original_hash = prepared.plan.plan_hash

    msg = plan_msg_from_prepared(prepared, "standing", "agent1qsender")
    assert isinstance(msg, PlanMsg)
    assert msg.plan_hash == original_hash          # hash carried onto the wire

    rebuilt, decision = prepared_from_plan_msg(msg)
    assert rebuilt.plan.plan_hash == original_hash  # hash survives the round-trip
    assert rebuilt.fast is True and decision is None  # standing needs no decision
    assert rebuilt.class_key == SCHED_CK
    assert [(s.tool, s.args) for s in rebuilt.plan.steps] == \
           [(s.tool, s.args) for s in prepared.plan.steps]


def test_converter_human_decision_binds_sender(sim_client, mem, monkeypatch):
    t1, _ = mem
    sim = SimTools(client=sim_client)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    prepared = _prepared_for(sim, t1, 1)           # slow-path -> 'ready'
    assert prepared.outcome == "ready"
    msg = plan_msg_from_prepared(prepared, "approve", "agent1qHUMANsender")
    rebuilt, decision = prepared_from_plan_msg(msg)
    assert rebuilt.fast is False
    assert decision is not None
    assert decision.decision == "approve"
    assert decision.approver_principal == "agent1qHUMANsender"   # verbatim
    assert decision.channel == "chat"
    assert decision.plan_hash == prepared.plan.plan_hash


# --------------------------------------------------------------------------- #
# Librarian.serve_retrieval — permit / deny / no leak
# --------------------------------------------------------------------------- #
def test_serve_retrieval_permits_scheduling_ops(mem):
    from agents import librarian
    t1, _ = mem
    msg = TriageMsg(incident_id="INC-2", class_key=SCHED_CK,
                    extraction_method="deterministic", principal="scheduling-ops")
    res = librarian.serve_retrieval(msg, conn=t1)
    assert res.permitted is True and res.hit_count >= 1
    assert res.denied_owner_team is None


def test_serve_retrieval_denies_rights_ops_no_leak(mem):
    from agents import librarian
    t1, _ = mem
    msg = TriageMsg(incident_id="INC-3", class_key=RIGHTS_CK,
                    extraction_method="deterministic", principal="scheduling-ops")
    res = librarian.serve_retrieval(msg, conn=t1)
    # scheduling-ops lacks the Rights Ops constraint -> denied, owner disclosed only.
    assert res.permitted is False and res.hit_count == 0
    assert res.denied_count >= 1
    assert res.denied_owner_team == "Rights Ops"
    blob = res.model_dump_json()
    assert RESTRICTED_FIX not in blob      # no restricted fix content leaks
    assert "fp-rights" not in blob         # no fingerprint/title/body


def test_serve_retrieval_unresolved_class_is_denied(mem):
    from agents import librarian
    t1, _ = mem
    msg = TriageMsg(incident_id="INC-X", class_key=None,
                    extraction_method="llm_proposed", principal="scheduling-ops")
    res = librarian.serve_retrieval(msg, conn=t1)
    assert res.permitted is False and res.hit_count == 0 and res.denied_count == 0


# --------------------------------------------------------------------------- #
# Operator.serve_execution — fast-path verified against the real sim
# --------------------------------------------------------------------------- #
def test_serve_execution_fast_path_verifies(sim_client, mem, monkeypatch):
    from agents import operator
    t1, _ = mem
    sim = SimTools(client=sim_client)
    ladder.promote(SCHED_CK, "ops-lead", conn=t1, force=True)   # STANDING pre-seed

    def _boom(*a, **k):
        raise AssertionError("LLM called on the STANDING fast-path")
    monkeypatch.setattr(venice, "chat", _boom)
    monkeypatch.setattr(venice, "embed", _boom)

    prepared = _prepared_for(sim, t1, 2)
    assert prepared.fast is True
    msg = plan_msg_from_prepared(prepared, "standing", "agent1qsender")
    res = operator.serve_execution(msg, conn=t1, tools=sim)
    assert res.verified is True and res.rolled_back is False
    assert res.outcome == "resolved"
    assert res.audit_hash and len(res.audit_hash) == 64   # audit tail recorded
    assert any(q["incident_id"] == "INC-2" for q in operator.JIRA_QUEUE)  # write-behind


# --------------------------------------------------------------------------- #
# Chat gate — decision binding + reply mapping
# --------------------------------------------------------------------------- #
def _req():
    return ApprovalRequest(incident_id="INC-1", plan_hash="abc123", risk_class="standard_change",
                           ladder_level="L2", requested_at=db.utcnow_iso(),
                           expires_at=db.utcnow_iso(), channel="chat")


def test_make_decision_binds_sender_address():
    from agents import watcher
    sender = "agent1qw8xdemoSENDERaddress"
    decision = watcher.make_decision(_req(), sender)
    assert decision.approver_principal == sender    # verbatim identity
    assert decision.channel == "chat"
    assert decision.plan_hash == "abc123"


def test_decide_from_reply_maps_approve_and_reject():
    from agents import watcher
    # P0.2: only an explicit approve/reject token decides; bare "ok"/"yes"/"go"/"no"
    # and any reply containing "?" RE-PRESENT (None) rather than executing/rejecting.
    assert watcher.decide_from_reply("approve") == "approve"
    assert watcher.decide_from_reply("reject") == "reject"
    assert watcher.decide_from_reply("no, reject") == "reject"   # explicit token present
    assert watcher.decide_from_reply("yes please") is None       # was approve — now re-presents
    assert watcher.decide_from_reply("ok go ahead") is None      # was approve — now re-presents
    assert watcher.decide_from_reply("no thanks") is None        # was reject — now re-presents
    assert watcher.decide_from_reply("ok, what does this do?") is None
    assert watcher.decide_from_reply("what does this do?") is None
    assert watcher.decide_from_reply("") is None


def test_hop_trail_footer_formats():
    from agents import watcher
    footer = watcher.hop_trail_footer([
        {"agent": "Watcher", "address": "a", "ms": 3},
        {"agent": "Librarian", "address": "b", "ms": 12},
        {"agent": "Operator", "address": "c", "ms": 40},
    ])
    assert "Watcher→Librarian→Operator" in footer
    assert "55ms" in footer   # total 3+12+40


# --------------------------------------------------------------------------- #
# Approval TTL table — record/lookup, expiry, non-execution
# --------------------------------------------------------------------------- #
def test_approval_record_then_lookup(mem):
    t1, _ = mem
    from datetime import timedelta
    req = ApprovalRequest(incident_id="INC-9", plan_hash="hash9", risk_class="standard_change",
                          ladder_level="L2", requested_at=db.utcnow_iso(),
                          expires_at=(db.utcnow() + timedelta(minutes=10)).isoformat(),
                          channel="chat")
    approval.record_pending(t1, req, "agent1qsender")
    row = approval.lookup_pending(t1, "INC-9")
    assert row is not None and row["plan_hash"] == "hash9"
    assert approval.pending_for_sender(t1, "agent1qsender")


def test_expire_stale_marks_past_expiry(mem):
    t1, _ = mem
    from datetime import timedelta
    past = ApprovalRequest(incident_id="INC-8", plan_hash="hash8", risk_class="standard_change",
                           ladder_level="L2", requested_at=db.utcnow_iso(),
                           expires_at=(db.utcnow() - timedelta(minutes=1)).isoformat(),
                           channel="chat")
    approval.record_pending(t1, past, "agent1qsender")
    # already past expiry -> lookup treats it as absent (fail-closed)...
    assert approval.lookup_pending(t1, "INC-8") is None
    expired = approval.expire_stale(t1)
    assert ("INC-8", "hash8") in expired
    row = t1.execute("SELECT status FROM approval WHERE incident_id='INC-8'").fetchone()
    assert row["status"] == "expired"


def test_expired_or_absent_approval_yields_no_execution(sim_client, mem, monkeypatch):
    """A slow-path plan whose approval never arrives (absent) must NOT execute: with
    no ApprovalDecision, commit_execution refuses (outcome 'rejected'), verified False."""
    t1, _ = mem
    sim = SimTools(client=sim_client)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    prepared = _prepared_for(sim, t1, 1)               # slow-path -> needs a decision
    assert prepared.fast is False
    # No decision recorded / expired -> commit refuses to run the plan.
    res = orchestrator.commit_execution(prepared, conn=t1, tools=sim, decision=None,
                                        actor="scheduling-ops")
    assert res.verified is False
    assert res.step_results[0]["outcome"] == "rejected"


# --------------------------------------------------------------------------- #
# RULE 1/2 — Librarian imports no model id; RULE badges present
# --------------------------------------------------------------------------- #
def test_librarian_imports_no_model():
    src = (REPO / "agents" / "librarian.py").read_text()
    import_lines = [ln for ln in src.splitlines()
                    if ln.lstrip().startswith(("import ", "from "))]
    for ln in import_lines:
        assert "precedent.venice" not in ln, f"librarian imports a model client: {ln!r}"
        assert "precedent.models" not in ln, f"librarian imports the model registry: {ln!r}"
    # No literal model id anywhere in the source (RULE 1 — the check-open-weight grep).
    for banned in ("claude-", "openai-", "gpt-", "gemini-", "grok-", "mercury-"):
        assert banned not in src, f"banned model token {banned!r} in librarian.py"


def test_agents_readme_has_both_badges():
    readme = (REPO / "agents" / "README.md").read_text()
    assert "innovationlab" in readme
    assert "hackathon" in readme
