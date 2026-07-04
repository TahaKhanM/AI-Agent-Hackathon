# Precedent — Recorded Video Shot List + On-Screen Captions

> **Scope.** The full recorded video (~4:36 with shot 0). One video serves BOTH the DoraHacks/Conduct
> submission and the Fetch.ai 3–5 min deliverable. Shot 5 (ASI:One) is the Fetch centrepiece — 80
> seconds, top billing, never shortened.
> **Source of truth.** Shots 0–8 mirror `Idea/refinement/04-demo-and-video-script.md` §7; every caption
> number traces to `Prep/final-numbers.md`. **VO is reconciled (V1):** the `VO_shotN` cues below are
> word-identical to `Prep/video/vo-script.md`, both derived from `Prep/video/pipeline/vo_canonical.json`
> and enforced by `Prep/video/pipeline/check_vo_sync.py`. Each VO cue is **one physical line** so the
> checker can extract it — do not re-wrap them.
> **Timeline.** Durations are reconciled; the **absolute cumulative timeline** is the table in
> §"Runtime" (no more ±14s guesswork — shot 0 is already counted).
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
- **Never ship a bracket.** `[measured]` and `[repo]` (and `<FILL …>`) are placeholders a human fills
  at export (EDIT 1 / EDIT 2). If the real value hasn't landed, the clause is **deleted**, not
  bracketed.
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
- **VO cue (`VO_shot0`):** NONE. Captions + music carry it. `VO_shot0` does not exist.
- **Honesty note:** 8h51m is the business MTTR anchor; 15s is this demo's stopwatch. No blend.

