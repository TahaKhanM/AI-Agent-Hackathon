# Precedent — Recorded Video Shot List + On-Screen Captions

> **Scope.** The full recorded video (~4:15–4:30, shot 0 included). One video serves BOTH the
> DoraHacks/Conduct submission and the Fetch.ai 3–5 min deliverable. Shot 5 (ASI:One) is the Fetch
> centrepiece — 80 seconds, top billing, never shortened.
> **Source of truth.** Shots 0–8 mirror `Idea/refinement/04-demo-and-video-script.md` §7; every caption
> number traces to `Prep/final-numbers.md`. This file adds per-shot durations, VO cues, and the
> honesty guardrails baked into each caption. **Timestamps are DURATIONS, not absolutes** — shot 0
> shifts everything +14s.
> **Owner.** N2 assembles from T2's raw clips + N1's VO in the `precedent-video-drop` folder.

---

## Number-honesty guardrails this shot list obeys (every caption checked against these)

- **"25k-record store"** (24,918 incidents). The 141k figure is a **provenance line only** ("141k
  events / 24,918 incidents") — **never** "P99 over 141k events". Shot 7's latency clause names the
  **25k-record store** or is deleted.
- **NEVER-BLEND.** 18.2h is **CALENDAR** (ours, UCI); 8.85h / **"8h51m"** is **BUSINESS** (MetricNet).
  The video's spoken/captioned MTTR anchor is **8h51m (business)**; the corpus repeat-median is **18h
  calendar**. They corroborate — never averaged, swapped, or blended.
- **94% = fix-class EXISTENCE** (closed_code known at resolution). Do not restate as accuracy.
- Every third-party number carries its source on screen (Splunk 2026, MetricNet, ServiceNow KCS, UCI,
  CrowdStrike). No unlabelled vendor claim. PagerDuty-style vendor stats, if ever used, carry
  "(vendor-claimed)"; NeuBird carries "(2026 vendor-sponsored survey)". Neither appears in this cut.
- **L3 is "Standing Approval", NEVER "Autonomous".**
- The **~15s** standing-approval time is engineered/paced (real work ~6–8s) — presented as the
  on-screen stopwatch of *this instrumented demo*, never as a general latency benchmark.
- **Open-weight only.** Model roles are FAST/SMART/HEAVY/EMBED; the only pinned ids live in
  `precedent/models.py` + the PR-README. No caption or VO names a model id — shot 7 says
  "open-weight models (Venice-served), named in README".
- **Never ship a bracket.** `[measured]` and `[repo]` are placeholders a human fills at export
  (EDIT 1 / EDIT 2). If the real value hasn't landed, the clause is **deleted**, not bracketed.
- TMDB/IMDb rejected on licence grounds — never named. Refuted claims (Komodor "no autonomous
  execution / K8s-only / RAG"; "$400B combined") never appear.

---

## Shot table (0–8)

### Shot 0 — Results-first cold open
- **Duration:** 0:14 (0:00–0:14)
- **On screen:** 12–15s captioned montage, three payoff frames cut from the master — (a) the
  **58s-vs-8h51m** elapsed bar, (b) the **15s stopwatch**, (c) the **refusal card**. Music/beat only,
  no console chrome narration. Hard beat-cuts between frames.
- **Caption (verbatim):** **8 h 51 m → 15 seconds. Approval never leaves the loop.**
- **VO cue:** NONE. Captions + music carry it. `VO_shot0` does not exist.
- **Honesty note:** 8h51m is the business MTTR anchor; 15s is this demo's stopwatch. No blend.

### Shot 1 — Cold-open narrative (CrowdStrike hook)
- **Duration:** 0:15 (0:14–0:29)
- **On screen:** 3s Sky News / CrowdStrike outage headline still (`asset_skynews_headline.png`) → cut
  to the manual-loop time-lapse (`asset_manual_loop_timelapse.mp4`, same asset as live beat 0).
- **Caption (verbatim):** **Downtime: $600B/yr across the Global 2000 (Splunk 2026) — ~$200M per company**
- **VO cue (`VO_shot1`):** "When the CrowdStrike outage took Sky News off air, the fix was already
  documented — humans applied it by hand, thousands of times. One of us watched that loop every day
  inside Disney+ operations."
- **Honesty note:** "$600B/yr … Splunk 2026" is paired in the same caption with "~$200M per company"
  (Oxford/Splunk 2024) — the per-company figure is the load-bearing one; never the refuted "$400B".
  Say "inside Disney+ operations", never a product/brand the operator worked inside.

### Shot 2 — Manual loop → the repeat-incident premise
- **Duration:** 0:25 (0:15–0:40 as a duration; sits ~0:29–0:54 after shot 0's +14s)
- **On screen:** manual-loop time-lapse continues; freeze on the approval-queue email; the **Baseline
  Bar** animates in and pins.
- **Caption (verbatim):** **8h51m avg MTTR (MetricNet)** · **>60% repeat incidents (ServiceNow KCS study)**
- **VO cue (`VO_shot2`):** "Read the ticket, hunt the runbook, click through a legacy admin console,
  wait for approval. Average: 8 hours 51 minutes. And at ServiceNow's own support desk, over 60% of
  incidents were repeats — the fix already existed. Precedent is the agent that remembers every fix
  your organisation has ever applied, and applies it again: risk-classified, approval-gated, audited,
  reversible."
- **Honesty note:** 8h51m carries "(MetricNet)"; >60% carries "(ServiceNow KCS study)". Both
  attributed on screen. 8h51m is BUSINESS hours — not merged with the 18h calendar figure (which
  appears only in shot 7).

### Shot 3 — Console home + provenance
- **Duration:** 0:15 (0:40–0:55 duration)
- **On screen:** console home; slow pan across the incident feed; memory counter (25k+ precedents);
  provenance footer zoomed for 2s (`raw_shot03_consolepan_takeN.mp4`).
- **Caption (verbatim):** **Real data: UCI ServiceNow log (141k events, CC BY 4.0) · GitLab/K8s runbooks · CrowdStrike remediation bulletin · TVmaze/XMLTV programme metadata (CC BY-SA)**
- **VO cue (`VO_shot3`):** "This is MediaCo, our simulated broadcaster — seeded entirely with real
  public data: a 141,000-event ServiceNow incident log as its history, real published runbooks, real
  programme metadata. Tickets live in a real Jira Service Management instance."
- **Honesty note:** "141k events" is legitimate HERE — it is the provenance line for the ingest
  source, paired with "24,918 incidents" context in shot 7. It is a corpus-size provenance statement,
  NOT a P99 denominator. TMDB/BBC-programmes never named; sources are UCI / GitLab-K8s / CrowdStrike /
  TVmaze-XMLTV only.

### Shot 4 — Incident 1: messy ticket → one human click
- **Duration:** 0:40 (0:55–1:35 duration). Live-script beat 1 at ~1.5× with cuts. **Squeeze target:
  compress to 25s if the cut must shrink toward 3:30 — never shot 5, never shot 0.**
- **On screen:** messy ticket card → triage normalisation (raw text → corrected code `PUB-4012` →
  matched class) → plan panel with risk class LOW + rollback plan rendered *above* the Approve button
  → **Approve** click (hero click #1) → execute → verify green → real Jira ticket closes with evidence
  → memory +1 → **Promote to Standing Approval** click (hero click #2). Source
  `raw_shot04_incident1_takeN.mp4`. Phone-clock PiP in a corner is fine as timestamp proof.
- **Caption (verbatim):** **58 seconds vs 8h51m** · **Human approval — requester ≠ approver, immutably logged**
- **VO cue (`VO_shot4`):** "A publish failure — filed with typos and the wrong error code; inputs are
  mutated every run. Precedent triages it, retrieves the documented fix, classifies risk, and writes
  the rollback *before* asking. One human click approves. It executes, verifies, and closes the real
  Jira ticket with evidence. Then the operations lead pre-approves this fix class — a standing
  approval she can revoke at any time."
- **Honesty note:** "58 seconds" is this demo's measured elapsed bar vs the 8h51m business baseline —
  a same-demo comparison, not a benchmark. "Standing approval", never "autonomous". No model named
  (the triage/retrieval is FAST/SMART-role work, not stated on screen).

### Shot 5 — ★ ASI:One SEGMENT (Fetch centrepiece, 80s — NEVER shortened)
- **Duration:** 1:20 / 80s (1:35–2:55 duration). This is the longest single shot and the Fetch
  primary artifact. Do not compress under any squeeze rule.
- **On screen:** clean recording of a single ASI:One conversation, cursor visible, **no console
  anywhere** (`raw_shot05_asione_takeN.mp4`):
  (a) user types *"our EPG publish to the evening slot failed, error 4012 i think — can you fix it?"*
  → (b) agent replies with one well-formatted message: triage, matched precedent, **risk class LOW**,
  execution plan + rollback plan, "reply **approve** to execute" → (c) user: "approve" → (d) agent
  streams executing → verified → **Jira ticket link** (cut 2s to the ticket closing) → audit-trail
  link, approver recorded as the chat sender address → (e) **same session**, second incident reported
  → resolved under **Standing Approval** in ~15s, the timer quoted in the reply. Brief cut to the
  Agentverse profile pages (3 agents, addresses visible, Innovation Lab + hackathon badges).
- **Caption (verbatim):** **3 agents on Agentverse · Agent Chat Protocol · discoverable via ASI:One** · **agent addresses on screen** · **Approver = chat sender, logged** · **Runs without any custom frontend**
- **VO cue (`VO_shot5`):** "Everything you just saw needs no custom frontend at all. Precedent's
  agents live on Fetch.ai's Agentverse and speak the Chat Protocol — the gateway agent, the retrieval
  agent and the execution agent are separate Agentverse agents passing messages between themselves.
  Here's the whole loop inside one ASI:One conversation: report the incident in plain English… get the
  plan and the rollback… type 'approve' — that approval is bound to the chat sender's address and
  logged as the authorising principal… and the real Jira ticket closes. Same session, second
  occurrence: fifteen seconds, standing approval. The agents stay registered and running on Agentverse
  after this hackathon."
- **Honesty note:** The "approve" step is a HUMAN typing approve — the permission decision is the
  deterministic gate keyed on the chat-sender identity, never the model. "Standing approval" (not
  autonomous). The 15s is the on-screen timer of this session. Capture the **public shared-chat URL**
  the same night; README points to the exact turn ("jump to turn 6") where the 15s run happens.

### Shot 6 — Recovery + refusal, back-to-back
- **Duration:** 0:25 (2:55–3:20 duration). Live beats R and 3 condensed.
- **On screen:** verification FAILS (red) → pre-written rollback fires → pre-state restored, verify-
  restore green → **demotion event** in the audit log (Standing Approval → L1); then the rights-
  conflict **refusal**: risk HIGH + permission denied → investigation dossier → routed to Rights Ops
  queue. Source `raw_shot06_recovery_refusal_takeN.mp4`.
- **Caption (verbatim):** **Auto-rollback on failed verification → class demoted** · **Permission-aware memory: restricted runbook → refusal, audited**
- **VO cue (`VO_shot6`):** "When a remembered fix fails, verification catches it, the pre-written
  rollback restores the system, and the class is demoted — it must earn approval again. And when the
  only documented fix is one it's not permitted to read — here, a rights runbook restricted to another
  team — it refuses, and routes a dossier to the humans who are. It knows what it's not allowed to
  touch, down to the permissions on the runbook itself."
- **Honesty note:** The refusal card discloses only that a fix exists and access is denied under this
  identity + the owning team (Rights Ops) — never the restricted runbook's title/body/secret
  (fail-closed). Demotion is mechanical (any rollback demotes), not an LLM decision. Contains the
  verbatim memorable line **"it knows what it's not allowed to touch"** (VO wording).

### Shot 7 — Scale artifact
- **Duration:** 0:25 (3:20–3:45 duration). **Squeeze target: compress to 15s toward 3:30 — never
  shot 5, never shot 0.**
- **On screen:** terminal/notebook showing the ingest run; retrieval + permission-check latency chart;
  ONE architecture slide (the only slide in the video) with the four integration tiers. Source
  `raw_shot07_terminal_takeN.mp4`.
- **Caption (verbatim, with human-filled EDIT 1):** **141k events / 24,918 incidents ingested · 94% pre-matched to a documented fix · P99 permission-check: <FILL P99 ms from metrics block> over the 25k-record store** · **Graduation: 3 verified successes → standing approval; any rollback → demote** · **100% open-weight models (Venice-served), named in README**
  - **EDIT 1 (human, at export):** replace `<FILL P99 ms from metrics block>` with the measured P99
    from `precedent_memory/bench/RESULTS.md`. The clause MUST read **"over the 25k-record store"** —
    **never** "P99 over 141k events". **If no P99 value has landed, delete the entire P99 clause** —
    never ship a bracket. (Committed bench value sits ~5 orders of magnitude under the 200ms
    threshold; quote the committed number, not a re-measured one.)
- **VO cue (`VO_shot7`):** "Does it hold at scale? We ingested 141,000 events — twenty-five thousand
  real incidents — as day-one memory: **94% arrived with their fix already precedented, and those
  repeats still took a median of 18 hours by hand.** Permission-checked retrieval over that store stays
  under our latency budget at P99 — measured, with false-negative and false-positive rates over
  ground-truth queries, in the repo. Real estates aren't clean REST — they're BXF file drops, FTP
  folders and worse — so the execution layer is a four-tier adapter stack, and every action is a typed
  call, never free-form. Autonomy is mechanical, not vibes: a class reaches standing approval after
  three consecutive verified successes, and any rollback demotes it. The whole pipeline runs on
  open-weight models."
- **Honesty note:** THE never-blend crux. "141k events / 24,918 incidents ingested" is the ingest
  provenance line. "18 hours by hand" is the **calendar** repeat-median (ours, UCI) — said in the same
  breath as 94% existence, and kept separate from the 8h51m business MTTR of shots 0/2. The P99 clause
  names the **25k-record store**, never 141k. 94% is fix-class **existence**, not accuracy. No model id
  — "open-weight models (Venice-served), named in README" (the ids live only in `precedent/models.py`
  + PR-README).

### Shot 8 — Close + links
- **Duration:** 0:30 (3:45–4:15 duration).
- **On screen:** team card (Disney+ alum flagged), the loop diagram, links card held 5s. Source is a
  built end-card, not a raw console clip.
- **Caption (verbatim, with human-filled EDIT 2):** **<FILL public repo URL from metrics block> · ASI:One shared chat · Agentverse profiles** · **Precedent — the second time is free**
  - **EDIT 2 (human, at export):** replace `<FILL public repo URL from metrics block>` with the real
    public repo URL. Never ship the `[repo]` bracket.
- **VO cue (`VO_shot8`):** "AI SREs fix broken code — but in real enterprises the fix is almost never
  code. It's a documented change, waiting to be remembered. ServiceNow paid $2.85 billion for
  Moveworks; the memory layer is worth buying. We're Precedent — every incident resolved becomes
  precedent. Repo, live agents and the ASI:One chat linked below."
- **Honesty note:** Caption carries the verbatim memorable line **"the second time is free"**.
  "$2.85 billion for Moveworks" is a public deal comp. No secrets, no real names on the links card (a
  role-flagged team card, "Disney+ alum", not a named person).

---

## Runtime + squeeze rules
- **Target ~4:30 with shot 0** (inside Fetch's 3–5 min window). Shot-list times are durations; shot 0
  adds 14s at the front, so downstream shots shift +14s.
- **If it must shrink toward 3:30:** compress shot 4 → 25s and shot 7 → 15s. **Never compress shot 5
  (the 80s ASI:One centrepiece) and never shot 0.**
- **Flag any assembly that drifts outside 4:15–4:45.** Never below 3:30 (Fetch floor), never above
  5:00 (Fetch ceiling).

## Placeholder / bracket guard (run before export)
- `grep -nE '\[measured\]|\[repo\]|‹|<FILL' <exported caption sources>` MUST return nothing before the
  master is uploaded. EDIT 1 and EDIT 2 are the only two human fills; the P99 clause is deleted (not
  bracketed) if its value hasn't landed.
