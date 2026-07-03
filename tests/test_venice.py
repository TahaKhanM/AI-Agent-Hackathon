"""Venice client tests — offline, no network. Proves rule 2 (safe canned fallback),
tool-call parsing, the prompt-hash cache, and the BM25 fallback. The single live
round-trip lives in a separate guarded manual check, never in the unit suite.
"""
from __future__ import annotations

import pytest

from precedent import bm25, venice


@pytest.fixture(autouse=True)
def _clean_cache(monkeypatch):
    venice._MEM_CACHE.clear()
    venice._DISK_LOADED = False
    monkeypatch.delenv("PRECEDENT_VENICE_CACHE", raising=False)
    monkeypatch.setenv("PRECEDENT_MODEL_BACKEND", "venice")
    yield
    venice._MEM_CACHE.clear()


def _content(text):
    return {"choices": [{"message": {"content": text}}]}


def test_chat_returns_content(monkeypatch):
    monkeypatch.setattr(venice, "_post", lambda *a, **k: _content("triage: publisher"))
    out = venice.chat("FAST", [{"role": "user", "content": "epg broke"}])
    assert out == "triage: publisher"


def test_chat_parses_tool_call(monkeypatch):
    resp = {"choices": [{"message": {"tool_calls": [
        {"function": {"name": "propose_fields",
                      "arguments": '{"service":"publisher","error_code":"PUB-4012"}'}}]}}]}
    monkeypatch.setattr(venice, "_post", lambda *a, **k: resp)
    out = venice.chat("FAST", [{"role": "user", "content": "x"}], tools=[{"type": "function"}])
    assert isinstance(out, dict)
    assert out["__tool__"] == "propose_fields"
    assert out["args"]["error_code"] == "PUB-4012"


def test_chat_canned_fallback_on_error(monkeypatch):
    def boom(*a, **k):
        raise TimeoutError("simulated venice timeout")
    monkeypatch.setattr(venice, "_post", boom)
    out = venice.chat("SMART", [{"role": "user", "content": "rationale?"}])
    assert out == venice.CANNED_FALLBACK  # never raises; degrades safely (rule 2)


def test_chat_cache_makes_reruns_instant(monkeypatch):
    calls = {"n": 0}

    def once(*a, **k):
        calls["n"] += 1
        return _content("cached-answer")
    monkeypatch.setattr(venice, "_post", once)
    msgs = [{"role": "user", "content": "unique-prompt-42"}]
    first = venice.chat("FAST", msgs)
    # Now the backend "fails" — a cache hit must still return the first answer.
    monkeypatch.setattr(venice, "_post", lambda *a, **k: (_ for _ in ()).throw(RuntimeError()))
    second = venice.chat("FAST", msgs)
    assert first == second == "cached-answer"
    assert calls["n"] == 1  # only the first call hit the backend


def test_embed_returns_vectors(monkeypatch):
    resp = {"data": [{"embedding": [0.1, 0.2]}, {"embedding": [0.3, 0.4]}]}
    monkeypatch.setattr(venice, "_post", lambda *a, **k: resp)
    vecs = venice.embed(["a", "b"])
    assert vecs == [[0.1, 0.2], [0.3, 0.4]]


def test_embed_raises_on_outage(monkeypatch):
    monkeypatch.setattr(venice, "_post", lambda *a, **k: (_ for _ in ()).throw(OSError()))
    with pytest.raises(venice.VeniceError):
        venice.embed(["a"])


def test_bm25_ranks_relevant_doc_first():
    corpus = [
        "duplicate schedule slot overlap after late change",
        "epg publish failure missing episode metadata",
        "vod item outside licence window takedown",
    ]
    ranked = bm25.rank("epg publish failed missing metadata", corpus, top_k=1)
    assert ranked[0][0] == 1  # the EPG-publish doc
    assert ranked[0][1] > 0


def test_demo_retrieval_path_imports_no_embedding_backend():
    """The demo makes ZERO embedding calls: retrieval enforces ACLs by structured equality
    and never imports the model backend (rule 2 + airplane-mode)."""
    import pathlib
    src = (pathlib.Path(__file__).resolve().parent.parent
           / "precedent_memory" / "retrieve.py").read_text()
    assert "venice" not in src and "import" in src
    assert "embed" not in src.lower()


def test_committed_kb_embeddings_are_present_and_well_formed():
    import json
    import pathlib
    p = pathlib.Path(__file__).resolve().parent.parent / "data" / "embeddings" / "kb_vectors.json"
    assert p.exists(), "precomputed KB vectors must be committed (build-time artifact)"
    d = json.loads(p.read_text())
    assert d["count"] == 10 and d["dim"] > 0
    assert len(d["entries"]) == 10 and all(e.get("vector") for e in d["entries"])
