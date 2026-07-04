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
import re

from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    chat_protocol_spec,
)

from agents import approval, common
from agents.protocol import IncidentMsg, TriageMsg
from precedent import extractor, orchestrator
from precedent.contracts import ApprovalDecision, ApprovalRequest, IncidentEvent
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

# P0.2 — approval vocabulary guard. ONLY an explicit approve/reject token decides. A bare
# "ok"/"yes"/"go"/"y"/"n"/"no" or ANY reply containing "?" re-presents the gate rather than
# executing/rejecting — an approval must be unambiguous, so "ok, what does this do?" can never
# execute and "no worries" can never reject. "approve"/"reject" (the ASI:One video script,
# shot 5) work verbatim. (case-insensitive)
_APPROVE_WORDS = {"approve", "approved"}
_REJECT_WORDS = {"reject", "rejected", "cancel", "abort"}
# A negation next to an approve token contradicts it — "don't approve", "no, actually approve",
# "never approve" must NOT execute; they re-present (P0.2). "no"/"not" only DIS-qualify an
# approve; they never turn a reject into an approve, so "no, reject" still rejects.
_NEGATIONS = {"no", "not", "dont", "don't", "never", "cancel", "stop", "wait", "hold",
              "cant", "can't", "wont", "won't", "aint", "nope"}


# --------------------------------------------------------------------------- #
# Registerable Chat Protocol
#   build_watcher()            -> the LIVE full-loop handler (the registerable default)
#   build_watcher(reply=fn)    -> a text-only reply fn (degraded L0 / tests) via
#                                 build_chat_protocol(fn) — NO echo fallback any more
# --------------------------------------------------------------------------- #
def build_chat_protocol(reply) -> Protocol:
    """A text-only Chat Protocol: `reply(text) -> str`. Used by the hosted degraded-L0
    Watcher (triage/classify, never execute) and by unit tests. There is deliberately NO
    echo default — the registerable Watcher wires the live loop (build_live_chat_protocol),
    so a plain ASI:One chat runs the deterministic loop rather than echoing."""
    if reply is None:
        raise ValueError("build_chat_protocol requires an explicit reply function")
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


# In-process pending-gate map (sender address -> Prepared) for the LIVE loop. The hard
# TTL + fail-closed sweep live in the DB `approval` ledger (agents/approval.py); this map
# only carries the transient Prepared across the two chat turns in ONE process. If the
# process restarts the DB row still ages out to non-action (never an unauthorised run).
_LIVE_PENDING: dict[str, orchestrator.Prepared] = {}


# P0.1 — a judge who opens a session or sends a mid-turn message must ALWAYS get a reply.
_DEGRADED_TURN_REPLY = (
    "Sorry — I hit a temporary problem handling that turn. Nothing was executed and no "
    "restricted content was disclosed. Please try again in a moment (for example, say "
    "\"incident 1\")."
)


def greeting() -> str:
    """First-contact greeting (StartSession / empty message): what Precedent does + the three
    demo incidents with example phrasing. P0.1: replaces the unsolicited 'Couldn't identify the
    incident class...' a judge used to see the moment they opened a chat."""
    return (
        "Precedent Watcher — I retrieve your organisation's own documented fix and run it "
        "behind an approval gate, with audit and rollback. Three incidents are ready to try:\n"
        "  1) EPG publish failure — the evening guide is blank "
        "(e.g. \"our 9pm EPG publish failed, error 4012\").\n"
        "  2) Duplicate schedule slot — the same show booked twice "
        "(e.g. \"incident 2 — duplicate slot\").\n"
        "  3) VOD rights-window breach — a title still on demand past its licence "
        "(e.g. \"incident 3 — rights window expired\").\n"
        "Report one in plain English (or say \"incident 1/2/3\") and I'll triage it."
    )


