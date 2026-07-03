# Precedent Demo Day Deck — Complete Build Brief (for a fresh Fable 5 session)

You are about to BUILD the Precedent pitch deck for UK AI Agent Hackathon EP5. This one file is your complete orientation: it tells you what Precedent is, which rubrics the deck must satisfy, exactly how to build and export it, which numbers are legal, what is real today, and every honesty rule you must obey. It does **not** replace the two spec files you must open — it points you at them and constrains how you use them. If this brief and `03-pitch-deck.md` ever disagree on wording or a number, **the spec wins.**

---

## 1. Purpose, audience & how to use this file

**Purpose.** This is the self-contained brief for a fresh Claude/Fable 5 session whose job is to BUILD (transcribe, lay out, export) the Precedent Demo Day deck — 12 core slides + 9 appendix slides, plus two PDF exports. You have repo access. Read this file, then open the two source-of-truth files it names, then build. It orients and constrains you; it is **not** the deck.

**CRITICAL AUDIENCE NOTE — this is a no-speaker, self-narrating deck.** In this initial stage the deck is shown to the **founders directly, with NO speaker and no live narration**. Every core slide must **self-narrate**: a founder reading in silence must get the full argument from the slide alone. This is the single most important adaptation for THIS build and it changes the caption layer (see §7). The original spec assumed a thin one-line grey caption for a live speaker; you must instead fold the **substance of each slide's speaker notes** onto the slide as a visible, readable **self-narration band** (2–3 tight lines beneath or beside the hero element), while still RETAINING the full speaker notes in the slide notes field for later live/stage use.

**A note on "Fable."** *You* run on the Claude **Fable 5** model, which is the expected, correct author tool for this deck. This is UNRELATED to `claude-fable-5` being a **banned closed model inside the Precedent product runtime** (the runtime is open-weight-only; a closed `claude-fable-5` in `precedent/models.py` would be eligibility-fatal). "Fable 5 authors the deck" is fine; "claude-fable-5 in the runtime" is not. Two different uses of the same word — never conflate them on a slide or in the README.

