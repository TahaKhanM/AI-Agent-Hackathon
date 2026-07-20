"""WP-CONSOLE hard boundary — ``console/product/`` imports NO kernel.

The page package is a pure presentation surface: it consumes state ONLY over HTTP and must never
import ``precedent`` / ``precedent_memory`` / ``precedent_pack`` / ``precedent_analyzer`` / ``sim``
/ ``console.demo_state``. This is enforced in CI by ``scripts/check_product_imports.sh`` (a grep,
mirroring the open-weight guard). These tests assert:

  1. the guard PASSES on the real tree;
  2. the guard FAILS on a SEEDED violation (so it can actually catch one) — mirroring the
     open-weight guard's own contract;
  3. a pure-Python static scan agrees (the invariant holds even without the shell);
  4. importing ``console.product`` really does not drag a kernel module into ``sys.modules`` that
     was not already there.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GUARD = REPO / "scripts" / "check_product_imports.sh"
PRODUCT_DIR = REPO / "console" / "product"

_FORBIDDEN_PREFIXES = ("precedent", "precedent_memory", "precedent_pack", "precedent_analyzer",
                       "sim", "console.demo_state")


def _run_guard(target: str | None = None) -> subprocess.CompletedProcess:
    cmd = ["bash", str(GUARD)]
    if target is not None:
        cmd.append(target)
    return subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)


# --------------------------------------------------------------------------- #
def test_guard_passes_on_real_tree() -> None:
    r = _run_guard()
    assert r.returncode == 0, f"guard should pass on the real tree:\n{r.stdout}\n{r.stderr}"
    assert "OK" in r.stdout


def test_guard_fails_on_seeded_violation(tmp_path) -> None:
    """Seed a fake console/product/ with a forbidden import; the SAME guard must flag it (exit 1).
    Mirrors the open-weight guard's seed-a-violation contract."""
    d = tmp_path / "console" / "product"
    d.mkdir(parents=True)
    (d / "ok.py").write_text("from fastapi import APIRouter\n", encoding="utf-8")
    (d / "bad.py").write_text("from precedent import models  # smuggled kernel import\n",
                              encoding="utf-8")
    r = _run_guard(str(d))
    assert r.returncode == 1, "the guard must FAIL on a seeded kernel import"
    assert "bad.py" in r.stderr and "VIOLATION" in r.stderr


def test_guard_ignores_lookalike_module_names(tmp_path) -> None:
    """A word that merely STARTS with 'sim' (e.g. simplejson) is not a kernel import."""
    d = tmp_path / "console" / "product"
    d.mkdir(parents=True)
    (d / "ok.py").write_text("import simplejson_not_real\nfrom fastapi import APIRouter\n",
                             encoding="utf-8")
    r = _run_guard(str(d))
    assert r.returncode == 0, f"lookalike names must not trip the guard:\n{r.stderr}"


def test_static_scan_agrees_no_kernel_import() -> None:
    """A pure-Python AST scan of every console/product/*.py: no import resolves to a kernel pkg."""
    offenders: list[str] = []
    for py in PRODUCT_DIR.rglob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        for node in ast.walk(tree):
            mods: list[str] = []
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                mods = [node.module]
            for m in mods:
                top = m.split(".")[0]
                if top in ("precedent", "precedent_memory", "precedent_pack", "precedent_analyzer",
                           "sim") or m.startswith("console.demo_state"):
                    offenders.append(f"{py.relative_to(REPO)}: {m}")
    assert not offenders, "console/product/ must import no kernel:\n" + "\n".join(offenders)


def test_importing_product_pulls_no_kernel() -> None:
    """Import console.product in a FRESH interpreter and assert no kernel module got imported as a
    side effect (a subprocess so this test does not itself pre-warm sys.modules)."""
    code = (
        "import sys; import console.product; "
        "bad=[m for m in sys.modules if m=='precedent' or m.startswith('precedent.') "
        "or m.startswith('precedent_memory') or m.startswith('precedent_pack') "
        "or m.startswith('precedent_analyzer') or m=='sim' or m.startswith('sim.') "
        "or m=='console.demo_state']; "
        "print('BAD:'+','.join(sorted(bad))); "
        "sys.exit(1 if bad else 0)"
    )
    r = subprocess.run([sys.executable, "-c", code], cwd=str(REPO), capture_output=True, text=True)
    assert r.returncode == 0, f"console.product imported a kernel module:\n{r.stdout}\n{r.stderr}"
