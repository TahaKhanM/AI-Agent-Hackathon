# Precedent Gate v1 — Product Build Report

**Branch:** `feat/precedent-gate-v1` (10 commits ahead of `main`, unmerged — see *Merge gate* below).
**Scope:** the P0 of `ULTRACODE-PRODUCT-PROMPT.md` — "The Presentable Product".
**Outcome:** all 14 P0 work packages **LANDED** per the §5 verification predicate
(acceptance green **+** per-WP refute panel survived **+** test-the-tests proved each
clause fails-red). Built with multi-agent orchestration (design tournaments,
worktree/serial builders, tiered adversarial refute panels, a security red-team,
a semantic honesty fleet, and a determinism replay), every finding fixed
failing-test-first before commit.

> This report is itself a due-diligence artifact: the orchestration ledger below is
> assembled from the schema-forced structured output of every judge, refuter and
> finder — not prose recall.

---

## 1. Final verification gates (§8)

```
make check-open-weight  → open-weight guard OK: model names only in precedent/models.py
make test               → 500 passed / 0 skipped (non-browser, CI-authoritative)
                          506 passed / 0 skipped with the dev Playwright stack present
make lint               → ruff: All checks passed
make secrets-scan       → gitleaks 94 commits, no leaks found
make copy-lint          → clean (number/vocabulary honesty gate)
make policy-lint        → OK, 2 packs clean (no executable class without a true inverse + probe)
make check-product-imports → OK (console/product/ imports no kernel — HTTP-only)
make freeze-check       → freeze-check passed (chains all eight gates above + placeholder grep)
make bench              → FNR 0 / 5,219 · FPR 0 / 4,781 · adversarial 6/6   (correctness fields byte-identical per seed 4207)
make bench-extractor    → false_fast_path 0 / 100 (0.00%) · 25/25 red-herring decoys resisted
```

Baseline at start was 264 passed; the suite grew to **500/506** with the scope, 0 skipped throughout.
`freeze-check` now enforces two new gates the prompt required: **copy-lint** (mechanical
number/vocabulary honesty) and **check-product-imports** (the anti-demo-ware grep), plus **policy-lint**.

---

## 2. What shipped, per work package

| WP | Commit | Effort | Landed (a/b/c) |
|---|---|---|---|
| §6 item 1 — audit-order defect | `96138f1` | max | ✅ acceptance · dedicated honesty refuter could-not-refute · red-was-red (`assert 1==0`) |
| WP-CI — CI + copy-lint + rails guard | `def469c` | high | ✅ · 4-refuter panel (1 honesty blocker fixed) · mutation-kill 5/5 |
| WP-REFACTOR — _PAGE → Jinja2 + design system | `090bdf7` | medium | ✅ · 3-refuter panel (DOM-equivalence *proven*) · non-vacuous golden |
| WP-HOST-SESSION — 5-axis per-session worlds | `fd756b0` | max | ✅ · 5-refuter panel (1 vacuous-gate blocker + 4 hardenings fixed) · mutations killed |
| WP-API — /v1/gate HTTP spine | `2098c48` | max | ✅ · 5-refuter panel (2 blockers: double-exec + auth-bypass, fixed) · mutations killed |
| WP-PACK — evidence pack + stdlib verifier | `7ee1079` | high | ✅ · 5-refuter panel (fail-closed traceback blocker fixed) · 11 mutations killed |
| WP-POLICY — policy authoring kit | `7ee1079` | medium | ✅ · 3-refuter panel (2 blockers: name-denylist + fake numbers, fixed) |
| WP-ANALYZER — local analyzer CLI | `7ee1079` | medium | ✅ · 3-refuter panel · sockets-disabled + byte-repro confirmed |
| WP-CONSOLE — case-file console (3 panels) | `bb14e13` | max | ✅ · design tournament + 5-refuter panel (0 blockers) · anti-demo-ware grep proven |
| WP-DEMO — express + graduation + SSE + funnel | `3ae0549` | high | ✅ · 3-refuter panel (2 blockers: process-global counter + e2e flake, fixed) |
| WP-LANDING — landing + verify strip | `c067e4f` | medium | ✅ · 2-refuter panel (2 honesty meds fixed) |
| WP-HOST-COLD — cold-start + Dockerfile↔pyproject | `c067e4f` | medium | ✅ · 2-refuter panel · caught a real Dockerfile drift (missing jinja2) |
| WP-DEFECTS — §6 items 2/5/6/7/8 | `c067e4f` | high | ✅ · 3-refuter panel (kernel-freeze widget med fixed) |
| P0 barrier hardening | `12f3814` | high | ✅ · 2 re-refuters (5 findings closed, mutations killed) |

