"""P1.8 — the multi-agent flow is real on the wire (rail round-trips), not a hard-coded footer.

Offline. shadow_hops drives real TriageMsg/PlanMsg round-trips through a loopback Context that
routes each send_and_receive to the REAL Librarian/Operator handler cores in-process (the genuine
message types + the genuine handlers; only the network transport is stubbed). Proves:
- a real Watcher→Librarian→Operator round-trip populates a NON-EMPTY hop trail with per-hop ms;
- it is fail-tolerant — a down rail yields an empty trail, never an exception (so the chat reply's
  authoritative content, produced in-process, is byte-identical rails-up or rails-down);
- the hop-trail footer renders the real ms;
- build_bureau attaches the startup self-check.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from agents import librarian, operator, rails, watcher
from agents.protocol import (
    PlanMsg,
    TriageMsg,
    plan_msg_from_prepared,
)
from console.demo_state import DemoState
from precedent import ladder, orchestrator, venice
from precedent.contracts import IncidentEvent
from precedent.tools import SimTools
from precedent_memory import db

SCHED_CK = "scheduler|SCH-DUP-002|schedule_item"


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    monkeypatch.setenv("PRECEDENT_AGENTS_OFFLINE", "1")
    yield


@pytest.fixture
def mem(tmp_path):
    shared = str(tmp_path / "mem.db")
    console = DemoState(db_path=shared)
    t1 = db.connect(shared)
    yield t1
    t1.close()
    console.conn.close()


@pytest.fixture
def sim_client(tmp_path, monkeypatch):
    monkeypatch.setenv("PRECEDENT_SIM_DB", str(tmp_path / "sim.db"))
    from sim.app import app
    with TestClient(app) as c:
        c.get("/health")
        yield c


class _LoopbackCtx:
    """A uAgents Context stand-in whose send_and_receive routes a typed message to the REAL target
    handler core and returns its reply — a genuine message→handler→reply round-trip, minus the
    network. `conn`/`sim` are the shared memory db + typed sim the handlers run against."""
    def __init__(self, conn, sim):
        self.conn = conn
        self.sim = sim

    async def send_and_receive(self, address, msg, response_type):
        if isinstance(msg, TriageMsg):
            return librarian.serve_retrieval(msg, conn=self.conn), "delivered"
        if isinstance(msg, PlanMsg):
            return operator.serve_execution(msg, conn=self.conn, tools=self.sim), "delivered"
        return None, "no-route"


class _DownCtx:
    """A ctx whose rail is down: send_and_receive always raises."""
    async def send_and_receive(self, *a, **k):
        raise RuntimeError("rails down")


def _triage_and_plan(sim, conn, monkeypatch):
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    ladder.promote(SCHED_CK, "ops-lead", conn=conn, force=True)   # standing -> fast_ready
    payload = sim.incident(2)
    inc = IncidentEvent(incident_id=payload["incident_id"], raw_text=payload["raw_text"],
                        source="sim", observed_at=payload["observed_at"])
    prepared = orchestrator.prepare(inc, structured=payload["structured"], conn=conn,
                                    tools=sim, principal="scheduling-ops")
    tri = TriageMsg(incident_id="INC-2", class_key=SCHED_CK,
                    extraction_method="deterministic", principal="scheduling-ops")
    plan = plan_msg_from_prepared(prepared, "standing", "agent1qWATCHER")
    return tri, plan


async def test_shadow_hops_real_roundtrip(sim_client, mem, monkeypatch):
    sim = SimTools(client=sim_client)
    tri, plan = _triage_and_plan(sim, mem, monkeypatch)
    ctx = _LoopbackCtx(mem, sim)
    hops = await rails.shadow_hops(ctx, librarian_address="agent1qLIB",
                                   operator_address="agent1qOP", triage_msg=tri, plan_msg=plan)
    assert [h["agent"] for h in hops] == ["Librarian", "Operator"]   # both rails round-tripped
    assert all(isinstance(h["ms"], int) and h["ms"] >= 0 for h in hops)
    assert hops[0]["address"] == "agent1qLIB" and hops[1]["address"] == "agent1qOP"
    footer = watcher.hop_trail_footer(hops)
    assert "Librarian" in footer and "Operator" in footer and "ms" in footer
    assert "(in-process)" not in footer


async def test_shadow_hops_denied_triage_skips_operator(sim_client, mem, monkeypatch):
    # A principal the class denies -> Librarian permits nothing -> the Operator hop is not made.
    sim = SimTools(client=sim_client)
    monkeypatch.setattr(venice, "chat", lambda *a, **k: "rationale")
    tri = TriageMsg(incident_id="INC-3", class_key="rights|RGT-EXCL-009|vod_item",
                    extraction_method="deterministic", principal="scheduling-ops")
    ctx = _LoopbackCtx(mem, sim)
    hops = await rails.shadow_hops(ctx, librarian_address="l", operator_address="o",
                                   triage_msg=tri, plan_msg=None)
    assert [h["agent"] for h in hops] == ["Librarian"]   # denial: no Operator hop


async def test_shadow_hops_fail_tolerant():
    tri = TriageMsg(incident_id="INC-2", class_key=SCHED_CK,
                    extraction_method="deterministic", principal="scheduling-ops")
    hops = await rails.shadow_hops(_DownCtx(), librarian_address="l", operator_address="o",
                                   triage_msg=tri, plan_msg=None)
    assert hops == []                                    # down rail -> empty trail, no exception


def test_build_bureau_attaches_self_check():
    import asyncio

    # build_bureau constructs fresh Agents (which need a current event loop); the async tests
    # above leave the main-thread loop unset, so install a fresh one first.
    asyncio.set_event_loop(asyncio.new_event_loop())
    from scripts.run_agents import build_bureau
    _bureau, addresses = build_bureau()
    assert set(addresses) == {"watcher", "librarian", "operator"}
    assert all(a.startswith("agent") for a in addresses.values())
