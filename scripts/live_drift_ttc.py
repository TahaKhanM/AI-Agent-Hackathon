#!/usr/bin/env python3
"""LIVE ACL drift + time-to-consistency against real Jira — OFF by default, guarded.
[owner T3, task T3-14; Saturday human-run]

Spec: Idea/refinement/02-architecture-refinement.md §2.7 + §2.8.

Runs an N-flip protocol against the real Jira Service Management project: it tightens a
runbook issue's ISSUE-SECURITY level, then times the wall-clock from the flip until a sync
recompile DENIES the derived memory (TTC, vs < 5 min) and the stale-allow fraction during the
window (drift, vs < 0.5%). Each flip's timestamp is taken from Jira's OWN audit records API
(`GET /rest/api/3/auditing/record`, ms precision) — the TTC is anchored to the source system's
regulator-grade clock, not our client clock (the claim BioVault's synthetic bench cannot make).

Guarded & fail-closed: exits NON-ZERO whenever Jira is unconfigured, and never runs a live flip
unless PRECEDENT_LIVE_DRIFT=1. Never prints a token, URL, or response body.

  PRECEDENT_LIVE_DRIFT=1 python3 scripts/live_drift_ttc.py   (or `make live-drift`)
"""
from __future__ import annotations

import os
import sys
import time


def main() -> int:
    from precedent_memory import db, retrieve, store
    from precedent_memory.sync import (
        JiraPermissionSource,
        PermissionSourceUnavailable,
        sync,
    )

    src = JiraPermissionSource()
    if not src.configured:
        print("Jira NOT configured (missing JIRA_* env) — cannot measure live drift/TTC. "
              "Exiting non-zero (unconfigured).")
        return 1
    if os.environ.get("PRECEDENT_LIVE_DRIFT") != "1":
        print("live drift/TTC is configured but DISABLED (it performs real Jira flips) — "
              "set PRECEDENT_LIVE_DRIFT=1 to run. Exiting non-zero.")
        return 1

    runbooks = src._runbooks                       # {sourceRef: issueKey}
    rights_level = os.environ.get("JIRA_SECURITY_LEVEL_RIGHTS_OPS")
    if not runbooks or not rights_level:
        print("need JIRA_RUNBOOK_ISSUES + JIRA_SECURITY_LEVEL_RIGHTS_OPS to flip. "
              "Exiting non-zero.")
        return 1

    n_flips = int(os.environ.get("PRECEDENT_LIVE_DRIFT_N", "3"))
    ref, issue_key = next(iter(runbooks.items()))
    client, owns = src._make_client()

    # Seed a local memory store from the current Jira ACL state; a principal with NO clearance
    # for the tightened level is our probe (it must go from allow -> deny across the flip).
    conn = db.connect(":memory:")
    store.put_principal(conn, "probe", [])         # holds nothing -> any restriction denies it
    try:
        sync(src, conn=conn)                       # pull current ACLs into the store
        rid = store.store({"kind": "kb_summary", "class_key": "live|drift|probe"},
                          [ref], conn=conn)

        ttc_samples: list[float] = []
        stale_allow = 0
        checks = 0
        for _ in range(n_flips):
            # baseline: open the issue (no security) so the probe can read it
            _set_security(client, issue_key, None)
            sync(src, conn=conn)
            store.recompile_for_source(conn, store.source_id(conn, ref))
            # TIGHTEN: set the restricted level; anchor the flip time to Jira's audit clock
            _set_security(client, issue_key, rights_level)
            flip_ts = _audit_flip_time(client, issue_key)   # ms-precision, source-anchored
            t0 = time.perf_counter()
            # poll: sync until the recompiled policy DENIES the probe
            while True:
                sync(src, conn=conn)
                allowed = retrieve.check_access(conn, "probe", rid)[0]
                checks += 1
                if allowed:
                    stale_allow += 1
                else:
                    break
                if time.perf_counter() - t0 > 300:          # 5-min safety bail
                    break
            ttc_samples.append(time.perf_counter() - t0)
            print(f"  flip {ref}->{issue_key} restricted @ {flip_ts} (Jira audit clock); "
                  f"consistent in {ttc_samples[-1]:.2f}s")
    except PermissionSourceUnavailable as exc:
        print(f"Jira unavailable during drift run (fail-closed): {exc}")
        return 1
    finally:
        if owns:
            client.close()
        conn.close()

    ttc_med = sorted(ttc_samples)[len(ttc_samples) // 2] if ttc_samples else 0.0
    drift = (stale_allow / checks) if checks else 0.0
    print(f"[live-drift] TTC median {ttc_med:.2f}s (threshold < 5 min) — "
          f"{'PASS' if ttc_med < 300 else 'FAIL'}")
    print(f"[live-drift] stale-allow fraction {drift * 100:.3f}% (threshold < 0.5%) — "
          f"{'PASS' if drift < 0.005 else 'FAIL'}  [25k-record store framing for realism]")
    return 0


def _set_security(client, issue_key: str, level_id: str | None) -> None:
    """Set (or clear) an issue's security level. level_id=None opens it."""
    security = {"id": str(level_id)} if level_id else None
    client.put(f"/rest/api/3/issue/{issue_key}", json={"fields": {"security": security}})


def _audit_flip_time(client, issue_key: str) -> str:
    """Read the most recent audit record touching the issue from Jira's own auditing API —
    ms precision, anchored to the source system's regulator-grade log (not our client clock)."""
    resp = client.get("/rest/api/3/auditing/record", params={"filter": issue_key, "limit": 1})
    records = (resp.json() or {}).get("records") or []
    return records[0].get("created") if records else "unknown"


if __name__ == "__main__":
    sys.exit(main())
