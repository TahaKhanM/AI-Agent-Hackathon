"""make sim — boot the MediaCo sim + the judge console (with T1 in-process).  [task T1-6]

Two processes: the MediaCo sim (uvicorn sim.app:app, :8100, its own db) and the SAME-PROCESS
demo server (scripts/demo_server:app = the console + T1's in-process drive endpoint, :8000).
Running T1's orchestrator inside the console process means only ONE process writes the
shared memory db (no cross-process SQLite contention) and every loop hop lights the live
trace panel directly. Run `make demo-reset` first. Ctrl-C stops both.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys

SIM_PORT = os.environ.get("PRECEDENT_SIM_PORT", "8100")
CONSOLE_PORT = os.environ.get("PRECEDENT_CONSOLE_PORT", "8000")
# Default localhost-only (airplane-mode safe). Set PRECEDENT_HOST=0.0.0.0 to let
# other devices on the same network reach the console.
HOST = os.environ.get("PRECEDENT_HOST", "127.0.0.1")


def main() -> None:
    env = dict(os.environ)
    env.setdefault("PRECEDENT_SIM_DB", "data/sim.db")
    env.setdefault("PRECEDENT_MEMORY_DB", "data/precedent.db")   # shared: console + in-proc T1
    env.setdefault("PRECEDENT_SIM_URL", f"http://127.0.0.1:{SIM_PORT}")

    procs = [
        subprocess.Popen([sys.executable, "-m", "uvicorn", "sim.app:app",
                          "--host", "127.0.0.1", "--port", SIM_PORT,
                          "--log-level", "warning"], env=env),
        subprocess.Popen([sys.executable, "-m", "uvicorn", "scripts.demo_server:app",
                          "--host", HOST, "--port", CONSOLE_PORT,
                          "--log-level", "warning"], env=env),
    ]
    print(f"MediaCo sim   -> http://127.0.0.1:{SIM_PORT}/health")
    print(f"Judge console -> http://127.0.0.1:{CONSOLE_PORT}/   (T1 drives in-process)")
    print(f"Shared memory db: {env['PRECEDENT_MEMORY_DB']}   (run `make demo-reset` first)")
    print("Drive:  curl -XPOST http://127.0.0.1:8000/api/drive/1   (1 slow, 2 fast, 3 refused)")
    print("        .venv/bin/python scripts/drive_incident.py 2")
    print("Ctrl-C to stop both.")

    def _stop(*_a):
        for p in procs:
            p.terminate()
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    for p in procs:
        p.wait()


if __name__ == "__main__":
    main()
