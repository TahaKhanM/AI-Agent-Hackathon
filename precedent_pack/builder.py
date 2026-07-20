"""Evidence Pack builder + renderer.  [WP-PACK]

Reads the hash-chained audit log (``precedent_memory/audit.py`` rows: ts, actor, event_type,
payload, prev_hash, hash; GENESIS_HASH) plus the memory/lineage tables, and assembles a
per-incident, self-authenticating bundle: a canonical JSON document and a self-contained HTML
rendering (inline CSS, no external refs — it renders on an air-gapped auditor laptop).

Determinism: the canonical form is ``json.dumps(sort_keys, compact, ensure_ascii=False)`` — the
SAME formula the audit chain and ``verify_pack.py`` use, so the manifest digest is reproducible
byte-for-byte on any machine.

RULE 1/2: no model id, no LLM here. RULE 3: this module only reports the fail-closed pipeline's
recorded decisions; it decides nothing.
"""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
from typing import Any

# Mirror precedent_memory.db.GENESIS_HASH / canonical_json WITHOUT importing a decision-path
# module into a place that must also be reproducible by the stdlib-only verifier. The values are
# asserted to agree with the memory layer by tests/test_pack.py.
GENESIS_HASH = "0" * 64
PACK_VERSION = "1"
PACK_KIND = "precedent.evidence_pack.v1"
DISCLAIMER = (
    "This Evidence Pack provides evidence support, not a compliance determination. It is "
    "self-authenticating without a secret key: any isolated tampering breaks the recomputable "
    "hash chain or the sha256 manifest. The strongest assurance comes from checking the "
    "tail-hash anchor against a tail hash re-derived independently from the live audit database."
)

_TEMPLATE_PATH = Path(__file__).with_name("template.html")


def canonical_json(obj: Any) -> str:
    """Deterministic JSON: sorted keys, no whitespace. IDENTICAL to precedent_memory.db and to
    verify_pack.py — the manifest digest depends on this agreeing across all three."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def manifest_digest(pack_without_manifest: dict) -> str:
    """sha256 over the canonical bytes of the pack EXCLUDING its ``manifest`` field."""
    return hashlib.sha256(canonical_json(pack_without_manifest).encode("utf-8")).hexdigest()


def _row_hash(prev_hash: str, ts: str | None, actor: str | None, event_type: str,
              payload_json: str) -> str:
    """Recompute an audit row's hash — byte-identical to precedent_memory.audit._row_hash."""
    material = f"{prev_hash}|{ts or ''}|{actor or ''}|{event_type}|{payload_json}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# low-level reads
# --------------------------------------------------------------------------- #
def _all_rows(conn) -> list[dict]:
    """The FULL ordered audit chain as plain dicts. ``payload`` stays the raw canonical STRING
    exactly as stored, so the recomputed hash reproduces the stored hash bit-for-bit."""
    cur = conn.execute(
        "SELECT seq, ts, actor, event_type, payload, prev_hash, hash "
        "FROM audit_log ORDER BY seq ASC"
    )
    return [
        {"seq": r["seq"], "ts": r["ts"], "actor": r["actor"], "event_type": r["event_type"],
         "payload": r["payload"], "prev_hash": r["prev_hash"], "hash": r["hash"]}
        for r in cur.fetchall()
    ]


def _payload_obj(row: dict) -> dict:
    try:
        obj = json.loads(row["payload"]) if row["payload"] else {}
    except (ValueError, TypeError):
        return {}
    return obj if isinstance(obj, dict) else {}


def _class_key_from_structured(structured: dict | None) -> str | None:
    if not structured:
        return None
    svc = structured.get("service")
    code = structured.get("error_code")
    tot = structured.get("target_object_type")
    if svc and code and tot:
        return f"{svc}|{code}|{tot}"
    return None


