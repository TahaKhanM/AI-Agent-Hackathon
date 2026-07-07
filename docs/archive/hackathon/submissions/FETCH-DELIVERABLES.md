# Fetch.ai deliverables checklist (bounty 1367)

The Fetch hard gates + the three account-bound artifacts. Everything code-side is prepared to a
single human action; the account-bound acts (registration, ASI:One capture, URL fills) stay human.

## Hard gates (each must be demonstrably true before submit)

| Gate | State | Evidence / where |
|---|---|---|
| ≥1 agent on Agentverse | code ready — **human registers** | `agents/watcher.py` / `librarian.py` / `operator.py` build as MAILBOX agents with stable env seeds (`WATCHER_/LIBRARIAN_/OPERATOR_AGENT_SEED`); addresses survive the B1 handler swap |
| Agent Chat Protocol | ✅ done | Watcher includes `chat_protocol_spec` (`publish_manifest=True`); the LIVE handler runs the full loop (B1), not an echo |
| Core use case demonstrable INSIDE an ASI:One conversation | code ready — **human runs ≥10 discoverability chats** | `serve_chat_turn` drives report → approval gate → execute → audit-hash reply entirely in chat; keyword-rich `DESCRIPTION` drives discoverability |
| Meaningful tool execution / multi-agent | ✅ done | The three agents exchange **real `PRECEDENT_PROTOCOL` messages on the wire**: `agents/rails.py::shadow_hops` sends a typed `TriageMsg`→Librarian (ACL retrieval) and `PlanMsg`→Operator (typed SimTools execution) via uAgents `send_and_receive`, and `scripts/run_agents.py` runs a **startup rails self-check** that logs the real per-hop ms (`[rails self-check] real Watcher->Librarian round-trip`). Each agent carries only its own handler (own `Protocol` instance) and only accepts messages from the Watcher (sender allowlist). The in-process deterministic kernel stays authoritative for the chat reply (latency + determinism unchanged); the rails carry the provenance hop-trail. |
| Primary workflow works WITHOUT a custom frontend | ✅ done | the whole loop runs from an ASI:One chat message; no bespoke UI required |
| Public repo | ✅ (already public) | verify logged-out in incognito that no secret is exposed (gitleaks clean) |

## Both mandatory badges present on every agent README

`agents/README.md` carries both (verified): `![tag:innovationlab]` and `![tag:hackathon]`. Each agent
passes `readme_path=agents/README.md, publish_agent_details=True`, so a plain re-run publishes the
badges to that agent's Agentverse profile.

## The three account-bound artifacts to capture (fill after registration)

| Artifact | URL | Status |
|---|---|---|
| Watcher Agentverse profile | `https://agentverse.ai/agents/details/agent1q2m0gk9wdvs0lyc3nfuyeet4y3nc68m9y24kehun2t70hadwf7qxjcgkldx/profile` | **registered · active** (confirmed via Almanac API 2026-07-04) |
| Librarian Agentverse profile | `https://agentverse.ai/agents/details/agent1qv760pr29kmy9w5lst4tffr06rv6qqmt0ef74w6ycfezd5hfh0e0kse9xv7/profile` | **registered · active** |
| Operator Agentverse profile | `https://agentverse.ai/agents/details/agent1qwesj8x7797jatzt3dwn8gxk2skxsaghrcpa76n548s6a6fz97wvuxna02g/profile` | **registered · active** |
| ASI:One shared-chat URL | `https://asi1.ai/invite?channelInviteKey=NmIsH5-DHQVhnf78uThoWX3fVkRXiSpGz78rMsPkoUQ` | **captured** — full loop (approve → standing fast-path → refusal) inside ASI:One, no frontend |

All four Fetch artifacts are now captured: the 3 profile URLs (Almanac-confirmed `status=active`) and
the ASI:One shared-chat URL of a live conversation demonstrating the core use case inside ASI:One —
report → approval gate → execute + audit hash, the zero-LLM standing repeat, and the fail-closed refusal.
Verify the invite link opens for a logged-out viewer before submitting (incognito check).

## Agent-count honesty rule

Say **"Three on Agentverse" only if three register.** If only two register, say "Two on Agentverse"
(Assessor/Auditor are in-process by design). Never claim three if two are registered.

## Post-hackathon bonus

Deploy the hosted **degraded-L0 Watcher** (`agents/watcher.build_degraded_watcher()`) — answers a
described incident at L0 without MediaCo creds, never executes — kept running on Agentverse.
