"""Case-file READ / control router for the product console (WP-CONSOLE).

This router is the DATA source the kernel-free ``console/product/`` page consumes over HTTP. It
lives OUTSIDE ``console/product/`` on purpose, so — unlike the page module — it MAY import the
kernel + the pack builder (``precedent``, ``precedent_memory``, ``precedent_pack``, the sim via
the session). The page never imports any of them; it only ``fetch()``es these endpoints.

What it serves, all read-only unless noted:
  * GET  /api/incidents               — the seeded, drivable demo incidents (bodies to propose)
  * GET  /api/case-files              — one summary row per incident (the case-file index)
  * GET  /api/case-file/{id}          — the full display record: build_pack(...) MINUS the manifest,
                                        plus a DERIVED ``safety_net`` block (pre-state snapshot ref
                                        + typed inverse + plan_hash) and the No-LLM flag
  * GET  /api/pack/{id}               — the SEALED pack: the canonical bytes the manifest seals and
                                        ``verify_pack.py`` recomputes (byte-identical download)
  * GET  /api/pack/{id}.html          — render_html(pack): the self-contained air-gapped HTML pack
  * GET  /api/pack/{id}/verify        — run the verify_pack.py logic against the bytes; row-by-row
  * GET  /api/ladder                  — per-class ladder state (level, X-of-3, promoter, ceiling)
  * POST /api/ladder/promote          — eligibility-gated human promotion (audited, names principal)
  * POST /api/ladder/revoke           — instant demotion to L1 (audited, names principal)
  * POST /api/sim/arm-flake           — DEMO fault injection: arm the publisher flake so the next
                                        drive fails verification and auto-rolls-back + demotes live

RULE 2: nothing here calls an LLM. The pack + ladder + verify are deterministic. RULE 3: the
promote path is eligibility-gated and an unregistered principal is a non-action (fail-closed);
the pack builder only REPORTS what the fail-closed pipeline already decided.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel

from console.demo_state import LEVEL_LABELS, STANDING, level_label
from gate.world import DEFAULT_PRINCIPALS
from precedent import ladder
from precedent_pack import build_pack, canonical_json, manifest_digest, render_html

# The seeded demo incidents, in filing order. INC-N maps to sim incident N.
KNOWN_INCIDENTS = ("INC-1", "INC-2", "INC-3")

SessionResolver = Callable[[Request], Any]


class LadderReq(BaseModel):
    class_key: str
    principal: str | None = None


# --------------------------------------------------------------------------- #
# derived display blocks (NEVER written into the sealed pack — display only)
# --------------------------------------------------------------------------- #
def _safety_net(pack: dict) -> dict | None:
    """The Stage-4 'safety net armed BEFORE execution' block, DERIVED from the sealed pack.

    The rollback inverse + pre-state snapshot ref are built by ``orchestrator.prepare()`` BEFORE
    any typed call (proof-link: precedent/orchestrator.py prepare()). We surface them here for
    display WITHOUT touching the sealed pack format:

      * ``pre_state_snapshot_ref`` — recomputed with the SAME formula the orchestrator used
        (``snapshot:{incident_id}:{plan_hash[:12]}``), so it is byte-identical to the real ref;
      * ``inverse`` — the pre-generated typed inverse is ALWAYS ``restore`` back to the captured
        pre-state of the incident's object (service/type/id from the structured extraction);
      * ``plan_hash`` — the hash the inverse was prepared against; it MUST byte-match the plan_hash
        carried on the Stage-5 ``executed`` transcript row (``plan_hash_matches_execution``), a
        mismatch is visible by eye and means the executed plan differed from the prepared one.

    None when the record has no plan (denied/escalated before a plan was built) — a denial is a
    complete, valid record with no safety net to arm.
    """
    dec = pack.get("decision") or {}
    plan_hash = dec.get("plan_hash")
    if not plan_hash:
        return None
    inc = pack.get("incident") or {}
    incident_id = inc.get("incident_id")
    structured = inc.get("structured") or {}
    executed_plan_hash = next(
        (e.get("payload", {}).get("plan_hash")
         for e in (pack.get("execution_transcript") or [])
         if e.get("event_type") == "executed"),
        None,
    )
    return {
        "pre_state_snapshot_ref": f"snapshot:{incident_id}:{plan_hash[:12]}",
        "inverse": {
            "tool": "restore",
            "target": {
                "service": structured.get("service"),
                "object_type": structured.get("target_object_type"),
                "object_id": structured.get("object_id"),
            },
        },
        "plan_hash": plan_hash,
        "executed_plan_hash": executed_plan_hash,
        # None (not executed yet / denied) is neither a match nor a mismatch; only a real
        # executed row that DISAGREES is a tamper signal.
        "plan_hash_matches_execution": (
            None if executed_plan_hash is None else (executed_plan_hash == plan_hash)
        ),
    }


# The gate's decide path is provably zero-LLM for these verdicts (allow-standing = the Standing
# fast path; needs-approval = deferred-rationale slow path; deny = denied before any LLM branch).
# The badge is scoped: "No LLM in THIS decision" — the SMART model may still author non-load-
# bearing rationale prose elsewhere.
_ZERO_LLM_VERDICTS = frozenset({"allow-standing", "needs-approval", "deny"})


def _no_llm_badge_lit(pack: dict) -> bool:
    return (pack.get("decision") or {}).get("decision") in _ZERO_LLM_VERDICTS


def _redact_precedent_for_denial(prov: dict) -> dict:
    """Fail-closed (RULE 3): a DENIED record discloses only count + owning team, NEVER the withheld
    remediation content. ``build_pack``'s provenance loads the policy rule + memorised fix body by
    class_key WITHOUT an access check (it is written for an already-authorised auditor); when the
    console serves a denial to the principal who was just refused, that body would be a side channel
    leak. So we strip the remediation content, keeping only the ACL/freshness lineage METADATA (it
    shows WHY the denial fired — stale/revoked) and fingerprints (hashes, not content)."""
    return {
        "class_key": prov.get("class_key"),
        "lineage_sources": prov.get("lineage_sources") or [],   # metadata only — the "why"
        "policy_rule": None,                                     # action_type names the remediation
        "memorised_records": [                                   # keep existence, drop the body
            {"record_id": r.get("record_id"), "fingerprint": r.get("fingerprint")}
            for r in (prov.get("memorised_records") or [])
        ],
        "redacted": True,
        "note": ("restricted remediation withheld (fail-closed) — disclosing only the owning team "
                 "+ count, never the hidden content"),
    }


def _apply_denial_redaction(pack: dict) -> dict:
    """Return the pack unchanged UNLESS it is a denial, in which case strip the restricted
    provenance content and RE-SEAL the manifest over the redacted bytes, so the served pack still
    verifies offline (byte-identical algorithm) yet carries no withheld remediation."""
    if (pack.get("decision") or {}).get("decision") != "deny":
        return pack
    red = dict(pack)
    red["retrieved_precedent"] = _redact_precedent_for_denial(pack.get("retrieved_precedent") or {})
    body = {k: v for k, v in red.items() if k != "manifest"}
    man = dict(pack.get("manifest") or {})
    man["digest"] = manifest_digest(body)                        # re-seal over the redacted bytes
    red["manifest"] = man
    return red


def _ceiling_for(class_key: str | None) -> str | None:
    """The documented ladder ceiling for a class (from the deterministic policy pack), or None."""
    if not class_key:
        return None
    try:
        from precedent import policy
        return policy.rule_for(class_key).get("ladder_ceiling")
    except Exception:  # noqa: BLE001 — best-effort context, never load-bearing
        return None


# --------------------------------------------------------------------------- #
# router
# --------------------------------------------------------------------------- #
def make_read_router(resolve_session: SessionResolver) -> APIRouter:
    """Build the case-file read/control router. ``resolve_session(request)`` returns the current
    per-cookie session world (the same resolver the gate mount + the rest of console.app use)."""
    router = APIRouter(tags=["console-read"])

    # -- helpers (closures over the resolver) ------------------------------- #
    def _sim_incident(session: Any, incident_id: str) -> dict | None:
        """The full seeded incident body (raw_text + structured) from THIS session's sim, or None.
        Fetched OUTSIDE the memory lock (a different resource)."""
        try:
            n = int(str(incident_id).rsplit("-", 1)[-1])
        except (ValueError, IndexError):
            return None
        sim_tools = getattr(session, "sim_tools", None)
        if sim_tools is None:
            return None
        try:
            return session.sim_tools().incident(n)
        except Exception:  # noqa: BLE001 — sim optional for a bare read; degrade to no structured
            return None

    def _pack_for(session: Any, incident_id: str) -> dict:
        incident = _sim_incident(session, incident_id)
        state = session.state
        with state._lock:
            pack = build_pack(state.conn, incident_id, incident=incident)
        # Fail-closed: a denial served to the refused principal must carry no withheld content.
        return _apply_denial_redaction(pack)

    def _has_record(pack: dict) -> bool:
        return bool(pack.get("execution_transcript")) or bool(
            (pack.get("decision") or {}).get("decision"))

    # -- incidents (drivable seed set) -------------------------------------- #
    @router.get("/api/incidents", summary="The seeded, drivable demo incidents (propose bodies)")
    def list_incidents(request: Request) -> Any:
        session = resolve_session(request)
        out = []
        for iid in KNOWN_INCIDENTS:
            body = _sim_incident(session, iid)
            if body is None:
                out.append({"incident_id": iid, "available": False})
                continue
            out.append({
                "incident_id": body.get("incident_id", iid),
                "raw_text": body.get("raw_text"),
                "source": body.get("source"),
                "observed_at": body.get("observed_at"),
                "structured": body.get("structured"),
                "available": True,
            })
        return {"incidents": out}

    # -- case-file index ---------------------------------------------------- #
    @router.get("/api/case-files", summary="One summary row per incident — the case-file index")
    def list_case_files(request: Request) -> Any:
        session = resolve_session(request)
        rows = []
        for iid in KNOWN_INCIDENTS:
            pack = _pack_for(session, iid)
            dec = pack.get("decision") or {}
            ver = pack.get("verification") or {}
            rows.append({
                "incident_id": iid,
                "source": (pack.get("incident") or {}).get("source"),
                "observed_at": (pack.get("incident") or {}).get("observed_at"),
                "verdict": dec.get("decision"),
                "class_key": dec.get("class_key"),
                "risk_class": dec.get("risk_class"),
                "ladder_level": dec.get("ladder_level"),
                "outcome": ver.get("outcome"),
                "verified": ver.get("verified"),
                "denied_owner_team": dec.get("denied_owner_team"),
                "denied_count": dec.get("denied_count"),
                "has_record": _has_record(pack),
            })
        return {"case_files": rows}

    # -- full display record ------------------------------------------------ #
    @router.get("/api/case-file/{incident_id}",
                summary="Full case-file display record (pack minus manifest + derived safety net)")
    def get_case_file(incident_id: str, request: Request) -> Any:
        from precedent import venice
        session = resolve_session(request)
        pack = _pack_for(session, incident_id)
        record = {k: v for k, v in pack.items() if k != "manifest"}
        # DISPLAY-ONLY augmentations (never part of the sealed, verifiable bytes):
        record["safety_net"] = _safety_net(pack)
        record["no_llm_badge_lit"] = _no_llm_badge_lit(pack)
        record["ladder_ceiling"] = _ceiling_for((pack.get("decision") or {}).get("class_key"))
        record["live_model_calls"] = venice.model_call_count()
        record["has_record"] = _has_record(pack)
        # The manifest DIGEST is echoed (self-authenticating sigil) but the record body itself is
        # the un-sealed view; the sealed bytes live at /api/pack/{id}.
        record["manifest_digest"] = (pack.get("manifest") or {}).get("digest")
        return record

    # -- sealed pack: HTML (register BEFORE the plain {id} route) ------------ #
    @router.get("/api/pack/{incident_id}.html", response_class=HTMLResponse,
                summary="Self-contained HTML pack for an air-gapped auditor laptop")
    def get_pack_html(incident_id: str, request: Request) -> Any:
        session = resolve_session(request)
        pack = _pack_for(session, incident_id)
        safe = "".join(c for c in incident_id if c.isalnum() or c in "-_") or "pack"
        return HTMLResponse(render_html(pack), headers={
            "Content-Disposition": f'attachment; filename="{safe}.pack.html"'})

    # -- sealed pack: offline verifier result ------------------------------- #
    @router.get("/api/pack/{incident_id}/verify",
                summary="Run the verify_pack.py logic against the pack bytes; row-by-row chain")
    def verify_pack_endpoint(incident_id: str, request: Request) -> Any:
        import verify_pack as vp
        session = resolve_session(request)
        pack = _pack_for(session, incident_id)
        errors = vp.verify_pack(pack)
        cp = pack.get("chain_proof") or {}
        rows = cp.get("rows") or []
        inc_seqs = set(cp.get("incident_row_seqs") or [])
        expected_prev = vp.GENESIS_HASH
        row_results = []
        for i, row in enumerate(rows):
            prev_ok = row.get("prev_hash") == expected_prev
            recomputed = vp._row_hash(row.get("prev_hash", ""), row.get("ts"), row.get("actor"),
                                      row.get("event_type", ""), row.get("payload", ""))
            hash_ok = recomputed == row.get("hash")
            row_results.append({
                "index": i, "seq": row.get("seq"), "event_type": row.get("event_type"),
                "actor": row.get("actor"), "prev_ok": prev_ok, "hash_ok": hash_ok,
                "incident_row": row.get("seq") in inc_seqs,
            })
            expected_prev = row.get("hash")
        return {
            "incident_id": incident_id,
            "verified": not errors,
            "errors": errors,
            "expected_len": cp.get("expected_len"),
            "expected_tail_hash": cp.get("expected_tail_hash"),
            "incident_row_seqs": sorted(inc_seqs),
            "rows": row_results,
            "caveat": vp.CAVEAT,
        }

    # -- sealed pack: canonical JSON bytes (register LAST of the pack routes) - #
    @router.get("/api/pack/{incident_id}",
                summary="The SEALED pack — exact canonical bytes the manifest seals")
    def get_pack(incident_id: str, request: Request) -> Any:
        session = resolve_session(request)
        pack = _pack_for(session, incident_id)
        safe = "".join(c for c in incident_id if c.isalnum() or c in "-_") or "pack"
        # Serve the EXACT canonical bytes (sorted keys, compact) — so a downloaded file is
        # byte-identical to what `python verify_pack.py <file>.json` recomputes, and the on-page
        # verifier re-derives the same manifest digest.
        return Response(content=canonical_json(pack), media_type="application/json", headers={
            "Content-Disposition": f'attachment; filename="{safe}.pack.json"'})

    # -- ladder state ------------------------------------------------------- #
    @router.get("/api/ladder", summary="Per-class ladder state (level, X-of-3, promoter, ceiling)")
    def get_ladder(request: Request) -> Any:
        session = resolve_session(request)
        state = session.state
        with state._lock:
            keys = [r["class_key"] for r in state.conn.execute(
                "SELECT class_key FROM class_ladder ORDER BY class_key").fetchall()]
            rungs = []
            for ck in keys:
                row = state.conn.execute(
                    "SELECT level, consecutive_verified, promoted_by, promoted_at "
                    "FROM class_ladder WHERE class_key = ?", (ck,)).fetchone()
                level = row["level"] if row else "L1"
                rungs.append({
                    "class_key": ck,
                    "level": level,                                  # canonical token
                    "level_label": level_label(level),              # display only
                    "consecutive_verified": row["consecutive_verified"] if row else 0,
                    "eligible": ladder.eligible(ck, conn=state.conn),
                    "promoted_by": row["promoted_by"] if row else None,
                    "promoted_at": row["promoted_at"] if row else None,
                    "ladder_ceiling": _ceiling_for(ck),
                    "is_standing": level == STANDING,
                    "eligible_streak": ladder._ELIGIBLE_STREAK,
                })
        return {"ladder": rungs, "standing_token": STANDING,
                "standing_label": LEVEL_LABELS[STANDING]}

    # -- ladder control (audited, names the principal) ---------------------- #
    @router.post("/api/ladder/promote",
                 summary="Human promotion to Standing Approval — eligibility-gated, audited")
    def promote_class(req: LadderReq, request: Request) -> Any:
        session = resolve_session(request)
        principal = req.principal or session.state.principal
        # Fail-closed: an unregistered principal can never promote (out-of-band identity).
        if principal not in DEFAULT_PRINCIPALS:
            return JSONResponse(
                {"ok": False, "class_key": req.class_key, "reason": "unregistered_principal",
                 "detail": "promotion principal is not registered out-of-band"},
                status_code=403)
        state = session.state
        with state._lock:
            # force=False → requires 3 consecutive verified at L2 (a real HUMAN click, never
            # automatic). Not eligible ⇒ ok=false, NO state change (fail-closed).
            result = ladder.promote(req.class_key, principal, conn=state.conn, force=False)
        return result

    @router.post("/api/ladder/revoke",
                 summary="Instant demotion to L1 — always available, audited")
    def revoke_class(req: LadderReq, request: Request) -> Any:
        session = resolve_session(request)
        principal = req.principal or session.state.principal
        if principal not in DEFAULT_PRINCIPALS:
            return JSONResponse(
                {"ok": False, "class_key": req.class_key, "reason": "unregistered_principal",
                 "detail": "revoke principal is not registered out-of-band"},
                status_code=403)
        state = session.state
        with state._lock:
            result = ladder.demote(req.class_key, conn=state.conn, reason="revoked",
                                   actor=principal)
        return {**result, "ok": True, "revoked_by": principal,
                "level_label": level_label(result.get("level", "L1"))}

    # -- demo fault injection (sibling to /api/audit/tamper) ---------------- #
    @router.post("/api/sim/arm-flake",
                 summary="DEMO fault injection: arm the publisher flake so the next drive fails")
    def arm_flake(request: Request) -> Any:
        session = resolve_session(request)
        sim_tools = getattr(session, "sim_tools", None)
        if sim_tools is None:
            return JSONResponse({"ok": False, "detail": "no sim world on this session"},
                                status_code=409)
        try:
            res = session.sim_tools().arm_flake()
        except Exception as e:  # noqa: BLE001
            return JSONResponse({"ok": False, "detail": str(e).splitlines()[0][:200]},
                                status_code=502)
        return {"ok": True, "armed": True, "detail": "publisher flake armed for the next execute",
                "sim": res}

    return router
