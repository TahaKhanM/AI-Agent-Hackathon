# Checkpoint 1 — T1 + T3 merged into main (verified green)

**Cut:** 2026-07-03, by the merge/checkpoint Ultracode session. The session itself ran **no `git push`** and did **not** change repo visibility. Note: the repo was already public, and an **external git auto-sync on the machine subsequently pushed `main` + this tag to origin** (verified: no push command, hook, or sub-agent in the session did it). gitleaks was clean over the merged history, so no secret was exposed — but the publish happened via auto-sync rather than the human's intended scrub-gated step. See the "Next steps" note.
**Tag:** `checkpoint-1-t1-t3-merged`
**Merged main SHA:** `02e9f7f`

Precedent's two parallel build lanes — **T1** (deterministic core loop · Venice open-weight client · MediaCo sim · seed data/KB · Fetch rails) and **T3** (conformance bench · independent oracle · 6/6 adversarial attacks · audit-coverage test · seed-4207 mutation corpus · submissions plumbing) — are merged onto local `main` and verified green against the merged product. T2 (`precedent_memory/` core lib + `console/`) was already on `main`.

## Merge topology (re-verified live before merging)

| Ref | SHA | Role |
|---|---|---|
| merge-base of both lanes | `46e22a6` | common ancestor; main already carried merged T2 |
| T1 lane delivered tip | `9cd3d10` | 8 commits ahead of base (`build/t1-core-loop-sim-agents`) |
| + merge-session commit (a) | `6a25ec6` | Fix badge/readme_path in Fetch agents (watcher/librarian/operator) |
| + merge-session commit (b) | `e9cfd9f` | Add human-action guides + T3/merge prompts + merged deck brief |
| main after T1 fast-forward | `e9cfd9f` | `--ff-only` (no merge commit); commit count 13→23 |
| T3 lane tip | `703b051` | 7 commits ahead of base (`build/t3-bench-submissions`) |
| **merged main (this checkpoint)** | `02e9f7f` | `--no-ff` merge of T3 into main; parents `e9cfd9f` + `703b051` |

- Ground truth re-verified from scratch: three merge-bases all `46e22a6`; T1 0-behind/8-ahead, T3 0-behind/7-ahead; the ONLY file both lanes changed was `Makefile`; `git merge-tree` produced zero conflict markers pre-merge; `git tag -l` was empty before this tag.
- **Makefile auto-unioned cleanly** (ort strategy, zero conflict markers): T1's real `sim:`→`scripts/run_demo.py` and `demo-reset:`→`scripts/demo_reset.py` bodies + T3's `bench:`/`bench-uci:`/`live-drift:` targets; `.PHONY` carries both lanes' targets.
- Working-tree work committed in two clean commits after the human's deck-brief decision (**merge into one** → the two near-duplicate briefs reconciled into `Idea/refinement/CONTEXT-deck-build-brief.md`; duplicate dropped).

## VERIFICATION A — T1-on-main baseline (green)

