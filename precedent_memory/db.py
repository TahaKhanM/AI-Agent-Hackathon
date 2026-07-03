"""Shared storage primitives for precedent_memory.  [owner T2]

One place for: SQLite connection setup against the canonical schema, the
constraint-bitmap encoding (the B fast-path), canonical JSON (for hashing and
digests) and UTC timestamps. Every T2 module (store/retrieve/audit/sync) imports
these helpers so the bit semantics can never diverge between the write path and
the read path.

RULE 1/2 reminder: this file contains NO model ids and NO LLM/model imports —
it is pure deterministic plumbing. Keep it that way.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

# Default freshness window for restricted records in live mode (02 §2.5).
FRESHNESS_WINDOW_SECONDS = 60

# Genesis link for the hash-chained audit log.
GENESIS_HASH = "0" * 64

# Reserved constraint used to fail a record CLOSED when a lineage source is
# unknown/unverified: no principal is ever granted this bit, so any record that
# inherits it is denied until a real sync clarifies the source.
UNVERIFIED_SOURCE_REF = "unverified-source"
UNVERIFIED_SOURCE_SYSTEM = "system"


# --------------------------------------------------------------------------- #
# Connections
# --------------------------------------------------------------------------- #
def connect(path: str | os.PathLike | None = None, *,
            check_same_thread: bool = True) -> sqlite3.Connection:
    """Open a SQLite connection with the canonical schema applied.

    path=None or ':memory:' gives an in-memory db (tests + demo default).
    Foreign keys on; Row factory so callers read columns by name.
    check_same_thread=False lets the console share one connection across the ASGI
    threadpool (the caller MUST serialise access with a lock).
    """
    if path is None:
        path = os.environ.get("PRECEDENT_MEMORY_DB", ":memory:")
    conn = sqlite3.connect(str(path), check_same_thread=check_same_thread)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    # WAL on a FILE db lets a T1 writer and the console reader share it without
    # "database is locked". :memory: does not support WAL.
    if str(path) != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 3000")
    conn.executescript(SCHEMA_PATH.read_text())
    return conn


# --------------------------------------------------------------------------- #
# Constraint bitmaps  (constraint_def.id == bit position; bit value == 1 << id)
# --------------------------------------------------------------------------- #
def ids_to_bits(ids) -> int:
    """Fold a set of constraint ids into an integer bitmap."""
    bits = 0
    for cid in ids or ():
        bits |= 1 << int(cid)
    return bits


def bits_to_ids(bits: int) -> list[int]:
    """Expand a bitmap back into a sorted list of constraint ids."""
    out, cid = [], 0
    while bits:
        if bits & 1:
            out.append(cid)
        bits >>= 1
        cid += 1
    return out


def bits_to_blob(bits: int) -> bytes:
    """Serialise a bitmap int to big-endian bytes for a BLOB column."""
    if bits <= 0:
        return b""
    return bits.to_bytes((bits.bit_length() + 7) // 8, "big")


def blob_to_bits(blob) -> int:
    """Deserialise a BLOB column back to a bitmap int. None/empty -> 0."""
    if not blob:
        return 0
    return int.from_bytes(bytes(blob), "big")


def is_superset(grant_bits: int, required_bits: int) -> bool:
    """Conjunction check: does the principal satisfy ALL required constraints?

    (grant & required) == required  — a single bitmask AND, sub-microsecond.
    An empty requirement (0) is satisfied by anyone.
    """
    return (grant_bits & required_bits) == required_bits


# --------------------------------------------------------------------------- #
# Canonical JSON + hashing input
# --------------------------------------------------------------------------- #
def canonical_json(obj) -> str:
    """Deterministic JSON: sorted keys, no whitespace. Used for digests, the
    audit hash chain, and lineage content hashes."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


# --------------------------------------------------------------------------- #
# Time
# --------------------------------------------------------------------------- #
def utcnow() -> datetime:
    return datetime.now(UTC)


def utcnow_iso() -> str:
    return utcnow().isoformat()


def parse_iso(ts: str) -> datetime | None:
    """Parse an ISO-8601 timestamp; return None if unparseable (caller treats
    None as 'freshness unknown' -> stale -> fail closed)."""
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt
