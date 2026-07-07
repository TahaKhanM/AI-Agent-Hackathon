The enterprise ops idea is an AI-native operational memory and execution layer for complex media ERP/workflow systems.

The wedge is media operations teams using tools like WhatsOn, Mydas, scheduling systems, rights systems, transmission workflows, content metadata tools, and internal admin/config platforms. In these environments, a large amount of operational work is repetitive but high-stakes: resolving tickets, changing configurations, checking schedules, validating metadata, routing approvals, interpreting KB articles, investigating incidents, and escalating only when the issue requires software engineering changes.

The core product is an autonomous enterprise operations agent that learns from every historical ticket, configuration change, approval, rollback, audit log, KB article, and operator action. Over time, it becomes the company’s operational memory system.

Technically, the system has four layers:

1. **Ingestion layer**
   It connects to ticketing systems, Slack/Teams, KB docs, admin panels, audit logs, config histories, ERP APIs, and approval workflows. It extracts structured operational knowledge: issue type, affected system, root cause, previous fix, permission required, risk level, rollback path, and final outcome.

2. **Operational memory layer**
   This is a domain-specific memory graph/vector store combining semantic retrieval with structured entities. It does not just store documents. It stores operational patterns:
   “when this type of scheduling error happens in WhatsOn, the likely cause is X, the safe config change is Y, approval from Z is needed, and rollback is R.”

3. **Reasoning and policy layer**
   The agent classifies each incoming issue by determinism and risk. Low-risk, high-determinism problems can be resolved automatically. Medium-risk actions require human approval. High-risk or code-level problems are routed to the correct engineering team with a full investigation summary. This layer enforces permissions, auditability, approval gates, and rollback constraints.

4. **Execution layer**
   The agent uses deterministic tools and APIs to perform allowed actions: update configs, attach evidence to tickets, request approvals, apply known fixes, run validation checks, generate rollback plans, and close tickets once verified. Every action is logged with the evidence, reasoning trace, approver, system state before/after, and rollback option.

The moat is the proprietary operational memory. Generic enterprise AI tools can answer questions from docs, but they do not accumulate a company-specific map of how incidents, approvals, config changes, and resolutions actually happen in production. The more the system is used, the more valuable it becomes because it learns the organisation’s real operational behaviour.

The first vertical is media ERP because operations are workflow-heavy, configuration-heavy, audit-sensitive, and often rely on legacy systems. A lot of work is stuck between support, operations, and engineering. The agent starts by assisting with triage and knowledge retrieval, then moves into approved execution for high-confidence issues, and eventually becomes the autonomous operations layer for the enterprise.

The simplest version of the thesis is:

We are building the AI brain for enterprise operations: a closed-loop operational memory and execution system that learns from every ticket, approval, audit log, and configuration change, then safely resolves future operational incidents with deterministic tool use, human approval gates, and full rollback/auditability.