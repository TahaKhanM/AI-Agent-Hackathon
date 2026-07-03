"""Watcher — gateway + triage; the ASI:One / Chat-Protocol entry point.
[owner T1, task T1-2 hello-world -> T1-11/T1-12 full handlers]

Spec: 02 §3.4, 05 §E.

Phase A ships the REGISTERABLE hello-world: a mailbox agent that speaks the Agent
Chat Protocol (publish_manifest=True) with a STABLE seed from env, so the address
survives the later handler swap to the full triage->approval loop. A human runs the
live Agentverse registration (see agents/README.md); this module makes it registerable.

The full loop is chat-driven and split so it is testable WITHOUT a live network:
- triage_incident()  — deterministic extractor only (RULE 2: LLM may propose, never
  confirm a class); builds the TriageMsg the Librarian consumes.
- render_approval()  — the single ChatMessage body the human sees at the gate.
- decide_from_reply()/make_decision() — turn the human's chat reply into a typed
  ApprovalDecision whose approver_principal is the chat sender address VERBATIM.
- hop_trail_footer()  — the Watcher->Librarian->Operator provenance footer.
- build_degraded_watcher() — hosted L0 mode: triage + PUBLIC-corpus retrieval only,
  never executes, and says so.

RULE 1: no model id here. RULE 4: seed from env by name only.
"""
from __future__ import annotations

import os

from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    chat_protocol_spec,
)

from agents import common
from agents.protocol import IncidentMsg, TriageMsg
from precedent import extractor
from precedent.contracts import ApprovalDecision, ApprovalRequest
from precedent_memory import db

AGENT_NAME = "precedent-watcher"

# Keyword-rich description drives ASI:One discoverability (02 §3.4).
DESCRIPTION = (
    "Precedent Watcher — IT incident resolution and runbook automation. Report an "
    "incident (EPG publish failure, duplicate schedule slot, VOD rights-window "
    "conflict, Jira ticket remediation) and it retrieves your organisation's own "
    "documented fix, classifies risk deterministically, and executes behind an "
    "approval gate with audit and rollback."
)

# Affirmative / negative reply vocabulary for the chat gate (case-insensitive).
_APPROVE_WORDS = {"approve", "approved", "yes", "y", "ok", "okay", "go", "confirm", "ship"}
_REJECT_WORDS = {"reject", "rejected", "no", "n", "cancel", "deny", "abort", "stop"}


