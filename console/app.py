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
from fastapi.responses import HTMLResponse, PlainTextResponse
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
 body{font:14px/1.45 system-ui,sans-serif;margin:0;background:#0f1420;color:#e7ecf3}
 header{padding:14px 20px;background:#161d2b;border-bottom:1px solid #263149;display:flex;
   align-items:center;gap:16px;flex-wrap:wrap}
 h1{font-size:20px;margin:0;letter-spacing:.5px}
 .banner{font-size:12px;color:#9fb0c9;display:flex;gap:10px;flex-wrap:wrap}
 .pill{padding:2px 8px;border-radius:10px;background:#22304a}
 .pill.bad{background:#5b1f27;color:#ffd7dc}
 .pill.chip{background:#1f3a2c;color:#c7f4dd}
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
 .badge.ttr{background:#1f3a2c;color:#a6f0c9}
 button{font:12px system-ui;padding:5px 9px;border:1px solid #33507e;background:#1c2942;
   color:#dce7f7;border-radius:6px;cursor:pointer;margin:3px 3px 0 0}
 button:hover{background:#243a5e}
 button.danger{border-color:#7e3340;background:#3a1d24}
 button.hero{border-color:#2f7d55;background:#1c3a2b}
 .feed{max-height:280px;overflow:auto;font-family:ui-monospace,monospace;font-size:12px}
 .feed div{padding:3px 0;border-bottom:1px solid #1c2536}
 .muted{color:#7f92ac}
 small.note{color:#7f92ac}
 .stopwatch{font:22px ui-monospace,monospace;color:#7fe3b0;margin:2px 0 6px}
 .caveat{font-size:11px;color:#7f92ac;margin-top:4px}
 .strip{font-size:12px;color:#a6f0c9;margin-top:6px}
 .gatecard{border:1px solid #2f7d55;border-radius:8px;padding:12px;background:#12241b}
 .diff{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:8px 0}
 .diff pre{background:#0d1622;border:1px solid #223047;border-radius:6px;padding:8px;
   font-size:11px;white-space:pre-wrap;word-break:break-word;max-height:160px;
   overflow:auto;margin:2px 0}
 .dl{font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:#8ea3c2}
 code{background:#0d1622;padding:1px 5px;border-radius:4px;font-size:11px}
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
});
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
  $('#chain').textContent = 'chain: '+ev.audit_chain;
  $('#trace').innerHTML = ev.trace.slice().reverse().map(t=>
    '<div><span class="muted">'+esc((t.ts||'').slice(11,19))+'</span> '+
    '<b>'+esc(t.step)+'</b> '+esc(t.detail)+'</div>').join('');
  $('#audit').innerHTML = ev.audit.map(a=>
    '<div><span class="muted">#'+a.seq+' '+esc((a.ts||'').slice(11,19))+'</span> '+
    '<b>'+esc(a.event_type)+'</b> <span class="muted">'+esc(a.actor||'')+'</span></div>').join('');
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
