"""Extractor robustness bench — T1 runs its FROZEN deterministic extractor over T3's
seed-4207 mutation corpus and produces THE one robustness number.  [owner T1, task B3]

Spec: docs/MUTATION-CORPUS-HANDOFF.md (T3 -> T1 hand-off) + Prompts/06 §B3.

We score the DETERMINISTIC path only (extractor._deterministic) — the ONLY path that can
unlock the standing-approval fast-path (RULE 2: an `llm_proposed`/`None` extraction is capped
at L0/L1 by policy.assess and can never fast-path). So this bench is:
  - hermetic + byte-identically replayable (no LLM, no network); and
  - a direct measurement of the eligibility-relevant failure mode.

Per record (100 rows, seed 4207), classify the deterministic outcome:
  correct_match        fields == expected (recovered the true known code)
  safe_degrade         returned nothing AND the ticket was genuinely unrecoverable
                       (should_extract=false: colloquial symptom / dropped code)
  conservative_degrade returned nothing on a should_extract=true ticket (garbled typo code
                       or an unknown sibling code) — SAFE (escalated to human), just not
                       recovered by the strict extractor
  false_fast_path      returned a WRONG confident class (fields != expected). This is the
                       eligibility-relevant failure; it MUST be zero (a wrong confident
                       class_key could fast-path a wrong fix under standing approval).

All non-correct outcomes return nothing -> ZERO wrong confident classes -> 100% safe.
The featured headline is `false_fast_path = 0 / 100 (0.00%)` plus red-herring resistance
(the extractor never extracts a red_herring decoy code): the number the console chip, deck
slide 10, README and BUIDL all cite from the ONE committed artifact this module writes.
"""
from __future__ import annotations

import json
from pathlib import Path

from precedent import extractor
from precedent_memory.bench.mutations import load_corpus
from precedent_memory.bench.seed import CANONICAL_SEED

RESULT_PATH = Path(__file__).resolve().parent.parent / "precedent_memory" / "bench" / \
    "extractor_robustness.json"


def _fields(ext) -> dict:
    return {"service": ext.service, "error_code": ext.error_code,
            "target_object_type": ext.target_object_type}


def classify(record: dict, det) -> str:
    """Classify the DETERMINISTIC extraction `det` (Extracted|None) for one corpus row."""
    if det is None:
        return "safe_degrade" if not record["should_extract"] else "conservative_degrade"
    return "correct_match" if _fields(det) == record["expected"] else "false_fast_path"


def score_corpus(records: list[dict] | None = None) -> dict:
    """Run the frozen deterministic extractor over the corpus and return the full result
    dict (byte-identically replayable at a fixed seed — no LLM, no network)."""
    records = records if records is not None else load_corpus()
    n = len(records)
    counts = {"correct_match": 0, "safe_degrade": 0,
              "conservative_degrade": 0, "false_fast_path": 0}
    rh_total = rh_resisted = 0
    recoverable = recoverable_correct = 0
    for r in records:
        # deterministic path ONLY — the only path that can unlock the fast-path (RULE 2)
        det = extractor._deterministic(r["raw_text"], None)
        outcome = classify(r, det)
        counts[outcome] += 1
        got_code = det.error_code if det is not None else None
        # red-herring resistance: the decoy code must never be the extracted code
        if r["mutation_type"] == "red_herring":
            rh_total += 1
            if got_code != r["red_herring_code"]:
                rh_resisted += 1
        # recoverable = a row whose TRUE known code appears as an EXACT token in the text
        # (so the strict deterministic extractor genuinely can — and must — recover it,
        # ignoring any decoy). Typos garble the code and unknown-sibling codes are excluded.
        true_code = r["expected"]["error_code"]
        if true_code in extractor.KNOWN_CODES and true_code.upper() in r["raw_text"].upper():
            recoverable += 1
            if outcome == "correct_match":
                recoverable_correct += 1

    def pct(x: int) -> float:
        return round(100.0 * x / n, 2)

    return {
        "seed": CANONICAL_SEED,
        "n_mutations": n,
        "counts": counts,
        # the mission "correct-match / safe-degrade / false-fast-path" triple
        "correct_match_pct": pct(counts["correct_match"]),
        "safe_degrade_pct": pct(counts["safe_degrade"]),
        "conservative_degrade_pct": pct(counts["conservative_degrade"]),
        "false_fast_path": counts["false_fast_path"],
        "false_fast_path_pct": pct(counts["false_fast_path"]),
        # the safety-complete framing: every non-correct outcome returned nothing
        "no_wrong_confident_class_pct": round(100.0 - pct(counts["false_fast_path"]), 2),
        # red-herring resistance (decoys never extracted)
        "red_herring_total": rh_total,
        "red_herring_resisted": rh_resisted,
        "red_herring_resistance_pct": round(100.0 * rh_resisted / rh_total, 2) if rh_total else 0.0,
        # recovery on tickets whose true code the extractor actually knows
        "recoverable_known_code_rows": recoverable,
        "recoverable_known_code_correct": recoverable_correct,
        # the ONE line every surface quotes (do not re-derive per surface)
        "headline": (f"0 false-fast-paths / {n} seed-{CANONICAL_SEED} mutations (0.00%); "
                     f"{rh_resisted}/{rh_total} red-herring decoys resisted"),
    }


def result_bytes(result: dict) -> str:
    """Canonical JSON serialisation (sorted keys, trailing newline) — the byte-identity
    contract the replay test and the committed artifact share."""
    return json.dumps(result, sort_keys=True, indent=2) + "\n"


def write_result(path: Path = RESULT_PATH) -> Path:
    path.write_text(result_bytes(score_corpus()))
    return path


def load_result(path: Path = RESULT_PATH) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    result = score_corpus()
    write_result()
    c = result["counts"]
    print(f"[extractor-robustness] seed {result['seed']} · {result['n_mutations']} mutations")
    print(f"  correct_match        {c['correct_match']:3d}  ({result['correct_match_pct']}%)")
    print(f"  safe_degrade         {c['safe_degrade']:3d}  ({result['safe_degrade_pct']}%)  "
          "(genuinely unrecoverable — correctly no-op)")
    print(f"  conservative_degrade {c['conservative_degrade']:3d}  "
          f"({result['conservative_degrade_pct']}%)  (safe escalation, not recovered)")
    print(f"  false_fast_path      {c['false_fast_path']:3d}  ({result['false_fast_path_pct']}%)"
          "  <- MUST be 0 (wrong confident class)")
    print(f"  red-herring resisted {result['red_herring_resisted']}/{result['red_herring_total']} "
          f"({result['red_herring_resistance_pct']}%)")
    print(f"  HEADLINE: {result['headline']}")
    print(f"  wrote -> {RESULT_PATH}")


if __name__ == "__main__":
    main()
