# T3 — GitHub Publication: secrets scrub → repo public → BasedAI fork/PR (human tasks)

> **Owner:** T3. These stay **HUMAN tasks** — **no GitHub token is wired into the repo**, so none of this can run in an agent session. You do it with your own GitHub account + browser + local git.
> **Phasing (dependency-based, not clock-pinned):**
> - **Kickoff:** open the BasedAI skeleton PR (§2) — satisfies the earliest submission reading and unblocks nothing else, so land it first.
> - **Before the freeze / before N2's DoraHacks draft:** run the full secrets scrub (§3), then make the main repo public (§4). The DoraHacks draft cannot go in until the repo is public, so this is a hard predecessor for N2's submission work.
> - **After T3's bench numbers land (`bench/RESULTS.md` + the mutation numbers):** commit real benchmark content into the PR (§5).
> - **Before Saturday judging:** PR FINAL-READY — video link + measured benchmarks + link check (§6).
> **You are the hub:** announce each gate as it closes in the team thread; write evidence lines into `docs/evidence/README.md` (the evidence index). N2's DoraHacks packet and N1's deck both consume your URLs, so they're waiting on these announcements.

---

## Driving your AI tool

You have a capable coding agent — use it for the reading/checking work, not the account-level actions:
- Point it at `Precedent/README.md` (in your fork) and the BasedAI `_TEMPLATE/README.md` and ask it to **verify every template heading is present and in order**, and flag any `‹XX›` / `TODO` / `TBD`.
- Have it **interpret redacted scan output** and the pattern-grep hits (§3) — "is this a variable name or a real value?" — but you run the scans and make the leak call yourself.
- Have it draft the PR body and the evidence lines, then you review and commit.
- **What it CANNOT do:** fork, push, open/merge the PR, or flip repo visibility — those need your GitHub session. There's no token, by design. Don't wait on an agent for them.

---

## 1. Why the order is locked

The main repo **must be public before N2 files the DoraHacks draft** (Fetch hard gate: public repo with run instructions — every BUIDL/deck/PR link points at it). Public repos expose **full git history**, so the scrub comes first, always. The BasedAI PR has its own timeline: the event README said "3 Jul end of day" while the track doc says "4 Jul before judging" — the **skeleton PR at kickoff satisfies both readings**; content lands as the benches complete; final-ready before Saturday judging.

---

## 2. Kickoff — BasedAI skeleton PR (~30 min)

Land this first thing; it has no upstream dependencies.

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
   - A "Benchmark results" section stating in prose that FNR/FPR/P50/P99/overhead/drift/time-to-consistency vs the track's published thresholds are committed before Saturday judging (no `‹XX›` brackets — prose now, real numbers once the benches land).
   - Link to the main repo (note: "public soon" until §4 is done — update the wording after).
5. Fix `Precedent/.env.example`: **delete the template's ANTHROPIC/OPENAI example keys** (the open-weight declaration must not sit next to closed-vendor keys); list our real variable NAMES with placeholder values only (`VENICE_API_KEY=your-venice-key`, `JIRA_*`, `AGENTVERSE_*`, etc.) + comment `# open-weight only — pinned model IDs in README`.
6. Commit, push, open the PR against `BasedAICo/hackathons` main. Title: `Precedent — permission-aware agent memory (UK AI Agent Hackathon EP5)`. Body: 3 lines + "content commits land through 4 Jul; final before Saturday judging."
7. **Only-touch-your-folder check:** PR "Files changed" tab must list ONLY `Precedent/README.md` and `Precedent/.env.example`. If anything else appears (line-ending churn, editor droppings), fix before requesting anything.
8. Announce the PR URL in the thread; add it to the evidence index. It's also a facts-pack line for N2's DoraHacks packet.

---

## 3. Git-history secrets scrub (main Precedent repo — before the repo goes public)

Run ALL of A–E; any single pass is not sufficient. **gitleaks is already installed and history was verified clean earlier — this is a re-confirm, not a fresh discovery.** Still run every pass: new commits have landed since.

**A. Automated scan (gitleaks; trufflehog as alternative):**
```bash
cd <main-repo>
gitleaks detect --source . --log-opts="--all" --redact -v
# alternative / second opinion:
brew install trufflehog && trufflehog git file://. --only-verified
```
`--redact` keeps secrets out of your terminal/scrollback. Expect false positives on committed API *response* dumps — verify each hit by eye before panicking.

