# Precedent — Scale Story & Full Q&A Bank (refinement round 2)

> Builder deliverable, 3 July 2026. Lane: the credible scale story Conduct's rubric demands, the merged Q&A bank covering every round-1 judge question plus the idea doc's existing rebuttals, and the traps-to-avoid list.
> Sources: [Idea-Development.md](../Idea-Development.md) §4, [Research ch. 04](../../Research/04-media-broadcast-ops-vertical.md) §6–7, [ch. 06](../../Research/06-gaps-differentiation-and-positioning.md), [ch. 07](../../Research/07-rpa-hyperautomation-competitors.md), [00-verified-claims.md](../../Research/00-verified-claims.md).
> Terminology note used throughout (per round-1 rulings): **L3 is called "Standing Approval (pre-approved standard change)"** — never "Autonomous" — and the incident-class key is the **deterministic fingerprint (service, error_code, target_object_type)**. Graduation rule quoted verbatim everywhere: *"L3 after 3 consecutive verified L2 successes with zero rollbacks; any verification failure or rollback demotes the class to L1; a human clicks Promote, a human can click Revoke."*

---

## PART 1 — THE CREDIBLE SCALE STORY

Conduct's brief, verbatim: *"You won't have a real enterprise system to test on, and that's fine. Show you've thought about how this holds up on something far bigger and messier."* This section is that answer, in four layers: (1) the integration reality, (2) the distribution multiplier, (3) how the policy engine and memory scale across orgs, (4) what breaks first at 10x/100x — with the measured artifact that proves we did the work.

### 1.1 The 30-second spoken version (for the deck's one scale slide)

> "MediaCo mirrors the real chain — and the real chain is messier than a REST API. Our own research says integration in this vertical is a four-tier stack: documented REST APIs where you're lucky, BXF file exchange where standards were adopted, FTP watch-folders as the ubiquitous glue, and screen-level automation as the explicit last resort. We built the Operator as a typed-tool adapter layer so a fix executes the same way at every tier — and where a system only accepts files, the agent *prepares and stages* the exact payload behind the same approval gate instead of pretending to click. To prove the memory scales, we ingested [N] real historical incidents from a public ServiceNow-derived event log and measured retrieval match-rate and permission-check P99 over the full corpus — the numbers are on this slide and in the repo."

