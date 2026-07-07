# Precedent — finish runbook (exact steps to submission)

## STATUS (updated 2026-07-04 — automatable work done)

**✅ Done automatically (evidence: `docs/evidence/LIVE-PROOFS.md`):**
- Live Jira wiring: MEDIA-2 (kb:KB-0004) + MEDIA-3 (kb:KB-0005) created, security "Rights Ops Only";
  `JIRA_RUNBOOK_ISSUES` set in `.env`; smoke sees 2 sources.
- `make live-drift`: TTC 0.24 s median, 0.000% stale-allow.
- `make bench-uci`: 24,918-record store, FNR 0/7,529, FPR 0/2,471, P99 0.590 µs.
- Venice live `/models` open-weight guard + FAST chat round-trip.
- Agentverse: 3 profile URLs captured (registered · active) and filled into deck A7 / FETCH-DELIVERABLES
  / DoraHacks worksheet; PR-README + final-numbers updated with the UCI numbers; deck PDFs rebuilt.
- Secrets scrub A–E: gitleaks clean; no API key/token/seed in history.

**✅ Also done since:** ASI:One shared-chat URL captured + filled everywhere
(`https://asi1.ai/invite?channelInviteKey=NmIsH5-DHQVhnf78uThoWX3fVkRXiSpGz78rMsPkoUQ`); Agentverse
credit code redeemed; **BasedAI fork PR submitted**; practitioner outreach **not being done** →
slide-12 validation line stays deleted (never faked).

**⏳ Manual-only remaining (accounts / web forms):**
1. **Origin push** — `git push --follow-tags origin main` (publish act; auto-sync handles main, the tag needs this).
2. **DoraHacks BUIDL** (Step 7) — event 2272, bounties 1370/1367/1364; paste me the organizer questions for exact answers + T1 sign-off.
3. **Video capture** (Step 8) + fill `[[WAIT:VIDEO-LINK]]`.
4. **BasedAI mentor deadline** — ask the mentor → I fill `[[WAIT:MENTOR-ANSWER]]` (or edit the already-open PR).
5. **~22:00 selection-branch call** (Step 9).
6. *(optional)* remove `precedent-scheduling-ops` from the "Rights Ops Only" level for a textbook-clean refusal.

**I can still do for you on request:** fill `[[WAIT:MENTOR-ANSWER]]` / `[[WAIT:VIDEO-LINK]]` once you
have them; remove role 10008 from the level.

---

Everything buildable is done + committed (Checkpoint 2). What remains is account-bound. Do these in
order; each is one action. Commands run from the **main repo root**. Never commit `.env`. Env-var
names below live in `.env` (values never printed anywhere).

**Already verified live (this session):** Venice client + open-weight `/models` guard PASS; the four
pinned ids resolve to huggingface.co sources; a FAST chat round-trips. Jira client authenticates
(`configured: True`). `PRECEDENT_DEV_MODELS`/`ALLOW_PROPRIETARY_DEV` are unset (Rule 1 safe).

**Your agent addresses (public — cross-check on Agentverse):**
- Watcher: `agent1q2m0gk9wdvs0lyc3nfuyeet4y3nc68m9y24kehun2t70hadwf7qxjcgkldx`
- Librarian: `agent1qv760pr29kmy9w5lst4tffr06rv6qqmt0ef74w6ycfezd5hfh0e0kse9xv7`
- Operator: `agent1qwesj8x7797jatzt3dwn8gxk2skxsaghrcpa76n548s6a6fz97wvuxna02g`

---

## STEP 1 — Finish the live Jira wiring (needed for the drift proof + incident 3 live)

The Jira client already authenticates; it has no runbook issues to watch (`JIRA_RUNBOOK_ISSUES` empty).

1. In your Jira project, create/pick two issues for the restricted runbooks (rights takedown +
   exclusivity) and set each issue's **Issue Security** level to the "Rights Ops Only" level (your
   `JIRA_SECURITY_LEVEL_RIGHTS_OPS` is already set). Note their keys, e.g. `MEDIA-113`, `MEDIA-114`.
2. Add to `.env`: `JIRA_RUNBOOK_ISSUES=MEDIA-113,MEDIA-114` (optionally fill
   `JIRA_RIGHTS_OPS_ACCOUNT_ID` / `JIRA_SCHEDULING_OPS_ACCOUNT_ID` for the two-seat variant).
