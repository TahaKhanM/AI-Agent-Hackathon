"""Sponsor-protocol conformance bench — entry point.  [owner T3, tasks T3-2/3/5/6/7/12]

Spec: Idea/refinement/02-architecture-refinement.md §2.7.

`make bench` -> `python -m precedent_memory.bench.conformance_bench`:
  1. build the deterministic topology (seed 4207) and realize it into a memory DB via the
     product write API;
  2. build 10,000 ground-truth queries;
  3. grade the compiler-under-test against the INDEPENDENT oracle (FNR/FPR), sample hot-path
     latency, and measure drift/TTC, derived-memory correctness, audit coverage and the
     O(1) latency-vs-size curve;
  4. run the adversarial suite to fill the attacks row with a MEASURED count;
  5. emit RESULTS.md + results.json.

Decoupling contract: this file imports the compiler (store/retrieve) to drive it, and the
oracle to grade it — two independent implementations that meet only at the comparison. The
oracle imports neither store nor retrieve (guarded by a test).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from precedent_memory import db
from precedent_memory.bench import emit, grade, topology
from precedent_memory.bench.queries import build_queries
from precedent_memory.bench.seed import CANONICAL_SEED

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ADVERSARIAL = _REPO_ROOT / "tests" / "test_adversarial.py"


def _run_attacks(total: int = 6) -> dict:
    """Run the adversarial suite in a subprocess and parse the measured pass count. Any
    declared non-claim is expected to be an xfail (counted separately) — we aim for 6/6."""
    if not _ADVERSARIAL.exists():
        return {"ran": False}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(_ADVERSARIAL), "-q", "--no-header",
         "-p", "no:cacheprovider"],
        cwd=_REPO_ROOT, capture_output=True, text=True,
    )
    out = proc.stdout + proc.stderr
    passed = int(m.group(1)) if (m := re.search(r"(\d+) passed", out)) else 0
    xfailed = int(m.group(1)) if (m := re.search(r"(\d+) xfailed", out)) else 0
    failed = int(m.group(1)) if (m := re.search(r"(\d+) failed", out)) else 0
    return {"ran": True, "passed": passed, "xfailed": xfailed, "failed": failed,
            "total": total, "returncode": proc.returncode, "non_claims": []}


def run_bench(seed: int = CANONICAL_SEED, *,
              curve_sizes=(1000, 5000, 25000, 100000)) -> dict:
    conn = db.connect(":memory:")
    manifest = topology.build_manifest(seed)
    real = topology.realize(conn, manifest)
    queries = build_queries(manifest, seed)

    conformance = grade.run_conformance(conn, manifest, real, queries)
    conn.close()

    results = {
        "seed": seed,
        "conformance": conformance,
        "drift_ttc": grade.run_drift_ttc(seed),
        "derived_memory": grade.run_derived_memory(seed),
        "audit": grade.run_audit_coverage(seed),
        "latency_curve": grade.run_latency_curve(curve_sizes, seed=seed),
        "attacks": _run_attacks(),
    }
    return results


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    fast = "--fast" in argv          # smaller curve for a quick local smoke
    curve = (1000, 5000, 25000) if fast else (1000, 5000, 25000, 100000)

    print(f"[bench] building topology + grading vs independent oracle (seed {CANONICAL_SEED})...")
    results = run_bench(CANONICAL_SEED, curve_sizes=curve)
    md_path, json_path = emit.write_results(results, Path(__file__).parent)

    c = results["conformance"]
    print(f"[bench] FNR {c['fnr_leaks']} leaks / {c['deny_expected']:,} deny-expected · "
          f"FPR {c['fpr_outages']} / {c['allow_expected']:,} allow-expected · "
          f"P99(permitted) {c['p99_permitted_ms'] * 1000:.3f} µs")
    atk = results["attacks"]
    if atk.get("ran"):
        print(f"[bench] adversarial suite: {atk['passed']}/{atk['total']} passed "
              f"({atk.get('xfailed', 0)} xfail, {atk.get('failed', 0)} fail)")
    print(f"[bench] wrote {md_path.relative_to(_REPO_ROOT)} "
          f"and {json_path.relative_to(_REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
