"""Venice inference client — the ONLY model backend.  [owner T1, task T1-1/T1-3]

Spec: Idea/refinement/02-architecture-refinement.md §1.

RULE 1: this file never names a model. Every call resolves a ROLE
(FAST/SMART/HEAVY/EMBED) through precedent.models — the single enforcement point.
At startup, call GET /models and hand the {id: modelSource} map to
precedent.models.assert_open_weight() so a closed model can never enter the pipeline.

RULE 2: chat() output only ever PROPOSES (triage fields, rationale prose). It NEVER
decides a risk class or gates execution. On timeout/outage chat() returns a benign
canned string so a missing proposal degrades safely (the deterministic path decides).

Local-first: every hot-path call has a 5-6 s timeout with a canned fallback; a prompt-
hash response cache makes rehearsed reruns instant (airplane mode); PRECEDENT_MODEL_BACKEND=
local routes to a local Ollama daemon (open-weight tags in precedent.models.LOCAL_MODELS).
"""
from __future__ import annotations

import hashlib
import json
import os
import time

import httpx

from precedent import models

BASE_URL = os.environ.get("VENICE_BASE_URL", "https://api.venice.ai/api/v1")
LOCAL_BASE_URL = os.environ.get("PRECEDENT_LOCAL_BASE_URL", "http://localhost:11434/v1")

# 5-6 s hot-path budget (02 §1.3). Overridable per call.
DEFAULT_TIMEOUT = float(os.environ.get("PRECEDENT_VENICE_TIMEOUT", "5.5"))

# Benign sentinel returned when the model is unreachable. It is NOT a valid proposal:
# the extractor cannot parse fields out of it, so a failed triage falls back to the
# deterministic path (or caps at L0/L1) — never to an LLM-authored decision (rule 2).
CANNED_FALLBACK = "[[venice-unavailable]]"


class VeniceError(RuntimeError):
    """Raised by embed() when the embedding backend is unreachable (build-time only;
    the caller falls back to BM25). chat() never raises — it returns CANNED_FALLBACK."""


# --------------------------------------------------------------------------- #
# Backend selection
# --------------------------------------------------------------------------- #
def _backend() -> str:
    return os.environ.get("PRECEDENT_MODEL_BACKEND", "venice").strip().lower()


def _endpoint(path: str) -> str:
    base = LOCAL_BASE_URL if _backend() == "local" else BASE_URL
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def _resolve_model(role: str) -> str:
    return models.local_model_id(role) if _backend() == "local" else models.model_id(role)


def _headers() -> dict[str, str]:
    h = {"Content-Type": "application/json"}
    if _backend() != "local":
        key = os.environ.get("VENICE_API_KEY")
        if key:
            h["Authorization"] = f"Bearer {key}"
    return h


# --------------------------------------------------------------------------- #
# Prompt-hash response cache (in-memory always; on-disk if PRECEDENT_VENICE_CACHE set)
# --------------------------------------------------------------------------- #
_MEM_CACHE: dict[str, object] = {}
_DISK_LOADED = False


def _cache_path() -> str | None:
    return os.environ.get("PRECEDENT_VENICE_CACHE")


def _load_disk_cache() -> None:
    global _DISK_LOADED
    if _DISK_LOADED:
        return
    _DISK_LOADED = True
    path = _cache_path()
    if path and os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                _MEM_CACHE.update(json.load(fh))
        except (OSError, ValueError):
            pass


def _persist_disk_cache() -> None:
    path = _cache_path()
    if not path:
        return
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(_MEM_CACHE, fh, sort_keys=True)
    except OSError:
        pass


