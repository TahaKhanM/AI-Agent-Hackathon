"""B1 dry-run — drive the LIVE Watcher chat handler through the full loop, offline.

No Agentverse, no network: an in-process MediaCo sim (TestClient) + a seeded memory db.
Exercises exactly what an ASI:One chat to the registered Watcher runs:

  slow-path : report incident 1 -> ONE approval message -> "approve" -> execute -> audit hash
  STANDING  : report incident 2 (pre-promoted) -> zero-LLM fast-path -> ~15s, no prompt
  refusal   : report incident 3 as scheduling-ops -> denied_count + owner team only (no body)
  fail-closed: a dropped gate expires -> a late "approve" never executes

Run:  .venv/bin/python scripts/dryrun_watcher_chat.py
"""
from __future__ import annotations

import os

# Airplane-mode: point Venice at an unreachable URL BEFORE precedent.venice is imported
# (its BASE_URL is read at import time), so the slow-path rationale (a PROPOSE-only prose
# call) degrades to its canned fallback with NO network. The STANDING fast-path makes zero
# venice calls regardless (proven by the spy test tests/test_watcher_live_loop.py).
os.environ.setdefault("VENICE_BASE_URL", "http://127.0.0.1:9/unreachable")
os.environ.setdefault("PRECEDENT_AGENTS_OFFLINE", "1")

import tempfile  # noqa: E402
from datetime import timedelta  # noqa: E402
from pathlib import Path  # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

from agents import watcher  # noqa: E402
from console.demo_state import DemoState  # noqa: E402
from precedent import ladder  # noqa: E402
from precedent.tools import SimTools  # noqa: E402
from precedent_memory import db  # noqa: E402

SCHED_CK = "scheduler|SCH-DUP-002|schedule_item"


def _hr(title: str) -> None:
    print("\n" + "=" * 78 + f"\n{title}\n" + "=" * 78)


def main() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="watcher-dryrun-"))
    mem_path = str(tmp / "mem.db")
    console = DemoState(db_path=mem_path)          # seeds the 3 demo records + ACLs + principals
    conn = db.connect(mem_path)

    os.environ["PRECEDENT_SIM_DB"] = str(tmp / "sim.db")
    from sim.app import app
    with TestClient(app) as client:
        client.get("/health")
        sim = SimTools(client=client)
        pending: dict = {}

        _hr("1) SLOW-PATH — report incident 1 -> ONE gate message")
        sender = "agent1qHUMANdemoSender"
        r1 = watcher.serve_chat_turn(
            "hiya the epg guide is blank for the 9pm slot (incident 1), can someone sort it",
            sender, conn=conn, tools=sim, pending=pending)
        print(r1)

        _hr("2) approve -> execute -> audit-hash reply (approver = sender verbatim)")
        r2 = watcher.serve_chat_turn("approve", sender, conn=conn, tools=sim, pending=pending)
        print(r2)

        _hr("3) STANDING repeat-class — report incident 2 (pre-promoted) -> zero-LLM ~15s")
        ladder.promote(SCHED_CK, "ops-lead", conn=conn, force=True)
        r3 = watcher.serve_chat_turn(
            "flagging a duplicate slot, same show twice overlapping (incident 2)",
            "agent1qREPEATcaller", conn=conn, tools=sim, pending=pending)
        print(r3)

        _hr("4) REFUSAL — report incident 3 as scheduling-ops -> count + owner ONLY")
        r4 = watcher.serve_chat_turn(
            "a title still live on demand but the licence expired, exclusivity breach (incident 3)",
            "agent1qX", conn=conn, tools=sim, pending=pending, principal="scheduling-ops")
        print(r4)

        _hr("5) FAIL-CLOSED — open a gate, force expiry, a late 'approve' never executes")
        dropper = "agent1qDROPcaller"
        print(watcher.serve_chat_turn("epg guide blank 9pm slot incident 1",
                                      dropper, conn=conn, tools=sim, pending=pending)[:80] + " ...")
        conn.execute("UPDATE approval SET expires_at=? "
                     "WHERE incident_id='INC-1' AND status='pending'",
                     ((db.utcnow() - timedelta(minutes=1)).isoformat(),))
        conn.commit()
        r5 = watcher.serve_chat_turn("approve", dropper, conn=conn, tools=sim, pending=pending)
        print("late approve ->", r5)

    conn.close()
    console.conn.close()
    print("\n[dry-run complete] full loop exercised offline — "
          "no network, no LLM on the standing path.")


if __name__ == "__main__":
    main()
