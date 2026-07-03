"""Shared FastAPI dependency: a per-request SQLite connection to the sim DB."""
from __future__ import annotations

from collections.abc import Iterator

from sim import db


def get_conn() -> Iterator:
    conn = db.connect()
    try:
        yield conn
    finally:
        conn.close()
