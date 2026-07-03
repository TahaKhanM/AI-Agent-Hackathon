"""B1 — the live Watcher Chat-Protocol handler runs the FULL deterministic loop.

Offline (PRECEDENT_AGENTS_OFFLINE=1, in-process sim TestClient — no network). Proves the
network-free core `watcher.serve_chat_turn` composes report -> ONE approval message ->
approve -> execute -> audit-hash reply, and holds the three hard rules on the live path:

- RULE 2: the STANDING repeat-class turn makes ZERO venice.chat/venice.embed calls;
- RULE 3: a refusal discloses ONLY denied_count + denied_owner_team (no title/body/secret);
- fail-closed: a dropped/expired approval NEVER executes and re-presents on reconnect.

The full loop was composed ONLY in scripts/demo_server.py before B1; here it is driven by a
chat turn exactly as an ASI:One message would drive the registered Watcher.
"""
from __future__ import annotations

import re
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from agents import approval, watcher
from console.demo_state import DemoState
from precedent import ladder, venice
from precedent.tools import SimTools
from precedent_memory import db

SCHED_CK = "scheduler|SCH-DUP-002|schedule_item"
RESTRICTED_FIX = "takedown + republish per rights runbook"
_HEX64 = re.compile(r"[0-9a-f]{64}")


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


# --------------------------------------------------------------------------- #
# resolve_incident_n — deterministic (zero-LLM) report -> incident mapping
# --------------------------------------------------------------------------- #
def test_resolve_incident_n_explicit_and_keyword():
    assert watcher.resolve_incident_n("please handle incident 2") == 2
    assert watcher.resolve_incident_n("INC-3 needs a look") == 3
    assert watcher.resolve_incident_n("the epg guide is blank for the 9pm slot") == 1
    assert watcher.resolve_incident_n("duplicate slot, same show twice overlapping") == 2
    assert watcher.resolve_incident_n("a title still live on demand but the licence expired") == 3
    assert watcher.resolve_incident_n("the canteen wifi is down") is None


# --------------------------------------------------------------------------- #
# Full slow-path loop: report -> ONE gate message -> approve -> execute -> hash
# --------------------------------------------------------------------------- #
def test_chat_full_loop_report_gate_approve_execute(sim_client, mem, monkeypatch):
    t1, _ = mem
    sim = SimTools(client=sim_client)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "documented fix rationale")
    pending: dict = {}
    sender = "agent1qHUMANsender"

    r1 = watcher.serve_chat_turn("hiya the epg guide is blank for the 9pm slot (incident 1)",
                                 sender, conn=t1, tools=sim, pending=pending)
    # exactly ONE formatted gate message: triage + fix + risk + rollback + Jira + TTL
    assert "INC-1" in r1
    assert "Risk class" in r1 and "Rollback" in r1 and "Jira" in r1
    assert "Reply approve/reject" in r1 and "expires in 10 min" in r1
    assert sender in pending                                  # gate stashed in-process
    assert approval.lookup_pending(t1, "INC-1") is not None   # + recorded in the TTL ledger

    r2 = watcher.serve_chat_turn("approve", sender, conn=t1, tools=sim, pending=pending)
    assert "Approved by agent1qHUMANsender" in r2             # approver = sender verbatim
    assert "resolved" in r2
    assert _HEX64.search(r2), "execution reply must carry the 64-hex audit tail hash"
    assert "hop trail" in r2                                  # provenance footer
    assert sender not in pending                              # gate closed
    assert approval.lookup_pending(t1, "INC-1") is None       # ledger marked terminal


# --------------------------------------------------------------------------- #
# RULE 2 — STANDING repeat-class turn is zero-LLM, quotes ~15s, never "Autonomous"
# --------------------------------------------------------------------------- #
def test_chat_standing_fast_path_is_zero_llm(sim_client, mem, monkeypatch):
    t1, _ = mem
    sim = SimTools(client=sim_client)
    ladder.promote(SCHED_CK, "ops-lead", conn=t1, force=True)   # STANDING pre-seed

    def _boom(*a, **k):
        raise AssertionError("LLM called on the STANDING fast-path (RULE 2)")
    monkeypatch.setattr(venice, "chat", _boom)
    monkeypatch.setattr(venice, "embed", _boom)

    pending: dict = {}
    sender = "agent1qREPEAT"
    r = watcher.serve_chat_turn("duplicate slot, same show twice overlapping (incident 2)",
                                sender, conn=t1, tools=sim, pending=pending)
    assert "Standing Approval" in r and "~15s" in r
    assert "Autonomous" not in r                              # terminology rule
    assert sender not in pending                              # executed straight through, no gate
    assert _HEX64.search(r)                                   # audit hash on the reply


