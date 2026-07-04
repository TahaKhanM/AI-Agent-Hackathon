# Precedent — Complete Human Production Guide (video + audio, from scratch)

This is the definitive, do-it-yourself guide to shooting and cutting the Precedent submission video to a
**professional** standard. It assumes you want to redo the audio and video by hand (better than the
auto-assembled draft). Everything you need is here: the script, per-shot directions, the accounts and
logins, the demo setup, and how to use the assets already built for you.

> **You are making three files** (all 1920×1080, 30 fps, H.264/AAC):
> 1. **Master** — ~4:30 (hard window **4:15–4:45**; floor 3:30, ceiling 5:00). Serves BOTH DoraHacks/Conduct AND the Fetch 3–5 min deliverable.
> 2. **90-second cut** — ≤1:35. Goes FIRST on the BUIDL page if you're not selected to present.
> 3. **30-second teaser** — ≤0:31. Social / DoraHacks header loop, captioned, no VO.

> **A reference cut already exists** at `precedent-video-drop/exports/precedent-full-v2.mp4` (+ 90s/30s).
> It's watchable and every number is gate-checked, but the visuals lean on built cards and the VO is
> synthetic. Use it as a **storyboard and a fallback** — match its timing and captions, replace its
> shots with your better recordings.

---

## 0. The golden rules (break one and you can lose eligibility)

These are enforced by the honesty gates (`Prep/final-numbers.md`, `Idea/refinement/04 §0`). Non-negotiable:

1. **Every number is on `Prep/final-numbers.md` with its label.** If it isn't on that page, it doesn't go on screen. No exceptions, no rounding, no blending.
2. **NEVER blend 8h51m and 18.2h.** 8h51m = **business** MTTR (MetricNet, shots 0/2). 18.2h = **calendar** repeat-median (UCI, shot 7). They never share a caption or a breath.
3. **"25k-record store", never "P99 over 141k events."** 141k is a provenance count (captions only, shots 4A/7A); P99 (0.590 µs) is always "over the 25k-record store" and never in the same caption cue as 141k.
4. **L3 is "Standing Approval", NEVER "Autonomous."** Grep every caption and every VO line.
5. **No model id on screen or spoken.** Say "open-weight models (Venice-served), named in README." The four pinned ids live only in `precedent/models.py`.
6. **The two memorable lines survive every cut:** *"the second time is free"* and *"it knows what it's not allowed to touch."*
7. **No secrets, tokens, real teammate names, or internal URLs in any frame.** Roles, not names ("Disney+ operations alum"). The one name-shaped thing allowed on screen is the **public repo URL**.
8. **The 15-second run is "this demo's on-screen stopwatch,"** never a general benchmark. The 58-second run is "this demo's elapsed bar vs the 8h51m baseline," a same-demo comparison.
9. **Music must be CC0 / YouTube Audio Library** with the licence URL recorded in `docs/evidence/`. No broadcast footage, no AI-generated footage of real people/newsrooms.

The one-page number reference to keep open while you edit: **`Prep/final-numbers.md`.**

---

## 1. Accounts & logins you need

