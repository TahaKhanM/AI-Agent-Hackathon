"""Fail-closed: when ACL freshness is uncertain, restricted records are DENIED.
A stale cache may narrow access, never widen it.

STARTER TEST SKELETON (02 §2.4-§2.5). Implement retrieve.stale() + permitted() to green.
"""
import pytest

pytestmark = pytest.mark.skip(reason="STARTER SKELETON — remove skip when retrieve.stale() lands")


def test_fallback_mode_denies_all_restricted():
    """In fallback mode (Jira unreachable), EVERY restricted record is denied,
    regardless of cached grant_bits. Public-lineage records remain retrievable."""
    raise NotImplementedError


def test_live_mode_denies_when_freshness_exceeds_window():
    """Live mode: a restricted record whose min_source_freshness is older than the
    60s window is denied with audit reason 'acl_freshness_uncertain'."""
    raise NotImplementedError


def test_stale_cache_never_widens_access():
    """Property: no combination of stale cache + fallback mode ever returns a record
    that a fresh check would have denied. (The inverse — denying something a fresh
    check would allow — is acceptable; fail-closed trades availability for safety.)"""
    raise NotImplementedError