**Source-of-truth files you MUST open first-hand (do not build from this brief's paraphrases):**

| File | Role |
|---|---|
| `Idea/refinement/03-pitch-deck.md` | THE deck. Every slide's on-slide text, layout, and speaker notes, run-of-show, PDF-export layer, placeholder list — already written and judge-reviewed. |
| `Plan/workflows/N1-deck-build.md` | THE build method: format options, the concrete theme hex/pt values, build-sheet-per-slide, `[[WAIT]]` cells, export sequence, DONE checklist, cut rules. |
| `data/analysis/uci-baseline-results.md` | Our measured numbers (94.4% / 98.6% / 18.2h calendar / 558 classes) with exact framing — for the QC pass. |
| `Research/00-verified-claims.md` | Every industry number's verified source + caveat — for the QC pass. |

**THE GOLDEN RULE (stated once here, repeated throughout).** On-slide text and every figure are copied **VERBATIM** from `Idea/refinement/03-pitch-deck.md`. Your job is *transcription with discipline, not creative writing*. Never reword, shorten, or "improve" any on-slide copy or figure. This context file is a MAP; the spec is the territory. Where this brief paraphrases a line, go to the file for the exact wording before it reaches a slide.

---

## 2. The 60-second pitch

- **Thesis (verbatim, slide 4):** "AI SREs fix broken code. In real enterprises, the fix is almost never code — it's a documented admin change."
- **One-liner (product):** "Precedent remembers every fix your organisation has ever applied — and applies it again." Four badges: risk-classified · approval-gated · audited · reversible.
- **Companion framing (Conduct):** "Conduct makes legacy legible; Precedent makes legacy operable."
- **Tagline:** "Every incident resolved becomes precedent."
- **The two memorable lines the room MUST remember (load-bearing; must survive any cut, and are the last words before Q&A):**
  1. **"the second time is free"**
  2. **"it knows what it's not allowed to touch"**

The loop, in seven plain words (no agent names): detect → find the documented fix → check risk → get approval → execute → verify → remember.

---

## 3. The hackathon & the rubric it must hit

UK AI Agent Hackathon EP5 × Conduct, Imperial College London, 28 Jun – 4 Jul 2026. One BUIDL can apply to up to 10 DoraHacks bounties — pitch once, tick every bounty. Precedent targets three tracks, each with a **different reward function and a different eligibility gate**. The deck must speak to all three at once.

**Demo Day / format.** Sat 4 Jul, Blackett LT1, 10:00–16:30, in-person only. **5 min total = ~3 min pitch + 2 min Q&A.** Judges are VCs (LocalGlobe, Antler, EWOR) + sponsor judges. DoraHacks submission (repo + deck PDF + video) due 4 Jul 23:59. Recorded video target 3–5 min (Fetch's band; also satisfies Conduct's "short and snappy"). **Rehearse to 2:40, not 3:00**, and have the 90-second cut ready for schedule drift. Never demo ASI:One live on stage — it lives in the video.

| Track | Prize | What it rewards that the deck must show | Eligibility gate → which slides answer it |
|---|---|---|---|
| **Conduct "Make Legacy Move"** | £8,000 (biggest single track) | Technical execution 35% ("real engineering, not a wrapper around a prompt"; recovers from errors on messy/ambiguous input) · Impact & speed-up 30% (weeks→hours, time/cost/expertise saved) · User stays in control 20% ("Control beats autonomy") · The demo 20% ("clear, live before/after a non-engineer grasps in 90 seconds"). Wants a REAL enterprise process + credible scale story + realistic public data. | General DoraHacks entry. → slides 2–7 (before/after, approval gate, refusal, recovery). |
| **BasedAI "Enterprise Memory Governance at Scale"** | $3,800 credits + Hirebase | Permission-aware memory, five-bullet spec: sync ACLs under concurrency · **deterministic** enforcement at the retrieval layer (**no LLM in the decision**) · regulatory audit logs · sub-200ms P99 permission checks · govern derived memory by lineage (revoke a source → cascades). Bonus: temporal access rules, query-time inference prevention. No published % rubric. | **HARD, eligibility-fatal:** open-weight models only — "no closed, proprietary models in the loop." **Separate submission mechanic:** a PR-per-team into `github.com/BasedAICo/hackathons`, open before judging on 4 Jul. → slide 8 tech, appendix A4. |
| **Fetch.ai** | 1,000 USDT (cash 1st £500 / 2nd £350 / 3rd £150) | Functionality 25% · Fetch integration 25% · Innovation 20% · Real-world impact 20% · UX/presentation 10%. | **HARD gates:** ≥1 agent on Agentverse · Agent Chat Protocol · discoverable/usable via ASI:One with the core use case demonstrable INSIDE an ASI:One conversation · meaningful tool execution/multi-agent · primary workflow works WITHOUT a custom frontend · public repo. **Separate artifacts:** ASI:One shared-chat URL + Agentverse profile URL(s). → slide 8 strip, appendix A7. |

**How the thesis maps 1:1 to the rubrics** (put on a positioning/why-we-win slide only using the spec's words):
- "no LLM in the decision" + "it knows what it's not allowed to touch" = BasedAI's deterministic permission path + open-weight-only rule.
- approval gate + typed tools + auto-rollback = Conduct's "User stays in control" (20%) and "recover from errors" (inside the 35%).
- "the second time is free" (retrieve the org's own documented fix) = Conduct's 30% Impact & speed-up.

**Eligibility-fatal cautions for the deck:** (a) Never show or imply a **closed/proprietary model** anywhere — BasedAI's open-weight rule is the whole loop. (b) Never describe the permission/risk gate as **LLM-driven** — it is deterministic. (c) Don't attribute Fetch's 25/25/20/20/10 weights to Conduct or vice versa. (d) Don't fabricate a BasedAI weighting (none is published) — cite only the five-requirement spec + open-weight rule.

---

## 4. The product: Precedent

**Problem.** Something breaks → find the manual → click through an admin console. Average incident MTTR is **8.85 business hours** (MetricNet/HDI) for a fix that is often minutes of keystrokes once known. It's universal and priced: **$600B/yr** downtime across the Global 2000 (Splunk 2026), **≈$200M per company** (Oxford Economics/Splunk 2024), and **>60% of incidents are repeats** whose fix already exists but nobody can find (ServiceNow's own support org).

**Solution loop.** DETECT → TRIAGE → RETRIEVE (KB + memory, ACL-filtered) → RISK-CLASSIFY (deterministic policy engine — **no LLM in the decision**) → GATE → EXECUTE (typed tools) → VERIFY (auto-rollback on failure) → MEMORISE (executed-fix-with-provenance). The verbatim slide-4 ribbon is seven plain-English words, no agent names: detect → find the documented fix → check risk → get approval → execute → verify → remember. The unit of memory is "an executed fix with provenance" (symptom → verified fix → approver → risk → rollback → outcome), not RAG-over-runbooks.

**Moat / differentiation.** (1) "The model narrates, deterministic policy disposes" — the LLM may propose fields/prose but the decision is a computed fingerprint; a class match counts only on extractor-confirmed field **equality**, never semantic similarity. (2) A company-specific operational memory that compounds with use. Differentiation vs AI-SRE incumbents: "$340M+ of AI-SRE VC points at code/infra diagnosis and stops before execution in business apps." Precedent executes the documented admin fix — gated, audited, reversible. ServiceNow paid **$2.85B** for Moveworks — resolution memory is worth buying; Precedent builds the version that *executes*.

**The four hard rules (eligibility-fatal — treat as absolute):**
1. **Open-weight only, no closed model anywhere in the loop** (BasedAI). Every model in the loop has published Hugging Face weights; a closed model anywhere disqualifies. The deck must not show or imply a closed/proprietary model. "It runs on Venice" is NOT a compliance argument — Venice's 2026 catalog proxies closed frontier models too.
2. **No LLM in the permission/risk decision.** The class match is deterministic **fingerprint field equality** (`sha256(service|error_code|target_object_type)`), never semantic similarity; the risk class comes from a deterministic policy engine + human identity; the LLM only proposes fields and writes rationale prose. Failed extraction ⇒ capped at L0/L1. Never describe the risk gate as LLM-driven.
3. **L3 is "Standing Approval," NEVER "Autonomous."** Graduation is earned and printed in the audit log: **3 consecutive verified L2 successes, zero rollbacks → eligible; a human clicks "Promote to Standing Approval." Any verification failure or rollback auto-demotes the class to L1** (and a visible Revoke always demotes on demand). "Approval moves earlier in time; it never leaves the loop." Saying "autonomous" is a Conduct skim-level disqualifier.
4. **Fail-closed permissions.** Access to a derived fix requires satisfying the constraints of **every** source it was built from (conjunction, not strictest-label). When the ACL source (Jira) is unreachable, every restricted memory record is denied — a stale cache can narrow access, never widen it.

**Target vertical: MediaCo / media-broadcast ops** — workflow-heavy, config-heavy, audit-sensitive, legacy-bound, work stuck between support/ops/engineering; demo-rich and Netflix-proved but unproductised. Disney+ is the **origin story** (first-hand internship observation only) — NEVER assert "Disney runs WHATS'ON" as a vendor fact.

---

## 5. The deck structure

12 core slides + 9 appendix slides (A1–A9). **Appendix order in-file is A1, A2, A3, A4, A5, A6, A7, A9, A8 — A9 comes BEFORE A8. Keep that order; do not "fix" it.** The header of `03-pitch-deck.md` says "8 appendix slides" — that is a known undercount; the 9 in-file bodies are authoritative. For every slide, the verbatim on-slide text lives in `03-pitch-deck.md`; the table below is a map, not a substitute. Banned from core slides (speaker notes / appendix only): agent names (Watcher/Librarian/…), YAML, ACL, SoD, "five-element schema."

### Core deck (12 slides)

| # | Title | Purpose | Load-bearing element |
|---|---|---|---|
| 1 | Title | Walk-up slide, zero talk time | Wordmark "Precedent" + tagline "Every incident resolved becomes precedent." + track logos. Team ‹name› = `[[WAIT:TEAM]]`. |
| 2 | Cold open: the loop (problem 1) | Name the manual loop, dramatised | Hero number **8.85 hours**; three-step loop diagram. CrowdStrike/Sky News + Disney+ cold-open in notes. |
| 3 | Problem is universal & priced (problem 2) | Size the pain + repeat-rate | **$600B/yr** + **≈$200M per company** in the same breath; **>60% repeats** band. |
| 4 | Solution (thesis) | The reframe | Thesis line + product line + four badges (risk-classified · approval-gated · audited · reversible) + 7-word closed-loop ribbon. |
| 5 | Before/After stopwatch | The pitch's visual joke | **Three time bars TO SCALE**: 8.85 hrs full-width, ~60 s & ~15 s slivers. Kicker "The second time is free." **NEVER cut or degrade.** |
| 6 | The demo | Use case + demo flow | MediaCo · real data · live Jira · unscripted. Three incidents (60 s / 15 s / refused) + provenance strip (verbatim small type). On screen when cutting to recording. |
| 7 | Control, not autonomy | Trust story | Ladder L0→L3 **Standing Approval** (never Autonomous); real product buttons [Promote to standing approval] [Revoke]; kicker "Approval moves earlier in time. It never leaves the loop." |
| 8 | How it works (tech) | One diagram, one slide | ONE diagram, five UNNAMED agent nodes, shield "deterministic policy gate — no LLM in the authorisation path", memory cylinder, strip "Live Jira · open-weight end-to-end · Fetch.ai Agentverse / ASI:One". **Q&A-only on stage.** |
| 9 | Nobody does this (white space) | Competitive gap | Lifecycle bar with the empty Fix+Learn gap; "$2.85B for Moveworks" proof-strip. **Q&A-only.** |
| 10 | The moat: memory compounds | Flywheel + proof | Record schema + flywheel + metrics strip: 141k events · 94% precedented · median **18 hrs (calendar)** + `[[WAIT:BENCH]]` P99 ms + 3 extractor % cells. **Q&A-only.** |
| 11 | Market: beachhead, not ceiling | Why now | Media→MSP→everyone chevrons; **$22 → $69 → $104** deflection ladder; Encompass/Amagi vendor-claimed superscripts. |
| 12 | Team + Ask | Close | Faces + ask (two intros, applying to Antler & EWOR) in largest type + closing kicker "ServiceNow paid $2.85B for resolution memory. We're building the version that executes." Team text = `[[WAIT:TEAM]]`. |

Slides **8, 9, 10 are NOT spoken on stage** — they live in the submitted deck and are jumped to in Q&A only. **Self-narration applies to every core slide (1–12):** the narration band carries the substance of that slide's speaker notes; the hero line/number stays minimal. Slides 8/9/10 must still self-narrate for the silent founder read.

### Appendix (9 slides — keep the file's order: A9 comes BEFORE A8)

| # | Title | Purpose |
|---|---|---|
| A1 | Every number, sourced | 15-row table; jump here when a number is challenged. "verified 3–0" / "(vendor-claimed)" labels; 94.4% (symptom 98.6%); 18.2 **calendar** hrs (p75 136.6); 558 classes = 94.8% volume. |
| A2 | Data provenance | "The systems are simulated; the content is real." TVmaze/Freeview/Kaggle/UCI licences; TMDB & IMDb rejected (state why) — a credibility beat. |
| A3 | Standing approval: exact semantics | Deterministic fingerprint; 3-consecutive-success graduation; rollback-before-execute; approver identity. |
| A4 | Permission-aware memory (BasedAI depth) | Conjunction over all sources; effective-policy cache **P99 `[[WAIT:BENCH]]`**; FNR/FPR bench; dual-enforcement revocation; fail-closed. |
| A5 | Why won't ServiceNow/Conduct build this? | "They meter the workflow; we delete it." They *acquire* this layer (Jeli $29.7M, Moveworks $2.85B). |
| A6 | Integration reality | Four-tier surface strategy (REST → BXF/file → FTP → RPA-on-console); typed tool calls only. |
| A7 | Fetch.ai deliverables | ‹3› Agentverse addresses + ASI:One shared-chat URL = `[[WAIT:FETCH-URLS]]`. |
| **A9** | **Bottoms-up ACV** (added after judge round 2) | 1 MSP NOC × tickets × repeat share × $50 deflection ⇒ seven-figure ACV/site; every input sourced. **Placed BEFORE A8.** |
| **A8** | Liability & regulated ops | Customer's own change-management encoded; documented-fix-only execution; execution-success + rollback rate, never model benchmarks; audit schema. |
| +extra | "What exists Monday morning" (PDF only) | Four durable artifacts (hosted Watcher live on Agentverse · `precedent_memory` standalone library · the ground-truth conformance bench · the public evidence index). **NO human-intent claims** (those stay on the team slide). Appended at export. |

---

## 6. The demo & the on-stage narrative

The live demo runs **three named incidents + one recovery beat** (Beats 1, 2, R, 3), targeting 2:42, rehearsed to 2:40. The full second-by-second script is in `Idea/refinement/04-demo-and-video-script.md` (§2 spoken lines are verbatim; §4.3 — not the deck — is the single source of truth for live-first vs recorded-first). Deterministic seed = **4207** (`sim/incidents.py::SEED`); incidents 1/2/3 replay byte-identically; observation time is frozen (no wall-clock). Summary:

- **Beat 1 (incident 1, ~60 s):** messy EPG/VOD publish-fail ticket (wrong error code on purpose), one human **Approve** click, ~58 s vs 8h51m, ends with **Promote to Standing Approval**.
- **Beat 2 (the "second time is free" wow, ~15 s):** same fingerprint, nobody at the keyboard, fingerprint fast-path resolves in ~15 s on an on-screen stopwatch, **zero LLM calls**.
- **Beat R (recovery, ~20 s):** deterministic publisher-503 injected mid-write → verification FAILS red → pre-written rollback fires → state restored → class **demoted** Standing Approval → L1 → escalated. (This beat answers Conduct's 35% "recovers from errors" — do not cut it from the narrative.)
- **Beat 3 (refusal):** rights-window conflict; a documented fix exists but Jira's own "Rights Ops Only" issue-security hides the runbook from the scheduling-ops identity, so Precedent refuses and routes a dossier. Payoff: "it knows what it's not allowed to touch."

**Console surfaces** the slides point at: persistent Baseline Bar ("Manual: ticket → find runbook → admin console → approval queue → resolve = 8 hrs 51 min avg") with green elapsed bars per incident; a Precedents/Memory counter (seeded 25,412); Promote + always-visible Revoke; degraded-mode amber banner ("Jira degraded — running on cached mirror, will re-sync") as a feature not an apology; cumulative close strip ("Tonight: 3 incidents · manual ≈26 h · Precedent 1 m 28 s"); the provenance footer.

The ~15 s Standing-Approval time is **engineered/paced-up** (real work ~6–8 s, streamed to read as visible activity), not a raw benchmark — never present 15 s as measured latency.

**Live vs video split.** Demo execution mode (live-local-first vs narrated-recording) is decided **mechanically by `04-demo-and-video-script.md` §4.3's rehearsal gates at Sat 09:00, NOT by the deck.** The live demo leans on 8h51m / 58s / 15s / $70M / $2.85B / $600B–$200M. Video-only (never in the live spoken script): ">60% repeats", the "$22→$69→$104" ROI ladder, "KB article resolves 66% faster", and the 94%/18h scale numbers. The recorded video (~4:15–4:30) serves both DoraHacks/Conduct and Fetch, with an ~80-second ASI:One centerpiece.

**Pre-ordered cut-lines (locked):** the 90-second cut is slides **2 → 5 → 6 (incident-2 clip only, 25 s) → 7 → 12** — and the two memorable lines must survive it. Shrink the video by compressing shot 4→25s and shot 7→15s, **never** shot 5 (ASI:One) or shot 0 (cold open); if the live demo runs hot, cut only "for what is usually minutes of keystrokes once the fix is known." Slide-5 time bars are the pitch and must **never** be cut.

---

## 7. The design system

**Theme (the concrete hex/pt values come from `N1-deck-build.md` §3, NOT from `03-pitch-deck.md` — the spec file itself only says "dark background, one accent colour, numbers 3–5× body size, ~15 words max, no bullet list >3." Cite the specifics to their true source):**
- Background: very dark **#0B0F14** every slide.
- Body text: **#E6E6E6**, font **Inter** (Roboto fallback), ~18pt.
- ONE accent colour: green **#34D399** (matches the console's elapsed-time green) — big numbers, kicker lines, "second time is free." If T1 vetoes the colour, it's a one-line theme edit; don't block on it.
- Big numbers ("8.85 hours", "$600B", "$2.85B"): **3–5× body** (60–90pt).
- Max ~15 words of body per slide; no bullet list longer than 3 on any core slide.
- Every vendor-claimed number gets a small superscript "(vendor-claimed)" — honesty is part of the brand.

**The load-bearing slide-5 time bars:** three rounded rectangles — the 8.85-hr bar spans the FULL slide width; the ~60 s and ~15 s bars are thin slivers. The visual joke IS the point. **Never degrade or cut this slide**, even in the deepest cut.

**Banned vocabulary on CORE slides** (allowed in speaker notes / appendix only): agent names (Watcher/Librarian/Assessor/Operator/Auditor), YAML, ACL, SoD, "five-element schema". Slide 8 shows FIVE UNNAMED agent nodes; slide 4's ribbon uses seven plain-English words. Also keep out of the hero line the stage-banned words per the prep spec (lineage, embeddings, "deterministic policy engine", P99) — these live in Q&A-depth notes and technical appendices.

**THE SELF-NARRATION BAND (the key adaptation for this no-speaker founder deck).** ~50% of judges see only the PDF with no speaker, and in this initial stage the founders read it with no narration at all — so it must self-narrate. Replace the original spec's thin one-line grey caption bar with a fuller narration band on every core slide:
- **What it is:** a smaller secondary text layer (roughly 2–3 lines, up to ~45 words) placed beneath or beside the hero element, drawn from the EXISTING speaker notes for that slide in `03-pitch-deck.md`. It **supersedes and expands** the original single grey caption (which the spec sized at #8A8F98, ~12pt, one sentence) for this founder deck.
- **Word-limit interaction:** the "max ~15 words" theme rule governs ONLY the hero line/number — keep it bold and minimal. The narration band is a separate layer.
- **Honesty:** introduce NO new claim, number, or vocabulary beyond what the spec's on-slide text and speaker notes already contain. The calmer narration band may use fuller plain language but stays honest, secret-free, and invents nothing. Keep every honesty and placeholder rule intact.
- **Retention:** RETAIN the full speaker notes in the slide notes field for later live/stage use — the band is a distillation onto the slide, not a replacement of the notes.
- Example, from slide 7's speaker notes: the hero stays "Approval moves earlier in time. It never leaves the loop."; the narration band distils "No one approved that second ticket — the operations lead pre-approved this fix class after watching it succeed; standing approval is an ITIL standard change, earned through verified history and revocable with one click."

---

## 8. The numbers

Every on-slide figure must trace to `data/analysis/uci-baseline-results.md` or `Research/00-verified-claims.md` with the **same framing the source uses**, and carry its caveat label. Two number families must **never be blended, averaged, or swapped**: our measured **calendar**-hour figures vs the industry **business**-hour MTTR. "They corroborate each other; never average them." Never blend 18.2h (calendar) with 8.85h (business).

| Figure | Where | Source / label | Caveat |
|---|---|---|---|
| **8.85 hours** (business) avg MTTR | Slide 2, 5 (Baseline Bar), A1 | MetricNet/HDI | **BUSINESS** hours. Vintage ~2019–2020; never relabel "2024". Never blend with 18.2h. |
| **$600B/yr**, +50% in 2 yrs | Slide 3, A1 | Splunk 2026 press release | Always pair with $200M/company in the same breath; never say "$400B" bare. |
| **≈$200M per company** | Slide 3, A1 | Oxford Economics/Splunk 2024 | Verified 3–0. Preferred over the aggregate. |
| **>60% repeats** | Slide 3, A1 | ServiceNow's own support org (KCS case study) | Verified 3–0. |
| **$22 → $69 → $104** ticket ladder | Slide 11, A1 | MetricNet whitepaper | Vintage ~2019–2020 — never relabel "2024". |
| **$2.85B** Moveworks | Slide 9, 12, A1, A5 | ServiceNow newsroom Mar 2025 | Verified. Closing comp. |
| **141,000** events / 24,918 incidents | Slide 6, 10, A1, A2 | UCI ML Repo #498, CC BY 4.0 | Real ServiceNow instance audit log; measured baseline. |
| **94% / 94.4%** precedented (98.6% symptom-class) | Slide 10, A1 | Our measurement, script committed 3 Jul | Precedent EXISTENCE (key includes closed_code, known only at resolution) — NOT arrival-time. 98.6% = arrival-knowable; do not swap. |
| median **18 / 18.2 hrs (calendar)**, precedented repeats (p75 136.6) | Slide 10, A1 | Our measurement | **CALENDAR** hours. Keep the label; never blend with 8.85h. |
| **558 classes = 94.8%** of volume (≥4 occurrences) | A1 | Our measurement | Ladder-bootstrap evidence. |
| Arrival-time floor: Top-1 **59.4%** / Top-3 **87.7%** | (A-depth / Q&A, not a headline) | Our measurement | A naive-baseline FLOOR, NOT a product-accuracy claim. Justifies fingerprint-equality-not-similarity. |
| Encompass 1,200+ / Amagi 5,000+ | Slide 11 | Vendor marketing | **(vendor-claimed)** superscript required. |
| Moveworks 50–88% deflection | A1 | Moveworks | **(vendor-claimed)**. |

**The measured baseline** (the "unattackable, ours" numbers): 94.4% / 98.6% / 18.2 calendar hrs / 558 classes = 94.8%, all from `data/analysis/uci-baseline-results.md`. These are already real and go straight onto slide 10 / A1 — do NOT treat them as placeholders. The `knowledge=true/false` MTTR split is a confound — never present it causally.

**The `[[WAIT]]` cells still pending** (mark with the literal token, never `‹XX›`, and never export while either token exists):

| Cell | Token | Fills from |
|---|---|---|
| Slide 10 strip: P99 ms + extractor correct-match / safe-degrade / false-fast-path % | `[[WAIT:BENCH]]` | T3 bench (`precedent_memory/bench/RESULTS.md`) + extractor mutation run, committed to repo |
| A4 P99 sentence | `[[WAIT:BENCH]]` | same |
| A7: 3 Agentverse addresses + ASI:One shared-chat URL | `[[WAIT:FETCH-URLS]]` | T1 Fetch-rail capture (human runs live registration) |
| Slide 1 + 12 team name/roles/credentials | `[[WAIT:TEAM]]` | human-written, never AI-drafted |
| Slide 12 practitioner-validation line | `[[WAIT:TEAM]]` | only if outreach genuinely happened |

**Degraded rule:** if a bench/URL/team value is still missing at the freeze, **DELETE that cell entirely** and ship only the measured, committed numbers (94% / 18.2h / 558-class). Never ship a bracket or placeholder to fill the gap. A thin true slide beats a rich fake one.

---

## 9. Current build state (so the deck never over-claims)

**Real and demonstrable today** (branch `build/t1-core-loop-sim-agents`, G1 slice green, live-verified):
- The full DETECT→…→MEMORISE kernel (`precedent/orchestrator.py`), split into `prepare()` + `commit_execution()`.
- Incident 1 slow-path (human approval), incident 2 STANDING fast-path (**zero venice.chat/embed calls** — provable in code), recovery beat R (rollback + demote), incident 3 refused (discloses only count + owner team).
- Deterministic guarantees enforced in code: risk class/rule/ceiling from a YAML pack (no LLM); a non-deterministic extraction is force-capped to L1 so an LLM proposal can never unlock the fast-path.
- **119 tests pass** (`.venv/bin/python -m pytest -q`). `make check-open-weight` exits 0. Seed = **4207**. `make demo-reset` in 0.4s pre-seeds the repeat class to STANDING. Same-process demo server, 20s ACL re-sync, airplane-mode safe.
- Four pinned open-weight models declared ONLY in `precedent/models.py`: FAST qwen3-5-35b-a3b (Apache-2.0), SMART deepseek-v4-flash (MIT), HEAVY deepseek-v4-pro (MIT), EMBED text-embedding-bge-m3 (MIT), verified vs Hugging Face 3 Jul 2026.

**Planned / pending — the deck must NOT claim as done (all behind `[[WAIT]]`):**
- **Conformance bench** — historically a stub in the T1 branch; the numbers land from T3's bench (`precedent_memory/bench/RESULTS.md`) committed at merged main. Until the bench numbers are committed and read into the strip, P99/FNR/FPR/all 10 metrics + 6/6 attacks stay `[[WAIT:BENCH]]`. Do not print a P99 the repo can't back.
- **Extractor mutation-corpus rates** (correct-match / safe-degrade / false-fast-path) come from running T3's seed-4207 corpus against the merged extractor → `[[WAIT:BENCH]]` until run.
- **No real Agentverse addresses and no ASI:One shared-chat URL** exist in the repo yet — agents are registerable but a human must run live registration → `[[WAIT:FETCH-URLS]]`. Do NOT claim "registered/discoverable" as done.
- Live Jira is implemented + **mock-verified only** — never write "verified against real Jira".
- Console is **JSON-polling (setInterval 1500ms), not true SSE** — prefer "server-rendered + polling" over claiming streaming.
- gitleaks full-history not re-run locally at deck-build time — do not caption "gitleaks-clean" unless the scrub has run.

**Doc-vs-reality traps:** any runbook/ledger that still says "56 passed" predates the T1 merge; the real number is **119** — never quote 56.

---

## 10. Honesty & compliance rules for the deck

1. **Never ship a placeholder** in an exported PDF: no `‹XX›`, no `‹Name›`, no `[[WAIT:…]]`. The pre-export sweep (search `‹` → zero, search `[[WAIT` → zero) is non-negotiable. **Degraded rule:** if a bench/URL/team value is missing at the freeze, DELETE that cell entirely and ship only measured, committed numbers. Never ship a bracket to fill a gap.
2. **Real names only.** Slide 1/12 team text is human-written and true — role titles and real names only, never AI-invented credentials. The team/human slide is a VC-fatal placeholder both rounds and cannot be faked: write it honestly or ship role titles only.
3. **No secrets** on any slide, in the repo, or in a screenshot — no keys, tokens, `.env`, wallet seeds.
4. **Open-weight framing:** the whole loop is open-weight end-to-end; only `precedent/models.py` may name a model. Never imply a closed model. "It runs on Venice" is not a compliance argument. Recall the Fable disambiguation (§1): Fable 5 authoring the deck ≠ a closed runtime model.
5. **Vendor-claimed labels:** every vendor stat carries "(vendor-claimed)". Never quote an LLM benchmark as an accuracy claim — only verified execution-success + rollback counts.
6. **L3 = "Standing Approval", never "Autonomous".** The permission flip is a "local Jira-shaped source", never "real Jira flip".
7. **Number honesty:** calendar (18.2h) vs business (8.85h) labels intact, never blended; $600B always paired with $200M, never "$400B" bare; every number traces to `uci-baseline-results.md` / `00-verified-claims.md` with the source's own framing.
8. **Caption/self-narration discipline:** the band says only what the speaker notes already say — no new claim sneaks in via the band.
9. **Never** say "nobody executes in third-party apps" (RPA/Ignio/Klaudia falsify it — the whitespace is the *combination*); never assert "Disney runs WHATS'ON"; never end without the ask.

---

## 11. How to build it (Fable session guidance)

You are transcribing, not authoring — follow `Plan/workflows/N1-deck-build.md` exactly.

**Format options (pick one):** (1) **Google Slides** — fastest, easiest live review; new file "Precedent — Demo Day deck", Widescreen 16:9; export two PDFs to `docs/submission/`, keep the Slides link (anyone-with-link, viewer) in the PR description. (2) **Versioned HTML/Reveal deck** in `docs/deck/` (the ambition option, §9 of N1) — only if it won't crowd out the numbers-fill and only **after** the core deck is committed. A committed honest Google Slides deck beats a half-built HTML one. Honesty and caption/placeholder rules are identical either way.

**Build-sheet-per-slide method.** Point your tool at `03-pitch-deck.md`; for each slide produce: (1) slide title, (2) on-slide text verbatim in placement order (largest element first), (3) layout as 3–6 plain-English steps, (4) speaker notes verbatim, **(5) the self-narration band distilled from those speaker notes**, (6) placeholder flags for every `‹…›` token. **Verify as you go:** diff on-slide text/numbers against the file character-for-character; confirm banned vocabulary appears in ZERO core slides; surface every `‹…›` and `[[WAIT:…]]` token on a running checklist, never silently dropped. Suggested passes: Core 1–6, then Core 7–12 (with the spec's "PLACEHOLDERS TO FILL" section as a checklist); Appendix A1–A9 in file order (A1…A7, **A9, A8**); then the self-narration band on all 12 core slides; then the "What exists Monday morning" PDF-only slide.

**Export sequence (do NOT reorder):**
1. Fill all `[[WAIT:…]]` cells from committed repo numbers; apply the degraded rule to any still-missing cell.
2. Placeholder sweep: search `‹` (zero results), then `[[WAIT` (zero results).
3. Clean stage PDF: copy "Precedent — deck (stage)", export now = caption-free Demo Day backup.
4. Self-narration/caption layer: add the narration band to each of the 12 core slides (grey `#8A8F98`, sized as a readable secondary layer, not the thin 12pt caption bar the original spec assumed) + append "What exists Monday morning".
5. Submission PDF: export "Precedent — deck (submission).pdf".
6. Commit both PDFs (`docs/submission/precedent-deck.pdf` + the stage backup) on your branch, open PR/merge per convention, put the Slides link in the PR description. This is the file attached to DoraHacks — commit **before the freeze**.

**Which PDF the founders read now.** The **submission PDF (with the self-narration band)** is what the no-speaker founders read in this initial stage AND what ships to DoraHacks; the **clean stage PDF (caption-free)** is the backup for the LATER live Demo Day, where a speaker narrates. The self-narration adaptation EXPANDS the caption layer — it does not collapse the source's two-PDF split; produce both.

**DONE checklist:** 12 core + 9 appendix matching spec verbatim (PDF adds the narration band + 1 slide); all numbers match committed bench/evidence with calendar-vs-business labels intact; zero `‹` and zero `[[WAIT` in either PDF; vendor-claimed superscripts present; banned vocabulary absent from core slides; every numbered surface carries the identical mutation-robustness number; both PDFs committed + Slides link in PR, merged before the freeze.

**Cut rules (demo & honesty win every conflict with ambition), in order:** (1) appendix A6/A8 layout polish; (2) slide artwork degrades to labelled boxes/arrows — **never cut the slide-5 time bars**; (3) minimum shippable deck = 12 core + A1 + A2 with the narration band. **Never cut:** the placeholder sweep, the self-narration/caption layer, the calendar/business labels.

---

## 12. Q&A backup (hardest objections + answers)

The full bank is `Idea/refinement/05-scale-story-and-qa.md` (44 objection→answer pairs; each answer's **bold opener** is the rehearsed first sentence — copy verbatim). The residual open findings from the judge panel are the objection map. Highest-value answers:

- **"Zero product code / can you actually build this by Friday?"** → the G1 slice is green now: one kernel drives console + chat-approval; 119 tests pass (seed 4207); the recovery beat and refusal are demonstrable today; the residual gap is the bench and the team slide, priced honestly as execution risk, not design regression.
- **"Isn't the LLM deciding permissions?"** → "No — the class key is computed, not inferred. The model narrates; it never authorises." Fingerprint field equality, deterministic policy engine, human identity.
- **"Is L3 just autonomy?"** → "Nothing here is autonomous — L3 is a Standing Approval, and a named human granted it on screen." Revoke always visible; any rollback demotes. Approval moved earlier in time; it never left the loop.
- **"Your 94% is a resolution-code trick."** (self-disclosed honesty trap, C7) → arrival-time floor: 98.6% precedent existence at symptom level, top-1 59.4%, top-3 87.7% (naive baseline) — which is exactly why execution requires fingerprint equality, never rank-1 similarity. Do not conflate the two.
- **"Nobody executes in third-party apps?"** → never say that (RPA/Ignio/Klaudia do). The whitespace is the COMBINATION: org's documented fix + business-app execution + graduated approval + compounding memory.
- **"You just built the simulator."** → four-tier surface strategy (REST → BXF/MOS → FTP → RPA-on-console), same gate/audit/rollback at every tier; "sits architecturally exactly where a qibb flow sits"; connectors are deliberately not the moat.
- **"Why won't ServiceNow/Conduct build this?"** → they meter the workflow; they *acquire* this layer (Jeli $29.7M, Moveworks $2.85B). Conduct makes legacy legible; we make it operable.
- **Fetch "how many agents?"** → "Three on Agentverse" (Watcher, Librarian, Operator); Assessor/Auditor in-process by design. **Conditional:** if only two register, say "Two on Agentverse" — never say three if two are registered.
- **BasedAI "single strictest label?"** → "No — conjunction of all source constraints." Revocation is lineage-indexed; fallback fails closed. Doctrine sentence: "There is no LLM call in any permission decision — the model proposes, deterministic policy disposes."
- **"Isn't BioVault already doing this?"** → acknowledge a strong governance demo, then differentiate — never disparage: our lineage governance runs inside a working multi-agent system executing real fixes against a **live Jira ACL source** over a **real ~25k-incident corpus**, benchmarked in the track's own FNR/FPR/P50–P99 vocabulary — numbers a synthetic standalone structurally cannot show. (BioVault = the purpose-built BasedAI competitor, PR #3.)
- **Attribution:** the A/B/C permission semantics were worked out publicly in the BasedAI Discord and endorsed there — credit the thread if asked; NEVER say the sponsor "endorsed our design."
- **A7 founder-market fit** is un-writable by a document — leave a clearly-marked gap, do not fabricate. **Never end without the ask** — design-partner intros + Antler/EWOR applications + the Moveworks comp as the last thing they hear. The literal placeholder "Ask." is the one unforgivable VC-judge failure.

---

## 13. Source-file index

| File | Why the builder opens it |
|---|---|
| `Idea/refinement/03-pitch-deck.md` | **THE deck.** Verbatim on-slide text, layout, speaker notes for all 12 core + 9 appendix slides, run-of-show, PDF export layer, placeholder list. Transcribe character-for-character. |
| `Plan/workflows/N1-deck-build.md` | Build method, the concrete theme hex/pt values, format options, `[[WAIT]]` table, export sequence, DONE checklist, cut rules. |
| `data/analysis/uci-baseline-results.md` | The measured slide-safe numbers (94.4% / 98.6% / 18.2h calendar / 558 classes) + arrival-time floor + the never-average rule. QC every measured figure here. |
| `Research/00-verified-claims.md` | Every third-party stat's verified source, vote count, and caveat (vendor-claimed / vendor-sponsored / stated-goal). QC every industry figure here. |
| `Idea/refinement/04-demo-and-video-script.md` | Second-by-second demo + video script; §5 stat-consistency table (the only numbers anyone may say); §4.3 = single source of truth for live-vs-recorded. For demo/teaser/video slides. |
| `Idea/refinement/05-scale-story-and-qa.md` | Scale story + full Q&A bank (bold openers) for the appendix and speaker prep. |
| `Idea/refinement/02-architecture-refinement.md` | Appendix-grade technical detail for A3/A4/A6 + the slide-8 diagram (fingerprint, A/B/C semantics, model registry, Fetch topology). |
| `Idea/Idea-Development.md` | The thesis blockquote, the closed loop, the ladder, the two takeaway lines — verbatim anchors for slides 4/5/7/10. |
| `data/raw/SOURCES.md` | Data licences (TVmaze CC BY-SA, Freeview GPL-3.0, Kaggle CC0, UCI CC BY 4.0; TMDB/IMDb rejected) — for A2 and the slide-6 provenance strip. |
| `data/kb/README.md` | KB corpus (restricted / stale / escalate articles; codes PUB-4012, RGT-EXCL-009) — seeds the refusal beat. |
| `README.md` / `docs/evidence/T2-EVIDENCE-LEDGER.md` | Safe/unsafe wording per claim + status strata for any build-state claim — do not upgrade a MOCK-PROVEN claim to sound proven. |

---

**Remember the golden rule:** on-slide text and every figure are copied VERBATIM from `Idea/refinement/03-pitch-deck.md`. This brief orients and constrains; it does not replace that spec. When in doubt, open the spec.
