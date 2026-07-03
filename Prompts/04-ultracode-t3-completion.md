# Ultracode session prompt — Complete T3 (conformance bench · independent oracle · 6/6 attacks · verification safety-net · submissions plumbing)

> **Target model:** Claude **Opus 4.8**, `ultracode` (multi-agent Workflow orchestration, highest reasoning effort). Paste the whole of the section below **"PROMPT — paste from here"** as the first message of a fresh Claude Code session opened in this repo's root. The leading `ultracode` keyword opts the session into Workflow orchestration; optionally append a token-budget directive (e.g. `ultracode +800k`).
>
> **Before you start (human checklist):**
> - Work happens on branch **`build/t3-bench-submissions`** (already exists; **0 commits ahead of `main`** — its tip is an ancestor of `main` — and several commits behind, and `main` is **actively advancing as the parallel T1 session lands commits**). The session's FIRST job is to create a worktree off that branch and merge the **latest `main`** into it so the bench runs against the real, current product; re-merge `main` as T1 lands more. The session stays on that branch and **does not merge to `main`** itself — merges happen at the plan's phase boundaries.
> - This session runs **SIMULTANEOUSLY with a separate T1 session** on `build/t1-core-loop-sim-agents`. T3 is **code-decoupled by design** — its bench, oracle, and attacks import **zero** product code, so the two build in parallel with no merge collision. The only cross-lane links are **temporal** (T3 runs the bench against merged main before the Friday 21:00 freeze) and **one shared constant** (canonical seed `4207`) plus **two hand-offs** (T3 hands T1 the mutation corpus; T3 pre-registers the agent skeletons T1 later swaps handlers into).
> - `.env` is populated and **never committed**. The session runs **airplane-first**: it builds and measures everything offline against the committed schema + product library; it makes **no** live calls except the ones a human runs. It will **not** fork the repo, push, open the PR, flip repo visibility, create Agentverse accounts, spend ASI:One quota, or run the ≥10-interaction chats — those are **human/account acts** with no token wired by design. The session **prepares** every one of those to a single click/paste and writes the runbook.
> - This prompt was written against verified repo ground truth (the bench stub, the merged T2 store/retrieve/audit/db API and the real `schema.sql` column names, the conftest `scenario` fixture, the Makefile target scopes, the `check_open_weight.sh` scope, the publication workflow, `.env.example`, and `Research/00-verified-claims.md`) and a multi-agent read of every T3-relevant spec section. Treat `CLAUDE-AVAILABLE-APIS.md`, `docs/compliance/`, and the spec files named below as ground truth; read precisely.

---

## PROMPT — paste from here

# MISSION: Complete T3 — Precedent's credibility layer, safety net, and submissions plumbing

You are a fresh Claude **Opus 4.8** "Ultracode" session with multi-agent **Workflow** orchestration at the highest reasoning effort. Your job is to **implement T3 in full** in the repo at `/Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon`: the **conformance bench** that grades the merged product against BasedAI's exact published rubric, the **independent oracle** that makes FNR/FPR credible instead of self-graded, the **6/6 adversarial attack suite + 100% audit-coverage test**, the **seed-4207 mutation corpus** you hand to T1, the **Librarian + Operator echo-skeleton agents** you pre-register so T1 only swaps handlers, and the **submissions plumbing** (everything an agent can prepare so the human's step is one click/paste). **T1 and T2 build the product — you MEASURE it and you never rebuild it. The bench/oracle/attacks import ZERO product decision code.**

This is a hackathon entry whose eligibility depends on four hard rules that are trivial to violate by accident and **eligibility-fatal** to get wrong. **Read this entire prompt before writing a line of code.** You are the **numbers owner** — every stat you emit must be **measured, not fabricated**, and traceable to `Research/00-verified-claims.md` with its caveat. Evidence before assertions: you run every verification yourself before claiming anything is done, and you paste the actual command output.

Work on branch **`build/t3-bench-submissions`** (in its own worktree). Commit as you go; **do not merge to `main`** — that happens at the plan's phase boundaries.

---

## STEP 0 — Load context before designing (mandatory, in this order)