| # | Service | What it's for | How to get in | Gotchas |
|---|---|---|---|---|
| 1 | **The repo** | The demo you film + all scripts/assets | `git clone` the repo, `make install` (creates `.venv`, py3.13). | The video pipeline lives in `Prep/video/pipeline/`; media in the gitignored `precedent-video-drop/`. |
| 2 | **ASI:One** (Fetch) | **Shot 5** — the account-bound take | Log in at **asi1.ai** (the project account is `contact.mtaha@gmail.com`). Free; Pro via hackpack code **`UKAIAGENTUKAIAGENTAV`**. | The Precedent agent is **already live** — see §5.5. You reach it by `@`-mentioning its address. |
| 3 | **Agentverse** (Fetch) | The 3-agent cut-away + profile URLs | **agentverse.ai**, same Fetch login. Premium via the same code. | The 3 agents are registered + active (Almanac-confirmed): gateway `agent1q2m0gk9…jcgkldx`, retrieval `agent1qv760pr…kse9xv7`, execution `agent1qwesj8x…uxna02g`. |
| 4 | **Venice AI** | Powers the agents' open-weight models | **venice.ai/settings/api**, redeem **`IMPERIAL50X`** (or `IMPERIAL50`); Pro via `IMPERIAL`. Key goes in `.env` as `VENICE_API_KEY`. | Only needed if you re-run the live agents. The recorded console demo (shots 3/4/6) runs offline. |
| 5 | **Jira** (MediaCo project) | The real ticket that closes in shots 4/5 | The team's Atlassian login. The demo works **without** live Jira (local Jira-shaped source); only the "real ticket closes" beat needs it. | Never claim "live Jira" on the local path; say "local Jira-shaped source." Set `JIRA_*` in `.env` only for the live beat. |
| 6 | **ElevenLabs** | The voice-over (if not using a human) | Key is already in `.env` as `ELEVENLABS_API_KEY`. Or a human + a decent mic. | Recommended voice: **George** (British, calm) — id `JBFqnCBsd6RMkjVDRZzb`. |
| 7 | **Screen recorder** | Capturing the console + ASI:One | **OBS Studio** (free) or QuickTime. Set canvas to **1920×1080, 30 fps**. | Record a clean desktop — no other windows, no notifications, no dock. |
| 8 | **Video editor** | Assembly | **DaVinci Resolve** (free, recommended) / CapCut / Premiere. | Or drive the automated `assemble.py` and swap shots — see §6.2. |
| 9 | **Music** | The bed | **youtube.com/audiolibrary** (filter to "Attribution not required") or a CC0 source. | Record the track name + licence URL in `docs/evidence/`. |

---

## 2. Set up the demo environment (the console you'll film for shots 3/4/6)

```bash
cd <repo>
make install                       # .venv + deps (first time)
make demo-reset                    # seed the frozen seed-4207 state (< 30s)
make sim                           # boots the MediaCo sim (:8100) + the judge console (:8200-ish)
# open the console URL it prints; drive incidents over HTTP:
curl -XPOST http://127.0.0.1:8000/api/drive/1            # incident 1 (slow path → approval gate)
curl -XPOST http://127.0.0.1:8000/api/drive/2            # incident 2 (Standing Approval, ~15s, zero-LLM)
curl -XPOST http://127.0.0.1:8000/api/drive/3            # incident 3 (refusal — rights)
```

