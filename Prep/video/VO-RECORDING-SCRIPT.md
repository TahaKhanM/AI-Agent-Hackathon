# Precedent — Voice-Over Recording Script (matched to the v2 cut)

**Read this straight down.** It is the exact narration for `precedent-video-drop/exports/precedent-full-v2.mp4`
(~4:30). Each block gives the **timecode** it plays over, a **read budget** (how long your read should
take), what's **on screen** so you can pace it, and the **words** — read them **verbatim**.

### How to record
- **Calm, unhurried, warm.** Let the stopwatch and the pictures do the drama — you don't push.
- **Read the numbers exactly as written** (they're spelled out on purpose). Never round, swap, or add a
  number that isn't here. "eight hours fifty-one minutes" ≠ "about nine hours."
- Record **one shot at a time**, hitting the read budget (± a second). Leave **0.5 s of silence** at the
  head and tail of every take. Shorter-than-budget is fine — the picture fills the gap.
- **Land the two signature lines** — say them cleanly, with a beat before each: **"the second time is
  free"** (shot 5) and **"it knows what it's not allowed to touch"** (shot 6).
- `( / )` = a short breath. `…` = a longer, deliberate pause (mostly shot 5).
- A reference read (ElevenLabs "George", British) sits at `precedent-video-drop/vo/vo-shot{n}.wav` if you
  want to hear the intended pacing. Mic: cardioid ~20 cm, pop filter, quiet room. Target **−14 LUFS**.

**Total narration: 8 reads (shot 0 is music only). Save each as `vo/vo-shot{n}.wav`.**

---

### 0:00 – 0:14 · SHOT 0 — cold-open montage
**NO VOICE-OVER.** Music/beat only over three frames (the 58-second bar → the 15-second stopwatch → the
refusal card). Stay silent.

---

### 0:14 – 0:29 · SHOT 1 — the hook   *(read ~13 s)*
*On screen: a title card, then the sped-up "manual loop."*

> When the CrowdStrike outage took broadcasters off air, the fix was already documented — humans
> applied it by hand, thousands of times. One of us watched that loop every day inside Disney-plus
> operations.

---

### 0:29 – 0:59 · SHOT 2 — the manual loop   *(read ~27 s)*
*On screen: the admin-console grind time-lapse; the grey 8h51m Baseline Bar slides in.*

> Read the ticket, hunt the runbook, click through a legacy admin console, wait in an approval queue. ( / )
> The industry average: **eight hours fifty-one minutes** — MetricNet's business-hours benchmark. And at
> ServiceNow's own support desk, over **sixty percent** of incidents were repeats — the fix already
> existed, and nobody could find it. ( / ) Precedent remembers every fix your organisation has ever
> applied, and applies it again: risk-classified, approval-gated, audited, reversible.

---

### 0:59 – 1:07 · SHOT 3 — the setup   *(read ~8 s — brisk)*
*On screen: the console home; the precedents counter.*

> This is MediaCo, our simulated broadcaster — seeded entirely with real public data, running on a real
> Jira Service Management instance.

---

### 1:07 – 1:47 · SHOT 4 — one human click   *(read ~28 s; picture runs 40 s)*
*On screen: a messy ticket → the live trace triages it → a plan with the rollback → the **Approve** click →
verify green → the real Jira ticket closes → **Promote to Standing Approval**.*

> A publish failure — filed with typos and the wrong error code; the inputs are mutated every run.
> Precedent triages it, retrieves the organisation's own documented fix, classifies the risk, and writes
> the rollback *before* asking. ( / ) One human click approves. It executes, verifies, and closes the real
> Jira ticket with the evidence attached. ( / ) Then the operations lead pre-approves this fix class — a
> standing approval she can revoke at any time.

---

### 1:47 – 3:07 · SHOT 5 — ★ ASI:One   *(read ~44 s; picture runs 80 s — use the pauses)*
*On screen: the real ASI:One conversation with the agent — report, plan, approve, resolved, then the repeat
in ~15 seconds.*

> Everything you just saw needs no custom frontend at all. Precedent's agents live on Fetch-dot-A-I's
> Agentverse and speak the Chat Protocol — the gateway agent, the retrieval agent and the execution agent
> are separate Agentverse agents passing messages between themselves. ( / ) Here's the whole loop inside
> one ASI-One conversation: report the incident in plain English… get the plan and the rollback… type
> 'approve' — that approval is bound to the chat sender's address and logged as the authorising principal…
> and the real Jira ticket closes. ( / ) Same session, second occurrence: fifteen seconds, standing
> approval — **the second time is free.** ( / ) The agents stay registered and running on Agentverse after
> this hackathon.

---

### 3:07 – 3:35 · SHOT 6 — recovery + refusal   *(read ~27 s — keep it moving, one continuous thought)*
*On screen: a verification fails red → auto-rollback → "class demoted"; then the rights refusal card.*

> When a remembered fix fails, verification catches it, the pre-written rollback restores the system, and
> the class is demoted — it must earn approval again. And when the only documented fix is one it isn't
> permitted to read — here, a rights runbook restricted to another team — it refuses, and routes a dossier
> to the humans who are. ( / ) **It knows what it's not allowed to touch** — down to the permissions on the
> runbook itself.

---

### 3:35 – 4:06 · SHOT 7 — does it hold at scale   *(read ~27 s)*
*On screen: the scale artifact — bench numbers, the latency chart, the four-tier adapter stack.*

> Does it hold at scale? Twenty-five thousand real incidents, seeded as day-one memory: **ninety-four
> percent** arrived with their fix already precedented — and those repeats still took a median of
> **eighteen calendar hours** by hand. ( / ) Permission-checked retrieval over that store leaks nothing:
> zero leaks across five thousand two hundred and nineteen deny-expected queries, six of six attacks,
> graded by an independent oracle. ( / ) It runs entirely on open-weight models.

---

### 4:06 – 4:36 · SHOT 8 — the close   *(read ~22 s; let the last line land)*
*On screen: the end card — team, the loop diagram, the links.*

> AI SREs fix broken code — but in real enterprises the fix is almost never code. It's a documented change,
> waiting to be remembered. ( / ) ServiceNow paid **two-point-eight-five billion dollars** for Moveworks;
> the memory layer is worth buying. ( / ) We're Precedent — every incident resolved becomes precedent.
> Repo, live agents and the ASI-One chat are linked below.

---

## Pronunciation & number cribs (say it this way)
- **Disney-plus** (not "Disney plus operations" run together) · **ASI-One** (say the letters: "A-S-I One") ·
  **Fetch-dot-A-I** · **MetricNet** · **Moveworks** · **MediaCo** ("media-co").
- Numbers stay spelled-out exactly: *eight hours fifty-one minutes* · *sixty percent* · *fifteen seconds* ·
  *ninety-four percent* · *eighteen calendar hours* · *five thousand two hundred and nineteen* ·
  *six of six* · *twenty-five thousand* · *two-point-eight-five billion dollars*.
- **Never** say "autonomous" — it is **standing approval**. **Never** blend 8h51m with the 18-hour figure
  (one is *business*, one is *calendar*).

## After you record
Drop the eight WAVs into `precedent-video-drop/vo/` (named `vo-shot1.wav … vo-shot8.wav`), then re-cut:
`source precedent-video-drop/scratch/env.sh && .venv/bin/python Prep/video/pipeline/assemble.py all 3`
(bumps to v3). Or drop them on the shot rows in your editor. The words match the burned captions and the
number gate exactly, so no re-checking is needed — just record and place.
