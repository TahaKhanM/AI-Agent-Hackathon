# Precedent — Spoken Q&A Bank (Demo Day, Sat 4 Jul)

> **How to use this file.** Every answer is sized for **15–25 spoken seconds** (~40–65 words at stage pace): say the **bold opener** first, then the 2–3 sentences. Numbers are pre-armed — say them exactly as printed; anything not in here or on appendix slide A1 does not get quoted. Long-form versions with full sourcing live in `docs/idea/refinement/05-scale-story-and-qa.md` — this file is the spoken layer; where an answer was cut for time, the depth is in 05 and the appendix slides, and Q&A can jump there.
> **Answer ownership (per 03 logistics — map to real people at stand-up; never printed here):** one person owns *numbers* (appendix A1, printed sheet in pocket), one owns *tech* (A3/A4/A6 + this file's B/C/F sections), one owns *market* (A5/A8 + section A here). **Never two people answering one question.**
> **The two lines that must survive any answer:** *"the second time is free"* and *"it knows what it's not allowed to touch."*

---

## 1. THE FIVE HARDEST QUESTIONS (recorded verbatim from the 3 Jul judging sessions — rehearse these first)

### 1.1 Conduct — *"Your 94% match rate uses the resolution code, which you only know after the fix. What does triage achieve at ARRIVAL time, measured?"*

**"We measured exactly that — three honest numbers."** The 94.4% measures precedent *existence* — the fix that eventually resolved the incident had been applied before. At arrival time, on symptom fields alone: the symptom class had precedent **98.6%** of the time, and a naive most-common-prior-fix baseline ranks the true fix **top-1 59.4%, top-3 87.7%** — over 24,470 evaluable incidents, script committed. That's the retrieval floor before any product intelligence: the right fix is on the operator's first screen nine times in ten. And that 59% top-1 is precisely *why* standing-approval execution requires extractor-confirmed fingerprint equality, never rank-1 similarity — nothing executes on a guess.

### 1.2 Technical — *"What's your MEASURED confident-but-wrong normalisation rate on mutated tickets?"*

**"Measured — a 100-ticket mutation bench ran against the frozen extractor, and the numbers sit on the triage trace itself."** ‹X› correct-match, ‹Y› safe-degrade, **‹Z› false fast-paths** — and the design target for that last number is zero, because the failure modes are asymmetric: a missed match costs a human sixty seconds at L1; a false fast-path would be a safety failure. So the extractor only confirms codes in its known dictionary, and anything it can't confirm is hard-capped at L0/L1. *(FILL ‹X›/‹Y›/‹Z› from the 100-mutation run at Fri 18:30 — the chip numbers must exist before the 20:00 run-through. If the run slips, the honest line is: "the bench is in the repo and runs in minutes — the architecture caps unconfirmed extractions at L1 regardless.")*

### 1.3 BasedAI — *"What is your measured FNR, and which of the six named attacks did you run?"*

**"FNR ‹X›% over 10,000 ground-truth queries — labelled by an independent oracle, not by the engine under test — and we ran all six named attacks."** Ground truth comes from a separate naive lineage-conjunction walk, so FNR is bitmap-versus-oracle disagreement, never the exam grading itself; with 3,000+ deny-expected queries, FNR below 0.1% is statistically claimable. The six attacks are in `tests/test_adversarial.py` under your own names: query inference, metadata bypass, timing, collection, prompt injection, derived-memory. And the drift and time-to-consistency numbers are anchored to Jira's own audit-records API — the ACL source's regulator-grade clock, not ours: a live permission flip goes dark in **≤8 seconds worst case**, enforced twice — Jira itself 404s the runbook in ≤5 s, our derived memory dies within one poll tick, two audit logs timestamp-matched. *(FILL FNR/FPR/P50/P99 from `bench/RESULTS.md`, committed before the 21:00 freeze.)*

### 1.4 Fetch.ai — *"Fresh ASI:One session, day-old agent — route my query without an address. Is direct-address really 'discoverable'?"*

**"Honest answer: day-old discoverability isn't force-able, so we engineered around it — and we don't claim what we haven't seen."** We registered in hour one Friday with both Innovation Lab badges and keyword-rich descriptions, ran the ten-plus interactions the discoverability evaluation requires, and re-tested from a fresh session this morning. If routing misses right now, direct-address chat works on the spot — and no, we don't call that "discoverable"; we call it the fallback, and the README says which one you're seeing. The public shared-chat URL captured against the frozen build means the deliverable never depended on routing luck.

### 1.5 VC — *"Who's full-time Monday, and what has an actual buyer said?"* — **HUMAN-ONLY. A document cannot write this. Fill and rehearse aloud Friday evening.**

Template — each clause must be true or deleted:

> **"‹Name/role› is on this full-time from Monday** — ‹one honest sentence: e.g. "notice handed in" / "full-time on acceptance to Antler or EWOR — we're applying with exactly this" / "nights-and-weekends until the first design partner signs"›. On buyers: we put it in front of **‹N› ops practitioners this week** — ‹strongest one-line quote, verbatim, attributed by role not name› — and the honest status is **design-partner conversations, not signatures**. That's what the two intros are for."

Rules: if outreach didn't land, the middle sentence becomes *"no buyer has seen it yet — that's exactly what the two intros are for"* and you move straight to the ask. Never fake intent; never let this question find two teammates with different answers — agree the sentences at Friday 19:00, out loud, twice.

---

## 2. THE FULL BANK (every 05 Part 2 answer, tightened to spoken length)

### A. Defensibility & market

**A1. ServiceNow owns the ticket, the KEDB and the workflow — why aren't you a feature?**
**"They monetise the workflow; we delete it."** ServiceNow's pricing is seat- and ticket-based — a product whose success metric is "tickets nobody touched" attacks their own licence base, and they're visibly hedging with hybrid pricing. Nobody's agent executes admin fixes inside WHATS'ON or a rights DB. And incumbents *acquire* this layer: Jeli $29.7M, Moveworks **$2.85B** — that's the comp, and honestly, one exit path.

**A2. Conduct raised $60M to make legacy legible — why are you the complement, not the feature?**
**"Conduct makes legacy legible; we make legacy operable — same thesis, adjacent layer."** Different corpus — runbooks and executed fixes, not source code; different user — ops, not engineering; different risk machinery — approvals, rollback, audit. If they ever build execution they'll need exactly the permission-aware fix memory we're building — that's a partnership slide. SAP invested in Conduct rather than building it; incumbents outsource this layer.

**A3. Your memory moat is empty at every new customer — why doesn't Atlassian have it on day one?**
**"The history isn't the moat — the executed-fix records are, and nobody has those because nobody executes."** Day one we ingest what already exists — here, ~25k real incidents — and run at L0/L1; Meta got a 42% root-cause hit-rate from historical investigations alone. Atlassian owns ticket *text*; the compounding record — symptom, verified fix, approver, rollback, outcome — only exists once a fix executes through us.

**A4. Who signs the cheque, what's the ACV, how long is the cycle?**
**"First cheque: a playout MSP's COO — every automated incident on a fixed-price SLA contract is pure margin."** Red Bee runs 2.7M+ hours a year with ~2,500 staff; Encompass services 1,200+ channels daily — one deployment covers dozens of broadcasters, and their NOCs already maintain the runbooks we need. Floor: every deflected escalation is a $22–$104 ticket avoided before downtime at $4,537 a minute. Land read-only in one NOC, expand per channel.

**A5. $600B is the whole Global 2000 — what's your serviceable market, bottoms-up?**
**"The headline sizes the pain; our unit economics don't depend on it."** Per company it's ~$200M a year — Oxford Economics/Splunk 2024, independently verified. Bottoms-up: repeats are 60%+ of volume at ServiceNow's own desk, and one MSP NOC handles tens of thousands of tickets a year — deflect the repeat 60% at a $50 blended value and that's a seven-figure ACV justification per site. *(Arithmetic on appendix A9.)*

**A6. Why now?**
**"Retrieval-plus-safe-execution only became buildable this year — and the incumbents are priced to meter it, not ship it."** Netflix proved the pattern in-house — 56% of a failure class auto-remediated, zero humans — and nobody productised it downstream. Gartner's 40%-cancellation prediction is about *missing* risk controls; our risk controls are the product.

**A7. Founder-market fit is one internship — who's carried a pager, who's full-time?** — **HUMAN-ONLY.**
Documented first sentence: **"The internship found the problem; the industry's own literature confirmed it's the codified norm"** — one of us watched the loop daily inside Disney+ operations, and ITIL formally mandates it: check the Known Error Database, apply the documented workaround. Then → the §1.5 template, verbatim as agreed Friday evening.

**A8. Why media first?**
**"First-hand pain, regulated failure, and an in-house proof nobody productised."** Ofcom found Channel 4 in breach over an eight-week subtitles outage whose recovery was manual, knowledge-scarce ops; CrowdStrike took Sky News off air and the fix was a documented admin procedure executed thousands of times by hand; Netflix auto-remediates 56% of a class internally. 24/7 deadlines, legacy consoles, small expert teams — beachhead, not ceiling.

### B. Safety, trust & the autonomy ladder

**B1. Who granted L3, where's it logged, who revokes, what stops drift?**
**"Nothing here is autonomous — L3 is a Standing Approval, and a named human granted it on screen."** The rule is printed in the product: three consecutive verified L2 successes, zero rollbacks; the ops lead clicks *Promote* — an audit event with their identity — and *Revoke* sits beside it. Any verification failure or rollback auto-demotes the class and logs it. Approval moved earlier in time; it never left the loop.

**B2. Who chose N=3 — can I graduate a class with synthetic tickets?**
**"N=3 is a policy value in YAML, per class, chosen by the customer — and tickets don't graduate anything; verified executions do."** Only executions that passed post-fix verification against real system state, from authenticated sources, on distinct target objects, with requester ≠ approver on every run. An attacker who can fabricate verified fixes in your production systems already has more access than our agent does — and promotion still needs the human click.

**B3. The Librarian retrieves a stale, wrong runbook — what stops execution?**
**"Three independent stops, none of them the LLM's judgement."** Ranking: executed-fix records with recency and success-rate metadata outrank raw documents — last Tuesday's verified fix beats the superseded procedure. The gate: risk class comes from deterministic policy on the fingerprint, not the document — anything short of an exact graduated match runs at L1 in front of a human. Verification: a wrong fix fails post-checks, fires the pre-generated rollback, demotes the class, and flags the source — which is how we'd know.

**B4. Fix executes, verifier passes, fix was wrong — who catches it?**
**"The same people who catch it today — except now there's a complete provenance trail."** A false pass means the *check* was mis-specified; when the symptom surfaces, the audit record shows exactly what changed, by which rule, with before/after state — and the correction both rolls back and rewrites that class's verification spec. Compare the status quo: the same wrong fix, made by a human, living in nobody's memory at all.

**B5. Walk me through the rollback byte by byte — and if the rollback write fails?**
**"Rollback is generated before execution and is a precondition of the gate — no rollback plan, no execution."** The Operator snapshots the full pre-state JSON into the append-only, hash-chained audit store, computes the inverse write, then requests the gate. Verification fails → the inverse fires automatically. If the rollback write itself fails, the class freezes to L0 and a human is paged with the stored pre-state and a prepared manual restore. Loudly stuck, never silently wrong.

**B6. Autonomous agents are dangerous — remember Replit deleting a prod DB.**
**"Exactly — that story is why our architecture looks the way it does."** Replit's agent had free-form access and no gate; ours has typed tools only — no shell — no LLM in any permission decision, requester ≠ approver immutably logged, and rollback written *before* execution. Only ~8% of leaders accept full autonomy anyway — that's why we sell a ladder, not a switch.

**B7. A remembered fix breaches a rights window at an Ofcom-regulated customer — who's liable?**
**"The same liability model as every change-management tool: the authorising principal is a human, on the record."** At L0–L2 a named person approved that specific change; at Standing Approval a named ops lead pre-approved the class — an ITIL standard change. Our audit trail is *better* Ofcom evidence than a tired human at 2am with no record. And rights incidents are exactly what the demo shows Precedent *refusing* to touch.

**B8. Your accuracy numbers?**
**"We quote verified per-incident execution success and rollback rates from the demo environment — never model benchmarks."** The incident.io-versus-Rootly credibility war is the cautionary tale: controlled LLM benchmarks are not production precision. Our headline metric is instrumented live in the console: incidents matched to a documented fix, executions verified, rollbacks fired.

### C. Technical robustness & the demo's honesty

**C1. Every incident came from your generator. I file a vague, typo'd ticket right now — what happens?**
**"Please do — that's the beat we rehearsed."** Triage reads structured fields first, LLM second; the fingerprint requires exact field equality, so a typo'd error code can't silently match a graduated class — best case it's a candidate match running at L1 with a human reading the plan; low confidence degrades to L0 with an investigation dossier. Our generator mutates ticket text every run precisely so triage-of-mess is the tested path.

**C2. The class label that unlocks L3 comes from LLM triage — hasn't the model authorised itself upstream?**
**"No — the class key is computed, not inferred."** The fingerprint is service, error code, target-object type, from structured fields; the LLM may *propose* candidates, but a match only counts on deterministic-extractor equality, and anything short runs at L1-plus behind a human gate. The model narrates; it never authorises.

**C3. The 15-second fix — how much is inference, what did you cache?**
**"Almost none of it is inference — that's the point of a remembered fix."** An exact fingerprint match skips LLM triage entirely: retrieve, gate-check, execute, verify are all deterministic; at most one short summary call with a five-second timeout and a canned fallback. Embeddings are precomputed at build time; Jira writes are async. The second time is fast *because* it's memory, not generation.

**C4. Between an admin revoking a KB article and your sync running — can the Librarian still retrieve it?**
**"The window exists, we bound it, we measured it, and we fail closed at its edges."** A 2–3-second versioned poll applies revocations; every retrieval checks the record's effective policy at query time. Measured: Jira's own propagation ≤5 s plus our ≤3 s tick — **flip to dark in ≤8 seconds worst case**, timestamp-anchored to Jira's own audit log. If freshness is uncertain, affected records are simply not served.

**C5 (+F5). Which models are in the loop — including the embedder?**
**"Open-weight end-to-end, declared in the README — and verified against the live catalog with the evidence committed."** Triage on Qwen3.5-35B-A3B, Apache-2.0; synthesis and dossiers on DeepSeek-V4-Flash and Pro, MIT; the memory index on BGE-M3, MIT — all Venice-served, weights checked file-by-file on Hugging Face, pinned in one module, with the `/models` dumps in `docs/compliance/`. Nothing closed touches the pipeline.

**C6. Your KB has 10 articles; a real broadcaster has 50,000. What breaks first? Show me the number.**
**"Retrieval precision breaks first — so we measured it: over 24,918 real incidents, 94.4% arrived with their exact fix class already precedented, and those repeats still took a median 18.2 hours to resolve by hand."** *(Calendar hours; script committed.)* And we don't rank by similarity alone — executed fixes carry recency and success-rate, so the verified-last-Tuesday fix beats the stale article. The risk classifier is corpus-size-independent, and the permission check is one indexed lookup — the P99 bench shows both.

**C7. The 94% uses the resolution code — what can triage match at arrival time?**
→ **§1.1, verbatim.** (59.4% top-1 / 87.7% top-3 / 98.6% symptom-level, 24,470 incidents.)

### D. Scale & integration

**D1. Your only real integration is Jira — everything else is a simulator you wrote.**
**"We own it: MediaCo mirrors the real chain, and the agents touch it only through the surfaces the real vendors expose."** WHATS'ON publishes documented REST, and a commercial connector ecosystem — qibb — already ships third-party CRUD flows for it; our agent sits exactly where a qibb flow sits. The connectors are deliberately not the moat — the retrieval, gating and executed-fix memory above them are; and one MSP integration covers dozens of client channels.

**D2. Your own research says most of the chain is BXF drops, FTP folders, screen-scraping. What fraction of fixes is executable at all?**
**"Our first fix classes concentrate on the REST and BXF tiers — and below that the Operator degrades from execute to prepare-and-stage, never to pretending."** On file-drop systems it generates the exact payload and stages it behind the same approval gate, verifying via the as-run path — reads exist even where writes don't. Honest number: the executable fraction is deployment-specific and unmeasured — but every tier keeps the same gate, audit and rollback semantics, so coverage grows without the safety story changing.

**D3. The 8.85 hours is mostly queueing. What did you actually compress, measured?**
**"We compress three of the four segments immediately, and the ladder deletes the fourth over time."** Diagnosis, lookup, context assembly — about 20% of agent time is literally searching — collapse to seconds; execution and verification become one gated action; the approval wait shrinks from a CAB queue to a one-click card — and the 60%+ repeat classes graduate out of the queue entirely. On screen: 60 seconds at L1, 15 at Standing Approval, against the 8.85-hour bar.

**D4. Isn't this UiPath / RPA?**
**"RPA executes what a developer pre-built weeks earlier; we retrieve and execute what your org already documented, at incident time."** UiPath's Healing Agent heals selectors, not incidents — build-first economics is exactly why the long tail of documented, infrequent fixes was never automated. Our unit is a remembered fix: the KB article is the source, the marginal fix costs nothing to author, and every execution upgrades the class.

### E. Fetch.ai track

**E1. How many agents are actually on Agentverse — show me a Chat Protocol message.**
**"Three — Watcher, Librarian and Operator are registered Agentverse agents passing uAgents messages — and every ASI:One reply carries the hop trail in its footer: the three addresses with millisecond timings, verifiable in the shared chat."** The Assessor and Auditor run in-process by design — we keep permission decisions out of network hops on principle. **⚠️ If cut-line #3 fired:** *"Two — the gateway and the executor; retrieval runs in-process next to the permission kernel, deliberately."* **Never say three if two are registered.**

**E2. Close your console — resolve an incident inside ASI:One.**
**"One conversation: you report the failure; the agent replies with triage, the documented fix, risk class and rollback in a single message; you type 'approve'; it executes and the real Jira ticket closes, with audit and ticket links returned."** The Standing Approval repeat runs in the same session in about 15 seconds. The public shared-chat URL of exactly this flow is in the submission.

**E3. ASI:One doesn't route to your agent — fallback? Did you test from a fresh account?**
→ **§1.4, verbatim.** (Hour-one registration, 10+ interactions, fresh-session re-test, direct-address as the *named* fallback, shared-chat URL insurance.)

**E4. In an ASI:One chat the approver is an anonymous session — who's the authorising principal?**
**"The Chat Protocol sender address — recorded verbatim as the authorising principal in the audit record."** Requester — the agent — is never the approver — the chat principal — and it's immutably logged; in an enterprise that address maps to SSO identity. The mechanism that matters — a distinct, logged principal who is not the agent — is fully present in the chat path.

**E5. Session drops between proposal and approval — does the pending execution leak?**
**"It expires, closed."** A proposed plan is a pending approval object with a ten-minute TTL; no approval message, no execution — ever — and on reconnect the agent re-presents the plan rather than resuming silently. A dropped session can only produce a non-action, which is the correct failure direction for an execution gate.

**E6. What does Fetch tech do that FastAPI wasn't already doing?**
**"It's the agent transport and the front door: discovery, identity, and the conversational approval surface."** The three agents communicate over uAgents messaging; the Watcher is usable from ASI:One with no custom frontend; and the chat sender address is load-bearing — it's the authorising principal in our audit log. Agentverse isn't a checkbox; it's where the human-in-the-loop actually lives.

**E6b. Where's the monetization? The bonus list names the Payment Protocol.**
**"Designed, not wired — deliberately."** The metered unit is the escalation dossier: triage, retrieval and standing-approval runs are the free loop; the heavy-model investigation dossier is the billable artifact, and the Payment Protocol — FET or Skyfire — is exactly the rail we'd meter it on; the README describes the model. We spent those hours on reliability and live Jira instead — a payment demo that wobbles on venue Wi-Fi costs more than the bonus earns.

**E7. Will your agent still respond next Wednesday — and what does it do without your simulator?**
**"Yes — the Watcher is a hosted agent that stays live after submission, and the README says so."** Without MediaCo credentials it does the general-purpose half: triage a described incident, retrieve against the public runbook corpus, and return a risk-classified fix plan with an explicit "no execution target configured" state — L0 behaviour, honestly labelled.

### F. BasedAI track

**F1. A record derived from a rights-restricted article AND a scheduling ticket — can a rights-ops principal without scheduling access read it?**
**"No — and that's the design, not an accident."** Every derived record stores the full *set* of source lineage constraints, and retrieval must satisfy **all** of them — conjunction, not a single strictest label, which collapses in exactly the multi-source case you're describing. The fast path is a precompiled effective-policy bitmap, one indexed lookup; a broader-access derivative exists only through the governed redaction flow. *(Attribution if asked: the A/B/C semantics come from the public track-Discord thread — ours is the implementation: the bitmap compiler, live-Jira sync, fail-closed cache, and the working product around it. Never say the sponsor "endorsed our design.")*

**F2. You revoke the source article — what physically happens to the derived embedding vectors?**
**"Quarantined immediately, via the lineage index — and we show it live, with Jira enforcing the same flip on its side."** One sync pass kills the effective policy on every derived record, summary and embedding entry — excluded at query time from that moment, hard-deleted in the background. On screen: set the issue's security level in Jira — **Jira itself 404s the runbook within ~5 seconds, real enforcement — and our derived memory goes dark within one poll tick.** Two layers, two audit logs, timestamps matched.

**F3. Permission check passes, record fetched 40ms later — where's your TOCTOU boundary?**
**"Check and fetch are one operation — the ACL filter is a predicate inside the retrieval query, not a preceding step."** One transaction; the fetched row's policy version is compared to the checked one, mismatch means recheck. The residual window is sync lag from Jira — seconds, versioned, stated as the consistency window — and inside any uncertainty, records fail closed.

**F4. Jira unreachable, cache 10 minutes stale — fail open or closed? Point me at the line.**
**"Closed — and it's one explicit line in the retrieval path."** Every record's effective-policy entry carries a freshness version; in fallback mode, any restricted record that can't be confirmed within the stated window is excluded, and a degraded-mode audit event is written. A stale cache that widens access is a leak by construction — the fallback exists for reads we're sure of, never for permission optimism.

**F5. Name every model — including the embedder.** → **C5.**

**F6. Your P99 — over how many records, how many principals, what query rate? Sub-200ms over 30 rows is not a claim.**
**"Agreed — which is why the benchmark runs your exact published protocol and reports in your own metric names."** Five hierarchy levels, twenty roles, a thousand ACL-tagged docs, ten thousand ground-truth queries — labels from an independent oracle — plus the realism run over the 25k-record real-incident store with forty principals under concurrent retrieval: FNR, FPR, P50/P99, end-to-end overhead, drift, time-to-consistency, each versus its published threshold, pass/fail. Three-thousand-plus deny-expected queries make FNR under 0.1% statistically claimable. *(Numbers: `bench/RESULTS.md`, committed pre-freeze.)*

**F7. Incident 3 shows the agent knows a restricted fix EXISTS — leaked metadata?**
**"Yes — it's a deliberate, policy-controlled disclosure, and we say so."** Routing metadata — a fix class exists, owner Rights Ops — is classified separately from content, because operationally you want the incident escalated to the right team, not the restricted procedure reinvented. A stricter tenant sets full-deny and routing happens on risk class alone. Inference prevention beyond that is a stated non-claim — we'd rather declare the boundary than pretend it isn't there.

**F8. An agent read a restricted record; its comment sits on a public ticket — does lineage cover agent outputs?**
**"Yes in design, stubbed in the build: agent outputs are derived artifacts and inherit the source constraint set."** The Auditor checks the constraints against the destination's audience — full detail posts to a restricted ticket; a broader ticket gets only a redacted stub with an ACL-enforcing link. We demo the retrieval boundary; the write-side inheritance is documented, with the schema already carrying it.

**F9. Who holds redact/declassify — can an agent request one?**
**"A named human role holds it — the data steward — and agents can request, never grant."** A declassified derivative is a *new* governed object: explicit grants, a redaction attestation, source hashes, a lineage record, approved by a redact-capability holder, all logged. Same doctrine as our execution gate: the model never authorises itself — not for actions, not for declassification.

**F10. Your own document called this track "first on the cut-line" — why rank a hedge over purpose-built entries?**
**"That document is stale — the memory layer got promoted, and the repo shows it."** It's a standalone module with its own tests and a benchmark reported against your published framework: FNR, FPR, P50/P99, time-to-consistency, six named attacks. And the embedding is the argument: our lineage governance runs inside a working multi-agent system executing real fixes against live Jira ACLs over 25,000 real incidents — the memory isn't a subsystem; it's the reason an enterprise lets the product in the door. *(If BioVault is named: acknowledge a strong governance demo, then differentiate on the live ACL source, the real corpus, and the framework-metric numbers. Never disparage.)*

---

## 3. JUDGE-SPECIFIC PROBE MAPS

### 3.1 Conduct's CTO-type judges — what the rubric makes them ask (rubric weights 35/30/20/20; provenance is the 27 Jun Discord announcement export, **never cite "the bounty page"** — the live page shows no criteria)

Their published words, and where our answer lives:

| Rubric-verbatim probe | Our answer |
|---|---|
| *"work with realistic data rather than something you made up"* | Provenance slide A2 + C6: 141k-event UCI log, real runbooks with `adapted_from` URLs, TVmaze/XMLTV — and the TMDB/IMDb licence *rejections* as the diligence beat |
| The 35% demo criterion: not *"only a scripted demo"*, *"recovers from errors"* | C1 + the live recovery beat (verification fail → auto-rollback → demotion) + the judge-files-a-ticket party trick — offer it before they ask |
| *"a fully autonomous agent is a non-starter"* | B1 — Standing Approval vocabulary, Promote/Revoke on screen. This is a skim-level disqualifier; the wording IS the answer |
| *"You won't have a real enterprise system… show how this holds up on something far bigger and messier"* | C6 what-breaks-first ordering with the measured numbers; D2 four-tier degradation; §1.1 arrival-time honesty |
| *"start with the process"* | A2 — "Conduct makes legacy legible; we make legacy operable" |

CTO instincts beyond the rubric: they decompose the MTTR claim (D3), ask where the human is at each ladder step (B1/B2), and probe the simulator (D1). The pattern in every winning answer: **a measured number plus a mechanism, never an adjective.**

### 3.2 VC judges — LocalGlobe / Antler / EWOR patterns

- **LocalGlobe (seed fund):** market bottoms-up (A5 → appendix A9 arithmetic), who signs and how long (A4), why-not-incumbent (A1/A2/A3), why now (A6), liability in a regulated vertical (B7). They respect a sourced retreat position more than a big number — lead with the $200M/company framing, not $600B alone.
- **Antler / EWOR (founder programmes):** these judges buy *founders*, not decks — expect §1.5 (full-time Monday), A7 (who's carried a pager), and "what would you do with 90 days in our programme?" The ask on slide 12 names them — so have one sentence ready: what the first design-partner sprint looks like. **All human-only; agree the sentences Friday 19:00.**
- **Universal VC probes:** "what has a buyer said" (only the truthful outreach line — or the honest "that's what the intros are for"), "what's defensible in 18 months" (A3 — executed-fix records + tenure-compounding accuracy), "what's the wedge" (A4 — SLA margin at MSPs).
- Discipline: numbers-owner fields anything with a figure in it; never two voices on one question; close every market answer toward the ask.

### 3.3 Sponsor engineers — what they verify with their own hands

- **Fetch.ai engineers** will *click*: Agentverse profile URLs, both README badges, the shared-chat URL — and jump to the turn where the 15-second standing-approval run happens. Rehearsed: E1 (agent count — with the two-agent contingency line), E4 (sender address as principal), E5 (session-drop expiry), E7 (hosted persistence — true only because the Watcher deploys Friday night), E6b (Payment Protocol: designed, not wired). The hop-trail footer is the proof artifact — point at it, don't describe it.
- **BasedAI engineers** know their published thresholds by heart — FNR <0.1% ("critical failure"), FPR <2%, P50 <50ms, P99 <200ms, overhead <100ms, correctness >99%, drift <0.5%, TTC <5min, 100% audit coverage. Answer in their vocabulary (F6), name the six attacks unprompted, volunteer the independent-oracle construction (§1.3) — the oracle question is *their* recorded hardest. Offer the dual-enforcement Jira story (F2) as the thing a synthetic standalone cannot show. Attribution discipline per F1.
- **Venice / "sponsor tech 20%" probe** (the suggested BasedAI rubric scores "Use of BasedAI/sponsor tech"): pre-armed line — *"The entire runtime is Venice-served open-weight inference — Venice is the track's gold sponsor — and the README carries a BasedAPIs portability note: the memory library's model calls go through one registry module, so repointing is a config change, not a rewrite."* If asked why those models: pinned IDs with public HF weights, verified file-by-file, dumps committed — offer `precedent/models.py` and `docs/compliance/` on screen.

---

## 4. TRAPS — one line each (rehearse as hard NOs; full text in 05 Part 3)

1. **Never say "autonomous" about L3** — it is *"Standing Approval — a pre-approved standard change"*; the saving line is *"approval moved earlier in time; it never left the loop."*
2. **Never say "nobody executes in third-party apps"** — say *"nobody retrieves the org's documented fix at incident time and turns it into governed execution, without pre-building each remediation as a workflow."*
3. **Never quote a vendor stat without saying "vendor-claimed" out loud** (Moveworks, Aisera, PagerDuty, Mediagenix, Amagi/Red Bee/Encompass, Cato).
4. **Never assert "Disney runs WHATS'ON"** — the locked framing is *"watched inside Disney+ operations."*
5. **Never quote an LLM benchmark as an accuracy claim** — only verified execution-success and rollback counts from the instrumented demo.
6. **Never say $600B without "~$200M per Global 2000 company (Oxford Economics/Splunk 2024)" in the same breath** — and never say "$400B."
7. **Never claim the data is real if the ingest didn't land — and never fail to claim it if it did**; one provenance line, slide and README.
8. **Never say "the LLM decides" near permissions, risk, or graduation** — *"the model proposes, deterministic policy disposes"*; the class key is a computed fingerprint.
9. **Never claim the non-claims** (enterprise-scale ACL concurrency, query-time inference prevention) — volunteer the fail-closed boundary instead.
10. **Never freshen the MetricNet vintage** — $22/$69/$104 is ~2019–2020, say so.
11. **Never let the 15 seconds be dead air or magic** — narrate *"fingerprint match → gate → execute → verify: no generation, just memory"*; if anything stalls: *"this is the cached fallback — the recorded live-Jira run is in the video."* Never apologise.
12. **Never end without the ask** — two intros + Antler/EWOR + the Moveworks $2.85B close is the last thing they hear.

**Added after the session-2 verification pass (same discipline):**
13. **Never say "P99 over 141k events"** — the bench store is the 25k-record corpus; captions must match `bench/RESULTS.md` exactly.
14. **Never blend the 18.2 *calendar*-hour median with the 8.85 *business*-hour MetricNet MTTR** — different clocks, label both.
15. **Never say the sponsor "endorsed our design"** — credit the public Discord thread for the A/B/C semantics; claim the implementation.
16. **Never say "three agents" if two are registered** (and if cut-line #3 fired, sweep "three" from deck A7, video captions and README before the freeze).
