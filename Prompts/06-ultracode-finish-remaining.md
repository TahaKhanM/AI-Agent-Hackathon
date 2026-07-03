# Ultracode session prompt — Finish Precedent's remaining buildable work (post T1+T3 merge)

> **Target model:** Claude **Opus 4.8**, `ultracode` (multi-agent Workflow orchestration, highest reasoning effort). Paste the whole of the section below **"PROMPT — paste from here"** as the first message of a fresh Claude Code session opened in this repo's root. The leading `ultracode` keyword opts the session into Workflow orchestration; optionally append a token-budget directive (e.g. `ultracode +800k`).
>
> **Before you start (human checklist):**
> - Work happens on `main`, which now carries the **merged T1 + T2 + T3** product (Checkpoint 1, tag `checkpoint-1-t1-t3-merged`, merged SHA `02e9f7f`, checkpoint commit `ee432e4`). The full evidence is in `docs/checkpoints/CHECKPOINT-1-T1-T3-MERGE.md` — read it first; it is the definitive record of what is already done and verified green so you do not redo it.
> - `.env` is populated per `CREDENTIALS-CHECKLIST.md` (Venice / ASI:One / Agentverse / Jira keys) and **never committed**. The session runs **airplane-first**: it builds and tests everything offline, and makes at most the ONE live Venice round-trip (plus the live `/models` open-weight guard) that proves the client — no other live calls; account-level acts are human steps.
> - **Reality note (verified 3 Jul 2026):** the GitHub repo is **already public** and an **external git auto-sync on the machine pushes local `main` commits to origin without an explicit `git push`** (the merge commit auto-pushed at 23:13). So "commit locally, don't push" does **not** keep work off the public remote. This session must not itself push or flip visibility; if you need to stage work you don't want public yet, do it on a side branch and tell the human. gitleaks was clean at the merge — no secret is exposed — but be deliberate about what lands on `main`.
> - This prompt was written against the **re-verified merged state** by the merge/checkpoint session — the contracts, schema, model registry, and T2 API are FROZEN. You finish the remaining buildable work; you do not redesign anything.

---

## PROMPT — paste from here

# MISSION: Finish all remaining buildable work on Precedent (post T1+T3 merge)

You are a fresh Claude **Opus 4.8** "Ultracode" session with multi-agent **Workflow** orchestration at the highest reasoning effort. Precedent's two build lanes (T1 core-loop/sim/agents, T3 bench/submissions) are **merged onto `main` and verified green** (Checkpoint 1). Your job is to **finish every remaining buildable item** — the integration gap the merge left open, the ambition-ladder stretches, and the N1/N2 submission + demo content — ending with a step-by-step human walkthrough of the account-bound acts your work unblocks.

This is a hackathon entry whose eligibility depends on four hard rules that are trivial to violate by accident and **eligibility-fatal** to get wrong. **Read this entire prompt before writing a line of code.** Evidence before assertions — you run every verification yourself and paste the actual command output before claiming anything is done.

Work on `main` (the merged product). **Do not push to origin and do not flip repo visibility** — those are human acts (and note the auto-sync caveat above). Commit as you go with the repo's `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` trailer.

---

## STEP 0 — Load context + re-verify the merged state (mandatory, in this order)

1. **Invoke the `precedent` project skill FIRST** (via the Skill tool). It encodes the four hard rules, the build-plan gate discipline, and the working conventions. Do this before touching any file.
2. Read the authoritative context, in this order:
   - `.claude/skills/precedent/SKILL.md` (rules + conventions)
   - `docs/checkpoints/CHECKPOINT-1-T1-T3-MERGE.md` (**what is already done and green — do not redo it**; it names the known-open items you are here to finish)
   - `Plan/BUILD-PLAN.md` — §5 the ambition ladder (floor → stretch → reach) and §5.1 the cut order; §4 the per-person missions
   - `EXPLAINER-idea-and-plan.md` and `EXPLAINER-roles.md` (the "why", the moat, the demo narrative)
   - `Prompts/03-ultracode-t1-completion.md` and `Prompts/04-ultracode-t3-completion.md` (the bar these lanes built to — inherit their style, rigour, and rule discipline; the class-key registry, the seed-4207 decision, the ten metrics, the oracle-independence rule)
   - `Research/00-verified-claims.md` (**every number carries its caveat from here** — you are the number-honesty owner for all shipped copy)
   - `Idea/refinement/03-pitch-deck.md` + `Idea/refinement/CONTEXT-deck-build-brief.md` (the deck spec + the self-contained build brief), `Plan/prep-spec.md` (the demo-prep deliverables), and `Plan/workflows/*` (the per-task briefs the content lanes implement to)
   - `Prep/submissions/{BASEDAI-PR-README.md, DORAHACKS-WORKSHEET.md, README.md, SCRUB-AND-PUBLISH-CHECKLIST.md}`, `docs/MUTATION-CORPUS-HANDOFF.md`, `docs/evidence/{README.md, T2-EVIDENCE-LEDGER.md, T3-AGENTS-VERIFICATION.md}`, `docs/compliance/*.json`
