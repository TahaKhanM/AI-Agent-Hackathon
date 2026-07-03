"""SQLite schema + connection helpers for the MediaCo sim.

This is dumb MediaCo infrastructure: it stores operational objects (channels,
programmes, schedule slots, EPG payloads, VOD items, rights records, KB articles)
and a small demo-incident table. There is NO permission / risk / ACL logic here —
`acl` is stored on kb_article purely for browsing/provenance display, never enforced.

One SQLite file, path from ``PRECEDENT_SIM_DB`` (default ``data/sim.db``).
"""
from __future__ import annotations

import os
import sqlite3

DEFAULT_DB_PATH = "data/sim.db"

# --------------------------------------------------------------------------- #
# DDL — one script, executed idempotently by build_sim().
# --------------------------------------------------------------------------- #
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS channel (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,
    country  TEXT
);

CREATE TABLE IF NOT EXISTS programme (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL,
    genres        TEXT,          -- JSON array (may be empty)
    summary       TEXT,          -- REAL null kept
    externals_json TEXT          -- JSON object (tvrage/thetvdb/imdb, may be nulls)
);

CREATE TABLE IF NOT EXISTS schedule_slot (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    episode_id    INTEGER,       -- TVmaze episode id (NOT unique: one real dup across days)
    channel_id    INTEGER,
    programme_id  INTEGER,
    episode_name  TEXT,
    summary       TEXT,          -- episode synopsis; REAL null kept (58 real defects)
    airstamp      TEXT,
    runtime       INTEGER,       -- REAL null kept
    season        INTEGER,       -- REAL null kept
    number        INTEGER,       -- REAL null kept
    has_overlap   INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (channel_id)   REFERENCES channel (id),
    FOREIGN KEY (programme_id) REFERENCES programme (id)
);

CREATE TABLE IF NOT EXISTS epg_payload (
    id               INTEGER PRIMARY KEY,
    schedule_slot_id INTEGER,
    xmltv            TEXT,
    missing_metadata INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (schedule_slot_id) REFERENCES schedule_slot (id)
);

CREATE TABLE IF NOT EXISTS vod_item (
    id                        INTEGER PRIMARY KEY,
    programme_id              INTEGER,
    title                     TEXT,
    availability_window_start TEXT,
    availability_window_end   TEXT,
    licensed_regions_json     TEXT,      -- JSON array
    exclusivity               INTEGER NOT NULL DEFAULT 0,
    live                      INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (programme_id) REFERENCES programme (id)
);

CREATE TABLE IF NOT EXISTS rights_record (
    id                    INTEGER PRIMARY KEY,
    title                 TEXT,
    type                  TEXT,
    licensed_regions_json TEXT,          -- JSON array (from country, may be empty)
    window_start          TEXT,          -- from date_added (may be null)
    window_end            TEXT,          -- start + 24m movie / 36m tv
    exclusivity           INTEGER NOT NULL DEFAULT 0,
    source_catalog        TEXT
);

CREATE TABLE IF NOT EXISTS rights_programme_link (
    id               INTEGER PRIMARY KEY,
    rights_record_id INTEGER,
    programme_id     INTEGER,
    match_ratio      REAL,
    FOREIGN KEY (rights_record_id) REFERENCES rights_record (id),
    FOREIGN KEY (programme_id)     REFERENCES programme (id)
);

CREATE TABLE IF NOT EXISTS kb_article (
    id                 TEXT PRIMARY KEY,
    title              TEXT,
    service            TEXT,
    error_codes_json   TEXT,             -- JSON array
    target_object_type TEXT,
    adapted_from       TEXT,
    acl                TEXT,             -- stored for browsing/provenance only; NOT enforced
    stale              INTEGER NOT NULL DEFAULT 0,
    owner              TEXT,
    last_reviewed      TEXT,
    body               TEXT
);

CREATE TABLE IF NOT EXISTS demo_incident (
    n                  INTEGER PRIMARY KEY,
    service            TEXT,
    error_code         TEXT,
    target_object_type TEXT,
    object_id          TEXT,
    raw_text           TEXT
);

-- Global one-shot verification flake (the recovery beat). Single row (id=1).
CREATE TABLE IF NOT EXISTS flake_state (
    id    INTEGER PRIMARY KEY CHECK (id = 1),
    armed INTEGER NOT NULL DEFAULT 0
);
"""

# Tables we own — dropped by reset() before a rebuild.
_TABLES = [
    "flake_state",
    "demo_incident",
    "kb_article",
    "rights_programme_link",
    "rights_record",
    "vod_item",
    "epg_payload",
    "schedule_slot",
    "programme",
    "channel",
]


def db_path() -> str:
    return os.environ.get("PRECEDENT_SIM_DB", DEFAULT_DB_PATH)


def connect(path: str | None = None) -> sqlite3.Connection:
    """Open a connection with row access by name and FK enforcement off (we insert
    parents/children in dependency order but keep the graph loose to preserve messy,
    non-matching rights links)."""
    target = path or db_path()
    conn = sqlite3.connect(target)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    # Ensure the single flake row exists (idempotent).
    conn.execute("INSERT OR IGNORE INTO flake_state (id, armed) VALUES (1, 0)")
    conn.commit()


def drop_tables(conn: sqlite3.Connection) -> None:
    for table in _TABLES:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()


def counts(conn: sqlite3.Connection) -> dict[str, int]:
    out: dict[str, int] = {}
    for table in reversed(_TABLES):
        try:
            out[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        except sqlite3.OperationalError:
            out[table] = 0
    return out
