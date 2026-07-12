# ULTRACODE BUILD PROMPT — "The Approver's Seat" (Precedent demo v2)

> Paste this entire file as the prompt for an Opus 4.8 **ultracode** session opened
> in this repository. It is self-contained, but the session MUST load the repo skill
> and read the referenced docs before writing code.
>
> **Relationship to [`ULTRACODE-PROMPT.md`](ULTRACODE-PROMPT.md):** this prompt
> SUPERSEDES that file's §P0.4 (hosted demo) and absorbs its §5 defect items 1, 3
> and 4. If the P0 scope from that file has already landed (Gate API, evidence
> pack, analyzer), reuse those artifacts here instead of rebuilding; if it has
> not, this prompt is independently buildable and includes the minimal evidence
> pack it needs. Delete this file once the demo has shipped (its record lives in
> git history and `docs/DEMO-BUILD-REPORT.md`).
>
> Provenance: this design is the output of an 11 Jul 2026 multi-agent run —
> six repo readers + a code-level completeness critic, then four independent
> demo concepts (theatre / participation / credibility / buyer angles) scored by
> four audience-lens judges (non-technical exec, skeptical engineer,
> design-partner buyer, demo producer), then a synthesis pass. Every build
> constraint in §5 was verified against the actual code, not assumed.

ultracode

## 0. Mission

Rebuild Precedent's public demo as **"The Approver's Seat"** — one build, two
drive modes:

> **Your agent proposes. Precedent decides.** A live incident war-room where the
> visitor takes the approver's chair: they gate the agent, fail to trick it, earn
> it Standing Approval, sabotage it, watch it roll back byte-for-byte and demote
> itself — then leave with a tamper-evident evidence pack bearing their own name.

The current demo (console/ + showcase.py) is a competent hackathon dashboard
with a passive caption tour: every tour beat has `action: None`, the incidents
are already resolved when the page loads, the strongest capabilities (rollback
arc, permission flip, offline chat loop, KB provenance) are hidden behind small
buttons or curl-only endpoints, and the framing is sponsor-track language. The
kernel underneath is real, green (256/256 tests) and airplane-mode safe. You are
building a new demo SURFACE and choreography on top of an engine that already
works — the engine's contracts (`prepare()`/`commit_execution()`, the ladder,
the memory layer) must not change except where §5 names a defect.

**Two audiences, both must leave impressed.** Non-technical (exec, buyer,
investor): visible cause-and-effect, stakes, a break-and-recover climax, their
own name in the artifact they take home. Technical (staff engineer, security
reviewer): falsifiable live proofs — a zero-LLM fast path they can time, a real
tamper they perform themselves, a chain verifier that catches it, real data, no
canned theatre. Two modes from ONE build: a cold self-guided hosted tour
(self-paced, ~8–9 min full / ~3 min express) and a founder-led live pitch
(~3 min express cut, ~7 min buyer-meeting cut) via `?presenter=1`.

**Capacity model:** ~2–3 weeks agent-accelerated. P0 is the demo that ships; P1
is depth for skeptics; cut from the bottom (§9), never a P0 item for a P1 polish.

## 1. Read before any code (in this order)

1. `.claude/skills/precedent/SKILL.md` — load via the Skill tool. The four hard
   rules and conventions are CI-enforced.
2. `docs/DIRECTION.md` — the decided Gate story, the two doors, the two CTAs,
   what was killed and why.
3. `docs/numbers.md` — the ONLY numbers any surface may render, with labels.
4. `docs/demo/airplane-mode.md` + `docs/demo/one-minute-demo.md` — the current
   choreography (note: the one-minute script is silently broken; see §5.9).
5. `console/app.py`, `console/demo_state.py`, `console/showcase.py`,
   `scripts/demo_server.py` — the surface you are replacing.
6. `agents/watcher.py` (`serve_chat_turn`, `decide_from_reply`, `greeting`) —
   the pure offline chat loop that becomes the demo's core primitive.
7. `precedent/ladder.py` (`eligible`, `promote`, `demote`,
   `on_verification_result`, the anti-gaming window) — the graduation mechanics.
8. §5 of this file — the verified constraint/defect ledger. Every item there was
   confirmed against the code; do not rediscover them, fix them.

## 2. Non-negotiable invariants (violating any of these fails the build)

1. **Open-weight only, one registry.** No model id anywhere except
   `precedent/models.py`. Guard: `make check-open-weight`.
2. **No LLM in any permission or risk decision.** The demo adds NO path where
   model output picks an action, sets a class, or unlocks a ladder level.
   `precedent_memory/retrieve.py` keeps zero LLM imports. The chat panel calls
   the same deterministic guards the tests spy on.
3. **Fail-closed.** Expired/absent approvals are non-action. Refusals disclose
   only a live-rendered count + owning team — never content. Every new failure
   path (session eviction, rate limit, chat ambiguity) fails toward non-action.
4. **No secrets; committing to `main` IS publishing.** The repo is public with
   an external auto-sync. `gitleaks protect --staged` before every commit;
   `make secrets-scan` before ending any session. Visitor handles are
   session-scoped, TTL-evicted, never persisted, never shown to other sessions.
