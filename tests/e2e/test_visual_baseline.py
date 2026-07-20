"""WP-REFACTOR — compact perceptual-hash baseline of the shared design system (Playwright).

The WP-REFACTOR change moved the console off a single ``_PAGE`` string onto a Jinja2 template +
a shared static design system (``console/static/css/precedent.css`` + ``demo.js``). That refactor
deferred a visual baseline because Playwright was not installed. Playwright now IS installed here,
so this captures that baseline: a *perceptual* dHash of the rendered page at the three canonical
breakpoints (1380 / 768 / 375 px), committed to ``baseline/visual_baseline.json`` alongside tiny
downscaled grayscale thumbnails for human eyeballing.

Perceptual (not pixel) hashing on an aggressively downscaled grayscale image is deliberate: it is
robust to sub-pixel font/AA differences yet still trips on a real layout/skin regression. The
comparison allows a small Hamming tolerance. Regenerate after an INTENTIONAL redesign with::

    PRECEDENT_UPDATE_VISUAL_BASELINE=1 .venv/bin/python -m pytest tests/e2e/test_visual_baseline.py

This is dev-only: the baseline artifacts are tiny and the capture never runs in the product image.
"""
from __future__ import annotations

import io
import json
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.browser

_BASE_DIR = Path(__file__).parent / "baseline"
_BASELINE_JSON = _BASE_DIR / "visual_baseline.json"

# (name, width, height). The three shared-design-system breakpoints.
_BREAKPOINTS = [("desktop", 1380, 900), ("tablet", 768, 1024), ("mobile", 375, 812)]

_HASH_SIZE = 16                 # 16x16 => 256-bit dHash
_TOLERANCE_BITS = 26            # ~10% of 256 bits — absorbs AA/font drift, catches a real reskin

_KILL_MOTION = "*,*::before,*::after{animation:none!important;transition:none!important}"


def _dhash_bits(png: bytes, size: int = _HASH_SIZE) -> list[int]:
    """Row-wise difference hash of a downscaled grayscale render (size*size bits)."""
    from PIL import Image

    img = Image.open(io.BytesIO(png)).convert("L").resize((size + 1, size), Image.LANCZOS)
    px = img.tobytes()   # size*(size+1) grayscale bytes, row-major (no deprecated getdata)
    bits: list[int] = []
    for r in range(size):
        base = r * (size + 1)
        for c in range(size):
            bits.append(1 if px[base + c] < px[base + c + 1] else 0)
    return bits


def _bits_to_hex(bits: list[int]) -> str:
    n = 0
    for b in bits:
        n = (n << 1) | b
    return f"{n:0{len(bits) // 4}x}"


def _hex_to_bits(h: str, size: int = _HASH_SIZE) -> list[int]:
    n = int(h, 16)
    total = size * size
    return [(n >> (total - 1 - i)) & 1 for i in range(total)]


def _hamming(a: list[int], b: list[int]) -> int:
    return sum(1 for x, y in zip(a, b, strict=True) if x != y)


def _thumb(png: bytes, width: int = 240) -> bytes:
    """A compact grayscale thumbnail (committed reference; not asserted, only for human review)."""
    from PIL import Image

    img = Image.open(io.BytesIO(png)).convert("L")
    h = max(1, round(img.height * width / img.width))
    out = io.BytesIO()
    img.resize((width, h), Image.LANCZOS).save(out, format="PNG", optimize=True)
    return out.getvalue()


def _render(browser, base_url: str, width: int, height: int) -> bytes:
    ctx = browser.new_context(viewport={"width": width, "height": height},
                              device_scale_factor=1)
    try:
        page = ctx.new_page()
        page.goto(base_url + "/", wait_until="load")
        page.add_style_tag(content=_KILL_MOTION)
        # Wait until the design system has actually painted its live chips/rail (deterministic
        # for a fresh cold-open session), so the hash reflects the real skin, not a blank shell.
        page.wait_for_function("() => document.getElementById('kh')"
                               " && document.getElementById('kh').textContent.trim() !== '…'",
                               timeout=10_000)
        page.wait_for_timeout(400)
        return page.screenshot(full_page=False)
    finally:
        ctx.close()


def _load_baseline() -> dict:
    if _BASELINE_JSON.exists():
        return json.loads(_BASELINE_JSON.read_text())
    return {}


@pytest.mark.parametrize("name,width,height", _BREAKPOINTS)
def test_design_system_visual_baseline(browser, live_server, name, width, height):
    png = _render(browser, live_server, width, height)
    cur = _dhash_bits(png)
    cur_hex = _bits_to_hex(cur)

    if os.environ.get("PRECEDENT_UPDATE_VISUAL_BASELINE"):
        _BASE_DIR.mkdir(parents=True, exist_ok=True)
        baseline = _load_baseline()
        baseline[name] = {"viewport": [width, height], "hash_size": _HASH_SIZE, "dhash": cur_hex}
        _BASELINE_JSON.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n")
        (_BASE_DIR / f"{name}.png").write_bytes(_thumb(png))
        pytest.skip(f"baseline updated for {name} ({cur_hex})")

    baseline = _load_baseline()
    assert name in baseline, (
        f"no committed baseline for {name!r} — regenerate with "
        "PRECEDENT_UPDATE_VISUAL_BASELINE=1")
    dist = _hamming(cur, _hex_to_bits(baseline[name]["dhash"]))
    assert dist <= _TOLERANCE_BITS, (
        f"{name} @ {width}x{height}: perceptual drift {dist} bits > {_TOLERANCE_BITS} "
        f"(current {cur_hex} vs baseline {baseline[name]['dhash']}). If this reskin is "
        "intentional, regenerate with PRECEDENT_UPDATE_VISUAL_BASELINE=1.")
