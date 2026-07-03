# Precedent — 30-second teaser + 90-second cut + assembly conventions

> Derived from the master shot list (`Prep/video/shot-list.md`) and the locked cut-lines in
> `Idea/refinement/04-demo-and-video-script.md` §4.3. **Both cuts MUST preserve the two memorable
> lines:** *"the second time is free"* and *"it knows what it's not allowed to touch."* Never cut the
> ASI:One segment (shot 5) or the cold-open payoff (shot 0). Number-honesty guardrails carry over
> verbatim from the shot list.

## 30-second teaser (social / DoraHacks header loop)

Purpose: stop-the-scroll proof, no narration required (captioned). Pull three frames from the master
so it stays byte-identical to the full cut.

| t | Source frame | On screen (caption) |
|---|---|---|
| 0:00–0:08 | shot 0 / shot 4 payoff | "8h 51m to fix one incident, by hand." → the 58s elapsed bar lands |
| 0:08–0:18 | shot 5 (ASI:One 15s stopwatch) | "The second time is free." — 15s stopwatch, zero LLM calls |
| 0:18–0:26 | shot 6 refusal card | "It knows what it's not allowed to touch." — refusal card (count + owner only) |
| 0:26–0:30 | shot 8 close | wordmark + "Precedent — retrieve your org's own documented fix. Repo · deck · ASI:One." |

Rules: 8h51m is labelled **business**; the 15s is *this demo's on-screen stopwatch* (engineered/paced,
never a latency benchmark); the refusal card shows only `denied_count` + owning team — no body.

## 90-second cut (the "not selected to present" version — goes FIRST on the BUIDL page)

Locked cut-line sequence (mirrors the deck's 90-second short version 2→5→6→7→12):

| t | Shot(s) | Beat | VO source |
|---|---|---|---|
| 0:00–0:15 | shot 1 (+ shot 2 open) | Cold open: the manual loop + 8h51m | vo-script shots 1–2 (trimmed) |
| 0:15–0:30 | shot 4 (compressed to 25s→15s) | Incident 1: messy ticket → one Approve → ~60s → Promote to Standing Approval | vo-script shot 4 (first half) |
| 0:30–0:55 | **shot 5 (ASI:One, 25s core)** | The repeat runs in ~15s inside ASI:One, zero LLM; **"the second time is free"** | vo-script shot 5 (para 1) |
| 0:55–1:10 | shot 6 refusal | The refusal: **"it knows what it's not allowed to touch"** | vo-script shot 6 (refusal half) |
| 1:10–1:30 | shot 8 close | Ask + Moveworks $2.85B close | vo-script shot 8 |

Compression rules: shrink shot 4 → 25→15s and shot 7 is **dropped entirely** in this cut; **never**
shorten shot 5's core beat or drop either memorable line. If it still runs long, cut only descriptive
clauses, never a number's source label.

## Shared-folder naming convention (the `precedent-video-drop` folder)

```
precedent-video-drop/
  raw/            shot{0..8}-{take}.mov      # T2's screen captures, frozen build, seed 4207
  vo/             vo-shot{0..8}.wav          # N1's narration takes
  music/          bed-{name}.wav
  captions/       captions.srt               # numbers checked vs Prep/final-numbers.md
  exports/        precedent-full-v{n}.mp4    # ~4:15–4:30 master
                  precedent-90s-v{n}.mp4     # the 90-second cut (first on the BUIDL page)
                  precedent-30s-v{n}.mp4     # the teaser loop
```

Convention: `{shot}-{take}` ascending; the **highest take number is canonical**; never overwrite a
take. Every export filename carries a version `v{n}`; the committed/submitted one is recorded in
`docs/evidence/`. All clips are captured against the FROZEN build (seed 4207) so the demo replays
byte-identically; the video is stored LOCAL on disk, never streamed on stage.
