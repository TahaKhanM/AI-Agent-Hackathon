#!/usr/bin/env python3
"""Offline Evidence Pack verifier — STDLIB ONLY.  [WP-PACK]

Verifies a Precedent Evidence Pack (produced by ``precedent_pack``) on an auditor's laptop with
NO network, NO third-party packages, and NO secret key. A test (tests/test_pack.py) asserts this
file imports nothing outside the Python standard library — keep it that way.

What "verify" means here, and its honest limits:

  1. MANIFEST — recompute sha256 over the pack's canonical bytes (excluding the manifest field)
     and compare. Catches any edited byte anywhere in the pack body. The manifest's own metadata
     (algo, scope, secret_key, self-authenticating flag) is NOT covered by that digest, so it is
     checked separately against the fixed, expected template — an isolated edit to a manifest
     sub-field is therefore still caught.
  2. CHAIN — recompute the hash-chained audit log from GENESIS: every row's prev_hash must link
     to the previous row's hash, and every row's hash must equal
     sha256("prev|ts|actor|event_type|payload"). Catches a flipped payload byte and reordered
     rows even if the manifest were re-sealed by a forger.
  3. ANCHORS — the row count must equal ``expected_len`` and the last row's hash must equal
     ``expected_tail_hash``. A bare hash chain cannot detect TAIL truncation on its own (every
     remaining prefix still verifies); the length + tail-hash anchors make it detectable.
  4. INCIDENT ROWS — every seq the pack attributes to the incident must be present in the chain.
  5. DISPLAY BINDING — the human-readable sections (decision, verification, execution_transcript,
     rollback) are RE-DERIVED from the chain rows and must match the embedded sections. Without
     this a keyless forger who rebuilds nothing could still rewrite the readable narrative while
     the tamper-evident audit rows stayed intact; re-derivation binds the narrative to the chain.

Honest limitation (documented, not hidden): the anchors live INSIDE the pack, so a forger who
rebuilds the ENTIRE chain can produce a self-consistent forgery — there is no secret key to stop
that. The strongest assurance is to compare ``expected_tail_hash`` against a tail hash re-derived
INDEPENDENTLY from the live audit database. This verifier prints that caveat on every run.

FAIL-CLOSED: any malformed / missing / wrong-typed field yields a clean INVALID verdict (a reason
string) and a non-zero exit — NEVER a Python traceback.

Exit code: 0 = verified; 1 = tamper/verification failure; 2 = usage / unreadable pack.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys

GENESIS_HASH = "0" * 64

# The manifest's own metadata is not covered by its digest (the digest is taken over the pack
# EXCLUDING the manifest field). These are the fixed values precedent_pack.builder emits; the
# verifier requires them verbatim so an isolated edit to a manifest sub-field is still caught.
_MANIFEST_ALGO = "sha256"
_MANIFEST_SCOPE = "canonical_json(pack) excluding the 'manifest' field"

CAVEAT = (
    "NOTE: This confirms internal consistency without a secret key. For the strongest assurance, "
    "compare expected_tail_hash against a tail hash re-derived independently from the live audit "
    "database. This pack is evidence support, not a compliance determination."
)


def canonical_json(obj) -> str:
    """Deterministic JSON — IDENTICAL formula to precedent_memory.db and precedent_pack."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _row_hash(prev_hash, ts, actor, event_type, payload_json) -> str:
    material = f"{prev_hash}|{ts or ''}|{actor or ''}|{event_type}|{payload_json}"
    return _sha256_hex(material)


# --------------------------------------------------------------------------- #
# derived-section re-derivation — a stdlib-only mirror of precedent_pack.builder's reducers.
# These MUST stay byte-for-byte equivalent to builder._decision_block / _outcome_block etc.; a
# freshly built pack is asserted to re-derive to its own embedded sections (tests/test_pack.py).
# --------------------------------------------------------------------------- #
_TERMINAL_VERDICTS = {
    "gate_allow_standing": "allow-standing",
    "gate_needs_approval": "needs-approval",
    "gate_denied": "deny",
}


def _payload_obj(row) -> dict:
    if not isinstance(row, dict):
        return {}
    payload = row.get("payload")
    try:
        obj = json.loads(payload) if payload else {}
    except (ValueError, TypeError):
        return {}
    return obj if isinstance(obj, dict) else {}


def _class_key_from_structured(structured) -> str | None:
    if not isinstance(structured, dict):
        return None
    svc = structured.get("service")
    code = structured.get("error_code")
    tot = structured.get("target_object_type")
    if svc and code and tot:
        return f"{svc}|{code}|{tot}"
    return None


