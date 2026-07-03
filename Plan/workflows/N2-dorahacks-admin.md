# PACKET — DoraHacks BUIDL Page Admin (draft early, edit later, ONE-SHOT answers)

> **Owner:** N2 · **Runs:** Fri 15:30–17:30 (copy + one-shot answer drafts) · Fri 20:30–21:15 (numbers in, T1 review ~21:00) · Fri 22:00 (selection watch, 5 min, phone) · **Sat 06:30–08:30 → DRAFT SUBMIT 08:30** · Sat 17:00–17:45 → **FINAL SUBMIT ~17:30** (platform deadline 22:59 UTC = 23:59 BST — never plan on the last hour)
> **Budget:** ~2.5 ph (ledger rows: BUIDL page 1.0 + DoraHacks submission/logistics 1.5)
> **Sent to you by:** T3 via WhatsApp/email with ONE attachment: `facts-pack.md` (T3 compiles by Fri 15:00: every link, the stat table with sources, the three tracks' requirement one-liners, contact email). Teaser stills arrive separately from T2 via shared drive (they go straight to DoraHacks, not to Claude).
> **You also need:** the team DoraHacks login — T1 shares it via WhatsApp/password manager Friday afternoon. If sharing is refused, you draft everything and sit with T3 who drives the browser; the packet is otherwise unchanged.
> **Your output goes to:** the live BUIDL page itself + a copy of all final text to T3 (committed to `docs/evidence/`)

---

## 1. Why this exists

~50% of judges will only skim the BUIDL page — no video click, no repo visit. The hackathon (DoraHacks event 2272) already has 18+ BUIDLs. The page must deliver the whole story in a **60-second skim**, tick exactly the right bounties, and survive the platform's one trap: **organizer questions are answered ONCE and can never be edited, while everything else stays editable until the deadline.**

Rules this page obeys (from the team's locked specs):
- **Numbers:** only numbers that appear in the facts-pack stat table, with their source labels. Vendor figures always carry "(vendor-claimed)". **Never ship a ‹XX› placeholder** — before every submit, Ctrl-F the page text for `‹` and for "XX".
- **Degraded rule (pre-ratified):** if Friday-night bench/mutation numbers didn't land, the metrics block ships with ONLY the measured 94.4% / 18.2h / 558-class numbers — missing rows are **removed**, not bracketed.
- Honesty beats ambition everywhere: no "coming soon", no claims the repo can't back.

## 2. Page structure — the 60-second skim (build it in this order, top to bottom)

1. **Hook block (2 lines):**
   > **Precedent — every incident resolved becomes precedent.**
   > The agent that remembers every documented fix your org has applied and re-applies it — approval-gated, audited, auto-rollback. **8 h 51 m → 15 seconds, with a human's approval always in the loop.**
2. **Video** — the 4:15 cut embedded/linked first. **IF the team was NOT selected to present (you learn this at Fri 22:00): the standalone 90-second cut goes FIRST, above the 4:15.**
3. **Teaser strip** — the 6 stills with their 5-word captions (T2 exports from the video master): messy ticket → "Fix found. Rollback written first." → "One human click. 58 seconds." → "Next time: 15 seconds. Pre-approved." → "Failed fix? Auto-rollback. Trust revoked." → "It knows what it can't touch."
4. **Measured-numbers block** (table, each row with its source label from the facts pack): 94.4% fix-class match over 24,918 real incidents · 18.2 h median (calendar) for precedented repeats · 558 recurring classes = 94.8% of volume · arrival-time top-1 59.4% / top-3 87.7% · P99 permission-check ms + FNR/FPR (Friday-night bench) · mutation bench (100 tickets: correct-match / safe-degrade / 0 false fast-paths). Apply the degraded rule if needed.
5. **"For each judge, click this" block — three lines:**
   - **Conduct:** video 0:00–2:00 (before/after + approval loop) · repo README (run instructions) · playtest + provenance in `docs/evidence/`
   - **Fetch.ai:** ASI:One public shared-chat URL — **"jump to turn 6"** for the 15-second standing-approval run · 3 Agentverse profile URLs (Innovation Lab + hackathon badges) · video 1:35–2:55
   - **BasedAI:** the PR into BasedAICo/hackathons · `bench/RESULTS.md` (FNR/FPR/P50/P99 vs published thresholds) · video 2:55–3:20
6. **Repo link + run instructions line + contact email** (the slide-12 contact address — same one as the deck).
7. Below the fold: the longer description (PROMPT 1 output), team block (roles, the Disney+-operations origin line — no invented credentials), provenance paragraph (real public data: UCI ServiceNow log CC BY 4.0, GitLab/K8s runbooks, CrowdStrike bulletin, TVmaze CC BY-SA / XMLTV, CC0 catalogs).

## 3. Bounty ticks — EXACTLY these three, nothing else

When submitting the BUIDL to hackathon **2272**, tick:
- [ ] **1370 — Conduct "Make Legacy Move"**
- [ ] **1367 — Fetch.ai**
- [ ] **1364 — BasedAI**

The platform allows up to 10. **Do not tick any others** — the track strategy is locked; irrelevant ticks dilute the story in front of the judges who matter. If the UI pre-selects anything, deselect it.

## 4. THE ONE-SHOT TRAP — organizer questions (read twice)

DoraHacks BUIDL content stays editable until the deadline, **but the organizer-defined question answers are submitted once and locked**. They lock at the **Sat 08:30 draft submit**. So:

1. **Fri 15:30:** open the submission form (do NOT press submit), copy every organizer question verbatim into a doc. Screenshot the form.
2. **Fri 16:00–17:00:** draft answers with PROMPT 3.
3. **Fri ~21:00:** T1 reviews and signs off every answer (catch T1 at the 21:00 freeze window; WhatsApp the doc by 20:45 with "ONE-SHOT answers — need sign-off tonight").
4. **Sat 08:30:** enter the signed-off answers character-for-character and submit the draft. Never improvise an answer at the form.

## 5. Claude prompts (claude.ai free tier, attach `facts-pack.md` to each chat)

**PROMPT 1 — hook + description:**
```
Attached is our facts pack (links, measured numbers with sources, track requirements). Write, for
a DoraHacks hackathon submission page: (a) 3 alternative one-sentence hook lines (≤16 words) for
"Precedent" — an agent that re-applies an org's own documented fixes, approval-gated, audited,
auto-rollback, permission-aware memory; (b) a 150-word above-the-fold description a skimming VC
or sponsor judge reads in 30 seconds. Hard rules: use ONLY numbers present in the facts pack,
keep each number's source label, never say "autonomous" (the term is "Standing Approval"), no
agent codenames, no jargon (no ACL/YAML/embeddings/P99 outside the metrics table). Plain text.
```

**PROMPT 2 — per-track click blocks:**
```
Using the attached facts pack, write three 2-line "what to look at" blocks addressed to the
Conduct, Fetch.ai, and BasedAI judges respectively. Each names its links (video timestamp, repo
path, chat URL "jump to turn 6", PR link, bench file) exactly as given in the facts pack. Skimmable,
no marketing filler, ≤35 words per block.
```

**PROMPT 3 — one-shot organizer answers:**
```
Attached is our facts pack. Below are the organizer questions from the DoraHacks submission form,
copied verbatim. Draft an answer to each, ≤100 words, factual, first person plural. Hard rules:
every claim must be traceable to the facts pack — if you cannot support a claim from it, write
[NEEDS-FACT: what's missing] instead of inventing; never say "autonomous"; label vendor-claimed
figures. These answers are submitted once and can never be edited, so flag anything you are
uncertain about at the end.
QUESTIONS: [paste]
```
Resolve every `[NEEDS-FACT]` with T3 before the T1 review — never delete the flag silently.

## 6. Fri 22:00 — selection watch (5 min, from your phone; agreed as outside-shift)

Watch Discord/email for the Demo-Day presenter announcement (~22:00). Post the result in the team thread immediately (**T1 owns the branch decision**). Consequence for you: **NOT selected → Sat morning the 90-second cut goes first on the page** (T2 cuts it; you place it before the 08:30 draft submit if it's ready, else at the 17:30 final pass).

## 7. Pre-submit checklist (run at BOTH submits — Sat 08:30 and Sat 17:30)

- [ ] Ctrl-F page text: no `‹`, no "XX", no "TODO", no "TBD"
- [ ] Every number matches the facts-pack stat table; degraded rule applied if bench rows are missing
- [ ] All links opened in an **incognito window**: repo is public and README renders · video plays (unlisted is fine) · ASI:One shared-chat URL loads logged-out · 3 Agentverse profiles load, badges visible · BasedAI PR link loads · bench/RESULTS.md path correct
- [ ] Exactly 3 bounties ticked (1370 / 1367 / 1364)
- [ ] 08:30 only: one-shot answers = the T1-signed doc, verbatim
- [ ] Screenshot the submitted state; post to team thread

## 8. DONE when

- [ ] Draft BUIDL live by Sat 08:30 with one-shot answers locked, checklist passed
- [ ] Final submit done ~17:30 Sat, checklist passed again, screenshots posted
- [ ] Full final page text + the one-shot answers doc sent to T3 (committed to `docs/evidence/dorahacks-buidl.md`)

## 9. If it goes wrong

- **A link fails incognito at 08:15 Sat:** submit the draft anyway WITHOUT that link (a missing link is editable later; a broken one looks worse), flag T3/T2 in the thread, add it at the next edit.
- **Video not uploaded by 08:30:** draft-submit with the teaser stills + "video: see repo README" and add the URL the moment it exists (editable). The one-shot answers must never reference the video for this reason.
- **T1 unreachable Friday night for sign-off:** T1 review moves to Sat 06:30–07:30 (T1 is on shift). The answers do NOT go in unreviewed — if 08:15 arrives with no sign-off, submit the draft with answers T1 signed and hold ONLY the unsigned ones… if the form forces all answers, escalate: a 2-minute phone call to T1 beats an unreviewed one-shot answer.
- **Platform hiccup near 17:30 final:** you have until 23:59 BST, and Sat 17:00–19:00 is your shift — retry at 18:30; if still failing, T3 takes over from their machine. Nothing waits past 19:00.