5. **Rollback precedes execution.** Unchanged: no plan without a pre-state
   snapshot and pre-generated inverse. The demo makes this VISIBLE ("Rollback
   was written before anything ran") — it never weakens it.
6. **Honesty rules on every rendered surface.**
   - L3 is **"Standing Approval"**, never "Autonomous" — add a copy-lint check
     that bans the word on the demo surface.
   - Static numbers render ONLY from `docs/numbers.md`, through ONE shared
     component, with their exact labels: 94.4% = existence claim; 98.6% =
     arrival-knowable; 18.2 h = CALENDAR (ours) never blended with 8h51m =
     BUSINESS (MetricNet); 558 classes ≥4 occ → 94.8% of volume; naive floor
     top-3 87.7% is never product accuracy; 0/100 false-fast-paths is a SAFETY
     number, never recall (recovery was 8/100 on that adversarial corpus — say
     so wherever recall could be inferred); "25k-record store", never "141k
     events"; vendor numbers carry "(vendor-claimed)".
   - The ONLY comparative timings on the surface are live-measured in-session
     and labelled "(measured just now)". The current "26.5 hours saved",
     "~60s", "~15s" strings are deleted (§5.11).
   - Hosted mode NEVER claims "airplane" or "offline" (it's a hosted server —
     the claim would be false). Hosted attestation = kernel-hash ✓ + a live
     per-session model-call counter reading 0. The literal Wi-Fi-off proof
     exists only in presenter mode, where it is physically true.
   - Denial copy interpolates the REAL denied count from the response — never a
     hardcoded number.
7. **Determinism.** Canonical seed 4207. The cold-open incident, recurrence
   seeding and replay control are byte-identical per seed. Any change to
   checked-in demo copy requires a deliberate MANIFEST re-freeze (§4.15) or the
   kernel-hash badge shows ✗ on stage.

## 3. The demo you are building

### 3.1 Shape: one surface, two drive modes

- **Hosted self-guided** (default): chaptered, self-paced, resumable. The
  visitor drives every beat; a "Watch instead" link runs the same beats
  auto-paced for lean-back visitors. Refresh mid-tour resumes the same chapter
  with state intact (server-side session chapter state).
- **Presenter mode** (`?presenter=1`, same build): keyboard beat rail (number
  keys inject each beat's canonical ticket text — no live typing risk), one
  focal card per beat, captions become speaker notes, larger type, a
  presenter-only state-sanity strip (flake armed / ACL flip hot / ladder level /
  pending holds), and a one-key seed-4207 full reset. The founder hands "the
  seat" to a buyer's own phone via the hosted URL (isolated session) — no
  hotspot hardware is ever load-bearing. In buyer meetings the BUYER clicks
  Approve and Promote, never the founder.
- **Express path** (~3 min): a pre-earned Standing class lets the arc compress
  to break → hold + trick + forgery + approve → second-time-free →
  sabotage/rollback → tamper + evidence → two CTAs. Serves both the strict
  founder slot and the impatient cold visitor. The full path (with live
  graduation and the kill-click) is the default hosted tour.

### 3.2 Narrative arc (build exactly this; copy in quotes is canonical)

**Beat 0 — The break, then the seat** (0:00–0:25). Page loads into the
indigo/cream brand and a real EPG grid from TVmaze rows. Two seconds in, the
actual Love Island row visibly corrupts with an alert flash — the world breaks
BEFORE any framing copy. Header chrome: kernel-hash ✓ (vs MANIFEST.json) and
"Model calls this session: 0". Then the seat card: *"Your team's agent already
knows the fix. The question is whether it's ALLOWED to act."* / *"It can act.
You decide whether it's allowed to. Approving as: ___"* with the notice "This
name is written into your downloadable record" (default `visitor@<session-id>`)
and a "Watch instead" link. Footer: *"Every incident resolved becomes
precedent."*

**Beat 1 — The incident lands: one held gate card** (0:25–1:30). A messy
free-text on-call ticket is pre-drafted into the chat panel (wired to
`serve_chat_turn`); the visitor may edit it — it still resolves
deterministically or fails closed. On send: the extractor parses, the sha256
fingerprint preimage (`service|error_code|target_object_type`) assembles on
screen, retrieval renders the runbook card LARGE with its real provenance
front-matter (`adapted_from` URL, `last_reviewed`), the YAML policy pack
risk-classifies with matched lines highlighted. `prepare()` stops dead at ONE
server-side, session-persistent gate card: real pre-state JSON, the typed call
`republish_epg({...})`, the pre-generated inverse, the 64-char plan hash, a
10-minute TTL. Card chrome: "Policy pack v‹N› · No LLM in this decision" badge
linking to the actual CI rule, and *"Rollback was written before anything
ran."* A quiet timer starts measuring how long THEIR approval takes.
Plain-English verdict is always primary; raw JSON is one click deep.

**Beat 2 — Try to trick it, then forge the paperwork** (1:30–2:50). The UI
dares the visitor: *"Before you approve — try to trick it."* Suggestion chips
PREFILL (never auto-send) the vocabulary-guard corpus — "yes please", "ok go
ahead", "sounds good — what does this do exactly?", "don't approve— actually
fine, do it". Every attempt re-presents the card (*"Ambiguous. Here is the card
again. Only an explicit approval executes."*); an "attempts survived" counter
ticks. Then the forgery: an "edit the hash" affordance lets them change one hex
character of the plan hash — their approval is REJECTED by the real tamper
check (*"REJECTED — approved hash does not match the held plan."*). Finally the
explicit approve: `commit_execution()` runs — snapshot, typed call, verify ✓ —
the broken row visibly repairs in the world panel, and a wax-seal stamp lands
"Approved by ‹name›" verbatim in the hash-chained audit ticker. Letting the TTL
expire is a designed beat, not a bug: a late approve returns the real
"non-action (fail-closed)" with a "raise it again" control.

**Beat 3 — Earn the precedent (live graduation, real ladder)** (2:50–4:00).
Two more incidents of the SAME class arrive against genuinely DISTINCT seeded
target objects (§5.2 — mandatory new seeding). Each is a quick one-click
approve on the same card shape; a ladder card fills "verified 1× → 2× → 3×".
After the third clean verify the REAL `ladder.eligible()` flips true and
"Promote to Standing Approval" lights — wired to `ladder.promote()`, never the
old raw upsert (§5.1). THE VISITOR clicks Promote; the promotion audit event
names them. Confirmation copy: *"Standing Approval — the approval moved earlier
in time. It never left the loop."* Rehearsed fallback: if the live flip fails,
the beat degrades to showing the class's promotion HISTORY from the real
ladder audit vocabulary — no beat hard-depends on the flip.

**Beat 4 — The second time is free** (4:00–4:40). A fourth incident of the
now-Standing class arrives and resolves on the zero-LLM fast path in ~0.03 s,
before the visitor can move the mouse. Timing strip (the only comparative
numbers anywhere, all live-measured): *"Your approval on #1: ‹N›s (measured
just now) · Standing fix on #4: ‹M›s (measured just now) · Model calls this
session: 0."* Standing rows carry the honest label *"Standing Approval —
executes immediately; revoke standing to force review."* and NO Hold control
(§5.3). The line: *"The second time is free — because you paid for the first
one."* The audit rows cite THEIR promotion as the standing approval's
provenance.

**Beat 5 — It knows what it's not allowed to touch** (4:40–5:40). A
rights-restricted incident is REFUSED fail-closed — plain-English verdict
first: *"‹count› matching precedent(s) exist — owned by Rights Ops. Nothing
else is disclosed."* (count interpolated live). Then the kill-click, main rail:
the VISITOR throws one large Jira-shaped ACL toggle and the scheduler's fix
card goes dark in the same second — then the scripted sub-beat: re-fire the
Standing class → now REFUSED, because retrieval precedes the fast path (§5.5
converted from footgun to proof): *"One permission change. The fix — including
its earned Standing Approval — just went dark."* A pinned "ACL flip active"
banner persists until revert; auto-revert on beat advance with a 60 s failsafe
in self-guided mode. Skeptic side-dish one click deep: the 100-probe barrage
("100 probes · 0 leaked · P50/P99 in µs · live, this session").

**Beat 6 — Sabotage it: fail, roll back, demote** (5:40–6:40; the climax).
A "Sabotage the next verification" toggle arms the one-shot flake against the
visitor's OWN earned Standing class, with the REWRITTEN choreography (§5.4):
hold card renders FIRST → visitor approves → EXECUTE → VERIFY FAILS in red →
the pre-generated inverse restores pre-state byte-for-byte (the on-screen diff
collapses to zero, matching hashes shown) → the class auto-demotes STANDING→L1
with a visible audit event. Copy: *"VERIFY FAILED."* / *"Pre-state restored
byte-for-byte — diff: 0 bytes."* / *"STANDING → L1. Next run needs a human
again."* Then one more incident of that class arrives — and the approval card
is BACK, waiting: *"It lost the privilege you gave it. It's asking you again."*
The visitor injected the failure themselves — live-failure risk becomes the
feature.

**Beat 7 — Knows when NOT to act** (6:40–7:20). KB-0010 ESCALATE fires: the
runbook says no safe admin fix exists — the agent triages, snapshots
pre-state, REFUSES to build a plan, and pages a human, rendered as a
first-class outcome with the runbook's real provenance link. Copy: *"No safe
admin fix documented. Snapshot taken. No plan built. A human has been paged."*
/ *"The most trustworthy thing an agent can do is decline."* Companion (P1):
KB-0009 stale runbook (last_reviewed 2022, retired dropbox path) degrades to
L1 with the staleness reason printed. Skeptic affordance (P1): the
paste-your-own-ticket extractor sandbox.

**Beat 8 — Tamper with history** (7:20–8:00). The fake "Tamper (visual)"
button is deleted; in its place a REAL one: the visitor picks WHICH audit row
to corrupt — including their own approval row — a single UPDATE flips one byte
in their session-scoped chain copy, and the real `/api/audit/verify` recomputes
the sha256 chain live and fails AT THAT ROW, stored vs recomputed hash side by
side; transactional restore re-verifies clean. Copy: *"CHAIN VERIFICATION
FAILED at row ‹N› — stored ≠ recomputed."* One click deep, "For skeptics": the
tail-truncation honesty demo (bare chain passes after truncation; the anchor
check catches it) and (P1) the byte-identical seed-4207 replay control diffed
against a committed reference transcript hash.

**Beat 9 — Leave with the evidence: your name, two doors out** (8:00–8:45).
"Download your evidence pack" builds a tamper-evident bundle from THE
VISITOR'S OWN session: audit rows with `approved_by: ‹their name›` verbatim,
their promotion and demotion events, the ITIL change records, chain hashes, a
manifest, and the zero-dependency stdlib `verify_pack.py` with the exact
offline command rendered: *"python3 verify_pack.py precedent-evidence-‹name›.zip
— Run this on your laptop, offline. You don't have to trust us."* Above it,
the DIY pre-empt panel is generated FROM THEIR OWN SESSION ARTIFACTS: (1)
their rollback-anchor timestamp provably preceding their execute timestamp;
(2) their Promote event beside the auto-demotion event; (3) the pack + the
standalone verifier. Panel header: *"A Slack bot asks permission. It doesn't
pre-generate the inverse, demote itself on failure, or hand your auditor a
chain they can verify without trusting you. Yours just did all three — here
are your timestamps."* The honest tally renders ONLY `docs/numbers.md` values
with exact labels. Exactly two CTAs, nothing else clickable: (1) the
copy-paste local analyzer command — "Runs on your ticket export. Your data
never leaves your machine."; (2) "Book a design-partner slot." Epilogue: the
pending approval card from Beat 6 still glows — *"Incident open. It's waiting
for you."*

### 3.3 Signature moments (protect these when trading scope)

1. Sabotage your OWN earned Standing Approval → execute → red verify failure →
   byte-for-byte restore → self-demotion → it asks you again.
2. Your name wax-sealed verbatim into a hash-chained ledger that reappears in
   the evidence pack you verify offline.
3. "The second time is free" — ~0.03 s with a live model-call counter at 0,
   next to YOUR own measured approval time.
4. You personally fail to defeat the gate twice: trick phrases bounce; your
   forged plan hash gets YOUR approval rejected.
5. Real tamper, your choice of row — the verifier fails at exactly that record.
6. The security kill-click — even the Standing Approval you granted goes dark
   in one second, and returns on revert.
7. Earned promotion the ladder refuses to offer until 3 verified fixes on 3
   distinct targets.
8. KB-0010 ESCALATE — the agent that declines and pages a human.

### 3.4 Visual system

Full reskin to the brand: cream `#F1F1E2` surfaces, indigo `#3C3B62` accents,
ink `#2A2A48` text, NO green anywhere. Wax-seal + Ionic column mark and serif
PRECEDENT wordmark from `assets/brand/` (logo on light surfaces only; never
recolor/stretch the seal). Wax-seal stamp animation at every MEMORISE and on
the chapter scoreboard — the brand thesis "every incident resolved becomes
precedent" made mechanical. Server-rendered + SSE (sse-starlette is already a
dependency and currently unused — see §5.12); targeted DOM patches, never the
current 1.5 s innerHTML full rewrite. Responsive enough for the buyer's-phone
seat (the approval card and chat must work on a phone). Plain-English verdicts
primary; raw payloads one click deep, always available, never the main path.

