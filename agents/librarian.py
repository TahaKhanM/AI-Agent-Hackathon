"""Librarian — retrieval + memory governance over Fetch rails.
[owner T1, task T1-8]

Spec: Idea/refinement/02-architecture-refinement.md §2.4 + §3.4.

The Librarian is the governance boundary on the network. It answers ONE question,
deterministically: "for this triaged class and this principal, is there a permitted
documented fix — and if not, whose team owns the denied one?"

RULE 1 / RULE 2 (both eligibility-fatal, enforced by test + the check-open-weight
grep over agents/): THIS MODULE IMPORTS NO LLM AND NO MODEL REGISTRY — neither the
Venice client nor the model-role registry. Retrieval is a structured ACL match
delegated to precedent_memory.retrieve — one bitmask conjunction, no semantic
similarity, no model in the permission decision.

RULE 3: on a denial we surface ONLY the count and the owning team. `serve_retrieval`
maps the RetrievalBundle to a RetrievalResultMsg that carries no title, symptom,
body, or secret — never the fix content.
"""
from __future__ import annotations

import os

from uagents import Agent, Context

from agents import common
from agents.protocol import PRECEDENT_PROTOCOL, RetrievalResultMsg, TriageMsg
from precedent_memory import db, retrieve

AGENT_NAME = "precedent-librarian"

DESCRIPTION = (
    "Precedent Librarian — permission-aware memory governance. Given a triaged "
    "incident class it retrieves the organisation's own documented fix ONLY when the "
    "requesting principal is authorised, enforcing Jira/ACL lineage as a deterministic "
    "bitmask conjunction (no LLM in the permission decision). On a denial it discloses "
    "only how many remediations are hidden and which team owns them — never the fix "
    "content. Fail-closed: uncertain freshness denies."
)


def serve_retrieval(msg: TriageMsg, *, conn) -> RetrievalResultMsg:
    """Core (network-free) retrieval governance. Deterministic, no LLM.

    An unresolved class (extractor could not confirm one) is not retrievable — we
    return permitted=False with zero hits and disclose nothing. Otherwise we delegate
    the audited, ACL-filtered decision to precedent_memory.retrieve and project its
    bundle to the wire message, carrying ONLY count + owner team on a denial (RULE 3).
    """
    if msg.class_key is None:
        return RetrievalResultMsg(
            incident_id=msg.incident_id,
            principal_id=msg.principal,
            permitted=False,
            hit_count=0,
            denied_count=0,
            denied_owner_team=None,
        )

    bundle = retrieve.retrieve(
        msg.principal,
        {"class_key": msg.class_key, "incident_id": msg.incident_id},
        conn=conn,
        actor=msg.principal,
    )
    return RetrievalResultMsg(
        incident_id=bundle.incident_id or msg.incident_id,
        principal_id=bundle.principal_id,
        permitted=bool(bundle.hits),
        hit_count=len(bundle.hits),
        denied_count=bundle.denied_count,
        denied_owner_team=bundle.denied_owner_team,
    )


def build_librarian() -> Agent:
    """Construct the registerable Librarian (stable address from the env seed)."""
    librarian = Agent(
        name=AGENT_NAME,
        seed=common.resolve_seed("librarian"),
        mailbox=common.use_mailbox(),
        description=DESCRIPTION,
        readme_path=common.README_PATH,      # both badges → Agentverse profile (Fetch gate)
        publish_agent_details=True,
    )

    @PRECEDENT_PROTOCOL.on_message(TriageMsg)
    async def _on_triage(ctx: Context, sender: str, msg: TriageMsg) -> None:
        # Each retrieval opens its own conn to the shared memory db (the caller owns
        # the handle; the library never opens a hidden global one).
        conn = db.connect(os.environ["PRECEDENT_MEMORY_DB"])
        try:
            result = serve_retrieval(msg, conn=conn)
        finally:
            conn.close()
        await ctx.send(sender, result)

    librarian.include(PRECEDENT_PROTOCOL, publish_manifest=True)
    return librarian


librarian = build_librarian()

if __name__ == "__main__":
    # Human runs this after filling LIBRARIAN_AGENT_SEED + AGENTVERSE_API_KEY in .env.
    print(f"{AGENT_NAME} address: {librarian.address}")
    librarian.run()
