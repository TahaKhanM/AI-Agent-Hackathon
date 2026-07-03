# PACKET N1-DECK — Build the Precedent pitch deck (12 core + 9 appendix slides)

> WHO OWNS THIS: **N1** — owns the data+content lane AND the deck. You have repo access and a capable AI coding tool (Claude Code / Codex-class). You build the deck and **commit it yourself** (branch/worktree → merge or PR per team convention). No one relays files to you and no one commits on your behalf.
> WHERE IT FITS IN THE PLAN'S PHASES: the deck is a **harden+ambition** deliverable, not a foundations one. Two hard demo-critical items in your lane come first — the KB articles (packet N1-KB) and the licence packet (N1-LICENCE) — because the sim can't run without them. Draft the core deck structure any time after kickoff (the spec is already written), but the **numbers-fill and final export happen after T3's bench + extractor numbers land**, and the whole thing must be committed **before the freeze** so Saturday is pure assemble/submit.
> WHAT ARRIVES FROM ELSEWHERE: the measured numbers (P99, extractor correct-match/safe-degrade/false-fast-path, Agentverse addresses, ASI:One URL) come from **T3's bench + extractor runs** and the Fetch-rail capture. You pull them from the repo once they're committed — see §5.

---

## 0. What you are making and why it matters

The deck spec file **IS the deck**: `Idea/refinement/03-pitch-deck.md` contains every slide's on-slide text, layout notes, and speaker notes, already written and judge-reviewed. Your job is transcription with discipline, not creative writing. Roughly half the judges will only ever see the **PDF export with no speaker** — so the PDF must self-narrate (caption layer, §6) and must never contain an unfilled placeholder.

Deliverables:
1. The deck: **12 core slides + 9 appendix slides (A1–A9, in the file's order — note the file lists A9 before A8; keep the file's order)**.
2. A **clean stage PDF** (no captions) — backup for Demo Day.
3. A **submission PDF** with the caption layer + one extra appendix slide ("What exists Monday morning") — this is what goes to DoraHacks.

**Two ways to build it (pick one):**
- **Google Slides** — fastest, most familiar, easiest for teammates to review live. Export the two PDFs and commit them to the repo (`docs/submission/`). Keep the Slides share link in the PR description.
- **Versioned HTML/Reveal deck in the repo (ambition option — see §9)** — a small self-contained `docs/deck/` Reveal.js or plain HTML deck that lives in git, diffs cleanly, and exports to PDF via print-to-PDF. Choose this only if it won't crowd out the KB/licence work or the numbers-fill. Either way the honesty rules and the caption/placeholder discipline are identical.

## 1. Repo files you work from

| # | Repo path | Why you need it |
|---|---|---|
| 1 | `Idea/refinement/03-pitch-deck.md` | The deck spec — the single source of truth for on-slide text, layout, speaker notes |
| 2 | `data/analysis/uci-baseline-results.md` | Our measured numbers (94.4% / 18.2h / 558 classes) — for the QC pass |
| 3 | `Research/00-verified-claims.md` | Every industry number's verified source — for the QC pass |

Read these straight from your checkout. When you drive your AI tool, point it at these paths rather than pasting contents by hand.

## 2. Ground rules (read once, obey always)

- **Verbatim on-slide text.** Copy on-slide text and every number EXACTLY from `03-pitch-deck.md`. Do not reword, shorten, or "improve" on-slide copy or any figure.
- **Never ship a placeholder.** No `‹XX›`, no `‹Name›`, no `[[WAIT:…]]` in any exported PDF. This is the deck-side version of the team's never-ship-‹XX› rule (§6 sweep enforces it).
- **No secrets.** Never put keys, tokens, or anything sensitive on a slide or in the repo. Slide 1/12 team text is human-written and true — role titles and real names only, never AI-invented credentials.
- **Caption discipline.** The PDF caption layer says exactly what the speaker would have said — one grey line per core slide, drawn from that slide's speaker notes. No new claims sneak in via captions.

## 3. Deck setup (do this once before building)

**If Google Slides:** New file named **"Precedent — Demo Day deck"**, Widescreen 16:9.
**If HTML/Reveal:** scaffold `docs/deck/` with one section per slide; the theme rules below become CSS variables.

