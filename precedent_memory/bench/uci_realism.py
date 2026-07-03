"""UCI realism run — point the SAME bench harness at the real ~25k-record incident store.
[owner T3, task T3-14; Saturday human-run]

Spec: Idea/refinement/02-architecture-refinement.md §2.7.

The realism corpus is UCI dataset #498 (CC BY 4.0, 141,712 events → 24,918 incidents). ACL
boundaries come from the REAL `assignment_group` field; 40 principals get random clearances.
The same compiler-vs-independent-oracle grading + hot-path latency sampling run over it, so
the P99 the video/deck quote is measured on a real 25k-record store.

⚠️ CAPTION RULE: this is always a "**25k-record store**" — NEVER "P99 over 141k events". The
141,712 is the raw EVENT count; the 24,918 collapsed incidents are the records.

Airplane-first: the raw CSV is NOT committed (size + data honesty). The human downloads it and
runs `make bench-uci` on Saturday; the command exits non-zero when the CSV is absent.
"""
from __future__ import annotations

import csv
import os
import random
import sys
from pathlib import Path

from precedent_memory import db, retrieve, store
from precedent_memory.bench import grade
from precedent_memory.bench.oracle import oracle_allow
from precedent_memory.bench.seed import CANONICAL_SEED

DEFAULT_CSV = os.environ.get("PRECEDENT_UCI_CSV", "data/raw/incident_event_log.csv")
CAPTION = "25k-record store"   # never "141k events"


def _int(x, default=-1):
    try:
        return int(x)
    except (TypeError, ValueError):
        return default


def load_incidents(csv_path: str | Path, limit: int | None = None) -> list[dict]:
    """Collapse the event log to one record per incident (last event by sys_mod_count)."""
    latest: dict[str, tuple[int, dict]] = {}
    with open(csv_path, newline="") as fh:
        for row in csv.DictReader(fh):
            num = (row.get("number") or "").strip()
            if not num:
                continue
            mc = _int(row.get("sys_mod_count"))
            prev = latest.get(num)
            if prev is None or mc >= prev[0]:
                latest[num] = (mc, row)
    incidents = [r for _, r in latest.values()]
    incidents.sort(key=lambda r: (r.get("number") or ""))     # deterministic order
    return incidents[:limit] if limit else incidents


def build_uci_store(conn, incidents: list[dict], *, seed: int = CANONICAL_SEED,
                    n_principals: int = 40) -> dict:
    """Realize the incidents into a memory store; ACL boundary = real assignment_group."""
    rng = random.Random(seed)
    groups = sorted({(i.get("assignment_group") or "").strip() for i in incidents} - {"", "?"})
    group_cid = {g: store.ensure_constraint(conn, "assignment_group", g, f"Group {g}")
                 for g in groups}

    prin_sets: dict[str, frozenset[int]] = {}
    for k in range(n_principals):
        held = frozenset(group_cid[g] for g in groups if rng.random() < 0.25)
        store.put_principal(conn, f"uci-prin-{k:03d}", sorted(held))
        prin_sets[f"uci-prin-{k:03d}"] = held

    fresh = db.utcnow().isoformat()
    record_ids: list[int] = []
    for idx, inc in enumerate(incidents):
        g = (inc.get("assignment_group") or "").strip()
        num = (inc.get("number") or f"idx-{idx}").strip()
        if g and g != "?":
            ref = f"uci:{num}"
            store.put_source(conn, ref, [group_cid[g]], last_verified_at=fresh)
            lineage = [ref]
        else:
            # keep the real data's messiness: a null assignment_group is unknown provenance,
            # so it fails CLOSED (unverified sentinel) rather than being silently world-readable.
            lineage = [f"uci-unknown:{num}"]
        ck = (f"{inc.get('category')}|{inc.get('subcategory')}|{inc.get('closed_code')}")
        rid = store.store({"kind": "kb_summary", "class_key": ck, "uci_number": num},
                          lineage, conn=conn)
        record_ids.append(rid)
    return {"record_ids": record_ids, "prin_sets": prin_sets, "n_groups": len(groups)}


def run_uci_realism(csv_path: str | Path, *, seed: int = CANONICAL_SEED,
                    n_queries: int = 10000) -> dict:
    conn = db.connect(":memory:")
    incidents = load_incidents(csv_path)
    built = build_uci_store(conn, incidents, seed=seed)
    rids = built["record_ids"]
    prin_sets = built["prin_sets"]
    prin_ids = list(prin_sets)

    rng = random.Random(seed ^ 0x0C1)
    fnr = fpr = deny_expected = allow_expected = 0
    perm_ms: list[float] = []
    principals = {p: retrieve._load_principal(conn, p) for p in prin_ids}
    for _ in range(min(n_queries, len(rids) * len(prin_ids))):
        pid = rng.choice(prin_ids)
        rid = rng.choice(rids)
        expected = oracle_allow(conn, rid, prin_sets[pid])
        policy = retrieve._build_policy(conn, rid)
        pr = principals[pid]
        t0 = _perf()
        for _r in range(20):
            actual = retrieve.permitted(pr, policy)
        perm_ms.append((_perf() - t0) / 20 / 1e6)
        if expected:
            allow_expected += 1
        else:
            deny_expected += 1
        if actual != expected:
            if (not expected) and actual:
                fnr += 1
            else:
                fpr += 1
    conn.close()
    return {
        "caption": CAPTION,
        "n_records": len(rids),
        "n_incidents": len(incidents),
        "n_groups": built["n_groups"],
        "deny_expected": deny_expected,
        "allow_expected": allow_expected,
        "fnr_leaks": fnr,
        "fpr_outages": fpr,
        "p50_permitted_ms": grade.percentile(perm_ms, 50),
        "p99_permitted_ms": grade.percentile(perm_ms, 99),
    }


def _perf() -> int:
    import time
    return time.perf_counter_ns()


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    csv_path = argv[0] if argv else DEFAULT_CSV
    if not Path(csv_path).exists():
        print(f"UCI incident log not found at {csv_path!r} — download dataset #498 "
              "(see data/raw/SOURCES.md), then: make bench-uci  (or pass the path). "
              "Exiting non-zero (unconfigured).")
        return 2
    r = run_uci_realism(csv_path)
    print(f"[uci-realism] {CAPTION}: {r['n_records']:,} records "
          f"({r['n_incidents']:,} incidents, {r['n_groups']} assignment-groups)")
    print(f"[uci-realism] FNR {r['fnr_leaks']}/{r['deny_expected']:,} deny-expected · "
          f"FPR {r['fpr_outages']}/{r['allow_expected']:,} allow-expected")
    print(f"[uci-realism] P99 permitted() = {r['p99_permitted_ms'] * 1000:.3f} µs "
          f"over the {CAPTION} (NEVER '141k events')")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