1. **Invoke the `precedent` project skill FIRST** (via the Skill tool). It encodes the four hard rules, the build-plan gate discipline, and the working conventions for this repo. Do this before touching any file under `precedent_memory/bench/`, `tests/`, or `agents/`.
2. Read the authoritative spec/context, in this order:
   - `.claude/skills/precedent/SKILL.md` (rules + conventions)
   - `Idea/refinement/02-architecture-refinement.md` **§2.7** (the bench — this is your primary technical source: the sponsor's exact topology, the 10 metrics with their thresholds, the independent-oracle non-negotiable, the six named attacks, the realism run, the live bench/drift/TTC, the Tier-C stretch) and **§2.8** (the revocation/dual-enforcement moment your drift bench measures)
   - `Plan/BUILD-PLAN.md` **§3 (T3 mission)**, **§1.1** (human action items), **§5** (the ambition ladder — item 1 is your headline: the full green-tick table with the independent oracle + 6/6), **§5.1** (cut order)
   - `Plan/workflows/T3-github-publication.md` (the secrets scrub A–E, the repo-public flip, the BasedAI fork/PR — all HUMAN tasks you PREPARE and check)
   - `Plan/workflows/N2-basedai-pr-readme.md` and `Plan/workflows/N2-dorahacks-admin.md` (the PR README you draft for the human to commit; the DoraHacks BUIDL + the one-shot organizer answers)
   - `Research/00-verified-claims.md` (EVERY number you print carries its caveat from here — the vendor labels, the calendar-vs-business-hours split, the naive-frequency floor, the inverted stat, the refuted claims to never use)
   - `docs/compliance/venice-models-2026-07-03.json` and the two sibling dumps (the open-weight eligibility evidence the PR cites; the pinned model ids live here and in `precedent/models.py` — never retype them)
   - `Prompts/03-ultracode-t1-completion.md` (**the T1 completion prompt — read it in full for the interlock contract**: the canonical class-key registry, the seed-4207 decision, what T1 explicitly defers to you, and the agent-seed-stability requirement)
   - The product library you MEASURE (read thoroughly — you call it from the bench, and the oracle **independently reimplements its decision** from the raw tables): `precedent_memory/store.py` (`ensure_constraint`, `put_principal`, `put_source`, `store`/`store_memory_write`, `compile_effective_policy`), `precedent_memory/retrieve.py` (`Principal`, `RecordPolicy`, `permitted()`, `stale()`, `_build_policy()`, `check_access()`, `retrieve()`), `precedent_memory/db.py` (`connect`, `ids_to_bits`/`bits_to_ids`, `is_superset`, `blob_to_bits`, `parse_iso`, `FRESHNESS_WINDOW_SECONDS`, `UNVERIFIED_SOURCE_SYSTEM`/`_REF`), `precedent_memory/audit.py` (`audit()`, `verify_chain(expected_len=…)`), `precedent_memory/sync.py`, and **`precedent_memory/schema.sql`** (the canonical tables + column names your oracle reads: `acl_source(constraint_ids JSON, last_verified_at, revoked)`, `constraint_def`, `memory_record(status IN active/quarantined/tombstoned)`, `lineage(record_id, source_id)`, `effective_policy(required_bits, is_restricted, min_source_freshness)`, `principal(grant_bits)`, `audit_log`, `class_ladder`)
   - `precedent_memory/tests/conftest.py` (the canonical `scenario` fixture your topology generator scales up: constraints RIGHTS/SCHED; principals `rights_only`/`sched_only`/`both`/`nobody`; sources `kb:KB-0001` public, `kb:KB-0004` RIGHTS, `jira:MEDIA-113` SCHED — your oracle MUST reproduce these hand-checkable labels exactly)
   - `precedent_memory/bench/conformance_bench.py` (the 25-line `NotImplementedError` stub you implement) and `precedent_memory/bench/__init__.py` (the docstring stating the decoupling contract)
   - `Makefile` (note: `bench:` is a TODO stub that `exit 1`s — you wire it; `check-open-weight`, `test`, `secrets-scan`, `freeze-check` are LIVE — read exactly what they scan; see the traps below), `scripts/check_open_weight.sh`, `.env.example`, `CLAUDE-AVAILABLE-APIS.md`
3. **Do NOT relitigate settled design.** The contracts, the schema, the model registry, and the merged T2 API are **FROZEN**. The bench calls the product API and reads the schema tables **as they are** — you do not add columns, rename tokens, or "improve" the product to make a metric pass. If a metric legitimately fails, you **report the honest measured value and mark it FAIL** — you never fabricate a pass or edit the product to hide a disagreement.

---

## THE FOUR HARD RULES (non-negotiable invariants — each is eligibility-fatal, and each bites T3 in a specific way)

These bind every line you write, including the bench, the oracle, the tests, the mutation corpus, the agent skeletons, the PR README draft, and any committed scratch.

**Rule 1 — Open-weight only.** A literal closed-model id may appear in **`precedent/models.py` and nowhere else** — not in `bench/`, not in `oracle.py`, not in `tests/`, not in the mutation corpus, not in a comment or docstring, not in the PR README draft, not in `.env.example`. `make check-open-weight` greps `precedent precedent_memory sim console agents` for `claude-|openai-|gpt-|gemini-|grok-|mercury-`. **TRAP (verified): the guard does NOT scan `tests/`** — so a model id you leave in `tests/test_adversarial.py` will pass `make check-open-weight` but is still a violation a judge can grep for. Your red-team pass must grep `tests/` and the mutation corpus too. **The bench and oracle have no reason to name any model at all** — they are pure deterministic Python over the ACL tables; if you find yourself typing a model id, you have taken a wrong turn. For the **PR README's open-weight declaration**: paste the four pinned ids **byte-for-byte from `docs/compliance/venice-models-2026-07-03.json` / `precedent/models.py`** (Qwen / DeepSeek / BGE-M3 with their Apache-2.0/MIT licences and `huggingface.co` `modelSource` URLs) — **never retype them from memory**, and **delete the `_TEMPLATE`'s ANTHROPIC/OPENAI example keys** from `Precedent/.env.example` so the open-weight declaration does not sit next to closed-vendor keys. No closed model is named anywhere as in-loop.

**Rule 2 — No LLM in the decision, AND the oracle is INDEPENDENT (this is the T3 rule).** Two distinct obligations:
- **No LLM in any label or decision.** The bench, the oracle, and every ground-truth label are pure deterministic Python. There is **no model import anywhere in the authorization/label path**. An LLM never sets an allow/deny, a risk class, or a metric.
- **The oracle must NOT import `store` or `retrieve` and must NOT use the bitmap.** The entire reason FNR/FPR are credible (and not the exam grading itself) is that the expected labels come from a **separate, naive reimplementation** of the ACL decision. `precedent_memory/bench/oracle.py` (~40 lines) reads the raw tables (`lineage`→`acl_source.constraint_ids`, `acl_source.revoked`, `acl_source.last_verified_at`, `memory_record.status`, `principal` constraint sets) and decides allow/deny by a **plain-Python-set lineage-conjunction walk**: union the constraint-ids across ALL of a record's lineage sources, allow iff the principal's constraint-id **set is a superset** of that union **AND** the fail-closed conditions hold — revoked source → deny, unverified/unknown-provenance source → deny, `status != 'active'` (quarantined/tombstoned) → deny, stale/unknown freshness (older than `db.FRESHNESS_WINDOW_SECONDS`, or `""`/None) → deny, fallback mode (Jira unreachable) → every restricted record denied. It imports **only** stdlib + `db` connection/parse primitives (`db.parse_iso`, `db.FRESHNESS_WINDOW_SECONDS`, `db.UNVERIFIED_SOURCE_SYSTEM/_REF`) — **NO `from precedent_memory import store` / `import retrieve`, NO `is_superset` bitmap call, NO `blob_to_bits` on `effective_policy`.** It reproduces the semantics of `retrieve.permitted()` **by hand over sets**, so that FNR = (oracle says DENY, compiler says ALLOW) and FPR = (oracle says ALLOW, compiler says DENY) are a genuine cross-check of two independent implementations. **A CI grep/test asserts the no-import, no-bitmap rule** and fails the build if violated. If the oracle ever imports the thing it grades, FNR=0 is circular and a round-2 judge rejects it — treat that as a build-breaking regression.

**Rule 3 — Fail-closed is exactly what the attacks probe.** The oracle AND the compiler must **agree on DENY** for: revoked sources, unverified/unknown provenance, quarantined/tombstoned records, stale freshness (>60 s in live mode), and fallback mode (Jira unreachable → every restricted record denied). Your bench must **exercise these paths and count any disagreement as a real FNR/FPR — never suppress or special-case a fail-closed disagreement to make a number look good.** The six attacks each assert a fail-closed invariant holds under adversarial input (deny + no restricted-content leak + an audit event, or a bounded timing delta, or no-leak-under-union). Denials disclose only `denied_count` + `denied_owner_team` — never a title, symptom, body, or secret; every attack asserts that boundary too. `jira-smoke` and the live bench **exit non-zero when unconfigured** — never fake a live result.

**Rule 4 — No secrets (you own the scrub that gates the repo going public).** The repo does **not** go public until the full A–E scrub is clean (any single pass is insufficient). Agent seeds, mailbox keys, tokens, real teammate names, and Jira accountIds never appear in code, a commit, a screenshot, the PR, the BUIDL, or any prompt you send to a sub-agent. Agent skeleton seeds are read from **env** at runtime, never inlined. You **prepare and check** the scrub (interpret redacted/pattern-grep output — "variable name or real value?") but the **human runs the scans and makes the leak call**; a real leak means **rotate the key on the vendor dashboard FIRST**, then `git-filter-repo` only with T1's OK. Re-run gitleaks on the **fork** before the human's final push.

If any task appears to require breaking one of these, **STOP and find the compliant path** — there always is one.

---

## RESOLVED DECISIONS (proceed autonomously on these — do not ask, do not relitigate)

- **Canonical seed `4207`.** Declare the fixed integer `4207` **once** as a shared constant (e.g. `precedent_memory/bench/seed.py::CANONICAL_SEED = 4207`, with a one-line comment "shared with T1's incident generator — override together at G0"). The topology, the 10,000 queries, and the 100-mutation corpus all derive from it and must replay **byte-identically** across two runs. `grep` confirmed no `4207` exists in code yet — you create it. If the team overrides it at G0, both T1 and T3 change that one constant together.
- **Go for the FULL green-tick table — NOT the 4/6 fallback.** Measure **all ten** published metrics (FNR / FPR / P50 / P99 / end-to-end overhead / derived-memory correctness / ACL drift / time-to-consistency / audit coverage / O(1)–O(log n) curve) vs threshold vs pass/fail, land **6/6** adversarial attacks, and land the Tier-C stretch (derived-memory-correctness bench + the 1k/5k/25k/100k latency-vs-size curve). 4/6 is the honest degrade ONLY if an attack proves genuinely unenforceable — in which case it becomes a **declared NON-CLAIM in the attacks row, never a faked pass**.
- **Airplane-first + one live proof.** Build and measure the entire **synthetic** bench, the 6/6 attacks, and the audit-coverage test **offline** against the committed schema + product library — this is the number that ships in the PR Friday night. **Build** the live-bench command and the live-drift/TTC N-flip command (both exit non-zero when unconfigured), but the **actual live Jira run is a human step captured once** on Saturday (creds are in the human's local `.env`, never committed). You do not run it.
- **The UCI realism run is framed "25k-record store", NEVER "P99 over 141k events".** The number is **24,918 incidents**, not the 141,712 raw event count. Every caption, the RESULTS.md row, and the PR text say "25k-record store".
- **Every number carries its caveat label from `Research/00-verified-claims.md`.** `18.2h` is always "calendar hours" (never blended with MetricNet's 8.85 business-hour figure); `94.4%` is precedent-EXISTENCE (98.6% is the symptom-class arrival-knowable one); `59.4%`/`87.7%` arrival-time top-1/top-3 is a **naive-frequency FLOOR**, not product accuracy; the `knowledge=true 74.6h vs 8.6h` stat is **inverted/confounded** — never causal; NeuBird rows are "a 2026 industry survey (NeuBird)"; Google toil is "stated goal"; prefer "$200M/year per Global 2000 co" over the $400B aggregate; never use the four refuted Komodor/Klaudia claims.
- **The oracle is built by a DIFFERENT sub-agent lineage** than anything that reads `store`/`retrieve`, to keep it genuinely independent (see the orchestration section).

---

## THE T1 ↔ T3 INTERLOCK CONTRACT (implement to this exactly — both tracks build simultaneously)

T3 is decoupled in code and coupled only at three seams. Get these right or the two sessions collide or drift.

1. **Zero product-decision imports → own worktree, parallel build.** The bench *calls* the product write API (`store.*`) to build the topology and *calls* `retrieve.permitted()`/`check_access()` as the **compiler-under-test**; but the **oracle imports neither `store` nor `retrieve`**, and the **attacks/oracle produce the ground truth**, so FNR/FPR are not self-graded. Because nothing you author is a product dependency, you run in a **separate worktree on `build/t3-bench-submissions`** with no merge collision against T1's `build/t1-core-loop-sim-agents`.
2. **Seed `4207` is the one shared constant.** T3 **produces** the 100-mutation extractor corpus off `4207` and **hands it to T1** for the ~18:30 extractor bench (its single robustness number feeds the on-screen chip / slide 10 / README / BUIDL). Both tracks must replay byte-identically; if `4207` is overridden at G0 both change together. Write the corpus to a stable path (e.g. `precedent_memory/bench/mutation_corpus.jsonl` or `data/bench/`) with a loader T1 can import, and record the exact path + format in your hand-off note.
3. **T3 owns the Agentverse pre-registration the T1 prompt defers.** The T1 completion prompt explicitly defers to human/T3: Agentverse registration, the ≥10-interaction discoverability run, and the insurance shared-chat URL. **You add the Librarian + Operator echo-skeleton agents** to `agents/` (Watcher's echo is T1's job) as `uagents` agents with `mailbox=True`, **stable seeds read from env** (`LIBRARIAN_AGENT_SEED`, `OPERATOR_AGENT_SEED` from `.env.example`), `publish_manifest=True`, `chat_proto` included, both README badges (`![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)` + `![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)`), and keyword-rich descriptions. **The seeds must be the exact env seeds T1's real handlers later reuse** — if the seed changes on handler swap, the Agentverse address changes and the ≥10-interaction discoverability clock resets. You build them **registerable**; the human registers them.
4. **Temporal seam: run the bench against MERGED MAIN before the G2 / Friday-21:00 freeze.** Your synthetic bench + 6/6 attacks + audit-coverage test run against `main` (carrying merged T1+T2), the numbers are frozen, and they **commit into the BasedAI PR Friday night** — the PR is never numbers-free under the strict deadline reading. Saturday's live run only *adds* the realism/drift numbers.
5. **Downstream consumers of your outputs:** N2's PR README table cells (`[[WAIT:BENCH-SYNTH]]` / `[[WAIT:BENCH-CURVE]]` / `[[WAIT:ATTACKS]]`), N2's DoraHacks draft (gated on the public-repo URL you unblock), N1's deck slide 10, and N2's video shot-7/8 captions (P99 + repo URL) all wait on your RESULTS.md + the public URL. Announce each as it lands.

---

## THE TEN METRICS AND THEIR THRESHOLDS (from 02 §2.7 — the RESULTS.md table)

RESULTS.md is a table with columns **exactly** `Metric | Measured | Threshold | Pass/Fail`, one row per metric, plus an attacks row. Thresholds (BasedAI's published rubric):

| Metric | Threshold | How T3 measures it |
|---|---|---|
| **FNR** (false-negative rate = leak: oracle DENY but compiler ALLOW) | **< 0.1%** | disagreement over the ≥3,000 deny-expected queries; **the row states deny-expected N and leak count**, never a bare % |
| **FPR** (false-positive rate = oracle ALLOW but compiler DENY) | **< 2%** | disagreement over allow-expected queries |
| **P50** latency | **< 50 ms** | measured on the `permitted()`/bitmap check (NOT full `retrieve()`, which does owner-team + audit work on the deny path) |
| **P99** latency | **< 200 ms** | same sample set, 99th percentile |
| **end-to-end overhead** | **< 100 ms** | the added cost of the permission check on the hot path |
| **derived-memory correctness** | **> 99%** | Tier-C: ~1k lineage-derived artifacts graded vs the oracle |
| **ACL drift** | **< 0.5%** | stale-allow fraction during a revoke window (synthetic now; live Saturday) |
| **time-to-consistency (TTC)** | **< 5 min** | flip→recompiled-deny wall-clock (synthetic now; live Saturday, anchored to Jira's `/rest/api/3/auditing/record`) |
| **audit coverage** | **100%** | `tests/test_audit_coverage.py` — every allow/deny/sync/execution path writes a row + `verify_chain` passes |
| **O(1)/O(log n) permission-check curve** | flat/log | Tier-C: latency-vs-size at 1k / 5k / 25k / 100k records |
| **attacks** | **6/6** | "N of 6" + any declared non-claims |

**Number-honesty traps (you are the numbers owner):**
- **FNR < 0.1% is claimable ONLY with ≥3,000 deny-expected queries at ZERO leaks** (rule of three). The FNR row states the **deny-expected N and the leak count** explicitly. If leaks > 0, report the **honest measured FNR and mark FAIL** — never a bare %.
- **Oracle independence** — if the oracle imports `store`/`retrieve` or reuses the bitmap, FNR=0 is circular. Guard it with a test.
- **Degraded rule:** if a bench slips, **REMOVE the unmeasured row** — never bracket (`‹XX›`), never "coming soon". A row without a real Pass/Fail is worse than an absent row. Unmeasured-until-Saturday metrics (live drift/TTC/UCI) say `"not yet measured — realism run lands Saturday"` in the Measured cell (that is a stated status, not a placeholder token).

---

## DEPENDENCY-ORDERED WORK PLAN (build order is strict; each step names its verification)

Build toward the **G2 freeze deliverable** first: a green synthetic RESULTS.md (all measurable-offline metrics) + 6/6 attacks + audit-coverage passing against merged main, plus the mutation corpus handed to T1 and the agent skeletons pre-registerable. Everything past that (UCI realism, live drift/TTC, the live-bench command wiring) is strictly additive and the live half is human-run.

### Phase 0 — Worktree, seed, scaffold, and everything the human needs to click at G0 (T3-0, T3-1, submissions-prep)
- **T3-0 Worktree off merged main.** `git worktree add` a working dir off `build/t3-bench-submissions`; merge the **latest `main`** (carrying merged T2, and merged T1 as it lands — the T1 session is already committing) into it so the bench runs against the real, current product; re-merge `main` periodically as T1 lands more. The bench imports zero product-decision code so **no collisions are expected**; resolve any trivially.
  *Verify:* `git status` shows a clean worktree whose `git log` contains main's tip; `make test` is green on the branch before you add anything.
- **T3-1 Ratify seed 4207 as one shared constant.** Create the single authoritative `CANONICAL_SEED = 4207` and reference it from the topology generator, the query generator, the mutation corpus, and the README. `grep` the tree to prove exactly one authoritative definition.
  *Verify:* `grep -rn "4207"` shows one definition + references; a replay test proves two runs are byte-identical.
- **Submissions PREP (agent prepares; human executes — see the HUMAN STEPS section).** Draft the BasedAI PR README (from `N2-basedai-pr-readme.md` + `02 §2.7`) with the 8 verbatim template headings, the open-weight declaration (ids pasted byte-for-byte from `docs/compliance/`), the six attack names verbatim, `docs/compliance/` cites, and `[[WAIT:BENCH-SYNTH]]`/`[[WAIT:ATTACKS]]`/`[[WAIT:BENCH-CURVE]]`/`[[WAIT:VIDEO-LINK]]`/`[[WAIT:MENTOR-ANSWER]]` sentinels for the human to replace. Draft the Venice-only `Precedent/.env.example` (template's ANTHROPIC/OPENAI keys **deleted**). Draft the DoraHacks one-shot organizer-answer worksheet and the `docs/evidence/` scrub-evidence line. Write the scrub A–E commands and the repo-public pre-flight into a checklist the human runs.
  *Verify:* the drafts exist under a clearly-marked prep path (e.g. `docs/evidence/` or `Prep/`), contain **no secrets and no closed-model ids**, and every human action is a copy/paste or one-click with the exact command/file named.

### Phase 1 — The independent oracle (T3-4, built FIRST and by an isolated sub-agent lineage)
Build the oracle **before** the topology/queries so the ground truth is defined independently of how you generate data.
- **T3-4 `precedent_memory/bench/oracle.py` (~40 lines).** Naive lineage-conjunction over the raw tables using **plain Python sets**. For a `(principal, record)` pair: gather the record's lineage `source_id`s → for each, load `acl_source.constraint_ids` (JSON), `.revoked`, `.last_verified_at`; **union** the constraint-id sets; DENY if any source revoked, any source unverified/unknown-provenance, `memory_record.status != 'active'`, or freshness stale/unknown (parse `last_verified_at`, compare to `db.FRESHNESS_WINDOW_SECONDS`; `""`/None → stale) or `mode != 'live'` (fallback → deny all restricted); else ALLOW iff the principal's constraint-id **set ⊇ the union**. Public record (empty union) → ALLOW. **Imports ONLY stdlib + `db` parse/const primitives — never `store`, never `retrieve`, never `is_superset`/`blob_to_bits` on the compiled bitmap.**
  *Verify:* a CI grep/test asserts `oracle.py` contains no `import ...store` / `import ...retrieve` and no bitmap call; the oracle's labels on the **conftest `scenario`** cases match by hand — `rights_only`/`sched_only`/`both`/`nobody` × `kb:KB-0001`(public)/`kb:KB-0004`(RIGHTS)/`jira:MEDIA-113`(SCHED) — e.g. `both`→all allow, `nobody`→only public, `rights_only`→public+KB-0004, `sched_only`→public+MEDIA-113; and revoked/quarantined/stale variants all DENY.

### Phase 2 — Topology + ground-truth corpus (T3-2, T3-3)
- **T3-2 Deterministic topology generator** (in `conformance_bench.py` or `bench/seed_corpus.py`), seeded by `CANONICAL_SEED`: **5 hierarchy levels / 20 roles / 1,000 ACL-tagged docs / 40 principals**, scaling the conftest `scenario` semantics. Map roles→`constraint_def` bits via `store.ensure_constraint`; principals→`store.put_principal(constraint_ids)`; docs→`store.put_source(acl_source, constraint_ids)` + `store.store_memory_write(...)` with lineage so `compile_effective_policy` populates `required_bits` for every restricted doc. Include revoked / unverified / quarantined / stale sources so the fail-closed paths are represented.
  *Verify:* two runs at seed `4207` yield identical row counts/content; the DB has exactly **20 roles, 1,000 docs, 40 principals**; `effective_policy.required_bits` is populated for every restricted doc.
- **T3-3 10,000 ground-truth queries, ≥3,000 deny-expected.** Deterministic `(principal, doc/query)` pairs spanning allow and deny, **including the fail-closed cases** (revoked / unverified / quarantined / stale). At least **3,000 must be deny-expected** (oracle-labelled) so FNR < 0.1% is statistically claimable.
  *Verify:* a test asserts `len(queries) == 10000` and `deny_expected_count >= 3000`; the distribution is written to the raw JSON.

### Phase 3 — Grade, emit, wire (T3-5, T3-6, T3-7)
- **T3-5 Grade compiler vs oracle + measure latency.** Drive the **compiler-under-test** (`store.compile_effective_policy` + `retrieve.permitted()`/`check_access()`) over the 10k queries; FNR/FPR = bitmap-vs-oracle disagreement (any fail-closed disagreement is a **real** FNR/FPR, never suppressed). Sample latency on the **`permitted()`/bitmap check** (not full `retrieve()`) for P50/P99/end-to-end overhead. Compute synthetic ACL-drift and TTC (real values land Saturday).
  *Verify:* FNR/FPR/P50/P99/overhead computed from actual samples; disagreements are counted, not hidden; the numbers are reproducible from the committed raw JSON.
- **T3-6 Emit `precedent_memory/bench/RESULTS.md` + raw JSON.** The `Metric | Measured | Threshold | Pass/Fail` table for all ten metrics + the attacks row (N of 6 + declared non-claims). **The FNR row states deny-expected N + leak count.** Commit the raw per-query/timing/disagreement JSON alongside. **No `‹XX›`/`[[WAIT]]` in RESULTS.md**; unmeasured-until-Saturday metrics say `"not yet measured — realism run lands Saturday"`. The table must be convertible to N2's results-block keys.
  *Verify:* a `grep '‹' RESULTS.md` finds nothing; every metric row has a Pass/Fail; the FNR row shows deny-N + leak count; re-parsing the raw JSON reproduces the table.
- **T3-7 Wire `make bench`.** Replace the TODO stub so `make bench` runs `python -m precedent_memory.bench.conformance_bench` and regenerates RESULTS.md **in seconds** (the Q&A live-bench weapon), reproducibly.
  *Verify:* `make bench` exits 0 and (re)writes RESULTS.md; a second run reproduces identical synthetic numbers.

### Phase 4 — The 6/6 attacks + audit coverage (T3-8, T3-9)
- **T3-8 `tests/test_adversarial.py` — six pytests, verbatim names.** One test each, each asserting a security invariant:
  1. **query inference** — a principal cannot infer restricted content by probing; deny + no content leak + audit event.
  2. **metadata bypass** — a tenant full-deny toggle (revoke/quarantine) denies even a previously-permitted principal; only `denied_count`+`owner_team` may surface.
  3. **timing attack** — the allow-vs-deny latency-distribution **delta on the bitmap check** is bounded (assert the delta is within a stated tolerance, so timing doesn't leak membership).
  4. **collection attack** — the **union of many low-privilege queries never reconstructs a restricted record**; only count+owner_team may ever leak.
  5. **prompt injection** — a mutated ticket instructing the Librarian to quote restricted memory → assert **deny + audit event** (no restricted body in the reply).
  6. **derived-memory attack** — revoke a lineage source → **all records derived from it are denied** (lineage conjunction); assert the fan-out denies.
  Target **6/6**; any genuinely unenforceable one is a **declared NON-CLAIM in RESULTS.md, never a faked pass**.
  *Verify:* `pytest tests/test_adversarial.py` passes for each enforced attack; each asserts deny + no restricted content leak + an audit row (or a bounded timing delta); grep confirms **no model id in the test file** (the open-weight guard doesn't scan `tests/` — you must).
- **T3-9 `tests/test_audit_coverage.py`.** Assert **every** retrieval/denial/sync/execution path appends an `audit_log` row and `audit.verify_chain(expected_len=…)` passes (catches tail truncation → 100% is 100%). Make it a **real** coverage check: deliberately dropping an audit call in a fixture must make the test FAIL.
  *Verify:* `pytest` passes; a fixture that drops an audit call flips the test to red (proving it checks coverage, not just chain validity).

### Phase 5 — Mutation corpus hand-off + agent skeletons (T3-10, T3-11)
- **T3-10 Seed-4207 extractor mutation corpus → hand to T1.** A deterministic **100-mutation** corpus (typos, colloquial symptoms, dropped codes, red-herrings) off `CANONICAL_SEED`, byte-identical to T1's fixtures, at a stable path with a loader. Write the hand-off note (path, format, how to load, the single robustness number's four destinations).
  *Verify:* the corpus replays byte-identically twice; the hand-off note names the exact path/format so T1's extractor bench can load it.
- **T3-11 Librarian + Operator echo-skeleton agents in `agents/`.** Instantiate both as echo skeletons, `mailbox=True`, **stable seeds from env** (`LIBRARIAN_AGENT_SEED`/`OPERATOR_AGENT_SEED`), `publish_manifest=True`, `chat_proto` included, both README badge markdown snippets present in each agent's README section, keyword-rich descriptions. Structure them so T1 swaps in real handlers **without the seed/address changing**.
  *Verify:* the agents instantiate and include `chat_proto`; `make check-open-weight` green over `agents/`; seeds read from env (grep proves none inlined); both badge snippets present in each README section; a registration-runbook note lists which env vars the human fills.

### Phase 6 — Tier-C stretch (T3-12, at capacity — upgrades the table)
- **T3-12 Derived-memory-correctness bench + latency-vs-size curve.** ~1k lineage-derived artifacts graded vs the oracle (>99% row); O(1)/O(log n) latency-vs-size curve at **1k / 5k / 25k / 100k** records (a tabulated/plotted row). Add both rows to RESULTS.md **with real numbers or omit them honestly (never bracket)**.
  *Verify:* curve points measured; derived-correctness % computed vs oracle; both rows carry real numbers or are absent.

### Phase 7 — Freeze run + additive live prep (T3-13, T3-14)
- **T3-13 Run the full synthetic bench + 6/6 attacks + audit coverage against merged main before Fri 21:00.** Freeze the numbers; they commit into the PR Friday night (the human's commit).
  *Verify:* RESULTS.md + raw JSON committed; `make check-open-weight`, `make test`, `make secrets-scan` clean; `grep '‹' RESULTS.md` empty; the numbers are ready for the human to paste into the PR before 21:00.
- **T3-14 Saturday additive (BUILD the commands; the live run is human-captured once).** Build the **live-bench** CLI (re-runs the bench + regenerates RESULTS.md in seconds) and the **live drift/TTC N-flip** command against real Jira (role membership 10007/10008 + issue-security 10000/10001), reading each flip timestamp from `/rest/api/3/auditing/record` (ms precision, source-system-anchored, **not** the client clock); TTC vs < 5 min, stale-allow fraction vs drift < 0.5%. Point the same harness at the **UCI ~25k-record store** ("25k-record store" caption, never "141k events"). Both live commands **exit non-zero when unconfigured**; the human runs them Saturday with local `.env` creds and pastes the values as a PR comment.
  *Verify:* the commands exist and exit non-zero unconfigured; the UCI P99 row is added with the "25k-record store" caption; the drift/TTC rows carry the Jira-audit-anchored framing; the human-run instructions are written.

---

## MULTI-AGENT EXECUTION STRATEGY (use the Workflow tool — maxed out)

Leverage orchestration; do not build this serially where parallelism is safe.

- **Respect the dependency DAG:** Phase 0 → oracle (Phase 1) → topology/queries (Phase 2) → grade/emit/wire (Phase 3). Attacks (Phase 4) and audit-coverage depend only on merged main (parallelisable with Phases 1–3). Mutation corpus + agent skeletons (Phase 5) depend only on the seed + worktree (start early, in parallel). Tier-C (Phase 6) depends on the emitter.
- **The oracle is built by a DIFFERENT sub-agent lineage than anything touching `store`/`retrieve`.** Spin the oracle implementer in its own worktree with an instruction that it may read only `schema.sql` + `db.py` primitives and the conftest `scenario` — it must **never** read `retrieve.py`'s `permitted()` implementation. This keeps the reimplementation genuinely independent (two people can't accidentally converge on the same bug). The bench-harness sub-agent (which calls `store`/`retrieve`) is a separate lineage; they meet only at the grading step, which compares their outputs.
- **TDD per module** (`superpowers:test-driven-development`): write the failing test that encodes each verification criterion above, then implement to green. The oracle's "test" is the hand-checked conftest `scenario` labels; the audit-coverage test's own meta-test is the dropped-audit-call fixture flipping it red.
- **One attack per sub-agent, each with an adversarial verifier.** Fan out the six attacks to six implementer sub-agents; pair each with a **verifier sub-agent that independently confirms the attack is REAL** (the exploit would actually leak restricted content if the defence were removed) **and that the defence holds** (deny + no leak + audit event, or bounded timing delta). An attack that passes trivially (because it never exercised the restricted path) is a **fake pass** — the verifier must reject it.
- **Serialise the integration chokepoints:** the RESULTS.md emitter and `make bench` wiring are owned by one integrator sub-agent; implementers hand it green modules and the integrator re-runs every verification.
- **A dedicated RED-TEAM pass** (`superpowers:requesting-code-review` + `superpowers:verification-before-completion`) that independently checks:
  1. **Oracle independence** — grep `oracle.py` for `store`/`retrieve` imports and any bitmap call; fail the build on a hit. Confirm FNR/FPR are a two-implementation cross-check, not self-grading.
  2. **Number honesty** — every stat in RESULTS.md and the PR draft traces to `Research/00-verified-claims.md` with its caveat; the FNR row states deny-N + leak count (no bare %); "25k-record store" never "141k events"; the calendar/business-hour, existence-vs-symptom, naive-floor, and inverted-stat labels are correct; no refuted claim appears.
  3. **Open-weight airtightness** — grep the WHOLE tree **including `tests/` and the mutation corpus** (which `make check-open-weight` does NOT scan) for `claude-|openai-|gpt-|gemini-|grok-|mercury-`; confirm the PR README's four ids are byte-identical to `docs/compliance/` and that the template's ANTHROPIC/OPENAI keys are deleted from `Precedent/.env.example`.
  4. **Secrets-clean** — no seed/key/token/accountId/real-name in any committed file, the PR draft, the BUIDL draft, or any evidence artifact; agent seeds read from env.
  5. **Fail-closed disagreements are counted, not suppressed** — the bench does not special-case revoked/unverified/quarantined/stale to make a metric pass.
  6. **Reproducibility** — two `make bench` runs at seed `4207` produce byte-identical synthetic numbers; the mutation corpus replays byte-identically.
- **Never claim done without running the command.** Paste the actual output as evidence. If a sub-agent reports green, the integrator re-runs it.

**The quality bar:** `make bench` emits a complete measured-vs-threshold-vs-pass/fail RESULTS.md; `make check-open-weight`, `make secrets-scan`, and `make freeze-check` are clean; the six attacks pass (or an unenforceable one is a declared non-claim); the audit-coverage test is a real coverage check; the oracle is provably independent; the PR README draft is template-verbatim with the full green-tick table ready for the human to commit.

---

## HUMAN STEPS (hand these to your teammate — the agent PREPARES everything; the human just executes)

No GitHub token or Agentverse/ASI:One session is wired by design. The agent prepares each of these to a **single click/paste** and writes the exact command/file; the human performs the account-level act. Delineated by gate:

**G0 (kickoff):**
- **Ratify seed 4207** at stand-up as the shared constant binding T3's corpus to T1's generator (or override — both change together). *(Agent has written it once; human confirms the value.)*
- **Create the T3 worktree** off `build/t3-bench-submissions` and merge merged-main in. *(Agent supplies the exact `git worktree add` + merge commands.)*
- **Open the BasedAI skeleton PR** from your GitHub account: fork `github.com/BasedAICo/hackathons` → clone to `~/basedai-hackathons` → `checkout -b precedent-submission` → check merged/open PRs (e.g. PR #3 "BioVault") for the exact submissions-folder path → `cp -r UK-AI-Agent-EP5/submissions/_TEMPLATE .../submissions/<team-name>/` → paste the **agent-drafted README** (8 verbatim headings, open-weight declaration, six attack names, `docs/compliance` cites, placeholder video link) → paste the **agent-drafted Venice-only `.env.example`** (ANTHROPIC/OPENAI keys deleted) → commit → push → open PR titled **"Precedent — permission-aware agent memory (UK AI Agent Hackathon EP5)"** touching ONLY your team folder.
- **Ask a BasedAI mentor which deadline governs** (event README "3 Jul EOD" vs track doc "4 Jul before judging"); record the answer in the PR, replacing `[[WAIT:MENTOR-ANSWER]]`.
- **Register the three Fetch agents on Agentverse** (Watcher/Librarian/Operator) as MAILBOX agents using the **stable env seeds the agent wrote** (so the address survives T1's handler swap); confirm both badges render; capture the 3 profile URLs; fill the empty `.env` IDs.
- **Run ≥10 discoverability chats + capture the insurance ASI:One shared-chat URL** early (final anchored one at G4); fill `ASI_ONE_SHARED_CHAT_URL`.
- *(optional)* **Invite the 2nd Jira seat**, add to role 10007, fill `JIRA_RIGHTS_OPS_ACCOUNT_ID`/`JIRA_SCHEDULING_OPS_ACCOUNT_ID` locally (never committed) — or use the single-account role-flip fallback.

**G1–G2 (Friday build → 21:00 freeze):**
- **Hand the seed-4207 mutation corpus to T1** (~18:30, after the vertical-slice gate); record the single robustness number for the on-screen chip / slide 10 / README / BUIDL. *(Agent produced the byte-identical corpus + the hand-off note.)*
- **Run the five-pass secrets scrub A–E** on the main repo (gitleaks `--all --redact` / `.env`-never-committed / pattern grep / literal-value scan / worktree sweep — exact commands in `Plan/workflows/T3-github-publication.md §3`, which the agent has pre-filled into the checklist). Eyeball each surviving hit; make the leak call yourself. A real leak → **rotate the key FIRST**, then `git-filter-repo` only with T1's OK.
- **Write the scrub-evidence line** into `docs/evidence/README.md` and **flip the main repo PUBLIC** (Settings → Danger Zone → Change visibility), after the pre-flight (scrub clean; run instructions present; badges on each agent README; LICENSE + data-attribution lines). Verify logged-out in an incognito window. Post the public URL + PR URL + `precedent_memory/bench/RESULTS.md` path in the team thread. *(This unblocks N2's DoraHacks draft and N1's deck.)*
- **Commit the measured bench numbers into the PR before Fri 21:00** — paste the agent's measured 10-metric table + mutation line + 6/6 attack results, replacing `[[WAIT:BENCH-SYNTH]]`/`[[WAIT:ATTACKS]]`/`[[WAIT:BENCH-CURVE]]`; state oracle-independence explicitly; verify "Files changed" lists ONLY your team folder.
- **Freeze the DoraHacks one-shot organizer answers with T1 sign-off** (open the BUIDL form for event **2272** WITHOUT submitting; copy every question verbatim into `docs/evidence/`; the agent drafted answers; get T1 sign-off on EVERY answer; resolve every `[NEEDS-FACT]`).

**G3 (after repo public):**
- **Submit the DoraHacks BUIDL draft** (event 2272): enter the signed answers character-for-character; tick **exactly three** bounties **1370 / 1367 / 1364** (deselect extras); incognito link-check + no-`‹`/no-XX Ctrl-F; submit; screenshot; post to thread.

**G4–G6 (Saturday):**
- **Run the UCI 25k realism run + live drift/TTC in front of judges** (caption "25k-record store", never "141k events"); the live Jira flips read timestamps from `/rest/api/3/auditing/record`. Requires live Jira creds in your local `.env`. Paste values as a PR comment. *(Agent built the commands; they exit non-zero unconfigured.)*
- **Push the PR final:** paste the video URL (from N2's unlisted upload) replacing `[[WAIT:VIDEO-LINK]]`; add any late realism number; **re-run gitleaks on the FORK** before the final push; rebase onto `upstream/main` if it moved; verify only-your-folder; comment "Final for judging — video + measured benchmarks included."
- **Final DoraHacks submit before 23:59 BST / 22:59 UTC** (never the last hour); screenshot; commit the final page text + locked one-shot answers to `docs/evidence/dorahacks-buidl.md`.
- **Watch for the Demo-Day presenter announcement** (Discord/email); if not selected, place the 90-second cut first on the BUIDL page.

---

## ACCEPTANCE CHECKLIST (run these yourself; paste evidence)

- [ ] Worktree off `build/t3-bench-submissions` contains merged main; `make test` green on the branch
- [ ] `CANONICAL_SEED = 4207` defined **once**; `grep -rn "4207"` shows one definition + references; two generator runs diff to **zero bytes**
- [ ] `precedent_memory/bench/oracle.py` exists (~40 lines); a test asserts **no `store`/`retrieve` import, no bitmap call**; oracle labels the conftest `scenario` cases correctly by hand (`rights_only`/`sched_only`/`both`/`nobody` × KB-0001/KB-0004/MEDIA-113 + revoked/quarantined/stale variants)
- [ ] Topology: DB has exactly **20 roles, 1,000 docs, 40 principals**; `effective_policy.required_bits` populated for every restricted doc; reproducible at seed 4207
- [ ] Ground truth: `len(queries) == 10000`, `deny_expected_count >= 3000`; distribution in the raw JSON
- [ ] `make bench` exits 0, (re)writes `precedent_memory/bench/RESULTS.md` reproducibly; raw JSON committed alongside; re-parsing the JSON reproduces the table
- [ ] RESULTS.md has the `Metric | Measured | Threshold | Pass/Fail` table for all ten metrics + an attacks row; **the FNR row states deny-expected N + leak count**; `grep '‹' RESULTS.md` empty; unmeasured-Saturday metrics say "not yet measured — realism run lands Saturday"
- [ ] `pytest tests/test_adversarial.py` — **6/6** attacks pass (verbatim names) OR an unenforceable one is a declared NON-CLAIM in RESULTS.md; each enforced attack asserts deny + no restricted content leak + an audit row (or a bounded timing delta)
- [ ] `pytest tests/test_audit_coverage.py` passes AND a dropped-audit-call fixture flips it red (proves it checks coverage); `verify_chain(expected_len=…)` passes
- [ ] Tier-C: derived-memory-correctness row (>99% vs oracle) + the 1k/5k/25k/100k latency-vs-size curve row present with real numbers (or honestly omitted)
- [ ] Seed-4207 **mutation corpus** at a stable path with a loader + hand-off note; replays byte-identically twice
- [ ] Librarian + Operator echo skeletons in `agents/`: `mailbox=True`, `publish_manifest=True`, `chat_proto` included, **seeds read from env** (grep proves none inlined), both badge snippets in each README section
- [ ] `make check-open-weight` clean **AND** a manual grep of `tests/` + the mutation corpus for `claude-|openai-|gpt-|gemini-|grok-|mercury-` is empty (the guard doesn't scan `tests/`)
- [ ] `make secrets-scan` clean; no seed/key/token/accountId/real-name in any committed file, the PR draft, or evidence artifacts
- [ ] `make freeze-check` passes (open-weight + tests + secrets + no `‹`)
- [ ] Live-bench + live drift/TTC + UCI commands exist and **exit non-zero when unconfigured**; the "25k-record store" caption is used, never "141k events"; human-run instructions written
- [ ] Every number in RESULTS.md and the PR README draft traces to `Research/00-verified-claims.md` with its caveat; no refuted claim used
- [ ] Submissions prep complete: PR README draft (template-verbatim, ids byte-for-byte from `docs/compliance/`, six attacks, `[[WAIT:…]]` sentinels), Venice-only `.env.example` (ANTHROPIC/OPENAI deleted), DoraHacks organizer-answer worksheet, scrub-checklist + repo-public pre-flight, evidence line — all secret-free, all reduced to one human click/paste

---

## DEFINITION OF DONE

T3 is done when: the worktree off `build/t3-bench-submissions` carries merged main and `make test` is green; `make bench` emits a complete `precedent_memory/bench/RESULTS.md` (all ten metrics measured-vs-threshold-vs-pass/fail + a 6/6 attacks row) with committed raw JSON, reproducibly at seed **4207**, with the **FNR row stating deny-expected N + leak count**; the **independent oracle** is provably decoupled (no `store`/`retrieve` import, no bitmap) and its labels match the hand-checked conftest scenario; `tests/test_adversarial.py` lands **6/6** (or an honest declared non-claim) and `tests/test_audit_coverage.py` is a real 100%-coverage check; the Tier-C derived-correctness + latency-curve rows carry real numbers; the seed-4207 **mutation corpus** is handed to T1 and the **Librarian + Operator echo skeletons** are pre-registerable with stable env seeds + both badges; the live-bench/drift/TTC/UCI commands are built and exit non-zero unconfigured; `make check-open-weight`, `make secrets-scan`, and `make freeze-check` are clean (including a manual `tests/`-and-corpus grep the guard misses); every number traces to `Research/00-verified-claims.md` with its caveat and "25k-record store" is never "141k events"; and **all submissions plumbing is prepared to a single human click/paste** — the PR README draft, the Venice-only `.env.example`, the DoraHacks worksheet, the scrub checklist, and the repo-public pre-flight — with every claim backed by pasted command output.

Do not fabricate a number, do not self-grade the FNR, do not merge to `main`, and do not perform the account-level acts reserved for the human. Implement the bench and the safety net; measure the product honestly; prepare the submissions. **Begin by loading the `precedent` skill.**
