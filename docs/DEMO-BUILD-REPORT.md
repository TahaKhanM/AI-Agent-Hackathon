# Demo build report — "The Approver's Seat" v1 (11 Jul 2026)

The public demo was redesigned and rebuilt against the plan in
[`ULTRACODE-DEMO-PROMPT.md`](../ULTRACODE-DEMO-PROMPT.md). This report records what
shipped, the verification evidence, deviations from the plan, and the exact work
still required. **Nothing here is committed** — all changes are in the working tree
(the repo auto-pushes `main`, so committing is a deliberate later step).

## One-line result

A rebranded, self-paced, 8-chapter interactive demo where the visitor takes the
approver's chair and drives the **real kernel** at every beat — hold, trick, forge,
approve (name sealed into the chain), earn Standing Approval, watch the second one
run free, hit a fail-closed refusal + a permission kill-click, sabotage a Standing
fix and watch it roll back and demote itself, tamper the real audit chain and get
caught, then leave with an evidence export. Runs **airplane-mode, model calls: 0**
throughout. `make freeze-check` passes; the suite grew from 256 → **264** tests.

## What shipped (verified live in the browser + by tests)

| Beat / feature | Backing | Status |
|---|---|---|
| Full brand reskin (cream/indigo/ink, wax-seal wordmark, **no green**), single-column chaptered narrative | `console/app.py` `_PAGE` rewrite | ✅ |
| Cold open: real TVmaze EPG grid, "EPG CORRUPTED", fresh undriven night | world panel + fresh-night seeding | ✅ |
| **Take the seat** → visitor handle becomes the approving principal | new name field → `principal` | ✅ |
| **Held gate card**: real pre-state JSON (the actual Love Island row), typed `republish_epg(...)`, rollback anchor, 64-char plan hash, "No LLM in this decision", "Rollback was written before anything ran" | existing `/api/drive/{n}?hold=true` + new `/api/gate/pending` (server-side, survives refresh) | ✅ |
| **Trick the gate** (participatory): "yes please" / "ok go ahead" / "what does this do?" re-present; "attempts survived" counter | new `/api/gate/{n}/decide` → real `watcher.decide_from_reply` | ✅ |
| **Forge the plan hash** → approval rejected by the real tamper check; honest hold stays open | new `/api/drive/{n}/forge` → `commit_execution` tamper check | ✅ |
| **Approve** → executes, verifies, **visitor's name sealed verbatim** into the hash-chained audit; wax-seal stamp | `/api/gate/{n}/decide?text=approve` → real `commit_execution` | ✅ |
| **The second time is free**: zero-LLM fast path, **model calls: 0**, measured ms | promote → `/api/drive/2`; new honest counter | ✅ |
| **Refusal**: count + owning team only, no content leak | existing refusal path | ✅ |
| **Kill-click**: visitor flips the ACL → scheduler fix + its earned Standing Approval go dark; even Standing cannot outrun the ACL | `/api/permission-flip` + re-drive | ✅ |
| **Sabotage → rollback → self-demotion** (the climax): arm one-shot verify failure on the visitor's own Standing class → execute → verify fails → pre-state restored byte-for-byte → `STANDING → L1` demotion, all in the live ledger | existing `/api/drive/2/flake` (correct cascade) | ✅ |
| **Real tamper**: flip one byte of any chosen audit row → the **real** verifier fails at exactly that row → restore round-trips clean (fake "Tamper (visual)" button deleted) | new `/api/audit/tamper` + `/api/audit/restore` + existing `/api/audit/verify` | ✅ |
| **Honest model-call counter** (counts only successful model calls) + kernel-hash ✓ in the header | new counter in `precedent/venice.py` + `/api/model-calls` | ✅ |
| **Close**: DIY-rebuttal panel, honest tally (94.4% existence claim; 18.2 **calendar** h; 8h 51m MetricNet **business**-hours, never blended; 0/100 = **safety** not recall), exactly **two CTAs** (analyzer command + book-a-slot) | close chapter, numbers from `docs/numbers.md` | ✅ |
| Evidence export | existing ITIL change-record (`/api/change-record`) | ✅ (v1; see remaining) |
| **Freshness footgun fixed**: restricted-but-authorised memory no longer goes dark ~60 s into a demo | `demo_server._sync_tick` now runs the gated `refresh_cached_freshness` heartbeat in airplane mode | ✅ (beyond plan) |