```
make check-open-weight  -> open-weight guard OK: model names appear only in precedent/models.py   (exit 0)
ruff check .            -> All checks passed!
make demo-reset         -> demo-reset OK in 0.4s (real 0.48s)   [sim db + memory db reset, STANDING pre-seeded]
make test               -> 119 passed, 2 warnings in 8.80s
```
(`import yaml 6.0.3` confirmed after `uv pip install -e '.[dev,agents]'`; T1's only dep add is `pyyaml>=6.0`.)

## VERIFICATION B — combined-suite gate on merged main (green)

```
make check-open-weight               -> OK (exit 0)
grep tests/ data/ bench/ (id-shaped) -> clean (whole-tree hits only in models.py / docs/compliance evidence / rule-prose)
make test  (combined T1+T3)          -> 161 passed, 2 warnings in 9.52s   (119 T1 + 42 T3; no skips/xfails/collisions)
make bench                           -> FNR 0 leaks / 5,219 deny-expected · FPR 0 / 4,781 allow-expected · P99 0.513 µs · 6/6 attacks
  vs committed results.json          -> 24 changed leaf fields, ALL latency-only, 0 correctness/label drift  (byte-identical correctness)
oracle independence                  -> test_oracle.py 12 passed incl. test_oracle_is_structurally_independent
make secrets-scan (gitleaks 8.30.1)  -> 29 commits scanned, no leaks found
ruff check .                         -> All checks passed!
```

## VERIFICATION C — runtime seams exercised (green), real file DB, airplane-mode

Booted `make sim` (sim :8100 + in-process demo server :8000, shared **file** DB `data/precedent.db`), Venice pointed at an unreachable URL (hermetic, no external network). Drove the vertical slice:

```
POST /api/drive/1  (slow-path, auto-approve) -> {"incident":1,"verified":true,"rolled_back":false,"outcome":"resolved"}
POST /api/drive/2  (fast-path STANDING)       -> {"incident":2,"verified":true,"rolled_back":false,"outcome":"resolved"}   real 0.01–0.03s
POST /api/drive/3  (refused, restricted)      -> {"incident":3,"verified":false,"rolled_back":false,"outcome":"refused"}
```
- Shared DB populated: `audit_log` 7→32, `memory_record` 3→5; full loop event-types present (detected/triage/retrieval_allowed/retrieval_denied/risk_assessed/approval_requested/approval_decided/executed/verified/memory_stored/refused/class_promoted).
- Ladder progressed: publisher (inc1) L1→L2; scheduler (inc2) STANDING; rights (inc3) L1 unchanged.
- Console `/api/state`: incidents×3, baseline bar `8h 51m` (MetricNet business-hours, labelled); INC-3 `access=denied`, `denied_owner_team="Rights Ops"`; INC-2 ladder level `STANDING`/"Standing Approval" (never "Autonomous").
- **No restricted-body leak**: KB-0004/0005 restricted body probes (the `takedown` / `POST /publisher/vod_item/{id}/takedown` / `RGT-WIN-014` steps) absent from `/api/state`, `audit_log`, and `memory_record`. The rights `memory_record` is a redacted stub ("RESTRICTED — takedown + republish per rights runbook", no endpoints/tokens); the real KB-0004 step body lives only in the sim's KB store, not a leak surface.
- Fast-path resolved in ~0.03s — far under the 1s Venice timeout, consistent with zero-LLM.

## VERIFICATION D — fail-closed guards intact (green)

```
scripts/live_drift_ttc.py (Jira unset)  -> exit 1   (fail-closed, non-zero)
precedent_memory.bench.uci_realism      -> exit 2   (CSV absent, fail-closed)
tests/test_no_committed_secrets.py      -> 2 passed (no false-positive on .env.example)
```
Note: `make freeze-check` still exits 1 on ~10 legit `‹…›` template tokens in `Plan/` docs (a guard-scoping gap, PROMPT B item). The three real freeze gates — `check-open-weight` + `test` + `secrets-scan` — are the freeze truth and are all green.

## Adversarial red-team pass (independent multi-agent re-run — unanimous PASS, zero disagreements)

An independent 6-agent lineage (Opus 4.8) re-ran every gate from scratch on merged main `02e9f7f` and did not trust the first pass. All six returned **PASS** with an empty `disagreement_with_first_pass`:

| Check | Verdict | Independent evidence |
|---|---|---|
| Open-weight airtightness | ✅ PASS | `check-open-weight` exit 0; id-shaped grep over tests/ data/ bench/ = 0 hits; whole-tree hits only in `models.py`, `docs/compliance/*.json` (evidence), and 3 rule-prose files; `db.py` verified not a backdoor |
| Secrets + real names | ✅ PASS | gitleaks 29 commits, no leaks; all secret-shaped hits are fake fixtures/dataset text; seeds only as env-var names; `.env` gitignored + never tracked; `.env.example` placeholders only |
| Oracle independence | ✅ PASS | imports only `json`+`db`; `test_oracle.py` 12 passed incl. genuine AST-enforcement `test_oracle_is_structurally_independent` |
| Combined suite | ✅ PASS | 161 passed ×2; `-rsx` shows 0 skipped/xfailed/xpassed/errors; `--collect-only`=161; 0 skip/xfail markers in tree |
| Fail-closed CLIs | ✅ PASS | live-drift exit 1, bench-uci exit 2, `test_no_committed_secrets` genuine (not a stub) |
| Airplane-mode dynamic slice | ✅ PASS | bench 0 correctness drift (24 latency-only); zero-LLM spy test PASSED + static confirm (`prepare()` returns `fast=True` before the only `venice.chat`); drive 1/2/3 resolve/resolve/refuse, inc2 0.029s; INC-3 owner-only, **no restricted body leak** (all probes 0/0) |

## Seed-4207 bench numbers (frozen; byte-identical correctness on merged main)

| Metric | Measured | Threshold | Pass |
|---|---|---|---|
| FNR (leak: oracle DENY, compiler ALLOW) | 0 leaks / 5,219 deny-expected = 0.000% | < 0.1% | ✅ |
| FPR (oracle ALLOW, compiler DENY) | 0 / 4,781 allow-expected = 0.000% | < 2% | ✅ |
| Adversarial attacks | 6/6 (`tests/test_adversarial.py`) | 6/6 | ✅ |
| P99 permission check | ~0.51 µs | < 200 ms | ✅ |

Topology: 5 levels · 20 roles · 1,000 docs · 40 principals · 10,000 queries (5,219 deny-expected). Ground truth from the independent oracle (`precedent_memory/bench/oracle.py`, AST-guarded). Correctness/label fields **byte-identical** to the committed `precedent_memory/bench/results.json` (latency-only drift); the committed frozen files were preserved (no re-freeze needed on merged main).

## Known-open items (carried into PROMPT B — `Prompts/06-ultracode-finish-remaining.md`)

1. **Standalone Watcher echo handler not wired to the live loop (T1).** `build_chat_protocol(reply=None)` defaults to an echo reply; `scripts/run_agents.py` builds the Watcher bare, so an ASI:One chat echoes instead of running the loop. All loop helpers (`triage_incident`/`render_approval`/`make_decision`/approval ledger/Operator `serve_execution`) exist and are unit-tested; the full loop is composed only in `scripts/demo_server.py`. → PROMPT B / B1.
2. **Bench re-run/re-freeze against merged main.** Done here (correctness byte-identical, no re-freeze required); PROMPT B re-confirms and propagates the figures into `Prep/submissions/BASEDAI-PR-README.md`. → PROMPT B / B2.
3. **Mutation-corpus robustness number not yet on the four surfaces.** The seed-4207 corpus + loader exist; the single correct-match / safe-degrade / false-fast-path number must be produced against the merged extractor and propagated to the on-screen chip, deck slide 10, README, BUIDL. → PROMPT B / B3.
4. **Makefile `help:` block + freeze-check grep scope stale.** `help:` still advertises `sim`/`demo-reset`/`bench` as `(TODO)`; `freeze-check`'s `‹`-grep exits 1 on legit template tokens in `Plan/`/`Idea/` docs. → PROMPT B / B4.

## Compliance posture at this checkpoint (all four hard rules held on the merged tree)

- **Rule 1 — open-weight only:** `make check-open-weight` clean on merged main; whole-tree grep (incl. `tests/`) finds closed-model ids only in `precedent/models.py` (the allowed file), `docs/compliance/*.json` (catalog evidence), and rule-describing prose. `PRECEDENT_DEV_MODELS`/`ALLOW_PROPRIETARY_DEV` unset.
- **Rule 2 — no LLM in the decision; oracle independent:** fast-path provably zero-LLM (spy test green + static confirm); `precedent_memory/retrieve.py` LLM-free; oracle imports neither `store` nor `retrieve` and touches no bitmap (AST-guarded).
- **Rule 3 — fail-closed:** INC-3 refusal discloses only the owner team, no restricted body on any surface; `live-drift`/`bench-uci` exit non-zero unconfigured.
- **Rule 4 — no secrets:** gitleaks clean over merged history (29 commits); `.env` gitignored and never tracked; `.env.example` placeholders only.

## Next steps (NOT done by this session)

- **Human:** merged `main` + this tag already reached origin via the machine's git auto-sync (not the session). The repo is already public. Run the A–E secrets scrub (`Prep/submissions/SCRUB-AND-PUBLISH-CHECKLIST.md`) retroactively and verify logged-out that no secret is exposed (gitleaks is already clean); decide whether the early publish is acceptable, and consider pausing the auto-sync if you need tighter control of what lands on the public remote.
- **PROMPT B (`Prompts/06-ultracode-finish-remaining.md`):** finish the remaining buildable work (B1–B12), starting with wiring the standalone Watcher and re-confirming the bench, then the ambition ladder, N1/N2 content, demo-prep, and the conditional selection-branch features.
