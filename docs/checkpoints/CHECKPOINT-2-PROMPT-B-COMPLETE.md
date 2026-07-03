# Checkpoint 2 — PROMPT B complete (B1–B12 built + verified green)

**Cut:** 2026-07-04, by the PROMPT B ("finish remaining buildable work") Ultracode session. The
session ran **no `git push`** and did **not** change repo visibility. All 12 commits below are local
(the machine's external auto-sync may subsequently push them — that is not this session).

Built atop Checkpoint 1 (T1+T3 merged, `checkpoint-1-t1-t3-merged`). Baseline re-verified green before
building; every claim below is backed by pasted command output in the session transcript.

## What was built (dependency-ordered)

| Item | What | Evidence |
|---|---|---|
| **B1** | Wired the standalone Watcher's live Chat Protocol to the FULL deterministic loop (`serve_chat_turn`); echo path gone; opens conn+SimTools lazily so the address survives the swap | `tests/test_watcher_live_loop.py` (7): full slow-path loop; venice spy = ZERO calls on the STANDING branch (Rule 2); refusal count+owner only (Rule 3); dropped-approval expiry → non-action + reconnect re-present. `scripts/dryrun_watcher_chat.py` drives it offline (hermetic Venice). |
| **B3** | Extractor robustness bench — **found + fixed a real 17→0 false-fast-path bug** (the extractor was grabbing known decoy codes on red-herring rows). Fix: first well-formed code is authoritative; unknown-first degrades (fail-closed). | `make bench-extractor` → **0 false-fast-paths / 100 (0.00%)**, 25/25 red-herring decoys resisted; `precedent_memory/bench/extractor_robustness.json` is the single source of truth. `tests/test_extractor_robustness.py` (5): false_fast_path=0, byte-identical replay, committed-JSON-not-stale. |
| **B4** | Makefile `help:` no longer marks implemented targets `(TODO)`; `freeze-check` placeholder grep scoped to shippable surfaces + matches complete `‹…›` tokens | `make freeze-check` exits 0 on the clean tree. |
| **B5** | Temporal-embargo `unlock_at` predicate (deterministic check + independent oracle), oracle-graded deny-before/allow-after; no schema change (reads the record body) | `precedent_memory/tests/test_temporal_embargo.py` (3), oracle-graded; conformance bench correctness byte-identical (embargo is a no-op on bench records). |
| **B2** | Re-confirmed the bench byte-identical on merged main; propagated the exact 10-metric table + 6/6 attacks + oracle-independence + the B3 robustness number into `BASEDAI-PR-README.md` | table matches committed `RESULTS.md`; only the two `[[WAIT]]` sentinels remain; `grep '‹'` = 0. |
| **B6** | The Demo Day deck (12 core + 9 appendix + Monday slide = 22 pages) via `docs/deck/build_deck.py` → LibreOffice PDF; real numbers baked in; self-narration band; degraded rule applied | `docs/submission/precedent-deck.pdf` (+ clean stage PDF). Verified on the export: 0 `‹`, 0 `[[WAIT`, no "Autonomous" L3 label, no closed-model id, both memorable lines present. |
| **B7** | Data-provenance table + attribution + TMDB/IMDb-rejected sentence; KB integrity review (all 10 adapted_from URLs, ACL, stale/escalate flags); raw-data messiness preserved | `docs/data-provenance.md`, `docs/kb-integrity-report.md` (zero FLAGS; nulls/dups match SOURCES.md). |
| **B8** | DoraHacks worksheet finalized (the one `[NEEDS-FACT]` = B3 number resolved; exactly bounties 1370/1367/1364); Fetch deliverables checklist; model ids byte-identical vs models.py/compliance | `Prep/submissions/DORAHACKS-WORKSHEET.md`, `FETCH-DELIVERABLES.md`. |
| **B9** | Video shot-list (agent) + VO script + 30s/90s cut plans + playtest rubric | `Prep/video/*` — both memorable lines preserved in both cuts; 8h51m is the business figure. |
| **B10** | Canonical numbers reference (`Prep/final-numbers.md`) + the number-honesty audit mapping every shipped number → source + caveat | `docs/number-honesty-audit.md`: zero refuted claims, NEVER-BLEND enforced, vendor labels present, zero placeholders. |
| **B11** | Run-of-show (live+recorded), 5 per-role crib sheets, systems walkthrough, rehearsal-gate (two-failures→recording), airplane-mode script | `Prep/run-of-show.md`, `Prep/crib-sheets/{T1..N2}.md`, `Prep/systems-walkthrough.md`, `Prep/rehearsal-gate-checklist.md`, `Prep/airplane-mode-script.md`. |
| **B12** | (reach) change-record artifact rendering an ITIL change document from REAL audit rows; both selection branches pre-staged | `scripts/render_change_record.py` + `tests/test_change_record.py` (2); `Prep/selection-branch-staging.md`. |

## Final verification (this session, own commands)

```
make check-open-weight  -> OK (only precedent/models.py)
make test               -> 180 passed (161 baseline + 19 new), 0 skips
make bench              -> FNR 0/5,219 · FPR 0/4,781 · 6/6 attacks; correctness byte-identical (restored)
make bench-extractor    -> 0 false-fast-paths / 100; 25/25 decoys resisted (byte-identical replay)
make secrets-scan       -> gitleaks clean
ruff check .            -> All checks passed!
make freeze-check       -> passed (open-weight + test + secrets + placeholder grep)
airplane-mode slice     -> drive 1/2/3 = resolved/resolved/refused; INC-3 owner-only; leak probe 0
```

## Four hard rules on the finished tree

- **Rule 1 (open-weight):** guard clean; whole-tree grep (incl. tests/, data/, corpus, Prep/, docs/) finds closed ids only in `models.py`, `docs/compliance/*.json`, and rule-describing prose.
- **Rule 2 (no LLM in the decision):** B1 standing path venice-spy = zero calls; `retrieve.py` LLM-free; oracle AST-independent; extractor false-fast-path = 0.
- **Rule 3 (fail-closed):** refusal discloses only count + owner team on every surface (console, chat, change-record); leak probe 0.
- **Rule 4 (no secrets):** gitleaks clean; no keys/tokens/real names in code, commits, deck, or submissions.

## Not done by this session (account-bound human acts — see the closing walkthrough)

Origin push; repo-visibility decision; live Agentverse registration + the 3 profile URLs; the ASI:One
shared-chat capture; live Venice/Jira round-trips; the Saturday UCI 25k + live drift/TTC run; the
BasedAI PR; the DoraHacks BUIDL submit; the video capture; practitioner outreach; the ~22:00 selection-
branch call. Each is prepared to a single human action.