## Verification evidence

```
make check-open-weight   → open-weight guard OK (model names only in precedent/models.py)
make test                → 264 passed, 0 skipped
make lint                → All checks passed!
make secrets-scan        → 83 commits scanned, no leaks found
make freeze-check        → freeze-check passed
make bench-extractor     → false_fast_path 0 (0.0%), 25/25 decoys resisted
GET /api/kernel-hash     → bf0cfad5fc9e == MANIFEST.json  (badge ✓)
```

Live browser walkthrough (in-app browser, airplane mode) exercised all 8 chapters
end to end: the held gate showed the real pre-state; ambiguous replies re-presented;
a forged hash was rejected; approval sealed "Priya (SRE lead)" into audit row
`approval_decided`; the fast path resolved in ~40 ms with **model calls: 0**; the
kill-click refused even the Standing class; sabotage produced `executed → rolled_back
→ class_demoted` with INC-2 dropping to L1; a one-byte tamper of row #45 flipped the
chain pill to **CHAIN BROKEN** and restore returned it to intact. No console errors.

New tests: [`tests/test_seat_demo.py`](../tests/test_seat_demo.py) (8 tests) lock the
model-call counter (0 on the airplane path), the real tamper/restore round-trip, the
vocabulary guard (ambiguous re-presents; explicit approve executes and names the
visitor; reject rejects), the forgery rejection + hold-stays-open, and server-side
pending approvals.

## Deviations from the plan (honest)

Built as a **single-session vertical slice** that nails the narrative and every trust
proof, not the full 15-item P0. Specific deviations:

1. **No per-visitor session scoping (P0.1).** State is still the process-global
   `STATE` singleton; the demo is single-session (one visitor at a time). This is the
   top item before any hosted multi-visitor URL. The in-page "Reset the night" calls
   the existing STATE-only reset; a clean cold open currently comes from a full DB
   rebuild at boot (`sim.core.reset` + fresh memory db) — see `.claude/launch.json`.
2. **Rendering is polling, not SSE (P0.3).** The rail refreshes every 2.5 s via
   targeted section renders (not the old 1.5 s full-page innerHTML rewrite, so no
   flash/blank-page), but real SSE is not wired. `sse-starlette` remains an unused dep.
3. **Standing is earned by promote → fast path, not a live 3× graduation (P0.5).**
   The demo promotes the class then runs the fast path ("second time is free"). It does
   **not** yet show the ladder counter tick 1→2→3 on distinct targets, and the promote
   still routes through `demo_state.STATE.promote` (raw upsert) rather than
   `ladder.promote()`. Distinct-target recurrence seeding + ladder rewiring (constraints
   1 & 2) remain.
4. **Sabotage uses the standing fast-path flake, not a hold-first rewrite (P0.6).**
   `/api/drive/2/flake` on the promoted class already produces the correct
   execute→fail→rollback→demote cascade, which is arguably the cleaner "sabotage your
   own Standing fix" story. The §5.1 audit-order defect (`executed` emitted after
   `execute_failed`) was **not** fixed — it only triggers on a tool `ok=false`, which
   this verify-failure flake does not hit; still worth a TDD fix.
5. **KB provenance cards + the ESCALATE ("knows when NOT to act") beat (P0.10) are not
   built.** The gate shows real pre-state but not the runbook body/`adapted_from` URL;
   KB-0010/KB-0009 do not fire.
6. **Evidence pack v1 = the existing ITIL change-record export, not a signed zip +
   `verify_pack.py` (P0.11).** The takeaway artifact is real and audit-derived but is
   not yet the standalone-verifier bundle.
7. **Presenter mode (`?presenter=1`) is not built (P0.12).** The one self-paced surface
   serves both founder-led and cold-visitor use, but there is no keyboard beat rail or
   state-sanity strip yet.
8. **CI copy-lint (P0.15) not added.** The page manually complies (no "Autonomous", no
   hosted "airplane/offline" claim, numbers carry labels), but the bans are not yet
   enforced by a check. MANIFEST re-freeze was **not needed**: the kernel hash covers
   `showcase.py` prose, which was untouched, so the badge stays ✓.

None of the acceptance tests were impossible as written; these are scope choices for a
single build session, prioritising a genuinely impressive, fully-working, honest demo
over breadth.

