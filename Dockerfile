# Precedent demo — always-on container image.
# Runs the MediaCo sim (internal :8100) + the judge console (public :$PORT) in one
# container, reseeding the demo state on boot so it comes up armed and offline.
#
# Offline by design: no VENICE_API_KEY is baked in, so every model call falls back
# to the canned rationale — no external calls, no credit burn, no secrets in the image.
FROM python:3.13-slim

WORKDIR /app
COPY . /app

# Runtime deps come from ONE source of truth — [project].dependencies in pyproject.toml.
# We `pip install .` (non-editable) so the image never hand-lists a requirement set that can
# drift away from pyproject. The wheel packages precedent*/precedent_memory/precedent_analyzer/
# precedent_pack; console/ and sim/ are served off the source tree via PYTHONPATH=/app (set in
# scripts/docker_start.sh). The dev-only [dev]/[e2e] extras (pytest, Playwright) are NOT
# installed, and tests/ is dockerignored — the image stays slim and offline-capable.
# All runtime deps ship manylinux wheels, so no compiler is needed.
RUN pip install --no-cache-dir .

# Console binds the platform port on all interfaces; sim stays loopback-internal.
ENV PRECEDENT_HOST=0.0.0.0 \
    PRECEDENT_SIM_PORT=8100 \
    PYTHONUNBUFFERED=1 \
    PORT=8000
EXPOSE 8000

CMD ["sh", "scripts/docker_start.sh"]
