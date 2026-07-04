# Ultracode session prompt — Code excellence pass (post Checkpoint 2)

> **Target model:** Claude **Opus 4.8**, `ultracode` (multi-agent Workflow orchestration, highest reasoning effort). Paste the whole of the section below **"PROMPT — paste from here"** as the first message of a fresh Claude Code session opened in this repo's root. Optionally append a token-budget directive to the first line (e.g. `ultracode +800k`).
>
> **Before you start (human checklist):**
> - This prompt was authored 4 Jul 2026 from a four-agent critical analysis (Conduct core-loop, Fetch rails, BasedAI memory, video plan) run against the Checkpoint 2 tree. The findings below carry file:line references from that analysis — the session must **re-verify every finding in the code before acting on it** (an analysis pass can be wrong; the code is the truth).
> - `.env` populated per `CREDENTIALS-CHECKLIST.md`, never committed. Airplane-first: everything builds and tests offline; no live calls except where an item explicitly says so.
> - **Auto-sync caveat (verified):** an external git auto-sync pushes local `main` commits to the public origin without an explicit push. Work in **worktrees on side branches**; merge a lane to `main` only when its full gate set is green — merging IS publishing.
> - **Timing:** DoraHacks locks 4 Jul 22:59 UTC; the demo video (Prompts/08) captures against this tree. P0 and P1.7 should land as early as possible so the console improvements appear on screen. If the clock bites, obey the cut order in §CUT ORDER — a smaller green tree always beats a larger red one.
> - **Parallel-safe:** this prompt may run **concurrently with Prompts/08** (video production) in a separate session. The body's §PARALLEL-RUN PROTOCOL defines the file-ownership, port, and commit-marker contract that makes that safe — both sessions must honour it.
> - The BasedAI fork PR is **already open** — improvements that change submitted claims must be reflected there by the human (the session prepares the exact comment/diff text; the human posts it).

---

## PROMPT — paste from here

ultracode

# MISSION: Raise Precedent from "verified green" to "excellent" — fix every live-demo defect, close the judged-surface gaps, and harden the moat, without breaking the frozen demo or any eligibility rule

You are a fresh Claude **Opus 4.8** "Ultracode" session with multi-agent **Workflow** orchestration at the highest reasoning effort. Precedent is at **Checkpoint 2**: all buildable work done, 180 tests green, bench 6/6, BasedAI PR open, agents live on Agentverse. An independent four-agent critical analysis has since found **real defects and real scoring gaps**. Your job is to fix them — as an autonomous builder/evaluator multi-agent system — and leave the tree strictly better and provably green after every merge.

This is a hackathon entry whose eligibility depends on four hard rules that are trivial to violate and **eligibility-fatal** to get wrong. **Read this entire prompt before writing a line of code.** Evidence before assertions: you run every verification yourself and paste actual command output before claiming anything is done. Every finding below must be **re-verified in the code** before you fix it; if a finding is wrong, record why and skip it — never "fix" a non-bug.

Work in git worktrees on side branches; merge to `main` lane-by-lane only when green (the auto-sync publishes `main`). Commit with the `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` trailer. **Never push, never flip visibility, never commit `.env` or media files.**

---

## STEP 0 — Load context + re-verify the baseline (mandatory, in this order)

