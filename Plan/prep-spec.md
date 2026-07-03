# Prep Spec — BUILD-DEPENDENT prep documents

> Written Fri 3 Jul 2026 ~07:00, lands with the 08:00 plan. Owner of this spec: planning lane.
> Scope: the five prep documents that **cannot be written until build reality exists** (post-gate artifacts). The static prep docs — `Prep/industry-primer.md`, `Prep/qa-bank.md`, `Prep/tech-explainer.md` — are owned by the static-prep workstream and are assumed to exist by Fri 17:00; this spec only *refreshes* them (PREP-4) and consumes them (PREP-3, PREP-5).
> Sources of truth this spec derives from and never contradicts: `Idea/refinement/03-pitch-deck.md` (run-of-show, Q&A assignments), `04-demo-and-video-script.md` (§2 script, §4 gates, §5 stat table, §6 fallbacks), `02-architecture-refinement.md` (§3 topology, §5 checkpoints). Gate letters (G0–G8) refer to the master plan's locked gate list.

---

## 0. Schema, conventions, and the dependency graph

### 0.1 Entry schema (every entry below follows it)

```yaml
entry:
  id: PREP-<n>
  deliverable: <name>                       # what gets produced
  generator: <T1|T2|T3|N1|N2 + seat/channel> # who runs the prompt
  bundler_sender: <profile|n/a>             # free-tier packets only: who assembles + sends the packet
  receiver_committer: <profile>             # who receives the output and commits it to the repo
  when: <gate anchor + clock window + hard deadline>
  inputs: <named files; ≤3 small attachments if the generator is a free-tier claude.ai seat>
  prompt: <EXACT paste-ready text, self-contained>
  output: <repo path(s)>
  consumers: <who uses it, at which gate>
  fallback: <what happens if the session caps out or the slot slips>
```

### 0.2 Global conventions (apply to every entry; the prompts restate the load-bearing ones)

1. **Profiles only, never real names.** T1/T2/T3/N1/N2 everywhere — in prompts, outputs, commit messages. The team maps names to profiles themselves (worst-case-honest rule). Any generated text containing a real name is edited before commit.
2. **Free-tier packet protocol (N1/N2 generate on claude.ai FREE tier — assume it):** each packet = ≤3 small attachments + a chunked prompt (no marathon single generation; multi-part outputs are requested as numbered follow-up messages in the same conversation). **T3 bundles + sends every packet** (WhatsApp or email), **T3 receives every output and commits it.** If an attachment is big (qa-bank may be), T3 trims it to the named section before sending — the prompts say which section.
3. **Seat discipline:** PREP-1 runs on T2's Max seat (single medium Claude Code session, post-freeze — T2's seat carries the big sessions by plan). PREP-2A runs on T1's Max seat (medium session — T1's budget is partly spent on the overnight runs, so this stays bounded). PREP-4 runs on T3's Claude Pro as **three separate short sessions** (one per doc) so a cap kills at most one doc, never all three. Nothing in this spec puts T3's seat on a path that dies if a session caps out — every entry has a hand-off fallback.
4. **Numbers law (embedded in every prompt):** only numbers from 04 §5's consistency table / deck Appendix A1 may appear. 18.2h median is always labelled **calendar** hours and never blended with the 8.85 **business**-hour MetricNet figure. Vendor figures carry "(vendor-claimed)". Friday-night measured numbers come only from `bench/RESULTS.md` and the 100-mutation run via `Prep/final-numbers.md` (PREP-1 byproduct). **No document ever ships a ‹XX› placeholder** — missing cells are removed, not bracketed.
5. **Language law:** L3 is "**Standing Approval — a pre-approved standard change**", never "autonomous". Stage-banned words (Watcher/Librarian/Assessor/Operator/Auditor beyond one "five specialised agents", YAML, ACL, lineage, SoD, embeddings, deterministic policy engine, P99) stay out of anything spoken; they are allowed in Q&A-depth notes and technical appendices. Required lines that must survive every document: *"the second time is free"*, *"it knows what it's not allowed to touch"*, *"approval moved earlier in time — it never left the loop"*, *"unscripted"*.
6. **Output locations:** everything lands under `Prep/`. T3 owns all commits of packet outputs; T1/T2 commit their own Claude Code outputs.
7. **Conduct rubric + demo win every conflict with ambition.** Where a prompt forces a cut (e.g. a crib answer that would overclaim), the prompt says to cut toward honesty.

### 0.3 Dependency graph and clock

