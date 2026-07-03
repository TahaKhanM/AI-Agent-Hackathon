"""Eligibility guard (covers tests/ too, which scripts/check_open_weight.sh does not):
no closed-model ids and no real-secret literals anywhere in the T2 code or its tests.
The fake tokens used in Jira mocks ('FAKE-TOKEN...', 'SUPER-SECRET-TOKEN-42') are
deliberately NOT in real-secret formats, so they do not (and must not) match.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SELF = pathlib.Path(__file__).name

CLOSED_MODEL = re.compile(r"claude-|openai-|gpt-|gemini-|grok-|mercury-", re.I)
REAL_SECRET = re.compile(r"sk-[A-Za-z0-9]{16}|ghp_[A-Za-z0-9]{20}|xoxb-[0-9]|"
                         r"ATATT[A-Za-z0-9]{8}|-----BEGIN [A-Z ]*PRIVATE KEY")


def _t2_py_files():
    files: list[pathlib.Path] = []
    for d in ("precedent_memory", "console"):
        files += (ROOT / d).rglob("*.py")
    for name in ("test_console.py", "test_t1_integration.py"):
        p = ROOT / "tests" / name
        if p.exists():
            files.append(p)
    return [f for f in files if f.name != SELF]


def test_no_closed_model_ids_in_t2_paths():
    hits = [f"{f}:{i}" for f in _t2_py_files()
            for i, line in enumerate(f.read_text().splitlines(), 1)
            if CLOSED_MODEL.search(line)]
    assert not hits, f"closed-model id(s) found in T2 paths: {hits}"


def test_no_real_secret_literals_in_t2_paths():
    hits = [f"{f}:{i}" for f in _t2_py_files()
            for i, line in enumerate(f.read_text().splitlines(), 1)
            if REAL_SECRET.search(line)]
    assert not hits, f"real-secret-shaped literal(s) found in T2 paths: {hits}"
