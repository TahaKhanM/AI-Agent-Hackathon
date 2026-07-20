"""Rails-collection guard.

The four rails test files below import ``agents.*``, which pulls in
``uagents`` / ``uagents_core`` at module import time. On a checkout WITHOUT
the ``agents`` extra installed, that import raises ``ModuleNotFoundError``
during pytest *collection* — surfacing as collection ERRORS rather than a
clean skip.

To keep a bare checkout green we DESELECT those files via ``collect_ignore``
when ``uagents`` is not importable. In our ``.venv`` (extra installed) the
list is empty, so all four are collected and the suite stays at its full
count with zero skips.

The decision lives in the pure helper ``_rails_collect_ignore`` so it is
directly unit-testable without manipulating the interpreter's import state.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

# P0.2 — the rails test modules build their agent singletons at IMPORT time (during pytest
# collection), which calls agents.common.resolve_seed BEFORE any per-test fixture runs. With the
# fail-closed seed guard, an unset seed in a public context now raises. The test session is an
# OFFLINE rehearsal (no mailbox is ever opened), so declare that here — before collection — so
# the import-time build takes the deterministic dev placeholder. Individual tests may still
# monkeypatch this away (e.g. to assert the public-context refusal). ``setdefault`` respects an
# explicit outer-environment value.
os.environ.setdefault("PRECEDENT_AGENTS_OFFLINE", "1")

# Rails test files that import ``agents.*`` (→ uagents) at module import.
_RAILS_TEST_FILES = [
    "test_fetch_rails.py",
    "test_rails_hardening.py",
    "test_rails_wire.py",
    "test_watcher_live_loop.py",
]

# The dev-only Playwright end-to-end harness lives in this subdir. It imports playwright at
# collection time, so on a checkout WITHOUT the browser stack it must be dropped from collection
# (same rationale as the rails guard) rather than erroring or skipping.
_E2E_DIR = "e2e"


def _rails_collect_ignore(uagents_available: bool) -> list[str]:
    """Basenames to ignore during collection given uagents availability.

    Returns the four rails test basenames when uagents is NOT importable
    (so they are deselected cleanly — not collected, not skipped, not
    errored), and an empty list when uagents IS importable (so the full
    suite is collected).
    """
    if uagents_available:
        return []
    return list(_RAILS_TEST_FILES)


def _playwright_browsers_path() -> Path:
    """The directory Playwright downloads browser builds into (respects the override env var).

    Mirrors Playwright's own default-location logic so we can detect an installed Chromium
    WITHOUT importing playwright or spawning its node driver at collection time.
    """
    override = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if override and override != "0":
        return Path(override)
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "ms-playwright"
    if sys.platform.startswith("win"):
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "ms-playwright"
    return Path.home() / ".cache" / "ms-playwright"


def _browser_stack_available() -> bool:
    """True only when BOTH the playwright package and an installed Chromium build are present.

    Cheap and import-free: a package spec check plus a directory glob (no driver subprocess). The
    e2e ``browser`` fixture keeps a defensive, EXPLAINED skip for the rare half-installed case
    where a build dir exists but the binary won't launch."""
    if importlib.util.find_spec("playwright") is None:
        return False
    base = _playwright_browsers_path()
    if not base.exists():
        return False
    return any(base.glob("chromium-*")) or any(base.glob("chromium_headless_shell-*"))


def _e2e_collect_ignore(browser_available: bool) -> list[str]:
    """``[]`` when the browser stack is present (collect the e2e dir), else the e2e dir name (drop
    it cleanly — not collected, not skipped, not errored), mirroring the rails guard."""
    if browser_available:
        return []
    return [_E2E_DIR]


collect_ignore = (
    _rails_collect_ignore(importlib.util.find_spec("uagents") is not None)
    + _e2e_collect_ignore(_browser_stack_available())
)


@pytest.fixture(autouse=True)
def _drain_hosting_sessions():
    """WP-HOST-SESSION: the served console keeps a process-wide ``SessionStore`` (one per-cookie
    world each holding sqlite connections + temp db files). Non-pinned console tests create real
    sessions; without a drain they would accumulate across the whole run and exhaust file
    descriptors. Close + delete every live session after each test so state never leaks between
    tests and no FD/orphan-file piles up. Cheap no-op for tests that never create a session.
    """
    yield
    try:
        from console.session import SESSIONS
    except Exception:  # pragma: no cover - console not importable in a bare checkout slice
        return
    SESSIONS.close_all()
