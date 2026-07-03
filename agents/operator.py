"""Operator — execution + Jira write-behind over Fetch rails.
[owner T1, task T1-8]

Spec: Idea/refinement/02-architecture-refinement.md §3.4.

The Operator is the ONLY agent that touches MediaCo, and it does so exclusively
through the typed SimTools client — never free-form shell. It receives a fully
gated PlanMsg (built by the Watcher from a `Prepared`), rebuilds the `Prepared`
+ decision, and hands them to the authoritative orchestrator.commit_execution,
which runs the SAME execute -> verify -> (rollback|memorise) kernel the console
path uses. The plan_hash tamper check bites here: a PlanMsg whose hash was altered
on the wire is rejected before any typed call runs.

RULE 1 / RULE 2: no model id, no LLM in this module. The risk class and the gate
decision were already fixed in prepare(); the Operator only executes typed calls
and records provenance. The Jira write-behind is a non-blocking local stub: a human
wires the real JiraPermissionSource client at registration. No secrets here.
"""
from __future__ import annotations

import os

from uagents import Agent, Context

from agents import common
from agents.protocol import PRECEDENT_PROTOCOL, PlanMsg, ResultMsg, prepared_from_plan_msg
from precedent import orchestrator
from precedent.tools import SimTools
from precedent_memory import db

AGENT_NAME = "precedent-operator"

DESCRIPTION = (
    "Precedent Operator — typed-tool execution with audit and rollback. Given an "
    "approved (or standing-approved) execution plan it runs the documented fix through "
    "typed tool calls only, verifies the post-state, auto-restores the pre-state "
    "snapshot on failure, and records the executed fix with provenance in a hash-chained "
    "audit log. A Jira write-behind queues a ticket note without ever blocking the loop."
)


# --------------------------------------------------------------------------- #
# Jira write-behind stub (local, non-blocking). A human wires the real
# JiraPermissionSource client at registration; this never blocks the flow and
# holds NO secrets. Polling + write-behind by design (no webhooks — venue Wi-Fi).
# --------------------------------------------------------------------------- #
JIRA_QUEUE: list[dict] = []


def enqueue_jira(incident_id: str, summary: str) -> dict:
    """Append a write-behind Jira note (local-demo). Returns the queued item. The
    real client drains this queue out-of-band; enqueue never touches the network."""
    item = {"incident_id": incident_id, "summary": summary}
    JIRA_QUEUE.append(item)
    return item


def _audit_tail_hash(conn) -> str | None:
    row = conn.execute("SELECT hash FROM audit_log ORDER BY seq DESC LIMIT 1").fetchone()
    return row["hash"] if row else None


def serve_execution(msg: PlanMsg, *, conn, tools, trace=None) -> ResultMsg:
    """Core (network-free) execution. Rebuild the Prepared + decision from the wire
    message and drive the authoritative commit_execution kernel. The plan_hash is
    preserved through prepared_from_plan_msg, so the tamper check still guards the
    hop. A Jira note is queued write-behind (never blocks)."""
    prepared, decision = prepared_from_plan_msg(msg)
    result = orchestrator.commit_execution(
        prepared,
        conn=conn,
        tools=tools,
        decision=decision,
        actor=msg.approver_principal,
        trace=trace,
    )
    outcome = result.step_results[0]["outcome"] if result.step_results else "unknown"

    enqueue_jira(msg.incident_id,
                 f"Precedent {outcome} {msg.policy_rule_id} on "
                 f"{msg.ref.get('object_type')} {msg.ref.get('object_id')} "
                 f"(verified={result.verified}, rolled_back={result.rolled_back})")

    return ResultMsg(
        incident_id=result.incident_id,
        plan_hash=result.plan_hash,
        verified=result.verified,
        rolled_back=result.rolled_back,
        outcome=outcome,
        audit_hash=_audit_tail_hash(conn),
        hop_trail=[],
    )


def build_operator() -> Agent:
    """Construct the registerable Operator (stable address from the env seed)."""
    operator = Agent(
        name=AGENT_NAME,
        seed=common.resolve_seed("operator"),
        mailbox=common.use_mailbox(),
        description=DESCRIPTION,
        readme_path=common.README_PATH,      # both badges → Agentverse profile (Fetch gate)
        publish_agent_details=True,
    )

    @PRECEDENT_PROTOCOL.on_message(PlanMsg)
    async def _on_plan(ctx: Context, sender: str, msg: PlanMsg) -> None:
        conn = db.connect(os.environ["PRECEDENT_MEMORY_DB"])
        tools = SimTools(base_url=os.environ["PRECEDENT_SIM_URL"])
        try:
            result = serve_execution(msg, conn=conn, tools=tools)
        finally:
            conn.close()
        await ctx.send(sender, result)

    operator.include(PRECEDENT_PROTOCOL, publish_manifest=True)
    return operator


operator = build_operator()

if __name__ == "__main__":
    # Human runs this after filling OPERATOR_AGENT_SEED + AGENTVERSE_API_KEY in .env.
    print(f"{AGENT_NAME} address: {operator.address}")
    operator.run()