3. Re-run the **read-only** smoke — it should now report 2 sources:
   ```bash
   set -a; . ./.env; set +a; PRECEDENT_LIVE_JIRA_SMOKE=1 .venv/bin/python scripts/jira_smoke.py
   ```
   Expect: `snapshot OK — 2 runbook source(s): [...]` with `constraints=1` each.

---

## STEP 2 — Confirm the Fetch agents + capture the 4 URLs

Agents are registered (you said). Finish the last mile:

1. On agentverse.ai → *Hosting → Mailbox agents*: confirm all three appear at the addresses above,
   and that **both** badges (`innovationlab` + `hackathon`) render on each agent's README panel.
2. Copy each agent's **profile URL** (3 URLs).
3. Run **≥10 real chats** with the Watcher from a fresh ASI:One session (discoverability is
   activity-gated), then copy the **shared-chat URL**.
4. Redeem the Agentverse credit code `UKAIAGENTUKAIAGENTAV` if not already.
5. Put the 4 URLs in `.env` (`WATCHER_/LIBRARIAN_/OPERATOR_AGENT_PROFILE_URL`,
   `ASI_ONE_SHARED_CHAT_URL`) **or paste them to me** — I'll fill every surface (deck A7 + rebuild the
   PDF, `BASEDAI-PR-README.md`, `DORAHACKS-WORKSHEET.md`, `FETCH-DELIVERABLES.md`) in one pass.

---

## STEP 3 — Saturday realism numbers (post as a PR comment)

1. **UCI 25k run.** Download the raw CSV to `data/raw/uci/` from
   `archive.ics.uci.edu/static/public/498/…zip`, then:
   ```bash
   make bench-uci
   ```
   Caption the result **"25k-record store"** — never "141k events". *(I can download + run this for
   you — just say so.)*
2. **Live Jira drift/TTC** (mutates real Jira; self-restores):
   ```bash
   set -a; . ./.env; set +a; PRECEDENT_LIVE_DRIFT=1 make live-drift
   ```
   It performs N security-level flips and times flip→deny against Jira's audit-records API. Paste the
   drift % + TTC values as a comment on the BasedAI PR.

---

## STEP 4 — Secrets scrub (A–E) + repo-public pre-flight

Full detail: `Prep/submissions/SCRUB-AND-PUBLISH-CHECKLIST.md`. Run all five, eyeball each hit:

```bash
gitleaks detect --source . --log-opts="--all" --redact -v          # A: full-history scan (clean now)
git log --all --full-history -- .env                                # B: MUST print nothing
git check-ignore -v .env                                            # B: MUST match a .gitignore rule
git log -p --all | grep -nE "(VENICE|JIRA|AGENTVERSE|ASI|KAGGLE)[A-Z_]*(KEY|TOKEN|SECRET|PASSWORD)[[:space:]]*[=:]" \
  | grep -vE "your-|placeholder|<|example|README|CHECKLIST"         # C: pattern grep
while IFS='=' read -r k v; do case "$k" in \#*|"") continue;; esac; v="${v%\"}"; v="${v#\"}"; \
  [ "${#v}" -lt 12 ] && continue; \
  [ -n "$(git log -S"$v" --oneline --all)" ] && echo "LEAK in history: $k"; done < .env   # D: literal-value scan
grep -rInE "(Bearer [A-Za-z0-9._-]{16,}|api[_-]?key\"?[[:space:]]*[:=][[:space:]]*\"?[A-Za-z0-9]{16,})" \
  docs/ data/ --include="*.json" --include="*.md" | grep -viE "example|placeholder"        # E: worktree sweep
```
Pre-flight (all TRUE before flipping visibility): A–E clean · `make freeze-check` passes · README has
run instructions · both badges render · `LICENSE` (MIT) + data-attribution present ·
`precedent_memory/bench/RESULTS.md` committed + green. The repo is already public → verify **logged-out
in incognito** that no secret is exposed; if a leak is found, **rotate the key on the vendor dashboard
FIRST**, then `git-filter-repo` with T1's OK.

---

## STEP 5 — Push (your authorization required)

