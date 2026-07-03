# Precedent, explained simply — the idea and the plan

*Plain-English version for the whole team. No jargon. If you want the deep detail, everything here points to a fuller document.*

---

## Part 1 — The idea

### The problem (a story)

Something breaks at a big company — the TV guide shows the wrong programmes, a show goes out in a country it isn't licensed for, an app won't let people log in. Here's the thing almost nobody outside these teams realises: **the fix is usually not new code.** It's a known, boring admin change that someone already wrote down in a manual somewhere. Flip a setting. Re-publish a file. Clear a queue.

So why does it take **nearly 9 hours on average** to fix? Because a human has to: notice the problem, dig through a pile of documents to find the right fix, wait for someone to approve it, log into some clunky old admin screen, do it, and then type up notes that nobody will ever find again. The *fixing* takes minutes. The *finding, waiting, and clicking* takes hours.

We measured this on **24,918 real past incidents** (a public dataset). **94% of them had already been solved before** — the exact same kind of problem, with a known fix sitting in the history. And even those "we've seen this before" cases still took a median of **18 hours** to sort out by hand. The knowledge existed. Nobody could act on it fast.

### What Precedent is

**Precedent is an AI assistant that remembers every fix a company has ever applied, and applies it again — safely.**

When a problem comes in, Precedent:
1. **Notices** it.
2. **Finds** the documented fix from the company's own knowledge (not a guess — the actual runbook or a past solved case).
3. **Checks the risk** using fixed rules (not the AI's opinion — more on this below).
4. **Asks a human** to approve (unless it's already been pre-approved — see "the second time is free").
5. **Does the fix** through safe, pre-defined actions.
6. **Checks it worked** — and if it didn't, **automatically undoes it**.
7. **Remembers** what happened, with a full record.

The one-line pitch: *"AI coding assistants fix broken code. But in real companies, the fix is almost never code — it's a documented admin change. Precedent is the thing that remembers it and does it again, with a human's approval, a full paper trail, and an undo button."*

### The three ideas that make it click

- **"The second time is free."** The first time a problem type appears, a human approves the fix (one click). After the system has watched that fix succeed a few times, the operations lead can press **"Promote to standing approval"** — meaning "next time this exact thing happens, just do it." From then on, that fix happens in ~15 seconds with nobody at the keyboard. The approval didn't disappear — *it moved earlier in time*. A human still granted it, and there's always a visible **"Revoke"** button to take it back.

- **"It knows what it's not allowed to touch."** Some fixes are restricted — only certain teams are allowed to see or use them. Precedent respects those permissions exactly. If it finds a fix it isn't allowed to read, it **refuses** and passes the problem to the team that is allowed, instead of peeking or guessing. That refusal is the thing that gets an AI past a company's security officer.

- **The safety net is the product.** A human approves. Every action is recorded (who, what, when, why — the kind of record auditors want). An undo is written *before* anything runs. Nothing risky happens autonomously. Companies don't buy "a clever AI" — they buy "a clever AI I can trust and control."

### Why it can win

Loads of AI startups are chasing this space, but almost all of them stop at *"here's what's probably wrong"* and they focus on **engineering** problems (code, servers). Nobody combines: (1) using the company's *own documented fixes*, (2) actually *doing* the admin fix in business systems, (3) approval + audit + undo as the core, and (4) a memory that gets more valuable every time it's used. That combination is the gap. Media/broadcast is our starting example because it's full of exactly this kind of pain (24/7 deadlines, regulators, old systems) — but the idea works for any team drowning in runbooks.

---

## Part 2 — The three competitions (tracks) we're entering

One project, three prizes, judged three ways:

| Track | What they care about | Our angle |
|---|---|---|
| **Conduct** (£8,000 — our main prize) | A real, slow company process made dramatically faster, *with the human in control*. A clear before/after a non-engineer gets in 90 seconds. | The whole demo. This is the one we're optimising for. |
| **Fetch.ai** | The agents must live on their network ("Agentverse"), talk in their chat system, and be usable inside their chat assistant ("ASI:One") with no custom app. | Our agents run on their rails; you can resolve an incident just by chatting. |
| **BasedAI** | A permission-aware memory that never leaks across teams, enforces access without the AI deciding, keeps audit logs, stays fast, and uses only open (non-secret) AI models. | Our memory layer does exactly this — and we prove it with their own scorecard, against a live permissions source a copycat can't match. |

### The honesty rules (non-negotiable, on every track)

- **Only open AI models** in the product (a hard requirement for one track — using a closed model like GPT or Claude in the running product would disqualify us). Verified and locked.
- **The AI never makes a permission or risk decision** — fixed rules and a human do. The AI only suggests.
- **Every number we show traces to a verified source**, with honest labels. No made-up stats.
- **The demo data is real public data** (real schedules, real incident logs), flowing through simulated company systems. We never present invented data as real.
- **No secrets ever committed** to the public code.

---

## Part 3 — The plan, explained simply

### The situation

It's **Friday**. Everything must be submitted by **Saturday night**. There are **five of us**, everyone has access to the code and good AI coding tools. The design is done and heavily stress-tested; **now we build it.**

### How we work: gates, not a clock

We don't run to a minute-by-minute schedule. We run toward a small number of **checkpoints ("gates")** in a fixed order. Think of them like levels you have to clear:

1. **Kickoff** — everyone agrees who's doing what, submits the Demo Day sign-up form, and starts.
2. **The vertical slice** — *the most important moment.* This is when the core demo works end-to-end on real data: a problem comes in, gets fixed with one approval, the same problem recurs and gets fixed instantly, and a failed fix gets automatically undone. **Until this works, nothing else matters. Everything bends toward it.**
3. **Harden + get ambitious** — once the core works, we make it more robust *and* add the impressive extras (the memory scorecard that beats the competition, a self-running demo, etc.).
4. **Freeze + record** — we stop changing the code and record the demo video against the frozen version.
5. **Saturday** — finish the video, finalise the submission for each track, rehearse the pitch, and submit with hours to spare.

### The one rule that settles every argument

**The demo comes first.** If we ever have to choose between an impressive extra and getting the core demo solid, the core demo wins — every time. The extras are a bonus layered on top of a protected core, never a replacement for it. There's even a written "cut order" so if time runs short, we know exactly what to drop (the fancy extras first) and what we *never* drop (the core two incidents, the requirements that keep us eligible).

### What could go wrong (and what we do about it)

- **The demo breaks live** → we have a recorded backup of the real thing, and a rehearsal check the morning of that decides live-vs-recorded by a fixed rule.
- **The internet/venue Wi-Fi dies** → the demo is built to run offline; it's been designed to pass with Wi-Fi off.
- **We don't get picked to present** (announced Friday night) → judging still happens online, so we redirect our energy to making the submission page and video excellent.
- **We run out of time** → the cut order tells us what to drop; the core is always protected.

### The things only humans can do (not the code — us)

- Submit the **Demo Day form by 6pm Friday**.
- A couple of us reach out to real industry people for a quote ("would this get past your change board?") — the investors judging care about real signal.
- Write our own team slide honestly (who we are, what we'll do after Saturday).
- Open the one track's submission on GitHub.

### Where to go next

- **To start building:** `GETTING-STARTED.md` (setup + your first task).
- **What each person does, in plain words:** `EXPLAINER-roles.md`.
- **The full plan:** `Plan/BUILD-PLAN.md`.
- **The full idea:** `Idea/Idea-Development.md`.
