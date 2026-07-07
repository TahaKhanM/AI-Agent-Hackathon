# Session Working Notes — v4 → v5 refinement run (3 July 2026)

> Autonomous multi-agent refinement session (Claude, ultracode). Mission: close the gap from the 79/80/80/80/79 panel baseline to a winning entry across Conduct / Fetch.ai / BasedAI. This file is the audit trail: every decision, verification, and score movement is recorded here as it happens.

---

## 1. Direct verifications performed THIS SESSION (hard evidence, not planning)

All checks run ~05:00–05:30 Fri 3 Jul against live services using the local `.env` (no secrets printed or committed).

### 1.1 Venice open-weight verification — **BasedAI-fatal item CLOSED**

- `GET /models` (auth OK): **89 text models**; full dumps committed as eligibility evidence:
  - `docs/compliance/venice-models-2026-07-03.json` (default/text)
  - `docs/compliance/venice-models-all-2026-07-03.json` (288 models, all types)
  - `docs/compliance/venice-models-embedding-2026-07-03.json` (9 embedding models)
- **All three pinned text models present**, and Venice's own API metadata (`model_spec.modelSource`) points at their public weight repos:
  | Role | Venice ID | HF weights (from Venice API) | HF status (checked live) |
  |---|---|---|---|
  | FAST | `qwen3-5-35b-a3b` | Qwen/Qwen3.5-35B-A3B | public, ungated, **Apache-2.0**, 14 safetensors shards |
  | SMART | `deepseek-v4-flash` | deepseek-ai/DeepSeek-V4-Flash | public, ungated, **MIT**, 46 shards |
  | HEAVY | `deepseek-v4-pro` | deepseek-ai/DeepSeek-V4-Pro | public, ungated, **MIT**, 64 shards |
  | EMBED | `text-embedding-bge-m3` | BAAI/bge-m3 | public, ungated, **MIT** |
- **EMBED gap closed**: embedding models are only visible via `GET /models?type=embedding` (not the default listing — document this in models.py). `text-embedding-bge-m3` is live; `.env` `VENICE_EMBED_MODEL` now pinned to it.
- **Trap confirmed live**: Venice hosts closed models incl. `claude-fable-5`, `claude-opus-4-8`, `grok-4-3`, `gemini-3-5-flash`, and — in the *embeddings* list — OpenAI's closed `text-embedding-3-small/large` and `gemini-embedding-2-preview`. The whitelist/CI-grep guard must cover embedding IDs too. ⚠️ **Heuristic correction (round-2 judge catch, re-verified against our own dump):** closed models do NOT all have `modelSource: null` — `grok-4-3`, `gemini-3-5-flash` and `qwen-3-7-plus` carry non-null vendor-doc URLs. The only safe automated guard is the one in 02 §1.2: **assert every registry entry's `modelSource` is a non-empty `huggingface.co` URL**, plus the manual HF weights check (done for all four pins).
- **Fallback bench corrections** (02-architecture §1.2 had two bad IDs from the third-party catalog):
  - `llama-4-maverick` — **does not exist** on Venice; remove.
  - `qwen-3-6-27b` — wrong spelling; the real ID is **`qwen3-6-27b`**.
  - `zai-org-glm-5-2` (GLM-5.2, MIT, public) and `kimi-k2-7-code` (public weights, licence "other" = Moonshot modified-MIT — fine for API use, note it) both verified present.
  - Embedding alternates verified present: `text-embedding-qwen3-0-6b`, `text-embedding-qwen3-8b` (both open-weight Qwen repos).

### 1.2 Jira — **JSM Standard trial dependency REMOVED (major de-risk + finding)**

