# PACKET — GitHub Publication: secrets scrub → repo public → BasedAI fork/PR (T3, human tasks)

> **Owner:** T3 (these are HUMAN tasks — **no GitHub token is configured in the repo**, so nothing here can be delegated to an agent session; you use your own GitHub account + browser + local git)
> **Runs:** Fri 09:00 (skeleton PR at stand-up, G0) · Fri ~19:30–20:15 (secrets scrub) · Fri ~20:15 (repo public) · Fri 21:00–22:00 (PR content commits, G4) · **Sat 08:45 PR FINAL-READY (G6, before judging)**
> **Budget:** ~2.0 ph total (PR mechanics ~1.0 after the morning-skeleton simplification + scrub/publication ~1.0)
> **Hand-back:** you are the hub — announcements go to the team WhatsApp thread; evidence lines go to `docs/evidence/README.md` (the evidence index)
> **Claude Pro use (bounded, off critical path):** interpreting scan output (redacted), checking the PR README against the template headings. Never start a long agentic session on this — if a session caps out mid-task, finish by hand; every step below is executable without Claude.

---

## 1. Why the order is locked

The repo **must be public before the DoraHacks draft goes in Sat 08:30** (Fetch hard gate: public repo with run instructions — and every BUIDL/deck/PR link points at it). Public repos expose **full git history**, so the scrub comes first, always. The BasedAI PR has its own clock: the event README said "3 Jul end of day" while the track doc says "4 Jul before judging" — the **skeleton PR at Friday stand-up satisfies both readings**; content lands through Friday night; final-ready Sat 08:45.

---

## 2. Fri 09:00 — BasedAI skeleton PR (at stand-up, ~30 min)

1. Browser: `github.com/BasedAICo/hackathons` → **Fork** (to your personal account).
2. Clone your fork locally and branch:
   ```bash
   git clone https://github.com/<YOUR-GH-USERNAME>/hackathons.git ~/basedai-hackathons
   cd ~/basedai-hackathons && git checkout -b precedent-submission
   ```
