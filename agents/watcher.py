"""Watcher — gateway + triage; the ASI:One / Chat-Protocol entry point.
[owner T1, task T1-2 hello-world → T1-11/T1-12 full handlers]

Spec: 02 §3.4, 05 §E.

Phase A ships the REGISTERABLE hello-world: a mailbox agent that speaks the Agent
Chat Protocol (publish_manifest=True) with a STABLE seed from env, so the address
survives the later handler swap to the full triage→approval loop. A human runs the
live Agentverse registration (see agents/README.md); this module makes it registerable.

RULE 1: no model id here. RULE 4: seed from env by name only.
"""
from __future__ import annotations

from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    chat_protocol_spec,
)

from agents import common

AGENT_NAME = "precedent-watcher"

# Keyword-rich description drives ASI:One discoverability (02 §3.4).
DESCRIPTION = (
    "Precedent Watcher — IT incident resolution and runbook automation. Report an "
    "incident (EPG publish failure, duplicate schedule slot, VOD rights-window "
    "conflict, Jira ticket remediation) and it retrieves your organisation's own "
    "documented fix, classifies risk deterministically, and executes behind an "
    "approval gate with audit and rollback."
)


def build_chat_protocol(reply=None) -> Protocol:
    """The Chat Protocol handlers. `reply(text) -> str` is the triage function; the
    hello-world default echoes. The full loop swaps in a triage→approval reply
    without changing the agent address (same seed)."""
    reply = reply or (lambda text: f"Precedent Watcher received: {text}")
    chat_proto = Protocol(spec=chat_protocol_spec)

    @chat_proto.on_message(ChatMessage)
    async def _on_chat(ctx: Context, sender: str, msg: ChatMessage) -> None:
        await ctx.send(sender, common.ack_for(msg))
        answer = reply(common.text_of(msg))
        await ctx.send(sender, common.text_message(answer))

    @chat_proto.on_message(ChatAcknowledgement)
    async def _on_ack(ctx: Context, sender: str, msg: ChatAcknowledgement) -> None:
        ctx.logger.debug(f"ack from {sender} for {msg.acknowledged_msg_id}")

    return chat_proto


def build_watcher(reply=None) -> Agent:
    """Construct the registerable Watcher (stable address from the env seed)."""
    watcher = Agent(
        name=AGENT_NAME,
        seed=common.resolve_seed("watcher"),
        mailbox=common.use_mailbox(),
    )
    watcher.include(build_chat_protocol(reply), publish_manifest=True)
    return watcher


watcher = build_watcher()

if __name__ == "__main__":
    # Human runs this after filling WATCHER_AGENT_SEED + AGENTVERSE_API_KEY in .env.
    print(f"{AGENT_NAME} address: {watcher.address}")
    watcher.run()
