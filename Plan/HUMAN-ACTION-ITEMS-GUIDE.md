# Human action items — complete step-by-step guide (self-contained)

> The two Ultracode build sessions (**T1** = [`Prompts/03-ultracode-t1-completion.md`](../Prompts/03-ultracode-t1-completion.md), **T3** = [`Prompts/04-ultracode-t3-completion.md`](../Prompts/04-ultracode-t3-completion.md)) do all the code, tests, bench, data, and submission *drafts* automatically. This file is everything **a human must do by hand** — with every path, name, ID, and command spelled out. You should be able to do each task from this file alone.
>
> Companion: [`HUMAN-ACTION-ITEMS-T1-T3.md`](HUMAN-ACTION-ITEMS-T1-T3.md) is the one-line checklist; this is the how-to.

---

## 0. Reference — every name, path, and ID in one place

| Thing | Value |
|---|---|
| **Main repo on disk** | `/Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon` (branch `build/t1-core-loop-sim-agents`, T1 building here) |
| **T3 worktree on disk** | `/Users/tahakhan/Documents/Work/Projects/precedent-t3-bench` (branch `build/t3-bench-submissions`, run T3 here) |
| **Project Python** | **`.venv/bin/python`** — the project virtualenv (has `uagents`, `fastapi`, etc.). **NOT** plain `python` / conda `base`. Always run as `.venv/bin/python …` or via `make …`. |
| **Your secrets file** | `.env` in the main repo — **gitignored, never committed**. All real keys/tokens/account IDs live only here. |
| **BasedAI upstream repo** | `github.com/BasedAICo/hackathons` |
| **Your fork name** | **`hackathons`** — keep GitHub's default, do **not** rename. It becomes `github.com/<your-username>/hackathons`. |
| **Fork clone location** | `~/basedai-hackathons` |
| **Fork branch name** | `precedent-submission` |
| **Event folder (upstream)** | `UK-AI-Agent-EP5/` (event: 28 Jun – 4 Jul 2026, Imperial College London) |
| **Submission template** | `UK-AI-Agent-EP5/submissions/_TEMPLATE/` — contains exactly `README.md` + `.env.example` |
| **Your submission folder** | `UK-AI-Agent-EP5/submissions/precedent/` — team-folder names must be **lowercase-hyphenated** (rule from upstream `CONTRIBUTING.md`); "precedent" is one word, so just `precedent` |
| **PR title** | `Precedent — permission-aware agent memory (UK AI Agent Hackathon EP5)` |
| **Fetch badges** | `![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)` and `![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)` |
| **Open-weight models to declare** | Qwen3.5-35B-A3B (Apache-2.0), DeepSeek-V4-Flash + DeepSeek-V4-Pro (MIT), BGE-M3 embedder (MIT) — all Venice-served. **Copy the exact pinned IDs byte-for-byte from `precedent/models.py` and `docs/compliance/venice-models-2026-07-03.json`** — do not retype from memory. |
| **DoraHacks** | Event **2272**; the project's three bounties are **1370 / 1367 / 1364** (confirm the labels on the form) |
| **Jira role IDs** | Rights Ops role `10007`, Scheduling Ops role `10008` |
| **Jira issue-security IDs** | scheme `10000`; level Rights Ops `10000`, level Scheduling Ops `10001` |
| **Deadlines** | DoraHacks final: **23:59 BST / 22:59 UTC, Sat 4 Jul**. BasedAI PR: final before Saturday judging (confirm exact — item 4). |

**Three golden rules (apply to everything below):**
1. **Never commit a secret.** Real keys/tokens/passwords/account IDs live only in your local `.env`. `.env.example` and every committed file contain **variable names + placeholder values only**.
2. **Never say "Autonomous."** The product's top autonomy level is always called **"Standing Approval."**
3. **Every number** on a slide/PR/BUIDL traces to `Research/00-verified-claims.md` with its caveat (e.g. "18.2h calendar hours", "25k-record store" never "141k events").

---

## Running two build sessions at once (do this first)

The T1 session is live in the main repo folder. To run **T3 at the same time without breaking T1**, T3 uses its **own folder** (a git "worktree"), not a branch-switch of the shared folder. **That worktree is already created:** `/Users/tahakhan/Documents/Work/Projects/precedent-t3-bench`.

