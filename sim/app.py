"""MediaCo simulated services.  [STUB — owner T1, task T1-2]

Spec: Idea/refinement/01-realistic-data-plan.md + 02 §4.3.

One FastAPI app, 4 routers (scheduler / rights / publisher / kb), one SQLite file,
seeded from committed raw public data (TVmaze GB CC BY-SA, Freeview XMLTV, CC0 Kaggle
catalogs, UCI incident log). KEEP the real data's messiness (null metadata, duplicate
titles) — it triggers incidents and is what the Conduct rubric rewards; do not sanitise.

Endpoints the demo script needs: fixed-seed incident fixtures (1/2/3 replay identically),
POST /sim/publisher/flake?once=true (the recovery beat), and the 2 restricted runbook
issues seeded with issue-security level (IDs in .env). make demo-reset resets state <30s.
"""
from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="MediaCo (Precedent sim)")


@app.get("/health")
def health():
    return {"status": "stub", "todo": "T1-2: seed from data/raw, wire 4 routers — see 01 + 02 §4.3"}
