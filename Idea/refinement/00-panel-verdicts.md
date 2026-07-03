# Refinement Panel Verdicts (3 July 2026, ~02:00)

> Multi-agent refinement run: 5 judges scored the v3 idea against the tracks' **published** criteria → 5 builders produced the deliverables in this folder → a fresh 5-judge panel re-scored the revised package.

## Scores

| Judge | Round 1 | Round 2 | Round-2 verdict (condensed) |
|---|---|---|---|
| **Conduct** (35/30/20/20 rubric) | 73 | **79** | Likely 1st–3rd **if the build lands the critical path**; realistic-data violation genuinely fixed |
| **Fetch.ai** (25/25/20/20/10) | 68 | **80** | Likely 1st–3rd if the hard gates land; round-1 fatal "gates cuttable while track committed" contradiction resolved |
| **BasedAI** | 58 (borderline **ineligible**) | **80** | Likely 2nd–3rd, 1st in reach if benchmark + live revocation demo + Friday-night PR land |
| **Technical execution** | 59 | **80** | Reliability/graduation semantics now engineered, not hand-waved; scope still the #1 risk |
| **Demo Day VC** | 77 | **79** | Likely 1st–3rd if the demo lands as scripted; human-layer content still placeholder |

## What round 1 caught (now fixed in the deliverables)

1. **Invented data violated Conduct's brief verbatim** ("work with realistic data rather than something you made up") → [01-realistic-data-plan.md](01-realistic-data-plan.md): simulated *services* stay, but the *content* is real — TVmaze GB schedule (CC BY-SA) + Freeview-EPG XMLTV snapshot, CC0 Kaggle streaming catalogs for the rights DB, the **UCI ServiceNow incident event log (141k events, CC BY 4.0)** ingested as day-one memory, and KB articles adapted clause-by-clause from *real published runbooks* (CrowdStrike Channel File 291, GitLab runbooks, kube-prometheus, the Ofcom Red Bee review). TMDB and IMDb **rejected on licence grounds** despite the judge suggesting them (TMDB's terms prohibit AI/ML use) — say so on the provenance slide.
2. **"L3 Autonomous" invited a skim-level disqualification** under "a fully autonomous agent is a non-starter" → renamed **"Standing Approval (pre-approved standard change)"** everywhere; a human clicks **Promote** live in incident 1, a **Revoke** button stays visible; script line: *"Approval moved earlier in time — it never left the loop."*
3. **The scripted-demo trap** ("incident generator on cue" = the thing the 35% criterion penalises) → mutated messy ticket text, the spoken word "unscripted", a **judge-files-a-ticket-from-their-phone** offer, and a **live recovery beat** (injected 503 → verification fails → pre-written rollback fires → class demoted).
4. **No visible "before"** → the **Baseline Bar**: persistent stopwatch bars (manual 8h51m vs 60s approved vs 15s standing-approval) in the console header and on slide 5, inside the first 90 seconds.
5. **BasedAI ineligibility** (closed-model keys in the loop; missing PR) → open-weight-only model registry via Venice (verify IDs via GET /models **before** pipeline code; Ollama fallback), sponsor-endorsed **A/B/C permission semantics** implemented verbatim, fail-closed ACL cache, RESTRICT-vs-REVOKE paths defined, and the **separate PR into github.com/BasedAICo/hackathons** added to the critical path (draft PR Friday night).
6. **Fetch contradiction** (track committed but gates on the cut-line) → gates now **non-cuttable and front-loaded**: Agentverse registration + Chat Protocol echo + ASI:One discovery test first thing (needs zero product code); 3 mailbox agents; hosted Watcher for the "keeps running post-hackathon" bonus; ASI:One gets 80s of the video.

## Remaining fatal/major items after round 2 (the to-do list that matters)

