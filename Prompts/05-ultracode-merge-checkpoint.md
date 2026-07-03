# Ultracode session prompt — Merge T1 + T3, cut Checkpoint 1, and author PROMPT B (the finish-the-remaining prompt)

> **Target model:** Claude **Opus 4.8**, `ultracode` (multi-agent Workflow orchestration, highest reasoning effort). Paste the whole of the section below **"PROMPT — paste from here"** as the first message of a fresh Claude Code session opened in this repo's root. The leading `ultracode` keyword opts the session into Workflow orchestration; optionally append a token-budget directive (e.g. `ultracode +800k`).
>
> **Before you start (human checklist):**
> - This session runs in the repo at `/Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon`. Both build branches are **fully committed on their own tips and the parallel T1/T3 sessions have finished**. This session's job is to **understand both**, **merge them into `main` locally**, **cut a checkpoint (tag + doc)**, and **author the next prompt (PROMPT B)** — it does **NOT** push to origin and does **NOT** make the repo public (both are human GitHub steps; no token is wired).
> - `.env` is populated and **never committed**. This session runs **airplane-first**: everything it verifies (guards, tests, bench, the vertical slice) runs offline against committed fixtures. It makes **no** live Venice/ASI:One/Jira calls — those are human steps it documents.
> - This prompt was written against verified live git ground truth (branches, ahead/behind, merge-base, the single-file Makefile overlap, the exact uncommitted T1-folder state). **Do not trust those SHAs blindly — the FIRST thing you do is re-verify them with your own git commands**, because a drifting branch invalidates the whole merge plan.
> - **Read this entire prompt before running a single command.** Evidence before assertions — you run every verification yourself and paste the actual output before claiming anything is done.

---

## PROMPT — paste from here

# MISSION: Merge Precedent's T1 + T3 branches into main, cut Checkpoint 1, and author PROMPT B

You are a fresh Claude **Opus 4.8** "Ultracode" session with multi-agent **Workflow** orchestration at the highest reasoning effort. Two parallel build lanes have landed on their own branches:
- **T1** (`build/t1-core-loop-sim-agents`) — the deterministic core loop + Venice open-weight client + MediaCo sim + seed data/KB + the three Fetch agents.
- **T3** (`build/t3-bench-submissions`) — the conformance bench + independent oracle + 6/6 adversarial attacks + audit-coverage test + mutation corpus + submissions plumbing.

**T2** (`precedent_memory/` core lib + `console/`) is already merged onto `main`. Your job has three phases:
1. **UNDERSTAND** — fan out parallel readers over T1's branch and T3's worktree and build a definitive, file-level map of what is *done* and what *remains* on each lane. Read the real files; assume nothing.
2. **MERGE + CHECKPOINT** — commit T1's outstanding working-tree work, merge both branches into `main` **locally**, run the full guard/test/bench matrix **against the merged product**, boot the demo and run the G1 vertical slice, and cut a checkpoint (annotated git tag + a committed `docs/checkpoints/CHECKPOINT-1-T1-T3-MERGE.md`).
3. **AUTHOR PROMPT B** — write, to `Prompts/06-ultracode-finish-remaining.md`, a maxed-out autonomous Ultracode prompt that finishes all remaining buildable work in a fresh session, ending with its own step-by-step human walkthrough.

This is a hackathon entry whose eligibility depends on four hard rules that are trivial to violate by accident and **eligibility-fatal** to get wrong. This session does **not push to origin** and does **not flip the repo public** — it merges and checkpoints **locally only**, then hands the human the exact push commands at the very end.

---

## STEP 0 — Load context before touching anything (mandatory, in this order)