```bash
git push --follow-tags origin main
```
Adds the 13 PROMPT-B commits + the `checkpoint-1-t1-t3-merged` tag. (An auto-sync may have already
pushed `main`; this ensures the tag + all commits land.) Then write the scrub-evidence line into
`docs/evidence/README.md` and post the repo URL in the team thread.

---

## STEP 6 — BasedAI fork PR

1. Fork `github.com/BasedAICo/hackathons`; clone; `git checkout -b precedent-submission`.
2. Check an existing merged PR for the exact submissions path, then
   `cp -r <UK-AI-Agent-EP5/submissions/_TEMPLATE> <…/submissions/precedent>/`.
3. Paste `Prep/submissions/BASEDAI-PR-README.md` as that folder's `README.md` (8 template headings, the
   measured table, six attack names, the four pinned ids **byte-for-byte** — already verified matching
   `precedent/models.py`), and the repo's **Venice-only `.env.example`** (already clean — no
   ANTHROPIC/OPENAI keys).
4. Ask a BasedAI mentor which deadline governs → replace `[[WAIT:MENTOR-ANSWER]]`; Saturday replace
   `[[WAIT:VIDEO-LINK]]`. Confirm `grep -n '\[\[WAIT' README.md` returns only those two before, zero
   after.
5. Re-run `gitleaks` on the fork; ensure "Files changed" lists ONLY your team folder; open the PR
   titled **"Precedent — permission-aware agent memory (UK AI Agent Hackathon EP5)"** before judging.

---

## STEP 7 — DoraHacks BUIDL (one-shot answers lock at submit)

Worksheet: `Prep/submissions/DORAHACKS-WORKSHEET.md`.
1. Open the BUIDL form for **event 2272** WITHOUT submitting. Tick **exactly** bounties **1370
   (Conduct) / 1367 (Fetch) / 1364 (BasedAI)** — deselect any pre-selected extras.
2. Copy each organizer question **verbatim** into the worksheet table; fill from the drafts; get **T1
   sign-off on every answer** (they lock at submit and can't be edited).
3. Fill the standard fields from the worksheet (repo URL, BasedAI PR URL, the 4 Fetch URLs, video URL);
   the headline numbers are already resolved (0 false-fast-paths / 100, 6/6, FNR 0/5,219).
4. Ctrl-F the page: no `‹`, `XX`, `TODO`, `TBD`. Incognito link-check every URL. Submit **before 22:59
   UTC** (never the last hour). Screenshot; commit the page text to `docs/evidence/dorahacks-buidl.md`.

---

## STEP 8 — Video capture + playtest

1. Record against the **frozen build** (seed 4207) using `Prep/video/shot-list.md` → `vo-script.md`;
   store the file **local on disk**. Shot 5 (ASI:One, 80s) is the Fetch centrepiece — never shortened.
2. Assemble the full (~4:15) + the 90-second cut (`cut-plans-30s-90s.md`) + the 30s teaser; both cuts
   keep "the second time is free" and "it knows what it's not allowed to touch".
3. Run `Prep/video/playtest-rubric.md` on a stranger — ship at ≥4/5 TRIAGED, 0 CONFUSED.

---

## STEP 9 — Outreach + selection-branch call

1. 10 warm practitioner sends (the change-board question). A real reply → the slide-12 validation line;
   otherwise **delete the line, never fake it**.
2. Watch the **~22:00 Fri** presenter-selection announcement and call the branch per
   `Prep/selection-branch-staging.md`: selected → attract-mode idle loop + live RESTRICT hotkey
   (local Jira-shaped role-flip) + the change-record on a hotkey; not-selected → the RESTRICT flip is
   the video insert and the 90-second cut goes first on the BUIDL page.
3. Rehearse to 2:40 (three run-throughs, one Wi-Fi-off via `Prep/airplane-mode-script.md`); the
   `Prep/rehearsal-gate-checklist.md` two-failures rule decides LIVE vs RECORDED mechanically.

---

## What I can execute for you on request

- Paste me the 4 Fetch URLs → I fill all surfaces + rebuild the deck PDF.
- Download the UCI CSV + run `make bench-uci`.
- Run `make live-drift` once `JIRA_RUNBOOK_ISSUES` is set (mutates real Jira — only on your go-ahead).
- Fill `[[WAIT:MENTOR-ANSWER]]` / `[[WAIT:VIDEO-LINK]]` once you have them.
