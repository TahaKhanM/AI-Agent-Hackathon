"""Precedent Gate API — the versioned HTTP spine every surface consumes.

``gate/`` exposes a mountable FastAPI router (``/v1/gate``) with three operations —
``propose`` / ``decision/{ref}`` / ``outcome`` — over the EXISTING deterministic core. It adds
no decision logic and calls no LLM: every verdict is computed by ``precedent.policy`` +
``precedent.ladder`` and every execution runs through ``precedent.orchestrator``. See
``gate/README.md`` for the trust posture (out-of-band principals, fail-closed, no metering).

RULE 1/2/3/4 all hold here: no model id, no LLM in the decision path, fail-closed on
expiry/absence, no secrets.
"""
from __future__ import annotations

from gate.api import create_gate_app, make_gate_router
from gate.models import (
    DecisionStateResponse,
    OutcomeRequest,
    OutcomeResponse,
    ProposeRequest,
    ProposeResponse,
)
from gate.world import GateWorld, build_seeded_world, gate_world_from_session

__all__ = [
    "make_gate_router",
    "create_gate_app",
    "GateWorld",
    "build_seeded_world",
    "gate_world_from_session",
    "ProposeRequest",
    "ProposeResponse",
    "DecisionStateResponse",
    "OutcomeRequest",
    "OutcomeResponse",
]