# --------------------------------------------------------------------------- #
# provenance
# --------------------------------------------------------------------------- #
def _provenance(conn, class_key: str | None) -> dict:
    """Documented-fix provenance for the incident's class: the policy rule's lineage source refs
    with their live ACL/freshness state, plus any memorised executed-fix record for the class.

    Read-only — NO audit rows are written building a pack (a pack must never mutate the chain)."""
    prov: dict[str, Any] = {"class_key": class_key, "policy_rule": None,
                            "lineage_sources": [], "memorised_records": []}
    if not class_key:
        return prov

    try:
        from precedent import policy
        rule = policy.rule_for(class_key)
        prov["policy_rule"] = {
            "policy_rule_id": rule.get("policy_rule_id"),
            "action_type": rule.get("action_type"),
            "risk_class": rule.get("risk_class"),
            "ladder_ceiling": rule.get("ladder_ceiling"),
            "lineage_refs": list(rule.get("lineage_refs") or []),
        }
        lineage_refs = list(rule.get("lineage_refs") or [])
    except Exception:  # noqa: BLE001 — provenance is best-effort context, never load-bearing
        lineage_refs = []

    for ref in lineage_refs:
        row = conn.execute(
            "SELECT external_ref, constraint_ids, acl_version, last_verified_at, revoked "
            "FROM acl_source WHERE external_ref = ?", (ref,)
        ).fetchone()
        if row is None:
            prov["lineage_sources"].append({"external_ref": ref, "present": False})
            continue
        try:
            cids = json.loads(row["constraint_ids"] or "[]")
        except (ValueError, TypeError):
            cids = []
        prov["lineage_sources"].append({
            "external_ref": row["external_ref"], "present": True,
            "acl_version": row["acl_version"], "last_verified_at": row["last_verified_at"],
            "revoked": bool(row["revoked"]),
            "constraint_count": len(cids), "is_restricted": len(cids) > 0,
        })

    for rec in conn.execute(
        "SELECT id, kind, class_key, fingerprint, body, status FROM memory_record "
        "WHERE class_key = ? AND status = 'active' ORDER BY id", (class_key,)
    ).fetchall():
        try:
            body = json.loads(rec["body"]) if rec["body"] else {}
        except (ValueError, TypeError):
            body = {}
        src_hashes = [
            {"external_ref": lr["external_ref"], "source_content_hash": lr["source_content_hash"]}
            for lr in conn.execute(
                "SELECT s.external_ref AS external_ref, "
                "l.source_content_hash AS source_content_hash "
                "FROM lineage l JOIN acl_source s ON s.id = l.source_id WHERE l.record_id = ?",
                (rec["id"],),
            ).fetchall()
        ]
        prov["memorised_records"].append({
            "record_id": rec["id"], "kind": rec["kind"], "fingerprint": rec["fingerprint"],
            "status": rec["status"], "body": body, "lineage": src_hashes,
        })
    return prov


# --------------------------------------------------------------------------- #
# decision + transcript
# --------------------------------------------------------------------------- #
_TERMINAL_VERDICTS = {
    "gate_allow_standing": "allow-standing",
    "gate_needs_approval": "needs-approval",
    "gate_denied": "deny",
}


def _decision_block(inc_rows: list[dict]) -> dict:
    """Reduce the incident's audit narrative to the decision the gate/orchestrator recorded."""
    d: dict[str, Any] = {
        "decision": None, "reason": None, "class_key": None, "risk_class": None,
        "policy_rule_id": None, "ladder_level": None, "plan_hash": None,
        "proposer_principal": None, "approver_principal": None,
        "denied_count": None, "denied_owner_team": None,
    }
    for row in inc_rows:
        et = row["event_type"]
        p = _payload_obj(row)
        if et in _TERMINAL_VERDICTS:
            d["decision"] = _TERMINAL_VERDICTS[et]
            d["proposer_principal"] = d["proposer_principal"] or row["actor"]
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
            d["approver_principal"] = d["approver_principal"] or row["actor"]
        elif et == "refused":
            d["denied_count"] = p.get("denied_count")
            d["denied_owner_team"] = p.get("denied_owner_team")
    return d


def _outcome_block(inc_rows: list[dict]) -> dict:
    """The verification + rollback outcome the orchestrator recorded for the incident."""
    o: dict[str, Any] = {"executed": False, "verified": False, "rolled_back": False,
                         "rollback_failed": False, "outcome": None, "rollback": None}
    for row in inc_rows:
        et = row["event_type"]
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


