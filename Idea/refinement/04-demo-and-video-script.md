# Precedent — Demo & Video Script (Refinement Lane 04)

> Written 3 July 2026, early morning; updated same day (v5 session). Capacity model: **60–80 productive person-hours to Sat code freeze** — the committed ledger is in 06 §7 (supersedes the old "~30–36h" figure). Demo Day pitch: **3 min + 2 min Q&A**, Blackett LT1, VC judges (LocalGlobe, Antler, EWOR) + sponsor judges in the room.
>
> This file is the **performance layer**: exactly what is said, clicked, and shown. It bakes in the round-1 judge fixes that live in this lane: the 20-second manual "before" (Conduct: before/after in 90s), the renamed **L3 → "Standing Approval"** with visible Promote/Revoke clicks (Conduct: "autonomous" is a skim-disqualifier), the **live error-recovery beat** (Conduct 35% criterion: "recovers from errors"), the **messy-ticket robustness beat + Q&A party trick** (Conduct: "not only a scripted demo"), the **jargon purge and real ask** (VC), the **stopwatch-not-architecture** framing (VC/Conduct), and the **ASI:One segment with top billing in the video** (Fetch: the shared-chat URL is their primary artifact).

---

## 0. Ground rules the whole script obeys

1. **Words banned on stage** (VC judge): Watcher/Librarian/Assessor/Operator/Auditor (say "five specialised agents" once, max), YAML, ACL, lineage, SoD, embeddings, deterministic policy engine, P99. All of it lives in Q&A backup slides where it becomes a strength.
2. **Words required on stage**: "**the second time is free**", "**it knows what it's not allowed to touch**", "**approval moved earlier in time — it never left the loop**", "**unscripted**".
3. **Never say "autonomous" about L3.** The tier is "**Standing Approval** — a pre-approved standard change". A human is shown granting it and a Revoke button is shown on screen. (Conduct judge, major severity — this is a pure reframe, not a relitigation of the ladder itself.)
4. **Stopwatches, not architecture.** The persistent **Baseline Bar** (see §1.2) is on screen for the entire demo. Non-engineers read elapsed time.
5. **Every number spoken or captioned appears in the consistency table (§5)** with its verified source. Nothing else gets quoted.
6. **Rehearse to 2:40, not 3:00** (VC judge). The script below totals ~2:42 at ~150 wpm; the buffer absorbs one stumble or one slow API call.
7. **Local-first execution** (technical judge): the on-stage run must pass an airplane-mode rehearsal. Jira is write-behind enrichment; embeddings are precomputed; the L3 path uses the fingerprint fast-path so 15 seconds is engineered, not hoped for.

---

## 1. Stage setup (before you walk on)

### 1.1 Machines & windows