## 4. Build scope

### P0 (the demo that ships — all must land)

**P0.1 — Session layer (ships FIRST; hosted-URL blocker).** Per-visitor
session: copy-on-write SQLite copies seeded from frozen template DBs (memory db
AND sim db), TTL eviction, hard concurrent-session cap with a polite queue,
per-session rate limits on ALL mutating endpoints, per-session Reset. Replace
the process-global `STATE` singleton, the module-global `_PENDING` dict and the
single sim `flake_state` row with session-scoped equivalents. The visitor
handle + session token flow as `sender` into `serve_chat_turn(sender=...,
conn=session_conn)`. Tamper/truncation/flip/flake operate ONLY on the visitor's
session copies. Env-tunable: `PRECEDENT_DEMO_MAX_SESSIONS` (default 24),
`PRECEDENT_DEMO_SESSION_TTL_S` (default 1800). Document new env vars in
`docs/ops/services.md`.
*Acceptance:* two concurrent Playwright sessions complete the full tour without
interference; one session's Reset/tamper/flip never touches the other; a test
asserts the template DB chain hash is unchanged after a session tamper cycle;
evicted sessions 410 politely.

**P0.2 — Chat panel + server-side gate cards.** New session-scoped
`POST /api/chat` wrapping the pure `serve_chat_turn()`; pending-hold state
moves out of the client JS variable into server session state so refresh,
second tabs, phones and scripted drives all render the card (fixes §5.9's
silently-broken one-minute demo). TTL-expired late approve surfaces the real
"non-action (fail-closed)" message with a "raise it again" control. Includes
the visitor-name safety package: length/charset sanitisation, offline-wordlist
profanity screen, the disclosure notice, default `visitor@<session-id>`;
presenter mode may pre-fill the buyer's name.
*Acceptance:* end-to-end test: chat report → gate card → trick phrases
re-present (enumerate the full vocabulary-guard corpus from the existing
tests) → explicit approve executes in sim → audit names the session handle;
gate card survives a page refresh and renders in a second tab of the same
session; expired approval is non-action.

