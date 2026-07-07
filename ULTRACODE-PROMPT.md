# ULTRACODE BUILD PROMPT — "Precedent Gate" (P0→P2)

> Paste this entire file as the prompt for an Opus 4.8 **ultracode** session opened
> in this repository. It is self-contained, but the session MUST load the repo skill
> and read the referenced docs before writing code. Delete this file once the scope
> has shipped (its record lives in git history and `docs/DIRECTION.md`).

ultracode

## 0. Mission

You are building the decided post-hackathon scope for **Precedent** — see
[`docs/DIRECTION.md`](docs/DIRECTION.md) for the full decision package. One line:

> **Precedent Gate — change control for AI agents.** "Your team already built an
> agent that CAN act. Precedent makes it ALLOWED to act — and proves it."

The codebase is real and green (256/256 tests, `make freeze-check` passes end to
end; the demo boots, resolves incidents 1–2 through the gate, refuses incident 3 on
ACL, and the Docker image is verified working). You are NOT rescuing a hackathon
hack — you are hardening and extending a working system into: a Gate API/MCP
server, an evidence-pack artifact, a local-first analyzer, and a public hosted
demo that converts. Work happens in this repo on `main` unless stated otherwise.

**Capacity model:** roughly 2–3 weeks of agent-accelerated work. P0 is the
non-negotiable core; P1 is high-value; P2 is optionality. Cut from the bottom
(§7) — never cut a P0 item to polish a P2 item.

## 1. Read before any code (in this order)

1. `.claude/skills/precedent/SKILL.md` — load via the Skill tool; the four hard
   rules and conventions live there and are CI-enforced.
2. `docs/DIRECTION.md` — what was decided and killed, and why.
3. `docs/numbers.md` — the ONLY numbers any surface may quote, with labels.
4. `docs/idea/refinement/02-architecture-refinement.md` — the as-built design
   (fingerprint, ladder, A/B/C memory semantics, fast-path).
5. §5 of this file — the verified defect ledger you will burn down.

## 2. Non-negotiable invariants (violating any of these fails the build)

1. **Open-weight only, one registry.** No model id anywhere except
   `precedent/models.py`. Guard: `make check-open-weight`. Venice hosts closed
   models too — "it runs on Venice" proves nothing; the registry asserts every
   entry's `modelSource` is a huggingface.co URL.
2. **No LLM in any permission or risk decision.** `precedent_memory/retrieve.py`
   keeps zero LLM imports. Class matches count only on extractor-confirmed field
   EQUALITY; `llm_proposed` extraction never builds an executable plan. The Gate
   API you build must preserve this: deterministic decisions, model narrates only.
3. **Fail-closed.** Uncertain ACL freshness ⇒ deny. Refusals disclose count +
   owning team only. Every new failure path fails toward non-action.
4. **No secrets committed; committing to `main` IS publishing.** The repo is
   public and an external auto-sync pushes `main` within seconds. Run
   `gitleaks protect --staged --config .gitleaks.toml` before EVERY commit; run
   `make secrets-scan` before ending any work session. Never commit customer data,
   real ticket exports, `.env`, or tokens.
5. **Rollback precedes execution.** No plan executes without a pre-state snapshot
   and pre-generated inverse. Action classes without a true inverse (password
   resets, credential rotations) are REJECTED by policy lint — do not ship them.
6. **Honesty rules on every surface.** L3 is "Standing Approval", never
   "Autonomous". 94.4% is an existence claim; 98.6% is arrival-knowable; 59.4/87.7
   is a naive floor, never product accuracy; 18.2h is CALENDAR, 8.85h is BUSINESS —
   never blended. Vendor numbers carry "(vendor-claimed)". Numbers not in
   `docs/numbers.md` do not ship. The extractor's "0 false fast-paths /100" is a
   SAFETY number — never present it as recall (recovery was 8/100 on that
   deliberately-adversarial corpus; say so wherever recall could be inferred).
7. **Determinism.** Canonical seed 4207. Bench correctness fields are
   byte-identical per seed; only latency fields may drift. `sim/incidents.py`
   replays byte-identically. Do not introduce wall-clock or randomness into any
   deterministic surface (the demo's kernel-hash check must keep passing:
   `GET /api/kernel-hash` matches `MANIFEST.json` — update BOTH together,
   deliberately, when tour content changes).

