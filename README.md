<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/brand/precedent-seal-dark.png">
    <img src="assets/brand/precedent-logo.png" alt="Precedent" width="240">
  </picture>
</p>

# Precedent

> **Every incident resolved becomes precedent.**

Precedent is an agent that detects an enterprise incident, retrieves the **documented fix from the organisation's own knowledge** (KB + a permission-aware memory of executed fixes), classifies its risk with a **deterministic policy engine (no LLM in the decision)**, executes it through **typed tools behind an approval gate**, verifies the result and **auto-rolls-back on failure**, and remembers the outcome as an *executed fix with provenance*.

> AI SREs fix broken code. In real enterprises the fix is almost never code — it's a documented admin/config change. Precedent is the layer that retrieves and safely executes it.

Built for the **UK AI Agent Hackathon EP5** across three tracks — Conduct ("Make Legacy Move"), Fetch.ai (Agentverse / Agent Chat Protocol / ASI:One), and BasedAI (permission-aware memory governance).

> **▶ Team, start here: [`GETTING-STARTED.md`](GETTING-STARTED.md)** — setup in ~10 minutes and your first task, per person.
> **New to the project?** Read it in plain words first: [`EXPLAINER-idea-and-plan.md`](EXPLAINER-idea-and-plan.md) (the what and the how) and [`EXPLAINER-roles.md`](EXPLAINER-roles.md) (who does what, thoroughly, no jargon).

## Hard rules (do not break)

- **Open-weight models only.** Every model call goes through the Venice OpenAI-compatible API; the *only* file allowed to name a model is [`precedent/models.py`](precedent/models.py). No OpenAI/Anthropic/Gemini/Grok/closed model touches the runtime pipeline. CI grep guards this (`scripts/check_open_weight.sh`).
- **No LLM in any permission or risk decision.** The model may *propose*; the deterministic policy engine and a human identity *dispose*.
- **No secrets committed.** `.env` is gitignored; use `.env.example`. Verified clean via `gitleaks` across all history.
- **Fail-closed.** When ACL freshness is uncertain, restricted memory is denied, never served.

## Architecture (the closed loop)

```
DETECT → TRIAGE → RETRIEVE (KB + memory, ACL-filtered) → RISK-CLASSIFY (deterministic)
      → GATE (human approval / standing approval) → EXECUTE (typed tools) → VERIFY
      → (auto-rollback on failure) → MEMORISE (executed-fix-with-provenance)
```

| Package / dir | What it is | Owner (build plan) |
|---|---|---|
| [`precedent/`](precedent/) | Core loop: model registry, message contracts, deterministic extractor + fingerprint, YAML policy engine, ladder + fast-path, orchestrator | T1 |
| [`precedent_memory/`](precedent_memory/) | Standalone permission-aware memory library (A/B/C lineage semantics, fail-closed retrieval, hash-chained audit, conformance bench) | T2 / T3 |
| [`sim/`](sim/) | MediaCo simulated services (scheduler/rights/publisher/kb) seeded with real public data | T1 |
| [`console/`](console/) | Server-rendered + SSE demo console (Baseline Bar, Approve/Promote/Revoke, trace, audit) | T2 |
| [`agents/`](agents/) | Fetch.ai rails: Watcher / Librarian / Operator (Agentverse mailbox agents, Chat Protocol) | T1 |
| [`data/`](data/) | Committed raw seed data + the UCI baseline analysis | data lane |
| [`docs/`](docs/) | Compliance evidence (`/models` dumps), the evidence index | — |

Full detail: [`Idea/refinement/02-architecture-refinement.md`](Idea/refinement/02-architecture-refinement.md). Build plan: [`Plan/BUILD-PLAN.md`](Plan/BUILD-PLAN.md). Project skill: [`.claude/skills/precedent/SKILL.md`](.claude/skills/precedent/SKILL.md).

## Setup

```bash
# 1. Environment (Python 3.11+; uv recommended)
uv venv --python 3.13
uv pip install -e ".[dev]"          # core + dev; add ".[dev,agents]" for the Fetch rails

# 2. Credentials — copy the template and fill from your own secrets (never commit .env)
cp .env.example .env                 # then edit

# 3. Sanity checks
make check-open-weight               # CI guard: model names appear only in precedent/models.py
make test                            # pytest (spec skeletons skip until implemented)
make secrets-scan                    # gitleaks full-history scan (must be clean before repo goes public)
```

## Run (once scaffolding is implemented)

```bash
make sim        # MediaCo sim + console on localhost
make demo-reset # reset sim state, memory counters, ladder — <30s between rehearsals
make bench      # conformance bench → precedent_memory/bench/RESULTS.md
```

## Open-weight models (BasedAI declaration)

| Role | Venice model | Weights | Licence |
|---|---|---|---|
| FAST (triage) | `qwen3-5-35b-a3b` | [Qwen/Qwen3.5-35B-A3B](https://huggingface.co/Qwen/Qwen3.5-35B-A3B) | Apache-2.0 |
| SMART (synthesis) | `deepseek-v4-flash` | [deepseek-ai/DeepSeek-V4-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) | MIT |
| HEAVY (dossiers) | `deepseek-v4-pro` | [deepseek-ai/DeepSeek-V4-Pro](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro) | MIT |
| EMBED | `text-embedding-bge-m3` | [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) | MIT |

Verified live against `GET /models` + Hugging Face on 3 Jul 2026; evidence dumps in [`docs/compliance/`](docs/compliance/).

## Data provenance

Real public data through simulated services: UCI ServiceNow incident log (CC BY 4.0, 141k events) as day-one memory; TVmaze GB schedule (CC BY-SA) + Freeview XMLTV for the EPG; CC0 Kaggle catalogs for rights; runbooks adapted from real published procedures (CrowdStrike CF-291, GitLab, kube-prometheus). Only licence-window terms are synthesised, by a stated rule. TMDB/IMDb rejected on licence grounds. Full plan: [`Idea/refinement/01-realistic-data-plan.md`](Idea/refinement/01-realistic-data-plan.md).

## License

MIT (see [`LICENSE`](LICENSE)).