1. If a **"Uncommitted changes / stash / switch branch"** dialog appears on the main folder → **click Cancel.** Never stash or switch that folder while T1 is running (7 sessions share it).
2. Open a **new Claude Code session** whose folder is `/Users/tahakhan/Documents/Work/Projects/precedent-t3-bench`.
3. Open [`Prompts/04-ultracode-t3-completion.md`](../Prompts/04-ultracode-t3-completion.md), copy from the line **"PROMPT — paste from here"** downward, and paste it as the first message (keep the leading `ultracode`).
4. T3's first step merges the latest `main` into its worktree, so it picks up all of T1's committed work.

Recreate the worktree if ever needed: `git worktree add ../precedent-t3-bench build/t3-bench-submissions` (run from the main repo). Remove it later: `git worktree remove ../precedent-t3-bench`.

---

## Setup — your `.env` files and which folder to use (read this before items 5, 6, 9, 12, 15)

You now have **two working folders**, and this is the thing that trips people up:

| Folder | Path | Has a `.env`? |
|---|---|---|
| **Main repo** — T1 builds here; **you run + register the Fetch agents here** | `/Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon` | ✅ Yes — the real, already-populated one |
| **T3 worktree** — T3 builds here | `/Users/tahakhan/Documents/Work/Projects/precedent-t3-bench` | ❌ No — you must copy one in |

**Why the T3 folder has no `.env`:** `.env` is gitignored, and `git worktree add` does **not** copy gitignored files — so the new folder starts without one.

**The rule: the MAIN repo's `.env` is the canonical one.** Every real key, **every agent seed**, and every account ID goes **there**, and you run/register the Fetch agents from the main folder. Give the T3 worktree its own copy so its session can read config too:
```bash
cp /Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon/.env /Users/tahakhan/Documents/Work/Projects/precedent-t3-bench/.env
```
If you later change a value (e.g. add the seeds), update the main `.env` and re-copy. **Never commit either `.env`** — run `git status`; it must never list `.env`.

### Generate the three Fetch agent seeds now (answers "do I make the seed with a random generator?")

**Yes.** A "seed" is a secret random string that permanently becomes an agent's identity/address (same seed → same address, forever — details in item 5). Generate three — one per agent:
```bash
openssl rand -hex 32        # run this 3 times, once per agent
# (or: python3 -c "import secrets; print(secrets.token_hex(32))")
```
Open the **main** repo's `.env` (**not** the T3 one) and paste one value into each line (these already exist as empty placeholders):
```
WATCHER_AGENT_SEED=<paste the 1st value>
LIBRARIAN_AGENT_SEED=<paste the 2nd value>
OPERATOR_AGENT_SEED=<paste the 3rd value>
```
Then re-copy the `.env` to the T3 worktree (command above) so both stay in sync.
**Rules:** each seed is private-key-grade — **never commit it, never paste it into a chat / PR / screenshot, and never change it once the agent is registered** (a changed seed = a brand-new agent with a new address, and the ≥10-interaction discoverability clock resets to zero).

---

# G0 — Kickoff

## 1. [both] Ratify the canonical seed `4207`
**Goal:** one shared random-seed number so every replay is byte-identical and one benchmark number appears on all four surfaces (on-screen chip / slide 10 / README / BUIDL).
**Steps:**
1. At the kickoff stand-up (or in the team thread) state in writing: **"Canonical seed = 4207."**
2. Nothing else — both build prompts already default to `4207` and write it as a single constant.
**If you want a different number:** tell **both** the T1 and T3 sessions to change it (one constant each). Never change one and not the other.
**Done when:** the value is agreed in writing.

## 2. [T3] Confirm the T3 worktree
**Already created for you.** Verify:
```bash
cd /Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon
git worktree list
```
**Done when:** you see two lines — the main folder (`build/t1-core-loop-sim-agents`) and `precedent-t3-bench` (`build/t3-bench-submissions`).

