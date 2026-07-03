"""Chat-approval TTL table — the pending-approval ledger for the ASI:One gate.
[owner T1, task T1-8]

Spec: Idea/refinement/02 §3.4 (approval-via-ASI:One is a REAL gate).

When the Watcher presents an ApprovalRequest in chat, it records it here as PENDING
with a hard expiry (10-min TTL). The human's reply marks it approved/rejected; a
dropped or expired session is swept to 'expired'. This table is OWNED by T1 and
created at RUNTIME with CREATE TABLE IF NOT EXISTS — it deliberately does NOT touch
precedent_memory/schema.sql (T2's frozen schema).

Failure direction is ALWAYS non-action: an approval that is dropped, expired, or
simply absent NEVER executes. On reconnect the Watcher re-presents still-pending
requests (pending_for_sender) so the human can decide again — a lost message can
only cost a re-ask, never an unauthorised execution.
"""
from __future__ import annotations

from precedent.contracts import ApprovalRequest
from precedent_memory import db

_STATUS_PENDING = "pending"
_STATUS_EXPIRED = "expired"


def ensure_table(conn) -> None:
    """Create the approval ledger if absent (runtime-owned; not in schema.sql)."""
    conn.execute(
        "CREATE TABLE IF NOT EXISTS approval("
        "incident_id TEXT, plan_hash TEXT, sender_address TEXT, "
        "requested_at TEXT, expires_at TEXT, status TEXT, "
        "PRIMARY KEY(incident_id, plan_hash))"
    )
    conn.commit()


def record_pending(conn, req: ApprovalRequest, sender_address: str) -> None:
    """Insert (or refresh) a PENDING approval for this (incident, plan_hash)."""
    ensure_table(conn)
    conn.execute(
        "INSERT INTO approval(incident_id, plan_hash, sender_address, requested_at, "
        "expires_at, status) VALUES(?,?,?,?,?,?) "
        "ON CONFLICT(incident_id, plan_hash) DO UPDATE SET "
        "sender_address=excluded.sender_address, requested_at=excluded.requested_at, "
        "expires_at=excluded.expires_at, status=excluded.status",
        (req.incident_id, req.plan_hash, sender_address, req.requested_at,
         req.expires_at, _STATUS_PENDING),
    )
    conn.commit()


def lookup_pending(conn, incident_id: str):
    """Return the still-PENDING, non-expired approval row for an incident, or None.
    A row past its expiry is treated as absent (fail-closed — never returned as live)."""
    ensure_table(conn)
    row = conn.execute(
        "SELECT incident_id, plan_hash, sender_address, requested_at, expires_at, status "
        "FROM approval WHERE incident_id = ? AND status = ? "
        "ORDER BY requested_at DESC LIMIT 1",
        (incident_id, _STATUS_PENDING),
    ).fetchone()
    if row is None or is_expired(row):
        return None
    return row


def mark(conn, incident_id: str, plan_hash: str, status: str) -> None:
    """Set the terminal status ('approved'/'rejected'/'expired') for a pending row."""
    ensure_table(conn)
    conn.execute(
        "UPDATE approval SET status = ? WHERE incident_id = ? AND plan_hash = ?",
        (status, incident_id, plan_hash),
    )
    conn.commit()


def is_expired(row) -> bool:
    """True when the approval's expiry has passed (or is unparseable -> fail-closed)."""
    ts = db.parse_iso(row["expires_at"]) if row["expires_at"] else None
    if ts is None:
        return True
    return db.utcnow() >= ts


def expire_stale(conn) -> list:
    """Sweep: mark every still-PENDING row whose expiry has passed 'expired'. Returns
    the list of expired (incident_id, plan_hash) tuples. A dropped approval that ages
    out can therefore NEVER execute — the failure direction is non-action."""
    ensure_table(conn)
    rows = conn.execute(
        "SELECT incident_id, plan_hash, expires_at FROM approval WHERE status = ?",
        (_STATUS_PENDING,),
    ).fetchall()
    expired = []
    for row in rows:
        if is_expired(row):
            conn.execute(
                "UPDATE approval SET status = ? WHERE incident_id = ? AND plan_hash = ?",
                (_STATUS_EXPIRED, row["incident_id"], row["plan_hash"]),
            )
            expired.append((row["incident_id"], row["plan_hash"]))
    conn.commit()
    return expired


def pending_for_sender(conn, sender: str) -> list:
    """Still-pending, non-expired approvals for a sender — re-shown on reconnect so a
    dropped chat session re-presents the gate rather than silently losing it."""
    ensure_table(conn)
    rows = conn.execute(
        "SELECT incident_id, plan_hash, sender_address, requested_at, expires_at, status "
        "FROM approval WHERE sender_address = ? AND status = ? "
        "ORDER BY requested_at DESC",
        (sender, _STATUS_PENDING),
    ).fetchall()
    return [r for r in rows if not is_expired(r)]
