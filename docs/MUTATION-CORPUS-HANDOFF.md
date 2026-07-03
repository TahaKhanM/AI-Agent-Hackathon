# Extractor mutation corpus — T3 → T1 hand-off

**What:** a deterministic **100-mutation** corpus for T1's frozen deterministic extractor
robustness bench. Owner: T3 (produced). Consumer: T1 (runs the extractor over it, reports one
number). Seed: **4207** (`precedent_memory/bench/seed.py::CANONICAL_SEED`) — the same constant
that drives T1's incident generator. If the team overrides the seed at G0, T1 and T3 change
that one constant together and regenerate.

## Path & how to load

- Committed corpus: **`precedent_memory/bench/mutation_corpus.jsonl`**
- Generator: `precedent_memory/bench/mutations.py`
- Loader (import this):

  ```python
  from precedent_memory.bench.mutations import load_corpus
  corpus = load_corpus()            # -> list[dict], 100 records
  ```

- Regenerate / verify not stale: `python -m precedent_memory.bench.mutations` writes the file;
  `test_committed_corpus_matches_generator` (in `precedent_memory/tests/test_mutation_corpus.py`)
  fails if the committed bytes ever drift from `generate_corpus(4207)`.

## Record format (one JSON object per line)

| field | meaning |
|---|---|
| `id` | 0..99 |
| `mutation_type` | `typo` \| `colloquial` \| `dropped_code` \| `red_herring` (25 each) |
| `raw_text` | the messy incident text the extractor sees |
| `expected` | `{service, error_code, target_object_type}` — the TRUE incident (present on every row) |
| `should_extract` | `true` → a competent extractor is expected to recover it; `false` → recovery is not expected and **safe-degrade (return nothing) is the correct behaviour** |
| `red_herring_code` | for `red_herring` rows only: the decoy code that must **not** be extracted |

**Why fields, not a class_key string:** the two frozen sources disagree on casing
(`extractor.fingerprint()` uppercases; `console/demo_state` locks lowercase). Score on the three
**fields** (`service` / `error_code` / `target_object_type`) equality and the casing ambiguity
never bites.

## Scoring (compute in T1's bench)

For each record, run the extractor on `raw_text` and classify the outcome:

- **correct_match** — extractor's fields `== expected`.
- **safe_degrade** — extractor returns nothing (no confident extraction) **and** `should_extract` is `false`.
- **false_fast_path** — extractor returns fields `!= expected` (a *wrong, confident* class). This is
  the eligibility-relevant failure: a wrong class_key could fast-path a wrong fix under standing
  approval. **This count MUST be zero.**

Headline robustness number = `(correct_match + safe_degrade) / 100`, reported alongside the
explicit `false_fast_path` count (state it is zero). The trace should show the safe-degrade
reason ("error code not in known dictionary — escalating for human confirmation").

## The one number's four destinations

The single robustness number feeds, verbatim, all four surfaces:
1. the on-screen triage-trace **chip**,
2. **slide 10** of the deck,
3. the **README**,
4. the DoraHacks **BUIDL**.

One measured number, four surfaces — do not re-derive it per surface.
