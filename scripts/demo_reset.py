"""make demo-reset — restore a clean demo state in < 30s.  [owner T1, task T1-6]

Resets the sim SQLite from the committed data (DROP+rebuild) and re-seeds the shared
permission-memory db fresh (records + ACLs + principals + ladder). WP-DEMO §b: the boot-time
force=True STANDING pre-seed of incident 2's class is RETIRED — the graduation class opens at
L2 / streak 0 (set by DemoState._seed), and the zero-LLM fast path fires only AFTER the visitor
earns Standing Approval live through the real ladder. A botched on-stage run recovers by
re-running this.
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

    # 2) Memory: delete + re-seed fresh (records, ACLs, principals; all classes L1; the
    #    graduation class at L2/streak-0 — NOT STANDING). No force pre-seed: the visitor promotes.
    mem_path = os.environ.get("PRECEDENT_MEMORY_DB", "data/precedent.db")
    for suffix in ("", "-wal", "-shm"):
        p = mem_path + suffix
        if os.path.exists(p):
            os.remove(p)
    from console.demo_state import DemoState
    state = DemoState(db_path=mem_path)

    dt = time.monotonic() - t0
    counts = simdb.counts(simdb.connect())
    print(f"demo-reset OK in {dt:.1f}s")
    print(f"  sim db: {simdb.db_path()}  counts: {counts}")
    print(f"  memory db: {mem_path}  (graduation class {SCHED_CLASS} at L2/streak-0 — "
          f"earned to STANDING live, never force-pre-seeded)")
    state.conn.close()


if __name__ == "__main__":
    main()
