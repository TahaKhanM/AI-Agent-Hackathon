"""Loaders — seed the sim's SQLite from committed raw public data.

Airplane-mode: reads ONLY from committed files under data/raw and data/kb. No network.

KEEP THE MESSINESS. Null summary/season/number/runtime, empty genres, duplicate titles
across catalogs, and fuzzy-match failures are REAL defects in the source and are what the
demo needs — they are preserved verbatim, never dropped, deduped, or repaired.

Determinism: the single module constant SEED (declared in sim/incidents.py and imported
here) drives every random choice (rights exclusivity subset, sampling) so a rebuild
replays byte-identically.
"""
from __future__ import annotations

import csv
import glob
import json
import os
import random
import sqlite3
from datetime import datetime, timedelta

import yaml

from sim.incidents import SEED

# --------------------------------------------------------------------------- #
# Paths (repo-relative; resolved from the repo root at import time).
# --------------------------------------------------------------------------- #
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
TVMAZE_GLOB = os.path.join(_ROOT, "data", "raw", "tvmaze", "schedule-GB-2026-07-0*.json")
KAGGLE_DIR = os.path.join(_ROOT, "data", "raw", "kaggle")
KB_GLOB = os.path.join(_ROOT, "data", "kb", "KB-00*.md")

# Seed only the top-N real channels by slot count (keeps the count in the 6-10 band).
# Slots on channels outside this set are KEPT but with channel_id=NULL — a real
# "unrecognised channel" defect, not a dropped row.
TOP_CHANNELS = 8

# How many rights_record rows to load (a few hundred, > 100 for the test).
RIGHTS_LOAD_LIMIT = 400
# Deterministic ~20% of rights get exclusivity=1.
RIGHTS_EXCLUSIVITY_FRACTION = 0.20
# How many fuzzy title cross-links to attempt (50-100 into rights_programme_link).
FUZZY_LINK_TARGET = 80


# --------------------------------------------------------------------------- #
# TVmaze -> channel / programme / schedule_slot / epg_payload / vod_item
# --------------------------------------------------------------------------- #
def _channel_of(show: dict) -> dict | None:
    """A channel is the show's network, or its webChannel if there is no network."""
    net = show.get("network")
    web = show.get("webChannel")
    src = net or web
    if not src:
        return None
    country = None
    c = src.get("country")
    if c:
        country = c.get("name")
    return {"id": src["id"], "name": src["name"], "country": country}


def _xmltv_for(slot: dict, programme: dict, channel: dict | None, missing: int) -> str:
    """Tiny XMLTV <programme> fragment. When metadata is missing the title/desc reflect
    the real defect (empty desc), so the payload visibly carries the fault."""
    chan = str(channel["id"]) if channel else "unknown"
    start = (slot.get("airstamp") or "").replace("-", "").replace(":", "").replace("T", "")
    title = programme["name"]
    desc = programme.get("summary") or ""
    return (
        f'<programme start="{start}" channel="{chan}">'
        f"<title>{title}</title>"
        f"<desc>{desc}</desc>"
        f"</programme>"
    )


def _top_channel_ids(files: list[str]) -> set[int]:
    """The top TOP_CHANNELS real channels by slot count across all day-files. Ties are
    broken by channel id (deterministic)."""
    from collections import Counter

    counts: Counter[int] = Counter()
    for path in files:
        with open(path, encoding="utf-8") as fh:
            for ep in json.load(fh):
                channel = _channel_of(ep.get("show") or {})
                if channel:
                    counts[channel["id"]] += 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return {cid for cid, _ in ranked[:TOP_CHANNELS]}


