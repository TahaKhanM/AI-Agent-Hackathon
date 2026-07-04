# Precedent — 30-second teaser + 90-second cut + assembly conventions

> Derived from the master shot list (`Prep/video/shot-list.md`) and the locked cut-lines in
> `Idea/refinement/04-demo-and-video-script.md` §4.3. **Both cuts MUST preserve the two memorable
> lines:** *"the second time is free"* and *"it knows what it's not allowed to touch."* Never cut the
> ASI:One segment (shot 5) or the cold-open payoff (shot 0). Number-honesty guardrails carry over
> verbatim from the shot list. **All three exports derive from ONE `edit-manifest.json` (V5)** — the
> cuts are shot-subset selections over the same source takes, so a frame in the teaser is byte-for-byte
> the same frame as in the master.

## 30-second teaser (social / DoraHacks header loop)

Purpose: stop-the-scroll proof, no narration required (captioned). Pull three frames from the master
so it stays byte-identical to the full cut. **≤ 0:31.**

| t | Source frame | On screen (caption) |
|---|---|---|
| 0:00–0:08 | shot 0 / shot 4 payoff | "8h 51m to fix one incident, by hand." → the 58s elapsed bar lands |
| 0:08–0:18 | shot 5 (ASI:One 15s stopwatch) | "The second time is free." — 15s stopwatch, zero LLM calls |
| 0:18–0:26 | shot 6 refusal card | "It knows what it's not allowed to touch." — refusal card (count + owner only) |
| 0:26–0:30 | shot 8 close | wordmark + "Precedent — retrieve your org's own documented fix. Repo · deck · ASI:One." |

Rules: 8h51m is labelled **business**; the 15s is *this demo's on-screen stopwatch* (engineered/paced,
never a latency benchmark); the refusal card shows only `denied_count` + owning team — no body.
**Both memorable lines are present by construction** (rows 2 and 3) — the teaser SRT is bracket-guarded
and memorable-line-checked before burn-in like every other caption source.

## 90-second cut (the "not selected to present" version — goes FIRST on the BUIDL page)

Locked cut-line sequence (mirrors the deck's 90-second short version 2→5→6→7→12). **≤ 1:35; opens the
problem within the first 0:15.**

| t | Shot(s) | Beat | VO source (canonical, `vo_canonical.json`) |
|---|---|---|---|
| 0:00–0:15 | shot 1 (+ shot 2 open) | Cold open: the manual loop + 8h51m business benchmark | shot 1, then shot 2 (first sentence only) |
| 0:15–0:30 | shot 4, **compressed to 15 s** | Incident 1: messy ticket → one Approve → ~60s → Promote to Standing Approval | shot 4 (first half, to "…evidence attached") |
| 0:30–0:55 | **shot 5 (ASI:One, 25s core)** | The repeat runs in ~15s inside ASI:One, zero LLM; **"the second time is free"** | shot 5 (the loop + second-occurrence sentence, incl. the memorable line) |
| 0:55–1:10 | shot 6 refusal half | The refusal: **"it knows what it's not allowed to touch"** | shot 6 (the refusal sentence + the memorable line) |
| 1:10–1:30 | shot 8 close | Ask + Moveworks $2.85B close | shot 8 |

Compression rules (**unambiguous**): in this cut, **shot 4 is 15 s** (the master's shot 4 is 40 s; the
"compress to 25 s" figure in the shot list is the *master's own* squeeze floor, not this cut) and
**shot 7 is dropped entirely**. **Never** shorten shot 5's core beat or drop either memorable line. If
it still runs long, cut only descriptive clauses, never a number's source label. The shot-5 25 s core
must still contain "the second time is free"; the shot-6 half must still contain "it knows what it's
not allowed to touch" — both asserted mechanically against each cut's SRT (V6).

## Shared-folder naming convention (the `precedent-video-drop` folder, gitignored)

```
precedent-video-drop/
  raw/            shot{0..8}-{take}.mp4      # T2's screen captures (Playwright webm → H.264), seed 4207
                  shot5-{take}.mov           # the ONE human take (ASI:One), account-bound (V7)
  cards/          asset_*.png                # built HTML→screenshot cards (cold open, end cards, arch)
  vo/             vo-shot{0..8}.wav          # narration (say-scratch now; human/ElevenLabs later)
  music/          bed-{name}.wav
  captions/       captions.srt               # numbers checked vs Prep/final-numbers.md; bracket-guarded
  manifest/       edit-manifest.json         # THE single per-shot in/out/caption/vo/music source of truth
  exports/        precedent-full-v{n}.mp4    # ≈4:36 master
                  precedent-90s-v{n}.mp4     # the 90-second cut (first on the BUIDL page)
                  precedent-30s-v{n}.mp4     # the teaser loop
```

Convention: `{shot}-{take}` ascending; the **highest take number is canonical**; never overwrite a
take. Every export filename carries a version `v{n}`; the committed/submitted one is recorded in
`docs/evidence/`. All clips are captured against the FROZEN build (seed 4207) so the demo replays
byte-identically; the video is stored LOCAL on disk, never streamed on stage. **No media is ever
committed** (`precedent-video-drop/` is gitignored); only the plan files here and the pipeline SOURCE
in `Prep/video/pipeline/` are committed.
