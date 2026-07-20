#!/usr/bin/env python3
"""Copy-lint — the mechanical number/vocabulary honesty gate.

A PURE, deterministic linter over shippable copy surfaces. It has NO knowledge of
meaning: it enforces that every number token on a shipped surface carries the exact
label `docs/numbers.md` mandates, and that banned vocabulary never appears. It is the
mechanical half of the honesty doctrine — the human still writes the prose, this just
refuses to let a number ship stripped of the caveat that keeps it honest.

Design:
  * ``lint_text(text, *, hosted=False) -> list[dict]`` is a PURE function. Each finding is
    ``{"rule": str, "line": int, "excerpt": str}``. It applies NO allowlist — that is the
    caller's job (so the fixtures in tests/ exercise the raw rules).
  * ``main()`` walks the SURFACES globs, applies the allowlist file, prints every surviving
    finding and exits non-zero if any remain.

Source of truth for every number+label pairing: ``docs/numbers.md`` (the NEVER-BLEND rule —
18.2 h is CALENDAR/ours, 8.85 h / 8h 51m is BUSINESS/MetricNet — lives there). No shipped
surface may state a number that is not on that page with its label.

Hard rules honoured: no model ids here (rule 1), no LLM anywhere in this path (rule 2 — this
is a pure string gate), and it fails CLOSED (any finding => non-zero exit).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Shippable copy surfaces (globs). Some are empty today; they grow later. Brace groups
# like ``*.{css,js}`` are expanded by _expand_braces below.
SURFACES: list[str] = [
    "README.md",
    "console/app.py",
    "console/showcase.py",
    "templates/**/*.html",
    "static/**/*.{css,js}",
    "docs/demo/**/*.md",
]

# Surfaces rendered on the public landing / hosted demo are linted with hosted=True (R5:
# no "offline"/"airplane" copy there). None exist yet — mark them here when they land, e.g.
# "templates/landing/**/*.html" or "docs/demo/hosted/**/*.md". The airplane-mode demo docs
# under docs/demo/ are AUTHORING surfaces, NOT hosted, so they may say offline/airplane.
HOSTED_GLOBS: list[str] = []

ALLOWLIST_PATH = Path(__file__).resolve().parent / "copy_lint_allowlist.txt"

# ~120-char adjacency window: a number token must find its label within its own line OR
# this many characters either side of it in the full text.
WINDOW = 120


# --------------------------------------------------------------------------- banned words

def _r1(line: str) -> bool:
    # 'Autonomous' as an L3/ladder label — the exact capitalised word (L3 is "Standing
    # Approval", never "Autonomous"). Lowercase "graduated autonomy" is fine.
    return re.search(r"\bAutonomous\b", line) is not None


def _r2(line: str) -> bool:
    # 'control plane' (case-insensitive) — we say "the gate".
    return re.search(r"control plane", line, re.IGNORECASE) is not None


def _r3(line: str) -> bool:
    # Flat "Azure fails open" overclaim. Permitted ONLY in the one sentence that also
    # carries BOTH 'failMode' and 'Stop-hook'.
    if not re.search(r"azure", line, re.IGNORECASE):
        return False
    if not re.search(r"fails? ?-?open", line, re.IGNORECASE):
        return False
    permitted = re.search(r"failMode", line, re.IGNORECASE) and re.search(
        r"Stop-hook", line, re.IGNORECASE
    )
    return not permitted


def _r4(line: str) -> bool:
    # Unfilled guillemet placeholder, e.g. ‹XX›.
    return re.search(r"‹[^›]*›", line) is not None


def _r5(line: str, hosted: bool) -> bool:
    # 'offline' / 'airplane' banned in HOSTED copy only.
    if not hosted:
        return False
    return re.search(r"offline|airplane", line, re.IGNORECASE) is not None


# ---------------------------------------------------------------------- adjacency (A/V)

# token: regex for the number token (searched case-insensitively).
# requires: labels of which AT LEAST ONE must appear in the window (case-insensitive).
# forbids: labels none of which may appear in the window (case-insensitive).
_ADJACENCY = [
    # A1: 18.2 h — CALENDAR (ours). Never labelled business.
    {"rule": "A1", "token": r"18\.2",
     "requires": ["calendar"], "forbids": ["business"]},
    # A2: 8.85 / 8h 51m / 8h51m — BUSINESS hours (MetricNet). Never labelled calendar.
    {"rule": "A2", "token": r"8\.85|8h\s?51m",
     "requires": ["business"], "forbids": ["calendar"]},
    # A3: 87.7 / 59.4 — the naive arrival-time FLOOR, not a product-accuracy claim.
    # The '%' is OPTIONAL: a bare 87.7 shipped without the floor/naive label evades honesty
    # just as much as 87.7%. The (?<!\d)...(?!\d) guards keep it from matching inside a longer
    # number (e.g. 187.7 or 87.72).
    {"rule": "A3", "token": r"(?<!\d)(?:87\.7|59\.4)%?(?!\d)",
     "requires": ["floor", "naive"], "forbids": []},
    # A4: 0/100 false-fast-paths — a SAFETY number; calling it 'recall' is itself a violation.
    {"rule": "A4", "token": r"0/100|0\s*false[\s-]?fast[\s-]?path",
     "requires": ["safety"], "forbids": ["recall"]},
    # A5: 94.4 — the EXISTENCE claim (key includes closed_code). forbids 'arrival' so a
    # SWAPPED 94.4↔98.6 pair (each number sitting next to the OTHER's label) trips too —
    # numbers.md §7 "don't swap 94.4 (existence) / 98.6 (arrival)". '%' optional.
    {"rule": "A5", "token": r"(?<!\d)94\.4%?(?!\d)",
     "requires": ["existence"], "forbids": ["arrival"]},
    # A6: 98.6 — the ARRIVAL-knowable claim (symptom level). forbids 'existence' (the §7 swap).
    {"rule": "A6", "token": r"(?<!\d)98\.6%?(?!\d)",
     "requires": ["arrival"], "forbids": ["existence"]},
    # V1: PagerDuty vendor numbers must carry "(vendor-claimed)" nearby (numbers.md §5/§7).
    {"rule": "V1", "token": r"99% faster|50% cost",
     "requires": ["vendor-claimed"], "forbids": []},
    # V2: the ServiceNow KCS case-study "% faster" figures must carry their source
    # (ServiceNow / KCS). numbers.md §5. (The generic NeuBird survey numbers 44/74/39 are too
    # collision-prone for a line linter — the semantic honesty fleet covers their
    # "(vendor-sponsored survey)" label; see the build report's NO-SILENT-CAPS note.)
    {"rule": "V2", "token": r"52% faster|66% faster",
     "requires": ["KCS", "ServiceNow"], "forbids": []},
]


def _line_index(text: str) -> list[tuple[int, int, str]]:
    """Return (line_no, start_offset, line_text) for each line in *text*."""
    out: list[tuple[int, int, str]] = []
    offset = 0
    for i, line in enumerate(text.splitlines(keepends=True), start=1):
        out.append((i, offset, line.rstrip("\n")))
        offset += len(line)
    return out


def _lineno_for_offset(index: list[tuple[int, int, str]], offset: int) -> tuple[int, str]:
    lineno, ltext = 1, ""
    for no, start, line in index:
        if start <= offset:
            lineno, ltext = no, line
        else:
            break
    return lineno, ltext


def lint_text(text: str, *, hosted: bool = False) -> list[dict]:
    """Pure linter. Return a list of findings for *text*; apply no allowlist.

    Each finding: ``{"rule": str, "line": int (1-indexed), "excerpt": str}``.
    """
    findings: list[dict] = []
    index = _line_index(text)

    # Line-scoped banned-word rules.
    for lineno, _start, line in index:
        if _r1(line):
            findings.append({"rule": "R1", "line": lineno, "excerpt": line.strip()})
        if _r2(line):
            findings.append({"rule": "R2", "line": lineno, "excerpt": line.strip()})
        if _r3(line):
            findings.append({"rule": "R3", "line": lineno, "excerpt": line.strip()})
        if _r4(line):
            findings.append({"rule": "R4", "line": lineno, "excerpt": line.strip()})
        if _r5(line, hosted):
            findings.append({"rule": "R5", "line": lineno, "excerpt": line.strip()})

    # Adjacency rules — window over the full text (same line OR ±WINDOW chars).
    for spec in _ADJACENCY:
        for m in re.finditer(spec["token"], text, re.IGNORECASE):
            g = m.start()
            lineno, ltext = _lineno_for_offset(index, g)
            window = text[max(0, g - WINDOW): m.end() + WINDOW]
            # Context = the token's own line UNION the char window.
            context = ltext + "\n" + window

            requires = spec["requires"]
            has_required = (not requires) or any(
                re.search(re.escape(lbl), context, re.IGNORECASE) for lbl in requires
            )
            has_forbidden = any(
                re.search(re.escape(lbl), context, re.IGNORECASE) for lbl in spec["forbids"]
            )
            if (not has_required) or has_forbidden:
                findings.append({"rule": spec["rule"], "line": lineno, "excerpt": ltext.strip()})

    findings.sort(key=lambda f: (f["line"], f["rule"]))
    return findings


# ------------------------------------------------------------------------------- runner

def _expand_braces(pattern: str) -> list[str]:
    """Expand a single ``{a,b}`` group in a glob (enough for our SURFACES)."""
    m = re.search(r"\{([^}]*)\}", pattern)
    if not m:
        return [pattern]
    pre, post = pattern[: m.start()], pattern[m.end():]
    return [f"{pre}{opt}{post}" for opt in m.group(1).split(",")]


def _iter_surface_files(root: Path) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    for glob in SURFACES:
        for expanded in _expand_braces(glob):
            for p in sorted(root.glob(expanded)):
                if p.is_file() and p not in seen:
                    seen.add(p)
                    files.append(p)
    return files


def _is_hosted(rel: str) -> bool:
    for glob in HOSTED_GLOBS:
        for expanded in _expand_braces(glob):
            if Path(rel).match(expanded):
                return True
    return False


def _load_allowlist(path: Path) -> list[re.Pattern]:
    """Each non-empty, non-comment line is a substring/regex; a trailing ``# reason`` is
    stripped. A finding is suppressed if any pattern matches its line text."""
    patterns: list[re.Pattern] = []
    if not path.exists():
        return patterns
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        body = re.split(r"\s+#", line, maxsplit=1)[0].strip()
        if not body:
            continue
        try:
            patterns.append(re.compile(body))
        except re.error:
            patterns.append(re.compile(re.escape(body)))
    return patterns


def main(argv: list[str] | None = None) -> int:
    root = REPO_ROOT
    allowlist = _load_allowlist(ALLOWLIST_PATH)
    total = 0
    for path in _iter_surface_files(root):
        rel = str(path.relative_to(root))
        text = path.read_text(encoding="utf-8")
        findings = lint_text(text, hosted=_is_hosted(rel))
        for f in findings:
            if any(p.search(f["excerpt"]) for p in allowlist):
                continue
            total += 1
            print(f"{rel}:{f['line']}: [{f['rule']}] {f['excerpt']}")
    if total:
        print(f"\ncopy-lint: {total} violation(s) — fix the label per docs/numbers.md "
              f"(never remove the number), or allowlist a genuine prose false positive.")
        return 1
    print("copy-lint: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
