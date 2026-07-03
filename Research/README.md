# Industry Research — AI Agent for Enterprise Incident Remediation

> Compiled 2 July 2026 for the UK AI Agent Hackathon EP5 × Conduct (submission deadline 4 July 2026, 23:59).
> Produced by a multi-agent research pipeline: 6 specialist web-research agents (10–18 searches each) + a deep-research harness that adversarially verified 25 headline claims (3 refutation votes each) + a completeness critic + a completion pass (chapter-04 deep dive, primary-source tracing of 15 aggregator-cited stats, re-verification of 9 interrupted claims). Cross-chapter inconsistencies flagged by the critic have been fixed.

## The one-paragraph takeaway

The Disney+ observation — *when enterprise software breaks, the fix is looked up in a manual and applied as admin/config work, not code* — is the **codified norm of the entire ITSM industry** (ITIL literally mandates checking the Known Error Database first), and it is where the money leaks: repeat incidents are 60%+ of support volume, every escalation multiplies ticket cost ~5x ($22 → $104+), and diagnosis-plus-queueing (not fixing) consumes most of the average 8.85-hour MTTR. A crowded, heavily-funded wave of "AI SRE" startups ($340M+ since 2024, one $1B unicorn) attacks the *engineering* half of this problem — logs, metrics, Kubernetes, code fixes — and almost all of them stop at diagnosis. **Nobody combines: (a) grounding in the org's existing documented fixes, (b) safe execution of admin/config remediation inside third-party business applications, (c) approval gates + audit + rollback as the core product, and (d) a memory that compounds — every executed fix becoming a reusable, provenance-carrying asset.** That is the white space, and the media/broadcast vertical (where the observation came from) is an unusually good wedge: 24/7 contractual deadlines, Ofcom-regulated failure, legacy vendor consoles, and in-house proof at Netflix that the pattern works (56% of a failure class auto-remediated) without anyone having productised it.

## Reading order

| File | What's inside | Read it for |
|---|---|---|
| [00-verified-claims.md](00-verified-claims.md) | 21 adversarially-verified claims (with caveats) + 4 refuted | Slide-safe numbers |
| [01-incident-resolution-status-quo.md](01-incident-resolution-status-quo.md) | Support tiers, ticket economics, ITIL/KEDB/KCS, runbook rot, standard changes, the P3/P4 long tail | The problem, in the industry's own language |
| [02-aiops-and-automation-incumbents.md](02-aiops-and-automation-incumbents.md) | AIOps platforms, runbook automation, ServiceNow/Moveworks/Azure SRE Agent, why scripted auto-remediation stalled, market sizes | "Why hasn't ServiceNow done this?" |
| [03-agentic-sre-startup-wave.md](03-agentic-sre-startup-wave.md) | 15+ startup profiles with funding, comparison table, converged trust playbook, white-space verification | Competitive slide + trust design to copy |
| [04-media-broadcast-ops-vertical.md](04-media-broadcast-ops-vertical.md) | WHATS'ON, MYDAS (Cataneo), traffic/MAM/playout chain, Red Bee/Channel 4, MGM-Starz rights breach, Netflix's in-house auto-remediation, vendor co-opetition; §6–7: integration surfaces (APIs/BXF/qibb), operator roles, managed-services channel (Red Bee, Encompass, Globecast, Amagi) as first buyer | The wedge story + demo scenario material + integration-feasibility Q&A |
| [05-quantified-pain-and-trust-requirements.md](05-quantified-pain-and-trust-requirements.md) | Downtime/MTTR/toil/alert-fatigue numbers with source quality flags; ITIL standard changes, SOX SoD, SOC 2 five-element log, EU AI Act dates, autonomy surveys | Every number for the deck + the compliance-as-feature argument |
| [06-gaps-differentiation-and-positioning.md](06-gaps-differentiation-and-positioning.md) | Lifecycle coverage map, operational-memory prior art (RCACopilot, Meta, Moveworks), service-as-software framing, pitch one-liners, risk register with rebuttals | Positioning + judge Q&A prep |
| [07-rpa-hyperautomation-competitors.md](07-rpa-hyperautomation-competitors.md) | UiPath agentic automation, Automation Anywhere+Aisera, Copilot Studio computer-use, Blue Prism WorkHQ, Tines/Torq/n8n/Workato, Resolve.io, Atomicwork | Surviving the "isn't this just RPA?" question |

