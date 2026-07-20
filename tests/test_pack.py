"""Evidence Pack v1 + offline verifier — WP-PACK (TDD).

Proves, against a REAL seeded world driven through the REAL gate:
  * a pack is built for EACH seed-4207 demo incident (INC-1 slow-path resolved, INC-2 standing
    fast-path resolved, INC-3 ACL-denied) and each verifies clean via verify_pack;
  * verify_pack FAILS LOUDLY on a tampered byte — and does so via the CHAIN PROOF specifically
    (we re-seal the manifest after tampering, so a manifest-only check could not catch it):
      - a flipped payload byte in an interior row,
      - reordered rows,
      - a truncated tail (with the length + tail anchors re-checked),
      - a wrong tail-hash anchor;
  * a round-trip: the pack's chain_proof rows == the audit-log rows byte-for-byte, and the
    per-incident transcript == the audit rows carrying that incident_id;
  * verify_pack.py imports NOTHING outside the standard library;
  * the pack's canonical_json / GENESIS_HASH agree with the memory layer and the verifier;
  * the standalone `python verify_pack.py <pack>` CLI exits 0 on a good pack, non-zero on a
    tampered one;
  * every pack carries the "evidence support, not a compliance determination" disclaimer.
"""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

import verify_pack
from console.demo_state import SCHED_CLASS_STANDING
from gate import service
from gate.models import OutcomeRequest, ProposeRequest, StructuredExtraction
from gate.world import build_seeded_world
from precedent_memory import audit as audit_mod
from precedent_memory import db as memdb
from precedent_pack import builder

REPO_ROOT = Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------- fixtures
@pytest.fixture
def driven_world(tmp_path):
    """A fresh seed-4207 world with all three demo incidents driven through the gate:
    INC-1 approved (slow path), INC-2 standing (fast path), INC-3 denied (restricted)."""
    world = build_seeded_world(tmp_path / "w", standing_classes=(SCHED_CLASS_STANDING,))

    incidents = {n: world.tools.incident(n) for n in (1, 2, 3)}

    def _propose(n):
        inc = incidents[n]
        return service.propose(world, ProposeRequest(
            incident_id=inc["incident_id"], principal="scheduling-ops",
            raw_text=inc["raw_text"], source="sim", observed_at=inc["observed_at"],
            structured=StructuredExtraction(**inc["structured"])))

    r1 = _propose(1)
    assert r1.decision == "needs-approval"
    service.report_outcome(world, OutcomeRequest(
        ref=r1.ref, decision="approve", approver_principal="ops-lead"))

    r2 = _propose(2)
    assert r2.decision == "allow-standing"
    service.report_outcome(world, OutcomeRequest(ref=r2.ref))

    r3 = _propose(3)
    assert r3.decision == "deny"

    try:
        yield world, incidents
    finally:
        world.close()


def _pack(world, incidents, n):
    inc = incidents[n]
    return builder.build_pack(world.conn, inc["incident_id"], incident=inc)


# --------------------------------------------------------------------------- constants agree
def test_canonical_and_genesis_agree_across_layers():
    assert builder.GENESIS_HASH == memdb.GENESIS_HASH == verify_pack.GENESIS_HASH
    sample = {"b": 2, "a": [1, {"z": None, "y": "x"}]}
    assert builder.canonical_json(sample) == memdb.canonical_json(sample) \
        == verify_pack.canonical_json(sample)


# --------------------------------------------------------------------------- happy path
@pytest.mark.parametrize("n", [1, 2, 3])
def test_pack_for_each_demo_incident_verifies(driven_world, n):
    world, incidents = driven_world
    pack = _pack(world, incidents, n)

    assert pack["incident"]["incident_id"] == f"INC-{n}"
    assert "evidence support, not a compliance determination" in pack["disclaimer"]
    assert pack["manifest"]["digest"] and pack["manifest"]["secret_key"] is None
    # The pack has an incident transcript and marks its rows in the chain.
    assert pack["execution_transcript"], "every demo incident has an audit narrative"
    assert pack["chain_proof"]["incident_row_seqs"]

    assert verify_pack.verify_pack(pack) == [], "a freshly built pack must verify clean"


