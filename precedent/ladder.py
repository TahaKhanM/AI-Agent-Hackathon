"""Autonomy ladder: graduation, demotion, and the standing-approval fast-path.
[owner T1, task T1-9]

Spec: Idea/refinement/02-architecture-refinement.md §3.3.

- Reads/writes the EXISTING class_ladder table only (PK class_key; level in
  L0/L1/L2/STANDING; consecutive_verified; promoted_by; promoted_at). Writes the
  CANONICAL token 'STANDING' — never the display text "Standing Approval".
- Promotion eligibility: 3 CONSECUTIVE verified successes AT L2, zero rollbacks. Promotion
  itself is a HUMAN click — never automatic. A visible Revoke demotes instantly.
- Demotion: any verification failure or rollback -> level L1 IMMEDIATELY and the counter
  RESET to 0 (not decremented) + a class_demoted audit event.
- Anti-gaming (judge Q "file N synthetic easy tickets"): successes count only from
  monitored sources (sim/jira), each with a DISTINCT target object; N identical-object
  repeats within an hour count once. The schema is frozen, so this is enforced via the
  audit log (ladder_verify_counted markers), not new columns.
- Fast-path: is_standing() True -> the orchestrator skips ALL LLM calls.
- Terminology: the top level is "Standing Approval"; the DB token stays 'STANDING'.
"""
from __future__ import annotations

import json

from precedent_memory import audit, db

STANDING = "STANDING"
MONITORED_SOURCES = frozenset({"sim", "jira"})
_ANTI_GAMING_WINDOW_S = 3600
_ELIGIBLE_STREAK = 3


# --------------------------------------------------------------------------- #
# Reads
# --------------------------------------------------------------------------- #
def _row(conn, class_key: str):
    return conn.execute(
        "SELECT level, consecutive_verified, promoted_by, promoted_at "
        "FROM class_ladder WHERE class_key = ?", (class_key,)).fetchone()


def level_of(conn, class_key: str) -> str:
    row = _row(conn, class_key)
    return row["level"] if row else "L1"


def is_standing(class_key: str, *, conn) -> bool:
    """True iff the class is at Standing Approval. The zero-LLM fast-path gates on this."""
    row = _row(conn, class_key)
    return bool(row) and row["level"] == STANDING


def consecutive_verified(conn, class_key: str) -> int:
    row = _row(conn, class_key)
    return row["consecutive_verified"] if row else 0


def eligible(class_key: str, *, conn) -> bool:
    """Human-promotion eligibility: at L2 with >= 3 consecutive counted verifies."""
    row = _row(conn, class_key)
    return bool(row) and row["level"] == "L2" and row["consecutive_verified"] >= _ELIGIBLE_STREAK


# --------------------------------------------------------------------------- #
# Writes
# --------------------------------------------------------------------------- #
def _upsert(conn, class_key: str, *, level: str, count: int,
            promoted_by=None, promoted_at=None) -> None:
    conn.execute(
        "INSERT INTO class_ladder(class_key, level, consecutive_verified, promoted_by, "
        "promoted_at) VALUES(?,?,?,?,?) ON CONFLICT(class_key) DO UPDATE SET "
        "level=excluded.level, consecutive_verified=excluded.consecutive_verified, "
        "promoted_by=excluded.promoted_by, promoted_at=excluded.promoted_at",
        (class_key, level, count, promoted_by, promoted_at))


def _recently_counted(conn, class_key: str, target_ref: str) -> bool:
    """Anti-gaming: has an identical (class_key, target_ref) success already been counted
    within the window? Enforced over the append-only audit log (schema is frozen)."""
    if not target_ref:
        return False
    now = db.utcnow()
    for r in conn.execute(
        "SELECT ts, payload FROM audit_log WHERE event_type = 'ladder_verify_counted' "
        "ORDER BY seq DESC LIMIT 200").fetchall():
        try:
            p = json.loads(r["payload"] or "{}")
        except ValueError:
            continue
        if p.get("class_key") == class_key and p.get("target_ref") == target_ref:
            ts = db.parse_iso(r["ts"])
            if ts and (now - ts).total_seconds() <= _ANTI_GAMING_WINDOW_S:
                return True
    return False


def demote(class_key: str, *, conn, reason: str = "verification_failure",
           actor: str = "system") -> dict:
    """Immediate demotion to L1, counter reset to 0, class_demoted audit event."""
    _upsert(conn, class_key, level="L1", count=0)
    audit.audit("class_demoted", conn=conn, actor=actor, class_key=class_key, reason=reason)
    conn.commit()
    return {"class_key": class_key, "level": "L1", "demoted": True, "reason": reason}


def on_verification_result(class_key: str, verified: bool, rolled_back: bool, *,
                           conn, actor: str = "system", target_ref: str | None = None,
                           source: str = "sim") -> dict:
    """Advance the consecutive counter on a (counted) success; demote to L1 + audit on any
    failure or rollback (counter reset to 0). Returns a small dict for the trace."""
    if rolled_back or not verified:
        return demote(conn=conn, class_key=class_key,
                      reason="rollback" if rolled_back else "verification_failure", actor=actor)

    # Success — apply anti-gaming before counting.
    if source not in MONITORED_SOURCES:
        audit.audit("ladder_verify_skipped", conn=conn, actor=actor, class_key=class_key,
                    reason="unmonitored_source", source=source)
        conn.commit()
        return {"class_key": class_key, "counted": False, "reason": "unmonitored_source"}
    if _recently_counted(conn, class_key, target_ref or ""):
        audit.audit("ladder_verify_skipped", conn=conn, actor=actor, class_key=class_key,
                    reason="anti_gaming_repeat", target_ref=target_ref)
        conn.commit()
        return {"class_key": class_key, "counted": False, "reason": "anti_gaming_repeat"}

    row = _row(conn, class_key)
    level = row["level"] if row else "L1"
    count = row["consecutive_verified"] if row else 0
    if level == "L0":
        level, count = "L1", 0
    elif level == "L1":
        level, count = "L2", 0
    elif level == "L2":
        count += 1
    else:  # STANDING — stays; fast-path successes keep the class graduated
        count += 1
    _upsert(conn, class_key, level=level, count=count,
            promoted_by=row["promoted_by"] if row else None,
            promoted_at=row["promoted_at"] if row else None)
    audit.audit("ladder_verify_counted", conn=conn, actor=actor, class_key=class_key,
                target_ref=target_ref, level=level, consecutive_verified=count)
    conn.commit()
    return {"class_key": class_key, "counted": True, "level": level,
            "consecutive_verified": count, "eligible": eligible(class_key, conn=conn)}


def promote(class_key: str, principal: str, *, conn, force: bool = False) -> dict:
    """Human 'Promote to Standing Approval' click. Writes the canonical 'STANDING' token +
    promoting principal. Requires eligibility unless force=True (the demo pre-seed path)."""
    if not force and not eligible(class_key, conn=conn):
        return {"ok": False, "class_key": class_key, "level": level_of(conn, class_key),
                "reason": "not_eligible (need 3 consecutive verified at L2)"}
    ts = db.utcnow_iso()
    _upsert(conn, class_key, level=STANDING, count=consecutive_verified(conn, class_key),
            promoted_by=principal, promoted_at=ts)
    audit.audit("class_promoted", conn=conn, actor=principal, class_key=class_key,
                level=STANDING)
    conn.commit()
    return {"ok": True, "class_key": class_key, "level": STANDING, "promoted_by": principal}
