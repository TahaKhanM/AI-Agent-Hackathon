# Data provenance & licences

**The systems are simulated; the content is real public data.** Precedent's MediaCo sim seeds from
committed public datasets under stated licences. Only licence-*window* terms in the rights DB are
synthesised, by the rule in `docs/idea/refinement/01-realistic-data-plan.md` §2. Source of truth for the
raw pull: `data/raw/SOURCES.md`.

## Provenance table

| Dataset | What it is | Licence | How Precedent uses it | Attribution |
|---|---|---|---|---|
| **UCI ServiceNow incident event log** (#498) | 141,712 events / 24,918 real incidents — the audit log of a real ServiceNow instance | **CC BY 4.0** | Day-one fix history + the scale artifact; the measured baseline (94.4% fix-class existence, 18.2 h **calendar** median for precedented repeats, 558 classes ≥4 occ = 94.8% of volume) | "Incident Management Process Enriched Event Log", UCI ML Repository #498, CC BY 4.0 |
| **TVmaze GB schedule** | Real UK broadcast schedule (programmes, slots, channels) | **CC BY-SA** | Seeds the scheduler/EPG programme metadata | Schedule data © TVmaze, CC BY-SA (`api.tvmaze.com`) |
| **Freeview-EPG (XMLTV)** | Backup UK EPG — real BBC/ITV/C4 rows (44,680 programme rows, 271 channels) | **GPL-3.0** (personal use) | Backup EPG rows for the publisher/scheduler sim | `github.com/dp247/Freeview-EPG`, GPL-3.0 |
| **Kaggle streaming catalogs** (Netflix + Disney+) | Real titles / regions / dates for the rights DB (8,807 + 1,450 rows) | **CC0** | Seeds the rights/VOD catalog; only the licence-*window* terms are synthesised, by a stated rule | `shivamb/netflix-shows` + `shivamb/disney-movies-and-tv-shows`, CC0 |
| **Published runbooks** (KB corpus) | ~10 KB articles, each adapted from a named public source | source-specific (see the KB integrity report) | The org's "documented fixes" Precedent retrieves | Each article carries its `adapted_from:` URL in front-matter |

## Rejected sources (the diligence is a credibility beat)

**TMDB and IMDb were checked and REJECTED on licence grounds** — TMDB's API terms prohibit AI/ML use,
and IMDb's data licence is incompatible with this use. They are never reintroduced as a data source,
in the runtime or on any slide. (Slide A2 / the deck's provenance strip state this explicitly.)

## The messiness is deliberate — the raw data keeps its nulls and duplicates

The Conduct rubric rewards realistic public data, so the committed raw snapshot is **not sanitised**
(verified against the committed files):

| File | Rows | Nulls / duplicates preserved |
|---|---|---|
| `data/raw/kaggle/netflix_titles.csv` | 8,807 | 2,634 blank `director`, 831 blank `country`, 1 duplicate title |
| `data/raw/kaggle/disney_plus_titles.csv` | 1,450 | 473 blank `director`, 219 blank `country` |
| `data/raw/freeview-epg.xml` — **removed 6 Jul 2026** (read by no loader; GPL-3.0 "personal use" licence unsuited to a public repo; recoverable from git history) | 44,680 programme rows across 271 channels | never used at runtime |

These nulls, duplicate titles, and fuzzy-match failures are what trigger the demo incidents and the
messy-ticket mutations — removing them would remove the realism the rubric rewards.
