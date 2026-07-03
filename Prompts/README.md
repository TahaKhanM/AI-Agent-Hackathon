# Ultracode session prompts

Two prompts for one Fable 5 ultracode session, run in sequence. Written to Anthropic's Fable 5 prompting guidance: the full task specification up front in a single well-specified turn, goals and constraints rather than step enumeration (over-prescriptive prompts measurably reduce Fable output quality), explicit autonomy and grounded-progress rules, and licence to delegate to parallel sub-agents. Both prompts were adversarially reviewed by a three-critic panel (Fable-prompting alignment, fact-check against the repo, ops feasibility) and revised.

## Before starting the session (human checklist)

- **Submit the Demo Day sign-up form before 18:00 Friday 3 July** (https://forms.gle/fnUe3vL24wyJo6pD7) — the session is told to assume this is handled and will not do it for you.
- While the session runs, execute the human items from `Idea/Idea-Development.md` §6 in parallel (JSM Standard trial confirmation, Venice model-ID check if not already done, Fetch account setup) — the plan will assume these are underway.
- `.env` populated per `CREDENTIALS-CHECKLIST.md` (never committed). `CLAUDE-AVAILABLE-APIS.md` should reflect current provisioning state — the prompts treat it as ground truth, read precisely.
- **Higgsfield MCP:** if you want AI-generated video elements planned as more than an optional track, connect the Higgsfield MCP to the session first (and note there is currently no Higgsfield account/config in this repo). The prompt tells the session to check for it and to plan a screen-recording-only cut as primary if absent — so skipping this is safe.
- Decide N1/N2's claude.ai plan tier and correct the plan's assumptions box if needed.
- Internet access for live verification of bounty pages, Fetch docs, and the BasedAI submission repo.

## How to run

1. Open a fresh Claude Code session **in this repo's root** with the model set to Fable 5.
2. Paste the full contents of [01-ultracode-idea-refinement.md](01-ultracode-idea-refinement.md) as the first message. The leading `ultracode` keyword opts the session into multi-agent Workflow orchestration; optionally append a token-budget directive to that first line (e.g. `ultracode +800k`) to set explicit scale.
3. Let it run to completion (expect a long autonomous run — multi-round judge/build/verify loops). Read its final report; it separates what it decided from decision points it left to the team, and reports its hour-ledger balance and any failed live checks.
4. In the **same session** (context intact), paste the full contents of [02-ultracode-build-plan.md](02-ultracode-build-plan.md). It also begins with the `ultracode` keyword (harmless if the opt-in persists, essential if it is per-message). It produces `Plan/BUILD-PLAN.md`, the non-technical workflow packets in `Plan/workflows/`, the build-independent prep drafts in `Prep/`, and `Plan/prep-spec.md`.

## 03 — T1 build prompt (Opus 4.8, run after the plan exists)

[03-ultracode-t1-completion.md](03-ultracode-t1-completion.md) is a **separate, later** prompt: a fully-specified, autonomous brief for a fresh **Claude Opus 4.8** `ultracode` session to **implement T1** (the core loop, the sim + seed data + KB corpus, and the Fetch rails) against the merged T2 memory/console. Unlike 01/02 (which produce docs on Fable 5), this one writes code — so it opens on branch `build/t1-core-loop-sim-agents`, leads with the four hard rules, pins the resolved decisions (T1 self-sufficient on data+KB with N1 reviewing; airplane-first + one live Venice proof; seed `4207`), gives the exact T2 integration contract, and ends on a run-it-yourself acceptance checklist. Two human decisions are baked in as defaults; the rest of the human steps (Agentverse registration, the 2nd Jira seat) are documented for a teammate, not attempted headless.

## Why two prompts, one session

Prompt 1 refines the *idea* (multi-agent judges → builders → adversarial verification → re-judge with anti-inflation rules, against the tracks' published criteria). Prompt 2 turns the refined idea into the *execution plan* for the five-person team (T1/T2 on Claude Max + ChatGPT Pro carry the programming; T3 on Claude Pro takes bounded tasks; N1/N2 run Claude workflow packets for deck, video, submissions, outreach and rehearsal). Keeping them in one session means the planner has full context of every refinement decision without re-reading — and the split keeps each mission's "done" unambiguous, with a human checkpoint between idea and plan.
