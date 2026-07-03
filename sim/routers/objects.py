"""Object read + typed-tool execution / verify / restore endpoints.

- GET  /sim/object/{service}/{object_type}/{object_id}
- POST /sim/execute
- POST /sim/verify
- POST /sim/restore
"""
from __future__ import annotations

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from sim import core
from sim.routers.deps import get_conn

router = APIRouter()

Conn = Annotated[sqlite3.Connection, Depends(get_conn)]


class ExecuteBody(BaseModel):
    tool: str
    args: dict


class ObjectRef(BaseModel):
    service: str
    object_type: str
    object_id: str


class VerifyBody(BaseModel):
    service: str
    object_type: str
    object_id: str


class RestoreBody(BaseModel):
    service: str
    object_type: str
    object_id: str
    snapshot: dict


@router.get("/sim/object/{service}/{object_type}/{object_id}")
def get_object(
    service: str,
    object_type: str,
    object_id: str,
    conn: Conn,
) -> dict:
    fields = core.object_fields(conn, object_type, object_id)
    if fields is None:
        raise HTTPException(status_code=404, detail=f"no {object_type} {object_id}")
    return {
        "service": service,
        "object_type": object_type,
        "object_id": object_id,
        "fields": fields,
        "healthy": core.is_healthy(conn, object_type, object_id),
    }


@router.post("/sim/execute")
def post_execute(body: ExecuteBody, conn: Conn) -> dict:
    return core.execute(conn, body.tool, body.args)


@router.post("/sim/verify")
def post_verify(body: VerifyBody, conn: Conn) -> dict:
    return core.verify(conn, body.object_type, body.object_id)


@router.post("/sim/restore")
def post_restore(body: RestoreBody, conn: Conn) -> dict:
    return core.restore(conn, body.object_type, body.object_id, body.snapshot)
