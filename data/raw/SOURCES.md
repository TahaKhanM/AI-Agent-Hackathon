# Raw seed data — sources & pull instructions

> Landing zone for the committed raw public data the sim seeds from. **Commit the raw files here** (the demo runs from the committed snapshot — airplane-mode rule). Full plan + licences: `docs/idea/refinement/01-realistic-data-plan.md`. Provenance table: `docs/data-provenance.md`.

| Source | What | Licence | Pull |
|---|---|---|---|
| **TVmaze GB schedule** | Real UK broadcast schedule (programmes, slots, channels) | CC BY-SA | `GET https://api.tvmaze.com/schedule?country=GB&date=<YYYY-MM-DD>` for ~7 days → `data/raw/tvmaze/*.json` (no auth) |
| **Kaggle streaming catalogs** | Real titles/regions/dates for the rights DB (windows synthesised by a stated rule) | CC0 | Netflix (`shivamb/netflix-shows`) + Disney+ (`shivamb/disney-movies-and-tv-shows`) → `data/raw/kaggle/*.csv` (Kaggle CLI or manual download) |
| **UCI incident event log** | 141,712 events / 24,918 real incidents — day-one memory + the scale artifact | CC BY 4.0 | Analysis results committed in `data/analysis/`. Raw CSV (44 MB, gitignored — needed only for `make bench-uci` / re-analysis): `archive.ics.uci.edu/static/public/498/…zip` → `data/raw/incident_event_log.csv` |

Removed 6 Jul 2026: `freeview-epg.xml` (Freeview-EPG XMLTV backup, GPL-3.0 "personal
use") — read by no loader, and its licence didn't suit redistribution in a public repo.
Recoverable from git history if ever needed; the TVmaze snapshot is the EPG source.

**Rules:** keep the real data's messiness (null metadata, duplicate titles) — it triggers incidents by design; do not sanitise. Only licence-window *terms* are synthesised, by the rule in `docs/idea/refinement/01-realistic-data-plan.md` §2 — say so in any provenance table. TMDB and IMDb are **rejected on licence grounds** (TMDB's terms prohibit AI/ML use) — do not reintroduce them.

## Fetched snapshot (2026-07-03)

Committed raw snapshot the sim loads under airplane-mode. Record/byte counts are approximate and raw (messiness preserved — nulls, blanks, and duplicate titles left intact; not de-duplicated or cleaned).

| Source | File(s) committed | Records | Bytes |
|---|---|---|---|
| **TVmaze GB schedule** | `data/raw/tvmaze/schedule-GB-2026-07-0{3..9}.json` (7 files) | 113 total (22 / 9 / 16 / 21 / 16 / 14 / 15 per day, 03→09 Jul) | ~218 KB |
| **Kaggle — Netflix** | `data/raw/kaggle/netflix_titles.csv` | ~8,809 title rows (blank director on 2,634; blank country on 831) | ~3.4 MB |
| **Kaggle — Disney+** | `data/raw/kaggle/disney_plus_titles.csv` | ~1,450 title rows (blank director on 473; blank country on 219) | ~384 KB |

**Fetch notes.** TVmaze: 7 consecutive GB days via the auth-free `/schedule` endpoint, all HTTP 200, JSON committed verbatim. Kaggle: fetched via the REST API (both datasets CC0); the original download zips are not kept in the repo. Manual/CLI fallback for the rights DB: `data/raw/kaggle/RIGHTS-FALLBACK.md`.
