"""Build/reset orchestration + object health, typed-tool execution, verify, restore.

This is the dumb-infrastructure core. It stores operational objects and applies TYPED
fixes toward a healthy state. There is NO permission / risk / ACL / LLM logic here — the
orchestrator decides *whether* to call these; the sim only stores and mutates.
"""
from __future__ import annotations

import json
import sqlite3
import time
from datetime import datetime

from sim import db, incidents, loaders


# --------------------------------------------------------------------------- #
# Build / reset
# --------------------------------------------------------------------------- #
def build_sim(conn: sqlite3.Connection) -> None:
    """Idempotent: create tables then load. Safe to call on a fresh or existing DB."""
    db.create_tables(conn)
    # Only load if empty (idempotent — a second call is a no-op on a seeded DB).
    already = conn.execute("SELECT COUNT(*) FROM channel").fetchone()[0]
    if already:
        return
    loaders.load_tvmaze(conn)
    loaders.load_kaggle(conn)
    loaders.load_kb(conn)
    incidents.seed_incidents(conn)
    conn.commit()


def reset(conn: sqlite3.Connection) -> None:
    """DROP + rebuild (< 30s)."""
    db.drop_tables(conn)
    db.create_tables(conn)
    loaders.load_tvmaze(conn)
    loaders.load_kaggle(conn)
    loaders.load_kb(conn)
    incidents.seed_incidents(conn)
    conn.commit()


# --------------------------------------------------------------------------- #
# Object lookup + health
# --------------------------------------------------------------------------- #
# Map (service, object_type) -> the table and healthiness rule. Kept dumb and explicit.
def _fetch_object(conn: sqlite3.Connection, object_type: str, object_id: str) -> dict | None:
    table = _TABLE_FOR.get(object_type)
    if table is None:
        return None
    try:
        row = conn.execute(
            f"SELECT * FROM {table} WHERE id = ?", (object_id,)
        ).fetchone()
    except (sqlite3.OperationalError, ValueError):
        return None
    if row is None:
        return None
    return dict(row)


_TABLE_FOR = {
    "schedule_item": "schedule_slot",
    "vod_item": "vod_item",
}


def _epg_for_slot(conn: sqlite3.Connection, slot_id) -> dict | None:
    row = conn.execute(
        "SELECT * FROM epg_payload WHERE schedule_slot_id = ? ORDER BY id LIMIT 1",
        (slot_id,),
    ).fetchone()
    return dict(row) if row else None


def object_fields(conn: sqlite3.Connection, object_type: str, object_id: str) -> dict | None:
    """Return all columns of the object (plus, for schedule_item, its epg flags)."""
    obj = _fetch_object(conn, object_type, object_id)
    if obj is None:
        return None
    if object_type == "schedule_item":
        epg = _epg_for_slot(conn, obj["id"])
        if epg is not None:
            obj["epg_payload_id"] = epg["id"]
            obj["missing_metadata"] = epg["missing_metadata"]
            obj["xmltv"] = epg["xmltv"]
    return obj


def is_healthy(conn: sqlite3.Connection, object_type: str, object_id: str) -> bool:
    """Deterministic health predicate per object type. Dumb infrastructure rules:
    - schedule_item: healthy when its EPG payload has no missing metadata AND it does
      not overlap another slot.
    - vod_item: healthy when NOT (live=1 and window_end in the past)."""
    obj = _fetch_object(conn, object_type, object_id)
    if obj is None:
        return False
    if object_type == "schedule_item":
        if obj.get("has_overlap"):
            return False
        epg = _epg_for_slot(conn, obj["id"])
        if epg is not None and epg["missing_metadata"]:
            return False
        return True
    if object_type == "vod_item":
        if obj.get("live"):
            end = obj.get("availability_window_end")
            if end and _is_past(end):
                return False
        return True
    return False


