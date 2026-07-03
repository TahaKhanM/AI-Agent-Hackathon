"""BM25 keyword ranker — the airplane-mode retrieval fallback.  [owner T1, task T1-3]

Spec: 02 §1.3 ("BM25 keyword fallback path"), §4.2 ("zero embedding calls at demo").

Pure-Python, zero deps, deterministic. Used only where candidate *generation* needs a
lexical ranker and precomputed embeddings are unavailable. NOTE (rule 2): this is a
ranking aid for candidate lists, NOT an access decision — precedent_memory.retrieve
enforces ACLs by structured equality and never consults similarity. No model id here.
"""
from __future__ import annotations

import math
import re
from collections import Counter

_TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall((text or "").lower())


class BM25:
    """Okapi BM25 over a small in-memory corpus."""

    def __init__(self, corpus: list[str], *, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.docs = [tokenize(d) for d in corpus]
        self.n = len(self.docs)
        self.doc_len = [len(d) for d in self.docs]
        self.avgdl = (sum(self.doc_len) / self.n) if self.n else 0.0
        self.tf = [Counter(d) for d in self.docs]
        df: Counter = Counter()
        for d in self.docs:
            for term in set(d):
                df[term] += 1
        # idf with the standard BM25 +0.5 smoothing, floored at 0.
        self.idf = {t: max(0.0, math.log((self.n - c + 0.5) / (c + 0.5) + 1.0))
                    for t, c in df.items()}

    def score(self, query: str, index: int) -> float:
        if not (0 <= index < self.n) or self.avgdl == 0:
            return 0.0
        tf = self.tf[index]
        dl = self.doc_len[index]
        s = 0.0
        for term in tokenize(query):
            if term not in tf:
                continue
            freq = tf[term]
            denom = freq + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            s += self.idf.get(term, 0.0) * (freq * (self.k1 + 1)) / denom
        return s

    def rank(self, query: str, *, top_k: int | None = None) -> list[tuple[int, float]]:
        """Return [(doc_index, score), ...] sorted by score desc (ties by index)."""
        scored = [(i, self.score(query, i)) for i in range(self.n)]
        scored.sort(key=lambda p: (-p[1], p[0]))
        return scored[:top_k] if top_k else scored


def rank(query: str, corpus: list[str], *, top_k: int | None = None) -> list[tuple[int, float]]:
    """One-shot convenience: build a BM25 over `corpus` and rank `query`."""
    return BM25(corpus).rank(query, top_k=top_k)