3. **Re-verify the merged state with your OWN commands before building** (do not trust this prompt; a red baseline invalidates the plan):
   - `git describe --tags` shows `checkpoint-1-t1-t3-merged`; `git log --oneline -3` shows the checkpoint commit atop the T3 merge commit.
   - `make check-open-weight` → clean (only `precedent/models.py` names ids).
   - `make test` → **161 passed** (0 skipped/xfailed).
   - `make bench` → 6/6 attacks, FNR `0 leaks / 5,219 deny-expected`; correctness byte-identical to the committed `precedent_memory/bench/results.json` (latency-only drift), then restore the file.
   - `make secrets-scan` → gitleaks clean; `.venv/bin/ruff check .` → clean.
   - Boot the demo (`make demo-reset` + `make sim`, real file DB via `PRECEDENT_MEMORY_DB`) and drive `POST /api/drive/1|2|3` — resolve / resolve(fast, near-instant) / refused, no restricted-body leak.
   Paste each result. If any is red, STOP and fix-forward before starting B1.
4. **Do NOT relitigate settled design.** Contracts, schema, model registry, and the T2 API are FROZEN. Implement *to* them; do not add columns, rename tokens, or fork an identifier.

---

## THE FOUR HARD RULES (as they bite finishing work — each is eligibility-fatal)

**Rule 1 — Open-weight only.** A closed/proprietary model id may appear in **`precedent/models.py` and nowhere else**. `make check-open-weight` is the guard, but it does **not** scan `tests/` or data files — so before ANY commit, also grep the whole tree (including `tests/`, `data/`, and `precedent_memory/bench/mutation_corpus.jsonl`) for the guard's closed-model-id patterns by hand, and confirm the only hits are the guard pattern itself inside enforcement tests, `precedent/models.py`, the `docs/compliance/*.json` catalog evidence, and rule-describing prose. Resolve every model by role (`FAST`/`SMART`/`HEAVY`/`EMBED`) via `precedent.models`. `PRECEDENT_DEV_MODELS` / `ALLOW_PROPRIETARY_DEV` stay UNSET. **Every artifact you author for a public surface (deck PDF, PR README, BUIDL copy) must itself be closed-model-id-clean.**

**Rule 2 — No LLM in the decision.** The deterministic policy engine + human identity decide; the model only proposes. This bites hardest in **B1**: the live Watcher handler you wire must run the SAME deterministic kernel (`orchestrator.prepare` / `commit_execution`) — an LLM reply must never gate execution or set a risk class. The STANDING fast-path stays zero-`chat()`/`embed()`; `precedent_memory/retrieve.py` stays LLM-free; the class match stays extractor-confirmed fingerprint equality. Gate B1 with a test that spies `venice.chat`/`venice.embed` and fails if either is invoked on the standing path.

**Rule 3 — Fail-closed.** Restricted memory is denied when ACL freshness is uncertain; a stale cache may narrow access, never widen it. On the live Watcher path (B1) the refusal must disclose only `denied_count` + `denied_owner_team` — never a title, symptom, body, or secret. The `live-drift` / `bench-uci` CLIs stay non-zero when unconfigured. Preserve the fail-closed behaviour end-to-end; never add a bypass that serves a restricted body.

**Rule 4 — No secrets.** `.env` is gitignored; `.env.example` holds placeholder names only. Never inline a key, token, seed, `accountId`, or a teammate's real name into code, a commit, a slide, the PR/BUIDL, or a prompt you send to a sub-agent. `make secrets-scan` must stay clean. Agent seeds are read from env at runtime, never inlined. The one credit/redemption code the human needs (`UKAIAGENTUKAIAGENTAV`, in the walkthrough) is a promo code, not a secret — everything credential-shaped stays out.

