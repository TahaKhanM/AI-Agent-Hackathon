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

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from console.demo_state import STATE

app = FastAPI(title="Precedent Console")


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
    return STATE.triage(req.incident_id)


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


# --------------------------------------------------------------------------- #
# The page
# --------------------------------------------------------------------------- #
@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(_PAGE)


_PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>Precedent</title>
<style>
 body{font:14px/1.45 system-ui,sans-serif;margin:0;background:#0f1420;color:#e7ecf3}
 header{padding:14px 20px;background:#161d2b;border-bottom:1px solid #263149;display:flex;
   align-items:center;gap:16px}
 h1{font-size:20px;margin:0;letter-spacing:.5px}
 .banner{font-size:12px;color:#9fb0c9;display:flex;gap:14px;flex-wrap:wrap}
 .pill{padding:2px 8px;border-radius:10px;background:#22304a}
 .pill.bad{background:#5b1f27;color:#ffd7dc}
 main{display:grid;grid-template-columns:1.2fr 1fr;gap:16px;padding:16px 20px}
 section{background:#141b29;border:1px solid #243149;border-radius:10px;padding:14px}
 h2{font-size:13px;text-transform:uppercase;letter-spacing:.6px;color:#8ea3c2;margin:0 0 10px}
 .bar{height:20px;border-radius:5px;background:#26324a;position:relative;margin:6px 0}
 .bar>span{position:absolute;left:0;top:0;bottom:0;border-radius:5px;background:#3ba776}
 .baseline>span{background:#8a6d3b}
 .inc{border:1px solid #243149;border-radius:8px;padding:10px;margin-bottom:10px}
 .inc .row{display:flex;justify-content:space-between;align-items:center;gap:8px}
 .badge{font-size:11px;padding:2px 7px;border-radius:9px;background:#22304a}
 .badge.deny{background:#5b1f27;color:#ffd7dc}
 .badge.ok{background:#1f4a34;color:#c7f4dd}
 .badge.standing{background:#3a2f5b;color:#e2d7ff}
 button{font:12px system-ui;padding:5px 9px;border:1px solid #33507e;background:#1c2942;
   color:#dce7f7;border-radius:6px;cursor:pointer;margin:3px 3px 0 0}
 button:hover{background:#243a5e}
 button.danger{border-color:#7e3340;background:#3a1d24}
 .feed{max-height:280px;overflow:auto;font-family:ui-monospace,monospace;font-size:12px}
 .feed div{padding:3px 0;border-bottom:1px solid #1c2536}
 .muted{color:#7f92ac}
 .flipwrap{margin-top:8px}
 small.note{color:#7f92ac}
 .stopwatch{font:22px ui-monospace,monospace;color:#7fe3b0;margin:2px 0 6px}
 .caveat{font-size:11px;color:#7f92ac;margin-top:4px}
</style></head>
<body>
<header>
  <h1>⟡ Precedent</h1>
  <div class="banner" id="banner"></div>
</header>
<main>
  <div>
    <section>
      <h2>Baseline vs Precedent</h2>
      <div class="stopwatch">Precedent elapsed: <span id="stopwatch">0.0s</span></div>
      <div id="baseline"></div>
      <div class="caveat">Manual baseline 8h 51m = MetricNet business-hours MTTR
        (industry benchmark, labelled) — not measured from this run.</div>
    </section>
    <section>
      <h2>Incident feed</h2>
      <div id="incidents"></div>
    </section>
    <section>
      <h2>Permission source (local-demo)</h2>
      <div class="flipwrap">
        <button onclick="flip()">Flip Jira permission (local-demo)</button>
        <div id="flipstatus" class="muted"></div>
        <small class="note">Simulates a Jira issue-security change in local mode —
          tightens the scheduling ticket to also require Rights Ops, so a
          scheduling-only fix goes dark. Reversible.</small>
      </div>
      <div style="margin-top:8px"><button class="danger" onclick="reset()">Reset demo</button></div>
    </section>
  </div>
  <div>
    <section>
      <h2>Trace</h2>
      <div class="feed" id="trace"></div>
    </section>
    <section>
      <h2>Audit &amp; memory (hash-chained)</h2>
      <div id="chain" class="muted"></div>
      <div class="feed" id="audit"></div>
    </section>
  </div>
</main>
<script>
const $ = s => document.querySelector(s);
async function post(u,b){await fetch(u,{method:'POST',headers:{'Content-Type':'application/json'},
  body:JSON.stringify(b||{})});await refresh();}
async function triage(id){await post('/api/triage',{incident_id:id});}
async function approve(id){await post('/api/approve',{incident_id:id});}
async function promote(k){await post('/api/promote',{class_key:k});}
async function revoke(k){await post('/api/revoke',{class_key:k});}
async function flip(){await post('/api/permission-flip',{});}
async function reset(){await post('/api/demo/reset',{});}
function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
async function refresh(){
  const st = await (await fetch('/api/state')).json();
  const ev = await (await fetch('/api/events')).json();
  const s = st.status;
  $('#banner').innerHTML =
    `<span class="pill">principal: ${esc(st.principal)}</span>`+
    `<span class="pill">memory: ${esc(s.memory)}</span>`+
    `<span class="pill">sync: ${esc(s.sync)}</span>`+
    `<span class="pill ${s.audit_chain==='intact'?'':'bad'}">audit: ${esc(s.audit_chain)}</span>`+
    `<span class="pill">precedents: ${st.precedents_count}</span>`;
  window._demoStart = Date.parse(st.demo_started_at);
  const bpct = Math.min(100, 100*st.elapsed_seconds/st.baseline.seconds);
  $('#baseline').innerHTML =
    `<div class="muted">Manual baseline: ${esc(st.baseline.label)}</div>`+
    `<div class="bar baseline"><span style="width:100%"></span></div>`+
    `<div class="muted">Precedent this run: ${st.elapsed_seconds}s (seconds, not hours)</div>`+
    `<div class="bar"><span style="width:${Math.max(1,bpct).toFixed(2)}%"></span></div>`;
  $('#incidents').innerHTML = st.incidents.map(i=>{
    const standing = i.ladder_level==='STANDING';
    const owner = esc(i.denied_owner_team||'restricted team');
    const acc = i.access==='permitted'
      ? '<span class="badge ok">fix permitted</span>'
      : `<span class="badge deny">restricted — owner: ${owner}</span>`;
    const lvl = standing
      ? '<span class="badge standing">Standing Approval</span>'
      : `<span class="badge">${esc(i.ladder_level_label)}</span>`;
    return `<div class="inc"><div class="row"><b>${esc(i.incident_id)}</b> `+
      `<span class="muted">${esc(i.service)} · ${esc(i.status)}</span></div>`+
      `<div class="row"><span>${acc} ${lvl}</span></div>`+
      `<div><button onclick="triage('${i.incident_id}')">Triage</button>`+
      `<button onclick="approve('${i.incident_id}')">Approve</button>`+
      `<button onclick="promote('${esc(i.class_key)}')">Promote to Standing Approval</button>`+
      `<button class="danger" onclick="revoke('${esc(i.class_key)}')">Revoke</button></div></div>`;
  }).join('');
  $('#chain').textContent = 'chain: '+ev.audit_chain;
  $('#trace').innerHTML = ev.trace.slice().reverse().map(t=>
    `<div><span class="muted">${esc((t.ts||'').slice(11,19))}</span> `+
    `<b>${esc(t.step)}</b> ${esc(t.detail)}</div>`).join('');
  $('#audit').innerHTML = ev.audit.map(a=>
    `<div><span class="muted">#${a.seq} ${esc((a.ts||'').slice(11,19))}</span> `+
    `<b>${esc(a.event_type)}</b> <span class="muted">${esc(a.actor||'')}</span></div>`).join('');
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
