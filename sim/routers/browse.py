"""Browsing endpoints (read seeded rows incl. nulls/dups) + flake arming.

- POST /sim/publisher/flake?once=true
- GET  /sim/scheduler/channels
- GET  /sim/scheduler/slots
- GET  /sim/rights/records
- GET  /sim/publisher/payloads
- GET  /sim/kb/articles
"""
from __future__ import annotations

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends

from sim import core
from sim.routers.deps import get_conn

router = APIRouter()

Conn = Annotated[sqlite3.Connection, Depends(get_conn)]


@router.post("/sim/publisher/flake")
def arm_flake(conn: Conn, once: bool = True) -> dict:
    # `once` is accepted for the documented ?once=true call; the flake is always a
    # single global one-shot regardless.
    _ = once
    return core.arm_flake(conn)


@router.get("/sim/scheduler/channels")
def scheduler_channels(conn: Conn) -> list[dict]:
    return core.list_channels(conn)


@router.get("/sim/scheduler/slots")
def scheduler_slots(conn: Conn) -> list[dict]:
    return core.list_slots(conn)


@router.get("/sim/rights/records")
def rights_records(conn: Conn) -> list[dict]:
    return core.list_rights(conn)


@router.get("/sim/publisher/payloads")
def publisher_payloads(conn: Conn) -> list[dict]:
    return core.list_payloads(conn)


@router.get("/sim/kb/articles")
def kb_articles(conn: Conn) -> list[dict]:
    return core.list_kb(conn)
