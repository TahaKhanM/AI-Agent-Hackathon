# Industry Primer — Read Tonight (20 minutes)

> Distilled 3 July 2026 from `Research/` (README, 00-verified-claims, chapters 01–07) and `data/analysis/uci-baseline-results.md`. Every number carries its source, vintage and caveat label — quote them exactly as written here, including the labels. If a number isn't in this file, check `Research/00-verified-claims.md` before saying it on stage.

## The thesis in one paragraph

When enterprise software breaks, the fix is usually looked up in a manual and applied as admin/config work — not code. That observation (from the Disney+ internship) is the codified norm of the whole ITSM industry: ITIL literally mandates checking the Known Error Database first. The money leaks exactly there: repeat incidents dominate volume, every escalation multiplies ticket cost ~5x, and most of MTTR is finding-and-queueing, not fixing. A heavily funded "AI SRE" wave attacks the *engineering* half (logs, Kubernetes, code PRs) and almost all of it stops at diagnosis. Nobody combines: (a) grounding in the org's own documented fixes, (b) safe execution of admin/config remediation inside third-party business applications, (c) approval gates + audit + rollback as the core product, and (d) a memory that compounds — every executed fix becoming a reusable, provenance-carrying asset. Media/broadcast is the wedge: 24/7 contractual deadlines, Ofcom-regulated failure, legacy vendor consoles, and Netflix proving in-house that the pattern works without anyone productising it.

---

## 1. The ten numbers (say the label with the number)