async def run_live_chat(ctx: Context, sender: str, msg: ChatMessage) -> None:
    """The LIVE chat turn, GUARDED so the sender ALWAYS gets a reply (never ack-then-silence,
    P0.1). An empty / StartSession-only message greets with the three demo incidents; any
    failure (sim outage, missing env, a mid-turn error) yields a graceful degraded message —
    no stack trace, nothing restricted disclosed, nothing executed."""
    try:
        await ctx.send(sender, common.ack_for(msg))
        text = common.text_of(msg)
        if not text:                          # StartSession / empty -> greet, DB/sim not needed
            await ctx.send(sender, common.text_message(greeting()))
            return
        if _degraded():                       # hosted L0: triage/classify, never execute
            await ctx.send(sender, common.text_message(_degraded_reply(text)))
            return
        from precedent.tools import SimTools
        from precedent_memory import sync as _sync
        conn = db.connect(os.environ["PRECEDENT_MEMORY_DB"])
        try:
            tools = SimTools(base_url=os.environ["PRECEDENT_SIM_URL"])
            # Re-affirm the cached ACL source before serving (freshness heartbeat). Gated
            # (P0.6): a real sync tick when a live source is configured, a heartbeat only in
            # airplane mode — never masks an un-polled upstream tightening. Revoked sources
            # stay dark, so the refusal path is preserved.
            _sync.refresh_cached_freshness(conn)
            answer = serve_chat_turn(text, sender, conn=conn, tools=tools, pending=_LIVE_PENDING)
        finally:
            conn.close()
        await ctx.send(sender, common.text_message(answer))
    except Exception as exc:                  # noqa: BLE001 — ALWAYS reply; never leak a trace
        try:
            ctx.logger.warning(f"watcher live chat turn failed: {exc!r}")
        except Exception:                     # pragma: no cover — logging must never mask reply
            pass
        try:
            await ctx.send(sender, common.text_message(_DEGRADED_TURN_REPLY))
        except Exception:                     # pragma: no cover — best-effort final reply
            pass


def build_live_chat_protocol() -> Protocol:
    """The LIVE Chat Protocol: every ASI:One ChatMessage drives the FULL deterministic loop
    via run_live_chat (guarded report -> ONE gate message -> approve -> execute -> audit hash).
    Opens the shared memory db + typed SimTools LAZILY at message time (like the Operator's
    on_plan), so construction stays offline/network-free and the address is stable across the
    handler swap. With no execution target configured it degrades to L0 (triage/classify only)
    — never executes. RULE 2: the STANDING branch is zero-LLM."""
    chat_proto = Protocol(spec=chat_protocol_spec)

    @chat_proto.on_message(ChatMessage)
    async def _on_chat(ctx: Context, sender: str, msg: ChatMessage) -> None:
        await run_live_chat(ctx, sender, msg)

    @chat_proto.on_message(ChatAcknowledgement)
    async def _on_ack(ctx: Context, sender: str, msg: ChatAcknowledgement) -> None:
        ctx.logger.debug(f"ack from {sender} for {msg.acknowledged_msg_id}")

    return chat_proto


def build_watcher(reply=None) -> Agent:
    """Construct the registerable Watcher (stable address from the env seed). With no
    `reply` it wires the LIVE full-loop handler (build_live_chat_protocol); pass a `reply`
    fn for the degraded-L0 / test text-only handler. Either way the address is identical
    (seed-derived), so the live registration survives the B1 handler swap."""
    watcher = Agent(
        name=AGENT_NAME,
        seed=common.resolve_seed("watcher"),
        mailbox=common.use_mailbox(),
        description=DESCRIPTION,
        readme_path=common.README_PATH,      # both badges → Agentverse profile (Fetch gate)
        publish_agent_details=True,
    )
    proto = build_live_chat_protocol() if reply is None else build_chat_protocol(reply)
    watcher.include(proto, publish_manifest=True)
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
    # No angle brackets — chat/markdown renderers (e.g. ASI:One) treat <...> as an HTML tag
    # and swallow the text inside it.
    jira = f"Jira: ticket for {prepared.incident.incident_id} (link attached on execution)"
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
    """Map a free-text chat reply to 'approve' | 'reject' | None (re-present). P0.2: a reply
    containing '?' is never a decision (a question re-presents), and only an explicit
    approve/reject token counts — a bare 'ok'/'yes'/'go'/'no' returns None so it re-presents
    the gate rather than accidentally executing or rejecting."""
    if not text:
        return None
    if "?" in text:                       # a question is never a decision — re-present
        return None
    words = {w.strip(".,!?:;").lower() for w in text.split()}
    if words & _APPROVE_WORDS:
        if words & _NEGATIONS:            # "don't approve" / "no, actually approve" -> re-present
            return None
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
# Deterministic report -> incident resolver (RULE 2: zero-LLM keyword/code match).
# A live chat report names one of the three seeded MediaCo incidents; the Watcher maps
# it to that incident's object of record (the sim holds the concrete object_id the plan
# needs). The extractor still CONFIRMS the class fingerprint from the fetched structured
# payload — the LLM never picks the incident and never confirms the class.
# --------------------------------------------------------------------------- #
_INCIDENT_KEYWORDS: dict[int, tuple[str, ...]] = {
    1: ("epg", "guide", "listing", "blank", "freeview", "9pm", "9 o clock", "nine pm",
        "pub-4012", "pub4012", "publish", "greyed"),
    2: ("duplicate", "dup", "double", "twice", "overlapping", "dedup", "sch-dup",
        "stacked", "double booked", "back to back", "same time"),
    3: ("rights", "licence", "license", "vod", "on demand", "on-demand", "exclusivity",
        "rights window", "takedown", "rgt-excl", "expired", "breach", "compliance",
        "availability window"),
}
_CODE_TO_N = {"PUB-4012": 1, "SCH-DUP-002": 2, "RGT-EXCL-009": 3}


