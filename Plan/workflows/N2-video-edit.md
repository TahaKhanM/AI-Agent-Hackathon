# PACKET N2-VIDEO — Assemble the 4:30 video, 30s teaser, and (conditional) 90s cut in CapCut

> WHO RUNS THIS: **N2** — non-technical teammate, working on **claude.ai FREE tier**, no repo access. Everything you need is in this file, the attachment T3 sends, and the raw-clip Drive folder.
> WHO BUNDLES AND SENDS: **T3** prepares the shot-list extract (§1) and emails it to N2; **T3 also creates a shared Google Drive folder "precedent-video-drop" by Fri 13:00** — T2 drops labelled raw clips there, N1 drops VO files there.
> WHO RECEIVES OUTPUT AND COMMITS: N2 puts exports in the same Drive folder and WhatsApps T3; **T3 uploads the master unlisted (YouTube) and pushes the link** into the DoraHacks BUIDL, the BasedAI PR, and the repo README (video-link push must land before **G6, Sat 08:45**).
> WHERE THIS FITS IN N2's DAY: Friday **13:30–21:30** (project setup, captions, insurance cut, first clean clips — your shift was deliberately late-shifted to cover the freeze/recording window). Saturday **06:30–09:30** (final assembly + exports + hand-off by 08:15).

---

## 0. What you are making and why it matters

One recording session (T2, Friday 21:00–22:30, against frozen code) feeds every video artifact. You assemble:

1. **The main cut, ~4:30** — this single video serves BOTH the DoraHacks/Conduct submission and the Fetch.ai 3–5 min deliverable. The ASI:One segment (shot 5) is the Fetch centerpiece: 80 seconds, top billing, never shortened.
2. **The 30-second teaser** — 6 stills with captions. Non-negotiable: it is the only before/after a skimming judge sees if the team is not selected to present.
3. **The not-selected 90-second cut** — built Saturday ONLY if the ~22:00 Friday announcement says no stage slot (T3 will WhatsApp you Friday night either way).
4. **The chapter-marker export for the QuickTime backup** — the live-demo fallback the presenters switch to on stage if the console dies.
5. **The insurance cut** (Friday evening) — a rough assembly of the 16:00 "dirty take" with scratch VO, so a broken evening still yields a narratable video.

Caption text is **verbatim** from the shot list — captions are load-bearing (they carry the sourced numbers) and were judge-reviewed word by word. Do not reword captions. Production style per the spec: 1080p screen capture, VO recorded separately, captions as simple lower-third text, **no motion graphics**.

## 1. What T3 sends you (Friday by 13:30)

| # | What | Source |
|---|---|---|
| 1 | `04-extract-shot-list.md` — T3 copies everything from the heading `## 7. VIDEO SCRIPT` to the end of `## 8. 30-SECOND TEASER CUT` (including the "Video recording checklist" and "NOT-SELECTED branch inserts") out of `Idea/refinement/04-demo-and-video-script.md` into one small file | email attachment |
| 2 | Link to the **precedent-video-drop** Drive folder | WhatsApp |
| 3 | (Friday ~21:30) the METRICS BLOCK (same one the deck gets) — you need `P99_permission_check_ms` for shot 7's caption and the repo URL for shot 8's caption | email + WhatsApp |

## 2. The raw material and its labelling contract

T2 labels every clip dropped into Drive using this scheme (this packet is the contract — if a clip arrives unlabelled, WhatsApp T2 via T3 rather than guessing):

```
raw_dirty16h.mp4                     Friday 16:00 insurance capture (whatever ran end-to-end)
raw_shot03_consolepan_takeN.mp4      console home slow pan, provenance footer zoom
raw_shot04_incident1_takeN.mp4      messy ticket -> approve -> Jira closes -> Promote click
raw_shot05_asione_takeN.mp4         the full ASI:One conversation, cursor visible
raw_shot06_recovery_refusal_takeN.mp4  failed verify -> rollback -> demotion; then refusal
raw_shot07_terminal_takeN.mp4       141k ingest run + latency chart + one architecture slide
raw_livemirror_takeN.mp4            full-speed console run mirroring the live script (for the backup)
still_teaser_1..6.png               the 6 teaser frames (or you screengrab them from clips)
asset_skynews_headline.png          shot 1 headline still
asset_manual_loop_timelapse.mp4     the sped-up manual "before" capture
```

VO files from N1 (see §6): `VO_shot1.m4a` … `VO_shot8.m4a`, plus `VO_scratch60.m4a`. Shot 0 has **no VO** — captions and music only.

