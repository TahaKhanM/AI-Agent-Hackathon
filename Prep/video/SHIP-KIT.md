# Precedent video — ship kit (one-page handoff)

Everything automatable is **built and gate-passed** from the frozen seed-4207 build. This page names
every remaining **human** act with its file/URL. Nothing here needs the machine — it's login-bound,
upload-bound, or a stranger's eyes.

> **To redo the whole thing to a professional standard by hand,** follow
> **[`HUMAN-PRODUCTION-GUIDE.md`](HUMAN-PRODUCTION-GUIDE.md)** — script, logins, demo setup, per-shot
> directions, assembly, QA, upload. This ship kit is the short handoff; that guide is the full manual.

## What's done (in `precedent-video-drop/`, gitignored — no media in git)

| Export | File | Duration | Status |
|---|---|---|---|
| Master | `exports/precedent-full-v2.mp4` | ~4:30 | assembled, gate-passed; **shot 5 = real ASI:One conversation** |
| 90-second cut | `exports/precedent-90s-v2.mp4` | ~1:31 | assembled, both memorable lines |
| 30-second teaser | `exports/precedent-30s-v2.mp4` | 0:30 | assembled, captioned |

All 1920×1080 / 30fps / AAC, −14.5…−14.8 LUFS (TP ≤ −1). VO is **ElevenLabs (George, British, calm)**.
Shot 5 renders the **real captured `precedent-watcher` conversation** (real audit hashes, chat-sender
approver, ~15s zero-LLM run) — the agent is **confirmed live on ASI:One**. One `edit-manifest.json`
drives all three.
Re-assemble any time: `source precedent-video-drop/scratch/env.sh && .venv/bin/python Prep/video/pipeline/assemble.py all <version>`.

## Human act 1 — the ASI:One take (the only capture a machine can't do)

Follow **[`asione-shot5-kit.md`](asione-shot5-kit.md)**: paste 3 messages, record one clean `.mov`,
grab the shared-chat URL + Agentverse screenshots the same night, drop the file, re-run `assemble.py all 2`,
re-run the gates. The master's shot-5 slot is an on-brand placeholder until then — the splice is a
source swap in the manifest.

## Human act 2 — the stranger playtest (Conduct's 20% "grasps it in 90s")

Show the **90-second cut** once to **5 strangers** (NOT teammates), no preamble beyond "this is an
incident-resolution agent for enterprise ops." Then `Prep/video/playtest-rubric.md`:
- **Pass bar: ≥ 4/5 TRIAGED, 0 CONFUSED** → ship. Any CONFUSED → find the frame they lost it on and
  recut that one caption (usually a jargon word), then re-derive from the manifest.
- Never coach the two memorable lines. If asked "is that number real?", give the labelled honest
  answer (8h51m = business benchmark; 94% = precedent *existence*; 15s = this demo's stopwatch).
- (A cold NAIVE-VIEWER agent pre-screened the transcript — see the `export-gates` result — but it
  *simulates*, it does not replace, the human stranger.)

## Human act 3 — upload + fill the video link

1. Upload the master **unlisted** (YouTube/Vimeo). Note the URL.
2. Fill `[[WAIT:VIDEO-LINK]]` everywhere the sentinel lives — run this to see the exact spots:
   ```bash
   grep -rn '\[\[WAIT:VIDEO-LINK\]\]' Prep/submissions/
   ```
   Today that is `Prep/submissions/BASEDAI-PR-README.md` (the BasedAI fork PR README, ×2) — plus the
   **DoraHacks BUIDL** video field and the **Devpost/Fetch** submission (external forms, not files).
   For the **BasedAI PR**, use the **90-second cut** link (that README asks for a 90s demo); for
   DoraHacks/Fetch, use the **master** (the 3–5 min deliverable).
3. Record the shipped version: append one line to `docs/evidence/` (e.g. `SUBMITTED-VERSION.md`):
   `Submitted video: precedent-full-v2.mp4 (master, shot-5 = live ASI:One take) · URL <…> · sha <git HEAD>`.

## Human act 4 — the selection-branch call (~22:00 Fri)

Per `Prep/selection-branch-staging.md`:
- **Not selected to present** → put the **90-second cut FIRST** on the DoraHacks BUIDL page, above the
  master. (The RESTRICT/refusal moment is already carried by shot 6 in the video — nothing extra to build.)
- **Selected** → the video is the submission + backup; present live per `04 §2`.

## Music licence (one line to record)

The assembled bed is a **self-generated low ambient drone** (no third-party audio → no licence needed).
If you swap in a CC0 / YouTube-Audio-Library track for polish, **record its licence URL** in
`docs/evidence/` (e.g. `MUSIC-LICENCE.md`) before upload — the honesty gate expects a licence line for
any third-party music.

## The two export-time EDITs (already filled from committed sources — verify, don't bracket)

- **EDIT 1 (shot-7 P99):** `0.590 µs over the 25k-record store` — from `Prep/final-numbers.md §4b`
  / `precedent_memory/bench/RESULTS.md`. **If a `P1.10:` commit regenerates RESULTS.md, re-check this
  value** before final export. If no P99 has landed, delete the clause — never bracket it.
- **EDIT 2 (shot-8 repo):** `github.com/TahaKhanM/AI-Agent-Hackathon` — confirm this is the intended
  **public** submission repo URL at export.

## Parallel-run note (Prompts/07 lane)

If a `P1.7:` commit upgrades the console, re-run the V3 console captures against it
(`Prep/video/pipeline/capture_console.mjs shot4|shot6`) — byte-identical retakes are the design — then
`assemble.py all`. Media never enters git; plan-file + pipeline-source edits are on the `video-pipeline`
branch (rebase onto latest `main` before merging).
