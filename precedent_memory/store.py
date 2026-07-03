"""Write path: lineage capture + effective-policy compilation.  [owner T2, task T2-1]

Spec: Idea/refinement/02-architecture-refinement.md §2.3-§2.4.

On write we record the full SET of source lineage constraints, then compile the
effective_policy row = union of constraint-ids across ALL lineage sources
(conjunction, semantic rule A), stored as a bitmap (implementation B).
is_restricted = required_bits nonempty. A missing lineage source is created as an
"unverified" restricted source so an unknown provenance fails CLOSED, never open.

RULE 1/2: no model ids, no LLM imports here — deterministic storage only.
"""
from __future__ import annotations

import hashlib
import json

from precedent_memory import audit, db


# --------------------------------------------------------------------------- #
# Constraints & sources (the ACL surface the read path enforces)
# --------------------------------------------------------------------------- #
def ensure_constraint(conn, source_system: str, external_ref: str,
                      description: str | None = None) -> int:
    """Get-or-create a constraint_def; its id is the bit position. `description`
    doubles as the safe owner-team label surfaced on a denial."""
    row = conn.execute(
        "SELECT id, description FROM constraint_def WHERE source_system = ? AND external_ref = ?",
        (source_system, external_ref),
    ).fetchone()
    if row is not None:
        if description and not row["description"]:
            conn.execute("UPDATE constraint_def SET description = ? WHERE id = ?",
                         (description, row["id"]))
        return row["id"]
    cur = conn.execute(
        "INSERT INTO constraint_def(source_system, external_ref, description) VALUES(?,?,?)",
        (source_system, external_ref, description),
    )
    return cur.lastrowid


def put_principal(conn, external_id: str, constraint_ids=(), kind: str = "human") -> int:
    """Upsert a principal with a precomputed grant_bits bitmap (the B fast path)."""
    grant = db.bits_to_blob(db.ids_to_bits(constraint_ids))
    conn.execute(
        "INSERT INTO principal(external_id, kind, grant_bits) VALUES(?,?,?) "
        "ON CONFLICT(external_id) DO UPDATE SET kind=excluded.kind, grant_bits=excluded.grant_bits",
        (external_id, kind, grant),
    )
    return conn.execute("SELECT id FROM principal WHERE external_id = ?",
                        (external_id,)).fetchone()["id"]


def _unverified_constraint_id(conn) -> int:
    return ensure_constraint(conn, db.UNVERIFIED_SOURCE_SYSTEM, db.UNVERIFIED_SOURCE_REF,
                             "Unverified source — fail closed")


def source_id(conn, external_ref: str) -> int | None:
    row = conn.execute("SELECT id FROM acl_source WHERE external_ref = ?",
                       (external_ref,)).fetchone()
    return row["id"] if row else None


def put_source(conn, external_ref: str, constraint_ids=(), *,
               last_verified_at: str | None = None, revoked: int = 0) -> dict:
    """Upsert an acl_source. Idempotent: acl_version bumps ONLY when the ACL state
    (constraint set or revoked flag) actually changes; a plain freshness refresh
    does not. Returns {"id", "changed"} so the caller can fan out recompiles."""
    ids = sorted({int(c) for c in constraint_ids})
    if last_verified_at is None:
        last_verified_at = db.utcnow_iso()
    existing = conn.execute(
        "SELECT id, constraint_ids, revoked, acl_version FROM acl_source WHERE external_ref = ?",
        (external_ref,),
    ).fetchone()
    if existing is None:
        cur = conn.execute(
            "INSERT INTO acl_source(external_ref, constraint_ids, acl_version, "
            "last_verified_at, revoked) VALUES(?,?,?,?,?)",
            (external_ref, json.dumps(ids), 1, last_verified_at, int(revoked)),
        )
        return {"id": cur.lastrowid, "changed": True}

    old_ids = sorted(json.loads(existing["constraint_ids"] or "[]"))
    changed = old_ids != ids or int(existing["revoked"]) != int(revoked)
    new_version = existing["acl_version"] + 1 if changed else existing["acl_version"]
    conn.execute(
        "UPDATE acl_source SET constraint_ids = ?, revoked = ?, acl_version = ?, "
        "last_verified_at = ? WHERE id = ?",
        (json.dumps(ids), int(revoked), new_version, last_verified_at, existing["id"]),
    )
    return {"id": existing["id"], "changed": changed}


def _resolve_lineage_source(conn, ref: str) -> int:
    """Map a lineage external_ref to an acl_source id, creating an unverified
    (fail-closed) source if it is unknown."""
    sid = source_id(conn, ref)
    if sid is not None:
        return sid
    put_source(conn, ref, constraint_ids=[_unverified_constraint_id(conn)],
               last_verified_at=None)
    return source_id(conn, ref)


