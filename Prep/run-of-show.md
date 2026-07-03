# Precedent — demo run-of-show (live + recorded)

> The second-by-second is `Idea/refinement/04-demo-and-video-script.md`; §4.3's rehearsal gates (not
> this file, not the deck) decide **live-first vs recorded-first**. Seed **4207** — incidents 1/2/3
> replay byte-identically, observation time frozen. Target **2:42**, rehearse to **2:40**. Numbers per
> `Prep/final-numbers.md`. L3 is **Standing Approval**, never "Autonomous".

## Pre-flight (both variants)

```bash
make demo-reset          # sim db + memory db reset, repeat class pre-seeded STANDING (~0.4s)
make sim                 # MediaCo sim :8100 + judge console :8000 (T1 in-process, shared file DB)
# baseline bar reads: "Manual: ticket → find runbook → admin console → approval queue → resolve = 8 hrs 51 min avg"
```
Video file LOCAL on disk; clicker ready; phone with the judge-ticket Jira form open (Q&A party trick).

## Beats (the persistent Baseline Bar draws each incident's real elapsed bar beneath the 8h51m manual baseline)

| Beat | ~t | What happens | Command / action | Payoff |
|---|---|---|---|---|
| **1 — Incident 1** | 0:00–0:60 | Messy EPG-publish ticket (wrong error code on purpose) → triage → retrieve documented fix → plan + rollback → **one human Approve click** → fixed ~58s, Jira ticket closes itself → **Promote to Standing Approval** | `curl -XPOST /api/drive/1?hold=true` then Approve (or the live console button) | "~58s vs 8h51m" |
| **2 — Incident 2 (the wow)** | 0:60–1:15 | Same fingerprint, nobody at the keyboard → fingerprint fast-path resolves in **~15s** on the on-screen stopwatch, **zero LLM calls** | `curl -XPOST /api/drive/2` | **"The second time is free."** |
| **R — Recovery** | 1:15–1:35 | Publisher-503 injected mid-write → verification FAILS red → pre-written rollback fires → state restored → class **demoted** Standing Approval → L1 → escalated | `curl -XPOST /api/drive/2/flake` | control includes recovering from failure |
| **3 — Refusal** | 1:35–2:05 | Rights-window conflict; a documented fix exists but Jira's "Rights Ops Only" issue-security hides the runbook from the scheduling-ops identity → Precedent **refuses**, discloses only `denied_count` + owning team, routes a dossier | `curl -XPOST /api/drive/3` | **"It knows what it's not allowed to touch."** |

Close strip: "Tonight: 3 incidents · manual ≈26 h · Precedent 1 m 28 s." The ~15s is **engineered/paced**
(real work ~6–8s) — never presented as raw latency.

## LIVE variant (local-first)

Drive the beats from the console buttons / `scripts/drive_incident.py`; the trace panel lights each
loop hop. One live **Approve** click on beat 1; everything else runs from the seeded state. If Wi-Fi is
hostile, the degraded-mode amber banner ("Jira degraded — running on cached mirror, will re-sync") is a
**feature on screen**, not an apology.

## RECORDED variant (narrated recording + one live Approve)

Play the frozen screen recording (captured against the freeze, seed 4207) and narrate live; do the
single Approve click live for authenticity. Never demo ASI:One live — it lives in the video (shot 5).
The switch between variants is made by the rehearsal gate below, mechanically — not on stage.

## Q&A jumps (slides 8/9/10 are Q&A-only)

competition → slide 9; moat/cold-start → slide 10; "how does it work" → slide 8 then appendix A3/A4.
Q&A ownership: one owns numbers (A1), one owns tech (A3/A4/A6), one owns market (A5/A8) — never two
people answering one question.
