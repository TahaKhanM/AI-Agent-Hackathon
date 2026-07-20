"""The injectable backing world the gate operates on — a memory conn + typed tools.

The gate never owns global mutable state: every operation runs against a ``GateWorld``
resolved per request. This makes the router (a) independently TestClient-testable against a
freshly-seeded world and (b) mountable into the deployed console where the world is the
current browser session's private db + in-process sim (WP-HOST-SESSION).

A ``GateWorld`` carries:
  * ``conn``   — the permission-aware memory SQLite connection (records/ACLs/ladder/audit),
  * ``tools``  — a typed tool client (SimTools-shaped: snapshot/execute/verify/restore),
  * ``lock``   — the world's single-writer lock (held across the deterministic prepare and the
                 execute-in-sim, mirroring scripts/demo_server.py),
  * ``refs``   — the in-process pending-decision registry (ref -> PendingEntry). Fail-closed by
                 construction: a restart drops it, so a pending ref becomes non-action rather
                 than a resurrected approval. The durable 10-min TTL for a needs-approval ref
                 additionally lives in the agents.approval ledger (the reused pattern),
  * ``principals`` — the set of identities registered OUT-OF-BAND. ``None`` means "do not
                 restrict here" (the deployed console configures this); a concrete set makes an
                 unregistered proposer/approver a non-action.

RULE 1/2: no model id, no LLM anywhere in this module — deterministic plumbing only.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any

DEFAULT_PRINCIPALS = frozenset({"scheduling-ops", "rights-ops", "ops-lead"})


@dataclass
class PendingEntry:
    """One held decision. ``prepared`` is cleared once consumed (no replay); ``status`` is the
    terminal verdict thereafter. ``expires_at`` is the fail-closed TTL horizon (ISO-8601)."""

    ref: str
    kind: str            # "standing" | "approval"
    incident_id: str
    plan_hash: str
    expires_at: str
    principal: str
    prepared: Any = None
    status: str = "pending"   # pending | approved | denied | expired


@dataclass
class GateWorld:
    conn: Any
    tools: Any
    lock: Any = field(default_factory=threading.RLock)
    refs: dict[str, PendingEntry] = field(default_factory=dict)
    principals: frozenset[str] | None = None
    # Optional owned resources so a standalone/test world can be torn down cleanly.
    _state: Any = None
    _client: Any = None

    def registered(self, principal: str | None) -> bool:
        """True iff ``principal`` is acceptable. Fail-closed: a missing principal is never OK;
        an unset ``principals`` set means the caller opted out of gate-side restriction."""
        if not principal:
            return False
        if self.principals is None:
            return True
        return principal in self.principals

    def close(self) -> None:
        """Best-effort teardown of any owned DemoState / sim TestClient (tests + deploy boot)."""
        client = self._client
        if client is not None:
            try:
                client.close()
            except Exception:  # noqa: BLE001 - a close hiccup must not mask the real result
                pass
        state = self._state
        if state is not None:
            try:
                state.conn.close()
            except Exception:  # noqa: BLE001
                pass


def gate_world_from_session(session: Any, *, principals: frozenset[str] | None = None) -> GateWorld:
    """Adapt a console per-cookie session (or the pinned _LegacySession) into a GateWorld.

    The pending registry is stashed on the session's DemoState — a stable object across the
    session's requests (and across a recreated _LegacySession wrapper, whose ``.state`` is the
    same pinned DemoState) — so a held ref survives between propose and outcome without adding a
    field to the frozen session/state classes.
    """
    state = session.state
    refs = state.__dict__.setdefault("_gate_refs", {})
    return GateWorld(conn=state.conn, tools=session.sim_tools(), lock=state._lock,
                     refs=refs, principals=principals)


def build_seeded_world(workdir: Any, *, standing_classes: tuple[str, ...] = (),
                       principals: frozenset[str] | None = DEFAULT_PRINCIPALS) -> GateWorld:
    """Build a fresh, fully-seeded GateWorld for an e2e test or a real deployment bootstrap.

    Memory: a per-world DemoState (records + ACLs + principals + ladder seeded at L1). Sim: a
    private copy of the cold-open MediaCo template driven through an in-process TestClient (no
    HTTP hop, airplane-mode). ``standing_classes`` promotes the named classes to Standing
    Approval (force=True) so the zero-LLM fast path can be exercised deterministically.

    Imports are LOCAL so this builder — a test/deploy convenience — never pulls the console/sim
    surface into the gate's decision-path import graph (gate/service.py, gate/api.py).
    """
    from pathlib import Path

    from fastapi.testclient import TestClient

    from console.demo_state import DemoState
    from console.session import _copy_sqlite_db, sim_template
    from precedent import ladder
    from precedent.tools import SimTools
    from sim.factory import make_sim_app

    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    mem_path = str(workdir / "gate_memory.db")
    sim_path = str(workdir / "gate_sim.db")

    state = DemoState(db_path=mem_path)                 # seeds records/ACLs/principals/ladder(L1)
    for class_key in standing_classes:
        ladder.promote(class_key, "ops-lead", conn=state.conn, force=True)

    _copy_sqlite_db(sim_template(), sim_path)           # memoised cold-open sim, hermetic copy
    client = TestClient(make_sim_app(sim_path))
    tools = SimTools(client=client)

    return GateWorld(conn=state.conn, tools=tools, lock=state._lock,
                     principals=principals, _state=state, _client=client)
