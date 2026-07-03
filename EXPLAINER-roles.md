# Who does what — every role, in plain words

*A thorough, jargon-free breakdown of all five roles. Read your own section closely; skim the others so you understand what your teammates are building and how it all fits. The five roles are labels (T1, T2, T3, N1, N2) — the team decides who is who at kickoff.*

**The shape of it:** Two people build the "engine" and "brain" of the product (T1, T2). One person builds the proof-and-paperwork layer and handles submitting (T3). Two people make the whole thing understandable and presentable — the real data, the fix-instructions, the deck, the video, the outreach (N1, N2). Everyone has the code and good AI tools, so N1 and N2 commit their own work directly.

A note that applies to everyone: **the goal is the demo working.** The single most important thing the whole team is racing toward is the "vertical slice" — the core demo running end-to-end. Everything else is secondary to that.

---

## T1 — The engine: the fix process, the fake company, and the chat agents

**Who you are, simply:** You build the part that actually *does the work* — the step-by-step process that takes a problem and turns it into a fix, plus the pretend company system we break and fix during the demo, plus the chat-based agents.

**What you're building, in order:**

1. **The connection to the AI models.** Our product is only allowed to use "open" AI models (a hard rule for one of the prizes). You wire up the connection to those models and add a safety check that refuses to run if anything tries to sneak in a banned model. You also register a first, simple chat agent early — because the network we're on takes time to "notice" a new agent, so starting it early matters.

2. **The fake company ("the simulator").** We can't demo on a real broadcaster's systems, so you build a realistic stand-in: a pretend TV scheduler, a rights database, a publishing system. It's seeded with **real public data** (a real UK TV schedule, real past-incident records), and — importantly — you *keep the messiness* (missing fields, duplicate names). That mess is what makes problems appear naturally, and the judges reward realism. You also build the exact demo problems (incidents 1, 2, 3) so they happen the same way every rehearsal, plus a switch that makes a fix fail on purpose (so we can show the automatic undo).

3. **The fix process itself ("the loop").** This is the heart of it: read the problem → work out exactly what kind of problem it is using fixed rules (not the AI guessing) → look up the fix → check the risk → ask for approval (or run instantly if pre-approved) → do it → check it worked → undo it if it didn't → remember it. The clever bit you protect: when a problem type has been pre-approved, the fix runs with **zero AI calls** — that's how it happens in ~15 seconds and why it's reliable on stage.

4. **The chat agents.** You make the agents "live" on Fetch's network so a judge can resolve an incident just by chatting to them — no app needed. When someone types "approve" in the chat, that person's identity becomes the official approver in our records. You also leave one agent running after the hackathon (a bonus the judges reward).

**Why it matters:** If your parts work, there is a demo. If they don't, there isn't. You're on the critical path.

**How you know you're done (each piece):** the models refuse anything banned; the simulator replays the same incidents identically; the loop resolves incident 1 with one approval, incident 2 instantly with no AI in the trace, and a failed fix auto-undoes; a judge can run the whole thing inside a chat.

**Your first move:** `git checkout build/t1-core-loop-sim-agents`, open `precedent/venice.py` and `precedent/models.py`, and wire up the model connection + the first chat agent. Full detail: `Plan/BUILD-PLAN.md` §4 (T1).

---

## T2 — The brain's memory and the face: permission-aware memory, live permissions, and the screen

**Who you are, simply:** You build two things — the *memory that respects permissions* (the part that wins one whole prize) and the *screen the judges watch* (the part that wins the demo). Both are yours because both have subtle traps where an AI tool gets it *almost* right, and "almost" isn't good enough for security.

**What you're building, in order:**

