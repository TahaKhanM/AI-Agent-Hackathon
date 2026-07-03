# Precedent — Pitch Deck (final build spec)

> Lane deliverable, refinement round 2 — 3 July 2026.
> This file IS the deck: drop each slide into Pitch/Keynote/Google Slides as written.
> 12 core slides + 8 appendix (Q&A backup) slides. Stage run-of-show, 90-second cut, and Demo Day logistics at the bottom.
>
> **Design rules for whoever builds the slides:** dark background, one accent colour, max ~15 words of body text per slide, numbers set 3–5× body size, no bullet lists longer than 3 on any core slide. Every vendor-claimed number carries a small "(vendor-claimed)" superscript — honesty is part of the brand. All agent names (Watcher/Librarian/…), YAML, ACL, SoD, and "five-element schema" vocabulary is BANNED from core slides — it lives in speaker notes and appendix only (VC judge instruction: the words the room should remember are *"the second time is free"* and *"it knows what it's not allowed to touch"*).

---

## CORE DECK (12 slides)

---

### Slide 1 — Title

**On-slide text:**

> # Precedent
> ### Every incident resolved becomes precedent.
> Team ‹name› · UK AI Agent Hackathon EP5 · Conduct "Make Legacy Move" · Fetch.ai · BasedAI

**Visual/layout:** Wordmark centred, tagline under it. Bottom strip: track logos, small. Nothing else. This slide is on screen while you walk up — it earns zero seconds of talk time.

**Speaker notes:**
- (Say nothing on this slide — go straight into the cold open as slide 2 appears.)
- Clicker in hand, demo machine already mirrored, video cued.

---

### Slide 2 — Cold open: the loop (problem, part 1)

**On-slide text:**

> **Something breaks → find the manual → click through an admin console.**
>
> # 8.85 hours
> average time to resolve an incident — for a fix that is often minutes of keystrokes once it's known

**Visual/layout:** The three-step loop as a large horizontal diagram (icons: alert → document → cursor-on-console). The 8.85 hours number dominates the lower half. Optional: faded screenshot of a real legacy admin console behind the number.

**Speaker notes:**
- Cold open, verbatim: *"When Sky News went off air in the CrowdStrike outage, the fix was a documented admin procedure — executed thousands of times, by hand. One of us watched that same loop every day inside **Disney+** operations: something breaks, find the manual, click through an admin console."*
- 8.85 business hours is MetricNet/HDI average incident MTTR; most of it is queueing and lookup, not fixing.
- Do NOT claim Disney runs any particular vendor — first-hand internship observation only (research caution, locked).

---

### Slide 3 — The problem is universal and priced (problem, part 2)

**On-slide text:**

> # $600B / year
> downtime cost across the Global 2000 — up 50% in two years *(Splunk, 2026)*
> ≈ **$200M per company** *(Oxford Economics/Splunk, 2024)*
>
> ## >60% of incidents are repeats — the fix already exists, nobody can find it *(ServiceNow's own support org)*

**Visual/layout:** $600B huge, the per-company figure directly beneath it in the same breath (pre-empts "inflated number" pushback). The >60% line as a highlighted band across the bottom. No other text.

