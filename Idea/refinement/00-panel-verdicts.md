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
