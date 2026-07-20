"""Per-session MediaCo sim app factory — one in-process FastAPI bound to an explicit db path.

WP-HOST-SESSION: the hosted demo gives every browser session its OWN sim world. Instead of
one out-of-process `uvicorn sim.app:app` sharing a single `data/sim.db` (the 5th shared-state
axis), each session builds a fresh FastAPI here whose `get_conn` dependency is overridden to
open the SESSION's private sim.db copy, wraps it in a fastapi.testclient.TestClient, and hands
that to `SimTools(client=...)`. No env var, no HTTP hop, no cross-session row mutation.

The same routers as `sim.app` are mounted, so the typed-tool / verify / restore / browse
contract is byte-identical — only the connection source differs. There is NO lifespan build
here: the per-session db is a COPY of the already-built cold-open snapshot, so `build_sim`
would short-circuit anyway; skipping the lifespan keeps TestClient construction cheap.

RULE 1/2: no model id, no LLM — this is dumb per-session infrastructure wiring only.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Iterator

from fastapi import FastAPI

from sim import db
from sim.routers import browse, incident, objects
from sim.routers.deps import get_conn


def make_sim_app(db_path: str) -> FastAPI:
    """Build a fresh sim FastAPI whose every request opens `db_path` (not the env default).

    The `get_conn` dependency is overridden with a per-request connection to `db_path`, so
    two sessions' apps never touch each other's rows or the global `flake_state` single-row.
    """
    app = FastAPI(title="MediaCo (per-session sim)")
    app.include_router(incident.router)
    app.include_router(objects.router)
    app.include_router(browse.router)

    def _get_conn() -> Iterator[sqlite3.Connection]:
        conn = db.connect(db_path)
        try:
            yield conn
        finally:
            conn.close()

    # Route every Depends(get_conn) at this session's private db file.
    app.dependency_overrides[get_conn] = _get_conn

    @app.get("/health")
    def health() -> dict:  # pragma: no cover - parity with sim.app, handy for probes
        conn = db.connect(db_path)
        try:
            counts = db.counts(conn)
        finally:
            conn.close()
        return {"status": "ok", "db": db_path, "counts": counts}

    return app