def _is_past(date_str: str) -> bool:
    try:
        end = datetime.strptime(date_str[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return False
    return end < datetime(2026, 7, 3)


# --------------------------------------------------------------------------- #
# Typed-tool execution — the ONLY way state mutates toward healthy.
# --------------------------------------------------------------------------- #
def execute(conn: sqlite3.Connection, tool: str, args: dict) -> dict:
    """Apply a typed fix. Returns {ok, object_ref, detail}."""
    if tool == "republish_epg":
        return _republish_epg(conn, args)
    if tool == "dedupe_slot":
        return _dedupe_slot(conn, args)
    if tool == "rights_takedown":
        return _rights_takedown(conn, args)
    return {
        "ok": False,
        "object_ref": None,
        "detail": f"unknown tool '{tool}'",
    }


def _republish_epg(conn: sqlite3.Connection, args: dict) -> dict:
    slot_id = args.get("schedule_slot_id")
    slot = conn.execute("SELECT * FROM schedule_slot WHERE id = ?", (slot_id,)).fetchone()
    if slot is None:
        return {"ok": False, "object_ref": None, "detail": f"no schedule_slot {slot_id}"}
    # Fill missing metadata: backfill season/number/runtime and a synopsis, then
    # republish the EPG payload (missing_metadata -> 0).
    prog = conn.execute(
        "SELECT * FROM programme WHERE id = ?", (slot["programme_id"],)
    ).fetchone()
    summary = (prog["summary"] if prog and prog["summary"] else "Synopsis backfilled by ops.")
    season = slot["season"] if slot["season"] is not None else 2026
    number = slot["number"] if slot["number"] is not None else 1
    runtime = slot["runtime"] if slot["runtime"] is not None else 30
    conn.execute(
        "UPDATE schedule_slot SET season = ?, number = ?, runtime = ? WHERE id = ?",
        (season, number, runtime, slot_id),
    )
    name = prog["name"] if prog else "Programme"
    xmltv = (
        f'<programme channel="{slot["channel_id"]}">'
        f"<title>{name}</title><desc>{summary}</desc></programme>"
    )
    conn.execute(
        "UPDATE epg_payload SET missing_metadata = 0, xmltv = ? WHERE schedule_slot_id = ?",
        (xmltv, slot_id),
    )
    conn.commit()
    return {
        "ok": True,
        "object_ref": {"service": "publisher", "object_type": "schedule_item",
                       "object_id": str(slot_id)},
        "detail": "republished EPG with backfilled metadata",
    }


def _dedupe_slot(conn: sqlite3.Connection, args: dict) -> dict:
    slot_id = args.get("schedule_slot_id")
    slot = conn.execute("SELECT * FROM schedule_slot WHERE id = ?", (slot_id,)).fetchone()
    if slot is None:
        return {"ok": False, "object_ref": None, "detail": f"no schedule_slot {slot_id}"}
    # Remove the overlap on the duplicate; also clear any sibling that overlapped it at
    # the same channel/airstamp (so the pair is resolved).
    conn.execute("UPDATE schedule_slot SET has_overlap = 0 WHERE id = ?", (slot_id,))
    conn.execute(
        "UPDATE schedule_slot SET has_overlap = 0 "
        "WHERE channel_id = ? AND airstamp = ? AND id != ?",
        (slot["channel_id"], slot["airstamp"], slot_id),
    )
    conn.commit()
    return {
        "ok": True,
        "object_ref": {"service": "scheduler", "object_type": "schedule_item",
                       "object_id": str(slot_id)},
        "detail": "removed overlapping duplicate slot",
    }


def _rights_takedown(conn: sqlite3.Connection, args: dict) -> dict:
    vod_id = args.get("vod_item_id")
    row = conn.execute("SELECT * FROM vod_item WHERE id = ?", (vod_id,)).fetchone()
    if row is None:
        return {"ok": False, "object_ref": None, "detail": f"no vod_item {vod_id}"}
    conn.execute("UPDATE vod_item SET live = 0 WHERE id = ?", (vod_id,))
    conn.commit()
    return {
        "ok": True,
        "object_ref": {"service": "rights", "object_type": "vod_item",
                       "object_id": str(vod_id)},
        "detail": "took VOD item offline (live=0)",
    }


# --------------------------------------------------------------------------- #
# Verify (with the one-shot flake) / restore / flake arming
# --------------------------------------------------------------------------- #
def verify(conn: sqlite3.Connection, object_type: str, object_id: str) -> dict:
    """verified = object healthy now. HONOUR the one-shot flake: if armed, the FIRST
    verify after arming returns verified=false and disarms."""
    armed = conn.execute("SELECT armed FROM flake_state WHERE id = 1").fetchone()
    if armed and armed["armed"]:
        conn.execute("UPDATE flake_state SET armed = 0 WHERE id = 1")
        conn.commit()
        return {"verified": False, "detail": "transient verification failure (one-shot flake)"}
    healthy = is_healthy(conn, object_type, object_id)
    return {
        "verified": healthy,
        "detail": "object healthy" if healthy else "object still unhealthy",
    }


def restore(conn: sqlite3.Connection, object_type: str, object_id: str, snapshot: dict) -> dict:
    """Roll an object back to a prior field snapshot (from GET /sim/object)."""
    table = _TABLE_FOR.get(object_type)
    if table is None:
        return {"ok": False}
    cols = {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    sets = {k: v for k, v in snapshot.items() if k in cols and k != "id"}
    if sets:
        assignments = ", ".join(f"{k} = ?" for k in sets)
        conn.execute(
            f"UPDATE {table} SET {assignments} WHERE id = ?",
            (*sets.values(), object_id),
        )
    # For schedule_item, also restore the EPG flags if the snapshot carried them.
    if object_type == "schedule_item" and "missing_metadata" in snapshot:
        conn.execute(
            "UPDATE epg_payload SET missing_metadata = ?, xmltv = COALESCE(?, xmltv) "
            "WHERE schedule_slot_id = ?",
            (snapshot["missing_metadata"], snapshot.get("xmltv"), object_id),
        )
    conn.commit()
    return {"ok": True}


def arm_flake(conn: sqlite3.Connection) -> dict:
    conn.execute("UPDATE flake_state SET armed = 1 WHERE id = 1")
    conn.commit()
    return {"armed": True}


# --------------------------------------------------------------------------- #
# Read helpers for the browsing endpoints (return rows incl. nulls/dups verbatim).
# --------------------------------------------------------------------------- #
def _rows(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def list_channels(conn: sqlite3.Connection) -> list[dict]:
    return _rows(conn, "SELECT * FROM channel ORDER BY id")


def list_slots(conn: sqlite3.Connection) -> list[dict]:
    return _rows(conn, "SELECT * FROM schedule_slot ORDER BY id")


def list_rights(conn: sqlite3.Connection) -> list[dict]:
    return _rows(conn, "SELECT * FROM rights_record ORDER BY id")


def list_payloads(conn: sqlite3.Connection) -> list[dict]:
    return _rows(conn, "SELECT * FROM epg_payload ORDER BY id")


def list_kb(conn: sqlite3.Connection) -> list[dict]:
    rows = _rows(conn, "SELECT * FROM kb_article ORDER BY id")
    for r in rows:
        r["error_codes"] = json.loads(r.pop("error_codes_json") or "[]")
    return rows


def get_incident(conn: sqlite3.Connection, n: int) -> dict | None:
    row = conn.execute("SELECT * FROM demo_incident WHERE n = ?", (n,)).fetchone()
    return dict(row) if row else None


def _now_ms() -> int:
    return int(time.time() * 1000)
