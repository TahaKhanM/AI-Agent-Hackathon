# Rights DB — Kaggle streaming catalogues (manual-download fallback)

The rights DB source is two **CC0** Kaggle datasets. In the 2026-07-03 snapshot they were
fetched successfully via the Kaggle REST API and the CSVs are committed alongside this file
(`netflix_titles.csv`, `disney_plus_titles.csv`). This document exists so the sim's rights
loader has a **documented, reproducible fallback** if a future re-fetch cannot reach the API
(no credentials, rate-limited, or airplane mode).

## Datasets (both CC0 — public domain)

| Purpose | Kaggle slug | File after unzip |
|---|---|---|
| Netflix catalogue | `shivamb/netflix-shows` | `netflix_titles.csv` |
| Disney+ catalogue | `shivamb/disney-movies-and-tv-shows` | `disney_plus_titles.csv` |

## Option A — Kaggle REST API (what the snapshot used)

The API accepts the account API token as the basic-auth password (username may be empty):

```bash
# Token lives in .env as KAGGLE_API_TOKEN (do NOT commit or print it).
TOKEN=$(grep -E '^KAGGLE_API_TOKEN=' .env | head -1 | cut -d= -f2-)
mkdir -p data/raw/kaggle
curl -sL -u ":$TOKEN" \
  "https://www.kaggle.com/api/v1/datasets/download/shivamb/netflix-shows" \
  -o data/raw/kaggle/netflix.zip
curl -sL -u ":$TOKEN" \
  "https://www.kaggle.com/api/v1/datasets/download/shivamb/disney-movies-and-tv-shows" \
  -o data/raw/kaggle/disney.zip
(cd data/raw/kaggle && unzip -o netflix.zip && unzip -o disney.zip)
```

If `.env` instead provides `KAGGLE_USERNAME` + `KAGGLE_KEY` (legacy kaggle.json fields),
use `-u "$KAGGLE_USERNAME:$KAGGLE_KEY"` in place of `-u ":$TOKEN"`.

## Option B — Kaggle CLI

```bash
pip install kaggle            # CLI is NOT installed in this environment by default
# Place kaggle.json at ~/.kaggle/kaggle.json (chmod 600), then:
kaggle datasets download -d shivamb/netflix-shows -p data/raw/kaggle --unzip
kaggle datasets download -d shivamb/disney-movies-and-tv-shows -p data/raw/kaggle --unzip
```

## Option C — Manual browser download (no credentials)

1. Visit https://www.kaggle.com/datasets/shivamb/netflix-shows and click **Download**.
2. Visit https://www.kaggle.com/datasets/shivamb/disney-movies-and-tv-shows and click **Download**.
3. Unzip both into `data/raw/kaggle/` so you get `netflix_titles.csv` and `disney_plus_titles.csv`.

## Messiness rule (do NOT sanitise)

Keep the raw messiness — blank `director`/`country`/`cast`/`rating` cells, duplicate titles,
inconsistent `date_added` formatting. Those gaps are what trigger incidents in the sim and are
what the Conduct rubric rewards. Only licence-window **terms** are synthesised downstream, by the
rule in `Idea/refinement/01-realistic-data-plan.md` §2. Both CSVs are CC0, so redistribution in
this repo is permitted.