def test_decisions_are_faithful(driven_world):
    world, incidents = driven_world
    p1 = _pack(world, incidents, 1)
    p2 = _pack(world, incidents, 2)
    p3 = _pack(world, incidents, 3)

    assert p1["decision"]["decision"] == "needs-approval"
    assert p1["decision"]["proposer_principal"] == "scheduling-ops"
    assert p1["decision"]["approver_principal"] == "ops-lead"      # four-eyes recorded
    assert p1["verification"]["verified"] is True
    assert p1["verification"]["outcome"] == "resolved"
    assert p1["rollback"] is None

    assert p2["decision"]["decision"] == "allow-standing"
    assert p2["verification"]["verified"] is True

    assert p3["decision"]["decision"] == "deny"
    assert p3["decision"]["reason"] == "restricted"
    assert p3["verification"]["verified"] is False


# --------------------------------------------------------------------------- round-trip
def test_chain_proof_roundtrips_audit_log(driven_world):
    world, incidents = driven_world
    pack = _pack(world, incidents, 1)

    live = world.conn.execute(
        "SELECT seq, ts, actor, event_type, payload, prev_hash, hash "
        "FROM audit_log ORDER BY seq ASC").fetchall()
    rows = pack["chain_proof"]["rows"]
    assert len(rows) == len(live) == pack["chain_proof"]["expected_len"]
    for got, exp in zip(rows, live, strict=True):
        assert got["seq"] == exp["seq"]
        assert got["ts"] == exp["ts"]
        assert got["actor"] == exp["actor"]
        assert got["event_type"] == exp["event_type"]
        assert got["payload"] == exp["payload"]      # the raw canonical string, unchanged
        assert got["prev_hash"] == exp["prev_hash"]
        assert got["hash"] == exp["hash"]

    # The independent memory-layer verifier agrees the chain + anchors are intact.
    tail = live[-1]["hash"]
    assert audit_mod.verify_chain(conn=world.conn, expected_len=len(live),
                                  expected_tail_hash=tail) is True

    # Every transcript row is an audit row carrying THIS incident_id, in order.
    inc_seqs = [r["seq"] for r in live if json.loads(r["payload"]).get("incident_id") == "INC-1"]
    assert [e["seq"] for e in pack["execution_transcript"]] == inc_seqs
    assert pack["chain_proof"]["incident_row_seqs"] == inc_seqs


# --------------------------------------------------------------------------- tamper detection
def _reseal(pack):
    """Re-seal the manifest so a manifest-only check would PASS — isolating the chain proof as
    the thing that must catch the tamper."""
    body = {k: v for k, v in pack.items() if k != "manifest"}
    pack["manifest"]["digest"] = builder.manifest_digest(body)
    return pack


def test_flipped_payload_byte_is_caught_by_chain(driven_world):
    world, incidents = driven_world
    pack = _pack(world, incidents, 1)
    rows = pack["chain_proof"]["rows"]

    # Flip a byte in an INTERIOR row's payload (a field the verifier MUST recompute over).
    i = len(rows) // 2
    p = json.loads(rows[i]["payload"])
    p["injected"] = "tamper"
    rows[i]["payload"] = builder.canonical_json(p)
    _reseal(pack)   # manifest now matches the tampered bytes — only the CHAIN can catch it

    errors = verify_pack.verify_pack(pack)
    assert errors, "a flipped payload byte must fail verification"
    assert any("row hash mismatch" in e for e in errors)


def test_reordered_rows_are_caught(driven_world):
    world, incidents = driven_world
    pack = _pack(world, incidents, 1)
    rows = pack["chain_proof"]["rows"]

    rows[1], rows[2] = rows[2], rows[1]     # swap two adjacent interior rows
    _reseal(pack)

    errors = verify_pack.verify_pack(pack)
    assert errors and any("chain break" in e for e in errors)


def test_truncated_tail_is_caught_by_anchors(driven_world):
    world, incidents = driven_world
    pack = _pack(world, incidents, 1)

    # Drop the last row. The remaining prefix STILL hash-links — only the length + tail-hash
    # anchors expose the truncation. Re-seal the manifest to prove the anchors do the work.
    pack["chain_proof"]["rows"].pop()
    _reseal(pack)

    errors = verify_pack.verify_pack(pack)
    assert errors
    assert any("length anchor mismatch" in e for e in errors)
    assert any("tail-hash anchor mismatch" in e for e in errors)


def test_wrong_tail_anchor_is_caught(driven_world):
    world, incidents = driven_world
    pack = _pack(world, incidents, 1)

    pack["chain_proof"]["expected_tail_hash"] = "0" * 64   # a plausible-looking but wrong anchor
    _reseal(pack)

    errors = verify_pack.verify_pack(pack)
    assert errors and any("tail-hash anchor mismatch" in e for e in errors)