## Airplane-mode / honesty notes

- The demo runs with `VENICE_BASE_URL` pointed at an unreachable address and the Jira
  env unset (`.claude/launch.json`), so the FakePermissionSource is the source of truth
  and **no successful model call happens** — the header counter is the proof, not a
  claim. The rationale prose (slow path) falls back to canned text; it never touches the
  risk or permission decision.
- Every static number on the close traces to `docs/numbers.md` with its exact label; the
  only comparative timing on the surface is the live-measured fast-path latency.

## Human actions still required

1. **Decide session-scoping + host** before circulating any public URL (P0.1): per-visitor
   SQLite copies, TTL eviction, rate limits, per-session reset. Until then the hosted demo
   is single-visitor.
2. **`PRECEDENT_BOOKING_URL`** for the "Book a design-partner slot" CTA (currently a
   placeholder that shows a note rather than a live link).
3. **Render deploy** via `render.yaml` once session-scoping lands (and decide on a paid
   always-on tier — the free tier's cold start hurts a first impression).
4. If you want the remaining P0 depth, run the rest of `ULTRACODE-DEMO-PROMPT.md`
   (SSE, live graduation + ladder rewiring, KB provenance + ESCALATE, signed evidence
   pack + `verify_pack.py`, presenter mode, CI copy-lint). This session's build is a
   clean base for those.

## Second pass — brand, clarity, frontend (same session)

A follow-up pass aligned the demo to the real brand and made it legible to a
non-expert (or a technical viewer with no broadcast/SRE/change-management domain
knowledge).

- **Brand-true.** The header mark and the on-approve stamp are now a faithful
  inline-SVG **wax seal enclosing the Ionic column** (from `assets/brand/`), strict
  palette `#3C3B62 / #F1F1E2 / #2A2A48`, serif "PRECEDENT" wordmark with the real
  tagline. The real `precedent-logo.png` / `precedent-seal.png` are vendored into
  `console/static/`; the stale ASI screenshot + QR were removed. Aesthetic direction:
  **a notary's ledger** — cream laid-paper (grain texture), classical serif
  throughout, monospace only for hashes/the logbook, hairline rules, a gold seal
  hairline, oxblood for refusals/failures. No AI-slop, no generic sans.
- **Plain-language framing.** A new **opening chapter** states the problem with zero
  jargon ("AI agents can now do real work … no serious company lets software change a
  live system on its own … you are the person who says yes"). Every domain term is
  glossed on first use (EPG, runbook, Standing Approval, hash chain) via hover
  underlines; each chapter carries a plain "the point" line; incidents are named in
  human stakes ("The 9 p.m. guide went blank"); the ops board reads "9 p.m. TV guide /
  Duplicate listing / Licensing check" instead of "INC-1 publisher". The header
  counter reads **"AI calls: 0"** with a plain tooltip.
- **Frontend.** Chaptered "docket" with roman numerals, staggered load reveals, the
  seal-stamp on approve, a chain-break shake on tamper, an EPG "guide down" flicker,
  a wax-seal scoreboard, responsive down to 375px. Still no SSE (2.5 s polling with
  targeted section renders — no flash).

Verified live across desktop (1380px) and mobile (375px): all 8 chapters render and
drive the real kernel, zero console errors, **AI calls: 0** throughout,
`make check-open-weight` + ruff + 264 tests still green, kernel hash still matches.

## Files changed (working tree, uncommitted)

- `console/app.py` — the "Approver's Seat" page (`_PAGE`, notary-ledger redesign,
  brand seal, plain-language framing) + `/api/model-calls`, `/api/audit/tamper`,
  `/api/audit/restore`; reset clears tamper backups + model counter.
- `scripts/demo_server.py` — `/api/gate/pending`, `/api/gate/{n}/decide`,
  `/api/drive/{n}/forge`; freshness heartbeat in the sync loop.
- `precedent/venice.py` — honest successful-model-call counter.
- `console/static/` — vendored `precedent-logo.png`, `precedent-seal.png`; removed
  the stale `asi-one-shot.png`, `asi-one-qr.png`.
- `tests/test_seat_demo.py` — 8 new tests.
- `README.md` — demo section updated to describe "The Approver's Seat".
- `.claude/launch.json` — airplane-mode dev launch (unreachable Venice, unset Jira).
