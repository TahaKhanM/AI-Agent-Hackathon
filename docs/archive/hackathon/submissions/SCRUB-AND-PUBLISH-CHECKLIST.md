# Secrets scrub (A–E) + repo-public pre-flight — human runbook

The repo does **not** go public until the full A–E scrub is clean (any single pass is
insufficient). Agent seeds, mailbox keys, tokens, real teammate names, and Jira accountIds must
never appear in code, a commit, a screenshot, the PR, the BUIDL, or any prompt. Run every pass;
eyeball each surviving hit yourself ("variable name or real value?"). **A real leak → rotate the
key on the vendor dashboard FIRST, then `git-filter-repo` only with T1's OK.**

Run from the **main repo root** (not this worktree).

## A — Automated full-history scan (gitleaks)

```bash
gitleaks detect --source . --log-opts="--all" --redact -v
```
`--redact` hides values in the output; a finding is a *location*, not proof of a real secret —
open the location and decide. `make secrets-scan` runs this same command.

## B — `.env` was never committed

```bash
git log --all --full-history -- .env            # MUST print nothing
git log --all --full-history -- ".env.*"        # only .env.example may ever appear
git check-ignore -v .env                         # MUST match a .gitignore rule
```

## C — Pattern grep across all history (credential families)

```bash
git log -p --all | grep -nE "(VENICE|JIRA|AGENTVERSE|ASI|KAGGLE|HIGGSFIELD)[A-Z_]*(KEY|TOKEN|SECRET|PASSWORD)[[:space:]]*[=:]" \
  | grep -vE "your-|placeholder|<|CHANGEME|example|\.example|README|CHECKLIST"
```
Any surviving line is a real assignment in history — investigate.

## D — Literal-value scan (strongest — searches history for the ACTUAL .env values)

```bash
while IFS='=' read -r k v; do
  case "$k" in \#*|"") continue;; esac
  v="${v%\"}"; v="${v#\"}"
  [ "${#v}" -lt 12 ] && continue                 # skip short values (role ids like 10007 false-positive)
  if [ -n "$(git log -S"$v" --oneline --all)" ]; then echo "LEAK in history: $k"; fi
done < .env
```

## E — Worktree sweep of committed dumps/evidence

```bash
grep -rInE "(Bearer [A-Za-z0-9._-]{16,}|api[_-]?key\"?[[:space:]]*[:=][[:space:]]*\"?[A-Za-z0-9]{16,})" \
  docs/ data/ --include="*.json" --include="*.md" | grep -viE "example|placeholder"
```
(The Venice `/models` dumps in `docs/compliance/` are public catalog data — no keys — but sweep anyway.)

## Also grep the paths the open-weight guard does NOT scan

`make check-open-weight` scans `precedent precedent_memory sim console agents` only. Also grep the
tests and the mutation corpus by hand for closed-model ids:

```bash
grep -rnE "claude-|openai-|gpt-|gemini-|grok-|mercury-" tests/ precedent_memory/bench/*.jsonl \
  | grep -v "test_invariants_guard.py\|test_mutation_corpus.py"   # those two hold the DETECTOR pattern, not a model
```
The only expected matches are the two detector files above (they build/hold the pattern to enforce
the rule); anything else is a violation.

## Repo-public pre-flight (all must be TRUE before flipping visibility)

- [ ] A–E scrub clean; `.env` untracked (`git status` shows it untracked)
- [ ] `make freeze-check` passes (open-weight + tests + secrets + no ‹ placeholder)
- [ ] README has run instructions (Fetch hard gate)
- [ ] Both Fetch badges render on each agent's README section (see `docs/evidence/T3-AGENTS-VERIFICATION.md`)
- [ ] `LICENSE` present (MIT) + data-attribution lines (UCI CC BY 4.0, TVmaze CC BY-SA) in README
- [ ] `precedent_memory/bench/RESULTS.md` committed and all-green

## Flip public + verify

1. GitHub → Settings → General → Danger Zone → Change visibility → **Make public**.
2. Verify in an **incognito** window: repo loads, README renders, `docs/compliance/*.json` load,
   `precedent_memory/bench/RESULTS.md` renders.
3. Write the scrub-evidence line into `docs/evidence/README.md`, e.g.:
   `> Secrets scrub A–E clean (gitleaks --all + .env-history + pattern grep + literal-value scan +
   worktree sweep), <date>; repo made public <date>; verified logged-out.`
4. Post the public repo URL + PR URL + `precedent_memory/bench/RESULTS.md` path in the team thread
   (this unblocks N2's DoraHacks draft and N1's deck).

## Before the FINAL push to the BasedAI fork

- [ ] Re-run gitleaks on the **fork** (`gitleaks detect --source . --log-opts="--all" --redact -v`).
- [ ] Rebase onto `upstream/main` if it moved; "Files changed" lists ONLY your team folder.