## 3. Orchestration mandate — use ultracode properly

This session is opted into multi-agent orchestration. Use it deliberately:

- **Understand phase (small):** the repo is well documented — do NOT re-map it
  wholesale. Spawn at most 2–3 readers for the precise seams you will cut
  (`precedent/ladder.py` + `policy.py` + `contracts.py` for the Gate API;
  `precedent_memory/audit.py` for the evidence pack; `console/app.py` +
  `demo_state.py` + `scripts/demo_server.py` for session scoping).
- **Design-verify before building:** for the three user-facing artifacts (Gate API
  shape, analyzer HTML report, demo tour), run a small judge panel (3 independent
  perspectives each: API consumer / security reviewer / first-time visitor) on a
  written design BEFORE implementation. Adopt or explicitly reject each finding.
- **Implement in parallel with worktree isolation:** the work packages in §4 are
  designed to be parallelisable. Use `isolation: "worktree"` for agents mutating
  overlapping areas; merge through the gates below.
- **Adversarial verify every merged package:** for each landed package, spawn
  reviewers prompted to REFUTE the package's acceptance claim (not to praise it).
  A claim survives only if the refuters fail. Minimum: correctness lens + security
  lens (the gate/evidence code is security-sensitive) + honesty-labels lens for
  any surface that renders numbers.
- **Loop-until-dry bug hunt** on the two public surfaces (hosted demo, analyzer)
  before declaring P0 done: keep spawning finders until 2 consecutive rounds find
  nothing new. Include: multi-session interference, XSS via ticket text, path
  traversal in the analyzer file input, evidence-pack tampering detection.
- **Completeness critic at the end:** one agent sweeps README + docs + demo copy
  for claims without proofs and placeholders (the `‹…›` grep is in freeze-check);
  what it finds becomes the final fix round.
- **TDD discipline for every defect fix:** failing test first, then the fix. The
  suite must END ≥256 tests, 0 skipped, with every new feature tested.

## 4. Build scope

### P0 (the core — all must land)

**P0.1 — Gate API + MCP server.**
Extract the decision path behind a versioned API without breaking existing callers:
`gate.propose_action` / `gate.get_decision` / `gate.report_outcome` over HTTP
(FastAPI, versioned prefix) and as an MCP server. Typed proposals reuse
`precedent/contracts.py`; decisions are deny / needs-approval(ref) / allow-standing,
computed ONLY by the existing deterministic policy engine + ladder (no new decision
logic; no LLM anywhere near it). Pending approvals get TTL expiry (the existing
10-minute pattern); a dropped session can only produce non-action. Principals are
registered out-of-band (config/API) — do NOT claim MCP client identity (no robust
standard in 2026; document this honestly in the API docs).
*Acceptance:* an end-to-end test drives propose → approval → execute-in-sim →
verify → audit-chain-verifies via the HTTP API alone; MCP server passes the same
flow through an MCP client harness; 0 new LLM imports in the decision path
(extend the existing venice-spy test to the gate module).

**P0.2 — Evidence Pack v1 + standalone verifier (one artifact).**
From the existing hash chain (`precedent_memory/audit.py`): per-incident signed
bundle — JSON + human-readable HTML — containing incident, retrieved precedent
with provenance, gate decision + policy-pack version, named human principal, typed
execution transcript, verification result, rollback record if any, and the chain
proof. Ship `verify_pack.py`: a **zero-dependency** (stdlib-only) script that
verifies a pack's hash chain offline, so an auditor needs no vendor licence.
Label every pack "evidence support, not a compliance determination."
*Acceptance:* pack generated for each of the three demo incidents; verifier passes
on them; verifier FAILS loudly on a tampered byte (test both); a round-trip test
proves pack content equals audit-log content.

