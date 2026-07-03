# Getting started — read this, then start building (all five of you)

This gets you from a fresh clone to your first real commit in ~10 minutes. The repo is **already scaffolded**: packages, a tested model registry, the memory schema, spec-encoding tests, a Makefile, and a stub for every module that names its spec section and owner. You are filling in a frame, not starting from a blank page.

**First, read the project skill:** [`.claude/skills/precedent/SKILL.md`](.claude/skills/precedent/SKILL.md). It's short and it carries the **four hard rules** that are eligibility-fatal to break. Your AI coding tool should load it automatically when you work in this repo; read it yourself once anyway.

---

## 1. Setup (everyone, once — ~5 min)

```bash
# You already have the repo. From its root:
uv venv --python 3.13                 # create the virtualenv
uv pip install -e ".[dev,agents]"      # core + dev + Fetch (uagents) — all verified on 3.13
cp .env.example .env                   # then fill from the team's real secrets — NEVER commit .env

# Prove the scaffold is wired (should be green):
make test                              # 4 scaffold smoke tests PASS, 9 spec tests SKIP (until you implement them)
make check-open-weight                 # BasedAI guard: model names only in precedent/models.py
```

If those two commands are green, you're ready. The 9 skips are the spec you implement; the 4 passes prove the registry, contracts, schema and fingerprint are already working.

The `.env` already documents every variable, with the verified Jira role/issue-security IDs pre-filled. You need real keys for Venice / Jira / Agentverse / ASI:One (the team has them) — but a lot of work (memory package, tests, the bench, KB articles, deck) needs **no** live keys.

## 2. How we work in parallel

Everyone has repo access and a capable AI tool. To avoid collisions, **each person works on their own branch** (already created) and merges at the phase boundaries (see [`Plan/BUILD-PLAN.md`](Plan/BUILD-PLAN.md) §2). Optionally use a git worktree so you can keep `main` checked out too:

```bash
git checkout <your-branch>                      # your branch is listed in §4 below
# or, for an isolated working copy:
git worktree add ../precedent-<you> <your-branch>
```

**Driving your AI tool:** point it at the **spec section named in your task** plus the project skill, tell it to implement to the spec (not redesign it), and make it **run `make test` / `make check-open-weight` before it claims done**. The specs in `Idea/refinement/` are the source of truth.

## 3. The four hard rules (full detail in the skill — internalise these)

1. **Open-weight models only.** Import a *role* (`FAST`/`SMART`/`HEAVY`/`EMBED`) from `precedent.models`; never write a literal model id anywhere but `precedent/models.py`. `make check-open-weight` guards it.
2. **No LLM in any permission or risk decision.** The model proposes; the deterministic policy engine and a human dispose. `precedent_memory/retrieve.py` has zero LLM imports.
3. **Fail-closed.** Uncertain ACL freshness → deny restricted memory, never serve it.
4. **No secrets committed.** `.env` is gitignored and history is verified clean; use `.env.example`.

## 4. Your first task — start here (by person)

Profiles map to people at the G0 stand-up. Find yours, check out the branch, open the two files, and go. Your full mission is in [`Plan/BUILD-PLAN.md`](Plan/BUILD-PLAN.md) §4; your detailed brief (where one exists) is in [`Plan/workflows/`](Plan/workflows/).

### T1 — core loop, sim, Fetch rails · branch `build/t1-core-loop-sim-agents`
**Own:** the engine the demo runs on. **Start now:**
```bash
git checkout build/t1-core-loop-sim-agents
```
Open `precedent/venice.py` (stub) and `precedent/models.py` (done). First task: implement the Venice chat + embeddings client using the model *roles*, add the `/models` startup guard, and register a hello-world Chat-Protocol Watcher on Agentverse to start the discoverability clock. *Drive your tool:* "implement `venice.py` per `Idea/refinement/02-architecture-refinement.md` §1.3 using `precedent.models` roles; then a minimal uagents mailbox echo agent with the Chat Protocol import shown in `agents/__init__.py`." Verify: one real ASI:One round-trip; `make check-open-weight` clean. **Then** move to the sim (`sim/app.py` + loaders from `data/raw/`, see `data/raw/SOURCES.md`). Mission: §4 T1.

### T2 — memory package, Jira sync, console · branch `build/t2-memory-jira-console`
**Own:** the BasedAI story and the console the judges watch. **Start now:**
```bash
git checkout build/t2-memory-jira-console
make test          # watch the 3 precedent_memory tests SKIP — those are your spec
```
Open `precedent_memory/schema.sql` (done) and `precedent_memory/tests/` (3 red test files). First task: implement `store.py` / `retrieve.py` / `audit.py` until `test_conjunction` (the multi-source incident-3 case), `test_fail_closed`, and `test_concurrency` pass. *Drive your tool:* "make `precedent_memory/tests/` pass — implement store/retrieve/audit per `02` §2; `retrieve.py` must import no model." Verify: `make test` green; grep `retrieve.py` for LLM imports (none). **Then** the Jira sync (needs live Jira — IDs are in `.env`) and the console. Mission: §4 T2.

