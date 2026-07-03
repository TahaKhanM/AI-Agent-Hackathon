"""Fetch.ai rails: Watcher / Librarian / Operator.  [STUBS — owner T1, task T1-8; register T3-2]

Spec: Idea/refinement/02 §3.4 + 05-scale-story-and-qa.md §E.

Three Agentverse MAILBOX agents (outbound-only; no public IP; survive venue NAT):
- Watcher   — gateway + triage; speaks the Agent Chat Protocol (the ASI:One entry point)
- Librarian — retrieval + memory governance (ACL-filtered)
- Operator  — execution + Jira writes

Chat Protocol import (verified on Python 3.13 this session):
    from uagents_core.contrib.protocols.chat import (
        ChatMessage, ChatAcknowledgement, TextContent, chat_protocol_spec,
    )
    agent.include(chat_proto, publish_manifest=True)

Approval-via-ASI:One is a REAL gate: the chat sender address = the authorising principal
in the audit log; pending approvals expire (10-min TTL) — a dropped session never leaks
an execution. Each agent README MUST carry both badges (innovationlab + hackathon).
Discoverability is activity-gated (>=10 interactions) — register early, run test chats.
"""
