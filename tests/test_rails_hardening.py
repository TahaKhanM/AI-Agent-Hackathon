"""RAILS hardening — P0.1 (chat resilience + greeting), P0.2 (approval vocabulary
guard), P0.3 (sender allowlist + per-agent protocol isolation).

Offline (PRECEDENT_AGENTS_OFFLINE=1). These encode the *Verify* lines of the three
never-cut RAILS correctness items:

- P0.1: the live chat handler ALWAYS replies (sim outage mid-turn -> graceful degraded
  message, never ack-then-silence); an empty/StartSession-only message greets with the
  three demo incidents instead of the unsolicited "Couldn't identify..." line.
- P0.2: a bare "ok"/"y"/"go" or any reply containing "?" RE-PRESENTS rather than
  executing; only an explicit approve/reject token decides. "approve"/"reject" (the
  ASI:One video script, shot 5) still work verbatim.
- P0.3: the Operator/Librarian reject a PlanMsg/TriageMsg from any sender that is not the
  Watcher (audited, nothing executes); each agent carries ONLY its own protocol handler
  (no cross-registration) and rebuilding is idempotent with a stable seed-derived address.
"""
from __future__ import annotations

import asyncio
import types

import pytest
from fastapi.testclient import TestClient

# Import the agent modules at collection time so their module-level Agent() singletons build
# while the default event loop is pristine (before any _run() below swaps loops).
from agents import approval, common, librarian, operator, watcher  # noqa: F401
from agents.protocol import TriageMsg, plan_msg_from_prepared
from console.demo_state import DemoState
from precedent import ladder, orchestrator, venice
from precedent.contracts import IncidentEvent
from precedent.tools import SimTools
from precedent_memory import db

SCHED_CK = "scheduler|SCH-DUP-002|schedule_item"
RIGHTS_CK = "rights|RGT-EXCL-009|vod_item"
RESTRICTED_FIX = "takedown + republish per rights runbook"


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    monkeypatch.setenv("PRECEDENT_AGENTS_OFFLINE", "1")
    # ensure no env override of the allowlist address leaks in from a real .env
    for k in ("WATCHER_ADDRESS", "LIBRARIAN_ADDRESS", "OPERATOR_ADDRESS"):
        monkeypatch.delenv(k, raising=False)
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


def _prepared_for(sim, mem_conn, n, principal="scheduling-ops"):
    payload = sim.incident(n)
    inc = IncidentEvent(incident_id=payload["incident_id"], raw_text=payload["raw_text"],
                        source="sim", observed_at=payload["observed_at"])
    return orchestrator.prepare(inc, structured=payload["structured"], conn=mem_conn,
                                tools=sim, principal=principal)


class _FakeCtx:
    """Minimal uAgents Context stand-in: captures ctx.send payloads; logger is a no-op."""
    def __init__(self):
        self.sent: list = []
        self.logger = types.SimpleNamespace(
            warning=lambda *a, **k: None, debug=lambda *a, **k: None,
            info=lambda *a, **k: None, error=lambda *a, **k: None)

    async def send(self, sender, message):
        self.sent.append((sender, message))


