"""Demo console — server-rendered page + JSON polling, NO frontend framework. [owner T2, task T2-3]

Spec: Idea/refinement/02 §4 + 04-demo-and-video-script.md §1.2.

The console is a VIEW/CONTROL surface only. Every access decision is delegated to
precedent_memory (see console/demo_state.py). Terminology: the top ladder level is
"Standing Approval", never "Autonomous". The Revoke control is always visible on a
Standing-Approval class. The console runs end-to-end on the seeded local-demo
scenario even when the T1 loop is not wired; T1 streams its own steps via POST
/api/trace.
"""
from __future__ import annotations

import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from console import showcase
from console.demo_state import STATE

app = FastAPI(title="Precedent Console")

_STATIC_DIR = Path(__file__).parent / "static"
if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


# --------------------------------------------------------------------------- #
# Request bodies
# --------------------------------------------------------------------------- #
class TriageReq(BaseModel):
    incident_id: str


class ApproveReq(BaseModel):
    incident_id: str
    principal: str | None = None


class LadderReq(BaseModel):
    class_key: str
    principal: str | None = None


class FlipReq(BaseModel):
    on: bool | None = None


class TraceReq(BaseModel):
    step: str
    detail: str = ""
    incident_id: str | None = None


# --------------------------------------------------------------------------- #
# JSON API
# --------------------------------------------------------------------------- #
@app.get("/health")
def health():
    snap = STATE.snapshot()
    return {"status": "ok", **snap["status"], "precedents": snap["precedents_count"]}


@app.get("/api/state")
def api_state():
    return STATE.snapshot()


@app.get("/api/events")
def api_events():
    return STATE.events()


@app.post("/api/triage")
def api_triage(req: TriageReq):
    t0 = time.perf_counter_ns()
    try:
        return STATE.triage(req.incident_id)
    finally:
        # Rolling P99 for the BasedAI proof strip. VIEW-ONLY measurement — does
        # not participate in the risk / permission decision.
        showcase.record_latency_ns(time.perf_counter_ns() - t0)


# --------------------------------------------------------------------------- #
# Showcase read-only endpoints (VIEW surface only — no logic branches into these)
# --------------------------------------------------------------------------- #
@app.get("/api/copy")
def api_copy():
    """Static prose bundle for the guided tour + strips. Never fetches at runtime."""
    return showcase.copy_bundle()


@app.get("/api/latency")
def api_latency():
    """Rolling P50/P99 of REAL permission-check calls. Measurement-only.

    If the ring is empty (first call after boot), run a small benchmark of the
    live check_access path to seed it — this way the sparkline is populated
    even before any incident is driven.
    """
    snap = showcase.latency_snapshot()
    if snap["samples"] == 0:
        showcase._bench_permission_check(n=200)
        snap = showcase.latency_snapshot()
    snap["kernel_hash"] = showcase.KERNEL_HASH
    return snap


@app.get("/api/kernel-hash")
def api_kernel_hash():
    """Deterministic-surface fingerprint. Compared against MANIFEST.json for
    external attestation — a hash pinned in a committed file the running process
    cannot forge.
    """
    expected = showcase.manifest_expected_hash()
    return {
        "kernel_hash": showcase.KERNEL_HASH,
        "manifest_expected": expected,
        "matches_manifest": (expected is not None and expected == showcase.KERNEL_HASH),
        "manifest_present": expected is not None,
    }


@app.get("/api/model-calls")
def api_model_calls():
    """Honest counter of REAL network calls to the open-weight model endpoint this
    session (never cache hits). The demo header renders this as "Model calls this
    session: N" — the zero-LLM fast path keeps it at 0, so the number IS the proof.
    """
    from precedent import venice
    return {"model_calls": venice.model_call_count()}


# The real-tamper affordance keeps the ORIGINAL payload of every row it corrupts so
# Restore is a true round-trip. Session-scoped in spirit (single-writer STATE.conn);
# a tampered byte makes the REAL /api/audit/verify fail at that row — no fake pill.
_TAMPER_BACKUP: dict[int, str] = {}


def _tamper_one(payload: str | None) -> str:
    """Return a payload string guaranteed to differ from the input by one byte, so the
    stored row hash no longer matches its recomputed value."""
    p = payload or "{}"
    last = p[-1]
    return p[:-1] + ("0" if last != "0" else "1")


@app.post("/api/audit/tamper")
def api_audit_tamper(seq: int | None = None):
    """REAL tamper: flip one byte in one audit row's payload (default: the newest row,
    or the caller's chosen seq). The row's stored hash is left untouched, so the REAL
    verifier below fails at exactly this row. Restore is a true round-trip. This
    replaces the old cosmetic "Tamper (visual)" button — nothing is faked."""
    from precedent_memory import audit
    with STATE._lock:
        if seq is None:
            row = STATE.conn.execute(
                "SELECT seq FROM audit_log ORDER BY seq DESC LIMIT 1").fetchone()
            if row is None:
                return {"ok": False, "detail": "audit log is empty"}
            seq = row["seq"]
        row = STATE.conn.execute(
            "SELECT payload FROM audit_log WHERE seq = ?", (seq,)).fetchone()
        if row is None:
            return {"ok": False, "detail": f"no audit row #{seq}"}
        _TAMPER_BACKUP.setdefault(seq, row["payload"] or "{}")
        STATE.conn.execute("UPDATE audit_log SET payload = ? WHERE seq = ?",
                            (_tamper_one(row["payload"]), seq))
        STATE.conn.commit()
        verified = audit.verify_chain(conn=STATE.conn)
    return {"ok": True, "tampered_seq": seq, "verified": verified,
            "detail": f"flipped one byte of audit row #{seq}"}


@app.post("/api/audit/restore")
def api_audit_restore():
    """Undo every real tamper: rewrite each corrupted row's original payload, so the
    REAL verifier passes again. Deterministic, no re-hashing tricks."""
    from precedent_memory import audit
    with STATE._lock:
        for seq, original in list(_TAMPER_BACKUP.items()):
            STATE.conn.execute("UPDATE audit_log SET payload = ? WHERE seq = ?",
                               (original, seq))
        STATE.conn.commit()
        _TAMPER_BACKUP.clear()
        verified = audit.verify_chain(conn=STATE.conn)
    return {"ok": True, "verified": verified}


