# PACKET N1-DECK — Build the Precedent pitch deck (12 core + 9 appendix slides, Google Slides)

> WHO RUNS THIS: **N1** — non-technical teammate, working on **claude.ai FREE tier**, no repo access. Everything you need is in this file plus the attachments T3 sends you.
> WHO BUNDLES AND SENDS: **T3** exports the three files in §1 and emails them to N1 (email, not WhatsApp — WhatsApp mangles .md files; WhatsApp is for pings only).
> WHO RECEIVES OUTPUT AND COMMITS: N1 sends the Google Slides share link + exported PDFs to **T3**; T3 attaches the PDF to the DoraHacks draft (Sat 08:30) and commits a copy to `docs/submission/precedent-deck.pdf`.
> WHERE THIS FITS IN N1's DAY: Friday **15:00–17:15** (core slides), Saturday **06:30–08:00** (metrics fill + appendix finish + caption layer + PDF export). KB articles (packet N1-KB) and the licence packet (N1-LICENCE) come FIRST on Friday — they are demo-critical; the deck's hard deadline is Saturday 08:00.

---

## 0. What you are making and why it matters

The deck spec file **IS the deck**: `Idea/refinement/03-pitch-deck.md` contains every slide's on-slide text, layout notes, and speaker notes, already written and judge-reviewed. Your job is transcription with discipline, not creative writing. Roughly half the judges will only ever see the **PDF export with no speaker** — so the PDF must self-narrate (caption layer, §6) and must never contain an unfilled placeholder.

Deliverables:
1. A Google Slides deck: **12 core slides + 9 appendix slides (A1–A9, in the file's order — note the file lists A9 before A8; keep the file's order)**.
2. A **clean stage PDF** (no captions) — backup for Demo Day.
3. A **submission PDF** with the caption layer + one extra appendix slide ("What exists Monday morning") — this is what goes to DoraHacks.

## 1. What T3 sends you (Friday by 14:30, one email)

| # | Repo path | Why you need it |
|---|---|---|
| 1 | `Idea/refinement/03-pitch-deck.md` | The deck spec — the single source of truth |
| 2 | `data/analysis/uci-baseline-results.md` | Our measured numbers (94.4% / 18.2h / 558 classes) — for the Saturday QC pass |
| 3 | `Research/00-verified-claims.md` | Every industry number's verified source — for the Saturday QC pass |

That is 3 attachments — the free-tier maximum per conversation. Never attach anything else alongside them.

## 2. Free-tier ground rules (read once, obey always)

- Max **3 small attachments** per conversation; run each conversation in §4 as a **separate chat**.
- Ask for output in small batches (the prompts below already do this). If a reply cuts off mid-slide, type **"continue"**.
- If claude.ai says you have hit your usage limit: STOP, note which slide you reached, and WhatsApp T3. T3 can run the remaining chunk on another seat — the prompts below work verbatim for anyone. Never retype a long prompt from memory; copy it from this file.
- Never paste secrets, keys, or team members' real names into Claude. Slides use `‹Name›` placeholders until the team supplies the human-written slide-12 text (see §5).

## 3. Google Slides setup (do this before any Claude conversation, ~15 min)