If any task appears to require breaking one of these, **STOP and find the compliant path** — there always is one.

---

## PRIORITY-ORDERED WORK PLAN (dependency-ordered; each step names its verification)

Order is load-bearing: **integration hardening (B1–B5) first → then the ambition-ladder items → then N1 buildable content (B6–B7) → then N2 buildable content (B8–B10) → then demo-prep (B11) → then the conditional selection features (B12).** If the clock bites, obey `Plan/BUILD-PLAN.md` §5.1 cut order (cut stretch in reverse priority; never cut incidents 1+2, the Fetch hard gates, the capture session, or the vertical slice). B6/B8 consume B2/B3's outputs — build the hardening first.

### B1 — Wire the standalone Watcher's live Chat Protocol to the full loop (T1)  [integration hardening]
The default `watcher` singleton and `scripts/run_agents.py`'s Bureau are built with the DEFAULT echo reply: `build_chat_protocol(reply=None)` returns `"Precedent Watcher received: {text}"`, and `scripts/run_agents.py` builds the Watcher bare — so an ASI:One chat to the registered Watcher **echoes**, it does not run the loop. All the pieces exist and are unit-tested individually: `agents/watcher.py::{triage_incident, render_approval, make_decision}`, the approval ledger `agents/approval.py` (`record_pending`/`lookup_pending`/`expire_stale`/`mark`), the deterministic kernel `precedent/orchestrator.py::{prepare, commit_execution}`, and the Operator `agents/operator.py::serve_execution`. The full loop is composed today **only** in `scripts/demo_server.py`. **Compose the same pieces into a live `on_message` chat handler** so an ASI:One chat runs: report → ONE formatted `ChatMessage` (triage + fix + risk + rollback + Jira link, `expires_at = requested_at + 600s`) → a reply matching approve/reject becomes an `ApprovalDecision` with `approver_principal = ctx.sender` → execute + close + reply with the audit hash + hop-trail footer. The repeat-class turn runs under Standing Approval with the ~15 s timer quoted and no prompt. All helpers exist — only the wiring is missing; do not rebuild them.
*Verify:* a scripted local dry-run drives the handler through the full loop (report→one-message→approve→execute→audit-hash reply); the echo path is gone from the registerable Watcher; a test spies `venice.chat`/`venice.embed` and asserts zero calls on the standing branch (Rule 2); a refusal path discloses only count + owner team (Rule 3); dropped-mid-approval expires to non-action and re-presents on reconnect.

### B2 — Re-run the bench + attacks + audit-coverage on merged main and propagate figures (T3-13)  [hardening]
Checkpoint 1 already confirmed the bench correctness is byte-identical on merged main (FNR `0/5,219`, FPR `0/4,781`, 6/6 attacks, P99 ~0.5 µs) with the committed frozen files preserved. Re-confirm (`make bench` + `pytest tests/test_adversarial.py tests/test_audit_coverage.py precedent_memory/tests/test_oracle.py`), then **propagate the measured 10-metric table + 6/6 attack results into `Prep/submissions/BASEDAI-PR-README.md`**, replacing its bench placeholders and leaving only the `[[WAIT:VIDEO-LINK]]` / `[[WAIT:MENTOR-ANSWER]]` sentinels. State oracle-independence explicitly. Load-bearing predecessor for the deck slide-10 fill (B6) and the BUIDL numbers (B8).
*Verify:* all suites green; `precedent_memory/bench/RESULTS.md` correctness byte-identical to the committed `results.json`; the PR-README table matches the committed bench exactly; `grep '‹' Prep/submissions/BASEDAI-PR-README.md` empty.