**P0.3 — Cold open + world panel + SSE.** The Beat-0 break choreography (real
EPG grid, Love Island row corrupts at entry), the world panel rendering
break/repair/rollback as visible diffs of real rows, the audit ticker
streaming via SSE, the wax-seal MEMORISE animation and chapter scoreboard, the
full brand reskin (§3.4).
*Acceptance:* Playwright asserts the corruption is visible before any framing
copy; SSE replaces polling (no full innerHTML rewrites; expanded audit rows
survive updates); airplane-mode run of the container still boots and renders
(no external fonts/CDNs — everything vendored).

**P0.4 — Trick-the-gate + plan-hash forgery.** Suggestion chips that PREFILL
but never auto-send; "attempts survived" counter; the "edit the hash"
affordance submitting a mutated plan hash to the real approve path → rejected
by the existing tamper check.
*Acceptance:* a test drives every chip through `/api/chat` and asserts
zero executions; the forgery test asserts rejection + an audit event + the
original hold still approvable afterwards.

**P0.5 — Graduation seeding + ladder rewiring.** Seed 3+ same-class
duplicate-slot incidents against genuinely DISTINCT target objects (sim data
change, zero kernel change). Rewire ALL Promote/Revoke surfaces through
`ladder.eligible()/promote()/demote()` with the ladder's audit vocabulary;
DELETE the raw-upsert path in `console/demo_state.py` outright (§5.1 — the
repo is public; a curl-able bypass disproves the ladder story). Fix the two
lineage mismatches the new provenance cards would expose (§5.8).
*Acceptance:* new CI test: `eligible()` flips ONLY on the 3rd distinct
verified target and identical `(class_key, target_ref)` within the hour still
don't count; Playwright drives the full earn-then-promote arc; grep confirms
no `promoted_standing_approval` event vocabulary remains.