def resolve_incident_n(text: str) -> int | None:
    """Map a chat report to incident n in {1,2,3}, deterministically. Explicit
    'incident N' / 'INC-N' / a normalised error code wins; otherwise the highest
    keyword score. Returns None (no unique class) -> the Watcher asks for clarification
    rather than guessing (fail-closed on ambiguity)."""
    if not text:
        return None
    low = text.lower()
    # explicit incident number
    m = re.search(r"(?:incident|inc)[\s\-#:]*([123])\b", low)
    if m:
        return int(m.group(1))
    # normalised error code (tolerate spaces/dashes and the O/0 garble)
    norm = re.sub(r"[\s\-]", "", low).upper().replace("O", "0")
    for code, n in _CODE_TO_N.items():
        if re.sub(r"[\s\-]", "", code).upper().replace("O", "0") in norm:
            return n
    scores = {n: sum(1 for kw in kws if kw in low) for n, kws in _INCIDENT_KEYWORDS.items()}
    best = max(scores, key=lambda n: scores[n])
    if scores[best] == 0:
        return None
    # require a unique winner (no tie) so an ambiguous report is escalated, not guessed
    if list(scores.values()).count(scores[best]) > 1:
        return None
    return best


# --------------------------------------------------------------------------- #
# serve_chat_turn — the network-free FULL loop, one ASI:One turn at a time.
# Composes the SAME deterministic kernel the console path uses (orchestrator.prepare /
# commit_execution) behind the chat gate. RULE 2: no LLM gates execution or sets a class
# (the STANDING branch makes zero venice calls). RULE 3: a refusal discloses only the
# denied count + owner team. Fail-closed: an expired/absent approval never executes.
# --------------------------------------------------------------------------- #
_STANDING_TIMER = "~15s"


def _audit_tail_hash(conn) -> str | None:
    row = conn.execute("SELECT hash FROM audit_log ORDER BY seq DESC LIMIT 1").fetchone()
    return row["hash"] if row else None


def _execution_reply(prefix: str, res, conn, hops) -> str:
    """Terminal reply after commit_execution: outcome + the hash-chained audit tail
    (provenance the human can cite) + the Watcher->Librarian->Operator hop-trail footer."""
    outcome = res.step_results[0].get("outcome") if res.step_results else "unknown"
    audit = _audit_tail_hash(conn) or "(pending)"
    body = (f"{prefix}\n"
            f"Outcome: {outcome} (verified={res.verified}, rolled_back={res.rolled_back}).\n"
            f"Audit: {audit}")
    return body + hop_trail_footer(hops or [])


