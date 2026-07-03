"""Demo console — server-rendered page + SSE, NO frontend framework.  [STUB — owner T2, task T2-3]

Spec: Idea/refinement/02 §4 + 04-demo-and-video-script.md §1.2.

BUILD ORDER IS LOAD-BEARING (the 18:00 vertical-slice gate needs exactly these first):
  1. Baseline Bar (CSS-width animation off one elapsed-seconds value)
  2. Approve / Promote to Standing Approval / Revoke buttons
Then: incident feed, streamed trace (SSE), audit JSON tail, degraded banner, provenance
footer, robustness chip slot, cumulative close strip.

Terminology: L3 = "Standing Approval", never "Autonomous". The Revoke button is always
visible on a Standing-Approval class.
"""
from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="Precedent Console")


@app.get("/health")
def health():
    return {"status": "stub", "todo": "T2-3: Baseline Bar + 3 buttons FIRST — see 02 §4, 04 §1.2"}
