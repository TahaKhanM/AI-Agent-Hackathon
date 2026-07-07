# Precedent — The Stack at Two Depths

> Prep artifact, 3 Jul 2026. Depth 1 is for whoever fields engineer/judge questions (source of truth: `docs/idea/refinement/02-architecture-refinement.md`). Depth 2 is the plain-English version for N1/N2 — read it once and you can explain the whole product without a single acronym. Each depth ≤2 pages.

---

## DEPTH 1 — ENGINEER

### The closed loop, component by component

Incidents enter from three sources: the seeded MediaCo generator (deterministic seeds, mutation layer for messy text), the real Jira Service Management project (2–3 s poll, no webhooks), and ASI:One chat. Then:

1. **Watcher** (Agentverse mailbox agent; speaks Chat Protocol — the ASI:One entry point). Triage: a **deterministic extractor** (regex + canonicalisation tables + a known error-code dictionary over structured fields) computes `(service, error_code, target_object_type)`. The FAST LLM may *propose* fields for messy free text, but **a class match counts only when the deterministic extractor confirms them**. Extraction failure (unknown code, missing fields) ⇒ incident hard-capped at L0/L1 regardless of the class's ladder level, with the reason on the trace.
   - `class_key = service|error_code|target_object_type` (canonicalised); `fingerprint = sha256(class_key)`. Equality, never similarity.
2. **Librarian** (Agentverse agent). Retrieval over `precedent_memory`: candidate generation (precomputed embeddings / BM25) runs first, but **nothing is returned — not a snippet, not a title — without `permitted()` passing** on the record row. Returns hits + `denied_count` + owning team (a deliberate, policy-controlled disclosure — see non-claims).
3. **Assessor** (in-process, deliberately — permission decisions never ride network hops). Deterministic policy engine: YAML rules keyed on (system × action type × risk class × autonomy level). **No LLM call in any permission decision**; the SMART model writes rationale *prose* only.
4. **Approval gate.** Ladder: L0 Observe → L1 Recommend → L2 Execute-after-approval → **L3 Standing Approval (pre-approved standard change — never "autonomous")**. Approver = console click identity or the ASI:One **Chat Protocol sender address**; requester ≠ approver on every run. Pending approvals carry a 10-min TTL — a dropped session expires to a non-action, never a leaked execution.
5. **Operator** (Agentverse agent). **Typed tool calls only** — no shell, no free-form console. Before the gate: full pre-state JSON snapshot captured + inverse write computed. **No rollback plan, no execution** — it's a gate precondition. Execute → verify (deterministic, per fix class, read-side: publish state green, rights window matches, EPG rendered).
6. **Failure path:** verification fails → pre-generated rollback fires automatically → class demoted to L1 (`class_demoted` audit event, success counters reset) → escalation dossier (HEAVY model, off the critical path). If the rollback *write* fails: class frozen to L0, human paged with the stored pre-state — loudly stuck, never silently wrong.
7. **Auditor** (in-process). Hash-chained audit log — `hash = sha256(prev_hash || canonical_json(row))` — five-element payload (input, reasoning, action, authorising rule, approver + before/after state). Memory write: the **executed-fix-with-provenance record** (symptom → verified fix → approver → risk → rollback → outcome) + lineage refs. That record, not the document, is the ranking unit — recency and success-rate metadata is why a verified-last-Tuesday fix outranks a stale article.

**Graduation, verbatim:** *L3 after 3 consecutive verified L2 successes with zero rollbacks; any verification failure or rollback demotes the class to L1; a human clicks Promote, a human can click Revoke.* Anti-gaming: only verified executions from authenticated monitored sources count, distinct target objects, identical-object repeats within an hour count once.

### The fingerprint fast-path (why 15 s is engineered, not hoped)

Fingerprint equality with a standing-approval class ⇒ **zero LLM calls**: poll pickup ≤2 s + fingerprint match (ms) + policy gate (ms) + execute ~1 s + verify ~2 s incl. one retry + async audit/memory write; an optional FAST summary sits behind a 5 s timeout the UI never waits on. Real work ≈6–8 s worst case, paced *up* to ~15 s with streamed step events. Elsewhere: FAST triage ≤3 s (5 s timeout), SMART synthesis ≤4 s (6 s), SMART risk prose ≤3 s, HEAVY dossiers unbounded off-path, EMBED **precomputed at build time — 0 ms at demo time**, BM25 fallback wired. Every LLM call has a timeout + canned fallback string; the loop stays deterministic without it.

### Permission-aware memory — A/B/C semantics + bitmap compilation