## 3. [T3] Open the BasedAI skeleton PR
**Goal:** a pull request into BasedAI's repo — this is the **only** way to enter the BasedAI track. Open an empty "skeleton" now to reserve your place; real numbers land later (item 12).
**You'll need:** a GitHub account; ~30 min. The T3 session will have **drafted the README and `.env.example`** — find them under the T3 worktree (it writes prep files under `docs/evidence/` or `Prep/` and names the path in its final report). If the T3 session hasn't run yet, you can draft from [`Plan/workflows/N2-basedai-pr-readme.md`](workflows/N2-basedai-pr-readme.md) + the model IDs in `docs/compliance/`.

**Step A — Fork (keep the default name `hackathons`):**
1. In a browser go to **`github.com/BasedAICo/hackathons`** → click **Fork** (top-right) → **Create fork** into your own account.
2. **Leave the repository name as `hackathons`** — do not rename it. Your fork is now `github.com/<your-username>/hackathons`. (The submission is a *folder inside* the repo; the repo name doesn't change.)

**Step B — Clone your fork and branch:**
```bash
git clone https://github.com/<your-username>/hackathons.git ~/basedai-hackathons
cd ~/basedai-hackathons
git checkout -b precedent-submission
```

**Step C — Create your team folder from the template:**
```bash
cp -r UK-AI-Agent-EP5/submissions/_TEMPLATE UK-AI-Agent-EP5/submissions/precedent
```
(The folder name must be **lowercase and hyphenated** per the upstream `CONTRIBUTING.md` — `precedent` is one word, so just `precedent`.)

**Step D — Fill the two template files** (the template has exactly these two):
1. `UK-AI-Agent-EP5/submissions/precedent/README.md` — paste the T3 session's drafted README. It must contain:
   - Project name + a 2-sentence description (permission-aware agent memory: lineage-conjunction ACLs from live Jira, deterministic retrieval-layer enforcement, fail-closed).
   - **Open-weight declaration:** Qwen3.5-35B-A3B (Apache-2.0), DeepSeek-V4-Flash/Pro (MIT), BGE-M3 embedder (MIT) — all Venice-served, verified against public HuggingFace weights; note the `/models` dumps live in the main repo under `docs/compliance/`. **Copy the exact IDs from `precedent/models.py` / `docs/compliance/venice-models-2026-07-03.json`.**
   - **The six attack names, verbatim:** query inference, metadata bypass, timing attack, collection attack, prompt injection, derived-memory attack.
   - A "Benchmark results" section — prose for now, with `[[WAIT:BENCH-SYNTH]]` / `[[WAIT:ATTACKS]]` / `[[WAIT:BENCH-CURVE]]` / `[[WAIT:VIDEO-LINK]]` / `[[WAIT:MENTOR-ANSWER]]` markers you replace later.
   - A link to your main repo (write "public soon" until item 10 is done, then update to the real URL).
   - The two **Fetch badges** (from the reference table) in each agent's section.
2. `UK-AI-Agent-EP5/submissions/precedent/.env.example` — **delete any `ANTHROPIC` / `OPENAI` example lines** from the template (the open-weight declaration must not sit next to closed-vendor keys). List your real variable **names** with placeholder values only (`VENICE_API_KEY=your-venice-key`, `JIRA_*`, `AGENTVERSE_*`, …) + a comment `# open-weight only — pinned model IDs in README`.

**Step E — Commit, push, open the PR:**
```bash
cd ~/basedai-hackathons
git add UK-AI-Agent-EP5/submissions/precedent
git commit -m "Precedent — permission-aware agent memory (skeleton)"
git push -u origin precedent-submission
```
Then on GitHub: open a **Pull Request** from `<your-username>:precedent-submission` into **`BasedAICo/hackathons` : `main`**. Title it exactly:
> **Precedent — permission-aware agent memory (UK AI Agent Hackathon EP5)**
Body: 3 lines describing the project + "content commits land through 4 Jul; final before Saturday judging."

**Step F — Verify and announce:**
1. On the PR's **"Files changed"** tab, confirm it lists **ONLY** files inside `UK-AI-Agent-EP5/submissions/precedent/`. Upstream rule: never modify other teams' folders or shared files (root `README.md`, `.github/`, `.gitleaks.toml`). If anything else appears, fix before requesting review.
2. Paste the PR URL into your team thread + `docs/evidence/README.md`.
**Watch out:** no real keys anywhere in the folder; only-your-folder; keep the fork named `hackathons`.

## 4. [T3] Ask a BasedAI mentor which deadline governs
**Goal:** remove a date ambiguity (event README implies "3 Jul EOD"; the track doc says "4 Jul before judging").
**Steps:**
1. On the hackathon Discord (or ask an organizer on-site): *"For the BasedAI track — does the '3 Jul end of day' or '4 Jul before judging' deadline govern the PR content?"*
2. Write the answer into the PR description, replacing the `[[WAIT:MENTOR-ANSWER]]` marker. If no one answers, write: "No answer received; we satisfied the earlier reading."
**Done when:** the PR has a real answer or that fallback sentence.

## 5. [both] Create + register the three Fetch agents on Agentverse
**Goal:** get the Watcher / Librarian / Operator agents live and discoverable on Fetch's network. **This is a pass/fail hard gate — partial integration scores zero.**

**Concepts first (so the steps make sense):**
- **Agent** = a small Python program the build sessions wrote in `agents/`. **Watcher** is the front door ASI:One talks to; **Librarian** does memory/permissions; **Operator** executes the fix.
- **Seed** = the agent's permanent secret identity — you generated these in the Setup section. Same seed → same address, forever.
- **Mailbox** = Agentverse hosts an inbox for your agent, so it's reachable **without running a public web server or having a public IP** — this is what survives the venue's network. (You don't open firewall ports.)
- **You do NOT create an agent by filling a "new agent" form on the website.** You **run the agent program** on your laptop; it **auto-registers itself** with Agentverse; then you **connect** it with one click on an "Inspector" page. *(Verified against Fetch's current docs — see sources in the chat.)*

**You'll need:** the three seeds in the **main** `.env` (Setup section); a free **Agentverse account** (sign up at **agentverse.ai**); the agent code (T1 wrote the Watcher; T3 writes the Librarian + Operator echo skeletons — each build session prints the exact run command in its final report).

**Steps:**
1. **Log in to agentverse.ai** in your browser and stay logged in — the Inspector page in step 4 links the agent to *your* account.
2. **Run an agent from the MAIN repo folder — using the project's venv Python, with `.env` loaded.** Two gotchas: (a) use **`.venv/bin/python`**, not plain `python` (your shell's `python` is conda `base`, which has no `uagents` → `ModuleNotFoundError`); (b) **load `.env` first**, or the agent falls back to a throwaway local-dev seed/address instead of your real one:
   ```bash
   cd /Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon
   set -a; source .env; set +a           # load your seeds/keys into this shell
   .venv/bin/python -m agents.watcher     # then agents.librarian, then agents.operator
   ```
   You don't edit code — the agent already has `mailbox=True` and reads its seed from `WATCHER_AGENT_SEED`.
   *(If `source .env` errors on a line, just `export WATCHER_AGENT_SEED=<your value>` before running — the seed is the only var registration strictly needs. And set the seed **before** you register: if you register the fallback dev address first, you'll have to re-register the real one and reset the discoverability clock.)*
3. **Read the terminal output.** You'll see the agent's address (`agent1q…`) followed by:
   ```
   Mailbox access token acquired
   Successfully registered as mailbox agent in Agentverse
   ```
   and an **Inspector URL** like `https://agentverse.ai/inspect/?address=agent1q…`.
4. **Open that Inspector URL** in your (logged-in) browser → click **Connect** → choose **Mailbox** → confirm. That's the registration. **No Agentverse API key is required** — the mailbox token was acquired automatically in step 3.
5. **Repeat for the Librarian and the Operator** — run each, open its Inspector URL, Connect → Mailbox.
6. **Check Agentverse → "My Agents":** all three should appear with a **Mailbox** tag, and each agent's README should render **both badges**:
   ```
   ![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
   ![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)
   ```
   (The build sessions add these to each agent's README and set `publish_agent_details=True` so they show. If a badge is missing, add the two lines to that agent's README and re-run it.)
7. **Copy the identifiers back into the main `.env`** and the team thread: each agent's **address** and its Agentverse **profile URL** (the **Watcher's** is the one ASI:One users chat with).

**What the startup logs mean (two warnings are expected — don't panic):**
- `Manifest published successfully: AgentChatProtocol` + `Registration on Almanac API successful` + `registration status … active` → ✅ it's registered and discoverable.
- `Agent mailbox not found: create one using the agent inspector` → **expected** until you do step 4 (Inspector → Connect → Mailbox). It clears on the next run once the mailbox exists.
- `I do not have enough funds to register on Almanac contract` / `send funds to wallet fetch1…` → **ignore it.** That's the *optional on-chain* Almanac **contract**; the Almanac **API** registration above is all you need for Agentverse + ASI:One. **Do not send any FET/testnet funds.**
- Sanity-check you're on your real seed (not the dev fallback): in the same shell, `echo $WATCHER_AGENT_SEED` should print your hex. If empty, you loaded no seed — set it and re-run **before** creating the mailbox.

**Done when:** all three appear in Agentverse "My Agents" with the Mailbox tag + both badges, and their addresses/profile URLs are saved in `.env`.

**Watch out:**
- **All three agents default to port 8000, so they can't run at the same time out of the box** — you'll hit `[Errno 48] address already in use` (and that agent won't register). For **registration**, run them **one at a time**: registration is one-time and the mailbox persists on Agentverse after you Connect, so Ctrl+C one before starting the next. To run all three **together** (needed only for the full ASI:One loop, not for registration), give each its own port (8000/8001/8002 via an env override) **or** use the console-driven demo (`make sim`), which drives the loop in-process with no port juggling.
- **Keep the relevant agent running for live use:** the Watcher must be up to receive ASI:One chats and accumulate the ≥10 interactions (the mailbox stores messages while it's offline, but the agent must be up to reply).
- **Never change a seed after registering** — you'd get a different agent with a new address, and the discoverability clock resets.
- **The seed is private-key-grade** — never commit it or paste it into a chat/PR/screenshot.
- *(Advanced, not needed here:)* if you'd rather register **programmatically** or **host** the agent instead of the Inspector click, you'll need an **Agentverse API key** (Agentverse → your profile → **API Keys**) in the `AGENTVERSE_API_KEY` slot. For this hackathon the run-and-Connect flow above is simplest and needs no key.

## 6. [both] Run ≥10 discoverability chats + capture the insurance shared-chat URL
**Goal:** clear Fetch's discoverability threshold (~≥10 real interactions) and save a public chat link as demo insurance.
**How discovery works:** your Watcher publishes its Chat Protocol manifest (`publish_manifest=True`, set in the code), so **ASI:One** (asi1.ai) can find and route to it. It becomes reliably discoverable once it has enough real interactions — so you seed those interactions yourself.
**You'll need:** the agents registered (item 5, still running); a free **ASI:One account** at **asi1.ai**.
**Steps:**
1. **Log in to asi1.ai.**
2. Start a chat and get it to your Watcher — search/mention it by name, or paste its **address** (`agent1q…` from item 5 step 7). Send a realistic incident, e.g.:
   > EPG publish failed — missing episode metadata on tonight's schedule.
3. You should get the full flow back: triage → the retrieved documented fix → an **approval request**. Reply **"approve"** and it executes and returns an audit hash + a Jira link. On a repeat of the same incident class it runs under **Standing Approval** (no prompt, ~15 seconds).
4. **Repeat ≥10 times** through the day, varying the wording and the incident. Each real exchange counts toward the bar.
5. Once a conversation is clean end-to-end, click ASI:One's **Share** to produce a **public shared-chat URL**. Save it early as your **insurance link** — if the venue Wi-Fi dies mid-demo, this is your proof the flow works.
6. Near the freeze (item 12 / G4), capture the **final** shared-chat URL — ideally one showing the ~15-second Standing-Approval repeat.
7. Put the URL into the **main** `.env` (`ASI_ONE_SHARED_CHAT_URL` — add the line if absent) and the team thread (N2 needs it for the BUIDL; N1 for the deck).
**Fallback:** if ASI:One routing is flaky at the venue, chat the agent **directly by its address** — document that as the honest fallback in your notes.
**Done when:** ≥10 interactions done and a working public shared-chat URL is saved.

## 7. [both] *(optional)* Invite the 2nd Jira seat
**Goal:** make incident 3's "one person allowed, another denied" split two **real** named people instead of one account changing hats.
**You'll need:** Jira admin access; ~30 min. Skip if short on time — the fallback works.
**Steps:**
1. Jira → **Settings → User management → Invite user** → add a second user to the site.
2. Add that user to role **`10007`** (Rights Ops).
3. Put both users' account IDs into your **local** `.env`: `JIRA_RIGHTS_OPS_ACCOUNT_ID` and `JIRA_SCHEDULING_OPS_ACCOUNT_ID`.
**Fallback (no 2nd seat):** do nothing — the demo flips one account between roles `10007`/`10008`; the build supports this. Note the few-second permission-cache propagation window on stage.
**Watch out:** account IDs go in your **local** `.env` only, never committed.

---

# G1 → G2 — Friday build to freeze

## 8. [both] Coordinate the seed-4207 mutation-corpus hand-off to T1
**Goal:** T3 produces 100 "messy" test tickets; T1 runs its extractor over them to produce one robustness score.
**Steps:**
1. After the vertical slice works (~18:30), check that the T3 session wrote the mutation corpus to its stated path (its final report names the exact file + how to load it — likely `precedent_memory/bench/mutation_corpus.jsonl` or `data/bench/`).
2. Tell the T1 session that file's path and have it run its extractor bench over it.
3. Record the single robustness number it prints — it goes on the on-screen chip, slide 10, the README, and the BUIDL (must be identical in all four).
**Done when:** the one number is recorded and identical everywhere.

## 9. [T3] Run the five-pass secrets scrub (A–E)
**Goal:** prove no secret is anywhere in the repo's history **before** it goes public. Run **all five** — one pass isn't enough. Run from the **main** repo folder. (Also detailed in [`workflows/T3-github-publication.md §3`](workflows/T3-github-publication.md).)
**You'll need:** `gitleaks` (`brew install gitleaks`).
```bash
cd /Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon
```
**A — automated scan:**
```bash
gitleaks detect --source . --log-opts="--all" --redact -v
```
**B — confirm `.env` was never committed** (first two print nothing; third must match a `.gitignore` rule):
```bash
git log --all --full-history -- .env
git log --all --full-history -- ".env.*"
git check-ignore -v .env
```
**C — pattern grep across all history:**
```bash
git log -p --all | grep -nE "(VENICE|JIRA|AGENTVERSE|ASI|KAGGLE|HIGGSFIELD)[A-Z_]*(KEY|TOKEN|SECRET|PASSWORD)[[:space:]]*[=:]" | grep -vE "your-|placeholder|<|CHANGEME|example|\.example|README|CHECKLIST"
```
**D — literal-value scan** (searches history for the actual values in your current `.env`; prints only variable NAMES, never values):
```bash
while IFS='=' read -r k v; do case "$k" in \#*|"") continue;; esac; v="${v%\"}"; v="${v#\"}"; [ "${#v}" -lt 12 ] && continue; if [ -n "$(git log -S"$v" --oneline --all)" ]; then echo "LEAK in history: $k"; fi; done < .env
```
**E — sweep committed dumps/evidence for auth headers** (the `docs/compliance` model dumps should be clean):
```bash
grep -rInE "(Bearer [A-Za-z0-9._-]{16,}|api[_-]?key\"?[[:space:]]*[:=][[:space:]]*\"?[A-Za-z0-9]{16,})" docs/ data/ --include="*.json" --include="*.md" | grep -viE "example|placeholder"
```
The T3 session can help you read a hit ("variable name or real value?"), but **you make the final call.**
**If a real leak is found:** (1) **rotate that key immediately** on the vendor dashboard — a rotated key in history is dead. (2) If it's in history, excise it with `git-filter-repo`, but **only with T1's OK** (it rewrites history; everyone re-clones). (3) Re-run A–D. **The repo does not go public until clean.**
**Done when:** all five pass clean, and you've added one line to `docs/evidence/README.md` (e.g. "gitleaks vX.Y full-history + literal-value scan: clean; .env never committed (verified)").

## 10. [T3] Flip the main repo public
**Goal:** make the repo public — a Fetch hard gate, and what unblocks the DoraHacks draft and the deck.
**Pre-flight (all must be true):**
- [ ] Item 9 scrub clean
- [ ] README has **run instructions** (if `make sim` / `make demo-reset` are still stubs, ping T1/T2)
- [ ] Fetch badges on each agent's README section
- [ ] `LICENSE` exists; data-attribution lines present (UCI CC BY 4.0, TVmaze CC BY-SA, Kaggle CC0)
- [ ] `git status` shows `.env` is **untracked**
**Steps:**
1. GitHub → your main repo → **Settings → General → Danger Zone → Change repository visibility → Make public** → type the repo name to confirm.
2. Open the repo URL in an **incognito** window; confirm the README, `docs/compliance/`, and `data/analysis/` all load logged-out.
3. Post the public URL in the team thread; update the BasedAI PR README's "public soon" line to the real URL.
**Done when:** the repo loads logged-out and the URL is shared.

## 11. [T3] Announce each gate + URLs in the team thread
**Goal:** N1's deck and N2's DoraHacks packet are blocked waiting on your links.
**Steps:** as each lands, post the **public repo URL**, the **BasedAI PR URL**, and the path **`precedent_memory/bench/RESULTS.md`**.
**Done when:** all three posted.

## 12. [T3] Commit the measured bench numbers into the PR (before Fri 21:00)
**Goal:** the PR must never be numbers-free once the benchmarks exist.
**You'll need:** the T3 session's `precedent_memory/bench/RESULTS.md`.
**Steps:**
1. In your fork (`~/basedai-hackathons`), open `UK-AI-Agent-EP5/submissions/precedent/README.md`.
2. Replace `[[WAIT:BENCH-SYNTH]]` / `[[WAIT:ATTACKS]]` / `[[WAIT:BENCH-CURVE]]` with the measured 10-metric table + the "N of 6 attacks" result + the mutation number. State explicitly that FNR is graded by an **independent oracle**.
3. Commit + push:
   ```bash
   cd ~/basedai-hackathons && git add UK-AI-Agent-EP5/submissions/precedent && git commit -m "Precedent — measured benchmark results" && git push
   ```
4. Re-check "Files changed" touches **only** your team folder.
**Watch out:** if a metric wasn't measured, **remove that row** — never leave a bracket or "coming soon." A row without a real pass/fail is worse than no row.
**Done when:** the PR shows real numbers and only touches your folder.

## 13. [T3] Freeze the DoraHacks one-shot organizer answers (with T1 sign-off)
**Goal:** the organizer questions on the BUIDL form **lock permanently** when you submit the draft — get them perfect first.
**You'll need:** the team's DoraHacks login; event **2272**.
**Steps:**
1. Open the BUIDL form for event **2272** **but do not submit.**
2. Copy every organizer question **verbatim** into a file under `docs/evidence/`, and screenshot the form.
3. The T3 session drafts answers; you resolve every `[NEEDS-FACT]` marker (never delete one silently).
4. Get **T1 to sign off on every answer.**
**Done when:** every answer is final and T1-approved, saved in `docs/evidence/`.
**Watch out:** you cannot edit these after the draft submits. Improvising at the form is unrecoverable.

---

# G3 — After the repo is public

## 14. [T3] Submit the DoraHacks BUIDL draft (event 2272)
**Goal:** enter the Conduct + Fetch tracks (the BasedAI PR is the separate BasedAI entry).
**You'll need:** repo public (item 10); answers frozen (item 13).
**Steps:**
1. In the BUIDL form, paste the signed answers **character-for-character**.
2. Tick **exactly three** bounties — **1370, 1367, 1364** (confirm the labels on the form). **Deselect** any pre-selected extras — irrelevant ticks dilute the story.
3. Incognito link-check; Ctrl-F for `‹` and `XX` to catch leftover placeholders.
4. Submit the draft. Screenshot the submitted state; post to the thread.
**Done when:** the draft is submitted with exactly those three bounties and clean links.

---

# G4 → G6 — Saturday

## 15. [T3] Run the UCI 25k realism run + live drift/TTC
**Goal:** show the benchmark against a realistic-size store and a **live** Jira permission flip — what a synthetic-only competitor can't do.
**You'll need:** live Jira creds in your **local** `.env`. The T3 session built the commands (they refuse to run unconfigured).
**Steps:**
1. Run the realism command → produces a P99 for the ~25k-record store. In every caption say **"25k-record store"** — **never "141k events."**
2. Run the live drift/TTC command → it flips Jira role membership (`10007`/`10008`) or issue-security (`10000`/`10001`) and times how fast the deny propagates, reading the timestamp from Jira's own audit log (`/rest/api/3/auditing/record`), not the client clock.
3. Paste the numbers as a **comment** on the BasedAI PR.
**Done when:** realism P99 + drift/TTC captured with correct captions.

## 16. [T3] Push the BasedAI PR final
**Goal:** PR is judging-ready — video + measured numbers, re-scrubbed.
**Steps:**
1. Paste the demo **video URL** (from N2's unlisted upload) into the README/RESULTS, replacing `[[WAIT:VIDEO-LINK]]`.
2. Add any late realism number.
3. **Re-run gitleaks on the fork** (it has your commits too):
   ```bash
   cd ~/basedai-hackathons && gitleaks detect --source . --log-opts="--all" --redact
   ```
4. If BasedAI's repo moved, rebase onto it:
   ```bash
   git remote add upstream https://github.com/BasedAICo/hackathons.git 2>/dev/null; git fetch upstream && git rebase upstream/main
   ```
5. Confirm "Files changed" is only your folder; comment on the PR: **"Final for judging — video + measured benchmarks included."**
**Done when:** PR clean + complete, final-ready comment + URL posted to the thread.

## 17. [T3] Final DoraHacks submit (before 23:59 BST / 22:59 UTC Sat 4 Jul)
**Goal:** the actual final submission.
**Steps:**
1. In the BUIDL, paste the video URL + any late number.
2. Re-run the pre-submit checklist (links open logged-out; no `‹`/`XX`).
3. Submit. Screenshot. Commit the final page text + locked answers to `docs/evidence/dorahacks-buidl.md`.
**Watch out:** finish **hours** early — never rely on the last hour.
**Done when:** final submission confirmed with a screenshot.

## 18. [both] Watch for the Demo-Day presenter announcement
**Goal:** react to whether you're selected to present live (announced ~22:00 Friday onward).
**Steps:**
1. Watch Discord/email for the presenter list.
2. **If selected:** the team runs the live demo (P1 speaks, P2 clicks approvals — a different person clicking is itself the segregation-of-duties story).
3. **If not selected:** redirect Saturday energy to the no-stage surfaces — 90-second cut first on the BUIDL page, README/deck polish, harden the hosted-Watcher + ASI:One links judges click. Post the outcome; T1 owns the branch decision.
**Done when:** the team knows its path and has acted on it.

---

## Appendix — the open-weight declaration (for the PR README)

BasedAI requires you to declare every model and prove it's open-weight. Paste this shape into the PR README, filling the **exact pinned IDs** from `precedent/models.py` / `docs/compliance/venice-models-2026-07-03.json`:

> **Models (all open-weight, Venice-served, verified against public HuggingFace weights):**
> - **FAST / SMART / HEAVY chat:** Qwen3.5-35B-A3B (Apache-2.0), DeepSeek-V4-Flash (MIT), DeepSeek-V4-Pro (MIT)
> - **EMBED:** BGE-M3 (MIT)
> - No closed/proprietary model is in the loop. Eligibility evidence: `/models` catalog dumps in `docs/compliance/` show each pinned id's `modelSource` as a `huggingface.co` URL.

**The six attack names (verbatim, for the PR + RESULTS.md):** query inference · metadata bypass · timing attack · collection attack · prompt injection · derived-memory attack.

**The ten bench metrics + thresholds:** FNR <0.1% · FPR <2% · P50 <50ms · P99 <200ms · end-to-end overhead <100ms · derived-memory correctness >99% · ACL drift <0.5% · time-to-consistency <5min · audit coverage 100% · O(1)/O(log n) latency-vs-size curve.
