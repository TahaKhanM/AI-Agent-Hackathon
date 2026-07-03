---
name: precedent
description: >-
  Architecture, hard rules and working conventions for the Precedent codebase — the
  UK AI Agent Hackathon EP5 entry: an approval-gated agent that retrieves an
  organisation's documented fix and executes it with audit and rollback. Use this
  skill whenever working ANYWHERE in this repo — writing or reviewing code in
  precedent/, precedent_memory/, sim/, console/, agents/, or data/; touching the
  model registry, the permission/ACL memory layer, the deterministic risk gate, the
  approval ladder, the demo console, the Fetch.ai agents, or the seed data; and
  whenever a task involves the open-weight-only rule, "no LLM in the decision",
  fail-closed behaviour, the demo gates, or the hackathon submission artifacts
  (DoraHacks / BasedAI PR / Fetch deliverables). Load it BEFORE editing any file
  here so the four hard rules and the build-plan gate discipline are respected —
  they are easy to violate by accident and expensive (eligibility-fatal) to get wrong.
---

# Working on Precedent

Precedent detects an enterprise incident, retrieves the **documented fix from the org's own knowledge**, classifies its risk **deterministically**, executes it through **typed tools behind an approval gate**, verifies and **auto-rolls-back on failure**, and remembers the outcome as an *executed fix with provenance*. The thesis: *AI SREs fix broken code; in real enterprises the fix is almost never code — it's a documented admin change.*

It targets three hackathon tracks at once, and each imposes a non-negotiable constraint. Getting any of the four hard rules below wrong doesn't just lower a score — it can make the entry **ineligible** for a track. Treat them as invariants, not preferences.

## The four hard rules (violating these is eligibility-fatal)

1. **Open-weight models only.** Every model call goes through the Venice OpenAI-compatible HTTP API. The *only* file allowed to name a model id is [`precedent/models.py`](../../../precedent/models.py). No `claude-*`, `openai-*`, `gpt-*`, `gemini-*`, `grok-*` — anywhere in the runtime, **including the embedding model**. *Why:* BasedAI's rule is "open-weight only, no closed models in the loop"; Venice also hosts closed models, so "it runs on Venice" is not a defence — the pinned ids are verified against public Hugging Face weights (evidence in `docs/compliance/`). Guard: `make check-open-weight` (a grep that must return only `models.py`'s own comment lines). If you need a model in new code, import a *role* (`FAST`/`SMART`/`HEAVY`/`EMBED`) from `precedent.models`, never a literal id.

2. **No LLM in any permission or risk decision.** The model may *propose* candidate fields, classes or prose; the **deterministic policy engine** and a **human identity** decide what executes. `precedent_memory/retrieve.py` must have zero LLM imports. The incident-class key is a computed fingerprint `sha256(service|error_code|target_object_type)` from a deterministic extractor — a class match counts only on extractor-confirmed field *equality*, never on semantic similarity. *Why:* both Conduct ("a fully autonomous agent is a non-starter") and BasedAI ("no LLM call in the permission decision") require it, and it's the moat — "the model narrates, deterministic policy disposes".

3. **Fail-closed.** When ACL freshness is uncertain (Jira unreachable, cache stale), restricted memory is **denied**, never served. A stale cache may narrow access, never widen it. *Why:* a leak is worse than an outage for the enterprise buyer; the fail-closed banner is a visible safety feature on stage, not an apology.

4. **No secrets committed.** `.env` is gitignored (verified clean across all history with `gitleaks`). Use `.env.example` with placeholder *names* only. Never paste a key, token, or a teammate's real name into code, a commit, or a prompt sent to a model. *Why:* the repo goes public (a Fetch hard gate) and the BasedAI PR is public — one leaked key fails the scrub gate.

## Package layout & who owns what (build plan §4)

