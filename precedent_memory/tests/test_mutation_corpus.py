"""Seed-4207 mutation corpus invariants (T3-10) — the T1 hand-off contract."""
from __future__ import annotations

import re
from collections import Counter

from precedent_memory.bench.mutations import (
    CORPUS_PATH,
    N_MUTATIONS,
    corpus_bytes,
    generate_corpus,
    load_corpus,
)
from precedent_memory.bench.seed import CANONICAL_SEED

# Built from fragments so this detector file does not itself contain a literal closed-model
# token (which would trip check-open-weight / test_invariants_guard, as their own patterns do).
_VENDORS = ("claude", "openai", "gpt", "gemini", "grok", "mercury")
_CLOSED = re.compile("|".join(v + "-" for v in _VENDORS), re.I)


def test_corpus_is_byte_identical_across_runs():
    assert corpus_bytes(generate_corpus(CANONICAL_SEED)) == \
        corpus_bytes(generate_corpus(CANONICAL_SEED))


def test_committed_corpus_matches_generator():
    """The committed .jsonl must equal generate_corpus(4207) — else T1 loads a stale corpus."""
    assert corpus_bytes(load_corpus(CORPUS_PATH)) == corpus_bytes(generate_corpus(CANONICAL_SEED))


def test_size_and_taxonomy():
    corpus = generate_corpus(CANONICAL_SEED)
    assert len(corpus) == N_MUTATIONS == 100
    assert [r["id"] for r in corpus] == list(range(100))
    counts = Counter(r["mutation_type"] for r in corpus)
    assert set(counts) == {"typo", "colloquial", "dropped_code", "red_herring"}
    assert all(v > 0 for v in counts.values())


def test_every_record_carries_ground_truth_fields():
    for r in generate_corpus(CANONICAL_SEED):
        exp = r["expected"]
        assert set(exp) == {"service", "error_code", "target_object_type"}
        assert all(exp[k] for k in exp)
        assert isinstance(r["should_extract"], bool)


def test_red_herring_decoy_never_equals_the_truth():
    """A red-herring's decoy code must differ from the true code — otherwise 'extract the decoy'
    would not be a false fast-path."""
    for r in generate_corpus(CANONICAL_SEED):
        if r["mutation_type"] == "red_herring":
            assert r["red_herring_code"] and r["red_herring_code"] != r["expected"]["error_code"]


def test_corpus_has_no_closed_model_ids():
    """The open-weight guard does not scan this data file — assert it directly."""
    assert not _CLOSED.search(CORPUS_PATH.read_text())
