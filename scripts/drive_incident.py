"""Drive one incident through the REAL orchestrator, live.  [owner T1, task T1-10]

Usage: python scripts/drive_incident.py <n> [--principal P] [--approve]
Fetches incident <n> from the running sim, runs orchestrator.handle over the shared
memory db, and streams every hop to the running console's live trace panel. This is the
on-stage action (and the airplane-mode rehearsal): `make sim` in one shell, this in
another. n=1 slow-path (approval), n=2 fast-path (STANDING, zero-LLM), n=3 refused (rights).
"""
from __future__ import annotations

import argparse
import os

from precedent import console_link, orchestrator
from precedent.contracts import ApprovalDecision, IncidentEvent
from precedent.tools import SimTools
from precedent_memory import db


def _auto_approve(principal: str):
    def approve(req):
        return ApprovalDecision(incident_id=req.incident_id, plan_hash=req.plan_hash,
                                decision="approve", approver_principal=principal,
                                channel="console", decided_at=db.utcnow_iso())
    return approve


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int, choices=(1, 2, 3))
    ap.add_argument("--principal", default="scheduling-ops")
    ap.add_argument("--approve", action="store_true",
                    help="auto-approve the slow-path gate (rehearsal); omit for a real human click")
    ap.add_argument("--console", default=os.environ.get("PRECEDENT_CONSOLE_URL",
                                                         "http://127.0.0.1:8000"))
    args = ap.parse_args()

    mem_path = os.environ.get("PRECEDENT_MEMORY_DB", "data/precedent.db")
    sim = SimTools()   # PRECEDENT_SIM_URL
    trace = console_link.http_trace(args.console)
    conn = db.connect(mem_path)
    try:
        p = sim.incident(args.n)
        inc = IncidentEvent(incident_id=p["incident_id"], raw_text=p["raw_text"],
                            source="sim", observed_at=p["observed_at"])
        res = orchestrator.handle(inc, structured=p["structured"], conn=conn, tools=sim,
                                  principal=args.principal, trace=trace,
                                  approve=_auto_approve("ops-lead") if args.approve else None)
        print(f"incident {args.n}: verified={res.verified} rolled_back={res.rolled_back} "
              f"outcome={res.step_results[0].get('outcome')}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
