"""Autonomy ladder: graduation, demotion, and the standing-approval fast-path.
[STUB — owner T1, task T1-5]

Spec: Idea/refinement/02-architecture-refinement.md §3.3.

- Promotion eligibility: 3 CONSECUTIVE verified L2 successes, zero rollbacks (per-class
  counter in class_ladder). Promotion itself requires a HUMAN click ("Promote to
  standing approval") — never automatic. Demotion: any verification failure or
  rollback -> class back to L1 + audit event; success counters reset.
- Fast-path: on a fingerprint match at STANDING, SKIP ALL LLM CALLS — retrieve the
  graduated record, policy-gate, snapshot, execute typed calls, verify, write
  memory+audit. This is what makes the 15s run deterministic (rule 2 + local-first).
- Terminology: L3 is "Standing Approval", NEVER "Autonomous".
"""
from __future__ import annotations


def is_standing(class_key: str) -> bool:
    """TODO T1-5: read class_ladder; True iff the class is at Standing Approval."""
    raise NotImplementedError("T1-5: ladder state — see 02 §3.3")


def on_verification_result(class_key: str, verified: bool, rolled_back: bool) -> None:
    """TODO T1-5: advance the consecutive counter on success; demote to L1 + audit on
    any failure/rollback."""
    raise NotImplementedError("T1-5: graduation/demotion — see 02 §3.3")
