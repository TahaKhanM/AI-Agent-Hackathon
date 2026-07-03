# PACKET — Practitioner Outreach (the VC judge's "what has an actual buyer said?" fix)

> **Owner:** N2 · **Runs:** Fri 3 Jul 13:30–15:30 (build list + send), reply-monitoring until 21:30, final cutoff **Sat 07:30**
> **Budget:** 2.0 person-hours (this is the ledger's "Practitioner outreach (or delete the line)" row — 2.0 ph, hard cap)
> **Sent to you by:** T3 via WhatsApp (this file only — no attachments needed; everything is inline)
> **Your output goes to:** T3, who routes quotes to the deck owner and commits the log to `docs/evidence/`
> **You need:** your phone/laptop with LinkedIn, this packet, claude.ai (free tier is fine), and 10 minutes of the Disney+-alum teammate's time around 14:00

---

## 1. Why this exists (read once, it sets the rules)

The VC judge's round-1 fatal was "the empty team slide + zero customer evidence." Two artifacts in the deck exist ONLY if this packet lands:

- **Slide 12** validation line: *"We put this in front of ‹N› ops engineers this week; every one of them said the refusal demo is what gets it past their CISO."*
- **Appendix A9** (bottoms-up ACV slide): consented practitioner quotes live there too.

**The honesty rule (locked in 03-pitch-deck): the line is spoken only if literally true. If no consented quotes land by Sat 07:30, the line and the A9 quote row get DELETED — cleanly, no soft version, no "we're talking to people."** Reporting "zero quotes, delete the line" is a *successful* outcome of this packet. The Conduct rubric and demo honesty win every conflict with ambition.

Corollaries:
- Quotes are **verbatim** — never paraphrased into something stronger.
- "Every one of them said X" is only usable if **every respondent** said it. Otherwise the softer true form: *"N of M ops engineers told us ‹verbatim thing›."*
- Attribution is **role + company type only** ("playout NOC shift lead, broadcast MSP") — never a name, never a company name, unless they explicitly volunteer it in writing.
- **This packet contains no real names and you never write real names into anything you hand back.** You build the contact list yourself; the log uses slot numbers.

## 2. What you're selling in one paragraph (memorise, don't improvise)

Precedent is an agent that remembers every documented fix an ops org has ever applied and re-applies it: approval-gated, fully audited, rollback written *before* execution — and it **refuses** to touch anything its identity isn't permitted to read (in the demo, a rights-restricted runbook: it refuses and routes to the right team). First fix ~60 seconds with a human click; pre-approved repeats ~15 seconds.

## 3. Target list — 10 sends, built in this priority order (~45 min)

| Tier | Who | How many | How |
|---|---|---|---|
| 1 — WARM | Ex-colleagues from the Disney+-alum teammate's network (ops/tooling/on-call people they actually know) | 3–5 | The teammate nominates them AND sends the DM **from their own LinkedIn account** (you draft it, they paste — 10 min of their time at ~14:00; ask T3 to broker). Warm sends answer 5–10× more often. |
| 2 — COLD, broadcast | Broadcast/playout/master-control/NOC practitioners. LinkedIn people-search: `"playout" OR "master control" OR "broadcast operations" OR "transmission controller" OR "NOC engineer"` filtered to Red Bee Media, Encompass Digital Media, Globecast, Amagi, Sky, ITV, Channel 4 | 3–4 | From your own account. If not connected, use the 280-char connect-note variant below. |
| 3 — COLD, MSP/ITSM | Service-desk managers, incident managers, NOC shift leads at IT MSPs | 2–3 | Same mechanics. |

Rules: practitioners not executives (shift leads, engineers, incident managers — people who file/approve changes); UK/EU timezone (it's Friday afternoon — same-day replies are realistic); stop at 10 sends; max ONE follow-up, warm contacts only, ~19:30.

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

## 5. Claude prompt — personalise the 10 DMs (one paste, claude.ai free tier)

Fill in the contact notes (role, org type, warm/cold, one context line — **still no real names**; use "Contact 1..10"), then paste:

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

If the free-tier reply cuts off, re-run with 5 contacts per paste.

## 6. Log everything in this table (keep it in your Notes app; this is your hand-back)

| Slot | Tier (warm/cold) | Role + org type | Channel | Sent | Replied? | Reply (verbatim) | Consent? (screenshot) | Attribution string |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | |

## 7. DONE when

- [ ] 10 sends logged (or fewer + a one-line reason, e.g. LinkedIn rate-limited)
- [ ] Every reply captured verbatim; every usable reply got the consent ask
- [ ] Each consented quote forwarded to T3 **the moment it lands** (WhatsApp): verbatim quote + attribution string + consent screenshot
- [ ] **Sat 07:30 cutoff message sent to T3, one of exactly two forms:**
  - "OUTREACH: ‹N› consented quotes attached — final count for slide 12 is ‹N› of ‹M› asked; ‹all/N› said ‹the thing›." — or
  - "OUTREACH: no consented quotes — **delete the slide-12 validation line and the A9 quote row.**"

## 8. Hand-back path

You → T3 (WhatsApp) → T3 pastes quotes to the deck owner (slide 12 + A9 placeholders) and commits your log table (names-free) to `docs/evidence/practitioner-outreach.md`. The deck's PDF export and the Sat 08:30 DoraHacks draft both read from what T3 has by **Sat 07:30** — nothing after that counts.

## 9. If it goes wrong

- **LinkedIn throttles connect requests:** stop sending cold; switch remaining sends to email if you can find addresses, or hand the slots to the teammate's warm channel.
- **Nobody replies by 20:00 Fri:** one follow-up to warm contacts only ("no worries if not — even a one-word answer helps us tomorrow"). Then stop. Do not widen the list past 10; do not post publicly.
- **Someone replies negatively** ("no, our change board would never allow an agent"): that is still a logged, valuable answer — forward it to T3 flagged NEGATIVE. It feeds Q&A prep, never a slide.
- **Any doubt about whether a quote is usable:** it isn't. Default to deletion; the honesty rule outranks the line.