Slide artifacts to show under it (owner: whoever lands the Kaggle ingest per Conduct fix #1/#5): **corpus size ingested (~141k events / ~25k incidents), retrieval match-rate %, permission-check P99 ms at that corpus size, and the four-tier adapter diagram.**

### 1.2 Layer 1 — the connector/integration strategy (grounded in ch. 04 §6)

**The four-tier integration pattern** (this is normal systems-integrator work in this vertical, not exotic research — [ch. 04 §6.4]):

| Tier | Surface | Real-world evidence | What the Operator does there |
|---|---|---|---|
| 1 | **Documented REST/JSON APIs** | Mediagenix WHATS'ON publishes REST/OpenAPI-documented, versioned APIs ([Mediagenix API docs](https://www.mediagenix.tv/help-and-documentation/api/)) | Typed tool calls, full execute + verify + rollback — the demo path |
| 2 | **Standards-based exchange (BXF/MOS)** | SMPTE ST 2021 (2008) carries schedules, as-run logs, content metadata; Mediagenix Linear ships "Standard BXF Playlist export & As Run import"; in practice often **file drops, not messaging** (Grass Valley STRATUS does traffic integration "via BXF files") | Generate the exact BXF payload, stage it behind the approval gate, verify via as-run import on the read path |
| 3 | **Flat files / FTP watch folders** | Still the ubiquitous glue between traffic, automation and archive tiers ([Grass Valley manual](https://wwwapps.grassvalley.com/manuals/gv_stratus_v6.10/core/x-cc/content/topic/atlas/segmentation/c_IntegrationWithTrafficAndPlayout.html)) | Prepare-and-stage: write the CSV/XML to the watch folder only after approval; verify by polling the response/log folder |
| 4 | **Middleware / RPA-on-console — explicit last resort** | qibb (Node-RED, Qvest spin-off) ships commercial CRUD connectors for WHATS'ON incl. scheduling/rights business logic, auth = host+username+password ([qibb docs](https://docs.qibb.com/platform/whatson)); Copilot Studio CUA-class executors are GA | Drive a certified middleware flow or a CUA-class executor as *one more typed tool* under the same policy engine — never free-form |

**The load-bearing sentence** (use verbatim in Q&A): *"Our agent sits architecturally exactly where a qibb flow sits — third parties are already permitted and practised at read/write automation on these systems; we add reasoning, risk classification, approval gates and audit on top."* qibb's existence (100+ media connectors, 800+ automated flows in production) is proof the write-surface is real, commercially tolerated, and credentialed like any service account.

**Why the connectors are NOT the moat — and why that's the right answer** (ch. 04 §6.4, ch. 07): adapters at all four tiers are standard SI work; the defensible IP is the layer above them — retrieval of the org's documented fix, deterministic risk-gating, and the executed-fix memory. This also converts the scariest competitors into roadmap: UiPath robots, Power Automate flows and Copilot computer-use agents become *pluggable executors* under our approval-and-memory layer (exactly how Aisera itself triggers UiPath/AA workflows).

**Why not RPA (the ch. 07 two-axis answer):** RPA proved enterprises will let software act inside their business apps — but only for fixes someone spent weeks pre-building, which is why it only pays back on high-frequency processes (UiPath built a whole Healing Agent product just to fight selector rot). Documented-but-infrequent known-error fixes — three occurrences a year each, thousands of classes per enterprise — are structurally unautomatable in the build-first model. Retrieval-grounded execution makes the marginal fix ~free: the KB article the org already wrote *is* the automation source.

### 1.3 Layer 2 — the MSP channel as the scale multiplier (ch. 04 §7)

One broadcaster buys Precedent to fix its incidents; a **playout/media-services MSP buys it once and applies it across dozens-to-hundreds of client channels** — and their fixed-price SLA contracts turn every automated incident directly into margin:

- **Red Bee Media** — ~2,500 staff, 2.7M+ hours of programming distributed/year, 500+ TV streams (and the operator at the centre of the 2021 Channel 4 subtitles incident we open the pitch with).
- **Encompass** — services 1,200+ channels daily from a 24/7 London NOC with guaranteed SLAs.
- **Globecast** — 150+ complex playout channels from six global media centres; already monetised ops automation (auto-QC "human by exception").
- **Amagi managed services** — 800+ playout chains, 5,000+ channel deliveries in 150+ countries, NOCs in India/UK/US, 127% net revenue retention (all vendor-claimed, 2026 — label them).

Why the MSP adopts: (1) SLA economics — automated remediation is pure margin; (2) one deployment covers many broadcasters; (3) **their NOCs already run runbook-driven, ITSM-tooled processes — the knowledge base Precedent needs already exists and is maintained**; (4) approval gates map onto their existing shift-lead sign-off culture. Honest counterweights to volunteer before a judge does: they may build in-house (Red Bee's ARC, Amagi's AI stack), and MSP procurement adds a second enterprise (the end-broadcaster's change control) to every sales cycle.

### 1.4 Layer 3 — how the policy engine and memory scale across orgs (the BasedAI tie-in)

This is where the Conduct scale story and the BasedAI memory-governance story are the *same* story — say that explicitly on the slide.

- **Policy engine scales because it is deterministic and corpus-size-independent.** Rules are YAML keyed on (system × action type × risk class × autonomy level) and the incident-class key is a deterministic fingerprint — evaluation cost does not grow with KB size or memory size. Per-tenant policy packs are just separate YAML trees; no LLM in any permission decision at any scale.
- **Memory is tenant-scoped by construction.** Every memory record carries the full **set** of source lineage constraints (the conjunction model: retrieval must satisfy ALL source constraints, not one strictest label), and tenant identity is simply the outermost constraint in that set. Cross-org leakage is therefore prevented by the same mechanism that prevents cross-team leakage inside one org — one enforcement path to test, not two. A **precompiled effective-policy bitmap per record** keeps the retrieval check a single indexed lookup, which is also why P99 stays flat as the corpus grows — the benchmark artifact demonstrates this.
- **Cross-tenant learning is an explicit, governed non-default.** Day one: no memory crosses a tenant boundary, full stop. The roadmap answer (only if asked): anonymised *fingerprint-class* statistics — "orgs like you resolve this error class at L2 with 98% success" — via the same governed-redaction flow (new object, explicit grants, redaction attestation, audit event) designed for the BasedAI track. Fix content never crosses; that's the customer-owned moat.
- **Revocation scales because it's lineage-indexed:** revoking one source article invalidates every derived record, summary and embedding entry via the lineage index in one pass — the same cascade whether the corpus is 10 records or 10 million.

### 1.5 Layer 4 — what breaks first at 10x / 100x, and the answer

Answer this before it's asked; it's the highest-signal scale slide content. Ordered by what actually breaks first:

1. **Retrieval precision breaks first** (at ~50k contradictory, stale, duplicated KB articles across Confluence/SharePoint/wikis). This is a *known* failure mode of naive RAG — practitioners complain vector search surfaces "outdated 2-year-old runbooks" because semantic similarity ≠ epistemic quality ([Dev|Journal, May 2026](https://earezki.com/ai-news/2026-05-17-the-runbook-is-already-lying-to-you/)). **Our answer is structural, not tuning:** the ranking unit is the *executed fix* with recency, success-rate, approver and rollback metadata — a fix verified in production last Tuesday outranks a stale article every time, and staleness gets flagged when execution verification contradicts the document. **The number, not the intuition:** retrieval match-rate and P99 measured over the full ~141k-event public incident ingest, on the slide and in the repo.
2. **ACL-sync concurrency breaks second.** Answer: version counters + idempotent upserts, a stated consistency window, a pytest harness firing simultaneous ACL updates and retrievals asserting no widened-access window, and **fail-closed** on any record whose ACL freshness is uncertain (incl. cached-Jira fallback mode). Stale cache never widens access.
3. **The human approval queue is the real ceiling — and that's the product working as designed.** L1/L2 throughput is bounded by approvers, which is why the ladder exists: the 60%+ repeat classes (ServiceNow's own number, verified 3–0) graduate to Standing Approval and leave the queue; humans concentrate on the novel tail. Autonomy is the *throughput* answer, earned per class — not a safety compromise.
4. **Fingerprint-class explosion at 100x** (too many distinct classes, each too rare to graduate). Answer: that long tail still gets L0/L1 value — diagnosis + retrieved fix + prepared plan is 80% of the 8.85-hour MTTR even when a human executes; and class keys are structured fields, so classes can be merged by policy, never by LLM judgement.
5. **Integration coverage at 100x** (tier-3/4 systems where "execute" means "stage a file"). Answer: the Operator degrades gracefully down the four tiers — execute → stage → prepare-checklist-and-verify — and every tier keeps the same gate, audit record and rollback-or-abort semantics. Verification is read-side (as-run logs, response folders) and reads are widely available even where writes aren't.

---

## PART 2 — THE FULL Q&A BANK

Every qa_question from all five round-1 judges, merged with the idea doc §4 rebuttals, deduplicated, grouped by theme. Answers are in the team's voice, sized for a 2-minute Q&A (15–25 seconds each). **Bold openers** are the first sentence to say out loud.

### A. Defensibility & market

**A1. "ServiceNow paid $2.85B for Moveworks and owns the ticket, the KEDB and the approval workflow. Why are you a company and not a feature they ship next quarter?"** *(Conduct #7, VC #3)*
**"They monetise the workflow; we delete it."** ServiceNow's core pricing is still seat- and ticket-based, and a product whose success metric is "tickets that never needed a fulfiller" attacks its own licence base — they're visibly hedging with hybrid pricing (The Register, Dec 2025). Second, execution surface: Now Assist recommends and acts inside ServiceNow's own workflow universe; nobody's agent executes admin fixes inside WHATS'ON, a rights DB, or an EPG publisher. And the precedent cuts our way: incumbents *acquire* this layer — Jeli for $29.7M, Moveworks for $2.85B — which is the comp, and honestly, one exit path.

**A2. "Conduct is sitting in this room, raised $60M to make legacy legible, and execution is their obvious next slide. Why are you the complement and not the feature?"** *(VC #2)*
**"Conduct makes legacy legible; we make legacy operable — same thesis, adjacent layer."** Their product reasons over code to explain systems; ours retrieves and executes the *organisation's documented operational fixes* with approval gates — different corpus (runbooks and executed fixes, not source code), different user (ops teams, not engineering), different risk machinery (SoD approvals, rollback, audit). If they ever build execution, they'll need exactly the permission-aware fix memory we're building — that's a partnership slide, not an extinction slide. SAP invested in Conduct rather than building the legibility layer itself; record-system incumbents outsource this layer, they don't build it.

**A3. "Your moat is memory that compounds — but it's empty at every new customer, and Atlassian owns the ticket history you'd learn from. Why doesn't the incumbent have your moat on day one?"** *(VC #4, idea doc cold-start rebuttal)*
**"The history isn't the moat — the executed-fix records are, and nobody has those because nobody executes."** Day one we ingest what already exists — years of tickets, KB articles, runbooks (in the demo: ~25k real incidents from a public ServiceNow-derived log) — and run at L0/L1; Meta got 42% root-cause hit-rate purely from historical investigations, so bootstrap works. Atlassian owns ticket *text*; the record that compounds is symptom → verified fix → approver → risk class → rollback → outcome, which only comes into existence when a fix is executed through us. KCS alone is worth 52% faster relief — and that's just the read side.

**A4. "Who signs the cheque, what's the ACV, and how long is the sales cycle at a broadcaster whose ops budget is shrinking?"** *(VC #6)*
**"First cheque: a playout MSP's COO, because every automated incident on a fixed-price SLA contract is pure margin."** Red Bee runs 2.7M+ hours/year with ~2,500 staff; Encompass services 1,200+ channels daily; one deployment covers dozens of broadcasters, and their NOCs already maintain the runbook corpus we need. Unit economics floor: every deflected escalation is a $22–$104 ticket cost avoided (MetricNet ladder, ~2019–20 vintage) before you count downtime at $4,537/minute (PagerDuty 2024); land read-only in one NOC (the Traversal/Cleric pattern), expand per channel — enterprise cycle, but SLA margin is the sharpest wedge in the vertical.

**A5. "$600 billion is the whole Global 2000's downtime bill. What's your actual serviceable market, bottoms-up?"** *(VC #8, idea doc $600B rebuttal)*
**"The headline sizes the pain; our unit economics don't depend on it."** Per company it's ~$200M/year (Oxford Economics/Splunk 2024, independently verified), and bottoms-up we price against the Tier-2/3 application-ops labour around record systems: repeat incidents are 60%+ of volume at ServiceNow's own support org, each escalation multiplies cost ~5x on the $22→$104 ladder, and Sequoia's services-to-software ratio is ~6:1 — we sell the work, not the seat. Beachhead maths: an MSP NOC running hundreds of channels handles tens of thousands of tickets a year; deflecting the repeat 60% at even $50 average is a seven-figure ACV justification per site.

**A6. "Why now?"** *(VC weakness #4 — must be volunteered in the close, not just answered)*
**"Retrieval-plus-safe-execution only became buildable this year, and the incumbents are priced to meter it, not ship it."** Every ops team drowning in runbooks has this loop — media is where we watched it first-hand. Netflix proved the pattern in-house (56% of a failure class auto-remediated, zero humans) and nobody productised it downstream; Gartner's 40%-cancellation prediction is about missing risk controls, and our risk controls are the product.

**A7. "Founder-market fit is one internship's observation. Who here has carried a pager, and who's going full-time after Saturday?"** *(VC #5)*
**"The internship found the problem; the industry's own literature confirmed it's the codified norm."** One of us watched the loop daily inside Disney+ operations, and ITIL formally mandates it — check the Known Error Database, apply the documented workaround. [Fill in before Saturday: names/roles of whoever has ops/on-call experience, the 3–5 practitioner conversations from the VC judge's ask, and an honest one-liner on post-hackathon intent — this answer cannot be written by a document, only rehearsed by the team.]

**A8. "Why media first?"** *(idea doc rebuttal — keep)*
**"First-hand pain, regulated failure, and an in-house proof nobody productised."** Ofcom found Channel 4 in breach of its licence over an 8-week subtitles outage whose recovery was manual, knowledge-scarce ops; CrowdStrike took Sky News off air and the fix was a documented admin procedure executed thousands of times by hand; Netflix auto-remediates 56% of a failure class internally. 24/7 contractual deadlines, legacy consoles, small expert teams — beachhead, not ceiling.

### B. Safety, trust & the autonomy ladder

**B1. "You wrote 'L3 executes instantly.' I published 'a fully autonomous agent is a non-starter.' Who granted L3, where is that logged, who can revoke it, and what stops autonomy drift?"** *(Conduct #3, Technical #8)*
**"Nothing here is autonomous — L3 is a Standing Approval, and a named human granted it on screen."** The rule is printed in the product: a class becomes eligible after 3 consecutive verified L2 successes with zero rollbacks; the operations lead clicks *Promote to standing approval* — that click is an audit event with their identity — and a one-click *Revoke* sits next to it. Any verification failure or rollback automatically demotes the class to L1 and writes a demotion event. Approval moved earlier in time; it never left the loop — and drift is answered by the demotion rule plus the fact that the class key is a deterministic fingerprint, so a "quietly changed system" produces different error codes and drops out of the class.

**B2. "N successes graduates a class — who chose N, and can an attacker graduate a class by filing N synthetic easy tickets?"** *(Technical #8)*
**"N=3 is a policy value in YAML, per-class, chosen by the customer — and tickets don't graduate anything; verified executions do."** Graduation counts only executions that passed post-fix verification against the target system's actual state, initiated from an authenticated incident source, with the requester ≠ approver SoD control on every L2 run. An attacker who can fabricate real verified fixes in your production systems already has more access than our agent does — and the promotion itself still requires the human click (B1).

**B3. "Your Librarian retrieves a semantically similar but WRONG runbook — stale, superseded — and the Assessor classifies it low-risk. What stops execution, and how would you even know?"** *(Conduct Q&A #2, idea-doc gap)*
**"Three independent stops, none of them the LLM's judgement."** First, ranking: executed-fix records with recency and success-rate metadata outrank raw documents — a superseded procedure loses to the fix that verifiably worked last week. Second, the gate: risk class comes from the deterministic policy engine keyed on the action's fingerprint, not from the document, and anything not exactly matching a graduated class runs at L1 with plan + rollback in front of a human. Third, verification: post-fix checks compare actual system state to the expected outcome; a wrong fix fails verification, fires the pre-generated rollback, demotes the class, and flags the source document as suspect in memory — which is how we'd know.

**B4. "The fix executes, the verifier passes, but the fix was wrong — who catches a false-positive verification?"** *(Technical #2)*
**"The same people who catch it today — except now there's a complete provenance trail."** Verification is deterministic per fix class (publish state green, rights window matches contract, EPG rendered), so a false-positive means the *check* was mis-specified; when the downstream symptom surfaces, the audit record shows exactly what was changed, by which rule, from which source, with before/after state — and the correction both rolls back and rewrites the verification spec for that class. Compare the status quo: a human makes the same wrong fix and the knowledge of it lives in nobody's memory at all.

**B5. "Walk me through the rollback for incident 1 byte by byte — what pre-state is captured, where is it stored, and what if the rollback write itself fails?"** *(Technical #3)*
**"Rollback is generated before execution and is a precondition of the gate — no rollback plan, no execution."** For a metadata fix: the Operator reads the target object, snapshots the full pre-state JSON into the audit store (append-only, hash-chained), computes the inverse write, and only then requests the gate. If verification fails, the inverse write fires automatically; if the rollback write itself fails, the system does the one safe thing left — freezes the class to L0, pages a human with the stored pre-state and a prepared manual restore, and logs the double-failure as its own audit event. Reversible where possible, loudly stuck where not — never silently wrong.

**B6. "Autonomous agents are dangerous — remember Replit deleting a prod DB."** *(idea doc rebuttal — keep, sharpened)*
**"Exactly — that story is why our architecture looks the way it does."** Replit's agent had free-form access and no gate; ours has deterministic typed tools only (no shell, no free-form console), a policy engine with no LLM in any permission decision, SoD approval (requester ≠ approver, immutably logged), and rollback generated *before* execution. Gartner's >40%-cancellation prediction is about *missing* risk controls — ours are the product, and only ~8% of leaders accept full autonomy anyway, which is why we sell a ladder, not a switch.

**B7. "The agent re-applies a remembered fix and it's wrong for the new context — rights window breached, content pulled. Who's liable, when the customer is Ofcom-regulated?"** *(VC #7)*
**"The same liability model as every change-management tool: the authorising principal is a human, on the record."** At L0–L2 a named person approved the specific change; at Standing Approval a named ops lead pre-approved the class, exactly like an ITIL standard change today — our audit trail (input, reasoning, action, policy rule, approver, before/after state) is *better* evidence for an Ofcom investigation than the status quo, where the same wrong fix gets made by a tired human at 2am with no record. Contractually we ship shadow-mode-first deployment and per-class risk caps; and note rights-class incidents are exactly what the demo shows Precedent *refusing* to touch autonomously.

**B8. "Your accuracy numbers?"** *(idea doc rebuttal — keep verbatim discipline)*
**"We quote verified per-incident execution success and rollback rates from the demo environment — never model benchmarks."** The incident.io-vs-Rootly credibility war is the cautionary tale: controlled LLM benchmarks are not production precision. Our headline metric is instrumented live in the console: % of incidents matched to a documented fix, executions verified, rollbacks fired.

### C. Technical robustness & the demo's honesty

**C1. "Every incident came from a generator you wrote. If I file a ticket right now — vague symptoms, wrong terminology, a typo in the error code — what happens, live?"** *(Conduct #1, Technical #4)*
**"Please do — that's the beat we rehearsed."** The Watcher triages from structured fields first and LLM reading second; the fingerprint requires exact structured-field equality, so a typo'd error code can't silently match a graduated class — best case it resolves to a candidate match that runs at L1 with a human reading the plan; low-confidence classification degrades to L0/Escalate with an investigation dossier, and the reasoning trace shows the whole decision. Our generator also mutates incident text (typos, colloquial symptoms, red herrings) precisely so triage-of-mess is the tested path, not the exception. [Build dependency: the messy-input mutation + live-ticket rehearsal from Conduct fixes #2 — this answer must be true by Saturday.]

**C2. "Your policy engine is deterministic, but the class label that unlocks L3 comes from LLM triage — hasn't the model authorised itself one hop upstream?"** *(Technical #1)*
**"No — the class key is computed, not inferred."** The fingerprint is (service, error_code, target_object_type) from structured incident fields; the LLM may *propose* candidate matches, but a match only counts on fingerprint equality, and anything short of that runs at L1+ with a human gate. The rule sits printed on the audit-log screen. The model narrates; it never authorises.

**C3. "The 15-second Standing Approval fix: how much is LLM inference, and what did you cache to make it repeatable on stage?"** *(Technical #6)*
**"Almost none of it is inference — that's the point of a remembered fix."** When the fingerprint exactly matches a graduated memory record, we skip LLM triage entirely: retrieve, gate-check, execute, verify are all deterministic; at most one short LLM call writes the human-readable summary, with a 5s timeout and a canned fallback. Embeddings are precomputed at build time; Jira writes are async write-behind. The second time is fast *because* it's memory, not generation — that's the architecture, not a stage trick.

**C4. "What happens between an admin revoking a KB article's permissions and your sync job running — can the Librarian still retrieve the derived record?"** *(Technical #5 — see also D-track F3 for the TOCTOU form)*
**"The window exists, we bound it, and we fail closed at its edges."** Webhook-triggered sync applies revocations in seconds with version counters and idempotent upserts; every retrieval checks the record's effective-policy entry at query time, so once the sync lands, derived records and their embeddings are dead in the same pass. If ACL freshness is uncertain — Jira unreachable, cache stale — retrieval fails closed on the affected records. We state the consistency window in the README rather than pretending it's zero.

**C5. "Which model is in the loop?"** *(Technical #7, BasedAI #5)*
**"Open-weight end-to-end, declared in the README."** Generation and classification run on Venice-served open-weight models (Llama 3.3 / Qwen family), and the memory index uses an open-weight embedder (BGE/nomic-class), all pinned in a single model-config module so it's auditable in one file. Nothing proprietary touches the pipeline — a BasedAI hard rule we're proud to over-comply with, since the doctrine is the same as our policy engine's: nothing closed, nothing unauditable, in the decision path. [Build dependency: the open-weight default swap — flagged fatal by two judges; must land Friday.]

**C6. "Your KB has 10 articles. A real broadcaster has 50,000 — contradictory, stale, duplicated. What breaks first: retrieval precision, the risk classifier, or the ACL sync? Show me the number."** *(Conduct #4)*
**"Retrieval precision breaks first — so we measured it."** [Numbers from the 141k-event ingest go here: match-rate %, P99 ms.] The structural answer is that we don't rank by semantic similarity alone: executed-fix records carry recency, success-rate and provenance, so the verified-last-Tuesday fix beats the stale 2-year-old article — the known rot mode of naive RAG. The risk classifier doesn't degrade with corpus size at all (deterministic YAML on fingerprints), and ACL sync scales as an indexed effective-policy lookup — which the same benchmark demonstrates.

### D. Scale & integration (the "you built the thing you're fixing" cluster)

**D1. "Your only real integration is Jira — everything else is a simulator you wrote. What does it cost to connect a real WhatsOn or SAP console, and why aren't you a bespoke-connector services business?"** *(VC #1)*
**"We own it: MediaCo mirrors the real chain, and the agents touch it only through the surfaces the real vendors expose."** WHATS'ON publishes documented REST/OpenAPI, and a commercial Node-RED ecosystem (qibb) already ships third-party CRUD connectors for it — our agent sits exactly where a qibb flow sits; the rest of the chain is BXF and file drops, which is adapter work every systems integrator in this vertical does routinely. The connectors are deliberately not the moat — the retrieval, gating and executed-fix memory above them are; that's also why the MSP channel matters: one integration effort at Red Bee or Encompass covers dozens of client channels.

**D2. "Your own research says WHATS'ON is the lucky case and the rest is BXF file drops, FTP folders and screen-scraping. What fraction of your documented fixes are executable at all through tier-3/4 surfaces, and what does the Operator do there?"** *(Conduct #5)*
**"The fix classes we target first concentrate on tier-1/2 surfaces — and below that the Operator degrades from 'execute' to 'prepare and stage', never to pretending."** Metadata, EPG and rights-window fixes live where REST and BXF live; on tier-3 the Operator generates the exact file payload and stages it in the watch folder *behind the same approval gate*, verifying via the as-run/response path — reads are widely available even where writes aren't. On tier-4 it drives certified middleware or a CUA-class executor as one more typed tool, and where even that's absent, an L0 prepared-checklist with verification is still most of the 8.85-hour win. Honest number: we haven't measured the executable fraction across a real estate yet — it's deployment-specific — but every tier keeps the same gate, audit and rollback-or-abort semantics, so coverage grows without the safety story changing.

**D3. "The 8.85-hour MTTR is mostly queueing and approval latency. Your L1/L2 tiers still wait for a human. So what did you actually compress — and by how much, measured?"** *(Conduct #6)*
**"We compress three of the four segments immediately, and the ladder deletes the fourth over time."** Diagnosis, lookup and context assembly (~20% of service-desk agent time is literally searching for the right resolution) collapse from hours to seconds — the console shows time-to-plan-ready live; execution and verification after approval collapse from console-clicking sessions to one gated action. The approval wait itself shrinks from "a CAB ticket in a queue" to "a one-click card with evidence and rollback attached" — and, decisively, the 60%+ repeat classes graduate to Standing Approval and exit the queue entirely. Measured in the demo: 60s at L1, 15s at Standing Approval, against the 8.85-hour baseline bar drawn on the same screen.

**D4. "Isn't this UiPath/RPA?"** *(idea doc rebuttal — keep, ch. 07 wording)*
**"RPA executes what a developer pre-built weeks earlier; we retrieve and execute what your org already documented, at incident time."** UiPath's ServiceNow trigger starts a specific pre-developed job, and its Healing Agent heals selectors, not incidents; the build-first economics is exactly why the long tail of documented, infrequent known-error fixes was never automated. Our unit isn't a workflow — it's a remembered fix; the marginal fix costs nothing to 'author' because the KB article is the source, and every execution upgrades the class's autonomy. Nobody in the RPA/hyperautomation table ships that loop.

### E. Fetch.ai track

**E1. "You pitch five agents. How many are on Agentverse, and can you show me a message exchanged between two of them over the Chat Protocol right now?"**
**"Three — Watcher, Librarian and Operator are registered Agentverse agents passing uAgents messages; here are the addresses and profiles."** The Assessor and Auditor run in-process by design: they're the deterministic policy and audit components, and we keep permission decisions out of network hops on principle. [Build dependency: the 3-agent split from the Fetch judge's ask — register tonight, capture profile URLs and a live message exchange screenshot for backup.]

**E2. "Close your console. Resolve an incident for me end-to-end inside ASI:One — what do I see at each turn?"**
**"One conversation: you report 'our EPG publish failed', the agent replies with triage, the retrieved documented fix, risk class and rollback plan as one formatted message; you type 'approve'; it executes, the real Jira ticket transitions and closes, and the agent returns the audit-trail and ticket links."** The Standing Approval repeat runs in the same session in ~15 seconds. The public shared-chat URL of exactly this flow is in the submission — the primary workflow needs no custom frontend.

**E3. "If ASI:One doesn't route my query to your agent — which happens — what's your fallback, and did you test discoverability from a fresh account?"**
**"Tested from a fresh ASI:One session before submitting, with the Innovation Lab badge and a keyword-rich agent description; and the fallback is direct agent-address chat, which we'll demo on the spot."** We also captured the public shared-chat URL from a successful run the night we froze the build, so the deliverable never depends on live routing luck.

**E4. "Your approval gate is a SOX SoD control, but in an ASI:One chat the approver is an anonymous session. Who is the authorising principal in your audit log when I type 'approve'?"**
**"The Chat Protocol sender address — recorded verbatim as the authorising principal in the five-element audit record."** The control structure is identical to production: requester (agent) ≠ approver (chat principal), immutably logged; in an enterprise deployment that address maps to SSO identity. The mechanism that matters — a distinct, logged principal who is not the agent — is fully present in the chat path.

**E5. "The chat session drops between the agent proposing the fix and the human approving — does the pending execution leak, expire, or re-prompt?"**
**"It expires, closed."** A proposed plan is a pending approval object with a TTL; no approval message, no execution — ever — and on session re-establishment the agent re-presents the plan rather than resuming silently. A dropped session can only ever produce a non-action, which is the correct failure direction for an execution gate.

**E6. "What does Fetch.ai technology actually do in your architecture that FastAPI wasn't already doing?"**
**"It's the agent transport and the front door: discovery, identity and the conversational approval surface."** Watcher, Librarian and Operator communicate over uAgents messaging, the Watcher is discoverable and usable from ASI:One without any custom frontend, and the chat sender address is load-bearing — it's the authorising principal in our audit log (E4). Agentverse isn't a checkbox; it's where the human-in-the-loop actually lives in the conversational path.

**E7. "Will your agent still respond on Agentverse next Wednesday, and what does it do for a user who isn't running your MediaCo simulator?"**
**"Yes — the Watcher is a hosted/mailbox agent that stays live after submission, and the README says so."** Without MediaCo credentials it still does the general-purpose half: triage a described incident, retrieve against the public runbook corpus we ingested, and return a risk-classified fix plan with an explicit 'no execution target configured' state — L0 behaviour, honestly labelled.

### F. BasedAI track

**F1. "A fix record derived from a rights-restricted KB article and a scheduling-project ticket — does a rights-ops principal WITHOUT scheduling-project access retrieve it? Defend against the multi-source case."**
**"No — and that's the design, not an accident."** Every derived record stores the full *set* of source lineage constraints, and retrieval requires satisfying **all** of them — conjunction, not a single strictest label, precisely because strictest-label collapses in the non-hierarchical multi-source case you're describing. The fast path is a precompiled effective-policy bitmap per record, compiled at write/sync time, so the check stays one indexed lookup; a weaker derivative for broader access exists only via the governed redaction flow (F9).

**F2. "You revoke the source KB article. What physically happens to the embedding vectors derived from it — filtered, quarantined, or deleted?"**
**"Quarantined immediately, via the lineage index — and we show it live."** The sync event flips the effective-policy entry for every derived record, summary and embedding-index entry in one pass; they're excluded at query time from that moment (deny events logged), and a background job hard-deletes quarantined vectors so nothing recoverable persists. The demo/video segment: flip the ACL in Jira, watch the previously-retrievable fix and its embeddings go dark within seconds, with the denial audit event on screen.

**F3. "Your permission check passes, then the record is fetched 40ms later. Where is your TOCTOU boundary?"**
**"Check and fetch are one operation — the ACL filter is a predicate inside the retrieval query, not a preceding step."** There is no separate 'then fetch': the query returns only rows whose effective-policy entry passes at execution time, under the same snapshot. The residual window is sync lag from Jira (seconds, versioned), which we state as the consistency window — and within any uncertainty, affected records fail closed.

**F4. "Jira is unreachable and the cache is 10 minutes stale — does memory retrieval fail open or fail closed? Point me at the line."**
**"Closed — and it's one explicit line in the retrieval path."** Every record's effective-policy entry carries a freshness version; in fallback mode, any record whose ACL version can't be confirmed within the stated window is excluded and a degraded-mode audit event is written. A stale cache that widens access is a leak by construction, so the fallback exists for stage safety on *reads we're sure of*, never for permission optimism.

**F5. "Name every model in the loop — generation, classification-at-write-time, AND the embedding model."** → merged with **C5**: Venice-served open-weight generation (Llama 3.3 / Qwen), open-weight embedder (BGE/nomic-class), all declared in the README, enforced via one model-config module.

**F6. "Your P99: over how many records, how many principals/ACL tags, at what concurrent query rate? Sub-200ms over 30 rows is not a claim."**
**"Agreed — which is why the benchmark corpus is seeded, not the demo rows."** Methodology committed to the repo: 5–10k ACL-tagged memory records across 3+ team boundaries and several dozen principals, measured under concurrent retrievals, with the concurrency harness also firing simultaneous ACL updates to assert no widened-access window. [Numbers go here once the script runs — the mechanism that keeps P99 flat is the precompiled bitmap: the check is one indexed lookup regardless of corpus size.]

**F7. "Incident 3 shows the agent knows a restricted fix EXISTS. Isn't that leaked metadata across the boundary?"**
**"Yes — it's a deliberate, policy-controlled disclosure, and we say so."** The record's routing metadata (a fix class exists; owner: Rights Ops) is classified separately from its content, because operationally you *want* the scheduling identity to escalate to the right team rather than reinvent a restricted procedure; a stricter tenant can set full-deny, where the Librarian returns nothing and routing happens on risk class alone. Query-time inference prevention beyond that is one of our stated non-claims — we'd rather declare the boundary than pretend it isn't there.

**F8. "An agent read a restricted record yesterday at L2 and its output comment sits on a public Jira ticket. Does lineage governance extend to agent-authored artifacts?"**
**"Yes in design, stubbed in the build: agent outputs are derived artifacts and inherit the source constraint set."** The Auditor checks the constraint set against the destination's audience before posting — a comment derived from restricted memory posts to a restricted ticket in full, and to a broader-audience ticket only as a redacted stub ('resolution details restricted to Rights Ops', with a link that enforces ACL). We demo the retrieval boundary; the write-side inheritance is documented as the designed flow with the schema already carrying it.

**F9. "Who holds the redact/declassify capability, and can an agent ever request one?"**
**"A named human role — the data steward/ops lead — holds it; agents can request, never grant."** The designed flow (stubbed per the track's C-model): a declassified derivative is a *new* governed object with explicit grants, a redaction attestation, source hashes and a lineage record, approved by a principal holding the redact capability, with the approval and attestation logged as audit events. The doctrine is the same one running our execution gate: the model never authorises itself — not for actions, not for declassification.

**F10. "Your own document lists this track as 'first on the cut-line'. Why should I rank a hedge above teams that built their whole submission for this brief?"**
**"That document is stale — the memory layer got promoted, and the repo shows it."** Permission-aware memory is now a standalone module with its own README section, its own tests, its own benchmark; Precedent imports it. And we'd argue the embedding beats the purpose-built demo: our lineage governance runs inside a working multi-agent system executing real fixes against live Jira ACLs — the memory isn't a subsystem of the product; it's the reason an enterprise lets the product in the door. [Requires the cut-line reorder + repo restructure from the BasedAI judge's fixes — flag if not landed.]

---

## PART 3 — TRAPS TO AVOID ON STAGE

Rehearse these as hard NOs. Each one is a word or number that converts a winnable Q&A into a lost one.

1. **Never say "autonomous" about L3.** The word is *Standing Approval — a pre-approved standard change*. Conduct's rubric says "a fully autonomous agent is a non-starter" verbatim; the substance complies, so don't let the vocabulary disqualify it. Banned phrasings: "resolves autonomously", "no human needed", "full autonomy". Approved line: *"No one approved this ticket — because the operations lead pre-approved this fix class after watching it succeed. Approval moved earlier in time; it never left the loop."*
2. **Never say "nobody executes in third-party business apps."** Falsified by UiPath/RPA/Komodor/Ignio (ch. 07 §6.2). The surviving sentence is *retrieval-not-build*: "nobody retrieves the org's documented fix at incident time and turns it into a governed execution — without pre-building each remediation as a workflow."
3. **Never quote a vendor stat without labelling it.** Moveworks 50–88% deflection, Aisera 64–84%, PagerDuty "99% faster", Mediagenix "80% faster channel launches", Traversal >90%, Amagi/Red Bee/Encompass scale figures, Cato "40% autonomous" (a *projection*) — all vendor-claimed; say "vendor-claimed" out loud or don't use them. NeuBird's alert-fatigue numbers: cite as "a 2026 industry survey (NeuBird)" — a sharp judge knows they're a vendor.
4. **Never assert "Disney runs WHATS'ON."** The evidence is Disney job postings + the internship, not vendor confirmation. Locked framing: the first-hand Disney+ operations observation — which is the stronger evidence anyway. Same discipline: don't quote "six-figure WHATS'ON subscriptions" or "dense UI" (single low-authority source); say "enterprise-priced, multi-year rollouts, dedicated administrators" (all vendor-corroborated).
5. **Never quote an LLM benchmark as an accuracy claim.** The incident.io-vs-Rootly spat is the cautionary tale judges may know. Only ever: verified execution success and rollback counts from the instrumented demo environment.
6. **Never present the $600B without its framing.** Locked stat, so pair it in the same breath with the verified retreat position: "about $200 million per Global 2000 company per year (Oxford Economics/Splunk 2024, independently verified)". And never say "$400B" — that phrasing was refuted in verification.
7. **Never claim the demo data is real if the Kaggle/public-runbook ingest didn't land** — and never fail to claim it if it did. One provenance line on a slide and in the README: what's real (incident history, runbooks, programme metadata, live Jira), what's simulated (the MediaCo service shells). Conduct's brief demands realistic data; unlabelled invented data is a direct rubric violation, and labelled real data is a scoring weapon.
8. **Never say "the LLM decides" anywhere near permissions, risk, or graduation.** The doctrine sentence, worth repeating on stage: *"There is no LLM call in any permission decision — the model proposes, deterministic policy disposes."* Also never let "the class label comes from triage" slip — the class key is a computed fingerprint (C2).
9. **Never claim hardened guarantees we explicitly non-claimed.** Concurrent ACL-sync at enterprise scale and query-time inference prevention are stated non-claims with designed boundaries (fail-closed, consistency window). Volunteering the boundary earns trust; getting caught overclaiming it loses the BasedAI track outright.
10. **Never freelance the MetricNet vintage.** $22/$69/$104 is ~2019–2020 (primary source traced); don't relabel it "2024" the way secondary blogs do.
11. **Never let the 15 seconds be dead air or magic.** Narrate what it is while the trace scrolls: deterministic fingerprint match → gate check → execute → verify — "no generation, just memory." If anything on stage stalls, the line is "this is the cached fallback — the recorded live-Jira run is in the video," never an apology.
12. **Never end without the ask.** The close is written (design-partner intros + programme applications + Moveworks comp as the last thing they hear) — the one unforgivable VC-judge failure is the literal placeholder "Ask."

---

## Appendix — build dependencies this document assumes (cross-lane)

These answers are written to be TRUE on Saturday only if the following round-1 fixes land; if any slips, the corresponding answer must be softened before rehearsal:

| Answer(s) | Depends on | Round-1 source |
|---|---|---|
| C1 (messy ticket live) | Input-mutation in generator + live-ticket rehearsal | Conduct fix #2 |
| C6, D-slide numbers, F6 | Kaggle 141k-event ingest + P99/match-rate benchmark + 5–10k ACL-seeded corpus | Conduct fixes #1/#5, BasedAI ask #3 |
| B1 (Promote/Revoke on screen) | L3 rename + Promote-to-standing-approval UI + Revoke button | Conduct fix #3 |
| C5/F5 (open-weight) | Venice open-weight default + model-config module + README declaration | BasedAI/Technical fatal fixes |
| E1–E7 | 3-agent Agentverse split, ASI:One scripted session + shared URL, hosted Watcher | Fetch asks #1–#6 |
| F2 (live revocation) | ACL-flip → sync → denial demo segment | BasedAI ask #2 |
| F10 | Memory layer as standalone module + cut-line reorder | BasedAI weakness #7 |
| B3/B4 (rollback demo) | Failure-recovery beat (verification fail → rollback → demotion) | Conduct ask #3, Technical fix #4 |
