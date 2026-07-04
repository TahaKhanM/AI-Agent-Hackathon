"""Inference-prevention bench (P1.9) — ADDITIONAL to the frozen 10-metric conformance bench.

Deterministically exercises the two query-time inference-prevention mechanisms and emits a
labelled section + a JSON artifact. It is INTENTIONALLY separate from conformance_bench so the
committed 10-metric results.json stays byte-identical; this only ADDS a new, clearly-labelled
measurement. Zero-LLM (deterministic set algebra + a windowed audit count).

Run:  .venv/bin/python -m precedent_memory.bench.inference_prevention
"""
from __future__ import annotations

import json
from pathlib import Path

from precedent_memory import audit, db, store
from precedent_memory import probing_detection as pd

_ARTIFACT = Path(__file__).parent / "inference_prevention.json"


def _seed(conn) -> dict:
    rights = store.ensure_constraint(conn, "jira", "issue-security:rights", "Rights Ops")
    sched = store.ensure_constraint(conn, "jira", "issue-security:scheduling", "Scheduling Ops")
    store.put_principal(conn, "prober", [])
    store.put_principal(conn, "both", [rights, sched])
    store.put_source(conn, "kb:KB-0001", [])
    store.put_source(conn, "kb:KB-0004", [rights])
    store.put_source(conn, "jira:MEDIA-113", [sched])
    return {"rights": rights, "sched": sched}


def _rec(conn, fp, lineage):
    return store.store({"kind": "executed_fix", "fingerprint": fp, "class_key": fp,
                        "body": {"fix": "x"}}, lineage, conn=conn)


def run(*, sweep: int = 8, threshold: int = 5) -> dict:
    """Run the two mechanisms over a synthetic scenario; return the measured result dict."""
    conn = db.connect(":memory:")
    try:
        _seed(conn)

        # (a) probing sweep: `sweep` denials from one principal in the window -> flagged + audited.
        for i in range(sweep):
            audit.audit("retrieval_denied", conn=conn, actor="prober", record_id=i, reason="probe")
        conn.commit()
        probe = pd.detect_probing(conn, "prober", threshold=threshold)
        probe_audited = conn.execute(
            "SELECT COUNT(*) c FROM audit_log WHERE event_type='probing_detected'"
        ).fetchone()["c"]

        # (b) cross-boundary co-occurrence: a disjoint bundle is denied; a same-boundary allowed.
        rid_r = _rec(conn, "fp-r", ["kb:KB-0004"])         # RIGHTS only
        rid_s = _rec(conn, "fp-s", ["jira:MEDIA-113"])     # SCHED only
        rid_s2 = _rec(conn, "fp-s2", ["jira:MEDIA-113"])   # SCHED only
        rid_pub = _rec(conn, "fp-pub", ["kb:KB-0001"])     # public
        cross_denied = pd.assess_bundle(conn, "both", [rid_r, rid_s])
        same_allowed = pd.assess_bundle(conn, "both", [rid_s, rid_s2])
        public_allowed = pd.assess_bundle(conn, "both", [rid_pub, rid_r])
        bundle_audited = conn.execute(
            "SELECT COUNT(*) c FROM audit_log WHERE event_type='bundle_cross_boundary_denied'"
        ).fetchone()["c"]

        return {
            "probing_detection": {
                "sweep_denials": sweep, "threshold": threshold,
                "flagged": probe["flagged"], "throttled": probe["throttle"],
                "audited": probe_audited,
            },
            "cross_boundary": {
                "disjoint_bundle_denied": not cross_denied["allowed"],
                "same_boundary_allowed": same_allowed["allowed"],
                "public_mix_allowed": public_allowed["allowed"],
                "denials_audited": bundle_audited,
            },
        }
    finally:
        conn.close()


def section_md(res: dict) -> str:
    p = res["probing_detection"]
    c = res["cross_boundary"]
    passed = (p["flagged"] and p["throttled"] and p["audited"] == 1
              and c["disjoint_bundle_denied"] and c["same_boundary_allowed"]
              and c["public_mix_allowed"] and c["denials_audited"] == 1)
    lines = [
        "## Additional (P1.9) — query-time inference prevention (deterministic, zero-LLM)",
        "",
        "Complements the frozen 10-metric bench (results.json unchanged). Two mechanisms:",
        "",
        "| Mechanism | Result |",
        "|---|---|",
        f"| Denial-burst / probing detection ({p['sweep_denials']} denials, threshold "
        f"{p['threshold']}) | **flagged + throttled + audited** "
        f"({'✅' if p['flagged'] else '✗'}) |",
        "| Cross-boundary bundle (disjoint restricted boundaries) | "
        f"**denied + audited** ({'✅' if c['disjoint_bundle_denied'] else '✗'}) |",
        "| Same-boundary bundle | allowed "
        f"({'✅' if c['same_boundary_allowed'] else '✗'}) |",
        "| Public record co-occurrence | allowed "
        f"({'✅' if c['public_mix_allowed'] else '✗'}) |",
        "",
        f"Overall: **{'PASS' if passed else 'FAIL'}**. Both fail toward non-action "
        "(flag/deny), never disclosure; every decision is written to the hash-chained audit log. "
        "`precedent_memory/retrieve.py` stays LLM-import-free.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    res = run()
    _ARTIFACT.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n")
    print(section_md(res))
    print(f"[inference-bench] wrote {_ARTIFACT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
