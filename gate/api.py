"""The versioned HTTP Gate API — a mountable FastAPI APIRouter over gate.service.

Two entry points:
  * ``make_gate_router(world_provider)`` — an APIRouter the deployed console mounts at
    ``/v1/gate`` (world_provider resolves the current browser session's world per request).
  * ``create_gate_app(world)`` — a standalone FastAPI bound to ONE fixed world, so the whole
    surface is exercisable with fastapi.testclient.TestClient in isolation (the e2e).

The routes are thin: they resolve the world and delegate to the deterministic gate.service.
RULE 2: this module imports no model backend and makes no LLM call.

Principal identity is supplied IN-BAND to the request body and is expected to have been
registered OUT-OF-BAND (config/API). The gate does not, and must not, trust an MCP client's
self-asserted identity — there is no robust MCP client-identity standard in 2026.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, FastAPI, Request

from gate import service
from gate.models import (
    DecisionStateResponse,
    GateInfo,
    OutcomeRequest,
    OutcomeResponse,
    ProposeRequest,
    ProposeResponse,
)
from gate.world import GateWorld

WorldProvider = Callable[[Request], GateWorld]


def make_gate_router(world_provider: WorldProvider) -> APIRouter:
    """Build the /v1/gate router. ``world_provider(request)`` returns the GateWorld to use."""
    router = APIRouter(tags=["gate"])

    @router.get("", response_model=GateInfo, summary="Gate trust posture (honest self-description)")
    def info() -> GateInfo:
        return GateInfo()

    @router.post("/propose", response_model=ProposeResponse,
                 summary="Propose a typed action; get a deterministic verdict")
    def propose_action(req: ProposeRequest, request: Request) -> ProposeResponse:
        """Run the deterministic pipeline (extractor/fingerprint → policy.assess → ladder) and
        return deny | needs-approval(ref, expires_at) | allow-standing. No LLM in this path."""
        return service.propose(world_provider(request), req)

    @router.get("/decision/{ref}", response_model=DecisionStateResponse,
                summary="Current state of a held decision (fail-closed on expiry/absence)")
    def get_decision(ref: str, request: Request) -> DecisionStateResponse:
        """pending | approved | denied | expired. An expired or absent ref is a non-action."""
        return service.get_decision(world_provider(request), ref)

    @router.post("/outcome", response_model=OutcomeResponse,
                 summary="Approve/execute-in-sim a held decision and record the outcome")
    def report_outcome(req: OutcomeRequest, request: Request) -> OutcomeResponse:
        """Execute the approved/standing plan in the sim and record verified/rolled_back via
        commit_execution + ladder. Expired/absent ⇒ non-action + a fail-closed audit row."""
        return service.report_outcome(world_provider(request), req)

    return router


def create_gate_app(world: GateWorld | Any) -> FastAPI:
    """A standalone gate app bound to ONE fixed world — for isolated TestClient testing and a
    single-tenant deployment. ``world`` may be a GateWorld or a zero-arg callable returning one.
    """
    resolved = world() if callable(world) else world

    def _provider(_request: Request) -> GateWorld:
        return resolved

    app = FastAPI(title="Precedent Gate API", version="v1")
    app.include_router(make_gate_router(_provider), prefix="/v1/gate")
    return app