def load_tvmaze(conn: sqlite3.Connection) -> None:
    files = sorted(glob.glob(TVMAZE_GLOB))
    top_ids = _top_channel_ids(files)
    seen_channels: set[int] = set()
    seen_programmes: set[int] = set()

    for path in files:
        with open(path, encoding="utf-8") as fh:
            episodes = json.load(fh)
        for ep in episodes:
            show = ep.get("show") or {}
            channel = _channel_of(show)
            # Only the top real channels are seeded (6-10 band). A slot whose channel is
            # outside the set is KEPT with channel_id=NULL (real messiness, not dropped).
            if channel and channel["id"] not in top_ids:
                channel = None

            if channel and channel["id"] not in seen_channels:
                conn.execute(
                    "INSERT OR IGNORE INTO channel (id, name, country) VALUES (?, ?, ?)",
                    (channel["id"], channel["name"], channel["country"]),
                )
                seen_channels.add(channel["id"])

            # programme (one per show id; keep null summary, empty genres verbatim).
            prog_id = show.get("id")
            if prog_id is not None and prog_id not in seen_programmes:
                conn.execute(
                    "INSERT OR IGNORE INTO programme "
                    "(id, name, genres, summary, externals_json) VALUES (?, ?, ?, ?, ?)",
                    (
                        prog_id,
                        show.get("name"),
                        json.dumps(show.get("genres") or []),
                        show.get("summary"),  # REAL null kept
                        json.dumps(show.get("externals") or {}),
                    ),
                )
                seen_programmes.add(prog_id)

            # schedule_slot — the episode itself. Nulls in season/number/runtime kept.
            season = ep.get("season")
            number = ep.get("number")
            runtime = ep.get("runtime")
            summary = ep.get("summary")
            # A REAL defect: the source record is missing required publish metadata.
            missing = 1 if (summary is None or season is None or number is None) else 0

            cur = conn.execute(
                "INSERT INTO schedule_slot "
                "(episode_id, channel_id, programme_id, episode_name, summary, airstamp, "
                " runtime, season, number, has_overlap) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)",
                (
                    ep["id"],
                    channel["id"] if channel else None,
                    prog_id,
                    ep.get("name"),
                    summary,  # episode synopsis — REAL null kept for 58 rows
                    ep.get("airstamp"),
                    runtime,
                    season,
                    number,
                ),
            )
            slot_id = cur.lastrowid

            programme_row = {
                "name": show.get("name"),
                "summary": summary if summary is not None else show.get("summary"),
            }
            xmltv = _xmltv_for(ep, programme_row, channel, missing)
            conn.execute(
                "INSERT INTO epg_payload (schedule_slot_id, xmltv, missing_metadata) "
                "VALUES (?, ?, ?)",
                (slot_id, xmltv, missing),
            )

    # A handful of VOD items derived from real programmes (for the rights incident).
    _seed_vod_items(conn)
    conn.commit()


def _seed_vod_items(conn: sqlite3.Connection) -> None:
    """Seed a small deterministic set of VOD items from the loaded programmes. One will
    become INC-3 (live=1 but window_end in the past)."""
    rng = random.Random(SEED)
    progs = [
        (r["id"], r["name"])
        for r in conn.execute(
            "SELECT id, name FROM programme ORDER BY id LIMIT 12"
        ).fetchall()
    ]
    now = datetime(2026, 7, 3)
    for i, (pid, name) in enumerate(progs):
        # Most windows are open; the incident seeder will pick one and expire it.
        start = now - timedelta(days=rng.randint(30, 400))
        end = start + timedelta(days=rng.randint(500, 1000))
        exclusivity = 1 if rng.random() < 0.3 else 0
        conn.execute(
            "INSERT INTO vod_item "
            "(programme_id, title, availability_window_start, availability_window_end, "
            " licensed_regions_json, exclusivity, live) VALUES (?, ?, ?, ?, ?, ?, 1)",
            (
                pid,
                name,
                start.strftime("%Y-%m-%d"),
                end.strftime("%Y-%m-%d"),
                json.dumps(["GB"]),
                exclusivity,
            ),
        )
        _ = i


# --------------------------------------------------------------------------- #
# Kaggle -> rights_record + fuzzy cross-link into rights_programme_link
# --------------------------------------------------------------------------- #
_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}


def _parse_date_added(raw: str) -> datetime | None:
    """Kaggle date_added is like 'September 25, 2021' (with a leading space sometimes).
    Missing values are REAL — return None and keep the row."""
    if not raw:
        return None
    s = raw.strip().rstrip(",").replace(",", "")
    parts = s.split()
    if len(parts) != 3:
        return None
    month = _MONTHS.get(parts[0].lower())
    if month is None:
        return None
    try:
        return datetime(int(parts[2]), month, int(parts[1]))
    except (ValueError, IndexError):
        return None


def _window_end(start: datetime | None, kind: str) -> datetime | None:
    if start is None:
        return None
    months = 24 if (kind or "").strip().lower() == "movie" else 36
    # Add months by advancing years/months arithmetically (no external dep).
    total = (start.year * 12 + (start.month - 1)) + months
    year, month = divmod(total, 12)
    month += 1
    day = min(start.day, 28)
    return datetime(year, month, day)