```
Fri 17:15  T3 bundles PREP-5 packet ──► N2 generates 17:30–18:15 ──► T3 commits ≤19:30
Fri 20:15  TABLE READ runs from Prep/table-read-agenda.md (all five; N1 by video call)
Fri 21:00  G4 CODE FREEZE
Fri 21:15  T1 generates PREP-2A (both run-of-show variants) ──► commit ≤22:00
Fri 22:30  T2 generates PREP-1 (post-recording) ──► commit ≤23:15, incl. Prep/final-numbers.md
Sat 06:45  T3 bundles PREP-3 packet (uses final-numbers.md)
Sat 07:00  N1 generates PREP-3 (cribs ×5, two chunks) ──► T3 commits + prints ≤08:10
Sat 07:30  T3 runs PREP-4 (qa-bank FIRST, then primer, then explainer) ──► diffs by 08:30
Sat 08:15  T3 hand-patches cribs from the qa-bank diff (pen on the printed copies is fine)
Sat 09:30  G7 decision ──► T1 executes PREP-2B (mechanical selection, 10 min, no Claude call)
```

T3's Saturday-morning stack is deliberately sequential and bounded: 06:45 bundle → 07:30–08:20 update passes → 08:30 crib patch → 08:45 G6 BasedAI PR final-ready. If T3 runs >15 min late at any step, the crib patch is the item that drops (cribs are already correct on Friday-night numbers; the patch is belt-and-braces).

Total new hours this spec consumes: ~4.6 ph of generation/commit time (T2 0.75, T1 0.95, T3 1.4, N1 1.0, N2 0.75), all inside the prep/rehearsal allocations already in the 06 §7 ledger ("Q&A prep + printed A1" + rehearsal lines). It removes the un-ledgered alternative: five people improvising these documents at the worst possible hours.

---

## PREP-1 — Systems-design walkthrough + final architecture diagram (incl. slide-8 description)

```yaml
id: PREP-1
deliverable: As-built systems-design walkthrough; one-diagram description for deck slide 8;
             Prep/final-numbers.md reality card (feeds PREP-3 and PREP-4)
generator: T2 — Claude Max seat, ONE Claude Code session over the frozen repo
bundler_sender: n/a (direct Claude Code session)
receiver_committer: T2 commits; pings T3 that final-numbers.md is ready for Saturday packets
when: Fri ~22:30, immediately after the G4 recording session ends (21:00–22:30).
      Hard deadline 23:15 — the one sanctioned overrun past the nominal 22:00 day end (~45 min).
inputs: the frozen repo itself (Claude Code reads it); Idea/refinement/02-architecture-refinement.md;
        bench/RESULTS.md; the 100-mutation run output; docs/compliance/
output: Prep/systems-design-walkthrough.md ; Prep/final-numbers.md
consumers: T2 (slide-8 build + tech Q&A owner, Sat); deck builder (slide 8 + PDF export);
           PREP-3 and PREP-4 packets (final-numbers.md); BasedAI PR README cross-check (G6)
fallback: if the session caps out mid-run, T2 finishes on ChatGPT Pro/Codex for the mechanical
          parts (file-tree summary, divergence table) and hand-writes the slide-8 description —
          the slide-8 paragraph and final-numbers.md are the two blocks that must exist by Sat 06:45.
```

**EXACT PROMPT (paste into a fresh Claude Code session at the repo root, frozen build checked out):**

