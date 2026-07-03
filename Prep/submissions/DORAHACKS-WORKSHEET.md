# DoraHacks BUIDL — one-shot organizer-answer worksheet

**Event:** `2272` · **Bounties to tick (exactly these three, deselect any extras):**
`1370` (Conduct — Make Legacy Move) · `1367` (Fetch.ai) · `1364` (BasedAI).

**One-shot trap:** organizer-defined question answers are submitted **once and locked** at draft
submit — they can never be edited. Every other BUIDL field stays editable until the deadline. So:
open the BUIDL form for event 2272 **without submitting**, copy each organizer question **verbatim**
into the table below, fill from the drafts, get **T1 sign-off on every answer**, resolve every
`[NEEDS-FACT]`, then enter the signed answers **character-for-character**. Submit before
**23:59 BST / 22:59 UTC** (never the last hour). Screenshot; commit the final page text to
`docs/evidence/dorahacks-buidl.md`.

Pre-submit Ctrl-F check: no `‹`, no `XX`, no `TODO`, no `TBD`; incognito link-check (repo public +
README renders, video plays, ASI:One shared-chat URL loads, Agentverse profiles load with badges,
BasedAI PR link loads, `bench/RESULTS.md` path correct).

## Standard BUIDL fields (drafts — editable until deadline)

**Name:** Precedent

**Tagline:** Permission-aware agent memory — retrieve your org's own documented fix, only for who's
allowed to see it, and prove it.

**What it does / how it works:** (use the BASEDAI-PR-README.md "What it does" + "How it works"
sections verbatim — one narrative across all surfaces.)

**Tech stack:** Python 3.13; SQLite effective-policy bitmaps + hash-chained audit; Venice
open-weight models (Qwen 3.5 35B-A3B, DeepSeek V4 Flash/Pro, BGE-M3 — no closed model anywhere);
Fetch.ai uAgents (3 Agentverse mailbox agents, Agent Chat Protocol); Jira Service Management (live
ACL source). No LLM in the permission or risk decision.

**Repo:** <public repo URL — fill after the repo-public flip>
**BasedAI PR:** <PR URL>
**Demo video:** <unlisted video URL — Saturday>
**Agentverse profiles:** Watcher / Librarian / Operator <3 URLs — after registration>
**ASI:One shared chat:** <shared-chat URL — after ≥10-interaction discoverability run>

**Headline measured numbers (one number, four surfaces — keep identical to deck/README/chip):**
- Conformance vs BasedAI's rubric: full green-tick table, **FNR 0 leaks / 5,219 deny-expected**,
  graded by an **independent oracle** (two implementations cross-checked, not self-graded).
- **6/6** named adversarial attacks.
- Extractor robustness (seed-4207 · 100-mutation corpus): **0 false-fast-paths / 100 (0.00%)** — no
  messy ticket produced a wrong confident class that could fast-path a wrong fix — and **25/25
  red-herring decoys resisted**. (Breakdown: correct-match 8 · safe-degrade 50 · conservative-degrade
  42 · false-fast-path 0. Source: `precedent_memory/bench/extractor_robustness.json`, `make bench-extractor`.)
- Realism: UCI **25k-record store** (24,918 incidents; never "141k events") — live P99 posted Saturday.

## Organizer-defined one-shot questions (COPY VERBATIM from the live form, then fill)

> The exact questions are only visible on the live event-2272 form. Paste each here verbatim, fill
> from the drafts above, get T1 sign-off, then enter into the form character-for-character.

| # | Question (verbatim from the form) | Signed answer | T1 sign-off |
|---|---|---|---|
| 1 | `[copy from form]` | `[fill]` | ☐ |
| 2 | `[copy from form]` | `[fill]` | ☐ |
| 3 | `[copy from form]` | `[fill]` | ☐ |

**Per-sponsor "why this bounty" (likely organizer questions — drafts ready):**
- **BasedAI (1364):** Permission-aware agent memory graded in BasedAI's own evaluation vocabulary
  — full metric table vs threshold, 6/6 adversarial attacks, and an **independent oracle** so
  FNR/FPR are a genuine two-implementation cross-check rather than the exam grading itself.
- **Fetch.ai (1367):** Three Agentverse mailbox agents (Watcher/Librarian/Operator) on the Agent
  Chat Protocol; the ASI:One chat sender address is the authorising principal at a real approval
  gate with a 10-minute TTL — a dropped session never leaks an execution.
- **Conduct (1370) — Make Legacy Move:** a legacy enterprise motion (a documented admin fix gated
  by Jira permissions) executed by an agent behind an approval gate with audit + auto-rollback,
  with graduated autonomy — approval moves earlier in time, never out of the loop.