- `GET /rest/api/3/instance/license` → **`jira-servicedesk: FREE`** (not Standard; the planned trial was never provisioned).
- The panel's assumption "Free cannot edit permission schemes → ACL story dead without Standard trial" **does not hold at the API level**. Verified live on the Free site:
  - Create project role → HTTP 200 (**`precedent-rights-ops` = role 10007**, **`precedent-scheduling-ops` = role 10008** — created for real, IDs now in `.env`)
  - Add user to role on MEDIA → 200; read membership → 200; remove → 204 (full ACL-flip cycle, the RESTRICT demo moment)
  - Create permission scheme → 201; add grant (BROWSE_PROJECTS → role 10007) → 201; delete scratch scheme → 204
  - Read MEDIA's scheme (id 10000, 126 grants) → 200
- **Honest caveat**: Free may not *enforce* custom schemes inside Jira's own UI. Not load-bearing: Precedent enforces at its own retrieval layer; Jira is only the polled ACL **source of truth**, and the source data (role membership + scheme grants) is fully read/writable on Free. If the team wants belt-and-braces, the Standard trial remains available — but it is **no longer on the critical path** (saves ~1h Friday morning + a provisioning risk).
- Site has **one human user** (Taha). Two-principal demo options: (a) invite a second free agent seat (JSM Free allows up to 3 agents) — 15 min human task; (b) flip the single account between roles; (c) model the second principal as an agent identity. Option (a) recommended for visual clarity; (b) is the zero-dependency fallback.
- `MEDIA-1` test issue creation was already verified per CLAUDE-AVAILABLE-APIS.md (not re-run).

### 1.2b Jira STANDARD upgrade — verified live (3 Jul, ~08:00, after the user provisioned it)

- `GET /rest/api/3/instance/license` → **`PAID`** (both `jira-servicedesk` and `jira-customer-service`). The Free-tier enforcement caveat in §1.2 is **superseded**.
- **Grant flip on the LIVE assigned scheme 10000 verified** (add 201 → delete 204) — the real demo mechanic, not just a scratch scheme.
- **Issue security (Standard-only feature) created, associated, and enforcement-proven:**
  - Scheme **"Precedent Restricted Runbooks" = 10000**, associated with MEDIA; levels **"Rights Ops Only" = 10000** (member: role 10007) and **"Scheduling Ops Only" = 10001** (member: role 10008); IDs in `.env`.
  - Set/unset `security` on an issue via API: 204 both ways; `SET_ISSUE_SECURITY` already granted to admins.
  - **Timed enforcement test on MEDIA-1**: with the level set, removing the principal from role 10007 → Jira returns **404 within ≤5 s** (stable at 15/30/60 s); re-adding the role restores 200; baseline fully restored after the test. (A first read at ~1 s returned 200 — permission-cache lag; the measured propagation window is seconds, consistent with our stated 2–3 s poll-tick consistency model. Quote "≤5 s Jira-side + ≤3 s poll tick ⇒ flip→dark ≤8 s worst case".)
- **Jira audit records API works** (`GET /rest/api/3/auditing/record`): 593 records; permission-scheme and role events with millisecond timestamps — adopted as the **independent external clock** for the drift/TTC bench and as audit corroboration ("the ACL source's own regulator-grade log cross-references ours").