**The demo is fully drivable over HTTP**, so your console takes are scripted and infinitely retakeable
(seed 4207 → byte-identical). The gotchas the automated harness learned (they'll bite you too):

- **Reset the running server with `POST /api/demo/reset` (in-process), NOT `make demo-reset`.** The
  external reset rebuilds the DB file out from under the live server and every retrieval then fails
  closed. Use the console's **Reset demo** button (or `curl -XPOST …/api/demo/reset`) between takes.
- **The approval gate:** to film the *human Approve*, drive with `?hold=true` (pauses at the gate),
  then Approve (the console button, or `POST /api/drive/1/approve`). Pace it so the elapsed bar reads
  **~58s** at resolve — that includes a realistic ~40s of a human reading the plan+rollback (which the
  58-second number already accounts for). The raw take is then sped ~1.5× to the 40-second slot.
- **The recovery beat (shot 6):** promote the **publisher** class to Standing Approval, then drive
  `POST /api/drive/1/flake` — its fix is a *public* runbook so it reliably reaches execution, then
  verification fails → auto-rollback → class demoted. (The scheduler fix is restricted and can
  fail-closed right after a reset.) Then Triage INC-3 for the refusal (count + owner only).
- **Ladder hygiene:** `/api/demo/reset` does NOT reset promoted classes; **Revoke** a class before a
  take that needs the approval gate to show.
- **Airplane-mode:** the whole console demo passes with Wi-Fi off. Rehearse it once that way.

The console is dark-themed and matches the video's look. Film it at **125% browser zoom** for LT1/1080p
legibility; incident feed + baseline bar left, live trace + audit right.

---

## 3. The script — word for word (the single source of truth)

**The canonical narration is `Prep/video/pipeline/vo_canonical.json`.** It is kept word-identical to
`Prep/video/shot-list.md` (the picture-paired VO cues) and `Prep/video/vo-script.md` (the read script)
by `python Prep/video/pipeline/check_vo_sync.py` — run it after any edit; it must print `RESULT: PASS`.

Read the VO **calm and unhurried — let the stopwatch do the drama.** Per-shot second budgets and the
absolute cumulative timeline are the table in `shot-list.md` §Runtime. The captions (verbatim, with
their honesty labels) are in `shot-list.md` per shot. **Do not paraphrase numbers or labels.**

Quick map (durations are the reconciled slots; full text in the files above):

| Shot | Slot | On screen | Narration gist (verbatim in the files) | Caption gist |
|---|---|---|---|---|
| 0 | 0:14 | Montage: 58s bar → 15s stopwatch → refusal card | *none (music/beat)* | "8 h 51 m → 15 seconds. Approval never leaves the loop." |
| 1 | 0:15 | Built cold-open card → manual-loop time-lapse | CrowdStrike hook; the fix was already documented; Disney+ ops | "Downtime: ~$200M per Global 2000 company, per year (Oxford Economics / Splunk 2024)" |
| 2 | 0:30 | Time-lapse + Baseline Bar | the manual loop; 8h51m business benchmark; >60% repeats | "8h51m avg MTTR (MetricNet) · >60% repeat incidents (ServiceNow KCS study)" |
| 3 | 0:08 | Console home (quick) | MediaCo, real public data, real Jira | "MediaCo — simulated broadcaster · 25,412 precedents seeded" |
| 4 | 0:40 | Incident 1: messy ticket → Approve → verify → Promote | triage/retrieve/risk/rollback-before-asking; one click; standing approval | 4A provenance (141k/UCI/GitLab/CrowdStrike/TVmaze) · 4B "58 seconds vs 8h51m · requester ≠ approver" |
| **5** | **1:20** | **★ ASI:One conversation (see §5)** | no custom frontend; the loop in chat; approve = chat sender; **the second time is free** | "3 agents on Agentverse · Chat Protocol · discoverable via ASI:One · Approver = chat sender · no custom frontend" |
| 6 | 0:28 | Recovery (rollback+demote) then refusal | remembered fix fails → rollback → demote; restricted → refuse; **it knows what it's not allowed to touch** | "Auto-rollback → class demoted · restricted runbook → refusal, audited" |
| 7 | 0:31 | Scale artifact (terminal + latency chart + arch) | 25k store; 94% precedented; 18 calendar hours; 0 leaks / 6-of-6 / oracle; open-weight | 7A "141k / 24,918 ingested · 94% pre-matched" · 7B "P99 0.590 µs over the 25k store · graduation · 100% open-weight" |
| 8 | 0:30 | End card: team (roles), loop, links | AI SREs fix code; the fix is a documented change; $2.85B Moveworks | "repo · ASI:One shared chat · Agentverse · Precedent — the second time is free" |

---

## 4. Record the voice-over (audio)

Pick ONE path. Either way, the text must be **verbatim** from `vo_canonical.json` (numbers included).

**Path A — ElevenLabs (fastest, consistent).** The key is in `.env`. Generate all 8 stems in one go:
```bash
export ELEVENLABS_API_KEY="$(grep ELEVENLABS_API_KEY .env | cut -d= -f2- | tr -d '"')"
.venv/bin/python Prep/video/pipeline/make_vo.py           # → precedent-video-drop/vo/vo-shot{1..8}.wav
```
It uses **George** (British, calm), loudnorm'd, and prints each stem's duration vs its slot. To try a
different voice, pass a voice_id: `make_vo.py <voice_id>`. Regenerate freely — it's cheap.

**Path B — a human voice (most premium).** Quiet room, a cardioid mic ~20 cm with a pop filter, phone
mic only as a last resort. Read from `vo-script.md`, one shot at a time, calm and even. Aim to land each
shot inside its second budget (shorter than the slot is fine — the picture fills the rest). Leave 0.5s
of silence head/tail on each take. Save as `precedent-video-drop/vo/vo-shot{n}.wav`.

**Loudness (both paths):** normalize the final mix to **−14 LUFS integrated, true peak ≤ −1 dBTP** (the
gate range is −16…−12 LUFS). `assemble.py` does this automatically; in an editor, use its loudness
meter / a `loudnorm` pass.

---

## 5. Record each shot (video)

You can shoot **all shots except 5** yourself, or reuse the built assets in `precedent-video-drop/cards/`
and `…/raw/` and just re-record the ones you want sharper. Record everything at **1920×1080, 30 fps.**

**Shot 0 — montage.** Three payoff frames, hard beat-cuts, 14s, music only: the **58s-vs-8h51m elapsed
bar** (from your shot-4 take), the **15s stopwatch** (`cards/stopwatch.html` or your shot-5 timer), the
**refusal card** (from your shot-6 take). Cut it LAST, from the best frames of the other shots.

**Shots 1–2 — the "before."** Two rights-safe built assets (already made — reuse or rebuild):
- The **cold-open card** (`cards/coldopen.html` → screenshot): "July 2024. A global IT outage takes broadcasters off air. The fix was already documented." **No Sky News still** (rights) — the card replaces it.
- The **manual-loop time-lapse**: Playwright grinds the dated admin mockup (`cards/legacy_admin.html`) — read the messy ticket → hunt the KB (wrong articles) → clunky admin form → raise approval → wait — then ffmpeg speeds it ~8× with the SLA clock. Rebuild with `node Prep/video/pipeline/capture_timelapse.mjs`. **No humans filmed, no product screengrab.**

**Shots 3, 4, 6 — the console (record with OBS against `make sim`).**
- **Shot 3 (8s):** console home; a slow pan across the incident feed + the 25k precedents counter.
- **Shot 4 (40s):** Reset → drive incident 1 with `?hold=true` → the live trace fills (deterministic triage → risk L2 → approval_requested) → **read the plan** (~40s so the elapsed bar reaches ~58s) → click **Approve** → execute → verify → memory_stored → click **Promote to Standing Approval** (badge flips). Speed the raw ~1.5× to 40s.
- **Shot 6 (28s):** Reset → promote the publisher class → drive `…/api/drive/1/flake` → the trace shows executed → **rolled_back (pre-state restored)** → **class_demoted → L1**; then Triage **INC-3** → the refusal card (denied count + owner **Rights Ops** only, no body).
- The automated harness that does all this is `Prep/video/pipeline/capture_console.mjs` (`shot3|shot4|shot6`) — run it for a clean reference take, or shoot it live with OBS for a more organic feel.

**Shot 5 — ★ the ASI:One take (the one account-bound capture).** See §5.5 below; the agent is LIVE.

**Shot 7 — the scale artifact (31s).** Three panels: a **terminal** running the bench
(`make bench-uci`, or show the committed `precedent_memory/bench/RESULTS.md`), a **latency chart**
(P99 0.590 µs vs the 200 ms budget), and the **one architecture slide** (the four-tier adapter stack).
The built card `cards/shot7_scale.html` composes all three honestly from `final-numbers.md`; reuse it or
film a real terminal for extra authenticity. **Every number labelled; no model id.**

**Shot 8 — the end card (30s).** Team (roles: "Disney+ operations alum," never names), the loop
diagram, and the links held ~5s: **repo URL**, **ASI:One shared chat**, **Agentverse profiles**, and the
tagline **"Precedent — the second time is free."** Built at `cards/endcard.html` (repo + ASI:One filled
from committed sources). Confirm the repo URL is the intended **public** one before export.

### 5.5 — The ASI:One take, step by step (CONFIRMED WORKING)

The Precedent agent (`precedent-watcher`) is **registered and responding on ASI:One right now.** A clean
take is: report → plan → **approve** → resolved (real Jira + audit) → report the repeat → resolved under
**Standing Approval in ~15s** (zero-LLM). **The refusal is NOT here — it's shot 6.**

1. **Set up:** asi1.ai, maximised, **no console anywhere on screen**, notifications off, cursor visible.
   Pre-open the 3 Agentverse profile tabs (addresses + `tag:innovationlab` + `tag:hackathon` visible) for
   the end cut-away. Put a **stopwatch** on screen for the ~15s beat. Start OBS at 1920×1080/30fps.
2. **Reach the agent:** in a new chat, address the gateway agent — type `@` then its address
   **`agent1q2m0gk9wdvs0lyc3nfuyeet4y3nc68m9y24kehun2t70hadwf7qxjcgkldx`** and pick it so the **To:**
   chip reads **precedent-watcher** (or reuse the existing "EPG Guide" chat, already addressed to it).
   *(Tip: paste the address — typing 62 characters by hand drops characters.)*
3. **Turn 1 (paste):** `our EPG publish to the evening slot failed, error 4012 i think — can you fix it?`
   → agent replies with one message: triage → matched precedent **INC-1 (PUB-4012)** → **risk LOW/L2** →
   plan + rollback → "Reply approve/reject; expires in 10 min."
4. **Turn 2 (paste):** `approve` → agent: "**Approved by** <your chat-sender address> … Executed
   republish_epg … Outcome: **resolved** … **Audit:** <hash> … real Jira ticket closed." (Cut ~2s to the
   Jira ticket closing if you have live Jira.)