1. **>60% of incidents at ServiceNow's own support org were repeats with known-but-uncapturable fixes.**
   Source: ServiceNow KCS case study (primary, vendor's own org). Adversarially verified 3–0. This is the single best citation for "most incidents have a pre-existing documented fix."

2. **$22 → $69 → $104: cost per ticket at L1 → desktop → L3.**
   Source: MetricNet's own "ROI of Service and Support" whitepaper (primary). **Vintage ~2019–2020 — quote it that way, NOT "2024"** (secondary blogs relabel it; the fake freshness is a trap). Companion: automated interactions cost $0.10–$3 (secondary, indicative only). Costs stack on escalation — an escalated ticket accrues L1 + L2 + L3.

3. **8.85 business hours: average incident MTTR.**
   Source: MetricNet/HDI (industry benchmark, historical). Label: **business** hours. For work that is often minutes of keystrokes once the fix is known. Never mix with our UCI 18.2h, which is **calendar** hours (see §4).

4. **85% of major human-error outages are procedure failures — the fix existed and wasn't followed correctly.**
   Source: Uptime Institute 2024 Resiliency Survey. This is the killer stat: the procedure existed; execution is the broken step.

5. **Cases with a KB article attached resolve 66% faster; KCS gave 52% faster time-to-relief.**
   Source: same ServiceNow KCS case study (primary, vendor's own org; 66% verified 2–1, 52% verified 3–0).

6. **$200M/year: average downtime cost per Global 2000 company.**
   Source: Oxford Economics / Splunk 2024, verified 3–0 — the most defensible big number. Do NOT say "$400B total" loosely: the exact framing is "$400B = 9% of profits *including hidden costs*". Splunk's 2026 refresh raises the headline to $600B — quote either only with its exact framing.

7. **Toil rose to 30% of SRE time in 2025 — the first rise in five years.**
   Source: Catchpoint SRE Report 2025 (primary, n=301). The report itself partly blames babysitting half-reliable AI — that's our verification/rollback argument, gift-wrapped.

8. **>40% of agentic AI projects will be cancelled by end-2027 for cost, unclear value, or inadequate risk controls.**
   Source: Gartner, June 2025 (poll of 3,412 orgs). Judges will know this one — pre-empt it: our approval-gate/audit/rollback design answers the three kill-reasons by construction.

9. **Only ~8% of leaders accept full agent autonomy; ~90% demand full audit logs of every agent action.**
   Source: 2025–26 surveys (CIO.com-reported survey for 8%; May 2026 US federal survey for ~90% logging / 79% human-in-the-loop). Label as "2025–26 industry surveys". Graduated autonomy is a purchase criterion, not a compromise.

10. **Netflix auto-remediates 56% of a whole failure class with zero humans (and cut associated compute cost ~50%).**
    Source: Netflix TechBlog (first-party, Pensive + LLM escalation). The pattern works at the richest operator in our wedge vertical; nobody sells it to everyone below Netflix scale.

---

## 2. The competitive map, in plain sentences

**AIOps platforms (BigPanda, Moogsoft→Dell, Dynatrace Davis, Splunk ITSI, IBM Cloud Pak).** They see everything and touch nothing: correlate alerts, point at probable root cause, then hand off to a human or to workflows the customer must pre-build. Moogsoft — the vendor that coined "AIOps" — exited to Dell for roughly what it raised: correlation alone didn't sustain a company.

**Runbook automation (PagerDuty/Rundeck, Ansible EDA, AWS SSM, StackStorm, Resolve.io).** Hands without a brain: real execution, but only of pre-scripted, human-authored jobs. Two decades of this stalled for documented reasons — brittle matchers, stale runbooks engineers learn to distrust, cascading machine-speed failures (Knight Capital 2012, AWS S3 2017, Facebook BGP 2021), no memory, and audit pain ("auditors do not love 'the system did it'"). Resolve.io is twenty years of proof that alert→runbook works and never generalised past hand-built content.

**The AI-SRE wave (Resolve AI, Traversal, Cleric, incident.io, Datadog Bits, PagerDuty SRE Agent, Azure SRE Agent — $340M+ raised since 2024, one $1B unicorn on ~$4M reported ARR).** They investigate autonomously and stop at "here's the likely cause" — or draft a code PR. Where execution exists it's Kubernetes-shaped (restart pod, roll back deploy). Azure SRE Agent is the reference architecture for the trust model (Review vs Autonomous modes, permission gate on every tool call, audit to the customer's own store) — steal that vocabulary — but it's Azure-resources-only and learns from its own runs, not the org's existing KB. All of them read telemetry; none of them reads the ops manual.

**RPA / hyperautomation (UiPath, Automation Anywhere + Aisera, Microsoft Copilot Studio computer-use, Blue Prism WorkHQ, Pega, Tines, Torq, Workato, n8n).** This category KILLS the naive whitespace sentence — never say "nobody executes in business apps." RPA has executed admin/config changes inside third-party apps, including green-screen legacy consoles, for a decade, and UiPath can be triggered by a ServiceNow "Incident Created" event today. The asterisk: **every remediation is a workflow someone pre-built.** The unit they ship is a workflow; ours is a remembered fix. Build-first economics only pays back on high-frequency processes — the documented-but-infrequent long tail (the Disney+ class) is structurally unautomatable in their model and free in ours.

**ServiceNow + Moveworks.** ServiceNow paid $2.85B (closed Dec 2025) for Moveworks — the strongest comp for "executing documented admin fixes is worth a lot." But the execution scope is employee-facing service-desk requests (passwords, access, provisioning) inside ServiceNow's own workflow universe, and ServiceNow monetises seats and tickets — deflection attacks its own licence base.

**The partial-execution honesty (Komodor Klaudia, Digitate Ignio — and Aisera).** Say this before a judge does: real autonomous remediation already exists in silos. Komodor's Klaudia (post-March-2026) genuinely executes and expanded beyond pure K8s troubleshooting — our earlier claims that it doesn't were refuted 0–3 in verification. Ignio has claimed closed-loop self-healing for years (setup-heavy). Aisera hits 64–84% auto-resolution (vendor-claimed) on the L1 *head* by catalog lookup. **The whitespace is the combination, not "nobody executes anything."**

## 3. The white-space sentence (memorise this wording)

> **No product closes the loop from incident → the org's own documented fix, retrieved at incident time → risk-classified, approval-gated execution in third-party business applications — without pre-building each remediation as a workflow — and none converts verified execution history into graduated, per-fix-class autonomy.**

Shorter, for the stage: *"RPA proved enterprises will let software act inside their business apps — but only for fixes someone spent weeks pre-building. We execute the fix your org already documented, retrieved at incident time, gated by approval, logged and reversible — and every execution makes the next one more autonomous. Nobody sells that loop."*

Three claims that survive adversarial Q&A: (1) **retrieval, not build** — competitors execute pre-authored workflows, nobody turns the KB article into a governed execution at incident time; (2) **the long tail, not the head** — thousands of fix classes too infrequent to repay a workflow build; (3) **the learning loop** — nobody stores executed fixes with outcome/approver/rollback metadata and promotes fix classes up an autonomy ladder.

## 4. The media-vertical wedge story

- **Origin:** the Disney+ observation — schedulers and ops teams fixing enterprise systems (Mediagenix WHATS'ON class) via documented admin actions. Phrase the Disney link as **first-hand internship experience corroborated by Disney's own job postings requiring WHATS'ON proficiency** — there is no vendor confirmation; don't name-drop it as fact.
- **The stack is a chain of legacy single-vendor systems** — rights (Rightsline) → scheduling (WHATS'ON: 180+ media groups incl. BBC, ITV, DAZN, vendor-confirmed) → traffic (WideOrbit ~70% US share under Constellation; MYDAS is **Cataneo's**, not MSA Focus — we corrected our own brief) → playout (Amagi, Grass Valley, Evertz). Most incidents are hand-off failures between these systems; most fixes are admin/config actions inside one of them.
- **Failure is regulated and contractual, not just embarrassing.** Red Bee Media 2021: fire-suppression discharge took out the London playout centre; Channel 4's subtitles were degraded ~8 weeks, ~500 Ofcom complaints, a formal licence-breach finding (Ofcom-documented — our UK opening story). CrowdStrike July 2024 took Sky News off air — and its fix was a documented, repetitive admin procedure executed thousands of times by hand. MGM admitted improperly licensing 244 titles during Starz exclusivity windows (~$70M in deals) — rights errors are board-level, silent failures.
- **Netflix proved the pattern in-house** (number 10 above, plus Data Canary metadata validation). Everyone below Netflix scale has the same failure classes and only runbooks + small teams. That asymmetry is the market.
- **Integration is feasible, not exotic:** WHATS'ON exposes documented REST/OpenAPI plus BXF playlist export/as-run import, and the qibb Node-RED connector ecosystem proves third-party read/write automation is permitted and practised — "we sit where qibb flows sit, and add reasoning, approval gates and audit." Everything else is the four-tier reality: REST where lucky, BXF/MOS file exchange, flat-file/FTP watch folders, middleware/RPA last.
- **First buyer is a playout MSP, not a broadcaster:** Red Bee, Encompass (1,200+ channels daily), Globecast, Amagi managed services (scale figures vendor-claimed). Fixed-price SLA contracts turn every automated incident into margin; one deal covers dozens of channels; their NOCs already maintain the runbook/ITSM knowledge base we need. Concede in the same breath: they may build in-house, and MSP procurement adds a second enterprise to every sale.
- **Co-opetition is real but siloed:** Mediagenix, Dalet, AWS all shipped agentic AI at NAB 2025/2026 — every one inside its own product. The cross-system incident→documented-fix→audited-remediation loop is unclaimed.

## 5. Our own measured numbers (UCI corpus — ours, computed, unattackable)

Source: UCI ML Repository #498 — the audit log of a **real ServiceNow instance**: 141,712 events / 24,918 incidents, measured by us 3 July 2026, reproducible via `data/analysis/uci_match_rate.py`. All durations are **calendar hours** (the log has no business-hours calendar) — label them, and never average with MetricNet's 8.85 *business*-hour MTTR; the two corroborate, they don't combine.

- **94.4% fix-class match rate**: "94% of 24,918 real incidents arrived when their exact fix class — same category, subcategory and resolution code — had already been resolved at least once before. The precedent existed; it just wasn't operational." **Caveat we volunteer:** the fix-class key includes `closed_code`, only known at resolution — so this is a claim about **precedent existence**, not what triage could match at arrival. The arrival-level number is the 98.6% symptom-class match. Say whichever fits the sentence; never swap them.
- **18.2 hours (calendar) median resolution for precedented repeats** — even with precedent, 36% breached SLA and 47% were reassigned at least once (first-of-class median: 92.1h). "Retrieval, not resolution, is the bottleneck."
- **59.4% top-1 / 87.7% top-3 arrival-time precision** — naive most-common-prior-fix baseline using only symptom fields available at arrival. Framing: "Before any product intelligence, the right fix is on the operator's first screen ~88% of the time — and the 59% top-1 is exactly why standing-approval execution requires extractor-confirmed fingerprint equality, never rank-1 similarity." This is a **floor** (naive frequency baseline, coarse public fields), not a product accuracy claim.
- **558 fix classes recur ≥4 times and cover 94.8% of volume** — the autonomy ladder isn't hypothetical; those are standing-approval candidates on day one.
- **Do NOT headline** the knowledge=true 74.6h vs 8.6h split — `knowledge` flags KB *usage*, harder incidents drive people to the KB (causal confound). Colour only: "incidents where staff had to reach for a knowledge document took a median of 74.6 hours — the lookup path is the slow path," and acknowledge the confound if probed.

## 6. Honest caveats we volunteer (before judges find them)

1. **No public statistic says "X% of incidents already have a documented fix."** We use the proxy chain (60% repeats at ServiceNow, 13.3% outright repeats, 20–50% password-class tickets, 85% procedure failures), our measured 94.4% precedent-existence rate, and we instrument the metric live in the demo.
2. **"Disney uses WHATS'ON" rests on job postings + first-hand internship**, not vendor confirmation. Phrase as experience, not fact.
3. **Vendor-claimed figures stay labelled**: Moveworks 50–88% deflection, incident.io 80% downtime cut, Mediagenix "80% faster channel launches," Traversal 85% MTTR, Aisera 64–84% auto-resolution, PagerDuty "99% faster," MSP scale figures (Red Bee/Encompass/Globecast/Amagi). Always say "vendor-claimed."
4. **The $22/$69/$104 ladder is ~2019–2020 vintage** (MetricNet primary) despite blogs relabelling it "2024." Quote the numbers, not the fake freshness.
5. **Komodor Klaudia and Digitate Ignio genuinely execute remediations in their silos** — our claim is the unclaimed *combination* (KB-retrieval + cross-system business-app execution + governance-as-product + compounding memory), never "nobody executes."
6. **The freshest alert-fatigue numbers (44% outages from ignored alerts; 78% no-alert incidents) come from NeuBird — an AI-SRE vendor's April 2026 survey.** Cite as "a 2026 industry survey (NeuBird)."
7. **Google's 50% toil ceiling is a "stated goal"** in the SRE book, not an enforced cap. Say "Google's stated goal."
8. **Our corpus numbers carry their own caveats** (closed_code / precedent-vs-arrival; calendar vs business hours; 59.4% is a naive floor; knowledge-flag confound) — §5 has the exact permitted framings.
9. **Cataneo MYDAS has no public API reference** — fall back to the four-tier integration pattern; and MYDAS is Cataneo's product, not MSA Focus's.
10. **WHATS'ON "dense UI" and "six-figure subscriptions" are downgraded to plausible-but-unverified** (single low-authority review). Say "enterprise-priced, multi-year rollouts, dedicated administrators" — all vendor-corroborated.
11. **Refuted claims we must never use:** any "Komodor doesn't execute / is K8s-only" wording; the bare "$400B downtime" figure without its exact "9% of profits incl. hidden costs" framing.

**Closing posture:** enterprises are not asking "can the agent fix it?" — they're asking "can I see, approve, audit and undo what it did?" Every conflict between ambition and the Conduct rubric or the demo resolves toward control and honesty. That's not hedging; per every 2025–26 survey, it's the purchase criterion.