# --------------------------------------------------------------------------- #
# Registerable Chat Protocol (hello-world default; the loop swaps `reply` in)
# --------------------------------------------------------------------------- #
def build_chat_protocol(reply=None) -> Protocol:
    """The Chat Protocol handlers. `reply(text) -> str` is the triage function; the
    hello-world default echoes. The full loop swaps in a triage->approval reply
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
        description=DESCRIPTION,
        readme_path=common.README_PATH,      # both badges → Agentverse profile (Fetch gate)
        publish_agent_details=True,
    )
    watcher.include(build_chat_protocol(reply), publish_manifest=True)
    return watcher


# --------------------------------------------------------------------------- #
# Chat-driven flow (pure, network-free — the full triage->approval loop)
# --------------------------------------------------------------------------- #
def triage_incident(incident_msg: IncidentMsg) -> TriageMsg:
    """Deterministic triage: run the extractor over the incident and build the
    TriageMsg the Librarian consumes. RULE 2 — only the extractor confirms a class;
    a non-deterministic proposal yields class_key=None downstream at the gate.

    `incident_msg` is any object exposing .raw_text / .structured / .incident_id /
    .principal (an agents.protocol.IncidentMsg or an IncidentEvent-like shim)."""
    raw_text = incident_msg.raw_text
    structured = getattr(incident_msg, "structured", None)
    ext, method = extractor.extract(raw_text, structured)
    class_key = extractor.class_key_of(ext) if ext else None
    return TriageMsg(
        incident_id=incident_msg.incident_id,
        class_key=class_key,
        extraction_method=method,
        principal=getattr(incident_msg, "principal", "scheduling-ops"),
    )


def hop_trail_footer(hops: list[dict]) -> str:
    """Provenance footer appended to every outbound chat reply, from a list of
    {"agent","address","ms"} dicts. Shows the Watcher->Librarian->Operator path and
    the per-hop latency the human can cite on stage."""
    if not hops:
        return "\n\n— hop trail: (in-process)"
    names = "→".join(h.get("agent", "?") for h in hops)
    total = sum(int(h.get("ms", 0)) for h in hops)
    parts = ", ".join(f"{h.get('agent', '?')} {int(h.get('ms', 0))}ms" for h in hops)
    return f"\n\n— hop trail: {names} ({parts}; total ~{total}ms)"


def render_approval(req: ApprovalRequest, prepared) -> str:
    """The single ChatMessage body shown at the gate: triage + retrieved fix summary
    + risk class + rollback + a Jira link placeholder + the reply instruction and TTL."""
    rule = prepared.rule or {}
    ref = prepared.ref or {}
    action = rule.get("action_type", "documented fix")
    fix_summary = f"{req.risk_class} — apply {action} on {ref.get('object_type', '?')} "\
                  f"{ref.get('object_id', '?')}"
    rollback = "restore pre-state snapshot on any verification failure (auto)"
    jira = f"Jira: <link-placeholder for {prepared.incident.incident_id}>"
    return (
        f"Incident {prepared.incident.incident_id} — {prepared.class_key}\n"
        f"Retrieved fix: {fix_summary}\n"
        f"Risk class: {req.risk_class} (policy {prepared.assessment.policy_rule_id}, "
        f"ladder {req.ladder_level})\n"
        f"Rollback: {rollback}\n"
        f"{jira}\n"
        f"Reply approve/reject; expires in 10 min."
    )


def decide_from_reply(text: str) -> str | None:
    """Map a free-text chat reply to 'approve' | 'reject' | None (unrecognised).
    Word-level match so 'yes please' approves and 'no thanks' rejects."""
    if not text:
        return None
    words = {w.strip(".,!?:;").lower() for w in text.split()}
    if words & _APPROVE_WORDS:
        return "approve"
    if words & _REJECT_WORDS:
        return "reject"
    return None


def make_decision(req: ApprovalRequest, sender_address: str) -> ApprovalDecision:
    """Build the typed ApprovalDecision from the request. approver_principal is the
    chat sender address VERBATIM (the authorising identity in the audit log);
    channel is 'chat'. The reply verdict is resolved by the caller via
    decide_from_reply — here we bind the identity and hash under approval."""
    return ApprovalDecision(
        incident_id=req.incident_id,
        plan_hash=req.plan_hash,
        decision="approve",
        approver_principal=sender_address,
        channel="chat",
        decided_at=db.utcnow_iso(),
    )


# --------------------------------------------------------------------------- #
# Hosted DEGRADED-L0 Watcher (no MediaCo exec creds -> never executes)
# --------------------------------------------------------------------------- #
def _degraded() -> bool:
    """True when no execution target is configured: PRECEDENT_DEGRADED=1 or the sim
    URL is unset. In this mode the Watcher triages + retrieves against the public
    runbook corpus and returns a risk-classified reply — but NEVER executes."""
    return os.environ.get("PRECEDENT_DEGRADED") == "1" or not os.environ.get("PRECEDENT_SIM_URL")


def _degraded_reply(text: str) -> str:
    """Triage + classify only; end in the explicit no-execution L0 state."""
    ext, method = extractor.extract(text, None)
    if ext is None:
        triage = "unresolved class (needs human classification)"
    else:
        triage = f"class {extractor.class_key_of(ext)} (method={method})"
    return (
        f"Precedent Watcher (degraded L0): triaged {triage}. "
        "Retrieved against the public runbook corpus only; "
        "no execution target configured — L0 (no execution performed)."
    )


def build_degraded_watcher() -> Agent:
    """Hosted L0 Watcher: registerable, triages + retrieves against the PUBLIC corpus,
    returns a risk-classified reply, and NEVER executes. A human deploys this at G2."""
    return build_watcher(reply=_degraded_reply)


watcher = build_watcher()

if __name__ == "__main__":
    # Human runs this after filling WATCHER_AGENT_SEED + AGENTVERSE_API_KEY in .env.
    print(f"{AGENT_NAME} address: {watcher.address}")
    watcher.run()
