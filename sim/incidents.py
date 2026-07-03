"""Deterministic demo incidents + messy-ticket generation.

SEED is the single canonical constant for the whole sim. Every random choice in the
package derives from ``random.Random(SEED)`` so incidents 1/2/3 (and any sampled
subset) replay BYTE-IDENTICALLY across runs.

The three demo incidents are *operational objects with a defect* plus a MESSY human
ticket (typos, colloquial phrasing, sometimes a garbled/dropped error code, one
red-herring). The sim is dumb infrastructure: it only records the class the incident
belongs to (service/error_code/target_object_type) and the raw ticket text. It does NOT
classify, gate, or reason — that is the orchestrator's job.
"""
from __future__ import annotations

import json
import random
import sqlite3
from datetime import datetime, timedelta

# --------------------------------------------------------------------------- #
# THE canonical seed. One number backs the chip/slide/README/BUIDL surfaces.
# --------------------------------------------------------------------------- #
SEED = 4207

# Canonical incident classes. These MUST stay in sync with precedent/extractor.py's
# KNOWN_CODES and the KB error_codes. They are the ground truth the tests assert on.
INCIDENT_CLASSES = {
    1: {"service": "publisher", "error_code": "PUB-4012", "target_object_type": "schedule_item"},
    2: {"service": "scheduler", "error_code": "SCH-DUP-002", "target_object_type": "schedule_item"},
    3: {"service": "rights", "error_code": "RGT-EXCL-009", "target_object_type": "vod_item"},
}

# A stable observation time (airplane-mode: no wall-clock in the payload, so /sim/incident
# is byte-identical across runs and machines).
_OBSERVED_AT = "2026-07-03T20:07:00+00:00"


# --------------------------------------------------------------------------- #
# Messy-ticket generation. Fully deterministic: seeded from random.Random(SEED)
# offset per incident so each ticket is fixed but the three differ.
# --------------------------------------------------------------------------- #
# Per-incident phrase banks. The generator picks colloquial fragments, optionally
# garbles/drops the error code, and appends exactly one red-herring.
_TICKET_BANK: dict[int, dict] = {
    1: {
        "openers": [
            "hiya",
            "hey team",
            "morning all",
            "ugh sorry to bug you",
        ],
        "bodies": [
            "the guide thingy is blank for the 9pm slot on telly",
            "epg is showing an empty box where the 9 o clock prog should be",
            "viewers ringing in, the 9pm listing is just blank on freeview",
            "the tv guide has gone blank for the nine pm slot again",
        ],
        "codes": ["PUB-4012", "PUB 4012", "pub4012", None, "PUB-4O12"],
        "tails": [
            "can someone sort it pls",
            "not urgent but looks bad",
            "cheers",
            "ta",
        ],
        "red_herrings": [
            "btw the canteen wifi is down again",
            "(unrelated: my headset keeps cutting out)",
            "p.s. is the 4k feed meant to be greyed out in the portal?",
            "oh and someone left the edit suite lights on",
        ],
    },
    2: {
        "openers": [
            "flagging this",
            "heads up",
            "quick one",
            "not sure who owns this",
        ],
        "bodies": [
            "there are two of the same programme stacked at the same time on one channel",
            "looks like a duplicate slot, same show twice at the same airtime",
            "the schedule has the exact same prog twice back to back overlapping",
            "double booked slot, same channel same time, two entries",
        ],
        "codes": ["SCH-DUP-002", "SCH DUP 002", None, "sch-dup-002", "SCH-DUP-OO2"],
        "tails": [
            "prob a late change gone wrong",
            "playout will trip over this",
            "needs deduping",
            "thanks",
        ],
        "red_herrings": [
            "also the coffee machine on 3 is broken",
            "(side note the archive drive is nearly full)",
            "unrelated but the meeting room booking system is playing up",
            "btw did anyone move my stapler",
        ],
    },
    3: {
        "openers": [
            "urgent-ish",
            "legal flagged this",
            "compliance heads up",
            "please look asap",
        ],
        "bodies": [
            "a title is still live on demand but i think the licence ran out",
            "vod asset playing outside its rights window, exclusivity thing",
            "we might be streaming something past its licence end date",
            "the on demand item is up but the deal window looks expired",
        ],
        "codes": ["RGT-EXCL-009", "RGT EXCL 009", None, "rgt-excl-009", "RGT-EXCL-OO9"],
        "tails": [
            "could be a breach, flagging early",
            "rights ops should confirm",
            "take it down if so",
            "thx",
        ],
        "red_herrings": [
            "unrelated: the vpn was slow this morning",
            "(btw the disney catalog import finished fine)",
            "p.s. my parking pass expires friday",
            "oh and the subtitle QA queue is a bit long",
        ],
    },
}


