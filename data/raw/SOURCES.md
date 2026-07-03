# Raw seed data — sources & pull instructions

> Landing zone for the committed raw public data the sim seeds from. **Commit the raw files here** (the live demo runs from the committed snapshot — airplane-mode rule). Full plan + licences: `Idea/refinement/01-realistic-data-plan.md`. Provenance/attribution table: `Plan/workflows/N1-licence-attribution.md`.

| Source | What | Licence | Pull |
|---|---|---|---|
| **TVmaze GB schedule** | Real UK broadcast schedule (programmes, slots, channels) | CC BY-SA | `GET https://api.tvmaze.com/schedule?country=GB&date=<YYYY-MM-DD>` for ~7 days → `data/raw/tvmaze/*.json` (no auth) |
| **Freeview-EPG XMLTV** | Backup UK EPG (real BBC/ITV/C4 rows) | GPL-3.0 (personal use) | `curl -o data/raw/freeview-epg.xml https://raw.githubusercontent.com/dp247/Freeview-EPG/master/epg.xml` |
| **Kaggle streaming catalogs** | Real titles/regions/dates for the rights DB (windows synthesised by a stated rule) | CC0 | Netflix (`shivamb/netflix-shows`) + Disney+ (`shivamb/disney-movies-and-tv-shows`) → `data/raw/kaggle/*.csv` (Kaggle CLI or manual download) |
| **UCI incident event log** | 141,712 events / 24,918 real incidents — day-one memory + the scale artifact | CC BY 4.0 | Already downloaded + analysed → `data/analysis/`. Raw CSV: `archive.ics.uci.edu/static/public/498/…zip` |

**Rules:** keep the real data's messiness (null metadata, duplicate titles) — it triggers incidents and is what the Conduct rubric rewards; do not sanitise. Only licence-window *terms* are synthesised, by the rule in `01-realistic-data-plan.md` §2 — say so in the README provenance table. TMDB and IMDb are **rejected on licence grounds** (TMDB's terms prohibit AI/ML use) — do not reintroduce them.

## Fetched snapshot (2026-07-03)

Committed raw snapshot the sim loads under airplane-mode. Record/byte counts are approximate and raw (messiness preserved — nulls, blanks, and duplicate titles left intact; not de-duplicated or cleaned).

| Source | File(s) written | Records | Bytes |
|---|---|---|---|
| **TVmaze GB schedule** | `data/raw/tvmaze/schedule-GB-2026-07-0{3..9}.json` (7 files) | 113 total (22 / 9 / 16 / 21 / 16 / 14 / 15 per day, 03→09 Jul) | ~218 KB (218,273 B) |
| **Freeview-EPG XMLTV** | `data/raw/freeview-epg.xml` | ~44,680 `<programme>` rows across 271 channels | ~20.0 MB (19,996,786 B) |
| **Kaggle — Netflix** | `data/raw/kaggle/netflix_titles.csv` (+ `netflix.zip`) | ~8,809 title rows (blank director on 2,634; blank country on 831) | CSV ~3.4 MB (3,399,671 B); zip 1,400,865 B |
| **Kaggle — Disney+** | `data/raw/kaggle/disney_plus_titles.csv` (+ `disney.zip`) | ~1,450 title rows (blank director on 473; blank country on 219) | CSV ~384 KB (383,571 B); zip 134,087 B |

**Fetch notes.** TVmaze: 7 consecutive GB days via the auth-free `/schedule` endpoint, all HTTP 200, JSON committed verbatim. Freeview: `epg.xml` from `dp247/Freeview-EPG@master`, HTTP 200. Kaggle: fetched via the REST API using `KAGGLE_API_TOKEN` from `.env` as the basic-auth password (`.env` had empty `KAGGLE_USERNAME`/`KAGGLE_KEY`; the token alone succeeded), both datasets are CC0. Manual/CLI fallback for the rights DB is documented in `data/raw/kaggle/RIGHTS-FALLBACK.md`. Licence table above is unchanged.
