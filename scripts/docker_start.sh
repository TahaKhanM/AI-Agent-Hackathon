#!/usr/bin/env sh
# Container entrypoint: seed the demo state, then boot sim + console.
# The console binds the platform-provided $PORT (Render sets it; default 8000).
set -e

export PRECEDENT_CONSOLE_PORT="${PORT:-8000}"

# The image installs only dependencies (no editable project install), so the repo
# root must be importable for `sim`, `console`, `precedent*` when scripts run with
# sys.path[0] = scripts/.
export PYTHONPATH="/app${PYTHONPATH:+:$PYTHONPATH}"

# Rebuild the sim + memory dbs from committed data. WP-DEMO §b: the graduation class opens at
# L2/streak-0 (NOT force-pre-seeded to STANDING) — the visitor earns the zero-LLM fast path live.
# Idempotent; safe on every boot.
python scripts/demo_reset.py

# Boot the MediaCo sim (127.0.0.1:8100) and the console (0.0.0.0:$PORT). Blocks.
exec python scripts/run_demo.py
