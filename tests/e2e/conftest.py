"""Fixtures for the dev-only Playwright end-to-end harness (WP-HOST-SESSION).

These tests drive REAL browser sessions against a REAL uvicorn server running the served
console app (``scripts.demo_server:app`` = ``console.app`` + the in-process drive routes) — the
one surface a hosted visitor actually hits. They are the browser-level companion to the
authoritative pure-Python isolation gate in ``tests/test_session_isolation.py``.

They are guarded OUT of a bare checkout by the collection guard in ``tests/conftest.py``: when
Playwright or its Chromium build is absent, the whole ``tests/e2e`` directory is dropped from
collection (never collected, never skipped, never errored) — exactly like the rails guard. So a
plain checkout stays green with zero unexplained skips.

BOTH fixtures are FUNCTION-scoped on purpose:

  * ``sync_playwright().start()`` parks a RUNNING asyncio loop on the MAIN thread until
    ``stop()``. Under ``asyncio_mode = auto`` a leaked loop makes pytest-asyncio's per-test
    runner raise "cannot be called from a running event loop" for EVERY later async test. Tearing
    the browser down per test guarantees the loop is gone before any sibling test runs, regardless
    of collection order.
  * ``live_server`` takes the function-scoped ``monkeypatch`` to set airplane env via
    ``setenv`` — auto-reverted at teardown, so the unreachable-Venice config never leaks into the
    rest of the suite.

AIRPLANE MODE: the server boots with ``VENICE_BASE_URL`` pointed at an unreachable loopback port
and no API key, so any slow-path rationale attempt is refused instantly and falls back to the
canned string WITHOUT a network call — the model-call counter stays 0 and runs are deterministic
(mirrors CLAUDE.md's bench-extractor pattern). This is dev-only; the product image never imports it.
"""
from __future__ import annotations

import socket
import threading
import time

import httpx
import pytest


def _free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _wait_healthy(base: str, *, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if httpx.get(base + "/health", timeout=1).status_code == 200:
                return
        except Exception:  # noqa: BLE001 - server not up yet
            time.sleep(0.15)
    # pragma: no cover
    raise RuntimeError(f"server {base} did not become healthy in {timeout:.0f}s")


@pytest.fixture
def live_server(monkeypatch) -> str:
    """Yield the base URL of a served console instance.

    If ``PRECEDENT_E2E_BASE_URL`` is set (the CI/founder container path — see
    ``tests/e2e/run_container_e2e.sh``), target THAT already-running server instead of booting
    one, so the exact same isolation e2e runs against ``docker run`` of the product image.

    Otherwise boot ``scripts.demo_server:app`` under uvicorn in a daemon thread, in airplane mode.
    Per-cookie sessions are created by the middleware exactly as for a real visitor."""
    import os

    external = os.environ.get("PRECEDENT_E2E_BASE_URL")
    if external:
        external = external.rstrip("/")
        _wait_healthy(external)
        yield external
        return

    # Airplane mode via monkeypatch (auto-reverted): an unreachable base URL means any slow-path
    # rationale POST is refused instantly (ECONNREFUSED) -> canned fallback, no external call,
    # model-call counter stays 0. venice reads these at call time and the server is in-process.
    monkeypatch.setenv("PRECEDENT_AGENTS_OFFLINE", "1")
    monkeypatch.setenv("VENICE_BASE_URL", "http://127.0.0.1:9/unreachable")
    monkeypatch.delenv("VENICE_API_KEY", raising=False)

    import uvicorn

    import scripts.demo_server as ds

    port = _free_port()

    class _Server(uvicorn.Server):
        def install_signal_handlers(self) -> None:  # never touch the test process signal handlers
            pass

    config = uvicorn.Config(ds.app, host="127.0.0.1", port=port, log_level="warning",
                            lifespan="on")
    server = _Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    base = f"http://127.0.0.1:{port}"
    try:
        _wait_healthy(base)
        yield base
    finally:
        server.should_exit = True
        thread.join(timeout=10)


@pytest.fixture
def browser():
    """A headless Chromium, started + fully stopped per test (see module docstring for why).

    If the browser stack is half-installed (build dir present but launch fails), skip with a clear
    reason rather than erroring — an EXPLAINED skip, never a mystery."""
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # noqa: BLE001 - collection guard should prevent this
        pytest.skip(f"playwright not importable: {exc}")

    pw = None
    br = None
    try:
        pw = sync_playwright().start()
        br = pw.chromium.launch(headless=True)
    except Exception as exc:  # noqa: BLE001 - browser binary missing/broken -> explained skip
        if br is not None:
            br.close()
        if pw is not None:
            pw.stop()
        pytest.skip(f"chromium not launchable: {exc}")

    try:
        yield br
    finally:
        br.close()
        pw.stop()   # clears the main-thread event loop before any sibling test runs
