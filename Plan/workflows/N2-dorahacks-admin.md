# PACKET — DoraHacks BUIDL Page Admin (draft early, edit later, ONE-SHOT answers)

> **Owner:** N2 · **Commits your own work directly** (docs branch/worktree → merge/PR per team convention). You have repo access and a capable AI coding tool — use it to draft, and paste finished copy into the live BUIDL page yourself.
> **Phase:** draft the page + one-shot answers during the **harden+ambition** phase, once the vertical slice exists and T3's bench numbers have landed (or the degraded rule is confirmed). **Draft-submit before the freeze.** Final edit pass on Saturday assemble. The platform deadline is 22:59 UTC (23:59 BST) — never plan on the last hour.
> **Inputs you work from (in the repo):**
> - `docs/evidence/` — measured numbers with source labels, provenance paragraph, playtest results.
> - `bench/RESULTS.md` — FNR/FPR/P50/P99 vs published thresholds (T3 lands these).
> - The three tracks' requirement one-liners and contact email (deck slide 12 — same address).
> - Video master + the 6 teaser stills with captions (T2's lane; they go straight to DoraHacks, not through any relay).
> **You also need:** the team DoraHacks login for event **2272** — grab it from the team's shared password manager / thread. If login can't be shared, draft everything and pair with whoever holds it to drive the browser; the packet is otherwise unchanged.
> **Your output:** the live BUIDL page itself + the final page text and one-shot answers committed to `docs/evidence/dorahacks-buidl.md`.

---

## 1. Why this exists

~50% of judges will only skim the BUIDL page — no video click, no repo visit. The hackathon (DoraHacks event 2272) already has 18+ BUIDLs. The page must deliver the whole story in a **60-second skim**, tick exactly the right bounties, and survive the platform's one trap: **organizer questions are answered ONCE and can never be edited, while everything else stays editable until the deadline.**

Rules this page obeys (from the team's locked specs):
- **Numbers:** only numbers that appear in the `docs/evidence/` stat table, with their source labels. Vendor figures always carry "(vendor-claimed)". **Never ship a ‹XX› placeholder** — before every submit, Ctrl-F the page text for `‹` and for "XX".
- **Degraded rule (pre-ratified):** if bench/mutation numbers didn't land in time, the metrics block ships with ONLY the measured 94.4% / 18.2h / 558-class numbers — missing rows are **removed**, not bracketed.
- **Caption discipline:** describe what the system actually is (a "25k-record store" of real incidents), never inflate. TMDB was rejected as a source — do not cite it.
- Honesty beats ambition everywhere: no "coming soon", no claims the repo can't back.

## 2. Page structure — the 60-second skim (build it in this order, top to bottom)

1. **Hook block (2 lines):**
   > **Precedent — every incident resolved becomes precedent.**
   > The agent that remembers every documented fix your org has applied and re-applies it — approval-gated, audited, auto-rollback. **8 h 51 m → 15 seconds, with a human's approval always in the loop.**
2. **Video** — the 4:15 cut embedded/linked first. **IF the team was NOT selected to present (see §6): the standalone 90-second cut goes FIRST, above the 4:15.**
3. **Teaser strip** — the 6 stills with their 5-word captions (T2 exports from the video master): messy ticket → "Fix found. Rollback written first." → "One human click. 58 seconds." → "Next time: 15 seconds. Pre-approved." → "Failed fix? Auto-rollback. Trust revoked." → "It knows what it can't touch."
4. **Measured-numbers block** (table, each row with its source label from `docs/evidence/`): 94.4% fix-class match over 24,918 real incidents · 18.2 h median (calendar) for precedented repeats · 558 recurring classes = 94.8% of volume · arrival-time top-1 59.4% / top-3 87.7% · P99 permission-check ms + FNR/FPR (from `bench/RESULTS.md`) · mutation bench (100 tickets: correct-match / safe-degrade / 0 false fast-paths). Apply the degraded rule if any row is missing.
5. **"For each judge, click this" block — three lines:**
   - **Conduct:** video 0:00–2:00 (before/after + approval loop) · repo README (run instructions) · playtest + provenance in `docs/evidence/`
   - **Fetch.ai:** ASI:One public shared-chat URL — **"jump to turn 6"** for the 15-second standing-approval run · 3 Agentverse profile URLs (Innovation Lab + hackathon badges) · video 1:35–2:55
   - **BasedAI:** the PR into BasedAICo/hackathons · `bench/RESULTS.md` (FNR/FPR/P50/P99 vs published thresholds) · video 2:55–3:20
6. **Repo link + run instructions line + contact email** (the slide-12 contact address — same one as the deck).
7. Below the fold: the longer description (see §5 draft note), team block (roles, the Disney+-operations origin line — no invented credentials), provenance paragraph (real public data: UCI ServiceNow log CC BY 4.0, GitLab/K8s runbooks, CrowdStrike bulletin, TVmaze CC BY-SA / XMLTV, CC0 catalogs).

## 3. Bounty ticks — EXACTLY these three, nothing else

When submitting the BUIDL to hackathon **2272**, tick:
- [ ] **1370 — Conduct "Make Legacy Move"**
- [ ] **1367 — Fetch.ai**
- [ ] **1364 — BasedAI**

The platform allows up to 10. **Do not tick any others** — the track strategy is locked; irrelevant ticks dilute the story in front of the judges who matter. If the UI pre-selects anything, deselect it.

## 4. THE ONE-SHOT TRAP — organizer questions (read twice)

DoraHacks BUIDL content stays editable until the deadline, **but the organizer-defined question answers are submitted once and locked**. They lock at the **draft submit** (which you do before the freeze). So:

1. **Open the submission form** (do NOT press submit): copy every organizer question verbatim into a doc under `docs/evidence/`. Screenshot the form.
2. **Draft answers** (see §5) while the vertical slice is live and numbers are settled.
3. **Get T1 sign-off on every answer** before the freeze — a builder freezes the text. Post the doc in the team thread flagged "ONE-SHOT answers — need sign-off before freeze"; nothing goes in unreviewed.
4. **At draft submit:** enter the signed-off answers character-for-character and submit the draft. Never improvise an answer at the form.

## 5. Driving your AI tool (draft in the repo, verify against the evidence)

Point your AI tool at `docs/evidence/` (the stat table + provenance), `bench/RESULTS.md`, and the track requirement one-liners, and have it draft the copy below. It's a capable model — you don't need a locked script; steer it and then **verify every number and link yourself against the source files** before anything goes live. Have it flag, never invent: any claim it can't trace to the evidence should come back as `[NEEDS-FACT: what's missing]` for you to resolve, not filled in.

**Draft A — hook + description.** Ask for: (a) 3 alternative one-sentence hook lines (≤16 words) for "Precedent" — an agent that re-applies an org's own documented fixes, approval-gated, audited, auto-rollback, permission-aware memory; (b) a 150-word above-the-fold description a skimming VC or sponsor judge reads in 30 seconds. Hard rules to give it: use ONLY numbers present in `docs/evidence/`, keep each number's source label, never say "autonomous" (the term is "Standing Approval"), no agent codenames, no jargon (no ACL/YAML/embeddings/P99 outside the metrics table). Plain text.

**Draft B — per-track click blocks.** Three 2-line "what to look at" blocks addressed to the Conduct, Fetch.ai, and BasedAI judges respectively. Each names its links (video timestamp, repo path, chat URL "jump to turn 6", PR link, bench file) exactly as they appear in the repo. Skimmable, no marketing filler, ≤35 words per block. **Verify each link opens** (see §7).

**Draft C — one-shot organizer answers.** Feed it the organizer questions copied verbatim from the form. One answer each, ≤100 words, factual, first person plural. Hard rules to give it: every claim must be traceable to `docs/evidence/` — if it can't support a claim, it writes `[NEEDS-FACT: what's missing]` instead of inventing; never "autonomous"; label vendor-claimed figures; flag anything uncertain at the end. **Resolve every `[NEEDS-FACT]` with T3 before the T1 review — never delete the flag silently.** These answers are submitted once and can never be edited.

## 6. Selection watch — presenter announcement

Watch for the Demo-Day presenter announcement (Discord/email). Post the result in the team thread immediately (**T1 owns the branch decision**). Consequence for this page: **NOT selected → the 90-second cut goes FIRST on the page** (T2 cuts it; you place it before the draft submit if it's ready, else at the Saturday final pass).

## 7. Pre-submit checklist (run at BOTH submits — draft submit and Saturday final)

- [ ] Ctrl-F page text: no `‹`, no "XX", no "TODO", no "TBD"
- [ ] Every number matches the `docs/evidence/` stat table; degraded rule applied if bench rows are missing
- [ ] All links opened in an **incognito window**: repo is public and README renders · video plays (unlisted is fine) · ASI:One shared-chat URL loads logged-out · 3 Agentverse profiles load, badges visible · BasedAI PR link loads · `bench/RESULTS.md` path correct
- [ ] Exactly 3 bounties ticked (1370 / 1367 / 1364)
- [ ] Draft submit only: one-shot answers = the T1-signed doc, verbatim
- [ ] No secrets anywhere on the page or in the committed copy (no tokens, keys, private URLs)
- [ ] Screenshot the submitted state; post to team thread

## 8. §5 ambition hook — temporal-embargo media beat

If T2 lands the **temporal-embargo** ambition beat (memory that refuses to re-apply a fix until its embargo window clears), it earns a line in the description and a teaser-strip caption ("It waits when it must") — **only if the repo actually demonstrates it.** Same honesty rule as everything else: if the beat didn't ship, the line doesn't exist. Don't pre-write it.

## 9. DONE when

- [ ] Draft BUIDL live before the freeze, with one-shot answers locked (T1-signed) and the checklist passed
- [ ] Final submit done on Saturday assemble, checklist passed again, screenshots posted
- [ ] Full final page text + the one-shot answers doc committed to `docs/evidence/dorahacks-buidl.md`

## 10. If it goes wrong

- **A link fails incognito at draft submit:** submit the draft WITHOUT that link (a missing link is editable later; a broken one looks worse), flag T3/T2 in the thread, add it at the next edit.
- **Video not uploaded by draft submit:** draft-submit with the teaser stills + "video: see repo README" and add the URL the moment it exists (editable). The one-shot answers must never reference the video for this reason.
- **T1 unreachable for sign-off before the freeze:** the answers do NOT go in unreviewed. Submit the draft with the answers T1 has signed and hold ONLY the unsigned ones; if the form forces all answers, escalate — a 2-minute call to T1 beats an unreviewed one-shot answer.
- **Platform hiccup near the final submit:** you have until 23:59 BST — retry; if it's still failing, T3 takes over from their machine. Don't let it slip into the last hour.