**P0.6 — Flake/rollback choreography rewrite + audit-order defect.** First,
TDD the orchestrator defect (ULTRACODE-PROMPT §5.1): `commit_execution`
currently emits an unconditional `executed` audit event after a step reports
`ok=false` and `execute_failed` fires — the rollback beat would display
executed-after-failed. Failing test first, fix, extend the chain-consistency
test. Then the sequencing rewrite (§5.4): sabotage toggle arms the session's
flake ONLY inside a path that will execute; order is hold card → visitor
approve → execute → one-shot verify failure → byte-for-byte restore (rendered
as an empty diff with matching hashes) → STANDING→L1 demotion event → next
same-class incident re-holds. `prepare()`/`commit_execution()` contract
untouched — endpoint sequencing only.
*Acceptance:* integration test asserts the full order; the audit log for a
flaked run contains `execute_failed`/`rolled_back`/`class_demoted` and NO
`executed`-after-failure; Playwright runs the beat end to end.

**P0.7 — Refusal + ACL kill-click beat.** Plain-English refusal card with the
live-interpolated count + owner team; raw denial JSON one click deep. The big
session-scoped permission toggle; pinned "ACL flip active" banner; auto-revert
on beat advance + 60 s failsafe; the scripted Standing-class-now-refused
sub-beat; per-session reset restores flip state.
*Acceptance:* existing no-leak tests extended to the new surfaces (grep every
new endpoint's responses for restricted content = 0 matches); Playwright:
flip → dark → Standing refused → revert → returns.

**P0.8 — Attestation + timing honesty.** Per-session model-call counter
instrumented at the `venice.py` call sites, surfaced on every action response
and pinned in the header. Populate `ExecutionResult.elapsed_ms` from a real
monotonic measurement; DELETE the hard-coded "~15s" audit detail string in
`orchestrator.py`; the timing strip renders only live session measurements
labelled "(measured just now)". Presenter mode adds the Wi-Fi-off outbound
probe badge; hosted mode never says airplane/offline.
*Acceptance:* fast-path response carries `model_calls: 0` (spy test); no
"~15s"/"~60s"/"26.5 hours" string anywhere in the tree (grep in CI);
timing strip values change between two runs (proving they're measured).

**P0.9 — Real tamper (delete the fake in the same commit).** Session-scoped
tamper endpoint: one UPDATE flips one visitor-chosen byte in one row of THEIR
chain copy; real `/api/audit/verify` fails at that row with stored vs
recomputed hashes rendered; transactional restore. The fake "Tamper (visual)"
button and its hardcoded "BROKEN (visual demo)" string are deleted in the SAME
change.
*Acceptance:* test: tamper → verify fails at exactly the chosen row → restore
→ verifies clean; template/seed chain unaffected; the "For skeptics"
truncation demo (bare pass, anchor-caught fail) works behind its toggle.

**P0.10 — KB provenance cards + Beat 7 ESCALATE.** Render runbook front-matter
provenance (adapted_from URL, last_reviewed, owner) at every RETRIEVE. New
drive path for KB-0010 ESCALATE (AUTH-CAP-900): triage → snapshot → refuse to
plan → "human paged" outcome card.
*Acceptance:* Playwright: ESCALATE beat renders the decline outcome with
provenance; policy lint (if landed from the other prompt) or a test asserts
the class builds NO plan; provenance URLs render for every retrieved KB.

**P0.11 — Close: DIY panel + honest tally + two CTAs + evidence pack v1.**
The DIY pre-empt panel rendered from the visitor's own session artifacts
(rollback-anchor timestamp vs execute timestamp; their Promote beside the
demotion; the pack + verifier). The tally and all static numbers through the
single numbers.md-sourced component. Exactly two CTAs; the booking CTA target
comes from `PRECEDENT_BOOKING_URL` (env; if unset, render the analyzer CTA
alone — never a dead link, never a committed personal calendar). Evidence pack
v1: per-session zip — audit rows, promotion/demotion events, ITIL change
records (reuse `scripts/render_change_record.py`), chain tail hash + anchor,
manifest, and a zero-dependency stdlib `verify_pack.py` that recomputes the
chain offline. **Honesty:** v1 is "tamper-evident" (hash chain + anchor), NOT
"signed" — do not render the word "signed" unless a real key mechanism ships
(see §6.1). If ULTRACODE-PROMPT P0.2's pack already landed, reuse it.
*Acceptance:* pack downloads with the visitor's handle in its audit rows;
`verify_pack.py` passes on it offline and FAILS loudly on a tampered byte
(test both); round-trip test proves pack content equals session audit content;
CTA surface has exactly two interactive elements; every static number on the
close screen carries its numbers.md label (snapshot test).

**P0.12 — Presenter kit.** `?presenter=1`: keyboard beat rail injecting
canonical ticket text, focal-card layout, speaker-note captions, state-sanity
strip, one-key seed-4207 full reset. The express path (pre-earned Standing
class) works in both modes.
*Acceptance:* a scripted Playwright run completes the 3-minute express cut via
keyboard only; reset restores ladder levels, flip state, flake state and
pending holds in <30 s.

**P0.13 — Deletions.** Remove: the 7-beat caption tour (`GUIDED_BEATS`) and
its false Beat-3 copy; the ever-ticking stopwatch; "Approve (record)" and the
six-button incident rows; all hackathon framing (sponsor track chips, static
Fetch pills, ASI:One screenshot + QR — 438 KB reclaimed); the green palette;
any Hold control on STANDING rows (§5.3); the raw-upsert promote path; the
fake tamper button; unlabelled numbers. `docs/demo/` gains the new tour
script; stale `Prep/*.pdf` references and the "6 beats" tooltip die with it.
*Acceptance:* greps for the deleted strings return nothing; kernel hash
re-frozen (P0.15); the Fetch.ai rails remain in `agents/` (they are product,
not demo chrome) — only the static console strip is removed.

**P0.14 — Docker/Render + Playwright CI.** The one-container image serves the
new demo; `render.yaml` updated; the full-tour Playwright suite (including the
2-session isolation run) executes against the built container as a CI-able
check.
*Acceptance:* `docker build && docker run` then Playwright green against the
container; container runs with no network egress (model-call counter stays 0
through the whole tour).

**P0.15 — Release gate: MANIFEST re-freeze + ship checks.** A named make
target re-freezes `MANIFEST.json` from the new checked-in demo copy;
freeze-check fails on a stale manifest. Extend the copy-lint: bans
"Autonomous" on the demo surface, bans unlabelled static numbers (grep against
a numbers.md-derived allowlist), bans "airplane"/"offline" in hosted-mode
templates, bans `‹…›` placeholders.
*Acceptance:* `make freeze-check` green end to end; header badge shows ✓ on
the frozen build; every §8 gate green.

### P1 (depth for skeptics + the second door, in order)

**P1.1 — Attack theatre + probe barrage + burst detection.** Extract the six
adversarial attack bodies from `tests/test_adversarial.py` into a shared
module (e.g. `precedent_memory/attacks.py`) imported by BOTH the tests and a
session-scoped `/api/attacks` endpoint — the demo executes the literal
CI-tested code and CI fails if they diverge. Six cards, plain-English verdict
first, raw attacker request/response one click deep. Probe-barrage widget over
the existing probes endpoint (n capped, session-scoped) — live numbers never
conflated with bench numbers. Wire `probing_detection.py` (5 denials/60 s →
flagged + throttled + audited) into the live demo ACL path.
*Acceptance:* attack cards and tests share one implementation (import graph
test); barrage leaks 0; a scripted 6-denial burst gets flagged and throttled.

**P1.2 — Extractor sandbox + KB-0009 stale chapter.** Paste-your-own-ticket
panel calling the real extractor: known code → deterministic class; garbled →
`llm_proposed` → capped L1, escalated, NO plan; unknown-first-code with a
known decoy later → degrades, decoy ignored. The 0/100 + 25/25 chip rendered
beside it with the SAFETY label and the 8/100-recovery caveat. KB-0009 stale
runbook chapter (degrade to L1, staleness reason printed).
*Acceptance:* sandbox is rate-limited and session-scoped; the three canonical
inputs produce the three documented outcomes in a test; no sandbox path can
reach execution.

**P1.3 — Persona lens (Door 1).** Post-Beat-2 toggle: "See this as your own
agent's queue" — a copy-pack reskin of the transcript for the platform-eng
ICP, with the mandatory honest tag "(simulated third-party agent — same
engine, same decisions)". Copy only; zero engine changes.
*Acceptance:* toggling mid-session preserves state; the honesty tag is
always visible in that skin; snapshot tests for both copy packs.

**P1.4 — Byte-identical replay control.** "For skeptics": rerun the canonical
seed-4207 drive in a fresh scratch session and diff the transcript hash
against a committed reference.
*Acceptance:* replay matches the committed hash in CI and in the container.

**P1.5 — Lean-back "Watch instead" auto-tour.** Auto-paced traversal of the
same beats (server-driven timers, visible cursor ghost), pausable, switchable
to the seat at any beat.
*Acceptance:* Playwright: full auto-tour completes unattended; taking the seat
mid-tour keeps session state.

### P2 (only if P0+P1 are green)

- **P2.1** UCI "day-one memory" beat: materialise the 558 standing-approval
  candidate classes from the committed analysis (labelled), as a closing
  visual for the analyzer CTA.
- **P2.2** Sim data browse panel ("systems simulated, content real"): the
  59 null-summary slots, the injected duplicate, the Netflix-vs-Disney+
  duplicate title — one click from the world panel.
- **P2.3** Second streaming scenario pack (SCH-OVL-204 overlap cascade) for
  Door-2 variety, seeded deterministically.

## 5. Pre-verified constraint & defect ledger (respect or fix; do not rediscover)

Each item below was verified against the code by the design run. TDD every fix.

1. **Ladder bypass:** `console/demo_state.py` `STATE.promote()` raw-upserts
   `level='STANDING'` with no eligibility check and emits
   `promoted_standing_approval`, while the real `ladder.promote()` emits
   `class_promoted`; `STATE.revoke()` skips `ladder.demote()` (counter never
   resets). Two rival audit vocabularies coexist. Fix per P0.5: rewire and
   DELETE the bypass.
2. **Graduation is impossible with current seeding:** each demo incident has
   ONE fixed `object_id`, `/api/drive` accepts only n∈{1,2,3}, and the ladder
   anti-gaming window counts an identical `(class_key, target_ref)` success
   once per 3600 s — `consecutive_verified` can never reach 3 live. Distinct-
   target recurrence seeding (P0.5) is a build item, not wiring.
3. **STANDING hold executes immediately:** in `scripts/demo_server.py`
   `api_drive` the fast branch returns `commit_execution()` BEFORE the
   `hold=true` check. Resolution: never render a Hold control on STANDING rows;
   show the honest label instead (§3.2 Beat 4).
4. **Flake choreography is wrong as coded:** `doForceFlake` runs a full
   auto-approved drive (flake consumed, rollback fires before any card
   exists), THEN opens a fresh un-flaked hold that will succeed — and that
   hold never renders because `window._gate` isn't set. The rollback beat
   needs the hold-first rewrite (P0.6), not a button on the old endpoint.
5. **Permission flip left ON refuses even Standing** (retrieval precedes the
   fast branch in `prepare()`): scripted as the Beat-5 sub-beat with pinned
   banner + auto-revert. Never an ambient toggle.
6. **Kernel hash covers checked-in demo copy:** any copy change flips the
   header badge to ✗ until `MANIFEST.json` is re-frozen (P0.15). Also fix the
   strip copy that overclaims what the hash covers (it hashes showcase prose,
   not rules or seed).
7. **Plain-English translator keys don't match reality:** `PLAIN_ENGLISH` uses
   DETECT/RETRIEVE/APPROVE/… but the orchestrator emits detected/
   retrieval_check/approval_decided/executed/verified/memory_stored — the
   translator falls back to raw text exactly when the loop runs. Fix the keys;
   all captions derive from the fixed translator.
8. **Lineage mismatches the provenance cards will expose:** the KB article
   carrying RGT-EXCL-009 is KB-0005, but `policy_pack.yaml` and the demo seed
   cite kb:KB-0004; SCH-DUP-002 has NO KB article — its precedent is
   jira:MEDIA-113 (narrate honestly: "precedent from a resolved Jira ticket,
   not a runbook" — a richer story, not a bug to hide); several non-demo
   classes carry filler `["kb:KB-0001"]` lineage_refs — replace for any class
   a demo beat drives.
9. **The scripted one-minute demo is silently broken:** curl-fired holds never
   render a card (client-side `window._gate`), so its Beat 2 instructs a click
   on the wrong "Approve" and INC-1 never resolves. Fixed structurally by
   P0.2 (server-side pending state); rewrite `docs/demo/` scripts against the
   new surface and delete `run_one_min_demo.sh`'s hardcoded absolute paths.
10. **No staleness beat:** the 60 s ACL freshness window never lapses under
    the demo server (20 s heartbeat) — do not design around it; the only
    dark-out is the explicit kill-click.
11. **Unlabelled numbers on the current surface:** "26.5 hours saved",
    "~60s", "~15s" (including the hard-coded audit detail string in
    `orchestrator.py` and the never-populated `ExecutionResult.elapsed_ms`).
    Fixed by P0.8; the copy-lint keeps them out.
12. **SSE claim vs polling reality:** sse-starlette is a declared dependency,
    imported nowhere; the page polls at 1.5 s with full innerHTML rewrites
    (observed blank-page failure during testing). P0.3 implements real SSE —
    resolving ULTRACODE-PROMPT §5.4's "decide once, apply everywhere".
13. **`agents/common.resolve_seed` dev-seed fallback** (ULTRACODE-PROMPT
    §5.2): if the demo build touches the rails path, land that fix too;
    otherwise leave for the main prompt — record which.

## 6. Decisions already made (do not relitigate; record deviations in the report)

1. **Evidence pack v1 is "tamper-evident", not "signed".** Hash chain + anchor
   verification only; `verify_pack.py` checks exactly that; the word "signed"
   does not render. A real signing mechanism (env-injected key, published
   pubkey) is a later, deliberate upgrade — the repo is public and a committed
   key is a hard-rule violation.
2. **Persona lens ships as P1.3** (slim copy-pack), not v1-blocking.
3. **The founder express cut** drops live graduation and the kill-click from
   the 3-minute stage cut (both stay one spoken sentence + hosted-URL
   pointer); the ~7-minute buyer-meeting cut keeps them with the buyer
   clicking Promote. Both cuts are presenter-mode presets, not separate builds.
4. **Name screening:** conservative charset + length limits + offline wordlist;
   false positives fall back to `visitor@<session-id>` with a polite note;
   presenter mode may pre-fill the buyer's name.
5. **Booking CTA:** `PRECEDENT_BOOKING_URL` env var; unset ⇒ the CTA does not
   render (analyzer CTA alone). No committed personal calendar link.
6. **Hosting:** the existing Docker/render.yaml kit, session cap default 24,
   TTL 30 min, both env-tunable. Render free-tier cold starts are a known
   limitation — note it in the report; a paid always-on tier is a founder
   decision, not a build item.
7. **The analyzer CTA renders the command + labelled UCI numbers even if the
   analyzer itself (ULTRACODE-PROMPT P0.3) hasn't landed** — the command is
   the decided funnel instrument. If the analyzer package name/entrypoint
   changes when it lands, the CTA copy is a one-line update.

## 7. Orchestration mandate — use ultracode deliberately

- **Understand phase (small):** this prompt + §5 already encode the repo map;
  spawn at most 2–3 readers for the precise seams you cut first
  (`console/demo_state.py` session boundary; `scripts/demo_server.py` drive/
  hold/flake paths; `agents/watcher.py` chat contract). Do NOT re-map the repo.
- **Design-verify before building the three visitor-facing surfaces** (the
  session/chat API shape, the beat-flow state machine, the evidence pack
  format): a small judge panel each (API consumer / security reviewer /
  first-time visitor), on a written design, BEFORE implementation. Adopt or
  explicitly reject each finding in the report.
- **Implement in parallel with worktree isolation:** P0.1→P0.2 are the
  spine (serialize those); P0.3/P0.4/P0.8/P0.9/P0.10 parallelize cleanly after
  P0.1 lands. Use `isolation: "worktree"` for agents touching overlapping
  files; merge through the §8 gates.
- **Adversarial verify every merged package:** refuters, not praisers —
  correctness lens + security lens (session isolation, name handling, tamper
  endpoint, rate limits are attack surface) + honesty-labels lens on every
  surface that renders copy or numbers.
- **Loop-until-dry bug hunt on the hosted surface before calling P0 done:**
  keep spawning finders until 2 consecutive rounds find nothing new. Must
  include: cross-session interference, XSS via visitor name/ticket text/chat,
  session-token guessing, rate-limit bypass, evidence-pack path traversal,
  tamper-endpoint escaping its session copy, the ACL flip failsafe, TTL races,
  SSE connection exhaustion.
- **Playwright is the arbiter:** every beat lands with a Playwright assertion;
  the full-tour suite (both modes + 2-session isolation) runs against the
  built container.
- **TDD discipline:** failing test first for every §5 fix and every new
  endpoint. The suite must END ≥256 passed, 0 skipped, and grow with the scope.
- **Completeness critic at the end:** sweep README + docs/demo + all rendered
  copy for claims without proofs, numbers without labels, and `‹…›`
  placeholders; what it finds is the final fix round.

## 8. Verification gates (run them; paste outputs in the final report)

```bash
make check-open-weight    # model names only in precedent/models.py
make test                 # ≥256 passed, 0 skipped (suite grows with the scope)
make lint                 # ruff clean
make secrets-scan         # gitleaks full history, clean
make freeze-check         # all of the above + placeholder grep + new copy-lint
make bench-extractor      # false-fast-path MUST stay 0
# demo-specific:
docker build -t precedent-demo . && docker run -p 8000:8000 precedent-demo
#   → full-tour Playwright suite against the container (both modes)
#   → 2-session isolation Playwright run
#   → model-call counter stays 0 through the entire hosted tour
# MANIFEST re-freeze target run after final copy; header badge ✓
# airplane-mode pass per docs/demo/airplane-mode.md (presenter mode)
```

Standing checks: gitleaks on staged changes before every commit; every static
number on any new surface traces to `docs/numbers.md` with its label; no
"Autonomous", no "airplane/offline" in hosted templates, no unlabelled timing.

## 9. Cut-lines (fire in order if capacity runs short; never cut upward)

1. P2 entirely.
2. P1.5 Watch-instead → P1.4 replay → P1.3 persona lens → P1.2 sandbox +
   KB-0009 → P1.1 attack theatre (keep the existing probes endpoint wired to
   a simple counter if cut).
3. Within P0: Beat 7 ESCALATE (P0.10's new drive path) may degrade to a
   provenance-cards-only release; the truncation skeptic panel may slip; the
   express-cut presets may ship before the buyer-meeting preset.
4. NEVER cut: P0.1 session layer, P0.2 chat + server-side gate cards, P0.5
   ladder rewiring + graduation seeding, P0.6 rollback choreography + the
   audit-order fix, P0.9 real tamper (with the fake deleted), P0.11 two CTAs +
   pack v1, P0.13 deletions, P0.15 release gate — or any invariant in §2.

## 10. Working agreements

- Conventional, small commits on `main` (auto-published — §2.4); each commit
  message states which gate it keeps green. Co-author trailer per repo
  convention.
- New code matches the existing idiom: typed pydantic contracts at boundaries,
  stdlib+sqlite, vanilla server-rendered UI + SSE — no SPA framework, no build
  step, no new heavyweight dependency without a recorded reason (the container
  must stay slim and offline-capable).
- Docs move with code: `docs/demo/` gets the new tour script (both cuts) and a
  presenter runbook; `docs/ops/services.md` gets every new env var; README's
  demo section is rewritten for the new tour (keep its honesty labels).
- The engine is not yours to redesign: `prepare()`/`commit_execution()`, the
  ladder semantics, the memory layer's fail-closed rules are fixed. Where a
  beat needs the engine to behave differently, the answer is choreography or a
  §5-listed fix — never a new decision path.
- If a finding contradicts this prompt (e.g. an acceptance test is impossible
  as written), record the deviation with reasoning in the final report — do
  not silently reinterpret.
- Deliver `docs/DEMO-BUILD-REPORT.md`: what shipped per item, gate outputs,
  deviations, the §5 ledger scoreboard, Playwright evidence, and the exact
  human actions still required (Render deploy click-path, `PRECEDENT_BOOKING_URL`,
  domain, the decision on a paid always-on tier).

## 11. Definition of done

All P0 acceptance criteria green; §8 gates green end to end; the container
passes the full-tour Playwright suite in both modes plus the 2-session
isolation run with the model-call counter at 0 throughout; every §5 item
either fixed (failing test first) or explicitly recorded as out of scope with
reasoning; the evidence pack verifies offline and fails loudly when tampered;
MANIFEST re-frozen with the header badge ✓; no unlabelled number, no
"Autonomous", no `‹…›` placeholder, no secret, anywhere in the tree;
`docs/DEMO-BUILD-REPORT.md` written.
