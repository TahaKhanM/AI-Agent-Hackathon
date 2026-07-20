"""WP-HOST-COLD — zero cold-start + first-impression guards.

Three deterministic (never wall-clock-flaky beyond a generous in-process ceiling) proxies for
the always-on deploy's first impression:

1. deps-from-pyproject — the container image installs its runtime deps FROM pyproject.toml
   (single source of truth). The Dockerfile must NOT hand-list a divergent set of requirements
   that can drift away from pyproject.

2. render-TIME budget — '/' and '/demo' render server-side under a generous in-process ceiling
   (measured with a warmup so we time steady-state render, not first-request app init).

3. static-asset BYTE budget + no-blocking-render — the total weight of the assets a page pulls
   stays under a cold-start ceiling (this locks in the recompressed brand PNGs), and neither
   page performs a synchronous external fetch in its <head> (nothing blocks first paint).
"""
from __future__ import annotations

import re
import time
import tomllib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from console.app import app

REPO = Path(__file__).resolve().parent.parent
STATIC = REPO / "console" / "static"


@pytest.fixture
def client():
    return TestClient(app)


# --------------------------------------------------------------------------- helpers

def _pyproject_runtime_dep_names() -> set[str]:
    """The normalised package names of the [project].dependencies runtime set."""
    data = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    names = set()
    for spec in data["project"]["dependencies"]:
        # strip extras + version markers: "uvicorn[standard]>=0.32" -> "uvicorn"
        name = re.split(r"[<>=!~;\[ ]", spec, maxsplit=1)[0].strip().lower()
        if name:
            names.add(name)
    return names


def _dockerfile_pip_install_lines() -> list[str]:
    """Return the `pip install` invocations in the Dockerfile (RUN steps), joined per-command
    across backslash line continuations."""
    text = (REPO / "Dockerfile").read_text(encoding="utf-8")
    # collapse backslash-newline continuations so a multi-line RUN is one logical line
    joined = re.sub(r"\\\s*\n", " ", text)
    return [ln for ln in joined.splitlines() if "pip install" in ln]


def _head(html: str) -> str:
    lower = html.lower()
    i = lower.find("</head>")
    return html[: i if i != -1 else len(html)]


def _referenced_static_paths(html: str) -> set[Path]:
    """Every /static/... asset the page pulls, resolved to a file on disk (deduped)."""
    out: set[Path] = set()
    for m in re.finditer(r'(?:src|href)="(/static/[^"?#]+)', html):
        rel = m.group(1)[len("/static/"):]
        p = STATIC / rel
        if p.is_file():
            out.add(p)
    return out


# --------------------------------------------------------- 1. deps come from pyproject

def test_dockerfile_installs_from_pyproject_not_a_handlisted_set():
    """The image must resolve runtime deps from pyproject.toml (single source of truth), and must
    NOT hand-list a divergent requirement set that can silently drift from pyproject."""
    pip_lines = _dockerfile_pip_install_lines()
    assert pip_lines, "Dockerfile has no `pip install` step"

    # (a) at least one install resolves the local project (pip install . / pip install -e .),
    # which pulls [project].dependencies straight from pyproject.toml.
    installs_project = any(
        re.search(r"pip install[^\n]*(?<![\w./-])(-e\s+)?\.(?:\s|$)", ln) for ln in pip_lines
    )
    assert installs_project, (
        "Dockerfile must install the project from pyproject (e.g. `pip install .`) so runtime "
        f"deps have a single source of truth; got: {pip_lines}"
    )

    # (b) no pip install line hand-lists the runtime dependency names (that is the drift bug).
    dep_names = _pyproject_runtime_dep_names()
    handlisted = {
        name
        for ln in pip_lines
        for name in dep_names
        # a hand-listed requirement appears as a quoted spec, e.g. "fastapi>=0.115"
        if re.search(rf'"{re.escape(name)}[<>=!~\[" ]', ln)
    }
    assert not handlisted, (
        "Dockerfile hand-lists runtime deps that will drift from pyproject.toml: "
        f"{sorted(handlisted)}. Install from pyproject instead."
    )


# --------------------------------------------------------------- 2. render-time budget

RENDER_CEILING_S = 2.0  # generous in-process ceiling; a real cold page renders in << 100ms


@pytest.mark.parametrize("path", ["/", "/demo"])
def test_server_render_time_under_budget(client, path):
    client.get(path)  # warmup: pay app-init / template-compile once, outside the measurement
    t0 = time.perf_counter()
    r = client.get(path)
    dt = time.perf_counter() - t0
    assert r.status_code == 200
    assert dt < RENDER_CEILING_S, f"{path} server render took {dt:.3f}s (> {RENDER_CEILING_S}s)"


# ----------------------------------------------------- 3a. static-asset byte budget

# Cold-start page-weight ceiling. Post-recompression '/' and '/demo' sit well under this; a
# regression of a brand PNG back to its unoptimised size busts it. Generous but meaningful.
PAGE_WEIGHT_CEILING = 384 * 1024

# Hard per-asset lock on the recompressed brand PNGs (were 319KB / 167KB before WP-HOST-COLD).
PNG_CEILING = 64 * 1024


@pytest.mark.parametrize("path", ["/", "/demo"])
def test_total_page_weight_under_budget(client, path):
    html = client.get(path).text
    asset_bytes = sum(p.stat().st_size for p in _referenced_static_paths(html))
    total = len(html.encode("utf-8")) + asset_bytes
    assert total <= PAGE_WEIGHT_CEILING, (
        f"{path} total page weight {total} bytes exceeds {PAGE_WEIGHT_CEILING}"
    )


@pytest.mark.parametrize("name", ["precedent-seal.png", "precedent-logo.png"])
def test_brand_pngs_are_recompressed(name):
    size = (STATIC / name).stat().st_size
    assert size <= PNG_CEILING, f"{name} is {size} bytes (> {PNG_CEILING}); recompress it"


# ------------------------------------------------------- 3b. no blocking render in <head>

@pytest.mark.parametrize("path", ["/", "/demo"])
def test_no_blocking_external_fetch_in_head(client, path):
    head = _head(client.get(path).text)
    # No synchronous external resource in <head>: no cross-origin script/style/font/link. Every
    # head asset must be a local /static/... reference (or inline). The only external asset on the
    # landing (the CI-status badge <img>) lives in the body and is lazily fetched by the browser.
    assert "http://" not in head and "https://" not in head, (
        f"{path} <head> references an external URL — a blocking fetch that delays first paint"
    )
    # No external <script src> in head at all (blocking parse); page scripts load at end of body.
    assert not re.search(r'<script[^>]+src=', head, re.IGNORECASE), (
        f"{path} loads a blocking <script src> in <head>"
    )