def make_raw_text(n: int) -> str:
    """Build the MESSY ticket for incident n — byte-identical every run (seeded)."""
    bank = _TICKET_BANK[n]
    # Offset the seed per-incident so the three tickets differ but each is fixed.
    rng = random.Random(SEED + n)
    opener = rng.choice(bank["openers"])
    body = rng.choice(bank["bodies"])
    code = rng.choice(bank["codes"])
    tail = rng.choice(bank["tails"])
    herring = rng.choice(bank["red_herrings"])

    parts = [opener + " -", body]
    if code:
        # Sometimes the code is present but garbled/mistyped; sometimes it's dropped.
        parts.append(f"(ref {code}?)")
    parts.append(tail + ".")
    parts.append(herring)
    return " ".join(parts)


# --------------------------------------------------------------------------- #
# Seed the three demo incident objects into demo_incident, mutating the sim so the
# referenced object genuinely carries the defect.
# --------------------------------------------------------------------------- #
def seed_incidents(conn: sqlite3.Connection) -> None:
    _seed_inc1(conn)
    _seed_inc2(conn)
    _seed_inc3(conn)
    conn.commit()


def _insert_incident(conn: sqlite3.Connection, n: int, object_id: str) -> None:
    cls = INCIDENT_CLASSES[n]
    conn.execute(
        "INSERT OR REPLACE INTO demo_incident "
        "(n, service, error_code, target_object_type, object_id, raw_text) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (n, cls["service"], cls["error_code"], cls["target_object_type"],
         object_id, make_raw_text(n)),
    )


def _seed_inc1(conn: sqlite3.Connection) -> None:
    """INC-1: a schedule_slot whose epg_payload has missing_metadata=1.

    Prefer a real 9pm (21:00) slot with a null summary so the garbled 'guide blank for
    the 9pm slot' ticket points at a genuine defect. Deterministic pick (lowest id)."""
    row = conn.execute(
        "SELECT s.id AS sid FROM schedule_slot s "
        "JOIN epg_payload e ON e.schedule_slot_id = s.id "
        "WHERE e.missing_metadata = 1 AND s.airstamp LIKE '%T20:00:00%' "  # 21:00 BST == 20:00Z
        "ORDER BY s.id LIMIT 1"
    ).fetchone()
    if row is None:
        # Fall back to any slot with missing metadata.
        row = conn.execute(
            "SELECT s.id AS sid FROM schedule_slot s "
            "JOIN epg_payload e ON e.schedule_slot_id = s.id "
            "WHERE e.missing_metadata = 1 ORDER BY s.id LIMIT 1"
        ).fetchone()
    slot_id = row["sid"]
    _insert_incident(conn, 1, str(slot_id))


def _seed_inc2(conn: sqlite3.Connection) -> None:
    """INC-2: create a DUPLICATE overlapping schedule_slot (same channel/time) and mark
    has_overlap=1. This is a NEW row we inject — a real duplicate, not deduped away."""
    base = conn.execute(
        "SELECT id, channel_id, programme_id, airstamp, runtime, season, number "
        "FROM schedule_slot WHERE channel_id IS NOT NULL AND airstamp IS NOT NULL "
        "ORDER BY id LIMIT 1"
    ).fetchone()
    cur = conn.execute(
        "INSERT INTO schedule_slot "
        "(channel_id, programme_id, airstamp, runtime, season, number, has_overlap) "
        "VALUES (?, ?, ?, ?, ?, ?, 1)",
        (base["channel_id"], base["programme_id"], base["airstamp"],
         base["runtime"], base["season"], base["number"]),
    )
    dup_id = cur.lastrowid
    # Mark the original as overlapping too (both entries collide).
    conn.execute("UPDATE schedule_slot SET has_overlap = 1 WHERE id = ?", (base["id"],))
    # Give the duplicate an epg_payload so it is a complete object.
    conn.execute(
        "INSERT INTO epg_payload (schedule_slot_id, xmltv, missing_metadata) VALUES (?, ?, 0)",
        (dup_id, f'<programme channel="{base["channel_id"]}"><title>DUPLICATE</title></programme>'),
    )
    _insert_incident(conn, 2, str(dup_id))


def _seed_inc3(conn: sqlite3.Connection) -> None:
    """INC-3: a vod_item with live=1 but availability_window_end in the past (outside its
    licence window). Deterministically expire the lowest-id VOD item."""
    row = conn.execute(
        "SELECT id FROM vod_item ORDER BY id LIMIT 1"
    ).fetchone()
    vod_id = row["id"]
    past_start = (datetime(2026, 7, 3) - timedelta(days=800)).strftime("%Y-%m-%d")
    past_end = (datetime(2026, 7, 3) - timedelta(days=30)).strftime("%Y-%m-%d")
    conn.execute(
        "UPDATE vod_item SET live = 1, exclusivity = 1, "
        "availability_window_start = ?, availability_window_end = ?, "
        "licensed_regions_json = ? WHERE id = ?",
        (past_start, past_end, json.dumps(["GB", "IE"]), vod_id),
    )
    _insert_incident(conn, 3, str(vod_id))


def observed_at() -> str:
    return _OBSERVED_AT
