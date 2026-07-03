# 02 — Architecture Refinement: Models, Permission Semantics, Topology, Reliability

> Refinement-panel deliverable, Fri 3 Jul 2026 (early morning). Lane: architecture, open-weight compliance & BasedAI semantics.
> Fixes the fatal/major findings from the BasedAI, technical, and Fetch judges without relitigating locked decisions.
> Companion docs: 01 (data/Conduct lane), 03 (pitch/demo lane) — where a beat is owned by another lane it is cross-referenced, not respecified.

---

## 0. TL;DR — the decisions this document makes

| # | Decision | Replaces |
|---|---|---|
| 1 | **Open-weight-only runtime, enforced in one config module.** Default stack: `qwen3-5-35b-a3b` (FAST), `deepseek-v4-flash` (SMART default) / `deepseek-v4-pro` (SMART-heavy, dossiers only), `text-embedding-bge-m3` (EMBED, precomputed at build time). All via Venice API ($50 `IMPERIAL50X` credits). OpenAI/Anthropic keys **never touch the pipeline** — dev-flag only, off by default. | "Venice credits plus any OpenAI/Anthropic keys" (BasedAI-fatal) |
| 2 | **A/B/C permission semantics** exactly as endorsed by BasedAI's Thomas (c0b4lt_27) in the track Discord: A = conjunction over ALL source lineage constraints; B = precompiled effective-policy cache (one indexed lookup, this is the P99 answer); C = governed redacted derivatives (designed + stubbed). Fail-**closed** on stale ACLs in Jira-fallback mode. | Single strictest-label inheritance (loses information in the non-hierarchical multi-source case — Precedent's own incident-3 example) |
| 3 | **Memory governance is a standalone package** (`precedent_memory/`) with its own README, tests, seeded 8k-record benchmark, and hash-chained audit log. Precedent imports it. | Memory buried inside the remediation app |
| 4 | **Incident-class key = deterministic fingerprint** `(service, error_code, target_object_type)` from structured extraction; LLM may *propose*, only fingerprint *equality* counts. No deterministic extraction → hard cap at L1. Graduation: 3 consecutive verified L2 successes → *eligible*; a **human clicks "Promote to standing approval"** (L3 renamed per Conduct judge); any verification failure or rollback auto-demotes to L1 with an audit event. | Undefined graduation; LLM indirectly in the authorisation path |
| 5 | **Three agents on Fetch rails** (Watcher, Librarian, Operator) as Agentverse **mailbox agents** exchanging uAgents messages; Watcher speaks Chat Protocol; **approval-via-ASI:One is a real gate** (sender address = authorising principal, 10-min expiry, no leaked executions). Registered **today (Friday), before console polish**. | Single wrapped Watcher, "gates cuttable" |
| 6 | **Local-first demo:** Jira via 2–3 s polling + write-behind cache (no webhooks/ngrok), embeddings precomputed and committed, LLM fast-path skips inference for graduated classes (the 15 s is engineered, not hoped for), one designed error-recovery beat (verification fails → auto-rollback → demotion → human re-approval). Code freeze Fri 21:00; video + ASI:One shared-chat URL recorded that night. | Webhook + live-everything demo |

---

## 1. Model strategy — open-weight compliance that survives audit

### 1.1 The rule and the trap

BasedAI hard rule (track brief + submission guide, verbatim): *"build with open-weight models only"*, *"no closed, proprietary models in the loop"*, and the README must declare *"the open-weight models you used (required)"*. This covers **every** model call: generation, write-time classification, **and the embedding model behind the memory index**.

**The trap:** Venice's 2026 catalog is no longer open-weight-only. It now proxies closed frontier models — `claude-sonnet-5`, `claude-opus-4-8`, `openai-gpt-55`, `gemini-3-5-flash`, `grok-4-3`, and Alibaba's commercial "`qwen-3-7-plus`" tier, plus Inception's `mercury-2` (weights not public) ([venicestats.com/venice-models](https://venicestats.com/venice-models)). **"It runs on Venice" is not a compliance argument.** Eligibility means pinning specific model IDs whose weights are verifiably published on Hugging Face.

### 1.2 The model registry (single enforcement point)

One module, `precedent/models.py`, is the only place a model ID may appear. Everything else imports roles:

