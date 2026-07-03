"""Precompute + commit KB embeddings (BUILD-TIME ONLY).  [owner T1, task T1-3]

Spec: 02 §1.3 / §4.2 — "ALL embeddings precomputed at build time; zero embedding calls at
demo time." Retrieval enforces ACLs by STRUCTURED equality (precedent_memory.retrieve) and
never consults similarity, so these vectors feed the scale/bench + open-weight-embedder
compliance story, not the demo hot path. The committed artifact makes the airplane demo pass
by construction (no /embeddings call ever happens on stage).

Runs venice.embed (the open-weight EMBED role = bge-m3) if online; falls back to deterministic
offline vectors (clearly labelled) if not — so the build never depends on connectivity. BM25
(precedent.bm25) is the lexical fallback the retrieval path uses when vectors are absent.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import struct

OUT = "data/embeddings/kb_vectors.json"
_OFFLINE_DIM = 256


def _front_matter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    _, fm, _body = text.split("---", 2)
    out: dict[str, str] = {}
    for line in fm.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def _body(text: str) -> str:
    return text.split("---", 2)[-1] if text.startswith("---") else text


def _offline_vector(text: str) -> list[float]:
    """Deterministic pseudo-embedding (labelled non-bge-m3) so the build is airplane-safe."""
    out: list[float] = []
    seed = text.encode("utf-8")
    for i in range((_OFFLINE_DIM + 15) // 16):
        h = hashlib.sha256(seed + struct.pack("<i", i)).digest()
        out.extend(b / 255.0 for b in h[:16])
    return out[:_OFFLINE_DIM]


def main() -> None:
    files = sorted(glob.glob("data/kb/KB-*.md"))
    entries = []
    bodies = []
    metas = []
    for f in files:
        text = open(f, encoding="utf-8").read()
        fm = _front_matter(text)
        codes = (fm.get("error_codes") or "[]").strip("[]").replace(" ", "")
        code = codes.split(",")[0] if codes else ""
        class_key = f"{fm.get('service','')}|{code}|{fm.get('target_object_type','')}"
        metas.append({"id": fm.get("id", os.path.basename(f)), "class_key": class_key})
        bodies.append((fm.get("title", "") + "\n" + _body(text))[:2000])

    model = "bge-m3"
    generated_by = "venice-live-bge-m3"
    vectors: list[list[float]]
    try:
        from precedent import venice
        vectors = venice.embed(bodies, timeout=60, use_cache=False)
    except Exception as exc:  # noqa: BLE001 — offline build is expected sometimes
        print(f"[offline] live embed unavailable ({type(exc).__name__}); deterministic vectors")
        vectors = [_offline_vector(b) for b in bodies]
        model = "offline-deterministic"
        generated_by = "sha256-fallback (run online to replace with bge-m3)"

    for meta, vec in zip(metas, vectors, strict=True):
        entries.append({**meta, "vector": vec})

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"model": model, "dim": len(vectors[0]) if vectors else 0,
                   "generated_by": generated_by, "count": len(entries),
                   "note": "BUILD-TIME artifact; the demo makes ZERO embedding calls "
                           "(retrieval is structured-equality only). BM25 is the lexical fallback.",
                   "entries": entries}, fh)
    print(f"wrote {OUT}: {len(entries)} vectors, model={model}, dim={len(vectors[0])}")


if __name__ == "__main__":
    main()