3. **Copy the `_TEMPLATE` folder** to a team folder — first look at merged/open PRs (e.g. PR #3 "BioVault") to mirror exactly where submission folders live, then:
   ```bash
   cp -r _TEMPLATE Precedent
   ```
4. Fill `Precedent/README.md` — **keep every template heading exactly as-is**, fill under each. Skeleton content minimum:
   - Project name + 2-sentence description (permission-aware agent memory: lineage-conjunction ACLs from live Jira, deterministic retrieval-layer enforcement, fail-closed).
   - **Open-weight declaration** (BasedAI hard rule): Qwen3.5-35B-A3B (Apache-2.0), DeepSeek-V4-Flash/Pro (MIT), BGE-M3 embedder (MIT) — all Venice-served, verified against public HF weights; `/models` eligibility dumps live in the main repo at `docs/compliance/`.
   - **Name all six adversarial attacks** the suite covers: query inference, metadata bypass, timing attack, collection attack, prompt injection, derived-memory attack.
   - A "Benchmark results" section stating in prose that FNR/FPR/P50/P99/overhead/drift/time-to-consistency vs the track's published thresholds are committed before Saturday judging (no `‹XX›` brackets — prose, then real numbers tonight).
   - Link to the main repo (note: "public later today" until §4 is done — update the wording after).
5. Fix `Precedent/.env.example`: **delete the template's ANTHROPIC/OPENAI example keys** (the open-weight declaration must not sit next to closed-vendor keys); list our real variable NAMES with placeholder values only (`VENICE_API_KEY=your-venice-key`, `JIRA_*`, `AGENTVERSE_*`, etc.) + comment `# open-weight only — pinned model IDs in README`.
6. Commit, push, open the PR against `BasedAICo/hackathons` main. Title: `Precedent — permission-aware agent memory (UK AI Agent Hackathon EP5)`. Body: 3 lines + "content commits land through 4 Jul; final before Saturday judging."
7. **Only-touch-your-folder check:** PR "Files changed" tab must list ONLY `Precedent/README.md` and `Precedent/.env.example`. If anything else appears (line-ending churn, editor droppings), fix before requesting anything.
8. Announce PR URL in the thread; add it to the evidence index. It's also a facts-pack line for N2's DoraHacks packet.

---

## 3. Fri ~19:30 — git-history secrets scrub (main Precedent repo, timebox 45 min)

Run ALL of A–E; any single pass is not sufficient.

**A. Automated scan (gitleaks; trufflehog as alternative):**
```bash
brew install gitleaks
cd <main-repo>
gitleaks detect --source . --log-opts="--all" --redact -v
# alternative / second opinion:
brew install trufflehog && trufflehog git file://. --only-verified
```
`--redact` keeps secrets out of your terminal/scrollback. Expect false positives on committed API *response* dumps — verify each hit by eye before panicking.

**B. Confirm `.env` was NEVER committed (verify, don't assume — it was gitignored from the first commit, check that's true):**
```bash
git log --all --full-history -- .env          # MUST print nothing
git log --all --full-history -- ".env.*"      # only .env.example may ever appear
git check-ignore -v .env                      # MUST match a .gitignore rule
```

**C. Pattern grep across all history** (our credential families — VENICE_/JIRA_/AGENTVERSE_ etc.):
```bash
git log -p --all | grep -nE "(VENICE|JIRA|AGENTVERSE|ASI|KAGGLE|HIGGSFIELD)[A-Z_]*(KEY|TOKEN|SECRET|PASSWORD)[[:space:]]*[=:]" \
  | grep -vE "your-|placeholder|<|CHANGEME|example|\.example|README|CHECKLIST"
```
Hits that survive the exclusion filter get eyeballed: variable name alone = fine; a real-looking value = leak.

**D. Literal-value scan (the strongest check — searches history for the actual secret values in today's `.env`):**
```bash
cd <main-repo>
while IFS='=' read -r k v; do
  case "$k" in \#*|"") continue;; esac
  v="${v%\"}"; v="${v#\"}"
  [ "${#v}" -lt 12 ] && continue            # skip short values (role IDs like 10007 false-positive)
  if [ -n "$(git log -S"$v" --oneline --all)" ]; then echo "LEAK in history: $k"; fi
done < .env
```
(Prints only variable NAMES, never values.)

**E. Worktree sweep of committed dumps/evidence** (the `/models` dumps are response bodies and should be clean — confirm):
```bash
grep -rInE "(Bearer [A-Za-z0-9._-]{16,}|api[_-]?key\"?[[:space:]]*[:=][[:space:]]*\"?[A-Za-z0-9]{16,})" \
  docs/ data/ --include="*.json" --include="*.md" | grep -viE "example|placeholder"
```

**If a real leak is found — decision rule, no improvising:**
1. **Rotate the key immediately** (Venice / Jira / Agentverse dashboard). Rotation is the safety floor — a rotated key in history is dead.
2. If it's in history: `brew install git-filter-repo` and excise the file/blob — only with T1's OK (it rewrites history while T1/T2 are still pushing; coordinate a push-pause, everyone re-clones after).
3. Re-run A–D from scratch. If not clean by **20:15, escalate to T1**: the repo does NOT go public until clean — and the DoraHacks draft slips with it, so this outranks everything else you're doing.

**Record it:** add one line to `docs/evidence/README.md` — "3 Jul ~20:00: gitleaks vX.Y full-history scan + literal-value scan: clean; `.env` never committed (verified)". Commit.

---

## 4. Fri ~20:15 — make the repo public (10 min)

Pre-flight (all must be true):
- [ ] §3 clean
- [ ] README has **run instructions** (Fetch hard gate) — if missing, ping T2 now; publication waits for this, not for polish
- [ ] Fetch **badges** on each agent README section: `![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)` `![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)` (mandatory per hackpack; 5-min fix if absent)
- [ ] LICENSE file exists; data-attribution lines present (UCI CC BY 4.0, TVmaze CC BY-SA) — flag T1 if not, don't block on it past 20:30
- [ ] `git status` shows `.env` untracked

Then: GitHub → repo → **Settings → General → Danger Zone → Change visibility → Make public** → type the repo name to confirm.

Post-flight: open the repo URL in an **incognito window** — README renders, `docs/compliance/` dumps load, `data/analysis/` loads. Post the public URL in the thread (N2 needs it for the facts pack / BUIDL; the deck and video captions link it). Update the BasedAI PR README's "public later today" wording.

---

## 5. Fri 21:00–22:00 — PR content commits (G4 window)

As the freeze lands and `bench/RESULTS.md` + the 100-mutation numbers exist:
```bash
cd ~/basedai-hackathons   # your fork
```
- Paste the measured bench table into `Precedent/README.md` (FNR / FPR / P50 / P99 / end-to-end overhead / ACL drift / time-to-consistency — each against its published threshold, pass/fail) + the mutation-bench line + link to `bench/RESULTS.md` in the now-public main repo.
- Degraded rule if the bench slipped: ship only what was measured; **remove** unmeasured rows, never bracket them.
- Commit + push — the open PR updates automatically. Re-check "Files changed" still touches only `Precedent/`.

---

## 6. Sat 08:45 — PR FINAL-READY (G6, before judging; you're on shift from 06:30)

- [ ] Push the **video link** commit (URL from N2/T2 — the unlisted upload from last night)
- [ ] `grep -rn '‹' Precedent/` returns nothing; no "TODO"/"TBD" in the README
- [ ] All README links open logged-out (incognito): main repo, bench file, compliance dumps, video
- [ ] "Files changed" = only `Precedent/` files; no merge conflicts against upstream (if upstream moved: `git fetch upstream && git rebase upstream/main` — upstream remote: `git remote add upstream https://github.com/BasedAICo/hackathons.git`)
- [ ] Comment on the PR: "Final for judging — video + measured benchmarks included."
- [ ] Announce in the thread: "G6 done — BasedAI PR final-ready" + give N2 the final PR URL for the BUIDL page

## 7. No-secrets checklist for the PR (run at EVERY push to the fork)

- [ ] `Precedent/.env.example`: placeholder values only, no real keys anywhere in the folder
- [ ] No committed output/dump files carrying auth headers
- [ ] `cd ~/basedai-hackathons && gitleaks detect --source . --log-opts="--all" --redact` on the fork before the final push (30 seconds — the fork has your commits too)

## 8. DONE when

Skeleton PR open by Fri 09:30 · scrub evidence line committed · repo public + incognito-verified by Fri ~20:30 · bench commits pushed by Fri 22:00 · PR final-ready announced by Sat 08:45. Every gate announced in the thread as it closes — N2's DoraHacks packet and the deck both consume your URLs.
