# Realistic Data & Demo Credibility Plan

> Refinement lane 1 — written Fri 3 July 2026, early morning. Fixes the Conduct judge's #1 major finding: *"work with realistic data rather than something you made up — publicly available data works fine… the bigger and messier, the better the story."* The MediaCo **systems** stay (conceded acceptable by the judge); every byte of **content** flowing through them becomes real, publicly-sourced, licence-checked data.
>
> Total budget for everything in this file: **~8–10 person-hours**, front-loaded to Friday morning/afternoon because seeding data is upstream of every agent test.

---

## 0. The decision (read this if you read nothing else)

| MediaCo component | Seed with | Licence | Effort |
|---|---|---|---|
| `scheduler` (channels, slots, programme metadata) | **TVmaze API GB schedule** (primary) + **Freeview-EPG XMLTV snapshot** (backup, committed to repo) | CC BY-SA / GPL-3.0 (data pulled from repo output) | 2h |
| `rights` (titles, licence windows, regions) | **Kaggle streaming-catalog datasets (CC0)** — real titles + real regional availability, windows synthesised by a documented rule | CC0 | 1.5h |
| `publisher` (EPG/VOD publish payloads) | Derived from the same TVmaze/XMLTV records — publish = re-serialising real records, failures = real defects already in the data | — | 0.5h |
| `kb` (~10 runbooks) | Written by us, **adapted clause-by-clause from real published procedures** (CrowdStrike Channel File 291, GitLab runbooks, kube-prometheus runbooks, Ofcom/Red Bee incident review) with an `adapted_from:` citation in every article header | MIT / Apache / public bulletins | 3h |
| Historical ticket memory (bootstraps the autonomy ladder + IS the scale artifact) | **UCI "Incident Management Process Enriched Event Log"** — 141,712 events / 24,918 real ServiceNow incidents, CC BY 4.0 | CC BY 4.0 | 2–3h |

**Do NOT use TMDB.** The Conduct judge suggested it, but TMDB's API terms explicitly prohibit use "in connection with, including for training, a machine learning (ML) or artificial intelligence (AI) based Application" ([TMDB API Terms of Use](https://www.themoviedb.org/api-terms-of-use); [TMDB FAQ](https://developer.themoviedb.org/docs/faq)). An AI-agent hackathon entry is squarely inside that prohibition. Using it would hand a sponsor judge a licence violation to find. Saying *"we checked the licence and swapped TMDB out for CC0/CC BY-SA sources"* on the provenance slide is itself a credibility beat — it proves the data diligence is real. (Flagged for the team below.)

