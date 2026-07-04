# Ultracode session prompt — Video production (evaluator-builder system)

> **Target model:** Claude **Opus 4.8**, `ultracode` (multi-agent Workflow orchestration, highest reasoning effort). Paste the whole of the section below **"PROMPT — paste from here"** as the first message of a fresh Claude Code session opened in this repo's root. Optionally append a token-budget directive (e.g. `ultracode +600k`).
>
> **Before you start (human checklist):**
> - **This prompt may run in PARALLEL with `Prompts/07-ultracode-code-excellence.md`** (in a separate session) — the body's §PARALLEL-RUN PROTOCOL defines the port/DB namespacing, file ownership, and the `P1.7:` commit-marker sync that makes that safe. The pipeline is built so captures are mechanically re-runnable: it captures against whatever tree is current, and re-captures cheaply when 07's console upgrade merges. If 07 never runs, this prompt still works against the Checkpoint 2 tree; the session must state which tree (HEAD sha) each export was captured from.
> - Grant **Screen Recording permission** to the terminal app once (System Settings → Privacy & Security → Screen Recording) — required for `screencapture -v` / avfoundation fallbacks. Playwright's own recording needs no permission.
> - Homebrew available (the session will `brew install ffmpeg` if missing — say yes to that prompt).
> - **VO decision:** if `ELEVENLABS_API_KEY` is in `.env`, the session synthesizes VO with a **stock voice** (ElevenLabs is an ecosystem partner of this hackathon; never clone anyone's voice). If absent, the session produces a timed scratch track + a human recording kit and you record ~3 minutes of narration from the reconciled script.
> - **The one human-only take:** shot 5 (ASI:One, 80s) needs you logged into ASI:One. The session prepares the exact messages to paste and a capture timer; you perform the take.
> - A stranger for the playtest (`Prep/video/playtest-rubric.md`) before shipping — the session cannot do this.
> - **Media never goes in git.** All raw takes/exports live in `precedent-video-drop/` (gitignored or outside the repo). The auto-sync pushes `main` commits — nothing heavy or unfinished lands there.
> - Deadline: the video URL fills `[[WAIT:VIDEO-LINK]]` in the BasedAI PR and the DoraHacks BUIDL (locks 4 Jul 22:59 UTC).

---

## PROMPT — paste from here

ultracode

# MISSION: Reconcile Precedent's video plan, then produce the master (~4:15–4:45), the 90-second cut, and the 30-second teaser through an agent-automated capture/assembly pipeline — with machine-verified honesty and quality gates, leaving only the account-bound acts to the human

You are a fresh Claude **Opus 4.8** "Ultracode" session with multi-agent **Workflow** orchestration at the highest reasoning effort. Precedent's video *plan* exists (`Prep/video/`: shot list, VO script, cut plans, playtest rubric) but **nothing is recorded**, the plan has internal defects (below), and zero raw assets exist on disk. Your job is an **evaluator-builder system**: builders produce the plan fixes, captures, VO, and cuts; independent evaluators gate every artifact against machine-checkable criteria; the loop iterates until every gate passes. **Evidence before assertions** — paste `ffprobe`/grep output, never claim a gate passed without running it.

The key production insight: **the demo is fully drivable over HTTP** (`make sim`, then `POST /api/drive/{1,2,3}` per `scripts/drive_incident.py`) against the frozen seed-4207 build, so console takes are Playwright-orchestrated, perfectly timed, and infinitely retakeable. The only human-required capture is the ASI:One session (account-bound).

Never commit media or `.env`. Plan-file edits to `Prep/video/*` are committed (they're docs); everything else stays in the gitignored `precedent-video-drop/` tree per the naming convention in `Prep/video/cut-plans-30s-90s.md`.

---

## STEP 0 — Load context + verify the ground (mandatory, in this order)

1. **Invoke the `precedent` project skill FIRST** (Skill tool).
2. Read, in order: `Prep/video/{shot-list,vo-script,cut-plans-30s-90s,playtest-rubric}.md` · `Idea/refinement/04-demo-and-video-script.md` (the source spec, incl. its §0 stage-language rules and §4.3 cut lines) · `Prep/final-numbers.md` (**the only numbers any caption or VO may carry, with their labels**) · `Prep/FINISH-RUNBOOK.md` STEP 8 · `Prep/selection-branch-staging.md` · `Hackathon Information/HACKATHON-GUIDE.md` §3.1 (Conduct: "short and snappy… the problem and the wow moment"), §3.6 (Fetch: 3–5 min deliverable, judging weights), §5 (submission) · `docs/T2-DEMO-RUNBOOK.md`.
3. Verify the ground with your own commands: `make test` green on the tree you will capture (state its HEAD sha in the final report); `make demo-reset` + `make sim` boots; `POST /api/drive/1|2|3` → resolved / resolved(fast) / refused, twice, byte-identical; toolchain check (`ffmpeg -version` — brew-install if missing; `playwright --version` + Chromium; `ELEVENLABS_API_KEY` present or absent — decide the VO branch now and say so).
4. **Frozen invariants:** the build is captured as-is (seed 4207) — this session changes NO product code; shot 5 is 80 s and is never shortened in the master; both memorable lines ("**the second time is free**", "**it knows what it's not allowed to touch**") survive every cut; the master lands in 4:15–4:45 (hard floor 3:30 / ceiling 5:00 — Fetch); the two human EDIT fills (P99 value, repo URL) are template variables that are verified non-bracketed at export — if a value is missing, **the clause is deleted, never bracketed**.

---

## PARALLEL-RUN PROTOCOL (a Prompts/07 code session may be running concurrently — honour this even if you can't see it)

- **Runtime namespacing (mandatory):** run YOUR entire demo stack isolated so you never collide with the 07 session's verifier on the default ports/DBs. Export before any boot:
  `PRECEDENT_CONSOLE_PORT=8200 PRECEDENT_SIM_PORT=8300 PRECEDENT_SIM_URL=http://127.0.0.1:8300 PRECEDENT_MEMORY_DB=precedent-video-drop/scratch/memory.db PRECEDENT_SIM_DB=precedent-video-drop/scratch/sim.db`
  (all five are honoured by `scripts/run_demo.py`, `sim/db.py`, `precedent_memory/db.py`, `scripts/demo_reset.py`). Never bind `:8000`/`:8100`; never touch `data/precedent.db` or the default sim DB. Drive endpoints and the console URL use YOUR ports everywhere in the harness.
- **File ownership (hard boundary):** YOU own `Prep/video/**`, `precedent-video-drop/**` (gitignored), your pipeline code under `Prep/video/pipeline/`, and appended lines in `docs/evidence/` (music licence, submitted-version). You NEVER edit product code (`precedent/`, `precedent_memory/`, `agents/`, `console/`, `sim/`, `scripts/` outside your pipeline dir, `tests/`, `Makefile`) or `Prep/submissions/` — if a capture reveals a product bug, report it as a handoff note; do not fix it.
- **Sync points (poll, don't block):** structure the work so everything except V3's console takes proceeds regardless of 07. Poll `git log origin/main --oneline` between work items for a commit subject starting **`P1.7:`** — when it appears, `git pull --rebase`, re-verify the tree green, re-run the V3 capture harness against the upgraded console (byte-identical retakes are the design), and re-splice via the manifest. A subject starting **`P1.10:`** means `RESULTS.md` was regenerated — re-check the end-card EDIT-1 P99 value against the new committed file before final export. If neither marker has appeared by the human-declared capture deadline, ship captures from the current tree and state its sha.
- **Git discipline:** commit your plan-file/pipeline changes on a side branch; `git pull --rebase` onto latest `main` before merging (the 07 session merges lanes to `main` too). Ownership makes content conflicts impossible; the rebase handles ordering. Media never enters git either way.

---

## HARD RULES AS THEY BITE VIDEO (eligibility- and honesty-fatal; the evaluators enforce all of these mechanically)

- **No model id on screen or in VO** — roles only ("open-weight models (Venice-served), named in README"). The evaluator greps captions/VO/OCR against the four pinned ids in `precedent/models.py`.
- **No secrets, tokens, real teammate names, or internal URLs in any frame** — OCR sweep required (below).
- **Number honesty (from `Prep/final-numbers.md`, non-negotiable):** 8h51m is BUSINESS (MetricNet) and 18.2 h is CALENDAR (UCI) — never blended, never in the same caption; "25k-record store", never "P99 over 141k events"; 94% is fix-class EXISTENCE; the ~15 s standing-approval time is *this demo's on-screen stopwatch*, never a benchmark; every third-party number carries its source label on screen; no refuted claim ($400B, Komodor); TMDB/IMDb never named.
- **L3 is "Standing Approval", NEVER "Autonomous"** — grep-enforced on captions, VO text, and OCR.
- **Licensing:** music only from a verifiably-licensed source (CC0 / YouTube Audio Library), licence URL recorded in `docs/evidence/`; no broadcast-footage frame grabs (see V2); no AI-generated footage of real people or newsrooms.

---

## KNOWN DEFECTS TO FIX FIRST (found by an independent analysis pass — re-verify each against the files before acting)

1. **The VO script and shot list have FORKED.** `vo-script.md` differs from the `VO_shotN` cues in `shot-list.md` for shots 1, 2, 3, 5, 6, 7, 8. Worst: vo-script's shot 5 pulls the refusal + "it knows what it's not allowed to touch" INTO shot 5 while the shot list keeps the refusal picture in shot 6 — recorded as-is, the audio narrates a refusal the picture doesn't show yet. vo-script shot 5 also says "the Watcher agent" (a banned stage word per 04 §0) and shot 7 has two entirely different scripts (ingest/94%/adapters vs conformance-bench numbers).
2. **Zero assets exist.** No `.mp4/.mov/.wav` anywhere in the repo; `asset_skynews_headline.png` and `asset_manual_loop_timelapse.mp4` are referenced but don't exist; no `precedent-video-drop/` folder. The Sky News frame also has an unresolved rights question — replace it (V2), don't source it.
3. **Duration/notation traps:** shot 2's header range vs shot 0's +14 s shift; the 90s cut's "compressed to 25s→15s" ambiguity — resolve them in the plan files so an editor (or ffmpeg manifest) can't misread.
4. **No edit manifest** — the assembly, the two cuts, and the evaluator gates all need ONE per-shot in/out source of truth.

---

## WORK PLAN (dependency-ordered; every item names its verification)

**V1 — Reconcile the plan into ONE canonical script (blocks everything).** Merge `vo-script.md` into the shot-list's `VO_shotN` cues (the picture-paired text wins); refusal narration stays with shot 6's picture; remove "Watcher" from VO (use "the gateway agent" per the shot-list wording); choose shot 7's script deliberately (recommend: the shot-list ingest/94%/18h-calendar/adapter text, with vo-script's one-sentence bench line — "zero leaks across five thousand two hundred and nineteen deny-expected queries, six of six attacks, graded by an independent oracle" — merged in, since it fits the on-screen latency chart); keep "zero LLM calls on the fast path" only where the caption context supports it. Update all four `Prep/video/` files to the reconciled truth and fix the duration/notation traps (defect 3).
*Verify:* a committed cross-check script asserts VO text is byte-identical between vo-script.md and shot-list.md per shot; CAPTION-AUDITOR (below) passes on the reconciled captions; both memorable lines present in master + both cut plans; banned-word grep ("Watcher", "Autonomous") clean on VO/captions.

**V2 — Rights-safe "before" assets (replaces the two missing ones).** (a) Cold open / shot 1: replace the Sky News still with a **built text-card** ("July 2024. A global IT outage takes broadcasters off air. The fix was already documented." — HTML → Playwright screenshot, house style per `assets/brand/`) — kills the rights question. (b) The manual-loop time-lapse: **stage it programmatically** — Playwright drives a human-speed grind through the sim's browse/KB/ticket screens (mouse moves, scrolling, pauses), recorded, then time-lapsed 8× in ffmpeg with the clock overlay. No humans filmed, fully retakeable.
*Verify:* both assets exist in `precedent-video-drop/raw/`; ffprobe durations match the shot slots; TECH-QC OCR sweep on both (no real names/brands beyond the licensed source list).

**V3 — Capture harness + console/terminal takes.** Build the harness: Playwright (Chromium, 1920×1080) records the console while the harness issues the drive POSTs on a scripted timeline (seed-4207 → byte-identical retakes). Capture: shot 3 (console pan + provenance footer), shot 4 (incident 1: messy ticket → triage → plan+rollback card → Approve → verify → Jira close → Promote; use the REAL hold+Approve path if the 07 console upgrade is present), shot 6 (flake → rollback → demotion; then the incident-3 refusal card), shot 7 (terminal: `make bench-uci` / bench output + the latency chart + the one architecture slide from the deck PDF). Playwright's webm output transcodes to 30 fps H.264 via ffmpeg; if frame pacing disappoints, fall back to `ffmpeg -f avfoundation` screen capture with Playwright only driving.
*Verify:* every take in `raw/` named `shot{n}-{take}` per the convention; ffprobe ≥1080p; a take-manifest JSON records the drive timeline per take so any shot re-captures identically; the refusal frame shows count + owning team ONLY (leak probe on the OCR text).

**V4 — VO synthesis (or human kit).** From the reconciled script: if `ELEVENLABS_API_KEY` present → per-shot WAVs (`vo/vo-shot{n}.wav`), one calm stock voice, "read calm, let the stopwatch do the drama"; else → a `say`-based scratch track for timing plus a printable human recording kit (script with per-shot second budgets, mic notes). Either way, loudness-normalize stems.
*Verify:* per-shot WAV durations fit the shot slots (±1.5 s); no VO text drifts from the reconciled script (byte-diff the TTS input); the session states which branch it took.

**V5 — Edit manifest + assembly.** ONE `edit-manifest.json`: per-shot source file, in/out, caption text + display window, VO stem, music bed + ducking. Assemble with ffmpeg: shot-0 montage via `filter_complex` (three payoff frames cut from shots 4/5/6 takes), `concat`, VO-over-music with `sidechaincompress` ducking, `loudnorm` to −14 LUFS integrated / ≤ −1 dBTP. Captions: author `captions.srt` from the manifest's caption column, run the bracket guard on the SRT BEFORE burn-in, then burn (`subtitles=…`) — burned-in is correct for muted autoplay embeds. End cards (shot 8) as HTML → Playwright screenshots with EDIT 1 (P99 from committed `RESULTS.md`, phrased "over the 25k-record store") and EDIT 2 (repo URL) as template fills verified non-empty and non-bracketed; a missing value deletes its clause. Music from a CC0/YT-Audio-Library bed; licence URL written to `docs/evidence/`.
*Verify:* `precedent-full-v1.mp4` exists; every TECH-QC and CAPTION-AUDITOR gate (below) passes; shot 5's slot in the manifest is ≥78 s (a placeholder segment until V7 splices the human take).

**V6 — The 90-second cut + 30-second teaser, derived mechanically.** Both come from the SAME manifest (different shot subsets per `cut-plans-30s-90s.md`): 90s = shots 1→4(15s)→5-core(25s)→6-refusal→8, shot 7 dropped; 30s teaser = the three payoff frames + close. Both cuts preserve both memorable lines by construction (assert it).
*Verify:* durations ≤1:35 / ≤0:31; memorable-lines grep on each cut's SRT; the 90s cut opens the problem in ≤15 s.

**V7 — The human ASI:One take (prepared to one action).** Produce the shot-5 kit: the exact two incident messages to paste (from the demo script — the EPG-publish report, then the repeat-class report), the "approve" turn, a capture timer/checklist (cursor visible, no console anywhere on screen, Agentverse profile tabs pre-opened for the 3-agent cut-away, stopwatch visible for the ~15 s standing beat), and the splice instructions (manifest slot + in/out). When the human drops `raw/shot5-{take}.mov`, splice, re-run V5's assembly, re-run all gates.
*Verify:* after splice — master duration in window; shot-5 segment ≥78 s measured from the manifest; the approver-principal frame (chat sender address) is legible at 1080p.

**V8 — Ship kit.** Final gate run on all three exports; `exports/` named per convention (`precedent-full-v{n}.mp4` etc.); a one-page handoff: playtest instructions (rubric, pass bar ≥4/5 TRIAGED, 0 CONFUSED — a stranger, not a teammate), upload steps, where `[[WAIT:VIDEO-LINK]]` gets filled (BasedAI PR + DoraHacks), the selection-branch note (not selected → the 90s cut goes FIRST on the BUIDL page), and the submitted-version line for `docs/evidence/`.
*Verify:* the handoff names every human act with its file/URL; a dry `grep -n '\[\[WAIT' Prep/submissions/*` shows exactly the sentinels the human will fill.

---

## THE EVALUATOR-BUILDER SYSTEM (Workflow tool — builders never grade their own work; on disagreement the evaluator wins)

**Builders:** PLAN-BUILDER (V1–V2 plan edits + cards), CAPTURE-BUILDER (V3 harness + takes), AUDIO-BUILDER (V4), ASSEMBLY-BUILDER (V5–V6). Each iterates until its paired evaluator passes it — a bounded loop (max 3 rounds per artifact; if still failing, escalate to the orchestrator with the failing gate named).

**Evaluators (independent sub-agents, each re-runs its checks itself and pastes output):**
- **PLAN-CRITIC** (gates V1/V2 before any capture): judge-fit review against Conduct ("short and snappy… wow moment") and the Fetch weights — is anything before 0:55 skippable? (the analysis flagged shot 3 as the most skippable 15 s: recommend trimming to ~8 s and folding provenance into a caption over shot 4, giving the seconds to shot 5 breathing room — adopt unless it breaks a constraint); pacing of the 80 s chat segment (pre-typed pastes, never live typing at reading speed); confirms the reconciled script kills all four known defects. Anti-inflation: must quote the rubric line justifying each verdict.
- **CAPTION-AUDITOR** (gates every SRT/caption/end-card BEFORE burn-in, and the VO text): greps against `Prep/final-numbers.md` — bracket guard (`\[measured\]|\[repo\]|‹|<FILL` → empty); "Autonomous" → empty; the four pinned model ids → empty; "141k" never within a window of "P99"; "8h51m"/"8h 51m" never in the same caption as "18.2"/"18 hours"; source labels present (MetricNet, Splunk, ServiceNow KCS, UCI, CrowdStrike); both memorable lines verbatim in master + both cuts; "(vendor-claimed)" where required.
- **TECH-QC** (gates every export): ffprobe — master ∈ [4:15, 4:45], 90s ≤ 1:35, teaser ≤ 0:31, ≥1080p, ≥25 fps, AAC present; `loudnorm` analysis −16..−12 LUFS integrated, true peak ≤ −1 dBTP; shot-5 slot ≥78 s from the manifest; **OCR sweep** — 1 fps frame dump, OCR, grep for `@`, "Bearer", key-shaped strings, teammates' real names, "TMDB", "$400B", "Autonomous", model ids.
- **NAIVE-VIEWER** (gates the master + 90s cut): answers the three playtest-rubric questions from the captions+VO transcript alone, cold (a fresh sub-agent given ONLY the transcript, no project context); if its answers wouldn't grade TRIAGED (repeat = *pre-approval* not "it learned"; refusal = *permission* not failure), the failing beat's caption is rewritten and re-gated. This simulates — it does not replace — the human stranger playtest.

**Orchestrator rules:** V1 blocks all capture; CAPTION-AUDITOR blocks burn-in; TECH-QC blocks export naming; a gate run without pasted output did not happen.

---

## ACCEPTANCE CHECKLIST (run yourself; paste evidence)

- [ ] Ground verified: capture-tree sha stated, demo drives byte-identical twice, toolchain resolved, VO branch decided and stated
- [ ] V1 reconciliation committed: cross-check script proves vo-script ≡ shot-list VO per shot; defects 1–4 all closed
- [ ] V2 both "before" assets built rights-safe; Sky News frame gone from the plan
- [ ] V3 all console/terminal takes captured from the frozen build with take-manifests; refusal frame leak-probe clean
- [ ] V4 VO stems produced (or human kit delivered) matching the reconciled script byte-for-byte
- [ ] V5 master assembled from the single edit manifest; captions bracket-guarded BEFORE burn-in; music licence recorded in `docs/evidence/`
- [ ] V6 90s + 30s derived from the same manifest; memorable lines in all three
- [ ] V7 ASI:One kit delivered; splice path rehearsed with a placeholder
- [ ] All four evaluators PASS on the final exports (paste each gate's output)
- [ ] No media committed; plan-file edits committed; `[[WAIT:VIDEO-LINK]]` locations listed for the human
- [ ] V8 handoff written: playtest, upload, PR/BUIDL fills, selection-branch note

## DEFINITION OF DONE

Done when: the plan is reconciled to one canonical script with all four defects closed; every automatable asset (cards, time-lapse, console/terminal takes, VO stems, captions, end cards) exists in `precedent-video-drop/` built from the frozen seed-4207 tree; the master, 90-second, and 30-second exports assemble mechanically from one edit manifest and pass every PLAN-CRITIC / CAPTION-AUDITOR / TECH-QC / NAIVE-VIEWER gate with pasted evidence; the shot-5 human take is prepared to a single paste-and-record action with a rehearsed splice path; and the human holds a one-page ship kit for the playtest, the upload, and the `[[WAIT:VIDEO-LINK]]` fills — with no media in git, no bracket in any caption, both memorable lines in every cut, and every number wearing its label.

**Begin by loading the `precedent` skill, then reading the four `Prep/video/` files against `Idea/refinement/04-demo-and-video-script.md`.**

---

## CLOSING HUMAN WALKTHROUGH (only you can do these)

1. **Record shot 5** in ASI:One with the prepared kit (one clean take; the shared-chat URL is already captured — reference the exact turn in the README per the shot-list note).
2. *(If human-VO branch)* record the ~3 min narration from the kit; drop WAVs in `vo/`.
3. **Playtest with a stranger** (≥4/5 TRIAGED, 0 CONFUSED) — recut only the failing beat if it misses.
4. **Upload** (per the ship kit), fill `[[WAIT:VIDEO-LINK]]` in the BasedAI PR + DoraHacks worksheet, record the submitted version in `docs/evidence/`, and submit the BUIDL before 22:59 UTC.
5. **Selection-branch call (~22:00):** not selected → the 90-second cut goes first on the BUIDL page.