5. **Turn 3 (paste):** `same programme booked twice at the same time — can you sort it?` → agent:
   "**INC-2 … Standing Approval … applied in ~15s, no prompt (zero-LLM fast-path) … resolved.**" Watch
   the stopwatch hit ~15s — **this is "the second time is free."**
6. **Cut-away:** the 3 Agentverse profile tabs (addresses + both badges).
7. **Capture the artifacts THE SAME NIGHT:** copy the **public shared-chat URL** (Share → copy link),
   screenshot the 3 profiles. Paste the URL into the README/DoraHacks/Devpost drafts, pointing to the
   **incident-2 turn** ("jump to the ~15s standing-approval run").
8. Save the recording as `precedent-video-drop/raw/shot5-{take}.mov`.

*(A faithful, honest recreation of this exact real conversation — real audit hashes and the chat-sender
approver address — is already in the reference cut as `cards/asione_conversation.html`. Your live screen
recording replaces it for the final; drop the `.mov` and re-run `assemble.py all <ver>`, or drop it on
the editor timeline in shot 5's slot.)*

---

## 6. Assemble (edit)

### 6.1 By hand (DaVinci Resolve — most control)
- New 1920×1080 / 30 fps timeline. Lay shots 0–8 to the durations in `shot-list.md` §Runtime.
- **Captions:** burned-in lower-thirds (muted autoplay embeds need them). Use the **exact** caption text
  per shot from `shot-list.md` — do not retype numbers from memory. Split shot 7's caption into **two
  windows** (7A = 141k, 7B = P99) so the ingest count and the latency percentile never share a cue.
- **VO:** drop each `vo-shot{n}.wav` at its shot start; leave the picture longer than the VO where noted
  (shot 5's 80s runs long on purpose — pauses over the conversation).
- **Music:** a CC0/YT-Audio-Library bed at low level, **ducked** under the VO (side-chain compressor).
  Record its licence URL in `docs/evidence/`.
- **Loudness:** −14 LUFS integrated, true peak ≤ −1 dBTP. Export H.264 high, AAC 192k, faststart.
- **Cuts:** the 90s = shots 1→4(15s)→5-core(25s)→6-refusal→8 (drop 7); the 30s = the three payoff frames
  + close. Both **must keep both memorable lines** — the 90s via shot 5 & 6, the 30s via captions.

### 6.2 Or drive the automated pipeline and swap shots (fastest to a gate-passing cut)
The whole thing assembles from one manifest:
```bash
source precedent-video-drop/scratch/env.sh
.venv/bin/python Prep/video/pipeline/assemble.py all <version>
```
`precedent-video-drop/manifest/edit-manifest.json` is the single source of in/out points, captions, VO
stems, and music. To use YOUR recording for a shot, put the file in `…/raw/`, point that shot's `src`
at it, and re-run. Captions auto-burn (bracket-guarded first), VO + ducked bed auto-mix, loudnorm auto-runs.
This is the quickest route to a cut that passes every honesty gate; then polish in an editor if you want.

---

## 7. QA gates — run ALL of these before you upload

1. **Number honesty:** every on-screen/spoken number is on `Prep/final-numbers.md` with its label.
   `python Prep/video/pipeline/check_vo_sync.py` must print `RESULT: PASS` (VO sync + no "Watcher"/"autonomous" + both memorable lines + no model id).
2. **Bracket guard:** `grep -nE '\[measured\]|\[repo\]|<FILL|‹' <your caption source>` returns nothing.
3. **Model-id / secret sweep:** OCR a frame every 3s and grep for `@`, `Bearer`, key-shaped strings, the
   four model ids, "TMDB", "$400B/$600B", "Autonomous". Expect none. (`assemble.py` + the `export-gates`
   workflow do this; or spot-check by eye.)
4. **Loudness/format:** `ffprobe` each export — duration in window, ≥1080p, ≥25 fps, AAC present;
   loudness −16…−12 LUFS, TP ≤ −1 dBTP.
5. **The stranger playtest (Conduct's 20%):** show the **90-second cut** once to **5 strangers** (not
   teammates). Ask: (a) in one sentence, what does it do? (b) why was the second time faster? (c) why did
   it refuse the third? **Pass bar: ≥ 4/5 TRIAGED, 0 CONFUSED** (`Prep/video/playtest-rubric.md`). Any
   CONFUSED → find the frame they lost it on and recut that one caption.

---

## 8. Upload & submit

1. Upload the master **unlisted**; note the URL.
2. Fill `[[WAIT:VIDEO-LINK]]` everywhere — `grep -rn '\[\[WAIT:VIDEO-LINK\]\]' Prep/submissions/`
   (today: `BASEDAI-PR-README.md` ×2). Also the **DoraHacks BUIDL** video field and the **Devpost/Fetch**
   submission. BasedAI PR wants the **90-second** cut; DoraHacks/Fetch want the **master**.
3. **Selection branch (~22:00 Fri):** not selected → the **90-second cut goes FIRST** on the BUIDL page.
4. Record the shipped version: one line in `docs/evidence/` (file · URL · git sha).

---

## Appendix — what's already built for you (in `precedent-video-drop/`, gitignored)

| Asset | Path | Use |
|---|---|---|
| Cold-open card | `cards/asset_coldopen_card.png` | Shot 1 opener (rights-safe) |
| Manual-loop time-lapse | `raw/asset_manual_loop_timelapse.mp4` | Shots 1–2 "before" |
| Console takes | `raw/shot{3,4,6}-take*.mp4` | Reference console shots (frozen seed 4207) |
| ASI:One conversation card | `cards/asset_asione_conversation.png` | Shot 5 reference (real conversation content) |
| Scale artifact | `cards/asset_shot7_scale.png` | Shot 7 |
| Stopwatch / end card | `cards/asset_stopwatch.png`, `cards/asset_endcard.png` | Shot 0 middle frame / Shot 8 |
| VO stems | `vo/vo-shot{1..8}.wav` | ElevenLabs George narration |
| Captions | `captions/captions.srt` | Exact caption text + timings |
| Edit manifest | `manifest/edit-manifest.json` | Single source of the whole edit |
| Reference exports | `exports/precedent-{full,90s,30s}-v2.mp4` | Storyboard + fallback |

**Pipeline source (committed):** `Prep/video/pipeline/` — `capture*.mjs`, `render_caption.mjs`,
`make_vo.py`, `assemble.py`, `check_vo_sync.py`, `vo_canonical.json`, `cards/*.html`.
**Companion docs:** `Prep/video/asione-shot5-kit.md` (the ASI:One take), `Prep/video/SHIP-KIT.md` (the
one-page handoff), `Prep/video/{shot-list,vo-script,cut-plans-30s-90s,playtest-rubric}.md`.