def _decision_block(inc_rows) -> dict:
    d: dict = {
        "decision": None, "reason": None, "class_key": None, "risk_class": None,
        "policy_rule_id": None, "ladder_level": None, "plan_hash": None,
        "proposer_principal": None, "approver_principal": None,
        "denied_count": None, "denied_owner_team": None,
    }
    for row in inc_rows:
        et = row.get("event_type")
        p = _payload_obj(row)
        if et in _TERMINAL_VERDICTS:
            d["decision"] = _TERMINAL_VERDICTS[et]
            d["proposer_principal"] = d["proposer_principal"] or row.get("actor")
            d["class_key"] = p.get("class_key") or d["class_key"]
            d["plan_hash"] = p.get("plan_hash") or d["plan_hash"]
            d["reason"] = p.get("reason") or d["reason"]
        elif et == "risk_assessed":
            d["risk_class"] = p.get("risk_class") or d["risk_class"]
            d["policy_rule_id"] = p.get("policy_rule_id") or d["policy_rule_id"]
            d["ladder_level"] = p.get("ladder_level") or d["ladder_level"]
        elif et == "triage":
            d["class_key"] = d["class_key"] or p.get("class_key")
        elif et == "approval_decided":
            if p.get("approver"):
                d["approver_principal"] = p.get("approver")
        elif et == "gate_outcome_recorded":
            d["approver_principal"] = d["approver_principal"] or row.get("actor")
        elif et == "refused":
            d["denied_count"] = p.get("denied_count")
            d["denied_owner_team"] = p.get("denied_owner_team")
    return d


def _outcome_block(inc_rows) -> dict:
    o: dict = {"executed": False, "verified": False, "rolled_back": False,
               "rollback_failed": False, "outcome": None, "rollback": None}
    for row in inc_rows:
        et = row.get("event_type")
        p = _payload_obj(row)
        if et == "executed":
            o["executed"] = True
        elif et == "verified":
            o["verified"] = True
            o["outcome"] = o["outcome"] or "resolved"
        elif et == "rolled_back":
            o["rolled_back"] = True
            o["outcome"] = "rolled_back"
            o["rollback"] = {"kind": "restored_pre_state",
                             "detail": "verification failed — pre-state snapshot restored",
                             "plan_hash": p.get("plan_hash")}
        elif et == "execute_failed":
            o["outcome"] = o["outcome"] or "execute_failed"
        elif et == "gate_outcome_recorded":
            o["outcome"] = p.get("outcome") or o["outcome"]
            o["verified"] = bool(p.get("verified")) or o["verified"]
            o["rolled_back"] = bool(p.get("rolled_back")) or o["rolled_back"]
        elif et == "escalated" and p.get("snapshot_ref"):
            o["rollback_failed"] = True
            o["outcome"] = "rollback_failed"
            o["rollback"] = {"kind": "rollback_failed", "snapshot_ref": p.get("snapshot_ref")}
    return o


def _check_display_bindings(pack, rows, errors) -> None:
    """Re-derive the human-readable sections FROM the chain rows and require them to match the
    embedded sections. Binds the narrative to the tamper-evident chain (item 2)."""
    inc = pack.get("incident")
    if inc is not None and not isinstance(inc, dict):
        errors.append("incident section is malformed (not a JSON object)")
        return
    incident_id = inc.get("incident_id") if isinstance(inc, dict) else None
    structured = inc.get("structured") if isinstance(inc, dict) else None

    dict_rows = [r for r in rows if isinstance(r, dict)]
    inc_rows = [r for r in dict_rows if _payload_obj(r).get("incident_id") == incident_id]

    decision = _decision_block(inc_rows)
    decision["class_key"] = decision.get("class_key") or _class_key_from_structured(structured)
    if pack.get("decision") != decision:
        errors.append(
            "decision display section does not match the chain — the human-readable decision was "
            "altered without a corresponding audit row")

    outcome = _outcome_block(inc_rows)
    verification = {"verified": outcome["verified"], "executed": outcome["executed"],
                    "outcome": outcome["outcome"]}
    if pack.get("verification") != verification:
        errors.append(
            "verification display section does not match the chain — the recorded "
            "verification/outcome was altered without a corresponding audit row")

    if pack.get("rollback") != outcome["rollback"]:
        errors.append(
            "rollback display section does not match the chain — the rollback narrative was "
            "altered without a corresponding audit row")

    transcript = [
        {"seq": r.get("seq"), "ts": r.get("ts"), "actor": r.get("actor"),
         "event_type": r.get("event_type"), "payload": _payload_obj(r)}
        for r in inc_rows
    ]
    if pack.get("execution_transcript") != transcript:
        errors.append(
            "execution_transcript display section does not match the chain rows — the readable "
            "transcript was altered without a corresponding audit row")


