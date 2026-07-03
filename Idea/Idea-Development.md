# Precedent — Idea Development v5 (verified & battle-tested, 3 July 2026)

> **Precedent: every incident resolved becomes precedent.**
> v4 (panel-refined) went through a second full multi-agent cycle on 3 July: **live verification of every eligibility rule** (6/6 sources fetched — DoraHacks pages, Fetch hackpack, BasedAI repo + track brief), **hands-on verification of the provisioning stack** (Venice, Jira, ASI:One, Agentverse — all tested with real keys), a fresh 5-judge scoring round with as-of-deadline discounting (Conduct 81 · Fetch 74 · VC 74 · Technical 73 · BasedAI 69), a builder round that attacked and improved the adoption list, and adversarial verification of every new claim. Round history: [refinement/00-panel-verdicts.md](refinement/00-panel-verdicts.md); full audit trail: [refinement/06-session-working-notes.md](refinement/06-session-working-notes.md). The five build specs in [refinement/](refinement/) remain the authoritative detail; this document is the master summary.
>
> Clock: Demo Day sign-up closes **today 3 Jul 18:00** ([form](https://forms.gle/fnUe3vL24wyJo6pD7) — human task, presenters announced ~22:00; treat stage time as probable, not guaranteed); **BasedAI draft PR opens TONIGHT** (live repo README says "3 Jul end of day" — deadline conflict resolved by opening early); DoraHacks closes **4 Jul 22:59 UTC = 23:59 BST**.

---

## 1. The thesis

> **AI SREs fix broken code. In real enterprises, the fix is almost never code — it's a documented admin change. Precedent is the agent that remembers every fix your organisation has ever applied and applies it again: risk-classified, approval-gated, audited, reversible.**

Conduct framing: **Conduct makes legacy legible; Precedent makes legacy operable.** The slow enterprise process: *incident resolution by manual lookup* — a human reads a ticket, searches the KB, follows a runbook in a legacy admin console, waits for approvals, and types resolution notes nobody will find next time. Average MTTR 8.85 business hours for what is often minutes of keystrokes once the fix is known.

**Headline stat (locked):** "$600B/yr for the Global 2000, up 50% in two years" (Splunk 2026 refresh) — delivered in the same breath as the verified **$200M/company** (Oxford Economics 2024, verified 3–0). **Origin story (locked):** Disney+ named outright; never assert "Disney runs WHATS'ON" as vendor fact.

**NEW — our own measured numbers (computed 3 Jul on the real 141k-event UCI corpus, script committed in `data/analysis/`):** in 24,918 real incidents, **94.4% arrived with their exact fix class already precedented** (98.6% at symptom level) — **and those precedented repeats still took a median of 18.2 calendar hours to resolve by hand** (36% breached SLA; 47% were reassigned at least once). 558 recurring classes cover 94.8% of all volume — the autonomy ladder's bootstrap is measured, not asserted. *(The previously-planned `knowledge=true` "killer stat" is inverted in the real data — confounded — and is demoted to labelled colour; see `data/analysis/uci-baseline-results.md`.)*

Why it wins (research-backed): (1) the Disney+ observation is ITIL's codified norm — >60% of ServiceNow's own support incidents were repeats with existing fixes (verified 3–0), and now our own corpus measurement says 94%; (2) $340M+ of AI-SRE VC points at code/infra diagnosis and stops before execution in business apps; (3) the trust envelope (gates/audit/rollback) is the moat — Gartner's 40%-cancellation prediction is about *missing* risk controls; (4) the media wedge is demo-rich and Netflix-proved but unproductised; (5) the memory unit is an **executed fix with provenance**, not RAG-over-runbooks.

---

## 2. Product concept

### The closed loop
DETECT → TRIAGE → RETRIEVE (KB + memory, ACL-filtered) → RISK-CLASSIFY (deterministic policy engine — no LLM in the decision) → GATE → EXECUTE (typed tools) → VERIFY (auto-rollback on failure) → MEMORISE (executed-fix-with-provenance).

### Graduated approval ladder — **"Standing Approval", never "Autonomous"** (locked)

| Level | Behaviour | Example |
|---|---|---|
| L0 Observe | Diagnose + link the documented fix; human does everything | New/unknown incident class |
| L1 Recommend | Prepared plan + rollback; human clicks approve | First occurrence of a known fix |
| L2 Approval-gated execute | Executes after one human approval, fully logged | Fix seen before, medium risk |
| **L3 Standing Approval** | Pre-approved standard change: a **human clicked "Promote to standing approval"** after watching the class succeed; executes on recurrence, self-verifies, auto-rollback; **Revoke button always visible** | Same fix class, N=3 clean successes, low risk — ITIL standard change |
| Escalate | Full investigation dossier routed to the right team | Code-level / novel / high-risk / permission-denied |

Stage line: *"No one approved this ticket — because the operations lead pre-approved this fix class after watching it succeed. Approval moved earlier in time; it never left the loop."*

**Incident-class key:** deterministic fingerprint `sha256(service | error_code | target_object_type)` — the LLM may propose fields, but only extractor-confirmed equality counts; failed extraction ⇒ no fast-path, degrade to L0/L1. Graduation N=3 clean successes; any verification failure or rollback **demotes the class**. **NEW: the extractor's accuracy is measured, not asserted** — a 100-mutated-ticket bench reports correct-match / safe-degrade / false-fast-path rates on slide 10, in the README, and as an on-trace "robustness chip" during the live demo (the pre-answer to both red-team judges' hardest questions).

### Permission-aware memory — A/B/C semantics (BasedAI)
Implemented exactly as worked out publicly in the track Discord and endorsed there by BasedAI's team: **(A)** reading a derived artifact requires satisfying **all** source lineage constraints (conjunction, not one strictest label); **(B)** precompiled effective-policy bitmaps make the check one indexed lookup (the sub-200ms P99 story — O(1) in role count); **(C)** redacted/declassified derivatives only as new governed objects with attestation and lineage. Fail-**closed** when ACL freshness is uncertain. Jira role membership + permission-scheme grants are the synced ACL source of truth (2–3s versioned idempotent polling). **RESTRICT** (ACL change → deny via recompiled policy, reversible — the live demo moment) vs **REVOKE/DELETE** (source removal → quarantine) are distinct paths. *(Attribution discipline: credit the public Discord thread; never say the sponsor "endorsed our design" — the implementation, live-Jira sync, fail-closed cache and working product around it are what's ours. The thread's author is plausibly the BioVault team — the purpose-built competitor whose PR is already open.)*

**NEW — benchmarked in the sponsor's own published evaluation vocabulary** (recovered from the live track brief, which the local exports had missed): FNR/FPR over **10,000 ground-truth queries** on the exact published protocol topology (5 hierarchy levels / 20 roles / 1,000 ACL-tagged docs), P50/P99, end-to-end overhead, ACL drift, time-to-consistency — each vs its published threshold, pass/fail, committed to `bench/RESULTS.md`; **all six named adversarial attacks** covered in `tests/test_adversarial.py`; a realism run over the UCI-derived 25k-record store with real team boundaries; live drift/TTC measured against real Jira role flips (roles 10007/10008 — created and verified this session). This is the differentiation plan vs BioVault: protocol-shaped numbers against a live external ACL source, which a synthetic standalone cannot show.

### Open-weight-only model registry — **VERIFIED, evidence committed** (BasedAI eligibility)
All four pinned Venice models verified live on 3 Jul with public, ungated Hugging Face weights: FAST `qwen3-5-35b-a3b` (Apache-2.0) · SMART `deepseek-v4-flash` (MIT) · HEAVY `deepseek-v4-pro` (MIT) · EMBED `text-embedding-bge-m3` (MIT; embedding models appear only under `GET /models?type=embedding`). `/models` dumps committed to `docs/compliance/` as eligibility evidence. **No OpenAI/Anthropic/closed models anywhere in the loop** — and the trap is real: Venice also serves `claude-fable-5`, `grok-4-3`, and closed embedders (`text-embedding-3-*`); closed models have `modelSource: null` in the API, so the registry asserts every entry's `modelSource` is a huggingface.co URL. Fallback bench corrected against the live catalog (`llama-4-maverick` doesn't exist; `qwen3-6-27b`, `zai-org-glm-5-2`, `kimi-k2-7-code` verified). Ollama-local profile remains stage insurance. README adds a BasedAPIs portability note ("any OpenAI-compatible open-weight endpoint") for the suggested rubric's 20% sponsor-tech line.

