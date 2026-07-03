# PACKET — Rehearsal Runner (timing, judge-question drill, Sat 09:00 §4.3 gates)

> **Owner:** N1 · **Runs:** Fri 17:00–18:00 (prep, inside shift) + **Sat 06:45–09:30** (rehearsals 06:45–09:00, §4.3 gates 09:00–09:30, then everyone departs for Blackett LT1)
> **Budget:** ~2.0 ph (the ledger's "Rehearsal + gates" row)
> **Sent to you by:** T3 via WhatsApp with ONE attachment: `QA-bank-extract.md` (T3 prepares it Friday by 17:00: the question lines + their bold one-sentence openers from the team's Q&A bank — nothing else, ~2 pages)
> **Your output goes to:** the team thread (photos of filled sheets) + T3, who files them in `docs/evidence/`
> **You need:** phone stopwatch, paper or Notes app for scoring sheets, claude.ai (free tier), the attachment
> **Also:** hand the §3 scoring sheet to **N2 on Friday by 18:00** — N2 scores the Fri 18:30 and 20:00 run-throughs with the same sheet (you're off shift at 18:00); results go in the same thread.

---

## 1. Why this exists

The pitch is 3 min + 2 min Q&A, VC judges (LocalGlobe, Antler, EWOR) + sponsor judges. The script is written to **2:42 at ~150 wpm; the rehearsal target is 2:40, hard ceiling 2:45**. Whether Saturday's demo runs live or as a narrated recording is decided **mechanically** by the §4.3 gate checklist you run at 09:00 — not by mood, not by debate (the rule was ratified at Friday stand-up). You are the timekeeper, the drill sergeant, and the gate clerk. You never negotiate the rules; you record against them.

## 2. Fixed facts you score against (memorise the numbers, keep this page open)

**Beat map (cumulative clock):** Beat 0 hook ends **0:25** · Beat 1 (messy ticket → Approve → Promote) ends **1:20** · Beat 2 (15-second repeat) ends **1:50** · Beat R (rollback + demotion) ends **2:10** · Beat 3 (refusal) ends **2:28** · Close + ask ends **~2:42**.

**The two takeaway lines that must land:** *"the second time is free"* and *"it knows what it's not allowed to touch."* Test: after each run, someone who ISN'T presenting (you) writes from memory the two phrases the pitch wants remembered. If you can't, they didn't land — that's a fail regardless of timing.

**Also required out loud:** "approval moved earlier in time — it never left the loop" · "unscripted" · the ask ("two introductions from this room — to anyone running a 24/7 ops or NOC team…").

**Banned words (any one spoken = note it):** "autonomous"/"autonomously" (about L3 — the correct term is **Standing Approval**), Watcher/Librarian/Assessor/Operator/Auditor (saying "five specialised agents" once is allowed), YAML, ACL, lineage, SoD, embeddings, "deterministic policy engine", P99.

**Contingency lines (must be delivered verbatim in the drills):**
- Jira-degraded (§4.1): *"We've dropped to our cached mirror — everything still executes locally and re-syncs to Jira the moment the venue Wi-Fi does. The live sync is in our submission video."*
- Backup-video switch (§4.2): *"Demo gods. Here's the identical run, recorded last night against this exact build — I'll narrate it live."* (Switch must take **<5 seconds**.)

**Choreography to watch (Presenter 2):** hotkey `G` fires each incident · hero click 1 = APPROVE · hero click 2 = PROMOTE TO STANDING APPROVAL · Revoke is HOVERED at 1:43, never clicked · Window-B (Jira) hops only when the console's sync-tick is green — if not green, the cut is skipped silently.

## 3. Scoring sheet (one per run — copy 8 blanks Friday)

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

Paste into claude.ai with the `QA-bank-extract.md` attachment (re-attach each new chat; keep one chat per rehearsal block):

```
You are a panel of hostile hackathon judges (a VC, a sponsor-track judge, and a sceptical
engineer). Attached is our Q&A bank extract: known questions and the one-sentence openers we
rehearsed. Generate 10 FRESH questions for rehearsal round ‹N›:
- 6 must be re-phrasings or sharper versions of bank questions (different words, same trap);
- 3 must be curveballs NOT in the bank but fair game for this pitch (an agent that re-applies an
  org's documented fixes with approval gates, audit, auto-rollback, permission-aware memory,
  demoed on a simulated broadcaster with real public data and live Jira);
- 1 must be an aggressive interruption-style question a VC would fire mid-answer.
Do NOT repeat any question from this list of already-used ones: [paste previous runs' questions,
or "none"]. Output: a numbered list of the 10 questions only — no answers, no commentary.
```

Drill mechanics: fire 6 of the 10 (your pick, favour the curveballs), 20 seconds per answer, hard cut. Score each: did the answer start from (or clearly land) the bank's bold opener? Did exactly ONE person answer (numbers/tech/market ownership)? Log misses on the sheet. Hand any question that stumped the room to T3 for the Q&A owners to prep overnight/at breakfast.

## 5. Friday prep (17:00–18:00, inside your shift)

1. Confirm T3 sent `QA-bank-extract.md`; run PROMPT once as a smoke test (round "0").
2. Make 8 blank scoring sheets; test your stopwatch lap function against the beat map.
3. Hand N2 a sheet + the §2 page for the Fri 18:30 and 20:00 run-throughs; agree they post filled sheets to the thread.
4. Post in the thread: "Rehearsal blocks Sat 06:45–09:00, gates 09:00–09:30 — presenters + demo machine + phone (party-trick tickets) required."

## 6. Saturday morning schedule (you own the clock)

| Time | What |
|---|---|
| 06:45–07:00 | Setup: demo machine reset (`make demo-reset` — time it, that's gate 6 data), sheets out, Claude chat open |
| 07:00–08:40 | Timed full runs + drill after each. Aim for 4–6 runs. Order: 2 normal · 1 **airplane mode** (Wi-Fi + hotspot OFF; §4.1 line delivered once, exactly) · 1 **video-switch drill** (at beat 2, presenter kills the console feed on your signal; P2 must be narrating the backup video within 5s, §4.2 line verbatim) · then normal runs until 3 CONSECUTIVE cleans exist |
| 08:40–09:00 | Party-trick rehearsal: the two tickets chosen at Friday's playtest, filed from the phone, both outcomes shown on the big screen |
| 09:00–09:30 | **§4.3 GATES (below)** — fill, photograph, announce |
| 09:30 | Hard stop. Depart for Blackett LT1 (doors 10:00). |

## 7. The §4.3 gate checklist (run at 09:00 — this decides live vs recorded)

- [ ] **Gate 0 (prerequisite, verify with the team):** the Fri ~20:00 full two-presenter run-through happened
- [ ] **Gate 1:** 3 consecutive clean full runs at ≤2:45, timed (from this morning's sheets)
- [ ] **Gate 2:** 1 full run in airplane mode passed (degraded-banner path; §4.1 line delivered)
- [ ] **Gate 3:** 1 full run switching to backup video at beat 2; switch <5s (§4.2 drill)
- [ ] **Gate 4:** party trick — 2 messy phone tickets, one triaged correctly, one degraded safely, both on the projector
- [ ] **Gate 5:** `make demo-reset` restores counters/ladder state in <30s

**THE MECHANICAL RULE (pre-ratified — you announce, T1 confirms, nobody debates):**
- **0–1 gates failed → GO LIVE** (live-local-first, drilled video fallback armed).
- **2+ gates failed → FLIP: narrated recording + ONE live element (the Approve click against the cached-mode console).** This is the VC judge's preferred configuration anyway — announce it as a landing zone, not a defeat.

## 8. DONE when

- [ ] Fri: N2 has the sheet + posted results for the 18:30 and 20:00 runs
- [ ] Sat 09:30: all scoring sheets + the gate checklist photographed into the team thread
- [ ] One-line announcement posted and said out loud: "GATES: ‹n› failed → **LIVE** / **RECORDED+one-click**" — T1 ratifies in the thread
- [ ] Stump-questions list handed to T3

## 9. If it goes wrong

- **Presenters resist the flip at 09:25:** read the rule aloud; it was ratified Friday. Your job ends at recording + announcing; T1 owns enforcement.
- **Runs keep failing on time:** the script's own cut is pre-authorised — drop "for what is usually minutes of keystrokes once the fix is known" from the hook. Any bigger cut is the presenters' call, not yours; you just keep timing.
- **Claude free tier caps mid-morning:** reuse round-0 and Friday's generated questions (that's why every list is saved in the thread); the drill degrades to repetition, never to skipped.
- **Clock pressure:** gates outrank extra runs. At 09:00 you stop rehearsing and start gating, whatever the run count.