**P0.3 — Precedent Analyzer (local-first CLI).**
Generalise `data/analysis/uci_match_rate.py` + `precedent/extractor.py` into
`precedent-analyze <export.csv>`: accepts ServiceNow CSV, Jira CSV, and generic
CSV (column-mapping config with sensible auto-detection); computes the org's OWN
repeat-rate, precedented-median, and standing-approval-candidate classes; emits a
local HTML report headlined for the Gate buyer (candidate classes + gated-action
volume sizing) with the existence-vs-arrival caveats PRINTED ON THE REPORT so
prospects cannot misquote us. **Data never leaves the machine — enforce with a
test that disables sockets during an analyzer run.** Packaging: runnable via
`pipx run` / `uv run` from the repo.
*Acceptance:* running on the UCI export reproduces 94.4% / 98.6% / 18.2h / 558
byte-for-byte in the report; the sockets-disabled test passes; a second-format
fixture (Jira-shaped, committed, synthetic) exercises the column mapper; malformed
CSVs fail with helpful errors, never tracebacks.

**P0.4 — Hosted demo repointed to the gate story.**
On the existing kit (`console/app.py`, `console/showcase.py`, `sim/`, `Dockerfile`,
`render.yaml`): three-pane view (agent transcript | gate decisions | live audit
chain). Minute-by-minute spec:
- 0:00–0:20 landing: positioning line, one button ("Unleash the agent"), honesty
  banner (labels; "Standing Approval — human-promoted, always revocable").
- 0:20–1:00 an incident fires in the sim; an agent proposes a risky fix as a TYPED
  proposal (JSON visible); the gate intercepts: sha256 class key, risk class,
  policy-pack version, and a "no LLM in this decision" badge linking to the CI rule.
- 1:00–1:40 the VISITOR approves in a simulated Slack-style pane; pre-state
  snapshot + pre-generated inverse shown BEFORE execution; execution runs in sim;
  verification passes; the audit chain grows with the visitor as named principal.
- 1:40–2:20 time-compressed recurrences: class verifies 3×, visitor clicks
  Promote to Standing Approval (Revoke adjacent); next recurrence runs the
  zero-LLM fast-path — caption "the second time is free".
- 2:20–2:50 the trust moment: injected verification failure → auto-rollback →
  auto-demotion; then a fail-closed ACL denial disclosing only count + owning team.
- 2:50–3:00 visitor clicks "Export evidence pack", downloads the real bundle,
  watches the standalone verifier pass on screen with copy-paste instructions.
- Exit CTAs, exactly two: analyzer command ("data never leaves your machine",
  UCI numbers with labels) and "Book a design-partner slot".
**Multi-session is required:** per-visitor session scoping (token/cookie keyed,
TTL-evicted) replacing the global `STATE` singleton, module-level `_PENDING`
dicts, and the global flake row — one visitor's Reset must not touch another's
session. Rate-limit the public endpoints.
*Acceptance:* a scripted Playwright run completes the whole tour on the built
Docker image; two concurrent Playwright sessions do not interfere; airplane-mode
pass (no network beyond localhost); `docker build && docker run` then the
Playwright suite against the container is a CI-able check; kernel-hash still
matches MANIFEST.

**P0.5 — Policy-pack authoring kit (right-sized).**
Documented YAML schema for action classes (risk class, required approver role,
inverse generator, verification probe) + `precedent policy lint` CLI + **8–10
sim-executable action classes** seeded from the head of the 558 UCI fix classes.
Lint REJECTS classes without a true inverse or probe.
*Acceptance:* lint green on all shipped packs; every class's inverse and probe
exercised by a sim test; a deliberately-broken pack fixture fails lint with a
clear message.

**P0.6 — Defect-ledger burn-down (§5, items marked P0).** TDD each one.

### P1 (high value, in order)

**P1.1 — Real Slack approvals:** Block Kit Approve / Deny / Promote / Revoke wired
to the existing ladder; every click writes a hash-chained audit record naming the
human principal; verification failure auto-demotes. Buildable + testable without
a live workspace (fake Slack transport in tests); live wiring lands when the
founder registers the app. *Acceptance:* end-to-end test gate.propose → (fake)
Slack approve → execute-in-sim → chain verifies.

**P1.2 — SDKs + adapters (kills the self-referential-demo objection):** thin
Python and TypeScript clients (`gate.guard(action)`); middleware adapters for the
Claude Agent SDK and LangGraph tool-execution hooks; keep `agents/rails.py`
(Fetch.ai) working as a third rail. *Acceptance:* a quickstart gates a toy
third-party LangGraph agent in under 15 minutes — the quickstart is executed and
timed by a CI docs test.