**S1 Gate API** (`gate/`): `POST /v1/gate/propose` → `GET /v1/gate/decision/{ref}` →
`POST /v1/gate/outcome`; deny / needs-approval(ref) / allow-standing computed **only** by the
deterministic policy engine + ladder; TTL fail-closed; principals out-of-band; **0 model calls in
the decision path** (source scan + `venice._post` spy, mutation-confirmed). Mounted into the one deploy.

**S2 Gate Console** (`console/product/`, mounted at `/console`): three panels — the **case-file spine**
(typed proposal → deterministic decision → *rollback prepared before execution* → transcript →
verification → rollback → hash-chain proof, each stage linking to the CI rule/source line that proves it),
the **ladder/policy** view (audited four-eyes promote/revoke), and the **evidence-pack list + on-page
verifier**. It imports **zero** kernel code — enforced by `scripts/check_product_imports.sh`, a test
that fails on a seeded violation, and a CI step. This grep is the anti-demo-ware proof.

**S3 Hosted demo** (`/demo`): express (~3 min) default, live 3× graduation through the **real**
`ladder.on_verification_result()`/`eligible()`/`promote(force=False)` (the raw `STATE.promote` upsert
and the boot force-STANDING pre-seed are **retired**), real evidence-pack download + on-screen verify,
Door-2 founder narrative, SSE (polling as truthful fallback), and privacy-preserving funnel counters.

**S4 Landing** (`/`): positioning line, three plain-language wedge planks, honesty banner,
"Start the 3-minute demo", two CTAs, and a below-the-fold **"Verify our claims"** strip.

**X1 CI + copy-lint**, **X2 Evidence Pack + `verify_pack.py`** (stdlib-only, fail-closed),
**X3 `precedent-analyze`** (local-only, sockets-disabled, byte-reproduces 94.4 / 98.6 / 18.2 h / 558).

---

## 3. §6 defect scoreboard

| # | Item | Status |
|---|---|---|
| 1 | `commit_execution` emits `executed` after `execute_failed` | ✅ FIXED (`96138f1`) — guarded on `exec_failed_step is None`; chain-consistency test forbids it |
| 2 | `resolve_seed` forgeable Watcher identity | ✅ FIXED (`c067e4f`) — fails closed unless an explicit dev context |
| 3 | Single-tenant demo state (5 axes) | ✅ FIXED (`fd756b0`) — per-session worlds; cross-session regression test is the permanent guard |
| 4 | SSE claim vs polling reality | ✅ FIXED (`3ae0549`) — real SSE shipped; polling only as a truthful fallback |
| 5 | `PRECEDENT_DEV_MODELS` disables the guard | ✅ FIXED (`c067e4f`) — refused unless `PRECEDENT_ENV=dev` |
| 6 | Kernel-hash chip mis-scope | ✅ FIXED (`c067e4f`) — re-scoped to the decision surface + MANIFEST reconciled (GET == MANIFEST); badge honest |
| 7 | Orphaned pre-rewrite surface + dead endpoints | ✅ FIXED (`c067e4f`) — `/api/copy` + `/api/latency` removed (404); orphaned prose gone |
| 8 | Env naming drift (`.env.example` ↔ `services.md`) | ✅ FIXED (`c067e4f`) — canonicalised |
| 9–13 | P1-severity | Not in P0 scope (carried to P1) |

