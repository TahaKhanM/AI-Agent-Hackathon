"""Tests for the rails-collection guard in ``tests/conftest.py``.

Asserts the pure helper's decision table and confirms that in THIS
environment (our ``.venv`` with the ``agents`` extra) uagents is importable,
so the four rails files are collected rather than deselected.
"""

from __future__ import annotations

import importlib.util

from tests.conftest import (
    _E2E_DIR,
    _RAILS_TEST_FILES,
    _browser_stack_available,
    _e2e_collect_ignore,
    _rails_collect_ignore,
)

_EXPECTED = [
    "test_fetch_rails.py",
    "test_rails_hardening.py",
    "test_rails_wire.py",
    "test_watcher_live_loop.py",
]


def test_helper_ignores_rails_when_uagents_absent() -> None:
    # Without uagents the four rails basenames are deselected cleanly.
    assert _rails_collect_ignore(uagents_available=False) == _EXPECTED


def test_helper_collects_all_when_uagents_present() -> None:
    # With uagents importable, nothing is ignored — full collection.
    assert _rails_collect_ignore(uagents_available=True) == []


def test_rails_file_list_matches_expected() -> None:
    assert list(_RAILS_TEST_FILES) == _EXPECTED


def test_uagents_importable_in_this_env() -> None:
    # Our .venv installs the agents extra, so the rails suite runs here.
    assert importlib.util.find_spec("uagents") is not None


# --------------------------------------------------------------------------- #
# The e2e (Playwright) collection guard — same shape as the rails guard.
# --------------------------------------------------------------------------- #
def test_e2e_helper_ignores_dir_when_browser_absent() -> None:
    # Without the browser stack the whole e2e dir is deselected cleanly.
    assert _e2e_collect_ignore(browser_available=False) == [_E2E_DIR]


def test_e2e_helper_collects_dir_when_browser_present() -> None:
    # With Playwright + Chromium present, nothing is ignored — the e2e dir is collected.
    assert _e2e_collect_ignore(browser_available=True) == []


def test_browser_stack_detection_is_boolean() -> None:
    # The detector must never raise and always answer True/False (it gates collection).
    assert isinstance(_browser_stack_available(), bool)