### T3 — benches, verification, submissions · branch `build/t3-bench-submissions`
**Own:** the numbers that beat the competitor, and the mechanics of submitting. **Start now:**
```bash
git checkout build/t3-bench-submissions
```
First task (a human GitHub step): fork `github.com/BasedAICo/hackathons`, copy `_TEMPLATE`, open the **skeleton PR** — full steps in [`Plan/workflows/T3-github-publication.md`](Plan/workflows/T3-github-publication.md). In parallel, open `precedent_memory/bench/conformance_bench.py` (stub) and `02` §2.7, and build the conformance bench + **independent oracle** + all **6/6** adversarial attacks (decoupled — zero product-code imports, so you can start before the loop is merged). *Drive your tool:* "implement `conformance_bench.py` to emit `precedent_memory/bench/RESULTS.md` as a measured-vs-threshold-vs-pass/fail table; the oracle is a separate naive-conjunction module with no import from store/retrieve." Mission: §4 T3.

### N1 — data & content lane, deck · branch `content/n1-data-deck`
**Own:** the material that makes the demo real, and the deck. You have repo access — **commit your own work.** **Start now:**
```bash
git checkout content/n1-data-deck
```
First task: write the **critical-five KB articles** into `data/kb/` (see [`data/kb/README.md`](data/kb/README.md) + [`Plan/workflows/N1-kb-articles.md`](Plan/workflows/N1-kb-articles.md) + `Idea/refinement/01-realistic-data-plan.md` §4). These feed the retrieval demo, so they're wanted early. *Drive your tool:* attach `01` §4's table and have it draft each article in the exact YAML front-matter shape; you review the `adapted_from`/ACL/stale flags and commit to `data/kb/`. **Then** the seed data (`data/raw/`, with T1's loaders), the provenance table, and the deck from `03-pitch-deck.md`. Mission: §4 N1.

### N2 — video, submissions, outreach, QA · branch `content/n2-video-submissions`
**Own:** how the work is presented and submitted. You have repo access — **commit your own work.** **Start now:**
```bash
git checkout content/n2-video-submissions
```
First task: **practitioner outreach** — 10 warm-first sends (the one thing only a human closes; it needs time to land). Draft from [`Plan/workflows/N2-practitioner-outreach.md`](Plan/workflows/N2-practitioner-outreach.md); log results (names-free) to `docs/evidence/`. In parallel, stand up the submission scaffolding: the shared video folder convention, the BUIDL page copy, and the one-shot organizer answers (a builder freezes the text before submit). Mission: §4 N2; briefs: `N2-dorahacks-admin.md`, `N2-basedai-pr-readme.md`, `N2-video-edit.md`, `N1N2-demo-playtest.md`.

## 5. The rhythm (gates, not a clock — full detail in the plan §1–2)

Kickoff (G0) → foundations converge at the **first merge** → the **vertical slice** (G1, the immovable floor) → harden + the ambition ladder (§5) → **code freeze + capture** (G2) → selection branch (G3) → Saturday: assemble, PR final (G4), rehearse (G5), submit (G6). Navigate by "after the merge / before the freeze," not by the clock. **When ambition and the clock collide, the demo and Conduct win** — the vertical slice is never sacrificed for a stretch item.

## 6. Commands you'll use

| Command | What |
|---|---|
| `make test` | pytest (your spec skeletons skip until implemented) |
| `make check-open-weight` | rule-1 guard — model names only in `precedent/models.py` |
| `make lint` | ruff |
| `make secrets-scan` | gitleaks full-history (must be clean before the repo goes public) |
| `make freeze-check` | pre-freeze guard: open-weight + tests + secrets + no `‹XX›` placeholders |
| `make sim` / `make demo-reset` / `make bench` | TODO targets you'll wire (T1/T2/T3) |

## 7. Where everything lives

- **What to build & why:** [`Plan/BUILD-PLAN.md`](Plan/BUILD-PLAN.md) (missions, gates, ambition ladder, risks). Detailed briefs: [`Plan/workflows/`](Plan/workflows/).
- **The design (source of truth):** [`Idea/Idea-Development.md`](Idea/Idea-Development.md) (master) → [`Idea/refinement/02-architecture-refinement.md`](Idea/refinement/02-architecture-refinement.md) (deepest technical) + `01`/`03`/`04`/`05`.
- **Every stat's verified source:** [`Research/00-verified-claims.md`](Research/00-verified-claims.md) — nothing goes on a slide or caption without tracing here.
- **What's provisioned right now:** [`CLAUDE-AVAILABLE-APIS.md`](CLAUDE-AVAILABLE-APIS.md) (keys, IDs, tiers, tooling).
- **Prep for the pitch:** [`Prep/`](Prep/) (read tonight) + [`Plan/prep-spec.md`](Plan/prep-spec.md).
- **Evidence index (claim → proof):** [`docs/evidence/README.md`](docs/evidence/README.md).
