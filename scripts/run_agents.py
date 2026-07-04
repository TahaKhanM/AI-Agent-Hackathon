"""Local dry-run Bureau — Watcher + Librarian + Operator in one process.
[owner T1, task T1-8]

Spec: Idea/refinement/02 §3.4.

For the LOCAL dry-run only: a single-process uAgents Bureau that hosts all three
agents so the Watcher->Librarian->Operator flow can be exercised without live
Agentverse registration. LIVE registration (mailbox agents on Agentverse, ASI:One
discovery) is the HUMAN step documented in agents/README.md — the code is already
registerable there; this script is the wire-it-up-locally convenience.

Wiring:
- PRECEDENT_MEMORY_DB  — the shared SQLite memory file all three read/write.
- PRECEDENT_SIM_URL    — the running MediaCo sim the Operator's typed tools call.

Importing this module never starts the Bureau (guarded by __main__), so tests and
tools can import build_bureau() / the agent addresses safely.
"""
from __future__ import annotations

import os

from uagents import Bureau

from agents.librarian import build_librarian
from agents.operator import build_operator
from agents.protocol import TriageMsg
from agents.rails import shadow_hops
from agents.watcher import build_watcher

# A read-only self-check message: the scheduler class incident-2 retrieval (a TriageMsg carries
# no mutation), so the startup wire-check never changes sim/memory state.
_SELF_CHECK_TRIAGE = TriageMsg(
    incident_id="INC-2", class_key="scheduler|SCH-DUP-002|schedule_item",
    extraction_method="deterministic", principal="scheduling-ops")


def _attach_rails_self_check(watcher, addresses: dict[str, str]) -> None:
    """P1.8: at Bureau startup, push ONE real message through the Librarian rail and log the
    per-hop ms — the concrete 'multi-agent is true on the wire' evidence. Read-only (a TriageMsg
    retrieval) so it mutates nothing, and sent FROM the Watcher's identity so it satisfies the
    P0.3 rails allowlist. Fail-tolerant: if peers are still registering, it logs and moves on."""
    @watcher.on_event("startup")
    async def _rails_self_check(ctx) -> None:   # noqa: ANN001 — uAgents Context
        hops = await shadow_hops(ctx, librarian_address=addresses["librarian"],
                                 operator_address=addresses["operator"],
                                 triage_msg=_SELF_CHECK_TRIAGE)
        if hops:
            trail = ", ".join(f"{h['agent']} {h['ms']}ms" for h in hops)
            ctx.logger.info(f"[rails self-check] real Watcher->Librarian round-trip: {trail}")
        else:
            ctx.logger.info("[rails self-check] no rail reply yet (peers still registering)")


def build_bureau(self_check: bool = True) -> tuple[Bureau, dict[str, str]]:
    """Construct the three agents and a Bureau hosting them. Returns the Bureau and a
    {name: address} map (addresses are stable, derived from the env seeds). With self_check=True
    the Watcher runs the P1.8 startup rails self-check."""
    watcher = build_watcher()
    librarian = build_librarian()
    operator = build_operator()

    bureau = Bureau()
    bureau.add(watcher)
    bureau.add(librarian)
    bureau.add(operator)

    addresses = {
        "watcher": watcher.address,
        "librarian": librarian.address,
        "operator": operator.address,
    }
    if self_check:
        _attach_rails_self_check(watcher, addresses)
    return bureau, addresses


def _require_env() -> None:
    """The local dry-run needs the shared memory db and the sim URL wired in."""
    missing = [k for k in ("PRECEDENT_MEMORY_DB", "PRECEDENT_SIM_URL")
               if not os.environ.get(k)]
    if missing:
        raise SystemExit(
            "run_agents (local dry-run) needs env: " + ", ".join(missing) + ".\n"
            "  PRECEDENT_MEMORY_DB  — shared SQLite memory file (T1<->console seam)\n"
            "  PRECEDENT_SIM_URL    — base URL of the running MediaCo sim\n"
            "Live Agentverse registration is the human step (see agents/README.md)."
        )


if __name__ == "__main__":
    _require_env()
    bureau, addresses = build_bureau()
    print("Precedent local Bureau — Watcher -> Librarian -> Operator")
    for name, address in addresses.items():
        print(f"  {name:10s} {address}")
    print(f"  memory db : {os.environ['PRECEDENT_MEMORY_DB']}")
    print(f"  sim url   : {os.environ['PRECEDENT_SIM_URL']}")
    bureau.run()