| Path | What it is | Rules that bite hardest here |
|---|---|---|
| `precedent/models.py` | The open-weight registry + startup guard. **The only file that may name a model.** | Rule 1 |
| `precedent/` | Core loop: contracts (pydantic), deterministic extractor + fingerprint, YAML policy engine, ladder + standing-approval fast-path (zero LLM), orchestrator | Rules 1, 2 |
| `precedent_memory/` | Standalone permission-aware memory library — A/B/C lineage semantics (conjunction over ALL sources), precompiled effective-policy bitmaps (the P99 fast path), hash-chained audit, fail-closed retrieval, conformance bench | Rules 2, 3 |
| `sim/` | MediaCo simulated services (scheduler/rights/publisher/kb) seeded with **real public data**. Keep the real data's messiness (nulls, dup titles) — it's demo fodder, don't sanitise it | data honesty (below) |
| `console/` | Server-rendered page + SSE (no framework). Build order is load-bearing: **Baseline Bar + Approve/Promote/Revoke buttons FIRST** (the 18:00 vertical-slice gate needs exactly these) | demo gates |
| `agents/` | Fetch rails: Watcher / Librarian / Operator as Agentverse mailbox agents. Chat Protocol via `from uagents_core.contrib.protocols.chat import ...` + `publish_manifest=True`. Approval principal = chat sender address | Fetch gates |
| `data/`, `docs/` | Committed raw seed + UCI baseline analysis; compliance evidence + the evidence index | data honesty |

## Coding conventions

- **Match the existing spec, don't reinvent.** The authoritative design already exists — read the relevant `Idea/refinement/` file (below) before designing. `precedent_memory/schema.sql` and the test skeletons in `precedent_memory/tests/` are already written from the spec; implement to green, don't redesign the schema.
- **Typed everywhere the contract crosses a boundary.** Inter-agent and loop messages are pydantic models in `precedent/contracts.py`; the Operator executes only *typed tool calls*, never free-form shell.
- **Deterministic seeds.** The incident generator and the mutation corpus take a fixed seed so a demo replays identically and one number backs four surfaces (chip, slide, README, BUIDL). One canonical seed, declared at the Friday stand-up.
- **Local-first / airplane-mode.** Embeddings precomputed and committed; Jira via 2–3 s polling + write-behind cache (no webhooks); the standing-approval fast-path skips all LLM calls. The demo must pass with Wi-Fi off.
- **Honest data.** The *services* are simulated; the *content* is real public data (labelled licences). Never present invented data as real; never claim real data the build didn't actually seed. TMDB/IMDb are rejected on licence grounds — don't reintroduce them.

## Demo & gate discipline (build plan §1)

The build runs to hard gates, in this locked order: **vertical slice → code freeze + video capture → BasedAI draft PR → rehearsal go/no-go.** The mandatory cut-fire checkpoint (G1) and the immovable 18:00 vertical-slice gate protect the demo — if you're behind, fire the pre-ordered cut-lines (C-flow demo → temporal extras → third agent in-process → incident 3 video-only), never cut incidents 1+2 or the Fetch hard gates. Terminology on stage and in UI: **L3 is "Standing Approval", never "Autonomous".**

## Before you claim done — run the checks

```bash
make check-open-weight   # rule 1 guard: model names appear only in precedent/models.py
make test                # pytest (spec skeletons skip until implemented)
make secrets-scan        # gitleaks full-history; must be clean before the repo goes public
.venv/bin/ruff check .   # lint
```

## Authoritative spec files (read the relevant one before designing; this skill points, it does not duplicate)

- **Idea & thesis:** `Idea/Idea-Development.md` (v5, the master summary)
- **Architecture, models, A/B/C semantics, topology, build order:** `Idea/refinement/02-architecture-refinement.md` — the deepest technical source
- **Data plan & licences:** `Idea/refinement/01-realistic-data-plan.md`
- **Deck / demo script / scale story & Q&A:** `Idea/refinement/03`, `04`, `05`
- **Verified session facts (Venice/Jira/UCI) + adoption ledger:** `Idea/refinement/06-session-working-notes.md`
- **The execution plan (gates, tasks, hours, risks):** `Plan/BUILD-PLAN.md`
- **What's provisioned right now (keys, ids, tiers):** `CLAUDE-AVAILABLE-APIS.md`
- **Every stat's verified source + caveat labels:** `Research/00-verified-claims.md` — nothing goes on a slide or in a caption without tracing here.

## Common ways to get this wrong (don't)

- Writing a model id (even in a test or a comment) outside `precedent/models.py` → breaks the CI grep and rule 1.
- Letting an LLM output gate execution or set a risk class → breaks rule 2 and the whole trust story.
- Adding a webhook/ngrok dependency to the Jira path → dies on venue Wi-Fi; use polling + write-behind.
- Sanitising the seed data's nulls/duplicates → removes the messiness the Conduct rubric rewards.
- Quoting a number without checking `Research/00-verified-claims.md` and keeping its caveat label (e.g. UCI medians are *calendar* hours, never blended with MetricNet's *business* hours).
- Saying "Autonomous" for L3, or claiming the sponsor "endorsed our design" (credit the public Discord thread instead).