Theme (the spec's design rules, made concrete — keep these exact so the deck is consistent):
- Background: very dark **#0B0F14** on every slide.
- Body text: **#E6E6E6**, font **Inter** (or Roboto if Inter is unavailable), ~18pt.
- ONE accent colour: **green #34D399** (matches the console's elapsed-time green). Used for: big numbers, the kicker lines, the "second time is free" text. If T1 vetoes the colour, recolouring is one theme edit — don't block on it.
- Big numbers ("8.85 hours", "$600B", "$2.85B"): **3–5x body size** (60–90pt).
- Max ~15 words of body text per slide; no bullet list longer than 3 on any core slide.
- Every vendor-claimed number gets a small superscript "(vendor-claimed)".

**Banned vocabulary on core slides** (allowed in speaker notes and appendix only): agent names (Watcher/Librarian/Assessor/Operator/Auditor), YAML, ACL, SoD, "five-element schema". The two lines the room must remember: **"the second time is free"** and **"it knows what it's not allowed to touch."**

**Slide 5's three time bars** are load-bearing: draw three rounded rectangles — the 8.85-hr bar spans the full slide width; the 60s and 15s bars are thin slivers. The visual joke IS the point. Never degrade or cut this slide.

## 4. Driving your AI tool

You have a good model — you don't need a locked script. Point it at `Idea/refinement/03-pitch-deck.md` and have it produce **build sheets** you transcribe into slides (or generate the HTML sections directly if you took the Reveal option). A build sheet per slide should give you:

1. **Slide title** (your reference)
2. **On-slide text** — verbatim from the file, in placement order (largest element first)
3. **Layout** — the file's visual/layout notes as 3–6 plain-English steps (text boxes, relative sizes, simple shapes like horizontal bars or badges)
4. **Speaker notes** — verbatim from the file, ready to paste
5. **Placeholder flags** — every `‹…›` token and what fills it later (§5)

Make the tool **verify** as it goes:
- On-slide text and numbers match the spec character-for-character (have it diff its output against the file).
- Banned vocabulary (agent names / YAML / ACL / SoD / "five-element schema") appears in **zero** core slides.
- Every `‹…›` and `[[WAIT:…]]` token is surfaced in a running checklist, never silently dropped.

Suggested passes (adapt freely):
- **Core 1–6**, then **core 7–12** — plus the file's "PLACEHOLDERS TO FILL BEFORE EXPORT" section as a checklist to keep beside you.
- **Appendix A1–A9** in the file's own order (A1, A2, A3, A4, A5, A6, A7, **A9, A8** — yes, A9 before A8, keep it). These are Q&A backup slides: plain layouts, small type, tables allowed.
- **PDF caption layer**: for each of the 12 core slides, one single-line grey caption — the sentence the speaker would have said, drawn from that slide's speaker notes. (The file gives slide 7's example: *"No one approved that second ticket — the approval moved earlier in time; it never left the loop."*)
- **The extra PDF-only appendix slide "What exists Monday morning"**: a 4-item list of exactly the durable artifacts the file's PDF EXPORT LAYER section names — hosted Watcher live on Agentverse · `precedent_memory` as a standalone importable library · the ground-truth conformance bench · the public evidence index. No human-intent claims.

## 5. Cells that WAIT for late numbers — and how they reach you

Build everything else first. Mark each waiting cell with the literal token `[[WAIT:name]]` (never `‹XX›` — and never export while either token exists). These numbers come from other people's committed work; you pull them from the repo, you don't wait on an email.

| Waiting cell | Token | Filled by | How it reaches you |
|---|---|---|---|
| Slide 10 metrics strip: P99 ms + extractor correct-match / safe-degrade / false fast-path % | `[[WAIT:BENCH]]` | **T3's bench + extractor run** | Land in the repo (bench output / results file). Pull them once T3's numbers are committed. |
| Appendix A4: P99 sentence | `[[WAIT:BENCH]]` | same | same |
| Appendix A7: 3 Agentverse addresses + ASI:One shared-chat URL | `[[WAIT:FETCH-URLS]]` | **T1's Fetch-rail capture** | Committed alongside the rail work / captured during a demo run. |
| Slide 1 + 12: team name, names/role titles/credentials | `[[WAIT:TEAM]]` | human-written, never AI-drafted | The team supplies the exact text. If it hasn't landed by the freeze, ship slide 12 with role titles only — a thin true slide beats a rich fake one. |
| Slide 12 practitioner-validation line | `[[WAIT:TEAM]]` | only if outreach really happened | Include only if outreach genuinely happened and someone confirms "TRUE, include". Otherwise delete the line cleanly (never fabricate a quote). |

