#!/usr/bin/env python3
"""Optional LIVE Jira smoke test — OFF by default, guarded, never prints secrets.

Run:  PRECEDENT_LIVE_JIRA_SMOKE=1 python3 scripts/jira_smoke.py   (or `make jira-smoke`)

Reads JIRA_* + JIRA_RUNBOOK_ISSUES from the environment, calls the real
JiraPermissionSource.snapshot() over the network, and prints ONLY counts and source
refs — never a token, URL, or response body. Fails closed (non-zero exit) if the
source is unconfigured or unavailable.
"""
from __future__ import annotations

import os
import sys


def main() -> int:
    if os.environ.get("PRECEDENT_LIVE_JIRA_SMOKE") != "1":
        print("live Jira smoke disabled — set PRECEDENT_LIVE_JIRA_SMOKE=1 to enable")
        return 0
    from precedent_memory.sync import JiraPermissionSource, PermissionSourceUnavailable

    src = JiraPermissionSource()
    if not src.configured:
        print("Jira NOT configured (missing JIRA_* env) — failing closed")
        return 1
    try:
        snap = src.snapshot()
    except PermissionSourceUnavailable as exc:
        print(f"Jira unavailable (fail-closed): {exc}")
        return 1
    print(f"snapshot OK — {len(snap)} runbook source(s): {list(snap.keys())}")
    for ref, spec in snap.items():
        print(f"  {ref}: constraints={len(spec['constraints'])} revoked={spec['revoked']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
