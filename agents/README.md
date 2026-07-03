# Precedent — Fetch.ai agents (Watcher · Librarian · Operator)

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

Three **Agentverse mailbox agents** wrap Precedent's deterministic loop. They run on the
team laptop, connect **outbound** to Agentverse (no public IP, survive venue NAT), and
carry the frozen `precedent/contracts.py` models as a custom `PrecedentProtocol`. The
**Watcher** additionally speaks the **Agent Chat Protocol** (`publish_manifest=True`) — the
ASI:One entry point and the human approval gate.

| Agent | Role | Protocols |
|---|---|---|
| **Watcher** (`agents/watcher.py`) | Gateway + triage; `IncidentEvent → TriageResult` | Chat Protocol + `PrecedentProtocol` |
| **Librarian** (`agents/librarian.py`) | Retrieval + memory governance (ACL-filtered; **no LLM import**); `TriageResult → RetrievalBundle` | `PrecedentProtocol` |
| **Operator** (`agents/operator.py`) | Execution + Jira write-behind; approved `ExecutionPlan → ExecutionResult` | `PrecedentProtocol` |

Assessor and Auditor stay **in-process** by design — the deterministic safety kernel gains
nothing from a network hop. *"Inter-agent orchestration and the human approval gate ride
Fetch rails; the deterministic safety kernel deliberately does not."*

## Human registration runbook (the live step — code is already registerable)

The code builds each agent with a **stable address** derived from an env seed, so you can
register once and swap in the full handlers without the address changing. Steps:

1. **Fill `.env`** (never commit it): `AGENTVERSE_API_KEY`, `FETCH_AGENT_MAILBOX_KEY`, and a
   stable seed per agent — `WATCHER_AGENT_SEED`, `LIBRARIAN_AGENT_SEED`, `OPERATOR_AGENT_SEED`.
   Any high-entropy string works; keep it secret and stable (the address is derived from it).
2. **Print the addresses** (no network needed):
   `PRECEDENT_AGENTS_OFFLINE=1 .venv/bin/python -c "from agents.watcher import build_watcher; print(build_watcher().address)"`
   (same for `agents.librarian` / `agents.operator`). Record them in `.env` for cross-wiring.
3. **Run each agent** so it connects its mailbox to Agentverse:
   `.venv/bin/python -m agents.watcher` (then `agents.librarian`, `agents.operator`).
4. **On agentverse.ai**: confirm each agent appears under *Hosting → Mailbox agents*, paste
   the keyword-rich description (already in each module's `DESCRIPTION`), and confirm both
   badges above render on the agent's README panel.
5. **Discoverability is activity-gated** (≥10 interactions before ranking): run 10+ real test
   chats with the Watcher from a fresh ASI:One session, then re-test discovery.
6. **Redeem** the hackathon Agentverse credit code (`UKAIAGENTUKAIAGENTAV`) if not already.

Env vars to fill (names only — values live in `.env`, never here):
`AGENTVERSE_API_KEY`, `FETCH_AGENT_MAILBOX_KEY`, `WATCHER_AGENT_SEED`,
`LIBRARIAN_AGENT_SEED`, `OPERATOR_AGENT_SEED`, and (for cross-wiring) the three resulting
addresses. `ASI_ONE_API_KEY` / `ASI_ONE_BASE_URL` are used by the ASI:One capture session.

## Hosted degraded-L0 Watcher

`agents/watcher.py` (via the full loop) also supports a **hosted degraded-L0 mode**: without
MediaCo execution creds it still triages + retrieves against the **public** runbook corpus and
returns a risk-classified plan with an explicit *"no execution target configured — L0"* state.
This is the "agents that keep running" post-hackathon bonus; a human deploys it at G2.