def _cache_key(kind: str, role: str, payload: dict) -> str:
    material = json.dumps({"kind": kind, "backend": _backend(), "role": role,
                           "payload": payload}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# Honest model-call counter — counts REAL network calls to the model endpoint
# (chat/embed), never cache hits. The demo surface reads this to render
# "Model calls this session: 0" while the zero-LLM fast path resolves: the
# counter is the proof, not a claim. View-only; participates in no decision.
# --------------------------------------------------------------------------- #
_MODEL_CALLS = 0


def model_call_count() -> int:
    """Number of real HTTP calls made to the model endpoint this process/session."""
    return _MODEL_CALLS


def reset_model_calls() -> None:
    global _MODEL_CALLS
    _MODEL_CALLS = 0


# --------------------------------------------------------------------------- #
# HTTP (isolated so tests monkeypatch one seam)
# --------------------------------------------------------------------------- #
def _post(url: str, payload: dict, *, timeout: float) -> dict:
    """POST JSON, return parsed JSON. Raises on any transport/HTTP error. Tests
    monkeypatch this single function; nothing else in the module touches network."""
    global _MODEL_CALLS
    resp = httpx.post(url, json=payload, headers=_headers(), timeout=timeout)
    resp.raise_for_status()
    _MODEL_CALLS += 1     # count only a SUCCESSFUL model response — a timed-out/refused
    return resp.json()    # attempt consulted no model (the deterministic path handled it)


# --------------------------------------------------------------------------- #
# startup_guard — already delegated to the tested registry guard
# --------------------------------------------------------------------------- #
def startup_guard(catalog: dict[str, str | None]) -> None:
    """Pass a live {id: modelSource} map from GET /models; raises if any pinned model
    is missing or non-open-weight. Delegates to the tested guard in precedent.models."""
    models.assert_open_weight(catalog)


def fetch_catalog(*, timeout: float = 10.0) -> dict[str, str | None]:
    """Live GET /models (+ ?type=embedding) → {model_id: modelSource}. Used once at
    startup to feed startup_guard. Venice exposes embedding models only under the
    embedding type, so both lists are merged."""
    out: dict[str, str | None] = {}
    for params in ({}, {"type": "embedding"}):
        resp = httpx.get(_endpoint("models"), headers=_headers(), params=params, timeout=timeout)
        resp.raise_for_status()
        for m in (resp.json() or {}).get("data", []):
            mid = m.get("id")
            if not mid:
                continue
            spec = m.get("model_spec") or {}
            out[mid] = spec.get("modelSource") or m.get("modelSource")
    return out


# --------------------------------------------------------------------------- #
# chat()  — proposes only; never decides (rule 2)
# --------------------------------------------------------------------------- #
def _parse_chat(data: dict) -> str | dict:
    """OpenAI-compatible parse. A tool call → dict {'__tool__', 'args'}; else the
    message content string."""
    choices = data.get("choices") or []
    if not choices:
        return CANNED_FALLBACK
    msg = choices[0].get("message") or {}
    tool_calls = msg.get("tool_calls") or []
    if tool_calls:
        fn = (tool_calls[0] or {}).get("function") or {}
        raw = fn.get("arguments")
        try:
            args = json.loads(raw) if isinstance(raw, str) else (raw or {})
        except ValueError:
            args = {}
        return {"__tool__": fn.get("name"), "args": args}
    return msg.get("content") or CANNED_FALLBACK


def chat(role: str, messages: list[dict], *, tools: list | None = None,
         temperature: float = 0.2, max_tokens: int | None = None,
         timeout: float | None = None, use_cache: bool = True, **kw) -> str | dict:
    """OpenAI-compatible chat completion. Returns a str (content) or a dict (parsed
    tool call). On timeout/outage returns CANNED_FALLBACK (never raises). `role` ∈
    {FAST, SMART, HEAVY}. Model id resolved from the role — never named here."""
    payload: dict = {"model": _resolve_model(role), "messages": messages,
                     "temperature": temperature}
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if tools:
        payload["tools"] = tools
    payload.update(kw)

    key = _cache_key("chat", role, payload)
    if use_cache:
        _load_disk_cache()
        if key in _MEM_CACHE:
            return _MEM_CACHE[key]

    try:
        data = _post(_endpoint("chat/completions"), payload,
                     timeout=timeout or DEFAULT_TIMEOUT)
        result = _parse_chat(data)
    except Exception:
        # Timeout, connection error, HTTP error, malformed body — degrade safely.
        return CANNED_FALLBACK

    if use_cache:
        _MEM_CACHE[key] = result
        _persist_disk_cache()
    return result


# --------------------------------------------------------------------------- #
# embed()  — BUILD-TIME ONLY; zero calls at demo time (02 §1.3, §4.2)
# --------------------------------------------------------------------------- #
def embed(texts: list[str], *, timeout: float = 30.0, use_cache: bool = True) -> list[list[float]]:
    """Embeddings via /embeddings, model resolved from the EMBED role. Precompute at
    build time and COMMIT the vectors; the demo makes zero embedding calls. Raises
    VeniceError on any outage so the caller falls back to BM25 (precedent.bm25)."""
    payload = {"model": _resolve_model("EMBED"), "input": list(texts)}
    key = _cache_key("embed", "EMBED", payload)
    if use_cache:
        _load_disk_cache()
        if key in _MEM_CACHE:
            return _MEM_CACHE[key]
    try:
        data = _post(_endpoint("embeddings"), payload, timeout=timeout)
    except Exception as exc:  # noqa: BLE001 — surfaced as a typed build-time error
        raise VeniceError(f"embedding backend unreachable ({type(exc).__name__})") from None
    rows = data.get("data") or []
    vectors = [r.get("embedding") for r in rows]
    if len(vectors) != len(texts) or any(v is None for v in vectors):
        raise VeniceError("embedding response shape mismatch")
    if use_cache:
        _MEM_CACHE[key] = vectors
        _persist_disk_cache()
    return vectors


# --------------------------------------------------------------------------- #
# warm-up (avoid first-token cold start mid-pitch; best-effort, never raises)
# --------------------------------------------------------------------------- #
def warm_up(roles: tuple[str, ...] = ("FAST",)) -> dict[str, float]:
    """Fire one tiny request per role; return {role: latency_s}. Best-effort."""
    out: dict[str, float] = {}
    for role in roles:
        t0 = time.monotonic()
        chat(role, [{"role": "user", "content": "ok"}], max_tokens=1, use_cache=False)
        out[role] = round(time.monotonic() - t0, 3)
    return out
