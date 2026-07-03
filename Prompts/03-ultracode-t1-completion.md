# Ultracode session prompt — Complete T1 (core loop · sim · Fetch rails)

> **Target model:** Claude **Opus 4.8**, `ultracode` (multi-agent Workflow orchestration). Paste the whole of the section below **"PROMPT — paste from here"** as the first message of a fresh Claude Code session opened in this repo's root. The leading `ultracode` keyword opts the session into Workflow orchestration; optionally append a token-budget directive (e.g. `ultracode +800k`).
>
> **Before you start (human checklist):**
> - Work happens on branch **`build/t1-core-loop-sim-agents`** (already exists). The session is told to stay on it and **not** merge to `main` itself — merges happen at the plan's phase boundaries.
> - `.env` is populated per `CREDENTIALS-CHECKLIST.md` (Venice / ASI:One / Agentverse / Jira keys) and **never committed**. The session runs **airplane-first**: it builds and tests everything offline, and makes exactly **one live Venice round-trip** (plus the live `/models` open-weight guard) to prove the client. It will **not** create Agentverse accounts, spend ASI:One quota, or register agents — those are human/T3 steps; it makes the agents *registerable* and documents the steps.
> - **Scope note (role change, ratified):** T1 is now **self-sufficient** — it fetches + commits the public seed data and **authors** the KB runbook corpus itself, so the demo never waits on the content lane. **N1 reviews** that data + KB for content integrity (provenance, ACL/stale flags, preserved messiness) — see `Plan/BUILD-PLAN.md` §4. The session should produce the data + KB and not block on anyone.
> - This prompt was written against verified repo ground truth (contracts, schema, the merged T2 API, the console seam, the Makefile) and a multi-agent read of every T1-relevant spec section. Treat `CLAUDE-AVAILABLE-APIS.md` and the spec files it names as ground truth; read precisely.

---

## PROMPT — paste from here

# MISSION: Complete T1 — Precedent's deterministic control plane (engine + sim + Fetch rails)

You are a fresh Claude **Opus 4.8** "Ultracode" session with multi-agent **Workflow** orchestration. Your job is to **implement T1 in full** in the repo at `/Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon`: the Venice open-weight inference client + model-registry usage, the MediaCo sim + seed data + KB corpus, and the deterministic core loop wrapped by the Fetch.ai (Agentverse / Chat Protocol) agent rails. **T2 (`precedent_memory/` + `console/`) is already merged and green — you plug into it, you never rebuild it.**

This is a hackathon entry whose eligibility depends on four hard rules that are trivial to violate by accident and **eligibility-fatal** to get wrong. **Read this entire prompt before writing a line of code.** Evidence before assertions — you run every verification yourself before claiming anything is done.

Work on branch **`build/t1-core-loop-sim-agents`**. Commit as you go; **do not merge to `main`** — that happens at the plan's phase boundaries.

---

## STEP 0 — Load context before designing (mandatory, in this order)

