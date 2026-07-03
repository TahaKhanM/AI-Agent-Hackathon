"""Incident fixture endpoint — GET /sim/incident/{n} (n in 1,2,3).

Returns the canonical structured class plus a MESSY human ticket, byte-identical every
run (deterministic from random.Random(SEED)).
"""
from __future__ import annotations

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from sim import core, incidents
from sim.routers.deps import get_conn

router = APIRouter()

Conn = Annotated[sqlite3.Connection, Depends(get_conn)]


@router.get("/sim/incident/{n}")
def get_incident(n: int, conn: Conn) -> dict:
    if n not in (1, 2, 3):
        raise HTTPException(status_code=404, detail="incident n must be 1, 2 or 3")
    row = core.get_incident(conn, n)
    if row is None:
        raise HTTPException(status_code=404, detail=f"incident {n} not seeded")
    return {
        "incident_id": f"INC-{n}",
        "source": "sim",
        "observed_at": incidents.observed_at(),
        "raw_text": row["raw_text"],
        "structured": {
            "service": row["service"],
            "error_code": row["error_code"],
            "target_object_type": row["target_object_type"],
            "object_id": row["object_id"],
        },
    }
