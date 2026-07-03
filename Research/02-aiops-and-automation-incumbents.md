# Chapter 2 — AIOps & Automation Incumbents: Who Already Automates Incident Response, and Exactly Where They Stop

*Research date: 2 July 2026. Figures older than 2024 are labelled with their year.*

## TL;DR

- **Three incumbent generations coexist:** (1) AIOps correlation platforms (BigPanda, Moogsoft/Dell, Dynatrace Davis, Splunk ITSI, IBM Cloud Pak) that reduce noise and point at root cause but do not execute; (2) runbook/process automation (Rundeck, StackStorm, Ansible EDA, AWS SSM, Azure Automation) that executes but only pre-scripted, brittle, human-authored jobs; (3) the 2025–2026 wave of "AI SRE" agents (Azure SRE Agent, Datadog Bits AI SRE, PagerDuty SRE Agent, incident.io AI SRE, ServiceNow AIOps AI Specialist) that investigate autonomously and are only now cautiously adding gated execution.
- **The market has validated the exact loop our project targets.** Azure SRE Agent (GA late 2025) proposes mitigations and executes them only after human approval, with a "permission gate" that evaluates every tool call ([Microsoft Learn, 2026](https://learn.microsoft.com/en-us/azure/sre-agent/overview)). Microsoft claims 35,000+ incidents handled autonomously internally ([Azure, 2025](https://azure.microsoft.com/en-us/products/sre-agent)) — vendor-claimed, internal-only.
- **Almost nobody closes the full detect→diagnose→decide→execute→learn loop on *admin/config* fixes grounded in an org's own operational knowledge base.** Incumbents either correlate/recommend (AIOps), execute without learning (runbook automation), or investigate code-centric root causes (AI SREs that propose *pull requests*, not admin actions).
- **Scripted auto-remediation stayed niche for well-documented reasons:** brittle matcher rules, stale runbooks engineers learn to distrust, cascading automation failures (Knight Capital 2012, AWS S3 2017, Facebook BGP 2021), and zero contextual memory ([RubixKube, 2025](https://rubixkube.ai/blog/aiops-auto-remediation-memory-failure); [incident.io](https://incident.io/blog/automated-runbook-guide)).
- **Consolidation confirms strategic value:** ServiceNow closed its **$2.85B** Moveworks acquisition on 15 Dec 2025 after a DOJ second-request antitrust review ([Moveworks, 2025](https://www.moveworks.com/us/en/company/news/press-releases/servicenow-completes-acquisition-of-moveworks)); Nvidia bought auto-remediation startup Shoreline.io for ~$100M (2024); Dell bought Moogsoft (2023); Automation Anywhere bought Aisera (Nov 2025); Resolve bought Espressive (Sep 2025).
- **Money is real:** ServiceNow's Now Assist passed **$600M ACV in 2025, doubling YoY**, tracking to $1B in 2026 ([CX Today, 2026](https://www.cxtoday.com/service-management-connectivity/servicenow-ai-adoption-q4-growth/)). AIOps market estimates for 2025–26 range from ~$11B to ~$19B depending on definition (analyst-firm numbers, treat as directional).
- **But scepticism is equally real:** Gartner predicts **>40% of agentic AI projects will be canceled by end-2027** (June 2025), estimates only ~130 of thousands of "agentic AI" vendors are genuinely agentic, and the Catchpoint SRE Report 2025 found reported toil *rose* from 25%→30% — partly blamed on supervising half-reliable AI. Trust, approval gates and auditability are the battleground, which is precisely our project's design centre.

---

## 1. Framing: the five-layer incident loop

To place each incumbent, we use the pipeline the hackathon product must close end-to-end:

**Detect → Diagnose → Decide → Execute → Learn**

- **Detect:** ingest alerts/events, suppress noise, correlate into incidents.
- **Diagnose:** root-cause analysis, change correlation, impact analysis.
- **Decide:** select a remediation, assess risk, get approval.
- **Execute:** actually perform the fix (restart, config change, permission fix, cache flush, failover — the *admin* actions the Disney+ ops teams applied by hand).
- **Learn:** persist what worked into durable, retrievable operational memory.

The one-line thesis of this chapter: **generation 1 owns Detect/Diagnose, generation 2 owns Execute (dumbly), generation 3 is racing to own Diagnose/Decide — and the Execute-with-learning layer for documented admin fixes is still mostly open.**

---

## 2. Generation 1 — AIOps correlation platforms: they see everything, touch nothing

### BigPanda

BigPanda is the archetypal event-correlation AIOps vendor: it ingests alerts from monitoring tools and uses ML to compress them into incidents, claiming **>95% alert-volume reduction** ([BigPanda](https://www.bigpanda.io/blog/what-is-an-aiops-platform/)). It raised **$190M at a $1.2B valuation in January 2022** led by Advent International and Insight Partners ([GlobeNewswire, 2022](https://www.globenewswire.com/news-release/2022/01/12/2365641/0/en/BigPanda-Raises-190-Million-in-Funding-at-1-2-Billion-Valuation.html)). In May 2025 it pivoted to "agentic IT operations," launching **AI Detection and Response** (an autonomous L1-ops agent) and **AI Incident Assistant** (the "Biggy" chat agent in Slack/Teams), pitched at what it calls the "$200 billion ITOps market" — a vendor-marketing number ([BusinessWire, May 2025](https://www.businesswire.com/news/home/20250528507389/en/BigPanda-Launches-Agentic-IT-Operations-to-Bring-Intelligent-Automation-to-the-%24200-billion-ITOps-Market)). In November 2025 it acquired Velocity to accelerate that agentic push ([BusinessWire, Nov 2025](https://www.businesswire.com/news/home/20251110426205/en/BigPanda-Acquires-Velocity-to-Accelerate-Leadership-in-Agentic-IT-Operations)). Pricing is not public ([Capterra](https://www.capterra.com/p/134318/BigPanda/)). **Layer coverage:** Detect and Diagnose, moving into Decide; its agents "identify possible root cause" and validate changes, but remediation execution is delegated to customers' automation tools.

### Moogsoft → Dell APEX AIOps

Moogsoft, the original "AIOps" coiner, raised roughly **$93–95M** before being acquired by **Dell in July 2023** ([Dell, 2023](https://www.dell.com/en-us/dt/corporate/newsroom/announcements/detailpage.press-releases~usa~2023~07~dell-technologies-announces-intent-to-acquire-moogsoft.htm); [SiliconANGLE, 2023](https://siliconangle.com/2023/07/20/dell-acquires-venture-backed-aiops-startup-moogsoft/)). Dell folded it, together with CloudIQ, into **APEX AIOps** ([IBM/industry commentary](https://www.ibm.com/think/insights/gartner-market-guide-for-aiops-essential-reading-for-itops-and-sre)). Instructive datapoint: a correlation-only pioneer could not sustain independence — it exited for roughly the amount it had raised. **Layer coverage:** Detect/Diagnose only.

### Dynatrace Davis AI

Dynatrace's Davis AI does causal (not just correlational) root-cause analysis over its topology map, and in **February 2025** Dynatrace announced "preventive operations" — agentic capabilities that predict issues and trigger **automated remediation workflows** (e.g., restart a crashed service, scale capacity, generate Kubernetes resource adjustments) ([BusinessWire, Feb 2025](https://www.businesswire.com/news/home/20250204836622/en/Dynatrace-Advances-AIOps-with-Preventive-Operations); [Dynatrace blog](https://www.dynatrace.com/news/blog/remediation-intelligence-accelerate-mttr-with-ai-powered-context-and-knowledge/)). Its "remediation intelligence" surfaces AI-picked context and past-incident knowledge to responders. **Layer coverage:** strong Detect/Diagnose, workflow-based Execute — but the workflows are customer-authored Dynatrace Workflows (pre-scripted), and it only sees what Dynatrace instruments. It does not retrieve fixes from an org's own KB/manual.

### Datadog Watchdog

Watchdog is Datadog's always-on anomaly-detection layer — unsupervised ML over metrics/logs/traces that flags deviations without configured thresholds ([Medium/devops-radar comparison, 2025](https://medium.com/@garakh/ai-enhanced-monitoring-and-observability-mastering-datadog-watchdog-ai-dynatrace-davis-ai-new-b55700b1263b)). **Layer coverage:** Detect only; execution ambitions live in Bits AI SRE (Section 5).

### New Relic AI

New Relic offers anomaly detection, suggested root causes, and a GenAI chat interface, plus AI-app observability ([Better Stack comparison, 2026](https://betterstack.com/community/comparisons/datadog-vs-newrelic/)). Its notable 2025 move: at Microsoft Ignite (Nov 2025) it shipped an **MCP server so the Azure SRE Agent can pull New Relic telemetry** during automated investigations ([New Relic press release, 18 Nov 2025](https://newrelic.com/press-release/20251118)). That is, New Relic chose to be a *data source for someone else's executing agent* — a telling positioning. **Layer coverage:** Detect/Diagnose.

### Splunk ITSI (Cisco)

Splunk IT Service Intelligence provides service-health KPIs, ML-based **adaptive thresholds** recalculated nightly, predictive analytics, and (2025) "Event iQ" AI-driven event correlation ([Splunk docs, 2025](https://help.splunk.com/en/splunk-it-service-intelligence/splunk-it-service-intelligence/visualize-and-assess-service-health/4.18/advanced-thresholding/create-adaptive-kpi-thresholds-in-itsi); [Splunk community, 2025](https://community.splunk.com/t5/Community-Blog/Cisco-Use-Cases-ITSI-Best-Practices-and-More-New-Articles-from/ba-p/700810)). **Layer coverage:** Detect/Diagnose; execution requires wiring into SOAR/ITSM tooling.

### Elastic Observability

Elastic ships zero-config ML anomaly detection on logs/metrics/traces and an **Observability AI Assistant** (RAG over the customer's own telemetry and knowledge base) ([Elastic](https://www.elastic.co/observability/aiops); [Elastic docs](https://www.elastic.co/docs/solutions/observability/ai/observability-ai-assistant)); it was named a Leader in the 2025 Gartner MQ for Observability Platforms ([Elastic blog, 2025](https://www.elastic.co/blog/elastic-leader-gartner-magic-quadrant-observability-platforms-2025)). **Layer coverage:** Detect/Diagnose + conversational assist. Notably, its assistant already does RAG over a customer knowledge base — but it answers questions; it doesn't execute.

### IBM Cloud Pak for AIOps

IBM's enterprise AIOps suite ingests events from 90+ tools, correlates incidents, and — unusually for gen-1 — includes **runbook automation** that can execute predefined remediation steps, with a claimed up-to-50% MTTR reduction (vendor-claimed) ([IBM](https://www.ibm.com/products/cloud-pak-for-aiops); [IBM features](https://www.ibm.com/products/cloud-pak-for-aiops/features)). **Layer coverage:** Detect/Diagnose plus scripted Execute; the runbooks are still human-authored and static — no learning loop.

**Gen-1 verdict:** these platforms answer "*what is broken and probably why*." Their nearly universal stopping point is the keyboard: the fix is a recommendation in a console, and any execution is a hand-off to pre-scripted workflows the customer must build and maintain.

---

## 3. Generation 2 — Runbook & process automation: hands without a brain

### PagerDuty Process Automation (Rundeck)

PagerDuty acquired Rundeck in **October 2020 for ~$100M** to add "auto-remediation and self-healing" to incident response ([PagerDuty, 2020](https://www.pagerduty.com/newsroom/pagerduty-to-aquire-rundeck/)). Today it sells Runbook Automation (SaaS/self-hosted) and **Automation Actions** — push-button diagnostics/remediations attached to PagerDuty services ([PagerDuty docs](https://support.pagerduty.com/main/docs/automation-actions)). PagerDuty's own marketing claims that done right, **40–60% of common incidents never need human escalation** and customers see up to 50% faster response ([PagerDuty/DevOpsil, 2026](https://devopsil.com/articles/2026-04-27-runbook-automation-with-pagerduty-and-rundeck-for-faster-mtt)) — vendor-claimed. PagerDuty AIOps (the noise-reduction layer) is licensed **per accepted event, from ~$699/month** base ([PagerDuty pricing](https://www.pagerduty.com/pricing/aiops/); [Spendflo guide](https://www.spendflo.com/blog/pagerduty-pricing-guide)).

### Shoreline.io → Nvidia

Shoreline — founded 2019 by ex-AWS Aurora GM Anurag Gupta, raised ~$57M (Insight, Dawn, Canvas) — built exactly "detect the incident, run the remediation loop across the fleet." It was **acquired by Nvidia in mid-2024 for ~$100M** ([SiliconANGLE, June 2024](https://siliconangle.com/2024/06/19/nvidia-reportedly-acquires-incident-automation-startup-shoreline-100m/); [Bloomberg, 2024](https://www.bloomberg.com/news/articles/2024-06-18/nvidia-agrees-deal-to-buy-software-startup-shoreline)) and its product disappeared into Nvidia's internal ops. Lesson: a pure remediation-automation startup, pre-LLM-agents, exited small — the standalone category never got big, but the *capability* was valuable enough for Nvidia to buy for itself.

### StackStorm

The open-source "IFTTT for Ops" (rules engine + workflows + 160 integration packs / 6,000+ actions), transitioned to the Linux Foundation by Extreme Networks in 2019 and still maintained ([GitHub](https://github.com/StackStorm/st2); [PR Newswire, 2019](https://www.prnewswire.com/news-releases/extreme-networks-transitions-stackstorm-to-the-linux-foundation-300931607.html)). It proves the event→rule→action pattern works technically; it also proves that pattern alone doesn't create a big company.

### Ansible / Event-Driven Ansible (Red Hat)

Event-Driven Ansible consumes observability events, matches conditional rules, and fires remediation playbooks; Red Hat markets it explicitly as the path to "self-healing infrastructure," with Insights detecting issues and AAP applying remediations, and 2025's AAP 2.6 adding AI-assisted features and Lightspeed integration ([Red Hat](https://www.redhat.com/en/technologies/management/ansible/event-driven-ansible); [Red Hat blog, 2025](https://www.redhat.com/en/blog/2025-red-hat-ansible-automation-platform-year-review)). Still fundamentally rules + human-authored playbooks.

### AWS Systems Manager Automation & Azure Automation

Both hyperscalers ship the plumbing: CloudWatch alarm → EventBridge rule → SSM Automation runbook is AWS's canonical self-healing pattern ([AWS blog](https://aws.amazon.com/blogs/mt/use-amazon-eventbridge-rules-to-run-aws-systems-manager-automation-in-response-to-cloudwatch-alarms/); [AWS docs](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-automation.html)); Azure Automation offers PowerShell/Python runbooks similarly ([Microsoft Learn](https://learn.microsoft.com/en-us/azure/automation/overview)). Free-ish and ubiquitous, yet most orgs use only a handful of stock runbooks — selection ("which fix applies to *this* incident?") remains human.

### ServiceNow Flow Designer / Workflow

ServiceNow's low-code Flow Designer automates ITSM processes (approvals, routing, provisioning). It is deterministic workflow automation; its agentic layer arrived only with 2025's releases (Section 4).

### Why scripted auto-remediation stayed niche

This is the crucial industry history for our pitch. Two decades of runbook automation produced real but narrow adoption, because:

1. **Brittle matching and stale runbooks.** Matcher rules that pick which runbook to fire degrade as systems change; runbooks reference deprecated commands and dead dashboards, so "engineers learn to ignore runbooks they can't trust" ([incident.io](https://incident.io/blog/automated-runbook-guide); [SRE School, 2026](https://sreschool.com/blog/operational-runbook/)).
2. **Cascading failures at machine speed.** Automations don't know about each other. Canonical disasters cited across the literature: Knight Capital's **$440M loss in 45 minutes** (2012, deployment automation + dead code path), the 2017 **AWS S3 four-hour outage** (an automated capacity-removal command removed too many nodes), and Facebook's 2021 six-hour global outage (config push → BGP withdrawal that locked out the recovery tooling) ([RubixKube, 2025](https://rubixkube.ai/blog/aiops-auto-remediation-memory-failure)).
3. **No memory, no learning.** "Most automation runs without a model of system state, change history, or downstream dependencies — when something unusual happens, automation amplifies it instead of catching it" ([RubixKube, 2025](https://rubixkube.ai/blog/aiops-auto-remediation-memory-failure)). Scripts execute; they never get wiser.
4. **Maintenance burden.** Every scripted remediation is code someone must own, test and update; the library rots faster than it grows.
5. **Audit/compliance pain.** Machine-speed auto-actions without a recorded "why" make SOC 2 reviews painful — "auditors do not love 'the system did it'" ([RubixKube, 2025](https://rubixkube.ai/blog/aiops-auto-remediation-memory-failure)). This is why approval gates + audit trails are not a nice-to-have but the adoption unlock.

---

## 4. Generation 3a — ITSM & enterprise AI agents

### ServiceNow: the 800-lb gorilla

- **Product:** Now Assist (GenAI across modules) plus, from the 2025 **Zurich release**, genuinely agentic constructs: an **AI Agent Orchestrator**, **Agentic Playbooks** (AI-executed workflows with human-in-the-loop exception routing), and for IT operations specifically an **"AIOps AI Specialist"** agent that autonomously monitors, triages and resolves infrastructure/application alerts, with a companion **remediation agent** that "automatically identifies and executes the appropriate remediation subflow for an alert" ([ServiceNow community/docs, 2025](https://www.servicenow.com/docs/r/zurich/it-operations-management/now-assist-for-it-operations-management/install-now-assist-ai-agents-itom.html); [CIO.com, 2025](https://www.cio.com/article/4054799/servicenow-zurich-release-introduces-agentic-ai-to-the-platform.html); [Kanini, 2025](https://kanini.com/blog/servicenow-zurich-release-for-agentic-enterprise/)). Note the limitation: the remediation agent *selects among pre-built subflows* — the execution vocabulary is still deterministic ServiceNow workflows.
- **Traction:** Now Assist surpassed **$500M ACV in Q3 2025** and **$600M+ ACV for full-year 2025 (doubling YoY)**, with $1M+ Now Assist customers up >130% YoY, on track for a stated **$1B ACV target in 2026** ([Futu/ServiceNow Q3 call, 2025](https://news.futunn.com/en/post/64241484/servicenow-nowus-q3-earnings-call-assist-growth-exceeds-expectations-targeting); [CX Today, 2026](https://www.cxtoday.com/service-management-connectivity/servicenow-ai-adoption-q4-growth/)).
- **Pricing:** never public. From **9 April 2026** ServiceNow reorganised everything into three AI-bundled tiers — **Foundation** (GenAI summarisation/insights), **Advanced** (deterministic + agent-executed workflows), **Prime** (replace whole roles, e.g. L1 service desk), bundling AI Control Tower, Workflow Data Fabric and a new "Context Engine," with per-seat licences plus AI-token metering ([TechTarget, 2026](https://www.techtarget.com/searchitoperations/news/366641692/ServiceNow-AI-pricing-change-takes-on-enterprise-ROI-struggles)). TechTarget quotes ServiceNow SVP John Aisien mocking the old model: "You bought the car, but, oh, you want a steering wheel?" — an admission the previous à-la-carte AI pricing hurt ROI perception.
- **Moveworks:** announced March 2025 at **$2.85B** (ServiceNow's largest deal ever), hit a **DOJ antitrust second request** in July 2025 ([TechCrunch, 2025](https://techcrunch.com/2025/07/18/servicenows-acquisition-of-moveworks-is-reportedly-being-reviewed-over-antitrust-concerns/)), and **closed 15 December 2025** ([Moveworks press release](https://www.moveworks.com/us/en/company/news/press-releases/servicenow-completes-acquisition-of-moveworks); [CX Today](https://www.cxtoday.com/crm/servicenow-moveworks-acquisition/)). Moveworks' value was the employee-facing agent that *actually resolves* IT requests (password resets, access grants, software provisioning) — i.e., admin-fix execution for the service-desk domain. That ServiceNow paid $2.85B for it is the single strongest comp for "executing documented admin fixes is worth a lot."

### Salesforce Agentforce

Relevant mostly as a pricing/adoption cautionary tale: three pricing models in ~18 months — **$2/conversation** at launch (2024), **Flex Credits at $0.10/action** (May 2025), then **per-user licences from ~$125/month** under an "Agentic Enterprise License Agreement" (late 2025) — because adoption was tepid: of ~5,000 early Agentforce deals only ~3,000 were paid, and by May 2025 only ~8,000 of 150,000+ Salesforce customers had adopted ([SaaStr, 2025](https://www.saastr.com/salesforce-now-has-3-pricing-models-for-agentforce-and-maybe-right-now-thats-the-way-to-do-it/); [Monetizely](https://www.getmonetizely.com/blogs/the-doomed-evolution-of-salesforces-agentforce-pricing)). Lesson for us: usage-priced agents create ROI anxiety; buyers want predictable pricing tied to outcomes.

### Atlassian Rovo

Atlassian went the opposite way on pricing: Rovo (search, chat, agents over Jira/Confluence) became **included in all paid cloud plans** through 2025, metered by included credits (25/70/150 credits per user/month on Standard/Premium/Enterprise) with overage billing not yet enforced ([Atlassian support](https://support.atlassian.com/rovo/kb/understand-rovo-billing-and-managing-costs-in-atlassian-cloud/); [TechTarget, 2025](https://www.techtarget.com/searchitoperations/news/366622263/Atlassian-Rovo-pricing-shifts-amid-AI-adoption-struggles)). Rovo agents read/write Jira and Confluence — knowledge-work actions, not infrastructure remediation.

### Aisera → Automation Anywhere

Aisera sold "agentic service desk" auto-resolution: customers including Autodesk, McAfee and Lifescan documented **65–89% auto-resolution rates** on incoming support requests (vendor-published case numbers), across 75M+ end users; it raised $164.5M (Series D $90M, Goldman Sachs/Thoma Bravo, 2022) and was **acquired by Automation Anywhere on 4 Nov 2025** ([Automation Anywhere press release](https://www.automationanywhere.com/company/press-room/automation-anywhere-acquires-aisera-supercharge-autonomous-enterprise); [Aisera, 2022](https://aisera.com/press-releases/90m-series-d-funding/)). Aisera's pitch that "up to 40% fewer ITSM seats are needed" is vendor-claimed.

### Espressive → Resolve

Espressive's Barista virtual agent (80–85% employee adoption, 50–70% help-desk call deflection, vendor-claimed) was **acquired by Resolve (agentic automation/orchestration vendor) on 10 Sep 2025** to power its "Zero Ticket IT" mission ([Resolve, 2025](https://resolve.io/news/resolve-acquires-espressive); [PRWeb](https://www.prweb.com/releases/resolve-acquires-espressive-a-leader-in-conversational-ai-for-the-enterprise-to-accelerate-its-zero-ticket-it-mission-302551496.html)). Pattern: every independent ITSM-AI-agent vendor of scale was bought in 2025.

**Gen-3a verdict:** ITSM agents *do* execute admin fixes — but almost exclusively for **employee-facing service-desk requests** (password, access, provisioning) inside the ITSM suite. The **ops/incident-facing** version of the same idea — execute the documented fix for a production incident from the org's operational knowledge — is much less served.

---

## 5. Generation 3b — Observability & incident vendors bolting on agents (2025–2026)

### Microsoft Azure SRE Agent — the reference architecture

GA'd in late 2025 and the closest public analogue to our product. From [Microsoft's docs (updated June 2026)](https://learn.microsoft.com/en-us/azure/sre-agent/overview):

- On alert, it queries monitoring tools, correlates changes (e.g., links a memory trend to a GitHub deployment), proposes mitigations (restart pod, adjust HPA), and files the ticket — the on-call engineer **approves with a single action**.
- Two autonomy levels: **Review mode** (diagnose, then act only after approval) and **Autonomous mode** ([Microsoft Learn, incident management](https://learn.microsoft.com/en-us/azure/sre-agent/incident-management)).
- A **permission gate** evaluates *every proposed tool call* pre-execution — human approval, policy rules, or blocks — with **audit telemetry routed to the customer's own App Insights** for compliance.
- **"Knowledge that never leaves":** every investigation persists root causes, resolution steps and team preferences — explicitly the "operational memory" concept.
- Extensible via skills, subagents, Python tools, MCP connectors (Datadog, Splunk, Dynatrace, CloudWatch…), and agent hooks.
- Microsoft claims **35,000+ incidents handled autonomously and 50,000+ developer-hours saved internally** ([Azure product page, 2025](https://azure.microsoft.com/en-us/products/sre-agent)) — vendor-claimed, first-party workloads.
- Pricing: **Azure Agent Units (AAU)** at ~**$0.10/AAU** in US regions; a fixed always-on cost of **4 AAU/agent-hour** (~$0.40/hr ≈ ~$290/month per always-on agent) plus token-metered active-flow charges ([Microsoft Learn pricing](https://learn.microsoft.com/en-us/azure/sre-agent/pricing-billing); [Azure pricing](https://azure.microsoft.com/en-us/pricing/details/sre-agent/)).
- **Gap for our thesis:** it is Azure-centric (executes Azure CLI-shaped actions on Azure resources), English-only, and its knowledge accrues from its own investigations — it does not start from an org's *existing* ops manuals/KB, and it does nothing for the vast estate of non-Azure enterprise apps (SaaS admin consoles, legacy on-prem systems) where Disney+-style config fixes live.

### Datadog Bits AI SRE

Launched at DASH June 2025, **GA in late 2025** as Datadog's first generally available AI agent ([Datadog investor release](https://investors.datadoghq.com/news-releases/news-release-details/datadog-launches-bits-ai-sre-agent-resolve-incidents-faster); [Datadog blog](https://www.datadoghq.com/blog/bits-ai-sre/)). It starts investigating autonomously the moment an alert fires — "by the time you get to your laptop… it has often already identified a likely root cause and even proposed a code fix" ([Datadog, 2025](https://www.datadoghq.com/blog/bits-ai-sre-deeper-reasoning/)). Pricing is unusually public: originally **$500/month for 20 "conclusive investigations"** (~$25 each; $36 on-demand), moved in 2026 to an **AI Credits model ($500 per 500 credits, ~6.5 credits ≈ ~$6.50 per average investigation** — a 74–82% effective price cut, suggesting price discovery/adoption pressure) ([NoBS, 2026](https://www.nobs.tech/blog/datadog-bits-ai-pricing-ai-credits-governance); [struct.ai, 2026](https://blog.struct.ai/datadog-bits-ai-pricing-2026/)). **Gap:** investigation-first; remediation output is a recommendation or *code fix PR*, not gated admin execution, and it's confined to the Datadog data universe.

### PagerDuty AI agent suite

Fall 2025: PagerDuty launched what it calls the "industry's first end-to-end AI agent suite" — SRE Agent, Scribe Agent, Shift Agent, Insights Agent — claiming up to 50% faster resolution (vendor-claimed) ([PagerDuty newsroom, 2025](https://www.pagerduty.com/newsroom/2025-fall-productlaunch/)). The **SRE Agent** is the most on-point comp: it "learns from related incidents, automatically surfaces context, recommends and **executes diagnostics and remediations** [with human approval]" and — critically — **generates self-updating runbooks** ([PagerDuty blog, 2025](https://www.pagerduty.com/blog/ai/we-built-an-sre-agent-with-memory-and-its-transforming-incident-response/)). PagerDuty's own writeup says customers found **memory "make or break"**: "siloed knowledge was the hidden catalyst behind their biggest inefficiencies." It also announced a December 2025 early-access integration where its SRE Agent collaborates with Azure's ([PagerDuty blog](https://www.pagerduty.com/blog/ai/pagerduty-azure-ai-sre-agent/)). **Gap:** execution rides on PagerDuty's automation stack (Rundeck lineage) — i.e., the actions still need to exist as runbooks/automation jobs; the learning loop generates runbooks but the enterprise-app admin-console world is out of scope.

### incident.io AI SRE

Launched 2 July 2025; London-based incident.io raised a **$62M Series B (April 2025, Insight Partners, ~$400M valuation, $95.4M total per TechCrunch)** ([Clay dossier](https://www.clay.com/dossier/incidentio-funding); [Insight Partners](https://www.insightpartners.com/ideas/incidentio-leadership-story/)). AI SRE triages alerts, correlates code changes/dashboards/past incidents, drafts post-mortems, claims **up to 80% MTTR/downtime reduction** (vendor-claimed), emphasises "surfaces evidence, not guesses," and its execution modality is **generating pull requests** ([incident.io, 2025](https://incident.io/blog/introducing-ai-sre)). **Gap:** code-fix-centric — the opposite of the Disney+ observation that most enterprise fixes are admin/config, not code.

### Rootly

YC-backed incident-management platform (Series A **$12M, Aug 2023**, Renegade Partners + Google's Gradient Ventures; ~$15.2M total) now marketing itself "AI-native" with AI SRE agents for automated RCA and suggested fixes ([TechCrunch, 2023](https://techcrunch.com/2023/08/10/incident-response-management-platform-rootly-secures-12m/); [Rootly](https://rootly.com/)). Smaller, but its public "AI SRE guide" is a useful honest source on limits: LLMs "can produce hallucinated or overconfident explanations, particularly when telemetry is sparse," and outputs are nondeterministic, "requiring operators to verify hypotheses before taking action" ([Rootly AI SRE guide, 2026](https://rootly.com/ai-sre-guide)).

---

## 6. The coverage matrix — where every incumbent stops

| Vendor / product | Detect | Diagnose | Decide | Execute | Learn | The stopping point |
|---|---|---|---|---|---|---|
| BigPanda | ✅ | ✅ | partial (agentic 2025) | ❌ | ❌ | Recommends; hands execution to your tools |
| Moogsoft (Dell APEX) | ✅ | ✅ | ❌ | ❌ | ❌ | Correlation only |
| Dynatrace Davis | ✅ | ✅✅ | partial | pre-scripted workflows | ❌ | Executes only customer-authored workflows, own-telemetry world |
| Datadog Watchdog | ✅ | partial | ❌ | ❌ | ❌ | Anomaly flags |
| New Relic AI | ✅ | ✅ | ❌ | ❌ | ❌ | Feeds other agents via MCP |
| Splunk ITSI | ✅ | ✅ | ❌ | ❌ | ❌ | Correlation/prediction |
| Elastic | ✅ | ✅ | ❌ | ❌ | ❌ | RAG assistant answers, doesn't act |
| IBM Cloud Pak AIOps | ✅ | ✅ | partial | scripted runbooks | ❌ | Static runbook library |
| Rundeck / SSM / Azure Automation / StackStorm / Ansible EDA | ❌ | ❌ | ❌ | ✅ (pre-scripted) | ❌ | No intelligence; brittle matchers; humans pick the job |
| ServiceNow Zurich agents + Moveworks | ✅ (in-platform) | ✅ | ✅ | ✅ *within ServiceNow subflows / service-desk requests* | partial | Execution vocabulary = ServiceNow workflows; ops-side fixes outside the platform untouched; opaque pricing |
| Salesforce Agentforce | — | — | ✅ | ✅ (CRM domain) | partial | Wrong domain; pricing churn |
| Azure SRE Agent | ✅ | ✅ | ✅ (approval gate) | ✅ Azure resources | ✅ | **Azure-only**; learns from own runs, not org's existing KB |
| Datadog Bits AI SRE | ✅ | ✅✅ | partial | ❌ (proposes code fix) | partial | Investigation product; Datadog data universe |
| PagerDuty SRE Agent | ✅ | ✅ | ✅ (approval) | via runbook stack | ✅ (self-updating runbooks) | Actions must exist as automation jobs |
| incident.io AI SRE | ✅ | ✅ | partial | PRs (code) | partial | Code-fix centric |

**The white space, stated precisely:** an agent that (a) starts from the organisation's *existing documented operational knowledge* (manuals, KB articles, past-ticket resolutions — the Disney+ binder), (b) executes **admin/config remediations across arbitrary enterprise systems** (SaaS admin consoles, legacy apps, internal tools) rather than one cloud or one platform's workflow language, (c) with approval gates + rollback + audit by design, and (d) whose every execution enriches a proprietary operational memory. Each incumbent has 2–3 of these; none has all four, and none is oriented at the *legacy enterprise app* estate that Conduct AI's "Make Legacy Move" track targets.

---

## 7. Market sizing and the scepticism you must pre-empt

### Market numbers (all analyst-firm estimates; ranges disagree because definitions differ)

- **AIOps:** $11.08B (2025) → $14.44B (2026) at 30.2% CAGR ([Research and Markets, 2026](https://www.researchandmarkets.com/reports/5767606/aiops-market-report)); $18.95B in 2026 → $37.79B by 2031 ([Mordor Intelligence](https://www.mordorintelligence.com/industry-reports/aiops-market)); MarketsandMarkets' older figure was $11.7B (2023) → $32.4B (2028) ([MarketsandMarkets](https://www.marketsandmarkets.com/Market-Reports/aiops-platform-market-251128836.html)). Fortune Business Insights sits far lower ($2.23B in 2025) on a narrower definition ([FBI](https://www.fortunebusinessinsights.com/aiops-market-109984)) — a good illustration to cite when arguing these numbers are directional only.
- **ITSM:** ~$12.8–15.3B in 2025, ~15–17% CAGR to ~$28–30B by 2030 ([Mordor](https://www.mordorintelligence.com/industry-reports/information-technology-service-management-market); [Grand View Research](https://www.grandviewresearch.com/industry-analysis/it-service-management-market-report); [Fortune Business Insights](https://www.fortunebusinessinsights.com/itsm-market-109485)).
- **BigPanda's "$200B ITOps market"** ([BusinessWire, 2025](https://www.businesswire.com/news/home/20250528507389/en/BigPanda-Launches-Agentic-IT-Operations-to-Bring-Intelligent-Automation-to-the-%24200-billion-ITOps-Market)) is vendor marketing (it counts human labour spend, not software TAM) — but the labour-spend framing is actually the honest one for an agent that replaces manual ops work.

### Gartner's cold water (use these to show judges you know the failure modes)

- **">40% of agentic AI projects will be canceled by end of 2027"** due to escalating costs, unclear business value or inadequate risk controls (June 2025, poll of 3,412 orgs); Gartner also estimates **only ~130 of the thousands of self-described agentic-AI vendors are real**, the rest doing "agent washing" ([Gartner press release, 25 Jun 2025](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)). Same release, upside: **15% of day-to-day work decisions made autonomously by 2028** (from ~0% in 2024) and **33% of enterprise software with agentic AI by 2028**.
- **"By 2029, agentic AI will autonomously resolve 80% of common customer service issues without human intervention, leading to a 30% reduction in operational costs"** ([Gartner, March 2025](https://www.gartner.com/en/newsroom/press-releases/2025-03-05-gartner-predicts-agentic-ai-will-autonomously-resolve-80-percent-of-common-customer-service-issues-without-human-intervention-by-20290)).
- Gartner's long-standing AIOps line — "there is no future of IT operations that does not include AIOps" — dates to its Market Guide (2022-era; historical but still universally quoted) ([IBM summary](https://www.ibm.com/think/insights/gartner-market-guide-for-aiops-essential-reading-for-itops-and-sre)).

### Practitioner reality check

- **The SRE Report 2025 (Catchpoint, n=301):** median reported toil *rose* to 30% from 25% in 2024 — the report explicitly floats that "manual supervision of AI systems that are mostly right, or make subtle and hard-to-predict errors, can easily raise the operational load of a team" ([Catchpoint, 2025](https://www.catchpoint.com/learn/sre-report-2025)). Half-trustworthy AI is *negative* productivity; this is the strongest argument for verification, rollback and confidence-gated autonomy.
- Practitioner-facing reviews of AI-SRE tooling note the tools are "expensive and need quite a bit of training," and that LLM investigators produce "hallucinated or overconfident explanations" on sparse telemetry ([Fernando Duran, Medium, 2025](https://medium.com/@duran.fernando/the-complete-guide-to-ai-powered-sre-tools-hype-vs-reality-06520e81fe40); [Rootly AI SRE guide](https://rootly.com/ai-sre-guide)).

---

## 8. Implications for our project

1. **Position against the matrix, not against any one vendor.** One slide: gen-1 sees but can't act; gen-2 acts but can't think or learn; gen-3 thinks but acts only in its own walled garden (Azure resources, ServiceNow subflows, Datadog investigations, code PRs). We close the loop on **documented admin fixes for legacy/enterprise systems** — the layer everyone skipped, and exactly Conduct AI's "Make Legacy Move" brief.
2. **Steal Azure SRE Agent's trust architecture vocabulary** — Review vs Autonomous modes, a permission gate on every tool call, audit telemetry to the customer's own store ([Microsoft Learn, 2026](https://learn.microsoft.com/en-us/azure/sre-agent/overview)). Judges who know the space will recognise it as best practice; our differentiation is *what* we execute (KB-documented admin fixes anywhere) not *how* we gate it.
3. **Lead with the knowledge-base grounding.** No incumbent starts from the org's existing ops manual; they learn only from their own runs. Retrieval from the customer's proprietary runbook/KB is (a) instantly demoable, (b) an answer to hallucination concerns ("we only execute *documented* fixes"), and (c) the moat: PagerDuty's own customers called memory "make or break" ([PagerDuty, 2025](https://www.pagerduty.com/blog/ai/we-built-an-sre-agent-with-memory-and-its-transforming-incident-response/)).
4. **Pre-empt the Gartner 40% stat before judges raise it.** Our design directly targets the three cited kill-reasons: cost (small per-incident footprint vs always-on agents), unclear value (MTTR delta measurable per incident), inadequate risk controls (approval gates, rollback, audit trail as first-class primitives).
5. **Pricing narrative:** Datadog's ~$25→~$6.50 per-investigation price collapse and Salesforce's three pricing models in 18 months show buyers reject opaque usage pricing; ServiceNow's April 2026 re-bundle shows the same from the other direction. A per-resolved-incident or flat-per-service price with a visible ROI counter is the credible story.
6. **Use the acquisition tape as exit/validation evidence:** Moveworks $2.85B (closed Dec 2025), Aisera→Automation Anywhere (Nov 2025), Espressive→Resolve (Sep 2025), Shoreline→Nvidia ~$100M (2024), Moogsoft→Dell (2023), BigPanda's $1.2B valuation (Jan 2022). Every layer of this stack gets bought; the unbought layer is the one we're building.

---

## Sources

- [Gartner press release, 25 Jun 2025](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027) — >40% agentic-AI project cancellations by 2027; ~130 "real" agentic vendors; 15%/33% 2028 predictions.
- [Gartner press release, 5 Mar 2025](https://www.gartner.com/en/newsroom/press-releases/2025-03-05-gartner-predicts-agentic-ai-will-autonomously-resolve-80-percent-of-common-customer-service-issues-without-human-intervention-by-20290) — 80% of common customer-service issues autonomously resolved by 2029.
- [Microsoft Learn — Azure SRE Agent overview, updated Jun 2026](https://learn.microsoft.com/en-us/azure/sre-agent/overview) — approval model, permission gate, knowledge persistence, integrations.
- [Microsoft Learn — Azure SRE Agent incident management](https://learn.microsoft.com/en-us/azure/sre-agent/incident-management) — Review vs Autonomous modes.
- [Microsoft Learn — Azure SRE Agent pricing](https://learn.microsoft.com/en-us/azure/sre-agent/pricing-billing) and [Azure pricing page](https://azure.microsoft.com/en-us/pricing/details/sre-agent/) — AAU model, ~$0.10/AAU, 4 AAU/agent-hour.
- [Azure SRE Agent product page](https://azure.microsoft.com/en-us/products/sre-agent) — 35,000+ incidents / 50,000+ hours (vendor-claimed).
- [Datadog Bits AI SRE launch blog](https://www.datadoghq.com/blog/bits-ai-sre/) and [investor release](https://investors.datadoghq.com/news-releases/news-release-details/datadog-launches-bits-ai-sre-agent-resolve-incidents-faster) — autonomous investigation agent, 2025 launch/GA.
- [NoBS on Datadog Bits AI pricing, 2026](https://www.nobs.tech/blog/datadog-bits-ai-pricing-ai-credits-governance) and [struct.ai analysis](https://blog.struct.ai/datadog-bits-ai-pricing-2026/) — $500/20 investigations → AI Credits (~$6.50/investigation).
- [PagerDuty Fall 2025 launch](https://www.pagerduty.com/newsroom/2025-fall-productlaunch/) — end-to-end AI agent suite, up-to-50%-faster claims.
- [PagerDuty "SRE agent with memory" blog, 2025](https://www.pagerduty.com/blog/ai/we-built-an-sre-agent-with-memory-and-its-transforming-incident-response/) — memory "make or break"; self-updating runbooks; approval-gated remediation.
- [PagerDuty + Azure SRE Agent integration blog](https://www.pagerduty.com/blog/ai/pagerduty-azure-ai-sre-agent/) — cross-vendor agent collaboration (EA Dec 2025).
- [PagerDuty Rundeck acquisition, 2020](https://www.pagerduty.com/newsroom/pagerduty-to-aquire-rundeck/) and [Automation Actions docs](https://support.pagerduty.com/main/docs/automation-actions) — runbook-automation lineage.
- [PagerDuty AIOps pricing](https://www.pagerduty.com/pricing/aiops/) and [Spendflo pricing guide](https://www.spendflo.com/blog/pagerduty-pricing-guide) — per-event licensing, ~$699/mo base.
- [incident.io "AI SRE has entered the chat", Jul 2025](https://incident.io/blog/introducing-ai-sre) — capabilities, evidence-first framing, 80% claims (vendor-claimed).
- [Clay — incident.io funding](https://www.clay.com/dossier/incidentio-funding) and [Insight Partners](https://www.insightpartners.com/ideas/incidentio-leadership-story/) — $62M Series B (Apr 2025), ~$400M valuation.
- [incident.io automated runbook guide](https://incident.io/blog/automated-runbook-guide) — brittle matchers, stale-runbook distrust.
- [RubixKube — why auto-remediation without memory fails, 2025](https://rubixkube.ai/blog/aiops-auto-remediation-memory-failure) — cascading automation failures (Knight Capital 2012, AWS S3 2017, Facebook 2021 — historical), memory/audit arguments.
- [TechCrunch — Rootly $12M Series A, 2023](https://techcrunch.com/2023/08/10/incident-response-management-platform-rootly-secures-12m/) and [Rootly AI SRE guide](https://rootly.com/ai-sre-guide) — funding; candid AI-SRE limitations.
- [Moveworks press release — acquisition completed 15 Dec 2025](https://www.moveworks.com/us/en/company/news/press-releases/servicenow-completes-acquisition-of-moveworks) and [ServiceNow announcement, Mar 2025](https://newsroom.servicenow.com/press-releases/details/2025/ServiceNow-to-extend-leading-agentic-AI-to-every-employee-for-every-corner-of-the-business-with-acquisition-of-Moveworks-03-10-2025-traffic/default.aspx) — $2.85B deal.
- [TechCrunch — DOJ review of Moveworks deal, Jul 2025](https://techcrunch.com/2025/07/18/servicenows-acquisition-of-moveworks-is-reportedly-being-reviewed-over-antitrust-concerns/) — antitrust second request.
- [Futu — ServiceNow Q3 2025 earnings call](https://news.futunn.com/en/post/64241484/servicenow-nowus-q3-earnings-call-assist-growth-exceeds-expectations-targeting) and [CX Today, 2026](https://www.cxtoday.com/service-management-connectivity/servicenow-ai-adoption-q4-growth/) — Now Assist $500M→$600M+ ACV, $1B 2026 target.
- [TechTarget — ServiceNow AI pricing change, 2026](https://www.techtarget.com/searchitoperations/news/366641692/ServiceNow-AI-pricing-change-takes-on-enterprise-ROI-struggles) — Foundation/Advanced/Prime tiers from 9 Apr 2026; analyst quotes.
- [CIO.com — Zurich release, 2025](https://www.cio.com/article/4054799/servicenow-zurich-release-introduces-agentic-ai-to-the-platform.html) and [ServiceNow Zurich ITOM docs](https://www.servicenow.com/docs/r/zurich/it-operations-management/now-assist-for-it-operations-management/install-now-assist-ai-agents-itom.html) — AIOps AI Specialist, remediation agent, Agentic Playbooks.
- [SaaStr — Agentforce's three pricing models, 2025](https://www.saastr.com/salesforce-now-has-3-pricing-models-for-agentforce-and-maybe-right-now-thats-the-way-to-do-it/) and [Monetizely analysis](https://www.getmonetizely.com/blogs/the-doomed-evolution-of-salesforces-agentforce-pricing) — $2/conversation → Flex Credits → per-user; tepid adoption stats.
- [Atlassian — Rovo billing](https://support.atlassian.com/rovo/kb/understand-rovo-billing-and-managing-costs-in-atlassian-cloud/) and [TechTarget on Rovo pricing shift, 2025](https://www.techtarget.com/searchitoperations/news/366622263/Atlassian-Rovo-pricing-shifts-amid-AI-adoption-struggles) — bundled-with-credits model.
- [Automation Anywhere acquires Aisera, 4 Nov 2025](https://www.automationanywhere.com/company/press-room/automation-anywhere-acquires-aisera-supercharge-autonomous-enterprise) and [Aisera Series D, 2022](https://aisera.com/press-releases/90m-series-d-funding/) — acquisition; $90M Series D; 65–89% auto-resolution (vendor-claimed).
- [Resolve acquires Espressive, Sep 2025](https://resolve.io/news/resolve-acquires-espressive) — Barista deflection stats (vendor-claimed).
- [SiliconANGLE — Nvidia acquires Shoreline ~$100M, Jun 2024](https://siliconangle.com/2024/06/19/nvidia-reportedly-acquires-incident-automation-startup-shoreline-100m/) and [Bloomberg](https://www.bloomberg.com/news/articles/2024-06-18/nvidia-agrees-deal-to-buy-software-startup-shoreline) — Shoreline fate, ~$57M raised.
- [Dell acquires Moogsoft, Jul 2023](https://www.dell.com/en-us/dt/corporate/newsroom/announcements/detailpage.press-releases~usa~2023~07~dell-technologies-announces-intent-to-acquire-moogsoft.htm) and [SiliconANGLE](https://siliconangle.com/2023/07/20/dell-acquires-venture-backed-aiops-startup-moogsoft/) — deal + ~$93–95M raised.
- [BigPanda $190M at $1.2B, Jan 2022](https://www.globenewswire.com/news-release/2022/01/12/2365641/0/en/BigPanda-Raises-190-Million-in-Funding-at-1-2-Billion-Valuation.html); [agentic launch, May 2025](https://www.businesswire.com/news/home/20250528507389/en/BigPanda-Launches-Agentic-IT-Operations-to-Bring-Intelligent-Automation-to-the-%24200-billion-ITOps-Market); [Velocity acquisition, Nov 2025](https://www.businesswire.com/news/home/20251110426205/en/BigPanda-Acquires-Velocity-to-Accelerate-Leadership-in-Agentic-IT-Operations); [95% noise-reduction claim](https://www.bigpanda.io/blog/what-is-an-aiops-platform/).
- [Dynatrace preventive operations, Feb 2025](https://www.businesswire.com/news/home/20250204836622/en/Dynatrace-Advances-AIOps-with-Preventive-Operations) and [remediation-intelligence blog](https://www.dynatrace.com/news/blog/remediation-intelligence-accelerate-mttr-with-ai-powered-context-and-knowledge/) — Davis AI + automated remediation workflows.
- [New Relic press release, 18 Nov 2025](https://newrelic.com/press-release/20251118) — MCP server feeding Azure SRE Agent.
- [Splunk ITSI adaptive thresholds docs, 2025](https://help.splunk.com/en/splunk-it-service-intelligence/splunk-it-service-intelligence/visualize-and-assess-service-health/4.18/advanced-thresholding/create-adaptive-kpi-thresholds-in-itsi) — ML thresholding/predictive analytics.
- [Elastic AIOps page](https://www.elastic.co/observability/aiops), [AI Assistant docs](https://www.elastic.co/docs/solutions/observability/ai/observability-ai-assistant), [2025 Gartner MQ Leader blog](https://www.elastic.co/blog/elastic-leader-gartner-magic-quadrant-observability-platforms-2025) — Elastic capabilities/positioning.
- [IBM Cloud Pak for AIOps](https://www.ibm.com/products/cloud-pak-for-aiops) and [features page](https://www.ibm.com/products/cloud-pak-for-aiops/features) — runbook automation, up-to-50% MTTR claim (vendor-claimed).
- [StackStorm GitHub](https://github.com/StackStorm/st2) and [Linux Foundation transition, 2019](https://www.prnewswire.com/news-releases/extreme-networks-transitions-stackstorm-to-the-linux-foundation-300931607.html) — OSS event-driven automation status.
- [Red Hat Event-Driven Ansible](https://www.redhat.com/en/technologies/management/ansible/event-driven-ansible) and [2025 year in review](https://www.redhat.com/en/blog/2025-red-hat-ansible-automation-platform-year-review) — self-healing positioning.
- [AWS blog — EventBridge + SSM Automation](https://aws.amazon.com/blogs/mt/use-amazon-eventbridge-rules-to-run-aws-systems-manager-automation-in-response-to-cloudwatch-alarms/) and [SSM Automation docs](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-automation.html); [Azure Automation overview](https://learn.microsoft.com/en-us/azure/automation/overview) — hyperscaler runbook plumbing.
- [Catchpoint SRE Report 2025](https://www.catchpoint.com/learn/sre-report-2025) — toil rose 25%→30%; AI-supervision burden.
- [Fernando Duran — AI-powered SRE tools: hype vs reality, 2025](https://medium.com/@duran.fernando/the-complete-guide-to-ai-powered-sre-tools-hype-vs-reality-06520e81fe40) — practitioner scepticism.
- [Research and Markets AIOps report, 2026](https://www.researchandmarkets.com/reports/5767606/aiops-market-report); [Mordor Intelligence AIOps](https://www.mordorintelligence.com/industry-reports/aiops-market); [MarketsandMarkets AIOps](https://www.marketsandmarkets.com/Market-Reports/aiops-platform-market-251128836.html); [Fortune Business Insights AIOps](https://www.fortunebusinessinsights.com/aiops-market-109984) — divergent AIOps market sizings.
- [Mordor ITSM](https://www.mordorintelligence.com/industry-reports/information-technology-service-management-market); [Grand View ITSM](https://www.grandviewresearch.com/industry-analysis/it-service-management-market-report); [Fortune Business Insights ITSM](https://www.fortunebusinessinsights.com/itsm-market-109485) — ITSM market sizings.
- [IBM on Gartner AIOps Market Guide](https://www.ibm.com/think/insights/gartner-market-guide-for-aiops-essential-reading-for-itops-and-sre) — "no future of IT operations that does not include AIOps" (2022-era, historical).