### Shot 1 — Cold-open narrative (CrowdStrike hook)
- **Duration:** 0:15 (0:14–0:29)
- **On screen:** 3s **built text-card cold open** (`asset_coldopen_card.png` — HTML → Playwright
  screenshot, house style per `assets/brand/`; text: *"July 2024. A global IT outage takes broadcasters
  off air. The fix was already documented."*) → cut to the programmatically-staged manual-loop
  time-lapse (`asset_manual_loop_timelapse.mp4`, Playwright-driven sim grind, 8× with a clock overlay —
  same asset as live beat 0; **built rights-safe, no broadcast footage, no humans filmed** — see V2).
- **Caption (verbatim):** **Downtime: ~$200M per Global 2000 company, per year (Oxford Economics / Splunk 2024)**
- **VO cue (`VO_shot1`):** "When the CrowdStrike outage took broadcasters off air, the fix was already documented — humans applied it by hand, thousands of times. One of us watched that loop every day inside Disney+ operations."
- **Honesty note:** the ONLY sanctioned downtime number is **"$200M/year per Global 2000 company
  (Oxford Economics/Splunk 2024)"** (`final-numbers.md` §5). The **$600B/Global-2000 aggregate is
  dropped** — it is not on `final-numbers.md` and §6 refutes Global-2000 aggregates ("$400B combined"
  → use $200M/company). CAPTION-AUDITOR flag closed.
  Say "inside Disney+ operations", never a product/brand the operator worked inside. **The Sky News
  still is GONE** (rights question) — replaced by the built text-card; the VO names the CrowdStrike
  event (a factual reference, no footage) but the picture shows no broadcaster's frame.

### Shot 2 — Manual loop → the repeat-incident premise
- **Duration:** 0:26 (0:29–0:55)
- **On screen:** manual-loop time-lapse continues; freeze on the approval-queue email; the **Baseline
  Bar** animates in and pins.
- **Caption (verbatim):** **8h51m avg MTTR (MetricNet)** · **>60% repeat incidents (ServiceNow KCS study)**
- **VO cue (`VO_shot2`):** "Read the ticket, hunt the runbook, click through a legacy admin console, wait in an approval queue. The industry average: eight hours fifty-one minutes — MetricNet's business-hours benchmark. And at ServiceNow's own support desk, over sixty percent of incidents were repeats — the fix already existed, and nobody could find it. Precedent remembers every fix your organisation has ever applied, and applies it again: risk-classified, approval-gated, audited, reversible."
- **Honesty note:** 8h51m carries "(MetricNet)"; >60% carries "(ServiceNow KCS study)". Both
  attributed on screen. 8h51m is BUSINESS hours, labelled in speech ("business-hours benchmark") — not
  merged with the 18h calendar figure (which appears only in shot 7).

### Shot 3 — Console home (trimmed per PLAN-CRITIC)
- **Duration:** 0:08 (0:55–1:03). **PLAN-CRITIC trim adopted** — the provenance list folds into a
  caption over shot 4 (Window 4A below), tightening the pre-hero-click runway (Conduct "short and
  snappy"). Shot 5 keeps its 80s.
- **On screen:** console home; quick pan across the incident feed; memory counter (25k+ precedents)
  (`raw_shot03_consolepan_takeN.mp4`).
- **Caption (verbatim):** **MediaCo — simulated broadcaster · 25,412 precedents seeded**
- **VO cue (`VO_shot3`):** "This is MediaCo, our simulated broadcaster — seeded entirely with real public data, running on a real Jira Service Management instance."
- **Honesty note:** the full provenance (141k-event UCI log + runbooks + programme metadata + licences)
  now lives in **shot-4 Window 4A**, a caption — a corpus-size provenance statement, NOT a P99
  denominator (shot 4 has no P99, so no proximity issue). TMDB/BBC-programmes never named; sources are
  UCI / GitLab-K8s / CrowdStrike / TVmaze-XMLTV only. "141k" appears only in captions (Window 4A +
  Window 7A), never in VO, never near a P99 clause.

### Shot 4 — Incident 1: messy ticket → one human click
- **Duration:** 0:40 (1:03–1:43). Live-script beat 1 at ~1.5× with cuts. **Squeeze target: compress to
  25s if the cut must shrink toward 3:30 — never shot 5, never shot 0.**
- **On screen:** messy ticket card → triage normalisation (raw text → corrected code `PUB-4012` →
  matched class) → plan panel with risk class LOW + rollback plan rendered *above* the Approve button
  → **Approve** click (hero click #1, the real hold+Approve path) → execute → verify green → real Jira
  ticket closes with evidence → memory +1 → **Promote to Standing Approval** click (hero click #2).
  Source `raw_shot04_incident1_takeN.mp4`. Phone-clock PiP in a corner is fine as timestamp proof.
- **Caption — TWO sequential windows:**
  - **Window 4A (first ~8s, folded from shot 3):** **Real data: UCI ServiceNow log (141k events, CC BY 4.0) · GitLab/K8s runbooks · CrowdStrike remediation bulletin · TVmaze/XMLTV programme metadata (CC BY-SA)**
  - **Window 4B (the Approve/verify beat):** **58 seconds vs 8h51m** · **Human approval — requester ≠ approver, immutably logged**
- **VO cue (`VO_shot4`):** "A publish failure — filed with typos and the wrong error code; the inputs are mutated every run. Precedent triages it, retrieves the organisation's own documented fix, classifies the risk, and writes the rollback before asking. One human click approves. It executes, verifies, and closes the real Jira ticket with the evidence attached. Then the operations lead pre-approves this fix class — a standing approval she can revoke at any time."
- **Honesty note:** "58 seconds" is this demo's measured elapsed bar vs the 8h51m business baseline —
  a same-demo comparison, not a benchmark. "Standing approval", never "autonomous". No model named
  (the triage/retrieval is FAST/SMART-role work, not stated on screen).

### Shot 5 — ★ ASI:One SEGMENT (Fetch centrepiece, 80s — NEVER shortened)
- **Duration:** 1:20 / 80s (1:51–3:11). This is the longest single shot and the Fetch primary artifact.
  Do not compress under any squeeze rule.
- **On screen:** clean recording of a single ASI:One conversation, cursor visible, **no console
  anywhere** (`raw_shot05_asione_takeN.mov`):
  (a) user types *"our EPG publish to the evening slot failed, error 4012 i think — can you fix it?"*
  → (b) agent replies with one well-formatted message: triage, matched precedent, **risk class LOW**,
  execution plan + rollback plan, "reply **approve** to execute" → (c) user: "approve" → (d) agent
  streams executing → verified → **Jira ticket link** (cut 2s to the ticket closing) → audit-trail
  link, approver recorded as the chat sender address → (e) **same session**, second incident reported
  → resolved under **Standing Approval** in ~15s, the timer quoted in the reply. Brief cut to the
  Agentverse profile pages (3 agents, addresses visible, Innovation Lab + hackathon badges).
- **Caption (verbatim):** **3 agents on Agentverse · Agent Chat Protocol · discoverable via ASI:One** · **agent addresses on screen** · **Approver = chat sender, logged** · **Runs without any custom frontend**
- **VO cue (`VO_shot5`):** "Everything you just saw needs no custom frontend at all. Precedent's agents live on Fetch.ai's Agentverse and speak the Chat Protocol — the gateway agent, the retrieval agent and the execution agent are separate Agentverse agents passing messages between themselves. Here's the whole loop inside one ASI:One conversation: report the incident in plain English… get the plan and the rollback… type 'approve' — that approval is bound to the chat sender's address and logged as the authorising principal… and the real Jira ticket closes. Same session, second occurrence: fifteen seconds, standing approval — the second time is free. The agents stay registered and running on Agentverse after this hackathon."
- **Honesty note:** The "approve" step is a HUMAN typing approve — the permission decision is the
  deterministic gate keyed on the chat-sender identity, never the model. "Standing approval" (not
  autonomous). The 15s is the on-screen timer of this session. **The refusal narration is NOT here** —
  it stays with shot 6's picture (V1 fork fix). "the gateway agent", never "the Watcher". Contains the
  verbatim memorable line **"the second time is free"** (VO wording). Capture the **public shared-chat
  URL** the same night; README points to the exact turn ("jump to turn 6") where the 15s run happens.

### Shot 6 — Recovery + refusal, back-to-back
- **Duration:** 0:28 (3:11–3:39). Live beats R and 3 condensed.
- **On screen:** verification FAILS (red) → pre-written rollback fires → pre-state restored, verify-
  restore green → **demotion event** in the audit log (Standing Approval → L1); then the rights-
  conflict **refusal**: risk HIGH + permission denied → investigation dossier → routed to Rights Ops
  queue. Source `raw_shot06_recovery_refusal_takeN.mp4`.
- **Caption (verbatim):** **Auto-rollback on failed verification → class demoted** · **Permission-aware memory: restricted runbook → refusal, audited**
- **VO cue (`VO_shot6`):** "When a remembered fix fails, verification catches it, the pre-written rollback restores the system, and the class is demoted — it must earn approval again. And when the only documented fix is one it isn't permitted to read — here, a rights runbook restricted to another team — it refuses, and routes a dossier to the humans who are. It knows what it's not allowed to touch — down to the permissions on the runbook itself."
- **Honesty note:** The refusal card discloses only that a fix exists and access is denied under this
  identity + the owning team (Rights Ops) — never the restricted runbook's title/body/secret
  (fail-closed). Demotion is mechanical (any rollback demotes), not an LLM decision. Contains the
  verbatim memorable line **"it knows what it's not allowed to touch"** (VO wording).

### Shot 7 — Scale artifact
- **Duration:** 0:27 (3:39–4:06). **Squeeze target: compress to 15s toward 3:30 — never shot 5, never
  shot 0. When squeezed, drop the bench sentence; keep 94% / 18-calendar / open-weight.**
- **On screen:** terminal/notebook showing the ingest run; retrieval + permission-check latency chart;
  ONE architecture slide (the only slide in the video) with the four integration tiers. Source
  `raw_shot07_terminal_takeN.mp4`.
- **Caption — TWO sequential windows (so the ingest-count and the latency-percentile never share a
  caption window; satisfies the proximity guard mechanically):**
  - **Window 7A (first ~13s of shot 7):** **141k events / 24,918 incidents ingested · 94% pre-matched to a documented fix**
  - **Window 7B (next ~14s of shot 7, with human-filled EDIT 1):** **P99 permission-check: <FILL P99 ms from metrics block> over the 25k-record store · Graduation: 3 verified successes → standing approval; any rollback → demote · 100% open-weight models (Venice-served), named in README**
  - **EDIT 1 (human, at export):** replace `<FILL P99 ms from metrics block>` with the measured P99
    from `precedent_memory/bench/RESULTS.md`. The clause MUST read **"over the 25k-record store"** —
    **never** "P99 over 141k events". **If no P99 value has landed, delete the entire P99 clause** —
    never ship a bracket. (Committed bench value sits ~5 orders of magnitude under the 200ms
    threshold; quote the committed number, not a re-measured one.)
- **VO cue (`VO_shot7`):** "Does it hold at scale? Twenty-five thousand real incidents, seeded as day-one memory: ninety-four percent arrived with their fix already precedented — and those repeats still took a median of eighteen calendar hours by hand. Permission-checked retrieval over that store leaks nothing: zero leaks across five thousand two hundred and nineteen deny-expected queries, six of six attacks, graded by an independent oracle. It runs entirely on open-weight models."
- **Honesty note:** THE never-blend crux. "141k events / 24,918 incidents ingested" is the ingest
  provenance line (caption). "eighteen calendar hours" is the **calendar** repeat-median (ours, UCI) —
  said in the same breath as 94% existence, and kept separate from the 8h51m business MTTR of shots
  0/2. The bench clause (0 leaks / 5,219 deny-expected / 6-of-6 / independent oracle) is measured
  (`bench/RESULTS.md`). The P99 clause (caption) names the **25k-record store**, never 141k. 94% is
  fix-class **existence**, not accuracy. No model id — "open-weight models (Venice-served), named in
  README" (the ids live only in `precedent/models.py` + PR-README).

### Shot 8 — Close + links
- **Duration:** 0:30 (4:06–4:36).
- **On screen:** team card (Disney+ alum flagged), the loop diagram, links card held 5s. Source is a
  built end-card, not a raw console clip.
- **Caption (verbatim, with human-filled EDIT 2):** **<FILL public repo URL from metrics block> · ASI:One shared chat · Agentverse profiles** · **Precedent — the second time is free**
  - **EDIT 2 (human, at export):** replace `<FILL public repo URL from metrics block>` with the real
    public repo URL. Never ship the `[repo]` bracket.
- **VO cue (`VO_shot8`):** "AI SREs fix broken code — but in real enterprises the fix is almost never code. It's a documented change, waiting to be remembered. ServiceNow paid two-point-eight-five billion dollars for Moveworks; the memory layer is worth buying. We're Precedent — every incident resolved becomes precedent. Repo, live agents and the ASI:One chat are linked below."
- **Honesty note:** Caption carries the verbatim memorable line **"the second time is free"**.
  "$2.85 billion for Moveworks" is a public deal comp. No secrets, no real names on the links card (a
  role-flagged team card, "Disney+ alum", not a named person).

---

## Runtime + squeeze rules

**Reconciled absolute timeline (shot 0 already counted — no ±14s guesswork):**

| Shot | Dur | In | Out |
|---|---|---|---|
| 0 | 0:14 | 0:00 | 0:14 |
| 1 | 0:15 | 0:14 | 0:29 |
| 2 | 0:26 | 0:29 | 0:55 |
| 3 | 0:08 | 0:55 | 1:03 |
| 4 | 0:40 | 1:03 | 1:43 |
| 5 | 1:20 | 1:43 | 3:03 |
| 6 | 0:28 | 3:03 | 3:31 |
| 7 | 0:27 | 3:31 | 3:58 |
| 8 | 0:30 | 3:58 | 4:28 |

**Master target ≈ 4:28** (inside Fetch's 3–5 min window; inside the 4:15–4:45 house target).
- **If it must shrink toward 3:30:** compress shot 4 → 25s and shot 7 → 15s. **Never compress shot 5
  (the 80s ASI:One centrepiece) and never shot 0.** Shot 4 −15s + shot 7 −12s → ≈4:09; drop shot 3 to
  8s (fold provenance into a caption over shot 4) → ≈4:01. Floor is 3:30.
- **Flag any assembly that drifts outside 4:15–4:45.** Never below 3:30 (Fetch floor), never above
  5:00 (Fetch ceiling). The edit manifest (V5) is the single source of these in/out points.

## Placeholder / bracket guard (run before export)
- `grep -nE '\[measured\]|\[repo\]|‹|<FILL' <exported caption sources>` MUST return nothing before the
  master is uploaded. EDIT 1 and EDIT 2 are the only two human fills; the P99 clause is deleted (not
  bracketed) if its value hasn't landed. (This guard runs on the exported `captions.srt` / end-cards,
  **not** on this plan file — the `<FILL …>` tokens above are intentional export-time variables.)

## VO reconciliation (V1)
- The `VO_shotN` cues here are word-identical to `Prep/video/vo-script.md`, both derived from
  `Prep/video/pipeline/vo_canonical.json`. Run `python Prep/video/pipeline/check_vo_sync.py` — it must
  print `RESULT: PASS` (per-shot sync, banned words "Watcher"/"autonomous" clean, both memorable lines
  present, no model id in VO) before any capture or assembly.