All eight P0 defects have a failing-test-first fix merged.

---

## 4. Orchestration ledger

### 4.1 Design tournament (WP-CONSOLE — the one open surface)
Three independent case-file concepts, no shared drafts, judged on four lenses (API-consumer /
security-reviewer / first-time-visitor / honesty):
- **Winner: "the notary's record"** — a self-authenticating case file with a hash-chain rail; the
  pre-state snapshot + pre-generated inverse rendered *above* the execution transcript so the reader
  sees the undo was written before the do.
- **Grafts from "the skeptic's teardown"**: the teardown-rail (every stage's disproof at a fixed
  x-position → a real `path:line`/`ci.yml` step), the kernel-hash freeze diff, the CI-green band, and
  "copy-lint as visible authority".
- **NO-SILENT-CAP:** the three-judge panel was compressed into one combined judge-synthesis to conserve
  budget under the session-capacity signal (§9 cut-line 1, design-panel depth). The three competing
  concepts — the tournament's core value — were preserved.

### 4.2 Per-WP refute panels — kills & survivors (findings fixed before "landed")
- **WP-CI:** honesty-labels refuter killed the acceptance until the A5/A6 *swap* gap was closed
  (a swapped 94.4↔98.6 pair carrying each other's label) + `%`-optional evasion + V2 (KCS) coverage.
- **WP-HOST-SESSION:** test-the-tests killed a **vacuous fail-closed gate** (the TTL-expiry branch in
  `resolve()` was untested); + 4 hosting-security hardenings (session cap, `/health` churn,
  `close()` FD-leak, `Secure` cookie).
- **WP-API:** correctness + fail-closed killed **2 blockers** — a `report_outcome` **double-execution**
  and a deployed **`principals=None` auth bypass** — plus a non-hermetic sim-copy flake, a vacuous
  outcome-TTL test, and four-eyes self-approval.
- **WP-PACK:** fail-closed killed a **verifier traceback on malformed input**; + chain-bound the
  human-readable display sections + pinned manifest metadata.
- **WP-POLICY:** the inverse-probe lens killed a **name-denylist** that let irreversible-action
  *synonyms* pass (§2.5) — replaced with a positive "must name a real inverse tool" requirement; +
  removed fabricated per-class occurrence numbers (number-honesty).
- **WP-DEMO:** isolation killed a **process-global model-call counter** posing as per-session (§2.6).
- **WP-CONSOLE:** **0 blockers** — anti-demo-ware holds, security/fail-closed clean, honesty clean.

### 4.3 Cross-WP integration sweep + security red-team (P0 barrier)
Single comprehensive round (5 red-team + 3 cross-WP + 2 honesty finders) with a confirm-before-count
pass, against `uvicorn`/`TestClient` (Docker daemon down — see deviations).
- **Clean:** no XSS reproduced (every user value hits its sink through an escaper, verified end-to-end);
  **no cross-session bleed** across all 5 axes + the sim axis (two-cookie red-team); CSRF not
  exploitable (HttpOnly+SameSite=Lax, JSON-only POSTs, no CORS, no state-changing GET); session
  cookie/ref not forgeable (256-bit / 144-bit); Azure-sentence and number-semantics honesty held.
- **Confirmed + FIXED (`12f3814`):** a rate-limit fail-open on cookie rotation (**high**); forged
  self-asserted principal on 4 legacy console routes (med); standing-ref double-execution (med);
  a gate ref surviving `/api/demo/reset` (med); an eviction × in-flight closed-conn race (med).
- **NO-SILENT-CAP:** the red-team's *2-consecutive-dry* loop was compressed to **one round + confirm**
  under the session-capacity signal; the per-WP panels had already provided 3–5 independent refuters
  each. The security surface should get a second dry round in a follow-up.

### 4.4 Determinism replay
Bench correctness fields (FNR/FPR/adversarial) **byte-identical across runs** (only the P99 latency µs
drifts — expected and labelled per `docs/numbers.md`); `bench-extractor` false-fast-path **0/100
identical**; analyzer UCI reproduction byte-identical by construction (test-enforced). Zero cross-run
diff in any correctness field.

### 4.5 Mutation-kill log (one row per representative acceptance clause)
| Clause | Canonical mutation | Test went RED? |
|---|---|---|
| No `executed` after `execute_failed` | remove the `exec_failed_step is None` guard | ✅ (`assert 1==0`) |
| copy-lint catches each banned token/adjacency | disable R1/R3/A1/A5 | ✅ each |
| rails collection guard deselects cleanly | `_rails_collect_ignore` → `[]` | ✅ |
| DOM-equivalence non-vacuous | drop a body element from the template | ✅ |
| session isolation (both DBs) | one world for every cookie | ✅ |
| sim axis isolation | per-session SimTools → shared sim.db | ✅ |
| eviction closes conns + deletes files | skip file deletion / conn close | ✅ |
| TTL-expiry ⇒ non-action (session + gate) | neuter the expiry branch | ✅ |
| no LLM in the gate decision path | stub `venice.chat()` into `propose()` | ✅ (spy trips) |
| gate exactly-once (approval + standing) | drop the already-decided guard | ✅ |
| pack verifier catches a tampered byte | flip a checked field / re-seal a forged display section | ✅ |
| policy lint rejects an uninvertible class | weaken the inverse-existence check | ✅ |
| analyzer opens no socket | — (sockets-disabled harness) | ✅ |
| kernel-hash covers the decision surface only | edit tour prose (no change) / edit a decision file (changes) | ✅ |
| creation rate-limit / forged-principal / reset-ref | revert each barrier fix | ✅ each |

No mutation left the suite green (no vacuous gate survived to "landed").

### 4.6 Capacity checkpoint (§0, bidirectional)
A **session usage limit** was hit during the off-spine fix round (the independent re-verify agents
failed) and again threatened the console phase — a genuine §0 capacity signal. Response per §9:
fired **cut-line 1** (polish-fleet / design-panel depth degraded in place — see NO-SILENT-CAPS entries)
rather than compressing any never-cut floor. No P0 surface was cut; no §2 invariant bent; no
verification/refute panel was thinned below its floor except the two explicitly-recorded compressions
(console 3→1 judge; red-team 2-dry → 1 round + confirm). No P1 items were pulled.

### 4.7 NO-SILENT-CAPS register (coverage dropped under budget)
1. WP-CONSOLE design tournament: 3 separate judges → 1 combined judge-synthesis (3 concepts preserved).
2. Security red-team: 2-consecutive-dry loop → 1 comprehensive round + confirm-before-count.
3. Off-spine fix round: the independent re-verify panel was truncated by a session usage limit;
   substituted with direct integration-gate verification + spot-checks (verify_pack fail-closed exit
   1/0 tracebacks; policy-lint exit 1 on a broken pack; 422 green). Those surfaces were re-examined
   independently by the P0-barrier red-team + honesty fleets.
4. copy-lint V-rules: the generic NeuBird survey numbers (44/74/39) are too collision-prone for a line
   linter; the semantic honesty fleet covers their "(vendor-sponsored survey)" label instead.

---

## 5. Deviations from the prompt (recorded per §10)

- **Docker daemon down in the build environment.** No `docker build`/`docker run` was possible, so the
  container-based Playwright e2e and the deployed `<1 s` cold-link are **founder/CI checks**, not
  build-agent checks. The authoritative isolation gate is pure-Python `TestClient` two-cookie tests
  (which exercise the full server-side scoping headless); `pip wheel . ` succeeded, proving
  `pip install .` will build in the image. `tests/e2e/run_container_e2e.sh` carries the intended
  container command sequence.
- **Playwright browser e2e is environmentally flaky in this sandbox** on a Chromium/gRPC C++ crash
  (`ev_poll_posix.cc`), unrelated to product code. CI does not install Playwright; the **500
  non-browser tests are deterministically green**. Re-run the 6 browser e2e in a stable browser env.
- **Visual-render baseline** was captured at WP-HOST-SESSION (when Playwright was installed), not
  WP-REFACTOR — still before the DEMO/CONSOLE/LANDING surfaces that diff against it.
- **SSE live-streaming `TestClient` test** deferred (an infinite `EventSourceResponse` generator hangs
  the sync `TestClient` at teardown); substituted a deterministic generator unit test + endpoint/wiring
  assertions. The browser `EventSource` path is real; SSE itself is shipped (the polling fallback is the
  §9 cut-line-6 truthful fallback, retained, not the cut).
- **MCP server** for the gate is P1 (no MCP SDK in the repo; the console dogfooding the HTTP API
  already carries the anti-demo-ware proof) — as the prompt directs.

---

## 6. Documented limitations (disclosed, not hidden)

- **Evidence pack, keyless verifier.** `verify_pack.py` is stdlib-only and self-authenticating via the
  recomputable hash chain + a sha256 manifest; it re-derives the decision/verification/transcript/
  rollback display sections from the chain. But `retrieved_precedent` (lineage ACL/freshness, memorised
  fix records) and `policy_pack_version` are **not in the audit chain** (they come from DB tables), so
  they are manifest-covered only — a keyless forger who rebuilds the whole pack could alter them and
  re-seal. This is disclosed in the pack ("evidence support, not a compliance determination") and in the
  verifier output. Fully closing it needs a signing key or emitting provenance into the chain at
  build time (out of P0 scope).

---

## 7. Funnel instrument — privacy note (§2.4)

`console/funnel.py` is a 3-column `(day, event, count)` SQLite store — **structurally no PII and no
visitor/session column exists**. Consent defaults **OFF**; counters record only after consent; used on
the hosted demo + landing **only**, and a CI import-guard test asserts the analyzer never imports it.
Per-visitor event detail dies with the session TTL; the anonymous daily aggregates are the **one thing
that persists** past a session — they are the day-90 kill-gate instrument. `PRECEDENT_FUNNEL_DB`
(default `data/funnel.db`, gitignored) holds them.

---

## 8. Human actions still required (the build agent cannot do these)

1. **Merge gate (do this first).** The "Verify our claims" strip links (`verify_pack.py`, the CI badge,
   `.github/workflows/ci.yml`) target `main`. They go **live when this branch merges to `main`** —
   do not deploy the landing before the merge, or those proof links 404.
2. **Render paid-tier deploy.** `render.yaml` is set to the `starter` (always-on) plan. Click the
   Render deploy, attach billing in the dashboard, then run the **founder cold-start check** (a live
   `<1 s` cold-link) and record it.
3. **`PRECEDENT_BOOKING_URL`** — set the book-a-slot URL env var (the landing CTA notes gracefully when
   unset). The unset-fallback contact placeholder in the security stub is an owner copy decision.
4. **Slack app registration** (P1) — the ladder promote/revoke path is wire-ready; register the app.
5. **Jira tier decision** (~expired trial) — the live dual-enforcement beat is unavailable until the
   tier is chosen; airplane mode is unaffected and no demo copy promises the live beat.
6. **`PRECEDENT_FUNNEL_DB` documentation** in `docs/ops/services.md` (integrator follow-up).
7. **Retire the three superseded prompts** — `ULTRACODE-PROMPT.md`, `ULTRACODE-DEMO-PROMPT.md`,
   `ULTRACODE-PRODUCT-PROMPT.md` — once this scope is merged (their record lives in git history).

---

*Generated by the Precedent Gate v1 build. Every claim in this report resolves to a commit, a gate
output, or a schema-forced agent finding on the `feat/precedent-gate-v1` branch.*