| # | Time | Decision | Reason |
|---|---|---|---|
| D8 | 08:05 | Jira tier caveat retired; consistency window restated with measured numbers (≤5 s Jira-side propagation) | §1.2b live tests |
| D9 | 08:10 | **ADOPT (Tier A1, net +0.5 ph):** restricted KB runbooks get their ACL from **real Jira issue security** — each restricted article (KB #4/#5) is mirrored/linked as a MEDIA "runbook" issue carrying the "Rights Ops Only" level; `sync.py` polls the `security` field on the same 2–3 s tick (replaces the planned sim-side "KB restriction fields" source, −0.5 ph). The 04 script line "flips the article's restriction in Jira" becomes literally true; the RESTRICT demo becomes **dual-enforcement** (Jira 404 + Precedent deny, two audit logs) | §1.2b; makes an existing script claim real; BasedAI differentiation |
| D10 | 08:10 | ADOPT (free): drift/TTC bench timestamps cross-referenced against Jira's auditing API; README audit-posture line added | §1.2b |

### 1.3 ASI:One + Agentverse

- ASI:One chat completions: live request succeeded (model `asi1` replied). Key verified.
- Agentverse API token: authenticates (HTTP 200 on `/v1/hosting/agents`; zero agents — registration remains a Friday-morning build task as planned).

### 1.4 `.env` gaps filled this session

- `JIRA_RIGHTS_OPS_ROLE_ID=10007`, `JIRA_SCHEDULING_OPS_ROLE_ID=10008`, `VENICE_EMBED_MODEL=text-embedding-bge-m3`.
- Still empty (expected — build outputs): agent seeds/addresses/profile URLs, shared-chat URLs, ops account IDs (needs the second-user invite or decision (b)/(c) above), Kaggle username/key (KAGGLE_API_TOKEN is set; CLI absent — manual CSV download is the documented alternative).

## 2. Baseline hour ledger (supersedes "~30–36h" in 00-panel-verdicts.md)

Capacity: **60–80 productive person-hours** to Sat code freeze (2 near-full-time builders, 1 bounded technical, 2 non-technical). Costed from the v4 specs:

| Workstream | Est. (ph) | Notes |
|---|---|---|
| models.py registry + Ollama profile | 0.5 | verification already done this session (was 1.5) |
| ~~JSM Standard provisioning~~ | 0 | eliminated this session (was 1); +0.5 contingency for 2nd-user invite |
| Agentverse ×3 registration + Chat Protocol echo + discovery test | 3.5 | non-cuttable, front-loaded |
| precedent_memory (schema, write/retrieve, A/B) | 3 | |
| Core loop (contracts, extractor, policy YAML, ladder, fast-path) | 4 | |
| Sim app + surfaces + seeded generator w/ mutations | 3.5 | |
| Jira poll + write-behind + ACL sync + fail-closed | 3 | |
| Approval-via-ASI:One E2E | 2.5 | |
| Console UI (feed, trace, buttons, Baseline Bar, audit) | 5 | |
| Revocation demo + concurrency test + p99 bench | 3 | |
| Data plan (raw pulls, loaders, UCI ingest+stats, provenance) | 5.5 | KB articles moved to non-code row |
| 10 KB articles from real runbooks | 3 | part non-technical |
| BasedAI PR (Sat) | 1.5 | |
| **Technical subtotal** | **≈38.5** | |
| Deck build | 4.5 | non-technical |
| Video record + edit | 3 | |
| Rehearsal + gates | 2 | |
| DoraHacks submission + Demo Day logistics | 1.5 | |
| Q&A prep + printed A1 | 1 | |
| Practitioner outreach (or delete the line) | 2 | |
| **Non-code subtotal** | **≈14** | |
| **Total planned** | **≈52.5** | vs 60–80 capacity → **slack ≈ 7.5–27.5 ph** |

Working rule for this session: treat **~12 ph as safely spendable slack** (midpoint minus coordination/debug overhead). Every adopted improvement must fit inside it or name a displacement. Ledger updates appended below as decisions land.

## 3. Decision log (appended as the session proceeds)

| # | Time | Decision | Reason |
|---|---|---|---|
| D1 | 05:15 | Venice pins confirmed; fallback bench corrected (drop `llama-4-maverick`, fix `qwen3-6-27b`) | live /models + HF checks (§1.1) |
| D2 | 05:25 | JSM Standard trial demoted from critical-path to optional; roles 10007/10008 created; ACL demo mechanics verified on Free | live API tests (§1.2) |
| D3 | 05:30 | ~2.5 ph returned to slack (Venice verify done, JSM provisioning eliminated, roles pre-created) | §1.1–1.2 |
| D4 | 05:40 | UCI match-rate computation DONE (was a Major open item): **94.4% fix-class match rate; 18.2h median for precedented repeats; 558 classes ≥4 occurrences cover 94.8%**. Slide-10 framing updated; the planned `knowledge=true` "killer stat" is INVERTED in real data (74.6h vs 8.6h — confound) and demoted to labelled colour. Script + results in `data/analysis/`. ~0.5 ph returned to slack | measured this session on the real 141k-event corpus |
| D5 | 05:45 | **BasedAI PR moved to Friday evening (~20:00 draft, final before 23:00)** — live GitHub event README says deadline "3 Jul (end of day)" (maintainer TODO) while the Google Doc says 4 Jul before judging; CONTRIBUTING adds "late submissions may not receive evaluation". Opening tonight satisfies both readings. 02 §5's "Saturday AM" line was already inconsistent with 00's "Friday night" — resolved to Friday | live-check discrepancy (see §5) |
| D6 | 05:45 | ADOPT: report the memory bench in BasedAI's own published evaluation vocabulary (FNR/FPR/P50/P99/end-to-end overhead/derived-memory correctness/ACL drift/time-to-consistency; adversarial test names). The track brief Google Doc publishes a full evaluation framework the local exports missed. Est +2 ph (extends the existing bench, no new mechanism) | live-check new info (see §5) |
| D7 | 05:50 | Competitive intel logged: **BioVault (PR #3, pkaysantana = the Discord A/B/C interlocutor)** already submitted to BasedAI — governance-only, FastAPI+React, 20 tests, synthetic payroll demo. Differentiation sharpened in F10 answer: live-Jira ACL sync + real corpus + track-metric bench vs their synthetic standalone. Their compliance claim is narrower than the rule ("no closed calls *in the permission path*") — we claim the full runtime | GitHub PR fetch this session |

## 5. Live-source verification results (6/6 fetched — no LIVE CHECK FAILED items)

All six targets were fetched live this session (workflow `precedent-verify-judge-r1`; DoraHacks needed curl with a browser user-agent — WebFetch gets HTTP 405).

| Source | Verdict | Load-bearing findings |
|---|---|---|
| DoraHacks bounty 1370 (Conduct) | fetched | £8,000 GBP + mission text confirmed. **The 35/30/20/20 rubric is NOT on the live page** (`judgingCriteria` empty) — it lives in the Discord announcement (our `conduct-ai.txt` export, timestamped 27 Jun). Export remains authoritative; note the provenance. |
| DoraHacks bounty 1367 (Fetch) | fetched | Agentverse + ASI:One gates confirmed live. Chat Protocol / no-frontend / weights / bonuses are NOT on the bounty page — they come from the hackpack. Prize shown live: 1,000 USDT total. |
| Fetch hackpack | fetched | All gates + 25/25/20/20/10 weights + Payment Protocol (FET & Skyfire) bonus + 3–5 min video + shared-chat URL confirmed **verbatim**. **NEW-1: hackpack says "Submit the following through Devpost"** — possibly boilerplate (this event runs on DoraHacks), but a missed separate channel would forfeit the track: confirm with the Fetch dev advocate (Gautam, Discord) TODAY; if any Devpost link exists, submit both. **NEW-2: mandatory README badges** on each agent: `![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)` + `![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)` (5-min task, add to registration checklist). Also required: Agentverse profile URL per agent + brief problem/user/outcome description. |
| DoraHacks bounty 1364 (BasedAI) + track-brief Google Doc | fetched | All 5 requirements + both bonus challenges confirmed **verbatim**. Open-weight rule confirmed in the Doc + repo instructions (not on the bounty page). **NEW: full evaluation framework** — FNR <0.1% ("critical failure"), FPR <2%, P50 <50ms, P99 <200ms, end-to-end overhead <100ms, derived-memory correctness >99%, ACL drift <0.5%, time-to-consistency <5 min, 100% audit coverage, O(1)/O(log n) checks; adversarial set: query inference, metadata bypass, timing attack, collection attack, prompt injection, derived-memory attack; test protocol: 5 hierarchy levels / 20 roles / 1,000 ACL-tagged docs / 10,000 ground-truth queries. |
| BasedAICo/hackathons repo | fetched | Template = README.md + .env.example only; headings verbatim captured. **Deadline conflict: event README says "3 Jul (end of day)" (TODO-confirm) vs Doc "4 Jul before judging"** → PR tonight (D5). Suggested rubric (TODO): Autonomy/tech 30, Innovation 25, **Use of BasedAI/sponsor tech 20**, Usefulness 15, Demo 10. Template .env.example lists ANTHROPIC/OPENAI keys as generic examples — our README must explicitly override with the open-weight declaration. Competitive: PR #3 = BioVault (see D7). |
| DoraHacks hackathon 2272 | fetched | Deadline 4 Jul 22:59 UTC = 23:59 BST confirmed. 10-bounty limit confirmed. Platform does NOT enforce repo/video links (`mandatoryGitRepoLink:false`) — Conduct's Discord ask still applies. 18 BUIDLs already submitted. `isBountyRequired:false`. |

Residual live-rule risks: (a) BasedAI prize split ($2k/$1k/$500/HMs) appears only in Discord/local export — live sources show only the $3,800 total; harmless. (b) "Use of BasedAI / sponsor tech 20%" in the suggested rubric — we use Venice (gold sponsor) not BasedAPIs; pre-arm a Q&A line. (c) Conduct rubric provenance is the Discord announcement, not the bounty page — fine, but don't cite "the bounty page" on stage.

## 6. Judge round 1 (fresh instances, scored as-of-deadline) — results

| Judge | Score | Verdict core | Hardest question |
|---|---|---|---|
| Conduct | **81** | 1st–3rd if the Fri 18:00 vertical slice lands; zero code at T-40h is the only thing between this and 1st | "94% match rate uses closed_code — what does triage achieve at ARRIVAL time, measured?" |
| Fetch.ai | **74** | Strongest integration story judged, but all gates at 0%; contends 1st–2nd if Fri-AM registration lands | "Fresh ASI:One session, day-old agent — route my query without an address. Is direct-address 'discoverable'?" |
| VC | **74** | Top-3 pitch on paper; the empty team slide is the only unanswered VC question | "Who's full-time Monday, and what has an actual buyer said?" |
| Technical | **73** | Strongest-engineered plan at the event; Friday freeze arithmetic ~6ph short; two submission gates unowned | "What's your MEASURED confident-but-wrong normalisation rate on mutated tickets?" |
| BasedAI | **69** | Requirement-literal design, but zero measured numbers vs the published evaluation framework; BioVault edges it without FNR/FPR | "What is your measured FNR, and which of the six named attacks did you run?" |

(Deltas vs the v4 paper baseline 79/80/80/80/79 reflect the as-of-deadline discount for unbuilt work — an honesty correction, not regression.)

## 7. Builder round + adversarial verification — outcomes

**Verifications (all live-fetched):** Devpost channel **REFUTED** (hackpack boilerplate from the Mar–Apr 2025 edition; EP5 submits via DoraHacks — the Fetch judge's fatal dissolves; keep a 2-min courtesy confirm with Gautam). JSM Free 3-agent limit **CONFIRMED** (2nd seat safe). TVmaze CC BY-SA + UCI CC BY 4.0 **CONFIRMED**. ASI:One day-old discoverability **CONFIRMED unreliable** — Agentverse docs require agent activity and **≥10 interactions** before discoverability evaluation → new zero-cost checklist item: perform 10+ test chats with the Watcher during Friday testing; register in hour one. Hosted Agentverse agents stay online post-hackathon **CONFIRMED**. `uagents_core.contrib.protocols.chat` + `publish_manifest=True` **CONFIRMED current**. Payment-Protocol rejection rationale **corrected** (wallet setup is easy — testnet faucet; the real risk is transfer implementation + venue variance; rejection stands on time-risk grounds). DoraHacks BUIDLs **editable until deadline** (submit draft early Saturday; organizer-question answers are one-shot).

**Final adoption tiers (supersedes the interim list):**

- **Tier A1 — unconditional (~+18.5 ph):** sponsor-protocol conformance bench (exact published topology: 5 levels/20 roles/1,000 docs/10,000 ground-truth queries; FNR/FPR/P50/P99/overhead/correctness/drift/TTC vs thresholds, pass/fail table; ≥3,000 deny-expected queries so FNR<0.1% is statistically claimable) 3.0 ▪ **6/6 named-attack adversarial suite** (degradable to 4/6; tonight's PR README names all six + commits the skeleton) 3.5 ▪ audit 100%-coverage test 1.0 ▪ extractor false-match measurement (100 mutated tickets) 2.0 + on-trace robustness chip 0.5 ▪ console 5→6 ph 1.0 ▪ agent-hop trail footer in chat replies 1.5 ▪ BasedAPIs portability note + pre-armed Q&A line 0.25 ▪ non-code: badges 0.1, dirty take Fri 16:00 1.0, manual time-lapse owner 0.5, run-throughs Fri 18:30 + 20:00 1.0, why-us Q&A triplet 0.5, evidence-index page 0.25, BUIDL page as 60-s skim artifact 1.5, README first screen (GIF + metrics + links) 1.0, self-narrating deck-PDF captions 0.5, "what exists Monday morning" block 0.5, results-first 12–15s video cold-open montage (within video budget) 0.
- **Tier A2 — schedule-gated (Fri 17:00 checkpoint green, ~+5.5 ph):** TVmaze committed-snapshot quote in chat triage (fetched-at timestamp; genuinely-live call only in the video take) 0.5 ▪ rollback proof panel (pre/post state-hash check) 1.0 ▪ cumulative Baseline-Bar close strip 0.5 ▪ hosted degraded-L0 Watcher (Friday night, NOT Sat AM) 1.5 ▪ live ACL-drift + time-to-consistency measurement vs real Jira role flips 1.0 net ▪ live bench command 1.0.
- **Tier B — branch on tonight's ~22:00 selection announcement (exclusive branches, ~+3–3.5 ph):** SELECTED → attract-mode idle loop 1.5 + live RESTRICT hotkey Q&A weapon 1.5. NOT SELECTED → standalone 90-s video cut (first on the BUIDL page) 1.5 + RESTRICT flip recorded as 15-s shot-6 insert 1.5 + party-trick phone-ticket shot 0.5.
- **Tier C — only at the 80-ph capacity end:** temporal-embargo constraint as bench-test + Q&A slide (NO demo beat — two builders independently rejected the fifth demo concept) 1.5 ▪ derived-memory correctness bench (~1k lineage artifacts vs >99% bar) 1.0 ▪ O(1)/O(log n) latency-vs-size curve 1.0 ▪ change-record ITIL artifact hotkey 1.0 ▪ BasedAPIs venue credit run 0.5.
- **Rejected (final):** on-chain Payment Protocol integration (README monetization model + E6b Q&A line instead) ▪ Devpost as a submission task (refuted; courtesy confirm only) ▪ dual-surface phone ticket ▪ mid-demo Jira-degraded toggle ▪ judge-ticket-as-incident-2 default ▪ final-slide live counter wiring (bake real numbers into the PDF export instead — freeze-checklist line) ▪ temporal-embargo demo beat.

## 8. Judge round 2 (fresh instances, v5 state) — results & convergence

| Judge | R1 | R2 | Why it moved (or didn't) |
|---|---|---|---|
| Conduct | 81 | **81** | Impact criterion now "largely DONE" (measured corpus); still refuses to pay for the unbuilt 38.5-ph Friday — correctly |
| Technical | 73 | **74** | De-risking rated 92/100; feasibility still the binding constraint; caught the A1 under-sum + circular-oracle + PR-owner gaps (all now fixed in the docs) |
| VC | 74 | **74** | Craft rated best-at-event in both worlds; the two fatals are human-only (team slide, build execution) |
| Fetch.ai | 74 | **71** | Sharper on gate risk: all six gates AT_RISK simultaneously with zero calendar buffer; fixes adopted (hello-world Watcher in first 30 min, insurance URL by midday, hosted Watcher → A1) |
| BasedAI | 69 | **65** | Sharper on deliverable risk: bench was on the cut-line and results were post-deadline under the stricter reading; fixes adopted (bench decoupled from product code + run before freeze; skeleton PR at stand-up; independent oracle) |

**Convergence check:** movement ≤4 points across two fresh rounds → the anti-inflation stop rule fires. **No third round.** The residual gap to ceiling is Friday execution + the human layer, which documents cannot score higher without inflation. Round-2 concrete catches (TMDB stragglers in the video captions, the refuted `modelSource:null` heuristic, the 1.1 ph ledger under-sum, circular FNR oracle, robustness-chip sequencing, PR ownership timing) were all fixed in-session and are reflected in the specs — a third panel would be re-scoring plan-stage work with the same discount structure.

**Round-2 in-session closures (zero team cost):** arrival-time top-1/top-3 precedent precision **measured** (59.4% / 87.7% over 24,470 incidents — answers the Conduct hardest question; in `data/analysis/` + Q&A C7) · TMDB/BBC swept from 04's fixture + shot-3 caption · stale "~30–36h" header fixed · `modelSource` guard corrected · conformance bench decoupled + oracle specified · PR moved to morning skeleton · mutation bench retimed to 18:30 · hello-world Watcher first-30-minutes rule · insurance shared-chat URL by midday · '‹'-grep + degraded-strip rule in the freeze checklist · slide-12 contact QR · A9 bottoms-up ACV appendix · three-agent sweep contingency.

**Closing ledger (re-added after the round-2 Technical judge caught a 1.1 ph under-sum, and amended for round-2 adoptions):**
- Baseline 52.0 (after this session's −3.0 verified savings, incl. UCI stats + arrival-time precision computed in-session at zero team cost).
- Tier A1 re-summed at 19.6 ph, then amended: **+1.5 independent FNR/FPR oracle** (round-2 BasedAI hardest question — the ground-truth labels must come from a separate naive conjunction-walk implementation, never the compiler under test), **+1.5 hosted Watcher promoted A2→A1** (Fetch bonus honesty), **−1.0 trims** (BUIDL page 1.5→1.0, README first screen 1.0→0.5), **−0.5** (PR mechanics simplified by the morning-skeleton move). **Tier A1 final ≈ 21.1 ph → committed ≈ 73.1 ph.**
- Tier A2 (schedule-gated) now 4.0 (hosted Watcher promoted out): TVmaze snapshot quote 0.5 · rollback proof panel 1.0 · cumulative close strip 0.5 · live drift/TTC 1.0 · live bench command 1.0 → **77.1 if Friday holds**.
- **Post-Standard amendment (D9): +0.5 net** — restricted runbooks' ACL moves to real Jira issue security (sync reads one more field; replaces the sim-side KB-restriction source). Committed ≈ **73.6**; the dual-enforcement RESTRICT beat and the audit-API external clock cost nothing further (same demo slot, same bench).
- One Tier-B branch ≈ +3.0–3.5 → **≈80.1–80.6 absolute worst case — 0.6 over the 80 ceiling**, so the pre-ratified rule is: if the Tier-B branch fires in full, the cumulative close strip (0.5) and one A2 item drop automatically. Tier C stays unfunded.
- Structural change (round-2): the conformance bench + oracle + adversarial suite (~7 ph) are **decoupled from product code** and run with the bounded-technical contributor from Friday morning, with synthetic results committed BEFORE the 21:00 freeze — this removes them from Friday's two-builder wall-clock (the binding constraint) and from the "BasedAI extras" cut-line.
- Enforcement: 13:00/17:00 checkpoints; 18:00 vertical-slice gate immovable; mutation bench at 18:30 (chip numbers must pre-date the 20:00 run-through); **stand-up must produce a named-person hour grid** (the documents deliberately do not assign people — round-2 Technical fatal is that no one owns the PR; the owner is named at stand-up).
