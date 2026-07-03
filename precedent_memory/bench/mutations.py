"""Seed-4207 extractor mutation corpus — T3 produces it, T1's extractor bench consumes it.
[owner T3, task T3-10]

Spec: Idea/refinement/02-architecture-refinement.md §3.2 (deterministic extractor) +
Prompts/03-ultracode-t1-completion.md §"Canonical G0 seed" / T1-6.

A deterministic 100-mutation corpus (typos, colloquial symptoms, dropped codes, red-herrings)
off CANONICAL_SEED. T1 runs its FROZEN deterministic extractor over it and reports ONE robustness
number (correct-match / safe-degrade / false-fast-path), which lands on the on-screen chip,
slide 10, the README, and the BUIDL.

Ground truth is the EXTRACTED FIELDS {service, error_code, target_object_type}, NOT a pre-cased
class_key string — the two frozen sources disagree on casing (extractor uppercases; the console
seed is lowercase), so scoring on fields sidesteps the ambiguity. Per record:

  id                 stable index
  mutation_type      typo | colloquial | dropped_code | red_herring
  raw_text           the messy incident text the extractor sees
  expected           {service, error_code, target_object_type} — the TRUE incident (always)
  should_extract     True  -> a competent deterministic extractor is expected to recover it
                     False -> recovery is not expected; SAFE-DEGRADE (return nothing) is correct
  red_herring_code   for red_herring rows: the decoy code that must NOT be extracted

Scoring (documented for T1, see MUTATION-CORPUS-HANDOFF.md):
  correct_match    extractor fields == expected            (any row)
  safe_degrade     extractor returns nothing AND not should_extract
  false_fast_path  extractor returns fields != expected     <-- the eligibility-relevant failure;
                   MUST be zero (a wrong confident class_key could fast-path a wrong fix).
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from precedent_memory.bench.seed import CANONICAL_SEED

CORPUS_PATH = Path(__file__).with_name("mutation_corpus.jsonl")
N_MUTATIONS = 100

# Base incidents — the 3 canonical class keys (anchored to console/demo_state) + a few plausible
# siblings for variety. Fields are lowercase-service / code-as-is / lowercase-object.
_BASE = (
    {"service": "publisher", "error_code": "PUB-4012", "target_object_type": "schedule_item",
     "clean": ("EPG publish job {code} failed — schedule_item metadata missing "
               "for {slot} on {chan}."),
     "colloquial": "The on-screen TV guide for {chan} is blank for {slot} — nothing's publishing.",
     "dropped": "EPG publish job failed again for {chan}; the {slot} listing never went out.",
     "herring": "SCH-DUP-002"},
    {"service": "scheduler", "error_code": "SCH-DUP-002", "target_object_type": "schedule_item",
     "clean": ("Scheduler raised {code}: duplicate schedule_item booked into the "
               "{slot} slot on {chan}."),
     "colloquial": "Two programmes are fighting over the same {slot} slot on {chan} again.",
     "dropped": "The scheduler double-booked the {slot} slot on {chan}; overlap not resolved.",
     "herring": "PUB-4012"},
    {"service": "rights", "error_code": "RGT-EXCL-009", "target_object_type": "vod_item",
     "clean": ("Rights engine {code}: vod_item exclusivity window conflict for "
               "'{title}' in {region}."),
     "colloquial": "'{title}' shouldn't be streamable in {region} right now — licence looks wrong.",
     "dropped": "'{title}' is up on VOD in {region} but the licence window seems off.",
     "herring": "RGT-WIN-011"},
    {"service": "publisher", "error_code": "PUB-4020", "target_object_type": "schedule_item",
     "clean": "Publisher {code}: schedule_item image asset failed validation for {slot} on {chan}.",
     "colloquial": "The programme artwork for {slot} on {chan} won't show on the guide.",
     "dropped": "Artwork for the {slot} listing on {chan} is missing from the published guide.",
     "herring": "PUB-4012"},
    {"service": "scheduler", "error_code": "SCH-GAP-005", "target_object_type": "schedule_item",
     "clean": "Scheduler {code}: schedule_item gap detected — {slot} on {chan} has no programme.",
     "colloquial": "There's a dead air gap around {slot} on {chan}, nothing scheduled.",
     "dropped": "A blank gap opened up at {slot} on {chan} with no programme booked.",
     "herring": "SCH-DUP-002"},
    {"service": "rights", "error_code": "RGT-WIN-011", "target_object_type": "vod_item",
     "clean": ("Rights {code}: vod_item availability window expired for '{title}' "
               "but still live in {region}."),
     "colloquial": "'{title}' is still watchable in {region} even though its window ended.",
     "dropped": "'{title}' should have come down in {region} but it's still on VOD.",
     "herring": "RGT-EXCL-009"},
)

_SLOTS = ("19:00", "20:00", "21:00", "22:30", "18:15")
_CHANS = ("Channel-1", "Channel-4-GB", "Freeview-7", "Regional-North", "Kids-2")
_TITLES = ("Northern Lights", "The Coast Road", "Quiz Night Live", "Harbour Town", "Midnight Line")
_REGIONS = ("GB", "GB-Scotland", "GB-Wales", "IE", "GB-North")

_CONFUSABLE = {"-": "_", "0": "O", "1": "l", "O": "0", "l": "1", "2": "Z"}


def _fill(rng, template: str) -> str:
    return template.format(
        code="{code}", slot=rng.choice(_SLOTS), chan=rng.choice(_CHANS),
        title=rng.choice(_TITLES), region=rng.choice(_REGIONS),
    )


def _typo_code(rng, code: str) -> str:
    """A MILD, recoverable corruption (separator/confusable swap) — a robust extractor with a
    canonicalisation table should still resolve it; a strict one safely degrades. Never mutates
    the code into a different VALID code."""
    chars = list(code)
    swappable = [i for i, ch in enumerate(chars) if ch in _CONFUSABLE]
    if swappable:
        i = rng.choice(swappable)
        chars[i] = _CONFUSABLE[chars[i]]
    return "".join(chars)


def _mutate(rng, base: dict, mtype: str) -> dict:
    expected = {"service": base["service"], "error_code": base["error_code"],
                "target_object_type": base["target_object_type"]}
    rec = {"mutation_type": mtype, "expected": expected, "red_herring_code": None}

    if mtype == "typo":
        text = _fill(rng, base["clean"]).replace("{code}", _typo_code(rng, base["error_code"]))
        rec.update(raw_text=text, should_extract=True)
    elif mtype == "colloquial":
        rec.update(raw_text=_fill(rng, base["colloquial"]), should_extract=False)
    elif mtype == "dropped_code":
        rec.update(raw_text=_fill(rng, base["dropped"]), should_extract=False)
    elif mtype == "red_herring":
        # the REAL code is present (structured) but a decoy code is name-dropped in prose.
        text = _fill(rng, base["clean"]).replace("{code}", base["error_code"])
        text += f" (NB: earlier alert mentioned {base['herring']} — unrelated, ignore.)"
        rec.update(raw_text=text, should_extract=True, red_herring_code=base["herring"])
    else:  # pragma: no cover
        raise AssertionError(mtype)
    return rec


def generate_corpus(seed: int = CANONICAL_SEED, n: int = N_MUTATIONS) -> list[dict]:
    """Total function of `seed`: a byte-identical 100-mutation corpus across runs."""
    rng = random.Random(seed)
    types = ("typo", "colloquial", "dropped_code", "red_herring")
    out = []
    for i in range(n):
        base = _BASE[i % len(_BASE)]
        mtype = types[i % len(types)]
        rec = _mutate(rng, base, mtype)
        rec["id"] = i
        out.append(rec)
    return out


def corpus_bytes(records: list[dict]) -> str:
    """Canonical JSONL serialisation (sorted keys) — the byte-identity contract."""
    return "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in records)


def write_corpus(path: Path = CORPUS_PATH, seed: int = CANONICAL_SEED) -> Path:
    path.write_text(corpus_bytes(generate_corpus(seed)))
    return path


def load_corpus(path: Path = CORPUS_PATH) -> list[dict]:
    """The loader T1's extractor bench imports: `from precedent_memory.bench.mutations import
    load_corpus`."""
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


if __name__ == "__main__":
    p = write_corpus()
    print(f"wrote {len(load_corpus(p))} mutations -> {p}")
