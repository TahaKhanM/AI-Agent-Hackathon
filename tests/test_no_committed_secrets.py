"""Real-secret guard over EVERY tracked file (the scrub, enforced in CI).  [owner T3]

check-open-weight scans only precedent*/sim/console/agents, and test_invariants_guard scans
a subset of paths — neither scans `.env.example`, the mutation corpus, docs/, or Prep/. A live
`.env` accidentally saved over `.env.example` would therefore slip past both. This test closes
that gap: it greps every tracked text file for real-secret token shapes (Atlassian/OpenAI/GitHub/
Slack tokens, private keys, Venice inference keys), so `make test` goes red BEFORE such a file is
committed. Placeholder values in `.env.example` (`your-venice-key`, `ATATT<token>`) do not match.
"""
from __future__ import annotations

import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SELF = pathlib.Path(__file__).name

# Token SHAPES that cannot be a placeholder (a real secret only). Built so this file itself does
# not contain a literal match (each prefix is separated from its charclass).
_SECRET = re.compile(
    "ATATT" + r"3[A-Za-z0-9._-]{20,}"          # Atlassian API token
    "|" + "sk-" + r"[A-Za-z0-9]{20,}"           # OpenAI-style key
    "|" + "ghp_" + r"[A-Za-z0-9]{20,}"          # GitHub PAT
    "|" + "xoxb-" + r"[0-9]{6,}"                 # Slack bot token
    "|" + "VENICE_INFERENCE_KEY_" + r"[A-Za-z0-9-]{10,}"   # a real Venice inference key value
    "|" + "-----BEGIN " + r"[A-Z ]*PRIVATE KEY"  # PEM private key
)

_TEXT_SUFFIXES = {".py", ".md", ".json", ".jsonl", ".txt", ".example", ".sql", ".sh",
                  ".toml", ".cfg", ".ini", ".yaml", ".yml", ".env", ""}


def _tracked_files() -> list[pathlib.Path]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    files = []
    for line in out.stdout.splitlines():
        p = ROOT / line
        if p.name == SELF:
            continue
        if p.suffix.lower() in _TEXT_SUFFIXES and p.exists() and p.stat().st_size < 2_000_000:
            files.append(p)
    return files


def test_no_real_secret_in_any_tracked_file():
    hits = []
    for p in _tracked_files():
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if _SECRET.search(line):
                hits.append(f"{p.relative_to(ROOT)}:{i}")
    assert not hits, f"real secret token(s) found in tracked file(s): {hits}"


def test_env_example_is_placeholders_only():
    """.env.example must never hold a real value — it is the committed, public template."""
    env_example = ROOT / ".env.example"
    assert env_example.exists()
    text = env_example.read_text()
    assert not _SECRET.search(text), ".env.example contains a real secret — restore the template"