## Ten numbers to build the pitch on

1. **>60% of incidents at ServiceNow's own support org were repeats with known-but-unfindable fixes** (ServiceNow KCS case study — verified 3–0).
2. **$22 → $69 → $104**: cost per ticket at L1 → desktop → L3 (now traced to [MetricNet's own whitepaper (primary, 2020)](https://www.metricnet.com/wp-content/uploads/2020/08/ROI-of-Service-and-Support-v1.pdf); quote the vintage as ~2019–2020, not "2024"); automated interactions cost $0.10–$3 (secondary, indicative).
3. **8.85 business hours**: average incident MTTR — for work that is often minutes of keystrokes once the fix is known (MetricNet/HDI).
4. **85% of major human-error outages are procedure failures** — the fix existed and wasn't followed correctly (Uptime Institute 2024).
5. **Cases with a KB article attached resolve 66% faster; KCS = 52% faster time-to-relief** (ServiceNow — verified).
6. **$200M/year**: average downtime cost per Global 2000 company (Oxford Economics/Splunk 2024 — verified 3–0).
7. **Toil rose to 30% of SRE time in 2025** — first rise in five years, partly blamed on babysitting unreliable AI (Catchpoint 2025).
8. **>40% of agentic AI projects will be cancelled by 2027** for cost/unclear value/**inadequate risk controls** (Gartner, June 2025) — our approval-gate/audit/rollback design answers the kill-reasons.
9. **Only ~8% of leaders accept full agent autonomy; ~90% demand full audit logs** (2025–26 surveys) — graduated autonomy is a purchase criterion, not a compromise.
10. **Netflix auto-remediates 56% of a whole failure class with zero humans** (Pensive/LLM escalation, Netflix TechBlog) — the pattern works; nobody sells it to everyone below Netflix scale.

## The competitive sentence

> AIOps correlates alerts but doesn't act; runbook automation acts but only via brittle pre-written scripts; AI SREs investigate but stop at "here's the likely cause" (or draft a code PR); RPA executes clicks but is process-blind and incident-blind; ServiceNow/Moveworks deflect L1 requests inside their own platform; Azure SRE Agent proves the full loop but only for Azure resources. **The closed loop — detect → retrieve the org's own documented fix → risk-classify → approval-gated execution in third-party business systems → verified, audited, remembered — is unclaimed.**

## Known gaps & cautions (be honest on stage)

- **No public statistic directly states "X% of incidents already have a documented fix."** Use the proxy chain (60% repeats at ServiceNow, 13.3% outright repeat incidents, 20–50% password-class tickets, 85% procedure failures) and instrument the metric in the demo itself.
- "Disney uses WHATS'ON" rests on Disney job postings + the teammate's internship, not vendor confirmation — phrase as first-hand experience, don't name-drop the vendor relationship as fact.
- Several eye-catching figures are **vendor-claimed** (Moveworks 50–88% deflection, incident.io 80% downtime cut, Mediagenix "80% faster channel launches", Traversal 85% MTTR) — always label them.
- The $22/$69/$104 MetricNet ticket-cost ladder is now traced to [MetricNet's own whitepaper (primary)](https://www.metricnet.com/wp-content/uploads/2020/08/ROI-of-Service-and-Support-v1.pdf) — but its vintage is ~2019–2020, despite secondary blogs relabelling it "2024". Quote the numbers, not the fake freshness.
- Komodor Klaudia (post-March-2026) and Digitate Ignio genuinely execute remediations in their silos — the whitespace claim is the *combination*, not "nobody executes anything."
- The freshest alert-fatigue numbers (44% outages from ignored alerts, 78% no-alert incidents, Apr 2026) come from **NeuBird's** survey — an AI-SRE vendor; cite as "a 2026 industry survey (NeuBird)".
- Google's 50% toil ceiling is an **"advertised goal"** in the SRE book, not an enforced cap — say "Google's stated goal".
- Residual thin spots after the completion pass: Cataneo MYDAS has no public API reference (chapter 04 §6.3 says so and falls back to the four-tier integration pattern); the managed-services scale figures (Red Bee/Encompass/Globecast/Amagi) are vendor-claimed marketing numbers, labelled as such.
