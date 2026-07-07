# Checkpoint 3 — Ultracode "verified-green → excellent" pass (P0.1–P1.10 landed)

**Cut:** 2026-07-04, by the Opus 4.8 Ultracode session that raised Precedent from Checkpoint 2
("verified green") by fixing every re-verified live-demo defect and closing the judged-surface gaps
found by the four-agent critical analysis. **No `git push` was run by this session**; commits land
on local `main` and the external auto-sync publishes it. No `.env` or media committed; repo
visibility untouched.

Every item below was: **finding re-verified in the code → failing test first (TDD) → implemented to
green → verified**. P0 was gated by an **independent adversarial evaluator** (verdict pasted in the
session); every merge passed the **GUARDIAN** gate and a **DEMO-VERIFIER** byte-identical replay.

Baseline before/after: **183 → 256 tests passed, 0 skipped**; ruff clean; `check-open-weight` clean;
`secrets-scan` clean; bench correctness + `extractor_robustness.json` byte-identical throughout
(RESULTS.md is the ONE deliberate P1.10 exception); demo drives 1/2/3 replay resolved / resolved
(Standing) / refused with zero server errors.

---

## STEP 0 — baseline regression found + fixed-forward

`make secrets-scan` was **RED (5 findings)** at session start — commit 773c92f had filled the public
ASI:One shared-chat invite URL (`asi1.ai/invite?channelInviteKey=…`) across five submission
surfaces *after* Checkpoint 2's clean scan. That URL is a **public share link** (published by design
on the BasedAI PR / DoraHacks / Fetch deliverables), not a credential; gitleaks' generic-api-key
heuristic false-positived. **Fix:** a scoped `.gitleaks.toml` allowlist for the asi1.ai invite-URL
pattern only (real Venice/Jira/Agentverse secrets still caught). `secrets-scan` / `freeze-check` →
green. (commit 535dd36)

---

## (a) Fixed, with proof