**P1.3 — Thin-gate OSS release prep** (release happens from a SEPARATE new public
repo, not this one): extract the gate/MCP server + quickstart + extractor-
robustness bench instructions into `oss/` staging here, with a RELEASE-CHECKLIST
(gitleaks on the staged tree; no commercial code; no customer-data path; licence;
MCP directory listing prep). The full `precedent_memory` library STAYS CLOSED
pending pricing signal — that call is recorded in `docs/DIRECTION.md`; do not
Apache it. *Acceptance:* clean-clone quickstart from the staged tree passes green.

**P1.4 — Streaming-ops scenario pack (Door 2):** one broadcast/playout-flavoured
incident scenario in `sim/` + a `showcase.py` tour segment speaking that buyer's
language. *Acceptance:* airplane-mode tour covers it end to end; kernel-hash and
MANIFEST updated together.

**P1.5 — Weekly gate report:** per-tenant HTML report (actions gated, approvals by
principal, standing-approval runs, rollbacks, approval latency, hours-returned)
generated from audit-log data ONLY. *Acceptance:* deterministic output from the
committed demo audit log fixture.

### P2 (optionality — only after P0+P1 are green)

- **P2.1** Design-partner deploy kit: docker-compose + hardening notes; SQLite→
  Postgres option for `precedent_memory` (precondition for any usage-billed or
  multi-tenant production deal); red-team page reusing the extractor-robustness
  and conformance benches as the security-review artifact.
- **P2.2** Analyzer PSA export formats (ConnectWise / Autotask / HaloPSA CSV) —
  keeps the parked MSP wave-2 open.
- **P2.3** Evidence-pack regulatory field mapping (DORA / FCA op-res / EU AI Act
  record-keeping vocabulary) — ONLY with a "pending legal review" banner; every
  export keeps the "evidence support, not a compliance determination" label.
- **P2.4** Wire `precedent_memory/probing_detection.py` into the retrieval path
  (fail-closed, audited) or visibly de-scope it in docs — one or the other.
- **P2.5** Microsoft Teams approvals — only if a paying design partner requires it.

## 5. Verified defect ledger (burn down; TDD each)

**P0 severity (trust-story or hosting blockers):**
1. `precedent/orchestrator.py` `commit_execution` (~lines 244–253): after a step
   reports ok=false it emits `execute_failed` and breaks, then unconditionally
   emits an `executed` audit event — the audit log records executed-after-failed.
   Failing test first; fix; extend the chain-consistency test to forbid
   `executed` after `execute_failed` for the same plan hash.
2. `agents/common.resolve_seed`: falls back to a committed dev seed when env seeds
   are unset → forgeable Watcher identity + derivable rails allowlist. Hard-fail
   (or refuse rails registration) unless an explicit dev flag is set; test both.
3. Single-tenant demo state (global `STATE`, `_PENDING`, flake row id=1) — fixed
   by P0.4's session scoping; keep a regression test for cross-session isolation.
4. SSE claim vs polling reality: `console/app.py` polls every 1.5 s while docs say
   SSE. Implement real SSE (sse-starlette is already a dependency) OR correct every
   claim surface — decide once, apply everywhere.
5. `PRECEDENT_DEV_MODELS` escape hatch in `precedent/models.py` disables the
   open-weight guard: refuse it outside an explicit dev context (e.g. also require
   `PRECEDENT_ENV=dev`), and test that the demo/container path cannot enable it.

**P1 severity:**
6. `precedent_memory/retrieve.py:24` imports `precedent.contracts` — the only
   parent-package import; invert the seam (move `Hit`/`RetrievalBundle` into the
   library or a shared module) so the "standalone" claim is literally true.
7. `tests/test_adversarial.py` lives at repo root but the bench's 6/6 attacks row
   shells out to it via pytest-output regex — move it in-package (or make the
   dependency explicit and tested) so packaging can't silently break the row.
8. `scripts/demo_server.py`: deprecated FastAPI `@app.on_event`; reaches into
   `STATE._lock` (private); `console/app.py` imports from `scripts.render_change_record`
   (console→scripts layering). Clean all three.
