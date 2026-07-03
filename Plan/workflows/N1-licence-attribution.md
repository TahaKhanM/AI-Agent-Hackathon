# PACKET N1-LICENCE — Verify licences and write the attribution lines + README data-provenance table

> WHO RUNS THIS: **N1** — data + content lane. You have repo access and a capable AI coding tool (Claude Code / Codex-class). You do a browser-verification pass yourself, drive your AI tool against the data plan, and **commit the results directly** (branch/worktree → merge or PR per team convention).
> WHERE THIS FITS: **Phase 1 (foundations)**, alongside the data lane and before the repo goes public. This is a hard gate: the `## Data provenance` section must be in the README **before the repo is made public** — the Fetch public-repo gate and the gitleaks scrub both come after it, and the same text feeds the deck's provenance strip (slide A2). Land it early in foundations; don't let it slip toward the freeze.

---

## 0. What you are making and why it matters

Every byte of demo content is real public data, and saying so — with licences verified and two sources visibly REJECTED on licence grounds — is itself a scoring beat ("the diligence is the point"). You produce and commit four small text artifacts:

1. The repo README `## Data provenance` section (intro + table + three fixed paragraphs).
2. The console footer attribution one-liner (T2 renders it verbatim in the console — hand them the exact string).
3. The `data/raw/SOURCES.md` content (terse per-file table).
4. A verification record: you personally opened each licence page today and confirmed the wording — commit it in the commit message / a `data/raw/VERIFICATION.md`.

## 1. What you work from

Your source of truth is already in the repo:

| Repo path | Why |
|---|---|
| `Idea/refinement/01-realistic-data-plan.md` | The data plan — its §0 table, §2 construction rule, §3 honest framing, and §7 provenance text are canonical. Do not contradict it. |

## 2. The browser verification pass (do this FIRST, before you write anything)

Open each link below in your browser. For each, confirm the exact thing listed and note "VERIFIED [date/time]" or "MISMATCH: [what you saw]". A mismatch is escalated to the team immediately — never silently edit around one. This is the same-day re-check that the public pages still say what we cite. This pass is yours alone: your AI tool cannot browse these for you, and the human eyeball is the whole point.

| Source | URL | Confirm this |
|---|---|---|
| TVmaze API | https://www.tvmaze.com/api | Licence is **CC BY-SA**; attribution requirement = link back to TVmaze |
| UCI dataset #498 | https://archive.ics.uci.edu/dataset/498/incident+management+process+enriched+event+log | Licence badge says **CC BY 4.0**; copy the page's own "cite this dataset" text word-for-word into your notes (we use THEIR citation, never a reconstructed one) |
| Kaggle Netflix titles | https://www.kaggle.com/datasets/shivamb/netflix-shows | Licence shown is **CC0: Public Domain** |
| Kaggle Disney+ titles | https://www.kaggle.com/datasets/shivamb/disney-movies-and-tv-shows | Licence shown is **CC0: Public Domain** |
| Freeview-EPG repo | https://github.com/dp247/Freeview-EPG | Repo licence is **GPL-3.0**; note the "for personal use" wording if present |
| TMDB API terms | https://www.themoviedb.org/api-terms-of-use | The terms contain the prohibition on use in connection with **AI/ML applications** (this justifies our rejection sentence) |

Keep these notes — you paste them into your AI tool and into the verification record you commit.

## 3. Driving your AI tool

Point your tool at `Idea/refinement/01-realistic-data-plan.md` (sections 0, 2, 3, 7) and feed it your §2 verification notes. You know your tool; drive it however you like — the scaffold below is the *content spec*, not a script to paste verbatim. What matters is that the four parts come out exactly to spec and you verify each against your own notes before committing.

Prompt it with something like:

```
You are writing the data-licence and attribution text for a hackathon project README. The attached
data plan (Idea/refinement/01-realistic-data-plan.md, sections 0, 2, 3, 7) is the source of truth.
I have just re-verified each licence page in my browser; my notes:

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

Make your tool verify: the four caption/paragraph honesty rules hold ("25k real incidents", exact licence strings, TMDB/BBC only in the rejected paragraph, the rights-window sentence verbatim). Then read the output against your own notes once — **you are the human check that no licence got mangled.**

## 4. Committing and what DONE looks like

- Commit directly on a branch/worktree, then merge or open a PR per the team's convention. Split the artifact across its homes:
  - Part 1 → repo README `## Data provenance` section.
  - Part 2 → hand the exact one-liner to **T2** for the console footer (rendered verbatim); you can also drop it in a short `data/raw/FOOTER.md` so it's version-controlled.
  - Part 3 → `data/raw/SOURCES.md`.
  - Part 4 → the commit message and/or `data/raw/VERIFICATION.md`.
- DONE checklist:
  - [ ] All six §2 verifications recorded with date/time; any MISMATCH escalated to the team before writing.
  - [ ] TVmaze row includes the link-back AND the share-alike note on the committed derived data.
  - [ ] UCI citation is the UCI page's own text, not reconstructed.
  - [ ] Freeview-EPG carries the GPL-3.0 + "committed demo snapshot only, not redistributed as a product feed" note.
  - [ ] The TMDB-rejected sentence, the IMDb sentence, and the BBC sentence are present, in the rejected-sources paragraph only.
  - [ ] The rights-window rule is verbatim, ending "...only the window term is synthetic, and we say so."
  - [ ] No placeholder tokens (never ship a ‹XX›); no secrets in anything you commit.
  - [ ] The README `## Data provenance` section is merged **before** the repo goes public — flag T3 that the provenance gate is clear.

## 5. Fallbacks and honesty rules

- A licence page is down or changed: capture a screenshot, escalate to the team, and record the note as "page unreachable at [date/time]; citing today's verification." Never guess around a licence you couldn't confirm.
- The non-negotiable core is Part 1 (README section) — the Fetch public-repo gate and the provenance beat both hang off it, so it must land before the repo goes public. Parts 2–4 can follow shortly after if you're squeezed; flag the team rather than rushing the licence table. **Honest and slightly later beats fast and wrong here** — this is the one artifact where an error hands a judge a violation to find.