| Item | Finding (re-verified) | Fix | Test / proof |
|---|---|---|---|
| **P0.1** | `watcher._on_chat` unguarded — a sim outage / missing env mid-turn gives ack-then-silence; empty/StartSession → unsolicited "Couldn't identify…" | `run_live_chat` wraps the turn so the sender ALWAYS gets a graceful degraded reply (no trace, nothing restricted); empty/StartSession → greeting listing the 3 incidents | `test_rails_hardening.py` (greeting, empty-greets, always-replies-on-sim-outage) |
| **P0.2** | `decide_from_reply` treated bare "ok/go/y" as approve → "ok, what does this do?" executed; "no worries" rejected. Evaluator also found **negated approvals** ("don't approve") executed | Only explicit approve/reject tokens decide; any "?" or bare word re-presents; a negation next to an approve token re-presents | `test_rails_hardening.py` table (24 utterances incl. negations); `test_fetch_rails.py` updated |
| **P0.3** | (a) Operator/Librarian executed a `PlanMsg`/`TriageMsg` from ANY sender (forged `decision="standing"` ran with no tamper check); (b) one shared module-level `Protocol` cross-registered BOTH handlers onto BOTH agents (empirically confirmed) | (a) seed-derived sender allowlist (`common.authorised_sender`) — forged sender rejected+audited, nothing runs, no reply; (b) per-agent `build_precedent_protocol()` factory | `test_rails_hardening.py` (forged-sender no-execute, isolated handlers, idempotent rebuild, stable address) |
| **P0.4** | `api_drive` held `STATE._lock` across sim HTTP + the SMART `venice.chat`; the startup sync tick held the threading lock inside the event loop | `venice.chat` moved OUTSIDE the lock (`orchestrator.fill_rationale` + `prepare(defer_rationale=True)`); single `STATE.conn` under the lock (no cross-connection contention); sync tick via `asyncio.to_thread` + commit | `test_core_hardening.py::test_drive_does_not_block_state_reads`; live `/api/state` <1 ms during a drive; 4 replay cycles, 0 lock errors |
| **P0.5** | `orchestrator.prepare` called `rule_for(class_key)` even when `method=="llm_proposed"` — a model-proposed key selected the executable action | Require `method=="deterministic"` to build a plan; `llm_proposed` escalates to human confirmation | `test_core_hardening.py` (llm_proposed never builds a plan; the 3 demo incidents extract deterministically) |
| **P0.6** | `refresh_cached_freshness` re-affirmed cached ACLs as fresh with NO source consult + NO audit — with live Jira it served an un-polled upstream tightening indefinitely | Gated: live-source → a real `sync()` tick (fail-closed); airplane → heartbeat; both audited | `test_freshness_gating.py` (airplane heartbeat keeps incident-2 readable + incident-3 refused; live outage denies; env auto-selects the sync tick) |
| **P0.7** | (a) `tools.py` never `raise_for_status` — a 404 snapshot → empty pre_state → silent fail-open rollback; (b) execute `ok:false` ignored; (c) `_PENDING` never pruned; (d) `flake` fired `approve=False` and could stay armed | (a) `raise_for_status` on every typed call + refuse an empty snapshot; (b) `ok:false` → `execute_failed` audit + rollback; (c) `_prune_pending`; (d) flake armed only on an executing path; CLI `--hold` for the real gate | `test_core_hardening.py` (404 raises, empty-snapshot escalates, ok=false rolls back+audits, prune, flake-not-armed-on-refused) |
| **P1.7** | Console Approve only wrote `approval_recorded`; real held-gate resume was curl-only; robustness/close/TTR chips + export absent; unescaped `incident_id` in onclick | Hold & review → pending card with the **diff preview** (pre_state vs planned mutation + rollback anchor + plan hash) → Approve resumes the REAL gate / Reject untouched; robustness chip + cumulative-close strip + per-incident TTR; one-click change-record export; XSS fixed (data-* + delegation) | `test_console_gate.py` (6); **live Playwright**: Hold → diff card → Approve → resolved, TTR + close strip populate |
| **P1.8** | Nothing sent the Librarian/Operator a message; hop-trail hard-coded `[]`; FETCH-DELIVERABLES overclaimed multi-agent | `agents/rails.py::shadow_hops` sends real `TriageMsg`/`PlanMsg` via `send_and_receive` (timed, fail-tolerant, non-authoritative); `run_agents` startup rails self-check; FETCH-DELIVERABLES wording now honest | `test_rails_wire.py` (loopback round-trip → real hop trail; denied triage skips Operator; down rail → empty trail, no exception) |
| **P1.9** | No query-time inference detection (a named BasedAI bonus, absent) | `precedent_memory/probing_detection.py` — per-principal denial-burst detection + bundle cross-boundary co-occurrence check; both fail-closed + audited; standalone `inference_prevention` bench (new labelled section; results.json byte-identical) | `precedent_memory/tests/test_probing_detection.py` (11, oracle-graded) |
| **P1.10** | RESULTS.md said "live Saturday / not yet measured" while LIVE-PROOFS had measured values; PR-README undersold temporal-embargo | RESULTS.md regenerated via `make bench` + live UCI/drift rows added with exact labels + P1.9 section; PR-README temporal-embargo → implemented + P1.9 added; PR comment prepared (not posted); number-honesty re-audited | `grep` shows only the 2 legitimate `[[WAIT]]` sentinels, no stray `‹…›`; every number traces to final-numbers §4b / LIVE-PROOFS |

Four hard rules on the finished tree: **Rule 1** guard clean + whole-diff grep clean (only the
guard-test banned-list). **Rule 2** venice-spy standing tests green; `retrieve.py` LLM-free; P0.5
closes the grey zone. **Rule 3** refusals disclose only count+owner; every hardening item fails
toward non-action. **Rule 4** `secrets-scan` clean.