# --------------------------------------------------------------------------- #
# RULE 3 — a refusal discloses ONLY count + owner team, no restricted body
# --------------------------------------------------------------------------- #
def test_chat_refusal_discloses_only_count_and_owner(sim_client, mem, monkeypatch):
    t1, _ = mem
    sim = SimTools(client=sim_client)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    pending: dict = {}
    r = watcher.serve_chat_turn(
        "a title still live on demand but the licence expired, exclusivity breach (incident 3)",
        "agent1qX", conn=t1, tools=sim, pending=pending, principal="scheduling-ops")
    assert "Rights Ops" in r                     # owner team disclosed
    assert re.search(r"\b1\b", r)                # denied_count disclosed
    # NO restricted content leaks
    assert RESTRICTED_FIX not in r
    assert "takedown" not in r.lower()
    assert "RGT-WIN-014" not in r
    assert "agent1qX" not in pending             # a refusal opens no gate


# --------------------------------------------------------------------------- #
# Fail-closed — dropped approval expires to non-action; reconnect re-presents
# --------------------------------------------------------------------------- #
def test_chat_dropped_approval_expires_and_represents(sim_client, mem, monkeypatch):
    t1, _ = mem
    sim = SimTools(client=sim_client)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    pending: dict = {}
    sender = "agent1qDROP"

    watcher.serve_chat_turn("epg guide blank 9pm slot incident 1",
                            sender, conn=t1, tools=sim, pending=pending)
    assert sender in pending

    # reconnect while STILL LIVE: an ambiguous message re-presents the gate (not lost)
    r_reconnect = watcher.serve_chat_turn("are you still there?", sender,
                                          conn=t1, tools=sim, pending=pending)
    assert "expires in 10 min" in r_reconnect
    assert "INC-1" in r_reconnect

    # force the ledger row past expiry -> a late approve must NOT execute (non-action)
    t1.execute("UPDATE approval SET expires_at=? WHERE incident_id='INC-1'",
               ((db.utcnow() - timedelta(minutes=1)).isoformat(),))
    t1.commit()
    r_late = watcher.serve_chat_turn("approve", sender, conn=t1, tools=sim, pending=pending)
    assert "Approved by" not in r_late           # did NOT execute
    assert "expired" in r_late.lower() or "no live" in r_late.lower()
    assert sender not in pending                  # in-process gate swept in lock-step


def test_chat_reject_closes_without_executing(sim_client, mem, monkeypatch):
    t1, _ = mem
    sim = SimTools(client=sim_client)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    pending: dict = {}
    sender = "agent1qNO"
    watcher.serve_chat_turn("epg guide blank 9pm slot incident 1",
                            sender, conn=t1, tools=sim, pending=pending)
    r = watcher.serve_chat_turn("no, reject", sender, conn=t1, tools=sim, pending=pending)
    assert "ejected" in r                         # "Rejected"/"rejected"
    assert "Approved by" not in r
    assert sender not in pending
    # ledger row is no longer pending
    assert approval.lookup_pending(t1, "INC-1") is None


# --------------------------------------------------------------------------- #
# The registerable Watcher no longer echoes — its default handler is the live loop
# --------------------------------------------------------------------------- #
def test_registerable_watcher_has_no_echo_default(monkeypatch):
    monkeypatch.setenv("WATCHER_AGENT_SEED", "unit-test-stable-seed-value")
    src = (watcher.__file__)
    text = open(src).read()
    # the old echo string must be gone from the module
    assert "Precedent Watcher received:" not in text
    # build_watcher() (the registerable singleton path) constructs offline with the live loop
    agent = watcher.build_watcher()
    assert agent.address.startswith("agent")
