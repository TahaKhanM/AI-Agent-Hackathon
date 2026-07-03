"""Bench topology + query-corpus invariants (T3-2 / T3-3).

Verifies the BasedAI protocol dimensions, byte-identical reproducibility at seed 4207,
that effective_policy.required_bits is populated for every restricted doc, and that the
oracle-labelled deny pool clears the >=3,000 rule-of-three floor.
"""
from __future__ import annotations

import pytest

from precedent_memory import db
from precedent_memory.bench import topology
from precedent_memory.bench.oracle import oracle_allow
from precedent_memory.bench.queries import N_QUERIES, build_queries, queries_to_list
from precedent_memory.bench.seed import CANONICAL_SEED
from precedent_memory.bench.topology import (
    N_DOCS,
    N_PRINCIPALS,
    N_ROLES,
    build_manifest,
    manifest_digest,
)


@pytest.fixture
def conn():
    c = db.connect(":memory:")
    try:
        yield c
    finally:
        c.close()


def test_manifest_is_byte_identical_across_runs():
    assert manifest_digest(build_manifest(CANONICAL_SEED)) == \
        manifest_digest(build_manifest(CANONICAL_SEED))


def test_manifest_protocol_dimensions():
    m = build_manifest(CANONICAL_SEED)
    assert len(m.roles) == N_ROLES == 20
    assert len(m.principals) == N_PRINCIPALS == 40
    assert len(m.docs) == N_DOCS == 1000
    # every non-public doc is restricted
    restricted = [d for d in m.docs if d.category != "public"]
    assert len(restricted) == 850


def test_realized_db_has_exact_counts_and_restricted_policies(conn):
    m = build_manifest(CANONICAL_SEED)
    topology.realize(conn, m)

    assert conn.execute(
        "SELECT COUNT(*) c FROM constraint_def WHERE source_system='role'"
    ).fetchone()["c"] == 20
    assert conn.execute("SELECT COUNT(*) c FROM principal").fetchone()["c"] == 40
    assert conn.execute("SELECT COUNT(*) c FROM memory_record").fetchone()["c"] == 1000

    # effective_policy exists for every record; required_bits populated for every restricted one
    assert conn.execute("SELECT COUNT(*) c FROM effective_policy").fetchone()["c"] == 1000
    restricted_rows = conn.execute(
        "SELECT required_bits FROM effective_policy WHERE is_restricted=1"
    ).fetchall()
    assert len(restricted_rows) == 850
    assert all(len(bytes(r["required_bits"])) > 0 for r in restricted_rows)


def test_realization_is_reproducible_in_structure(conn):
    """Two realizations at the same seed produce identical role/record structure
    (timestamps differ by wall-clock, but structure and counts do not)."""
    m1 = build_manifest(CANONICAL_SEED)
    r1 = topology.realize(conn, m1)
    conn2 = db.connect(":memory:")
    r2 = topology.realize(conn2, build_manifest(CANONICAL_SEED))
    assert r1.role_constraint_id == r2.role_constraint_id
    assert set(r1.record_id) == set(r2.record_id)
    conn2.close()


def test_queries_count_and_reproducible():
    m = build_manifest(CANONICAL_SEED)
    q1 = build_queries(m, CANONICAL_SEED)
    q2 = build_queries(m, CANONICAL_SEED)
    assert len(q1) == N_QUERIES == 10000
    assert queries_to_list(q1) == queries_to_list(q2)


def test_oracle_deny_pool_clears_rule_of_three_floor(conn):
    m = build_manifest(CANONICAL_SEED)
    real = topology.realize(conn, m)
    queries = build_queries(m, CANONICAL_SEED)

    deny = allow = 0
    for q in queries:
        pset = m.principal_role_ids(real, q.principal_ext_id)
        rid = real.record_id[q.doc_index]
        if oracle_allow(conn, rid, pset):
            allow += 1
        else:
            deny += 1
    # FNR<0.1% needs >=3000 deny-expected at zero leaks; FPR needs a populous allow pool.
    assert deny >= 3000, f"deny pool too small: {deny}"
    assert allow >= 3000, f"allow pool too small: {allow}"
    assert deny + allow == N_QUERIES