| Item | Detail |
|---|---|
| **Window A (primary, full screen)** | Precedent console in a maximised browser window, 125% zoom, dark theme, font ≥16px (LT1 projector legibility). Incident feed left, agent activity trace centre, approval/audit panel right. Baseline Bar pinned top. |
| **Window B** | Real Jira Service Management board (MediaCo project), logged in, pre-filtered to today, one browser tab directly right of Window A's tab (`Cmd+Shift+]` to reach it — never alt-tab hunting). |
| **Window C (hidden)** | QuickTime with the **backup video** open, paused at chapter 1 marker, muted. Reachable via `Cmd+Tab` (keep only 3 apps running: browser, QuickTime, terminal). |
| **Terminal (hidden)** | `make demo-reset` armed — resets sim state, memory counters, and incident generator between rehearsals. Never touched during the pitch. |
| **Phone (presenter 2's pocket)** | Logged into the Jira portal as a requester — this is the Q&A party-trick device (§3). |
| **Clicker/roles** | Presenter 1 speaks. Presenter 2 drives the machine and performs the two hero clicks (Approve; Promote to Standing Approval) — a *different human* clicking approvals is itself the segregation-of-duties story, visible. |
| **Wi-Fi** | Laptop on phone hotspot, NOT venue Wi-Fi. Demo must also pass with both off (airplane-mode rehearsal, §4.3). |

### 1.2 Console elements the script points at (build dependencies)

These must exist in the UI or the corresponding line is cut — see §6 for the fallback wording per missing element.

- **Baseline Bar** (persistent header): a long grey bar labelled **"Manual: ticket → find runbook → admin console → approval queue → resolve = 8 hrs 51 min avg"**; each live incident draws its actual elapsed-time bar underneath in green as it runs (≈60s, ≈15s). *(Conduct judge fix #4 — the visual "before".)*
- **Memory counter** ("Precedents: N") and **autonomy badge** per incident class (L0/L1/L2/**Standing Approval**).
- **Promote to Standing Approval** button (appears after a verified success) and a permanently visible **Revoke** button on any class at Standing Approval. *(Conduct judge fix #3.)*
- **ROI ticker**: "deflected escalations × $22→$104 ticket-cost ladder" — a static counter that increments per resolved incident is fine (technical judge: don't burn hours animating it).
- **Data provenance footer** (small, persistent): "Seeded with: 25k real incidents (UCI ServiceNow event log, CC BY 4.0) · real public runbooks (GitLab/K8s/CrowdStrike bulletin) · real UK programme metadata (TVmaze CC BY-SA / XMLTV) · real catalog rights data (CC0)". *(Conduct judge fix #1 — say it AND show it. NEVER name TMDB or BBC /programmes here — 01 §0 rejected both on licence/access grounds and says so on the provenance slide.)*
- **Degraded-mode banner**: if Jira is unreachable, a visible amber strip: "Jira degraded — running on cached mirror, will re-sync". The fallback is a *feature on screen*, not an apology.
- **Incident text mutation**: generator-produced tickets carry typos/colloquialisms/wrong error codes by default, and the triage trace visibly normalises them. *(Conduct judge fix #2 — and the reason we can say "unscripted".)*
- **Robustness chip (adopted 3 Jul)**: when incident 1's triage confirms the class match, the trace shows a small chip — *"mutation bench: 100 tickets · ‹X› correct-match · ‹Y› safe-degrade · 0 false fast-paths"* (numbers from the Friday-night 100-mutation run). One 5-word spoken aside ("that number is measured"). Pre-answers the hardest Conduct+Technical question on stage instead of hoping it's asked against slide 10.
- **Rollback proof panel (Tier A2)**: at beat R, the moment auto-rollback completes, show pre-state snapshot hash vs restored-state hash side-by-side with a green "state identical" check — "restored exactly" becomes verifiable, not narrated.
- **Cumulative close strip (Tier A2)**: at beat 4 the Baseline Bar collapses into one line — *"Tonight: 3 incidents · manual ≈26 h · Precedent 1 m 28 s"* — spoken as the final sentence before the ask.
- **Attract-mode idle loop (Tier B, ONLY if selected to present)**: from doors-open the console visibly resolves seeded background incidents on its own (deterministic local generator; ROI ticker climbing; `make demo-reset` restores). Opening aside: *"it's been running while you watched the last three teams."* The strongest available "not a scripted demo" signal against 17 boot-on-walk-up competitors.

### 1.3 The three incidents + recovery beat (fixture definitions)

| Beat | Incident | Class fingerprint | Ladder state at start | What the audience sees |
|---|---|---|---|---|
| 1 | EPG/VOD publish fails on a missing-metadata error for a real programme title (from the committed TVmaze GB pull). Ticket text is deliberately messy: *"epg publsh failing agian for the 9pm slot?? err 4102 i think — guide showing blank on skyq"* (wrong error code on purpose; real code is `PUB-4012`). | `publisher × PUB-4012 × schedule_item` | L1 Recommend | Triage normalises the mess → retrieved documented fix + risk class + **rollback plan shown before execution** → human Approve → execute → verify green → real Jira ticket closes with evidence → Memory +1 → human clicks **Promote to Standing Approval**. |
| 2 | Same failure class, different real title, "three days later". | same fingerprint | **Standing Approval** (granted on stage 40s ago) | Fingerprint fast-path, no LLM in the loop: resolved end-to-end in ~15s with a visible on-screen timer; notification + audit trail; ROI ticker ticks; **Revoke** button pointed at. |
| R | Third recurrence of the same class — but the sim injects a publisher 503 mid-write (deterministic flake, triggered by the generator's third-occurrence flag). | same fingerprint | Standing Approval → **demoted** | Verification fails → **pre-generated rollback fires automatically**, pre-state restored on screen → class demoted to L1 → escalation to human with dossier → Jira ticket updated. *(Conduct "recovers from errors" + technical judge's designed beat — trust goes down as well as up.)* |
| 3 | Rights-window conflict (MGM/Starz-style): a title scheduled inside another platform's exclusivity window. A documented fix **exists** but the runbook is restricted to Rights Ops — **as a real Jira issue carrying the "Rights Ops Only" issue-security level (Standard, enforcement verified): Jira itself hides it from the scheduling identity**; the agent runs under scheduling-ops. | `rights × RGT-EXCL-009 × licence_window` | Escalate (permission-denied) | High-risk classification + "fix exists, access denied under this identity" → refusal → investigation dossier → routed to Rights Ops queue in Jira. Speaker line unchanged: "down to the permissions on the runbook itself" — now literally Jira's own permission model. |

---

## 2. THE LIVE 3-MINUTE DEMO SCRIPT (second-by-second)

Target runtime **2:42**. Column "Screen" = what Window A shows unless stated. **[P2: …]** = presenter 2's physical action. Spoken lines are verbatim — rehearse them as written, then loosen only after three clean runs.

### Beat 0 — Hook + the manual "before" (0:00 – 0:25)

| Time | Spoken (Presenter 1) | Screen |
|---|---|---|
| 0:00–0:12 | "When the CrowdStrike outage took Sky News off air, the fix that brought broadcasters back was already written down — a documented admin procedure, applied by hand, thousands of times. One of us watched that same loop every single day inside **Disney+** operations." | **15-second sped-up screen capture** (embedded in the console's opening screen, auto-playing, muted): a real human grinding the manual loop — reads the Jira ticket → keyword-searches the KB, opens two wrong articles → clunky admin console, six clicks deep → emails for approval → waits. Caption burned in: **"The manual loop: 8 hrs 51 min, on average."** |
| 0:12–0:25 | "Read the ticket. Hunt the runbook. Click through an admin console. Wait in an approval queue. Average time: **eight hours fifty-one minutes** — for what is usually minutes of keystrokes once the fix is known. Downtime now costs the Global 2000 **$600 billion a year** — roughly **$200 million per company**. This is Precedent, closing that loop, live." | Time-lapse ends freeze-framed on the approval-queue email; the **Baseline Bar** slides in pinned at top and stays for the rest of the demo. [P2: presses `G` — generator hotkey — arming incident 1.] |

> Timing note: 0:25 for the hook is 5s over the lane brief's "20 seconds" — taken from the close, which VC-judge feedback says should be lean anyway. If rehearsal runs hot, cut "for what is usually minutes of keystrokes once the fix is known."

### Beat 1 — Incident 1: messy ticket → one human click (0:25 – 1:20)

| Time | Spoken (Presenter 1) | Screen |
|---|---|---|
| 0:25–0:37 | "This is MediaCo, our simulated broadcaster — but nothing flowing through it is made up: real programme metadata, real published runbooks, and **twenty-five thousand real incidents** from a public ServiceNow event log seeded as its history." | Console home: incident feed, memory counter showing the pre-seeded corpus ("Precedents: 25,412"), data-provenance footer visible. [P2: hovers the footer for one second — don't read it out.] |
| 0:37–0:50 | "A publish to the TV guide just failed. And look at the ticket — typos, the **wrong error code**, written the way a stressed operator actually writes at 2am. These inputs are mutated every run. This demo is **unscripted** in the only way that matters: the system has never seen this exact ticket." | Incident 1 fires: messy ticket card appears in the feed **and** [P2: one click to Window B] the same issue visible on the real Jira board, then straight back to Window A. Live triage trace: raw text → normalised symptom → corrected error code `PUB-4012` → matched incident class. Green elapsed-bar starts drawing under the Baseline Bar. |
| 0:50–1:03 | "Precedent matches it against every fix this organisation has ever applied and comes back with three things: the **documented fix**, a **risk level**, and — written *before* anything runs — a **rollback plan**. It will not touch a thing yet. It's asking." | Plan panel: retrieved runbook citation, risk class "Low — standard change", execution steps (3 typed API calls), rollback plan rendered *above* the Approve button. Approve button pulses. |
| 1:03–1:12 | "One human click." *(beat — let the execution run in silence for ~3 seconds)* "It executes, verifies the guide is green, and closes the **real Jira ticket** with the evidence attached." | [P2: **clicks APPROVE** — hero click #1.] Steps stream: execute → verify → publish green. [P2: `Cmd+Shift+]` to Window B] Jira ticket transitions to Done with the audit comment, 2 seconds, [P2: back to Window A]. Elapsed bar stops: **~58 s vs 8h51m**. Memory counter ticks +1. |
| 1:12–1:20 | "And here's the part that matters: our operations lead just watched that fix succeed — so she **pre-approves it for next time**." | [P2: clicks **PROMOTE TO STANDING APPROVAL** — hero click #2.] Class badge flips L1 → "Standing Approval"; a **Revoke** button appears beside it and stays visible. |

### Beat 2 — Incident 2: the wow — the second time is free (1:20 – 1:50)

| Time | Spoken (Presenter 1) | Screen |
|---|---|---|
| 1:20–1:28 | "Three days later. Same failure, different show. **Nobody is at the keyboard.**" | [P2: presses `G` — incident 2 fires, then steps back from the laptop, visibly, hands off.] New messy ticket appears; fingerprint fast-path badge lights; a big **on-screen stopwatch** starts. |
| 1:28–1:43 | *(let the stopwatch run — narrate over it, don't fill every second)* "No one approved this ticket — because a human pre-approved this *class* of fix, on stage, forty seconds ago. The approval didn't leave the loop. It **moved earlier in time**." | Full loop replays itself at speed: match → gate check ("Standing Approval — rule SA-014") → execute → verify → Jira closed. Stopwatch stops at **~15s**. Elapsed bar: a sliver next to the 8h51m bar. ROI ticker increments (escalation deflected: $104 → $0.10-class cost). |
| 1:43–1:50 | "**The second time is free.** That's operational memory. And if the ops lead changes her mind —" *(point)* "— one click takes the permission back." | [P2: hovers the **REVOKE** button — hover only, don't click.] Memory counter +1. |

### Beat R — The recovery beat: it can lose trust too (1:50 – 2:10)

| Time | Spoken (Presenter 1) | Screen |
|---|---|---|
| 1:50–1:58 | "So what happens when the remembered fix *doesn't* work? Watch — same failure, third time, but tonight the publisher is flaky." | [P2: presses `G` — incident R fires with the injected 503.] Execution starts under Standing Approval… **verification FAILS, red**. |
| 1:58–2:10 | "Verification failed — so the rollback it wrote *before* executing fires on its own. System restored to exactly where it was. The fix class is **demoted** — it has to earn a human's approval again — and a person gets the escalation, with the whole story attached. It earns trust. It can also **lose** it." | Rollback trace runs → pre-state restored, verify-restore green. Class badge flips Standing Approval → **L1 (demoted)**, demotion event written to the on-screen audit log. Jira ticket updates to "Escalated — automated rollback completed". |

### Beat 3 — Incident 3: the refusal — it knows what it's not allowed to touch (2:10 – 2:28)

| Time | Spoken (Presenter 1) | Screen |
|---|---|---|
| 2:10–2:20 | "Last one. A rights conflict — the kind of error that put MGM in a **$70 million lawsuit** with Starz. Precedent finds the incident, and it knows a fix exists…" | [P2: presses `G` — incident 3 fires.] Triage: high risk. Retrieval result: **"Documented fix exists — access denied under scheduling-ops identity (restricted to Rights Ops)."** |
| 2:20–2:28 | "…but the runbook belongs to the rights team, and Precedent isn't allowed to read it. So it **refuses** — no autonomy, no peeking — packages everything it legitimately knows, and routes it to the humans who are allowed. **It knows what it's not allowed to touch — down to the permissions on the runbook itself.** That's what gets an agent past a CISO." | Refusal card: risk HIGH + permission denied → investigation dossier generated → routed to Rights Ops queue (visible in Jira board, 1-second cut). Audit log shows the denial event. |

### Beat 4 — Close + ask (2:28 – 2:42)

| Time | Spoken (Presenter 1) | Screen |
|---|---|---|
| 2:28–2:36 | "Every ops team drowning in runbooks has this exact loop — media is just where we watched it first. Agents finally make retrieve-*and-safely-execute* possible; the incumbents are priced to meter this workflow, not delete it. ServiceNow paid **$2.85 billion** for Moveworks — the memory layer is worth buying." | Final slide: team (Disney+ alum's face flagged), the loop diagram, ROI ticker's final state, QR code → Jira portal (armed for Q&A trick). |
| 2:36–2:42 | "We're Precedent. We want **two introductions from this room — to anyone running a 24/7 ops or NOC team; media is where we start, not where we stop** — and we're applying to Antler and EWOR with this. Come file a ticket — break it if you can." | Hold the slide. The broadened ask lets generalist VCs act on it (few have broadcast contacts); the last line arms the Q&A party trick and signals "unscripted" confidence. |

**Total: ~2:42.** Buffer to 3:00: 18 seconds.

---

## 3. Q&A weapons (2 minutes — designed, not improvised)

1. **The party trick (pre-armed by the closing line).** If any judge engages: hand them the QR code / have Presenter 2 offer their phone. Judge files a vague, typo-ridden ticket from the phone → Precedent triages it live on the projector, **or** visibly degrades: "low confidence — L0, escalated to a human with its best guess attached". Both outcomes win; rehearse both (§4.3). *(Conduct judge's explicit ask: "no other team will dare do it.")*
2. **"Wasn't that scripted?"** → "The failure classes are staged — the ticket *text* is mutated every run and you just filed one we'd never seen. The runbooks, the metadata and the 25,000-incident history are all real public data; provenance is in the README."
3. **"L3 is autonomy."** → "No — it's a **pre-approved standard change**, the ITIL term. You watched a human grant it, and the revoke button never leaves the screen. Graduation is mechanical: three consecutive verified successes at L2, any rollback demotes — you watched a demotion too. The model never authorises itself; the class key is a deterministic fingerprint, not an LLM label."
4. **"Why won't ServiceNow/Conduct build this?"** (20s, rehearsed until it doesn't sound coached) → "ServiceNow monetises seats and tickets — auto-resolution cannibalises both, which is why they bought Moveworks rather than build it. Conduct makes legacy *legible*; we make it *operable* — we'd rather be their execution layer than their competitor."
5. **Latency/reliability probing** → "The 15-second run is a deterministic fast-path — exact fingerprint match skips model calls entirely; the only LLM text is the summary, with a timeout and a canned fallback. It ran identically with the Wi-Fi off in rehearsal."

---

## 4. Contingency tree (decide in the moment by rule, not judgement)

### 4.0 Window B discipline (write-behind reality)
Jira writes are deliberately async (write-behind): the board may lag the console by seconds. **P2 tabs to Window B only when the console's sync-tick is green**; if the tick isn't green when the script reaches a Jira cut, skip that cut silently — the console's own audit panel carries the beat, and §4.1's line covers any judge question. Add "sync-tick green before every Window B cut" to the rehearsal-gate checklist.

### 4.1 Jira degraded (API hiccup / venue network)
Trigger: amber banner appears, or a Jira cut (Window B) doesn't render in 2 seconds.
**Do:** skip all Window B cuts for the rest of the pitch; the console's own audit panel carries the evidence.
**Say (once, exactly):** *"We've dropped to our cached mirror — everything still executes locally and re-syncs to Jira the moment the venue Wi-Fi does. The live sync is in our submission video."*
Then continue the script unchanged. (The fallback is a locked decision; the banner makes it a resilience feature.)

### 4.2 Console failure (frozen UI, generator misfire, any beat stalls >8s twice)
**Do:** `Cmd+Tab` to QuickTime (Window C), pre-positioned at the chapter marker of the *current* beat — chapter markers at 0:25 / 1:20 / 1:50 / 2:10 mirror the live script exactly, so narration continues without rewriting.
**Say (once):** *"Demo gods. Here's the identical run, recorded last night against this exact build — I'll narrate it live."*
Practise this switch; it must take <5 seconds. A narrated recording delivered confidently loses almost nothing (VC judge explicitly prefers it to dead air).

### 4.3 Rehearsal gates (Saturday morning, before signing off the live plan)
- [ ] **Prerequisite (Friday ~20:00): one full two-presenter run-through against whatever build exists** (video stand-ins for missing beats) — choreography (hotkey `G`, window hops, hero clicks) must not meet the script for the first time on Saturday. Saturday morning is gate-checking, not first contact.
- [ ] 3 consecutive clean full runs at ≤2:45, timed.
- [ ] 1 full run in **airplane mode** (Jira banner path, §4.1 line delivered).
- [ ] 1 full run switching to backup video at beat 2 (§4.2 drill).
- [ ] Party trick: 2 messy phone tickets — one that triages correctly, one that degrades to L0/Escalate — both shown on the projector.
- [ ] `make demo-reset` verified to restore counters/ladder state in <30s.
- **Rule:** if the live console fails any two gates, flip the default: video narrated live + one live element (the Approve click against the cached-mode console). That is the VC judge's preferred configuration anyway — it is a legitimate landing zone, not a defeat.

---

## 5. Stat consistency table (the only numbers anyone may say or caption)

| Claim as spoken/captioned | Exact framing | Source (verified) |
|---|---|---|
| "$600 billion a year" | Splunk 2026 refresh, Global 2000, "up 50% in two years" — always paired in the same breath with the per-company figure | Splunk 2026 press release (locked headline stat) |
| "~$200 million per company" | avg. per Global 2000 company, 2024 | Oxford Economics/Splunk 2024 — verified 3–0 (claims file row 11) |
| "8 hrs 51 min" | average incident MTTR, business hours (8.85h) | MetricNet/HDI (Research README #3) |
| "25,000 real incidents / 141k events" | seeded history corpus, Kaggle ServiceNow-derived event log | say "a public ServiceNow event log" — provenance slide/README |
| ">60% of incidents were repeats with existing fixes" (video only) | ServiceNow's own support org, pre-KCS | ServiceNow KCS case study — verified 3–0 (row 1) |
| "$22 → $69 → $104" (ROI ticker basis; video caption) | cost per ticket L1 → desktop → L3; vintage ~2019–2020, never "2024" | MetricNet whitepaper (primary) |
| "$2.85 billion for Moveworks" | ServiceNow acquisition comp | Research ch. 06 (public deal) |
| "$70 million lawsuit" (incident 3 colour) | Starz paid ~$70M for exclusive windows; MGM admitted improperly licensing 244 titles; settled 2023 | FilmTake 2020 / Bloomberg Law 2023 (ch. 04 §2.2) |
| "resolved in ~15 seconds" | measured on the fingerprint fast-path, on-screen stopwatch is the evidence | our own instrumented demo — never claim it as a general benchmark |
| "cases with a KB article resolve 66% faster" (video caption only) | ServiceNow KCS program | verified 2–1 (row 3) |
| "94% of 24,918 real incidents arrived with their fix already precedented" | fix-class match rate, chronological, computed 3 Jul; symptom-level counterpart 98.6% | our measurement, `data/analysis/uci-baseline-results.md` + script — quote the construction if probed (C7 answer) |
| "precedented repeats still took a median of 18 hours" | **calendar** hours (say "calendar" or omit units-qualifier only in speech, never on a slide); p75 = 136.6h | same measurement — never blend with MetricNet's 8.85 *business* hrs |
| ~~knowledge=true vs false medians~~ | **do not use causally** — KB-using incidents are 9× slower (confound) | permitted colour framing only, per `data/analysis/uci-baseline-results.md` |

**Do NOT say:** "$400B aggregate" (refuted framing) ▪ any LLM accuracy number ▪ "Disney runs WHATS'ON" (say "inside Disney+ operations") ▪ vendor deflection claims without the word "vendor-claimed".

---

## 6. Line fallbacks if a build dependency slips

| Missing element | Script change |
|---|---|
| Real-data seeding (Kaggle/runbooks/metadata) not landed | **Cut the 0:25–0:37 line entirely** — never claim real data falsely. Replace with: "This is MediaCo, our simulated broadcaster — modelled on the real scheduling-rights-publish chain." Flag: this re-opens the Conduct judge's biggest objection; treat data seeding as above-the-line work. |
| Promote/Revoke UI not built | Replace hero click #2 with a policy-file toggle shown on screen + line: "our ops lead marks this class pre-approved — and can revoke it the same way." Weaker; build the buttons (conduct judge sized it at ~2h). |
| Baseline Bar not built | Fall back to the on-screen stopwatch alone + spoken baseline. Keep the 8h51m grey bar as a static image header if nothing else. |
| Recovery injection flaky | Move beat R to the backup video and say at 1:50: "In the submission video you'll see a fix *fail* — verification catches it, the rollback fires, and the class is demoted." Costs live points; the beat is worth building. |
| Incident mutation not landed | Delete the word "unscripted" and the mutation sentence (0:37–0:50). Never claim it falsely — the party trick still partially covers robustness. |

---

## 7. VIDEO SCRIPT (~4:15 — also the Fetch.ai 3–5 min deliverable)

**One video serves both DoraHacks/Conduct and Fetch** (Fetch requires 3–5 min). Per the Fetch judge: **ASI:One gets top billing** — a full 80-second segment in the first half, not a 5-second afterthought. Record **Friday ~21:00 against frozen code** (technical judge); capture the **public ASI:One shared-chat URL and Agentverse profile URLs the same night** from the successful take.

Production: 1080p screen capture (OBS), presenter VO recorded separately over it (quiet room, phone mic is fine), captions as simple lower-third text (no motion graphics — no time). Chapter markers exported for the live-demo backup (§4.2) come from shots 4–8 of this same recording — **one recording session feeds both artifacts.**

### Shot list

| # | Time | Visual | VO (verbatim) | Caption overlay |
|---|---|---|---|---|
| 0 | 0:00–0:14 | **Results-first cold open (adopted 3 Jul):** 12–15s captioned montage, three payoff frames — the 58s-vs-8h51m bar → the 15s stopwatch → the refusal card. No VO; music/beat only. | *(none — captions carry it)* | **8 h 51 m → 15 seconds. Approval never leaves the loop.** |
| 1 | 0:14–0:29 | Cold open narrative: 3s Sky News/CrowdStrike headline still → cut to the manual-loop time-lapse (same asset as live beat 0) | "When the CrowdStrike outage took Sky News off air, the fix was already documented — humans applied it by hand, thousands of times. One of us watched that loop every day inside Disney+ operations." | **Downtime: $600B/yr across the Global 2000 (Splunk 2026) — ~$200M per company** |
| 2 | 0:15–0:40 | Manual loop time-lapse continues; freeze on the approval email; Baseline Bar animates in | "Read the ticket, hunt the runbook, click through a legacy admin console, wait for approval. Average: 8 hours 51 minutes. And at ServiceNow's own support desk, over 60% of incidents were repeats — the fix already existed. Precedent is the agent that remembers every fix your organisation has ever applied, and applies it again: risk-classified, approval-gated, audited, reversible." | **8h51m avg MTTR (MetricNet)** · **>60% repeat incidents (ServiceNow KCS study)** |
| 3 | 0:40–0:55 | Console home; slow pan across incident feed, memory counter (25k+), provenance footer zoomed for 2s | "This is MediaCo, our simulated broadcaster — seeded entirely with real public data: a 141,000-event ServiceNow incident log as its history, real published runbooks, real programme metadata. Tickets live in a real Jira Service Management instance." | **Real data: UCI ServiceNow log (141k events, CC BY 4.0) · GitLab/K8s runbooks · CrowdStrike remediation bulletin · TVmaze/XMLTV programme metadata (CC BY-SA)** |
| 4 | 0:55–1:35 | **Incident 1 condensed** (live-script beat 1 at 1.5× with cuts): messy ticket → triage normalisation → plan+rollback → Approve click → verify → Jira ticket closes → Promote to Standing Approval click | "A publish failure — filed with typos and the wrong error code; inputs are mutated every run. Precedent triages it, retrieves the documented fix, classifies risk, and writes the rollback *before* asking. One human click approves. It executes, verifies, and closes the real Jira ticket with evidence. Then the operations lead pre-approves this fix class — a standing approval she can revoke at any time." | **58 seconds vs 8h51m** · **Human approval — requester ≠ approver, immutably logged** |
| 5 | 1:35–2:55 | **★ ASI:One SEGMENT (the Fetch centerpiece, 80s).** Clean screen recording of a single ASI:One conversation, cursor visible, no console anywhere: (a) user types *"our EPG publish to the evening slot failed, error 4012 i think — can you fix it?"* → (b) agent replies with one well-formatted message: triage, matched precedent, risk class LOW, execution plan + rollback plan, "reply **approve** to execute" → (c) user: "approve" → (d) agent streams: executing → verified → **Jira ticket link (cut 2s to the ticket closing)** → audit-trail link, approver recorded as the chat sender address → (e) *same session*: second incident reported → resolved under Standing Approval in ~15s, timer quoted in the reply. Brief cut to the Agentverse profile pages (3 agents, addresses visible, Innovation Lab badge). | "Everything you just saw needs no custom frontend at all. Precedent's agents live on Fetch.ai's Agentverse and speak the Chat Protocol — the gateway agent, the retrieval agent and the execution agent are separate Agentverse agents passing messages between themselves. Here's the whole loop inside one ASI:One conversation: report the incident in plain English… get the plan and the rollback… type 'approve' — that approval is bound to the chat sender's address and logged as the authorising principal… and the real Jira ticket closes. Same session, second occurrence: fifteen seconds, standing approval. The agents stay registered and running on Agentverse after this hackathon." | **3 agents on Agentverse · Agent Chat Protocol · discoverable via ASI:One** · **agent addresses on screen** · **Approver = chat sender, logged** · **Runs without any custom frontend** |
| 6 | 2:55–3:20 | **Recovery + refusal, back-to-back** (live beats R and 3 condensed): verification fails → rollback fires → demotion event in audit log; then rights-conflict refusal → dossier routed | "When a remembered fix fails, verification catches it, the pre-written rollback restores the system, and the class is demoted — it must earn approval again. And when the only documented fix is one it's not permitted to read — here, a rights runbook restricted to another team — it refuses, and routes a dossier to the humans who are. It knows what it's not allowed to touch, down to the permissions on the runbook itself." | **Auto-rollback on failed verification → class demoted** · **Permission-aware memory: restricted runbook → refusal, audited** |
| 7 | 3:20–3:45 | Scale artifact: terminal/notebook showing the 141k-event ingest run; retrieval + permission-check latency chart; one architecture slide (the only one in the video) with the four integration tiers | "Does it hold at scale? We ingested 141,000 events — twenty-five thousand real incidents — as day-one memory: **94% arrived with their fix already precedented, and those repeats still took a median of 18 hours by hand.** Permission-checked retrieval over that store stays under our latency budget at P99 — measured, with false-negative and false-positive rates over ground-truth queries, in the repo. Real estates aren't clean REST — they're BXF file drops, FTP folders and worse — so the execution layer is a four-tier adapter stack, and every action is a typed call, never free-form. Autonomy is mechanical, not vibes: a class reaches standing approval after three consecutive verified successes, and any rollback demotes it. The whole pipeline runs on open-weight models." | **141k events / 24,918 incidents ingested · 94% pre-matched to a documented fix · P99 permission-check: [measured] ms over the 25k-record store** · **Graduation: 3 verified successes → standing approval; any rollback → demote** · **100% open-weight models (Venice-served), named in README** — ⚠️ caption must match `bench/RESULTS.md` exactly: the bench runs over the UCI-derived 25k-record store (primary), never claim "P99 over 141k events" if the store is 25k records |
| 8 | 3:45–4:15 | Close: team card (Disney+ alum flagged), the loop diagram, links card held 5s | "AI SREs fix broken code — but in real enterprises the fix is almost never code. It's a documented change, waiting to be remembered. ServiceNow paid $2.85 billion for Moveworks; the memory layer is worth buying. We're Precedent — every incident resolved becomes precedent. Repo, live agents and the ASI:One chat linked below." | **github.com/[repo] · ASI:One shared chat · Agentverse profiles** · **Precedent — the second time is free** |

**Runtime ~4:30 with shot 0** (inside Fetch's 3–5 min window; "short and snappy" for Conduct); later shot timestamps shift +14s — treat the table times as durations, not absolutes. If it must shrink toward 3:30: compress shot 4 to 25s and shot 7 to 15s — never shot 5, never shot 0.

**NOT-SELECTED branch inserts (build only if the ~22:00 announcement says no stage — the freed rehearsal hours fund them):** (a) 10-second party-trick shot into shot 4: a visibly uninvolved human thumb-types a garbage ticket on a phone on camera → console triages or safely degrades — the only third-party-verifiable "unscripted" proof an async judge gets; (b) 15-second RESTRICT insert into shot 6: set the runbook issue's security level in Jira → **Jira itself 404s the runbook for the scheduling principal (real enforcement, ≤5 s)** + `acl_sync_applied` → same memory query denied → flip back (replaces the live Q&A hotkey, which has no audience in this branch); (c) the standalone 90-second cut, placed FIRST on the DoraHacks BUIDL page.

### Video recording checklist (Friday, two-stage — insurance first)
- [ ] **~16:00 DIRTY TAKE (insurance, ~1 ph):** OBS-capture whatever runs end-to-end at that point (even incidents 1+2 without recovery, no VO). If the evening collapses, this take + narration is the video. Replace with the clean take only if the freeze holds.
- [ ] **First clean ASI:One E2E run (whenever it happens, PM):** capture a **provisional shared-chat URL immediately** and paste it into the Devpost/DoraHacks drafts — it is the submission artifact unless the 21:00 re-record succeeds. Do not wait for the freeze.
- [ ] Code frozen ~21:00; `make demo-reset`; record shots 4, 6 in one console session (two takes max). **Shot 4's stopwatch: film with a phone clock visible in a PiP corner** — timestamp-anchored proof the 15s fast-path is real (reused on slide 5 + teaser).
- [ ] Record shot 5 in a **fresh ASI:One session** (tests discoverability at the same time — Fetch judge's silent-failure warning); **save the public shared-chat URL immediately**; screenshot Agentverse profiles with addresses + BOTH badges (`tag:innovationlab`, `tag:hackathon`). In the README/submission, point to the exact chat turn where the 15-second standing-approval run happens ("jump to turn 6") so a skimming judge sees the wow without reading the whole thread.
- [ ] Record shot 3 pan + shot 7 terminal run; export chapter markers at live-beat boundaries for the QuickTime backup (§4.2).
- [ ] VO in one pass from this script; assemble; captions; export 1080p. **The 30s teaser strip (§8) is non-negotiable in this edit session** — it is the only before/after a skimming DoraHacks judge sees if the team isn't selected to present. **Standing rule: record a scratch VO over the 16:00 dirty take too** (60s "what we built and why" talking-head insert pre-written) so a broken evening still yields a narratable video.
- [ ] **Pre-export grep: `grep -r '‹' <deck source, README, BUIDL copy>` must return nothing** — the mechanical guard behind the "never ship ‹XX›" rule. Pre-ratified degraded rule: if the bench or mutation run slips, the metrics strip ships with only the measured 94% / 18.2h / 558-class numbers and the missing cells are removed (not bracketed).
- [ ] Upload unlisted + link in DoraHacks BUIDL, **Devpost submission (Fetch — finalize URLs)**, BasedAI PR README (push the video-link commit), and repo README.
- [ ] **If NOT selected to present (announcement ~22:00):** cut the standalone 90-second version Saturday (beats: Baseline Bar → 15s repeat → refusal → ask) and put it FIRST on the DoraHacks BUIDL page, above the 4:15 cut.

---

## 8. 30-SECOND TEASER CUT (deck "demo flow" slide)

Purpose: the deck must carry the demo for anyone skimming DoraHacks without pressing play. Build as 6 stills (or a 30s autoplay loop cut from the video master) laid out left→right on one slide, each with a 5-word caption. No VO; captions only.

| Beat | 5s frame | Caption |
|---|---|---|
| 1 | Messy Jira ticket (typos circled) | "A real, messy ticket arrives" |
| 2 | Plan + rollback panel, Approve button | "Fix found. Rollback written first." |
| 3 | Finger on Approve; Jira ticket closing | "One human click. 58 seconds." |
| 4 | Stopwatch at 0:15, nobody at keyboard | "Next time: 15 seconds. Pre-approved." |
| 5 | Red verify → rollback → "demoted" badge | "Failed fix? Auto-rollback. Trust revoked." |
| 6 | Refusal card + Rights Ops routing | "It knows what it can't touch." |

Strapline under the strip: **"8h51m → 15 seconds — with a human's approval always in the loop."**

---

## 9. Open decisions this lane forces (see flags)

1. **Live-first vs recorded-first — §4.3 IS THE SINGLE SOURCE OF TRUTH.** This script defaults to live-local-first with a drilled video fallback; 03-pitch-deck's logistics section previously said recorded-first — that wording is superseded. The §4.3 rehearsal gates decide mechanically at Sat 09:00 (two failed gates flips the default to narrated-recording + one live Approve click). Ratify this rule in writing at Friday stand-up so it isn't debated on the day; both documents now point here.
2. **The script hard-depends on**: L3 rename + Promote/Revoke UI, Baseline Bar, mutation of ticket text, deterministic recovery injection, fingerprint fast-path, real-data seeding, ASI:One flow working Friday night. Each has a §6 fallback, but every fallback loses judge points that round 1 already priced in.
3. **Demo Day sign-up form closes TODAY 3 Jul 18:00** — someone must submit it this morning regardless of build state.
