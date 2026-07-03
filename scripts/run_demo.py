"""make sim — boot the MediaCo sim + the judge console together.  [owner T1, task T1-6]

Launches the sim (uvicorn sim.app:app, port 8100) and the console (uvicorn console.app:app,
port 8000) as child processes sharing the demo dbs via env. T1's driver
(scripts/drive_incident.py) then resolves an incident and streams every hop to the
console's POST /api/trace — which the console process handles, lighting its live trace
panel (push_trace stores in-memory on the STATE singleton; an HTTP post from the driver
reaches that same process). The durable feed/audit/baseline panels light from the shared
db regardless. Ctrl-C stops both.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys

SIM_PORT = os.environ.get("PRECEDENT_SIM_PORT", "8100")
CONSOLE_PORT = os.environ.get("PRECEDENT_CONSOLE_PORT", "8000")


def main() -> None:
    env = dict(os.environ)
    env.setdefault("PRECEDENT_SIM_DB", "data/sim.db")
    env.setdefault("PRECEDENT_MEMORY_DB", "data/precedent.db")   # shared: console + T1
    env.setdefault("PRECEDENT_SIM_URL", f"http://127.0.0.1:{SIM_PORT}")

    procs = [
        subprocess.Popen([sys.executable, "-m", "uvicorn", "sim.app:app",
                          "--port", SIM_PORT, "--log-level", "warning"], env=env),
        subprocess.Popen([sys.executable, "-m", "uvicorn", "console.app:app",
                          "--port", CONSOLE_PORT, "--log-level", "warning"], env=env),
    ]
    print(f"MediaCo sim   -> http://127.0.0.1:{SIM_PORT}/health")
    print(f"Judge console -> http://127.0.0.1:{CONSOLE_PORT}/")
    print(f"Shared memory db: {env['PRECEDENT_MEMORY_DB']}   (run `make demo-reset` first)")
    print("Drive an incident:  .venv/bin/python scripts/drive_incident.py 1   (2=fast-path)")
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
