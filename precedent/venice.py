"""Venice inference client — the ONLY model backend.  [STUB — owner T1, task T1-1]

Spec: Idea/refinement/02-architecture-refinement.md §1.

RULE 1: import roles from precedent.models (FAST/SMART/HEAVY/EMBED); never a literal
model id. At startup, call GET /models and pass the {id: modelSource} map to
precedent.models.assert_open_weight() so a closed model can never enter the pipeline.
Every hot-path call has a 5-6s timeout with a canned fallback (local-first). An Ollama
profile (PRECEDENT_MODEL_BACKEND=local) is the airplane-mode fallback.
"""
from __future__ import annotations

import os

from precedent import models

BASE_URL = os.environ.get("VENICE_BASE_URL", "https://api.venice.ai/api/v1")


def startup_guard(catalog: dict[str, str | None]) -> None:
    """Pass a live {id: modelSource} map from GET /models; raises if any pinned model
    is missing or non-open-weight. Delegates to the tested guard in precedent.models."""
    models.assert_open_weight(catalog)


def chat(role: str, messages: list[dict], **kw):
    """TODO T1-1: OpenAI-compatible chat completion via httpx to BASE_URL, model =
    models.model_id(role), with timeout + canned fallback."""
    raise NotImplementedError("T1-1: Venice chat client — see 02 §1.3")


def embed(texts: list[str]):
    """TODO T1-3: embeddings via /embeddings, model = models.model_id('EMBED').
    Precompute at build time and commit vectors; zero embedding calls at demo time."""
    raise NotImplementedError("T1-3: Venice embeddings — see 02 §1.3")
