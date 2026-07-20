"""WP-REFACTOR — ACCESSIBILITY FLOOR (never-cut, §9).

The shared design-system CSS (console/static/css/precedent.css) is now the single
source of the palette. This test pins the palette's readability: it parses the :root
custom properties and computes WCAG 2.1 relative-luminance contrast ratios for the
text/background pairs the demo actually renders, and asserts each clears its floor.

It also guards the keyboard-focus indicator: a :focus-visible outline must exist, and
no interactive control may strip its outline (outline:none/0) without a :focus-visible
companion rule to restore a visible focus ring.
"""
from __future__ import annotations

import re
from pathlib import Path

CSS = Path(__file__).resolve().parents[1] / "console" / "static" / "css" / "precedent.css"


def _tokens() -> dict[str, str]:
    css = CSS.read_text()
    root = re.search(r":root\s*\{(.*?)\}", css, re.DOTALL)
    assert root, "no :root block in precedent.css"
    return dict(re.findall(r"--([\w-]+)\s*:\s*(#[0-9A-Fa-f]{6})", root.group(1)))


def _lin(channel: int) -> float:
    c = channel / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _luminance(hex_colour: str) -> float:
    r = int(hex_colour[1:3], 16)
    g = int(hex_colour[3:5], 16)
    b = int(hex_colour[5:7], 16)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def _contrast(fg: str, bg: str) -> float:
    a, b = _luminance(fg), _luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


# (foreground token, background token, floor). All are body-text pairs → 4.5:1.
_PAIRS = [
    ("ink", "paper", 4.5),
    ("ink", "card", 4.5),
    ("ink", "paper-2", 4.5),
    ("muted", "paper", 4.5),
    ("muted", "card", 4.5),
    ("oxblood", "oxblood-bg", 4.5),   # the refusal — a watched case
    ("indigo", "paper", 4.5),
]


# WCAG 2.1 SC 1.4.3 inactive-component exemptions — documented, never silent (§9 floor).
# Two rendered numerals sit below the 3:1 UI floor BY DESIGN: they mark inactive/upcoming
# state and recede on purpose. SC 1.4.3 exempts text that is part of an inactive UI
# component, which these are; their ACTIVE states clear the floor and are the ones a user
# reads. Kept auditable here so a colour change forces a conscious revisit rather than drift.
#   .dk pending step dot     #A9A692 on #EEECDD  ≈ 2.07:1  (→ .dk.now/.dk.done are high-contrast)
#   .rn unreached chapter №  #B6B39E on nav ~#F5F3E8 ≈ 2.6:1 (→ .rn.now indigo / .rn.seen darker)
_INACTIVE_EXEMPT = [
    ("#A9A692", "dk pending step dot"),
    ("#B6B39E", "rn unreached chapter numeral"),
]


def test_inactive_state_colours_present_and_documented():
    css = CSS.read_text()
    for fg, label in _INACTIVE_EXEMPT:
        assert fg in css, f"inactive-exempt colour {fg} ({label}) missing — revisit the exemption"


def test_token_contrast_floor():
    tok = _tokens()
    failures = []
    for fg, bg, floor in _PAIRS:
        assert fg in tok, f"missing token --{fg}"
        assert bg in tok, f"missing token --{bg}"
        ratio = _contrast(tok[fg], tok[bg])
        if ratio < floor:
            failures.append(f"--{fg} ({tok[fg]}) on --{bg} ({tok[bg]}) = {ratio:.2f} < {floor}")
    assert not failures, "contrast floor breached:\n" + "\n".join(failures)


def test_focus_visible_present():
    css = CSS.read_text()
    assert ":focus-visible" in css, "no :focus-visible rule for keyboard focus"
    # The :focus-visible rule must actually paint an outline (not none/0).
    fv_rules = re.findall(r":focus-visible[^{]*\{([^}]*)\}", css)
    assert any(
        re.search(r"outline\s*:\s*(?!none|0\b)[^;]+", block) for block in fv_rules
    ), ":focus-visible rule does not set a visible outline"


def test_no_uncompanioned_outline_removal():
    css = CSS.read_text()
    bare = re.findall(r"outline\s*:\s*(?:none|0)\b", css)
    if bare:
        # A bare outline:none is only acceptable when a :focus-visible outline rule
        # restores a keyboard focus indicator elsewhere in the sheet.
        fv_rules = re.findall(r":focus-visible[^{]*\{([^}]*)\}", css)
        assert any(
            re.search(r"outline\s*:\s*(?!none|0\b)[^;]+", block) for block in fv_rules
        ), "outline:none present without a :focus-visible outline companion"
