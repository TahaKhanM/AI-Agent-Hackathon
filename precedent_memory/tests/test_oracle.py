"""Tests for the INDEPENDENT bench oracle (precedent_memory.bench.oracle).

Part A asserts the oracle's allow/deny labels against the canonical two-team
conjunction scenario and every fail-closed variant. It is legitimate to use
`store` HERE (in the test) to build DB state — only the oracle MODULE must stay
clean of the compiler.

Part B is the CI credibility check: it parses oracle.py's AST and proves the
module imports neither store nor retrieve, calls none of the compiler's bitmap
helpers, and never reads the compiled effective_policy / required_bits. If the
oracle ever mirrored the code it grades, the whole cross-check would be circular.
"""
from __future__ import annotations

import ast
from pathlib import Path

from precedent_memory import store
from precedent_memory.bench.oracle import oracle_allow

ORACLE_PATH = Path(__file__).parent.parent / "bench" / "oracle.py"


# --------------------------------------------------------------------------- #
# Part A — label tests against the canonical scenario
# --------------------------------------------------------------------------- #
def _rec(conn, fp, lineage):
    return store.store(
        {"kind": "executed_fix", "fingerprint": fp, "body": {"fix": "secret"}},
        lineage, conn=conn,
    )


def test_public_record_allows_everyone(scenario):
    conn = scenario["conn"]
    rights, sched = scenario["rights"], scenario["sched"]
    rec = _rec(conn, "fp-pub", ["kb:KB-0001"])  # required {} (public)
    assert oracle_allow(conn, rec, {rights}) is True
    assert oracle_allow(conn, rec, {sched}) is True
    assert oracle_allow(conn, rec, {rights, sched}) is True
    assert oracle_allow(conn, rec, set()) is True


def test_rights_record_requires_rights(scenario):
    conn = scenario["conn"]
    rights, sched = scenario["rights"], scenario["sched"]
    rec = _rec(conn, "fp-rights", ["kb:KB-0004"])  # required {rights}
    assert oracle_allow(conn, rec, {rights}) is True            # rights_only
    assert oracle_allow(conn, rec, {rights, sched}) is True     # both
    assert oracle_allow(conn, rec, {sched}) is False            # sched_only
    assert oracle_allow(conn, rec, set()) is False              # nobody


def test_sched_record_requires_sched(scenario):
    conn = scenario["conn"]
    rights, sched = scenario["rights"], scenario["sched"]
    rec = _rec(conn, "fp-sched", ["jira:MEDIA-113"])  # required {sched}
    assert oracle_allow(conn, rec, {sched}) is True             # sched_only
    assert oracle_allow(conn, rec, {rights, sched}) is True     # both
    assert oracle_allow(conn, rec, {rights}) is False           # rights_only
    assert oracle_allow(conn, rec, set()) is False              # nobody


def test_multisource_record_requires_conjunction(scenario):
    """The incident-3 case: a fix derived from BOTH a rights KB article AND a
    scheduling ticket is readable ONLY by a principal holding BOTH constraints —
    strictest-label would wrongly allow partial clearance; conjunction denies."""
    conn = scenario["conn"]
    rights, sched = scenario["rights"], scenario["sched"]
    rec = _rec(conn, "fp-both", ["kb:KB-0004", "jira:MEDIA-113"])  # required {rights, sched}
    assert oracle_allow(conn, rec, {rights, sched}) is True     # both
    assert oracle_allow(conn, rec, {rights}) is False           # rights_only
    assert oracle_allow(conn, rec, {sched}) is False            # sched_only
    assert oracle_allow(conn, rec, set()) is False              # nobody


# --- fail-closed variants: each must DENY even the fully-cleared principal ----
def test_revoked_source_denies_even_fully_cleared(scenario):
    conn = scenario["conn"]
    rights, sched = scenario["rights"], scenario["sched"]
    rec = _rec(conn, "fp-rev", ["kb:KB-0004"])
    assert oracle_allow(conn, rec, {rights, sched}) is True     # baseline
    store.put_source(conn, "kb:KB-0004", [rights], revoked=1)
    assert oracle_allow(conn, rec, {rights, sched}) is False


def test_quarantined_record_denies_even_fully_cleared(scenario):
    conn = scenario["conn"]
    rights, sched = scenario["rights"], scenario["sched"]
    rec = _rec(conn, "fp-quar", ["kb:KB-0004"])
    conn.execute("UPDATE memory_record SET status='quarantined' WHERE id=?", (rec,))
    assert oracle_allow(conn, rec, {rights, sched}) is False