def serve_chat_turn(text: str, sender: str, *, conn, tools, pending: dict,
                    principal: str = "scheduling-ops", hops: list | None = None) -> str:
    """Drive ONE chat turn through the full loop and return the reply text. `pending`
    (sender -> Prepared) carries an open gate across the two turns; the DB `approval`
    ledger holds its hard TTL. Composes orchestrator.prepare / commit_execution — the
    deterministic kernel — never an LLM, for every permission/risk/gate decision."""
    if not (text or "").strip():          # P0.1: empty / StartSession -> greet, don't guess
        return greeting()
    approval.ensure_table(conn)
    # 1) fail-closed sweep FIRST: age out any expired gates, and drop their in-process
    #    Prepared in lock-step so a late 'approve' can never find a live plan.
    expired = set(approval.expire_stale(conn))
    for s, p in list(pending.items()):
        req = p.approval_request
        if req is not None and (req.incident_id, req.plan_hash) in expired:
            pending.pop(s, None)

    verdict = decide_from_reply(text)
    live = approval.pending_for_sender(conn, sender)

    # 2) an OPEN gate for this sender -> this turn is the decision (or a reconnect)
    if live and sender in pending:
        prepared = pending[sender]
        req = prepared.approval_request
        if verdict == "approve":
            decision = make_decision(req, sender)                 # approver = sender verbatim
            res = orchestrator.commit_execution(prepared, conn=conn, tools=tools,
                                                decision=decision, actor=sender,
                                                principal=principal)
            approval.mark(conn, req.incident_id, req.plan_hash, "approved")
            pending.pop(sender, None)
            ref = prepared.ref or {}
            action = (prepared.rule or {}).get("action_type", "fix")
            prefix = (f"Approved by {sender}. Executed {action} "
                      f"on {ref.get('object_type','?')} {ref.get('object_id','?')}.")
            return _execution_reply(prefix, res, conn, hops)
        if verdict == "reject":
            approval.mark(conn, req.incident_id, req.plan_hash, "rejected")
            pending.pop(sender, None)
            return (f"Rejected — no change made. Incident {req.incident_id} left untouched. "
                    "Nothing executed (the deterministic gate requires an explicit approval).")
        # reconnect / anything ambiguous while a gate is open -> RE-PRESENT it (never lose it)
        return "You still have a pending approval:\n\n" + render_approval(req, prepared)

    # 3) a decision word with NO live gate -> fail-closed non-action (expired/absent)
    if verdict is not None:
        return ("No live pending approval for you (expired or absent) — non-action "
                "(fail-closed). Re-report the incident to open a fresh gate.")

    # 4) otherwise treat the text as a NEW incident report
    n = resolve_incident_n(text)
    if n is None:
        return ("Couldn't identify the incident class from that report. Please name the "
                "service/error (EPG publish failure, duplicate schedule slot, VOD rights "
                "window) or the incident number, and I'll triage it.")
    payload = tools.incident(n)
    inc = IncidentEvent(incident_id=payload["incident_id"], raw_text=payload["raw_text"],
                        source="chat", observed_at=payload["observed_at"])
    prepared = orchestrator.prepare(inc, structured=payload["structured"], conn=conn,
                                    tools=tools, principal=principal, actor=principal)

    if prepared.outcome == "refused":
        r = prepared.result.step_results[0] if prepared.result.step_results else {}
        cnt = r.get("denied_count", "?")
        owner = r.get("denied_owner_team") or "the owning team"
        # RULE 3: count + owner ONLY — never a title, symptom, body, or secret.
        return (f"Incident {inc.incident_id} — restricted. {cnt} documented remediation(s) "
                f"hidden; owner team: {owner}. No content disclosed (fail-closed).")
    if prepared.outcome == "escalated":
        return (f"Incident {inc.incident_id} — no safe automated fix; routed to a human "
                "(ladder floor). Nothing executed.")

    if prepared.fast:
        # RULE 2: STANDING repeat-class — zero-LLM fast-path, no prompt, ~15s.
        res = orchestrator.commit_execution(prepared, conn=conn, tools=tools,
                                            principal=principal, actor=principal)
        prefix = (f"Incident {inc.incident_id} — {prepared.class_key}\n"
                  f"Standing Approval (pre-approved standard change) — applied in "
                  f"{_STANDING_TIMER}, no prompt (zero-LLM fast-path).")
        return _execution_reply(prefix, res, conn, hops)

    # slow-path: record the gate (hard TTL) + stash the Prepared, present ONE message.
    req = prepared.approval_request
    approval.record_pending(conn, req, sender_address=sender)
    pending[sender] = prepared
    return render_approval(req, prepared)


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