**Speaker notes:**
- Pair the two numbers in ONE sentence: *"Downtime now costs the Global 2000 six hundred billion dollars a year — about two hundred million per company — and here's the absurd part: at ServiceNow's own support desk, more than sixty percent of incidents were repeats whose fix already existed but couldn't be found."*
- Sources (verified 3–0 in our adversarial pass): Splunk 2026 refresh (https://www.prnewswire.com/news-releases/the-600-billion-wake-up-call-new-splunk-research-reveals-downtime-is-a-systemic-business-crisis-302774919.html); Oxford Economics/Splunk 2024 $200M/company (https://www.oxfordeconomics.com/resource/the-hidden-costs-of-downtime-the-400b-problem-facing-the-global-2000/); ServiceNow KCS case study PDF (>60% repeats).
- If pressed in Q&A: our unit economics don't depend on the macro number — every deflected escalation is a $22–$104 ticket avoided (Appendix A1).

---

### Slide 4 — Solution (the thesis)

**On-slide text:**

> **AI SREs fix broken code. In real enterprises, the fix is almost never code — it's a documented admin change.**
>
> ## Precedent remembers every fix your organisation has ever applied — and applies it again.
> risk-classified · approval-gated · audited · reversible

**Visual/layout:** Thesis sentence top, product sentence centre-stage, the four properties as four small badges in a row. One-slide closed-loop ribbon along the bottom: detect → find the documented fix → check risk → get approval → execute → verify → remember. Seven plain-English words, no agent names.

**Speaker notes:**
- *"Precedent is the agent that remembers every fix your organisation has ever applied and applies it again — with a human approval gate, a full audit trail, and a rollback prepared before anything runs."*
- The memory unit is not a document — it's an **executed fix with provenance**: symptom, verified fix, who approved it, risk class, rollback, outcome. That's the compounding asset (slide 10).
- Conduct framing if useful: *"Conduct makes legacy legible; Precedent makes legacy operable."*

---

### Slide 5 — Before / After (the 90-second stopwatch slide)

**On-slide text:**

> **Same incident. Same fix.**
>
> Manual: ticket → search KB → admin console → approval queue → resolve
> ████████████████████████████████████ **8.85 hrs**
>
> First time with Precedent (human approves) ▌ **~60 s**
> Every time after (pre-approved) ▏ **~15 s**
>
> ### The second time is free.

**Visual/layout:** Three horizontal time bars to scale (the 8.85-hr bar spans the full slide width; the 60 s and 15 s bars are slivers — the visual joke IS the point). "The second time is free." as the kicker line. **This exact graphic is also rendered as a persistent header in the live demo console**, where each incident draws its real elapsed-time bar underneath the manual baseline (Conduct judge's explicit ask: a stopwatch a non-engineer reads instantly).

**Speaker notes:**
- *"Non-negotiable picture: the manual loop is eight and a half hours of queueing and searching. Precedent's first resolution takes about a minute — because a human still clicks approve. Every repeat after that takes fifteen seconds. The second time is free."*
- The 15 s figure is engineered, not hoped-for: deterministic fingerprint fast-path skips LLM triage for known incident classes (Appendix A3).
- This slide appears within the first 90 seconds of the pitch. Do not move it later.

---

### Slide 6 — The demo (use case + demo flow)

**On-slide text:**

> **MediaCo** — a simulated broadcaster · **real data** · **live Jira Service Management** · **unscripted inputs**
>
> 1. **Broken EPG publish** → plan + rollback → human approves → fixed in ~60 s, Jira ticket closes itself
> 2. **Same class recurs** → pre-approved standard change → fixed in ~15 s
> 3. **Rights conflict, restricted runbook** → Precedent **refuses** and routes to the right team

**Visual/layout:** Three numbered panels with a stopwatch icon on each (60 s / 15 s / "refused"). Provenance strip along the bottom in small type: *"Seed data: real public runbooks (GitLab, Kubernetes SIG, the published CrowdStrike remediation), real programme metadata, and a 141k-event public IT-incident log ingested as fix history. Incident text is mutated at generation time — typos, vague symptoms, missing codes."* This is the slide on screen when you cut to the demo recording.

**Speaker notes:**
- Say the word **"unscripted"** on stage: *"The incident text is deliberately mangled — typos, wrong terminology, missing error codes — and any judge can file a ticket from their phone right now; Precedent triages it or safely escalates."* (Conduct's 35% criterion, answered out loud.)
- Incident 3 payoff in ONE sentence, no jargon: *"It isn't allowed to read that runbook — so it refused, and routed the incident to the team that is."* Then: *"It knows what it's not allowed to touch — that's why an enterprise lets it in the door."*
- Pre-empt the simulator question in one clause: *"MediaCo mirrors the real scheduling/rights/EPG chain — our agents only touch it through the same API surfaces the real vendors expose."*
- Demo execution: incidents 1–2 pre-recorded screen capture narrated live; ONE live element — the Approve click (cached-Jira fallback if venue Wi-Fi dies). Incident 3 in the recording.

---

### Slide 7 — Control, not autonomy (the trust story)

**On-slide text:**

> **Autonomy is earned per incident-class — and a human grants it.**
>
> L0 Observe → L1 Recommend → L2 Execute after approval → **L3 Standing Approval** *(pre-approved standard change)*
>
> [ Promote to standing approval ]   [ Revoke ]
>
> ### Approval moves earlier in time. It never leaves the loop.

**Visual/layout:** The ladder as four ascending steps; L3 visually labelled "Standing Approval", never "Autonomous". Render the two buttons exactly as they appear in the product UI (screenshot the real buttons). Kicker line big at the bottom.

**Speaker notes:**
- *"No one approved that second ticket — because the operations lead pre-approved the fix class after watching it succeed, with one click. Standing approval is an ITIL standard change: earned through verified history, revocable with one click, demoted automatically on any failure."*
- The permission decision is deterministic policy — **no LLM ever authorises an action**; the model proposes, the policy engine and a human identity dispose (details Appendix A3).
- Why this is the product, not a chore: only ~8% of leaders accept full autonomy, ~90% demand audit logs, and Gartner says >40% of agentic projects will die by 2027 on inadequate risk controls. The guardrails ARE the purchase criterion.

---

### Slide 8 — How it works (tech, one slide max)

**On-slide text:**

> Five specialised agents · deterministic policy engine · permission-aware memory
>
> [diagram]
>
> Live Jira Service Management · open-weight models end-to-end · agents live on Fetch.ai Agentverse / ASI:One

**Visual/layout:** ONE diagram: tickets/alerts enter left (Jira logo), five unnamed agent nodes in a pipeline, a shield icon between "decide" and "execute" labelled *"deterministic policy gate — no LLM in the authorisation path"*, memory cylinder underneath labelled *"executed fixes, permission-aware"*, arrows out to "target systems". Three-item tech strip at the bottom. That's it — resist all urges to add boxes.

**Speaker notes:**
- 15 seconds max if spoken at all: *"Five specialised agents run the loop; a deterministic policy engine — not the model — decides what may execute; and the memory inherits the permissions of the documents and tickets it learned from, live-synced from Jira."*
- For Fetch judges (video, not stage): three of the agents are registered on Agentverse and collaborate over Chat Protocol; the full loop runs inside an ASI:One conversation — public shared-chat URL in the submission.
- For BasedAI judges (README, not stage): 100% open-weight pipeline (Venice-served Llama/Qwen + open-weight embedder), models named in the README; the permission-aware memory ships as a standalone library Precedent imports.

---

### Slide 9 — Nobody does this (competition / white space)

**On-slide text:**

> AI SREs **stop at diagnosis**. RPA is **incident-blind**. Runbook automation only runs **pre-written scripts**. ServiceNow deflects tickets **inside its own walls**.
>
> ## The closed loop — retrieve *your* documented fix → approval-gated execution in third-party systems → verified, audited, **remembered** — is unclaimed.
>
> ServiceNow paid **$2.85B** for Moveworks — resolution memory is worth buying.

**Visual/layout:** Incident-lifecycle bar (Detect · Diagnose · **Fix** · Learn) with competitor logos crowded over Detect/Diagnose and a glowing empty gap over Fix+Learn where Precedent's mark sits. Moveworks line as the proof-strip at the bottom.

**Speaker notes:**
- $340M+ of VC since 2024 (Resolve AI at $1B on ~$4M ARR) is pointed at *code and infra* incidents, and almost all of it stops at "here's the likely cause."
- Honest scoping if pushed: Komodor's Klaudia and Digitate Ignio do execute remediations *in their silos* (K8s / their own automations) — the whitespace is the **combination**: org's own documented fixes + business-app admin surfaces + graduated approval + compounding memory.
- Why incumbents don't: ServiceNow monetises seats and tickets — auto-resolution cannibalises both; they *acquire* this layer (Moveworks $2.85B, Mar 2025 — https://newsroom.servicenow.com/press-releases/details/2025/ServiceNow-to-extend-leading-agentic-AI-to-every-employee-for-every-corner-of-the-business-with-acquisition-of-Moveworks-03-10-2025-traffic/default.aspx). That's also the exit narrative.

---

### Slide 10 — The moat: memory that compounds

**On-slide text:**

> Every resolution writes a record: **symptom → verified fix → approver → risk → rollback → outcome.**
>
> incident → fix → **precedent** → faster next time → more incidents trusted to it → ↻
>
> **141,000** real incident events ingested · **‹XX›%** matched to a documented fix · **P99 ‹XX› ms** permission-checked retrieval

**Visual/layout:** Flywheel diagram centre (four arrows in a circle). The three scale numbers as a metrics strip — **placeholders ‹XX› filled Friday night from the actual benchmark run** (Conduct judge's "scale artifact" ask). If the 141k ingest is cut from the build, replace the strip with the live demo counters (fixes remembered / tickets deflected / $ saved).

**Speaker notes:**
- *"Documents go stale; executed fixes with provenance don't. Every incident Precedent resolves makes the next one faster and safer — accuracy becomes a function of tenure in the account. That's the moat Moveworks proved and ServiceNow paid $2.85B for."*
- Cold-start answer: day one it ingests the KB and runbooks every org already has (that's the Disney+ observation) and runs in observe/recommend mode; KCS alone is worth 52% faster time-to-relief (verified). The ladder climbs on evidence.
- "% of incidents matched to a documented fix" is a stat the industry doesn't publish — we instrument it live in the product.

---

### Slide 11 — Market: beachhead, not ceiling (why now)

**On-slide text:**

> **Media ops first** — regulated failure (Ofcom), 24/7 deadlines, legacy consoles
> **One MSP deal = hundreds of channels** — Encompass runs 1,200+ channels/day; Amagi 5,000+ deliveries *(vendor-claimed)*
> **Then: every ops team drowning in runbooks** — every ticket deflected saves **$22 → $69 → $104** per escalation tier
>
> *Agents made retrieve-and-safely-execute possible this year. Incumbents are priced to meter the workflow, not delete it.*

**Visual/layout:** Three ascending chevrons (Broadcaster → MSP channel → All ops). The $22/$69/$104 ladder as three stacked coins/bars. Why-now line italicised at the bottom.

**Speaker notes:**
- Why media first, 10 seconds: *"First-hand pain, regulator-documented failures, and Netflix proved the pattern in-house — fifty-six percent of a failure class auto-remediated — but nobody sells it to everyone below Netflix scale."*
- The MSP channel is the wedge-scaler (research ch. 04 §7): playout MSPs (Red Bee ~2,500 staff/2.7M+ hrs-yr, Encompass 1,200+ channels daily, Globecast 150+ channels, Amagi 800+ chains — all vendor-claimed marketing figures, say so if pressed) sell fixed-price SLA ops, so every auto-remediated incident is pure margin, and their runbook/ITSM discipline means the knowledge base already exists.
- $22/$69/$104 = MetricNet cost-per-ticket at L1/desktop/L3 — primary source is MetricNet's own whitepaper, vintage ~2019–2020 (quote the numbers, not fake freshness): https://www.metricnet.com/wp-content/uploads/2020/08/ROI-of-Service-and-Support-v1.pdf

---

### Slide 12 — Team + Ask

**On-slide text:**

> [photo] ‹Name› — watched the loop inside **Disney+ operations**
> [photo] ‹Name› — ‹one-line credential›
> [photo] ‹Name› — ‹one-line credential›
>
> ## The ask: two intros to broadcast-ops or MSP design partners — and we're applying to Antler & EWOR with this.
>
> *ServiceNow paid $2.85B for resolution memory. We're building the version that executes.*

**Visual/layout:** Faces left (small, human), ask centre in the largest type on the slide, Moveworks kicker as the closing line — it is literally the last thing the room reads.

**Speaker notes:**
- Deliver the ask as a sentence, not a slide-read: *"We're taking Precedent to broadcast-ops design partners. We want two introductions from this room, and we're applying to Antler and EWOR with it."*
- If external validation landed (practitioner messages went out Friday): add one line — *"We put this in front of ‹N› ops engineers this week; every one of them said the refusal demo is what gets it past their CISO."* Only say it if true; drop cleanly if not.
- Last words before Q&A: *"The second time is free."*

---

## APPENDIX (Q&A backup slides — never shown unprompted)

### A1 — Every number, sourced

| Claim | Number | Source / label |
|---|---|---|
| Global 2000 downtime bill | $600B/yr, +50% in 2 yrs | Splunk 2026 press release (exact framing) |
| Per-company downtime cost | $200M/yr | Oxford Economics/Splunk 2024 — **verified 3–0** |
| Repeat incidents with existing fixes | >60% | ServiceNow KCS case study (their own support org) — **verified 3–0** |
| Cost per ticket L1 → desktop → L3 | $22 → $69 → $104 | MetricNet whitepaper, primary, vintage ~2019–2020 |
| Average incident MTTR | 8.85 business hrs | MetricNet/HDI |
| KB-attached cases resolve faster | 66% faster; KCS = 52% faster relief | ServiceNow — verified |
| Major human-error outages = procedure failures | 85% | Uptime Institute 2024 |
| Leaders accepting full autonomy / demanding audit logs | ~8% / ~90% | 2025–26 surveys |
| Agentic projects cancelled by 2027 (risk controls) | >40% | Gartner, Jun 2025 |
| Netflix auto-remediates a failure class in-house | 56% | Netflix TechBlog |
| Moveworks acquisition | $2.85B | ServiceNow newsroom, Mar 2025 |
| Deflection precedent | 50–88% | Moveworks — **vendor-claimed** |

Layout: plain table, small type. Purpose: when any number is challenged, jump here and show the sourcing discipline itself — it scores.

### A2 — Data provenance (the "not made up" slide)

- KB seeded with **real published runbooks**: GitLab public runbooks repo, Kubernetes SIG runbooks, the actual CrowdStrike channel-file remediation bulletin.
- Fix history bootstrapped from a **public ServiceNow-derived incident event log (~141k events / ~25k incidents, Kaggle)**.
- Scheduler/rights/EPG seeded with **real programme metadata** (TMDB / BBC /programmes / XMLTV feed — whichever the build landed).
- Incident text **mutated at generation time** (typos, colloquial symptoms, missing codes, red herrings) + live judge-filed tickets accepted.
- Speaker line: *"The systems are simulated; the content is real."*

### A3 — Standing approval: exact semantics (technical judge bait)

- Incident-class key = **deterministic fingerprint** (service, error_code, target-object type) computed from structured fields — the LLM proposes candidate matches, but a match only counts on fingerprint equality. **The model never authorises itself.**
- Graduation rule, printed in the audit log: **3 consecutive verified L2 successes, zero rollbacks → eligible; a human clicks "Promote to standing approval." Any verification failure or rollback auto-demotes the class to L1** and logs a demotion event.
- Rollback plan is generated **before** execution and is a precondition of the gate; verification failure fires it automatically.
- Approver identity is recorded per action (in chat flows, the Chat Protocol sender address; in production, SSO identity — the control structure is identical).

### A4 — Permission-aware memory (BasedAI depth)

- Every memory record stores the **full set of source permission constraints** (from the Jira/KB articles and tickets it derives from); retrieval must satisfy **all of them** — conjunction, not one strictest label.
- A precompiled effective-policy cache makes the check one indexed lookup — that's the P99 number: **‹XX› ms over ‹N›k ACL-tagged records, concurrent queries** (fill from benchmark).
- **Revocation cascades**: revoke the source article in Jira → derived fix records, summaries and embedding entries become unretrievable within seconds, with a denial audit event. (60-second segment in the video.)
- Fallback mode **fails closed**: if ACL freshness is uncertain, the record is not served.
- Ships as a standalone library; Precedent imports it. 100% open-weight models, named in README.

### A5 — "Why won't ServiceNow / Conduct build this?"

- ServiceNow monetises seats + tickets; auto-resolution cannibalises both (their hybrid-pricing hedge is public — The Register, Dec 2025). They **acquire** this layer: Jeli $29.7M, Moveworks $2.85B. We're building what they buy.
- Now Assist acts inside ServiceNow workflows; we execute inside **third-party business-app admin surfaces** — their walls are our territory.
- Conduct makes legacy **legible**; we make it **operable** — complement, and their brief told us to build exactly this ("start with the process").
- 20-second stage version, rehearsed: *"They meter the workflow; we delete it. Incumbents don't ship products that shrink their own ticket count — they buy them. That's the Moveworks story."*

### A6 — Integration reality (the "you built the simulator" defence)

- Four-tier surface strategy from our research: **REST APIs** (the lucky case — WhatsOn-class schedulers) → **BXF/file exchange** → **watched-folder/FTP drops** → **RPA-style console driving** (last resort, same approval gates).
- The Operator only executes **typed tool calls** per surface — never free-form shell; tier 3/4 fixes start life at L0/L1 and stay approval-gated.
- MediaCo's endpoints deliberately mirror the surfaces the real vendors document (Grass Valley STRATUS: "traffic integration via BXF files").

### A7 — Fetch.ai deliverables

- ‹3› agents registered on **Agentverse** (addresses on-slide), collaborating over uAgents Chat Protocol; Innovation Lab badge; agent stays live post-hackathon.
- Full loop inside **ASI:One**: report incident in chat → plan + rollback → "approve" → Jira ticket transitions and closes → audit link. Public shared-chat URL: ‹link›.
- Approval principal = Chat Protocol sender address, logged as the authorising identity.

### A8 — Liability & regulated ops (VC Q&A)

- Precedent executes only **documented, previously-verified fixes** at the customer's chosen autonomy level — the customer's own change-management policy, encoded and enforced. Shadow-mode-first deployment at MSPs.
- Headline metric we quote: per-class **execution success + rollback rate** from real runs — never model benchmarks (the incident.io-vs-Rootly accuracy-theatre war is the cautionary tale).
- Every action carries: input, reasoning, confidence, action, authorising rule + approver — the audit schema regulators and SOC 2 auditors already recognise.

---

## STAGE RUN-OF-SHOW (3-min pitch — rehearse to **2:40**)

| Clock | Slide(s) | Beat |
|---|---|---|
| 0:00–0:20 | 1→2 | Cold open: CrowdStrike/Sky News + Disney+ loop. 8.85 hours. |
| 0:20–0:40 | 3 | $600B → $200M/company → >60% repeats, one breath. |
| 0:40–1:00 | 4→5 | Thesis + stopwatch bars. Land *"the second time is free."* |
| 1:00–2:05 | 6 | Demo: pre-recorded incidents 1–2 narrated live, **one live Approve click**; incident 3 refusal ends the recording. Say **"unscripted"** and offer the judge-files-a-ticket moment. |
| 2:05–2:20 | 7 | Ladder + Promote/Revoke: *"approval moves earlier in time — it never leaves the loop."* |
| 2:20–2:40 | 11→12 | Beachhead→MSP→everyone in one sentence; team; the ask; close on Moveworks $2.85B. |

Slides 8, 9, 10 are **not spoken on stage** — they live in the submitted deck and are jumped to in Q&A (competition question → 9; moat/cold-start → 10; "how does it work" → 8 then A3/A4).

## 90-SECOND SHORT VERSION (if the schedule slips and pitches get cut)

Slides **2 → 5 → 6 (incident-2 clip only, 25 s) → 7 → 12**. Script: loop + 8.85 hrs (15 s) → stopwatch bars (15 s) → 15-second autonomous repeat clip (25 s) → "approval never leaves the loop" (15 s) → ask + Moveworks close (20 s). Everything else is Q&A material. The two lines that must survive any cut: *"the second time is free"* and *"it knows what it's not allowed to touch."*

## DEMO DAY LOGISTICS (Sat 4 Jul, Blackett LT1, 10:00–16:30)

- **Format: 5 min total = ~3 min pitch + 2 min Q&A, in-person only.** Judges are VCs (LocalGlobe, Antler, EWOR) + sponsor judges. Day opens with an EWOR fireside chat — expect schedule drift; have the 90-second cut ready.
- **Demo Day sign-up form was due TODAY 3 Jul 18:00** (https://forms.gle/fnUe3vL24wyJo6pD7); presenters announced ~22:00 tonight. DoraHacks submission (repo + this deck as PDF + video) due 4 Jul 23:59.
- **Reliability protocol:** freeze demo code Fri ~21:00; record the demo video and ASI:One shared-chat session that night against the frozen build. Incidents 1–2 pre-recorded for the stage; ONE live element (the Approve click) running on the cached-Jira fallback by default. Airplane-mode rehearsal must pass. Never demo ASI:One live on stage — it lives in the video.
- **Rehearse to 2:40, three full run-throughs**, one of them with Wi-Fi off and one against a stranger (jargon check: if they can't repeat "the second time is free" and "it knows what it's not allowed to touch," cut more words).
- **Kit:** laptop + HDMI/USB-C dongle, video file LOCAL on disk (never streamed), clicker, phone with the judge-ticket Jira form open as the Q&A party trick, printed one-pager of Appendix A1 numbers for the presenter's pocket.
- **Q&A assignments:** one person owns numbers (A1), one owns tech (A3/A4/A6), one owns market (A5/A8). Never two people answering one question.

## CONDUCT-FLOW COMPLIANCE MAP (deck requirement: problem, solution, product, tech, use case, demo flow)

problem = slides 2–3 · solution = slide 4 · product = slides 5, 7, 10 · tech = slide 8 (+A3/A4/A6) · use case = slides 6, 11 · demo flow = slide 6 + run-of-show table.

## PLACEHOLDERS TO FILL BEFORE EXPORT (owner: whoever builds the slides)

1. Slide 10 metrics strip: ‹XX›% match-rate and P99 ‹XX› ms from Friday-night benchmark — **if the 141k ingest is cut, swap in live demo counters instead; do not ship empty placeholders**.
2. Slide 12: team names/photos/credentials + (only if true) the practitioner-validation line.
3. Slide 6 provenance strip: replace with the datasets actually ingested.
4. A7: real Agentverse addresses + ASI:One shared-chat URL, captured Friday night.
5. Team name on slide 1; export deck as PDF for DoraHacks.