def test_tombstoned_record_denies_even_fully_cleared(scenario):
    conn = scenario["conn"]
    rights, sched = scenario["rights"], scenario["sched"]
    rec = _rec(conn, "fp-tomb", ["kb:KB-0004"])
    conn.execute("UPDATE memory_record SET status='tombstoned' WHERE id=?", (rec,))
    assert oracle_allow(conn, rec, {rights, sched}) is False


def test_stale_freshness_denies_but_fresh_control_allows(scenario, iso):
    conn = scenario["conn"]
    rights = scenario["rights"]
    # age kb:KB-0004 3600s into the past -> well beyond the 60s window
    store.put_source(conn, "kb:KB-0004", [rights], last_verified_at=iso(3600))
    stale = _rec(conn, "fp-stale", ["kb:KB-0004"])
    assert oracle_allow(conn, stale, {rights}, mode="live") is False

    # fresh control: a restricted record with the same clearance is allowed
    store.put_source(conn, "jira:MEDIA-113", [scenario["sched"]], last_verified_at=iso(1))
    fresh = _rec(conn, "fp-fresh", ["jira:MEDIA-113"])
    assert oracle_allow(conn, fresh, {scenario["sched"]}, mode="live") is True


def test_fallback_mode_denies_restricted_but_serves_public(scenario):
    conn = scenario["conn"]
    rights, sched = scenario["rights"], scenario["sched"]
    restricted = _rec(conn, "fp-fb-r", ["kb:KB-0004"])
    public = _rec(conn, "fp-fb-p", ["kb:KB-0001"])
    assert oracle_allow(conn, restricted, {rights, sched}, mode="fallback") is False
    assert oracle_allow(conn, public, set(), mode="fallback") is True


def test_unverified_provenance_denies_even_fully_cleared(scenario):
    """A record whose lineage references an unknown source inherits the reserved
    UNVERIFIED constraint (auto-created by store); no principal ever holds it, so
    even a fully-cleared principal is denied — provenance is unvouchable."""
    conn = scenario["conn"]
    rights, sched = scenario["rights"], scenario["sched"]
    rec = _rec(conn, "fp-unverified", ["unknown:NOPE"])
    assert oracle_allow(conn, rec, {rights, sched}) is False


def test_missing_record_denies(scenario):
    conn = scenario["conn"]
    assert oracle_allow(conn, 999999, {scenario["rights"], scenario["sched"]}) is False


# --------------------------------------------------------------------------- #
# Part B — structural independence guard (the CI credibility check)
# --------------------------------------------------------------------------- #
def test_oracle_is_structurally_independent():
    """Parse oracle.py's AST and prove it shares NO decision code with the compiler
    it grades. Uses ast (not substring grep) because the docstring legitimately
    contains the words 'store' and 'retrieve'."""
    tree = ast.parse(ORACLE_PATH.read_text())

    # (a) imports: nothing named/ending in 'store' or 'retrieve'; db + stdlib ok.
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            imported.append(base)
            imported += [f"{base}.{alias.name}" for alias in node.names]
    for name in imported:
        leaf = name.rsplit(".", 1)[-1]
        assert leaf not in ("store", "retrieve"), (
            f"oracle.py imports '{name}' — it MUST NOT import the compiler it grades"
        )

    # (b) no compiler helper is referenced by name (called or attribute-accessed).
    forbidden_names = {
        "is_superset", "ids_to_bits", "bits_to_ids", "blob_to_bits",
        "permitted", "check_access", "_build_policy", "grant_bits",
    }
    used: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            used.add(node.attr)
    leaked = forbidden_names & used
    assert not leaked, (
        f"oracle.py references compiler internals {sorted(leaked)} — it must "
        "recompute from raw acl_source, not reuse the bitmap decision path"
    )

    # (c) no SQL string reads the compiled policy tables/columns. Scoped to SQL
    #     literals (those containing SELECT/FROM/...) so the module docstring —
    #     which legitimately names effective_policy while describing what the
    #     oracle does NOT read — is not a false positive.
    # Identify the module docstring node itself (first stmt is a bare string expr)
    # so we can skip it — it names these tables only to say the oracle avoids them.
    docstring_node = None
    if (tree.body and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Constant)
            and isinstance(tree.body[0].value.value, str)):
        docstring_node = tree.body[0].value
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        if node is docstring_node:
            continue
        lowered = node.value.lower()
        looks_like_sql = any(kw in lowered for kw in ("select", "from", "where", "update"))
        if not looks_like_sql:
            continue
        assert "effective_policy" not in lowered, (
            "oracle.py SQL must not read the compiled effective_policy table"
        )
        assert "required_bits" not in lowered, (
            "oracle.py SQL must not read the compiled required_bits column"
        )