---

## 3. Demo & build

### Real data through simulated services (Conduct's realistic-data requirement)
Unchanged plan, now part-executed: TVmaze GB schedule (CC BY-SA — licence re-verified live) + Freeview-EPG XMLTV backup; CC0 Kaggle catalogs for rights (windows synthesised by a stated rule); **UCI ServiceNow event log (141k events / 24,918 incidents, CC BY 4.0 — re-verified) already downloaded, ingest-analysed, and measured** (94.4% match rate, 18.2h precedented-repeat median — `data/analysis/`); ~10 KB articles adapted clause-by-clause from real published runbooks. TMDB/IMDb stay rejected on licence grounds — say so on the provenance slide. Messiness by design: real null-metadata rows, mutated ticket text, the spoken word **"unscripted"**, judge-files-a-ticket offer.

### The demo (full scripts: [refinement/04-demo-and-video-script.md](refinement/04-demo-and-video-script.md))
2:42 live script (18s buffer): 25s manual-loop **before** with the persistent **Baseline Bar** → incident 1 (messy ticket → approve → fix → Jira closes → **Promote**; triage trace shows the measured **robustness chip**) → incident 2 (**15s standing-approval** — "the second time is free") → **live recovery beat** (injected 503 → verification fails → rollback fires with a **pre/post state-hash proof panel** → class demoted) → incident 3 (rights conflict: ACL-denied runbook → refusal + dossier — "it knows what it's not allowed to touch") → **cumulative close strip** ("Tonight: 3 incidents · manual ≈26h · Precedent 1m28s") + broadened ask. Demo-mode decision: **04 §4.3's rehearsal gates are the single source of truth** (live-first default; two failed gates flips it). Video: results-first 14s cold open → the loop → **80s ASI:One centerpiece** (chat replies carry the agent-hop trail footer; approval bound to sender address) → recovery + refusal → scale/bench shot → close. Dirty-take insurance recording at Fri 16:00; provisional shared-chat URL captured at the first clean afternoon run.