# --------------------------------------------------------------------------- #
# Effective-policy compilation (A via B)
# --------------------------------------------------------------------------- #
def compile_effective_policy(record_id: int, *, conn) -> None:
    """Recompute required_bits = union over ALL lineage sources; bump
    policy_version; set min_source_freshness (oldest source, None if any unknown);
    quarantine the record if any lineage source is revoked. Called on write and on
    every ACL sync."""
    sources = conn.execute(
        "SELECT s.constraint_ids, s.last_verified_at, s.revoked "
        "FROM lineage l JOIN acl_source s ON s.id = l.source_id WHERE l.record_id = ?",
        (record_id,),
    ).fetchall()

    required = 0
    freshness_dt = None
    freshness_str: str | None = None
    freshness_unknown = False
    any_revoked = False
    for s in sources:
        required |= db.ids_to_bits(json.loads(s["constraint_ids"] or "[]"))
        any_revoked = any_revoked or bool(s["revoked"])
        dt = db.parse_iso(s["last_verified_at"]) if s["last_verified_at"] else None
        if dt is None:
            freshness_unknown = True
        elif freshness_dt is None or dt < freshness_dt:
            freshness_dt, freshness_str = dt, s["last_verified_at"]
    # "" is the NOT-NULL sentinel for "freshness unknown" -> stale() treats it as
    # stale, so a restricted record with an unverifiable source fails closed.
    min_source_freshness = "" if (freshness_unknown or freshness_str is None) else freshness_str

    is_restricted = 1 if required != 0 else 0

    # Revocation -> quarantine; un-revocation restores an active record.
    status = conn.execute("SELECT status FROM memory_record WHERE id = ?",
                          (record_id,)).fetchone()["status"]
    if any_revoked and status == "active":
        conn.execute("UPDATE memory_record SET status = 'quarantined' WHERE id = ?", (record_id,))
    elif not any_revoked and status == "quarantined":
        conn.execute("UPDATE memory_record SET status = 'active' WHERE id = ?", (record_id,))

    prev = conn.execute("SELECT policy_version FROM effective_policy WHERE record_id = ?",
                        (record_id,)).fetchone()
    version = (prev["policy_version"] + 1) if prev else 1
    conn.execute(
        "INSERT INTO effective_policy(record_id, required_bits, is_restricted, "
        "policy_version, min_source_freshness, compiled_at) VALUES(?,?,?,?,?,?) "
        "ON CONFLICT(record_id) DO UPDATE SET required_bits=excluded.required_bits, "
        "is_restricted=excluded.is_restricted, policy_version=excluded.policy_version, "
        "min_source_freshness=excluded.min_source_freshness, compiled_at=excluded.compiled_at",
        (record_id, db.bits_to_blob(required), is_restricted, version,
         min_source_freshness, db.utcnow_iso()),
    )


def recompile_for_source(conn, sid: int) -> list[int]:
    """Revocation / ACL-flip fan-out: recompile every record derived from source
    `sid` (one indexed scan via idx_lineage_source). Returns affected record ids."""
    rows = conn.execute("SELECT record_id FROM lineage WHERE source_id = ?", (sid,)).fetchall()
    ids = [r["record_id"] for r in rows]
    for rid in ids:
        compile_effective_policy(rid, conn=conn)
    return ids


# --------------------------------------------------------------------------- #
# store()  — the public write entry point
# --------------------------------------------------------------------------- #
def store(record: dict, lineage: list[str], principal_ctx=None, *, conn) -> int:
    """Insert a memory_record + its lineage rows, compile the effective_policy
    bitmap, append an audit event. Returns the new record_id. Atomic."""
    if conn is None:
        raise ValueError("store() requires a conn (the caller owns the db handle)")
    kind = record.get("kind", "executed_fix")
    class_key = record.get("class_key")
    fingerprint = record.get("fingerprint")
    body = db.canonical_json(record)

    # Fail-closed on missing provenance for EVERY kind: a record with NO lineage
    # would otherwise compile to required_bits=0 (world-readable). Substitute an
    # unverified source so provenance-less content is denied until real lineage
    # lands. A genuinely PUBLIC record must carry a public lineage source
    # (constraint_ids == []), never an empty lineage list.
    effective_lineage = list(lineage or [])
    if not effective_lineage:
        effective_lineage = ["system:no-provenance"]

    with conn:  # single transaction across all tables
        cur = conn.execute(
            "INSERT INTO memory_record(kind, class_key, fingerprint, body, status) "
            "VALUES(?,?,?,?, 'active')",
            (kind, class_key, fingerprint, body),
        )
        record_id = cur.lastrowid
        for ref in effective_lineage:
            sid = _resolve_lineage_source(conn, ref)
            state = conn.execute(
                "SELECT constraint_ids, revoked FROM acl_source WHERE id = ?", (sid,)
            ).fetchone()
            content_hash = hashlib.sha256(
                db.canonical_json({"ref": ref, "c": json.loads(state["constraint_ids"] or "[]"),
                                   "r": state["revoked"]}).encode()
            ).hexdigest()
            conn.execute(
                "INSERT INTO lineage(record_id, source_id, source_content_hash) VALUES(?,?,?) "
                "ON CONFLICT(record_id, source_id) DO UPDATE "
                "SET source_content_hash=excluded.source_content_hash",
                (record_id, sid, content_hash),
            )
        compile_effective_policy(record_id, conn=conn)
        actor = principal_ctx.get("principal") if isinstance(principal_ctx, dict) else None
        audit.audit("memory_stored", conn=conn, actor=actor, record_id=record_id,
                    class_key=class_key, lineage_count=len(effective_lineage))
    return record_id


def store_memory_write(mw, principal_ctx=None, *, conn) -> int:
    """Adapter: persist a contracts.MemoryWrite (or any object/dict exposing the
    same fields — record, lineage_source_refs, class_key) WITHOUT changing the
    frozen contract. Maps class_key onto the record dict and lineage_source_refs
    onto store()'s lineage argument. This is the seam T1 uses to hand T2 a
    contract-shaped write instead of guessing store()'s positional layout."""
    def field(name):
        return mw.get(name) if isinstance(mw, dict) else getattr(mw, name, None)

    record = dict(field("record") or {})
    class_key = field("class_key")
    lineage = list(field("lineage_source_refs") or [])
    if class_key is not None:
        record.setdefault("class_key", class_key)
    return store(record, lineage, principal_ctx, conn=conn)