- **[FATAL — Conduct] Over-scope vs ~30–36h**: impose the **vertical-slice gate** — by Friday 18:00, incidents 1+2+recovery run end-to-end on seeded real data with Baseline Bar and Promote/Revoke; everything else waits. Pre-execute the technical judge's cuts now (collapse rights+publisher into one service; cut C-flow demo, temporal-embargo rule, in-process third Fetch agent, static ROI ticker; bench 8k→2k).
- **[FATAL — BasedAI] Verify Venice open-weight model IDs** (30-min GET /models + HF weights check) before any pipeline code; commit the /models dump to the repo; Ollama profile as fallback.
- **[FATAL — VC/logistics] Demo Day form by 18:00 TODAY** + name a BasedAI PR owner (draft PR Friday night; DoraHacks alone does not enter that track).
- **[Major] Run the UCI match-rate computation first** (~30 min pandas) *before* committing the "% matched to a documented fix" slide framing — if the raw rate is weak, reframe honestly.
- **[Major] Wire incident 1's retrieval to surface a genuine UCI-derived precedent** alongside the adapted runbook — otherwise "which executed fix came from the 25k real incidents?" has no answer.
- **[Major] Jira: provision the JSM STANDARD 14-day trial (not Free)** — the Free tier cannot edit permission schemes, which the ACL-sync story depends on; verify role-flip → sync within the first hour.
- **[Major] Decide the demo mode in writing** (recorded-first + one live Approve click vs live-local-first) and enforce the §4.3 rehearsal gate mechanically at Saturday 09:00 — two failed gates flips the default.
- **[Major] Fast-path provenance UI**: show raw messy ticket text side-by-side with the structured system event + extractor output, so "messy ticket" and "deterministic fingerprint" don't read as a contradiction live.
- **[Major] The human layer** (cannot be delegated to documents): three one-line team credentials, an honest post-Saturday-intent sentence, and ~2h of practitioner outreach for the validation line — or delete those lines from slide 12 rather than fake them.
- **[Major] Fetch bonus honesty**: laptop-hosted mailbox agents ≠ "keeps running post-hackathon" — deploy the Watcher as a true Agentverse hosted agent (or $5 VPS) in degraded L0 mode.

## Deliverables in this folder

| File | What it is |
|---|---|
| [01-realistic-data-plan.md](01-realistic-data-plan.md) | Licence-checked public datasets + ingest plan + messiness-by-design + honest-framing rules |
| [02-architecture-refinement.md](02-architecture-refinement.md) | Open-weight model registry, A/B/C permission schema, incident-class fingerprint + graduation rules, agent topology + Fetch wiring, demo-reliability doctrine, build order + new cut-lines |
| [03-pitch-deck.md](03-pitch-deck.md) | 12 slides + 8 Q&A appendix slides, build-ready, jargon-purged, 2:40 stage cut mapped |
| [04-demo-and-video-script.md](04-demo-and-video-script.md) | Second-by-second 2:42 live script (+recovery beat), 4-min video script (80s ASI:One), 30s teaser, fallback branches |
| [05-scale-story-and-qa.md](05-scale-story-and-qa.md) | Four-tier integration scale story, what-breaks-first ordering, full Q&A bank answering every judge question |

---

# SESSION 2 — v4 → v5 refinement run (3 July 2026, ~05:00–07:30)

