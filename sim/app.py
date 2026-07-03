"""MediaCo simulated services — one FastAPI app, one SQLite file.

Spec: Idea/refinement/01-realistic-data-plan.md + 02 §4.3.

Dumb MediaCo infrastructure: it stores operational objects (channels, programmes,
schedule slots, EPG payloads, VOD items, rights records, KB articles) seeded from
committed real public data, and applies TYPED fixes toward a healthy state. There is NO
LLM, NO model id, and NO permission / risk / ACL logic here — the orchestrator decides
*whether* to call these typed tools; the sim only stores and mutates.

KEEP the real data's messiness (null metadata, duplicate titles across catalogs, fuzzy
match failures) — it triggers the incidents and is what the Conduct rubric rewards.

Airplane-mode: loads only from committed files under data/raw and data/kb. No network.
Deterministic: sim.incidents.SEED drives every random choice so incidents 1/2/3 replay
byte-identically.
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from sim import core, db
from sim.routers import browse, incident, objects


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Build the sim (idempotent) on boot so the app is usable immediately."""
    conn = db.connect()
    try:
        core.build_sim(conn)
    finally:
        conn.close()
    yield


app = FastAPI(title="MediaCo (Precedent sim)", lifespan=_lifespan)

app.include_router(incident.router)
app.include_router(objects.router)
app.include_router(browse.router)


@app.get("/health")
def health() -> dict:
    conn = db.connect()
    try:
        core.build_sim(conn)  # idempotent guard so /health works even pre-startup
        counts = db.counts(conn)
    finally:
        conn.close()
    return {
        "status": "ok",
        "db": db.db_path(),
        "counts": counts,
    }
