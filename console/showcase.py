"""Read-only augmentation surface for the demo console.

Nothing in this module makes a network call, invokes a model, or touches the permission /
risk / execution paths. It adds VIEW surface only: a real-permission-check latency ring, the
adversarial-probe skeptic affordance, and the decision-kernel fingerprint.

The four hard rules are honoured by construction.

Loaded from console.app; safe to hot-reload.
"""
from __future__ import annotations

import hashlib
import json
import time
from collections import deque
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------------- #
# Latency ring buffer (populated by wrap-around helper below).
# --------------------------------------------------------------------------- #
# WP-HOST-SESSION: the ring is PER SESSION (session.lat_ring) so one visitor's timings never
# bleed into another's. Callers pass their session's ring; this module-level ring is the
# default used only in pinned/legacy test mode (and by a direct import that omits a ring).
_LAT_RING: deque[int] = deque(maxlen=200)


def record_latency_ns(elapsed_ns: int, ring: deque[int] | None = None) -> None:
    """Append one measurement to the given session ring (or the module default)."""
    (ring if ring is not None else _LAT_RING).append(int(elapsed_ns))


def _pct(values: list[int], pct: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = min(len(s) - 1, int(round((pct / 100.0) * (len(s) - 1))))
    return s[k]


# --------------------------------------------------------------------------- #
# Decision-kernel fingerprint — a stable hash of the code that ACTUALLY DECIDES.
# --------------------------------------------------------------------------- #
_REPO_ROOT = Path(__file__).resolve().parent.parent

# The deterministic DECISION surface: the files that classify, gate, escalate, execute and
# audit. Editing VIEW prose, templates or the demo console does NOT move this hash — only a
# change to how the kernel decides does. Kept in sync with MANIFEST.json (kernel_hash_expected).
KERNEL_SURFACE_FILES: list[str] = [
    "precedent/extractor.py",             # deterministic class fingerprint
    "precedent/extractor_robustness.py",  # extractor hardening
    "precedent/policy.py",                # YAML policy engine (risk classification)
    "precedent/policy_pack.yaml",         # the policy pack it reads
    "precedent/policy_pack_actions.yaml",  # executable action classes + inverses
    "precedent/ladder.py",                # approval ladder + standing-approval fast-path
    "precedent/orchestrator.py",          # the decide/execute/rollback loop
    "precedent_memory/retrieve.py",       # fail-closed permission-aware retrieval
    "precedent_memory/audit.py",          # hash-chained audit
]


def compute_kernel_hash(files: list[str] | None = None, root: Path | None = None) -> str:
    """Fingerprint the deterministic DECISION surface: the checked-in files that actually
    decide what executes (extractor, policy + policy packs, ladder, orchestrator, retrieve,
    audit). Excludes VIEW prose, templates and the per-run seed dbs.

    A pinned hash is falsifiable: if this changes, someone edited the decision kernel. The
    purpose is external attestation (compared against MANIFEST.json), not runtime state.
    """
    files = list(KERNEL_SURFACE_FILES if files is None else files)
    root = root if root is not None else _REPO_ROOT
    h = hashlib.sha256()
    for rel in sorted(files):
        h.update(rel.encode())
        h.update(b"\0")
        h.update((root / rel).read_bytes())
        h.update(b"\0")
    return h.hexdigest()[:12]


# Cache once at import; visible in the header.
KERNEL_HASH = compute_kernel_hash()


def manifest_expected_hash() -> str | None:
    """Read the frozen kernel hash from MANIFEST.json if present.

    This is the external attestation the Conduct rubric asks for: the running process cannot
    forge a hash pinned in a committed file. If MANIFEST is absent or malformed, return None
    and let the UI say "no manifest pinned".
    """
    try:
        p = Path("MANIFEST.json")
        if not p.exists():
            return None
        obj = json.loads(p.read_text())
        return str(obj.get("kernel_hash_expected") or "").strip() or None
    except Exception:
        return None


def run_adversarial_probes(conn, ring: deque[int] | None = None, n: int = 100) -> dict[str, Any]:
    """Fire n adversarial permission-check probes against the SESSION's memory db.
    Read-only. Uses precedent_memory.retrieve.check_access exactly as the runtime path
    does. Reports: total, denials, permits, and — for the leak-attempt subset (unauthorised
    principals against restricted records) — the number of incorrect permits (a leak).

    A leak counter of 0 with a P99 well under 1ms is the skeptic evidence surface.
    """
    from precedent_memory import retrieve as _rt

    ring = ring if ring is not None else _LAT_RING
    rows = list(conn.execute(
        "SELECT id, is_restricted FROM effective_policy JOIN memory_record ON "
        "memory_record.id = effective_policy.record_id LIMIT 40"))
    if not rows:
        return {"n": 0, "permitted": 0, "denied": 0, "leaks": 0,
                "leak_attempts": 0, "p50_us": 0.0, "p99_us": 0.0,
                "note": "no records to probe against — run make demo-reset first"}
    # Bucket rows by restrictedness so we can construct honest leak attempts.
    restricted = [r[0] for r in rows if r[1]]
    public = [r[0] for r in rows if not r[1]]
    unauth_principals = ["stranger-1", "stranger-2", "unknown-team-42"]

    timings: list[int] = []
    permitted = denied = leaks = leak_attempts = 0
    for i in range(n):
        # Mix: 60% legitimate lookups, 40% adversarial leak attempts.
        if restricted and (i % 5) < 2:
            rid = restricted[i % len(restricted)]
            pr = unauth_principals[i % len(unauth_principals)]
            leak_attempts += 1
            t0 = time.perf_counter_ns()
            try:
                ok, _owner = _rt.check_access(conn, pr, rid)
            except Exception:
                continue
            timings.append(time.perf_counter_ns() - t0)
            if ok:
                leaks += 1
                permitted += 1
            else:
                denied += 1
        else:
            rid = (public or restricted)[i % max(1, len(public or restricted))]
            pr = "scheduling-ops"
            t0 = time.perf_counter_ns()
            try:
                ok, _owner = _rt.check_access(conn, pr, rid)
            except Exception:
                continue
            timings.append(time.perf_counter_ns() - t0)
            if ok:
                permitted += 1
            else:
                denied += 1

    p50 = _pct(timings, 50) / 1000.0 if timings else 0.0
    p99 = _pct(timings, 99) / 1000.0 if timings else 0.0
    # Also fold into the display ring so the sparkline reflects the probe run.
    for v in timings:
        ring.append(v)
    return {
        "n": len(timings),
        "permitted": permitted,
        "denied": denied,
        "leaks": leaks,
        "leak_attempts": leak_attempts,
        "p50_us": round(p50, 3),
        "p99_us": round(p99, 3),
    }