1. New Google Slides file named **"Precedent — Demo Day deck"**. Page setup: Widescreen 16:9.
2. Theme (the spec's design rules, made concrete — keep these exact so the deck is consistent):
   - Background: very dark **#0B0F14** on every slide.
   - Body text: **#E6E6E6**, font **Inter** (or Roboto if Inter is unavailable), ~18pt.
   - ONE accent colour: **green #34D399** (matches the console's elapsed-time green). Used for: big numbers, the kicker lines, the "second time is free" text. If T1 vetoes the colour at the 13:00 check-in, recolouring is one theme edit — do not wait on it.
   - Big numbers ("8.85 hours", "$600B", "$2.85B"): **3–5x body size** (60–90pt).
   - Max ~15 words of body text per slide; no bullet list longer than 3 on any core slide.
   - Every vendor-claimed number gets a small superscript "(vendor-claimed)".
3. Banned vocabulary on core slides (allowed in speaker notes and appendix only): agent names (Watcher/Librarian/Assessor/Operator/Auditor), YAML, ACL, SoD, "five-element schema". The two lines the room must remember: **"the second time is free"** and **"it knows what it's not allowed to touch."**

## 4. Conversation plan (chunked prompts — copy-paste verbatim)

### Conversation D1 (Fri ~15:00) — build sheets, core slides 1–6
Attach: `03-pitch-deck.md` only. Paste:

```
You are helping me build a pitch deck in Google Slides for a hackathon project called Precedent.
The attached file (03-pitch-deck.md) IS the deck spec: every slide's on-slide text is already
written and must be copied EXACTLY — do not reword, shorten, or "improve" any on-slide text or
any number.

Produce a BUILD SHEET for CORE SLIDES 1–6 only. For each slide give me:
1. SLIDE TITLE (my reference)
2. ON-SLIDE TEXT — verbatim from the file, listed in placement order (largest element first)
3. LAYOUT — the file's visual/layout notes rewritten as 3–6 plain-English steps I can follow in
   Google Slides (text boxes, relative sizes, simple shapes like horizontal bars or badges)
4. SPEAKER NOTES — verbatim from the file, ready to paste into the notes pane
5. PLACEHOLDER FLAGS — list every ‹…› token on the slide and what fills it later

Design rules to respect (from the spec): dark background, one accent colour, max ~15 words of
body text per slide, numbers 3–5x body size, no bullet list longer than 3 on core slides,
"(vendor-claimed)" superscripts kept, and NO agent names / YAML / ACL / SoD / "five-element
schema" wording on core slides (that vocabulary is fine inside speaker notes).

Give me slides 1–3 first, then wait for me to say "next" before slides 4–6.
```

Build slides 1–6 in Google Slides as each batch arrives. Slide 5's three time bars: draw three rounded rectangles — the 8.85-hr bar spans the full slide width; the 60s and 15s bars are thin slivers. The visual joke IS the point.

### Conversation D2 (Fri ~16:00) — build sheets, core slides 7–12
New chat. Attach: `03-pitch-deck.md` only. Paste the D1 prompt but change the second paragraph's first line to:

```
Produce a BUILD SHEET for CORE SLIDES 7–12 only.
```

and append:

```
Also list, at the end, the "PLACEHOLDERS TO FILL BEFORE EXPORT" section from the file as a
checklist I can keep beside me.
```

### Conversation D3 (Sat ~06:30) — appendix A1–A9 + the PDF caption layer
New chat. Attach: `03-pitch-deck.md` only. Paste:

```
Same deck project (Precedent), same verbatim rule: copy text exactly from the attached spec.

Task 1 — Build sheets for the APPENDIX slides, in the file's own order (A1, A2, A3, A4, A5, A6,
A7, A9, A8 — yes, A9 before A8, keep that order). These are Q&A backup slides: plain layouts,
small type, tables allowed. Give me them 3 at a time; I'll say "next".

Task 2 — The PDF EXPORT LAYER: for each of the 12 core slides, give me ONE single-line grey
caption sentence — the sentence the speaker would have said — drawn from that slide's speaker
notes in the file (the file gives slide 7's example: "No one approved that second ticket — the
approval moved earlier in time; it never left the loop."). Output as a numbered list, 12 lines.

Task 3 — The extra PDF-only appendix slide "What exists Monday morning": on-slide text as a
4-item list, exactly the durable artifacts the file's PDF EXPORT LAYER section names (hosted
Watcher live on Agentverse · precedent_memory as a standalone importable library · the
ground-truth conformance bench · the public evidence index). No human-intent claims.
```

### Conversation D4 (Sat ~07:15) — metrics fill + number QC + placeholder sweep
New chat. Attach: `uci-baseline-results.md` + `00-verified-claims.md` (2 files). Paste, filling in the metrics block you received from T3 (see §5):

```
Final quality pass on a pitch deck. Below are (a) the measured-metrics block my team sent me
last night and (b) the exact text I plan to put on slide 10's metrics strip and appendix A4/A7.
The two attached files are our verified evidence.

METRICS BLOCK FROM THE TEAM:
[paste T3's 21:30 metrics block here]

MY DRAFT SLIDE-10 STRIP:
[paste your draft here]

Check:
1. Every number in my draft appears in the metrics block or one of the attached files, with the
   SAME framing (especially: 18.2h is CALENDAR hours and must keep that label; 8.85h is BUSINESS
   hours; never blended or averaged).
2. Rewrite my slide-10 strip with the real values baked in. If any metrics-block cell is empty,
   apply the degraded rule: DELETE that cell from the strip entirely (ship only the measured
   94% / 18.2h / 558-class numbers) — never ship a bracket or placeholder.
3. Give me the final one-line text for appendix A4's P99 sentence and A7's addresses/URL lines
   from the metrics block.
4. List every remaining thing I must manually search the deck for before export: the characters
   "‹" and "[[WAIT" must return ZERO results in Edit > Find.
```

## 5. Cells that WAIT for late numbers — and how they arrive

Build everything else first. Mark each waiting cell with the literal token `[[WAIT:name]]` (never `‹XX›` — and never export while either token exists).

| Waiting cell | Token | Filled when | How it reaches you |
|---|---|---|---|
| Slide 10 metrics strip: P99 ms + extractor correct-match / safe-degrade / false fast-path % | `[[WAIT:BENCH]]` | Fri-night bench + 100-mutation run | **T3 emails + WhatsApps the METRICS BLOCK at ~21:30 Friday.** You process it Saturday 06:30 — do not stay up for it. |
| Appendix A4: P99 sentence | `[[WAIT:BENCH]]` | same | same block |
| Appendix A7: 3 Agentverse addresses + ASI:One shared-chat URL | `[[WAIT:FETCH-URLS]]` | Fri-night capture | same block |
| Slide 1 + 12: team name, names/photos/credentials | `[[WAIT:TEAM]]` | human-written, never AI-drafted | T3 emails the exact text + up to 3 photos Fri evening. If it has not arrived by Sat 07:00, chase T3; if still missing at 07:45, ship slide 12 with photos and role titles only — a thin true slide beats a rich fake one. |
| Slide 12 practitioner-validation line | `[[WAIT:TEAM]]` | only if outreach really happened | Only include if T3's email says "TRUE, include". Otherwise delete cleanly. |

The METRICS BLOCK T3 sends at 21:30 Friday uses exactly this template (T3: copy it from here):

```
METRICS BLOCK — FINAL (from T3, Fri 21:30)
P99_permission_check_ms =
P50_ms =
extractor_correct_match_pct =
extractor_safe_degrade_pct =
extractor_false_fastpath_pct =
agentverse_watcher_url =
agentverse_librarian_url =
agentverse_operator_url =
asi_one_shared_chat_url =
public_repo_url =            (N2 needs this for the video's shot-8 caption — same block goes to both)
team_name =
slide12_practitioner_line = TRUE + text / FALSE
notes = (any cell empty ⇒ degraded rule: N1 deletes that cell from the deck)
```

## 6. Final export sequence (Saturday, in this order — do not reorder)

1. Fill all `[[WAIT:...]]` cells from the metrics block (Conversation D4 helps).
2. **Placeholder sweep**: Edit > Find for `‹` — zero results. Then Find for `[[WAIT` — zero results. This is the deck-side version of the team's "never ship ‹XX›" rule.
3. **File > Make a copy** named "Precedent — deck (stage)". Export that copy to PDF now — this is the clean stage backup.
4. In the ORIGINAL file, add the caption layer: on each of the 12 core slides, a single-line grey (#8A8F98, ~12pt) caption bar across the bottom with that slide's Conversation-D3 sentence. Add the "What exists Monday morning" appendix slide at the very end.
5. Export to PDF: "Precedent — deck (submission).pdf".
6. Email both PDFs + the Slides share link (anyone-with-link, viewer) to **T3 by 08:00 Saturday**. WhatsApp T3 "DECK SENT". T3 attaches the submission PDF to the DoraHacks draft at 08:30 and commits a copy to the repo.

## 7. What DONE looks like

- [ ] 12 core + 9 appendix slides matching the spec verbatim; PDF adds captions + 1 extra slide.
- [ ] All numbers match the metrics block / evidence files, calendar-vs-business-hour labels intact.
- [ ] Zero `‹` and zero `[[WAIT` anywhere in either exported PDF.
- [ ] Vendor-claimed superscripts present (slide 11 Encompass/Amagi figures; Moveworks deflection row in A1).
- [ ] Banned vocabulary absent from core slides.
- [ ] Both PDFs + share link with T3 by Sat 08:00.

## 8. If you are squeezed (cut rules — the demo and honesty win every conflict with ambition)

Cut in this order, and tell T3 what you cut: (1) appendix A6 and A8 layout polish (plain text tables are fine — appendix slides are never shown unprompted); (2) slide artwork/diagrams degrade to labelled boxes and arrows — never cut the slide-5 time bars, they are the pitch; (3) if Saturday collapses entirely, the minimum shippable deck is the 12 core slides + A1 + A2 with captions — appendix Q&A slides are insurance, the core deck is the submission. Never cut: the placeholder sweep, the caption layer, the calendar/business-hours labels.
