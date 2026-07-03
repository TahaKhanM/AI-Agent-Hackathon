"""A-semantics: reading a derived artifact requires satisfying ALL source lineage
constraints (conjunction), NOT a single strictest label.

Implemented against precedent_memory.store / retrieve (02 §2.1, §2.4). The
multi-source counterexample is the exact case that distinguishes conjunction (A)
from strictest-label — it is incident 3.

Run: pytest precedent_memory/tests/test_conjunction.py
"""
from __future__ import annotations

from precedent_memory import retrieve, store

SECRET = "SECRET-takedown-step-remove-title-42"


def _store_multisource_fix(conn):
    return store.store(
        {"kind": "executed_fix", "class_key": "rights|RGT-EXCL-009|vod_item",
         "fingerprint": "fp-rights", "body": {"fix": SECRET, "title": SECRET}},
        ["kb:KB-0004", "jira:MEDIA-113"], conn=conn,
    )


def test_multisource_conjunction_denies_partial_clearance(scenario):
    """The incident-3 case. A fix derived from BOTH a rights-restricted KB article
    AND a scheduling ticket must be UNREADABLE to a rights-ops principal who lacks
    scheduling access — even though they satisfy one source. Strictest-label would
    WRONGLY allow this; conjunction correctly denies."""
    conn = scenario["conn"]
    _store_multisource_fix(conn)

    denied = retrieve.retrieve("rights_only", {"fingerprint": "fp-rights"}, conn=conn)
    assert denied.hits == []
    assert denied.denied_count == 1
    # only safe metadata disclosed, and it names a team the principal actually lacks
    assert denied.denied_owner_team == "Scheduling Ops"
    # NO fix content leaks anywhere in the response
    assert SECRET not in denied.model_dump_json()

    sched_denied = retrieve.retrieve("sched_only", {"fingerprint": "fp-rights"}, conn=conn)
    assert sched_denied.hits == []
    assert sched_denied.denied_owner_team == "Rights Ops"
    assert SECRET not in sched_denied.model_dump_json()

    allowed = retrieve.retrieve("both", {"fingerprint": "fp-rights"}, conn=conn)
    assert [h.record_id for h in allowed.hits]  # a content-bearing hit
    assert allowed.denied_count == 0


def test_public_lineage_is_readable_by_all(scenario):
    """A record whose lineage sources are all public (constraint_ids == []) is
    retrievable by any principal; effective_policy.is_restricted == 0."""
    conn = scenario["conn"]
    rid = store.store(
        {"kind": "executed_fix", "class_key": "publisher|PUB-4012|schedule_item",
         "fingerprint": "fp-public", "body": {"fix": "republish epg"}},
        ["kb:KB-0001"], conn=conn,
    )
    ep = conn.execute("SELECT is_restricted FROM effective_policy WHERE record_id=?",
                      (rid,)).fetchone()
    assert ep["is_restricted"] == 0

    for principal in ("nobody", "rights_only", "sched_only", "both"):
        bundle = retrieve.retrieve(principal, {"fingerprint": "fp-public"}, conn=conn)
        assert [h.record_id for h in bundle.hits] == [rid]
        assert bundle.denied_count == 0


def test_no_snippet_leaks_without_permitted(scenario):
    """Candidate generation may SURFACE a restricted record internally, but
    retrieve() returns neither body, title nor snippet unless permitted() passes.
    Only denied-count + owning-team may leak (documented disclosure, 02 §2.4)."""
    conn = scenario["conn"]
    _store_multisource_fix(conn)
    bundle = retrieve.retrieve("nobody", {"fingerprint": "fp-rights"}, conn=conn)
    dumped = bundle.model_dump_json()
    assert SECRET not in dumped
    assert bundle.hits == []
    assert bundle.denied_count == 1
