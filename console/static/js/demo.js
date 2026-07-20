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