```python
# precedent/models.py — the ONLY file allowed to name a model.
# BasedAI track rule: open-weight only. Every entry must link a public
# weights repo. CI-greppable: `grep -rE "claude-|openai-|gemini-|grok-|mercury-" --include=*.py .`
# must return ONLY this comment.

OPEN_WEIGHT_MODELS = {
    # role: (venice_model_id, hf_weights_url, notes)
    "FAST":  ("qwen3-5-35b-a3b",      "https://huggingface.co/Qwen",      "MoE 35B/3B-active; triage, chat replies, mutation-tolerant extraction assist; tool-calling"),
    "SMART": ("deepseek-v4-flash",    "https://huggingface.co/deepseek-ai","284B/13B-active; retrieval synthesis, risk rationale text, plan drafting"),
    "HEAVY": ("deepseek-v4-pro",      "https://huggingface.co/deepseek-ai","escalation dossiers only — never in the hot path"),
    "EMBED": ("text-embedding-bge-m3","https://huggingface.co/BAAI/bge-m3","MIT licence; ALL embeddings precomputed at build time"),
}
ALLOW_PROPRIETARY_DEV = os.environ.get("PRECEDENT_DEV_MODELS") == "unsafe-dev-only"  # never set in demo/CI
```

Base URL `https://api.venice.ai/api/v1`, OpenAI-compatible SDK (per [Venice docs](https://docs.venice.ai/llms.txt) — chat completions with tool calling + `/embeddings` endpoint). Redeem `IMPERIAL50X` at https://venice.ai/settings/api this morning if not already done.

**Verification step (30 min, do before pinning):** call `GET /models` with the team key, confirm the four IDs exist, and confirm each has a public HF weights repo for the *exact* model card. If a listed ID turns out to be API-only (e.g. anything branded "Plus"/"Preview" without a weights release), substitute from the fallback bench below. Screenshot the `/models` response into the repo (`docs/compliance/venice-models.png`) — cheap audit evidence.

Fallback bench (all with well-established published weights): `llama-4-maverick` (Meta), `qwen-3-6-27b` (Apache-2.0), `zai-org-glm-5-2` (Z.ai), `kimi-k2-7-code` (Moonshot); embeddings alternates `qwen3-embedding-0.6b` (low latency) or `qwen3-embedding-8b` ([Qwen3 Embedding](https://qwen.ai/blog?id=qwen3-embedding); both open-weight, both on Venice per the venice-ai client docs).

**Local open-weight fallback (stage insurance + compliance bonus):** an Ollama profile (`qwen3:8b` generation, `bge-m3` embeddings) selected by `PRECEDENT_MODEL_BACKEND=local`. If Venice flakes on stage (users reported flaky API reliability in the hackathon guide), the loop still runs 100% open-weight on the presenting laptop. This also makes the airplane-mode rehearsal (§4.5) pass by construction.

### 1.3 Role → model mapping and latency budget

| Loop step | Model | Budget | Notes |
|---|---|---|---|
| Watcher: triage messy ticket text → candidate class + structured fields | FAST | ≤3 s, 5 s timeout | Short prompt, JSON tool-call output; the *deterministic extractor* (§3.2) decides, the LLM only proposes |
| Librarian: synthesise retrieved fix into plan narrative | SMART | ≤4 s, 6 s timeout | Only on first-occurrence (L0/L1) incidents |
| Assessor: risk rationale *text* | SMART | ≤3 s | Risk *class* itself is the deterministic YAML policy engine — LLM writes prose, never the decision |
| Operator: typed tool calls | — | ≤2 s | No LLM. Typed adapters only |
| Auditor: memory-record summary | FAST | 5 s timeout, canned fallback string | Async, off the critical path |
| Escalation dossier (incident 3) | HEAVY | no budget | Runs while the human reads the refusal screen |
| Embeddings | EMBED | **0 ms at demo time** | Precomputed at build, vectors committed to the repo; BM25 keyword fallback path |

**The 15-second L3/standing-approval run needs zero LLM calls** (§3.3 fast-path): poll pickup ≤2 s + fingerprint match (ms) + policy gate (ms, §2) + execute (~1 s) + verify (~2 s incl. one retry) + async audit/memory write + optional FAST summary under a 5 s timeout that the UI never waits on. Worst case ≈ 6–8 s of real work — pace it *up* to ~15 s with streamed step events so it reads as visible activity, not lag (technical judge's ask).

**Cost:** the whole build + rehearsal + demo is a few million tokens at $0.14–$3.50/M — $50 credits are an order of magnitude more than enough. No cost-driven reason to touch a closed model.

### 1.4 What to say in the README / on stage

- README "Models" section: the four IDs + HF links + the sentence *"No closed or proprietary model is called anywhere in the pipeline; the only file that may name a model is `precedent/models.py`, and CI greps for violations."*
- Stage line (BasedAI judge's ask — "say it proudly"): *"The entire loop — triage, retrieval, risk prose, audit summaries, and the memory index — runs on open-weight models."*

---

## 2. Permission semantics — the A/B/C model, implemented

### 2.1 Semantics (matching the sponsor's own words)

From the track Discord (2 Jul, santanasupplied ⇄ c0b4lt_27/Thomas, explicitly endorsed): **A** is the semantic rule — *to read a derived artifact, the principal must satisfy the source lineage constraints* (conjunction over ALL sources, not a single strictest label); **B** is the implementation optimisation — a *precompiled "effective policy"* so retrieval checks stay fast; **C** is the exception path — *deliberately redacted/declassified derivatives become new governed objects* with attestation, explicit grants, lineage record, source hashes, and an audit event, approved by a holder of a redact/declassify capability. Admin-defined policy templates; the system applies the safest default automatically; users never pick the mode at query time.

Why A beats strictest-label for Precedent's own demo: incident 3's fix record derives from a **rights-restricted KB article** *and* a **scheduling-project Jira ticket**. Under strictest-label, a rights-ops principal without scheduling-project access could read it. Under A, they can't — access requires satisfying *both* constraints. Name the model "A/B/C" verbatim in the README and demo script; the judge asked for exactly that.

### 2.2 Standalone package

```
precedent_memory/            # importable, reusable governance library — Precedent consumes it
  README.md                  # A/B/C semantics, consistency model, fail-closed policy, audit posture
  schema.sql
  store.py                   # write path: lineage capture + effective-policy compilation
  retrieve.py                # read path: ONE deterministic function, no LLM import allowed
  sync.py                    # Jira ACL poller — versioned, idempotent
  redaction.py               # C-flow: designed + stubbed (see 2.6)
  audit.py                   # hash-chained audit log
  bench/seed_corpus.py       # 8k records / 4 boundaries / 40 principals
  bench/p99_bench.py         # concurrent P50/P95/P99 report → bench/RESULTS.md
  tests/test_conjunction.py  # A-semantics incl. the multi-source counterexample
  tests/test_concurrency.py  # simultaneous ACL flips + retrievals: no widened-access window
  tests/test_fail_closed.py  # stale-cache fallback denies restricted records
```

### 2.3 Schema (SQLite; every field earns its place)

```sql
-- Principals & grants (synced from Jira project roles + KB article restrictions)
CREATE TABLE principal (
  id INTEGER PRIMARY KEY, external_id TEXT UNIQUE,      -- Jira accountId / agent identity / ASI:One sender address
  kind TEXT CHECK(kind IN ('human','agent','service')),
  grant_bits BLOB NOT NULL                              -- precomputed bitmap of constraint-ids this principal satisfies (B fast-path)
);

-- One row per access constraint discovered in a source system
CREATE TABLE constraint_def (
  id INTEGER PRIMARY KEY,                               -- bit position in bitmaps
  source_system TEXT, external_ref TEXT,                -- e.g. 'jira','RIGHTS project role=rights-ops'
  description TEXT, UNIQUE(source_system, external_ref)
);

-- Source artifacts (KB articles, tickets) and their current ACL state
CREATE TABLE acl_source (
  id INTEGER PRIMARY KEY, external_ref TEXT UNIQUE,     -- e.g. 'kb:KB-0042', 'jira:MEDIA-113'
  constraint_ids JSON NOT NULL,                         -- constraints this source imposes ([] = public)
  acl_version INTEGER NOT NULL DEFAULT 0,               -- bumped by sync on every observed change
  last_verified_at TEXT NOT NULL,                       -- freshness input to fail-closed rule
  revoked INTEGER NOT NULL DEFAULT 0
);

-- Memory records: executed-fix-with-provenance + KB summaries + embeddings rows
CREATE TABLE memory_record (
  id INTEGER PRIMARY KEY, kind TEXT,                    -- 'executed_fix','kb_summary','dossier'
  class_key TEXT, fingerprint TEXT,                     -- §3.2
  body JSON NOT NULL,                                   -- symptom, fix steps, approver, risk class, rollback, outcome
  status TEXT NOT NULL DEFAULT 'active'
    CHECK(status IN ('active','quarantined','tombstoned'))
);
CREATE TABLE lineage (record_id INT, source_id INT, source_content_hash TEXT,
                      PRIMARY KEY(record_id, source_id));

-- B: the compiled effective policy — retrieval touches ONLY this table
CREATE TABLE effective_policy (
  record_id INTEGER PRIMARY KEY REFERENCES memory_record(id),
  required_bits BLOB NOT NULL,       -- union of constraint-ids across ALL lineage sources (conjunction, A)
  is_restricted INTEGER NOT NULL,    -- 0 iff required_bits is empty
  policy_version INTEGER NOT NULL,   -- monotonic; bumped on every recompile
  min_source_freshness TEXT NOT NULL,-- oldest last_verified_at across lineage (fail-closed input)
  compiled_at TEXT NOT NULL
);
CREATE INDEX idx_lineage_source ON lineage(source_id);   -- revocation fan-out is one indexed scan

-- Embedding index rows carry NO independent access; joined to effective_policy at query time
CREATE TABLE embedding_index (record_id INTEGER PRIMARY KEY, vector BLOB, model TEXT);

-- Hash-chained audit log (retrievals, denials, sync events, executions, promotions/demotions, redactions)
CREATE TABLE audit_log (
  seq INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, actor TEXT, event_type TEXT,
  payload JSON,                       -- the SOC 2 five elements live here
  prev_hash TEXT NOT NULL, hash TEXT NOT NULL            -- sha256(prev_hash || canonical_json(row))
);

-- C: governed redacted derivatives (stub — full design in 2.6)
CREATE TABLE redaction_derivative (
  id INTEGER PRIMARY KEY, derived_record_id INT, original_record_id INT,
  included_source_hashes JSON, excluded_source_hashes JSON,
  attestation JSON, approved_by INT REFERENCES principal(id),  -- must hold 'redact' capability
  audit_seq INT REFERENCES audit_log(seq)
);
```

### 2.4 The deterministic retrieval path (A enforced via B)

```python
def permitted(principal, record_policy, mode) -> bool:          # NO LLM anywhere in this file
    if record_policy.is_restricted:
        if stale(record_policy.min_source_freshness, mode):     # fallback + stale ⇒ DENY (fail-closed)
            audit("retrieval_denied", reason="acl_freshness_uncertain"); return False
        ok = bits_superset(principal.grant_bits, record_policy.required_bits)  # one bitmask AND — sub-µs
    else:
        ok = True
    audit("retrieval_check", allowed=ok, policy_version=record_policy.policy_version)
    return ok
```

- Candidate generation (vector similarity / BM25) runs first, **but nothing is returned — not a snippet, not a title — without `permitted()` passing on the record row**. Embedding vectors have no ACL of their own; they are reachable only through the join, so revoking a source makes the derived vectors unretrievable automatically.
- **TOCTOU boundary (judge Q):** check + fetch happen in one SQLite transaction; the fetched row's `policy_version` is compared to the checked one, mismatch ⇒ recheck. SQLite's writer serialisation makes the window exact, and we can state it precisely: *revocations are visible to all retrievals at most one poll interval (≤3 s) after Jira, and atomically once written locally.* That sentence is the documented consistency model.
- **Restricted-existence leakage (judge Q, "inference prevention non-claim"):** policy decision — the Librarian may surface, to a non-cleared principal, only the *count* of denied records and the owning team (`"1 restricted remediation exists — owner: Rights Ops"`), never title, symptom, or content. That is a deliberate, documented disclosure choice (it is what makes incident 3's routing work), and it is listed in the README next to the inference-prevention non-claim so it reads as designed, not leaked.

### 2.5 Jira ACL sync — versioned polling, fail-closed fallback

**Poll, don't webhook** (technical judge): webhooks need a public tunnel to a laptop on venue Wi-Fi. A 2–3 s poll of (a) JSM project role/permission-scheme membership and (b) KB article restriction fields is indistinguishable from push on stage and needs no inbound connectivity.

- **Idempotent versioned upserts:** each observed ACL state hashes to a digest; digest change ⇒ `acl_version += 1`, `last_verified_at = now`, single transaction. Re-delivery/reorder is harmless (compare-and-set on digest).
- **Revocation fan-out:** on any `acl_source` change → `SELECT record_id FROM lineage WHERE source_id = ?` (indexed) → recompile each `effective_policy` row (union of lineage constraints, bump `policy_version`) → emit one `acl_sync_applied` audit event per record. Source *deleted* (not just restricted) ⇒ derived records `status='quarantined'`.
- **Fail-closed rule (the line the judge asked to be pointed at):** in `retrieve.py::stale()` — live mode: restricted records require `min_source_freshness` within 60 s; **fallback mode (Jira unreachable): every restricted record is denied, period.** Public-lineage records remain retrievable. A stale cache can narrow access, never widen it. The console shows a "Jira degraded — cached, ACL-restricted memory locked" banner, which turns the fallback into a visible safety feature.
- **Concurrency harness** (`tests/test_concurrency.py`): N writer threads flipping ACLs on random sources + M reader threads retrieving as various principals; invariant asserted: *no retrieval returns a record whose revocation committed before the retrieval transaction began.* Run it in CI and cite it in the README — this converts last version's disclaimer into a consistency story.

### 2.6 C-flow: governed redaction (designed, stubbed, honest)

Implemented as a code path with one happy-path test, demoed only if time allows: agent/user *requests* a weaker derivative → system recommends C and blocks until a principal holding the `redact` capability (seeded: "Head of Rights Ops") approves → new `memory_record` + `redaction_derivative` row with attestation (which sources included/excluded, content hashes), explicit grants replacing inherited conjunction, lineage preserved so **revoking an *included* source still propagates to the redacted derivative** → audit event. README states plainly: *stubbed flow — semantics designed, UI not built.* Judges reward the honest boundary; the schema shows the thinking.

### 2.7 Scale artifact: seeded corpus + P99 method

- `bench/seed_corpus.py`: **8,000 memory records** across **4 team boundaries** (scheduling-ops, rights-ops, platform, service-desk) and **40 principals** with mixed grant sets; lineage fan-in 1–4 sources per record; ~25% restricted. (Data lane may swap synthetic bodies for the Kaggle ServiceNow-derived incident corpus — the governance bench doesn't care what the bodies say, only the ACL topology.)
- `bench/p99_bench.py`: 20 concurrent asyncio workers × 500 retrievals each (mixed principals, mixed hit/deny), measuring the *permission-check* segment and the *end-to-end retrieval* separately; report P50/P95/P99 + methodology to `bench/RESULTS.md`, committed. Expected: a bitmask check over an indexed SQLite row is deep sub-millisecond; the sub-200 ms P99 bar is cleared by ~3 orders of magnitude — say that with the measured number, not the intuition.

### 2.8 The revocation demo moment (60 seconds, scripted for video + Q&A party trick)

1. Split screen: Jira KB article `KB-0042` (the incident-1 runbook) + Precedent memory browser showing the derived executed-fix record retrievable as `scheduling-ops` principal.
2. Presenter flips the article's restriction to Rights Ops in Jira.
3. Within one poll tick (≤3 s): console flashes `acl_sync_applied` audit event → re-run the same query → **denied**, including the embedding-index path (show the vector row still existing but unreachable).
4. Punchline: *"Revoke the source, and everything ever derived from it — summaries, fix records, embeddings — goes dark, in seconds, with an audit event to prove it."*
5. Flip it back; access restored; second audit event. (Restoration proves it's live, not a canned clip.)

---

## 3. Agent topology — five agents, hardened

### 3.1 Message contracts (pydantic models, shared `precedent/contracts.py`)

```
IncidentEvent    {incident_id, jira_key?, raw_text, source('sim'|'jira'|'chat'), observed_at}
TriageResult     {incident_id, extracted:{service, error_code, target_object_type} | null,
                  extraction_method('deterministic'|'llm_proposed'), candidate_class_key?, confidence}
RetrievalBundle  {incident_id, principal_id, hits:[{record_id, kind, score}], denied_count, denied_owner_team?}
RiskAssessment   {incident_id, risk_class, policy_rule_id, ladder_level, rationale_text}
ExecutionPlan    {incident_id, steps:[TypedToolCall], rollback_steps:[TypedToolCall],
                  pre_state_snapshot_ref, plan_hash}
ApprovalRequest  {incident_id, plan_hash, risk_class, ladder_level, requested_at, expires_at, channel}
ApprovalDecision {incident_id, plan_hash, decision('approve'|'reject'), approver_principal, channel, decided_at}
ExecutionResult  {incident_id, plan_hash, step_results, verified(bool), rolled_back(bool), elapsed_ms}
MemoryWrite      {record: executed-fix-with-provenance, lineage_source_refs, class_key}
```

Every hop appends to the hash-chained audit log; `ApprovalDecision.approver_principal` is the authorising principal in the five-element record (console click = logged-in demo user; ASI:One = Chat Protocol sender address — the pre-armed SoD answer: *"in production this maps to SSO; the control structure — requester ≠ approver, immutably logged — is identical"*).

### 3.2 Incident-class key — what makes two incidents "the same"

```
class_key   = f"{service}|{error_code}|{target_object_type}"        # canonicalised enums/uppercase
fingerprint = sha256(class_key)                                     # e.g. scheduler|EPG_PUBLISH_META_MISSING|schedule_item
```

- A **deterministic extractor** (regex + canonicalisation tables over the structured incident payload and known error-code dictionary) computes the fields. The FAST LLM may propose fields for messy free-text tickets (the judge-files-a-ticket moment), **but a class match counts only when the deterministic extractor confirms them** — extractor-confirmed equality, not semantic similarity.
- **If deterministic extraction fails** (typo'd unknown code, two incidents in one ticket, missing fields): the incident is capped at **L0/L1 regardless of the class's ladder level**, and the trace shows why ("error code not in known dictionary — escalating for human confirmation"). This is the graceful-degradation beat the Conduct judge asked to see live.
- This closes the "the LLM authorised itself one hop upstream" attack **in code**: nothing the LLM outputs can unlock standing-approval execution; only deterministic field equality can.

### 3.3 Ladder: graduation, demotion, and the fast-path

| Rule | Definition |
|---|---|
| Promotion eligibility | 3 **consecutive** verified L2 successes for the class, zero rollbacks, per-class counter in `class_ladder` |
| Promotion | **Human clicks "Promote to standing approval"** (UI + audit event, records the promoting principal). Never automatic. A visible **Revoke** button demotes instantly. *(Naming per Conduct judge: L3 = "Standing Approval — pre-approved standard change"; approval moves earlier in time, never out of the loop.)* |
| Demotion | Any verification failure or rollback ⇒ class → L1 immediately + `class_demoted` audit event. Also answers autonomy-drift: success counters reset on demotion, and the promotion event names a human owner. |
| Anti-gaming (judge Q: "file N synthetic easy tickets") | Successes only count from incidents whose source is the monitored systems (`sim`/`jira`-verified), each with a distinct target object; N identical-object repeats within an hour count once. One sentence in the audit-log slide. |
| Fast-path | `fingerprint` matches a class at standing-approval ⇒ **skip all LLM calls**: retrieve the graduated record, policy-gate, snapshot pre-state, execute typed calls, verify, write memory + audit; stream each step to the console. This is what makes the 15 s deterministic (§1.3). |

### 3.4 Where Fetch rails wrap the topology

**Three Agentverse-registered agents** (fetch judge's explicit ask), all **mailbox agents** — they run on the team laptop, connect *outbound* to Agentverse, need no public IP, and survive venue Wi-Fi NAT:

| Agent | On Fetch rails | Protocols |
|---|---|---|
| **Watcher** | Gateway + triage. Speaks **Chat Protocol** (`uagents_core.contrib.protocols.chat`: `ChatMessage`/`ChatAcknowledgement`/`StartSessionContent`/`TextContent`/`EndSessionContent`, `publish_manifest=True`) — the ASI:One entry point. Forwards `IncidentEvent`→`TriageResult` | Chat Protocol + custom `PrecedentProtocol` (the pydantic contracts as uAgents models) |
| **Librarian** | Retrieval + memory governance. Receives `TriageResult`, returns `RetrievalBundle` (ACL-filtered via `precedent_memory`) | `PrecedentProtocol` |
| **Operator** | Execution + Jira writes. Receives approved `ExecutionPlan`, returns `ExecutionResult` | `PrecedentProtocol` |

Assessor and Auditor stay in-process (deterministic policy engine and audit writer gain nothing from network hops, and saying so is the honest answer to "is Agentverse load-bearing?" — the answer becomes: *inter-agent orchestration and the human approval gate ride Fetch rails; the deterministic safety kernel deliberately does not*).

**Approval-via-ASI:One as a real gate:** `ApprovalRequest` renders as one well-formatted `ChatMessage` (triage + retrieved fix + risk class + rollback plan + Jira link). A reply matching `approve`/`reject` becomes an `ApprovalDecision` with `approver_principal = sender address`. Pending approvals live in the `approval` table with `expires_at = +10 min`; **a dropped session mid-approval expires the pending execution — it never leaks** (re-prompt on next contact). That is the scripted answer to the fetch judge's session-drop question.

**Today (Friday), before any console work:** register all three on Agentverse with keyword-rich descriptions ("IT incident resolution, EPG publish failure, Jira ticket remediation, runbook automation"), Innovation Lab README badge, redeem `UKAIAGENTUKAIAGENTAV`, then **test discovery end-to-end from a fresh ASI:One session** and capture a public shared-chat URL of incidents 1+2 the moment a clean run exists (re-record against the frozen build Friday night). Keep direct agent-address chat as the discoverability fallback. Docs: https://innovationlab.fetch.ai/resources/docs/intro, examples: https://github.com/fetchai/innovation-lab-examples.

**Scripted ASI:One conversation** (the submission artifact, mirrors the stage demo): report incident → one formatted message (triage + fix + risk + rollback) → "approve" → executes, closes the real Jira ticket, replies with audit-trail hash + Jira link → report the same class again → standing-approval run completes in-chat with no approval prompt, timer shown. Give this 60–90 s of the demo video, top billing per the fetch judge.

**Cheap bonus:** leave the Watcher running as a hosted/mailbox agent post-hackathon and say so in the README ("agents that keep running" bonus category).

---

## 4. Demo reliability engineering

### 4.1 Jira: local-first, write-behind, replayable

- **Read path:** poll JSM every 2–3 s (`/rest/api/3/search` with `updated >= -1m` JQL + permission-scheme reads for the ACL sync). No webhooks, no ngrok.
- **Write path:** all Jira writes (create, comment, transition, attach evidence) go through an async **write-behind queue** — the on-stage flow never blocks on Atlassian; the console renders from local state and shows a sync tick when Jira confirms.
- **Cache + replay:** every Jira response is cached (`jira_cache.sqlite`). Fallback mode serves reads from cache, queues writes for replay, flips the console banner, and **locks restricted memory** (§2.5 fail-closed). Rehearse the toggle — it's a feature beat, not a contingency.
- Provision the JSM trial **before noon today**; its friction is on the critical path (idea doc already flags this).

### 4.2 Models: pre-warmed, cached, canned

- Embeddings: computed at build time, vectors committed. Zero embedding calls at demo time; BM25 fallback wired.
- LLM calls: 5–6 s timeouts with canned fallback strings everywhere; a **response cache keyed by prompt hash** recorded during rehearsal makes reruns instant and makes airplane-mode rehearsal pass; live calls remain the default while connectivity holds.
- One warm-up request per model at app start (avoids first-token cold start mid-pitch).

### 4.3 Deterministic demo seeds

- Incident generator takes `--seed`; incidents 1/2/3 are fixed seeds producing identical payloads every run.
- **Messy-input mutations** (Conduct judge): mutation layer (typos, colloquial symptoms, dropped error codes, red-herring details) driven by the same seed — rehearsable yet honestly messy; say the word "unscripted" on stage when the judge files a live ticket from a phone (that path exercises §3.2 graceful degradation).
- Sim state resets from a fixture snapshot in one command (`make demo-reset`) so a botched run restarts in seconds.

### 4.4 The designed error-recovery beat (~20 s, technical judge's ask)

Scripted into the video and available live as a Q&A party trick: `POST /sim/publisher/flake?once=true` arms a single verification failure → incident 2's *first* execution fails verification → **auto-rollback restores the pre-state snapshot on screen** → class demotes (audit event: `class_demoted, reason=verification_failure`) → escalates to L1 → human re-approves → success → counter starts rebuilding. One beat demonstrates rollback-before-execute, verification, demotion, and human re-entry — four rubric items in twenty seconds. (Rollback pre-state: full JSON snapshot of the target object captured *before* execution, stored on `ExecutionPlan.pre_state_snapshot_ref`; a failed rollback write escalates with the snapshot attached to the Jira ticket — the byte-by-byte Q&A answer.)

### 4.5 Freeze & record discipline

- **Fri ~21:00: code freeze.** Record the 5-min video + the ASI:One shared-chat session against the frozen build that night; capture Agentverse profile URLs. Never show ASI:One live on stage — the pitch demos the console, the video demos the gates.
- **Airplane-mode rehearsal must pass** for incidents 1+2: local sim, cached Jira in write-behind, committed embeddings, cached/canned LLM responses, local Ollama backend available. If it passes with Wi-Fi off, venue Wi-Fi cannot kill the pitch.

---

## 5. Build order & critical path (workstreams, no role assignments)

Estimates assume the collapsed sim (one FastAPI app, 4 routers, one SQLite file — rights+publisher merged per the Conduct judge's pre-cut) and agents as orchestrated functions in one process, with uAgents mailbox wrappers only where §3.4 says so.

**Friday AM (unblockers — start all four in parallel):**
1. `models.py` pin + Venice `/models` verification + Ollama fallback profile — **1.5 h** (unblocks everything; BasedAI eligibility)
2. JSM trial provisioning + API token + demo project + permission schemes — **1 h elapsed, start by 10:00**
3. Agentverse registration × 3 (mailbox agents, Chat Protocol echo skeleton, Innovation Lab badge, fresh-account ASI:One discovery test) — **3–4 h** (fetch judge: before any console polish)
4. `precedent_memory` schema + write/retrieve paths (A/B semantics) — **3 h**

**Friday PM (core):**
5. Core loop: contracts, deterministic extractor + fingerprint, policy engine YAML, ladder table, fast-path — **4 h**
6. Sim app + seeded real data (data lane owns content; this lane owns the surfaces) + incident generator with seeds/mutations — **3–4 h**
7. Jira poll + write-behind + ACL sync + fail-closed fallback — **3 h**
8. Approval-via-chat flow end-to-end inside ASI:One; capture first shared-chat URL — **2–3 h**
9. Console: incident feed, trace stream, approve/promote/revoke buttons, before/after timeline bar, audit view — **4–6 h**
10. Revocation demo moment + concurrency test + `seed_corpus`/`p99_bench` run committed — **3 h**
11. **21:00 freeze → record video + ASI:One session + Agentverse URLs**

**Saturday AM:** BasedAI PR into `github.com/BasedAICo/hackathons` (fork, copy `UK-AI-Agent-EP5/submissions/_TEMPLATE/`, README with models/architecture/video link, **no secrets**, PR open before judging — **1.5 h, assign an owner at stand-up**); deck; DoraHacks form; rehearsal to 2:40; buffer.

**Updated cut-lines (ordered; replaces §3 of the idea doc):**
1. C-flow demo (keep the stub + schema — near-free)
2. Temporal-embargo YAML rule (BasedAI bonus flourish)
3. Third Fetch agent (Librarian) collapses in-process — **floor is two registered agents + Chat Protocol + ASI:One flow, which is NON-CUTTABLE** (see flag F1)
4. Stale-KB-repair nice touch; ROI ticker animation → static counter
5. P99 bench shrinks from 8k to 2k records (never to demo-rows-only)
6. Incident 3 (refusal) — **never cut incident 2**; the standing-approval repeat is the thesis
**Non-cuttable under any slip:** open-weight pin; BasedAI PR (if track pursued at all); Fetch hard gates; messy-input handling + error-recovery beat (35% Conduct criterion); fail-closed fallback.

---

## 6. Flags for the team (conflicts + decisions needed today)

- **F1 — Locked-decision contradiction (fetch judge called it fatal):** "Fetch.ai track committed" and old cut-line #2 "Fetch.ai gates cuttable" cannot both be true — partial Fetch integration scores zero. This doc makes the gates non-cuttable and front-loads them to Friday morning; if the team instead wants them cuttable, formally un-tick the Fetch bounty on DoraHacks today. Decide at stand-up, in writing.
- **F2 — Open-weight rule vs idea doc:** "plus any OpenAI/Anthropic keys" (Idea-Development §3) is BasedAI-ineligible as written. Resolved here (model choice was explicitly not locked): proprietary keys are dev-only behind `PRECEDENT_DEV_MODELS`, never set in demo/CI, and the README says so. Also note: **Venice hosts closed models now** — anyone grabbing `claude-sonnet-5` off the Venice catalog silently kills eligibility; the CI grep in §1.2 is the guard.
- **F3 — BasedAI PR is a separate submission mechanism** (PR into BasedAICo/hackathons before Demo Day judging); DoraHacks alone does not enter the track. Owner needed now.
- **F4 — L3 rename** ("Standing Approval — pre-approved standard change") is assumed throughout this doc's schema/UI (`class_ladder`, Promote/Revoke buttons) per the Conduct judge; pitch lane owns the wording on slides — coordinate so code labels and deck match.
- **F5 — Demo Day sign-up form due TODAY 18:00** (https://forms.gle/fnUe3vL24wyJo6pD7) — outside this lane but it gates the entire pitch.
- **F6 — Model availability risk:** the exact Venice IDs in §1.2 were taken from a third-party catalog snapshot ([venicestats.com](https://venicestats.com/venice-models)); the 30-minute `GET /models` + Hugging Face weights verification is mandatory before pinning, with the fallback bench ready. If Venice's open-weight lineup is thinner than listed, the Ollama-local profile is itself fully eligible.