def _verify_pack(pack) -> list[str]:
    errors: list[str] = []

    if not isinstance(pack, dict):
        return ["pack is not a JSON object"]

    # ---- (1) manifest over canonical bytes + manifest-metadata template ---- #
    manifest = pack.get("manifest")
    if not isinstance(manifest, dict) or "digest" not in manifest:
        errors.append("missing or malformed manifest")
    else:
        body = {k: v for k, v in pack.items() if k != "manifest"}
        recomputed = _sha256_hex(canonical_json(body))
        if recomputed != manifest.get("digest"):
            errors.append("manifest digest mismatch — the pack bytes were altered")
        # The manifest metadata is NOT covered by the digest above; pin it to the fixed template
        # so an isolated edit to a manifest sub-field cannot verify clean (item 3).
        if manifest.get("algo") != _MANIFEST_ALGO:
            errors.append("manifest metadata altered — 'algo' is not the expected sha256")
        if manifest.get("scope") != _MANIFEST_SCOPE:
            errors.append("manifest metadata altered — 'scope' does not match the expected scope")
        if manifest.get("secret_key") is not None:
            errors.append("manifest metadata altered — 'secret_key' must be null (this pack is "
                          "self-authenticating without a secret key)")
        if manifest.get("self_authenticating") is not True:
            errors.append("manifest metadata altered — 'self_authenticating' must be true")

    # ---- (2) + (3) chain recompute from GENESIS, then anchors ------------- #
    cp = pack.get("chain_proof")
    if not isinstance(cp, dict):
        errors.append("missing or malformed chain_proof")
        return errors  # nothing more to check without the chain

    if cp.get("genesis_hash") != GENESIS_HASH:
        errors.append("chain_proof.genesis_hash is not the canonical genesis link")

    rows = cp.get("rows")
    if not isinstance(rows, list) or not rows:
        errors.append("chain_proof.rows is empty or malformed")
        return errors

    expected_prev = GENESIS_HASH
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"row {i} is malformed")
            break
        if row.get("prev_hash") != expected_prev:
            errors.append(
                f"chain break at row index {i} (seq {row.get('seq')}): prev_hash does not link "
                "to the previous row — a row was reordered, inserted, or removed")
        recomputed = _row_hash(row.get("prev_hash", ""), row.get("ts"), row.get("actor"),
                               row.get("event_type", ""), row.get("payload", ""))
        if recomputed != row.get("hash"):
            errors.append(
                f"row hash mismatch at index {i} (seq {row.get('seq')}): a field of this audit "
                "row was tampered")
        expected_prev = row.get("hash")

    # Anchors — the truncation guard the bare chain cannot provide on its own.
    if cp.get("expected_len") != len(rows):
        errors.append(
            f"length anchor mismatch: expected_len={cp.get('expected_len')} but the pack carries "
            f"{len(rows)} rows — rows were truncated or inserted")
    last = rows[-1] if rows else None
    tail_hash = last.get("hash") if isinstance(last, dict) else GENESIS_HASH
    if cp.get("expected_tail_hash") != tail_hash:
        errors.append(
            "tail-hash anchor mismatch — the most-recent row(s) were truncated, or the anchor was "
            "altered")

    # ---- (4) the incident's rows are actually in the chain ---------------- #
    present = {row.get("seq") for row in rows if isinstance(row, dict)}
    seqs = cp.get("incident_row_seqs")
    if seqs is None:
        seqs = []
    if not isinstance(seqs, list):
        errors.append("chain_proof.incident_row_seqs is malformed (not a list)")
        seqs = []
    for seq in seqs:
        if seq not in present:
            errors.append(f"incident row seq {seq} is missing from the chain proof")

    # ---- (5) derived display sections must re-derive from the chain -------- #
    _check_display_bindings(pack, rows, errors)

    return errors


def verify_pack(pack) -> list[str]:
    """Return a list of human-readable failure reasons. Empty list == verified.

    FAIL-CLOSED: any unexpected structural problem is turned into a clean INVALID verdict rather
    than an exception — this function never raises on malformed input."""
    try:
        return _verify_pack(pack)
    except Exception as exc:  # noqa: BLE001 — fail-closed: malformed structure ⇒ clean reject
        return [f"pack is malformed and could not be verified ({type(exc).__name__})"]


def _incident_id(pack):
    """The incident id if the pack is shaped as expected, else None — never raises."""
    if isinstance(pack, dict):
        inc = pack.get("incident")
        if isinstance(inc, dict):
            return inc.get("incident_id")
    return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="verify_pack.py",
        description="Verify a Precedent Evidence Pack offline (stdlib only, no secret key).")
    parser.add_argument("pack", help="path to a <incident>.pack.json Evidence Pack")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print only the final verdict line and the honesty caveat")
    args = parser.parse_args(argv)

    try:
        with open(args.pack, encoding="utf-8") as fh:
            pack = json.load(fh)
    except (OSError, ValueError) as exc:
        print(f"UNVERIFIED: cannot read pack '{args.pack}': {exc}", file=sys.stderr)
        return 2

    errors = verify_pack(pack)
    incident_id = _incident_id(pack)

    if errors:
        print(f"PACK VERIFICATION FAILED for {incident_id or args.pack}:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PACK VERIFIED: {incident_id or args.pack}")
    if not args.quiet:
        cp = pack.get("chain_proof") or {}
        print(f"  chain: {cp.get('expected_len')} rows recomputed from GENESIS; "
              f"tail {str(cp.get('expected_tail_hash'))[:16]}… matches anchor")
    # The honesty caveat (evidence-support, no-secret-key) prints on EVERY successful run,
    # including -q — the verdict must never read as a bare compliance pass.
    print(f"  {CAVEAT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