def _run(coro):
    """Run a coroutine on a private event loop and restore a fresh loop afterward, so the
    module-level Agent() constructions in later tests still find a current event loop
    (asyncio.run() would leave it set to None)."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        asyncio.set_event_loop(asyncio.new_event_loop())


def _texts(ctx: _FakeCtx) -> list[str]:
    from uagents_core.contrib.protocols.chat import ChatMessage
    out = []
    for _sender, m in ctx.sent:
        if isinstance(m, ChatMessage):
            out.append(common.text_of(m))
    return out


# --------------------------------------------------------------------------- #
# P0.2 — approval vocabulary guard
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("reply,expected", [
    # explicit tokens decide (the ASI:One video script uses bare "approve"/"reject")
    ("approve", "approve"),
    ("Approve", "approve"),
    ("approved", "approve"),
    ("approve, thanks", "approve"),
    ("reject", "reject"),
    ("rejected", "reject"),
    ("no, reject", "reject"),      # explicit reject token present wins (video test relies on this)
    ("cancel", "reject"),
    ("abort", "reject"),
    # the embarrassing utterances: must NOT execute / NOT reject -> re-present (None)
    ("ok, what does this do?", None),
    ("ok", None),
    ("okay", None),
    ("y", None),
    ("go", None),
    ("go ahead", None),
    ("yes", None),
    ("yes please", None),
    ("sure", None),
    ("no worries", None),
    ("no thanks", None),
    ("approve?", None),           # any question re-presents even with an approve token
    ("should I approve?", None),
    ("what does this do?", None),
    ("", None),
])
def test_decide_from_reply_requires_explicit_token(reply, expected):
    assert watcher.decide_from_reply(reply) == expected


# --------------------------------------------------------------------------- #
# P0.1 — greeting + always-reply resilience
# --------------------------------------------------------------------------- #
def test_greeting_lists_three_incidents():
    g = watcher.greeting()
    low = g.lower()
    assert "epg" in low                    # incident 1
    assert "duplicate" in low or "schedule slot" in low   # incident 2
    assert "rights" in low or "vod" in low                # incident 3
    assert "1" in g and "2" in g and "3" in g
    assert "Couldn't identify" not in g


def test_serve_chat_turn_empty_greets(mem, sim_client):
    t1, _ = mem
    sim = SimTools(client=sim_client)
    r = watcher.serve_chat_turn("", "agent1qX", conn=t1, tools=sim, pending={})
    assert "Couldn't identify" not in r
    assert "epg" in r.lower()               # greeting, not the unsolicited error


def test_live_handler_greets_on_empty_message(monkeypatch, tmp_path):
    # StartSession/empty -> text_of == "" -> greeting, WITHOUT needing db/sim.
    monkeypatch.setenv("PRECEDENT_MEMORY_DB", str(tmp_path / "unused.db"))
    monkeypatch.delenv("PRECEDENT_SIM_URL", raising=False)
    monkeypatch.setenv("PRECEDENT_DEGRADED", "0")
    ctx = _FakeCtx()
    msg = common.text_message("")
    _run(watcher.run_live_chat(ctx, "agent1qEMPTY", msg))
    texts = _texts(ctx)
    assert texts, "handler must reply (never ack-then-silence)"
    assert any("epg" in t.lower() for t in texts)   # the greeting


def test_live_handler_always_replies_on_sim_outage(monkeypatch, mem):
    """Sim down mid-turn: the sender still gets a graceful reply, no stack trace, and
    nothing restricted is disclosed."""
    t1, _ = mem
    monkeypatch.setenv("PRECEDENT_MEMORY_DB", t1.execute("PRAGMA database_list").fetchone()["file"])
    monkeypatch.setenv("PRECEDENT_SIM_URL", "http://127.0.0.1:9/unreachable")  # sim is DOWN
    monkeypatch.setenv("PRECEDENT_DEGRADED", "0")
    ctx = _FakeCtx()
    # a real incident report -> serve_chat_turn will try tools.incident(1) -> connection error
    msg = common.text_message("our epg publish to the 9pm slot failed, incident 1")
    _run(watcher.run_live_chat(ctx, "agent1qDOWN", msg))
    texts = _texts(ctx)
    assert texts, "handler must ALWAYS reply even on a mid-turn outage"
    joined = " ".join(texts)
    assert "Traceback" not in joined and "Error" not in joined  # no raw stack trace
    assert RESTRICTED_FIX not in joined and "takedown" not in joined.lower()  # nothing restricted


# --------------------------------------------------------------------------- #
# P0.3(a) — sender allowlist on the rails
# --------------------------------------------------------------------------- #
def test_authorised_sender_only_watcher(monkeypatch):
    watcher_addr = common.agent_address("watcher")
    assert common.authorised_sender(watcher_addr, "watcher") is True
    assert common.authorised_sender("agent1qFORGED", "watcher") is False
    assert common.authorised_sender("", "watcher") is False
    # explicit env override wins
    monkeypatch.setenv("WATCHER_ADDRESS", "agent1qEXPLICIT")
    assert common.agent_address("watcher") == "agent1qEXPLICIT"
    assert common.authorised_sender("agent1qEXPLICIT", "watcher") is True
    assert common.authorised_sender(watcher_addr, "watcher") is False


def test_operator_rejects_forged_sender_no_execution(sim_client, mem, monkeypatch):
    t1, _ = mem
    sim = SimTools(client=sim_client)
    ladder.promote(SCHED_CK, "ops-lead", conn=t1, force=True)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    prepared = _prepared_for(sim, t1, 2)
    msg = plan_msg_from_prepared(prepared, "standing", "agent1qFORGED")

    before = t1.execute("SELECT COUNT(*) c FROM audit_log").fetchone()["c"]
    res = operator.guarded_serve_execution(msg, sender="agent1qFORGED", conn=t1, tools=sim)
    assert res.verified is False and res.outcome == "unauthorised_sender"
    # audited + nothing executed
    rej = t1.execute("SELECT COUNT(*) c FROM audit_log WHERE event_type='rails_sender_rejected'"
                     ).fetchone()["c"]
    assert rej >= 1
    execs = t1.execute("SELECT COUNT(*) c FROM audit_log WHERE event_type LIKE 'exec%'"
                       ).fetchone()["c"]
    assert execs == 0, "a forged plan must not execute"
    assert t1.execute("SELECT COUNT(*) c FROM audit_log").fetchone()["c"] > before


def test_operator_accepts_watcher_sender(sim_client, mem, monkeypatch):
    t1, _ = mem
    sim = SimTools(client=sim_client)
    ladder.promote(SCHED_CK, "ops-lead", conn=t1, force=True)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    prepared = _prepared_for(sim, t1, 2)
    watcher_addr = common.agent_address("watcher")
    msg = plan_msg_from_prepared(prepared, "standing", watcher_addr)
    res = operator.guarded_serve_execution(msg, sender=watcher_addr, conn=t1, tools=sim)
    assert res.verified is True and res.outcome == "resolved"


def test_librarian_rejects_forged_sender(mem):
    t1, _ = mem
    msg = TriageMsg(incident_id="INC-2", class_key=SCHED_CK,
                    extraction_method="deterministic", principal="scheduling-ops")
    res = librarian.guarded_serve_retrieval(msg, sender="agent1qFORGED", conn=t1)
    assert res.permitted is False and res.hit_count == 0
    assert t1.execute("SELECT COUNT(*) c FROM audit_log WHERE event_type='rails_sender_rejected'"
                      ).fetchone()["c"] >= 1


# --------------------------------------------------------------------------- #
# P0.3(b) — per-agent protocol isolation + idempotent rebuild
# --------------------------------------------------------------------------- #
def _agent_msg_models(agent) -> set[str]:
    names: set[str] = set()
    for p in agent.protocols.values():
        for m in p.models.values():
            names.add(m.__name__)
    return names


def test_each_agent_carries_only_its_own_handler():
    op = operator.build_operator()
    lib = librarian.build_librarian()
    op_models = _agent_msg_models(op)
    lib_models = _agent_msg_models(lib)
    assert "PlanMsg" in op_models and "TriageMsg" not in op_models, \
        f"operator cross-registered: {op_models}"
    assert "TriageMsg" in lib_models and "PlanMsg" not in lib_models, \
        f"librarian cross-registered: {lib_models}"


def test_rebuild_is_idempotent_and_address_stable():
    a1 = operator.build_operator()
    a2 = operator.build_operator()
    assert a1.address == a2.address        # seed-derived, unchanged across rebuilds
    # a rebuilt agent still carries exactly its one handler (no accumulation)
    assert _agent_msg_models(a2) == {"PlanMsg"}


def test_protocol_name_version_unchanged():
    from agents import protocol
    p = protocol.build_precedent_protocol()
    assert p.name == "precedent" and p.version == "1.0"
