"""Hash-chained audit log.  [owner T2, task T2-1]

Spec: Idea/refinement/02-architecture-refinement.md §2.3.

Append-only; each row's hash = sha256(prev_hash || canonical(row fields)). Covers
retrievals, denials, sync events, executions, promotions/demotions. Tampering with,
removing, or reordering any row breaks verify_chain(). Callers must pass only SAFE
metadata as payload — never restricted fix content, never secrets.
"""
from __future__ import annotations

import hashlib

from precedent_memory import db


def _row_hash(prev_hash: str, ts: str, actor: str | None, event_type: str,
              payload_json: str) -> str:
    material = f"{prev_hash}|{ts}|{actor or ''}|{event_type}|{payload_json}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def audit(event_type: str, *, conn, actor: str | None = None, **payload) -> int:
    """Append a hash-chained row; return its seq. `payload` is safe metadata only."""
    if conn is None:
        raise ValueError("audit() requires a conn")
    last = conn.execute("SELECT hash FROM audit_log ORDER BY seq DESC LIMIT 1").fetchone()
    prev_hash = last["hash"] if last else db.GENESIS_HASH
    ts = db.utcnow_iso()
    payload_json = db.canonical_json(payload)
    h = _row_hash(prev_hash, ts, actor, event_type, payload_json)
    cur = conn.execute(
        "INSERT INTO audit_log(ts, actor, event_type, payload, prev_hash, hash) "
        "VALUES(?,?,?,?,?,?)",
        (ts, actor, event_type, payload_json, prev_hash, h),
    )
    return cur.lastrowid


def verify_chain(*, conn, expected_len: int | None = None,
                 expected_tail_hash: str | None = None) -> bool:
    """Recompute the chain end-to-end; True iff intact (no modification, or removal
    or reorder of an INTERIOR row).

    Honest limitation: a bare hash chain cannot detect deletion of the TAIL (the
    most-recent rows) on its own — every remaining prefix still verifies. To detect
    truncation, the caller remembers the length and/or the last hash and passes
    expected_len / expected_tail_hash; a mismatch then fails verification.
    """
    if conn is None:
        raise ValueError("verify_chain() requires a conn")
    rows = conn.execute(
        "SELECT ts, actor, event_type, payload, prev_hash, hash FROM audit_log ORDER BY seq ASC"
    ).fetchall()
    expected_prev = db.GENESIS_HASH
    for row in rows:
        if row["prev_hash"] != expected_prev:
            return False
        recomputed = _row_hash(row["prev_hash"], row["ts"], row["actor"],
                               row["event_type"], row["payload"])
        if recomputed != row["hash"]:
            return False
        expected_prev = row["hash"]
    if expected_len is not None and len(rows) != expected_len:
        return False
    if expected_tail_hash is not None:
        tail = rows[-1]["hash"] if rows else db.GENESIS_HASH
        if tail != expected_tail_hash:
            return False
    return True
