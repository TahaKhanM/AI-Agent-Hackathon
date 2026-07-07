---
name: precedent
description: >-
  Architecture, hard rules and working conventions for the Precedent codebase — an
  approval-gated agent that retrieves an organisation's documented fix and executes
  it with audit and rollback. Born at the UK AI Agent Hackathon EP5 (submitted
  4 Jul 2026), now developed as a startup. Use this skill whenever working ANYWHERE
  in this repo — precedent/, precedent_memory/, sim/, console/, agents/, data/,
  docs/, or the hosted-demo kit — and whenever a task involves the model registry,
  the permission/ACL memory layer, the deterministic risk gate, the approval ladder,
  the demo console, or the four hard rules (open-weight registry, no LLM in
  decisions, fail-closed, no secrets). Load it BEFORE editing any file here — the
  rules are easy to violate by accident and expensive to get wrong.
---

# Working on Precedent

Precedent detects an enterprise incident, retrieves the **documented fix from the org's own knowledge**, classifies its risk **deterministically**, executes it through **typed tools behind an approval gate**, verifies and **auto-rolls-back on failure**, and remembers the outcome as an *executed fix with provenance*. The thesis: *AI SREs fix broken code; in real enterprises the fix is almost never code — it's a documented admin change.*

Built and submitted at the UK AI Agent Hackathon EP5 (4 Jul 2026; record in `docs/archive/hackathon/`). It is now a startup codebase. The four hard rules below began as track-eligibility constraints; **they survive as the product's trust doctrine** — "nothing closed, nothing unauditable, in the decision path" is the pitch, not a compliance chore. Change them only as a deliberate, recorded product decision — never incidentally in a PR.

## The four hard rules

1. **Open-weight models only, one registry.** Every model call goes through the Venice OpenAI-compatible HTTP API. The *only* file allowed to name a model id is [`precedent/models.py`](../../../precedent/models.py). No `claude-*`, `openai-*`, `gpt-*`, `gemini-*`, `grok-*` anywhere in the runtime, **including the embedding model**. Venice also hosts closed models, so "it runs on Venice" proves nothing — the registry asserts every entry's `modelSource` is a public huggingface.co URL (evidence in `docs/compliance/`). Guard: `make check-open-weight`. Need a model in new code? Import a *role* (`FAST`/`SMART`/`HEAVY`/`EMBED`) from `precedent.models`, never a literal id.

2. **No LLM in any permission or risk decision.** The model may *propose* candidate fields, classes or prose; the **deterministic policy engine** and a **human identity** decide what executes. `precedent_memory/retrieve.py` must have zero LLM imports. The incident-class key is a computed fingerprint `sha256(service|error_code|target_object_type)` from a deterministic extractor — a class match counts only on extractor-confirmed field *equality*, never semantic similarity; `llm_proposed` extraction never builds an executable plan. This is the moat: "the model narrates, deterministic policy disposes".

3. **Fail-closed.** When ACL freshness is uncertain (Jira unreachable, cache stale), restricted memory is **denied**, never served. A stale cache may narrow access, never widen it. Refusals disclose only a count + owning team, never content. Every hardening decision fails toward non-action.

4. **No secrets committed.** `.env` is gitignored (history verified with `gitleaks`; `make secrets-scan`). Use `.env.example` with placeholder names only. **The repo is PUBLIC and an external auto-sync pushes local `main` immediately — committing to main IS publishing.**

## Package layout

| Path | What it is | Rules that bite hardest |
|---|---|---|
| `precedent/models.py` | Open-weight registry + startup guard. **The only file that may name a model.** | 1 |
| `precedent/` | Core loop: pydantic contracts, deterministic extractor + fingerprint, YAML policy engine, ladder + standing-approval fast-path (zero LLM), orchestrator, typed tools | 1, 2 |
| `precedent_memory/` | Permission-aware memory library — A/B/C lineage semantics (conjunction over ALL sources), precompiled effective-policy bitmaps, hash-chained audit, fail-closed retrieval, conformance bench + independent oracle | 2, 3 |
| `sim/` | MediaCo simulated services seeded with **real public data** (keep its messiness — nulls and dup titles are by design) | data honesty |
| `console/` | Server-rendered demo console + `showcase.py` guided tour; `Dockerfile`/`render.yaml` host it offline-by-design | — |
| `agents/` | Fetch.ai rails: Watcher / Librarian / Operator mailbox agents (Chat Protocol; approval principal = chat sender address) | 2 |
| `data/`, `docs/` | Committed seed + UCI analysis; docs tree below | data honesty |

## Docs tree (post-reorg, 6 Jul 2026)

- **Thesis & specs:** `docs/idea/Idea-Development.md` (master summary), `docs/idea/refinement/02-architecture-refinement.md` (deepest technical source), `01` data plan, `03/04` deck & demo scripts, `05` scale story + Q&A bank, `06` verified session facts
- **Canonical numbers:** `docs/numbers.md` — no shipped surface may state a number that is not on that page, with its label (calendar vs business hours; existence vs arrival-knowable; vendor-claimed tags)
- **Verified market claims:** `docs/research/00-verified-claims.md` (+ chapters 01–07)
- **Ops / accounts / env:** `docs/ops/services.md` (Venice, Jira trial expiry ~17 Jul 2026, Agentverse agents, env vars)
- **Evidence:** `docs/evidence/` (claim→proof index, LIVE-PROOFS), `docs/compliance/` (model dumps), `docs/data-provenance.md`
- **Demo:** `docs/demo/` (systems walkthrough, airplane-mode, one-minute demo, walkthrough script)
- **Hackathon record (frozen):** `docs/archive/hackathon/`

## Coding conventions

- **Match the existing spec.** Read the relevant `docs/idea/refinement/` file before redesigning; implement to the tests. Typed contracts (`precedent/contracts.py`) cross every boundary; the Operator executes only typed tool calls, never free-form shell.
- **Deterministic seeds.** The incident generator, mutation corpus and bench take fixed seeds (canonical: **4207**) so runs replay identically and one number backs every surface.
- **Local-first / airplane-mode.** Embeddings precomputed and committed; Jira via 2–3 s polling + write-behind cache (no webhooks); the standing-approval fast-path makes zero LLM calls. The demo must pass with Wi-Fi off.
- **Honest data & numbers.** Services simulated, content real (licences recorded; TMDB/IMDb stay rejected). Never present invented data as real. Quote numbers only from `docs/numbers.md` with their caveat labels; never blend 18.2 h (calendar, ours) with 8.85 h (business, MetricNet). **L3 is "Standing Approval", never "Autonomous".**

## Before you claim done

```bash
make check-open-weight   # rule 1 guard
make test                # pytest — 256 passed, 0 skipped is the baseline
make lint                # ruff
make secrets-scan        # gitleaks full history
make freeze-check        # all of the above + placeholder grep (release gate)
```

## Common ways to get this wrong (don't)

- Writing a model id (even in a test or comment) outside `precedent/models.py`.
- Letting an LLM output gate execution, set a risk class, or unlock a fast-path.
- Adding a webhook/inbound-tunnel dependency to the Jira path (polling + write-behind is the design).
- Sanitising the seed data's nulls/duplicates.
- Quoting a number that isn't in `docs/numbers.md`, or dropping its caveat label.
- Saying "Autonomous" for L3, or claiming the BasedAI sponsor "endorsed our design" (credit the public Discord thread instead).
- Forgetting the auto-sync: anything committed to `main` is public seconds later.