1. **Invoke the `precedent` project skill FIRST** (via the Skill tool). It encodes the four hard rules, the build-plan gate discipline, and the working conventions for this repo. Do this before running any merge command or reading any lane's code.
2. Read the two completion prompts in full — they are the contract each lane built to, and PROMPT B must inherit their style, rigour, and rule discipline:
   - `Prompts/03-ultracode-t1-completion.md` (T1's mission, the canonical class-key registry, the seed-4207 decision, the T1 acceptance bar and DoD)
   - `Prompts/04-ultracode-t3-completion.md` (T3's mission, the ten metrics + thresholds, the oracle-independence rule, the interlock contract, the T3 acceptance bar and DoD)
3. Read the authoritative context, in this order:
   - `.claude/skills/precedent/SKILL.md` (rules + conventions)
   - `Plan/BUILD-PLAN.md` (build order, gate discipline, cut order, the ambition ladder in §5)
   - `EXPLAINER-idea-and-plan.md` and `EXPLAINER-roles.md` (the "why", the moat, the demo narrative, the lane split)
   - `Makefile` (the guard/test/bench/demo targets you will run — read exactly what each scans/does; note the `help:` block and the `freeze-check` placeholder-grep caveat below)
   - `scripts/check_open_weight.sh` (what the open-weight grep scans — note it does **not** scan `tests/`)
   - `Research/00-verified-claims.md` (every number carries its caveat label from here — you will need this when authoring PROMPT B's number-honesty section)
4. **Do NOT relitigate settled design.** The contracts, the schema, the model registry, and the merged T2 API are **FROZEN**. You are merging two branches that both built *to* those frozen surfaces — you do not redesign anything, add columns, rename tokens, or "improve" a boundary to make a merge cleaner. If a real conflict forces a design choice, take the minimal union and note it; do not fork an identifier.

---

## THE FOUR HARD RULES — as they bite a MERGE (non-negotiable; each is eligibility-fatal)

A merge is where a violation introduced on *either* branch first becomes visible on the shipped tree. Re-run every guard on the **merged** tree, not the branch tips.

**Rule 1 — Open-weight only.** A literal closed-model id may appear in **`precedent/models.py` and nowhere else**. `make check-open-weight` greps `precedent precedent_memory sim console agents` for `claude-|openai-|gpt-|gemini-|grok-|mercury-`. A model id introduced on either branch only surfaces **post-merge** — so re-run the guard on merged `main`, and **additionally grep `tests/` and any mutation-corpus / data files by hand** (the guard does not scan `tests/`). T1's models.py change adds new role rows there (the sanctioned location) — that is fine; a model id **anywhere else** is a build-breaking regression. `PRECEDENT_DEV_MODELS` / `ALLOW_PROPRIETARY_DEV` stay UNSET.

**Rule 2 — No LLM in the decision, and the oracle stays independent.** The merge must not let any branch's LLM output gate execution or set a risk class. `precedent_memory/retrieve.py` stays LLM-free; class match is deterministic fingerprint equality; the STANDING fast-path makes zero `chat()`/`embed()` calls. Because the T2 core lib is untouched by both branches, this is preserved by construction — but **re-confirm the oracle AST-independence guard still passes on merged main** (`precedent_memory/bench/oracle.py` must import neither `store` nor `retrieve` and must not touch the bitmap), or FNR becomes self-graded and circular.

**Rule 3 — Fail-closed.** Restricted memory is denied when ACL freshness is uncertain; a stale cache may narrow access, never widen it. Denials surface only `denied_count` + `denied_owner_team` — never a title, symptom, body, or secret. Verify end-to-end on a **real file DB** (not `:memory:`) via the INC-3 refusal + Jira-flip-goes-dark beat and the fail-closed-on-expired-pending approval path. The fail-closed CLI guards (`make live-drift` exit 1, `make bench-uci` exit 2 when unconfigured) must still exit non-zero on the merged tree.

**Rule 4 — No secrets.** `.env` is gitignored; `.env.example` holds placeholder names only. Before the checkpoint, `make secrets-scan` (gitleaks over **merged history**) must be clean — a key anywhere in *either* branch's history fails the eventual public-flip gate. Never inline a key, token, seed, accountId, or a teammate's real name into code, a commit, the checkpoint doc, PROMPT B, or a prompt you send to a sub-agent. You do **not** flip the repo public — you only prove the merged history is scrub-clean so the human can.

If any step appears to require breaking one of these, **STOP and find the compliant path** — there always is one.

---

## VERIFIED GIT GROUND TRUTH (re-verify these yourself FIRST — do not trust them blindly)

These were checked live when this prompt was written. A branch that drifted since invalidates the merge plan, so **your very first commands re-establish them**:

- **`main` = `46e22a6`** — the **exact** merge-base of both branches. `merge-base(T1,main)` = `merge-base(T3,main)` = `merge-base(T1,T3)` = `46e22a6`. Neither branch is behind main. Main already carries the merged T2 core lib.
- **`build/t1-core-loop-sim-agents` = `9cd3d10`** — 0 behind / **8 ahead** of main, **66 files** changed. Checked out in the **MAIN folder** `/Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon`, **with uncommitted work present** (see STEP 1).
- **`build/t3-bench-submissions` = `703b051`** — 0 behind / **7 ahead** of main, **27 files** changed. Checked out in the **worktree** `/Users/tahakhan/Documents/Work/Projects/precedent-t3-bench`.
- **The ONLY file both branches change is `Makefile`** (`comm -12` of the two name-only difflists returns exactly one path). `git merge-tree --write-tree` of T1↔T3 exits 0 and produces **zero conflict markers** — git **auto-unions** the Makefile (T1's `sim`/`demo-reset` hunks and T3's `.PHONY`/`bench`/`bench-uci`/`live-drift` hunks are non-adjacent). The brief's "manual union" is not needed unless a branch drifted.
- **T1 is fast-forwardable onto main** (`merge-base --is-ancestor main T1` = true). **T3 is NOT an ancestor of T1** → after T1 lands, T3 needs a real `--no-ff` merge commit (that is where the Makefile auto-merge fires).
- **No git tags exist yet** — the checkpoint tag is net-new; there is no naming convention to match.

**De-risking facts you must still re-confirm, not assume:**
- The `precedent_memory` **core lib** (store/retrieve/db/schema/audit/sync/`__init__`) is already on main from T2 and is **untouched by both branches** (`git diff main..T1 -- precedent_memory/` is empty; T3 touches only `precedent_memory/bench/*` and three `precedent_memory/tests/*`). So T3's bench grades the same core lib already on main — **no divergent-copy risk, only an integration-run risk.**
- **T1 does modify `precedent/models.py` (+18 lines)** — an intended additive change (new model-role rows in the sanctioned file), **not** a contract break. `precedent/contracts.py` and `precedent_memory/schema.sql` are untouched by both branches. Expect models.py to show as changed on the T1 merge; that is correct.
- T1 adds **`pyyaml>=6.0`** to `pyproject.toml`; T3 touches no deps. You **must** re-sync the venv after T1 lands or `precedent/policy.py` imports fail.

---

## PHASE 1 — UNDERSTAND (fan out; read the real files; produce a definitive done/remaining map)

Before merging, build the same file-level understanding a release architect would. **Do not skip this into the merge** — the merge plan is only safe if the two lanes are actually in the state this prompt describes.

**Fan out parallel reader sub-agents (Workflow tool), each with a narrow, read-only remit:**
- **Reader T1-code** — read T1's delivered surface on `build/t1-core-loop-sim-agents`: `precedent/{venice,extractor,policy,ladder,orchestrator,models,contracts}.py`, `sim/app.py`, `agents/{common,watcher,librarian,operator,approval,protocol}.py`, `scripts/{demo_server,run_agents}.py`, `data/raw/*`, `data/kb/*`. Confirm what's implemented vs stubbed. **Specifically confirm the one known T1 gap:** the full triage→approval→execute loop is composed only in `scripts/demo_server.py` (same-process console path); the standalone Watcher's live Chat Protocol handler still defaults to an **echo reply** (`build_chat_protocol(reply=None)`), so an ASI:One chat to the registered Watcher would echo, not run the loop — even though `triage_incident` / `render_approval` / `make_decision` / the approval ledger / Operator `serve_execution` all exist and are unit-tested individually.
- **Reader T1-tests** — read T1's test files and run `git log --stat main..build/t1-core-loop-sim-agents`; confirm the claimed "119 pytest passed, `make check-open-weight` clean, ruff clean, `make demo-reset` 0.4s, `test_t1_integration.py` passes against the REAL orchestrator" by inspecting the tests (you'll re-run them for real after the merge).
- **Reader T3-bench** — in the worktree `/Users/tahakhan/Documents/Work/Projects/precedent-t3-bench`, read `precedent_memory/bench/{conformance_bench,oracle,seed,seed_corpus,mutation_corpus}.py`, `RESULTS.md`, `results.json`, and `precedent_memory/tests/{test_bench,test_mutation_corpus,test_oracle}.py` + `tests/test_adversarial.py` + `tests/test_audit_coverage.py`. Confirm: canonical seed 4207 single-defined; oracle AST-independent; topology 5 levels/20 roles/1000 docs/40 principals; 10,000 queries with ≥3,000 deny-expected; 6/6 attacks with positive controls; real 100%-audit-coverage test with a red-flip meta-test; tier-C rows; mutation corpus (100 mutations, byte-identical replay); fail-closed CLIs. **Specifically confirm the biggest T3 gap:** the bench has **never been re-run against a main that carries T1** — it currently grades the merged T2 lib against a synthetic topology, and `sim/app.py` on the T3 branch is still the T1 stub. Note any working-tree drift in the worktree (e.g. latency-only re-run drift in `RESULTS.md`/`results.json`).
- **Reader submissions/plan** — read `Plan/HUMAN-ACTION-ITEMS-*.md`, `Prompts/04-ultracode-t3-completion.md`, any `Prep/submissions/*` and `Idea/refinement/*deck*` files present on either branch, and the two untracked `Idea/refinement/{CONTEXT-deck-build-brief,DECK-BUILD-CONTEXT}.md` in the T1 folder. Produce the human-decision list and the remaining-work list that PHASE 3 will encode into PROMPT B.

**Synthesise (you, the orchestrator):** a written **DONE / REMAINING map** with, per lane, exact file paths and the verification each remaining item needs. This map is a deliverable — it seeds both the checkpoint doc (PHASE 2) and PROMPT B's work plan (PHASE 3). **Do not proceed to the merge until you can state, from the files, that both lanes are in the state STEP 0 and the ground-truth section describe** — if a lane diverges, re-plan the merge before touching `main`.

---

## PHASE 2 — MERGE + CHECKPOINT (precise ordered plan; each step names its verification)

Run these in order. If any pre-condition fails to re-verify (a SHA moved, `--ff-only` errors, a `<<<<<<<` marker appears), **STOP, re-establish the topology, and re-plan** before continuing — do not force past a drift.

### STEP 1 — Re-verify topology
Run your own commands and confirm every fact in the ground-truth section: the three SHAs, all three merge-bases = `46e22a6`, ahead/behind counts (T1 0/8, T3 0/7), `comm -12` returns only `Makefile`, `git merge-tree --write-tree` of T1↔T3 shows zero conflict markers, `merge-base --is-ancestor main T1` is true, `git tag -l` is empty, and the T3 worktree exists at the stated path.
*Verify:* paste each command's output; every fact matches, or you re-plan.

### STEP 2 — Commit T1's outstanding working-tree work (on `build/t1-core-loop-sim-agents`, in the MAIN folder)
The MAIN folder has uncommitted work that must land **before** the merge. Verified state: `M agents/{common,librarian,operator,watcher}.py` (the badge/`readme_path` fix — adds `common.README_PATH` and wires `description=DESCRIPTION, readme_path=common.README_PATH, publish_agent_details=True` onto Librarian + Operator, which previously did not publish both badges); untracked `Plan/HUMAN-ACTION-ITEMS-GUIDE.md`, `Plan/HUMAN-ACTION-ITEMS-T1-T3.md`, `Prompts/04-ultracode-t3-completion.md`, and two near-duplicate deck briefs `Idea/refinement/{CONTEXT-deck-build-brief,DECK-BUILD-CONTEXT}.md` (355 differing lines).
- **First, a HUMAN GATE (blocks this commit):** the two deck briefs are near-duplicates that become public once the repo opens. **Present the human a `git diff --no-index` of the two files and ask which to keep — one, both, or a merged single file.** Stage only what the human names. Do not decide this yourself.
- Then make **two clean commits** (each body ending with the `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` line per repo convention):
  - (a) `git add agents/common.py agents/watcher.py agents/librarian.py agents/operator.py` → commit `Fix badge/readme_path in Fetch agents (common/watcher/librarian/operator)`.
  - (b) `git add Plan/HUMAN-ACTION-ITEMS-GUIDE.md Plan/HUMAN-ACTION-ITEMS-T1-T3.md Prompts/04-ultracode-t3-completion.md Prompts/05-ultracode-merge-checkpoint.md` **plus whichever deck file(s) the human kept** → commit `Add human-action guides + T3/merge Ultracode prompts + deck-build briefs`. (Note: `Prompts/05-ultracode-merge-checkpoint.md` is THIS prompt — commit it too so the merge session's own source is captured; also `git status` may show `Prompts/06-…` if you have already authored PROMPT B in PHASE 3 — include it in the PHASE 3 commit, not here.)
- Before staging, **grep all five untracked files + the four modified agents for secret-shaped strings** (`claude-|openai-|gpt-|gemini-|grok-|mercury-`, key/token/accountId/seed patterns, real teammate names) — none expected, but confirm.
*Verify:* `git status --porcelain` is clean after the two commits; `git log --oneline -3` shows both; no secret-shaped string in the committed diff; T1's tip advanced by exactly two commits.

### STEP 3 — Fast-forward T1 onto main
`git checkout main && git merge --ff-only build/t1-core-loop-sim-agents`. Main advances to T1's (new) tip with no merge commit. **If `--ff-only` errors, the branch drifted — STOP and re-verify.**
*Verify:* `git log --oneline -1 main` == T1's tip; `git rev-list --count main` increased by T1's commit count.

### STEP 3a — Re-sync the venv
`make install` (or `uv pip install -e '.[dev]'`) so T1's new `pyyaml>=6.0` is present before any test/bench run — else `precedent/policy.py` imports fail.
*Verify:* `python -c "import yaml"` succeeds in the venv; paste it.

### VERIFICATION A — T1-on-main baseline (all must pass before STEP 4)
Run and paste output for each: `make check-open-weight` (only `precedent/models.py` names ids); `make test` (full T1 suite — expect ~119 passed; note that `precedent/models.py` legitimately shows as changed vs the T2 "frozen-clean" proof because T1 added role rows there — that is the sanctioned additive change, not a contract break); `.venv/bin/ruff check .` (clean); `make demo-reset` (< 30 s). **If any fails, fix-forward or STOP — do not proceed to the T3 merge on a red baseline.**

### STEP 4 — Real-merge T3 onto main
`git merge --no-ff build/t3-bench-submissions -m 'Merge T3 bench + submissions into main'` (body ends with the Co-Authored-By line). Git auto-unions the Makefile.
- **Eyeball the merged `Makefile`:** BOTH T1's implemented `sim`/`demo-reset` bodies AND T3's `bench`/`bench-uci`/`live-drift` targets are present, and `.PHONY` lists `sim console jira-smoke demo-reset bench bench-uci live-drift freeze-check`. If any `<<<<<<<` markers appear, the branches drifted — abort the merge (`git merge --abort`) and re-verify SHAs. If a genuine conflict exists, resolve it by **unioning the target blocks** (never dropping either lane's targets), then continue.
*Verify:* `git status` clean post-merge; `grep -n '<<<<<<<' Makefile` empty; both lanes' targets present in the merged Makefile; `git log --oneline -1` is the new merge commit.

### VERIFICATION B — Combined-suite gate (THE critical run; all must pass)
This is the load-bearing check — the two test suites and the bench have only ever run on **separate** branches. Run and paste output for each:
- `make check-open-weight` on the **merged** tree, **plus** a manual `grep -rnE 'claude-|openai-|gpt-|gemini-|grok-|mercury-' tests/ data/ precedent_memory/bench/` (the guard skips `tests/`).
- `make test` — the **combined** T1 tests + T3 `tests/` + `precedent_memory/tests/` **together**. Watch for shared `conftest`/fixture/DB-temp-path/port collisions that only appear when both suites load in one session. If a collision surfaces, it is a **real merge defect** — fix it (isolate the fixture / temp path / port), do not skip the test.
- `make bench` and **diff its output vs the committed `precedent_memory/bench/results.json`**: correctness/label fields are seed-deterministic and must be **byte-identical**; only latency fields may vary. Any correctness/label drift is a real regression to investigate, not a re-freeze.
- Confirm the **oracle AST-independence guard** still passes (grep/test asserting `oracle.py` imports neither `store` nor `retrieve` and touches no bitmap) — FNR must not become self-graded.
- `make secrets-scan` (gitleaks over merged history) — clean.
- `.venv/bin/ruff check .` — clean.

### VERIFICATION C — Runtime seams (must EXERCISE, not import-only)
Prove the demo actually lights up on the merged tree, against a **real file DB** (set `PRECEDENT_MEMORY_DB` to a file path, Wi-Fi off / local-first):
- `make demo-reset` then `make sim` (boots app + console in the same process so live trace works).
- Drive incidents: `curl -XPOST http://127.0.0.1:8000/api/drive/1` (slow-path), `/api/drive/2` (fast-path, zero-LLM), `/api/drive/3` (refused). Confirm **BOTH** the console live-trace panel **AND** the shared-memory DB populate (the shared-SQLite seam: console/`demo_state.py` and T1's writer must agree on the same `PRECEDENT_MEMORY_DB` file; a `:memory:` DB shows blank state even though tests pass).
- Confirm the **INC-3 refusal** shows `restricted — owner: Rights Ops` with **no fix text**, and the Jira-flip beat goes dark (fail-closed).
*Verify:* paste the curl responses and the observed console/DB state; the fast-path shows zero LLM calls; no restricted body appears on any surface.

### VERIFICATION D — Fail-closed guards intact
- Confirm `make live-drift` exits non-zero (exit 1) and `make bench-uci` exits non-zero (exit 2) when Jira creds / the UCI CSV are absent.
- Confirm `tests/test_no_committed_secrets.py` does **not** false-positive on `.env.example` placeholders.
- **Do NOT rely on `make freeze-check` as-is:** its final placeholder-grep step exits 1 on legitimate `‹…›` mail-merge/template tokens in ~14 `Plan/`/`Idea/` docs (a guard-scoping gap, not a real leftover placeholder in a shippable deliverable). Run the three **real** gates directly — `make check-open-weight` + `make test` + `make secrets-scan` — and treat those as the freeze truth. (Fixing the freeze-check grep scope is a PROMPT B task, not a blocker here.)
*Verify:* paste the two non-zero exits and the secrets-test result.

### STEP 5 — Re-freeze T3 numbers if they changed (T3-13)
If `make bench` on merged main produced different `RESULTS.md`/`results.json` correctness fields than the committed frozen numbers (latency-only drift does **not** count), commit the regenerated files, then update the measured figures in `Prep/submissions/BASEDAI-PR-README.md` to match. Leave the `[[WAIT:VIDEO-LINK]]` / `[[WAIT:MENTOR-ANSWER]]` sentinels untouched (human fills them). If the numbers matched, record "bench byte-identical on merged main" and change nothing.
*Verify:* `git diff` of any regenerated bench files is latency-only OR a real correctness change is captured and explained; PR-README figures match the committed bench.

### STEP 6 — Cut Checkpoint 1 (only after A–D all green)
- (a) **Author `docs/checkpoints/CHECKPOINT-1-T1-T3-MERGE.md`** (no template exists — create from scratch) capturing: the merged `main` SHA; the three source SHAs (T1 `9cd3d10` / T3 `703b051` / base `46e22a6` — use the re-verified values); the exact guard/test/bench/demo commands run **with their pasted green results**; the seed-4207 bench numbers with a note whether they matched the committed `RESULTS.md`; the demo click-path (drive 1 / 2 / 3); and the **known-open items** (drawn from your PHASE 1 map — chiefly: standalone-Watcher echo handler not wired to the live loop; bench re-run/re-freeze against merged main; mutation-corpus robustness number not yet on the four surfaces; Makefile `help:` block + freeze-check grep scope stale). `git add` + commit (Co-Authored-By line).
- (b) **Annotated tag:** `git tag -a checkpoint-1-t1-t3-merged -m 'Checkpoint 1: T1 core-loop/sim/agents + T3 bench/submissions merged and verified green (seed 4207)'`. This is net-new; no naming convention to match.
- **Do NOT push the tag or main to origin** — that is the human step in the closing walkthrough.
*Verify:* the checkpoint doc exists and is committed; `git tag -l` shows `checkpoint-1-t1-t3-merged`; `git tag -n1 checkpoint-1-t1-t3-merged` shows the message; `git log --oneline -1` is the checkpoint doc commit sitting on top of the merge commit.

### OPTIONAL SAFETY NET (offer, don't default to)
If the human prefers not to merge direct-to-main: create `integration/checkpoint-1` off main, run STEP 3–4 + Verifications A–D there, then `git checkout main && git merge --ff-only integration/checkpoint-1`. Zero conflicts mean this adds ceremony without reducing risk — mention it as available, but the direct-to-main path above is the recommended default.

---

## ADVERSARIAL VERIFICATION PASS (maxed-out multi-agent — nothing is "done" without pasted output)

After Verifications A–D pass under your own hand, spin an **independent red-team sub-agent lineage** (`superpowers:requesting-code-review` + `superpowers:verification-before-completion`) that **re-runs the gates from scratch on merged main** and does not trust your first pass:
1. **Open-weight airtightness** — re-run `make check-open-weight`; independently `grep -rnE 'claude-|openai-|gpt-|gemini-|grok-|mercury-'` over the **whole merged tree including `tests/`, `data/`, and the mutation corpus**; confirm only `precedent/models.py` names ids.
2. **Bench against merged main** — re-run `make bench`; confirm the correctness/label fields are byte-identical to the committed `results.json`; confirm the **oracle is still import-independent** (grep for `store`/`retrieve` imports + any bitmap call in `oracle.py`) so FNR is a genuine two-implementation cross-check.
3. **Secrets** — re-run `make secrets-scan` over merged history; confirm no key/token/seed/accountId/real-name in any committed file, the checkpoint doc, or PROMPT B.
4. **Combined suite** — re-run `make test`; confirm no fixture/conftest/DB-path/port collision was skipped or xfailed to make the suite green.
5. **Airplane-mode vertical slice** — with **Wi-Fi off**, run `make demo-reset` + the drive-1/2/3 slice end-to-end from the committed snapshot with zero network calls; confirm the fast-path is provably zero-LLM (spy/patch `venice.chat`/`venice.embed`, fail if invoked on the STANDING branch) and no restricted body leaks to any console/trace/audit surface.
6. **Fail-closed** — re-confirm `make live-drift` (exit 1) and `make bench-uci` (exit 2) unconfigured.

If any red-team check disagrees with your first pass, the disagreement wins — fix-forward and re-run. **Paste every command's actual output.** A green claim without pasted output is not green.

---

## PHASE 3 — AUTHOR PROMPT B (write it fresh from the re-verified state)

Write a maxed-out autonomous Ultracode prompt to **`Prompts/06-ultracode-finish-remaining.md`** that finishes all remaining buildable work in a new session. **Author it fresh from what you actually verified in Phases 1–2** — do not copy a canned list; ground every item in a file path and a verification you confirmed. Model its **style, structure, and rigour** exactly on `Prompts/03-...` and `Prompts/04-...`: same "load the `precedent` skill FIRST" opener, same re-verify-before-you-build discipline, same four-hard-rules section (as they bite *finishing* work), same dependency-ordered work plan where every step names its verification, same maxed-out multi-agent + TDD + adversarial-verification strategy, same run-it-yourself acceptance checklist and Definition of Done, and its **own** closing step-by-step human walkthrough. Evidence-before-assertions throughout.

**PROMPT B must be structured to cover (author the real content; do not merely list these):**

- **Opener + re-verify.** Load the `precedent` skill; re-verify the merged state (checkpoint tag present, `make check-open-weight`/`make test`/`make bench`/`make secrets-scan` green on merged main) with its own commands before building. State that it must **not** push to origin or flip the repo public.

- **Priority-ordered buildable work** (integration hardening first, then the ambition ladder, then N1/N2/demo content — each with its file path and its verification):
  - **B1 — Wire the standalone Watcher's live Chat Protocol to the full loop (T1).** `build_watcher()` (the default `watcher` singleton + `scripts/run_agents.py` Bureau) is built with the DEFAULT echo reply (`build_chat_protocol(reply=None)` → `'Precedent Watcher received: {text}'`). Compose the existing, unit-tested pieces — `triage_incident()`, `render_approval()`, `make_decision()`, the approval ledger (`agents/approval.py`), and dispatch of the plan to the Operator (`serve_execution`) — into a live `on_message` handler so an ASI:One chat runs report→one-formatted-message→approve→execute+close→reply-with-audit-hash, not an echo. All helpers exist; only the wiring is missing. *Verify:* a scripted local dry-run drives the handler through the full loop; the echo path is gone.
  - **B2 — Re-run the T3 conformance bench + attacks + audit-coverage against merged main and re-freeze (T3-13).** After the merge the bench must grade the merged product; run `make bench` + the three T3 suites, confirm all-green (FNR/FPR/derived/audit/6-of-6), commit refreshed `RESULTS.md`/`results.json` if correctness changed, and update `Prep/submissions/BASEDAI-PR-README.md` figures. Load-bearing predecessor for the deck slide-10 and BUIDL number-fills. *(If STEP 5 above already re-froze, B2 in PROMPT B is a re-confirmation + downstream figure propagation.)*
  - **B3 — Run the seed-4207 mutation corpus against the merged extractor and record the ONE robustness number.** The corpus + loader exist (T3); run it against T1's merged extractor to produce the single correct-match / safe-degrade / false-fast-path number that feeds four surfaces (on-screen robustness chip, deck slide 10, README first screen, BUIDL page). The number does not exist on those surfaces yet.
  - **B4 — Fix the Makefile `help:` block + freeze-check grep scope (merge cosmetic).** The `help:` block still advertises `sim`/`demo-reset`/`bench` as `(TODO: T1/T2)`/`(TODO: T3)`; update those echo lines to match the implemented targets. Scope `freeze-check`'s final `grep -rn '‹' Plan Idea docs` to shippable surfaces (deck/README/BUIDL, per `Prompts/04` §4.3) or widen its exclusion list so it stops exiting 1 on legit template tokens — then `make freeze-check` can be green as-written.
  - **B5 — Verify the temporal-embargo bench test exists/passes post-merge (T3 stretch).** The `unlock_at` predicate in the deterministic check, covered by a bench test. Confirm present and green on merged main; if absent, add it.
  - **B6 — N1 pitch deck (12 core + 8 appendix slides).** Build from `Idea/refinement/03-pitch-deck.md` (and the kept deck-brief) as an in-repo HTML/Reveal deck; fill slide 10 P99 + extractor numbers from `RESULTS.md` + the mutation run (consumes B2/B3); bake REAL values into the PDF export (never placeholders); add the self-narrating grey caption layer; add the "What exists Monday morning" appendix slide; screenshot the real Promote/Revoke console buttons for slide 7.
  - **B7 — N1 provenance/licence layer + KB integrity review.** Build the README data-provenance table + attribution lines (UCI CC BY 4.0, TVmaze CC BY-SA, Freeview XMLTV, CC0 Kaggle) + the TMDB/IMDb-rejected diligence sentence. Then the honest-data gate: verify each of T1's ~10 KB articles has a real `adapted_from` URL, correct ACL (rights-ops-only on KB-0004/0005) + stale/escalate flags, and that raw data kept its messiness (nulls, dup titles) unsanitised.
  - **B8 — N2 submission scaffolding.** Polish `Prep/submissions/BASEDAI-PR-README.md` into submit-ready copy (measured bench table from B2, six attack names, docs cites; leave only the two `[[WAIT:…]]` sentinels; never retype pinned model ids — paste byte-for-byte from `docs/compliance/`). Turn `DORAHACKS-WORKSHEET.md` into submit-ready BUIDL copy (event 2272, bounties 1370/1367/1364) with every `[NEEDS-FACT]` resolved. Assemble the Fetch deliverables checklist (badges done, profile URLs, shared-chat URL).
  - **B9 — N2 video shot-list + VO script + assembly plan.** The shot list + captions (`25k-record store`, calendar-hours label, no unlabelled vendor claim), the 30-second teaser plan, the not-selected 90-second cut plan, the shared-folder naming convention, the manual-loop 8× time-lapse "8h51m" VO script, and the naive-user playtest grading rubric (TRIAGED/DEGRADED/CONFUSED). Capture is manual; the plans are buildable now.
  - **B10 — N2 QA number-honesty pass.** Cross-check every on-screen/in-caption number against `Research/00-verified-claims.md` + `data/analysis/`: enforce NEVER-BLEND (18.2h calendar vs 8.85h/8h51m business, never averaged), vendor `(vendor-claimed)` labels, `25k-record store` not `P99 over 141k events`, existence-vs-symptom and naive-floor and inverted-stat labels correct, no refuted claim used. Run the pre-export `‹`-grep on shippable surfaces; wire the logged-out link-sweep checklist.
  - **B11 — Demo-prep artifacts from `Plan/prep-spec.md`.** The demo run-of-show (live + recorded variants), the 5 per-person crib sheets (`Prep/crib-sheets/` is empty except `.gitkeep`), the systems walkthrough, the rehearsal-gate checklist (per `Prompts/04` §4.3 gates), and the airplane-mode rehearsal script.
  - **B12 — Selection-branch console features (conditional — build only if the team is selected to present).** Attract-mode idle loop + live RESTRICT hotkey (keypress → live Jira ACL flip → dual-enforcement deny → restore) + the REACH change-record artifact. Conditional on the ~22:00 Fri presenter announcement; PROMPT B pre-stages both branch outputs, the human calls the branch.

  PROMPT B must set the **priority order** as: integration hardening (B1–B5) first → then the ambition-ladder items → then N1 buildable content (B6–B7) → then N2 buildable content (B8–B10) → then demo-prep (B11) → then the conditional selection features (B12). It must obey the cut order in `Plan/BUILD-PLAN.md` §5.1 if the clock bites.

- **The four hard rules as they bite finishing work** — open-weight grep over the whole tree incl. `tests/` before any commit; secrets clean; no LLM in the decision (B1's live handler must not let an LLM output gate execution — the deterministic policy still disposes); fail-closed preserved on the live Watcher path.

- **Multi-agent + TDD + adversarial verification** — dependency DAG (B1–B5 hardening before B6+ content; B6/B8 consume B2/B3 outputs), fan out independent items to parallel sub-agents in git worktrees, TDD per module, a red-team pass that re-runs the guards and re-verifies numbers against `Research/00-verified-claims.md`, and a number-honesty auditor. Nothing done without pasted output.

- **PROMPT B's own closing step-by-step MANUAL walkthrough** — the account-bound human steps PROMPT B's work unblocks, each reduced to a single click/paste with the exact command/file, delineated by gate. It must include: run ≥10 ASI:One discoverability chats through the (now B1-wired, deployed) Watcher + capture the insurance shared-chat URL; the one live Venice round-trip + live `/models` open-weight guard; the Saturday UCI-25k + live Jira drift/TTC runs (fail-closed until creds/data present); deploy the hosted degraded-L0 Watcher; wire the real JiraPermissionSource client + seed issue-security levels; **authorize + perform the origin push of merged main + tag**; run the A–E secrets scrub then flip the repo public + verify logged-out; open the BasedAI fork PR + fill the two sentinels + ask the mentor which deadline governs; submit the DoraHacks BUIDL (event 2272, bounties 1370/1367/1364, answers lock at draft-submit → T1 sign-off first); capture the demo video against the frozen build; practitioner outreach; redeem the Agentverse credit code `UKAIAGENTUKAIAGENTAV`; ratify seed 4207 + lane mapping at G0; watch the ~22:00 Fri presenter-selection announcement and call the branch. For each: the agent prepares everything to a single human action; the account-level act stays human.

**Constraint on this phase:** do **not** write PROMPT B's full text *inside this prompt's output* — you write it to the file `Prompts/06-ultracode-finish-remaining.md`. Author it long enough to be complete and unambiguous with every line load-bearing, exactly as `03`/`04` are. After writing it, **grep the file** for `claude-|openai-|gpt-|gemini-|grok-|mercury-` and for any key/token/seed/accountId/real-name — PROMPT B is a public-repo artifact and must be secret-clean and model-id-clean itself.
*Verify:* `Prompts/06-ultracode-finish-remaining.md` exists, opens by loading the `precedent` skill, re-verifies the merged state, carries the four-hard-rules section, a priority-ordered work plan with per-step verifications, a multi-agent/TDD/adversarial strategy, an acceptance checklist, a DoD, and its own closing manual walkthrough; the model-id/secret greps over it are empty. Commit it (Co-Authored-By line).

---

## ACCEPTANCE CHECKLIST (run these yourself; paste evidence)

- [ ] Topology re-verified: three SHAs, all merge-bases `46e22a6`, T1 0/8 & T3 0/7, `comm -12` = `Makefile` only, `merge-tree` zero conflicts, `--is-ancestor main T1` true, `git tag -l` empty (before your tag)
- [ ] PHASE 1 DONE/REMAINING map produced from reading the real files on both lanes (T1 echo-handler gap + T3 bench-never-run-against-T1 gap explicitly confirmed)
- [ ] T1 working-tree committed in two clean commits after the human's deck-brief keep/drop decision; `git status` clean; no secret-shaped string in the diff
- [ ] `git merge --ff-only build/t1-core-loop-sim-agents` succeeded; venv re-synced (`import yaml` works)
- [ ] VERIFICATION A green: `make check-open-weight`, `make test` (~119), `ruff`, `make demo-reset` (<30s)
- [ ] `git merge --no-ff build/t3-bench-submissions` succeeded; merged Makefile has BOTH lanes' targets, zero `<<<<<<<` markers
- [ ] VERIFICATION B green: merged-tree `check-open-weight` + manual `tests/`/`data/` grep; combined `make test` (no skipped collisions); `make bench` correctness byte-identical to committed `results.json`; oracle still import-independent; `make secrets-scan` clean; ruff clean
- [ ] VERIFICATION C green: `make sim` + drive 1/2/3 against a **real file DB** light the console live-trace panel AND the shared DB; INC-3 shows `restricted — owner: Rights Ops` with no fix text; fast-path zero-LLM
- [ ] VERIFICATION D green: `make live-drift` exit 1, `make bench-uci` exit 2 unconfigured; `test_no_committed_secrets.py` no false-positive on `.env.example`
- [ ] Adversarial red-team pass independently re-ran every guard + the bench + the airplane-mode slice and agreed
- [ ] T3 numbers re-frozen if correctness changed (else "byte-identical" recorded); PR-README figures consistent
- [ ] `docs/checkpoints/CHECKPOINT-1-T1-T3-MERGE.md` committed (merged SHA + 3 source SHAs + pasted green evidence + demo click-path + known-open items); annotated tag `checkpoint-1-t1-t3-merged` created; **NOT pushed**
- [ ] `Prompts/06-ultracode-finish-remaining.md` authored to the `03`/`04` bar, model-id-clean and secret-clean, committed
- [ ] Nothing was pushed to origin and the repo was NOT made public

---

## DEFINITION OF DONE

This session is done when: the live topology is re-verified from scratch; both lanes' done/remaining state is mapped from the real files; T1's outstanding work is committed in two clean commits after the human's deck-brief decision; T1 is fast-forwarded and T3 is `--no-ff`-merged onto **local** `main` with the Makefile correctly unioned and zero conflict markers; Verifications A–D and an independent adversarial red-team pass are all green on the **merged** product — `make check-open-weight` (+ manual `tests/`/`data/` grep), the **combined** `make test`, `make bench` (correctness byte-identical to the committed `results.json`, oracle provably import-independent), `make secrets-scan`, and `ruff` all clean; the demo boots (`make sim`) and the drive-1/2/3 vertical slice runs end-to-end in airplane mode against a real file DB with the fast-path provably zero-LLM and no restricted leak; the fail-closed CLIs still exit non-zero unconfigured; the T3 numbers are re-frozen (or confirmed byte-identical) with PR-README figures consistent; **Checkpoint 1** exists as both a committed `docs/checkpoints/CHECKPOINT-1-T1-T3-MERGE.md` and the annotated tag `checkpoint-1-t1-t3-merged`; `Prompts/06-ultracode-finish-remaining.md` is authored to the `03`/`04` bar (four rules, priority-ordered work plan with per-step verifications, multi-agent/TDD/adversarial strategy, acceptance checklist, DoD, and its own closing manual walkthrough) and is itself model-id- and secret-clean; **nothing was pushed to origin and the repo was not made public** — with every claim backed by pasted command output.

Do not relitigate the frozen contracts, schema, model registry, or T2 API. Do not push or publish. Run the verification before you claim done. **Begin by loading the `precedent` skill, then re-verifying the git topology.**

---

## CLOSING MANUAL WALKTHROUGH — hand this to the human (the ONLY manual steps THIS session needs)

Everything above was automated. These remaining steps are account-bound (no token is wired) and must be done by you, the human. Do them in order.

**1. Confirm the checkpoint landed locally (agent already did this; you verify).**
```
git -C /Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon log --oneline -3 main
git -C /Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon tag -n1 checkpoint-1-t1-t3-merged
```
Expect: the top of `main` is the checkpoint-doc commit sitting on the T3 merge commit, and the tag prints its message.

**2. (Blocking, earlier) The one decision the agent paused for:** you already chose which of `Idea/refinement/CONTEXT-deck-build-brief.md` vs `DECK-BUILD-CONTEXT.md` to keep (one, both, or merged). Nothing further needed — noted here so it is on the record.

**3. Push merged `main` + the checkpoint tag to origin** (this is the GitHub step the agent cannot do — no token wired). From the repo root:
```
git -C /Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon push --follow-tags origin main
```
`--follow-tags` pushes both `main` and the annotated `checkpoint-1-t1-t3-merged` tag in one go.

**4. Confirm the push and the tag on origin:**
```
git -C /Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon ls-remote --tags origin | grep checkpoint-1-t1-t3-merged
git -C /Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon rev-parse origin/main
```
Expect the tag to appear on origin and `origin/main` to equal your local `main` tip.

**5. Do NOT flip the repo public yet.** The public-flip is gated on the full A–E secrets scrub over merged history and is sequenced in `Prompts/06-ultracode-finish-remaining.md`'s own manual walkthrough. Run PROMPT B next; it drives the remaining build and hands you the scrub + publish + submission steps at the right gates.

That is the entire manual surface for this phase: verify the local checkpoint, push `main` + the tag, confirm on origin. Everything else was automated, and everything downstream is sequenced in PROMPT B.