### B3 — Run the seed-4207 mutation corpus against the merged extractor → the ONE robustness number (T3→T1 hand-off)  [hardening]
The corpus + loader exist (`precedent_memory/bench/mutation_corpus.jsonl`, 100 records; `from precedent_memory.bench.mutations import load_corpus`; see `docs/MUTATION-CORPUS-HANDOFF.md`). Run T1's frozen deterministic extractor (`precedent/extractor.py`) over the corpus and produce the single robustness triple: **correct-match / safe-degrade / false-fast-path** rate. This number does not exist on any surface yet; it must appear **identically** on all four: the on-screen robustness chip (console), deck slide 10, the README first screen, and the BUIDL page. Write the run as a committed script + a small test so it replays byte-identically.
*Verify:* two runs at seed 4207 produce the identical triple; a test asserts the false-fast-path rate is 0% (an `llm_proposed`/`None` extraction can never unlock the fast-path — Rule 2); the number is recorded once in a single source-of-truth the four surfaces cite.

### B4 — Fix the Makefile `help:` block + freeze-check grep scope (merge cosmetic)  [hardening]
The `help:` block still advertises `sim`/`demo-reset`/`bench` as `(TODO: T1/T2)`/`(TODO: T3)` though all three are implemented — update those echo lines to match reality. Scope `freeze-check`'s final `grep -rn '‹' Plan Idea docs` to shippable surfaces (deck / README / BUIDL per `Prompts/04` §4.3), or widen its exclusion list, so it stops exiting 1 on the ~10 legit `‹…›` mail-merge/template tokens in `Plan/` docs.
*Verify:* `make help` shows no `(TODO)` for implemented targets; `make freeze-check` exits 0 on the clean tree (open-weight + test + secrets + the scoped placeholder grep all pass).

### B5 — Verify the temporal-embargo bench test exists/passes post-merge (T3 stretch)  [hardening]
Confirm the `unlock_at` temporal-embargo predicate is exercised by a bench/oracle test on merged main and is green (per `BUILD-PLAN` §5 stretch item 3 — a bench-test + Q&A/README claim, **not** a stage beat). If absent, add a deterministic test that a record embargoed until `unlock_at` denies before and allows after, graded by the independent oracle.
*Verify:* the test is present and green; it is graded by `oracle.py` (no self-grading); it does not add a fifth on-stage concept.

### B6 — N1 pitch deck (12 core + 9 appendix slides)  [N1 content — consumes B2, B3]
Build the deck from `Idea/refinement/03-pitch-deck.md` + `Idea/refinement/CONTEXT-deck-build-brief.md` (the self-contained brief — obey its self-narration-band adaptation and its export sequence). Fill slide-10 P99 + the extractor robustness cells from `precedent_memory/bench/RESULTS.md` (B2) and the mutation run (B3); **bake REAL values into the PDF export — never a placeholder** (apply the degraded rule: delete a cell rather than ship `‹XX›`/`[[WAIT]]`). Add the self-narrating grey caption/narration layer, the "What exists Monday morning" PDF-only appendix slide, and a screenshot of the REAL Promote/Revoke console buttons for slide 7. Commit both PDFs to `docs/submission/`.
*Verify:* `grep '‹'` and `grep '[[WAIT'` over the exported PDFs → zero; every number traces to `data/analysis/` or `Research/00-verified-claims.md` with its caveat; calendar (18.2h) vs business (8.85h) never blended; vendor-claimed superscripts present; L3 labelled "Standing Approval" never "Autonomous"; both PDFs committed.

### B7 — N1 provenance/licence layer + KB integrity review  [N1 content]
Write the README data-provenance table + attribution lines (UCI CC BY 4.0, TVmaze CC BY-SA, Freeview XMLTV, CC0 Kaggle Netflix/Disney+) and the TMDB/IMDb-rejected diligence sentence (per `Plan/workflows/N1-licence-attribution.md`). Then the honest-data gate: verify each of the ~10 KB articles in `data/kb/` has a real `adapted_from` URL, the correct ACL (`rights-ops-only` on KB-0004/KB-0005), and correct stale/escalate flags; and that `data/raw/` kept its messiness (nulls, duplicate titles, fuzzy-match failures) unsanitised.
*Verify:* every `adapted_from` URL resolves; ACL/stale flags match the canonical registry and the refusal beat; a diff shows the raw data still carries its nulls/dups; the provenance table is committed.