**Number-honesty rules (do not blend):** `18.2h` is **CALENDAR** hours and must keep that label; `8.85h` is **BUSINESS** hours; never blended or averaged. When you fill the slide-10 strip, verify every number against `uci-baseline-results.md` / `00-verified-claims.md` with the same framing the source uses.

**Degraded rule for any missing cell:** if a bench/URL/team value still isn't available at the freeze, **DELETE that cell from the strip entirely** and ship only the measured, committed numbers (e.g. the `94% / 18.2h / 558-class` baseline). Never ship a bracket or a placeholder to fill the gap.

## 6. Final export sequence (in this order — do not reorder)

1. **Fill all `[[WAIT:...]]` cells** from the numbers now committed to the repo (bench/extractor from T3, Fetch URLs from T1, team text from the team). Apply the degraded rule to any still-missing cell.
2. **Placeholder sweep**: search the deck for `‹` — zero results. Then search for `[[WAIT` — zero results. This is the deck-side version of the team's "never ship ‹XX›" rule. (In Google Slides: Edit > Find. In HTML: grep the source.)
3. **Clean stage PDF**: make a copy named "Precedent — deck (stage)" and export it to PDF now — the clean, caption-free backup for Demo Day.
4. **Caption layer**: on each of the 12 core slides, add a single-line grey (**#8A8F98**, ~12pt) caption bar across the bottom with that slide's caption sentence. Add the "What exists Monday morning" appendix slide at the very end.
5. **Submission PDF**: export "Precedent — deck (submission).pdf".
6. **Commit both PDFs** to the repo (`docs/submission/precedent-deck.pdf` for the submission PDF, plus the stage backup) on your branch/worktree, and open the PR / merge per team convention. Put the Slides share link (anyone-with-link, viewer) in the PR description so teammates can review live. This is the file T3/N2 attach to the DoraHacks submission — get it committed **before the freeze**.

## 7. What DONE looks like

- [ ] 12 core + 9 appendix slides matching the spec verbatim; PDF adds captions + 1 extra slide.
- [ ] All numbers match the committed bench/evidence files; calendar-vs-business-hour labels intact.
- [ ] Zero `‹` and zero `[[WAIT` anywhere in either exported PDF.
- [ ] Vendor-claimed superscripts present (slide 11 Encompass/Amagi figures; Moveworks deflection row in A1).
- [ ] Banned vocabulary absent from core slides.
- [ ] Both PDFs committed + Slides share link in the PR, merged before the freeze.

## 8. If you are squeezed (cut rules — the demo and honesty win every conflict with ambition)

Cut in this order, and flag the team on what you cut: (1) appendix A6 and A8 layout polish (plain text tables are fine — appendix slides are never shown unprompted); (2) slide artwork/diagrams degrade to labelled boxes and arrows — **never cut the slide-5 time bars, they are the pitch**; (3) if things collapse entirely, the minimum shippable deck is the **12 core slides + A1 + A2 with captions** — appendix Q&A slides are insurance, the core deck is the submission. Never cut: the placeholder sweep, the caption layer, the calendar/business-hours labels.

## 9. Ambition hook (§5 ladder — optional, only after the core deck is committed)

If the deck is done and committed well before the freeze, the on-ladder move for your lane is the **versioned HTML/Reveal deck in the repo** (§0 option two): a self-contained `docs/deck/` that diffs cleanly in git and print-to-PDFs to the same two outputs. It makes the deck a reviewable artifact rather than an external doc, and pairs naturally with the team's other artifact ambition beats (change-record artifact, public evidence index). Also worth folding in if the numbers land: a live-metrics appendix slide sourced from the actual bench output. Do NOT start this if it would push the KB/licence work, the numbers-fill, or the pre-freeze commit at any risk — a committed, honest Google Slides deck beats a half-built HTML one.
