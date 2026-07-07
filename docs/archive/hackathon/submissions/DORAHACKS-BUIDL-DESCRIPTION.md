# Precedent

**Your last outage already had a fix. Precedent finds it, checks the risk, gets a human's approval, executes it, then remembers it.**

*Every incident resolved becomes precedent.*

An approval-gated agent that detects an enterprise incident, retrieves the organisation's **own documented fix**, classifies its risk **deterministically**, executes it through typed tools **behind a human approval gate**, verifies the result and **auto-rolls-back on failure**, then remembers the outcome as an *executed fix with provenance*.

> **Thesis:** AI SREs fix broken *code*. In real enterprises the fix is almost never code. It is a *documented admin change* a human already wrote down. Precedent turns each resolved incident into reusable, permission-scoped institutional memory.

Four properties, in every loop: **risk-classified · approval-gated · audited · reversible.**

---

## The problem (priced)

Enterprises don't fail because the answer is unknown. They fail because the answer is *known, written down, and unreachable at 2am under the right permissions*.

- **>60% of issues are already-seen-and-solved repeats** (*ServiceNow's own KCS support-desk case study*). The fix usually already exists in a runbook.
- Yet unplanned downtime still costs the Global 2000 **~$200M/year per company** (*Oxford Economics / Splunk 2024*) and **$600B/year in aggregate** (*Splunk 2026 refresh*), because the runbook and the button live in two different worlds.
- Industry mean IT-support MTTR is **8h 51m (8.85 business hours)**, per the *MetricNet / HDI benchmark*.

The market is validating the thesis with capital: ServiceNow paid **$2.85B for Moveworks (March 2025)**.

When the CrowdStrike update took down endpoints in July 2024, staff at sites like **Disneyland Paris were forced back to checking tickets by hand**. The remediation runbook existed; reaching it fast and safely, under the right hands, did not.

---

## What it is (the solution)

Precedent closes one loop:

**detect → find the org's own documented fix → classify risk deterministically → get human approval → execute through typed tools → verify → auto-roll-back on failure → remember as an executed fix with provenance.**

- **The model proposes; deterministic policy disposes.** There is **zero LLM in the permission or risk decision.** An incident's class is a computed fingerprint, `sha256(service | error_code | target_object_type)`, matched only on extractor-confirmed field **equality**, never semantic similarity.
- **Memory is permission-aware.** A fix retrieved for one team is not served to another unless the org's live ACLs allow it, enforced in the retrieval layer, not by a prompt.
- **The loop is reversible.** Every typed tool call has a declared inverse; a failed verification triggers automatic rollback and demotes any standing approval. *Control beats autonomy.*

---

## What a judge sees in the demo (MediaCo)

The stage is **MediaCo**, a simulated broadcaster. The *systems* are simulated; the *content is real, licensed public data* (see Data provenance). One incident feed, one console, three incidents:

- **Incident 1, first-of-class (the full loop).** A scheduling conflict fires. Precedent fingerprints the incident, finds the org's documented fix, classifies it, and stops at a **human approval gate**. An operator clicks **Approve**; the Operator agent executes the typed tool call, verifies, and writes a hash-chained "executed fix with provenance" bound to the approver's identity. Weeks of process, compressed to minutes, with a human in control.
- **Incident 2, "the second time is free" (fast-path).** The *same class* recurs. Because a matching precedent exists and the class has earned **Standing Approval**, Precedent takes the pre-authorised fast-path: no LLM call, deterministic match, executed and verified in one motion.
- **Incident 3, the refusal (fail-closed).** An incident touches restricted **"Rights Ops Only"** memory while ACL freshness is uncertain. Precedent **refuses to serve it** and shows the fail-closed banner. A stale cache can narrow access, never widen it. A leak is worse than an outage, so the refusal *is* the feature.
- **Recovery / rollback.** When a verification fails, Precedent **auto-reverts** via the tool's declared inverse and **auto-demotes** that class's standing approval back to a manual gate. Control is never silently retained after a failure.

**Before / after** is on screen the whole time: the **Baseline Bar (8h 51m industry MTTR)** sits next to Precedent's live resolution, and every action is **Approve / Promote / Revoke**, one click, human-held.

---

## Why it wins each track

### Conduct, "Make Legacy Move"

A real enterprise process, incident-to-resolution at a broadcaster, taken from **weeks to minutes**, with a **human in control the whole time** (Approve / Promote / Revoke; L3 is *Standing Approval*, never autonomous). Built on a simulated MediaCo running on **real public data**. *Killer proof:* the on-stage before/after against the **8h 51m** industry baseline, resolved through the organisation's *own* documented fix, not invented code. *Control beats autonomy.*

### BasedAI, "Enterprise Memory Governance at Scale"

Permission-aware memory with **deterministic retrieval-layer enforcement (no LLM in the permission decision)**, lineage-governed revocation (A/B/C conjunction over *all* upstream sources), and regulator-grade hash-chained audit, on **open-weight models only**. *Killer proof:* **P99 `permitted()` = 0.590 µs over the 25,000-record store**, **0 leaks across 7,529 deny-expected checks**, **6/6 adversarial attacks defeated**, and a real **3-flip revocation-drift proof** (TTC median 0.24 s, 0.000% stale-allow).

### Fetch.ai

Three agents **registered and ACTIVE on Agentverse** (confirmed via the Almanac API, `status=active`, 2026-07-04), speaking the **Agent Chat Protocol**, usable **inside an ASI:One conversation with no custom frontend**. The approver is bound to the ASI:One sender address. *Killer proof:* a shared ASI:One chat with ten interactions and five distinct real audit hashes.

| Agent | Role | Address |
|---|---|---|
| **Watcher** | Gateway / triage / ASI:One entry point | `agent1q2m0gk9wdvs0lyc3nfuyeet4y3nc68m9y24kehun2t70hadwf7qxjcgkldx` |
| **Librarian** | Permission-aware retrieval | `agent1qv760pr29kmy9w5lst4tffr06rv6qqmt0ef74w6ycfezd5hfh0e0kse9xv7` |
| **Operator** | Typed-tool execution + audit + rollback | `agent1qwesj8x7797jatzt3dwn8gxk2skxsaghrcpa76n548s6a6fz97wvuxna02g` |

- **Try it in ASI:One:** https://asi1.ai/invite?channelInviteKey=NmIsH5-DHQVhnf78uThoWX3fVkRXiSpGz78rMsPkoUQ
- Profiles: [Watcher](https://agentverse.ai/agents/details/agent1q2m0gk9wdvs0lyc3nfuyeet4y3nc68m9y24kehun2t70hadwf7qxjcgkldx/profile) · [Librarian](https://agentverse.ai/agents/details/agent1qv760pr29kmy9w5lst4tffr06rv6qqmt0ef74w6ycfezd5hfh0e0kse9xv7/profile) · [Operator](https://agentverse.ai/agents/details/agent1qwesj8x7797jatzt3dwn8gxk2skxsaghrcpa76n548s6a6fz97wvuxna02g/profile)

---

## How it works

**Five roles, three of them Fetch agents:**

1. **Watcher**, gateway, triage, and the **ASI:One entry point** via the Agent Chat Protocol.
2. **Librarian**, permission-aware retrieval over the memory store.
3. **Operator**, typed-tool execution, hash-chained audit, and rollback.
4. **Extractor** *(deterministic, in-loop)*, computes the incident-class fingerprint.
5. **Policy engine** *(deterministic, in-loop)*, classifies risk and gates execution.

- **The decision has no LLM in it.** The class key is a deterministic fingerprint; the permission decision and the risk decision are pure policy over live ACLs. Models are open-weight and confined to *proposing*, never disposing.
- **Permission-aware memory.** Lineage is a **conjunction over all sources** (A/B/C semantics): a derived memory is reachable only if *every* upstream source permits the caller. Enforced deterministically in the retrieval layer.
- **Fail-closed.** If ACL freshness is uncertain (Jira unreachable or cache stale), **restricted memory is denied, never served.** A stale cache may narrow access, never widen it.
- **Standing Approval, never Autonomous.** A class graduates to L3 **Standing Approval** only after **3 consecutive verified successes with zero rollbacks**. Any single failure **auto-demotes** it, and it is **revocable in one click**. It is a pre-authorisation, not autonomy.
- **Live Jira, local-first.** ACLs come from a live Jira client (**implemented and mock-verified, with a real 3-flip revocation-drift proof**) via polling + write-behind cache, with no webhooks and no venue-WiFi dependency. The console is a **server-rendered page with polling**. The whole demo runs in **airplane mode**.

---

## The models (all open-weight, all named)

| Role | Model | Licence |
|---|---|---|
| FAST | Qwen3.5-35B-A3B (`qwen3-5-35b-a3b`) | Apache-2.0 |
| SMART | DeepSeek-V4-Flash (`deepseek-v4-flash`) | MIT |
| HEAVY | DeepSeek-V4-Pro (`deepseek-v4-pro`) | MIT |
| EMBED | BGE-M3 (`text-embedding-bge-m3`) | MIT |

All four resolve to public Hugging Face weights; the startup guard verifies every id against a `huggingface.co` source (PASS, 3 Jul 2026). No closed model is anywhere in the loop, including the embedding model.

---

## Why it's real (measured, not asserted)

**Tests and determinism.** **161 tests passing** (119 core + 42 memory; no skips or xfails). The full **Fetch agent-rails** suite requires the optional `agents` extra (`uv pip install -e ".[dev,agents]"`); the deterministic core runs green on the base `.[dev]` install. **Canonical seed: `4207`**, so the demo replays identically.

**Permission-check performance (airplane-mode conformance bench, seed 4207):**
- **P99 `permitted()` = 0.445 µs** (P50 0.423 µs) over the synthetic 1,000-doc topology; end-to-end overhead P99 **0.0130 ms**.
- **False-negative (leak) rate: 0 / 5,219 deny-expected = 0.000%.** **False-positive rate: 0 / 4,781 allow-expected = 0.000%.**
- **Adversarial: 6/6 passed**: query inference, metadata bypass, timing attack, collection attack, prompt injection, derived-memory attack.
- Derived-memory correctness **3,000/3,000 = 100%**; audit coverage **300/300 = 100%** with the hash chain verified; the permission-check curve is flat (O(1)) across 1k / 5k / 25k / 100k.

**Extractor robustness (seed 4207), the eligibility-critical invariant:**
- **0 false-fast-paths / 100 mutations (0.00%).** A mutated incident never wrongly matches a precedent's fast-path.
- **25/25 red-herring decoys resisted (100%)**: 8 correct-match, 50 safe-degrade, 42 conservative-degrade, 0 false-fast-path.

**Live realism run (`make bench-uci`, UCI dataset #498):**
- Store size **24,918 records / 24,918 incidents**, across **70 real `assignment_group` ACL boundaries**.
- **FNR 0 / 7,529 deny-expected · FPR 0 / 2,471 allow-expected.**
- **P99 `permitted()` = 0.590 µs over the 25,000-record store.**

**Live ACL-drift proof (`make live-drift`, 3 flips):**
- **Time-to-consistency median 0.24 s** (threshold < 5 min): PASS.
- **Stale-allow fraction 0.000%** (threshold < 0.5%): PASS.
- *Scope note:* a **3-flip liveness proof of the revocation path** over a 2-issue Jira ("Rights Ops Only"). The live Jira client is **implemented and mock-verified with a real 3-flip revocation-drift proof**, not a claim proven against production Jira; TTC is client-measured.

**Corpus provenance.** In a real **24,918-incident** corpus, **94.4% of incidents are precedented**: an *existence* measurement (a documented fix-class already exists), **not a product-accuracy claim**.

**Offline-capable.** Embeddings are precomputed and committed; the standing-approval fast-path skips all model calls; the demo passes with WiFi off.

---

## Data provenance

The **systems are simulated; the content is real, licensed public data.**

- **UCI incident-management log (dataset #498)**, CC BY 4.0, 24,918 incidents / 141,712 raw events, 70 real `assignment_group` ACL boundaries.
- **Real published runbooks**, including the real **CrowdStrike remediation** guidance.
- **TVmaze / Freeview / CC0-Kaggle** broadcast metadata for MediaCo's catalogue.
- **TMDB and IMDb were rejected on licence grounds** and are not used.

---

## Team

Taha Khan · Mahmoud Khoder · Arham Shuaib · Ian Gitau

---

## Links

- **Repository:** https://github.com/TahaKhanM/AI-Agent-Hackathon
- **Pitch deck:** `docs/submission/precedent-deck.pdf` (in the repository)
- **Try the agents in ASI:One:** https://asi1.ai/invite?channelInviteKey=NmIsH5-DHQVhnf78uThoWX3fVkRXiSpGz78rMsPkoUQ
- **Agentverse profiles:** Watcher · Librarian · Operator (addresses and profile URLs above)
