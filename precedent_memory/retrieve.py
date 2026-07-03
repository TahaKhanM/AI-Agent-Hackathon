"""Deterministic retrieval path — A enforced via B.  [owner T2, task T2-1]

Spec: Idea/refinement/02-architecture-refinement.md §2.4.

RULE 2 — THIS FILE HAS ZERO LLM/MODEL IMPORTS. permitted() is one bitmask AND
over an indexed effective_policy row (the P99 story). Candidate generation is a
deterministic structured match (fingerprint / class_key equality) — never
semantic similarity — and NOTHING is returned (not a snippet, not a title) for a
record whose permitted() does not pass.

RULE 3 — fail-closed: if a restricted record's ACL freshness is uncertain
(fallback mode / stale / missing / revoked / no compiled policy), DENY. A stale
cache narrows access, never widens it.

TOCTOU: the policy_version is read, access is checked, the body is fetched, then
the policy_version is re-read; a mismatch triggers one recheck and otherwise a
deny. This bounds the check-then-fetch window.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from precedent.contracts import Hit, RetrievalBundle
from precedent_memory import audit, db


# --------------------------------------------------------------------------- #
# Decision inputs (pure data — no DB handles, so permitted() is trivially testable)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Principal:
    external_id: str
    grant_bits: int = 0
    kind: str = "human"


@dataclass(frozen=True)
class RecordPolicy:
    record_id: int
    is_restricted: bool
    required_bits: int
    min_source_freshness: str | None
    policy_version: int
    any_revoked: bool = False
    record_status: str = "active"
    has_policy: bool = True
    # True iff the record inherits the reserved "unverified provenance" constraint;
    # such a record is denied unconditionally, even to a principal that (wrongly)
    # holds that bit — the fail-closed guarantee is enforced, not a convention.
    has_unverified: bool = False
    # constraint ids the record requires, for safe owner-team disclosure only
    required_ids: tuple[int, ...] = field(default_factory=tuple)
    # Optional temporal embargo: a record published with a FUTURE unlock_at is withheld
    # from everyone until then (a captured published-bonus predicate; §5 stretch item 3).
    unlock_at: str | None = None


# --------------------------------------------------------------------------- #
# stale()  — the fail-closed freshness rule (§2.5)
# --------------------------------------------------------------------------- #
def stale(min_source_freshness: str | None, mode: str = "live") -> bool:
    """True when a restricted record's freshness cannot be trusted.

    - fallback mode (Jira unreachable): always stale -> every restricted record
      is denied. Public records never consult this function.
    - live mode: missing/unparseable timestamp -> stale; older than the 60s
      window -> stale; a future timestamp (clock skew) -> stale.
    """
    if mode != "live":
        return True
    ts = db.parse_iso(min_source_freshness) if min_source_freshness else None
    if ts is None:
        return True
    age = (db.utcnow() - ts).total_seconds()
    return age > db.FRESHNESS_WINDOW_SECONDS or age < 0


# --------------------------------------------------------------------------- #
# embargoed()  — the temporal-embargo predicate (§5 stretch item 3)
# --------------------------------------------------------------------------- #
def embargoed(unlock_at: str | None, now=None) -> bool:
    """True while a record is under a temporal embargo (now < unlock_at). Fail-closed:
    an unparseable unlock_at is treated as still-embargoed. A None unlock_at (the common
    case) means no embargo. An embargo can only NARROW access, never widen it."""
    if unlock_at is None:
        return False
    ts = db.parse_iso(unlock_at)
    if ts is None:
        return True
    return (now or db.utcnow()) < ts


def _unlock_at_of(body) -> str | None:
    """Extract an optional temporal-embargo timestamp from a record body (JSON text or
    dict). Absent/malformed -> None (no embargo)."""
    if not body:
        return None
    try:
        data = body if isinstance(body, dict) else json.loads(body)
    except (TypeError, ValueError):
        return None
    val = data.get("unlock_at") if isinstance(data, dict) else None
    return val if isinstance(val, str) else None


# --------------------------------------------------------------------------- #
# permitted()  — deterministic conjunction, fail-closed. NO LLM.
# --------------------------------------------------------------------------- #
def permitted(principal: Principal | None, record_policy: RecordPolicy | None,
              mode: str = "live") -> bool:
    """Deterministically decide if `principal` may read a record. Total and
    fail-closed: any missing input or uncertain state returns False."""
    if principal is None or record_policy is None:
        return False
    # No compiled policy at all -> we cannot prove safety -> deny.
    if not record_policy.has_policy:
        return False
    # Revoked lineage or a non-active record -> deny (fail closed).
    if record_policy.any_revoked or record_policy.record_status != "active":
        return False
    # Unverified provenance -> deny unconditionally (the sentinel bit is not a
    # satisfiable grant; it means "we cannot vouch for where this came from").
    if record_policy.has_unverified:
        return False
    # Temporal embargo -> denied to EVERYONE until unlock_at, even a fully-cleared
    # principal and even a public record (an embargo narrows, never widens; fail-closed).
    if embargoed(record_policy.unlock_at):
        return False
    # Public (unrestricted) records: readable by anyone, freshness irrelevant.
    if not record_policy.is_restricted:
        return True
    # Restricted: freshness must be trustworthy...
    if stale(record_policy.min_source_freshness, mode):
        return False
    # ...and the principal must satisfy ALL required constraints (conjunction).
    return db.is_superset(principal.grant_bits, record_policy.required_bits)


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #
def _load_principal(conn, principal: Principal | str) -> Principal | None:
    if isinstance(principal, Principal):
        return principal
    row = conn.execute(
        "SELECT external_id, kind, grant_bits FROM principal WHERE external_id = ?",
        (principal,),
    ).fetchone()
    if row is None:
        return None
    return Principal(row["external_id"], db.blob_to_bits(row["grant_bits"]), row["kind"])


def _build_policy(conn, record_id: int) -> RecordPolicy:
    """Assemble the RecordPolicy for one record from effective_policy + lineage.
    Missing policy row -> a maximally-restrictive, fail-closed policy."""
    ep = conn.execute(
        "SELECT required_bits, is_restricted, policy_version, min_source_freshness "
        "FROM effective_policy WHERE record_id = ?",
        (record_id,),
    ).fetchone()
    status_row = conn.execute(
        "SELECT status, body FROM memory_record WHERE id = ?", (record_id,)
    ).fetchone()
    status = status_row["status"] if status_row else "tombstoned"
    unlock_at = _unlock_at_of(status_row["body"]) if status_row else None
    any_revoked = conn.execute(
        "SELECT EXISTS(SELECT 1 FROM lineage l JOIN acl_source s ON s.id = l.source_id "
        "WHERE l.record_id = ? AND s.revoked = 1) AS r",
        (record_id,),
    ).fetchone()["r"]
    if ep is None:
        # No compiled policy -> treat as restricted + unknown freshness -> deny.
        return RecordPolicy(
            record_id=record_id, is_restricted=True, required_bits=0,
            min_source_freshness=None, policy_version=-1, any_revoked=bool(any_revoked),
            record_status=status, has_policy=False, unlock_at=unlock_at,
        )
    required_bits = db.blob_to_bits(ep["required_bits"])
    required_ids = tuple(db.bits_to_ids(required_bits))
    unv = conn.execute(
        "SELECT id FROM constraint_def WHERE source_system = ? AND external_ref = ?",
        (db.UNVERIFIED_SOURCE_SYSTEM, db.UNVERIFIED_SOURCE_REF),
    ).fetchone()
    has_unverified = bool(unv) and unv["id"] in required_ids
    return RecordPolicy(
        record_id=record_id,
        is_restricted=bool(ep["is_restricted"]),
        required_bits=required_bits,
        min_source_freshness=ep["min_source_freshness"],
        policy_version=ep["policy_version"],
        any_revoked=bool(any_revoked),
        record_status=status,
        has_policy=True,
        has_unverified=has_unverified,
        required_ids=required_ids,
        unlock_at=unlock_at,
    )


def _owner_team(conn, policy: RecordPolicy, principal: Principal) -> str | None:
    """Safe metadata only: the owning team of the first required constraint the
    principal does NOT satisfy. Never returns fix content, titles or snippets."""
    for cid in policy.required_ids:
        if not db.is_superset(principal.grant_bits, 1 << cid):
            row = conn.execute(
                "SELECT description FROM constraint_def WHERE id = ?", (cid,)
            ).fetchone()
            if row and row["description"]:
                return row["description"]
    return None


def check_access(conn, principal, record_id: int, mode: str = "live") -> tuple[bool, str | None]:
    """Non-auditing permission PROBE for view surfaces (e.g. the console's state
    panel). Returns (allowed, owner_team). owner_team is safe metadata only. The
    authoritative, audited decision is always made by retrieve()."""
    pr = _load_principal(conn, principal)
    policy = _build_policy(conn, record_id)
    allowed = permitted(pr, policy, mode)
    owner = None if (allowed or pr is None) else _owner_team(conn, policy, pr)
    return allowed, owner


def _policy_version(conn, record_id: int) -> int:
    row = conn.execute(
        "SELECT policy_version FROM effective_policy WHERE record_id = ?", (record_id,)
    ).fetchone()
    return row["policy_version"] if row else -1


# --------------------------------------------------------------------------- #
# retrieve()  — candidate-generate, permit-filter, redact denials
# --------------------------------------------------------------------------- #
def retrieve(principal, query, mode: str = "live", *, conn=None,
             actor: str | None = None, _probe=None) -> RetrievalBundle:
    """Return only permitted records; disclose denials as count + owner team only.

    `query` may be a dict {incident_id, class_key, fingerprint} or a bare string
    (matched against fingerprint or class_key). `principal` may be a Principal or
    a principal external_id string. `conn` is required (the library never opens a
    hidden global db for a real retrieval). `_probe` is a test-only hook invoked
    once after the first policy read to exercise the TOCTOU recheck.
    """
    if conn is None:
        raise ValueError("retrieve() requires a conn (the caller owns the db handle)")

    if isinstance(query, str):
        query = {"fingerprint": query, "class_key": query}
    incident_id = str(query.get("incident_id") or "")
    fingerprint = query.get("fingerprint")
    class_key = query.get("class_key")

    resolved = _load_principal(conn, principal)
    principal_id = resolved.external_id if resolved else (
        principal if isinstance(principal, str) else "unknown")

    # Deterministic candidate generation: structured equality only, no similarity.
    rows = conn.execute(
        "SELECT id, kind FROM memory_record "
        "WHERE (? IS NOT NULL AND fingerprint = ?) OR (? IS NOT NULL AND class_key = ?) "
        "ORDER BY id",
        (fingerprint, fingerprint, class_key, class_key),
    ).fetchall()

    hits: list[Hit] = []
    denied_count = 0
    denied_owner_team: str | None = None

    for row in rows:
        rid = row["id"]
        policy = _build_policy(conn, rid)
        v_before = policy.policy_version

        if _probe is not None:
            _probe(conn, rid)  # tests may flip the policy here (concurrent writer)

        allow = permitted(resolved, policy, mode)

        # TOCTOU guard: if the policy changed between check and fetch, recheck once.
        if allow:
            v_after = _policy_version(conn, rid)
            if v_after != v_before:
                policy = _build_policy(conn, rid)
                allow = permitted(resolved, policy, mode)

        if allow:
            hits.append(Hit(record_id=rid, kind=row["kind"] or "memory", score=1.0))
            audit.audit("retrieval_allowed", conn=conn, actor=principal_id,
                        record_id=rid, policy_version=policy.policy_version, mode=mode)
        else:
            denied_count += 1
            if denied_owner_team is None and resolved is not None:
                denied_owner_team = _owner_team(conn, policy, resolved)
            audit.audit("retrieval_denied", conn=conn, actor=principal_id,
                        record_id=rid, reason="acl_conjunction_or_freshness",
                        policy_version=policy.policy_version, mode=mode)

    # Commit the append-only audit rows so retrieval never holds a write lock on a
    # shared file db (each audit row is independent; nothing here needs atomicity).
    conn.commit()
    return RetrievalBundle(
        incident_id=incident_id,
        principal_id=principal_id,
        hits=hits,
        denied_count=denied_count,
        denied_owner_team=denied_owner_team,
    )