- **A (the rule):** to read a derived artifact, the principal must satisfy **ALL** source lineage constraints — conjunction over the full set, not one strictest label. Why: incident 3's fix record derives from a rights-restricted KB article *and* a scheduling ticket; strictest-label would let a rights-ops principal without scheduling access read it. Conjunction can't.
- **B (the fast path):** an `effective_policy` row per record — `required_bits` = union of constraint ids across all lineage sources, **compiled at write/sync time**; each principal carries precomputed `grant_bits`. The runtime check is **one bitmask AND — sub-µs, O(1) in role count** — which is why P99 stays flat as the corpus grows.
- **C (the exception):** a redacted/declassified derivative is a **new governed object** — explicit grants, redaction attestation, source hashes, lineage preserved (revoking an included source still propagates). Approved only by a human holding the redact capability; agents can request, never grant. Designed + stubbed; the README says so plainly.
- **Sync:** 2–3 s versioned Jira poll over (a) project-role membership, (b) live permission-scheme 10000 grants, (c) the **issue-security field on restricted runbook issues** (real Jira enforcement — scheme 10000, levels 10000/10001, verified live). Digest compare-and-set, idempotent upserts. Revocation fan-out: one indexed scan over `lineage(source_id)` → recompile each effective-policy row → `acl_sync_applied` audit event per record. Source deleted ⇒ derived records quarantined; vectors hard-deleted in the background (embedding rows have no independent ACL — they're reachable only through the policy join).
- **TOCTOU:** the ACL filter is a predicate *inside* the retrieval query — check + fetch in one SQLite transaction, `policy_version` compared on the fetched row, recheck on mismatch. Stated consistency window (measured): Jira-side propagation ≤5 s + poll ≤3 s ⇒ **flip→dark ≤8 s worst case, atomic once written locally** — dual-enforced (Jira 404s the runbook itself) with both audit logs timestamp-matched via Jira's auditing API.

### Fail-closed rules (the complete list — volunteer these)

1. Restricted record with uncertain ACL freshness (>60 s in live mode) → **deny** + audit event.
2. Jira unreachable (fallback mode) → **every restricted record denied, period**; public-lineage records still served; amber "ACL-restricted memory locked" banner. A stale cache can narrow access, never widen it.
3. Deterministic extraction fails → L0/L1 cap.  4. No rollback plan → no execution.  5. Rollback write fails → class frozen L0 + human paged.  6. Chat session drops → pending approval expires (10 min TTL).  7. LLM timeout → canned fallback, deterministic loop continues.

### Bench architecture (BasedAI conformance — decoupled from product code)

- **`bench/conformance_bench.py`:** generates the sponsor's exact protocol topology — **5 hierarchy levels / 20 roles / 1,000 ACL-tagged docs / 10,000 ground-truth queries** (≥3,000 deny-expected, so FNR <0.1% is claimable by the rule of three). **Independent oracle:** expected labels come from a separate naive lineage-conjunction walk (~40 lines, no bitmaps) — FNR/FPR = bitmap-vs-oracle disagreement, never the compiler grading itself. Output: `bench/RESULTS.md`, measured-vs-threshold pass/fail for FNR <0.1% / FPR <2% / P50 <50 ms / P99 <200 ms / overhead <100 ms / correctness >99% / drift <0.5% / TTC <5 min / 100% audit coverage / O(1)–O(log n).
- **Realism run:** same harness over the **UCI-derived ~25k-record store** (ACL boundaries from real `assignment_group` fields + 40 principals, concurrent queries). Caption discipline: "P99 over the 25k-record store" — never "over 141k events".
- **`tests/test_adversarial.py`:** six named attacks verbatim — query inference, metadata bypass, timing, collection, prompt injection, derived-memory. **`test_concurrency.py`** invariant: no retrieval returns a record whose revocation committed before the retrieval transaction began. **`test_audit_coverage.py`**: every path writes an audit row. **Live drift/TTC:** flip timestamps taken from Jira's own audit-records API (ms precision) — the external, regulator-grade clock.
- **Extractor bench:** 100 mutated tickets → correct-match / safe-degrade / **false fast-path (target: 0)**; runs Fri 18:30; numbers surface as the on-trace robustness chip.

### Models (open-weight, one enforcement point)

| Role | Venice ID | Weights / licence |
|---|---|---|
| FAST (triage, chat, summaries) | `qwen3-5-35b-a3b` | Qwen3.5-35B-A3B — Apache-2.0 |
| SMART (synthesis, risk prose) | `deepseek-v4-flash` | MIT |
| HEAVY (dossiers only) | `deepseek-v4-pro` | MIT |
| EMBED (build-time only) | `text-embedding-bge-m3` | BAAI bge-m3 — MIT |

`precedent/models.py` is the **only** file allowed to name a model (CI grep enforces; startup asserts every entry's `modelSource` is a huggingface.co URL — the `null`-check heuristic was refuted, don't cite it). `/models` dumps committed in `docs/compliance/`. Ollama local profile (`qwen3:8b` + `bge-m3`) = airplane-mode insurance, still 100% open-weight.

---

## DEPTH 2 — PLAIN ENGLISH (for N1/N2)

### The one-paragraph story

Precedent is a new colleague for IT operations teams. When something breaks, it remembers every fix the company has ever applied, finds the right one, **asks a human before touching anything**, does the fix through official channels only, checks its own work, and writes everything down in a tamper-proof logbook. The more it's trusted with, the faster things get — and it earns that trust one verified success at a time, from a human who can take it back with one click.

### The pieces, each with its analogy

- **The problem.** When something breaks, the fix usually already exists — written down in a manual somewhere. But finding it and getting permission takes on average **8 hours 51 minutes**, for what is often minutes of actual work. It's a library where the book exists but nobody can find it, and you queue for the librarian anyway.
- **The five agents** are five colleagues with strict job descriptions: a **receptionist** (Watcher) who reads incoming complaints and works out what kind of problem it is; an **archivist** (Librarian) who finds how we fixed this before — but only opens filing cabinets *you* hold a key to; a **compliance officer** (Assessor) who checks a printed rulebook — no opinions, no judgement calls; an **engineer with a sealed toolbox** (Operator) who can only use the specific approved tools, never improvise; and a **notary** (Auditor) who writes every step in ink, in a ledger where tearing out a page is instantly visible.
- **The fingerprint is a barcode, not a description.** Two incidents count as "the same problem" only if their barcodes match *exactly* — which system, which error code, which kind of thing broke. A smudged or misread barcode never opens the express lane; a human looks at it instead. Importantly, the AI can *suggest* what the barcode says, but a mechanical check has to confirm it — the AI never grades its own reading.
- **Standing approval = a standing order at your bank.** You approved the rent payment once; it now goes out monthly without asking you again. You set the exact conditions, the bank records every payment, and you can cancel any time. It is *not* the bank spending your money on its own judgement. And it's earned like a probation period: three verified successes before a manager signs it off — and one failure puts it straight back under supervision, automatically.
- **Lineage = the ingredients list on a recipe.** Every remembered fix lists exactly which documents and tickets it was made from. If one ingredient is recalled — a document gets restricted or deleted — every dish made with it comes off the menu automatically, in seconds. We show this live: restrict a runbook in Jira, and both Jira *and* Precedent's memory hide everything made from it, each writing its own log entry.
- **The permission rule: two cabinets, two keys.** If a fix was written using files from two locked cabinets, reading it requires *both* keys. One key is never enough — that's how a fix built partly from rights-team secrets stays out of reach of anyone who isn't rights-team.
- **The speed trick: a keyring card.** Instead of walking to every cabinet to try your keys, everyone carries a card listing the keys they hold, and every file lists the keys it needs. Checking access is one glance at two cards — which is why it stays instant whether there are a hundred fixes in memory or a million.
- **Fail-closed = a door that locks when the power cuts.** If Precedent can't be *sure* what your permissions are right now — say Jira is unreachable — restricted memory locks shut. It never guesses open. A bank vault doesn't swing open in a blackout.
- **Rollback = writing the undo before you do.** Like photographing the shelf before rearranging it: before any fix runs, Precedent saves an exact "before" picture and writes the instructions to put everything back. If its self-check fails, the undo runs by itself. If even the undo can't run, it stops loudly and calls a human — never quietly wrong.
- **Verification = checking the TV guide actually shows the programme.** It doesn't trust that the button was pressed; it looks at the result and compares it with what should be there.
- **The refusal (the third demo incident).** Precedent knows a fix exists but the manual belongs to another team — so it says, in effect: *"there's a file on this, but it's the rights department's — I'll route you to them,"* without opening the file. That's the line that matters to security chiefs: **it knows what it's not allowed to touch.**
- **The chat version (ASI:One).** The whole thing works inside a chat conversation — you describe the problem, it replies with the fix, the risk, and the undo plan; you type "approve". That approval is signed by your chat identity, like signing for a parcel: there is always a named someone on the record, and it is never the agent itself.

### The numbers you might be asked to repeat (exactly these words)

- Manual average: **8 hours 51 minutes**. First fix with Precedent: **about 60 seconds** (a human clicks approve). Repeats: **about 15 seconds** — *"the second time is free."*
- We fed it **24,918 real incidents** from a public log: **94% arrived with their fix already known** — and those repeats *still* took a median **18 hours (calendar time)** to fix by hand. That's the waste we delete.
- After a permission change, everything derived from that document goes dark in **under 8 seconds** — enforced by both Jira and Precedent, with two matching logbooks.
- The two sentences to remember, whatever else is forgotten: **"The second time is free."** and **"It knows what it's not allowed to touch."**

### One warning (same for everyone)

Never call it "autonomous". The correct phrase is **"standing approval — a pre-approved standard change"**, and the saving sentence is: *"Approval moved earlier in time — it never left the loop."*
