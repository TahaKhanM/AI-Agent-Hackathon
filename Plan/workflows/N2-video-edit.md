# PACKET N2-VIDEO — Assemble the ~4:30 video, 30s teaser, and (conditional) 90s cut

> WHO RUNS THIS: **N2** — owns the video + submissions + outreach + QA lane. You have repo access and a capable AI editing/assist stack. You cut in CapCut/Descript (or your editor of choice) and you commit your own artifacts and the video-link updates directly (branch/worktree → merge or PR per team convention).
> WHERE THE RAW MATERIAL COMES FROM: **T2** drops labelled raw screen-recording clips into the shared `precedent-video-drop` folder; **N1** drops the VO files there. Real screen recordings only — no stock, no mockups, no reconstructions.
> WHERE THIS FITS: this is a late-lane job. You do project setup, captions, and the insurance cut early; the main assembly happens **after the freeze recording session lands** and rides the **Saturday assemble/submit** phase. The video link (unlisted YouTube master) must be pushed into the DoraHacks BUIDL, the BasedAI PR, and the repo README **before the submission freeze**.

---

## 0. What you are making and why it matters

One recording session (T2, against **frozen code** during the freeze window) feeds every video artifact. You assemble:

1. **The main cut, ~4:30** — this single video serves BOTH the DoraHacks/Conduct submission and the Fetch.ai 3–5 min deliverable. The ASI:One segment (shot 5) is the Fetch centerpiece: 80 seconds, top billing, never shortened.
2. **The 30-second teaser** — 6 stills with captions. Non-negotiable: it is the only before/after a skimming judge sees if the team is not selected to present.
3. **The not-selected 90-second cut** — built only if the selection announcement says no stage slot (you'll know before the Saturday phase).
4. **The chapter-marker export for the QuickTime backup** — the live-demo fallback the presenters switch to on stage if the console dies.
5. **The insurance cut** (early, before the freeze) — a rough assembly of the "dirty take" with scratch VO, so a broken evening still yields a narratable video.

Caption text is **verbatim** from the shot list — captions are load-bearing (they carry the sourced numbers) and were judge-reviewed word by word. Do not reword captions. Production style per the spec: 1080p screen capture, VO recorded separately, captions as simple lower-third text, **no motion graphics**.

## 1. What you work from

Everything is in the repo — pull it, don't wait for anyone to bundle it:

| # | What | Where |
|---|---|---|
| 1 | **The shot list** — the authoritative table of shots 0–8 (durations, visuals, VO text, caption overlays), the 30-second teaser spec, the recording checklist, and the NOT-SELECTED branch inserts | `Idea/refinement/04-demo-and-video-script.md`, sections `## 7. VIDEO SCRIPT` through `## 8. 30-SECOND TEASER CUT` |
| 2 | **The raw clips + VO** | the shared `precedent-video-drop` folder (T2 drops clips, N1 drops VO) |
| 3 | **The METRICS BLOCK** (same one the deck uses) — you need the measured **P99 permission-check** value for shot 7's caption and the real public **repo URL** for shot 8's caption | lands from T3's bench run; check the repo/metrics artifact once T3's numbers are in |

## 2. The raw material and its labelling contract

T2 labels every clip dropped into the folder using this scheme. If a clip arrives unlabelled or ambiguous, ping T2 rather than guessing — a mislabelled clip in the wrong shot is a correctness bug in the video:

```
raw_dirty16h.mp4                     early insurance capture (whatever ran end-to-end)
raw_shot03_consolepan_takeN.mp4      console home slow pan, provenance footer zoom
raw_shot04_incident1_takeN.mp4       messy ticket -> approve -> Jira closes -> Promote click
raw_shot05_asione_takeN.mp4          the full ASI:One conversation, cursor visible
raw_shot06_recovery_refusal_takeN.mp4  failed verify -> rollback -> demotion; then refusal
raw_shot07_terminal_takeN.mp4        141k ingest run + latency chart + one architecture slide
raw_livemirror_takeN.mp4             full-speed console run mirroring the live script (for the backup)
still_teaser_1..6.png                the 6 teaser frames (or you screengrab them from clips)
asset_skynews_headline.png           shot 1 headline still
asset_manual_loop_timelapse.mp4      the sped-up manual "before" capture
```

VO files from N1 (see §6): `VO_shot1.m4a` … `VO_shot8.m4a`, plus `VO_scratch60.m4a`. Shot 0 has **no VO** — captions and music only.

## 3. The captions — VERBATIM (paste these into your editor's text layers, lower-third, plain)

These are copied from the shot list's caption column. The only two edits you are allowed to make are marked.

| Shot | Caption text (verbatim) |
|---|---|
| 0 | **8 h 51 m → 15 seconds. Approval never leaves the loop.** |
| 1 | **Downtime: $600B/yr across the Global 2000 (Splunk 2026) — ~$200M per company** |
| 2 | **8h51m avg MTTR (MetricNet)** · **>60% repeat incidents (ServiceNow KCS study)** |
| 3 | **Real data: UCI ServiceNow log (141k events, CC BY 4.0) · GitLab/K8s runbooks · CrowdStrike remediation bulletin · TVmaze/XMLTV programme metadata (CC BY-SA)** |
| 4 | **58 seconds vs 8h51m** · **Human approval — requester ≠ approver, immutably logged** |
| 5 | **3 agents on Agentverse · Agent Chat Protocol · discoverable via ASI:One** · **agent addresses on screen** · **Approver = chat sender, logged** · **Runs without any custom frontend** |
| 6 | **Auto-rollback on failed verification → class demoted** · **Permission-aware memory: restricted runbook → refusal, audited** |
| 7 | **141k events / 24,918 incidents ingested · 94% pre-matched to a documented fix · P99 permission-check: [measured] ms over the 25k-record store** · **Graduation: 3 verified successes → standing approval; any rollback → demote** · **100% open-weight models (Venice-served), named in README** — EDIT 1: replace `[measured]` with the P99 value from the metrics block. WARNING (from the spec): the caption must say **"25k-record store"**, never "P99 over 141k events". If no P99 arrives, delete that clause entirely — never ship a bracket. |
| 8 | **github.com/[repo] · ASI:One shared chat · Agentverse profiles** · **Precedent — the second time is free** — EDIT 2: replace `github.com/[repo]` with the real public repo URL from the metrics block. |

Timing note from the spec: shot 0 adds 14s at the front, so the shot-list timestamps are **durations, not absolutes**. Total runtime ~4:30. If it must shrink toward 3:30: compress shot 4 to 25s and shot 7 to 15s — **never shot 5, never shot 0**.

Honesty guardrails baked into these captions — do not drift off them:
- **"25k-record store"**, calendar-hours framing ("8h51m") — never restate P99 as "over 141k events", never invent a duration.
- **No unlabelled vendor claim** — every third-party number on screen carries its source (Splunk 2026, MetricNet, ServiceNow, UCI, CrowdStrike). If you can't attribute it, it doesn't go on screen.
- **Never ship a bracket** — no `[measured]`, no `[repo]`, no `‹XX›` in any exported frame. If the real value hasn't landed, delete the clause per EDIT 1's rule rather than shipping a placeholder.
- TMDB was rejected as a source — do not reintroduce it in any caption or lower-third.

## 4. Driving your AI tool

You have a capable model — use it to turn the shot list into an assembly plan, not to write your captions (those are locked in §3). Point it at `Idea/refinement/04-demo-and-video-script.md` (sections 7–8) and ask it to produce, and make it **verify each item against the file** before you trust it:

- **An edit decision list** — one row per shot: start/end time (remember shot 0 shifts everything +14s; treat the file's times as durations), which raw clip goes there (`raw_shotNN_description_takeN.mp4`), any speed change (shot 4 runs ~1.5x with cuts), and which VO file (`VO_shot1.m4a` … `VO_shot8.m4a`; shot 0 has none). Have it flag any shot where the total drifts outside 4:15–4:45.
- **A beginner-safe editor checklist** — import bins, placing clips, adding lower-third text captions (you paste the §3 text yourself — it just tells you where each goes and roughly when it appears/disappears), VO audio under each shot, one music bed under shot 0 only, 1080p MP4 export settings.
- **A 60-second scratch VO script** titled "what we built and why" for the insurance cut: plain first-person, no jargon, drawn ONLY from the file's VO column — must cover the manual loop and 8h51m, one human click and 58 seconds, the 15-second pre-approved repeat, the refusal ("it knows what it's not allowed to touch"), and the closing line "the second time is free". **No number that isn't in the file.** Hand this to N1 early so the scratch VO (`VO_scratch60.m4a`) can be recorded while you build.
- **The teaser build sheet** — section 8 specifies 6 beats, each a 5-second frame with a short caption + a strapline. Have it map each beat to a still/frame from the named clips, list the exact caption per beat COPIED VERBATIM from the file's teaser table, the strapline verbatim, and hard-cut-every-5s steps (captions only, no VO).
- **The 90-second standalone EDL** (only if not selected) — beats: Baseline Bar "before" → the 15-second pre-approved repeat → the refusal → the ask. Source per beat: shot 2 material for the before, incident-2 material from shots 4/5 for the repeat (with its on-screen stopwatch), the refusal half of shot 6, the close from shot 8. Duration per beat totalling 90s, which existing §3 captions to reuse, which VO lines from the file's VO column to reuse (trimmed, verbatim — no new sentences).

The model drafts structure; the file is truth. If the model produces a caption or a number that isn't in §3 or the shot list, discard it.

## 5. Phases (what you do when)

**Setup / foundations phase**
- Read this packet and the shot list. Create the project (1080p, 30fps). Build the §3 caption text layers into a saved preset/style so every shot pulls from the same source of truth.
- Get the 60-second scratch VO script (§4) to N1 as early as possible — it unblocks the insurance cut and gives N1 a warm-up read before the real VO.

**Before the freeze — bank the insurance cut**
- When `raw_dirty16h.mp4` lands, rough-assemble the **insurance cut**: dirty take + `VO_scratch60.m4a` + a shot-0-style caption card. Export it and drop it in the folder; tell the team "INSURANCE CUT BANKED". If the evening collapses, this is the video — that is its whole job.
- Build the teaser skeleton with placeholder frames so only the real stills need swapping later.

**Freeze recording lands**
- As T2 records clean clips against frozen code, pull them, check labels against §2, and replace dirty material. Don't block on the last clip — T2 finishes the session after you've started.

**Selection announcement (before Saturday assemble)**
- You'll learn SELECTED or NOT SELECTED. This decides whether the Saturday phase includes the 90s cut.

**Saturday assemble/submit phase**
- **Final assembly of the main cut**: all clean clips, all VO, captions with §3 EDIT 1+2 applied from the metrics block (once T3's bench numbers land). Then the teaser (swap placeholders for real stills).
- **Export main cut + teaser** — render back-to-back.
- **IF NOT SELECTED**: also cut the 90s version (the §4 EDL) and export — it goes FIRST on the DoraHacks BUIDL page, above the ~4:30 cut. T2 may drop two extra inserts (a ~10s phone party-trick shot and a ~15s Jira RESTRICT capture, per the not-selected branch); if they're in the folder in time, splice them into shots 4 and 6 respectively — if not, ship without them. **The submission deadline beats the extra footage.**
- **Picture-lock first, then link.** Lock picture on the main cut before the VO is perfect: if a late VO re-take arrives, swap the audio track under a locked picture — never let a VO swap block the PR video link. Upload the picture-locked master as the unlisted YouTube video and push its link into the DoraHacks BUIDL, the BasedAI PR, and the repo README **before the submission freeze**. A re-exported master at the same URL replaces the video without touching the link. Commit the README link update yourself.

## 6. Input you depend on: N1's voice-over

N1 records the VO for shots 1–8 from the **VO column of the shot-list extract, read verbatim** — these sentences were written to fit the shot durations at ~150 words/minute. Quiet room, phone voice-memo app is fine, hold the phone ~20cm away, one file per shot, re-take until there are no stumbles (each is only 15–80 seconds).

- Files: `VO_shot1.m4a` … `VO_shot8.m4a` (shot 0 needs nothing), plus `VO_scratch60.m4a` from the 60-second scratch script (§4).
- Slot: after the deck-core block, before the freeze recording — VO should be in the folder before the Saturday assemble phase so it isn't on the critical path.
- Upload all files to the `precedent-video-drop` folder and post "VO UP".
- Do not improvise or "fix" sentences — every number in the VO is consistency-table-locked. If a sentence feels unsayable, record it as written AND flag it; the words change only if T1 signs it off.

Because you picture-lock first (§5), a late or re-taken VO file never blocks the video link — it drops onto the locked picture.

## 7. The chapter-marker export (the live-demo QuickTime backup)

The presenters' on-stage fallback is a **full-speed console run that mirrors the live script** (source: `raw_livemirror_takeN.mp4` — NOT your ~4:30 promo cut, which is condensed and speed-ramped). Your deliverables:

1. Trim the best livemirror take into `backup-livemirror.mp4`: continuous, real-time, starting at the hook and running through the refusal. No captions, no VO (a presenter narrates it live).
2. Create `backup-chapters.txt` with the beat boundaries as they land in YOUR trimmed file (target values from the live script; adjust to the actual take):

```
00:00  Beat 0 — hook / manual before
00:25  Beat 1 — incident 1 (messy ticket -> approve)
01:20  Beat 2 — 15s standing-approval repeat
01:50  Beat R — recovery (rollback + demotion)
02:10  Beat 3 — refusal (rights runbook)
```

3. Drop both in the folder as soon as the livemirror take arrives (ahead of the rehearsal drill). T2 loads the file into QuickTime and uses the txt to pre-position at chapter points during rehearsal.

## 8. Ambition hook (§5 ladder — only if the beats exist on frozen code)

If T2's ambition beats made it into the freeze recording, the video is where they earn their screen time — but only real captured footage, never a mockup:
- **Temporal-embargo media beat** — if there's a clip showing a future-dated runbook refused until its embargo lifts, it's a strong 5-second insert near shot 6. Caption it truthfully (embargo date visible on screen) or don't use it.
- **Live RESTRICT hotkey / attract-mode idle loop** — the not-selected 90s cut and the teaser can borrow a few seconds of the attract-mode loop or a live RESTRICT toggle if T2 captured it; treat it like the party-trick insert — splice if it lands in time, ship without it if not.
- **Change-record artifact** — if a clip pans the immutable change-record, it reinforces shot 4's "immutably logged" caption. Only include it if the on-screen artifact is real.

Every ambition insert obeys the same rule as everything else: real screen recording, attributed number, no bracket, no reconstruction. If it isn't captured, it isn't in the cut — the base ~4:30 satisfies every track without it.

## 9. What DONE looks like

- [ ] Insurance cut banked in the folder before the freeze.
- [ ] Main cut ~4:30 (never <3:30, never >5:00 — Fetch requires 3–5 min), shot 5 at full 80s, captions verbatim with EDIT 1+2 applied, no `[measured]`, no `[repo]`, no bracket anywhere.
- [ ] 30s teaser: 6 frames, verbatim captions, strapline: **"8h51m → 15 seconds — with a human's approval always in the loop."**
- [ ] `backup-livemirror.mp4` + `backup-chapters.txt` in the folder.
- [ ] 90s cut exported IF not selected.
- [ ] Picture-locked master uploaded unlisted; video link committed into DoraHacks BUIDL, BasedAI PR, and repo README before the submission freeze.

## 10. Cut rules if squeezed (the demo and the deadline win every conflict with polish)

In order: (1) drop music entirely (shot 0 works silent with captions); (2) captions may sit on plain black bars instead of styled lower-thirds; (3) drop the not-selected / ambition inserts (party-trick, RESTRICT, embargo, change-record) even if footage exists; (4) if Saturday assembly overruns, ship the main cut and teaser and let the 90s cut die — the ~4:30 cut satisfies every track's requirement, the 90s cut is a skim-optimisation. Never cut: shot 5's 80 seconds, the verbatim captions, the pre-freeze video-link push.
