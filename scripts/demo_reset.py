"""make demo-reset — restore a clean demo state in < 30s.  [owner T1, task T1-6]

Resets the sim SQLite from the committed data (DROP+rebuild), re-seeds the shared
permission-memory db fresh (records + ACLs + principals + ladder at L1), and PRE-SEEDS
incident 2's class to STANDING so the zero-LLM fast-path fires reliably on stage. A
botched on-stage run recovers by re-running this.
"""
from __future__ import annotations

import os
import time

SCHED_CLASS = "scheduler|SCH-DUP-002|schedule_item"


def main() -> None:
    t0 = time.monotonic()

    # 1) Sim: DROP + rebuild from committed data/raw + data/kb.
    from sim import core
    from sim import db as simdb
    conn = simdb.connect()
    try:
        core.reset(conn)
    finally:
        conn.close()

    # 2) Memory: delete + re-seed fresh (records, ACLs, principals, ladder L1).
    mem_path = os.environ.get("PRECEDENT_MEMORY_DB", "data/precedent.db")
    for suffix in ("", "-wal", "-shm"):
        p = mem_path + suffix
        if os.path.exists(p):
            os.remove(p)
    from console.demo_state import DemoState
    state = DemoState(db_path=mem_path)

    # 3) Pre-seed incident 2's class at STANDING (fast-path demo) via the ladder.
    from precedent import ladder
    ladder.promote(SCHED_CLASS, "ops-lead", conn=state.conn, force=True)

    dt = time.monotonic() - t0
    counts = simdb.counts(simdb.connect())
    print(f"demo-reset OK in {dt:.1f}s")
    print(f"  sim db: {simdb.db_path()}  counts: {counts}")
    print(f"  memory db: {mem_path}  (fast-path class {SCHED_CLASS} pre-seeded STANDING)")
    state.conn.close()


if __name__ == "__main__":
    main()
