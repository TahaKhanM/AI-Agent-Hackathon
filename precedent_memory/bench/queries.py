"""Deterministic ground-truth query corpus (BasedAI protocol: 10,000 queries,
>=3,000 deny-expected).  [owner T3, task T3-3]

Spec: Idea/refinement/02-architecture-refinement.md §2.7.

A query is just a (principal, doc) pair — the EXPECTED label is NOT stored here; it is
produced at grade time by the independent oracle (bench.oracle.oracle_allow). Storing the
label would let the generator, not the oracle, define ground truth. Generation is only
BIASED toward allow/deny so both pools are populous:

  * >=3,000 deny-expected is required for FNR < 0.1% to be claimable at zero leaks
    (rule of three: 3/n < 0.001 needs n >= 3000).
  * A populous allow pool keeps FPR (< 2%) a meaningful rate rather than noise.

The corpus is a total function of the seed, so two runs replay byte-identically.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from precedent_memory.bench.seed import CANONICAL_SEED
from precedent_memory.bench.topology import Manifest

N_QUERIES = 10000


@dataclass(frozen=True)
class Query:
    index: int
    principal_ext_id: str
    doc_index: int
    lean: str            # 'allow' | 'deny' — generation bias only; NOT the ground-truth label


def build_queries(manifest: Manifest, seed: int = CANONICAL_SEED,
                  n: int = N_QUERIES) -> tuple[Query, ...]:
    # Distinct RNG stream from the topology (which used `seed` directly) so query
    # pairing is independent of doc/principal construction yet still deterministic.
    rng = random.Random(seed * 2654435761 & 0xFFFFFFFF)

    admins = [p.external_id for p in manifest.principals
              if len(p.role_indices) == len(manifest.roles)]
    regulars = [p.external_id for p in manifest.principals
                if 0 < len(p.role_indices) < len(manifest.roles)]
    nobodies = [p.external_id for p in manifest.principals if len(p.role_indices) == 0]
    underprivileged = regulars + nobodies

    public_docs = [d.index for d in manifest.docs if d.category == "public"]
    clean_restricted = [d.index for d in manifest.docs
                        if d.category in ("single", "multi", "derived")]
    failclosed = [d.index for d in manifest.docs
                  if d.category in ("revoked", "stale", "unverified", "tombstoned")]

    queries: list[Query] = []
    for i in range(n):
        if i % 2 == 0:
            # allow-lean: public (anyone) or a clean restricted doc paired with an admin
            # (holds every role -> allow) most of the time.
            if public_docs and rng.random() < 0.35:
                doc = rng.choice(public_docs)
                prin = rng.choice(manifest.principals).external_id
            else:
                doc = rng.choice(clean_restricted or public_docs)
                prin = (rng.choice(admins) if rng.random() < 0.80
                        else rng.choice(underprivileged or admins))
            lean = "allow"
        else:
            # deny-lean: a fail-closed doc (deny for everyone) or a clean restricted doc
            # paired with an under-privileged principal (likely missing a required role).
            if failclosed and rng.random() < 0.55:
                doc = rng.choice(failclosed)
                prin = rng.choice(manifest.principals).external_id
            else:
                doc = rng.choice(clean_restricted or failclosed)
                prin = rng.choice(underprivileged or admins)
            lean = "deny"
        queries.append(Query(index=i, principal_ext_id=prin, doc_index=doc, lean=lean))
    return tuple(queries)


def queries_to_list(queries: tuple[Query, ...]) -> list[dict]:
    """Serialisable form for the reproducibility test + committed raw JSON."""
    return [{"index": q.index, "principal_ext_id": q.principal_ext_id,
             "doc_index": q.doc_index, "lean": q.lean} for q in queries]
