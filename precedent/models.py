"""The ONLY file in the pipeline allowed to name a model.

BasedAI track rule: open-weight models only — no closed/proprietary model may be
called anywhere in the loop. Every entry below links a public Hugging Face weights
repo, verified live on 3 Jul 2026 (see docs/compliance/venice-models-*.json).

CI guard (must return ONLY this module's comment lines) — see scripts/check_open_weight.sh:
    grep -rnE "claude-|openai-|gpt-|gemini-|grok-|mercury-" --include=*.py precedent

Starter file written during planning so the build starts from a pinned, verified
registry rather than re-deriving it. IDs and licences are already confirmed.
"""
from __future__ import annotations

import os

VENICE_BASE_URL = os.environ.get("VENICE_BASE_URL", "https://api.venice.ai/api/v1")

# role -> (venice_model_id, hf_weights_url, licence, notes)
OPEN_WEIGHT_MODELS: dict[str, tuple[str, str, str, str]] = {
    "FAST": (
        "qwen3-5-35b-a3b",
        "https://huggingface.co/Qwen/Qwen3.5-35B-A3B",
        "Apache-2.0",
        "MoE 35B/3B-active; triage, chat replies, extraction assist; tool-calling",
    ),
    "SMART": (
        "deepseek-v4-flash",
        "https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash",
        "MIT",
        "retrieval synthesis, risk-rationale prose, plan drafting (first-occurrence only)",
    ),
    "HEAVY": (
        "deepseek-v4-pro",
        "https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro",
        "MIT",
        "escalation dossiers only — never in the hot path",
    ),
    "EMBED": (
        "text-embedding-bge-m3",
        "https://huggingface.co/BAAI/bge-m3",
        "MIT",
        "ALL embeddings precomputed at build time; only visible under GET /models?type=embedding",
    ),
}

# Verified fallback bench (corrected against the live catalog 3 Jul — the third-party
# list had two bad IDs: `llama-4-maverick` does not exist on Venice; `qwen-3-6-27b`
# is really `qwen3-6-27b`).
FALLBACK_BENCH: dict[str, list[str]] = {
    "text": ["qwen3-6-27b", "zai-org-glm-5-2", "kimi-k2-7-code"],
    "embed": ["text-embedding-qwen3-0-6b", "text-embedding-qwen3-8b"],
}

# Local Ollama airplane-mode profile (T1-1). Open-weight tags served by a local
# `ollama` daemon (OpenAI-compatible endpoint). These live HERE — the single
# enforcement point — so no model name ever appears outside this module. All tags
# are open-weight (none match the closed-model CI grep). Selected by
# PRECEDENT_MODEL_BACKEND=local; the response cache + canned fallbacks make the
# airplane rehearsal pass even when no daemon is running.
LOCAL_MODELS: dict[str, str] = {
    "FAST": "qwen3:8b",
    "SMART": "qwen3:8b",
    "HEAVY": "qwen3:8b",
    "EMBED": "bge-m3",
}

# Dev-only proprietary escape hatch — NEVER set in demo/CI. Guards against a closed
# model silently entering the pipeline.
ALLOW_PROPRIETARY_DEV = os.environ.get("PRECEDENT_DEV_MODELS") == "unsafe-dev-only"

_ALLOWED_IDS = frozenset(v[0] for v in OPEN_WEIGHT_MODELS.values())


def model_id(role: str) -> str:
    """Resolve a role to its pinned open-weight model id."""
    return OPEN_WEIGHT_MODELS[role][0]


def local_model_id(role: str) -> str:
    """Resolve a role to its local Ollama airplane-profile tag (open-weight)."""
    return LOCAL_MODELS[role]


def assert_open_weight(model_ids_from_catalog: dict[str, str | None]) -> None:
    """Startup guard. Pass a {model_id: modelSource} map from a live GET /models call.

    Asserts every pinned id is present AND its modelSource is a huggingface.co URL.
    The huggingface.co check is load-bearing: closed models on Venice do NOT reliably
    carry a null modelSource (grok-4-3, gemini-3-5-flash, qwen-3-7-plus expose vendor
    doc URLs), so "has a source" is not enough — it must be an HF source.
    """
    if ALLOW_PROPRIETARY_DEV:  # pragma: no cover - never in demo/CI
        return
    for role, (mid, _hf, _lic, _notes) in OPEN_WEIGHT_MODELS.items():
        if mid not in model_ids_from_catalog:
            raise RuntimeError(f"open-weight guard: pinned {role} id {mid!r} not in live catalog")
        src = (model_ids_from_catalog.get(mid) or "")
        if "huggingface.co" not in src:
            raise RuntimeError(
                f"open-weight guard: {role} id {mid!r} has non-HF modelSource {src!r}"
            )