1. **The permission-aware memory.** This is a proper little library. Every remembered fix knows which permissions it inherited from the documents it came from, and to read it you must satisfy **all** of them (not just the loosest one). Two hard properties you must get exactly right:
   - **No AI in the permission decision.** A fixed, fast lookup decides who can see what. The AI never gets a vote. (There's a file that must contain zero AI connections — keep it that way.)
   - **"Fail closed."** If we're ever unsure whether someone still has permission (say the connection to the permission source drops), we **deny** access rather than risk a leak. A stale guess must never *widen* access, only narrow it.
   You start from a ready-made database design and a set of failing tests that describe exactly the right behaviour — your job is to make those tests pass. One test is the money case: a fix built from two restricted sources must be invisible to someone who only has permission for one of them.

2. **Keeping permissions in step with the real Jira tool.** The company's real permission rules live in Jira (the ticketing tool). You build the part that checks Jira every couple of seconds and updates our memory's permissions to match. The showpiece: flip a permission in Jira, and within seconds **both** Jira itself *and* our memory stop showing the restricted item — two independent locks reacting to one change. You verify this against the *real* Jira site (we've already set it up).

3. **The console (the screen).** A clean web page the judges watch. The order you build it in matters: **first** the "stopwatch bar" (showing manual = 8h51m vs our seconds) and the three buttons (Approve / Promote / Revoke) — because the core demo needs exactly those. Then the live feed of problems, the step-by-step trace, the record log, and so on. One rule: the top level of autonomy is always called **"Standing Approval,"** never "Autonomous."

4. **The impressive extras (only after the core works):** a hotkey that flips a permission live on stage, a mode where the screen is already resolving problems by itself when judges walk in, and a one-key "here's the auditor's record" document.

**Why it matters:** You own the hardest-to-fake part (real permission enforcement, proven with numbers) and the most-watched part (the screen). Both are judged heavily.

**How you know you're done:** the memory tests pass and the permission file has no AI connections; a permission flip in Jira goes dark in our memory within ~8 seconds; the judges can drive incidents 1 and 2 by clicking, with the stopwatch drawing live.

**Your first move:** `git checkout build/t2-memory-jira-console`, run `make test` to see the three memory tests that are *waiting* to pass, then start making them pass. Full detail: `Plan/BUILD-PLAN.md` §4 (T2).

---

## T3 — The proof, the checks, and getting it submitted

**Who you are, simply:** You produce the *numbers that beat the competition*, the *checks that keep everyone honest*, and the *mechanics of actually submitting to each track*. Your work stands on its own (it doesn't wait for the others to finish), so you're also the flexible extra pair of hands.

**What you're building/doing, in order:**

1. **Open the one track's submission early.** One prize (BasedAI) is entered by opening a "pull request" on GitHub (a formal code submission), separate from the main submission site. You open a skeleton version first thing so the frame exists, then fill it in through the day. There's a step-by-step guide for this.

2. **Register the other two agents** on the network (so T1 only has to plug in the real behaviour later), and grab an early "here's it working in a chat" link as insurance.

3. **The scorecard ("the benchmark").** This is your headline contribution. The BasedAI sponsor published an exact list of targets a permission memory should hit (how rarely it wrongly denies or allows, how fast it is, how well it handles attacks, etc.). You build a test that measures our memory against **their own targets** and produces a clean pass/fail table — and you do it against our *live* permission source, which a copycat competitor (who built a standalone toy) simply cannot show. Crucially, you build an **independent checker** to grade the results, so we can't be accused of marking our own homework. You cover **all six** of the named "attack" tests, not a subset.

4. **The honesty checks and the submissions.** You run the "no secrets leaked" scan and make the code repository public (a hard requirement — the scan must be clean first; we've already verified it is). You commit the scorecard numbers into the submission. On Saturday you finalise everything: the last measurement run, the submission page, and the final submit — always with hours to spare, never at the last minute.

**Why it matters:** The scorecard is how we *decisively* win the memory track instead of just qualifying. The submissions plumbing is how the work actually reaches the judges — get it wrong and great work scores zero.

**How you know you're done:** the scorecard table shows measured-vs-target-vs-pass for every metric with the independent checker; the repository is public and secret-free; all three tracks are submitted with working links.

**Your first move:** `git checkout build/t3-bench-submissions`, then open the BasedAI submission (guide at `Plan/workflows/T3-github-publication.md`) *and* start the scorecard (`precedent_memory/bench/conformance_bench.py`). Full detail: `Plan/BUILD-PLAN.md` §4 (T3).

---

## N1 — The real stuff and the deck: data, fix-instructions, and the slides

**Who you are, simply:** You make the demo *real* and you make the pitch *look the part*. You have the code and a good AI tool, so you commit your own work — you don't hand it to anyone.

**What you're doing, in order:**

1. **The fix-instructions ("KB articles").** When Precedent looks up a fix, it reads a written instruction (a "runbook"). You write about ten of these, adapted from **real, published procedures** (with a link to the real source in each — never invented). Five come first because the demo needs them: the main "TV guide publish failed" one, two restricted ones (only the rights team can see them — this is what makes the "it refuses" moment work), the famous CrowdStrike outage fix, and one deliberately out-of-date one (so we can show the AI flagging staleness). There's an exact format to follow, and your AI tool can draft these fast — your job is to check the sources and the permission flags and commit them.

2. **The real data.** You pull the real public datasets (a real UK TV schedule, streaming catalogues, the incident log) into the repository so the simulator has real content to work with. Where this touches code (loading the data in), your AI tool does the heavy lifting and a builder gives it a quick look. **Keep the mess** — the missing and duplicate bits are what make it realistic.

3. **The honesty labels.** You write the little "where every piece of data came from and what licence it's under" table, including the honest note that we *deliberately rejected* two data sources because their terms don't allow AI use. (That diligence is itself a point-scorer.)

4. **The slide deck.** You build the pitch deck from a spec that's already written slide-by-slide — you're mostly transcribing it accurately, not designing from scratch. The measured numbers get filled in near the end (from T3's scorecard). One firm rule: **never leave a blank "‹XX›" placeholder** in the final version — fill it with the real number or remove the line.

5. **Saturday:** the "before" time-lapse clip (you perform the slow manual fix once and speed it up 8×), the pitch cheat-sheets, and helping run the rehearsal.

**Why it matters:** "Realistic data" is something the main judge explicitly demands, and the deck is what half the judges see if we're not picked to present live. You own both.

**How you know you're done:** five fix-instructions committed with real source links and correct permission flags; the data table is honest and complete; the deck matches the spec with real numbers and zero blanks.

**Your first move:** `git checkout content/n1-data-deck`, open `data/kb/README.md` and the guide at `Plan/workflows/N1-kb-articles.md`, and write the five critical fix-instructions. Full detail: `Plan/BUILD-PLAN.md` §4 (N1).

---

## N2 — The story out: video, submissions, real-world signal, and quality control

**Who you are, simply:** You own how the work is *presented and submitted* — the video, the submission pages, the real-world credibility signal the investors want, and the final quality check that catches a wrong number before it ships. You commit your own work directly.

**What you're doing, in order:**

1. **Reach out to real people (start this early — it needs time).** The investor judges care whether anyone in the real world would actually use this. You send ten short, friendly messages to people who run 24/7 operations teams, asking one question: *"would the 'it refuses restricted fixes' demo get this past your change board?"* Good replies become a quote on a slide. If nobody replies honestly, **we delete the claim rather than fake it** — that's a firm rule. There's a message template ready.

2. **Set up the submission machinery.** The shared folder for video clips; the main submission page written as a punchy 60-second read (because judges skim); and — carefully — the one-shot answers to the submission form's questions (these *can't be edited after submitting*, so they're written on Friday and a builder signs off the exact wording before submit).

3. **Break the demo on purpose (the playtest).** Before we lock the code, you act like a clueless user: file deliberately awful, typo-ridden problem tickets from your phone and see how the system copes. You grade each one (handled it / safely gave up / got confused). This both hardens our "any judge can try it live" party trick and finds real bugs.

4. **The video (Saturday).** You assemble the ~4½-minute demo video from the real screen-recordings (captured against the frozen code) plus the voiceover. The spine is **real recordings — never faked.** You also cut a 30-second teaser and, if we're not picked to present, a punchy 90-second version to put first on the submission page. There's a shot-by-shot script and exact captions to follow (with strict rules — e.g. always label a measurement honestly).

5. **The final quality pass.** Before anything is submitted, you check every number on screen and in captions against the verified-sources list, sweep for any leftover blank placeholders, and click every submission link while logged out to make sure they actually work for a stranger.

**Why it matters:** The video and submission pages are what the judges actually experience — especially if we're judged online rather than live. And the real-world quote is the one thing that turns "clever hackathon project" into "this could be a company."

**How you know you're done:** ten outreach messages sent (quotes committed, or the claim removed); the video assembled from real footage with honest captions; the submission page reads well and every link works; the one-shot answers signed off before submit.

**Your first move:** `git checkout content/n2-video-submissions`, open `Plan/workflows/N2-practitioner-outreach.md`, and send the ten messages — then set up the submission scaffolding. Full detail: `Plan/BUILD-PLAN.md` §4 (N2).

---

## How it all fits together (one picture)

- **T1** makes problems happen and fixes them (the engine).
- **T2** remembers the fixes safely and shows it all on screen (the memory + the face).
- **T3** proves it with numbers and gets it submitted (the proof + the paperwork).
- **N1** makes it real and puts it on slides (the data + the deck).
- **N2** turns it into a video and a story, and checks nobody lied by accident (the presentation + the conscience).

Everyone's work meets at the same finish line: **the core demo works, it's recorded honestly, and it's submitted to all three tracks with time to spare.** The demo comes first, always.