### Build order & the checkpoint rule
**Vertical-slice gate (immovable): by Friday 18:00, incidents 1+2+recovery run end-to-end on seeded real data with Baseline Bar and Promote/Revoke.** Mechanical checkpoints — 13:00: memory+loop not integrated ⇒ fire cut-lines 1–2, pre-collapse the third agent; 17:00: slice not running ⇒ incident 3 goes video-only, audit view becomes a JSON tail. 18:30 first full two-presenter run-through; 20:00 second run + **BasedAI draft PR opens**; 21:00 freeze → video + ASI:One capture + hosted-Watcher deploy. **Fetch gates remain non-cuttable and front-loaded** — register in hour one, then **run 10+ test chats with the Watcher** (Agentverse discoverability is activity-gated: ≥10 interactions before evaluation — verified against the docs). Devpost is **not** a submission channel (adversarially verified: hackpack boilerplate from the 2025 edition; EP5 submits via DoraHacks — one courtesy confirm with the Fetch dev advocate closes it). Contingency order unchanged: BasedAI extras → (never Fetch gates) → Jira degrades to cached fallback → incident 3 — **never incident 2**.

### Jira (verified this session — better than planned)
The site is on JSM **FREE** and the planned Standard trial is **unnecessary**: the full ACL surface works on Free via API (role create/membership flip/permission-scheme edit — all tested live; roles `precedent-rights-ops`=10007 and `precedent-scheduling-ops`=10008 created). Caveat handled: Free may not enforce schemes in Jira's own UI — irrelevant, since Precedent enforces at its own retrieval layer and Jira is only the polled source of truth. Remaining 15-min human task: invite a 2nd agent seat (Free allows 3 — verified) so the two ops principals are distinct humans; single-account role-flip is the fallback. Write-behind cache + replay for stage safety; **Window B cuts only on a green sync-tick**.

---

## 4. Pitch (deck spec: [refinement/03-pitch-deck.md](refinement/03-pitch-deck.md); Q&A bank: [refinement/05-scale-story-and-qa.md](refinement/05-scale-story-and-qa.md))

12 slides + 8 Q&A appendix slides; stage cut rehearsed to 2:40. Jargon purge unchanged; the two takeaway lines: **"the second time is free"** and **"it knows what it's not allowed to touch."** Slide 10's metrics strip now carries **real measured numbers** (94% / 18h are computed; P99 + extractor rates fill Friday night — never ship ‹XX›). **~50% no-stage protection (new):** the PDF export gets a self-narrating caption layer; the README first screen becomes the investor above-the-fold (15s GIF of the standing-approval run + metrics table + links); the DoraHacks BUIDL page is rewritten as a 60-second skim artifact (hook line, 6-still teaser, measured-numbers block, per-track compliance links); a "What exists Monday morning" appendix lists the durable artifacts. The ask is broadened one clause: *"two intros to anyone running a 24/7 ops or NOC team — media is where we start, not where we stop."* Slide 12 stays human-written or gets deleted — never faked.

