# T2 Evidence Ledger

> Every T2 claim mapped to its proof and its **stratified status**. Nothing here is
> asserted without a passing test, a runtime probe, a command output, or an explicit
> disclosure. Reproduce with: `python3 -m pytest -q` · `ruff check .` ·
> `make check-open-weight`. Verified 2026-07-03.

**Status strata (Principle 5):** PROVEN (local test) · RUNTIME-PROVEN (observed on a
running server) · MOCK-PROVEN (verified against mocked I/O) · NOT-EXTERNALLY-VERIFIED
(implemented, real-instance smoke pending) · NOT-SAFE-TO-CLAIM.

| # | Claim | Evidence | Status | Safe wording | Unsafe wording |
|---|---|---|---|---|---|
| 1 | Permission-aware memory | `retrieve.permitted()`; `test_conjunction.py` (3) | PROVEN | "Reads are gated by a deterministic permission check." | — |
| 2 | Conjunction (satisfy ALL sources) | `test_conjunction.py::test_multisource_conjunction_denies_partial_clearance` | PROVEN | "A fix from two restricted sources needs both clearances." | "strictest-label" |
| 3 | Fail-closed (stale/revoked/missing/fallback) | `test_fail_closed.py` (6) | PROVEN | "Fails closed on stale, revoked, or missing permissions." | "always available" |
| 4 | Unverified-provenance sentinel (unforgeable) | `test_edge_hardening.py::test_unverified_provenance_denies_even_if_sentinel_bit_granted` | PROVEN | "Unknown provenance is denied even to a holder of the sentinel bit." | — |
| 5 | Empty-lineage hardening (all kinds) | `test_edge_hardening.py::test_kb_summary_empty_lineage_denied_but_public_lineage_allowed`; `test_fail_closed.py::test_executed_fix_without_lineage_fails_closed` | PROVEN | "A record with no provenance is never world-readable." | — |
| 6 | Audit hash chain (tamper/removal detected) | `test_audit.py` (5) | PROVEN | "Hash-chained audit; interior tamper/removal breaks verification." | "immutable / undeletable" |
| 6a | Tail-truncation honesty | `test_edge_hardening.py::test_tail_truncation_detected_only_with_a_remembered_anchor` | PROVEN | "Tail truncation is caught with a remembered length/hash anchor." | "detects all deletion" |
| 7 | T1 shared-DB integration | `test_t1_integration.py::test_t1_plugs_into_t2_over_shared_db` | PROVEN | "T1 shares one DB with the console; proven by an integration test." | — |
| 8 | Canonical `STANDING` stored | `test_console.py::test_class_ladder_row_holds_canonical_token_not_display_text` | PROVEN | "The ladder stores the canonical token `STANDING`." | — |
| 9 | Console displays "Standing Approval" | `test_console.py::test_promote_stores_canonical_standing_displays_label`; served HTML | PROVEN + RUNTIME | "The UI shows 'Standing Approval', never 'Autonomous'." | "Autonomous" |
| 10 | Live stopwatch | `test_console.py::test_live_timer_moves`; runtime 14.8s→16.4s over 1.6s | PROVEN + RUNTIME | "A live timer shows elapsed seconds vs the manual baseline." | — |
| 11 | Baseline caveat on screen | `test_console.py::test_baseline_caveat_visible_on_screen` | PROVEN + RUNTIME | "8h 51m is labelled as MetricNet business-hours MTTR, not this run." | "measured live" |
| 12 | Local Jira-shaped permission flip | `test_console.py::test_permission_flip_makes_restricted_memory_go_dark`; runtime | PROVEN + RUNTIME | "The local Jira-shaped flip takes memory dark, reversibly." | "real Jira flip" |
| 13 | Live Jira client implemented | `sync.py::JiraPermissionSource` (real `httpx`) | MOCK-PROVEN / NOT-EXTERNALLY-VERIFIED | "The live Jira client is implemented and mock-verified." | "verified against real Jira" |
| 14 | Mocked Jira green path | `test_jira_live.py` (6: green/tighten/revoke/outage/no-creds/no-leak) | MOCK-PROVEN | "The Jira read path is verified end-to-end against Jira-shaped responses." | "live dual-lock proven" |
| 15 | Optional live smoke (guarded) | `scripts/jira_smoke.py`; `make jira-smoke`; guard confirmed OFF by default | IMPLEMENTED / NOT-EXTERNALLY-VERIFIED | "A guarded live smoke exists (`PRECEDENT_LIVE_JIRA_SMOKE=1`)." | "smoke passed" (until run) |
| 16 | No AI in permission decisions | grep 0 model tokens in `precedent_memory`/`console`; `test_invariants_guard.py`; `retrieve.py` imports only contracts/db/audit | PROVEN | "No model is called in any permission decision." | — |
| 17 | Model IDs only in `models.py` | `make check-open-weight` OK | PROVEN | "Open-weight only; model ids live only in `precedent/models.py`." | — |
| 18 | No secrets introduced | grep (no real-secret literals); `.env` untouched; `jira_smoke.py` prints counts only | PROVEN (local) / gitleaks full-history NOT run | "No secrets in the T2 changes; token never logged." | "gitleaks-clean" (until run) |
| 19 | No restricted-content leak | `test_conjunction.py::test_no_snippet_leaks_without_permitted`; `test_console.py::test_no_endpoint_leaks_restricted_fix_content`; runtime sweep | PROVEN + RUNTIME | "Refusals disclose only a count and owner team." | "impossible to leak" |
| 20 | Frozen contracts unchanged | `git diff --quiet HEAD -- contracts.py models.py schema.sql` | PROVEN | "Frozen contracts/schema untouched." | — |

## Non-negotiable invariants (Principle 4) — all holding
No AI in permission/risk · fail closed · conjunction · no restricted leak · no secrets ·
model ids only in `models.py` · canonical `STANDING` stored / `"Standing Approval"` displayed.

## Known limitations (disclosed, not defects)
- **Live Jira** is implemented + mock-verified but **not smoked against the real instance** in this environment (needs network + creds; run `make jira-smoke`).
- **TOCTOU** is a deterministic recheck + WAL, not a production concurrency load test.
- **Audit tail-truncation** requires a remembered anchor to detect (documented).
- **`make secrets-scan`** (gitleaks full-history) not runnable locally (gitleaks absent); T2 added no secrets and did not touch `.env`.
