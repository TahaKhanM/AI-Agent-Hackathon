"""Concurrency: simultaneous ACL flips + retrievals never open a widened-access window.

STARTER TEST SKELETON (02 §2.5). This is the invariant the BasedAI judge asks for and
the one the README cites as the consistency story. Implement sync.py + retrieve.py to green.
"""
import pytest

pytestmark = pytest.mark.skip(reason="STARTER SKELETON — remove skip when sync + retrieve land")


def test_no_retrieval_returns_a_revoked_record():
    """Invariant: with N writer threads flipping ACLs on random sources and M reader
    threads retrieving as various principals, NO retrieval returns a record whose
    revocation committed (locally) before that retrieval's transaction began.

    Implementation: check + fetch happen in one SQLite transaction; the fetched row's
    policy_version is compared to the checked one; mismatch -> recheck (TOCTOU bound).
    """
    raise NotImplementedError


def test_revocation_fanout_hits_every_derived_record():
    """Revoking one acl_source invalidates every derived record, summary and embedding
    entry via idx_lineage_source in one indexed pass — asserted over a 100-record fan-in."""
    raise NotImplementedError


def test_idempotent_versioned_upserts():
    """Re-delivered / reordered ACL observations are harmless: digest compare-and-set
    means acl_version only advances on a real change; replaying the same observation
    twice is a no-op."""
    raise NotImplementedError