### B8 — N2 submission scaffolding  [N2 content — consumes B2, B3]
Polish `Prep/submissions/BASEDAI-PR-README.md` into submit-ready copy: the measured bench table (from B2), the six attack names verbatim, `docs/compliance/` cites, the pinned open-weight ids **pasted byte-for-byte from `docs/compliance/` / `precedent/models.py`** (never retyped), leaving only the two `[[WAIT:…]]` sentinels. Turn `Prep/submissions/DORAHACKS-WORKSHEET.md` into submit-ready BUIDL copy (event `2272`, bounties `1370`/`1367`/`1364`) with every `[NEEDS-FACT]` resolved (the extractor robustness number from B3). Assemble the Fetch deliverables checklist (badges present on each agent README, the three profile URLs to fill, the shared-chat URL slot).
*Verify:* `grep -n '\[NEEDS-FACT' Prep/submissions/DORAHACKS-WORKSHEET.md` → empty; exactly the three bounty ids present; the PR-README ids diff byte-identical against `docs/compliance/`; no closed-vendor keys in the Venice-only `.env.example` section; both drafts closed-model-id- and secret-clean.

### B9 — N2 video shot-list + VO script + assembly plan  [N2 content]
Build (per `Plan/workflows/N2-video-edit.md` + `Idea/refinement/04-demo-and-video-script.md`): the shot list + captions (`25k-record store`, the calendar-hours label, no unlabelled vendor claim), the 30-second teaser plan, the not-selected 90-second cut plan, the shared-folder naming convention, the manual-loop 8× time-lapse "8h51m" VO script, and the naive-user playtest grading rubric (TRIAGED / DEGRADED / CONFUSED, per `Plan/workflows/N1N2-demo-playtest.md`). Capture is a manual human step; the plans and scripts are buildable now.
*Verify:* the shot list captions obey the number-honesty labels (B10); the 30s/90s cuts preserve the two memorable lines; the VO script's "8h51m" is the business-hours figure, never blended with 18.2h calendar.

### B10 — N2 QA number-honesty pass  [N2 content — gates B6/B8/B9]
Cross-check every on-screen/in-caption number against `Research/00-verified-claims.md` + `data/analysis/`: enforce NEVER-BLEND (18.2h calendar vs 8.85h / 8h51m business, never averaged); vendor `(vendor-claimed)` labels; `25k-record store` (24,918 incidents) never "P99 over 141k events"; existence-vs-symptom (94.4% vs 98.6%), naive-floor (59.4%/87.7%), and inverted-stat (`knowledge=true`) labels correct; no refuted Komodor/Klaudia claim used. Run the pre-export `‹`-grep on shippable surfaces; wire the logged-out link-sweep checklist.
*Verify:* a written number-honesty audit maps each shipped number → its source row + caveat; zero refuted claims; zero `‹`/`[[WAIT]]` on any exported surface.

### B11 — Demo-prep artifacts from `Plan/prep-spec.md`  [demo-prep]
Build the demo run-of-show (live + recorded variants), the 5 per-person crib sheets (`Prep/crib-sheets/` is empty except `.gitkeep`), the systems walkthrough, the rehearsal-gate checklist (per `Prompts/04` §4.3 / `Plan/workflows/N1-rehearsal-runner.md`), and the airplane-mode rehearsal script.
*Verify:* all five `prep-spec` deliverables exist and are committed; the rehearsal-gate checklist encodes the two-failures→narrated-recording rule; the airplane-mode script boots the slice with Wi-Fi off.

### B12 — Selection-branch console features (conditional — build ONLY if selected to present)  [reach]
Per `BUILD-PLAN` §5 selection-branch item: the attract-mode idle loop (console resolves seeded background incidents from doors-open) + the live RESTRICT hotkey (keypress → live Jira ACL flip → dual-enforcement deny → restore) + the REACH change-record artifact (one hotkey renders the audit trail as an ITIL-style change document). **Conditional on the ~22:00 Fri presenter-selection announcement.** Pre-stage BOTH branch outputs (selected → these features; not-selected → the RESTRICT flip becomes a video insert); the human calls the branch.
*Verify:* if built, the RESTRICT hotkey drives a real Jira-shaped ACL flip → deny → restore with no restricted-body leak; the change-record renders from real audit rows; both branch outputs are staged so the human's call is one switch.

---

## MULTI-AGENT + TDD + ADVERSARIAL-VERIFICATION STRATEGY (use the Workflow tool — maxed out)

