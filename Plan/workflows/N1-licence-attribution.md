# PACKET N1-LICENCE — Verify licences and write the attribution lines + README data-provenance table

> WHO RUNS THIS: **N1** — non-technical teammate, working on **claude.ai FREE tier**, no repo access. One attachment, one Claude conversation, one browser-verification pass. Budget: **~1 hour**.
> WHO BUNDLES AND SENDS: **T3** emails N1 one file (§1).
> WHO RECEIVES OUTPUT AND COMMITS: N1 emails one markdown document to **T3**; T3 commits the pieces into the repo README (`## Data provenance`), `data/raw/SOURCES.md`, and hands the footer line to T2 for the console.
> WHERE THIS FITS IN N1's DAY: Friday **14:00–15:00** (after KB batch 2, before the deck-core block). HARD DEADLINE: output with T3 by **15:30** — the provenance section must be in the README before the repo goes public (~19:30 Friday, ahead of the gitleaks scrub and the Fetch public-repo gate), and the same text feeds the deck's provenance strip and slide A2.

---

## 0. What you are making and why it matters

Every byte of demo content is real public data, and saying so — with licences verified and two sources visibly REJECTED on licence grounds — is itself a scoring beat ("the diligence is the point"). You produce four small text artifacts:

1. The repo README `## Data provenance` section (intro + table + three fixed paragraphs).
2. The console footer attribution one-liner (T2 renders it verbatim).
3. The `data/raw/SOURCES.md` content (terse per-file table).
4. A verification record: you personally opened each licence page today and confirmed the wording.

## 1. What T3 sends you (Friday by 13:45)

| # | Repo path | Why |
|---|---|---|
| 1 | `Idea/refinement/01-realistic-data-plan.md` | The data plan — its §0 table, §2 construction rule, §3 honest framing, and §7 provenance text are your source of truth |

## 2. The browser verification pass (15 min — do this BEFORE the Claude conversation)

Open each link below in your browser. For each, confirm the exact thing listed and note "VERIFIED [time]" or "MISMATCH: [what you saw]". A mismatch goes to T3 immediately by WhatsApp — never silently edit around one. (The team verified these live earlier on 3 Jul; your pass is the same-day re-check that the public pages still say what we cite.)

| Source | URL | Confirm this |
|---|---|---|
| TVmaze API | https://www.tvmaze.com/api | Licence is **CC BY-SA**; attribution requirement = link back to TVmaze |
| UCI dataset #498 | https://archive.ics.uci.edu/dataset/498/incident+management+process+enriched+event+log | Licence badge says **CC BY 4.0**; copy the page's own "cite this dataset" text word-for-word into your notes (we use THEIR citation, never a reconstructed one) |
| Kaggle Netflix titles | https://www.kaggle.com/datasets/shivamb/netflix-shows | Licence shown is **CC0: Public Domain** |
| Kaggle Disney+ titles | https://www.kaggle.com/datasets/shivamb/disney-movies-and-tv-shows | Licence shown is **CC0: Public Domain** |
| Freeview-EPG repo | https://github.com/dp247/Freeview-EPG | Repo licence is **GPL-3.0**; note the "for personal use" wording if present |
| TMDB API terms | https://www.themoviedb.org/api-terms-of-use | The terms contain the prohibition on use in connection with **AI/ML applications** (this justifies our rejection sentence) |

## 3. The Claude conversation (one chat — copy-paste verbatim)

Attach: `01-realistic-data-plan.md` only. Paste, after filling in your verification notes:

