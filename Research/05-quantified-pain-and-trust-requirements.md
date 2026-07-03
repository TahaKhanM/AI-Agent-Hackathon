# Chapter 5 — Quantified Pain & Trust Requirements: The Numbers That Make the Pitch Land

*Research chapter for the UK AI Agent Hackathon (Conduct AI "Make Legacy Move" track). Compiled 2 July 2026. Every figure carries an inline source and year; vendor-sponsored numbers are flagged as such.*

## TL;DR

- **Downtime is a boardroom number now.** The famous Gartner "$5,600/minute" figure is from **2014** — retire it. Use instead: ITIC 2024 (over 90% of mid-size/large enterprises say one hour of downtime costs **>$300,000**; 41% say **$1M–$5M+**), EMA 2024 (**$14,056/min** average, $23,750/min for large enterprises), and Splunk/Oxford Economics 2024 (**$400B/year** for the Global 2000, ~$200M per company — updated to **$600B in the 2026 refresh**).
- **Most of an incident is spent finding, not fixing.** Maintenance-engineering research puts active repair at only **30–40% of MTTR**; Splunk's 2024 data shows human-error incidents take **17–18 hours to even detect**; and 54% of tech executives admit they sometimes *deliberately don't fix* root causes — so the same incidents come back.
- **The long tail is where the money leaks quietly:** L1 tickets cost **$22**, Tier 2/desktop **$69**, Tier 3 escalations **$104** ([MetricNet's own whitepaper — primary, published 2020](https://www.metricnet.com/wp-content/uploads/2020/08/ROI-of-Service-and-Support-v1.pdf); secondary relays label it "2024" — see §3.1); **20–50% of all help-desk calls are password-reset-class trivia** (Gartner, ~$70/reset per Forrester); SRE toil has climbed back to **30% of working time** (Catchpoint 2025) and ~**70% of SREs cite on-call stress as a burnout driver**.
- **Alert fatigue is measurable:** ~**74% of IT-ops alerts are noise** (BigPanda, vendor-claimed); SOC teams see ~**3,800 alerts/day and ignore ~62%** — the security ops numbers are the best-documented analogue for ops alert overload.
- **Tribal knowledge is a real balance-sheet risk:** 42% of institutional knowledge is unique to a single individual and large US firms lose ~$47M/year to inefficient knowledge sharing (Panopto/YouGov, 2018 — old but still the canonical study); 60%+ of senior mainframe developers are over 50.
- **Scripted auto-remediation stalled for rational reasons** — brittle scripts that become their own toil, governance gaps, and fear of a Knight-Capital-style $440M-in-45-minutes automation disaster. LLM agents change the economics (they read the prose runbook humans already wrote) but not the trust problem.
- **Enterprises will let agents act only inside a control envelope:** ITIL change enablement (pre-approved "standard changes" are the legal on-ramp), SOX ITGC (segregation of duties, tamper-proof audit trails retained ~7 years), SOC 2 logging of every autonomous decision, and — from **2 Aug 2026, one month after the 4 July hackathon deadline** — EU AI Act high-risk obligations (see §7.4). Surveys consistently show **only ~8% of leaders are comfortable with full agent autonomy**, but ~90% will accept agents that log everything and keep a human on the approval gate. That is *exactly* the product shape we're building.

---

## 1. The Cost of Downtime: Which Numbers to Use (and Which to Retire)

### 1.1 The $5,600/minute figure is twelve years old

Nearly every downtime pitch deck cites "Gartner: $5,600 per minute." That number comes from a **2014** Gartner blog analysis (≈$300–336K/hour) and is still repeated as a "baseline" ([Erwood Group, 2025](https://www.erwoodgroup.com/blog/the-true-costs-of-downtime-in-2025-a-deep-dive-by-business-size-and-industry/); [Atlassian](https://www.atlassian.com/incident-management/kpis/cost-of-downtime)). Use it only as historical context — every 2024–2026 survey lands meaningfully higher.

### 1.2 The credible 2024–2026 range

| Source (year) | Headline number | Notes |
|---|---|---|
| [ITIC 2024 Hourly Cost of Downtime](https://itic-corp.com/itic-2024-hourly-cost-of-downtime-report/) | **>$300K/hour for 90%+ of mid-size & large enterprises**; 41% report $1M–$5M+/hour | Independent web survey, 1,000+ firms, Nov 2023–Mar 2024; costs *exclude* litigation and penalties. Banking/finance, government, healthcare, manufacturing, retail, transport and utilities average **>$5M/hour** |
| [ITIC 2025 update](https://www.calyptix.com/resources/itic-hourly-cost-downtime-2/) | 97% of enterprises >1,000 employees say one hour costs **>$100K**; the >$300K and 41% $1M+ findings hold | Continuity of the 2024 series |
| [EMA "IT Outages: 2024 Costs and Containment"](https://www.enterprisemanagement.com/product/it-outages-2024-costs-and-containment/) | **$14,056/minute average** (up ~10% from 2022); **$23,750/min for large enterprises**; typical outage lasts 30 min–2 h | **Commissioned by BigPanda** — treat as vendor-sponsored but analyst-run ([BigPanda summary, 2024](https://www.bigpanda.io/blog/it-outage-costs-2024/)) |
| [New Relic 2024 Observability Forecast](https://newrelic.com/press-release/20241022) | High-impact outage costs **up to $1.9M/hour**; median **77 hours/year** of high-impact downtime; engineers spend **30% of their time** on disruptions | Survey of 1,700+ technology professionals, 16 countries, Apr–May 2024. Vendor-published but widely cited |
| [Splunk + Oxford Economics, "The Hidden Costs of Downtime" (June 2024)](https://www.splunk.com/en_us/newsroom/press-releases/2024/conf24-splunk-report-shows-downtime-costs-global-2000-companies-400-billion-annually.html) | **$400B/year across the Global 2000 = 9% of profits; ~$200M/company average** ($256M in the US) | 2,000 executives, 53 countries, 10 industries; Oxford Economics did the modelling — the most defensible "big number" available ([Oxford Economics, 2024](https://www.oxfordeconomics.com/resource/the-hidden-costs-of-downtime-the-400b-problem-facing-the-global-2000/)) |
| [Splunk 2026 refresh](https://www.prnewswire.com/news-releases/the-600-billion-wake-up-call-new-splunk-research-reveals-downtime-is-a-systemic-business-crisis-302774919.html) | Downtime cost for the Global 2000 has surged to **$600B/year — +50% in two years** | The freshest headline number for a July 2026 pitch |
| [PagerDuty 2026 State of AI-First Operations](https://www.pagerduty.com/newsroom/2026-state-of-ai-first-operations/) | **68% of organizations lose >$300K/hour; 34% >$500K/hour; 8% >$1M/hour** during unplanned disruptions | 1,000 business/IT leaders across US, UK&I, DACH, France, Japan, Nordics, ANZ; published 17 Mar 2026 |

The Splunk/Oxford breakdown is useful for showing downtime is not just lost revenue: per Global-2000 company per year, **$49M direct revenue loss (taking ~75 days to recover), $22M regulatory fines, $19M ransomware/extortion payouts, $16M SLA penalties**, plus a share-price hit of up to 9% that takes ~79 days to recover ([Splunk/Cisco newsroom, 2024](https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2024/m06/conf24-splunk-report-shows-downtime-costs-global-2000-companies-400b-annually.html)).

### 1.3 Glamour P1s vs. the long tail we actually target

Be honest in the pitch: the $1M/hour numbers describe **severe, headline P1 outages**, which are getting *rarer* — Uptime Institute classified only **9% of 2024 incidents as serious or severe**, its lowest ever ([Uptime Institute Annual Outage Analysis, 2025](https://uptimeinstitute.com/resources/research-and-reports/annual-outage-analysis-2025)). Our Disney+-style observation is about the **long tail**: the daily grind of known failures with documented admin fixes. The quantifiable pain there is different but just as real:

- Engineering teams spend **30% of their time addressing disruptions** ([New Relic, 2024](https://newrelic.com/resources/report/observability-forecast/2024/state-of-observability/outages-downtime-cost)) — at a fully-loaded £80–120K UK ops engineer cost, that is ~£25–35K per engineer per year burned on interruptions.
- Median **toil** (manual, repetitive, automatable work) rose to **30% of SRE working time in 2025**, its first increase in five years ([Catchpoint SRE Report, 2025](https://www.catchpoint.com/learn/sre-report-2025)).
- The typical outage in the EMA 2024 dataset lasts **30 minutes to 2 hours** ([BigPanda/EMA, 2024](https://www.bigpanda.io/ar-ema-outage-cost-2024/)) — i.e., most incidents are exactly the "someone finds the runbook page and flips the config" class, not multi-day disasters.

**Pitch framing:** the P1 numbers ($300K+/hour) establish *stakes*; the toil numbers (30% of engineer time, ticket costs below) establish *frequency*. Our agent's ROI story lives at the intersection: shave 30–90 minutes off hundreds of medium incidents a year, not 30 seconds off one catastrophe.

---

## 2. MTTR Anatomy: Diagnosis Is the Bottleneck, and the Fix Is Usually Already Known

### 2.1 Most of MTTR is not repair

- In maintenance-engineering research, **active repair accounts for only 30–40% of total MTTR**; the other 60–70% is detection delay, response delay, diagnosis and verification — and "when manuals and schematics are current and on hand, diagnosis time collapses" ([Douglas Machine, MTTR guide](https://www.douglas-machine.com/what-is-mean-time-to-repair-mttr-and-what-drives-it-up-or-down/)). That last clause is literally our product thesis.
- In software ops, an L2/L3 engineer or SRE typically burns **20–30 minutes per incident** just investigating across consoles, change records, and Slack before doing anything ([BigPanda, 2024](https://www.bigpanda.io/blog/ai-incident-assistant-servicenow-now-assist/), vendor content).
- Splunk's 2024 analysis found **human-error-caused incidents take 17–18 hours to detect (MTTD) and 67–76 hours to recover** — the worst class precisely because diagnosis is hard ([Splunk, "Downtime Demystified", 2024](https://www.splunk.com/en_us/blog/cio-office/downtime-demystified-causes.html)).
- New Relic's 2024 data shows organizations spend **42–219 hours per year just detecting outages** depending on region, with financial services (227 h) and media (331 h) worst ([New Relic Observability Forecast, 2024](https://newrelic.com/sites/default/files/2024-10/new-relic-2024-observability-forecast-report.pdf)).

### 2.2 Changes and humans cause most incidents — and process failure dominates

- A long-standing figure from Visible Ops / DevOps Handbook–era research and Gartner reports: **~80% of production outages result from someone making a change**, and 80% of unplanned downtime traces to people/process issues ([Octopus Deploy, "Change Advisory Boards Don't Work"](https://octopus.com/blog/change-advisory-boards-dont-work); treat the precise 80% as folklore-grade but directionally well-supported).
- Uptime Institute's resiliency survey data: **66–80% of outages involve human error**, ~40% of organizations suffered a *major* human-error outage in the past three years, and **85% of those stemmed from staff failing to follow procedures or flawed procedures** ([Uptime Institute via Amerruss summary, 2024](https://www.amerruss.com/post/2024-uptime-institute-annual-outage-analysis-and-why-failures-keep-occurring); [Uptime Institute 2024 Resiliency Survey](https://datacenter.uptimeinstitute.com/rs/711-RIA-145/images/2024.Resiliency.Survey.ExecSum.pdf)).

The killer implication: the procedure *existed* in 85% of major human-error outages — it just wasn't followed. An agent that reliably executes the documented procedure attacks the single largest recorded outage cause.

### 2.3 Repeat incidents and known errors: the honest state of the evidence

ITIL formalises exactly our observation: a **known error** is "a problem that has a documented root cause and a workaround," kept in a Known Error Database so that recurrences resolve fast ([Atlassian, ITSM problem management](https://www.atlassian.com/itsm/problem-management/process)). Repeat-incident rate is a standard KPI — e.g. 8 repeats out of 40 quarterly incidents = 20% ([Opsera, repeat incident rate](https://opsera.ai/knowledge-base/incident-analysis/repeat-incident-rate/)).

**Honest gap:** we found no single authoritative 2024–2026 survey stating "X% of incidents already have a documented fix." What *is* citable and adds up to the same conclusion:

- **54% of technology executives admit they sometimes intentionally do not fix the root cause** of a downtime incident ([Splunk, 2024](https://www.splunk.com/en_us/blog/cio-office/downtime-demystified-causes.html)) — guaranteeing recurrence of known failure modes.
- 85% of major human-error outages are procedure failures, i.e. the fix was documented ([Uptime Institute, 2024](https://datacenter.uptimeinstitute.com/rs/711-RIA-145/images/2024.Resiliency.Survey.ExecSum.pdf)).
- 20–50% of the entire service-desk workload is password/access trivia with a fully deterministic documented resolution (§3).
- Practitioner consensus: "if the same alert fires every week because nobody converted the root cause to an automated fix or an improved runbook, you're burning your team on a problem that was already solved" ([incident.io, automated runbook guide, 2025](https://incident.io/blog/automated-runbook-guide)).

For the pitch, phrase it as: *"the industry's own KPI framework (known errors, repeat-incident rate) exists because a large share of incidents are re-runs — and 54% of execs admit they knowingly leave root causes in place."* For the demo, instrument our own metric: % of incidents matched to an existing knowledge article. That becomes the "operational memory" flywheel stat.

---

## 3. Ticket Economics, Toil and Burnout: Pricing the Long Tail

### 3.1 What a ticket costs

- MetricNet benchmarks: **~$22 per L1/Tier-1 ticket**, rising to **$85+ when escalated to Tier 3** (2021 snapshot; MetricNet's own published North American averages put desktop support at **$69** and Tier 3 at **$104** — [MetricNet whitepaper, 2020 (primary)](https://www.metricnet.com/wp-content/uploads/2020/08/ROI-of-Service-and-Support-v1.pdf); see [chapter 01](01-incident-resolution-status-quo.md)), with the full North American range **$0.74–$104.68** depending on channel and complexity ([MetricNet, cost per ticket](https://www.metricnet.com/service-desk-cost-per-ticket-motm/); [InvGate summary](https://blog.invgate.com/cost-per-ticket)).
- HDI's benchmarking puts North American help-desk cost per ticket at **$6–$40+** ([HDI SupportWorld, 2021](https://www.thinkhdi.com/library/supportworld/2021/understanding-cost-per-ticket)). Every avoided escalation saves roughly the difference between tiers (~$60+).
- Volume: HDI data shows **30–198 tickets per technician per month** ([HDI, Metric of the Month](https://www.thinkhdi.com/~/media/HDICorp/Files/Library-Archive/Insider%20Articles/tickets-per-technician.pdf)); HDI's State of Tech Support in 2025 reports organisations processing an average of **10,675 tickets/month**, with **34% seeing ticket volumes increase** ([HDI SupportWorld, 2025 (primary)](https://www.thinkhdi.com/library/supportworld/2025/5-insights-hdi-state-of-tech-support-2025)); the ~21 tickets/agent/day figure appears only in aggregator compilations ([Unthread, 2026](https://unthread.io/blog/support-ticket-backlog-statistics/) — secondary/aggregator-sourced — could not trace to primary; treat as indicative).

### 3.2 The password-reset benchmark (the canonical "documented fix" incident)

- Gartner: **20–50% of all help-desk calls are password resets**; a commonly cited Gartner figure is 40% for password expirations/changes/resets ([BleepingComputer, 2024](https://www.bleepingcomputer.com/news/security/password-reset-calls-are-costing-your-org-big-money/)).
- Forrester: **~$70 of labour cost per reset**, and **large US organizations budget >$1M/year** for password-related support ([Avatier summary](https://www.avatier.com/blog/hidden-cost-of-password-reset/); [Specops, 2023](https://specopssoft.com/blog/save-money-self-service-password-resets/)).
- A Yubico-sponsored study (flag: **vendor-sponsored**) adds ~10.9 hours/user/year lost to password friction (~$5.2M/year for a 15,000-user org) ([BioConnect, 2021](https://bioconnect.com/blog/2021/12/08/are-password-resets-costing-your-company)).

This class of ticket is our "hello world": trivially documented, deterministic remediation, huge volume — and self-service reset tools proved enterprises *will* automate remediation when the guardrails are obvious.

### 3.3 Toil and on-call burnout

- **Toil rose to a median 30% of SRE time in 2025** (from 25% in 2024) — the first rise in five years, with the report openly asking whether AI is *adding* toil ("AI babysitting": validating model outputs, tuning automation, debugging AI-driven remediation) ([Catchpoint SRE Report 2025, PDF](https://resources.catchpoint.com/hubfs/Website%20Assets%20-%20Briefs,%20EBooks,%20etc/The%20SRE%20Report%202025%20Catchpoint.pdf); [Forbes coverage, Jan 2025](https://www.forbes.com/sites/adrianbridgwater/2025/01/13/toil-and-trouble-catchpoint-clears-the-mist-on-the-internet-performance-cauldron/)).
- **~70% of SREs cite on-call stress as a direct contributor to burnout**, and 28% feel *more* stressed after incidents are resolved ([Catchpoint SRE Report 2025 via Uptime Labs](https://www.uptimelabs.io/learn/reduce-on-call-burnout)).
- PagerDuty's State of Digital Operations series links unplanned disruption to **developer burnout (42%)**, productivity loss (48%) and recovery cost (50%), and warns that increasing late-night pages drives attrition ([PagerDuty State of Digital Operations, 2025 PDF](https://www.pagerduty.com/assets/2025/state-of-digital-operations-2025.pdf); [PagerDuty 2026 newsroom](https://www.pagerduty.com/newsroom/2026-state-of-ai-first-operations/)).
- Widely-circulated practitioner figures — "~50 alerts/week per on-call engineer, only 2–5% requiring human intervention; 74% of teams report alert overwhelm; 67% of engineers admit ignoring alerts" — appear in secondary engineering blogs attributing PagerDuty/incident.io data ([OneUptime, 2026](https://oneuptime.com/blog/post/2026-03-05-alert-fatigue-ai-on-call/view); [dev.to, 2025](https://dev.to/linchuang/alert-fatigue-is-real-heres-what-its-actually-costing-your-team-4fl2)). **Flag: secondary/unverified — use with attribution caution.**

---

## 4. Alert Fatigue: The Best-Documented Numbers Are in Security Ops

IT-ops-specific numbers are mostly vendor-claimed; the security operations centre (SOC) literature is the rigorous analogue:

- IT & cloud ops teams receive thousands of alerts daily, of which **~74% are noise** ([BigPanda](https://www.bigpanda.io/blog/alert-noise-reduction-strategies/) — **vendor-claimed**; BigPanda also claims up to 98% noise reduction, and Moogsoft claimed 90–99% alert compression — classic AIOps marketing, cite as vendor claims only).
- SOC benchmark: the average enterprise SOC receives **~3,832 alerts/day, and 62% are ignored** ([Vectra AI](https://www.vectra.ai/topics/alert-fatigue); corroborated ranges in the peer-reviewed survey [ACM Computing Surveys, 2025](https://dl.acm.org/doi/10.1145/3723158)).
- False positives: commonly **~50%+ of alerts**, with some orgs reporting 80%; the 2024 SANS Detection & Response Survey found >half of SOC teams cite false positives as a top pain and 62.5% feel overwhelmed by data volume ([StrangeBee summary, 2024](https://strangebee.com/blog/what-is-cybersecurity-alert-fatigue-and-how-to-fight-back/); [OP Innovate](https://op-c.net/blog/why-false-positives-killing-security-teams/)).
- A Trend Micro survey found **51% of SOC teams overwhelmed by alert volume**, with analysts spending **>25% of their time on false positives** ([Cymulate glossary summary](https://cymulate.com/cybersecurity-glossary/alert-fatigue/)).

**Use in pitch:** alert fatigue is why "just add monitoring" failed — the bottleneck moved from *seeing* problems to *acting* on them. An agent that closes the loop (detect → match to known fix → execute with approval) is the only step that reduces the human queue.

---

## 5. Tribal Knowledge and the Workforce Cliff

- The canonical study (old but unreplaced — label as **2018**): Panopto/YouGov found the average large US business loses **$47M/year in productivity from inefficient knowledge sharing** ($42.5M productivity + $4.5M inefficient onboarding); **42% of institutional knowledge is unique to one individual**; knowledge workers waste **5.3 hours/week** waiting for or recreating knowledge; new hires take **up to 6 months to ramp**, struggling ~3.5 months to self-discover job details ([Panopto, 2018](https://www.panopto.com/company/news/inefficient-knowledge-sharing-costs-large-businesses-47-million-per-year/); [PR Newswire, 2018](https://www.prnewswire.com/news-releases/inefficient-knowledge-sharing-costs-large-businesses-47-million-per-year-300681971.html)).
- Legacy-systems workforce cliff (highly relevant to the "Make Legacy Move" track): **over 60% of senior mainframe developers are over 50** and retiring with undocumented system knowledge ([Per Scholas, mainframe talent gap](https://enterprise.perscholas.org/the-mainframe-talent-gap-7-numbers-tech-leaders-need-to-know/); [BizTech, 2025](https://biztechmagazine.com/article/2025/04/how-financial-services-companies-can-maintain-mainframes-cobol-experts-retire)). A Computerworld survey found 46% of IT shops already seeing a COBOL programmer shortage ([Computerworld](https://www.computerworld.com/article/1545244/the-cobol-brain-drain.html)); counterpoint for balance: BMC's 2025 survey shows the mainframe workforce *younging* (51% millennials, 15% Gen Z) ([TechChannel, 2025](https://techchannel.com/skills-gap/bmc-survey-2025/)).
- Manufacturing analogue: Deloitte/Manufacturing Institute project a need for up to **3.8M US manufacturing workers by 2033**, with tribal-knowledge loss a named risk as 55+ workers retire ([Leo AI summary, 2026](https://www.getleo.ai/blog/engineering-retirement-knowledge-loss-2026); [Per Aspera 2024 survey](https://www.peraspera.us/p/tribalknowledgescomeback)).

**Use in pitch:** the org's fix knowledge currently lives in two fragile places — a stale wiki and a retiring engineer's head. An agent that *executes from* the knowledge base creates pressure to keep it current, and every executed incident enriches the "operational memory" — turning tribal knowledge into an owned asset with a bus factor > 1.

---

## 6. Why Scripted Auto-Remediation Stalled — and What LLM Agents Change

### 6.1 The pre-LLM failure mode

Runbook automation (Rundeck, Resolve, ServiceNow orchestrations, home-grown scripts) has existed for 15+ years. Adoption of *closed-loop* remediation stayed low for consistent, documented reasons:

1. **The automation became its own toil.** Scripted runbooks are brittle: every environment change breaks them, and "the runbook itself can become toil to maintain" — needing owners, SLAs and cross-team review just to stay alive ([incident.io, runbook automation guide, 2026](https://incident.io/blog/runbook-automation-tools-2026-the-complete-guide); [AiOps School, 2026](https://aiopsschool.com/blog/runbook-automation/)).
2. **Governance gaps.** Without a formal risk-classification framework, organizations default to "everything needs manual approval," and approval workflows are ad-hoc per team — repeatedly called out as the primary barrier to autonomous-operations adoption ([Cast AI, agentic runbooks, 2026](https://cast.ai/blog/agentic-runbooks/)).
3. **Fear of the one bad automation.** "Teams aren't afraid of automation — they're afraid of what happens when it goes wrong. A single automated fix applied in the wrong context can bring down production" ([Tamnoon, building trust in automated remediation](https://tamnoon.io/blog/building-trust-in-automated-remediation/)). Black-box behaviour compounds this: "when teams can't see the logic behind a fix, they can't trust it."

### 6.2 Knight Capital: the cautionary tale every CAB member knows

On 1 August 2012, Knight Capital lost **~$440–460M in 45 minutes** — not because automation acted, but because *ungoverned deployment and dead code* did: a technician manually deployed new code to only 7 of 8 servers (no written deployment procedure, no peer review); the 8th server ran dormant legacy code that started firing millions of erroneous orders; **97 automated warning emails were generated before market open and nobody read them** ([Henrico Dolfing case study](https://www.henricodolfing.ch/en/case-study-4-the-440-million-software-error-at-knight-capital/); [PRMIA case study, PDF](https://prmia.org/common/Uploaded%20files/eAI/PRMIA%20Case%20study%20-%20Knight%20Trading.pdf)). The firm needed a rescue financing within days.

Read correctly, Knight Capital is an argument **for** our design, not against it: the failure chain was (a) undocumented manual procedure, (b) no automated verification of deployment state, (c) alerts with no actioning loop, (d) no kill-switch/rollback. Approval gates + verified execution + audit trail + rollback is the anti-Knight architecture.

### 6.3 What changed with LLM agents

- **The script-authoring cost collapsed.** Pre-LLM, every remediation needed a hand-coded script per failure mode. An LLM agent can read the *prose* runbook/KB article ops teams already maintain and translate it into tool calls at incident time — the knowledge base becomes executable without a rewrite ([Cast AI, 2026](https://cast.ai/blog/agentic-runbooks/); [incident.io, 2026](https://incident.io/blog/runbook-automation-tools-2026-the-complete-guide)).
- **But trust did not collapse with it.** Practitioner guidance remains: keep AI actions behind human approval gates for anything touching production ([OneUptime, 2026](https://oneuptime.com/blog/post/2026-01-24-runbook-automation/view)), and the Catchpoint 2025 data shows AI so far *shifting* toil ("AI babysitting") rather than deleting it ([Catchpoint, 2025](https://www.catchpoint.com/learn/sre-report-2025)).
- **Sobriety check for the pitch:** Gartner predicts **>40% of agentic AI projects will be canceled by end-2027** on cost, unclear value, or *inadequate risk controls*, and estimates only ~130 of thousands of "agentic" vendors are genuinely agentic ("agent washing") ([Gartner press release, June 2025](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)). Judges will know this stat; pre-empt it by making risk controls the product, not an afterthought. Gartner's same note predicts **15% of day-to-day work decisions made autonomously by 2028** — the direction is not in doubt, the governance is.

---

## 7. The Enterprise Trust Envelope: What Must Be True Before an Agent May Act

### 7.1 ITIL change management: "standard changes" are the on-ramp

Under ITIL, a Change Advisory Board (CAB) reviews normal/major changes for risk, blast radius and **rollback readiness** — but ITIL 4's "change enablement" explicitly pushes organizations to reserve CAB review for high-risk changes and pre-authorize low-risk, repeatable **standard changes** ([Atlassian, ITSM change management](https://www.atlassian.com/itsm/change-management); [monday.com, CAB framework](https://monday.com/blog/teamwork/change-advisory-board/)). The heavyweight-CAB model is itself widely criticised as slow and ineffective ([Octopus Deploy](https://octopus.com/blog/change-advisory-boards-dont-work)). **Product mapping:** each documented fix the agent executes should be registered as a *standard change template* — pre-approved once by humans, executed many times by the agent, logged every time. That is the ITIL-native way to make an agent legitimate.

### 7.2 SOX: config changes to financially-relevant systems are audited

For any US-listed enterprise (and UK equivalents under UK SOX-like proposals), SOX §404 IT General Controls require: a formal change request/approval workflow; testing evidence before production; **segregation of duties — the person (or agent) who develops/requests a change cannot be the one who approves and deploys it**; and tamper-evident audit trails typically **retained ~7 years** ([Bitsight SOX checklist, 2026](https://www.bitsight.com/learn/compliance/sox-compliance-checklist); [Liquibase, SOX for database change management](https://www.liquibase.com/resources/guides/sox-compliance-for-database-change-management-best-practices); [MetricStream, SOX IT controls](https://www.metricstream.com/insights/sox-it-controls.htm)). **Product mapping:** the approval gate isn't UX sugar — it *is* the segregation-of-duties control. Agent proposes; human (different identity) approves; immutable log satisfies the auditor.

### 7.3 SOC 2: log the agent's mind, not just its hands

Analyses of SOC 2 Trust Services Criteria applied to agentic AI converge on a concrete logging bar: **every autonomous decision should record (1) input data, (2) reasoning chain, (3) confidence score, (4) action taken, (5) the authorizing policy rule**, with agent privileges time-bound and reviewed ([Teleport, "How AI Agents Impact SOC 2", 2025](https://goteleport.com/blog/ai-agents-soc-2/); [PolicyLayer, 2026](https://policylayer.com/blog/soc2-compliance-ai-agents)). That five-element schema is a free, citable spec for our audit-trail data model.

### 7.4 EU AI Act: the high-risk deadline lands one month after the hackathon

- **2 Aug 2025:** obligations for general-purpose AI model providers took effect ([European Commission AI Act timeline](https://ai-act-service-desk.ec.europa.eu/en/ai-act/timeline/timeline-implementation-eu-ai-act)).
- **2 Aug 2026 — one month after the hackathon deadline:** the bulk of the Act applies, including high-risk (Annex III) system requirements and transparency rules, with national enforcement beginning ([Implementation timeline, artificialintelligenceact.eu](https://artificialintelligenceact.eu/implementation-timeline/)).
- AI agents are **not a separate category**: the Commission's position is that AI-system and GPAI definitions already cover agents, so an agent used in a high-risk context inherits high-risk obligations — risk management, logging, human oversight, robustness ([EC AI Act Service Desk FAQ](https://ai-act-service-desk.ec.europa.eu/en/faq)). Most internal IT-ops remediation is *not* Annex III high-risk, but agents touching critical-infrastructure management could be — and the Act's human-oversight and logging expectations are becoming the de-facto enterprise procurement checklist regardless.

### 7.5 What leaders actually say about agent autonomy (2025–2026 surveys)

- **Less than half** of surveyed leaders trust agents to make autonomous decisions *even with guardrails*, and **only 8% are comfortable with total autonomy** ([CIO.com, "Agentic AI has big trust issues", 2025](https://www.cio.com/article/4087765/agentic-ai-has-big-trust-issues.html) — reporting survey data; verify the underlying survey before quoting in print).
- Deloitte (3,235 IT/business leaders): **only 21% have a mature agentic-AI governance model**; ~80% lack defined boundaries for which decisions agents may take independently vs. which need human approval ([Deloitte, "Agentic AI is scaling faster than guardrails", 2025](https://www.deloitte.com/us/en/insights/topics/emerging-technologies/ai-agents-scaling-faster.html)).
- US federal agencies survey (May 2026): **~90% require logging and audit trails for all agent actions; >80% require automated policy checks; 79% mandate human-in-the-loop approval for every action** in sensitive contexts ([Nextgov/FCW, 2026](https://www.nextgov.com/artificial-intelligence/2026/05/survey-more-half-federal-agencies-now-planning-agentic-ai-pilots/413324/)).
- McKinsey frames 2026 as the year AI trust programs must shift "to the agentic era" — governance as adoption enabler, not brake ([McKinsey, State of AI trust, 2026](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/tech-forward/state-of-ai-trust-in-2026-shifting-to-the-agentic-era)).
- Counterweight optimism: PagerDuty's 2026 report finds 59% already using AI in operations, and AI adopters report better resilience outcomes (75% vs 66%) ([PagerDuty, 2026](https://www.pagerduty.com/newsroom/2026-state-of-ai-first-operations/) — vendor survey).

The pattern is unambiguous: **enterprises are not asking "can the agent fix it?" — they're asking "can I see, approve, audit and undo what it did?"** Approval gates, immutable audit trails, policy checks and rollback are not compliance chores; they are the top-three purchase criteria in every 2025–2026 survey.

---

## Implications for Our Project

1. **Lead the pitch with the 2024–2026 numbers, not Gartner 2014.** Strongest trio: Splunk/Oxford **$400B → $600B** (2024→2026), ITIC **>$300K/hour for 90% of enterprises** (2024), New Relic **30% of engineering time on disruptions** (2024). Explicitly say we target the *long tail* (30min–2h incidents, EMA 2024), which is volume × toil, not the glamour P1.
2. **Our core claim has a citable spine:** 85% of major human-error outages are procedure failures (Uptime 2024) + 54% of execs knowingly leave root causes unfixed (Splunk 2024) + diagnosis consuming 60–70% of MTTR (maintenance research) = "the fix exists; finding and executing it is the broken step."
3. **Quantify the demo ROI simply:** escalation avoided ≈ $60+/ticket (MetricNet L1 vs L3); 30–90 minutes saved per incident × ITIC hourly cost; toil minutes returned per week (Catchpoint 30% baseline).
4. **Build the trust envelope as first-class features and name-check the frameworks in the demo:** standard-change templates (ITIL 4), approver ≠ requester (SOX SoD), five-element decision log (SOC 2 mapping), one-click rollback (CAB "rollback readiness"), and an EU-AI-Act-flavoured human-oversight mode. The 4 July 2026 demo lands one month before the Act's high-risk date — a gift of a narrative hook.
5. **Pre-empt the Gartner 40%-cancellation stat** (judges will raise it): our differentiation *is* the risk controls Gartner says failing projects lack.
6. **The "operational memory" moat maps to the tribal-knowledge numbers:** 42% of knowledge is single-person (Panopto 2018), ops onboarding takes up to 6 months — every approved agent execution converts tribal knowledge into an auditable, reusable asset.

---

## Sources

- [ITIC 2024 Hourly Cost of Downtime Report](https://itic-corp.com/itic-2024-hourly-cost-of-downtime-report/) — >$300K/hour for 90%+ of enterprises; 41% at $1M–$5M+; methodology (1,000+ firms).
- [ITIC 2025 Hourly Cost of Downtime results (Calyptix)](https://www.calyptix.com/resources/itic-hourly-cost-downtime-2/) — 2025 continuation; 97% of large enterprises >$100K/hour.
- [Splunk press release, June 2024 (Cisco newsroom)](https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2024/m06/conf24-splunk-report-shows-downtime-costs-global-2000-companies-400b-annually.html) — $400B/$200M figures, cost breakdown, 75/79-day recovery, 56% security-caused, methodology.
- [Oxford Economics, Hidden Costs of Downtime (2024)](https://www.oxfordeconomics.com/resource/the-hidden-costs-of-downtime-the-400b-problem-facing-the-global-2000/) — independent research-partner page for the $400B study.
- [Splunk $600B 2026 refresh (PR Newswire)](https://www.prnewswire.com/news-releases/the-600-billion-wake-up-call-new-splunk-research-reveals-downtime-is-a-systemic-business-crisis-302774919.html) — $600B, +50% in two years.
- [New Relic 2024 Observability Forecast press release](https://newrelic.com/press-release/20241022) — $1.9M/hour, 77 hours/year, 30% engineering time.
- [New Relic 2024 Observability Forecast, outages chapter](https://newrelic.com/resources/report/observability-forecast/2024/state-of-observability/outages-downtime-cost) — MTTD hours per year by size/industry.
- [EMA "IT Outages: 2024 Costs and Containment"](https://www.enterprisemanagement.com/product/it-outages-2024-costs-and-containment/) and [BigPanda summary](https://www.bigpanda.io/blog/it-outage-costs-2024/) — $14,056/min, $23,750/min large enterprise, 30min–2h typical outage (BigPanda-commissioned).
- [PagerDuty 2026 State of AI-First Operations newsroom](https://www.pagerduty.com/newsroom/2026-state-of-ai-first-operations/) — 68%/34%/8% hourly-loss tiers; 59% AI adoption; burnout impact.
- [PagerDuty State of Digital Operations 2025 (PDF)](https://www.pagerduty.com/assets/2025/state-of-digital-operations-2025.pdf) — disruption impact incl. 42% developer burnout.
- [Erwood Group downtime cost deep dive (2025)](https://www.erwoodgroup.com/blog/the-true-costs-of-downtime-in-2025-a-deep-dive-by-business-size-and-industry/) — dates the Gartner $5,600/min figure to 2014.
- [Atlassian, cost of downtime](https://www.atlassian.com/incident-management/kpis/cost-of-downtime) — Gartner baseline context.
- [Uptime Institute Annual Outage Analysis 2025](https://uptimeinstitute.com/resources/research-and-reports/annual-outage-analysis-2025) — only 9% of 2024 incidents serious/severe; costs rising.
- [Uptime Institute 2024 Resiliency Survey exec summary (PDF)](https://datacenter.uptimeinstitute.com/rs/711-RIA-145/images/2024.Resiliency.Survey.ExecSum.pdf) — human-error outage causes; procedure-failure findings.
- [Amerruss summary of Uptime 2024 analysis](https://www.amerruss.com/post/2024-uptime-institute-annual-outage-analysis-and-why-failures-keep-occurring) — 66–80% human error; 85% procedure failures; ~40% of orgs with major human-error outage.
- [Splunk, "Downtime Demystified" (2024)](https://www.splunk.com/en_us/blog/cio-office/downtime-demystified-causes.html) — MTTD 17–18h / MTTR 67–76h for human error; 54% intentionally don't fix root cause.
- [Douglas Machine, MTTR drivers](https://www.douglas-machine.com/what-is-mean-time-to-repair-mttr-and-what-drives-it-up-or-down/) — active repair only 30–40% of MTTR; documentation collapses diagnosis time.
- [BigPanda, ServiceNow Now Assist blog (2024)](https://www.bigpanda.io/blog/ai-incident-assistant-servicenow-now-assist/) — 20–30 min investigation per incident (vendor).
- [Octopus Deploy, "Change Advisory Boards Don't Work"](https://octopus.com/blog/change-advisory-boards-dont-work) — ~80% of outages change-caused (Visible Ops/Gartner lineage); CAB criticism.
- [Atlassian, ITSM problem management](https://www.atlassian.com/itsm/problem-management/process) — known-error / KEDB definitions.
- [Opsera, repeat incident rate](https://opsera.ai/knowledge-base/incident-analysis/repeat-incident-rate/) — repeat-incident KPI definition and worked example.
- [incident.io, automated runbook guide (2025)](https://incident.io/blog/automated-runbook-guide) — repeat-alert/runbook practitioner framing; MTTR reduction claims (vendor).
- [MetricNet, service desk cost per ticket](https://www.metricnet.com/service-desk-cost-per-ticket-motm/) — $22 L1 / $85+ L3; $0.74–$104.68 range (2021 snapshot; MetricNet's own 2020 whitepaper — primary, listed below — puts the ladder at $22/$69/$104).
- [InvGate, cost per ticket summary](https://blog.invgate.com/cost-per-ticket) — secondary confirmation of MetricNet tiers.
- [HDI SupportWorld, understanding cost per ticket (2021)](https://www.thinkhdi.com/library/supportworld/2021/understanding-cost-per-ticket) — $6–$40+ per ticket.
- [HDI, tickets per technician per month (PDF)](https://www.thinkhdi.com/~/media/HDICorp/Files/Library-Archive/Insider%20Articles/tickets-per-technician.pdf) — 30–198 tickets/tech/month.
- [HDI SupportWorld — 5 Insights from HDI's State of Tech Support in 2025 (primary)](https://www.thinkhdi.com/library/supportworld/2025/5-insights-hdi-state-of-tech-support-2025) — 10,675 tickets/month average; 34% of teams seeing volumes increase.
- [MetricNet — ROI of Service and Support whitepaper (PDF, 2020) (primary)](https://www.metricnet.com/wp-content/uploads/2020/08/ROI-of-Service-and-Support-v1.pdf) — $22 service desk / $69 desktop / $104 level 3 cost per ticket.
- [Unthread, support ticket statistics compilation (2026)](https://unthread.io/blog/support-ticket-backlog-statistics/) — ~21 tickets/agent/day (secondary/aggregator-sourced — could not trace to primary; treat as indicative; the 10,675 and 34% figures it relays are confirmed by the HDI primary above).
- [BleepingComputer, password reset costs (2024)](https://www.bleepingcomputer.com/news/security/password-reset-calls-are-costing-your-org-big-money/) — Gartner 20–50% share.
- [Avatier, hidden cost of password resets](https://www.avatier.com/blog/hidden-cost-of-password-reset/) — Forrester $70/reset, $1M+/yr large orgs.
- [Specops, self-service reset savings (2023)](https://specopssoft.com/blog/save-money-self-service-password-resets/) — password-ticket economics (vendor).
- [BioConnect, password reset costs (2021)](https://bioconnect.com/blog/2021/12/08/are-password-resets-costing-your-company) — Yubico-sponsored productivity-loss figures (vendor-sponsored).
- [Catchpoint SRE Report 2025 (PDF)](https://resources.catchpoint.com/hubfs/Website%20Assets%20-%20Briefs,%20EBooks,%20etc/The%20SRE%20Report%202025%20Catchpoint.pdf) — toil up to 30%; AI-babysitting discussion.
- [Uptime Labs, on-call burnout](https://www.uptimelabs.io/learn/reduce-on-call-burnout) — ~70% SRE on-call stress → burnout; 28% post-incident stress (citing Catchpoint 2025).
- [Forbes on Catchpoint SRE Report (Jan 2025)](https://www.forbes.com/sites/adrianbridgwater/2025/01/13/toil-and-trouble-catchpoint-clears-the-mist-on-the-internet-performance-cauldron/) — independent coverage of toil findings.
- [OneUptime, alert fatigue & AI (2026)](https://oneuptime.com/blog/post/2026-03-05-alert-fatigue-ai-on-call/view) — 50 alerts/week, 2–5% actionable (secondary, flag).
- [BigPanda, alert noise reduction](https://www.bigpanda.io/blog/alert-noise-reduction-strategies/) — 74% of alerts are noise (vendor-claimed).
- [Vectra AI, alert fatigue](https://www.vectra.ai/topics/alert-fatigue) — 3,832 SOC alerts/day, 62% ignored.
- [ACM Computing Surveys, alert fatigue in SOCs (2025)](https://dl.acm.org/doi/10.1145/3723158) — peer-reviewed survey of SOC alert-fatigue research.
- [StrangeBee, SOC alert fatigue (2024)](https://strangebee.com/blog/what-is-cybersecurity-alert-fatigue-and-how-to-fight-back/) — SANS 2024 false-positive findings.
- [Cymulate, alert fatigue glossary](https://cymulate.com/cybersecurity-glossary/alert-fatigue/) — Trend Micro 51% overwhelmed, >25% time on false positives.
- [Panopto, inefficient knowledge sharing (2018)](https://www.panopto.com/company/news/inefficient-knowledge-sharing-costs-large-businesses-47-million-per-year/) — $47M/year, 42% unique knowledge, 5.3 hrs/week, onboarding ramp.
- [PR Newswire, Panopto/YouGov study (2018)](https://www.prnewswire.com/news-releases/inefficient-knowledge-sharing-costs-large-businesses-47-million-per-year-300681971.html) — methodology (1,001 US workers).
- [Per Scholas, mainframe talent gap](https://enterprise.perscholas.org/the-mainframe-talent-gap-7-numbers-tech-leaders-need-to-know/) — >60% senior mainframe devs over 50.
- [BizTech, COBOL experts retiring (2025)](https://biztechmagazine.com/article/2025/04/how-financial-services-companies-can-maintain-mainframes-cobol-experts-retire) — financial-services mainframe workforce risk.
- [TechChannel, BMC mainframe survey (2025)](https://techchannel.com/skills-gap/bmc-survey-2025/) — counterpoint: workforce getting younger.
- [Computerworld, COBOL brain drain](https://www.computerworld.com/article/1545244/the-cobol-brain-drain.html) — 46% seeing COBOL shortage (older survey; historical).
- [Leo AI, engineering retirement knowledge loss (2026)](https://www.getleo.ai/blog/engineering-retirement-knowledge-loss-2026) — Deloitte/Manufacturing Institute 3.8M-jobs projection context.
- [incident.io, runbook automation tools guide (2026)](https://incident.io/blog/runbook-automation-tools-2026-the-complete-guide) — runbook maintenance burden; automation adoption barriers.
- [Cast AI, agentic runbooks (2026)](https://cast.ai/blog/agentic-runbooks/) — governance gaps as adoption barrier; LLM agents executing prose runbooks (vendor).
- [AiOps School, runbook automation guide (2026)](https://aiopsschool.com/blog/runbook-automation/) — runbook ownership/maintenance guidance.
- [Tamnoon, building trust in automated remediation](https://tamnoon.io/blog/building-trust-in-automated-remediation/) — fear of wrong-context automated fixes; black-box trust problem.
- [Henrico Dolfing, Knight Capital case study](https://www.henricodolfing.ch/en/case-study-4-the-440-million-software-error-at-knight-capital/) — $440M/45-minute failure chain detail.
- [PRMIA, Knight Capital case study (PDF)](https://prmia.org/common/Uploaded%20files/eAI/PRMIA%20Case%20study%20-%20Knight%20Trading.pdf) — risk-management framing; 97 unread alert emails.
- [Gartner press release, June 2025](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027) — >40% agentic projects canceled by 2027; agent-washing; 15%-of-decisions-by-2028.
- [Atlassian, ITIL change management](https://www.atlassian.com/itsm/change-management) — standard vs normal changes; CAB scope under ITIL 4.
- [monday.com, change advisory board framework](https://monday.com/blog/teamwork/change-advisory-board/) — CAB role incl. rollback readiness.
- [Bitsight, SOX compliance checklist (2026)](https://www.bitsight.com/learn/compliance/sox-compliance-checklist) — ITGC change-management and audit requirements.
- [Liquibase, SOX for database change management](https://www.liquibase.com/resources/guides/sox-compliance-for-database-change-management-best-practices) — segregation of duties (developer ≠ deployer).
- [MetricStream, SOX IT controls](https://www.metricstream.com/insights/sox-it-controls.htm) — audit-trail retention (~7 years), logging requirements.
- [Teleport, AI agents & SOC 2 (2025)](https://goteleport.com/blog/ai-agents-soc-2/) — mapping Trust Services Criteria to agentic AI.
- [PolicyLayer, SOC 2 for AI agents (2026)](https://policylayer.com/blog/soc2-compliance-ai-agents) — five-element decision-logging schema.
- [European Commission AI Act Service Desk, implementation timeline](https://ai-act-service-desk.ec.europa.eu/en/ai-act/timeline/timeline-implementation-eu-ai-act) — GPAI Aug 2025, high-risk Aug 2026 dates.
- [artificialintelligenceact.eu, implementation timeline](https://artificialintelligenceact.eu/implementation-timeline/) — independent tracker of the same dates.
- [EC AI Act Service Desk FAQ](https://ai-act-service-desk.ec.europa.eu/en/faq) — AI agents covered by existing AI-system/GPAI definitions.
- [CIO.com, "Agentic AI has big trust issues" (2025)](https://www.cio.com/article/4087765/agentic-ai-has-big-trust-issues.html) — <50% trust agents even with guardrails; 8% comfortable with total autonomy.
- [Deloitte, "Agentic AI is scaling faster than guardrails" (2025)](https://www.deloitte.com/us/en/insights/topics/emerging-technologies/ai-agents-scaling-faster.html) — 21% mature governance; ~80% lack decision boundaries (n=3,235).
- [Nextgov/FCW, federal agentic AI survey (May 2026)](https://www.nextgov.com/artificial-intelligence/2026/05/survey-more-half-federal-agencies-now-planning-agentic-ai-pilots/413324/) — ~90% require logging/audit trails; 79% mandate human-in-the-loop in sensitive contexts.
- [McKinsey, State of AI trust: shifting to the agentic era (2026)](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/tech-forward/state-of-ai-trust-in-2026-shifting-to-the-agentic-era) — trust/governance as the agentic adoption gate.
