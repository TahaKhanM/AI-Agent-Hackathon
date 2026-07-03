"""INDEPENDENT ORACLE for the permission-aware memory conformance bench.

This module is a SEPARATE, from-scratch reimplementation of the ACL allow/deny
decision. It exists solely so that grading the product's compiler (retrieve.py /
store.py) against it is a genuine TWO-implementation cross-check, never self-grading.

Independence contract (do not weaken):
  * It reads the RAW acl_source tables (constraint_ids JSON, revoked,
    last_verified_at) and decides with PLAIN PYTHON SETS.
  * It imports neither `store` nor `retrieve`; it never touches the compiled
    `effective_policy` table, `memory_record`'s bitmap, or `principal.grant_bits`;
    it calls none of is_superset / ids_to_bits / bits_to_ids / blob_to_bits.
  * The only product code it borrows is a handful of pure constants/helpers from
    `db` (parse_iso, FRESHNESS_WINDOW_SECONDS, the UNVERIFIED sentinel refs,
    utcnow) — none of which encode the allow/deny decision.

Because the two implementations share no decision code, the bench's
  FNR = (oracle DENY, compiler ALLOW)   -- a leak: compiler over-serves
  FPR = (oracle ALLOW, compiler DENY)   -- an outage: compiler under-serves
are a real independent cross-check, not a tautology.
"""
from __future__ import annotations

import json

from precedent_memory import db


def _embargo_until(body):
    """Parse an optional temporal-embargo (unlock_at) timestamp from a raw record body.
    Recomputed independently of the compiler — reads raw JSON, decides with plain data."""
    if not body:
        return None
    try:
        data = body if isinstance(body, dict) else json.loads(body)
    except (TypeError, ValueError):
        return None
    if not isinstance(data, dict) or not data.get("unlock_at"):
        return None
    return db.parse_iso(data["unlock_at"])


def oracle_allow(conn, record_id, principal_constraint_ids, *, mode="live", now=None) -> bool:
    """Return True iff the principal may read record_id, decided from raw ACL rows.

    principal_constraint_ids is the principal's GRANTED constraint-id set, passed
    in as plain data (never read from the DB bitmap). Every branch below fails
    CLOSED: when anything about provenance, freshness or clearance is uncertain we
    deny, because for the enterprise buyer a leak is worse than an outage.
    """
    now = now or db.utcnow()
    principal = set(principal_constraint_ids)

    # 1. STATUS. A quarantined/tombstoned (or missing) record is never served —
    #    its content is under active dispute or has been retracted.
    row = conn.execute(
        "SELECT status, body FROM memory_record WHERE id=?", (record_id,)
    ).fetchone()
    if row is None or row["status"] != "active":
        return False

    # 1b. TEMPORAL EMBARGO. A record published with a FUTURE unlock_at is withheld from
    #     everyone until then — even a fully-cleared principal, even a public record. An
    #     embargo can only narrow access, never widen it (an unparseable stamp => still
    #     embargoed => deny). Recomputed here from the raw record body, independently.
    embargo = _embargo_until(row["body"])
    if embargo is not None and now < embargo:
        return False

    # 2. LINEAGE. Pull every source feeding this record. No lineage => provenance
    #    is unknown, so we cannot vouch for the ACL at all => fail closed.
    sources = conn.execute(
        "SELECT s.constraint_ids, s.revoked, s.last_verified_at "
        "FROM lineage l JOIN acl_source s ON s.id = l.source_id "
        "WHERE l.record_id = ?",
        (record_id,),
    ).fetchall()
    if not sources:
        return False

    # 3. REVOKED. If ANY contributing source has been revoked, the whole derived
    #    record is denied — revocation of one input taints the derivative.
    if any(s["revoked"] for s in sources):
        return False

    # 4. REQUIRED = union of the constraint ids across ALL sources (conjunction /
    #    A-semantics: a derived record inherits every input's restrictions).
    required: set[int] = set()
    for s in sources:
        required.update(json.loads(s["constraint_ids"] or "[]"))

    # 5. UNVERIFIED sentinel. A source whose provenance could not be vouched for is
    #    tagged with a reserved constraint that NO principal is ever granted. If a
    #    record inherits it, deny unconditionally — even a fully-cleared principal.
    sentinel = conn.execute(
        "SELECT id FROM constraint_def WHERE source_system=? AND external_ref=?",
        (db.UNVERIFIED_SOURCE_SYSTEM, db.UNVERIFIED_SOURCE_REF),
    ).fetchone()
    if sentinel is not None and sentinel["id"] in required:
        return False

    # 6. PUBLIC. No constraints required => readable by anyone. Public records are
    #    never freshness-gated (steps 1 & 3 already excluded revoked/inactive ones).
    if not required:
        return True

    # 7. FALLBACK. Restricted record + permission source unreachable => we cannot
    #    confirm freshness, so deny every restricted record in a degraded mode.
    if mode != "live":
        return False

    # 8. FRESHNESS (restricted, live only). Find the OLDEST last_verified_at across
    #    all sources. Any missing/unparseable timestamp is 'freshness unknown' =>
    #    stale => deny. A stale cache may narrow access, never widen it.
    oldest = None
    for s in sources:
        dt = db.parse_iso(s["last_verified_at"]) if s["last_verified_at"] else None
        if dt is None:
            return False
        if oldest is None or dt < oldest:
            oldest = dt
    if oldest is None:
        return False
    age = (now - oldest).total_seconds()
    if age > db.FRESHNESS_WINDOW_SECONDS or age < 0:  # stale, or future/clock-skew
        return False

    # 9. CONJUNCTION. Allow iff the principal holds EVERY required constraint.
    return required <= principal
