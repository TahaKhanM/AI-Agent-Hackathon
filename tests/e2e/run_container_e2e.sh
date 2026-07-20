#!/usr/bin/env bash
# WP-HOST-SESSION container end-to-end — the intended `docker build && docker run + 2-session
# Playwright` sequence, for CI or a founder machine WHERE THE DOCKER DAEMON IS UP.
#
# This is DEFERRED in the authoring environment: the Docker daemon is down there (see
# CLAUDE.md INFRA REALITY), so this script is committed to be run where infra permits — it is
# never executed as part of `make test`. It reuses the exact two-concurrent-session isolation
# e2e (tests/e2e/test_session_isolation_e2e.py) but points it at the RUNNING PRODUCT IMAGE via
# PRECEDENT_E2E_BASE_URL, so the container — not a throwaway uvicorn — is what gets proven.
#
# Prereqs on the runner: a working `docker`, and `.venv` with Playwright + Chromium installed
# (`uv pip install playwright && .venv/bin/playwright install chromium`).
#
# Usage:   tests/e2e/run_container_e2e.sh
set -euo pipefail

IMAGE="precedent-demo:e2e"
NAME="precedent-demo-e2e"
PORT="${PRECEDENT_E2E_PORT:-8000}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY="${ROOT}/.venv/bin/python"

cleanup() { docker rm -f "${NAME}" >/dev/null 2>&1 || true; }
trap cleanup EXIT

echo "==> docker build ${IMAGE}"
docker build -t "${IMAGE}" "${ROOT}"

echo "==> docker run ${NAME} (offline/airplane image — no VENICE_API_KEY baked in)"
cleanup
docker run -d --name "${NAME}" -p "${PORT}:8000" "${IMAGE}"

echo "==> waiting for the container to become healthy on :${PORT}"
for _ in $(seq 1 60); do
  if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    healthy=1; break
  fi
  sleep 1
done
[ "${healthy:-0}" = 1 ] || { echo "container never became healthy"; docker logs "${NAME}"; exit 1; }

echo "==> driving TWO concurrent browser sessions against the CONTAINER"
PRECEDENT_E2E_BASE_URL="http://127.0.0.1:${PORT}" \
  "${PY}" -m pytest "${ROOT}/tests/e2e/test_session_isolation_e2e.py" -v

echo "==> container 2-session isolation e2e PASSED"