## 3. The captions — VERBATIM (paste these into CapCut text layers, lower-third, plain)

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

## 4. Claude conversations (chunked prompts — copy-paste verbatim)

### Conversation V1 (Fri ~13:45) — turn the shot list into a CapCut assembly plan
Attach: `04-extract-shot-list.md` only. Paste:

```
I am assembling a ~4:30 hackathon demo video in CapCut on a tight deadline. The attached file is
the authoritative shot list: a table of shots 0-8 with durations, visuals, voice-over text, and
caption overlays, plus a 30-second teaser spec and a recording checklist.

I am a beginner CapCut editor. Produce, in this order:
1. An EDIT DECISION LIST: one row per shot — start time, end time (remember shot 0 shifts
   everything +14s; treat the file's times as durations), which raw clip goes there (clips are
   named raw_shotNN_description_takeN.mp4), any speed change (shot 4 runs at 1.5x with cuts),
   and which VO file (VO_shot1.m4a ... VO_shot8.m4a; shot 0 has no VO).
2. A step-by-step CapCut checklist for a beginner: import bins, placing clips, adding lower-third
   text captions (I will paste caption text myself — just tell me where each goes and roughly when
   it should appear/disappear), adding VO audio under each shot, one music bed under shot 0 only,
   export settings for 1080p MP4.
3. A 60-second scratch voice-over script titled "what we built and why" for an insurance cut:
   plain first-person, no jargon, drawn ONLY from the attached file's VO column — it must cover:
   the manual loop and 8h51m, one human click and 58 seconds, the 15-second pre-approved repeat,
   the refusal ("it knows what it's not allowed to touch"), and the closing line "the second time
   is free". No numbers that are not in the attached file.
4. A QC checklist to run before every export (audio levels consistent, captions on screen long
   enough to read, no clip flash-frames, total runtime between 4:15 and 4:45).

Give me item 1 first, then wait for "next".
```

Send item 3 (the scratch VO script) to T3 by 15:00 — T3 forwards it to N1 to record.

### Conversation V2 (Fri ~18:30) — teaser build sheet + 90s-cut EDL
New chat. Attach: `04-extract-shot-list.md` only. Paste:

```
Same project, same attached shot list. Two more build sheets:

1. THE 30-SECOND TEASER: the file's section 8 specifies 6 beats, each a 5-second frame with a
   short caption, plus a strapline. Give me a CapCut build sheet: which still/frame to use for
   each beat (from clips named in the file's shot list), the exact caption per beat COPIED
   VERBATIM from the file's teaser table, the strapline verbatim, and beginner steps to build a
   30s cut with hard cuts every 5 seconds, captions only, no VO.

2. THE 90-SECOND STANDALONE CUT (only built if the team is not selected to present): beats are
   Baseline Bar "before" -> the 15-second pre-approved repeat -> the refusal -> the ask. Give me
   an EDL: source material per beat (shot 2 material for the before, incident-2 material from
   shots 4/5 for the repeat with its on-screen stopwatch, the refusal half of shot 6, the close
   from shot 8), duration per beat totalling 90s, which existing captions to reuse, and which VO
   lines from the file's VO column to reuse (trimmed, verbatim — no new sentences).
```

### Conversation V3 (Sat, only if stuck) — troubleshooting
New chat, no attachments. Describe the specific CapCut problem in 2–3 sentences. Keep it short; your Saturday time is assembly time, not chat time.

## 5. Timeline (what you do when)

**Friday**
- 13:30–14:30 — Read this packet. Run Conversation V1. Create the CapCut project (1080p, 30fps). Build caption text layers from §3 into a saved preset/style.
- 15:00 — Send the scratch VO script to T3 (for N1).
- ~16:15 — `raw_dirty16h.mp4` lands in Drive. Rough-assemble the **insurance cut**: dirty take + `VO_scratch60.m4a` (arrives ~17:30) + shot 0-style caption card. Export by 19:00, drop in Drive, WhatsApp T3 "INSURANCE CUT BANKED". If the evening collapses, this is the video — that is its whole job.
- 18:30 — Run Conversation V2. Build the teaser skeleton with placeholder frames.
- 21:00–21:30 — First clean clips land as T2 records. Pull them, check labels, start replacing dirty material. **At 21:30 your shift ends — stop.** The remaining clips (T2 records until ~22:30) will be in Drive for your Saturday block.
- ~22:00 — T3 WhatsApps the selection announcement (G5): SELECTED or NOT SELECTED. This decides whether Saturday includes the 90s cut.

