"""Tests for the rails-collection guard in ``tests/conftest.py``.

Asserts the pure helper's decision table and confirms that in THIS
environment (our ``.venv`` with the ``agents`` extra) uagents is importable,
so the four rails files are collected rather than deselected.
"""

from __future__ import annotations

import importlib.util

from tests.conftest import _RAILS_TEST_FILES, _rails_collect_ignore

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
