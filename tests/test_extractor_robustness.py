"""B3 — extractor robustness bench: false-fast-path MUST be 0, replays byte-identically.

The frozen deterministic extractor is scored over the seed-4207 mutation corpus. The
eligibility-relevant invariant (RULE 2): NO mutation may produce a WRONG confident
(deterministic, fast-path-eligible) class — false_fast_path == 0. The result is the ONE
number the console chip, deck slide 10, README and BUIDL all cite; a committed
source-of-truth JSON is guarded here against drift so the four surfaces stay in lockstep.
"""
from __future__ import annotations

from precedent import extractor_robustness as er


def test_false_fast_path_is_zero():
    """No mutation produces a wrong confident class (an llm_proposed/None extraction can
    never unlock the fast-path; a deterministic extraction must never be wrong)."""
    result = er.score_corpus()
    assert result["false_fast_path"] == 0
    assert result["false_fast_path_pct"] == 0.0
    assert result["no_wrong_confident_class_pct"] == 100.0


def test_all_red_herring_decoys_resisted():
    """The extractor never extracts a red-herring decoy code (100% resistance)."""
    result = er.score_corpus()
    assert result["red_herring_resisted"] == result["red_herring_total"] == 25
    assert result["red_herring_resistance_pct"] == 100.0


def test_counts_sum_to_corpus_size_and_recoverable_all_correct():
    result = er.score_corpus()
    c = result["counts"]
    assert sum(c.values()) == result["n_mutations"] == 100
    # every ticket whose TRUE code the extractor actually knows is recovered correctly
    assert result["recoverable_known_code_correct"] == result["recoverable_known_code_rows"]


def test_replays_byte_identically_at_seed_4207():
    a = er.result_bytes(er.score_corpus())
    b = er.result_bytes(er.score_corpus())
    assert a == b, "robustness result must be byte-identical across runs (no LLM, no network)"


def test_committed_result_matches_fresh_run():
    """The committed source-of-truth JSON must equal a fresh run — else a surface could
    cite a stale robustness number. Regenerate with `make bench-extractor` if this fails."""
    committed = er.load_result()
    fresh = er.score_corpus()
    assert committed == fresh, (
        "committed extractor_robustness.json is stale — run `make bench-extractor`")
    assert committed["seed"] == 4207