def test_manifest_catches_edit_outside_the_chain(driven_world):
    world, incidents = driven_world
    pack = _pack(world, incidents, 1)

    # Edit a field OUTSIDE chain_proof (the human-readable decision) WITHOUT re-sealing: the
    # sha256 manifest over the pack's canonical bytes must catch it.
    pack["decision"]["approver_principal"] = "mallory"
    errors = verify_pack.verify_pack(pack)
    assert errors and any("manifest digest mismatch" in e for e in errors)


# --------------------------------------------------------------------------- HTML render
def test_html_is_self_contained_and_carries_disclaimer(driven_world):
    world, incidents = driven_world
    pack = _pack(world, incidents, 1)
    doc = builder.render_html(pack)

    assert "evidence support, not a compliance determination" in doc
    assert "INC-1" in doc
    assert "<pre id='pack-json'>" in doc            # embedded verifiable bytes
    # No external references — renders on an air-gapped laptop.
    for needle in ("http://", "https://", "src=", "cdn"):
        assert needle not in doc, f"HTML must be self-contained (found {needle!r})"


# --------------------------------------------------------------------------- verifier hygiene
def test_verify_pack_imports_only_stdlib():
    src = (REPO_ROOT / "verify_pack.py").read_text()
    tree = ast.parse(src)
    stdlib = set(getattr(sys, "stdlib_module_names", set()))
    assert stdlib, "need Python 3.10+ for sys.stdlib_module_names"
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imported.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imported.add(node.module.split(".")[0])
    imported.discard("__future__")
    offenders = {m for m in imported if m not in stdlib}
    assert not offenders, f"verify_pack.py imports non-stdlib modules: {offenders}"


# --------------------------------------------------------------------------- CLI e2e
def test_cli_exits_zero_on_good_and_nonzero_on_tampered(driven_world, tmp_path):
    world, incidents = driven_world
    pack = _pack(world, incidents, 1)

    good = tmp_path / "INC-1.pack.json"
    builder.write_pack(pack, good)
    r = subprocess.run([sys.executable, str(REPO_ROOT / "verify_pack.py"), str(good)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr + r.stdout
    assert "PACK VERIFIED" in r.stdout

    # Tamper a payload byte on disk, re-seal the manifest, and confirm a non-zero exit.
    tampered = json.loads(good.read_text())
    trows = tampered["chain_proof"]["rows"]
    p = json.loads(trows[0]["payload"])
    p["x"] = "evil"
    trows[0]["payload"] = builder.canonical_json(p)
    tampered["manifest"]["digest"] = builder.manifest_digest(
        {k: v for k, v in tampered.items() if k != "manifest"})
    bad = tmp_path / "INC-1.tampered.json"
    bad.write_text(builder.canonical_json(tampered))
    r2 = subprocess.run([sys.executable, str(REPO_ROOT / "verify_pack.py"), str(bad)],
                        capture_output=True, text=True)
    assert r2.returncode == 1
    assert "FAILED" in r2.stdout


def test_generate_demo_packs_writes_verifiable_bundles(tmp_path):
    written = builder.generate_demo_packs(tmp_path / "packs")
    ids = {w["incident_id"] for w in written}
    assert ids == {"INC-1", "INC-2", "INC-3"}
    for w in written:
        assert Path(w["json"]).exists() and Path(w["html"]).exists()
        r = subprocess.run([sys.executable, str(REPO_ROOT / "verify_pack.py"), w["json"]],
                           capture_output=True, text=True)
        assert r.returncode == 0, f"{w['incident_id']}: {r.stdout}{r.stderr}"


# --------------------------------------------------------------------------- fail-closed (item 1)
def _run_cli(path, *flags):
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "verify_pack.py"), *flags, str(path)],
        capture_output=True, text=True)


@pytest.mark.parametrize("name,mutate", [
    ("incident_non_dict", lambda p: p.__setitem__("incident", "not-a-dict")),
    ("chain_proof_missing", lambda p: p.pop("chain_proof", None)),
    ("chain_proof_non_dict", lambda p: p.__setitem__("chain_proof", ["oops"])),
    ("chain_proof_string", lambda p: p.__setitem__("chain_proof", "oops")),
    ("incident_row_seqs_non_iterable",
     lambda p: p["chain_proof"].__setitem__("incident_row_seqs", 5)),
    ("rows_non_dict_items", lambda p: p["chain_proof"].__setitem__("rows", [123])),
    ("rows_non_list", lambda p: p["chain_proof"].__setitem__("rows", {"seq": 1})),
    ("manifest_non_dict", lambda p: p.__setitem__("manifest", "oops")),
])
def test_malformed_structure_is_fail_closed_no_traceback(driven_world, tmp_path, name, mutate):
    world, incidents = driven_world
    pack = _pack(world, incidents, 1)
    mutate(pack)
    # verify_pack() must return a reason list — NEVER raise.
    errors = verify_pack.verify_pack(pack)
    assert isinstance(errors, list) and errors, f"{name}: expected a clean INVALID verdict"
    # ...and the CLI must exit non-zero with NO python traceback and a clear reason.
    bad = tmp_path / f"{name}.json"
    bad.write_text(json.dumps(pack))
    r = _run_cli(bad)
    assert r.returncode == 1, f"{name}: rc={r.returncode} {r.stdout}{r.stderr}"
    assert "Traceback" not in (r.stdout + r.stderr), f"{name}: leaked a traceback"
    assert "FAILED" in r.stdout, f"{name}: {r.stdout}"