```
You are writing the data-licence and attribution text for a hackathon project README. The attached
data plan is the source of truth (see its sections 0, 2, 3, and 7). I have just re-verified each
licence page in my browser; my notes:

[paste your §2 verification notes here, including the UCI page's own citation text]

Produce ONE markdown document with these four parts, exactly:

PART 1 — a README section titled "## Data provenance", containing:
  a) One intro sentence: everything the demo touches is real public data; systems are simulated,
     content is real.
  b) A table with columns: Source | Licence | What we derived | Attribution / link. Rows: TVmaze
     API (CC BY-SA — schedule + programme metadata; attribution link-back to https://www.tvmaze.com;
     note that the committed derived schedule data is shared alike under CC BY-SA); Freeview-EPG
     XMLTV snapshot (GPL-3.0 repo, "for personal use" — committed demo snapshot only, backup EPG
     source, not redistributed as a product feed); UCI Incident Management Process Enriched Event
     Log #498 (CC BY 4.0 — 141,712 events / 24,918 incidents used as the historical fix-memory
     corpus and baseline statistics; cite using the UCI page's own citation text from my notes);
     Kaggle "Netflix Movies and TV Shows" and "Disney+ Movies and TV Shows" by Shivam Bansal
     (CC0 public domain — real titles, regions, and catalog dates for the rights DB); public
     runbook sources for the KB (CrowdStrike CF-291 bulletin, GitLab runbooks (MIT), kube-
     prometheus runbooks, Ofcom Red Bee review — each KB article carries its own adapted_from URL).
  c) The rights-window construction rule, copied VERBATIM from the data plan's section 2 sentence
     beginning "each catalog row becomes a rights record" — including "Real titles, real regions,
     real start dates; only the window term is synthetic, and we say so."
  d) The UCI honest-framing paragraph from the data plan's section 3: this is an IT-company
     ServiceNow log, not a broadcaster's; we use it as the historical memory corpus and for
     baseline statistics; the three live demo incidents run on the media stack.
  e) A short paragraph titled "Sources we checked and rejected": TMDB — its API terms prohibit
     use in connection with training or operating machine-learning / AI applications, which an AI-
     agent hackathon entry is squarely inside, so we swapped it for CC0/CC BY-SA sources; IMDb
     non-commercial datasets — personal, non-commercial use only, legally grey for a prize
     competition; BBC /programmes — feeds decommissioned and the successor API is approval-gated.
     One closing sentence: we state this because the licence diligence is part of the product's
     trust story.

PART 2 — a single-line console footer attribution (must fit one line, small type):
  "Seeded with: 25k real incidents (UCI ServiceNow event log, CC BY 4.0) · real public runbooks
  (GitLab/K8s/CrowdStrike bulletin) · real UK programme metadata (TVmaze CC BY-SA / XMLTV) · real
  catalog rights data (CC0)" — adjust only if a licence in my notes contradicts it.

PART 3 — content for data/raw/SOURCES.md: a terse table (file-or-directory | source URL | licence
  | pulled/fetched date 2026-07-03) covering: uci/ (dataset #498), tvmaze/ (7-day GB schedule
  pull), freeview-epg/epg.xml (snapshot), kaggle/ (the two CSVs). One footer line: "See the
  README's Data provenance section for attribution and construction rules."

PART 4 — a "verification record" block: my notes from above, formatted as a checklist with today's
  date, suitable for pasting into a commit message.

Rules: do not invent licence terms beyond my notes and the attached plan; do not soften the
rejected-sources paragraph; keep the words "CC BY-SA", "CC BY 4.0", "CC0", "GPL-3.0" exactly;
never mention TMDB or BBC anywhere EXCEPT the rejected-sources paragraph.
```

Read the output against your own notes once — you are the human check that no licence got mangled.

## 4. Hand-back and what DONE looks like

- Email the single markdown document to **T3 by 15:30 Friday** as `licence-attribution.md`; WhatsApp "LICENCE PACKET SENT".
- T3 splits it: Part 1 → repo README; Part 2 → T2 (console footer, rendered verbatim); Part 3 → `data/raw/SOURCES.md`; Part 4 → the commit message.
- DONE checklist:
  - [ ] All six §2 verifications recorded with times; any MISMATCH escalated to T3 before writing.
  - [ ] TVmaze row includes the link-back AND the share-alike note on the committed derived data.
  - [ ] UCI citation is the UCI page's own text, not reconstructed.
  - [ ] Freeview-EPG carries the GPL-3.0 + "committed demo snapshot only, not redistributed as a product feed" note.
  - [ ] The TMDB-rejected sentence, the IMDb sentence, and the BBC sentence are present, in the rejected-sources paragraph only.
  - [ ] The rights-window rule is verbatim, ending "...only the window term is synthetic, and we say so."
  - [ ] No placeholder tokens; this packet has no waiting cells — it ships complete or not at all.

## 5. Fallbacks

- A licence page is down or changed: report to T3 with a screenshot; T3 decides (the team holds earlier same-day verification evidence — your note becomes "page unreachable at [time]; citing this morning's verification").
- Free-tier cap: this is a single bounded conversation — if it dies, T3 reruns the identical prompt on their own seat with your verification notes; the browser pass in §2 is yours alone and is already done.
- Squeezed: the non-negotiable core is Part 1 (README section) — the Fetch public-repo gate and the Conduct provenance beat both hang off it. Parts 2–4 can follow by 17:00 if needed; say so to T3 rather than rushing the licence table. Honest and late beats fast and wrong here — this is the one artifact where an error hands a judge a violation to find.
