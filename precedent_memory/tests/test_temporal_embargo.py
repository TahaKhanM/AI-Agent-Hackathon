"""B5 — temporal-embargo (unlock_at) predicate, oracle-graded (BUILD-PLAN §5 stretch 3).

A captured published-bonus challenge kept OFF the stage (a fifth on-stage policy concept
would dilute the two takeaway lines) and proven only here as a bench/oracle test + a
Q&A/README claim. The deterministic check gains an `unlock_at` predicate: a record published
with a FUTURE unlock_at is DENIED to everyone until then; once unlock_at passes, the normal
ACL resumes. Every case is GRADED by the INDEPENDENT oracle (oracle.py) — the compiler's
decision (retrieve.permitted, via check_access) must equal the oracle's, so this is a genuine
two-implementation cross-check, never self-grading. An embargo can only narrow access, never
widen it (fail-closed): it denies even a fully-cleared principal, and an unparseable stamp
stays embargoed. No schema change — unlock_at lives in the freeform record body JSON.
"""
from __future__ import annotations

from precedent_memory import retrieve, store
from precedent_memory.bench.oracle import oracle_allow


def _store(conn, fp, lineage, unlock_at=None):
    """Store a record; `unlock_at` is a RECORD-level attribute (like class_key/fingerprint),
    so it lands at the top level of the persisted body projection where the embargo predicate
    (compiler and oracle) reads it."""
    rec = {"kind": "kb_summary", "fingerprint": fp, "body": {"fix": "publish"}}
    if unlock_at is not None:
        rec["unlock_at"] = unlock_at
    return store.store(rec, lineage, conn=conn)


def _graded(conn, principal_ext, principal_ids, record_id):
    """Return (compiler_decision, oracle_decision) for one (principal, record). The oracle
    is the independent grader; the caller asserts they AGREE and match the expected verdict."""
    compiler, _owner = retrieve.check_access(conn, principal_ext, record_id, mode="live")
    oracle = oracle_allow(conn, record_id, principal_ids)
    return compiler, oracle


# --------------------------------------------------------------------------- #
# deny-before / allow-after on a PUBLIC record (the core stretch claim)
# --------------------------------------------------------------------------- #
def test_public_record_denied_before_unlock_and_allowed_after(scenario, iso):
    conn = scenario["conn"]

    # embargoed until 1h in the FUTURE -> denied to everyone (even nobody), oracle agrees
    future = _store(conn, "fp-embargo-future", ["kb:KB-0001"], unlock_at=iso(-3600))  # now + 1h
    compiler, oracle = _graded(conn, "nobody", set(), future)
    assert compiler is False and oracle is False        # deny-BEFORE, graded

    # a control published with unlock_at 1h in the PAST -> the embargo has lifted -> allowed
    past = _store(conn, "fp-embargo-past", ["kb:KB-0001"], unlock_at=iso(3600))       # now - 1h
    compiler, oracle = _graded(conn, "nobody", set(), past)
    assert compiler is True and oracle is True          # allow-AFTER, graded


# --------------------------------------------------------------------------- #
# an embargo trumps clearance: even a fully-cleared principal is denied until unlock
# --------------------------------------------------------------------------- #
def test_embargo_denies_even_fully_cleared_then_allows_after(scenario, iso):
    conn = scenario["conn"]
    rights = scenario["rights"]

    embargoed = _store(conn, "fp-embargo-rights", ["kb:KB-0004"],       # requires {rights}
                       unlock_at=iso(-3600))                            # future embargo
    compiler, oracle = _graded(conn, "rights_only", {rights}, embargoed)
    assert compiler is False and oracle is False        # embargo beats a valid clearance

    lifted = _store(conn, "fp-embargo-rights-lifted", ["kb:KB-0004"],
                    unlock_at=iso(3600))                                # past embargo
    compiler, oracle = _graded(conn, "rights_only", {rights}, lifted)
    assert compiler is True and oracle is True          # normal ACL resumes after unlock
    # ...and a principal WITHOUT the clearance is still denied once unlocked (ACL still bites)
    compiler2, oracle2 = _graded(conn, "sched_only", {scenario["sched"]}, lifted)
    assert compiler2 is False and oracle2 is False


# --------------------------------------------------------------------------- #
# control + fail-closed corner: no unlock_at means no embargo; a garbage stamp stays denied
# --------------------------------------------------------------------------- #
def test_no_unlock_at_is_not_embargoed_and_garbage_stays_closed(scenario, iso):
    conn = scenario["conn"]

    plain = _store(conn, "fp-no-embargo", ["kb:KB-0001"])   # no unlock_at at all
    compiler, oracle = _graded(conn, "nobody", set(), plain)
    assert compiler is True and oracle is True          # no unlock_at -> normal (public) allow

    # an unparseable unlock_at is treated as still-embargoed (fail-closed) by the predicate
    assert retrieve.embargoed("not-a-timestamp") is True
    assert retrieve.embargoed(None) is False