# --------------------------------------------------------------------------- #
# build
# --------------------------------------------------------------------------- #
def build_pack(conn, incident_id: str, *, incident: dict | None = None,
               generated_at: str | None = None) -> dict:
    """Assemble the canonical Evidence Pack dict for ONE incident from the audit log + memory.

    The pack embeds the FULL hash chain (chain_proof.rows) so a verifier can recompute from
    GENESIS; ``incident_row_seqs`` marks which rows belong to this incident. The length + tail
    anchors make tail-truncation detectable. A sha256 manifest seals the pack's canonical bytes.
    """
    if not incident_id:
        raise ValueError("build_pack requires a non-empty incident_id")

    rows = _all_rows(conn)
    inc_rows = [r for r in rows if _payload_obj(r).get("incident_id") == incident_id]

    decision = _decision_block(inc_rows)
    outcome = _outcome_block(inc_rows)

    structured = (incident or {}).get("structured") if incident else None
    class_key = decision.get("class_key") or _class_key_from_structured(structured)
    decision["class_key"] = class_key

    transcript = [
        {"seq": r["seq"], "ts": r["ts"], "actor": r["actor"], "event_type": r["event_type"],
         "payload": _payload_obj(r)}
        for r in inc_rows
    ]

    tail_hash = rows[-1]["hash"] if rows else GENESIS_HASH

    pack: dict[str, Any] = {
        "pack_version": PACK_VERSION,
        "kind": PACK_KIND,
        "disclaimer": DISCLAIMER,
        "generated_at": generated_at or _now_iso(),
        "incident": {
            "incident_id": incident_id,
            "source": (incident or {}).get("source"),
            "observed_at": (incident or {}).get("observed_at"),
            "raw_text": (incident or {}).get("raw_text"),
            "structured": structured,
        },
        "decision": decision,
        "policy_pack_version": _policy_pack_version(),
        "retrieved_precedent": _provenance(conn, class_key),
        "execution_transcript": transcript,
        "verification": {
            "verified": outcome["verified"],
            "executed": outcome["executed"],
            "outcome": outcome["outcome"],
        },
        "rollback": outcome["rollback"],
        "chain_proof": {
            "genesis_hash": GENESIS_HASH,
            "hash_construction": "sha256(prev_hash|ts|actor|event_type|payload_json)",
            "expected_len": len(rows),
            "expected_tail_hash": tail_hash,
            "incident_row_seqs": [r["seq"] for r in inc_rows],
            "rows": rows,
        },
    }
    pack["manifest"] = {
        "algo": "sha256",
        "scope": "canonical_json(pack) excluding the 'manifest' field",
        "self_authenticating": True,
        "secret_key": None,
        "digest": manifest_digest(pack),
    }
    return pack


