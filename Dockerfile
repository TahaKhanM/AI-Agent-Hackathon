# Precedent demo — always-on container image.
# Runs the MediaCo sim (internal :8100) + the judge console (public :$PORT) in one
# container, reseeding the demo state on boot so it comes up armed and offline.
#
# Offline by design: no VENICE_API_KEY is baked in, so every model call falls back
# to the canned rationale — no external calls, no credit burn, no secrets in the image.
FROM python:3.13-slim

# Runtime deps only (all have manylinux wheels — no compiler needed). Installed
# before the source copy so this layer caches across code changes.
RUN pip install --no-cache-dir \
    "fastapi>=0.115" "uvicorn[standard]>=0.32" "pydantic>=2.9" "httpx>=0.27" \
    "python-dotenv>=1.0" "sse-starlette>=2.1" "pandas>=2.2" "numpy>=1.26" "pyyaml>=6.0"

WORKDIR /app
COPY . /app

# Console binds the platform port on all interfaces; sim stays loopback-internal.
ENV PRECEDENT_HOST=0.0.0.0 \
    PRECEDENT_SIM_PORT=8100 \
    PYTHONUNBUFFERED=1 \
    PORT=8000
EXPOSE 8000

CMD ["sh", "scripts/docker_start.sh"]