> You are writing the as-built systems-design walkthrough for Precedent, a hackathon project that was code-frozen tonight at 21:00. Work ONLY from what is actually in this repository right now — run `git ls-files` first and read the real modules. The design intent is in `Idea/refinement/02-architecture-refinement.md`; treat it as the *intended* design and this repo as the *actual* one. Where they differ, the repo wins and the difference must be recorded, never papered over.
>
> Write `Prep/systems-design-walkthrough.md` with exactly these sections:
>
> 1. **System map, as built** — one screen: every top-level package/module that exists, one line each, with its real file path. No aspirational components.
> 2. **The loop, end to end** — trace one incident through the actual code: ingest → triage/extraction → retrieval → risk/policy gate → approval → execution → verification → memory write → audit. For each hop name the file and the function that does it, and which model role (FAST/SMART/HEAVY/EMBED per `precedent/models.py`) is called, if any. State explicitly where NO LLM is in the path (the policy gate and the standing-approval fast-path).
> 3. **Permission-aware memory, as built** — the A/B/C semantics from 02 §2: which of A (lineage conjunction), B (compiled effective policy), C (governed redaction) are implemented vs stubbed in `precedent_memory/`, with file references; the fail-closed rule as it actually reads in `retrieve.py`; the measured consistency window (flip→dark) if the drift run produced one.
> 4. **Ladder and fast-path, as built** — graduation/demotion rules as coded, the fingerprint definition, and what actually happens on the 15-second path.
> 5. **Fetch topology, as built** — how many agents are ACTUALLY registered on Agentverse right now (count them, don't assume three; if the Librarian collapsed in-process per cut-line 3, say so and include the rehearsed two-agent answer), which speak Chat Protocol, how the ASI:One approval gate binds sender address → approver, and the 10-minute expiry behaviour.
> 6. **Reliability layer, as built** — Jira poll + write-behind + cache/replay, degraded-mode banner, airplane-mode behaviour, `make demo-reset`.
> 7. **Divergence ledger** — a three-column table: `02 said | repo has | status (SHIPPED / CHANGED / STUB / CUT)`. Every row of 02's §0 TL;DR table must appear here. This ledger is the honesty backstop for Q&A: anything CUT or STUB may never be claimed on stage or in the README.
> 8. **Slide-8 one-diagram description** — a self-contained paragraph plus an ASCII sketch that a slide-builder with zero context can render, matching the deck spec exactly: tickets/alerts enter left (Jira logo); five UNNAMED agent nodes in a pipeline (adjust the count if the ledger says fewer — the deck must match reality); a shield icon between "decide" and "execute" labelled "deterministic policy gate — no LLM in the authorisation path"; a memory cylinder underneath labelled "executed fixes, permission-aware"; arrows out to "target systems"; three-item tech strip at the bottom: "Live Jira Service Management · open-weight models end-to-end · agents live on Fetch.ai Agentverse / ASI:One". Nothing else — no extra boxes.
> 9. **Q&A depth notes** — for each of the deck's technical appendix slides A3 (standing-approval semantics), A4 (permission-aware memory), A6 (integration tiers): a 5-line "if pushed, say this, and here is the file that proves it" note, using only what section 7 marks SHIPPED.
>
> Also write `Prep/final-numbers.md` — a ONE-PAGE reality card (it will be sent as a small attachment to free-tier claude.ai sessions tomorrow, so keep it under ~150 lines):
> - Every measured number from `bench/RESULTS.md` (P50/P99, FNR/FPR, drift, time-to-consistency) with its pass/fail vs the published threshold; every number from the 100-mutation extractor run (correct-match / safe-degrade / false fast-path).
> - The pre-verified corpus numbers verbatim: 94.4% fix-class match over 24,918 incidents; 18.2h median (LABEL IT "calendar hours"; p75 136.6); 558 recurring classes = 94.8% of volume.
> - Agent count actually registered on Agentverse; the ASI:One shared-chat URL and Agentverse profile URLs captured tonight; hosted-Watcher deploy status; repo URL.
> - A SHIPPED/CUT one-liner list from the divergence ledger (section 7).
> - Rules footer, verbatim: "Never blend 18.2 calendar hrs with 8.85 business hrs. Vendor figures say (vendor-claimed). L3 = Standing Approval, never autonomous. If a number is not on this card or in 04 §5, do not say it."
>
> Constraints: profiles T1/T2/T3/N1/N2 only, no real names anywhere. If a bench number does not exist, OMIT the row entirely — never write a placeholder like ‹XX›. When you finish, run `grep -rn '‹' Prep/` and fix any hit.

---

## PREP-2 — Demo run-of-show, two pre-written variants + post-decision final

```yaml
id: PREP-2
deliverable: Two complete run-of-show documents (live-first and recorded-first), every click,
             every verbatim line, every fallback cue; plus the mechanical Sat-morning selection step
generator: Stage A: T1 — Claude Max seat, one medium Claude Code session.
           Stage B: T1, by hand — NO Claude call.
bundler_sender: n/a
receiver_committer: T1 commits Stage A; Stage B final copy goes to both presenters' phones + one print
when: Stage A: Fri 21:15–22:00, pinned to G4 (freeze at 21:00 means clicks/UI/hotkeys are final;
      T1 just watched the 20:00 run-through so knows exactly what shipped). Commit by 22:00.
      Stage B: Sat 09:30–09:40, immediately after the G7 rehearsal-gate decision, before travel.
inputs: Idea/refinement/04-demo-and-video-script.md (whole file); T1's shipped/cut checklist
        (filled into the prompt's fill-in block — see prompt)
output: Prep/run-of-show-live-first.md ; Prep/run-of-show-recorded-first.md ;
        Prep/run-of-show-FINAL.md (Stage B: copy of the chosen variant + gate-outcome margin notes)
consumers: both presenters (P1 = T1 voice, P2 = T2 hands) at G7 rehearsal and on stage;
           N2 (timekeeper/backstage cues)
fallback: if Stage A slips past 22:00, the raw 04 §2 script IS the live-first variant (it already
          exists); T1 writes only the recorded-first variant Sat 06:30–07:00. Stage B never needs
          Claude — if both variants somehow don't exist at 09:30, the §4.3 rule still decides the
          mode and 04 §2/§4.2 are carried as-is.
```

**Why two variants pre-written:** the demo-mode decision is made mechanically by 04 §4.3's rehearsal gates at Sat 09:00–09:30 (two failed gates flips live→recorded). The decision arrives 30 minutes before the team must travel — there is no time to *write* anything then. So both variants exist by Friday night and Stage B is pure selection.

**EXACT PROMPT — Stage A (paste into a fresh Claude Code session at the repo root; T1 fills the checklist block BEFORE pasting):**

> You are producing the two performance run-of-show documents for tomorrow's 3-minute Demo Day pitch (Blackett LT1, 5 min total = ~3 min pitch + 2 min Q&A). The master script is `Idea/refinement/04-demo-and-video-script.md` — its §2 second-by-second script, §1 stage setup, §4 contingency tree, §5 stat table and §6 fallback table are the source of truth. Do not invent new spoken lines; where a line must change because a build element was cut, apply §6's exact replacement wording.
>
> Build reality as of tonight's 21:00 freeze (I have ticked each item — trust this block over any assumption):
> ```
> SHIPPED / CUT checklist (edit before running):
> [ ] Baseline Bar persistent header        [ ] Promote/Revoke buttons
> [ ] Ticket-text mutation layer            [ ] Deterministic recovery injection (beat R)
> [ ] Fingerprint fast-path (~15s run)      [ ] Real-data seeding (UCI/runbooks/TVmaze)
> [ ] Robustness chip (mutation bench)      [ ] Rollback proof panel (hash compare)
> [ ] Cumulative close strip                [ ] Jira sync-tick indicator
> [ ] Incident 3 live (vs video-only)       [ ] Attract-mode idle loop
> Hotkeys/tabs confirmed at the 20:00 run-through: incident generator = `G`;
> Window A→B = Cmd+Shift+]; QuickTime = Cmd+Tab; reset = `make demo-reset`.
> Backup-video chapter markers exist at 0:25 / 1:20 / 1:50 / 2:10: [ ] yes [ ] no
> ```
>
> Produce TWO files.
>
> **File 1 — `Prep/run-of-show-live-first.md`** (default mode: live local console, drilled video fallback):
> - A pre-walk-on checklist table lifted from 04 §1.1 (windows A/B/C, terminal armed, phone, clicker, hotspot ON, venue Wi-Fi OFF, zoom 125%, video file local on disk), each row with an owner column (P1 = presenter/voice, P2 = driver/hands, N2 = backstage/time).
> - The full 2:42 script as a four-column table: `clock | P1 says (verbatim from §2, with §6 substitutions for anything CUT above) | P2 does (every keypress and click, spelled out: "press G", "Cmd+Shift+] — ONLY if sync-tick green, else skip silently", "click APPROVE", "click PROMOTE TO STANDING APPROVAL", "hover REVOKE — do not click") | fallback cue`.
> - The fallback-cue column encodes §4.0–§4.2 as in-the-moment triggers: "Jira cut not rendered in 2 s → skip all Window B cuts, say the §4.1 line ONCE"; "any beat stalls >8 s twice → Cmd+Tab to QuickTime at the current chapter marker, say the §4.2 line, continue narration unchanged"; the switch must be executable in <5 seconds.
> - Q&A page: the five §3 weapons verbatim, plus the party-trick arming steps (phone, QR — the Jira-portal QR, never the contact QR) and both rehearsed outcomes (clean triage / visible safe-degrade).
> - A "numbers you may say" footer copied from 04 §5's first column only.
>
> **File 2 — `Prep/run-of-show-recorded-first.md`** (fallback mode per §4.3's rule: narrated recording + ONE live element):
> - Same structure, but the primary surface is the backup video played from QuickTime, narrated live by P1 using the same §2 lines; P2's column becomes video transport cues (pre-position at chapter markers; pause points).
> - The ONE live element: at beat 1's approval moment (chapter 0:25–1:20), P2 pauses the video and performs a REAL Approve click against the console running in cached/airplane mode, then resumes. Write the exact pause timestamp, the window switch both directions, and the resume cue. If even the cached console is dead, the run-of-show says: skip the live click, never apologise, keep narrating.
> - Opening line difference: P1 says once, confidently, near the start: "You're watching last night's run against the frozen build — I'll narrate it live, and we'll do one real approval in front of you." Never say "unfortunately".
> - Same Q&A page and numbers footer.
>
> Constraints for both files: 2:42 target with the 18-second buffer noted; the four required lines ("the second time is free", "it knows what it's not allowed to touch", "approval moved earlier in time — it never left the loop", "unscripted" — drop "unscripted" ONLY if the mutation layer is ticked CUT, per §6) must each appear exactly where §2 puts them; stage-banned words never appear in a "says" cell; L3 is always "Standing Approval". Profiles T1/T2/T3/N1/N2 only — on the page P1=T1, P2=T2, backstage=N2, party-trick phone=N1, printed-numbers pocket card=T3. End both files with a one-line version stamp: "written against freeze <git short-hash>, Fri 21:15".

**Stage B (mechanical, Sat 09:30–09:40, no Claude):** T1 takes the G7 outcome (§4.3 rule: <2 failed gates → live-first; ≥2 → recorded-first), copies the chosen file to `Prep/run-of-show-FINAL.md`, strikes the cover of the losing variant, and hand-notes any gate-specific margin cues (e.g. "airplane run passed — hotspot only", "party-trick degrade path only"). Both presenters get it on their phones; one printed copy in T2's bag. Commit when at a keyboard; the phone copy is the operative one.

---

## PREP-3 — Per-profile crib sheets ×5

```yaml
id: PREP-3
deliverable: Five one-page crib sheets (T1, T2, T3, N1, N2): stage ownership, 5 likeliest
             questions with answers, two takeaway lines; N1/N2 versions carry the bridge protocol
generator: N1 — claude.ai FREE tier (assume it), one conversation, two chunked prompts
bundler_sender: T3 bundles + sends the packet Sat 06:45 (WhatsApp or email)
receiver_committer: T3 receives both outputs, commits Prep/crib-sheets/, prints 2 copies of each
                    by 08:10 (one per person + spares in T2's bag)
when: Sat 07:00–07:50 (N1's 06:30–09:30 window), pinned between G4 outputs (final-numbers.md
      exists from PREP-1) and G7 (cribs must be in hands before the 09:00 rehearsal gates).
      Consistency patch: 08:15, T3 pen-patches printed cribs from PREP-4's qa-bank diff.
inputs: EXACTLY 3 attachments, bundled by T3:
        (1) Prep/qa-bank.md — if >1,500 lines, T3 trims to the "top questions" section
        (2) Prep/final-numbers.md (from PREP-1)
        (3) Prep/tech-explainer.md
        The Q&A role assignments from 03 and the G0 named-person grid go INLINE in the prompt
        (they are 10 lines — not an attachment).
output: Prep/crib-sheets/crib-T1.md, crib-T2.md, crib-T3.md, crib-N1.md, crib-N2.md
consumers: all five, on stage Sat + at the G7 gate session; N2's crib is also the cross-assignment
           card for Q&A
fallback: if N1's free session caps mid-way, chunk 2 (T3/N1/N2 cribs) moves to T1's Max seat
          Sat 08:00 window with the same prompt text; if the whole packet fails, the table-read
          notes (PREP-5 output) + printed A1 serve as degraded cribs — flag at 08:30, don't improvise.
```

**Stage-role mapping (default — CONFIRM OR OVERRIDE on the G0 named-person grid at Fri 09:00 stand-up; the prompt below carries whatever the grid says):**

| Profile | On stage | Q&A ownership (per 03: one owns numbers, one owns tech, one owns market — never two people on one question) |
|---|---|---|
| T1 | Presenter 1 — voice, narrative, the ask | Market/business: A5, A8, A9, slide 11, "why won't ServiceNow build this" |
| T2 | Presenter 2 — hands, hero clicks | Tech: A3, A4, A6, slide 8, latency/reliability, "wasn't that scripted" (tech half) |
| T3 | Numbers owner, pocket card | A1 table, A2 provenance sourcing, any challenged number |
| N1 | Party-trick marshal — phone with Jira portal QR | Data provenance in plain English; "is the data real?"; logistics/front-of-house |
| N2 | Timekeeper + backstage — video cue, demo-reset, 90-second-cut trigger | Plain-English product story; first-touch on any question while the owner steps in |

**EXACT PROMPT — chunk 1 (N1 pastes into a new claude.ai chat with the 3 attachments; T3 sends this text with the packet):**

> You are writing pocket crib sheets for a five-person hackathon team pitching "Precedent" at Demo Day today (3-min pitch + 2-min Q&A, VC judges + sponsor judges). Attached: (1) `qa-bank.md` — the full question bank with model answers; (2) `final-numbers.md` — the ONLY numbers anyone may say, with usage rules in its footer; (3) `tech-explainer.md` — the plain-English explanation of how the product works.
>
> Team profiles and ownership (fixed, use these labels, never invent names):
> - **T1 — Presenter 1 (voice).** Owns market/business questions: competition, "why won't ServiceNow/Conduct build this", liability, market size bottoms-up, the ask.
> - **T2 — Presenter 2 (hands, drives the demo).** Owns technical questions: standing-approval semantics, permission-aware memory, integration reality, latency/reliability, "wasn't that scripted" (technical half).
> - **T3 — Numbers owner.** Owns every quantitative claim and its source; carries the printed source table.
> - Rule from our deck: never two people answering one question — each crib must say when its owner takes over and when they stay silent.
>
> In THIS reply, produce crib sheets for **T1 and T2 only** (T3/N1/N2 come in my next message). Each crib sheet is ONE printable page, markdown, exactly this structure:
> 1. **Your job on stage** — 3 lines max (from the ownership above; T2's includes the physical actions: hero clicks, window discipline).
> 2. **Your 5 likeliest questions** — pick the 5 from `qa-bank.md` most likely to land on THIS person's ownership area, each with a tightened ≤40-word answer. Every number in an answer must appear in `final-numbers.md` — if it doesn't, rewrite the answer without it. Label 18.2h as "calendar hours" if used; vendor figures say "(vendor-claimed)".
> 3. **Your two takeaway lines** — the two sentences this person should land no matter what. T1's must include "the second time is free". T2's must include "it knows what it's not allowed to touch" and "the model never authorises itself".
> 4. **Handoff rule** — one line: which questions you deflect and to whom (by role, e.g. "numbers → our numbers owner").
> 5. **Never say** — 4 bullets: "autonomous" (say "Standing Approval — a pre-approved standard change"), any number not on the card, agent code-names/jargon (YAML, ACL, embeddings, P99 — plain English on stage), anything the shipped/cut list in `final-numbers.md` marks CUT.
> Keep each crib under 350 words. No real names — profiles only.

**EXACT PROMPT — chunk 2 (same conversation, sent after chunk 1 completes):**

> Now the remaining three cribs, same one-page structure, same rules. These three people are the numbers owner and two NON-TECHNICAL members — their cribs must let them survive a technical question without faking depth:
> - **T3 — Numbers owner.** Their 5 questions are the 5 most-challenged numbers in `qa-bank.md` (downtime cost, repeat-incident share, MTTR, our measured 94%/18.2h-calendar corpus numbers, ticket-cost ladder). Each answer = the number + its source name + vintage, ≤25 words. Add a 6th mini-row: "if a number is challenged that isn't on my card → 'good challenge — it's in our sourced appendix; the discipline matters more than the digit' and hand to T1."
> - **N1 — Party-trick marshal + data provenance.** Their 5 questions centre on "is the data real?" and the live-ticket trick. Answers in plain English from `tech-explainer.md`: real public runbooks, a 141k-event public incident log, real programme metadata; "the systems are simulated; the content is real."
> - **N2 — Timekeeper/backstage + plain-English first-touch.**
> For BOTH N1 and N2, add a **Bridge protocol** section (this is the heart of their cribs): a 3-step recipe for handling a technical question aimed at them: (1) answer the honest one-sentence core from `tech-explainer.md` — give them 5 pre-written one-sentence cores for the 5 likeliest technical questions (how does it know two incidents are the same; what stops the AI approving itself; what if the fix fails; why can't it read the restricted runbook; is 15 seconds real); (2) land the takeaway line ("approval never leaves the loop — it just moves earlier in time" / "it knows what it's not allowed to touch"); (3) bridge out with the exact handoff phrase: "…and for the implementation detail, that's exactly what our engineer built — [turn to T2]." The bridge must feel like teamwork, not evasion — write it so a judge hears a correct answer BEFORE the handoff.
> Keep each under 350 words. Output all three cribs in this one reply.

**T3 post-processing (Sat ~08:00):** split into five files under `Prep/crib-sheets/`, strip any real name, commit, print 2×5 copies. At 08:15, apply pen corrections from PREP-4's `update-pass-diff.md` (qa-bank rows only).

---

## PREP-4 — Update pass: refresh the three static prep docs against final build reality

```yaml
id: PREP-4
deliverable: Refreshed Prep/industry-primer.md, Prep/qa-bank.md, Prep/tech-explainer.md
             + Prep/update-pass-diff.md (what changed — drives the 08:15 crib patch)
generator: T3 — Claude Pro seat, THREE separate short sessions (one per doc, ~15 min each),
           order fixed: qa-bank FIRST (07:30), tech-explainer (07:50), industry-primer (08:05)
bundler_sender: n/a (T3 runs it directly)
receiver_committer: T3 commits all three + the diff file by 08:30
when: Sat 07:30–08:30, pinned after PREP-1 (needs Prep/final-numbers.md) and before G6 (08:45
      BasedAI PR final-ready — the refreshed qa-bank informs the PR's Q&A-facing README lines)
      and G7 (09:00 gates).
inputs: per session: the one doc being refreshed + Prep/final-numbers.md (2 attachments/paste-ins)
output: the three refreshed docs in place + Prep/update-pass-diff.md
consumers: crib patch 08:15; anyone answering Q&A Sat; G8 DoraHacks final-submit text
           (organizer-question answers are ONE-SHOT and were drafted Friday — the diff file is
           checked against those drafts before the 17:30 final submit, NOT to rewrite them, only
           to catch a now-false claim)
fallback: sessions are independent — if T3's Pro seat caps out after session 1, the remaining two
          docs go untouched (they are less volatile) and only update-pass-diff.md (qa-bank rows)
          is required downstream. Overflow route if even session 1 dies: hand this prompt + the two
          attachments to T1's Max seat 08:00 window.
```

**EXACT PROMPT (one prompt, parameterized — T3 runs it three times, replacing `{DOC}`; attach `{DOC}` and `Prep/final-numbers.md` each time):**

> This is a bounded update pass, not a rewrite. Attached: (1) `{DOC}` — a prep reference document written yesterday, partly before the build finished; (2) `final-numbers.md` — the post-code-freeze reality card: final measured numbers, what shipped, what was cut, final URLs, and the usage rules in its footer.
>
> Do exactly this and nothing more:
> 1. Scan `{DOC}` for every claim that `final-numbers.md` contradicts or supersedes: stale/placeholder numbers, features described as present that the SHIPPED/CUT list marks CUT or STUB, agent counts, missing URLs (ASI:One shared chat, Agentverse profiles, repo), anything phrased as intended-future that is now done (or now false).
> 2. Output the FULL corrected document, changing ONLY those lines. Do not restructure, do not restyle, do not add new sections, do not "improve" prose. If a number in the doc has no replacement on the reality card, delete the sentence rather than keep a stale or bracketed figure — never leave a ‹XX›.
> 3. Enforce the standing rules while you're in there: 18.2h median is labelled "calendar hours" everywhere it appears and is never merged with the 8.85 business-hour figure; vendor figures carry "(vendor-claimed)"; L3 is "Standing Approval — a pre-approved standard change", never "autonomous"; anything marked CUT is described in past-tense-honest form ("designed, not built this weekend") or removed.
> 4. After the document, output a section titled `DIFF` listing every change as `line-context: old → new`, one per line. I will paste that into a running diff file.
>
> Keep your changes minimal and mechanical. No real names — team members are T1/T2/T3/N1/N2 if mentioned at all.

**T3 assembly:** concatenate the three `DIFF` sections into `Prep/update-pass-diff.md` with a header row per doc; commit all four files by 08:30; carry the qa-bank rows to the printed cribs at 08:15 (qa-bank session finishes first precisely so this patch can happen on time).

---

## PREP-5 — Table-read rehearsal agenda (Fri 20:15, 25 min, all five)

```yaml
id: PREP-5
deliverable: A minute-by-minute 25-minute table-read agenda incl. the 15 preselected questions,
             the deliberate cross-assignment beat, a scoring rubric, and N2's provisional bridge card
generator: N2 — claude.ai FREE tier, one conversation, single bounded prompt (N2 is on shift
           13:30–21:30 and facilitates the table read itself)
bundler_sender: T3 bundles + sends the packet Fri 17:15 (immediately after the G2 17:00 checkpoint,
                so the question emphasis reflects any fired cut-lines)
receiver_committer: T3 receives, commits Prep/table-read-agenda.md by 19:30, prints one copy
when: generated Fri 17:30–18:15; used Fri 20:15–20:40 — wedged between the 20:00 second run-through
      and the 21:00 G4 freeze, deliberately: the builders' hands are off the keyboard anyway while
      the final pre-freeze push settles, and the read needs the run-through fresh in memory.
      NOTE (flag at G0 stand-up): N1's Friday shift ends 18:00 — N1 joins the 25-minute read by
      video call; T3 sends N1 the agenda PDF/photo at 19:45.
inputs: EXACTLY 3 attachments: (1) Prep/qa-bank.md (T3 trims to the top-questions section if large);
        (2) Prep/tech-explainer.md; (3) a T3-made half-page extract of 03-pitch-deck.md containing
        ONLY: the Q&A assignments paragraph, the banned/required words, and the two lines the room
        must remember. The stage-role mapping (same table as PREP-3) goes INLINE in the prompt.
output: Prep/table-read-agenda.md ; Prep/table-read-notes.md (T3 scribes during the read —
        blank template is part of the agenda output)
consumers: all five Fri 20:15; the notes feed PREP-3 (which questions wobbled → crib emphasis)
           and PREP-4 (answers that need sharper wording in qa-bank)
fallback: if the packet round-trip fails by 19:30, T3 hand-writes a 10-line version at 19:45:
          3 questions per person picked from the bank's headings + the one cross-assignment below —
          the read happens regardless; the agenda is an efficiency aid, not a gate.
```

**EXACT PROMPT (N2 pastes into a new claude.ai chat with the 3 attachments; T3 sends this text with the packet):**

> You are writing a tight 25-minute "table read" rehearsal agenda for tonight at 20:15 for a five-person hackathon team pitching "Precedent" tomorrow (3-min pitch + 2-min VC Q&A). Attached: (1) `qa-bank.md` — the question bank with model answers; (2) `tech-explainer.md` — the plain-English technical explainer; (3) `deck-extract.md` — Q&A ownership rules, banned/required words, and the two lines the room must remember.
>
> Team profiles (fixed labels, never invent names): **T1** presenter-voice, owns market/business Q&A · **T2** presenter-hands, owns technical Q&A · **T3** owns numbers and sources · **N1** non-technical, owns data-provenance-in-plain-English and the live-ticket party trick (joins tonight by video call) · **N2** non-technical, timekeeper/backstage, plain-English first-touch. Facilitator tonight: N2 (me). Scribe: T3.
>
> Produce `table-read-agenda.md` with exactly:
> 1. **Header block** — time 20:15–20:40 (hard stop 20:40: code freeze at 21:00), room + video-call link placeholder for N1, materials list (this agenda printed, phone timer, `qa-bank.md` open on one screen, notes template).
> 2. **Rules (0:00–0:03)** — read aloud: answers ≤30 seconds; every answer must end on a takeaway line; the banned words and the required lines from `deck-extract.md` listed verbatim; "pass" = correct + ≤30s + contains the required line where one applies; anyone may say "bank it" to stop a rambling answer.
> 3. **Quiz rounds (0:03–0:18)** — for EACH of the five profiles pick **3 questions from `qa-bank.md`** matched to their ownership above (15 total; for N1 and N2 pick plain-English-answerable ones, e.g. "is the data real?", "what does it actually do?", "what happens when the fix fails?"). Print each question with: who answers, the ≤30-word model answer from the bank (facilitator's key — folded so the answerer can't see it), and a one-line "listen for" cue. One minute per Q&A including feedback.
> 4. **Cross-assignment beat (0:18–0:23)** — the designed drill: the facilitator asks **N2** (yes, the facilitator hands their card to T3 and takes the hot seat) ONE deliberately technical question — use: *"How do you stop the AI from approving its own actions?"* — and N2 answers using ONLY the bridge method: one honest plain-English sentence (from `tech-explainer.md`: a fixed rulebook and a named human decide what runs — the AI only proposes), then the takeaway line ("approval never leaves the loop — it moves earlier in time"), then the handoff ("for the implementation detail — that's exactly what our engineer built" → turn to T2), and T2 adds ≤15 seconds of depth. Include a **provisional bridge card** for N2 inline in the agenda (5 one-sentence honest cores for the 5 likeliest technical questions + the handoff phrase) — tomorrow morning's full crib sheets will replace it, but tonight's drill runs off this card. Then 2 minutes of debrief: did the bridge sound like teamwork or evasion?
> 5. **Close (0:23–0:25)** — recap who owns what in Q&A tomorrow ("never two people answering one question"), tomorrow's timeline one-liner (cribs at 08:10, rehearsal gates 09:00, mode decision 09:30), and the two lines everyone repeats together once, out loud, as the last act: "the second time is free" / "it knows what it's not allowed to touch."
> 6. **Notes template** (`table-read-notes.md` skeleton) — a 15-row table: question | answerer | pass/wobble/fail | exact wobble | fix owner (crib emphasis vs qa-bank wording). T3 fills it during the read.
> Keep the whole agenda under 2 printed pages. Numbers in model answers must come from the bank verbatim — do not introduce new ones. No real names.

---

## Cross-checks this spec enforces (read at G0 stand-up, 60 seconds)

1. **Named-person grid → PREP-3/PREP-5 mapping.** The default stage-role table in PREP-3 is confirmed or overridden at G0; whatever the grid says is what T3 pastes into both packets. Profiles only, on paper and in prompts.
2. **N1's 20:15 video call** is agreed at G0 (25 min outside N1's Friday shift — it is the only out-of-shift ask in this spec).
3. **PREP-1 feeds everything Saturday.** If the 22:30 session produces nothing else, it must produce `Prep/final-numbers.md` — without it, PREP-3 and PREP-4 packets cannot be bundled at 06:45/07:30 and the cribs ship on Friday-afternoon numbers (legal but weaker).
4. **The ‹XX› grep** (`grep -rn '‹' Prep/`) runs twice: end of PREP-1 (T2) and after the 08:30 commits (T3). Same mechanical guard as the deck's pre-export grep.
5. **Nothing here moves a gate.** Every WHEN is inside existing availability windows except PREP-1's sanctioned ~45-min overrun (task-pinned) and N1's 25-min call; both are flagged, neither touches the critical path. Where prep ambition conflicted with the Conduct rubric or demo time (e.g. richer cribs vs one printable page; a second table read), this spec cut the ambition and says so here.
