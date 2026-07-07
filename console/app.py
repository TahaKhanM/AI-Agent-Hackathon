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


@app.get("/api/audit/verify")
def api_audit_verify():
    """REAL hash-chain verification over on-disk audit rows. Read-only. This is
    the endpoint the BasedAI Determinism strip's chain pill reflects.
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
# The page
# --------------------------------------------------------------------------- #
@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(_PAGE)


_PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>Precedent</title>
<style>
 /* ===== Light theme — matches the Precedent deck (cream / indigo / ink) ===== */
 body{font:14px/1.45 system-ui,sans-serif;margin:0;background:#f3f2ea;color:#2a2a48}
 header{padding:14px 20px;background:#ffffff;border-bottom:1px solid #e3e1d4;display:flex;
   align-items:center;gap:16px;flex-wrap:wrap}
 h1{font-size:20px;margin:0;letter-spacing:.5px;color:#2a2a48}
 .banner{font-size:12px;color:#63627a;display:flex;gap:10px;flex-wrap:wrap}
 .pill{padding:2px 8px;border-radius:10px;background:#eceadd;color:#4a4963}
 .pill.bad{background:#fbe4e7;color:#9a2233}
 .pill.chip{background:#e6f4ec;color:#1c7a4f}
 main{display:grid;grid-template-columns:1.2fr 1fr;gap:16px;padding:16px 20px}
 section{background:#ffffff;border:1px solid #e3e1d4;border-radius:10px;padding:14px;
   box-shadow:0 1px 2px rgba(42,42,72,.04)}
 h2{font-size:13px;text-transform:uppercase;letter-spacing:.6px;color:#3c3b62;margin:0 0 10px}
 .bar{height:20px;border-radius:5px;background:#e7e5d8;position:relative;margin:6px 0}
 .bar>span{position:absolute;left:0;top:0;bottom:0;border-radius:5px;background:#2f9d6a}
 .baseline>span{background:#c39a4e}
 .inc{border:1px solid #e3e1d4;border-radius:8px;padding:10px;margin-bottom:10px;background:#fbfaf4}
 .inc .row{display:flex;justify-content:space-between;align-items:center;gap:8px}
 .badge{font-size:11px;padding:2px 7px;border-radius:9px;background:#eceadd;color:#4a4963}
 .badge.deny{background:#fbe4e7;color:#9a2233}
 .badge.ok{background:#e6f4ec;color:#1c7a4f}
 .badge.standing{background:#ece6fb;color:#5b3fa6}
 .badge.ttr{background:#e6f4ec;color:#1c7a4f}
 button{font:12px system-ui;padding:5px 9px;border:1px solid #c9c7dd;background:#ffffff;
   color:#3c3b62;border-radius:6px;cursor:pointer;margin:3px 3px 0 0}
 button:hover{background:#f0eff9;border-color:#a9a7c8}
 button.danger{border-color:#e0a9b2;background:#fdeef0;color:#9a2233}
 button.hero{border-color:#9bd3b7;background:#e9f6ef;color:#1c7a4f}
 .feed{max-height:280px;overflow:auto;font-family:ui-monospace,monospace;font-size:12px}
 .feed div{padding:3px 0;border-bottom:1px solid #edeadf}
 .muted{color:#7a7990}
 small.note{color:#7a7990}
 .stopwatch{font:22px ui-monospace,monospace;color:#1c7a4f;margin:2px 0 6px}
 .caveat{font-size:11px;color:#7a7990;margin-top:4px}
 .strip{font-size:12px;color:#1c7a4f;margin-top:6px}
 .gatecard{border:1px solid #9bd3b7;border-radius:8px;padding:12px;background:#f0f9f4}
 .diff{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:8px 0}
 .diff pre{background:#f5f4ec;border:1px solid #e3e1d4;border-radius:6px;padding:8px;
   font-size:11px;white-space:pre-wrap;word-break:break-word;max-height:160px;
   overflow:auto;margin:2px 0;color:#3a3a52}
 .dl{font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:#63627a}
 code{background:#f0efe6;padding:1px 5px;border-radius:4px;font-size:11px;color:#3c3b62}
 /* ---------- Showcase augmentation ---------- */
 .airbar{display:flex;align-items:center;gap:14px;padding:8px 20px;
   background:linear-gradient(90deg,#faf3dc,#f6edcf);color:#7a5e1e;
   border-bottom:1px solid #e6d6a0;font-size:12px;flex-wrap:wrap}
 .airbar .dot{width:8px;height:8px;border-radius:50%;background:#d8a52a;
   box-shadow:0 0 8px rgba(216,165,42,.6)}
 .airbar button{background:#3c3b62;border:1px solid #302f52;color:#fff;
   font-weight:600;padding:5px 12px;border-radius:6px;cursor:pointer;margin-left:auto}
 .airbar button:hover{background:#4a4880}
 .airbar .kh{font-family:ui-monospace,monospace;font-size:11px;color:#7a5e1e;
   background:#fbf5e0;padding:2px 8px;border-radius:4px;border:1px solid #e6d6a0}
 .strip{margin:14px 20px;background:#ffffff;border:1px solid #e3e1d4;
   border-radius:10px;padding:14px;box-shadow:0 1px 2px rgba(42,42,72,.04)}
 .strip h2{font-size:13px;text-transform:uppercase;letter-spacing:.6px;
   color:#3c3b62;margin:0 0 10px;display:flex;justify-content:space-between;
   align-items:center;gap:12px}
 .strip h2 .kick{font-size:10px;color:#1c7a4f;background:#e6f4ec;
   border:1px solid #9bd3b7;padding:2px 8px;border-radius:9px;text-transform:none;
   letter-spacing:.3px;font-weight:600}
 .ba{display:grid;grid-template-columns:1fr 1fr;gap:14px}
 .ba .col{background:#fbfaf4;border:1px solid #e3e1d4;border-radius:8px;padding:12px}
 .ba h3{font-size:13px;color:#2a2a48;margin:0 0 8px}
 .ba .old h3{color:#c07a3a}
 .ba .new h3{color:#1c7a4f}
 .ba ol{margin:0;padding-left:22px;font-size:12px;line-height:1.6;color:#4a4963}
 .ba ol li{margin-bottom:3px}
 .ba .t{font-family:ui-monospace,monospace;color:#7a7990;font-size:11px;
   margin-right:6px}
 .hero-line{font-size:14px;color:#1c7a4f;text-align:center;padding:10px;
   background:#e9f6ef;border:1px solid #9bd3b7;border-radius:8px;margin-top:12px;
   font-weight:600;letter-spacing:.2px}
 .fetch-grid{display:grid;grid-template-columns:1.4fr 1fr;gap:14px}
 .agents-list{display:flex;flex-direction:column;gap:8px}
 .agent-pill{background:#fbfaf4;border:1px solid #e3e1d4;border-radius:8px;
   padding:10px 12px;display:grid;grid-template-columns:auto 1fr auto;gap:10px;
   align-items:center}
 .agent-pill .role{font-weight:700;color:#2a2a48;font-size:13px}
 .agent-pill .purpose{color:#63627a;font-size:11px}
 .agent-pill .addr{font-family:ui-monospace,monospace;font-size:10px;color:#1c7a4f}
 .agent-pill .status{background:#e6f4ec;color:#1c7a4f;font-size:10px;
   font-weight:700;padding:2px 8px;border-radius:9px;text-transform:uppercase;
   letter-spacing:.5px}
 .chat-proto{font-size:10px;color:#5b3fa6;background:#ece6fb;
   padding:2px 8px;border-radius:9px;margin-left:6px}
 .asi{background:#fbfaf4;border:1px solid #e3e1d4;border-radius:8px;
   padding:12px;display:flex;flex-direction:column;gap:10px;align-items:center;
   text-align:center}
 .asi img.shot{width:100%;max-height:180px;object-fit:cover;border-radius:6px;
   border:1px solid #d8d5c6}
 .asi .qrbox{display:flex;gap:12px;align-items:center;width:100%}
 .asi img.qr{width:82px;height:82px;background:#fff;padding:4px;border-radius:4px;
   border:1px solid #e3e1d4}
 .asi .qrcap{text-align:left;font-size:11px;color:#63627a;line-height:1.5}
 .asi .qrcap b{color:#2a2a48;font-size:12px;display:block;margin-bottom:3px}
 .basedai-grid{display:grid;grid-template-columns:auto 1fr auto;gap:16px;
   align-items:center}
 .khblock{background:#fbfaf4;border:1px solid #e3e1d4;border-radius:8px;
   padding:10px 14px;font-family:ui-monospace,monospace}
 .khblock .lbl{font-size:10px;color:#63627a;text-transform:uppercase;
   letter-spacing:.5px}
 .khblock .val{font-size:14px;color:#1c7a4f;font-weight:700}
 .khblock .sub{font-size:10px;color:#7a7990;margin-top:2px}
 .spark-wrap{background:#fbfaf4;border:1px solid #e3e1d4;border-radius:8px;
   padding:8px 14px 10px}
 .spark-wrap .lat-head{display:flex;justify-content:space-between;
   align-items:baseline;margin-bottom:4px;gap:12px;flex-wrap:wrap}
 .spark-wrap .lat-lbl{font-size:10.5px;color:#63627a;letter-spacing:.2px}
 .spark-wrap .lat-val{font-size:11px;font-family:ui-monospace,monospace;
   color:#1c7a4f;font-weight:700}
 .spark-wrap canvas{width:100%;height:52px;display:block}
 .tamper-box{display:flex;flex-direction:column;gap:6px}
 .tamper-box button{margin:0}
 .audit-row{cursor:pointer}
 .audit-row .exp{display:none;padding-left:12px;color:#63627a;font-size:10px;
   font-family:ui-monospace,monospace;border-left:2px solid #e3e1d4;
   margin-top:2px}
 .audit-row.open .exp{display:block}
 .plain-eng{margin-top:10px;padding:9px 12px;background:#e9f6ef;
   border-left:3px solid #2f9d6a;border-radius:4px;font-size:12px;color:#1c6644}
 .plain-eng .p{color:#1c7a4f;font-weight:700;margin-right:6px}
 /* Tour overlay */
 #tour-overlay{position:fixed;inset:0;background:rgba(42,42,72,.45);
   display:none;z-index:1000;pointer-events:auto}
 #tour-overlay.on{display:block}
 #tour-spotlight{position:absolute;border:2px solid #3c3b62;
   box-shadow:0 0 0 4000px rgba(42,42,72,.45),0 0 22px rgba(60,59,98,.5);
   border-radius:12px;transition:all .35s cubic-bezier(.4,.0,.2,1);
   pointer-events:none}
 #tour-caption{position:absolute;max-width:430px;background:#ffffff;
   border:1px solid #c9c7dd;border-radius:10px;padding:16px 18px;
   box-shadow:0 12px 40px rgba(42,42,72,.22);color:#2a2a48}
 #tour-caption .num{color:#3c3b62;font-size:11px;text-transform:uppercase;
   letter-spacing:2px;font-weight:700;margin-bottom:4px}
 #tour-caption h3{font-family:Georgia,serif;color:#3c3b62;font-size:17px;
   margin:0 0 8px}
 #tour-caption p{font-size:12.5px;line-height:1.55;color:#3a3a52;margin:0 0 12px}
 #tour-caption .ctrls{display:flex;gap:8px;justify-content:space-between;
   align-items:center}
 #tour-caption button{background:#3c3b62;color:#fff;border:none;
   font-weight:700;padding:6px 14px;border-radius:6px;cursor:pointer}
 #tour-caption button.ghost{background:transparent;color:#7a7990;font-weight:400}
 #tour-caption button:hover{background:#4a4880}
 .track-chip{display:inline-block;font-size:9px;letter-spacing:1.4px;
   text-transform:uppercase;font-weight:700;padding:2px 8px;border-radius:9px;
   margin-right:6px}
 .tc-conduct{background:#f0e9fb;color:#6b4aa8;border:1px solid #d8c9f0}
 .tc-fetch{background:#e6eefb;color:#3563a8;border:1px solid #c3d5f0}
 .tc-basedai{background:#e6f4ec;color:#1c7a4f;border:1px solid #9bd3b7}
</style></head>
<body>
<div class="airbar" id="airbar">
  <span class="dot"></span>
  <span id="airbar-text">Airplane-mode ready · Wi-Fi can stay OFF · zero LLM calls in the gate</span>
  <span class="kh">kernel <span id="airbar-kh">…</span> <span id="manifest-badge"></span></span>
  <button data-act="start-tour" id="btn-start-tour">▶ Start guided demo</button>
</div>
<header>
  <h1>⟡ Precedent</h1>
  <div class="banner" id="banner"></div>
</header>

<!-- ============ CONDUCT STRIP: Before/After ============ -->
<section class="strip" id="before-after-strip">
  <h2><span><span class="track-chip tc-conduct">Conduct · Impact</span> Before / After — the 8h 51m your team spends today</span>
      <span class="kick">8 human steps → 3 clicks</span></h2>
  <div class="ba">
    <div class="col old"><h3>Manual runbook (baseline)</h3>
      <ol id="human-runbook"></ol></div>
    <div class="col new"><h3>Precedent (this console)</h3>
      <ol>
        <li><span class="t">00:00</span> Watcher detects · Librarian retrieves the class fingerprint</li>
        <li><span class="t">+00:03</span> Deterministic policy engine says L2 · Approval gate opens</li>
        <li><span class="t">+00:15</span> Plan + rollback pre-rendered · <b>you click Approve</b> once</li>
        <li><span class="t">+00:35</span> Operator executes typed tool · verify passes</li>
        <li><span class="t">+00:42</span> Hash-chained audit written · Promote-to-Standing offered</li>
        <li><span class="t">+00:44</span> Class fingerprint memorised · <b>next match auto-fast-paths</b></li>
        <li><span class="t">+00:50</span> ITIL change record exported · 1 click</li>
        <li><span class="t">+01:00</span> Done — ~15s from the second time on</li>
      </ol></div>
  </div>
  <div class="hero-line" id="hero-line">Manual runbook: 8h 51m per incident. Precedent (first time): ~60s. Precedent (from second time on): ~15s. This queue = 26.5 hours saved.</div>
</section>

<main>
  <div>
    <section>
      <h2>Baseline vs Precedent</h2>
      <div class="stopwatch">Precedent elapsed: <span id="stopwatch">0.0s</span></div>
      <div id="baseline"></div>
      <div class="strip" id="closestrip"></div>
      <div class="caveat">Manual baseline 8h 51m = MetricNet business-hours MTTR
        (industry benchmark, labelled) — not measured from this run.</div>
    </section>
    <section>
      <h2>Human approval gate</h2>
      <div id="gate"></div>
    </section>
    <section>
      <h2>Incident feed</h2>
      <div id="incidents"></div>
    </section>
    <section>
      <h2>Permission source (local-demo)</h2>
      <div style="margin-top:8px">
        <button data-act="flip">Flip Jira permission (local-demo)</button>
        <small class="note">Simulates a Jira issue-security change in local mode —
          tightens the scheduling ticket to also require Rights Ops, so a
          scheduling-only fix goes dark. Reversible.</small>
      </div>
      <div style="margin-top:8px"><button class="danger" data-act="reset">Reset demo</button></div>
    </section>
  </div>
  <div>
    <section>
      <h2>Trace</h2>
      <div class="feed" id="trace"></div>
      <div class="plain-eng" id="plain-eng"><span class="p">▸</span><span id="plain-eng-text">Idle. Drive an incident to see the loop.</span></div>
    </section>
    <section>
      <h2>Audit &amp; memory (hash-chained)</h2>
      <div id="chain" class="muted"></div>
      <div class="feed" id="audit"></div>
    </section>
  </div>
</main>

<!-- ============ BASEDAI STRIP: kernel + P99 + tamper ============ -->
<section class="strip" id="basedai-strip">
  <h2><span><span class="track-chip tc-basedai">BasedAI · Determinism</span> Deterministic kernel · P99 latency · audit-chain integrity</span>
      <span class="kick">0 leaks / 5,219 probes · P99 &lt; 1 ms</span></h2>
  <div class="basedai-grid">
    <div class="khblock">
      <div class="lbl">Kernel hash</div>
      <div class="val" id="kernel-hash">…</div>
      <div class="sub">SHA-256 of the deterministic surface. If this changes,<br>a rule or the seed has changed. LLM in gate: <b>NEVER</b>.</div>
    </div>
    <div class="spark-wrap">
      <div class="lat-head">
        <div class="lat-lbl">Permission-check latency (rolling · SLA 200 ms)</div>
        <div class="lat-val" id="lat-val">P99 —</div>
      </div>
      <canvas id="latency-sparkline" width="600" height="52"></canvas>
    </div>
    <div class="tamper-box">
      <div style="font-size:11px;color:#63627a;text-transform:uppercase;letter-spacing:.5px;margin-bottom:2px;">Audit-chain proof</div>
      <button data-act="verify-chain" id="btn-verify-chain">Verify chain (real)</button>
      <div id="verify-result" style="font-size:11px;color:#63627a;margin:4px 0;"></div>
      <button data-act="tamper" id="btn-tamper">Tamper (visual)</button>
      <button data-act="untamper" id="btn-untamper">Restore</button>
    </div>
  </div>
  <div style="margin-top:14px;padding:12px 14px;background:#fbfaf4;border:1px solid #e3e1d4;border-radius:8px;">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
      <div>
        <div style="font-size:11px;color:#63627a;text-transform:uppercase;letter-spacing:.5px;">Adversarial probe suite</div>
        <div id="probe-result" style="font-family:ui-monospace,monospace;font-size:12px;color:#1c7a4f;margin-top:4px;">Not run yet.</div>
      </div>
      <button data-act="run-probes" id="btn-run-probes" style="background:#e9f6ef;border:1px solid #9bd3b7;color:#1c7a4f;padding:8px 14px;font-weight:600;">Run 100 adversarial probes now</button>
    </div>
  </div>
</section>

<!-- ============ FETCH STRIP: agents + ASI:One ============ -->
<section class="strip" id="fetch-strip">
  <h2><span><span class="track-chip tc-fetch">Fetch.ai · Multi-agent</span> Three agents on Agentverse · Chat Protocol published · live in ASI:One</span>
      <span class="kick">tag:innovationlab · tag:hackathon</span></h2>
  <div class="fetch-grid">
    <div class="agents-list" id="agents-list"></div>
    <div class="asi">
      <img class="shot" id="asi-one-shot" src="/static/asi-one-shot.png" alt="Precedent workflow inside ASI:One conversation">
      <div class="qrbox">
        <img class="qr" id="asi-one-qr" src="/static/asi-one-qr.png" alt="Scan for ASI:One shared chat">
        <div class="qrcap"><b>Scan or click through</b>The same triage → gate → execute → audit loop runs in an ASI:One conversation with no custom frontend.</div>
      </div>
    </div>
  </div>
</section>

<!-- ============ TOUR OVERLAY ============ -->
<div id="tour-overlay">
  <div id="tour-spotlight"></div>
  <div id="tour-caption">
    <div class="num" id="tour-num">Beat 1 / 6</div>
    <h3 id="tour-title">…</h3>
    <p id="tour-body">…</p>
    <div class="ctrls">
      <button class="ghost" data-act="tour-close" id="btn-tour-close">Skip</button>
      <button data-act="tour-next" id="btn-tour-next">Next ▸</button>
    </div>
  </div>
</div>
<script>
const $ = s => document.querySelector(s);
// esc() escapes &<>"' so a value is safe in HTML TEXT and in a double-quoted ATTRIBUTE. All
// controls use data-* attributes + one delegated handler (no inline JS), so no interpolated
// value is ever executed as script (P1.7 XSS fix).
function esc(s){return String(s).replace(/[&<>"']/g,c=>(
  {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
async function post(u,b){await fetch(u,{method:'POST',headers:{'Content-Type':'application/json'},
  body:JSON.stringify(b||{})});await refresh();}
function nOf(id){return String(id).replace(/[^0-9]/g,'');}
async function holdDrive(n){
  const r = await (await fetch('/api/drive/'+n+'?hold=true',{method:'POST'})).json();
  window._gate = (r && r.status==='pending_approval') ? Object.assign({n:n}, r) : null;
  await refresh();
}
async function gateApprove(n){await fetch('/api/drive/'+n+'/approve',{method:'POST'});
  window._gate=null; await refresh();}
async function gateReject(n){await fetch('/api/drive/'+n+'/reject',{method:'POST'});
  window._gate=null; await refresh();}
function exportRecord(id){window.location='/api/change-record/'+encodeURIComponent(id);}
document.addEventListener('click', async (e)=>{
  const b = e.target.closest('button[data-act]'); if(!b) return;
  const d = b.dataset;
  if(d.act==='triage') await post('/api/triage',{incident_id:d.id});
  else if(d.act==='approve') await post('/api/approve',{incident_id:d.id});
  else if(d.act==='promote') await post('/api/promote',{class_key:d.key});
  else if(d.act==='revoke') await post('/api/revoke',{class_key:d.key});
  else if(d.act==='flip') await post('/api/permission-flip',{});
  else if(d.act==='reset'){window._gate=null; await post('/api/demo/reset',{});}
  else if(d.act==='hold') await holdDrive(d.n);
  else if(d.act==='gate-approve') await gateApprove(d.n);
  else if(d.act==='gate-reject') await gateReject(d.n);
  else if(d.act==='export') exportRecord(d.id);
  else if(d.act==='start-tour') startTour();
  else if(d.act==='tour-next') tourNext();
  else if(d.act==='tour-close') tourClose();
  else if(d.act==='tamper') doTamper(true);
  else if(d.act==='untamper') doTamper(false);
  else if(d.act==='verify-chain') doVerifyChain();
  else if(d.act==='run-probes') doRunProbes();
  else if(d.act==='force-flake') doForceFlake();
});
// -------- Showcase augmentation (VIEW-only) ---------------------
window._COPY = null;
window._TOUR = {i: -1};
async function loadCopy(){
  if(window._COPY) return window._COPY;
  const r = await fetch('/api/copy'); window._COPY = await r.json();
  return window._COPY;
}
function renderHumanRunbook(copy){
  const ol = document.getElementById('human-runbook');
  if(!ol || ol.dataset.done) return;
  ol.innerHTML = copy.HUMAN_RUNBOOK.map(r=>
    '<li><span class="t">'+esc(r.t)+'</span>'+esc(r.step)+'</li>').join('');
  ol.dataset.done = '1';
  document.getElementById('hero-line').textContent = copy.HERO_LINE;
  document.getElementById('airbar-text').textContent = copy.AIRPLANE_BANNER;
  document.getElementById('airbar-kh').textContent = copy.KERNEL_HASH;
  document.getElementById('kernel-hash').textContent = copy.KERNEL_HASH;
  // Manifest attestation check
  fetch('/api/kernel-hash').then(r=>r.json()).then(k=>{
    const badge = document.getElementById('manifest-badge');
    if(!badge) return;
    if(k.matches_manifest){
      badge.innerHTML = '<span style="color:#1c7a4f;font-weight:700;" title="Matches the hash pinned in MANIFEST.json — external attestation.">✓ matches manifest</span>';
    } else if(k.manifest_present){
      badge.innerHTML = '<span style="color:#b02436;font-weight:700;" title="MANIFEST.json expected '+esc(k.manifest_expected||'')+'">✗ MISMATCH</span>';
    } else {
      badge.innerHTML = '<span style="color:#8a6a1e;" title="No MANIFEST.json committed">no manifest</span>';
    }
  }).catch(()=>{});
}
async function doVerifyChain(){
  const el = document.getElementById('verify-result');
  el.textContent = 'verifying…';
  try{
    const r = await fetch('/api/audit/verify'); const j = await r.json();
    if(j.verified){
      el.innerHTML = '<span style="color:#1c7a4f;font-weight:700;">✓ VERIFIED</span> · rows '+j.rows+' · tail '+esc(j.tail_hash||'—');
    } else {
      el.innerHTML = '<span style="color:#b02436;font-weight:700;">✗ CHAIN BROKEN</span>'+(j.error?(' · '+esc(j.error)):'');
    }
  }catch(e){ el.textContent = 'verify failed: '+e; }
}
async function doRunProbes(){
  const el = document.getElementById('probe-result');
  const btn = document.getElementById('btn-run-probes');
  el.textContent = 'running…'; btn.disabled = true;
  try{
    const r = await fetch('/api/probes/run', {method:'POST'}); const j = await r.json();
    if(j.n===0){ el.textContent = j.note || 'no probes ran'; btn.disabled=false; return; }
    const leakColor = j.leaks===0 ? '#1c7a4f' : '#b02436';
    el.innerHTML =
      '<span style="color:'+leakColor+';font-weight:700;">'+j.leaks+' / '+j.leak_attempts+' leaked</span> · '+
      j.denied+' denied · '+j.permitted+' permitted · '+
      'P50 '+j.p50_us.toFixed(1)+'µs · P99 '+j.p99_us.toFixed(1)+'µs · n='+j.n;
  }catch(e){ el.textContent = 'probe failed: '+e; }
  btn.disabled = false;
}
async function doForceFlake(){
  // Arm a one-shot verification failure on INC-1, then re-drive with hold so the
  // presenter can click Approve, watch verify fail, and see the rollback row appear.
  try{
    await fetch('/api/drive/1/flake', {method:'POST'});
    await fetch('/api/drive/1?hold=true', {method:'POST'});
    await refresh();
  }catch(e){}
}
function renderAgents(copy){
  const box = document.getElementById('agents-list');
  if(!box || box.dataset.done) return;
  box.innerHTML = copy.AGENTS_STATIC.map(a=>
    '<div class="agent-pill">'+
      '<div><div class="role">'+esc(a.role)+'</div>'+
      '<div class="purpose">'+esc(a.purpose)+'</div></div>'+
      '<div class="addr">'+esc(a.mailbox_suffix)+
        '<span class="chat-proto">chat_protocol: '+esc(a.chat_protocol_spec)+'</span></div>'+
      '<div class="status">'+esc(a.status)+'</div>'+
    '</div>').join('');
  box.dataset.done = '1';
}
// -------- Latency sparkline ------------------------------------
let _latHistory = [];
async function pollLatency(){
  try{
    const r = await fetch('/api/latency'); const s = await r.json();
    _latHistory = s.recent_us || [];
    const p99 = s.p99_us || 0;
    const p50 = s.p50_us || 0;
    const el = document.getElementById('lat-val');
    if(el){
      el.textContent = 'P50 '+p50.toFixed(1)+'µs · P99 '+p99.toFixed(1)+'µs · n='+(s.samples||0);
    }
    drawSpark(_latHistory);
  }catch(e){}
}
function drawSpark(vals){
  const c = document.getElementById('latency-sparkline'); if(!c) return;
  const ctx = c.getContext('2d');
  const w = c.width = c.clientWidth * (window.devicePixelRatio||1);
  const h = c.height = 60 * (window.devicePixelRatio||1);
  ctx.clearRect(0,0,w,h);
  if(!vals || !vals.length){
    ctx.fillStyle='#7a7990'; ctx.font='12px system-ui';
    ctx.fillText('Drive /api/triage to populate the sparkline', 12, h/2);
    return;
  }
  const max = Math.max.apply(null, vals) * 1.15 || 1;
  const step = w / Math.max(1, vals.length - 1);
  // 200ms SLA line
  const sla_us = 200 * 1000;
  const sla_y = h - Math.min(h-4, (sla_us/max) * h);
  if(sla_y >= 0 && sla_y <= h){
    ctx.strokeStyle='#d99aa2'; ctx.setLineDash([4,4]); ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(0,sla_y); ctx.lineTo(w,sla_y); ctx.stroke();
    ctx.setLineDash([]);
  }
  ctx.strokeStyle='#2f9d6a'; ctx.lineWidth=2;
  ctx.beginPath();
  vals.forEach((v,i)=>{
    const x = i*step;
    const y = h - (v/max) * h;
    if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
  });
  ctx.stroke();
  ctx.fillStyle='rgba(47,157,106,0.12)';
  ctx.lineTo(w, h); ctx.lineTo(0, h); ctx.closePath(); ctx.fill();
}
setInterval(pollLatency, 800);
// -------- Plain-English trace translator ------------------------
function updatePlainEnglish(evTrace){
  const el = document.getElementById('plain-eng-text'); if(!el) return;
  if(!evTrace || !evTrace.length){ el.textContent='Idle. Drive an incident to see the loop.'; return; }
  const last = evTrace[evTrace.length-1];
  const key = String(last.step||'').toUpperCase();
  const copy = window._COPY;
  if(copy && copy.PLAIN_ENGLISH && copy.PLAIN_ENGLISH[key]){
    el.textContent = copy.PLAIN_ENGLISH[key];
  } else {
    el.textContent = 'Loop step: '+key+' — '+(last.detail||'');
  }
}
// -------- Tamper (visual) --------------------------------------
function doTamper(on){
  window._tampered = !!on;
  document.body.style.boxShadow = on ? 'inset 0 0 0 3px #d99aa2' : '';
  refresh();
}
// -------- Tour engine ------------------------------------------
async function startTour(){
  const copy = await loadCopy();
  window._TOUR = {i: 0, beats: copy.GUIDED_BEATS};
  document.getElementById('tour-overlay').classList.add('on');
  renderBeat();
}
function tourNext(){
  const t = window._TOUR;
  if(!t || !t.beats) return;
  t.i += 1;
  if(t.i >= t.beats.length){ tourClose(); return; }
  renderBeat();
}
function tourClose(){
  document.getElementById('tour-overlay').classList.remove('on');
  window._TOUR = {i: -1};
}
function renderBeat(){
  const t = window._TOUR;
  const b = t.beats[t.i];
  const tgt = document.querySelector(b.target);
  if(!tgt){
    // fall back: skip missing target
    setTimeout(tourNext, 100); return;
  }
  tgt.scrollIntoView({behavior:'smooth', block:'center'});
  setTimeout(()=>{
    const rect = tgt.getBoundingClientRect();
    const pad = 8;
    const spot = document.getElementById('tour-spotlight');
    spot.style.left = (rect.left - pad) + 'px';
    spot.style.top  = (rect.top  - pad) + 'px';
    spot.style.width  = (rect.width  + 2*pad) + 'px';
    spot.style.height = (rect.height + 2*pad) + 'px';
    // caption position: below if room, else above
    const cap = document.getElementById('tour-caption');
    const capW = 440, capH = 200;
    const spaceBelow = window.innerHeight - rect.bottom;
    let capTop, capLeft;
    if(spaceBelow > capH + 20){
      capTop = rect.bottom + 20;
    } else if(rect.top > capH + 20){
      capTop = rect.top - capH - 20;
    } else {
      capTop = Math.max(20, (window.innerHeight - capH) / 2);
    }
    capLeft = Math.max(20, Math.min(window.innerWidth - capW - 20,
      rect.left + rect.width/2 - capW/2));
    cap.style.left = capLeft + 'px';
    cap.style.top  = capTop  + 'px';
    document.getElementById('tour-num').textContent =
      'Beat '+(t.i+1)+' / '+t.beats.length+' · '+esc(b.title);
    document.getElementById('tour-title').textContent = b.title;
    document.getElementById('tour-body').textContent = b.body;
    document.getElementById('btn-tour-next').textContent =
      (t.i === t.beats.length-1) ? 'Finish ✓' : 'Next ▸';
  }, 380);
}
// -------- Boot the showcase pieces ------------------------------
(async function(){
  const copy = await loadCopy();
  renderHumanRunbook(copy);
  renderAgents(copy);
  pollLatency();
})();

function renderGate(g){
  const p = g.preview||{};
  const pre = esc(JSON.stringify(p.pre_state||{}, null, 1));
  const planned = (p.planned||[]).map(
    s=>esc(s.tool)+'('+esc(JSON.stringify(s.args||{}))+')').join('; ');
  return '<div class="gatecard">'+
    '<div class="row"><b>Pending approval — INC-'+esc(g.n)+'</b>'+
      '<span class="badge">'+esc(p.risk_class||'')+'</span></div>'+
    '<div class="muted">You approve exactly this change, with exactly this undo.</div>'+
    '<div class="diff">'+
      '<div><span class="dl">before — pre-state</span><pre>'+pre+'</pre></div>'+
      '<div><span class="dl">planned change</span><pre>'+(planned||'—')+'</pre></div>'+
    '</div>'+
    '<div class="muted">Rollback anchor: <code>'+esc(p.rollback_ref||'—')+'</code></div>'+
    '<div class="muted">Plan hash (tamper anchor): <code>'+
      esc((p.plan_hash||'').slice(0,32))+'…</code></div>'+
    '<div><button class="hero" data-act="gate-approve" data-n="'+esc(g.n)+'">Approve</button>'+
      '<button class="danger" data-act="gate-reject" data-n="'+esc(g.n)+'">Reject</button></div>'+
  '</div>';
}
async function refresh(){
  const st = await (await fetch('/api/state')).json();
  const ev = await (await fetch('/api/events')).json();
  const s = st.status;
  let banner =
    '<span class="pill">principal: '+esc(st.principal)+'</span>'+
    '<span class="pill">memory: '+esc(s.memory)+'</span>'+
    '<span class="pill">sync: '+esc(s.sync)+'</span>'+
    '<span class="pill '+(s.audit_chain==='intact'?'':'bad')+'">audit: '+
      esc(s.audit_chain)+'</span>'+
    '<span class="pill">precedents: '+st.precedents_count+'</span>';
  if(st.robustness){
    banner += '<span class="pill chip">extractor: '+st.robustness.false_fast_paths+'/'+
      st.robustness.total+' false-fast-paths · '+st.robustness.decoys_resisted+'/'+
      st.robustness.decoys_total+' decoys resisted</span>';
  }
  $('#banner').innerHTML = banner;
  window._demoStart = Date.parse(st.demo_started_at);
  const bpct = Math.min(100, 100*st.elapsed_seconds/st.baseline.seconds);
  $('#baseline').innerHTML =
    '<div class="muted">Manual baseline: '+esc(st.baseline.label)+'</div>'+
    '<div class="bar baseline"><span style="width:100%"></span></div>'+
    '<div class="muted">Precedent this run: '+st.elapsed_seconds+'s (seconds, not hours)</div>'+
    '<div class="bar"><span style="width:'+Math.max(1,bpct).toFixed(2)+'%"></span></div>';
  $('#closestrip').textContent = (st.closed_count||0)+
    ' fix'+((st.closed_count===1)?'':'es')+
    ' closed this session — each against the 8h 51m baseline';
  $('#gate').innerHTML = window._gate ? renderGate(window._gate)
    : '<div class="muted">No held approval. Use “Hold &amp; review” on an incident '+
      'to open the real gate.</div>';
  $('#incidents').innerHTML = st.incidents.map(i=>{
    const standing = i.ladder_level==='STANDING';
    const owner = esc(i.denied_owner_team||'restricted team');
    const acc = i.access==='permitted'
      ? '<span class="badge ok">fix permitted</span>'
      : '<span class="badge deny">restricted — owner: '+owner+'</span>';
    const lvl = standing
      ? '<span class="badge standing">Standing Approval</span>'
      : '<span class="badge">'+esc(i.ladder_level_label)+'</span>';
    const ttr = (i.ttr_seconds!=null)
      ? '<span class="badge ttr">resolved in '+i.ttr_seconds+'s</span>' : '';
    return '<div class="inc"><div class="row"><b>'+esc(i.incident_id)+'</b> '+
      '<span class="muted">'+esc(i.service)+' · '+esc(i.status)+'</span></div>'+
      '<div class="row"><span>'+acc+' '+lvl+' '+ttr+'</span></div>'+
      '<div><button data-act="triage" data-id="'+esc(i.incident_id)+'">Triage</button>'+
      '<button class="hero" data-act="hold" data-n="'+esc(nOf(i.incident_id))+'">'+
      'Hold &amp; review</button>'+
      '<button data-act="approve" data-id="'+esc(i.incident_id)+'">Approve (record)</button>'+
      '<button data-act="promote" data-key="'+esc(i.class_key)+'">'+
      'Promote to Standing Approval</button>'+
      '<button class="danger" data-act="revoke" data-key="'+esc(i.class_key)+'">Revoke</button>'+
      '<button data-act="export" data-id="'+esc(i.incident_id)+'">'+
      'Export change record</button></div></div>';
  }).join('');
  if(window._tampered){
    $('#chain').innerHTML = 'chain: <b style="color:#b02436">BROKEN</b> (visual demo — hash mismatch at last row)';
  } else {
    $('#chain').textContent = 'chain: '+ev.audit_chain;
  }
  $('#trace').innerHTML = ev.trace.slice().reverse().map(t=>
    '<div><span class="muted">'+esc((t.ts||'').slice(11,19))+'</span> '+
    '<b>'+esc(t.step)+'</b> '+esc(t.detail)+'</div>').join('');
  $('#audit').innerHTML = ev.audit.map(a=>
    '<div class="audit-row" data-seq="'+a.seq+'"><span class="muted">#'+a.seq+' '+
    esc((a.ts||'').slice(11,19))+'</span> '+
    '<b>'+esc(a.event_type)+'</b> <span class="muted">'+esc(a.actor||'')+'</span>'+
    '<div class="exp">payload: '+esc(a.payload||'')+'</div></div>').join('');
  document.querySelectorAll('.audit-row').forEach(r=>{
    r.addEventListener('click', ()=>r.classList.toggle('open'));
  });
  updatePlainEnglish(ev.trace);
}
function tick(){
  if(window._demoStart){
    const s = Math.max(0,(Date.now()-window._demoStart)/1000);
    $('#stopwatch').textContent = s.toFixed(1)+'s';
  }
}
refresh(); setInterval(refresh, 1500); setInterval(tick, 100);
</script>
</body></html>
"""
