"""Grade the compiler-under-test against the independent oracle + measure latency.
[owner T3, task T3-5]

Spec: Idea/refinement/02-architecture-refinement.md §2.7.

Every allow/deny GROUND TRUTH comes from bench.oracle (a separate implementation);
the COMPILER-UNDER-TEST is store.compile_effective_policy (run at realize time) read
back through retrieve.permitted()/check_access(). FNR/FPR are the disagreement between
the two independent implementations — a genuine cross-check, never self-grading. Any
fail-closed disagreement (revoked/unverified/quarantined/stale) is counted as a real
FNR/FPR; nothing here special-cases a deny path to make a number look good.

Latency is sampled on the hot path (permitted()'s bitmask AND) and reported separately
from the deterministic labels, because wall-clock timing legitimately varies run to run
while the labels/counts are byte-identical at seed 4207.
"""
from __future__ import annotations

import time

from precedent_memory import audit, db, retrieve, store
from precedent_memory.bench import topology
from precedent_memory.bench.oracle import oracle_allow
from precedent_memory.bench.queries import build_queries
from precedent_memory.bench.seed import CANONICAL_SEED


# --------------------------------------------------------------------------- #
# percentile helper (no numpy dependency)
# --------------------------------------------------------------------------- #
def percentile(samples: list[float], p: float) -> float:
    if not samples:
        return 0.0
    s = sorted(samples)
    k = (len(s) - 1) * (p / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


# --------------------------------------------------------------------------- #
# 1. FNR / FPR + hot-path latency (the main 10k run)
# --------------------------------------------------------------------------- #
def run_conformance(conn, manifest, real, queries, *, mode: str = "live",
                    latency_repeats: int = 25) -> dict:
    """Compare oracle vs compiler over every query; sample permitted() + check_access()."""
    # Pre-resolve the compiler-side objects OUTSIDE the timed region so the P50/P99 sample
    # measures the permission CHECK (the bitmask AND), not the DB policy load.
    principals = {p.external_id: retrieve._load_principal(conn, p.external_id)
                  for p in manifest.principals}

    fnr = fpr = agree = 0
    deny_expected = allow_expected = 0
    permitted_ms: list[float] = []
    check_ms: list[float] = []
    disagreements: list[dict] = []
    category_breakdown: dict[str, dict[str, int]] = {}

    for q in queries:
        rid = real.record_id[q.doc_index]
        pset = manifest.principal_role_ids(real, q.principal_ext_id)
        pr = principals[q.principal_ext_id]

        expected = oracle_allow(conn, rid, pset, mode=mode)          # independent ground truth
        policy = retrieve._build_policy(conn, rid)

        # --- P50/P99 sample: the pure bitmask decision, objects pre-built ---
        t0 = time.perf_counter_ns()
        for _ in range(latency_repeats):
            actual = retrieve.permitted(pr, policy, mode)
        permitted_ms.append((time.perf_counter_ns() - t0) / latency_repeats / 1e6)

        # --- overhead sample: full check on the hot path (DB policy load + decide) ---
        t1 = time.perf_counter_ns()
        retrieve.check_access(conn, q.principal_ext_id, rid, mode)
        check_ms.append((time.perf_counter_ns() - t1) / 1e6)

        cat = manifest.docs[q.doc_index].category
        cb = category_breakdown.setdefault(cat, {"allow": 0, "deny": 0})
        cb["allow" if expected else "deny"] += 1

        if expected:
            allow_expected += 1
        else:
            deny_expected += 1
        if actual == expected:
            agree += 1
        else:
            kind = "FNR_leak" if (expected is False and actual is True) else "FPR_outage"
            if kind == "FNR_leak":
                fnr += 1        # oracle DENY, compiler ALLOW  -> a leak
            else:
                fpr += 1        # oracle ALLOW, compiler DENY  -> an outage
            disagreements.append({
                "query_index": q.index, "principal": q.principal_ext_id,
                "doc_index": q.doc_index, "category": cat,
                "oracle": expected, "compiler": actual, "kind": kind,
            })

    return {
        "n_queries": len(queries),
        "deny_expected": deny_expected,
        "allow_expected": allow_expected,
        "agree": agree,
        "fnr_leaks": fnr,
        "fpr_outages": fpr,
        "disagreements": disagreements,
        "category_breakdown": category_breakdown,
        "fnr_rate": (fnr / deny_expected) if deny_expected else 0.0,
        "fpr_rate": (fpr / allow_expected) if allow_expected else 0.0,
        "p50_permitted_ms": percentile(permitted_ms, 50),
        "p99_permitted_ms": percentile(permitted_ms, 99),
        "mean_permitted_ms": sum(permitted_ms) / len(permitted_ms),
        "p50_check_ms": percentile(check_ms, 50),
        "p99_check_ms": percentile(check_ms, 99),
        "overhead_p99_ms": percentile(check_ms, 99),
    }


# --------------------------------------------------------------------------- #
# 2. Synthetic ACL drift + time-to-consistency
# --------------------------------------------------------------------------- #
def run_drift_ttc(seed: int = CANONICAL_SEED, m_flips: int = 200) -> dict:
    """Model an ACL-TIGHTENING window: a source gains a constraint the principal lacks.

    Before a sync recompile the compiler reads the STALE compiled bitmap (stale-allow);
    the oracle reads the raw acl_source and already denies. One sync tick recompiles and
    the stale-allow disappears. We report:
      drift_before = stale-allow fraction while un-synced (proves the window is real)
      drift        = stale-allow fraction AFTER one sync tick (the product's guarantee)
      ttc_ms       = wall-clock from flip observed -> recompiled deny (median)
    The LIVE, poll-interval-anchored drift/TTC land Saturday (Jira /auditing/record clock).
    """
    conn = db.connect(":memory:")
    role_a = store.ensure_constraint(conn, "role", "role:drift-A", "Drift Ops A")
    role_b = store.ensure_constraint(conn, "role", "role:drift-B", "Drift Ops B")
    store.put_principal(conn, "drift-prin", [role_a])   # holds A, NOT B

    now = db.utcnow()
    fresh = now.isoformat()
    rids = []
    for i in range(m_flips):
        ref = f"kb:DRIFT-{i:04d}"
        store.put_source(conn, ref, [role_a], last_verified_at=fresh)
        rids.append((ref, store.store({"kind": "executed_fix", "class_key": f"d|D-{i}|o"},
                                       [ref], conn=conn)))

    # baseline: principal can read all M
    assert all(retrieve.check_access(conn, "drift-prin", rid)[0] for _ref, rid in rids)

    # TIGHTEN each source (add B) at the raw ACL level WITHOUT recompiling (unsynced window)
    import json as _json
    for ref, _rid in rids:
        conn.execute("UPDATE acl_source SET constraint_ids=? WHERE external_ref=?",
                     (_json.dumps(sorted([role_a, role_b])), ref))
    conn.commit()

    # oracle already denies (reads raw); compiler still allows off the stale bitmap
    stale_before = sum(1 for _ref, rid in rids
                       if retrieve.check_access(conn, "drift-prin", rid)[0])
    oracle_denies = sum(1 for _ref, rid in rids
                        if not oracle_allow(conn, rid, {role_a}))

    # one sync tick: recompile every tightened source; measure flip->deny wall-clock
    ttc_samples = []
    for ref, rid in rids:
        sid = store.source_id(conn, ref)
        t0 = time.perf_counter_ns()
        store.recompile_for_source(conn, sid)
        allowed = retrieve.check_access(conn, "drift-prin", rid)[0]
        ttc_samples.append((time.perf_counter_ns() - t0) / 1e6)
        assert not allowed, "recompile must deny the tightened record"
    conn.commit()

    stale_after = sum(1 for _ref, rid in rids
                      if retrieve.check_access(conn, "drift-prin", rid)[0])
    conn.close()
    return {
        "m_flips": m_flips,
        "oracle_denied_immediately": oracle_denies,
        "drift_before": stale_before / m_flips,
        "drift_after": stale_after / m_flips,
        "ttc_median_ms": percentile(ttc_samples, 50),
        "ttc_p99_ms": percentile(ttc_samples, 99),
    }


# --------------------------------------------------------------------------- #
# 3. Derived-memory correctness (Tier-C): ~1k lineage-derived artifacts vs oracle
# --------------------------------------------------------------------------- #
def run_derived_memory(seed: int = CANONICAL_SEED, n_records: int = 1000) -> dict:
    """Grade lineage-DERIVED records (each a union over 2-3 sources) against the oracle.
    Exercises the A-semantics conjunction specifically."""
    import random
    rng = random.Random(seed ^ 0xD1)
    conn = db.connect(":memory:")

    n_roles = 20
    roles = [store.ensure_constraint(conn, "role", f"role:dm-{i}", f"DM Ops {i}")
             for i in range(n_roles)]
    # base sources with random role subsets
    n_base = 30
    base_refs = []
    fresh = db.utcnow().isoformat()
    for i in range(n_base):
        k = rng.choice((0, 1, 1, 2))
        cids = sorted(rng.sample(roles, k)) if k else []
        ref = f"kb:BASE-{i:03d}"
        store.put_source(conn, ref, cids, last_verified_at=fresh)
        base_refs.append(ref)
    # principals with random clearances
    n_prin = 40
    prin_sets = {}
    for i in range(n_prin):
        held = frozenset(r for r in roles if rng.random() < 0.35)
        store.put_principal(conn, f"dm-prin-{i:03d}", sorted(held))
        prin_sets[f"dm-prin-{i:03d}"] = held
    # derived records: lineage = 2-3 base sources
    rids = []
    for i in range(n_records):
        lineage = rng.sample(base_refs, rng.choice((2, 3)))
        rid = store.store({"kind": "executed_fix", "class_key": f"dm|R-{i}|o"}, lineage, conn=conn)
        rids.append(rid)

    total = agree = disagree = 0
    for rid in rids:
        for pid in rng.sample(list(prin_sets), 3):   # 3 probes per derived record
            expected = oracle_allow(conn, rid, prin_sets[pid])
            actual = retrieve.check_access(conn, pid, rid)[0]
            total += 1
            if expected == actual:
                agree += 1
            else:
                disagree += 1
    conn.close()
    return {"n_records": n_records, "probes": total, "agree": agree,
            "disagree": disagree, "correctness": (agree / total) if total else 0.0}


# --------------------------------------------------------------------------- #
# 4. O(1)/O(log n) latency-vs-size curve (Tier-C)
# --------------------------------------------------------------------------- #
def run_latency_curve(sizes=(1000, 5000, 25000, 100000), *, probes: int = 2000,
                      repeats: int = 25, seed: int = CANONICAL_SEED) -> list[dict]:
    """Build a lean restricted store of each size and time permitted()/check_access on
    random records. A flat curve across 100x size is the O(1) permission-check claim."""
    import random
    out = []
    for n in sizes:
        rng = random.Random(seed ^ n)
        conn = db.connect(":memory:")
        role = store.ensure_constraint(conn, "role", "role:curve", "Curve Ops")
        store.put_principal(conn, "curve-prin", [role])
        fresh = db.utcnow().isoformat()
        # one shared restricted source keeps build cheap; each record derives from it
        store.put_source(conn, "kb:CURVE", [role], last_verified_at=fresh)
        rids = [store.store({"kind": "executed_fix", "class_key": f"c|{i}|o"},
                            ["kb:CURVE"], conn=conn) for i in range(n)]
        pr = retrieve._load_principal(conn, "curve-prin")
        sample_rids = [rng.choice(rids) for _ in range(probes)]
        policies = [retrieve._build_policy(conn, rid) for rid in sample_rids]

        perm_ms, chk_ms = [], []
        for rid, pol in zip(sample_rids, policies, strict=True):
            t0 = time.perf_counter_ns()
            for _ in range(repeats):
                retrieve.permitted(pr, pol, "live")
            perm_ms.append((time.perf_counter_ns() - t0) / repeats / 1e6)
            t1 = time.perf_counter_ns()
            retrieve.check_access(conn, "curve-prin", rid)
            chk_ms.append((time.perf_counter_ns() - t1) / 1e6)
        conn.close()
        out.append({
            "n_records": n,
            "p50_permitted_ms": percentile(perm_ms, 50),
            "p99_permitted_ms": percentile(perm_ms, 99),
            "p50_check_ms": percentile(chk_ms, 50),
            "p99_check_ms": percentile(chk_ms, 99),
        })
    return out


# --------------------------------------------------------------------------- #
# 5. Audit coverage over the retrieval path (the bench's own witness; the rigorous
#    coverage proof + dropped-call meta-test live in tests/test_audit_coverage.py)
# --------------------------------------------------------------------------- #
def run_audit_coverage(seed: int = CANONICAL_SEED, sample: int = 300) -> dict:
    """Drive retrieve.retrieve() (which audits every allow AND deny) over a sample and
    assert every decision produced exactly one audit row + the hash chain verifies."""
    conn = db.connect(":memory:")
    m = topology.build_manifest(seed)
    topology.realize(conn, m)
    queries = build_queries(m, seed)[:sample]

    before = conn.execute("SELECT COUNT(*) c FROM audit_log").fetchone()["c"]
    decisions = 0
    for q in queries:
        # retrieve by the record's own class_key so exactly one candidate (this record) is examined
        ck = m.docs[q.doc_index].class_key
        bundle = retrieve.retrieve(q.principal_ext_id, {"class_key": ck}, conn=conn)
        decisions += len(bundle.hits) + bundle.denied_count
    after = conn.execute("SELECT COUNT(*) c FROM audit_log").fetchone()["c"]
    chain_ok = audit.verify_chain(conn=conn, expected_len=after)
    conn.close()
    audited = after - before
    return {"decisions": decisions, "audit_rows_written": audited,
            "coverage": (audited / decisions) if decisions else 1.0,
            "chain_verified": chain_ok}
