# PACKET — Rehearsal Runner (timing, judge-question drill, Saturday §4.3 gates)

> **Owner:** N1 · **Phase:** runs during **harden+ambition** (a first prep pass once the pitch script is stable) and then the **Saturday assemble/submit** rehearsal block, ending at the §4.3 gates before everyone departs for Blackett LT1.
> **Work from:** `Prep/qa-bank.md` (the team's Q&A bank — the question lines + their bold one-sentence openers) and the current pitch script in the Plan. You have repo access; read these directly, no one hands them to you.
> **Your output:** filled scoring sheets + the gate checklist. Commit them into `docs/evidence/` on your own branch (or drop photos of paper sheets into `docs/evidence/` and the team thread), then merge/PR per the team's convention. No relay through T3.
> **You need:** a stopwatch (phone lap function), scoring sheets (paper or a Notes doc), your AI tool pointed at `Prep/qa-bank.md`.
> **Coordinate:** N2 also owns video/QA — if N2 runs any of the earlier run-throughs, hand them a copy of the §3 scoring sheet + the §2 facts page so they score against the same rubric and post results to the same thread.

---

## 1. Why this exists

The pitch is 3 min + 2 min Q&A, VC judges (LocalGlobe, Antler, EWOR) + sponsor judges. The script is written to **2:42 at ~150 wpm; the rehearsal target is 2:40, hard ceiling 2:45**. Whether Saturday's demo runs live or as a narrated recording is decided **mechanically** by the §4.3 gate checklist you run in the Saturday block — not by mood, not by debate (the rule is pre-ratified). You are the timekeeper, the drill sergeant, and the gate clerk. You never negotiate the rules; you record against them.

## 2. Fixed facts you score against (memorise the numbers, keep this page open)

**Beat map (cumulative clock):** Beat 0 hook ends **0:25** · Beat 1 (messy ticket → Approve → Promote) ends **1:20** · Beat 2 (15-second repeat) ends **1:50** · Beat R (rollback + demotion) ends **2:10** · Beat 3 (refusal) ends **2:28** · Close + ask ends **~2:42**.

**The two takeaway lines that must land:** *"the second time is free"* and *"it knows what it's not allowed to touch."* Test: after each run, someone who ISN'T presenting (you) writes from memory the two phrases the pitch wants remembered. If you can't, they didn't land — that's a fail regardless of timing.

**Also required out loud:** "approval moved earlier in time — it never left the loop" · "unscripted" · the ask ("two introductions from this room — to anyone running a 24/7 ops or NOC team…").

**Banned words (any one spoken = note it):** "autonomous"/"autonomously" (about L3 — the correct term is **Standing Approval**), Watcher/Librarian/Assessor/Operator/Auditor (saying "five specialised agents" once is allowed), YAML, ACL, lineage, SoD, embeddings, "deterministic policy engine", P99.

**Contingency lines (must be delivered verbatim in the drills):**
- Jira-degraded (§4.1): *"We've dropped to our cached mirror — everything still executes locally and re-syncs to Jira the moment the venue Wi-Fi does. The live sync is in our submission video."*
- Backup-video switch (§4.2): *"Demo gods. Here's the identical run, recorded last night against this exact build — I'll narrate it live."* (Switch must take **<5 seconds**.)

**Choreography to watch (Presenter 2):** hotkey `G` fires each incident · hero click 1 = APPROVE · hero click 2 = PROMOTE TO STANDING APPROVAL · Revoke is HOVERED at 1:43, never clicked · Window-B (Jira) hops only when the console's sync-tick is green — if not green, the cut is skipped silently.

> **Honesty rules (non-negotiable, same as every packet):** never say or show a placeholder like ‹XX› out loud or on screen. Caption/say the data as a **"25k-record store"** — never overstate scale. **TMDB was rejected** as a data source; don't reference it. If a claim in a required line isn't true of the current build, cut the line rather than assert it. No secrets, tokens, or internal URLs on screen.

## 3. Scoring sheet (one per run — make ~8 blanks before the first block)

```
RUN #__  ·  Date/time: ____  ·  Mode: live / airplane / video-switch drill
Total time: __:__   (target 2:40, hard ≤2:45)      Beat splits: 0:25 / 1:20 / 1:50 / 2:10 / 2:28 → actual: __/__/__/__/__
Takeaway line 1 recalled by listener?  Y / N        Takeaway line 2 recalled?  Y / N
Banned words spoken (list): ______________          Required lines all said?  Y / N (missing: ____)
Ask delivered word-for-word?  Y / N                 Choreography errors (G / clicks / window hops / sync-tick): ____
Stumbles >2s: __      Dead air during 15s stopwatch?  Y / N  (should be narrated, never silent)
Q&A DRILL — 6 questions fired, 20s each:
  Q1 opener landed? Y/N · Q2 Y/N · Q3 Y/N · Q4 Y/N · Q5 Y/N · Q6 Y/N
  One-owner-per-question discipline held (numbers/tech/market — never two people answering)?  Y / N
VERDICT: CLEAN / NOT CLEAN (any timing fail, missed takeaway, banned word, or choreography error = NOT CLEAN)
```

## 4. The judge-question drill (after every timed run, ~4 min)

The judge-question generator runs **in your own AI tool** against `Prep/qa-bank.md`. Point the tool at that file and drive it with something like the prompt below (keep it in one session per rehearsal block so it remembers what it already asked, and paste back the running list of used questions):

```
You are a panel of hostile hackathon judges (a VC, a sponsor-track judge, and a sceptical
engineer). Read Prep/qa-bank.md: our known questions and the one-sentence openers we rehearsed.
Generate 10 FRESH questions for rehearsal round ‹N›:
- 6 must be re-phrasings or sharper versions of bank questions (different words, same trap);
- 3 must be curveballs NOT in the bank but fair game for this pitch (an agent that re-applies an
  org's documented fixes with approval gates, audit, auto-rollback, permission-aware memory,
  demoed on a simulated broadcaster with real public data and live Jira);
- 1 must be an aggressive interruption-style question a VC would fire mid-answer.
Do NOT repeat any question already used: [paste previous rounds' questions, or "none"].
Output: a numbered list of the 10 questions only — no answers, no commentary.
```

Make the tool **verify** it actually pulled from `Prep/qa-bank.md` (the 6 re-phrasings should trace to real bank entries) and that it's not repeating earlier rounds. Save each generated list into the thread / evidence so rounds don't collide.

Drill mechanics: fire 6 of the 10 (your pick, favour the curveballs), 20 seconds per answer, hard cut. Score each: did the answer start from (or clearly land) the bank's bold opener? Did exactly ONE person answer (numbers/tech/market ownership)? Log misses on the sheet. Any question that stumped the room goes on the **stump list** for the Q&A owners to prep before the next block.

## 5. Prep pass (during harden+ambition, once the script is stable)

1. Read `Prep/qa-bank.md`; run the drill prompt once as a smoke test (round "0") to confirm your tool pulls from it cleanly.
2. Make ~8 blank scoring sheets; test your stopwatch lap function against the beat map.
3. If N2 (or anyone) is running earlier run-throughs, hand them a sheet + the §2 facts page and agree they post filled sheets to the thread.
4. Post in the thread: "Saturday rehearsal block needs presenters + demo machine + phone (party-trick tickets). Gates run at the end of the block — arrive with the build frozen."

## 6. Saturday rehearsal block (you own the clock)

Run the block in this order; it's dependency-ordered, not clock-pinned:

| Step | What |
|---|---|
| Setup | Demo machine reset (`make demo-reset` — **time it**, that's gate 6 data), sheets out, AI tool session open on `Prep/qa-bank.md` |
| Timed runs + drill | Full runs, drill after each. Aim for 4–6. Order: 2 normal · 1 **airplane mode** (Wi-Fi + hotspot OFF; §4.1 line delivered once, exactly) · 1 **video-switch drill** (at beat 2, presenter kills the console feed on your signal; P2 must be narrating the backup video within 5s, §4.2 line verbatim) · then normal runs **until 3 CONSECUTIVE cleans exist** |
| Party trick | The two tickets chosen at playtest, filed from the phone, both outcomes shown on the big screen |
| **Gates** | Run the **§4.3 gate checklist (§7 below)** — fill, save/photograph, announce |
| Depart | Hard stop for Blackett LT1 (doors 10:00). Gates outrank extra runs — when it's time to gate, you stop rehearsing and gate, whatever the run count. |

## 7. The §4.3 gate checklist (run at the end of the block — this decides live vs recorded)

- [ ] **Gate 0 (prerequisite, verify with the team):** a full two-presenter run-through happened before this morning (during harden)
- [ ] **Gate 1:** 3 consecutive clean full runs at ≤2:45, timed (from this block's sheets)
- [ ] **Gate 2:** 1 full run in airplane mode passed (degraded-banner path; §4.1 line delivered)
- [ ] **Gate 3:** 1 full run switching to backup video at beat 2; switch <5s (§4.2 drill)
- [ ] **Gate 4:** party trick — 2 messy phone tickets, one triaged correctly, one degraded safely, both on the projector
- [ ] **Gate 5:** `make demo-reset` restores counters/ladder state in <30s

**THE MECHANICAL RULE (pre-ratified — you announce, T1 confirms, nobody debates):**
- **0–1 gates failed → GO LIVE** (live-local-first, drilled video fallback armed).
- **2+ gates failed → FLIP: narrated recording + ONE live element (the Approve click against the cached-mode console).** This is the VC judge's preferred configuration anyway — announce it as a landing zone, not a defeat.

## 8. §5 ambition hooks that touch this brief

If T2's ambition beats have landed by the Saturday block, add one line each to the run so the drill actually exercises them (and the demo shows them off):
- **Live RESTRICT hotkey:** work the hotkey into one run — a judge names an entity, presenter hits RESTRICT live, the refusal (Beat 3) then visibly honours it. Score it under choreography.
- **Attract-mode idle loop:** if the console idles into attract-mode, confirm it's running on the big screen during setup/party-trick, and that a keypress cleanly exits it into the live demo (no reload).
- **Temporal-embargo media beat / change-record artifact:** if these are demoable, add one drill question to the bank prompt targeting each, so the Q&A owners can land the opener under fire.
None of these are gates — they're only in the run if T2 shipped them. Don't rehearse a beat that isn't in the build.

## 9. DONE when

- [ ] Prep pass complete: smoke-test round "0" ran, sheets made, earlier-run-through scorer briefed (if any)
- [ ] All scoring sheets + the gate checklist saved into `docs/evidence/` (committed on your branch, or photographed into the thread)
- [ ] One-line announcement posted and said out loud: "GATES: ‹n› failed → **LIVE** / **RECORDED+one-click**" — T1 ratifies in the thread
- [ ] Stump-questions list handed to the Q&A owners

## 10. If it goes wrong

- **Presenters resist the flip:** read the rule aloud; it was pre-ratified. Your job ends at recording + announcing; T1 owns enforcement.
- **Runs keep failing on time:** the script's own cut is pre-authorised — drop "for what is usually minutes of keystrokes once the fix is known" from the hook. Any bigger cut is the presenters' call, not yours; you just keep timing.
- **AI tool wanders / repeats questions:** reuse round-0 and earlier-round lists (that's why every list is saved); the drill degrades to repetition, never to skipped. Re-point it at `Prep/qa-bank.md` and paste the used-question list back in.
- **Clock pressure:** gates outrank extra runs. When it's time to gate, you stop rehearsing and start gating, whatever the run count.
