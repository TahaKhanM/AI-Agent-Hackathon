"""B12 (reach) — render an incident's hash-chained audit trail as an ITIL-style change record.

Reads the REAL audit_log rows Precedent wrote for one incident and formats them as the change
document a regulated ops team would file — the auditor-grade artifact from BUILD-PLAN §5's reach
tier. Deterministic: no LLM, no network; it only reshapes committed audit rows.

Usage:
  .venv/bin/python scripts/render_change_record.py INC-1 [--db data/precedent.db]
"""
from __future__ import annotations

import argparse
import json

from precedent_memory import db


def _rows(conn, incident_id: str) -> list:
    return conn.execute(
        "SELECT seq, ts, actor, event_type, payload, prev_hash, hash FROM audit_log "
        "WHERE payload LIKE ? ORDER BY seq", (f'%"{incident_id}"%',),
    ).fetchall()


def _by_type(rows) -> dict:
    """Last payload seen per event_type (dict), plus the row itself."""
    out = {}
    for r in rows:
        try:
            pl = json.loads(r["payload"] or "{}")
        except (TypeError, ValueError):
            pl = {}
        out[r["event_type"]] = {"row": r, "payload": pl}
    return out


def render(conn, incident_id: str) -> str:
    rows = _rows(conn, incident_id)
    if not rows:
        return f"# Change record — {incident_id}\n\n_No audit trail found for {incident_id}._\n"
    ev = _by_type(rows)
    tri = ev.get("triage", {}).get("payload", {})
    risk = ev.get("risk_assessed", {}).get("payload", {})
    appr = ev.get("approval_decided", {}).get("payload", {})
    plan_hash = (ev.get("executed", {}).get("payload", {}).get("plan_hash")
                 or ev.get("approval_requested", {}).get("payload", {}).get("plan_hash") or "")
    executed = "executed" in ev
    verified = "verified" in ev
    rolled_back = "rolled_back" in ev
    refused = "refused" in ev
    escalated = "escalated" in ev
    standing = appr.get("decision") == "standing" or ev.get("approval_decided", {}).get(
        "payload", {}).get("decision") == "standing"

    if refused:
        status = "REFUSED — restricted (routed to owning team)"
    elif rolled_back:
        status = "ROLLED BACK — verification failed, pre-state restored"
    elif escalated:
        status = "ESCALATED — no safe automated fix"
    elif verified:
        status = "IMPLEMENTED — verified successful"
    else:
        status = "IN PROGRESS"

    change_id = f"CHG-{plan_hash[:8].upper()}" if plan_hash else f"CHG-{incident_id}"
    first, last = rows[0], rows[-1]
    class_key = tri.get("class_key") or "unclassified"
    approver = appr.get("approver") or ("standing approval (pre-approved standard change)"
                                        if standing else "—")
    decision = appr.get("decision") or ("standing" if standing else "—")

    L = []
    L.append(f"# Change record {change_id}")
    L.append("")
    L.append(f"**Incident:** {incident_id}  ·  **Status:** {status}")
    L.append(f"**Change class:** {class_key}")
    L.append(f"**Requested by:** {first['actor']}  ·  **Opened:** {first['ts']}  ·  "
             f"**Closed:** {last['ts']}")
    L.append("")
    L.append("## 1. Classification (deterministic — no LLM in the decision)")
    L.append(f"- Risk class: **{risk.get('risk_class', '—')}**")
    L.append(f"- Policy rule: `{risk.get('policy_rule_id', '—')}`")
    L.append(f"- Autonomy level: {risk.get('ladder_level', '—')}"
             + ("  (Standing Approval — pre-approved standard change)" if standing else ""))
    L.append("")
    L.append("## 2. Authorisation")
    L.append(f"- Decision: **{decision}**  ·  Approver: **{approver}**")
    if not standing and ev.get("approval_decided"):
        L.append(f"- Recorded at: {ev['approval_decided']['row']['ts']}")
    L.append(f"- Plan hash (tamper anchor): `{plan_hash or '—'}`")
    L.append("")
    L.append("## 3. Implementation & rollback")
    if executed:
        L.append("- Implementation: documented fix executed via typed tool calls "
                 "(no free-form shell).")
        L.append("- Rollback plan: pre-state snapshot captured BEFORE execution; auto-restores on "
                 "any verification failure.")
    elif refused:
        L.append("- Not implemented — the identity is not permitted to read the required "
                 "restricted runbook; routed to the owning team. No restricted content disclosed.")
    else:
        L.append("- Not implemented — routed to a human (escalated).")
    L.append("")
    L.append("## 4. Verification")
    if verified:
        L.append("- Post-state verified healthy. ✅")
    elif rolled_back:
        L.append("- Verification failed → rollback fired → pre-state restored; class demoted. ↩")
    elif refused:
        L.append("- N/A — refused before execution (fail-closed).")
    else:
        L.append("- N/A")
    L.append("")
    L.append("## 5. Audit provenance (hash-chained)")
    L.append(f"- {len(rows)} audit events, seq {first['seq']}–{last['seq']}.")
    L.append(f"- Chain tail hash: `{last['hash']}`")
    L.append(f"- Prev-hash of tail: `{last['prev_hash']}`  (each event = sha256(prev_hash ‖ row)).")
    L.append("")
    L.append("| seq | event | actor |")
    L.append("|---|---|---|")
    for r in rows:
        L.append(f"| {r['seq']} | {r['event_type']} | {r['actor']} |")
    L.append("")
    L.append("_Rendered deterministically from the committed audit_log — no LLM, no network._")
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("incident_id")
    ap.add_argument("--db", default="data/precedent.db")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    conn = db.connect(args.db)
    doc = render(conn, args.incident_id)
    if args.out:
        with open(args.out, "w") as f:
            f.write(doc)
        print(f"wrote {args.out}")
    else:
        print(doc)


if __name__ == "__main__":
    main()