1. **Invoke the `precedent` project skill FIRST** (Skill tool), before touching any file.
2. Read: `docs/checkpoints/CHECKPOINT-2-PROMPT-B-COMPLETE.md` (what is done — do not redo it), `Prep/FINISH-RUNBOOK.md` (what remains and today's status), `Idea/refinement/02-architecture-refinement.md` (the design intent), `Prep/final-numbers.md` (the only numbers any surface may cite), `docs/evidence/LIVE-PROOFS.md`.
3. **Re-verify the baseline with your own commands** — paste each output; if any is red, STOP and fix-forward first:
   - `make check-open-weight` → clean; `make test` → **180 passed, 0 skipped**; `make bench` → 6/6 attacks, FNR 0/5,219, correctness byte-identical to committed `results.json` (restore after); `make bench-extractor` → 0/100 false-fast-paths, byte-identical replay; `make secrets-scan` → clean; `.venv/bin/ruff check .` → clean; `make freeze-check` → exit 0.
   - Boot the demo (`make demo-reset`, `make sim`) and drive `POST /api/drive/1|2|3` → resolved / resolved(fast) / refused, leak probe 0.
4. **Frozen invariants (do not relitigate):** seed **4207** and everything that makes the demo replay byte-identically (`sim/incidents.py`, loaders, the mutation corpus); the committed bench artifacts (`results.json`, `extractor_robustness.json`) stay byte-identical — the ONE deliberate exception is item P1.10; contracts/schema/model-registry are **additive-only**; the three registered agent addresses and their env seeds are untouchable (handler changes are fine — the address is seed-derived).

---

## PARALLEL-RUN PROTOCOL (a Prompts/08 video session may be running concurrently — honour this even if you can't see it)

- **File ownership (hard boundary):** YOU own `precedent/`, `precedent_memory/`, `agents/`, `console/`, `sim/`, `scripts/`, `tests/`, `Makefile`, `Prep/submissions/`, `docs/` (except `docs/evidence/` lines the video session appends). You NEVER write `Prep/video/**` or anything under `precedent-video-drop/` — those belong to the 08 session. If an item seems to require editing a video-owned file (e.g. a caption number changed by P1.10), write the needed change into your final report as a handoff note instead.
- **Runtime namespacing:** you use the DEFAULT ports and DBs (`:8000`/`:8100`, `data/precedent.db`, default sim DB). The 08 session is instructed to run its own stack on `PRECEDENT_CONSOLE_PORT=8200` / `PRECEDENT_SIM_PORT=8300` with its own scratch DB copies — never reset or write its DBs, never bind its ports.
- **Commit markers (the sync signal):** the merge commit that lands P1.7 MUST have a subject starting `P1.7:`, and P1.10's `P1.10:` — the 08 session polls `git log` for these to trigger its re-capture and its end-card P99 re-check. Announce both in your running commentary too.
- **Git discipline:** before every merge to `main`, `git pull --rebase` (the 08 session also commits plan files to `main`); if the rebase brought in changes, re-run the GUARDIAN gate set before pushing the merge. Ownership makes content conflicts impossible; the rebase handles ordering.

---

## THE FOUR HARD RULES (as they bite this pass — each is eligibility-fatal)

**Rule 1 — Open-weight only.** Model ids only in `precedent/models.py`; new code imports roles (`FAST`/`SMART`/`HEAVY`/`EMBED`). Before every merge: `make check-open-weight` PLUS a whole-tree grep (incl. `tests/`, `data/`, new files) for closed-model-id patterns.

**Rule 2 — No LLM in the decision.** This pass *strengthens* Rule 2 (item P0.5 closes a grey zone). The venice-spy standing-path test must stay green after every change; `precedent_memory/retrieve.py` stays LLM-import-free; nothing you add may let a model output gate execution, select an executable action, or set a risk class.

**Rule 3 — Fail-closed.** Item P0.6 exists because a fix *narrowed* this guarantee's scope — your change must restore "stale cache never widens access vs the source of truth" in live-source mode while keeping the airplane demo working. Refusals everywhere disclose only `denied_count` + owning team. Every hardening item must fail toward non-action, never toward serving restricted content.

**Rule 4 — No secrets.** `.env` gitignored; nothing credential-shaped in code, commits, tests, or sub-agent prompts; agent seeds from env only. `make secrets-scan` before every merge.

If any item appears to require breaking one of these, STOP and find the compliant path — there always is one.

---

## PRIORITY-ORDERED WORK PLAN

Findings are labelled with their source lane. **Re-verify each in the code first.** Every item: failing test first (TDD), then implement to green, then the lane evaluator attacks it.

### P0 — Live-demo correctness + rule hygiene (all lanes, do first)

**P0.1 — Watcher chat resilience (Fetch).** `agents/watcher.py::_on_chat` (~:102-121) has no exception handling: a sim outage or missing env mid-chat means a judge gets an ack then silence — the worst live failure mode. Wrap the turn in a guard that always replies (graceful degraded message, no stack trace, nothing restricted disclosed). Also: greet on `StartSessionContent`/empty text (list the three demo incidents + example phrasing) instead of the current unsolicited "Couldn't identify the incident class…".
*Verify:* tests — sim-down mid-turn yields a graceful reply; empty/`StartSession`-only message yields the greeting; no exception path leaves the sender unanswered; refusal semantics unchanged.

**P0.2 — Approval vocabulary guard (Fetch).** `decide_from_reply` (~watcher.py:53) treats bare "ok/go/y" as approve and runs the verdict branch before the ambiguity re-present (~:327-338) — "ok, what does this do?" executes; "no worries" rejects. Require an explicit approve/reject token; any reply containing "?" re-presents; bare "ok"/"y"/"go" re-presents rather than executing.
*Verify:* table-driven test over the exact embarrassing utterances; the happy-path "approve"/"reject" flows and the ASI:One script in `Prep/video/shot-list.md` shot 5 still work verbatim.

**P0.3 — Rails authentication + protocol isolation (Fetch).** (a) `agents/operator.py::_on_plan` (~:106) executes a `PlanMsg` from ANY sender — the address is public; a forged `decision="standing"` plan executes, and the tamper check compares two attacker-supplied hashes. Add a sender allowlist (env `WATCHER_ADDRESS`; reject + audit otherwise). Same for the Librarian's `TriageMsg`. (b) `PRECEDENT_PROTOCOL` is one module-level `Protocol` object (~protocol.py:36) that both Librarian and Operator decorate — each agent ends up including BOTH handlers, and re-building double-registers. Give each agent its own `Protocol` instance (factory), keeping the manifest name/version identical.
*Verify:* forged-sender test (rejected + audited, nothing executes); building Librarian + Operator together no longer cross-registers (inspect registered handlers); building twice is idempotent; agent addresses unchanged (seed-derived — assert in test).

**P0.4 — Demo-server responsiveness (Conduct).** `scripts/demo_server.py` (~:57-76) holds `STATE._lock` across sim HTTP calls AND the SMART rationale `venice.chat` — `/api/state` blocks, so the live trace panel appears all-at-once after the drive instead of streaming. The startup ACL-sync task (~:110-120) acquires the same threading lock inside `async def`, freezing the whole event loop if it fires mid-drive. Fix: never hold the lock across network/LLM work (snapshot-and-release for reads; acquire only around state mutation); run the sync tick via `asyncio.to_thread`. Do NOT upgrade FastAPI or touch the deprecated `@app.on_event` style today.
*Verify:* an integration test drives incident 1 while polling `/api/state` — polls return <100 ms and the trace step-count strictly increases mid-drive (streams, not bursts); all existing console/demo tests green.

**P0.5 — Close the Rule-2 grey zone (Conduct).** `precedent/orchestrator.py` (~:139/:149) calls `rule_for(class_key)` even when the extraction `method == "llm_proposed"` — a model-proposed key selects the executable action. Mitigated today (L1 cap + human approval), but it is the one line a probing judge can call "LLM in the loop". Require `method == "deterministic"` (fingerprint-confirmed) to build an executable plan; `llm_proposed` routes to the investigation-dossier/human-confirm path only.
*Verify:* new test — an `llm_proposed` extraction can never reach plan construction; venice-spy standing test green; the three demo incidents replay byte-identically (their extractions are deterministic); `make bench-extractor` byte-identical.

**P0.6 — Gate the freshness heartbeat + audit it (BasedAI).** Commit 5f29a2e's `refresh_cached_freshness` (`precedent_memory/sync.py` ~:208-227), called unconditionally per chat turn (`agents/watcher.py` ~:113-117), re-affirms cached ACLs as fresh **without consulting any source** — sound in airplane mode, but with live Jira configured the 60 s freshness window degenerates to "time since last chat", serving an un-polled upstream *tightening* indefinitely. Gate it: heartbeat only when no live source is configured (env-derived), a real `sync()` tick otherwise; and write an audit row per heartbeat/refresh (today it mutates freshness + bumps policy versions with zero audit trail).
*Verify:* tests for both modes (airplane: incident-2 standing beat still resolves, incident-3 stays refused; live-source-configured: stale window produces DENY until a real sync); audit rows present for the refresh path; `make bench` byte-identical.

**P0.7 — Tool + gate hardening (Conduct).** (a) `precedent/tools.py` (~:26-47) never checks HTTP status — a 404 snapshot yields an empty `pre_state` and a "successful" rollback that restores nothing (silent fail-open in the rollback story): `raise_for_status`, and refuse to build a plan on an empty snapshot. (b) `orchestrator.py` (~:216-217) ignores per-step `ok` on execute — treat `ok:false` as verification failure with an explicit audit row. (c) `commit_execution` (~:199-213) never checks `expires_at`; `_PENDING` (demo_server.py ~:31) never prunes — enforce the TTL on every commit path. (d) `/api/drive/{n}/flake` fires `approve=False`, which on a slow-path incident rejects without executing and leaves the flake armed to poison the next verify; `drive_incident.py --no-approve` says "leave to a human" but auto-rejects — fix both semantics (flake only arms when an execution will consume it; `--hold` flag for the real held gate).
*Verify:* failing tests first for each of (a)–(d); the three demo incidents + the recovery beat replay identically; airplane slice green.

### P1 — Judged-surface upgrades (highest score-per-hour after P0)

**P1.7 — Make the console Approve button real (Conduct — land BEFORE video capture).** Today the button only writes an `approval_recorded` audit row (`console/demo_state.py` ~:251-262) while the real held-gate resume is curl-only (`scripts/demo_server.py` ~:79-100) — the on-stage "human in control" moment is decorative. Wire it: drive with `hold=true` → pending-approval card → **the card shows the diff preview** (pre_state vs planned mutation + rollback hash from `Prepared` — "you approve exactly this change, with exactly this undo") → Approve/Reject buttons call the real resume. Add the spec-promised surfaces (arch-refinement item 9) the console never got: the **robustness chip** (headline from the committed `extractor_robustness.json`: "0 false-fast-paths / 100 · 25/25 decoys resisted"), a **cumulative close strip**, and **per-incident TTR chips** (populate `ExecutionResult.elapsed_ms` from audit rows: "resolved in N s" vs the labelled 8h51m business baseline — same-demo comparison framing, per `Prep/final-numbers.md`). Add a **one-click "Export change record"** button reusing `scripts/render_change_record.py`. Keep the existing non-hold flow untouched as the default; escape `incident_id` in the onclick (XSS nit, console/app.py ~:229-230).
*Verify:* Playwright (or httpx+SSE/poll) test — hold-drive shows the card with diff + rollback hash, Approve resumes the REAL gate (audit shows approver principal), Reject leaves state untouched; chips render the committed numbers byte-for-byte; `make demo-reset` still <30 s; every number on the console traces to `Prep/final-numbers.md` with its label.

**P1.8 — Make "multi-agent" true on the wire (Fetch).** The Librarian/Operator handlers exist and are unit-tested, but nothing ever sends them a message — the hop-trail is hard-coded `[]` (`agents/operator.py` ~:92) and the footer honestly prints "(in-process)", while `Prep/submissions/FETCH-DELIVERABLES.md:13` claims multi-agent is done (an overclaim a judge can catch). Fix by making it true: from the Watcher turn, send real `TriageMsg`/`PlanMsg` over the rails as **shadow messages** (fire-and-forget; the in-process result stays authoritative for the reply so demo latency/determinism is unchanged), handle the replies, and populate the hop-trail footer with real per-hop ms. Add a Bureau self-check driver in `scripts/run_agents.py` (startup pushes one message through each rail and logs the trail). Then update `FETCH-DELIVERABLES.md` to the now-true wording.
*Verify:* dry-run test shows a real `ctx.send`→handler→reply round-trip populating a non-empty hop trail; the chat reply's authoritative content is byte-identical with rails up or down (shadow = non-blocking, failure-tolerant); sender-allowlist (P0.3) still enforced; addresses unchanged.

**P1.9 — Query-time inference prevention (BasedAI — a NAMED bonus, currently absent).** The bench's `query inference` attack proves probes don't leak *content*, but nothing *detects cross-permission-boundary inference at query time*. Build it deterministically (Rule 2: zero LLM): (a) per-principal **denial-burst / probing-pattern detection** over the existing `audit_log` (sliding window, threshold → flag + throttle response, audited); (b) a **bundle-level cross-boundary co-occurrence check** before context assembly (a result set may not mix records whose effective policies imply disjoint principals — deny the bundle, audit the reason). New module in `precedent_memory/`, oracle-graded tests, and a NEW bench section — the committed 10-metric `results.json` stays byte-identical.
*Verify:* oracle-graded deny/allow tests for both mechanisms; a probing-sequence simulation triggers detection and the audit trail shows it; `retrieve.py` import list still LLM-free; committed bench artifacts byte-identical; new section appended to `RESULTS.md` clearly labelled as additional.

**P1.10 — Docs truth pass (all lanes; the ONE committed-artifact exception).** (a) `precedent_memory/bench/RESULTS.md` still says "live Saturday / not yet measured" for drift/TTC while `docs/evidence/LIVE-PROOFS.md` carries the measured values — regenerate RESULTS.md ONCE via `make bench` (correctness fields are seed-deterministic; latency re-measures — regenerate, never hand-edit) and add the UCI-25k + live-drift rows with their exact labels ("3-flip, 2-issue Jira liveness proof", never a "25k-store" claim). (b) `Prep/submissions/BASEDAI-PR-README.md` lists temporal-embargo under "what's next" although it is implemented and oracle-graded — move it to implemented (undersold bonus), and add the P1.9 mechanism honestly. (c) Prepare (do not post) the exact BasedAI PR comment text with the updated table. (d) Re-run the number-honesty audit over every surface you touched (`docs/number-honesty-audit.md` discipline: every number → `Prep/final-numbers.md` row + caveat).
*Verify:* `grep '‹'` and `[[WAIT` checks show only the two legitimate sentinels; every changed number traces to its source row; RESULTS.md regenerated not hand-edited (show the command).

### P2 — Hardening stretch (only if the clock allows, in this order)

**P2.11 — Memory-layer proofs (BasedAI):** real-thread concurrency stress test (file-backed WAL DB, a writer thread flipping ACLs under a retrieval loop; assert zero leaks + audit chain intact — turns the honest "seam proof" into a stronger claim); serialize the audit chain against multi-writer forks (`audit.py` ~:27-28 read-MAX-then-insert race — unique index on seq + `BEGIN IMMEDIATE`, or equivalent); hypothesis property tests for monotonicity (adding a constraint never widens; degraded ⊆ live); an AST import guard for `retrieve.py` mirroring the oracle's (the flagship Rule-2 file deserves the same fence); document-or-fix the `sync()`-never-commits footgun; signed JSONL audit export with a periodic anchor row (regulatory-grade export + closes the tail-truncation gap operationally); granular denial reasons in audit rows (revoked/stale/embargoed/conjunction/unverified — today one string covers all five).

**P2.12 — Cosmetics + honesty debt (Conduct):** `policy_pack.yaml` lineage_refs mostly point at `kb:KB-0001` even for KB-0002…0009 classes (provenance inconsistency — fix to the real refs); decide `bm25.py` (runtime-dead: wire it as the labelled retrieval fallback the docs claim, or delete the claim); remove/justify `console_link.http_trace` and `IncidentEvent.jira_key`; widen `ladder._recently_counted`'s 200-row audit window or bound it explicitly.

*Verify (both):* full gate set green after each; no new concept leaks onto stage surfaces (the demo stays a three-beat story).

---

## CUT ORDER (when the clock bites)

P0.1–P0.7 are never cut (they are correctness). Then: P1.7 → P1.8 → P1.9 → P1.10 → P2.11 → P2.12. Drop from the bottom. Never start an item you cannot land green before the video-capture handoff; a lane's worktree that isn't green by then simply does not merge — record it in the final report instead.

---

## MULTI-AGENT SYSTEM (use the Workflow tool — maxed out; builders never grade their own work)

- **Three implementer lanes in separate worktrees:** LANE-CORE (P0.4, P0.5, P0.7, P1.7, P2.12 — `precedent/`, `console/`, `scripts/demo_server.py`), LANE-RAILS (P0.1–P0.3, P1.8 — `agents/`, `scripts/run_agents.py`), LANE-MEMORY (P0.6, P1.9, P2.11 — `precedent_memory/`). P1.10 runs last on the merged result. TDD inside every lane: the failing test that encodes the item's *Verify* line comes first.
- **One adversarial EVALUATOR per lane**, a separate sub-agent that did not write the code. It must (a) re-run the lane's full verification itself and paste output, (b) actively try to break the change — forged senders, malformed chat turns, empty snapshots, stale-cache-with-live-source, probing sequences, concurrent drives, (c) re-check the four hard rules on the lane's diff, (d) check the lane did not touch a frozen invariant (`git diff --stat` against the frozen paths). The evaluator's verdict gates the merge; **on disagreement the evaluator wins** — fix-forward and re-submit. No lane merges on its own say-so.
- **GUARDIAN (cross-cutting, runs at every merge):** `make check-open-weight` + whole-tree closed-id grep (incl. `tests/`, new files) · venice-spy zero-LLM standing-path test · `make bench` + `make bench-extractor` byte-identity · `make secrets-scan` · `ruff` · `make freeze-check` · restricted-body leak probe on all three refusal surfaces (console, chat, change-record).
- **DEMO-VERIFIER (runs after each merge to `main`):** `make demo-reset` + `make sim`, drive 1/2/3 twice → byte-identical replays; the hold+Approve console path (after P1.7); the airplane-mode slice with Wi-Fi simulated off; `/api/state` latency during a drive (P0.4's regression fence).
- **Final RED-TEAM pass on the finished tree:** everything GUARDIAN + DEMO-VERIFIER runs, plus the number-honesty audit over every touched surface and a fresh read of the three analysis lanes' findings verifying each is either fixed (test cited) or explicitly skipped-with-reason. If the red team disagrees with any claim, the disagreement wins.
- **Anti-inflation rules:** a claim without pasted command output is not a claim; "tests pass" means the full suite, not the new tests; every evaluator verdict must name what it tried to break, not just what passed.

---

## ACCEPTANCE CHECKLIST (run yourself; paste evidence)

- [ ] Baseline re-verified green before any change (all eight commands)
- [ ] P0.1–P0.7 each: finding re-verified → failing test → green → evaluator verdict pasted
- [ ] P1.7 console gate is real (hold → diff-preview card → Approve resumes the actual gate; chips + TTR + export button; XSS nit fixed) — landed before video capture
- [ ] P1.8 hop-trail carries real per-hop ms from real rail messages; reply authoritative-content invariant holds rails-up and rails-down; FETCH-DELIVERABLES wording now true
- [ ] P1.9 inference-prevention module: oracle-graded, LLM-free, committed bench artifacts byte-identical, new RESULTS section labelled
- [ ] P1.10 RESULTS.md regenerated (not hand-edited); PR-README temporal line moved to implemented; PR comment text prepared for the human; number-honesty audit re-run
- [ ] P2 items: landed-or-skipped, each with reason
- [ ] Four hard rules re-verified on the finished tree (GUARDIAN set) — including the venice-spy and the whole-tree grep
- [ ] Demo replays byte-identically (two runs, diff shown); airplane slice green; `make demo-reset` <30 s
- [ ] Full suite ≥180 passed, 0 skipped; every new behaviour has a test
- [ ] Nothing pushed by this session; no media or `.env` committed; WIP stayed on side branches until green

## DEFINITION OF DONE

Done when: every P0 item is fixed with its failing-test-first proof and evaluator sign-off; P1.7–P1.10 are landed green (or explicitly cut by the cut order with the clock as the stated reason); the four hard rules hold on the finished tree with pasted evidence; the demo replays byte-identically and the console now shows the real gate, the diff preview, and the three spec-promised chips; the Fetch deliverable claims are true on the wire; the BasedAI surface carries the inference-prevention bonus and the corrected temporal claim; and a final report separates (a) fixed-with-proof, (b) skipped-with-reason, (c) the exact human follow-ups (post the PR comment, re-capture the video against the improved console, submit before 22:59 UTC).

**Begin by loading the `precedent` skill, then re-verifying the baseline.**

---

## CLOSING HUMAN WALKTHROUGH (the session prepares these; only you can do them)

1. **Video capture (Prompts/08 session)** — may already be running in parallel; it polls for your `P1.7:` merge marker and re-captures automatically. If it isn't running yet, start it any time (it does not need to wait for you).
2. **Post the prepared PR comment** (updated bench table + inference-prevention section) on the open BasedAI fork PR.
3. **DoraHacks BUIDL** — submit before 22:59 UTC with T1 sign-off; the improved robustness/console story is already reflected in the worksheet drafts the session updates.
4. **`git push --follow-tags origin main`** when you choose to publish the tag (auto-sync covers commits, not tags).
