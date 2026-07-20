# Playwright + Docker end-to-end harness (WP-HOST-SESSION)

Dev-only browser/container harness for the hosted-demo session model. It proves — through **real
Chromium sessions**, not just Python — that two concurrent visitors to the served console never
touch each other's world, and it pins a **perceptual visual baseline** of the shared design
system. None of this ships in the product image (`tests/` is `.dockerignore`d).

## What's here

| File | What it does |
|---|---|
| `conftest.py` | `live_server` fixture (boots `scripts.demo_server:app` under uvicorn in airplane mode, or targets an external server via `PRECEDENT_E2E_BASE_URL`) + a session-scoped headless `browser`. |
| `test_session_isolation_e2e.py` | Two Chromium contexts = two `precedent_sid` cookies. Asserts ladder / audit-chain / close-ledger and held approvals are all per-session. The browser-level companion to the authoritative `tests/test_session_isolation.py` (pure-Python TestClient gate). |
| `test_visual_baseline.py` | Renders `/` at 1380 / 768 / 375 px, computes a 256-bit perceptual dHash, compares to `baseline/visual_baseline.json` within a Hamming tolerance. |
| `baseline/` | Committed baseline: `visual_baseline.json` (the hashes) + tiny grayscale thumbnails per breakpoint for human review. |
| `run_container_e2e.sh` | The `docker build && docker run` + 2-session Playwright sequence, for CI / a founder box **where the Docker daemon is up** (deferred in the authoring env). |

## Collection guard (bare checkout stays green)

These tests import Playwright at collection time. The guard in `tests/conftest.py`
(`_browser_stack_available` → `_e2e_collect_ignore`) drops the whole `tests/e2e` directory from
collection when Playwright **or** its Chromium build is absent — the same "deselect, don't skip,
don't error" pattern as the rails guard. So a plain `.venv` without the browser stack runs the
suite with **zero unexplained skips**; only an environment that actually has Chromium runs these.

## Running locally

```bash
uv pip install -e ".[e2e]"                       # playwright + pillow (the e2e extra)
.venv/bin/playwright install chromium            # the browser build itself
.venv/bin/python -m pytest tests/e2e -v          # runs once the browser stack is present
```

Regenerate the visual baseline after an **intentional** reskin (writes JSON + thumbnails, skips):

```bash
PRECEDENT_UPDATE_VISUAL_BASELINE=1 .venv/bin/python -m pytest tests/e2e/test_visual_baseline.py
```

## Running against the container (CI / founder — Docker daemon required)

```bash
tests/e2e/run_container_e2e.sh
```

This builds the product image, runs it, waits for `/health`, then runs the **same** two-session
isolation e2e against the container via `PRECEDENT_E2E_BASE_URL`. **Deferred in the authoring
environment** — the Docker daemon is down there (CLAUDE.md INFRA REALITY), so the sequence is
committed to run where infra permits; it is never part of `make test`.

## Static Docker/session-model consistency (verified here without building)

- **Per-session temp dirs are writable in-container.** `SessionStore.root` and the cold-open
  templates live under `tempfile` (`/tmp/...`), writable in `python:3.13-slim`. No committed
  `data/cold-open/` snapshot exists, so templates are generated at first use from committed
  `data/raw` + `data/kb` (both ship) — offline, no single global world assumed.
- **No runtime Playwright dependency.** Nothing outside `tests/` imports Playwright, and `tests`
  is now `.dockerignore`d, so the browser stack never enters the image.
- **Open issue (flagged, not fixed here — lives in the given session core):** the middleware
  exempts only `/static`, so every `/health` probe (Render's `healthCheckPath`) resolves a *new*
  cookieless session. Under periodic probing these accumulate until the 20 s tick / TTL eviction
  reaps them. Consider exempting `/health` from session resolution, or answering it without
  touching the store.
- **Vestigial in production:** `scripts/docker_start.sh` still seeds `data/sim.db` +
  `data/precedent.db` and `run_demo.py` still boots the out-of-process sim on `:8100`; per-cookie
  drives now use in-process per-session sims (`sim.factory.make_sim_app`). Harmless, but that sim
  process and those seed files are no longer on the production drive path.
