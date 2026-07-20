/* WP-CONSOLE — the notarised case-file console.
 *
 * Kernel-free client. Every datum comes over HTTP from the read/gate endpoints; the on-page
 * verifier is PURE in-page arithmetic (a self-contained SHA-256 + the same canonical-JSON formula
 * and chain walk as verify_pack.py) — NO network, NO model — so an auditor can confirm the sealed
 * bytes in their own browser with the Wi-Fi off. Approvals also land in Slack (P1); this is the record.
 */
'use strict';
(function () {
  // --------------------------------------------------------------------- utils
  const $ = (id) => document.getElementById(id);
  const cls = (n, c) => { const e = document.createElement(n); if (c) e.className = c; return e; };
  const txt = (n, c, t) => { const e = cls(n, c); if (t != null) e.textContent = t; return e; };
  async function jget(p) { const r = await fetch(p); return { status: r.status, body: await r.json() }; }
  async function jpost(p, b) {
    const r = await fetch(p, { method: 'POST', headers: { 'content-type': 'application/json' },
      body: b == null ? null : JSON.stringify(b) });
    let body = null; try { body = await r.json(); } catch (e) { body = {}; }
    return { status: r.status, body };
  }
  const short = (h, n) => (h ? String(h).slice(0, n || 12) : '');
  // a two-column key/value table (skips undefined keys; null renders as an em-dash)
  function kv(pairs) {
    const t = cls('table', 'kv');
    pairs.forEach((p) => {
      if (p[1] === undefined) return;
      const tr = cls('tr');
      tr.appendChild(txt('th', null, p[0]));
      tr.appendChild(txt('td', null, p[1] == null ? '—' : String(p[1])));
      t.appendChild(tr);
    });
    return t;
  }

  // --------------------------------------------------- pure SHA-256 (stdlib-free)
  // A compact, self-contained SHA-256 over UTF-8 bytes. No Web Crypto dependency, so the verifier
  // runs in ANY context (matches verify_pack.py's stdlib-only, air-gapped ethos).
  const SHA = (function () {
    const K = new Uint32Array([
      0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
      0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
      0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
      0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
      0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
      0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
      0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
      0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2]);
    const rotr = (x, n) => (x >>> n) | (x << (32 - n));
    function bytes(str) { return new TextEncoder().encode(str); }
    function hex(data) {
      const H = new Uint32Array([0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]);
      const l = data.length; const bitLen = l * 8;
      const withOne = l + 1; const k = (56 - (withOne % 64) + 64) % 64;
      const total = withOne + k + 8; const buf = new Uint8Array(total);
      buf.set(data); buf[l] = 0x80;
      // 64-bit big-endian length (high 32 bits are 0 for our sizes)
      const hi = Math.floor(bitLen / 0x100000000), lo = bitLen >>> 0;
      buf[total - 8] = (hi >>> 24) & 0xff; buf[total - 7] = (hi >>> 16) & 0xff;
      buf[total - 6] = (hi >>> 8) & 0xff; buf[total - 5] = hi & 0xff;
      buf[total - 4] = (lo >>> 24) & 0xff; buf[total - 3] = (lo >>> 16) & 0xff;
      buf[total - 2] = (lo >>> 8) & 0xff; buf[total - 1] = lo & 0xff;
      const w = new Uint32Array(64);
      for (let i = 0; i < total; i += 64) {
        for (let t = 0; t < 16; t++) {
          const j = i + t * 4;
          w[t] = (buf[j] << 24) | (buf[j + 1] << 16) | (buf[j + 2] << 8) | buf[j + 3];
        }
        for (let t = 16; t < 64; t++) {
          const s0 = rotr(w[t-15],7) ^ rotr(w[t-15],18) ^ (w[t-15] >>> 3);
          const s1 = rotr(w[t-2],17) ^ rotr(w[t-2],19) ^ (w[t-2] >>> 10);
          w[t] = (w[t-16] + s0 + w[t-7] + s1) >>> 0;
        }
        let a=H[0],b=H[1],c=H[2],d=H[3],e=H[4],f=H[5],g=H[6],h=H[7];
        for (let t = 0; t < 64; t++) {
          const S1 = rotr(e,6) ^ rotr(e,11) ^ rotr(e,25);
          const ch = (e & f) ^ (~e & g);
          const t1 = (h + S1 + ch + K[t] + w[t]) >>> 0;
          const S0 = rotr(a,2) ^ rotr(a,13) ^ rotr(a,22);
          const maj = (a & b) ^ (a & c) ^ (b & c);
          const t2 = (S0 + maj) >>> 0;
          h=g; g=f; f=e; e=(d + t1) >>> 0; d=c; c=b; b=a; a=(t1 + t2) >>> 0;
        }
        H[0]=(H[0]+a)>>>0; H[1]=(H[1]+b)>>>0; H[2]=(H[2]+c)>>>0; H[3]=(H[3]+d)>>>0;
        H[4]=(H[4]+e)>>>0; H[5]=(H[5]+f)>>>0; H[6]=(H[6]+g)>>>0; H[7]=(H[7]+h)>>>0;
      }
      let out = '';
      for (let i = 0; i < 8; i++) out += ('00000000' + H[i].toString(16)).slice(-8);
      return out;
    }
    return { hexOf: (str) => hex(bytes(str)) };
  })();

  // canonical JSON — IDENTICAL formula to precedent_pack.canonical_json / verify_pack.canonical_json
  // (sorted keys, compact separators, ensure_ascii=False). JSON.stringify's string escaping matches
  // Python's for the pack's data (hashes, ISO timestamps, ASCII text, class keys).
  function canon(o) {
    if (o === null) return 'null';
    const t = typeof o;
    if (t === 'number') return String(o);
    if (t === 'boolean') return o ? 'true' : 'false';
    if (t === 'string') return JSON.stringify(o);
    if (Array.isArray(o)) return '[' + o.map(canon).join(',') + ']';
    const keys = Object.keys(o).sort();
    return '{' + keys.map((k) => JSON.stringify(k) + ':' + canon(o[k])).join(',') + '}';
  }
  const GENESIS = '0'.repeat(64);
  const M_ALGO = 'sha256';
  const M_SCOPE = "canonical_json(pack) excluding the 'manifest' field";

  // Byte-identical mirror of verify_pack.py: manifest digest + metadata, chain from GENESIS, anchors.
  function verifyInPage(pack) {
    const errors = [], steps = [];
    const man = pack.manifest;
    let manifestOk = true;
    if (!man || typeof man !== 'object' || !('digest' in man)) {
      errors.push('missing or malformed manifest'); manifestOk = false;
    } else {
      const body = {}; for (const k in pack) if (k !== 'manifest') body[k] = pack[k];
      const recomputed = SHA.hexOf(canon(body));
      if (recomputed !== man.digest) { errors.push('manifest digest mismatch — the pack bytes were altered'); manifestOk = false; }
      if (man.algo !== M_ALGO) { errors.push("manifest metadata altered — 'algo'"); manifestOk = false; }
      if (man.scope !== M_SCOPE) { errors.push("manifest metadata altered — 'scope'"); manifestOk = false; }
      if (man.secret_key !== null) { errors.push("manifest metadata altered — 'secret_key' must be null"); manifestOk = false; }
      if (man.self_authenticating !== true) { errors.push("manifest metadata altered — 'self_authenticating'"); manifestOk = false; }
    }
    steps.push({ ok: manifestOk, label: 'sha256 manifest over canonical bytes (ex-manifest)' });

    const cp = pack.chain_proof || {};
    const rows = cp.rows || [];
    let chainOk = rows.length > 0, prev = GENESIS;
    if (cp.genesis_hash !== GENESIS) { errors.push('genesis link is not canonical'); chainOk = false; }
    for (let i = 0; i < rows.length; i++) {
      const r = rows[i];
      if (r.prev_hash !== prev) { errors.push('chain break at seq ' + r.seq); chainOk = false; }
      const material = (r.prev_hash || '') + '|' + (r.ts || '') + '|' + (r.actor || '') + '|' + (r.event_type || '') + '|' + (r.payload || '');
      if (SHA.hexOf(material) !== r.hash) { errors.push('row hash mismatch at seq ' + r.seq); chainOk = false; }
      prev = r.hash;
    }
    steps.push({ ok: chainOk, label: 'recompute ' + rows.length + ' rows from GENESIS (prev-link + row hash)' });

    let anchorsOk = true;
    if (cp.expected_len !== rows.length) { errors.push('length anchor mismatch'); anchorsOk = false; }
    const tail = rows.length ? rows[rows.length - 1].hash : GENESIS;
    if (cp.expected_tail_hash !== tail) { errors.push('tail-hash anchor mismatch'); anchorsOk = false; }
    steps.push({ ok: anchorsOk, label: 'length + tail-hash anchors (truncation guard)' });

    return { ok: errors.length === 0, errors: errors, steps: steps, tail: tail, len: rows.length };
  }

  // --------------------------------------------------------------------- state
  const S = { current: null, incidents: {}, caseFiles: [], pending: {}, ladder: [], caseCache: {}, loadToken: 0 };

  // ------------------------------------------------------------------- boot
  async function boot() {
    wireNoLLM();
    await Promise.all([refreshKernel(), refreshModelCalls(), refreshCaseFiles(), loadIncidents()]);
    pollModelCalls();
  }

  async function loadIncidents() {
    const r = await jget('/api/incidents');
    (r.body.incidents || []).forEach((i) => { S.incidents[i.incident_id] = i; });
  }

  async function refreshKernel() {
    const r = await jget('/api/kernel-hash');
    const kh = r.body.kernel_hash || '';
    $('kh').textContent = short(kh, 12);
    const live = $('fz-live'); const eq = $('fz-eq');
    live.textContent = 'live ' + short(kh, 12);
    const match = r.body.matches_manifest;
    eq.textContent = match ? '=' : '≠'; eq.className = 'fz-eq ' + (match ? 'ok' : 'bad');
    $('chip-kernel').classList.toggle('ok', !!match);
  }

  async function refreshModelCalls() {
    const r = await jget('/api/model-calls');
    const n = r.body.model_calls != null ? r.body.model_calls : 0;
    $('mc').textContent = n;
    document.querySelectorAll('.livemc').forEach((e) => { e.textContent = n; });
  }
  function pollModelCalls() { setInterval(refreshModelCalls, 4000); }

  // ------------------------------------------------------------------- picker
  async function refreshCaseFiles() {
    const r = await jget('/api/case-files');
    S.caseFiles = r.body.case_files || [];
    renderPicker();
  }
  function renderPicker() {
    const p = $('picker'); p.textContent = '';
    S.caseFiles.forEach((cf) => {
      const b = cls('button', 'pk-inc'); b.type = 'button';
      b.setAttribute('data-inc', cf.incident_id);
      if (cf.incident_id === S.current) b.classList.add('sel');
      const dot = cls('span', 'st' + (cf.has_record ? (cf.verdict === 'deny' ? ' deny' : ' filed') : ''));
      b.appendChild(dot);
      b.appendChild(txt('span', null, cf.incident_id));
      const st = txt('span', 'rtok', cf.has_record ? (cf.verdict || '') : 'not filed');
      st.style.opacity = '.7'; st.style.fontSize = '10px'; b.appendChild(st);
      b.addEventListener('click', () => selectIncident(cf.incident_id));
      p.appendChild(b);
    });
  }

  function selectIncident(id) {
    S.current = id;
    renderPicker();
    loadCaseFile(id);
  }

  // --------------------------------------------------------------- case file
  async function loadCaseFile(id) {
    const token = ++S.loadToken;                      // guard: only the latest load may paint
    const r = await jget('/api/case-file/' + id);
    if (token !== S.loadToken) return;                // a newer selection superseded this one
    const rec = r.body; S.caseCache[id] = rec;
    if (rec.has_record) { renderSpine(rec); loadPackPanel(id, rec, token); }
    else { renderDrivePrompt(id); resetPackPanel(); }
    refreshLadder(rec.decision ? rec.decision.class_key : null);
    setVerdictChip(rec);
  }

  function setVerdictChip(rec) {
    const c = $('chip-verdict'); const v = rec.decision && rec.decision.decision;
    if (!v) { c.textContent = (S.current || '') + ' · not filed'; c.className = 'chip'; return; }
    const map = { 'allow-standing': 'ALLOW · STANDING', 'needs-approval': 'NEEDS APPROVAL', 'deny': 'DENIED' };
    c.textContent = map[v] || v; c.className = 'chip ok';
  }

  function renderDrivePrompt(id) {
    const cf = $('casefile'); cf.textContent = '';
    const box = cls('div', 'cf-empty');
    box.appendChild(txt('p', null, id + ' has not been filed yet. Drive it through the deterministic gate — '
      + 'the model narrates, the policy engine disposes — and its notarised record appears here.'));
    const b = txt('button', null, 'Drive ' + id + ' through the gate ▸'); b.type = 'button';
    b.addEventListener('click', () => driveIncident(id));
    box.appendChild(b);
    // Fault-injection affordance for the publisher incident (auto-rollback + demotion demo).
    if (id === 'INC-1') {
      const f = txt('button', 'ghost warn', 'Arm a verification failure first (fault-injection)'); f.type = 'button';
      f.style.marginLeft = '8px';
      f.addEventListener('click', async () => {
        const rr = await jpost('/api/sim/arm-flake', null);
        f.textContent = rr.body.ok ? 'Flake armed — the next run will roll back' : 'could not arm';
        f.disabled = true;
      });
      box.appendChild(f);
    }
    cf.appendChild(box);
  }

  async function driveIncident(id) {
    const body = S.incidents[id];
    if (!body || !body.available) return;
    const pb = { incident_id: body.incident_id, principal: 'scheduling-ops', raw_text: body.raw_text,
      source: 'sim', observed_at: body.observed_at, structured: body.structured };
    const r = await jpost('/v1/gate/propose', pb);
    const d = r.body;
    if (d.decision === 'allow-standing') {
      await jpost('/v1/gate/outcome', { ref: d.ref });               // Standing fast-path: no human
    } else if (d.decision === 'needs-approval') {
      S.pending[id] = { ref: d.ref, plan_hash: d.plan_hash, proposer: 'scheduling-ops' };  // hold for approve
    } // deny: the denial is itself a complete record
    await refreshCaseFiles();
    selectIncident(id);
  }

  async function approve(id) {
    const held = S.pending[id]; if (!held) return;
    // Four-eyes: the proposer (scheduling-ops) may never approve; a DISTINCT registered approver signs.
    await jpost('/v1/gate/outcome', { ref: held.ref, decision: 'approve', approver_principal: 'ops-lead' });
    delete S.pending[id];
    await refreshCaseFiles(); selectIncident(id);
  }
  async function reject(id) {
    const held = S.pending[id]; if (!held) return;
    await jpost('/v1/gate/outcome', { ref: held.ref, decision: 'reject', approver_principal: 'ops-lead' });
    delete S.pending[id];
    await refreshCaseFiles(); selectIncident(id);
  }

  // ---------------------------------------------------------- render the spine
  function renderSpine(rec) {
    const cf = $('casefile'); cf.textContent = '';
    const inc = rec.incident || {}, dec = rec.decision || {}, ver = rec.verification || {};
    const st = inc.structured || {}, cp = rec.chain_proof || {}, sn = rec.safety_net;

    // masthead
    const mast = cls('div', 'cf-mast');
    const top = cls('div', 'm-top');
    const left = cls('div');
    const h = txt('h2', null, inc.incident_id || S.current); left.appendChild(h);
    const sub = cls('div', 'm-sub');
    sub.appendChild(txt('span', null, 'paged via ' + (inc.source || '—') + ' · T0 '));
    sub.appendChild(txt('code', null, inc.observed_at || '—'));
    left.appendChild(sub);
    top.appendChild(left);
    const right = cls('div');
    const vmap = { 'allow-standing': ['ALLOW · STANDING', 'allow'], 'needs-approval': ['NEEDS APPROVAL', 'approval'], 'deny': ['DENIED', 'deny'] };
    const vd = vmap[dec.decision] || [dec.decision || '—', 'approval'];
    right.appendChild(txt('span', 'verdict ' + vd[1], vd[0]));
    const sig = cls('div', 'sigil');
    sig.appendChild(txt('div', 'sg-k', 'sealed · digest'));
    sig.appendChild(txt('div', 'sg-v', short(rec.manifest_digest, 16) + '…'));
    sig.appendChild(txt('div', 'sg-cap', 'self-authenticating — secret_key: null'));
    right.appendChild(sig);
    top.appendChild(right);
    mast.appendChild(top);
    cf.appendChild(mast);
    if (rec.disclaimer) cf.appendChild(txt('div', 'cf-disc', rec.disclaimer));

    // beads (chain rail) — one per incident audit seq
    renderChainRail(cp);

    const stages = cls('div', 'stages');
    const noLLM = !!rec.no_llm_badge_lit;

    // Stage 1 — typed proposal
    stages.appendChild(stageRow('1', 'Typed proposal', 'the model narrates; deterministic policy disposes', (b) => {
      const g = cls('div', 'twocol');
      const q = cls('div');
      q.appendChild(txt('span', 'st-op', 'ticket, as paged (subordinate)'));
      q.appendChild(txt('div', 'rawquote', '“' + (inc.raw_text || '—') + '”'));
      g.appendChild(q);
      const card = cls('div', 'typedcard');
      card.appendChild(txt('span', 'tc-k', 'authoritative typed extraction'));
      card.appendChild(kv([['service', st.service], ['error_code', st.error_code],
        ['target_object_type', st.target_object_type], ['object_id', st.object_id]]));
      g.appendChild(card);
      b.appendChild(g);
    }, [tchip('deterministic extractor', 'precedent/extractor.class_key_of', 'llm_proposed never builds an executable plan')]));

    // Stage 2 — deterministic decision (+ No-LLM badge)
    stages.appendChild(stageRow('2', 'Deterministic decision', 'policy engine + ladder — no model in this decision', (b) => {
      if (dec.class_key) {
        const f = cls('div');
        f.appendChild(txt('span', 'st-op', 'class_key = sha256(service|error_code|target_object_type)'));
        f.appendChild(txt('div', 'formula', dec.class_key));
        b.appendChild(f);
      }
      b.appendChild(kv([['risk_class', dec.risk_class], ['policy_rule_id', dec.policy_rule_id],
        ['ladder_level', dec.ladder_level], ['policy_pack_version', rec.policy_pack_version],
        ['plan_hash', dec.plan_hash ? short(dec.plan_hash, 24) + '…' : '(none — no plan built)']]));
      if (dec.decision === 'deny') {
        b.appendChild(txt('div', 'st-op', 'DENIED — disclosing count + owning team ONLY, never hidden content'));
        b.appendChild(kv([['reason', dec.reason], ['denied_count', dec.denied_count],
          ['denied_owner_team', dec.denied_owner_team]]));
      }
      if (noLLM) {
        const badge = txt('button', 'badge noll', 'No LLM in this decision'); badge.type = 'button';
        badge.title = 'spy.n==0 AND venice.model_call_count()==0 — activate the header badge for the proof refs';
        badge.addEventListener('click', () => toggleNoLLM(true));
        b.appendChild(badge);
      }
    }, [
      tchip('No LLM in THIS decision', 'tests/test_gate_api.py::test_standing_allow_fast_path_is_zero_llm', 'spy.n==0 AND model_call_count()==0'),
      tchip('class_key formula', 'precedent/extractor.class_key_of', 'field equality, never similarity'),
      tchip('plan_hash tamper-check', 'precedent/orchestrator._plan_hash', 'same hash flows event→plan→approval→result'),
    ]));

    // Stage 3 — retrieved precedent & provenance
    const prov = rec.retrieved_precedent || {};
    stages.appendChild(stageRow('3', 'Retrieved precedent & provenance', 'the documented fix from the org\'s own knowledge', (b) => {
      const rule = prov.policy_rule;
      if (rule) b.appendChild(kv([['policy_rule_id', rule.policy_rule_id], ['action_type', rule.action_type],
        ['risk_class', rule.risk_class], ['ladder_ceiling', rule.ladder_ceiling],
        ['lineage_refs', (rule.lineage_refs || []).join(', ') || '(none)']]));
      const srcs = prov.lineage_sources || [];
      if (srcs.length) {
        const t = cls('table', 'txtable');
        t.innerHTML = '<tr><th>source</th><th>present</th><th>acl_ver</th><th>revoked</th><th>restricted</th></tr>';
        srcs.forEach((s) => {
          const tr = cls('tr');
          const flagged = s.revoked || !s.present;
          tr.innerHTML = '<td>' + esc(s.external_ref) + '</td><td>' + esc(s.present) + '</td><td>'
            + esc(s.acl_version == null ? '—' : s.acl_version) + '</td><td class="' + (s.revoked ? 'hold' : '') + '">'
            + esc(!!s.revoked) + '</td><td>' + esc(!!s.is_restricted) + '</td>';
          if (flagged) tr.style.background = 'var(--oxblood-bg)';
          t.appendChild(tr);
        });
        b.appendChild(t);
      }
      const recs = prov.memorised_records || [];
      recs.forEach((mr) => {
        b.appendChild(kv([['record_id', mr.record_id], ['fingerprint', mr.fingerprint],
          ['fix', (mr.body || {}).fix]]));
      });
      if (!rule && !srcs.length) b.appendChild(txt('p', 'muted', 'No documented precedent was accessible (fail-closed).'));
    }, [tchip('fail-closed retrieval', 'precedent_memory/retrieve.py', 'stale/revoked ⇒ denied, never widened'),
        tchip('policy inverse exists', 'make policy-lint', 'every executable class declares a true inverse + probe')]));

    // Stage 4 — SAFETY NET ARMED (pivotal, rendered ABOVE stage 5)
    stages.appendChild(stageRow('4', 'Safety net armed — rollback prepared BEFORE execution',
      'screenshot prod, write the undo, THEN run it', (b) => {
        if (!sn) { b.appendChild(txt('p', 'muted', 'No plan was built — nothing to arm (a denial is a complete record).')); return; }
        b.appendChild(kv([['pre_state_snapshot_ref', sn.pre_state_snapshot_ref],
          ['inverse.tool', sn.inverse.tool],
          ['inverse.target', sn.inverse.target.service + '/' + sn.inverse.target.object_type + '/' + sn.inverse.target.object_id],
          ['plan_hash', short(sn.plan_hash, 24) + '…']]));
        const hm = cls('div', 'hashmatch');
        if (sn.plan_hash_matches_execution === true) {
          hm.appendChild(txt('span', 'ok', '✓ armed plan_hash byte-matches the executed plan_hash'));
        } else if (sn.plan_hash_matches_execution === false) {
          hm.appendChild(txt('span', 'bad', '✗ armed plan_hash ≠ executed plan_hash — tamper'));
        } else {
          hm.appendChild(txt('span', null, 'armed — not yet executed (the undo exists before any typed call runs)'));
        }
        b.appendChild(hm);
      }, [tchip('rollback before execute', 'precedent/orchestrator.prepare()', 'snapshot captured before commit_execution; empty-snapshot ⇒ escalate'),
          tchip('plan_hash binds', 'precedent/orchestrator._plan_hash', 'the approved hash must equal the run hash')], true));

    // Stage 5 — typed execution transcript (the chain rows)
    const tx = rec.execution_transcript || [];
    stages.appendChild(stageRow('5', 'Typed execution transcript', 'typed tool calls only, never shell', (b) => {
      if (!tx.length) { b.appendChild(txt('p', 'muted', 'No execution yet — the record is armed and awaiting the approve.')); return; }
      const t = cls('table', 'txtable');
      t.innerHTML = '<tr><th>seq</th><th>ts</th><th>actor</th><th>event</th><th>detail</th></tr>';
      tx.forEach((e) => {
        const tr = cls('tr', 'pick'); tr.setAttribute('data-seq', e.seq);
        const det = Object.assign({}, e.payload || {}); delete det.incident_id;
        tr.innerHTML = '<td>' + esc(e.seq) + '</td><td>' + esc((e.ts || '').slice(11, 19)) + '</td><td>'
          + esc(e.actor) + '</td><td class="ev"><code>' + esc(e.event_type) + '</code></td><td class="det">'
          + esc(canon(det)) + '</td>';
        tr.addEventListener('click', () => selectSeq(e.seq));
        t.appendChild(tr);
      });
      b.appendChild(t);
    }, [tchip('typed tools, never shell', 'precedent/tools.py SimTools', 'execute/verify/restore — a closed vocabulary')]));

    // Stage 6 — verification (+ approve/reject controls if pending)
    stages.appendChild(stageRow('6', 'Verification', 'deterministic probe — pass or hold', (b) => {
      const outcome = ver.outcome;
      const line = cls('div');
      if (ver.verified) line.appendChild(txt('span', 'pass', '✓ verified — post-state healthy (' + (outcome || 'resolved') + ')'));
      else if (outcome === 'rolled_back') line.appendChild(txt('span', 'hold', '↺ verification failed — pre-state snapshot restored (rolled_back)'));
      else if (outcome === 'rollback_failed') line.appendChild(txt('span', 'hold', '‼ rollback failed — escalated with the snapshot'));
      else if (dec.decision === 'needs-approval') line.appendChild(txt('span', null, 'awaiting a four-eyes approval before any execution'));
      else line.appendChild(txt('span', null, outcome || 'no execution'));
      b.appendChild(line);
      // Pending approval controls (keyboard-operable buttons).
      if (dec.decision === 'needs-approval' && S.pending[S.current]) {
        const bar = cls('div', 'ladderacts');
        const ap = txt('button', null, 'Approve (four-eyes, sign as ops-lead)'); ap.type = 'button';
        ap.setAttribute('data-act', 'approve');
        ap.addEventListener('click', () => approve(S.current));
        const rj = txt('button', 'ghost warn', 'Reject'); rj.type = 'button';
        rj.setAttribute('data-act', 'reject');
        rj.addEventListener('click', () => reject(S.current));
        bar.appendChild(ap); bar.appendChild(rj);
        b.appendChild(bar);
        b.appendChild(txt('p', 'actnote', 'The proposer (scheduling-ops) cannot approve its own proposal — the gate rejects a self-approval.'));
      }
    }, [tchip('fail-closed direction', 'gate/models.py GateInfo.failure_direction', 'an expired or absent ref is a non-action'),
        tchip('degraded cap', 'precedent/policy.py assess() RULE 2', 'uncertain freshness forces the ladder to L1')]));

    // Stage 7 — rollback record (only if present)
    if (rec.rollback) {
      stages.appendChild(stageRow('7', 'Rollback record', 'ties back to the Stage-4 snapshot', (b) => {
        b.appendChild(kv([['kind', rec.rollback.kind], ['detail', rec.rollback.detail],
          ['snapshot_ref', rec.rollback.snapshot_ref], ['plan_hash', rec.rollback.plan_hash ? short(rec.rollback.plan_hash, 24) + '…' : null]]));
      }, [tchip('restore is typed', 'precedent/tools.py SimTools.restore', 'the pre-state snapshot, replayed')]));
    }

    // Stage 8 — hash-chain proof
    stages.appendChild(stageRow('8', 'Hash-chain proof', 'the notary seal — recomputable from GENESIS', (b) => {
      b.appendChild(kv([['genesis_hash', short(cp.genesis_hash, 16) + '…'],
        ['construction', cp.hash_construction], ['expected_len', cp.expected_len],
        ['expected_tail_hash', short(cp.expected_tail_hash, 20) + '…'],
        ['incident_row_seqs', (cp.incident_row_seqs || []).join(', ')]]));
    }, [tchip('offline verifier', 'verify_pack.py', 'stdlib-only; non-zero exit on any tampered byte'),
        tchip('row hash', 'precedent_pack/builder._row_hash', 'sha256(prev|ts|actor|event_type|payload)')]));

    cf.appendChild(stages);
    // The tail anchor caption under the rail
    const tail = $('chainrail').querySelector('.tail');
    if (tail) tail.textContent = 'tail ' + short(cp.expected_tail_hash, 10);
  }

  function stageRow(n, title, op, fill, chips, pivotal) {
    const row = cls('div', 'stage-row');
    const main = cls('div', 'stage-main' + (pivotal ? ' pivotal' : ''));
    const hh = cls('div', 'st-h');
    hh.appendChild(txt('span', 'st-n' + (pivotal ? ' pivotal' : ''), n));
    hh.appendChild(txt('span', 'st-t', title));
    main.appendChild(hh);
    if (op) main.appendChild(txt('div', 'st-op', op));
    const body = cls('div', 'st-body'); fill(body); main.appendChild(body);
    row.appendChild(main);
    const td = cls('div', 'teardown');
    td.appendChild(txt('span', 'td-k', 'disproof'));
    (chips || []).forEach((c) => td.appendChild(c));
    row.appendChild(td);
    return row;
  }
  function tchip(label, ref, note) {
    const c = cls('div', 'tdchip');
    c.appendChild(txt('b', null, label));
    const code = txt('code', null, ref); code.style.display = 'block'; c.appendChild(code);
    if (note) c.appendChild(txt('span', null, note));
    return c;
  }

  function renderChainRail(cp) {
    const rail = $('chainrail'); rail.textContent = '';
    const seqs = cp.incident_row_seqs || [];
    seqs.forEach((sq, i) => {
      const bead = cls('div', 'bead');
      const dot = cls('div', 'dot inc'); dot.setAttribute('data-seq', sq);
      dot.title = 'audit seq ' + sq;
      dot.addEventListener('click', () => selectSeq(sq));
      bead.appendChild(dot);
      if (i < seqs.length - 1) bead.appendChild(cls('div', 'link'));
      rail.appendChild(bead);
    });
    rail.appendChild(txt('div', 'tail', ''));
  }

  // Primary interaction: the readable timeline IS the re-derived chain — click a row or a bead,
  // both highlight the same seq (verify_pack.py item 5 display-binding).
  function selectSeq(sq) {
    document.querySelectorAll('.chainrail .dot').forEach((d) =>
      d.classList.toggle('sel', d.getAttribute('data-seq') === String(sq)));
    document.querySelectorAll('.txtable tr.pick').forEach((r) =>
      r.classList.toggle('sel', r.getAttribute('data-seq') === String(sq)));
  }

  // ------------------------------------------------------------- pack panel
  function resetPackPanel() {
    $('packbox').innerHTML = '<p class="muted">Select a filed case to load its sealed pack, verify it '
      + 'offline in this page, and download the JSON + HTML for an air-gapped auditor.</p>';
    setStamp('idle', 'not run');
  }
  function setStamp(kind, label) {
    const s = $('verifier-stamp'); s.className = 'chainpill ' + kind; s.textContent = label;
  }

  async function loadPackPanel(id, rec, token) {
    const box = $('packbox'); box.textContent = '';
    // pack identity
    const idc = cls('div', 'packid');
    idc.innerHTML = '<span class="k">kind</span>precedent.evidence_pack.v1<br>'
      + '<span class="k">generated</span>' + esc((rec.generated_at || '').slice(0, 19)) + '<br>'
      + '<span class="k">manifest</span>sha256 · secret_key: null · self-authenticating<br>'
      + '<span class="k">digest</span>' + esc(short(rec.manifest_digest, 24)) + '…';
    box.appendChild(idc);

    // on-page verifier
    const vf = cls('div', 'verifier');
    const head = cls('div', 'vf-head');
    head.appendChild(txt('span', 'vf-title', 'On-page offline verifier'));
    const run = txt('button', null, 'Verify in this page'); run.type = 'button';
    run.setAttribute('data-act', 'verify');
    run.style.margin = '0'; run.style.fontSize = '12px'; run.style.padding = '7px 12px';
    head.appendChild(run);
    vf.appendChild(head);
    vf.appendChild(txt('p', 'muted', 'Pure in-page arithmetic over the embedded bytes — no network, no model. '
      + 'Byte-identical to verify_pack.py.'));
    const stepsBox = cls('div', 'vf-steps'); vf.appendChild(stepsBox);
    box.appendChild(vf);

    // fetch the SEALED canonical bytes once; keep for verify + download + <pre>
    const packText = await (await fetch('/api/pack/' + id)).text();
    if (token != null && token !== S.loadToken) return;   // superseded mid-fetch
    let pack = null; try { pack = JSON.parse(packText); } catch (e) { pack = null; }

    run.addEventListener('click', () => {
      if (!pack) { setStamp('bad', 'unreadable'); return; }
      const res = verifyInPage(pack);
      stepsBox.textContent = '';
      res.steps.forEach((s) => {
        const li = cls('div', 'li');
        li.appendChild(txt('span', 'mk ' + (s.ok ? 'ok' : 'bad'), s.ok ? '✓' : '✗'));
        li.appendChild(txt('span', null, s.label));
        stepsBox.appendChild(li);
      });
      if (res.ok) { setStamp('ok', 'VERIFIES OFFLINE'); }
      else {
        setStamp('bad', 'TAMPER DETECTED');
        res.errors.forEach((e) => { const li = cls('div', 'li'); li.appendChild(txt('span', 'mk bad', '✗')); li.appendChild(txt('span', null, e)); stepsBox.appendChild(li); });
      }
    });
    // auto-run once so the seal is visible immediately
    run.click();

    // collapsible canonical bytes
    const det = cls('details', 'packjson');
    det.appendChild(txt('summary', null, 'Canonical pack bytes (the verifiable JSON)'));
    const pre = cls('pre'); pre.id = 'pack-json'; pre.textContent = packText; det.appendChild(pre);
    box.appendChild(det);

    // downloads + CLI
    const dl = cls('div', 'dlrow');
    const aj = document.createElement('a'); aj.className = 'dlbtn'; aj.href = '/api/pack/' + id; aj.textContent = id + '.pack.json'; aj.setAttribute('download', id + '.pack.json');
    const ah = document.createElement('a'); ah.className = 'dlbtn'; ah.href = '/api/pack/' + id + '.html'; ah.textContent = id + '.pack.html'; ah.setAttribute('download', id + '.pack.html');
    dl.appendChild(aj); dl.appendChild(ah);
    box.appendChild(dl);
    box.appendChild(txt('code', 'cliline', 'python verify_pack.py ' + id + '.pack.json'));
    box.appendChild(txt('div', 'sealed-line', 'This record is sealed — take it to your auditor without us in the room.'));
  }

  // ------------------------------------------------------------- ladder panel
  async function refreshLadder(currentClassKey) {
    const r = await jget('/api/ladder');
    S.ladder = r.body.ladder || [];
    renderLadder(currentClassKey, r.body.standing_label || 'Standing Approval');
  }
  function renderLadder(currentClassKey, standingLabel) {
    const box = $('ladder'); box.textContent = '';
    const row = S.ladder.find((x) => x.class_key === currentClassKey) || S.ladder[0];
    $('ladder-classlbl').textContent = row ? row.class_key.split('|')[0] : '—';
    if (!row) { box.appendChild(txt('p', 'muted', 'No class selected.')); return; }

    const rungs = ['L0', 'L1', 'L2', 'STANDING'];
    const labels = { L0: 'L0 · observe', L1: 'L1 · recommend', L2: 'L2 · execute-gated', STANDING: standingLabel };
    const lit = row.level;
    rungs.forEach((rk) => {
      const d = cls('div', 'rung' + (rk === lit ? ' lit' : ''));
      d.appendChild(txt('span', 'rl', labels[rk]));
      const info = cls('div', 'rd');
      if (rk === 'STANDING') info.appendChild(txt('span', 'rtok', 'DB token: STANDING'));
      if (rk === lit) info.appendChild(txt('span', null, ' ← this class'));
      d.appendChild(info);
      box.appendChild(d);
    });

    // X-of-3 pip meter (streak toward eligibility at L2)
    const streak = row.consecutive_verified || 0, need = row.eligible_streak || 3;
    const pipwrap = cls('div');
    pipwrap.appendChild(txt('span', 'rtok', streak + ' of ' + need + ' consecutive verified at L2'));
    const pips = cls('div', 'pips');
    for (let i = 0; i < need; i++) pips.appendChild(cls('div', 'pip' + (i < streak ? ' on' : '')));
    pipwrap.appendChild(pips);
    box.appendChild(pipwrap);

    if (row.is_standing && row.promoted_by) {
      const p = cls('div', 'prov');
      p.innerHTML = 'promoted by <code>' + esc(row.promoted_by) + '</code> at <code>' + esc((row.promoted_at || '').slice(0, 19)) + '</code>';
      box.appendChild(p);
      box.appendChild(txt('p', 'prov', 'You promoted this class after watching it verify — that is why tonight ran without waking anyone.'));
    }

    // Promote / Revoke — confirm-with-consequence, keyboard-operable, adjacent.
    const acts = cls('div', 'ladderacts');
    const note = cls('p', 'actnote'); note.id = 'ladder-note';
    if (!row.is_standing) {
      const pro = txt('button', null, row.eligible ? 'Promote to ' + standingLabel : 'Promote (needs 3 verified)');
      pro.type = 'button'; pro.setAttribute('data-act', 'promote'); pro.disabled = false;
      armConfirm(pro, 'Confirm — promote to Standing?', async () => {
        const rr = await jpost('/api/ladder/promote', { class_key: row.class_key, principal: 'ops-lead' });
        setNote(rr.body.ok ? 'Promoted to ' + standingLabel + ' by ops-lead (audited).' :
          'Not promoted: ' + (rr.body.reason || 'not eligible'), rr.body.ok);
        refreshLadder(currentClassKey);
      });
      acts.appendChild(pro);
    }
    // Revoke ALWAYS adjacent.
    const rev = txt('button', 'ghost warn', 'Revoke → L1'); rev.type = 'button'; rev.setAttribute('data-act', 'revoke');
    armConfirm(rev, 'Confirm — demote to L1 now?', async () => {
      const rr = await jpost('/api/ladder/revoke', { class_key: row.class_key, principal: 'ops-lead' });
      setNote(rr.body.ok ? 'Revoked to L1 by ops-lead (audited).' : 'Revoke failed.', rr.body.ok);
      refreshLadder(currentClassKey);
    });
    acts.appendChild(rev);
    box.appendChild(acts);
    box.appendChild(note);
  }

  // two-step confirm on one control: first activate arms + shows consequence; second executes.
  function armConfirm(btn, confirmLabel, run) {
    const original = btn.textContent;
    btn.addEventListener('click', () => {
      if (btn.getAttribute('data-armed') === '1') {
        btn.removeAttribute('data-armed'); btn.textContent = original; run();
      } else {
        btn.setAttribute('data-armed', '1'); btn.textContent = confirmLabel;
        setTimeout(() => { if (btn.getAttribute('data-armed') === '1') { btn.removeAttribute('data-armed'); btn.textContent = original; } }, 4000);
      }
    });
  }
  function setNote(msg, good) {
    const n = $('ladder-note'); if (!n) return;
    n.textContent = msg; n.className = 'actnote ' + (good ? 'good' : 'bad');
  }

  // ------------------------------------------------------------- No-LLM popover
  function wireNoLLM() {
    const chip = $('chip-noll');
    chip.addEventListener('click', () => toggleNoLLM());
  }
  function toggleNoLLM(force) {
    const pop = $('noll-pop'), chip = $('chip-noll');
    const open = force != null ? force : pop.hasAttribute('hidden');
    if (open) { pop.removeAttribute('hidden'); chip.setAttribute('aria-expanded', 'true'); }
    else { pop.setAttribute('hidden', ''); chip.setAttribute('aria-expanded', 'false'); }
  }

  function esc(v) { const d = document.createElement('span'); d.textContent = v == null ? '' : String(v); return d.innerHTML; }

  document.addEventListener('DOMContentLoaded', boot);
  window.__precedentVerify = verifyInPage; // exposed for the e2e assertion
})();