### Independent verification sign-off

- **P0 adversarial evaluator: PASS** (verdict in-session) — attacked forged senders, malformed
  chats, empty snapshots, live-source-with-stale-cache, flake-poison, negated approvals. Only
  finding (negated approvals) was fixed-forward.
- **Final RED-TEAM on P1.7–P1.10 + the whole `c1b289f…HEAD` diff: PASS** — no attack succeeded, no
  rule violated, no frozen invariant touched, 256 passed, every number traces. Two documented
  non-defects: (1) a change-record for a change **ops-lead was authorised to make** names the
  public policy-rule-id `RGT-EXCL-009-TAKEDOWN` — no restricted runbook body is disclosed (the
  refusal path for an uncleared principal leaks nothing); (2) `results.json`'s 24 latency fields
  changed — the deliberate, documented P1.10 `make bench` re-measurement (correctness fields frozen,
  values match RESULTS.md).

---

## (b) Skipped, with reason

- **P2.11 (memory-layer proofs)** and **P2.12 (cosmetics)** — the P2 stretch tier. Deliberately NOT
  started: the entire P0 (never-cut) + P1 (highest-value) tiers were landed green first, per the cut
  order, and P2 is explicitly "only if the clock allows". Ready follow-ups, honestly assessed:
  - `audit.py` read-MAX-then-insert race — real but does not manifest today (all writes go through
    ONE `STATE.conn` under `STATE._lock`, and the bench is single-threaded); a `BEGIN IMMEDIATE`
    hardening is low-risk but touches the core audit path, so left for a dedicated pass.
  - AST import guard for `retrieve.py` — its LLM-freedom is already triple-enforced
    (`check-open-weight` grep + the invariants-guard oracle + a string test); marginal.
  - `policy_pack.yaml` lineage_refs provenance, `bm25.py` wire-or-delete, `console_link.http_trace`
    / `IncidentEvent.jira_key`, `ladder._recently_counted` window — cosmetics; touching
    policy_pack/ladder risks byte-identity, so deferred rather than rushed.
- The evaluator's negated-approval finding was **not** skipped — it was fixed-forward (P0.2 follow-up,
  commit b27455a).

---

## (c) Exact human follow-ups (account-bound / outside this session)

1. **Post the prepared BasedAI PR comment** — `Prep/submissions/BASEDAI-PR-COMMENT.md`, verbatim,
   once the mentor deadline answer is in (replaces `[[WAIT:MENTOR-ANSWER]]`).
2. **Re-capture the video** against the IMPROVED console — the on-stage "human in control" moment is
   now real (Hold & review → diff-preview card → Approve resumes the actual gate), with the
   robustness / cumulative-close / per-incident-TTR chips and the Export-change-record button.
   (The Prompts/08 video session polls `git log` for the `P1.7:` and `P1.10:` commit subjects, both
   now on `main`.)
3. **Submit before 22:59 UTC** (never the last hour) — DoraHacks BUIDL + the BasedAI PR.
4. Optionally run the runnable rails self-check (`make demo-reset && … run_agents.py`) to see the
   real Watcher→Librarian hop-trail logged (P1.8), and re-run `make live-drift` if a fresh
   audit-clock-anchored TTC is wanted.

---

## Parallel-run coordination notes (Prompts/08 video session)

- File ownership was honoured — this session never wrote `Prep/video/**` or `precedent-video-drop/`.
  The 08 session's uncommitted work in the shared tree was preserved untouched.
- One accidental commit to the 08 session's `video-pipeline` branch was cleanly reverted (their
  branch restored to pristine) and re-landed on `main`.
- All work was done in an isolated git worktree (`improve/checkpoint3`) with its own venv, merged to
  `main` by fast-forward after `git pull --rebase` onto `origin/main` (only `Prompts/*.md` came in;
  the GUARDIAN gate was re-run after the rebase).
