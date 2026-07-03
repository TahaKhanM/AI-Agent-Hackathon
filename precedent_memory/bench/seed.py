"""Canonical bench seed — the ONE shared constant binding T3's corpus to T1's generator.

`CANONICAL_SEED` is the fixed integer that makes the conformance-bench topology, the
10,000 ground-truth queries, and the 100-mutation extractor corpus replay
*byte-identically* across runs. T1's incident generator uses the SAME value — if the
team overrides it at G0 (Friday stand-up), T1 and T3 change this one constant TOGETHER
so both tracks stay in lockstep (see Prompts/03-ultracode-t1-completion.md §"Canonical G0 seed").

grep-anchor: this module holds the ONE authoritative definition of 4207 in code; every
other reference imports `CANONICAL_SEED` from here (topology, queries, mutation corpus,
README). Do not re-type the literal elsewhere.
"""
from __future__ import annotations

# Shared with T1's incident generator — override together at G0.
CANONICAL_SEED = 4207