- **Respect the dependency DAG.** Integration hardening **B1–B5 before** any content; **B6 and B8 consume B2/B3's outputs** (the bench table + the robustness number); **B10 gates B6/B8/B9** (number-honesty). Fan out independent items to parallel implementer sub-agents in **git worktrees** (`superpowers:using-git-worktrees`) so they don't collide — but note the auto-push caveat: keep un-public staging on side branches, and only the human pushes.
- **TDD per module** (`superpowers:test-driven-development`): write the failing test that encodes each step's verification, then implement to green. B1's "test" includes the venice-spy zero-LLM assertion and the fail-closed refusal assertion; B3's includes the false-fast-path=0% assertion; B5's is the temporal-embargo deny-before/allow-after.
- **A dedicated RED-TEAM pass** (`superpowers:requesting-code-review` + `superpowers:verification-before-completion`) that re-runs the guards on the finished tree from scratch: `make check-open-weight` + a manual whole-tree grep incl. `tests/`; `make secrets-scan`; `make test`; `make bench` (correctness byte-identical, oracle import-independent); the airplane-mode slice (fast-path provably zero-LLM via a spy); and **a number-honesty auditor** that re-checks every shipped number against `Research/00-verified-claims.md` with its caveat. If the red-team disagrees, the disagreement wins — fix-forward and re-run.
- **Never claim done without running the command.** Paste the actual output. A green claim without pasted output is not green.

---

## ACCEPTANCE CHECKLIST (run these yourself; paste evidence)

- [ ] Merged state re-verified green (`checkpoint-1-t1-t3-merged` present; `check-open-weight` / `test` 161 / `bench` 6/6 FNR 0/5,219 / `secrets-scan` / `ruff` all clean; demo drive 1/2/3 exercised)
- [ ] **B1** live Watcher handler runs the full loop (report→one-message→approve→execute→audit-hash reply); echo path gone; venice-spy proves zero-LLM on the standing branch; refusal discloses only count + owner team
- [ ] **B2** bench re-confirmed byte-identical; measured table propagated into `BASEDAI-PR-README.md`
- [ ] **B3** seed-4207 extractor robustness triple produced, replays byte-identically, false-fast-path = 0%, staged as one source-of-truth for the four surfaces
- [ ] **B4** `make help` accurate; `make freeze-check` exits 0
- [ ] **B5** temporal-embargo bench test present + green (oracle-graded)
- [ ] **B6** deck (12 core + 9 appendix + PDF slide) with REAL numbers baked in, zero `‹`/`[[WAIT]]`, both PDFs committed
- [ ] **B7** provenance/licence table + KB integrity (real `adapted_from`, correct ACL/stale flags, preserved messiness)
- [ ] **B8** PR-README + DoraHacks worksheet submit-ready (ids byte-for-byte, six attacks, only the two `[[WAIT]]` sentinels, `[NEEDS-FACT]` resolved, three bounties)
- [ ] **B9** video shot-list + VO + 30s/90s cut plans + playtest rubric
- [ ] **B10** number-honesty audit written; zero refuted claims; NEVER-BLEND enforced
- [ ] **B11** run-of-show + 5 crib sheets + systems walkthrough + rehearsal-gate + airplane-mode script
- [ ] **B12** (conditional) selection-branch features pre-staged both ways
- [ ] Four hard rules re-verified on the finished tree (whole-tree closed-model-id grep incl. `tests/`; secrets clean; no LLM in the decision on the B1 path; fail-closed preserved)
- [ ] Nothing pushed to origin **by this session** and repo visibility not changed by this session

## DEFINITION OF DONE

This session is done when: the merged state was re-verified green before building; the standalone Watcher's live Chat Protocol runs the full deterministic loop with a provably zero-LLM standing fast-path and a fail-closed refusal (B1); the bench is re-confirmed byte-identical and its measured table + the seed-4207 robustness number are propagated to every surface that cites them (B2/B3); the Makefile `help`/`freeze-check` are accurate (B4) and the temporal-embargo bench test is green (B5); the deck (B6), provenance/KB integrity (B7), PR-README + BUIDL worksheet (B8), video plan (B9), number-honesty audit (B10), and demo-prep artifacts (B11) are built and committed with every shipped number traced to `Research/00-verified-claims.md` and zero placeholders; the conditional selection-branch features are pre-staged both ways (B12); an independent red-team pass re-ran every guard and the number-honesty audit and agreed; and the four hard rules hold on the finished tree — with every claim backed by pasted command output. Do not push, do not flip visibility, do not relitigate the frozen contracts/schema/models/T2 API.

