"""Typed-tool client — the Operator's ONLY way to touch MediaCo.  [owner T1, task T1-10]

Spec: 02 §3.4 (Operator = typed tool calls, never free-form shell).

Wraps the sim's typed-tool HTTP contract. Accepts any object exposing .get/.post like an
httpx.Client OR a fastapi.testclient.TestClient, so the orchestrator runs the same code
against a live uvicorn sim (demo) or an in-process TestClient (tests / airplane mode).
RULE 1/2: no model id, no LLM here — deterministic typed calls only.
"""
from __future__ import annotations

import os

import httpx


class SimTools:
    """Thin typed adapter over the sim's loop endpoints (contract in sim/)."""

    def __init__(self, client=None, *, base_url: str | None = None, timeout: float = 10.0) -> None:
        if client is None:
            base_url = base_url or os.environ.get("PRECEDENT_SIM_URL", "http://127.0.0.1:8100")
            client = httpx.Client(base_url=base_url, timeout=timeout)
        self.c = client

    # P0.7(a): EVERY typed call checks the HTTP status. A 404 snapshot must NOT return an empty
    # body that the loop mistakes for a valid pre-state (a silent fail-open in the rollback
    # story) — a non-2xx raises, and prepare() refuses to build a plan on an empty snapshot.
    def _get(self, path: str) -> dict:
        r = self.c.get(path)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, **kw) -> dict:
        r = self.c.post(path, **kw)
        r.raise_for_status()
        return r.json()

    def incident(self, n: int) -> dict:
        return self._get(f"/sim/incident/{n}")

    def snapshot(self, service: str, object_type: str, object_id) -> dict:
        return self._get(f"/sim/object/{service}/{object_type}/{object_id}")

    def execute(self, tool: str, args: dict) -> dict:
        return self._post("/sim/execute", json={"tool": tool, "args": args})

    def verify(self, service: str, object_type: str, object_id) -> dict:
        return self._post("/sim/verify", json={"service": service,
                                               "object_type": object_type,
                                               "object_id": object_id})

    def restore(self, service: str, object_type: str, object_id, snapshot: dict) -> dict:
        return self._post("/sim/restore", json={"service": service,
                                                "object_type": object_type,
                                                "object_id": object_id,
                                                "snapshot": snapshot})

    def arm_flake(self) -> dict:
        return self._post("/sim/publisher/flake", params={"once": "true"})
