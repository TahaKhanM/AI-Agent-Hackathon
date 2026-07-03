"""Fail-closed: when ACL freshness is uncertain, restricted records are DENIED.
A stale cache may narrow access, never widen it (02 §2.4-§2.5).
"""
from __future__ import annotations

from precedent_memory import retrieve, store


def _restricted_fix(conn, source_ref="jira:MEDIA-113", fp="fp-fc"):
    return store.store(
        {"kind": "executed_fix", "class_key": "sched|S-1|slot", "fingerprint": fp,
         "body": {"fix": "secret"}}, [source_ref], conn=conn,
    )


def test_fallback_mode_denies_all_restricted(scenario, iso):
    """In fallback mode EVERY restricted record is denied, regardless of cached
    grant_bits; public-lineage records remain retrievable."""
    conn = scenario["conn"]
    _restricted_fix(conn)                       # SCHED-restricted
    store.store({"fingerprint": "fp-pub", "body": {"fix": "x"}}, ["kb:KB-0001"], conn=conn)

    # authorised principal, fresh -> allowed live, denied in fallback
    q = {"fingerprint": "fp-fc"}
    assert retrieve.retrieve("sched_only", q, mode="live", conn=conn).hits
    assert retrieve.retrieve("sched_only", q, mode="fallback", conn=conn).hits == []
    # public still served in fallback
    assert retrieve.retrieve("nobody", {"fingerprint": "fp-pub"}, mode="fallback", conn=conn).hits


def test_live_mode_denies_when_freshness_exceeds_window(scenario, iso):
    """A restricted record whose min_source_freshness is older than the 60s window
    is denied in live mode, even for an authorised principal."""
    conn = scenario["conn"]
    # age the SCHED source well beyond the 60s window
    store.put_source(conn, "jira:MEDIA-113", [scenario["sched"]], last_verified_at=iso(120))
    _restricted_fix(conn)
    assert retrieve.retrieve("sched_only", {"fingerprint": "fp-fc"}, conn=conn).hits == []

    # refresh freshness -> now allowed (control)
    store.put_source(conn, "jira:MEDIA-113", [scenario["sched"]], last_verified_at=iso(1))
    store.recompile_for_source(conn, store.source_id(conn, "jira:MEDIA-113"))
    assert retrieve.retrieve("sched_only", {"fingerprint": "fp-fc"}, conn=conn).hits


def test_missing_freshness_denies_restricted(scenario):
    """A restricted source with an unverifiable last_verified_at is treated as
    stale (schema forbids NULL, so an empty/garbage timestamp is the 'unknown' case)."""
    conn = scenario["conn"]
    _restricted_fix(conn)
    conn.execute("UPDATE acl_source SET last_verified_at = '' WHERE external_ref = ?",
                 ("jira:MEDIA-113",))
    store.recompile_for_source(conn, store.source_id(conn, "jira:MEDIA-113"))
    assert retrieve.retrieve("sched_only", {"fingerprint": "fp-fc"}, conn=conn).hits == []


def test_revoked_source_denies_restricted(scenario):
    """Revoking a lineage source denies every derived record (fail closed)."""
    conn = scenario["conn"]
    _restricted_fix(conn)
    assert retrieve.retrieve("sched_only", {"fingerprint": "fp-fc"}, conn=conn).hits  # baseline

    store.put_source(conn, "jira:MEDIA-113", [scenario["sched"]], revoked=1)
    store.recompile_for_source(conn, store.source_id(conn, "jira:MEDIA-113"))
    assert retrieve.retrieve("sched_only", {"fingerprint": "fp-fc"}, conn=conn).hits == []


def test_executed_fix_without_lineage_fails_closed(scenario):
    """Defense-in-depth: an executed_fix stored with NO provenance must not become
    world-readable — it fails closed until real lineage lands."""
    conn = scenario["conn"]
    store.store({"kind": "executed_fix", "fingerprint": "fp-noprov",
                 "body": {"fix": "secret"}}, [], conn=conn)
    for principal in ("nobody", "rights_only", "sched_only", "both"):
        assert retrieve.retrieve(principal, {"fingerprint": "fp-noprov"}, conn=conn).hits == []


def test_stale_cache_never_widens_access(scenario, iso):
    """Property: the set of records allowed under any degraded mode is a SUBSET of
    what a fresh live check allows. Fail-closed trades availability for safety, so
    denying-something-fresh-would-allow is fine; the inverse must never happen."""
    conn = scenario["conn"]
    _restricted_fix(conn)  # SCHED-restricted, fresh

    fresh_allowed = bool(retrieve.retrieve("sched_only", {"fingerprint": "fp-fc"},
                                           mode="live", conn=conn).hits)
    assert fresh_allowed  # authorised + fresh

    # every degraded condition must be <= fresh_allowed for the AUTHORISED principal
    fallback = bool(retrieve.retrieve("sched_only", {"fingerprint": "fp-fc"},
                                      mode="fallback", conn=conn).hits)
    assert fallback is False  # narrowed, never widened

    # an UNAUTHORISED principal is denied in all modes, always
    for mode in ("live", "fallback"):
        assert retrieve.retrieve("rights_only", {"fingerprint": "fp-fc"},
                                 mode=mode, conn=conn).hits == []