1. **Invoke the `precedent` project skill FIRST** (via the Skill tool). It encodes the four hard rules, the build-plan gate discipline, and the working conventions for this repo. Do this before touching any file under `precedent/`, `sim/`, `agents/`, `console/`, or `data/`.
2. Read the authoritative spec/context, in this order:
   - `.claude/skills/precedent/SKILL.md` (rules + conventions)
   - `Plan/BUILD-PLAN.md` (build order, gate discipline, cut order; §4 T1 is your mission, §4 N1 is who reviews your data/KB)
   - `EXPLAINER-idea-and-plan.md` and `EXPLAINER-roles.md` (the "why", the moat, the demo narrative, the T1/N1 split)
   - `Idea/refinement/02-architecture-refinement.md` §1.3 (Venice wiring) and §3.1–§3.4 (extractor/policy/ladder/orchestrator/recovery + Fetch rails) — the deepest technical source
   - `Idea/refinement/01-realistic-data-plan.md` §1–4, §6, §7 (data sources, KB articles, keep-the-messiness, fixtures)
   - `Idea/refinement/05-scale-story-and-qa.md` §E and `04-demo-and-video-script.md` (the on-stage ASI:One approval flow + demo beats)
   - `precedent/contracts.py` (all 13 pydantic v2 models — the frozen inter-agent/loop boundary)
   - `precedent/models.py` (the ONLY file allowed to name a model id; `model_id(role)`, `assert_open_weight(catalog)`)
   - `precedent/extractor.py` (`fingerprint()` is already implemented — key on it)
   - `precedent/venice.py` (`startup_guard()` implemented; `chat`/`embed` are stubs)
   - `precedent/policy.py`, `precedent/ladder.py`, `precedent/orchestrator.py` (all stubs raising `NotImplementedError`)
   - `precedent_memory/{db,store,retrieve,audit,sync}.py`, `precedent_memory/schema.sql` (the T2 API + tables you integrate with — read thoroughly; this is your integration surface)
   - `console/app.py` (note `POST /api/trace` at ~line 94 — T1's ONLY console ingress) and `console/demo_state.py` (note the canonical class-keys in `_seed()`, and that `push_trace` at ~line 309 stores trace in an **in-memory list on the STATE singleton**, not the DB)
   - `tests/test_t1_integration.py` and `tests/test_console.py` (the acceptance bar — currently green with T1 **simulated inline**; your real code must reproduce those exact calls/assertions)
   - `sim/app.py` (currently only `/health`), `agents/__init__.py` (docstring only), `data/kb/README.md` (front-matter schema), `data/raw/SOURCES.md`, `Makefile`, `CLAUDE-AVAILABLE-APIS.md`, `.env.example`
3. **Do NOT relitigate settled design.** The contracts, the schema, the model registry, and the T2 API are **FROZEN**. You implement *to* them — you do not redesign them, add columns, rename tokens, or "improve" the boundary. If something seems wrong, work within it and note it; do not change it.

---

## THE FOUR HARD RULES (non-negotiable invariants — each is eligibility-fatal)

These bind every line you write, including comments and tests.

**Rule 1 — Open-weight only.** A literal model id may appear in **`precedent/models.py` and nowhere else** — not in `venice.py`, not in `agents/`, not in a comment, not in a test, not in a docstring, not in this session's own scratch files that get committed. Resolve every model by role via `models.model_id(role)` where `role ∈ {FAST, SMART, HEAVY, EMBED}` — the **embedding model counts**. `make check-open-weight` greps for `claude-|openai-|gpt-|gemini-|grok-|mercury-`; a single hit anywhere but `models.py` breaks the gate. "It runs on Venice" is not a defence — Venice serves closed models too; `assert_open_weight` requires each pinned id's `modelSource` to be a `huggingface.co` URL (do NOT weaken it to a null-check — grok/gemini carry vendor-doc URLs). `PRECEDENT_DEV_MODELS` / `ALLOW_PROPRIETARY_DEV` stay UNSET in demo/CI.

**Rule 2 — No LLM in the decision.** The LLM may only **propose** (FAST triage fields, SMART rationale prose). It NEVER gates execution or sets a risk class.
- `extractor.extract()` computes the class **deterministically first**. Only if the deterministic path fails may it call `venice.chat('FAST', …)` to PROPOSE fields → `method='llm_proposed'`, which is **NOT class-confirmed**.
- `policy.assess()` derives `risk_class`, `policy_rule_id`, `ladder_level` from the **YAML policy pack only**. If `extraction_method != 'deterministic'` or `extracted is None`, it **caps `ladder_level` at L0/L1** with the reason in the trace. SMART may fill `rationale_text` ONLY — no `chat()` output may set `risk_class` or `ladder_level`.
- The STANDING fast-path fires **only** on deterministic-extractor-confirmed fingerprint equality, and makes **zero** `chat()`/`embed()` calls. Gate this with a test asserting `venice.chat` is never invoked on the STANDING branch.
- `precedent_memory/retrieve.py` has **zero LLM imports** — structured equality only, no similarity, no embed. Do not add any.

**Rule 3 — Fail-closed.** Trust `retrieve()`'s denials: surface only `denied_count` + `denied_owner_team` (the incident-3 routing signal) — never title, symptom, body, or secret. `sync()` returns `available=False` on outage **without raising** → treat as "restricted memory dark, public still serves." A stale cache may **narrow** access, never widen it. Empty lineage → UNVERIFIED source → denied to everyone. No bypass path that serves a restricted KB body without the Jira-backed check.

**Rule 4 — No secrets.** `.env` is gitignored; `.env.example` holds placeholder names only. Agent seeds, mailbox keys, tokens, real teammate names, and Jira accountIds never appear in code, a commit, or any prompt you send to a sub-agent model. The repo goes public — one leak fails the scrub gate. Read config from env at runtime; never inline a value.

If any task appears to require breaking one of these, **STOP and find the compliant path** — there always is one.

---

## RESOLVED DECISIONS (proceed autonomously on these)

- **Data & KB ownership (absorbed from N1):** You **fetch + commit** the public seed data and **author** the ~10-article KB corpus yourself. T1 is self-sufficient so the sim + retrieval demo run offline without waiting on the content lane. A human (N1) will **review** your output for content integrity — real `adapted_from` links, correct ACL/stale flags, preserved messiness — so make those correct, but do not block on them.
- **Live-API posture — airplane-first + one live proof:** Build and test **everything offline** (mocks / committed fixtures / precomputed embeddings / the local Ollama profile). Make exactly **one live Venice chat round-trip** to prove the client works, and run the live `/models` open-weight guard (`assert_open_weight` against the real catalog) — both using the keys already in `.env`. **Do not** create Agentverse accounts, register agents, spend ASI:One quota, or run the ≥10-interaction discoverability chats — those are human/T3 steps. You must make agents that are **registerable** (stable seeds from env, `publish_manifest=True`, both README badges) and document the exact registration steps + which env vars to fill.
- **Canonical G0 seed:** Use the fixed integer seed **`4207`**. Incidents 1/2/3 and the mutation corpus all derive from it and must replay **byte-identically**. Declare `4207` once as a constant and reference it everywhere (fixtures, generator, README). The team may override at G0 by changing that one constant.
- **Standing-approval demo path:** **Pre-seed** incident 2's graduated class at `STANDING` in `class_ladder` so the fast-path fires reliably on stage, **and** also implement the live-graduation path (3 clean verifies at L2 → human `promote()`) so the video can show it earned.
- **Jira principals:** Assume two distinguishable principals (requester ≠ approver) via `JIRA_RIGHTS_OPS_ACCOUNT_ID` / `JIRA_SCHEDULING_OPS_ACCOUNT_ID` read from env. If those are empty, fall back to single-account role-flip between security levels `10007`/`10008`, noting the few-second permission-cache propagation window in a comment. Never inline an accountId.
- **Trace process:** Run T1's orchestrator **in the same process as the console STATE singleton** (or a thin shared-process launcher) so `POST /api/trace` lights the live trace panel; the durable audit tail / feed / baseline panels work cross-process regardless because they read the shared DB.
- **YAML policy pack + known-code dictionary:** Draft a **minimal starter pack** covering the demo classes (see the canonical class-key registry below) with sensible risk classes + `policy_rule_id`s; mark all other codes **degrade-to-L1**. A human reviews/extends it at G0.

---

## INTEGRATION CONTRACT WITH THE MERGED T2 (implement to this exactly)

The acceptance bar is **turning `tests/test_t1_integration.py` and `tests/test_console.py` green with the REAL orchestrator** (not the inline simulation they currently pass with). Do not weaken, mock, or skip those tests.

### Canonical class-key registry (the frozen anchor — extractor, sim, KB, and fixtures must all agree)

`console/demo_state.py::_seed()` and `data/kb/README.md` **lock** these. Do **not** invent new services/codes for the demo classes:

| Incident | service | error_code | target_object_type | `class_key` | console fingerprint token | KB |
|---|---|---|---|---|---|---|
| **INC-1** EPG publish failed | `publisher` | `PUB-4012` | `schedule_item` | `publisher\|PUB-4012\|schedule_item` | `fp-epg` | KB-0001 (public) |
| **INC-2** duplicate schedule slot | `scheduler` | `SCH-DUP-002` | `schedule_item` | `scheduler\|SCH-DUP-002\|schedule_item` | `fp-sched` | (fast-path repeat class) |
| **INC-3** VOD outside licence window | `rights` | `RGT-EXCL-009` | `vod_item` | `rights\|RGT-EXCL-009\|vod_item` | `fp-rights` | KB-0004/0005 (rights-ops-only) |

`fingerprint()` = `sha256(class_key.upper())`. For a T1 execution to light up the **matching** console incident card over the shared DB, agree the fingerprint/class_key convention with the console seed — reuse the console's `class_key`s and fingerprint tokens as the canonical anchor rather than inventing new ones. If the friendly token vs `sha256` convention needs reconciling so a real run appears on the right card, coordinate the minimal adjustment with T2's console rather than forking the identifiers.

### The T2 API you call

**Shared SQLite (file, not `:memory:`).** T1 opens its OWN connection via `db.connect(shared_path)` — WAL on a file path makes T1-writer / console-reader concurrency safe. Point the console at the same file via `PRECEDENT_MEMORY_DB` or `DemoState(db_path=…)`. Thread that one `conn` through `retrieve`/`store`/`audit` in a single transaction wherever TOCTOU matters.

**Write memory** (contract-shaped adapter):
```
store.store_memory_write(
    MemoryWrite(record=…, lineage_source_refs=[…], class_key=…),
    principal_ctx={'principal': …},
    conn=t1,
)
```
Empty lineage → UNVERIFIED → denied to everyone. A genuinely public record needs a real lineage ref whose constraint set is empty. **T1's refs MUST match seeded `acl_source` refs** (e.g. `jira:MEDIA-113`, `kb:KB-0001`) or the record goes dark.

**Read memory:**
```
retrieve.retrieve(principal, {'fingerprint':…, 'class_key':…, 'incident_id':…}, mode, conn=t1, actor=…)
```
`conn` is REQUIRED. Structured equality only. It audits allow/deny internally and commits. Denials disclose only `denied_count` + `denied_owner_team`. Never bypass it to fetch content another way.

**Audit** — on every hop:
```
audit.audit(event_type, conn=t1, actor=…, **safe_payload)
```
Event types to emit across the loop: `detected, triage, retrieval_check, risk_assessed, approval_requested, approval_decided, executed, verified, rolled_back, class_promoted, class_demoted, memory_stored`. Payloads are **safe metadata only** — never fix content, secrets, or restricted body. `audit()` does **not** self-commit → call `conn.commit()` after each batch or the console never sees the rows.

**Ladder table:** `ladder.py` reads/writes the existing `class_ladder` (PK `class_key`; `level ∈ {L0,L1,L2,STANDING}`; `consecutive_verified`; `promoted_by`; `promoted_at`). Write the **canonical token `STANDING`** — never the display text "Standing Approval" (that's UI-label only).

**Console surfaces** (these light up from your DB writes + trace posts, replacing the console's current mocks):
- **Trace panel** — `POST /api/trace {step, detail='', incident_id?}` is T1's ONLY console ingress (`console/app.py:~94`). `push_trace` stores events in an **in-memory list on the STATE singleton** (`demo_state.py:~309`), so the LIVE trace panel only lights up if T1 posts to the **same console process** (hence the same-process decision above).
- **Baseline Bar, feed, audit tail, degraded banner, provenance footer** — all light up purely from durable DB writes on the console's ~1500 ms poll. Emit the right audit/memory rows and they populate with no extra API.
- **Buttons** — Approve / Promote / Revoke must be clickable and drive real state (approval decision, human `promote()`, demotion/revoke).

---

## DEPENDENCY-ORDERED WORK PLAN (build order is strict; each step names its verification)

Build toward the **G1 vertical slice** first: incidents **1 (LLM-assisted classify+propose, slow-path) + 2 (fast-path repeat, zero-LLM) + recovery R (auto-rollback + demotion)** running end-to-end on seeded real data with the console's Baseline Bar + Approve/Promote/Revoke clickable. Everything past the slice is strictly additive.

### Phase A — Venice client + hello-world Watcher (T1-1, T1-2, T1-3)
- **T1-1** `venice.chat(role, messages, **kw)`: OpenAI-compatible `POST {BASE_URL}/chat/completions` with `model=models.model_id(role)`, **5–6 s timeout**, **canned-fallback string on timeout**, returns `str` or parsed tool-call dict. `role ∈ {FAST,SMART,HEAVY}`. Wire the `PRECEDENT_MODEL_BACKEND=local` Ollama airplane profile. Add a response cache keyed by prompt hash so airplane-mode reruns are instant. **No literal id.**
  *Verify:* `make check-open-weight` returns only `models.py`; a unit test hits a mock endpoint and asserts the fallback string on timeout; **one live Venice round-trip** succeeds against the real API; grep confirms no literal id in `venice.py`.
- **T1-2** Startup `/models` guard: `GET /models`, pass `{id: modelSource}` to `venice.startup_guard`. Stand up an echo-level **Chat-Protocol Watcher** (`uagents Agent(name, seed, mailbox=True)`; `chat_proto=Protocol(spec=chat_protocol_spec)`; `watcher.include(chat_proto, publish_manifest=True)`) with a **STABLE seed from env** so the address survives the later handler swap. Both README badges verbatim; keyword-rich description. **You build it registerable; a human registers it.**
  *Verify:* `assert_open_weight` passes on the live catalog and **raises** on a closed id injected into the map; the Watcher runs locally and speaks Chat Protocol; you output the registration runbook (seeds/env to fill).
- **T1-3** `venice.embed(texts) -> list[list[float]]`: `POST {BASE_URL}/embeddings` with `model=models.model_id('EMBED')`. **Build-time only** — precompute and **commit** vectors; zero embedding calls at demo. No literal id. Provide a BM25 fallback path.
  *Verify:* `make check-open-weight` clean; embeddings committed under `data/`; BM25 fallback exercised; a demo-mode run makes **zero** `/embeddings` calls.

### Phase B — Data + sim + fixtures (T1-4, T1-5, T1-6)
- **T1-4** Commit `data/raw/` **FIRST** (nothing is on disk yet and it blocks the loaders): UCI incident CSV, TVmaze GB 7-day JSON (primary, auth-free), Freeview XMLTV (backup, auth-free), 2 CC0 Kaggle catalogs (Netflix + Disney+ — optional; if Kaggle creds absent, document the manual-download fallback and proceed). Author **~10 KB runbooks** as `.md` with the **11-field YAML front-matter** validated against `data/kb/README.md` (`id, title, adapted_from URL, service, error_code, target_object_type, acl, stale, last_reviewed`, …) + body (symptoms / preconditions / steps / verification / rollback / owner). **Critical five first:** #1 EPG-publish (`publisher|PUB-4012`), #4/#5 restricted rights (`rights|RGT-EXCL-009`, `acl: rights-ops-only`), #6 CrowdStrike CF-291, one stale. Include 2 ACL-restricted, 2 stale, 1 escalate-class. Real `adapted_from` URLs only (never invented); keep licence labels; **do not reintroduce TMDB/IMDb** (licence-rejected). N1 will review this for integrity.
  *Verify:* `data/raw` + `data/kb` populated and committed; front-matter validates; `adapted_from` URLs resolve; licence labels present; error codes match the canonical registry.
- **T1-5** `sim/app.py` → one FastAPI app, **4 routers** (scheduler / rights / publisher / kb) over **one SQLite file**. Loaders: scheduler+publisher from TVmaze (channel / programme / schedule_slot / epg_payload / vod_item, 6–10 real channels); rights from Kaggle (`licensed_regions`=real country list, `window_start`=real `date_added`, `window_end`=start+term [film 24 mo / series 36 mo], exclusivity on a deterministic subset), cross-link 50–100 rights records to programmes by **fuzzy title match**. **KEEP the messiness** — nulls, duplicate titles, fuzzy-match failures (a hard rule; it triggers the incidents and the Conduct rubric rewards it). Expose read endpoints + a **pre-state snapshot API** on target objects + publisher execution/verification endpoints the Operator calls. **NO LLM, no model id, no permission/risk logic in the sim.** Restricted-runbook ACL lives in Jira issue-security (seed MEDIA-113/114 with the level IDs from `.env`), NOT in the sim DB.
  *Verify:* GET endpoints return seeded rows incl. nulls/dups; incident payloads round-trip through `contracts.IncidentEvent`/`Extracted`; `make check-open-weight` clean over `sim/`; snapshot endpoint returns full target-object JSON.
- **T1-6** Fixed-seed incident generator: takes `--seed`; incidents 1/2/3 produce **byte-identical** payloads under seed **`4207`**; the mutation layer (typos, colloquial symptoms, dropped codes, red-herrings) is driven by the **same** seed. `POST /sim/publisher/flake?once=true` arms **exactly one** verification failure (once-semantics). Wire Makefile `sim` (`uvicorn sim.app:app` + console, **same process** for live trace) and `demo-reset` (reset sim SQLite from fixture snapshot, zero memory counters, reset ladder) to run in **<30 s**. The canonical fingerprint `publisher|PUB-4012|schedule_item` must be producible.
  *Verify:* two runs at seed `4207` diff to **zero bytes**; `flake?once=true` fails exactly one verification then succeeds; `make demo-reset` completes <30 s and restores state; `make sim` boots app+console.

### Phase C — Core loop (T1-7 … T1-10) — the vertical-slice engine
- **T1-7** `extractor.extract(raw_text, structured=None) -> (Extracted|None, Literal['deterministic','llm_proposed'])`: try regex + canonicalisation tables + known-error-code dictionary over `structured` FIRST → `method='deterministic'`. Only on failure call `venice.chat('FAST', …)` to PROPOSE → `method='llm_proposed'` (NOT class-confirmed). Return `(None, method)` when even a proposal can't yield all three fields. **Never** semantic similarity. Key on the already-implemented `fingerprint()`.
  *Verify:* clean structured payload → `deterministic` with correct `Extracted`; typo'd/unknown code → `llm_proposed` or `None`; a unit test asserts a known code resolves to the canonical `class_key`; `make check-open-weight` clean.
- **T1-8** `policy.assess(triage) -> RiskAssessment`: load a YAML policy pack keyed on `(system × action_type × risk_class × autonomy_level)`; return `risk_class` + `policy_rule_id` + `ladder_level`. If `triage.extraction_method != 'deterministic'` **or** `triage.extracted is None`, **FORCE `ladder_level` to L0/L1** (cap) with the reason in the trace. SMART fills `rationale_text` ONLY. Cost is corpus-size-independent (per-tenant YAML tree).
  *Verify:* deterministic triage of a known class → expected `risk_class`/`ladder_level`/`policy_rule_id`; `llm_proposed` triage → capped at L0/L1 regardless of the class's ladder level; a test asserts `chat()` output **cannot** change `risk_class`.
- **T1-9** Ladder: `is_standing(class_key)` (`SELECT level FROM class_ladder`; True iff `'STANDING'`). `on_verification_result(class_key, verified, rolled_back)`: on success `consecutive_verified += 1` subject to **anti-gaming** (distinct target object, once-per-hour, monitored sources only); on failure/rollback set `level='L1'`, `consecutive_verified=0` + a `class_demoted` audit event. Add `promote(class_key, principal)` / `eligible(class_key)` for the **human click** (3 consecutive verified at L2, zero rollbacks) writing canonical `'STANDING'` + `promoted_by`/`promoted_at`. Read/write existing columns only; never redesign; never write display text. **Demotion is immediate and resets the counter to 0** (not decrement); promotion is a human click (never automatic).
  *Verify:* 3 clean verifies → `eligible()==True`; `promote` writes `level='STANDING'` + `promoted_by`; any failure demotes to L1 and resets counter to 0; identical-object repeats within an hour count once; `class_ladder` holds `'STANDING'` not `'Standing Approval'`.
- **T1-10** `orchestrator.handle(incident)` owns the `conn` (`db.connect(shared_path)`) and threads it through retrieve/store/audit in one transaction where TOCTOU matters. Enforce the **`plan_hash` tamper check** (same hash flows `IncidentEvent→ExecutionPlan→ApprovalRequest→ApprovalDecision→ExecutionResult`; verify approved `plan_hash` == executed plan before execution) and **rollback ordering** (capture `pre_state_snapshot_ref` = full target-object JSON **BEFORE** any typed call; verify AFTER; on fail run `rollback_steps` to restore, **THEN** demote; a FAILED rollback escalates with the snapshot attached to the Jira ticket — never swallowed).
  - **FAST-PATH** (when `ladder.is_standing(fingerprint)` from a **deterministic** extract): retrieve graduated record → policy-gate → snapshot pre-state → execute typed calls → verify → `on_verification_result` → `store_memory_write` → audit, with **ZERO `chat()`/`embed()` calls**. Stream every hop to `/api/trace` so the audience sees zero-LLM.
  - **SLOW-PATH:** extract → (FAST propose if messy) → retrieve → assess → build `ExecutionPlan(plan_hash, pre_state_snapshot_ref)` → `ApprovalRequest` → await `ApprovalDecision` (verify `decision.plan_hash`) → execute → verify (auto-rollback restores snapshot on fail, THEN demote) → `on_verification_result` → memorise.
  - Surface only `denied_count` + `denied_owner_team`. Stream every hop to `POST /api/trace`; `conn.commit()` after audit batches.
  *Verify:* `tests/test_t1_integration.py::test_t1_plugs_into_t2_over_shared_db` passes with the **REAL** orchestrator (not simulated); incidents 1 (slow) and 2 (fast-path) resolve end-to-end; a test asserts `venice.chat` is **NEVER** called on the STANDING branch; recovery R: flake fails verification → rollback restores snapshot → `class_demoted` → re-approve → success; SECRET/restricted text absent from every console surface.

**★ G1 VERTICAL SLICE GATE — the immovable floor.** After T1-10, incidents 1 + 2 + recovery R must run end-to-end on seeded real data with the console buttons clickable. **Get this green before any Fetch polish or stretch work.** Never cut incidents 1+2, the Fetch hard gates, the capture session, or the slice.

### Phase D — Fetch rails (T1-11, T1-12) — additive, but the hard gates are pass/fail
The Fetch integration is a hard gate that scores **ZERO if partial**: Agentverse registration + Chat Protocol with `publish_manifest=True` + ASI:One discoverable + no-frontend-required + public repo. Do not leave it half-wired. (You implement + document; a human runs the live registration.)
- **T1-11** Wrap the in-process loop with **three Agentverse MAILBOX agents** (`mailbox=True`, stable seeds from env). `PrecedentProtocol` carries `contracts` models as uAgents `Model` messages: **Watcher** `IncidentEvent→TriageResult`; **Librarian** `TriageResult→RetrievalBundle` (calls `precedent_memory.retrieve`, **NO LLM import**, surfaces `denied_count`+`owner_team` only); **Operator** `ExecutionPlan(+ApprovalDecision)→ExecutionResult` (typed calls + Jira write-behind, never blocks the on-stage flow). **Assessor + Auditor stay IN-PROCESS by design.** Both README badges verbatim on each agent.
  *Verify:* a `PrecedentProtocol` message flows Watcher→Librarian→Operator locally; Librarian imports no model id and withholds content on denial; `make check-open-weight` clean over `agents/`; the registration runbook lists seeds/addresses/env to fill.
- **T1-12** Watcher speaks Chat Protocol (`publish_manifest=True`). An `ApprovalRequest` renders as **ONE** formatted `ChatMessage` (triage+fix+risk+rollback+Jira link) with `expires_at = requested_at + 600 s`. A reply matching approve/reject becomes an `ApprovalDecision` with `approver_principal = ctx.sender` address (verbatim). New **`approval`** table (`incident_id, plan_hash, sender_address, requested_at, expires_at, status`) for TTL expiry + **re-present-on-reconnect** (never resume silently; failure direction is always **non-action**). Append a **hop-trail footer** (Watcher→Librarian→Operator addresses + ms timings) to every outbound reply. The repeat-class turn runs under **Standing Approval** with the **~15 s timer QUOTED** in the reply and **no approval prompt**. Implement a **hosted degraded-L0 Watcher** that, without MediaCo creds, still triages/retrieves against the public runbook corpus and returns a risk-classified plan with an explicit "no execution target configured" L0 state (a human deploys it Friday night).
  *Verify (scriptable, human-run live):* report incident → one formatted message → 'approve' → executes + closes a Jira ticket + replies with audit hash + Jira link → repeat class runs standing-approval in-chat with no prompt and timer shown; dropped mid-approval session expires to non-action and re-presents on reconnect; hosted Watcher answers a described incident at L0 without creds; both badges present. You provide the script + a local dry-run.

### Phase E — Makefile finalisation (folded into T1-6; re-verify last)
`make sim` boots app+console (same process for live trace); `make demo-reset` restores in **<30 s** (reset sim SQLite from fixture snapshot, zero memory counters, reset ladder). A botched on-stage run must be recoverable in <30 s.

---

## MULTI-AGENT EXECUTION STRATEGY (use the Workflow tool)

Leverage orchestration — do not build this serially by hand where parallelism is safe.

- **Respect the dependency DAG.** Phase A → B → C → D. Within a phase, fan out independent modules to parallel implementer sub-agents in **git worktrees** (`superpowers:using-git-worktrees`) so they don't collide. Safe-to-parallelise clusters: {T1-1, T1-4} early; the KB runbooks author in parallel with the sim skeleton; {T1-7, T1-8, T1-9} once venice + sim exist (they share only the frozen schema + contracts).
- **TDD per module** (`superpowers:test-driven-development`): write the failing unit test that encodes the verification criterion above, then implement to green. For T1-10 the "test" is the real `test_t1_integration.py` turning green with the real orchestrator.
- **Serialise the merge points:** the orchestrator (T1-10) and the shared-SQLite/console wiring are integration chokepoints — one integrator sub-agent owns them; implementers hand it green modules.
- **Adversarial verification pass** (a dedicated red-team sub-agent — `superpowers:requesting-code-review` + `superpowers:verification-before-completion`) that independently checks:
  1. `make check-open-weight` returns **only** `precedent/models.py` — grep the whole tree for `claude-|openai-|gpt-|gemini-|grok-|mercury-` including comments/tests.
  2. The **fast-path trace shows zero LLM calls** (spy/patch `venice.chat`/`venice.embed`, fail if invoked on the STANDING branch).
  3. **Failed extraction caps at L0/L1** (`llm_proposed`/`None` never unlocks STANDING or the fast-path).
  4. `retrieve.py` denials surface only `denied_count` + `denied_owner_team`; **no restricted title/symptom/body/secret** leaks to any console surface, trace, audit payload, or agent reply.
  5. **Airplane-mode (Wi-Fi OFF) passes**: `make demo-reset` + the full G1 slice run entirely from the committed snapshot with zero network calls (embeddings precomputed, venice on the local Ollama profile with canned fallback, Jira via cache).
  6. `make demo-reset` completes in **<30 s**.
- **Never claim done without running the command.** Paste the actual command output as evidence. If a sub-agent reports green, the integrator re-runs it.

---

## ACCEPTANCE CHECKLIST (run these yourself; paste evidence)

- [ ] `make check-open-weight` → clean (only `precedent/models.py` names ids)
- [ ] `make test` → green, including `tests/test_t1_integration.py::test_t1_plugs_into_t2_over_shared_db` and `tests/test_console.py` passing with the **REAL** orchestrator (not the inline simulation)
- [ ] `make lint` (ruff) → clean
- [ ] `make secrets-scan` (gitleaks) → clean; `.env` gitignored; `.env.example` placeholders only; no seeds/keys/accountIds/teammate names in code or commits
- [ ] `make freeze-check` → passes (open-weight + test + secrets + no `‹` placeholders)
- [ ] Incident **1** (slow-path, LLM-assisted classify+propose) runs end-to-end on seeded real data
- [ ] Incident **2** (fast-path repeat) runs end-to-end with a test proving **zero** `venice.chat`/`venice.embed` on the STANDING branch, timer quoted
- [ ] Recovery **R**: `flake?once=true` → verification fails → rollback restores the pre-state snapshot → `class_demoted` → re-approve → success
- [ ] Console: Baseline Bar + feed + trace + audit tail populate from T1's DB writes / trace posts; **Approve / Promote / Revoke** clickable and driving real state
- [ ] Two generator runs at seed **`4207`** diff to **zero bytes**; canonical fingerprint `publisher|PUB-4012|schedule_item` producible
- [ ] `make sim` boots app + console (same process → live trace lights); `make demo-reset` restores in **<30 s**
- [ ] One **live Venice** round-trip succeeded and the **live `/models` guard** passed (both using `.env` keys)
- [ ] Fetch: three MAILBOX agents **registerable** (stable seeds, `publish_manifest=True`, both README badges), `PrecedentProtocol` flows Watcher→Librarian→Operator, Librarian imports no model id and withholds content on denial, hop-trail footer + one-message approval + hosted degraded-L0 Watcher implemented, **registration runbook written** for the human step
- [ ] Airplane-mode: full G1 slice runs Wi-Fi OFF from the committed snapshot with zero network calls
- [ ] `data/raw` + `data/kb` committed; front-matter validates; licence labels present; messiness (nulls, dup titles, fuzzy-match failures) preserved; error codes match the canonical registry

---

## OTHER LOAD-BEARING CONSTRAINTS (do not violate)

- **Terminology:** the ladder top level is **"Standing Approval"** in every code label and UI string — **never "Autonomous"**. The canonical DB token stays `STANDING`.
- **Number honesty** (in any copy you touch, traced to `Research/00-verified-claims.md`): `18.2h` is always "calendar hours" (never blended with the MetricNet 8.85 business-hour figure); `59.4%`/`87.7%` arrival-time is a naive-frequency FLOOR (not product accuracy); `94.4%` measures precedent EXISTENCE; the inverted `knowledge=true` stat is labelled colour, never causal.
- **Airplane-mode is the demo default:** live TVmaze/ASI:One/Jira calls only in the Friday-night video take; the stage demo runs from the committed snapshot with Wi-Fi off. Embeddings precomputed/committed; every hot-path Venice call has a 5–6 s timeout + canned fallback; Jira via poll + write-behind (no webhooks/ngrok).
- **Keep the messiness** — a hard rule. Do not "clean" the seed data.
- **Cut order when the clock bites** (per `Plan/BUILD-PLAN.md` §5.1): stretch visuals → incident 3 video-only → Jira cached fallback → collapse the third agent in-process (then sweep "three agents" from all copy — never say three if two are registered). Never cut incidents 1+2, the Fetch hard gates, the capture session, or the slice.

---

## DEFINITION OF DONE

T1 is done when: the **G1 vertical slice** (incidents 1 + 2 + recovery R) runs end-to-end on seeded real data with the console's Baseline Bar + Approve/Promote/Revoke clickable; `tests/test_t1_integration.py` and `tests/test_console.py` are green against the **real** orchestrator; `make check-open-weight`, `make test`, `make lint`, `make secrets-scan`, and `make freeze-check` are all clean; the fast-path is provably zero-LLM and failed extraction provably caps at L0/L1; the full slice runs in **airplane mode**; `make sim` and `make demo-reset` (<30 s) work; one live Venice round-trip + the live open-weight guard have passed; the three Agentverse mailbox agents (stable seeds, `publish_manifest=True`, both README badges) with `PrecedentProtocol`, one-message ASI:One approval, hop-trail footer, and hosted degraded-L0 Watcher are implemented **and** the human registration runbook is written; and `data/raw` + `data/kb` are committed with correct provenance/flags/messiness for N1's review — with every claim backed by pasted command output.

Do not relitigate the frozen contracts, schema, model registry, or T2 API. Implement to them. Stay on `build/t1-core-loop-sim-agents`; do not merge to `main`. Run the verification before you claim done. **Begin by loading the `precedent` skill.**
