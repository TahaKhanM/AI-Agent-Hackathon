"""Trigger the in-process orchestrator for one incident.  [owner T1, task T1-10]

Usage: python scripts/drive_incident.py <n> [--flake] [--hold] [--console URL]
POSTs to the same-process demo server's /api/drive/{n}, which runs the REAL loop inside the
console process (sharing the memory db, lighting the live trace panel). n=1 slow-path, n=2
fast-path (STANDING, zero-LLM), n=3 refused (rights). --flake arms the one-shot verification
failure first (the recovery beat). --hold PAUSES the slow-path at the gate for a human to
Approve/Reject in the console (the REAL held gate) instead of auto-approving. Requires
`make sim` running.
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.request


def _post(url: str) -> dict:
    req = urllib.request.Request(url, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 — localhost demo trigger
        return json.loads(r.read())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int, choices=(1, 2, 3))
    ap.add_argument("--flake", action="store_true", help="arm the recovery-beat flake first")
    ap.add_argument("--hold", "--no-approve", dest="hold", action="store_true",
                    help="pause the slow-path at the gate for a human (the REAL held gate) "
                         "instead of auto-approving — resolve via the console Approve button")
    ap.add_argument("--console", default=os.environ.get("PRECEDENT_CONSOLE_URL",
                                                         "http://127.0.0.1:8000"))
    args = ap.parse_args()
    base = args.console.rstrip("/")
    if args.flake:
        out = _post(f"{base}/api/drive/{args.n}/flake")
    else:
        q = "?hold=true" if args.hold else ""
        out = _post(f"{base}/api/drive/{args.n}{q}")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