**Begin by loading the `precedent` skill, then re-verifying the merged state.**

---

## CLOSING MANUAL WALKTHROUGH — hand this to the human (the account-bound acts B's work unblocks)

Everything above is automated to a single human action. These remaining steps are account-bound (no token wired by design) and only you can do them. Delineated by gate; each is reduced to one click/paste with the exact command/file.

**G0 (kickoff / ratify):**
1. **Ratify seed `4207`** at stand-up as the shared constant binding T1's incident generator to T3's corpus (or override — both change together via the one `precedent_memory/bench/seed.py::CANONICAL_SEED` constant). Confirm the T1–N2 named-person mapping onto the workstreams.

**Fetch / Agentverse (unblocked by B1):**
2. **Deploy + register the three Fetch agents** (Watcher/Librarian/Operator) on Agentverse as MAILBOX agents using the **stable env seeds** already wired (so the address survives the B1 handler swap); confirm both README badges render; capture the 3 profile URLs; fill the empty `.env` IDs.
3. **Run ≥10 ASI:One discoverability chats through the (now B1-wired, deployed) Watcher** and **capture the insurance shared-chat URL** early; fill `ASI_ONE_SHARED_CHAT_URL`. This is the artifact that proves the core use case works inside an ASI:One conversation with no custom frontend.
4. **Deploy the hosted degraded-L0 Watcher** (answers a described incident at L0 without MediaCo creds) for the post-hackathon bonus.
5. **Redeem the Agentverse credit code** `UKAIAGENTUKAIAGENTAV` on your Agentverse account.

**Live proofs (fail-closed until configured):**
6. **One live Venice round-trip + the live `/models` open-weight guard** using the `.env` keys (proves the client + the catalog is open-weight).
7. **Wire the real `JiraPermissionSource` client + seed the issue-security levels** on MEDIA-113/114; optionally invite the 2nd Jira seat and fill `JIRA_RIGHTS_OPS_ACCOUNT_ID` / `JIRA_SCHEDULING_OPS_ACCOUNT_ID` locally (never committed) — else use the single-account role-flip fallback.
8. **Saturday: the UCI 25k realism run + live Jira drift/TTC** (`make bench-uci`, `make live-drift`) with local `.env` creds — caption "25k-record store", never "141k events"; the flips read timestamps from Jira's `/rest/api/3/auditing/record`. Paste values as a PR comment.

**Publication + submission (human / account acts):**
9. **Authorize + perform the origin push** of the checkpoint tag + commit: `git push --follow-tags origin main`. *(Note: an auto-sync already pushed `main` up to the merge commit; this push adds the checkpoint commit + the `checkpoint-1-t1-t3-merged` tag.)*
10. **Run the A–E secrets scrub** (`Prep/submissions/SCRUB-AND-PUBLISH-CHECKLIST.md`) and **confirm repo visibility**. *(The repo is already public — verify logged-out in incognito that no secret is exposed; if the scrub finds a leak, rotate the key on the vendor dashboard FIRST, then `git-filter-repo` with T1's OK.)*
11. **Open the BasedAI fork PR** (fork `github.com/BasedAICo/hackathons` → copy the template → paste the B8-drafted README + Venice-only `.env.example`) and **ask a BasedAI mentor which deadline governs**; replace `[[WAIT:MENTOR-ANSWER]]` and, Saturday, `[[WAIT:VIDEO-LINK]]`.
12. **Submit the DoraHacks BUIDL** (event `2272`, tick exactly bounties `1370`/`1367`/`1364`). The organizer answers **lock at draft-submit** — get T1 sign-off on EVERY answer first; enter them character-for-character; incognito link-check; submit well before 23:59 BST / 22:59 UTC.

**Demo + outreach:**
13. **Capture the demo video** against the frozen build (real screen recordings; the B9 shot-list/VO/captions).
14. **Practitioner outreach** (10 warm sends, the change-board question) — a real reply becomes the slide-12 validation line, **or the line is deleted**, never faked.
15. **Watch the ~22:00 Fri presenter-selection announcement and call the B12 branch** (selected → attract-mode + RESTRICT hotkey; not selected → the RESTRICT flip becomes a video insert + the 90-second cut first on the BUIDL page).

For each: the agent prepared everything to a single human action; the account-level act stays human.
