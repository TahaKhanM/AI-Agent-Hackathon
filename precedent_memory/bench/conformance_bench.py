"""Sponsor-protocol conformance bench.  [STUB — owner T3, tasks T3-3/T3-6/T3-8]

Spec: Idea/refinement/02-architecture-refinement.md §2.7.

TODO T3-3: generate topology (5 hierarchy levels, 20 roles, 1,000 ACL-tagged docs) +
           10,000 ground-truth allow/deny queries incl. >=3,000 deny-expected.
TODO T3-6: independent oracle = a naive lineage-conjunction walk over acl_source with
           NO bitmap and NO import from store/retrieve. FNR/FPR = bitmap-vs-oracle
           disagreement. This decoupling is why FNR=0 is not circular.
TODO T3-8: run vs merged main; emit RESULTS.md (measured vs threshold vs pass/fail for
           FNR<0.1% / FPR<2% / P50<50ms / P99<200ms / overhead<100ms / derived-memory
           correctness>99% / ACL-drift<0.5% / TTC<5min / 100% audit coverage).

Run: python -m precedent_memory.bench.conformance_bench  (make bench)
"""
from __future__ import annotations


def main() -> None:
    raise NotImplementedError("T3-3/6/8: conformance bench — see 02 §2.7")


if __name__ == "__main__":
    main()