**Also avoid:** IMDb non-commercial datasets (personal, non-commercial use only, attribution-restricted — legally grey for a prize competition and the files are heavyweight); BBC /programmes JSON (the public JSON feeds were decommissioned years ago; the successor Nitro API is key-gated behind an approval process we cannot clear by Saturday — [get_iplayer forums](https://www.squarepenguin.co.uk/blog/bbc-iplayer-blows-up-tv-listing-feeds-radio-survives-for-now/)); MovieLens (research-licence, movie-only, no schedule/regional data — solves nothing we need).

---

## 1. Scheduler + publisher data: real UK EPG

### 1.1 Primary: TVmaze API

- **What**: full REST API, JSON, no auth for read. `GET https://api.tvmaze.com/schedule?country=GB&date=2026-07-03` returns every episode airing on GB channels for a date — programme title, episode, airtime/airstamp, runtime, network, summary, image, external IDs ([TVmaze API](https://www.tvmaze.com/api); [API reference](https://static.tvmaze.com/apidoc/)).
- **Licence**: **CC BY-SA** — free for any purpose with attribution (link back to TVmaze) and ShareAlike on the data. Attribution goes in the console footer + README ([TVmaze API page](https://www.tvmaze.com/api)).
- **Size/messiness**: a full GB day is ~1,000–2,000 episode records across dozens of channels; 7 days ≈ 10k records. Messiness is genuine and useful: missing episode summaries, null images, absent season/episode numbers, `airstamp` timezone handling, same programme titles across multiple channels (+1 catch-up channels), web-channel vs broadcast-channel duplication.
- **How to pull (Friday morning, one script)**: fetch 7 days × GB (optionally + US for a second region), write raw JSON to `data/raw/tvmaze/`, then a loader normalises into the scheduler's SQLite. **Commit the raw JSON to the repo** — the live demo must run from the committed snapshot (airplane-mode rule from the technical judge), and the fetch script proves it's real.

### 1.2 Backup: Freeview-EPG XMLTV

- **What**: open-source XMLTV for UK free-to-air TV/radio, 7 days of data rebuilt every 12 hours, sourced from UK TV providers' public data. Single-file grab: `https://raw.githubusercontent.com/dp247/Freeview-EPG/master/epg.xml` ([dp247/Freeview-EPG](https://github.com/dp247/Freeview-EPG), GPL-3.0).
- **Why keep it**: (a) it's literally the artefact class our `publisher` emits — a real XMLTV document, so the publisher's output format is grounded in the actual standard; (b) zero-code fallback if TVmaze rate-limits or wobbles; (c) an *actual UK EPG* on screen (BBC One, ITV1, Channel 4 rows) reads instantly real to UK judges.
- **Licence note**: the repo is GPL-3.0 and states "for personal use" — fine for a hackathon demo; note it on the provenance slide and don't redistribute it as a product feed.
- Tertiary fallback if both die: [iptv-org/epg](https://github.com/iptv-org/epg) grabbers (licensing per-source is grey — use only as emergency).

### 1.3 Mapping onto MediaCo entities

| MediaCo entity | Source field(s) | Notes |
|---|---|---|
| `channel` | TVmaze `network`/`webChannel` (id, name, country) | Keep 6–10 real channels (e.g. BBC One, ITV1, Channel 4, Sky Max…) so the console grid looks like a broadcaster's day |
| `programme` | show `id`, `name`, `genres`, `summary`, `externals` (tvrage/thetvdb/imdb ids) | External IDs = free realistic metadata cross-referencing (and free metadata-mismatch incidents) |
| `schedule_slot` | episode `airstamp`, `runtime`, `season`/`number` | Nulls in season/number and runtime are REAL and become incident fodder (§3) |
| `epg_payload` (publisher) | Slot re-serialised as XMLTV `<programme start= channel=>` | Publisher validation rules run against real records; Freeview-EPG shows the target format |
| `vod_item` (publisher) | Same programme + `availability_window` from the rights DB | |

The publisher's **failure modes need no invention**: reject on missing synopsis, missing episode numbering, runtime null, overlapping slots, slot outside rights window — all conditions that occur naturally in the pulled data (§3).

---

## 2. Rights DB: real titles + real regional availability, windows synthesised by a stated rule

Real licence windows are confidential contract data — **no public dataset of true rights windows exists** (be ready to say this in Q&A; it's correct and shows domain knowledge). The honest construction:

- **Source**: Kaggle streaming-catalog datasets by Shivam Bansal, **CC0 public domain** — [Disney+ Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/disney-movies-and-tv-shows) (~1.4k titles) and [Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows) (~8.8k titles). Fields: `title`, `type`, `country`, `date_added`, `release_year`, `rating`, `duration`.
- **Construction rule (document it verbatim in the README)**: each catalog row becomes a rights record — `licensed_regions` = the real `country` list; `window_start` = the real `date_added`; `window_end` = `window_start` + a term drawn per content type (film 24 months, series 36 months — typical industry terms per ch. 04 context); `exclusivity` flag set on a deterministic subset. **Real titles, real regions, real start dates; only the window term is synthetic, and we say so.**
- **The incident-3 conflict is then real-shaped**: pick titles that genuinely appear in both catalogs (there are many) — same title licensed in overlapping regions/windows is precisely the MGM/Starz failure mode (244 titles improperly licensed inside Starz exclusivity windows — [FilmTake](https://www.filmtake.com/distribution/starz-sues-mgm/), already in ch. 04). The demo's rights-conflict incident emerges from a real cross-catalog title collision, not a planted row.
- Cross-link ~50–100 rights records to scheduler programmes by title match (fuzzy — title matching is itself realistically messy; keep the mismatches, they're demo fodder).
- Using a *Disney+* catalog dataset rhymes with the locked origin story. It's CC0 public data about publicly visible catalog listings — safe. If the team prefers distance, use only the Netflix file; mechanics identical.

---

## 3. Historical ticket memory: the UCI ServiceNow event log (the scale artifact)

**Dataset**: [Incident Management Process Enriched Event Log — UCI ML Repository #498](https://archive.ics.uci.edu/dataset/498/incident+management+process+enriched+event+log). **141,712 events / 24,918 incidents** from the audit system of a real ServiceNow instance at an IT company, anonymised. **CC BY 4.0** — attribution-only, fully safe. 36 attributes including `incident_state`, `category`/`subcategory`, `priority`/`impact`/`urgency`, `assignment_group`, `reassignment_count`, `reopen_count`, `made_sla`, `knowledge` (KB-used flag), `closed_code`, `opened_at`/`resolved_at`/`closed_at`, `problem_id`, `rfc` (related change request).

This one ingest does four jobs simultaneously:

1. **Kills "invented data"** — Precedent's memory contains ~25k *real* incidents on day one of the demo.
2. **Bootstraps the autonomy ladder credibly.** Fingerprint each incident as `(category, subcategory, closed_code)` — deterministic fields, satisfying the technical judge's "class key must not come from the LLM" demand. Classes with many verified resolutions arrive already promoted (via the human "Promote to standing approval" action for the top handful — matching the L3-rename fix); rare classes sit at L0/L1. The ladder's opening state is *derived from real history*, not hand-set.
3. **IS the scale artifact.** Run the retrieval + ACL-filter benchmark over the full 141k-event corpus: report **P99 permission-check latency** and **match rate** ("% of incoming incidents whose fingerprint matches a documented prior fix") on one slide. This is the "% of incidents matched to a documented fix" stat the console already instruments — now measured over real data. (Feeds the BasedAI 5–10k-record benchmark ask too: tag ingested records across 3+ synthetic team boundaries using `assignment_group`.)
4. **Gives an honest, measured "before" baseline** — see §5.

**Ingestion plan (2–3h)**: download CSV → collapse events to per-incident records (last event per `number`, keep `reassignment_count`/`reopen_count` maxima) → map to the executed-fix-with-provenance schema: symptom = category/subcategory/description fields; fix = `closed_code` + linked `rfc` where present; approver = `resolved_by` (anonymised ID); outcome = `made_sla` + `reopen_count`; ACL tag = `assignment_group`-derived team boundary. Load into SQLite; precompute embeddings offline (open-weight embedder per BasedAI lane) and commit vectors.

**Honest framing (put in README + speaker notes)**: this is an *IT-company* ServiceNow log, not a broadcaster's — we use it as the historical memory corpus and for baseline statistics; the three live demo incidents run on the media stack. If a judge probes: "no broadcaster publishes its ticket history; this is the largest public real incident log in existence, and the loop is vertical-agnostic — which is our expansion argument anyway."

---

## 4. KB corpus: ~10 runbooks grounded in real published procedures

Rule: **no article invented from whole cloth.** Every article is adapted from a named public source, with an `adapted_from:` URL in its YAML front-matter, and follows the real runbook shape (title / symptoms / preconditions / steps / verification / rollback / owner / last-reviewed). Sources:

- **[CrowdStrike Channel File 291 remediation](https://www.crowdstrike.com/en-us/blog/falcon-update-for-windows-hosts-technical-details/)** + the official [falcon-windows-host-recovery](https://github.com/CrowdStrike/falcon-windows-host-recovery) repo — the actual published procedure (boot to safe mode, delete `C-00000291*.sys`, reboot). This is already the pitch hook; now the hook's runbook is literally in the KB.
- **[GitLab public runbooks](https://gitlab.com/gitlab-com/runbooks)** (MIT) — the gold standard of real production runbook *style*; steal structure, tone, verification-step discipline.
- **[kube-prometheus runbooks](https://github.com/prometheus-operator/runbooks)** ([runbooks.prometheus-operator.dev](https://runbooks.prometheus-operator.dev/)) — real alert-keyed runbooks; the alert→runbook keying pattern is exactly the Librarian's retrieval pattern.
- **[Ofcom's Red Bee incident review](https://www.ofcom.org.uk/siteassets/resources/documents/tv-radio-and-on-demand/reviews-and-investigations/broadcast-incidents/incident-review-red-bee-media.pdf)** + ch. 04 §2 — the real broadcast failure modes and their real remediation/escalation duties (MCR triage → escalate to scheduling/traffic on-call → discrepancy report → as-run reconciliation).

### The 10 articles (2 ACL-restricted, 2 stale — as per the locked design)

| # | Article | Grounded in | Flags |
|---|---|---|---|
| 1 | EPG publish failure — missing/invalid episode metadata | Real TVmaze null-field defects; XMLTV validation; FastPix/Infomir EPG-desync sources (ch. 04 §2.3) | **Demo incident 1/2** |
| 2 | EPG timezone/DST shift — listings off by one hour | [Infomir EPG-shift procedure](https://infomir.store/mismatch-in-tv-program-schedules-how-to-fix-epg-shift-time-zones-and-dst/) — a real published fix doc | Messy-input variant target |
| 3 | Schedule slot overlap after late change | ch. 04 §2.3 (overruns/breaking-news cascades) + GitLab runbook structure | |
| 4 | VOD item published outside rights window — takedown + republish | MGM/Starz failure mode; steps mirror as-run reconciliation duties (ch. 04 §6.5) | **ACL: Rights Ops only — demo incident 3** |
| 5 | Rights-window conflict between platforms (exclusivity breach check) | Same; cross-catalog title collision from §2 | **ACL: Rights Ops only** |
| 6 | Endpoint agent bad content update — boot-loop remediation | **CrowdStrike CF-291, near-verbatim** | The hook's own runbook |
| 7 | Publish pipeline job stuck/failed — requeue with verification | GitLab runbooks (sidekiq/job-queue patterns) | |
| 8 | Subtitle/access-service file missing on publish | Red Bee/Channel 4 Ofcom case (ch. 04 §2.1) | **Stale** — references a decommissioned backup path (agent flags staleness) |
| 9 | As-run log reconciliation mismatch | BXF/as-run reality (ch. 04 §6.4) | **Stale** — old file-drop directory |
| 10 | Authentication/entitlement backend capacity error | Disney+ launch-day auth failure (ch. 04 §2.5) | Escalate-class (no safe admin fix → routes to Escalate, showing the ladder's floor) |

**Provenance display**: the console's KB view shows the `adapted_from` link on every article. When the Librarian retrieves article 6, a real CrowdStrike URL is visible on stage.

---

## 5. Before/after quantification — honest math

Three layers, each labelled with exactly what it is. Never blend them.

1. **Industry baseline (cited)**: 8.85 business hours average MTTR (MetricNet/HDI — Research README #3); $22/$69/$104 ticket-cost ladder ([MetricNet primary whitepaper](https://www.metricnet.com/wp-content/uploads/2020/08/ROI-of-Service-and-Support-v1.pdf), quote vintage as ~2019–2020). Powers the ROI ticker; label on-slide as "industry benchmark".
2. **Measured baseline from the real corpus — ✅ COMPUTED (3 Jul session; results + script in `data/analysis/`)**: **94.4% fix-class match rate** (chronological — the incident's exact fix class had a prior resolved precedent; 98.6% at symptom level), and **precedented repeats still took a median 18.2 calendar hours** (p75 136.6 h; 36% breached SLA; 47% reassigned ≥1×). The line: *"in 24,918 real incidents, 94% arrived with a precedent already in the history — and still took a median of 18 hours to resolve. Retrieval, not resolution, is the bottleneck."* ⚠️ The originally-planned `knowledge=true` "killer stat" is **inverted in the real data** (KB-using incidents are 9× slower — causal confound); use only the permitted colour framing in `data/analysis/uci-baseline-results.md`, never the causal claim. Calendar-vs-business-hours labels are mandatory (UCI = calendar; MetricNet 8.85 = business).
3. **Measured demo delta (timed live)**: one team member performs the manual loop ONCE for incident 1's exact failure — read ticket → search KB → open admin console → apply fix → write resolution note — screen-recorded and timed honestly (expect 8–15 min without approval queueing; state "excluding approval-queue wait, which the industry baseline says dominates"). The persistent before/after header bar (Conduct fix #4) then shows three bars: **industry 8.85h → our manual walk-through Xm:Ys (recorded) → Precedent 60s / 15s (live elapsed, drawn in real time)**.

**Pre-armed answer to the sharp MTTR question** ("L1/L2 still wait for a human — what did you compress?"): we compress lookup + diagnosis + execution and we *move* approval from a queue to a one-click gate; for L3/standing-approval classes the approval moved earlier in time (the promotion decision), so elapsed time collapses to seconds — and the UCI `knowledge=true` median shows lookup latency is real even when the fix is documented.

---

## 6. Messiness by design — imperfections to EMBRACE, not clean

The data's real defects are the robustness demo. Do not sanitise the seed; instrument the agent's handling of it.

**Naturally present in the real data (free):**
- Missing episode synopses / season-episode numbers / runtimes in TVmaze GB → incident-1 class failures arise from *actual* defects; the Watcher's trace shows the real null field.
- Duplicate/near-duplicate titles (same show on ITV1 + ITV1 +1 + ITVX; same title in both streaming catalogs with different metadata) → Librarian disambiguation visible in the reasoning trace.
- Fuzzy title-match failures between scheduler and rights DB → the "known fix exists but match confidence low → degrade to L0/Escalate" beat.
- UCI log messiness: missing values documented as "unknown information", high `reassignment_count` / `reopen_count` incidents, same-value duplicate rows — quote these properties on the scale slide ("25k real incidents, with real gaps — the bigger and messier, the better the story").
- Timezone/DST edge in `airstamp` handling → article-2 incident class.

**Injected at generation time (the Conduct "unscripted" fix, ~2h):** the incident generator mutates ticket text — typos in error codes, colloquial symptom phrasing ("the guide thingy is showing the wrong programmes"), missing codes, one red-herring detail. The Watcher's triage of the messy variant is shown in the trace. Say the word **"unscripted"** on stage.

**The two live robustness beats this data plan must support:**
1. **Judge files a ticket live** (phone → Jira): vague/misspelled text. Fingerprint match confidence low → graceful degradation to L0/Escalate with a clean investigation dossier. Rehearse with 5+ deliberately awful inputs Friday night.
2. **Error-recovery beat**: incident 2's first execution hits an injected publisher flake → verification fails → pre-generated rollback fires on screen → class demotes → human re-approves. Grounded in a real defect (e.g. the republish payload still missing a mandatory field).

---

## 7. Build order (Friday), provenance slide, and README section

**Order (data is upstream of everything — start at 09:00):**
1. (30m) Download + commit raw: UCI CSV, TVmaze 7-day GB pull script + JSON, Freeview-EPG `epg.xml` snapshot, 2 Kaggle CSVs. All raw files under `data/raw/` with a `SOURCES.md`.
2. (2h) Loaders → SQLite: scheduler/publisher from TVmaze; rights from Kaggle rule (§2); cross-links.
3. (2–3h) UCI ingest → memory schema + fingerprints + offline embeddings; compute §5.2 baseline stats + match rate + P99.
4. (3h, parallelisable to a second person) 10 KB articles from the source list (§4).
5. (30m) Provenance surfacing: console footer attributions, KB `adapted_from` links, README section.

**Cut order if squeezed** (never cut 1 or 3 — they answer the judge's two direct rubric hits): drop Freeview-EPG backup → drop second region pull → reduce KB articles 10→7 (keep 1, 4, 5, 6, and one stale).

**Provenance slide (one slide, verbatim-ready):**
> *"Everything Precedent touched today is real public data: a real UK broadcast schedule (TVmaze, CC BY-SA; XMLTV), real streaming-catalog rights data (CC0), 24,918 real ServiceNow incidents (UCI, CC BY 4.0) as its memory, and runbooks adapted from CrowdStrike's actual Channel File 291 bulletin, GitLab's and Kubernetes' production runbooks. Only the licence-window terms are synthesised — because no company publishes its contracts — and we say exactly how."*

**README `## Data provenance` section**: table of source / licence / what we derived / link, plus the rights-window construction rule (§2) and the UCI honest-framing paragraph (§3).

---

## 8. What this plan deliberately does NOT claim

- No claim that rights windows are real contract data (synthesised by stated rule).
- No claim the UCI incidents are media incidents (IT-company ServiceNow log, used as memory corpus + baseline).
- No TMDB, no IMDb datasets, no BBC Nitro — licence/access reasons stated above.
- The manual-baseline recording is our own walk-through, labelled as such; the 8.85h figure stays clearly cited as the industry benchmark.

Sources: [UCI dataset #498](https://archive.ics.uci.edu/dataset/498/incident+management+process+enriched+event+log) · [TVmaze API](https://www.tvmaze.com/api) · [TVmaze API reference](https://static.tvmaze.com/apidoc/) · [dp247/Freeview-EPG](https://github.com/dp247/Freeview-EPG) · [iptv-org/epg](https://github.com/iptv-org/epg) · [TMDB API Terms](https://www.themoviedb.org/api-terms-of-use) · [TMDB FAQ](https://developer.themoviedb.org/docs/faq) · [Kaggle Disney+ titles](https://www.kaggle.com/datasets/shivamb/disney-movies-and-tv-shows) · [Kaggle Netflix titles](https://www.kaggle.com/datasets/shivamb/netflix-shows) · [GitLab runbooks](https://gitlab.com/gitlab-com/runbooks) · [prometheus-operator runbooks](https://github.com/prometheus-operator/runbooks) · [CrowdStrike CF-291 technical details](https://www.crowdstrike.com/en-us/blog/falcon-update-for-windows-hosts-technical-details/) · [falcon-windows-host-recovery](https://github.com/CrowdStrike/falcon-windows-host-recovery) · [MetricNet ROI whitepaper](https://www.metricnet.com/wp-content/uploads/2020/08/ROI-of-Service-and-Support-v1.pdf) · [Infomir EPG-shift fix](https://infomir.store/mismatch-in-tv-program-schedules-how-to-fix-epg-shift-time-zones-and-dst/) · [Ofcom Red Bee review](https://www.ofcom.org.uk/siteassets/resources/documents/tv-radio-and-on-demand/reviews-and-investigations/broadcast-incidents/incident-review-red-bee-media.pdf)
