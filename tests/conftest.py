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

# Rails test files that import ``agents.*`` (→ uagents) at module import.
_RAILS_TEST_FILES = [
    "test_fetch_rails.py",
    "test_rails_hardening.py",
    "test_rails_wire.py",
    "test_watcher_live_loop.py",
]


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


collect_ignore = _rails_collect_ignore(
    importlib.util.find_spec("uagents") is not None
)