---

## 5. Submissions & track strategy

| Track | Status | Critical notes |
|---|---|---|
| **Conduct £8,000** | Primary — judge round 1: **81**, "1st–3rd if the Fri 18:00 slice lands" | Zero product code at session time is the only gap between 81 and 1st; the checkpoint rule is the defence. Rubric provenance: Discord announcement (the live bounty page carries no criteria) — don't cite "the bounty page" |
| **Fetch.ai** | Committed, gates front-loaded & non-cuttable — judge: **74** | All gates at 0% until Friday AM; ≥10-interaction discoverability rule; provisional shared-chat URL Friday afternoon; hosted Watcher Friday night; Devpost refuted; live prize reality: 1,000 USDT total across 3 winners |
| **BasedAI** | Eligible with committed evidence — judge: **69**, "2nd–3rd; 1st in reach with FNR/FPR + attacks" | **Draft PR TONIGHT** (deadline conflict: repo README says 3 Jul EOD); conformance bench + 6/6 named attacks are the BioVault differentiator; open-weight gate CLOSED with committed dumps |
| Others | Skip | — |

**Deliverables:** DoraHacks BUIDL (repo, deck PDF, ~4:30 video, bounty ticks; **submit a draft early Saturday — BUIDLs stay editable until the deadline, but organizer-question answers are one-shot**) ▪ Demo Day form **today 18:00** (human) ▪ Fetch: ASI:One shared-chat URL + Agentverse profile URLs + both README badges ▪ BasedAI: PR with team folder (template headings verbatim, own `.env.example`, no secrets, video-link commit Saturday + PR comment).

## 6. Human action items the documents cannot do

1. Submit the Demo Day form **before 18:00 today** (screenshot the confirmation into the repo).
2. ~~Verify Venice model IDs~~ ✅ done this session (evidence committed). ~~JSM Standard trial~~ ✅ unnecessary — verified on Free.
3. Invite the 2nd Jira agent seat (15 min) and record its accountId in `.env`.
4. ~~Run the UCI match-rate computation~~ ✅ done this session — 94.4% / 18.2h / 558-class table in `data/analysis/`.
5. Name the BasedAI PR owner **at Friday stand-up**; fork + open the draft PR **tonight ~20:00**; ask a BasedAI mentor which deadline governs and note the answer in the PR description.
6. Write the three one-line team credentials + honest post-Saturday-intent sentence; do the ~2h practitioner outreach or delete the validation line. Rehearse the 15-second "why us / why now / why full-time" triplet as the first Q&A answer.
7. Ratify in writing at stand-up: the demo-mode gate rule (04 §4.3), the 13:00/17:00 checkpoints, and the 22:00 selection-announcement branch (selected → attract-mode + RESTRICT hotkey; not selected → 90s cut + video inserts).
8. Courtesy-confirm with Gautam (Fetch Discord) that DoraHacks is the only submission channel.

## 7. Decision record

Locked 3 Jul (user): Precedent ▪ media-vertical demo ▪ live Jira SM ▪ Fetch committed ▪ BasedAI-aligned ▪ $600B headline ▪ Disney+ named ▪ L3 = "Standing Approval". Session-adopted (v5, within unlocked space — full tiered list and hour ledger in [refinement/06-session-working-notes.md](refinement/06-session-working-notes.md) §7): sponsor-vocabulary conformance bench ▪ 6/6 adversarial suite ▪ extractor accuracy measurement + robustness chip ▪ BasedAI PR moved to Friday night ▪ Devpost refuted ▪ JSM-Free finding ▪ UCI numbers on-slide ▪ no-stage submission-surface package ▪ checkpoint rule ▪ hosted Watcher Friday night ▪ agent-hop trail + TVmaze snapshot quote in chat ▪ temporal-embargo demoted to bench-test-only (no demo beat). Rejected (one line each, ibid.): on-chain Payment Protocol; dual-surface ticket; mid-demo degraded toggle; judge-ticket-as-incident-2; final-slide counter wiring. Ledger closing balance: **70.5 ph committed / 76.0 with schedule-gated Tier A2 / ≈79.5 absolute worst case** against 60–80 capacity — upper tiers mechanically gated, Tier C unfunded below the 80-end.
