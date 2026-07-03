# PACKET — Practitioner Outreach (the VC judge's "what has an actual buyer said?" fix)

> **Owner:** N2 · **Phase:** start once the pitch is stable enough to describe in one paragraph (§2 below is already frozen — you don't need to wait for the build). Send early so replies have time to land; reply-monitoring runs through the build; **hard cutoff = before the freeze.**
> **Budget:** ~2.0 person-hours (this is the ledger's "Practitioner outreach (or delete the line)" row — treat 2.0 ph as a hard cap; this is a human task, not a build task).
> **You own this end-to-end:** you build the contact list, send, monitor, log, and commit the names-free log yourself. Quotes route to N1 (deck owner) for slide 12 / A9. Nobody bundles or relays for you.
> **You need:** your phone/laptop with LinkedIn, this packet, your AI tool, and ~10 minutes of the Disney+-alum teammate's time to broker warm intros.

---

## 1. Why this exists (read once, it sets the rules)

The VC judge's round-1 fatal was "the empty team slide + zero customer evidence." Two artifacts in the deck exist ONLY if this packet lands:

- **Slide 12** validation line: *"We put this in front of ‹N› ops engineers this week; every one of them said the refusal demo is what gets it past their CISO."*
- **Appendix A9** (bottoms-up ACV slide): consented practitioner quotes live there too.

**The honesty rule (locked in the pitch-deck brief): the line is spoken only if literally true. If no consented quotes land by the freeze, the line and the A9 quote row get DELETED — cleanly, no soft version, no "we're talking to people."** Reporting "zero quotes, delete the line" is a *successful* outcome of this packet. The Conduct rubric and demo honesty win every conflict with ambition.

Corollaries:
- Quotes are **verbatim** — never paraphrased into something stronger.
- "Every one of them said X" is only usable if **every respondent** said it. Otherwise the softer true form: *"N of M ops engineers told us ‹verbatim thing›."*
- Attribution is **role + company type only** ("playout NOC shift lead, broadcast MSP") — never a name, never a company name, unless they explicitly volunteer it in writing.
- **This packet contains no real names and you never write real names into anything you commit.** You build the contact list yourself; the log uses slot numbers.

## 2. What you're selling in one paragraph (memorise, don't improvise)

Precedent is an agent that remembers every documented fix an ops org has ever applied and re-applies it: approval-gated, fully audited, rollback written *before* execution — and it **refuses** to touch anything its identity isn't permitted to read (in the demo, a rights-restricted runbook: it refuses and routes to the right team). First fix ~60 seconds with a human click; pre-approved repeats ~15 seconds.

## 3. Target list — 10 sends, built in this priority order (~45 min)

| Tier | Who | How many | How |
|---|---|---|---|
| 1 — WARM | Ex-colleagues from the Disney+-alum teammate's network (ops/tooling/on-call people they actually know) | 3–5 | The teammate nominates them AND sends the DM **from their own LinkedIn account** (you draft it, they paste — ~10 min of their time; ask them directly or grab them in the team channel to broker). Warm sends answer 5–10× more often. |
| 2 — COLD, broadcast | Broadcast/playout/master-control/NOC practitioners. LinkedIn people-search: `"playout" OR "master control" OR "broadcast operations" OR "transmission controller" OR "NOC engineer"` filtered to Red Bee Media, Encompass Digital Media, Globecast, Amagi, Sky, ITV, Channel 4 | 3–4 | From your own account. If not connected, use the 280-char connect-note variant below. |
| 3 — COLD, MSP/ITSM | Service-desk managers, incident managers, NOC shift leads at IT MSPs | 2–3 | Same mechanics. |

Rules: practitioners not executives (shift leads, engineers, incident managers — people who file/approve changes); UK/EU timezone (same-day replies are realistic if you send early in the day); stop at 10 sends; max ONE follow-up, warm contacts only.

## 4. The message

### 4.1 The 60-word DM template (for existing connections / InMail / email)

> Hi ‹first name› — ‹one-line connection: "we overlapped at ‹place›" / "‹teammate› suggested you›"›. Two of us are demoing **Precedent** at Imperial tomorrow: an agent that re-applies your org's own documented fixes — approval-gated, audited, auto-rollback — and **refuses** anything its identity isn't permitted to read. One question from someone who's lived the on-call queue: **would that refusal demo get this past your change board?**

### 4.2 The 280-character connect-note variant (LinkedIn caps connection notes)

> Hi ‹name› — building Precedent: an agent that re-applies your org's documented fixes, approval-gated + audited, and refuses what it can't read. Demoing to VCs Sat. One question: would the refusal demo get past your change board? 30 sec, brutal honesty welcome.

### 4.3 The ONE question (never add a second)

**"Would the refusal demo get this past your change board?"** — it's answerable in one line, and any answer converts directly into the quote slot the deck needs. Do not ask about pricing, pilots, or "feedback generally."

### 4.4 The quote-consent line (send the moment a usable reply arrives)

> That's gold — may we quote that sentence on one slide at a demo day tomorrow, attributed only as "‹their job role›, ‹type of company›" — no name, no company name? Say no and it stays between us.

No reply to the consent ask = **no consent** = the quote is unusable. Screenshot every consent.

## 5. Driving your AI tool — personalise the 10 DMs

Fill in the contact notes (role, org type, warm/cold, one context line — **still no real names**; use "Contact 1..10"), then point your AI tool at §4.1 and drive it with something like the scaffold below. You have a capable model, so adapt freely — the only non-negotiables are the two guardrails (don't invent contact facts, don't soften the question).

```
You are helping personalise cold/warm outreach DMs. Below is a fixed 60-word template and notes
on up to 10 contacts. For each contact, produce: (a) a personalised DM of AT MOST 60 words that
keeps the product description and the final question EXACTLY as written in the template, changing
only the greeting and the one-line connection; (b) a variant of at most 280 characters for a
LinkedIn connection note. Do not invent facts about the contact. Do not soften or change the
question "would that refusal demo get this past your change board?". Output as a numbered list,
plain text, ready to paste.

TEMPLATE:
[paste §4.1]

CONTACTS:
Contact 1 — role: … · org type: … · warm/cold: … · connection line: …
Contact 2 — …
```

Make the tool **verify** every output against two rules before you send: (1) the product sentence and the change-board question are byte-for-byte the template — no softening, no rewording; (2) nothing invented about the contact beyond the note you supplied. If either fails, regenerate that one.

## 6. Log everything in this table (this is what you commit — names-free)

Keep it as `docs/evidence/practitioner-outreach.md` on your branch and commit it directly.

| Slot | Tier (warm/cold) | Role + org type | Channel | Sent | Replied? | Reply (verbatim) | Consent? (screenshot) | Attribution string |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | |

## 7. DONE when

- [ ] 10 sends logged (or fewer + a one-line reason, e.g. LinkedIn rate-limited)
- [ ] Every reply captured verbatim; every usable reply got the consent ask
- [ ] Each consented quote lands with N1 (deck owner) **the moment it arrives**: verbatim quote + attribution string + consent screenshot, for slide 12 + A9
- [ ] Names-free log committed to `docs/evidence/practitioner-outreach.md` (your branch → merge/PR per team convention)
- [ ] **Before the freeze, post the final count to the team channel in one of exactly two forms:**
  - "OUTREACH: ‹N› consented quotes committed — final count for slide 12 is ‹N› of ‹M› asked; ‹all/N› said ‹the thing›." — or
  - "OUTREACH: no consented quotes — **N1 delete the slide-12 validation line and the A9 quote row.**"

## 8. Where the output goes

Consented quotes → N1 places them on slide 12 + A9. Your names-free log → committed by you to `docs/evidence/practitioner-outreach.md`. The deck's PDF export and the Saturday DoraHacks draft both read from whatever is committed and posted **by the freeze** — nothing after that counts toward the honesty-checked line.

## 9. If it goes wrong

- **LinkedIn throttles connect requests:** stop sending cold; switch remaining sends to email if you can find addresses, or hand the slots to the teammate's warm channel.
- **Nobody replies:** one follow-up to warm contacts only ("no worries if not — even a one-word answer helps us tomorrow"). Then stop. Do not widen the list past 10; do not post publicly.
- **Someone replies negatively** ("no, our change board would never allow an agent"): that is still a logged, valuable answer — flag it NEGATIVE in the log and pass it to whoever owns Q&A prep. It feeds Q&A, never a slide.
- **Any doubt about whether a quote is usable:** it isn't. Default to deletion; the honesty rule outranks the line.
