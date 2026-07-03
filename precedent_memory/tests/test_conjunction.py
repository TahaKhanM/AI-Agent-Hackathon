"""A-semantics: reading a derived artifact requires satisfying ALL source lineage
constraints (conjunction), NOT a single strictest label.

STARTER TEST SKELETON — written during planning so T2 begins from a RED test that
encodes the spec (Idea/refinement/02 §2.1, §2.4). Implement precedent_memory.store /
retrieve until these pass. The multi-source counterexample below is the exact case
that distinguishes conjunction (A) from strictest-label (B-naive) — it is incident 3.

Run: pytest precedent_memory/tests/test_conjunction.py
"""
import pytest

pytestmark = pytest.mark.skip(reason="STARTER SKELETON — remove skip when store/retrieve land")

# from precedent_memory import store, retrieve  # noqa: ERA001  (uncomment when implemented)


def test_multisource_conjunction_denies_partial_clearance():
    """The incident-3 case. A fix record derived from BOTH a rights-restricted KB
    article AND a scheduling-project ticket must be UNREADABLE to a rights-ops
    principal who lacks scheduling access — even though they satisfy one source.

    Strictest-label would WRONGLY allow this (rights label >= scheduling). Conjunction
    correctly denies. This test is the reason A beats strictest-label.
    """
    # rights_only principal satisfies constraint 'rights-ops' but NOT 'scheduling-ops'
    # record R has lineage {kb: rights-ops}, {ticket: scheduling-ops}
    # EXPECT: retrieve(rights_only, R) -> denied; retrieve(both_roles, R) -> allowed
    raise NotImplementedError


def test_public_lineage_is_readable_by_all():
    """A record whose lineage sources are all public (constraint_ids == []) is
    retrievable by any principal; effective_policy.is_restricted == 0."""
    raise NotImplementedError


def test_no_snippet_leaks_without_permitted():
    """Candidate generation (vector/BM25) may SURFACE a restricted record internally,
    but retrieve() must return neither its body, title, nor a snippet unless
    permitted() passes. Only the denied-count + owning-team may leak (documented
    disclosure, 02 §2.4)."""
    raise NotImplementedError
