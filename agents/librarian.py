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
from agents.protocol import (
    RetrievalResultMsg,
    TriageMsg,
    build_precedent_protocol,
)
from precedent_memory import db, retrieve
from precedent_memory.audit import audit

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


def _audit_sender_rejected(conn, sender: str, message: str, incident_id: str) -> None:
    """Record a rails-authentication rejection (P0.3). Safe metadata only."""
    audit("rails_sender_rejected", conn=conn, actor=sender,
          rail=AGENT_NAME, message=message, incident_id=incident_id)
    conn.commit()


def guarded_serve_retrieval(msg: TriageMsg, *, sender: str, conn) -> RetrievalResultMsg:
    """Rails-authenticated retrieval (P0.3a): a TriageMsg is answered ONLY when it comes
    from our Watcher. Any other sender is rejected + AUDITED and gets an empty, content-free
    verdict (fail-closed — never a leak, never a hit)."""
    if not common.authorised_sender(sender, "watcher"):
        _audit_sender_rejected(conn, sender, "TriageMsg", msg.incident_id)
        return RetrievalResultMsg(
            incident_id=msg.incident_id, principal_id=msg.principal,
            permitted=False, hit_count=0, denied_count=0, denied_owner_team=None,
        )
    return serve_retrieval(msg, conn=conn)


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

    proto = build_precedent_protocol()   # P0.3(b): this agent's OWN protocol (only TriageMsg)

    @proto.on_message(TriageMsg)
    async def _on_triage(ctx: Context, sender: str, msg: TriageMsg) -> None:
        # Each retrieval opens its own conn to the shared memory db (the caller owns
        # the handle; the library never opens a hidden global one).
        conn = db.connect(os.environ["PRECEDENT_MEMORY_DB"])
        try:
            # P0.3(a): fail-closed sender allowlist — a forged triage is audited and gets
            # a content-free empty verdict.
            result = guarded_serve_retrieval(msg, sender=sender, conn=conn)
        finally:
            conn.close()
        await ctx.send(sender, result)

    librarian.include(proto, publish_manifest=True)
    return librarian


librarian = build_librarian()

if __name__ == "__main__":
    # Human runs this after filling LIBRARIAN_AGENT_SEED + AGENTVERSE_API_KEY in .env.
    print(f"{AGENT_NAME} address: {librarian.address}")
    librarian.run()