**B. Confirm `.env` was NEVER committed (verify, don't assume — it was gitignored from the first commit, check that's still true):**
```bash
git log --all --full-history -- .env          # MUST print nothing
git log --all --full-history -- ".env.*"      # only .env.example may ever appear
git check-ignore -v .env                       # MUST match a .gitignore rule
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
2. If it's in history: `brew install git-filter-repo` and excise the file/blob — only with T1's OK (it rewrites history while others are still pushing; coordinate a push-pause, everyone re-clones after).
3. Re-run A–D from scratch. **The repo does NOT go public until clean** — and the DoraHacks draft slips with it, so this outranks everything else you're doing. If you can't get it clean, escalate to T1.

**Record it:** add one line to `docs/evidence/README.md` — "gitleaks vX.Y full-history scan + literal-value scan: clean; `.env` never committed (verified)". Commit.

---

## 4. Make the repo public (after §3 is clean; before N2's DoraHacks draft)

Pre-flight (all must be true):
- [ ] §3 clean
- [ ] README has **run instructions** (Fetch hard gate) — if missing, ping T2 now; publication waits for this, not for polish
- [ ] Fetch **badges** on each agent README section: `![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)` `![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)` (mandatory per hackpack; 5-min fix if absent)
- [ ] LICENSE file exists; data-attribution lines present (UCI CC BY 4.0, TVmaze CC BY-SA) — flag T1 if not, don't block on it
- [ ] `git status` shows `.env` untracked

Then: GitHub → repo → **Settings → General → Danger Zone → Change visibility → Make public** → type the repo name to confirm.

Post-flight: open the repo URL in an **incognito window** — README renders, `docs/compliance/` dumps load, `data/analysis/` loads. Post the public URL in the thread (N2 needs it for the facts pack / BUIDL; the deck and video captions link it). Update the BasedAI PR README's "public soon" wording to the real URL.

---

## 5. PR content commits (once the bench numbers land)

When the freeze is in and `bench/RESULTS.md` + the 100-mutation numbers exist:
```bash
cd ~/basedai-hackathons   # your fork
```
- Paste the measured bench table into `Precedent/README.md` (FNR / FPR / P50 / P99 / end-to-end overhead / ACL drift / time-to-consistency — each against its published threshold, pass/fail) + the mutation-bench line + link to `bench/RESULTS.md` in the now-public main repo.
- Degraded rule if a bench slipped: ship only what was measured; **remove** unmeasured rows, never bracket them.
- Commit + push — the open PR updates automatically. Re-check "Files changed" still touches only `Precedent/`.

**§5 ambition hook:** if T3 lands the **full BasedAI green-tick eligibility table** (every model, license, HF weight verified) and the **6-of-6 attacks all passing** with **derived-memory correctness** and the **O(1) enforcement curve**, mirror that headline into the PR README's benchmark and compliance sections — it's the strongest single differentiator the judges see on the BasedAI side, so give it pride of place.

---

## 6. PR FINAL-READY (before Saturday judging)

- [ ] Push the **video link** commit (URL from N2/T2 — the unlisted upload)
- [ ] `grep -rn '‹' Precedent/` returns nothing; no "TODO"/"TBD" in the README
- [ ] All README links open logged-out (incognito): main repo, bench file, compliance dumps, video
- [ ] "Files changed" = only `Precedent/` files; no merge conflicts against upstream (if upstream moved: `git remote add upstream https://github.com/BasedAICo/hackathons.git` then `git fetch upstream && git rebase upstream/main`)
- [ ] Comment on the PR: "Final for judging — video + measured benchmarks included."
- [ ] Announce in the thread: "BasedAI PR final-ready" + give N2 the final PR URL for the BUIDL page

---

## 7. No-secrets checklist for the PR (run at EVERY push to the fork)

- [ ] `Precedent/.env.example`: placeholder values only, no real keys anywhere in the folder
- [ ] No committed output/dump files carrying auth headers
- [ ] `cd ~/basedai-hackathons && gitleaks detect --source . --log-opts="--all" --redact` on the fork before the final push (30 seconds — the fork has your commits too)

---

## 8. DONE when

Skeleton PR open at kickoff · scrub evidence line committed · main repo public + incognito-verified before N2's DoraHacks draft · bench commits pushed once the numbers land · PR final-ready announced before Saturday judging. Every gate announced in the thread as it closes — N2's DoraHacks packet and N1's deck both consume your URLs.
