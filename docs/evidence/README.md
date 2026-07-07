# Evidence index — every claim resolves to proof in two clicks

> Linked from the repo README and the BasedAI PR. Judges skimming 18 BUIDLs reward the one repo where every number has a source. Rows marked ⏳ are filled at Friday-night freeze — never ship a ⏳ in the final submission.

| Claim (as spoken/written) | Proof | Status |
|---|---|---|
| All runtime models are open-weight with public HF weights | [`docs/compliance/venice-models-2026-07-03.json`](../compliance/venice-models-2026-07-03.json) (+ `-all-`, `-embedding-` dumps); HF repos: Qwen/Qwen3.5-35B-A3B (Apache-2.0), deepseek-ai/DeepSeek-V4-Flash & -Pro (MIT), BAAI/bge-m3 (MIT) — all ungated, weight files verified 3 Jul | ✅ done |
| 94.4% of 24,918 real incidents arrived with their fix already precedented (98.6% symptom-level) | [`data/analysis/uci-baseline-results.md`](../../data/analysis/uci-baseline-results.md) + reproduction script [`uci_match_rate.py`](../../data/analysis/uci_match_rate.py); UCI dataset #498, CC BY 4.0 (licence re-verified live 3 Jul) | ✅ done |
| Precedented repeats still take a median 18.2 **calendar** hours (p75 136.6h; 36% SLA breach; 47% reassigned) | same files | ✅ done |
| Jira is a live, real ACL source (roles, membership, permission schemes flip via API) | roles `precedent-rights-ops`=10007, `precedent-scheduling-ops`=10008 created via API 3 Jul; full flip cycle HTTP-verified (see `docs/idea/refinement/06-session-working-notes.md` §1.2) | ✅ done |
| Permission-check P50/P99, end-to-end overhead | ⏳ `bench/RESULTS.md` (conformance run, Fri night) | ⏳ |
| FNR / FPR over 10,000 ground-truth queries on the published protocol topology | ⏳ `bench/RESULTS.md` + raw JSON | ⏳ |
| ACL drift & time-to-consistency vs live Jira role flips | ⏳ `bench/RESULTS.md` (drift/TTC section) | ⏳ |
| Six named adversarial attacks covered | ⏳ `tests/test_adversarial.py` (query inference · metadata bypass · timing · collection · prompt injection · derived-memory) | ⏳ skeleton in tonight's PR |
| 100% audit coverage (every retrieval/denial logged) | ⏳ `tests/test_audit_coverage.py` | ⏳ |
| Extractor accuracy on mangled tickets (correct-match / safe-degrade / false fast-path) | ⏳ 100-mutation bench output (Fri night) | ⏳ |
| 15-second standing-approval run is real | ⏳ video shot 4 with phone-clock PiP; on-screen stopwatch | ⏳ |
| ASI:One end-to-end flow, approval bound to sender address | ⏳ public shared-chat URL (provisional captured Fri PM; final at freeze) | ⏳ |
| Agents registered & discoverable | ⏳ Agentverse profile URLs ×3, both badges, ≥10 interactions logged | ⏳ |
| Industry stats ($600B/$200M/8.85h/>60% repeats/$22–104) | [`Research/00-verified-claims.md`](../research/00-verified-claims.md) — 21 claims adversarially verified, caveats labelled | ✅ done |
| Data licences (TVmaze CC BY-SA · UCI CC BY 4.0 · Kaggle CC0; TMDB/IMDb rejected on licence grounds) | [`Idea/refinement/01-realistic-data-plan.md`](../idea/refinement/01-realistic-data-plan.md) §0; licences re-verified live 3 Jul | ✅ done |
