"""P1.9 — query-time inference prevention, oracle-graded (zero-LLM).

Each mechanism is graded against an INDEPENDENT reference implementation (not the code under
test), mirroring the conformance-bench oracle discipline:
- (a) probing detection vs a naive Python re-count of windowed retrieval denials;
- (b) bundle cross-boundary vs a naive pairwise-disjointness reference.
Also asserts both mechanisms fail toward non-action (flag/deny) and audit their decision.
"""
from __future__ import annotations

import itertools
from datetime import timedelta

from precedent_memory import db, store
from precedent_memory import probing_detection as pd


def _raw_denial(conn, actor: str, seconds_ago: float) -> None:
    """Insert a retrieval_denied audit row with a controlled timestamp (bypasses the hash chain —
    fine here: the detector only counts by actor/type/ts, it does not verify the chain)."""
    ts = (db.utcnow() - timedelta(seconds=seconds_ago)).isoformat()
    conn.execute(
        "INSERT INTO audit_log(ts, actor, event_type, payload, prev_hash, hash) "
        "VALUES(?,?,?,?,?,?)",
        (ts, actor, "retrieval_denied", "{}", db.GENESIS_HASH, "0" * 64))
    conn.commit()


# --------------------------------------------------------------------------- #
# (a) probing detection — independent oracle
# --------------------------------------------------------------------------- #
def _oracle_denials(conn, principal: str, window_secs: int) -> int:
    """Independent re-count in Python over ALL audit rows (not the module's SQL COUNT)."""
    cutoff = db.utcnow() - timedelta(seconds=window_secs)
    n = 0
    for r in conn.execute("SELECT actor, event_type, ts FROM audit_log").fetchall():
        if r["event_type"] == "retrieval_denied" and r["actor"] == principal:
            ts = db.parse_iso(r["ts"])
            if ts is not None and ts >= cutoff:
                n += 1
    return n


def test_probing_flagged_at_threshold_matches_oracle(conn):
    for _ in range(6):
        _raw_denial(conn, "prober", 1)
    res = pd.detect_probing(conn, "prober", threshold=5, window_secs=60)
    assert res["denials"] == _oracle_denials(conn, "prober", 60) == 6
    assert res["flagged"] is True and res["throttle"] is True
    assert conn.execute("SELECT COUNT(*) c FROM audit_log WHERE event_type='probing_detected'"
                        ).fetchone()["c"] == 1     # the flag is audited


def test_probing_below_threshold_not_flagged(conn):
    for _ in range(3):
        _raw_denial(conn, "p", 1)
    res = pd.detect_probing(conn, "p", threshold=5, window_secs=60)
    assert res["flagged"] is False and res["denials"] == _oracle_denials(conn, "p", 60) == 3
    assert conn.execute("SELECT COUNT(*) c FROM audit_log WHERE event_type='probing_detected'"
                        ).fetchone()["c"] == 0


def test_probing_window_excludes_stale_denials(conn):
    for _ in range(6):
        _raw_denial(conn, "slow", 120)                # 2 min ago — outside a 60s window
    res = pd.detect_probing(conn, "slow", threshold=5, window_secs=60)
    assert res["denials"] == _oracle_denials(conn, "slow", 60) == 0
    assert res["flagged"] is False                    # an old, spread-out sweep does not trip


def test_probing_is_per_principal(conn):
    for _ in range(6):
        _raw_denial(conn, "a", 1)
    for _ in range(2):
        _raw_denial(conn, "b", 1)
    assert pd.detect_probing(conn, "a", threshold=5)["flagged"] is True
    assert pd.detect_probing(conn, "b", threshold=5)["flagged"] is False


# --------------------------------------------------------------------------- #
# (b) bundle cross-boundary co-occurrence — independent oracle
# --------------------------------------------------------------------------- #
def _oracle_cross(required_sets) -> bool:
    sets = [set(s) for s in required_sets if s]
    return any(not (sets[i] & sets[j])
               for i in range(len(sets)) for j in range(i + 1, len(sets)))


def test_bundle_cross_boundary_matches_oracle():
    universe = [set(), {1}, {2}, {1, 2}, {3}]
    for combo in itertools.product(universe, repeat=3):
        assert pd.bundle_cross_boundary(combo) == _oracle_cross(combo)


def test_bundle_cross_boundary_key_cases():
    assert pd.bundle_cross_boundary([{1}, {2}]) is True        # disjoint boundaries -> cross
    assert pd.bundle_cross_boundary([{1, 2}, {2}]) is False    # share a constraint -> same lattice
    assert pd.bundle_cross_boundary([{1}, set()]) is False     # public ignored
    assert pd.bundle_cross_boundary([{1}, {1}]) is False       # identical boundary
    assert pd.bundle_cross_boundary([{1}]) is False            # a single record never crosses


def _store_record(conn, fp, lineage):
    return store.store({"kind": "executed_fix", "fingerprint": fp, "class_key": fp,
                        "body": {"fix": "x"}}, lineage, conn=conn)


def test_assess_bundle_denies_disjoint_boundaries(scenario):
    conn = scenario["conn"]
    rid_r = _store_record(conn, "fp-r", ["kb:KB-0004"])        # RIGHTS only
    rid_s = _store_record(conn, "fp-s", ["jira:MEDIA-113"])    # SCHED only
    res = pd.assess_bundle(conn, "both", [rid_r, rid_s])       # even 'both' cannot co-mingle them
    assert res["allowed"] is False and res["reason"] == "cross_boundary_cooccurrence"
    assert conn.execute(
        "SELECT COUNT(*) c FROM audit_log WHERE event_type='bundle_cross_boundary_denied'"
    ).fetchone()["c"] == 1


def test_assess_bundle_allows_same_boundary(scenario):
    conn = scenario["conn"]
    rid1 = _store_record(conn, "fp-s1", ["jira:MEDIA-113"])
    rid2 = _store_record(conn, "fp-s2", ["jira:MEDIA-113"])
    res = pd.assess_bundle(conn, "sched_only", [rid1, rid2])
    assert res["allowed"] is True and res["reason"] is None


def test_assess_bundle_public_records_never_cross(scenario):
    conn = scenario["conn"]
    rid_pub = _store_record(conn, "fp-pub", ["kb:KB-0001"])    # public
    rid_r = _store_record(conn, "fp-r2", ["kb:KB-0004"])       # RIGHTS
    assert pd.assess_bundle(conn, "rights_only", [rid_pub, rid_r])["allowed"] is True


def test_inference_prevention_bench_passes():
    """The additional (P1.9) bench section reports PASS — both mechanisms fire deterministically."""
    from precedent_memory.bench import inference_prevention as ib
    res = ib.run()
    assert res["probing_detection"]["flagged"] and res["probing_detection"]["audited"] == 1
    assert res["cross_boundary"]["disjoint_bundle_denied"]
    assert res["cross_boundary"]["same_boundary_allowed"]
    assert "PASS" in ib.section_md(res)


def test_probing_module_imports_no_llm():
    """probing_detection.py must import no model client / registry (Rule 2). The check-open-weight
    grep + the invariants-guard oracle enforce the same over all of precedent_memory/."""
    import pathlib
    src = (pathlib.Path(__file__).resolve().parent.parent / "probing_detection.py").read_text()
    for ln in src.splitlines():
        if ln.lstrip().startswith(("import ", "from ")):
            assert "venice" not in ln and ".models" not in ln