@pytest.mark.parametrize("blob", ['{"incident":', "not json at all", "", "[1,2,3"])
def test_unreadable_pack_is_fail_closed_no_traceback(tmp_path, blob):
    bad = tmp_path / "unreadable.json"
    bad.write_text(blob)
    r = _run_cli(bad)
    assert r.returncode != 0
    assert "Traceback" not in (r.stdout + r.stderr), "leaked a traceback on unreadable input"


def test_verify_pack_never_raises_on_arbitrary_garbage():
    for junk in (None, 42, "a string", [1, 2, 3], {"chain_proof": 5},
                 {"incident": 7, "chain_proof": {"rows": [1, 2]}}):
        out = verify_pack.verify_pack(junk)
        assert isinstance(out, list) and out, f"garbage {junk!r} must yield a reason list"


# ------------------------------------------ derived-display binding to the chain (item 2)
def test_tampered_decision_display_fails_even_after_reseal(driven_world):
    world, incidents = driven_world
    pack = _pack(world, incidents, 1)
    assert verify_pack.verify_pack(pack) == []
    pack["decision"]["approver_principal"] = "mallory"   # chain rows untouched
    _reseal(pack)                                         # manifest now matches the forgery
    errors = verify_pack.verify_pack(pack)
    assert errors and any("decision" in e for e in errors), errors


def test_tampered_verification_display_fails_even_after_reseal(driven_world):
    world, incidents = driven_world
    pack = _pack(world, incidents, 1)
    pack["verification"]["verified"] = not pack["verification"]["verified"]
    _reseal(pack)
    errors = verify_pack.verify_pack(pack)
    assert errors and any("verification" in e for e in errors), errors


def test_tampered_transcript_display_fails_even_after_reseal(driven_world):
    world, incidents = driven_world
    pack = _pack(world, incidents, 1)
    pack["execution_transcript"][0]["actor"] = "mallory"
    _reseal(pack)
    errors = verify_pack.verify_pack(pack)
    assert errors and any("transcript" in e for e in errors), errors


def test_tampered_rollback_display_fails_even_after_reseal(driven_world):
    world, incidents = driven_world
    pack = _pack(world, incidents, 1)
    pack["rollback"] = {"kind": "restored_pre_state", "detail": "forged"}
    _reseal(pack)
    errors = verify_pack.verify_pack(pack)
    assert errors and any("rollback" in e for e in errors), errors


# --------------------------------------------- manifest metadata bound to the digest (item 3)
def test_manifest_secret_key_edit_fails(driven_world):
    world, incidents = driven_world
    pack = _pack(world, incidents, 1)
    assert verify_pack.verify_pack(pack) == []
    # digest excludes the manifest field, so this isolated edit leaves the digest matching.
    pack["manifest"]["secret_key"] = "leaked-key"
    errors = verify_pack.verify_pack(pack)
    assert errors and any("manifest" in e for e in errors), errors


def test_manifest_algo_edit_fails(driven_world):
    world, incidents = driven_world
    pack = _pack(world, incidents, 1)
    pack["manifest"]["algo"] = "md5"
    errors = verify_pack.verify_pack(pack)
    assert errors and any("manifest" in e for e in errors), errors


# ------------------------------------------------------- quiet mode keeps the caveat (item 4)
def test_quiet_mode_still_prints_caveat(driven_world, tmp_path):
    world, incidents = driven_world
    pack = _pack(world, incidents, 1)
    good = tmp_path / "INC-1.pack.json"
    builder.write_pack(pack, good)
    r = _run_cli(good, "-q")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "evidence support, not a compliance determination" in r.stdout
    assert "secret key" in r.stdout, "the no-secret-key caveat must survive -q"