def write_pack(pack: dict, path: str | Path) -> Path:
    """Write the pack as canonical JSON (the exact bytes the manifest seals). Returns the path."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(canonical_json(pack), encoding="utf-8")
    return p


def _now_iso() -> str:
    from datetime import UTC, datetime
    return datetime.now(UTC).isoformat()


def _policy_pack_version() -> Any:
    try:
        from precedent import policy
        return policy.load_pack().get("version")
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------- #
# HTML rendering — self-contained (inline CSS, embedded JSON), offline-verifiable
# --------------------------------------------------------------------------- #
def _esc(v: Any) -> str:
    return html.escape("" if v is None else str(v), quote=True)


def _kv_table(pairs: list[tuple[str, Any]]) -> str:
    body = "".join(
        f"<tr><th>{_esc(k)}</th><td>{_esc(v)}</td></tr>" for k, v in pairs
    )
    return f"<table class='kv'>{body}</table>"


def _transcript_table(transcript: list[dict]) -> str:
    head = ("<tr><th>seq</th><th>ts (UTC)</th><th>actor</th><th>event</th>"
            "<th>detail</th></tr>")
    rows = []
    for e in transcript:
        p = e.get("payload") or {}
        detail = {k: v for k, v in p.items() if k != "incident_id"}
        rows.append(
            f"<tr><td>{_esc(e.get('seq'))}</td><td>{_esc(e.get('ts'))}</td>"
            f"<td>{_esc(e.get('actor'))}</td><td><code>{_esc(e.get('event_type'))}</code></td>"
            f"<td><code>{_esc(canonical_json(detail))}</code></td></tr>"
        )
    return f"<table class='log'>{head}{''.join(rows)}</table>"


def _provenance_html(prov: dict) -> str:
    parts = []
    rule = prov.get("policy_rule")
    if rule:
        parts.append("<h3>Documented policy rule</h3>")
        parts.append(_kv_table([
            ("policy_rule_id", rule.get("policy_rule_id")),
            ("action_type", rule.get("action_type")),
            ("risk_class", rule.get("risk_class")),
            ("ladder_ceiling", rule.get("ladder_ceiling")),
            ("lineage_refs", ", ".join(rule.get("lineage_refs") or []) or "(none)"),
        ]))
    srcs = prov.get("lineage_sources") or []
    if srcs:
        parts.append("<h3>Lineage source ACL / freshness</h3>")
        head = ("<tr><th>source</th><th>present</th><th>acl_version</th>"
                "<th>last_verified_at</th><th>revoked</th><th>restricted</th></tr>")
        body = "".join(
            f"<tr><td><code>{_esc(s.get('external_ref'))}</code></td>"
            f"<td>{_esc(s.get('present'))}</td><td>{_esc(s.get('acl_version'))}</td>"
            f"<td>{_esc(s.get('last_verified_at'))}</td><td>{_esc(s.get('revoked'))}</td>"
            f"<td>{_esc(s.get('is_restricted'))}</td></tr>"
            for s in srcs
        )
        parts.append(f"<table class='log'>{head}{body}</table>")
    recs = prov.get("memorised_records") or []
    if recs:
        parts.append("<h3>Memorised executed-fix records</h3>")
        for r in recs:
            b = r.get("body") or {}
            parts.append(_kv_table([
                ("record_id", r.get("record_id")),
                ("kind", r.get("kind")),
                ("fingerprint", r.get("fingerprint")),
                ("fix", b.get("fix")),
                ("approver", b.get("approver")),
                ("risk_class", b.get("risk_class")),
                ("rollback", b.get("rollback")),
                ("outcome", b.get("outcome")),
            ]))
    return "".join(parts) or "<p class='muted'>No documented precedent was accessible.</p>"


def render_html(pack: dict) -> str:
    """A single self-contained HTML document (inline CSS, no external refs) rendering the pack
    for a human auditor, with the canonical JSON embedded for offline ``verify_pack.py`` use."""
    inc = pack.get("incident") or {}
    dec = pack.get("decision") or {}
    ver = pack.get("verification") or {}
    cp = pack.get("chain_proof") or {}
    man = pack.get("manifest") or {}
    structured = inc.get("structured") or {}

    incident_id = inc.get("incident_id")
    decision_verdict = dec.get("decision") or "(none recorded)"

    content = []
    content.append(f"<h1>Evidence Pack — {_esc(incident_id)}</h1>")
    content.append(f"<p class='disclaimer'>{_esc(pack.get('disclaimer'))}</p>")

    content.append("<section><h2>Incident</h2>")
    content.append(_kv_table([
        ("incident_id", incident_id),
        ("source", inc.get("source")),
        ("observed_at", inc.get("observed_at")),
        ("service", structured.get("service")),
        ("error_code", structured.get("error_code")),
        ("target_object_type", structured.get("target_object_type")),
        ("object_id", structured.get("object_id")),
    ]))
    if inc.get("raw_text"):
        content.append(f"<p class='muted'>Ticket: “{_esc(inc.get('raw_text'))}”</p>")
    content.append("</section>")

    content.append("<section><h2>Gate decision</h2>")
    content.append(_kv_table([
        ("decision", decision_verdict),
        ("reason", dec.get("reason")),
        ("class_key", dec.get("class_key")),
        ("risk_class", dec.get("risk_class")),
        ("policy_rule_id", dec.get("policy_rule_id")),
        ("policy_pack_version", pack.get("policy_pack_version")),
        ("ladder_level", dec.get("ladder_level")),
        ("plan_hash", dec.get("plan_hash")),
        ("proposer_principal", dec.get("proposer_principal")),
        ("approver_principal", dec.get("approver_principal")),
        ("denied_count", dec.get("denied_count")),
        ("denied_owner_team", dec.get("denied_owner_team")),
    ]))
    content.append("</section>")

    content.append("<section><h2>Retrieved precedent &amp; provenance</h2>")
    content.append(_provenance_html(pack.get("retrieved_precedent") or {}))
    content.append("</section>")

    content.append("<section><h2>Execution transcript</h2>")
    content.append(_transcript_table(pack.get("execution_transcript") or []))
    content.append("</section>")

    content.append("<section><h2>Verification &amp; rollback</h2>")
    content.append(_kv_table([
        ("executed", ver.get("executed")),
        ("verified", ver.get("verified")),
        ("outcome", ver.get("outcome")),
        ("rollback", canonical_json(pack.get("rollback")) if pack.get("rollback") else "none"),
    ]))
    content.append("</section>")

    content.append("<section><h2>Chain proof</h2>")
    content.append(_kv_table([
        ("genesis_hash", cp.get("genesis_hash")),
        ("hash_construction", cp.get("hash_construction")),
        ("expected_len", cp.get("expected_len")),
        ("expected_tail_hash", cp.get("expected_tail_hash")),
        ("incident_row_seqs", ", ".join(str(s) for s in (cp.get("incident_row_seqs") or []))),
        ("manifest.algo", man.get("algo")),
        ("manifest.digest", man.get("digest")),
    ]))
    content.append(
        "<p class='muted'>To verify offline: extract the JSON below to a file and run "
        "<code>python verify_pack.py &lt;file&gt;.json</code>. Any altered byte, reordered or "
        "dropped row, or wrong anchor fails verification with a non-zero exit.</p>")
    content.append("</section>")

    content.append("<section><h2>Canonical pack (verifiable bytes)</h2>")
    content.append(
        f"<pre id='pack-json'>{_esc(canonical_json(pack))}</pre>")
    content.append("</section>")

    body = "\n".join(content)
    template = _TEMPLATE_PATH.read_text(encoding="utf-8")
    return (template
            .replace("<!--TITLE-->", _esc(f"Evidence Pack — {incident_id}"))
            .replace("<!--CONTENT-->", body))


# --------------------------------------------------------------------------- #
# demo pack generation — seed a world, drive the 3 incidents, write packs
# --------------------------------------------------------------------------- #
def generate_demo_packs(outdir: str | Path) -> list[dict]:
    """Seed a fresh world (seed 4207), drive the three demo incidents THROUGH the real gate, and
    write a JSON + HTML pack for each. Returns a list of {incident_id, json, html} path dicts.

    Local imports so this test/ops convenience never pulls the console/gate surface into a plain
    ``import precedent_pack``. Airplane-mode: the world runs an in-process sim TestClient.
    """
    import tempfile

    from console.demo_state import SCHED_CLASS_STANDING
    from gate import service
    from gate.models import OutcomeRequest, ProposeRequest, StructuredExtraction
    from gate.world import build_seeded_world

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="precedent-pack-demo-"))
    world = build_seeded_world(work, standing_classes=(SCHED_CLASS_STANDING,))

    written: list[dict] = []
    try:
        incidents = {n: world.tools.incident(n) for n in (1, 2, 3)}

        def _propose(n: int) -> Any:
            inc = incidents[n]
            return service.propose(world, ProposeRequest(
                incident_id=inc["incident_id"], principal="scheduling-ops",
                raw_text=inc["raw_text"], source="sim", observed_at=inc["observed_at"],
                structured=StructuredExtraction(**inc["structured"])))

        # INC-1: slow path — propose (needs-approval), approve as a DISTINCT principal (four-eyes).
        r1 = _propose(1)
        if r1.ref:
            service.report_outcome(world, OutcomeRequest(
                ref=r1.ref, decision="approve", approver_principal="ops-lead"))
        # INC-2: Standing Approval fast path — propose (allow-standing), outcome (no human).
        r2 = _propose(2)
        if r2.ref:
            service.report_outcome(world, OutcomeRequest(ref=r2.ref))
        # INC-3: ACL-restricted — proposal is denied (fail-closed). A denial is still evidence.
        _propose(3)

        for n in (1, 2, 3):
            inc = incidents[n]
            pack = build_pack(world.conn, inc["incident_id"], incident=inc)
            jpath = write_pack(pack, outdir / f"{inc['incident_id']}.pack.json")
            hpath = outdir / f"{inc['incident_id']}.pack.html"
            hpath.write_text(render_html(pack), encoding="utf-8")
            written.append({"incident_id": inc["incident_id"], "json": str(jpath),
                            "html": str(hpath)})
    finally:
        world.close()
    return written
