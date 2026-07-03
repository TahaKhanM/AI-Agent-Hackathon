# Rehearsal go/no-go gate (live vs recorded)

> Per `Idea/refinement/04-demo-and-video-script.md` §4.3 and `Plan/workflows/N1-rehearsal-runner.md`.
> This checklist — not the deck, not vibes — mechanically decides whether the demo goes **LIVE** or
> **RECORDED+one-click** on stage. Run at **Sat 09:00** on the frozen build (seed 4207).

## The gate rule (mechanical, not a judgement call)

Run the full slice **three times** airplane-mode (Wi-Fi off). Count clean passes.

- **3/3 clean** → **LIVE** (local-first).
- **2/3 clean** → **LIVE**, but the dirty-take insurance recording (captured Fri ~16:00) is cued as the
  fallback for that one flaky beat.
- **≤ 1/3 clean, i.e. two or more failures** → **RECORDED**: play the narrated recording of the frozen
  build with exactly **one live Approve click** for authenticity. **This is the two-failures rule:
  two failed gates flips the whole demo to the recording — no heroics on stage.**

Announce the decision in one line in the team thread, T1 ratifies:
> `GATES: n failed → LIVE / RECORDED+one-click`

## Per-run pass criteria (a "clean pass" = all of these)

- [ ] `make demo-reset` completes < 30s; baseline bar reads "8 hrs 51 min avg".
- [ ] Beat 1: incident 1 → one Approve → **resolved & verified** in ~60s; Jira ticket closes; **Promote
      to Standing Approval** succeeds.
- [ ] Beat 2: incident 2 → STANDING fast-path resolves ~15s, **provably zero LLM** (airplane-mode: the
      fast-path cannot have called Venice).
- [ ] Beat R: injected publisher-503 → verification fails red → rollback fires → state restored →
      class **demoted** to L1.
- [ ] Beat 3: incident 3 → **refused**, discloses only `denied_count` + "Rights Ops"; **no restricted
      body leak** anywhere on screen or in the audit tail.
- [ ] Total demo ≤ 2:42; both memorable lines land; no jargon a stranger can't parse.
- [ ] No secret, token, real name, or internal URL visible on screen.

## Reliability protocol (the safety net around the gate)

- Dirty-take insurance recording captured **Fri ~16:00** (before the freeze) — the ultimate fallback.
- Freeze demo code **Fri ~21:00**; record the demo video + the ASI:One shared-chat session that night
  against the frozen build.
- **Airplane-mode rehearsal must pass** at least once before the freeze (`Prep/airplane-mode-script.md`).
- Never demo ASI:One live on stage — it lives in the video regardless of the LIVE/RECORDED call.
- Kit: laptop + dongle, video file LOCAL (never streamed), clicker, phone with the judge-ticket form,
  printed one-pager of the A1 numbers.