def _read_catalog(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _select_rows(rows: list[dict], cross_titles: set[str], budget: int) -> list[dict]:
    """Deterministically choose ``budget`` rows from a catalog, order-preserving.

    We take the head of the catalog and ADD every row whose title is a genuine
    cross-catalog duplicate (a title that also appears in the other catalog) — the real
    MGM/Starz-style collision KB-0005 references. Cross-catalog dups are scattered deep
    in the (much larger) Netflix file, so a plain head slice would miss them; including
    them keeps a REAL duplicate-title defect without inventing anything. Non-matching
    and null rows are kept untouched."""
    picked: list[dict] = []
    seen_idx: set[int] = set()
    # 1) genuine cross-catalog duplicates first (real messiness, deterministic by order).
    for i, row in enumerate(rows):
        if (row.get("title") or "") in cross_titles:
            picked.append(row)
            seen_idx.add(i)
    # 2) fill the rest from the catalog head, in file order.
    for i, row in enumerate(rows):
        if len(picked) >= budget:
            break
        if i not in seen_idx:
            picked.append(row)
            seen_idx.add(i)
    return picked[:budget]


def load_kaggle(conn: sqlite3.Connection) -> None:
    rng = random.Random(SEED)
    nf_path = os.path.join(KAGGLE_DIR, "netflix_titles.csv")
    dp_path = os.path.join(KAGGLE_DIR, "disney_plus_titles.csv")
    nf_rows = _read_catalog(nf_path)
    dp_rows = _read_catalog(dp_path)
    # Titles present in BOTH catalogs -> genuine cross-catalog duplicates.
    cross_titles = {r["title"] for r in nf_rows} & {r["title"] for r in dp_rows}

    budget = RIGHTS_LOAD_LIMIT // 2
    selection = [
        ("netflix", _select_rows(nf_rows, cross_titles, budget)),
        ("disney", _select_rows(dp_rows, cross_titles, budget)),
    ]
    for source, chosen in selection:
        for row in chosen:
            title = row.get("title")
            kind = row.get("type")
            country = row.get("country") or ""
            # licensed_regions from country (comma-separated in the source; keep
            # empties as empty list — a REAL defect, not a repair).
            regions = [c.strip() for c in country.split(",") if c.strip()]
            start = _parse_date_added(row.get("date_added", ""))
            end = _window_end(start, kind)
            exclusivity = 1 if rng.random() < RIGHTS_EXCLUSIVITY_FRACTION else 0
            conn.execute(
                "INSERT INTO rights_record "
                "(title, type, licensed_regions_json, window_start, window_end, "
                " exclusivity, source_catalog) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    title,
                    kind,
                    json.dumps(regions),
                    start.strftime("%Y-%m-%d") if start else None,
                    end.strftime("%Y-%m-%d") if end else None,
                    exclusivity,
                    source,
                ),
            )
    conn.commit()
    _fuzzy_link(conn)


def _fuzzy_link(conn: sqlite3.Connection) -> None:
    """Cross-link 50-100 rights records to programmes by FUZZY title match (difflib).
    Non-matches are KEPT (not every rights record links) — no forcing, no cleanup."""
    import difflib

    programmes = conn.execute("SELECT id, name FROM programme").fetchall()
    prog_names = [(p["id"], (p["name"] or "").lower()) for p in programmes]
    rights = conn.execute("SELECT id, title FROM rights_record").fetchall()

    links = 0
    for r in rights:
        if links >= FUZZY_LINK_TARGET:
            break
        rtitle = (r["title"] or "").lower()
        if not rtitle:
            continue
        best_pid = None
        best_ratio = 0.0
        for pid, pname in prog_names:
            if not pname:
                continue
            ratio = difflib.SequenceMatcher(None, rtitle, pname).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_pid = pid
        # Only link on a reasonably strong fuzzy match; weaker ones are left UNLINKED
        # on purpose (fuzzy-match failure is real messiness we keep — most rights records
        # do NOT link to any programme).
        if best_pid is not None and best_ratio >= 0.50:
            conn.execute(
                "INSERT INTO rights_programme_link "
                "(rights_record_id, programme_id, match_ratio) VALUES (?, ?, ?)",
                (r["id"], best_pid, round(best_ratio, 4)),
            )
            links += 1
    conn.commit()


# --------------------------------------------------------------------------- #
# KB -> kb_article (browsing/provenance only; NO ACL enforcement here)
# --------------------------------------------------------------------------- #
def _split_front_matter(text: str) -> tuple[dict, str]:
    """Parse leading YAML front-matter delimited by '---' lines."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = yaml.safe_load(parts[1]) or {}
    body = parts[2].lstrip("\n")
    return meta, body


def load_kb(conn: sqlite3.Connection) -> None:
    for path in sorted(glob.glob(KB_GLOB)):
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        meta, body = _split_front_matter(text)
        if not meta.get("id"):
            continue
        conn.execute(
            "INSERT OR REPLACE INTO kb_article "
            "(id, title, service, error_codes_json, target_object_type, adapted_from, "
            " acl, stale, owner, last_reviewed, body) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                meta.get("id"),
                meta.get("title"),
                meta.get("service"),
                json.dumps(meta.get("error_codes") or []),
                meta.get("target_object_type"),
                meta.get("adapted_from"),
                meta.get("acl"),
                1 if meta.get("stale") else 0,
                meta.get("owner"),
                str(meta.get("last_reviewed")) if meta.get("last_reviewed") else None,
                body,
            ),
        )
    conn.commit()