> Second full multi-agent cycle: live verification of all track rules (6/6 sources fetched), hands-on provisioning verification with real keys, fresh judges scoring **as-of-deadline** (unbuilt work discounted — a stricter standard than session 1's if-the-build-lands scoring), builder round, adversarial verification of every new claim. Full audit trail: [06-session-working-notes.md](06-session-working-notes.md).

## Scores per round

| Judge | S1 baseline (v4, if-build-lands) | S2 Round 1 (v5-in-progress, as-of-deadline) | What moved it |
|---|---|---|---|
| Conduct | 79 | **81** | UCI corpus measured (94.4%/18.2h) + verified de-risking banked; discounted for zero product code at T-40h |
| Fetch.ai | 80 | **74** | Honest discount: all gates verified at 0% (Agentverse API returns zero agents); design story rated best-in-class |
| BasedAI | 80 | **69** | The live track brief revealed a published evaluation framework (FNR/FPR/10 thresholds/6 named attacks) the entry had zero measured numbers against; open-weight gate PASSED with committed evidence |
| Technical | 80 | **73** | Friday freeze arithmetic ~6ph short; two submission gates unowned (both fixed in-session); de-risking rated "strongest seen" |
| VC | 79 | **74** | Team slide still placeholder (human-only item); pitch/memorability rated top-3 |

Score deltas vs session 1 are **not regression** — they price execution risk and newly-discovered rules that session 1's judges could not see. The remaining gap to ceiling is mostly *build execution*, not design.

## What this session verified or fixed (hard evidence, not planning)

1. **BasedAI open-weight gate CLOSED**: all 4 pinned Venice models verified live with public HF weights; dumps committed (`docs/compliance/`); embed model pinned; fallback bench corrected (2 bad IDs found).
2. **JSM Standard trial ELIMINATED**: full ACL API surface verified working on the Free tier; roles 10007/10008 created live; 2nd-seat limit (3 agents on Free) adversarially confirmed.
3. **UCI match-rate item CLOSED with real numbers**: 94.4% fix-class match / 98.6% symptom-level / 18.2h precedented-repeat median / 558 classes = 94.8% of volume. The planned `knowledge=true` framing found INVERTED in real data and demoted before it reached a slide.
4. **BasedAI PR deadline conflict FOUND** (repo README: "3 Jul end of day" vs Doc: "4 Jul before judging") → draft PR moved to Friday ~20:00.
5. **BasedAI published evaluation framework RECOVERED** (missed by local exports) → bench rebuilt to conformance shape (10k ground-truth queries, all thresholds, 6/6 named attacks).
6. **Fetch "Devpost fatal" REFUTED** by adversarial verification (hackpack boilerplate from the 2025 edition; EP5 = DoraHacks only). Mandatory README badges + ≥10-interaction discoverability gate found and adopted.
7. **Competitor intel**: BioVault (purpose-built BasedAI entry, PR #3 open since 30 Jun) — differentiation plan: protocol-shaped measured numbers against a live external ACL source.
8. ~20 doc-consistency fixes a probing judge would have caught (stale model names, TMDB references, webhook-vs-polling contradiction, demo-mode default conflict, bench/video overstatement).

## Adoption summary (full tiers + ledger: 06 §7)

Tier A1 unconditional ≈ +18.5 ph (conformance bench, 6/6 attacks, extractor measurement + robustness chip, audit test, hop-trail footer, console realism, submission-surface package for the ~50% no-stage world). Tier A2 schedule-gated ≈ +5.5. Tier B branches on tonight's 22:00 selection announcement. Rejected: on-chain Payment Protocol, dual-surface ticket, mid-demo degraded toggle, temporal-embargo demo beat (bench-test only). **Ledger closing balance: 70.5 committed / 76.0 gated / ≈79.5 worst case vs 60–80 capacity.**

## Remaining items after this session (the to-do list that matters)

- **[FATAL-if-missed, human, TODAY 18:00] Demo Day form** — unverifiable by documents; screenshot the confirmation.
- **[FATAL, tonight ~20:00] BasedAI draft PR** — owner named at stand-up; template headings verbatim; README names all 6 adversarial tests + cites `docs/compliance/`; measured results pushed Sat with a PR comment; ask a mentor which deadline governs.
- **[Blocking, Fri AM] Fetch gates from 0% → registered + 10+ interactions + provisional shared-chat URL.**
- **[Blocking, Fri] The build itself** — 13:00/17:00 checkpoints + 18:00 vertical-slice gate are the enforcement mechanism.
- **[Human] Team slide + post-Saturday intent + practitioner outreach (or delete the line); 2nd Jira seat invite; Gautam courtesy confirm.**
- **[Sat 07:00–09:30] Bench results into the PR; rehearsal gates; 22:00-branch execution.**