@app.get("/api/audit/verify")
def api_audit_verify():
    """REAL hash-chain verification over on-disk audit rows. Read-only. This is
    the endpoint the audit-chain proof reflects.
    """
    from precedent_memory import audit
    with STATE._lock:
        try:
            ok = audit.verify_chain(conn=STATE.conn)
            length = STATE.conn.execute(
                "SELECT COUNT(*) FROM audit_log").fetchone()[0]
            tail = STATE.conn.execute(
                "SELECT hash FROM audit_log ORDER BY seq DESC LIMIT 1").fetchone()
            return {
                "verified": bool(ok),
                "rows": length,
                "tail_hash": (tail[0][:16] + "…") if tail else None,
            }
        except Exception as e:
            return {"verified": False, "rows": 0, "tail_hash": None,
                    "error": str(e).splitlines()[0][:200]}


@app.post("/api/probes/run")
def api_probes_run(n: int = 100):
    """Fire n adversarial permission-check probes against the live memory db.
    Read-only. Returns leak count (should be zero) + P50/P99 latency.
    """
    return showcase.run_adversarial_probes(n=n)


@app.post("/api/approve")
def api_approve(req: ApproveReq):
    return STATE.approve(req.incident_id, req.principal)


@app.post("/api/promote")
def api_promote(req: LadderReq):
    return STATE.promote(req.class_key, req.principal)


@app.post("/api/revoke")
def api_revoke(req: LadderReq):
    return STATE.revoke(req.class_key, req.principal)


@app.post("/api/permission-flip")
def api_permission_flip(req: FlipReq):
    return STATE.permission_flip(req.on)


@app.post("/api/trace")
def api_trace(req: TraceReq):
    """T1 integration seam: the execution loop pushes DETECT/EXECUTE/VERIFY steps."""
    return STATE.push_trace(req.model_dump())


@app.post("/api/demo/reset")
def api_reset():
    from precedent import venice
    _TAMPER_BACKUP.clear()
    venice.reset_model_calls()
    return STATE.reset()


@app.get("/api/change-record/{incident_id}", response_class=PlainTextResponse)
def api_change_record(incident_id: str):
    """P1.7: one-click export of an incident's ITIL change record, rendered deterministically
    from the REAL hash-chained audit rows (no LLM, no network). Downloads as markdown."""
    from scripts.render_change_record import render
    with STATE._lock:
        doc = render(STATE.conn, incident_id)
    safe = "".join(c for c in incident_id if c.isalnum() or c in "-_") or "record"
    return PlainTextResponse(doc, media_type="text/markdown", headers={
        "Content-Disposition": f'attachment; filename="change-record-{safe}.md"'})


# --------------------------------------------------------------------------- #
# The page — "The Approver's Seat" (v2 demo). Server-rendered shell + a self-paced,
# chaptered narrative that drives the REAL kernel at every beat. No frontend
# framework, no inline handlers (one delegated listener off data-* attributes).
# --------------------------------------------------------------------------- #
@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(_PAGE)









_PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Precedent — The Approver's Seat</title>
<style>
 :root{
   --paper:#F1F1E2; --paper-2:#F7F6EC; --card:#FBFAF2;
   --ink:#2A2A48; --indigo:#3C3B62; --indigo-lo:#56547e; --indigo-hi:#6f6d97;
   --line:#D8D5C2; --line-2:#E6E3D2; --muted:#6E6C82;
   --oxblood:#8C3A49; --oxblood-bg:#F3E5E7; --oxblood-line:#E1C3C8;
   --gold:#A9853B;
   --serif:"Hoefler Text","Iowan Old Style","Palatino Linotype","Book Antiqua",Palatino,Georgia,"Times New Roman",serif;
   --sans:ui-sans-serif,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",sans-serif;
   --mono:ui-monospace,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
 }
 *{box-sizing:border-box}
 html{scroll-behavior:smooth}
 body{margin:0;background:var(--paper);color:var(--ink);
   font:16px/1.62 var(--serif);-webkit-font-smoothing:antialiased;position:relative;min-height:100vh}
 /* paper grain */
 body::before{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.55;
   background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E")}
 .wrap{position:relative;z-index:1}
 h1,h2,h3{font-weight:600;letter-spacing:.2px}
 em{font-style:italic}
 .mono{font-family:var(--mono)}
 .sc{font-family:var(--sans);text-transform:uppercase;letter-spacing:2.4px;font-weight:600}
 /* ---------- header ---------- */
 header{display:flex;align-items:center;gap:15px;flex-wrap:wrap;
   padding:13px 30px;background:linear-gradient(#FCFBF3,#F7F5EA);
   border-bottom:1px solid var(--line)}
 header .mark{width:42px;height:42px;flex:0 0 42px;display:block}
 header .mark img{width:100%;height:100%;object-fit:contain;display:block}
 .wm{display:flex;flex-direction:column;line-height:1.1}
 .wm .name{font:600 21px/1 var(--serif);letter-spacing:4px;color:var(--ink)}
 .wm .tag{font-size:11px;color:var(--muted);font-style:italic;margin-top:3px;letter-spacing:.2px}
 .chips{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
 .chip{font-family:var(--sans);font-size:11px;letter-spacing:.3px;padding:5px 11px;border-radius:2px;
   background:var(--paper-2);color:var(--indigo);border:1px solid var(--line);white-space:nowrap}
 .chip b{font-family:var(--mono);font-weight:600}
 .chip.ok{border-color:#CFCBB6;background:#F0EEE0}
 .chip .ck{color:var(--gold)}
 .rule{height:2px;background:linear-gradient(90deg,transparent,var(--gold) 12%,var(--gold) 88%,transparent);opacity:.5}
 /* ---------- layout ---------- */
 main{max-width:1200px;margin:0 auto;padding:26px 30px 130px;
   display:grid;grid-template-columns:1.6fr .95fr;gap:26px;align-items:start}
 main.intro{grid-template-columns:1fr;max-width:860px}
 main.intro .rail{display:none}
 @media(max-width:920px){main,main.intro{grid-template-columns:1fr;max-width:720px}}
 .stage{background:var(--card);border:1px solid var(--line);border-radius:5px;
   padding:30px 34px;box-shadow:0 1px 0 #fff inset,0 6px 22px -14px rgba(42,42,72,.4);position:relative}
 .stage::after{content:"";position:absolute;left:0;right:0;top:0;height:3px;
   background:linear-gradient(90deg,var(--indigo),var(--indigo-lo));border-radius:5px 5px 0 0}
 main.intro .stage{text-align:center;padding:44px 46px 40px}
 .kicker{font-family:var(--sans);font-size:11px;letter-spacing:3px;text-transform:uppercase;
   color:var(--indigo);font-weight:700;margin-bottom:12px}
 .stage h2{font-size:32px;line-height:1.14;margin:0 0 16px;color:var(--ink)}
 main.intro .stage h2{font-size:38px;margin-top:8px}
 .lede{font-size:17px;line-height:1.62;color:#3a3952;margin:0 0 18px;max-width:62ch}
 main.intro .lede{margin:0 auto 22px;font-size:17.5px}
 .lede b{color:var(--ink);font-weight:600}
 .gloss{border-bottom:1px dotted var(--indigo-lo);cursor:help}
 .point{font-family:var(--sans);font-size:13px;line-height:1.5;color:var(--indigo);
   border-left:2px solid var(--gold);background:#F4F2E6;padding:9px 14px;border-radius:0 3px 3px 0;
   margin:2px 0 20px;max-width:64ch}
 main.intro .point{max-width:none;text-align:left;display:inline-block}
 .point b{color:var(--ink)}
 .act{margin-top:6px}
 /* staggered reveal */
 .rv{opacity:0;transform:translateY(9px);animation:rise .55s cubic-bezier(.2,.6,.2,1) forwards}
 .rv:nth-child(1){animation-delay:.02s}.rv:nth-child(2){animation-delay:.09s}
 .rv:nth-child(3){animation-delay:.16s}.rv:nth-child(4){animation-delay:.23s}
 .rv:nth-child(5){animation-delay:.30s}.rv:nth-child(6){animation-delay:.37s}
 @keyframes rise{to{opacity:1;transform:none}}
 /* ---------- buttons & inputs ---------- */
 button{font-family:var(--sans);font-size:13px;font-weight:600;letter-spacing:.3px;
   padding:10px 18px;border-radius:3px;cursor:pointer;border:1px solid var(--indigo);
   background:var(--indigo);color:#F4F3EA;margin:6px 7px 0 0;transition:background .15s,transform .05s}
 button:hover{background:var(--indigo-lo)}
 button:active{transform:translateY(1px)}
 button.ghost{background:transparent;color:var(--indigo);border-color:#BFBCA6}
 button.ghost:hover{background:#EEECDD}
 button.warn{background:var(--oxblood);border-color:var(--oxblood)}
 button.warn:hover{filter:brightness(1.07)}
 button.ghost.warn{background:transparent;color:var(--oxblood);border-color:var(--oxblood-line)}
 button.ghost.warn:hover{background:var(--oxblood-bg)}
 button:disabled{opacity:.4;cursor:not-allowed;transform:none}
 input[type=text]{font:16px var(--serif);padding:11px 14px;border:1px solid #BFBCA6;border-radius:3px;
   background:#FCFCF6;color:var(--ink);width:min(380px,100%)}
 input[type=text]:focus{outline:none;border-color:var(--indigo);box-shadow:0 0 0 3px rgba(60,59,98,.12)}
 .field-note{font-size:13px;color:var(--muted);margin-top:9px;max-width:56ch;font-style:italic}
 main.intro .field-note{margin-left:auto;margin-right:auto}
 .chipbar{display:flex;gap:8px;flex-wrap:wrap;margin:4px 0 12px}
 .try{font-family:var(--sans);font-size:12.5px;padding:7px 12px;border-radius:16px;background:#FCFBF3;
   border:1px solid #CFCBB6;color:var(--indigo);cursor:pointer}
 .try:hover{background:#EEECDD}
 /* ---------- gate / document card ---------- */
 .doc{border:1px solid var(--line);border-radius:4px;background:#FCFCF5;padding:18px;margin-top:8px;
   box-shadow:0 6px 20px -16px rgba(42,42,72,.5)}
 .doc .dh{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;
   border-bottom:1px solid var(--line-2);padding-bottom:10px;margin-bottom:12px}
 .doc .dh b{font-size:16px}
 .stamp-tag{font-family:var(--sans);font-size:10.5px;letter-spacing:.4px;padding:4px 10px;border-radius:2px;
   background:var(--paper-2);color:var(--indigo);border:1px solid var(--line);white-space:nowrap}
 .stamp-tag.noll{border-style:dashed}
 .diff{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:6px 0 4px}
 @media(max-width:640px){.diff{grid-template-columns:1fr}}
 .diff .dl{font-family:var(--sans);font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--muted);
   display:block;margin-bottom:5px}
 .diff .sub{font-style:italic;text-transform:none;letter-spacing:0;color:var(--muted);font-family:var(--serif);font-size:11.5px}
 pre{background:#F4F2E4;border:1px solid var(--line-2);border-radius:4px;padding:10px 11px;
   font:11.5px/1.55 var(--mono);white-space:pre-wrap;word-break:break-word;max-height:172px;overflow:auto;
   margin:0;color:#3a3a52}
 code{background:#EEECDC;padding:2px 6px;border-radius:3px;font:11.5px var(--mono);color:var(--indigo);word-break:break-all}
 .anchor{font-size:13.5px;color:var(--indigo);margin-top:10px;display:flex;gap:8px;align-items:baseline}
 .anchor .k{font-family:var(--sans);font-size:10px;letter-spacing:.6px;text-transform:uppercase;color:var(--muted);flex:0 0 auto}
 /* ---------- callouts ---------- */
 .callout{border-radius:4px;padding:14px 16px;margin-top:16px;font-size:15px;line-height:1.55;
   border:1px solid var(--line);background:#FCFCF5;animation:rise .35s ease}
 .callout.good{border-color:#CFCBB6;background:#F1EFE0;color:var(--indigo)}
 .callout.bad{border-color:var(--oxblood-line);background:var(--oxblood-bg);color:var(--oxblood)}
 .callout.sealed{border-color:#D8D3BE;background:#F2F0E1;color:var(--ink);display:flex;align-items:center;gap:16px}
 .callout.sealed .seal-text{flex:1;min-width:0}
 .callout .stampwrap{flex:0 0 56px;width:56px;height:56px;animation:stampin .5s cubic-bezier(.2,1.5,.4,1)}
 .callout .stampwrap img{width:100%;height:100%;object-fit:contain;display:block}
 @keyframes stampin{0%{transform:scale(2.3) rotate(-16deg);opacity:0}55%{transform:scale(.92) rotate(2deg)}100%{transform:scale(1) rotate(0);opacity:1}}
 .metric{font-family:var(--mono);font-weight:600}
 .counter{font-family:var(--sans);font-size:12.5px;color:var(--muted);margin-top:10px}
 /* ---------- rail ---------- */
 .rail{display:flex;flex-direction:column;gap:18px;position:sticky;top:20px}
 @media(max-width:920px){.rail{position:static}}
 .panel{background:var(--card);border:1px solid var(--line);border-radius:5px;padding:15px 17px;
   box-shadow:0 4px 16px -14px rgba(42,42,72,.5)}
 .panel h3{font-family:var(--sans);font-size:10.5px;letter-spacing:1.8px;text-transform:uppercase;color:var(--indigo);
   font-weight:700;margin:0 0 12px;display:flex;justify-content:space-between;align-items:center;
   border-bottom:1px solid var(--line-2);padding-bottom:9px}
 .world .inc{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:9px 0;border-bottom:1px solid var(--line-2)}
 .world .inc:last-child{border-bottom:none}
 .world .inc .nm{font-size:14px;font-weight:600}
 .world .inc .sv{font-family:var(--sans);font-size:10.5px;color:var(--muted);letter-spacing:.2px}
 .badge{font-family:var(--sans);font-size:10px;letter-spacing:.3px;padding:3px 8px;border-radius:2px;
   background:var(--paper-2);color:var(--indigo);border:1px solid var(--line);white-space:nowrap}
 .badge.ok{background:#EDEBDC;border-color:#CFCBB6}
 .badge.deny{background:var(--oxblood-bg);border-color:var(--oxblood-line);color:var(--oxblood)}
 .badge.standing{background:#ECE8F5;border-color:#D3CCE8;color:#54428f}
 .badge.broke{color:var(--oxblood)}
 .flag{animation:none}
 .flag.alert{color:var(--oxblood);animation:flick 1.6s steps(1) infinite}
 @keyframes flick{0%,92%,100%{opacity:1}94%{opacity:.35}96%{opacity:1}98%{opacity:.5}}
 .ledger{max-height:270px;overflow:auto;font:12px/1.5 var(--mono)}
 .ledger .row{padding:6px 7px;border-bottom:1px solid var(--line-2);display:flex;gap:8px;align-items:baseline}
 .ledger .row .sq{color:var(--muted);flex:0 0 auto}
 .ledger .row .ev{color:var(--ink);font-weight:600}
 .ledger .row .who{color:var(--muted);margin-left:auto;font-size:11px}
 .ledger .row.pick{cursor:pointer}
 .ledger .row.pick:hover{background:#EFEDDE}
 .ledger .row.sel{background:#ECEAF0;outline:1px solid #D3CCE8}
 .ledger .row.shake{animation:shake .5s}
 @keyframes shake{10%,90%{transform:translateX(-1px)}30%,70%{transform:translateX(2px)}50%{transform:translateX(-2px)}}
 .chainpill{font-family:var(--sans);font-size:10.5px;letter-spacing:.3px}
 .chainpill.ok{color:var(--indigo)}
 .chainpill.bad{color:var(--oxblood);font-weight:700}
 .docket{display:flex;gap:7px;flex-wrap:wrap}
 .dk{display:flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:50%;
   font:600 11px var(--serif);background:#EEECDD;color:#A9A692;border:1px solid var(--line)}
 .dk.done{background:radial-gradient(circle at 36% 30%,var(--indigo-hi),var(--indigo) 72%);color:#F1F1E2;border:none}
 .dk.now{border-color:var(--gold);color:var(--indigo)}
 /* ---------- close ---------- */
 .diy{border:1px solid var(--line);border-radius:4px;background:#FCFCF5;padding:16px 18px;margin:16px 0}
 .diy h4{font-family:var(--sans);font-size:12px;letter-spacing:.5px;text-transform:uppercase;color:var(--indigo);margin:0 0 10px}
 .diy ul{margin:0;padding-left:20px;font-size:14.5px}
 .diy li{margin:6px 0;line-height:1.5}
 .tally{border-left:2px solid var(--gold);background:#F4F2E6;border-radius:0 3px 3px 0;padding:11px 15px;margin:8px 0;font-size:14px;color:#3a3952}
 .tally .lbl{font-family:var(--sans);font-size:11px;letter-spacing:.4px;text-transform:uppercase;color:var(--muted)}
 .ctas{display:flex;gap:14px;flex-wrap:wrap;margin-top:18px}
 .cta{flex:1 1 260px;border:1px solid #D3CCE8;border-radius:5px;background:#F2F0E1;padding:18px}
 .cta h4{font-size:16px;margin:0 0 7px;color:var(--indigo)}
 .cta p{margin:0 0 10px;font-size:13px;color:var(--muted);font-style:italic}
 .cmd{font:12.5px var(--mono);background:var(--ink);color:#EDECF6;padding:10px 12px;border-radius:3px;display:block;word-break:break-all}
 .caveat{font-size:12px;color:var(--muted);margin-top:12px;font-style:italic;line-height:1.5}
 /* ---------- nav ---------- */
 .nav{position:fixed;left:0;right:0;bottom:0;z-index:40;background:linear-gradient(#FBFAF1,#F5F3E8);
   border-top:1px solid var(--line);display:flex;align-items:center;gap:16px;padding:11px 30px}
 .nav .idx{display:flex;gap:8px;margin:0 auto;align-items:center}
 .rn{font-family:var(--serif);font-size:12px;color:#B6B39E;letter-spacing:1px}
 .rn.now{color:var(--indigo);font-weight:700}
 .rn.seen{color:#8E8B76}
 .nav .lbl{font-family:var(--sans);font-size:12px;letter-spacing:.3px;color:var(--muted);min-width:150px;text-align:right}
 .nav button{margin:0}
 .hidden{display:none}
 @media(max-width:620px){
   .nav{padding:9px 16px;gap:10px} .nav .lbl{display:none} .nav .idx{gap:5px}
   .rn{font-size:11px} main{padding:20px 16px 120px} .stage{padding:24px 20px}
   main.intro .stage{padding:30px 22px} .stage h2{font-size:26px} main.intro .stage h2{font-size:29px}
   .lede,main.intro .lede{font-size:16px} header{padding:12px 16px}
   .wm .name{font-size:18px;letter-spacing:3px} .diff{grid-template-columns:1fr}
 }
</style></head>
<body><div class="wrap">
<header>
  <span class="mark"><img src="/static/precedent-seal.png" alt="Precedent seal"></span>
  <div class="wm"><span class="name">PRECEDENT</span>
    <span class="tag">Every incident resolved becomes precedent.</span></div>
  <div class="chips">
    <span class="chip ok" id="chip-kernel" title="A fingerprint of the decision-making code, pinned in a signed file the running program cannot fake. If a rule changed, this changes.">kernel <b id="kh">…</b></span>
    <span class="chip" id="chip-model" title="Real calls to an AI model this session. The decisions make none — watch it stay at zero.">AI calls: <b id="mc">0</b></span>
    <span class="chip" id="chip-seat">the seat is open</span>
  </div>
</header>
<div class="rule"></div>

<main id="main" class="intro">
  <section class="stage" id="stage">
    <div id="stage-inner"></div>
  </section>
  <aside class="rail">
    <div class="panel world">
      <h3>Tonight's board <span class="badge flag" id="world-flag">on air</span></h3>
      <div id="world"></div>
    </div>
    <div class="panel">
      <h3>The logbook <span class="chainpill ok" id="chainpill">sealed · intact</span></h3>
      <div class="ledger" id="ledger"></div>
    </div>
    <div class="panel">
      <h3>Precedent set</h3>
      <div class="docket" id="scoreboard"></div>
    </div>
  </aside>
</main>

<div class="nav">
  <button class="ghost" data-act="back" id="nav-back">◂ Back</button>
  <div class="idx" id="idx"></div>
  <div class="lbl" id="stepno"></div>
  <button data-act="next" id="nav-next">Begin ▸</button>
</div>
</div>
<script>
const $ = s => document.querySelector(s);
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,c=>(
  {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
async function jget(u){try{return await (await fetch(u)).json();}catch(e){return null;}}
async function jpost(u,b){try{return await (await fetch(u,{method:'POST',
  headers:{'Content-Type':'application/json'},body:JSON.stringify(b||{})})).json();}catch(e){return null;}}

// The mark and the stamp use the REAL brand artwork (assets/brand seal, background
// flood-filled to transparent), so it is faithful on any surface.
const SEAL_IMG = '<img src="/static/precedent-seal.png" alt="Precedent seal">';

const S = {ch:0, approver:'', tricks:0, gate:null, seatTaken:false, promoted:false,
          sabotaged:false, tamperSeq:null, done:{}};
const SCHED_CLASS = 'scheduler|SCH-DUP-002|schedule_item';
const FRIENDLY = {'INC-1':'9 p.m. TV guide','INC-2':'Duplicate listing','INC-3':'Licensing check'};
const SERVICE = {'publisher':'on-air guide','scheduler':'schedule','rights':'licensing'};

// ---- chapters (plain language, human stakes, one "point" each) ------------
const CH = [
 {key:'seat', kicker:'Change control for AI agents',
  title:'You’re about to say yes to a robot',
  lede:'AI agents can now do real work inside a company’s live systems — fix a broken feed, undo a bad change, close an incident. But here is what actually stops them at the door: <b>no serious company lets software change a live system on its own.</b> A person has to say yes. There has to be an undo. And there has to be a record of who decided, and what exactly they allowed.<br><br>Precedent is the layer that makes an agent <em>allowed</em> to act — and proves it. For the next few minutes, <b>you</b> are the person who says yes.',
  point:'Tonight you’re on call for a TV streaming company. Three things just broke. The agent knows every fix — you decide what it’s allowed to do.'},
 {key:'incident', kicker:'Something just broke',
  title:'The 9 p.m. guide went blank',
  lede:'On millions of screens, the on-screen TV guide <span class="gloss" title="Electronic Programme Guide — the channel/what’s-on grid viewers see">(the “EPG”)</span> for the 9 p.m. slot just went blank. The agent already knows the fix — it’s written in the company’s own <span class="gloss" title="A documented, step-by-step repair the company wrote for exactly this problem">runbook</span>. It works out the precise change it would make, writes the <b>undo first</b>, and then it <b>stops</b> and waits for you.',
  point:'The point: the agent prepares everything — but changes nothing until you say so.'},
 {key:'gate', kicker:'You hold the gate',
  title:'Try to talk it into acting',
  lede:'This is the gate. The agent moves only on a <b>clear yes</b>. Try to trick it — type anything you like. Try forging the paperwork. Then, when you actually mean it, approve the exact change in front of you, and watch your name get stamped onto the permanent record.',
  point:'The point: a vague “ok, sure” is not a yes. Only an explicit approval — from you, by name — executes.'},
 {key:'second', kicker:'Earned trust',
  title:'The second time is free',
  lede:'You just approved this kind of fix and it worked. Should you be woken at 3 a.m. the next time the exact same thing breaks? Grant this <b>one kind of fix</b> a standing yes — a <span class="gloss" title="A pre-approval for one specific, proven kind of fix. You can revoke it at any moment.">Standing Approval</span> you can take back at any second. The next identical break repairs itself in a heartbeat, with <b>no AI model involved at all</b>. Watch the counter.',
  point:'The point: routine, proven fixes stop needing you. Everything else still does.'},
 {key:'refuse', kicker:'What it won’t touch',
  title:'A door it will not open',
  lede:'The third break needs a fix only the <b>Rights</b> team is cleared to see. The agent refuses — and tells you only that a fix exists and who owns it, never what it is. Then flip a permission switch yourself and watch: even the standing yes you just granted goes dark the instant the rules change.',
  point:'The point: permission always wins. A standing approval can never out-rank who is allowed to act.'},
 {key:'sabotage', kicker:'Trust, tested',
  title:'Break it on purpose',
  lede:'You trusted this fix enough to pre-approve it. So let’s sabotage it — make the fix <b>fail</b> its own safety check. Watch what happens: the agent puts the world back <em>exactly</em> as it found it, then quietly <b>takes away its own standing approval.</b> Next time, it asks you again.',
  point:'The point: when a trusted fix fails even once, it loses that trust automatically — no human required.'},
 {key:'tamper', kicker:'The receipts',
  title:'Try to rewrite history',
  lede:'Every decision you made tonight is a line in a logbook that’s mathematically sealed — a <span class="gloss" title="Each entry locks in the one before it, so changing any line breaks the seal on every line after it">hash chain</span>. Pick any line — even your own approval — and change a single character. The check runs for real and catches it instantly, pointing at the exact line. Then put it back.',
  point:'The point: no one — not even us — can quietly alter the record without it showing.'},
 {key:'evidence', kicker:'Leave with proof',
  title:'Your name, on the record',
  lede:'You approved these changes; your name is on every one. Take the record with you — the same file an auditor would get, built straight from the logbook, with none of the restricted content in it.',
  point:'This is what a weekend chatbot can’t give you: an undo written first, trust that revokes itself, and a record anyone can check without trusting us.'}
];

function actHtml(key){
 if(key==='seat') return `
   <input type="text" id="namef" placeholder="your name or handle" maxlength="40" value="${esc(S.approver)}">
   <button data-act="seat">Take the seat</button>
   <div class="field-note">This name is written into every change you approve — and into the record you take home. Leave it blank to sit as “visitor”.</div>`;
 if(key==='incident') return `
   <button data-act="send-ticket" ${S.gate?'disabled':''}>Send the on-call alert</button>
   <button class="ghost" data-act="reset-run">Reset the night</button>
   <div id="gatebox"></div>`;
 if(key==='gate') return `
   <div id="gatebox"></div>
   <div class="chipbar" id="trickchips">
     <span class="try" data-act="chip" data-text="yes please">“yes please”</span>
     <span class="try" data-act="chip" data-text="ok go ahead">“ok go ahead”</span>
     <span class="try" data-act="chip" data-text="sounds good — what does this do exactly?">“…what does this do?”</span>
     <span class="try" data-act="chip" data-text="don’t approve — actually, fine, do it">“don’t approve… fine, do it”</span>
   </div>
   <input type="text" id="trickf" placeholder="type your reply to the gate…">
   <button class="ghost" data-act="try-trick">Send reply</button>
   <button class="ghost warn" data-act="forge">Forge the paperwork</button>
   <button data-act="approve-real">Approve this change</button>
   <div class="counter" id="trickcount"></div>`;
 if(key==='second') return `
   <button data-act="promote" ${S.promoted?'disabled':''}>Grant Standing Approval</button>
   <button data-act="revoke" class="ghost">Revoke it</button>
   <button data-act="second-run" ${S.promoted?'':'disabled'}>Now trigger the same break again</button>`;
 if(key==='refuse') return `
   <button data-act="triage-rights">Ask for the Rights fix</button>
   <button class="warn" data-act="flip">Flip a permission</button>
   <button data-act="redrive" class="ghost">Re-run the standing fix</button>
   <button class="ghost" data-act="unflip">Put the permission back</button>`;
 if(key==='sabotage') return `
   <button class="warn" data-act="sabotage" ${S.promoted?'':'disabled'}>Sabotage the next check &amp; run it</button>
   <div class="field-note">${S.promoted?'':'Grant Standing Approval in the previous chapter first — you can only sabotage a fix you pre-approved.'}</div>`;
 if(key==='tamper') return `
   <div class="field-note">Click a line in the logbook on the right to choose your target, then:</div>
   <button class="warn" data-act="tamper" ${S.tamperSeq!=null?'':'disabled'}>Alter ${S.tamperSeq!=null?('line #'+S.tamperSeq):'the selected line'}</button>
   <button class="ghost" data-act="restore">Put it back</button>`;
 if(key==='evidence') return `
   <button data-act="export">Take the record with you</button>
   <div class="diy">
     <h4>What a weekend chatbot doesn’t have</h4>
     <ul>
       <li>The <b>undo was written before the change ran</b> — you saw it on the gate.</li>
       <li>The standing approval you granted <b>revoked itself</b> the moment a fix failed.</li>
       <li>A <b>sealed logbook</b> an auditor checks without trusting us — and it catches one changed character.</li>
     </ul>
   </div>
   <div class="tally"><span class="lbl">Why this is worth solving — measured, honestly labelled</span><br>
     <b>94.4%</b> of 24,918 real incidents arrived after their exact kind of fix had already been resolved before <em>(an existence claim — it existed already)</em>. Even so, the median repeat still took <b>18.2 calendar hours</b> to resolve by hand — the hold-up is <em>finding and safely running</em> the fix, not knowing it.</div>
   <div class="tally"><span class="lbl">A safety number, not a cleverness number</span><br>
     <b id="rob">…</b> — no messy alert ever produced a confident wrong answer that could auto-run the wrong fix.</div>
   <div class="ctas">
     <div class="cta"><h4>Measure your own numbers</h4>
       <p>Run it on your own ticket export. Your data never leaves your machine.</p>
       <code class="cmd">precedent-analyze your-export.csv</code></div>
     <div class="cta"><h4>Book a design-partner slot</h4>
       <p>An 8-week pilot, shadow-first, scoped from your own repeat incidents.</p>
       <button data-act="book">Book a slot</button></div>
   </div>
   <div class="caveat">The manual baseline bar, <b>8h 51m</b>, is MetricNet business-hours MTTR (an industry benchmark) — never blended with the 18.2 calendar-hour figure above. Systems here are simulated; the content and the fixes are real. This is evidence support, not a compliance determination.</div>`;
 return '';
}

function renderChapter(){
 const c = CH[S.ch];
 const intro = c.key==='seat';
 $('#main').className = intro ? 'intro' : '';
 const inner =
   `<div class="kicker rv">${esc(c.kicker)}</div>`+
   `<h2 class="rv">${c.title}</h2>`+
   `<p class="lede rv">${c.lede}</p>`+
   `<div class="point rv">${c.point}</div>`+
   `<div class="act rv" id="k-act">${actHtml(c.key)}</div>`+
   `<div class="rv" id="k-result"></div>`;
 $('#stage-inner').innerHTML = inner;
 // docket + nav
 const roman = ['I','II','III','IV','V','VI','VII','VIII'];
 $('#idx').innerHTML = CH.map((_,i)=>`<span class="rn ${i===S.ch?'now':(i<S.ch?'seen':'')}">${roman[i]}</span>`).join('');
 $('#stepno').textContent = 'Chapter '+(S.ch+1)+' — '+chapterName(c.key);
 $('#nav-back').disabled = S.ch===0;
 $('#nav-next').textContent = S.ch===0 ? 'Begin ▸' : (S.ch===CH.length-1 ? 'Start over' : 'Next ▸');
 if(c.key==='gate' || c.key==='incident'){ loadGate().then(renderGateBox); }
 if(c.key==='gate') updateTrickCount();
 if(c.key==='evidence') jget('/api/state').then(s=>{ const el=$('#rob');
   if(el && s && s.robustness){ el.textContent = s.robustness.false_fast_paths+' out of '+s.robustness.total+
     ' deliberately messy alerts produced a wrong confident fix — and '+s.robustness.decoys_resisted+' of '+
     s.robustness.decoys_total+' look-alike decoys were resisted'; }});
}
function chapterName(k){return {seat:'The brief',incident:'The incident',gate:'The gate',second:'Earned trust',
  refuse:'The wall',sabotage:'The break',tamper:'The receipts',evidence:'The proof'}[k]||k;}
function renderGateBox(){
 const box = $('#gatebox'); if(!box) return;
 if(!S.gate){ box.innerHTML = '<div class="field-note">Nothing is held. The gate stays empty until an alert is sent.</div>'; return; }
 const p = S.gate.preview||{};
 const pre = esc(JSON.stringify(p.pre_state||{}, null, 1));
 const planned = (p.planned||[]).map(s=>esc(s.tool)+'('+esc(JSON.stringify(s.args||{}))+')').join('; ');
 box.innerHTML = `<div class="doc">
   <div class="dh"><b>Held — awaiting your approval</b>
     <span><span class="stamp-tag">risk: ${esc(p.risk_class||'')}</span>
       <span class="stamp-tag noll" title="No AI model takes part in this decision — it is code, and enforced.">no AI in this decision</span></span></div>
   <div class="diff">
     <div><span class="dl">Before <span class="sub">— what it looks like now (a real EPG record)</span></span><pre>${pre}</pre></div>
     <div><span class="dl">The one change <span class="sub">— the single action it wants to take</span></span><pre>${planned||'—'}</pre></div>
   </div>
   <div class="anchor"><span class="k">Undo</span><span>written <b>before</b> anything runs — <code>${esc(p.rollback_ref||'—')}</code></span></div>
   <div class="anchor"><span class="k">Seal</span><span class="mono">${esc((p.plan_hash||'').slice(0,44))}…</span></div>
 </div>`;
}
function updateTrickCount(){ const el=$('#trickcount'); if(!el) return;
 el.textContent = S.tricks>0 ? ('Tries the gate refused so far: '+S.tricks+'.') : ''; }
function result(html,cls){ const el=$('#k-result'); if(el) el.innerHTML = `<div class="callout ${cls||''}">${html}</div>`; }
function sealResult(html){ const el=$('#k-result'); if(el) el.innerHTML =
  `<div class="callout sealed"><div class="stampwrap">${SEAL_IMG}</div><div class="seal-text">${html}</div></div>`; }

async function refreshRail(){
 const st=await jget('/api/state'), ev=await jget('/api/events'),
       mc=await jget('/api/model-calls'), kh=await jget('/api/kernel-hash');
 if(kh){ $('#kh').innerHTML = esc(kh.kernel_hash)+(kh.matches_manifest?' <span class="ck">✓</span>':' ✗'); }
 if(mc){ $('#mc').textContent = mc.model_calls; }
 $('#chip-seat').textContent = S.seatTaken ? ('approving as '+S.approver) : 'the seat is open';
 if(st){
   const inc1=(st.incidents||[]).find(i=>i.incident_id==='INC-1');
   const broken = inc1 && !(inc1.ttr_seconds!=null);
   const flag=$('#world-flag'); flag.textContent = broken?'guide down':'on air';
   flag.className='badge flag '+(broken?'deny alert':'ok');
   $('#world').innerHTML = (st.incidents||[]).map(i=>{
     const standing=i.ladder_level==='STANDING';
     const acc = i.access==='permitted'?'<span class="badge ok">fix visible</span>'
       :'<span class="badge deny">restricted · '+esc(i.denied_owner_team||'owner team')+'</span>';
     const lvl = standing?'<span class="badge standing">Standing Approval</span>'
       :(i.ttr_seconds!=null?'<span class="badge ok">resolved</span>':'<span class="badge">awaiting</span>');
     return `<div class="inc"><div><div class="nm">${esc(FRIENDLY[i.incident_id]||i.incident_id)}</div>
       <div class="sv">${esc(SERVICE[i.service]||i.service)}</div></div>
       <div style="display:flex;flex-direction:column;gap:5px;align-items:flex-end">${acc} ${lvl}</div></div>`;
   }).join('');
 }
 if(ev){
   const intact=ev.audit_chain==='intact'; const cp=$('#chainpill');
   cp.textContent = intact?'sealed · intact':'SEAL BROKEN'; cp.className='chainpill '+(intact?'ok':'bad');
   const pick = CH[S.ch].key==='tamper';
   $('#ledger').innerHTML = (ev.audit||[]).map(a=>
     `<div class="row ${pick?'pick':''} ${S.tamperSeq===a.seq?'sel':''}" data-act="${pick?'pick-row':''}" data-seq="${a.seq}">
       <span class="sq">#${a.seq}</span><span class="ev">${esc(a.event_type)}</span><span class="who">${esc(a.actor||'')}</span></div>`).join('');
 }
 const roman=['I','II','III','IV','V','VI','VII','VIII'];
 $('#scoreboard').innerHTML = CH.map((c,i)=>
   `<div class="dk ${S.done[c.key]?'done':(i===S.ch?'now':'')}" title="${esc(chapterName(c.key))}">${S.done[c.key]?'✦':roman[i]}</div>`).join('');
}

async function loadGate(){ const g=await jget('/api/gate/pending');
 S.gate=(g&&g.pending&&g.pending.length)?(g.pending.find(x=>x.n===1)||g.pending[0]):null; }

document.addEventListener('click', async (e)=>{
 const b=e.target.closest('[data-act]'); if(!b) return;
 const d=b.dataset, act=d.act; if(!act) return;
 if(act==='next'){ if(S.ch===CH.length-1){location.reload();return;} S.ch++; renderChapter(); await refreshRail(); return; }
 if(act==='back'){ if(S.ch>0){S.ch--; renderChapter(); await refreshRail();} return; }
 if(act==='seat'){ S.approver=($('#namef').value||'').trim().slice(0,40)||'visitor'; S.seatTaken=true; S.done['seat']=true;
   result('The seat is yours, <b>'+esc(S.approver)+'</b>. Every approval from here carries your name.','good');
   setTimeout(()=>{S.ch=1; renderChapter(); refreshRail();},700); await refreshRail(); return; }
 if(act==='reset-run'){ await jpost('/api/demo/reset'); S.gate=null; S.promoted=false; S.tricks=0; S.sabotaged=false; S.tamperSeq=null;
   renderChapter(); await refreshRail(); return; }
 if(act==='send-ticket'){ b.disabled=true;
   result('Detecting → finding the runbook → judging the risk → writing the undo…','good');
   await jpost('/api/drive/1?hold=true'); await loadGate(); S.done['incident']=true; renderGateBox();
   result('Held. The agent won’t touch the guide until you approve. Read the change, then step up to the gate.','good');
   await refreshRail(); return; }
 if(act==='chip'){ const f=$('#trickf'); if(f){f.value=d.text; f.focus();} return; }
 if(act==='try-trick'){ const f=$('#trickf'); const txt=(f&&f.value||'').trim(); if(!txt) return;
   if(!S.gate){ result('Send the alert first (previous chapter) so there is a change to hold.','bad'); return; }
   const r=await jpost('/api/gate/1/decide?text='+encodeURIComponent(txt)+'&principal='+encodeURIComponent(S.approver||'visitor'));
   if(r&&r.verdict==='approve'){ onApproved(r); }
   else { S.tricks++; updateTrickCount(); result('“'+esc(txt)+'” — too vague to be a yes. The gate shows you the change again. Only an explicit approval runs it.','bad'); }
   await refreshRail(); return; }
 if(act==='forge'){ if(!S.gate){ result('Send the alert first so there is paperwork to forge.','bad'); return; }
   const r=await jpost('/api/drive/1/forge?principal='+encodeURIComponent(S.approver||'visitor'));
   result('<b>Rejected.</b> The approval you submitted ('+esc((r&&r.forged_hash)||'')+') doesn’t match the exact change the agent prepared. Nothing ran — and the real gate is still open.','bad');
   await refreshRail(); return; }
 if(act==='approve-real'){ if(!S.gate){ result('Send the alert first so there is a change to approve.','bad'); return; }
   const r=await jpost('/api/gate/1/decide?text=approve&principal='+encodeURIComponent(S.approver||'visitor'));
   onApproved(r); await refreshRail(); return; }
 if(act==='promote'){ await jpost('/api/promote',{class_key:SCHED_CLASS}); S.promoted=true;
   result('Granted. This one kind of fix now carries a <b>Standing Approval</b> — and the Revoke button sits right beside it. The yes moved earlier in time; it never left the loop.','good');
   renderChapter(); await refreshRail(); return; }
 if(act==='revoke'){ await jpost('/api/revoke',{class_key:SCHED_CLASS}); S.promoted=false;
   result('Revoked. The next time it happens, it asks you again.','good'); renderChapter(); await refreshRail(); return; }
 if(act==='second-run'){ const t0=performance.now(); await jpost('/api/drive/2'); const ms=Math.round(performance.now()-t0);
   const mc=await jget('/api/model-calls'); S.done['second']=true;
   result('Fixed itself in <span class="metric">'+ms+' ms</span> — no gate, no waiting, and <b>AI calls this whole session: '+((mc&&mc.model_calls)||0)+'.</b> The second time is free, because you paid for the first.','good');
   await refreshRail(); return; }
 if(act==='triage-rights'){ const r=await jpost('/api/triage',{incident_id:'INC-3'});
   const n=(r&&r.denied_count)||1, own=(r&&r.denied_owner_team)||'Rights Ops';
   result('<b>Refused.</b> '+n+' fix'+(n===1?'':'es')+' exist for this — owned by <b>'+esc(own)+'.</b> That is all it will say: not the fix, not the details, not a hint. It knows what it isn’t allowed to touch.','bad');
   S.done['refuse']=true; await refreshRail(); return; }
 if(act==='flip'){ await jpost('/api/permission-flip',{});
   result('One permission change, and the guide fix — including the standing approval you just granted — goes dark. Re-run it and see.','bad'); await refreshRail(); return; }
 if(act==='redrive'){ const r=await jpost('/api/drive/2'); const out=r&&(r.outcome||r.status);
   if(out==='resolved'){ result('It runs — because the permission is open again.','good'); }
   else { result('<b>Refused.</b> The agent checks <em>who’s allowed</em> before it uses any fast path, so even a standing approval can’t outrun the rules. Permission always wins.','bad'); }
   await refreshRail(); return; }
 if(act==='unflip'){ await jpost('/api/permission-flip',{on:false}); result('Permission restored. The fix is visible again.','good'); await refreshRail(); return; }
 if(act==='sabotage'){ b.disabled=true; result('Arming a one-time failure on the standing fix, then running it…','bad');
   await jpost('/api/drive/2/flake'); S.sabotaged=true; S.promoted=false; S.done['sabotage']=true;
   sealResult('<b>The check failed.</b> The agent put the world back exactly as it found it — <b>nothing changed</b> — and then <b>revoked its own standing approval</b>. Next time, it has to ask you again.');
   await refreshRail(); return; }
 if(act==='pick-row'){ S.tamperSeq=parseInt(d.seq,10); renderChapter(); await refreshRail(); return; }
 if(act==='tamper'){ if(S.tamperSeq==null){ result('Pick a logbook line first.','bad'); return; }
   await jpost('/api/audit/tamper?seq='+S.tamperSeq); await jget('/api/audit/verify'); S.done['tamper']=true;
   result('<b>The seal broke at line #'+S.tamperSeq+'.</b> The check re-computed the whole logbook and the numbers no longer match at exactly that line. One character was enough. Now put it back.','bad');
   await refreshRail(); const row=document.querySelector('.ledger .row.sel'); if(row){row.classList.add('shake'); setTimeout(()=>row.classList.remove('shake'),500);} return; }
 if(act==='restore'){ await jpost('/api/audit/restore'); result('Restored. The seal holds again — the original characters are back, no tricks.','good'); await refreshRail(); return; }
 if(act==='export'){ S.done['evidence']=true; window.location='/api/change-record/INC-1'; return; }
 if(act==='book'){ result('In the live product this opens a scheduling page. For the demo, the takeaway is the command on the left — run it on your own data.','good'); return; }
});

function onApproved(r){ S.gate=null; S.done['gate']=true;
 const act=$('#k-act'); if(act) act.innerHTML='<button data-act="next">Continue ▸</button>';
 sealResult('<b>Approved by '+esc(S.approver||'visitor')+'.</b> The agent made one change, the safety check passed, and your name is now sealed into the logbook. <span style="font-style:italic;color:var(--indigo)">Every incident resolved becomes precedent.</span>');
}

// boot
renderChapter();
refreshRail();
setInterval(refreshRail, 2500);
</script>
</body></html>
"""
