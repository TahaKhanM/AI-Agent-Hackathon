"""Privacy-preserving funnel counters (WP-DEMO §d) — the day-90 kill-gate instrument.

ANONYMOUS AGGREGATES ONLY. This module persists nothing that identifies a visitor or a session:
the only stored fields are a COARSE (daily) date, the event name, and a running count. No session
id, no cookie, no IP, no user agent, no fine-grained timestamp — by construction there is nowhere
to put one (the table has three columns and the writer is given none of those values).

CONSENT-GATED. A call without an explicit ``consent=True`` is a NON-action: it records nothing and
returns ``recorded=False``. Consent is asked for once, in-surface, and defaults to OFF.

TWO LIFETIMES, on purpose. Per-visitor event detail lives (and dies) with the per-session world's
TTL (console/session.py) — it is never written here. These aggregates PERSIST across sessions and
restarts: they are the instrument the day-90 kill-gate reads to decide whether the demo converts.

SCOPE. Hosted demo + landing ONLY. This module is imported by console/app.py; it is NEVER imported
by the analyzer (precedent_analyzer/) — the analyzer runs on a customer's own machine over their own
tickets and must emit no telemetry at all. A CI import-guard test enforces that boundary.

RULES: deterministic, no LLM, no secrets. The store is a tiny local SQLite file.
"""
from __future__ import annotations

import datetime as _dt
import os
import sqlite3
import threading
from pathlib import Path

# The ONLY events the funnel will count. An unknown event is a fail-closed non-action (nothing is
# written) — the store can never accrue an attacker-chosen key, and the schema stays a closed set.
ALLOWED_EVENTS = frozenset({"express_complete", "pack_download", "cta_click"})

# Default location: a persistent file under data/ (survives restarts — these aggregates are the
# kill-gate instrument). Overridable for tests / hosting via PRECEDENT_FUNNEL_DB.
_DEFAULT_PATH = str(Path(__file__).resolve().parent.parent / "data" / "funnel.db")

_LOCK = threading.RLock()
_CONN: sqlite3.Connection | None = None
_CONN_PATH: str | None = None


def _today() -> str:
    """Coarse, day-granularity date (UTC). Deliberately NOT a fine timestamp — a per-second time
    would let a reader correlate two events back to one visitor. Day granularity cannot."""
    return _dt.datetime.now(_dt.UTC).strftime("%Y-%m-%d")


def db_path() -> str:
    return os.environ.get("PRECEDENT_FUNNEL_DB") or _DEFAULT_PATH


def _connect(path: str) -> sqlite3.Connection:
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Exactly three columns — day, event, count. There is structurally NO column for any visitor or
    # session identifier, so no caller can smuggle one in.
    conn.execute(
        "CREATE TABLE IF NOT EXISTS funnel_daily ("
        "  day   TEXT NOT NULL,"
        "  event TEXT NOT NULL,"
        "  count INTEGER NOT NULL DEFAULT 0,"
        "  PRIMARY KEY (day, event))")
    conn.commit()
    return conn


def _conn() -> sqlite3.Connection:
    """Process-wide connection to the persistent aggregate store, opened on first use. Re-opened if
    PRECEDENT_FUNNEL_DB changes (tests point it at a tmp file)."""
    global _CONN, _CONN_PATH
    path = db_path()
    with _LOCK:
        if _CONN is None or _CONN_PATH != path:
            if _CONN is not None:
                with _swallow():
                    _CONN.close()
            _CONN = _connect(path)
            _CONN_PATH = path
        return _CONN


class _swallow:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return True


def record(event: str, consent: bool) -> dict:
    """Count one funnel event — ONLY when consent is explicitly True and the event is allowed.

    Returns a small dict describing what happened. Records NOTHING that could identify a visitor:
    the write is a single ``(day, event) -> count += 1`` upsert. A missing consent, or an unknown
    event, is a non-action (``recorded=False``) — fail-closed."""
    if consent is not True:
        return {"recorded": False, "reason": "no_consent"}
    if event not in ALLOWED_EVENTS:
        return {"recorded": False, "reason": "unknown_event"}
    day = _today()
    with _LOCK:
        conn = _conn()
        conn.execute(
            "INSERT INTO funnel_daily(day, event, count) VALUES(?,?,1) "
            "ON CONFLICT(day, event) DO UPDATE SET count = count + 1",
            (day, event))
        conn.commit()
    return {"recorded": True, "event": event, "day": day}


def totals() -> dict:
    """The anonymous aggregate the day-90 kill-gate reads: per-day, per-event counts. No visitor or
    session detail exists to return — only ``{day, event, count}`` rows."""
    with _LOCK:
        rows = _conn().execute(
            "SELECT day, event, count FROM funnel_daily ORDER BY day, event").fetchall()
    by_event: dict[str, int] = {}
    daily = []
    for r in rows:
        by_event[r["event"]] = by_event.get(r["event"], 0) + r["count"]
        daily.append({"day": r["day"], "event": r["event"], "count": r["count"]})
    return {"totals": by_event, "daily": daily, "allowed_events": sorted(ALLOWED_EVENTS)}


def reset_for_test() -> None:
    """Test hook: drop the in-process connection so the next call re-opens PRECEDENT_FUNNEL_DB."""
    global _CONN, _CONN_PATH
    with _LOCK:
        if _CONN is not None:
            with _swallow():
                _CONN.close()
        _CONN = None
        _CONN_PATH = None