9. Hardcoded 60 s freshness window (`precedent_memory/db.FRESHNESS_WINDOW_SECONDS`)
   → configurable; protect the live-source-forces-real-sync gating (P0.6 behaviour)
   with an explicit regression test.
10. `audit.py` read-MAX-then-insert race: `BEGIN IMMEDIATE` hardening (relevant
    the moment sessions multiply); keep single-writer docs accurate.

**P2 severity (hygiene):**
11. `docs/evidence/README.md`: eight stale ⏳ rows although proofs landed
    (LIVE-PROOFS.md, bench/RESULTS.md, extractor_robustness.json) — point each row
    at its proof.
12. Stale docstrings: `precedent/__init__.py` ("stubs pending the Friday build"),
    `tests/test_scaffold_smoke.py` (claims skips that don't exist).
13. `precedent/bm25.py` + `data/embeddings/kb_vectors.json` unused by the runtime:
    wire into a candidate-ranking UX or remove both (removal strengthens the
    "no semantic similarity in the decision" story; keep the embeddings' compliance
    note in provenance docs either way).
14. `TriageResult.confidence` never populated — populate meaningfully or remove.
15. `sim/db.py` `kb_article.acl` column is display-only (enforcement lives in
    precedent_memory) — make the comment a docs note so nobody mistakes it for a
    control.

## 6. Verification gates (run them; paste outputs in the final report)

```bash
make check-open-weight    # model names only in precedent/models.py
make test                 # ≥256 passed, 0 skipped (suite grows with the scope)
make lint                 # ruff clean
make secrets-scan         # gitleaks full history, clean
make freeze-check         # all of the above + placeholder grep
make bench                # correctness fields byte-identical for seed 4207
make bench-extractor      # false-fast-path MUST stay 0
docker build -t precedent-demo . && docker run … # then Playwright tour + 2-session isolation against the container
```

Additional standing checks: gitleaks on staged changes before every commit;
airplane-mode run of the full demo tour; `GET /api/kernel-hash` matches
`MANIFEST.json` after any tour change; every number on any new surface traces to
`docs/numbers.md` with its label.

## 7. Cut-lines (fire in order if capacity runs short; never cut upward)

1. P2 entirely (each item is independently deferrable).
2. P1.5 weekly report → P1.4 scenario pack → P1.3 OSS staging → P1.2 TypeScript
   client (keep the Python client) → P1.1 live-Slack wiring (keep the fake-
   transport tests so it's wire-ready).
3. Within P0.4: cut the streaming flavour, never the session isolation, the
   rollback beat, the fail-closed beat, or the evidence-pack download.
4. NEVER cut: P0.1, P0.2, P0.3 acceptance tests, P0.6/§5 items 1–5, or any
   invariant in §2.

## 8. Working agreements

- Conventional, small commits on `main` (auto-published — see §2.4); each commit
  message states what gate it keeps green. Co-author trailer per repo convention.
- New code matches the existing idiom: typed pydantic contracts at boundaries,
  stdlib+sqlite in `precedent_memory`, no new heavyweight dependencies without a
  recorded reason (the Docker image must stay slim and offline-capable).
- Docs move with code: README gains a short Gate API + analyzer section when they
  land (keep the README's existing honesty labels); `docs/ops/services.md` gains
  any new env vars; `docs/demo/` gains the tour script.
- If a finding contradicts this prompt (e.g. an acceptance test is impossible as
  written), record the deviation in the final report with reasoning — do not
  silently reinterpret.
- Deliver a final report: what shipped per item, gate outputs, deviations,
  the defect-ledger scoreboard, and the exact human actions still required
  (Render deploy click-path via `render.yaml`, Slack app registration, OSS repo
  creation, DNS) — written to `docs/BUILD-REPORT.md`.

## 9. Definition of done

All P0 acceptance criteria green; §6 gates green end to end; the Docker image
passes the Playwright tour with two concurrent isolated sessions; the analyzer
byte-reproduces the UCI numbers under a sockets-disabled test; every §5 P0 defect
has a failing-test-first fix merged; `docs/BUILD-REPORT.md` written; no unlabelled
number, no `‹…›` placeholder, no secret, anywhere in the tree.