**Saturday (06:30–09:30; exports must leave your hands by 08:15)**
- 06:30–07:40 — Final assembly of the main cut: all clean clips, all VO, captions with §3 EDIT 1+2 applied from the metrics block. Then the teaser (replace placeholder frames with real stills).
- 07:40–07:55 — Export main cut + teaser (start both, they can render back-to-back).
- IF NOT SELECTED: also cut the 90s version (Conversation V2's EDL) and export — it goes FIRST on the DoraHacks BUIDL page, above the 4:30 cut. T2 may drop two extra inserts in Drive Saturday morning (a 10s phone party-trick shot and a 15s Jira RESTRICT capture, per the spec's not-selected branch); if they are there by 07:00, splice them into shots 4 and 6 respectively — if not, ship without them. The submission deadline beats the extra footage.
- 08:00–08:15 — Drop all exports + `backup-chapters.txt` (§7) in Drive. WhatsApp T3 "VIDEO FINAL IN DRIVE". T3 uploads unlisted and pushes the link before G6 (Sat 08:45).

## 6. Input you depend on: N1's voice-over (T3 forwards this sub-section to N1 on Friday morning)

N1: record the VO for shots 1–8 from the **VO column of the shot-list extract, read verbatim** — these sentences were written to fit the shot durations at ~150 words/minute. Quiet room, phone voice-memo app is fine, hold the phone ~20cm away, one file per shot, re-take until there are no stumbles (each is only 15–80 seconds).

- Files: `VO_shot1.m4a` … `VO_shot8.m4a` (shot 0 needs nothing), plus `VO_scratch60.m4a` from the 60-second scratch script T3 forwards ~15:00.
- Slot: Friday **17:15–18:00** (after the deck-core block).
- Upload all files to the precedent-video-drop Drive folder by 18:00; WhatsApp T3 "VO UP".
- Do not improvise or "fix" sentences — every number in the VO is consistency-table-locked. If a sentence feels unsayable, record it as written AND flag it to T3; the words change only if T1 signs it off.

## 7. The chapter-marker export (the live-demo QuickTime backup)

The presenters' on-stage fallback is a **full-speed console run that mirrors the live script** (source: `raw_livemirror_takeN.mp4` — NOT your 4:30 promo cut, which is condensed and speed-ramped). Your deliverables:

1. Trim the best livemirror take into `backup-livemirror.mp4`: continuous, real-time, starting at the hook and running through the refusal. No captions, no VO (a presenter narrates it live).
2. Create `backup-chapters.txt` with the beat boundaries as they land in YOUR trimmed file (target values from the live script; adjust to the actual take):

```
00:00  Beat 0 — hook / manual before
00:25  Beat 1 — incident 1 (messy ticket -> approve)
01:20  Beat 2 — 15s standing-approval repeat
01:50  Beat R — recovery (rollback + demotion)
02:10  Beat 3 — refusal (rights runbook)
```

3. Drop both in Drive Friday night if the livemirror take arrives before 21:30, otherwise first thing Saturday. T2 loads the file into QuickTime and uses the txt to pre-position at chapter points during rehearsal (G7, Sat 09:00–09:30).

## 8. What DONE looks like

- [ ] Insurance cut banked in Drive Friday by 19:00.
- [ ] Main cut ~4:30 (never <3:30, never >5:00 — Fetch requires 3–5 min), shot 5 at full 80s, captions verbatim with EDIT 1+2 applied, no `[measured]`, no `[repo]` left anywhere.
- [ ] 30s teaser: 6 frames, verbatim captions, strapline: **"8h51m → 15 seconds — with a human's approval always in the loop."**
- [ ] `backup-livemirror.mp4` + `backup-chapters.txt` in Drive.
- [ ] 90s cut exported IF not selected.
- [ ] Everything in Drive + T3 pinged by Sat 08:15.

## 9. Cut rules if squeezed (the demo and the deadline win every conflict with polish)

In order: (1) drop music entirely (shot 0 works silent with captions); (2) captions may sit on plain black bars instead of styled lower-thirds; (3) drop the not-selected inserts (party-trick / RESTRICT) even if footage exists; (4) if Saturday assembly overruns, ship the main cut and teaser and let the 90s cut die — the 4:30 cut satisfies every track's requirement, the 90s cut is a skim-optimisation. Never cut: shot 5's 80 seconds, the verbatim captions, the 08:15 hand-off.
