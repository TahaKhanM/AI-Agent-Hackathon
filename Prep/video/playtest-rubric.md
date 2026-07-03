# Naive-user playtest rubric (TRIAGED / DEGRADED / CONFUSED)

> Per `Plan/workflows/N1N2-demo-playtest.md`. Purpose: verify a person who has **never seen Precedent**
> grasps the before/after and the trust story from the video (or the live demo) alone — Conduct's 20%
> "a non-engineer grasps it in 90 seconds". Run against a stranger, not a teammate. No jargon coaching.

## Setup

- Show the 90-second cut (or the live slice) once, no preamble beyond "this is an incident-resolution
  agent for enterprise ops."
- Do NOT explain anything. Hand them the three tasks below. Time the first-grasp.

## The three tasks the naive user attempts

1. **Explain it back.** "In one sentence, what does it do?" (Looking for: retrieves the org's *own
   documented fix* and re-applies it, gated + audited + reversible — NOT "an AI that fixes bugs".)
2. **The repeat.** "Why was the second time faster than the first?" (Looking for: it was pre-approved
   after succeeding once — *"the second time is free"* — not "the AI learned/got smarter".)
3. **The refusal.** "Why did it refuse the third one?" (Looking for: it isn't *allowed* to read that
   restricted runbook, so it refused and routed it — *"it knows what it's not allowed to touch"* — not
   "it couldn't figure it out" / "it failed".)

## Grading (one grade per playtester)

| Grade | Bar |
|---|---|
| **TRIAGED** ✅ | Repeats BOTH memorable lines (or their meaning) unprompted; correctly explains the repeat as *pre-approval* and the refusal as *permission*, not capability. The before/after (8h51m → ~15s) landed. |
| **DEGRADED** ⚠️ | Gets the gist (faster the second time; refused the third) but misattributes WHY — e.g. "it learned" instead of "it was pre-approved", or "it couldn't do it" instead of "it wasn't allowed". Salvageable with one caption/word change. |
| **CONFUSED** ❌ | Cannot explain it back; thinks it's a generic AI-fixes-code tool; missed the refusal or read it as a failure. A structural miss — recut. |

## Pass bar

- **≥ 4 of 5 playtesters TRIAGED, 0 CONFUSED** → the cut ships.
- Any **CONFUSED** → find the exact frame where they lost it and recut that beat (usually a jargon word
  in a caption, or the refusal reading as a bug). The most common fix is replacing a technical caption
  word with the plain-language line the crib sheets already use.
- **DEGRADED clustered on one task** → that beat's caption is doing the wrong job; rewrite only that
  caption (never blend a number to "simplify").

## Honesty during the playtest

Never coach the memorable lines or feed the answer. If a playtester asks "is that a real number?", the
honest answer is the labelled one (8h51m business benchmark; 94% precedent *existence*; the 15s is this
demo's on-screen stopwatch) — never round up or blend to make the demo land harder.
