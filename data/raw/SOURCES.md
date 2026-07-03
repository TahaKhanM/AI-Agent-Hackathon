# Raw seed data — sources & pull instructions

> Landing zone for the committed raw public data the sim seeds from. **Commit the raw files here** (the live demo runs from the committed snapshot — airplane-mode rule). Full plan + licences: `Idea/refinement/01-realistic-data-plan.md`. Provenance/attribution table: `Plan/workflows/N1-licence-attribution.md`.

| Source | What | Licence | Pull |
|---|---|---|---|
| **TVmaze GB schedule** | Real UK broadcast schedule (programmes, slots, channels) | CC BY-SA | `GET https://api.tvmaze.com/schedule?country=GB&date=<YYYY-MM-DD>` for ~7 days → `data/raw/tvmaze/*.json` (no auth) |
| **Freeview-EPG XMLTV** | Backup UK EPG (real BBC/ITV/C4 rows) | GPL-3.0 (personal use) | `curl -o data/raw/freeview-epg.xml https://raw.githubusercontent.com/dp247/Freeview-EPG/master/epg.xml` |
| **Kaggle streaming catalogs** | Real titles/regions/dates for the rights DB (windows synthesised by a stated rule) | CC0 | Netflix (`shivamb/netflix-shows`) + Disney+ (`shivamb/disney-movies-and-tv-shows`) → `data/raw/kaggle/*.csv` (Kaggle CLI or manual download) |
| **UCI incident event log** | 141,712 events / 24,918 real incidents — day-one memory + the scale artifact | CC BY 4.0 | Already downloaded + analysed → `data/analysis/`. Raw CSV: `archive.ics.uci.edu/static/public/498/…zip` |

**Rules:** keep the real data's messiness (null metadata, duplicate titles) — it triggers incidents and is what the Conduct rubric rewards; do not sanitise. Only licence-window *terms* are synthesised, by the rule in `01-realistic-data-plan.md` §2 — say so in the README provenance table. TMDB and IMDb are **rejected on licence grounds** (TMDB's terms prohibit AI/ML use) — do not reintroduce them.
