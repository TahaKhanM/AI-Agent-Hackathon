# T3-11 — Fetch agent registerability: verification + human paste-blocks

**Status: MET by T1's implementation — not duplicated by T3.**

The T3 brief assumed T1 would build only the Watcher and defer the Librarian + Operator
skeletons to T3. In fact **T1 built all three agents** (`agents/watcher.py`,
`agents/librarian.py`, `agents/operator.py`, plus `agents/common.py`, `agents/protocol.py`,
`agents/approval.py`, `agents/README.md`) as registerable Agentverse mailbox agents on branch
`build/t1-core-loop-sim-agents`. Per the "you MEASURE it, you never rebuild it" rule, T3 does
**not** add duplicate agent modules (that would collide on merge). T3 instead **verified** them
against the registerability contract and prepared the paste-ready Agentverse profile blocks below.

> These files land in `main` at the T1→main phase-boundary merge; register after that merge (or
> from T1's worktree). The addresses are derived from the env seeds, so they survive the merge.

## Verification evidence (run against T1's `agents/*.py`)

| Check | Result |
|---|---|
| Rule 1 — no closed-model id in `agents/` (`claude-\|openai-\|gpt-\|gemini-\|grok-\|mercury-`) | clean (0 hits) |
| Rule 4 — no inlined agent seed (every `seed=` uses `common.resolve_seed`, env-derived) | clean |
| `publish_manifest=True` on each agent | watcher ✓ (chat + protocol) · librarian ✓ · operator ✓ |
| Stable env seed per agent | `resolve_seed("watcher"/"librarian"/"operator")` → `WATCHER_/LIBRARIAN_/OPERATOR_AGENT_SEED` |
| `mailbox=common.use_mailbox()` (outbound; survives venue NAT) | all three |
| Chat Protocol (`chat_protocol_spec`) — ASI:One entry point | Watcher ✓ |
| `PrecedentProtocol` inter-agent messages | all three |
| Keyword-rich `DESCRIPTION` (discoverability) | all three (see paste-blocks) |
| Both badges + human registration runbook | present in `agents/README.md` |

Seed → address stability is the interlock guarantee: the human registers once with the env seeds
below; when T1's handlers are already in place, the address never changes, so the ≥10-interaction
discoverability clock does not reset.

## Env vars the human fills (names only — values live in `.env`, never committed)

`AGENTVERSE_API_KEY`, `FETCH_AGENT_MAILBOX_KEY`, `WATCHER_AGENT_SEED`, `LIBRARIAN_AGENT_SEED`,
`OPERATOR_AGENT_SEED`. (Any high-entropy string per seed; keep secret + stable.) The full
step-by-step runbook is in `agents/README.md` ("Human registration runbook").

## Paste-ready Agentverse profile blocks (badges + description per agent)

Paste each block into the corresponding agent's README panel on agentverse.ai so both badges
render on every agent profile:

### Watcher
```markdown
![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

Precedent Watcher — IT incident resolution and runbook automation. Report an incident (EPG
publish failure, duplicate schedule slot, VOD rights-window conflict, Jira ticket remediation)
and it retrieves your organisation's own documented fix, classifies risk deterministically, and
executes behind an approval gate with audit and rollback.
```

### Librarian
```markdown
![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

Precedent Librarian — permission-aware memory governance. Given a triaged incident class it
retrieves the organisation's own documented fix ONLY when the requesting principal is authorised,
enforcing Jira/ACL lineage as a deterministic bitmask conjunction (no LLM in the permission
decision). On a denial it discloses only how many remediations are hidden and which team owns
them — never the fix content. Fail-closed: uncertain freshness denies.
```

### Operator
```markdown
![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

Precedent Operator — typed-tool execution with audit and rollback. Given an approved (or
standing-approved) execution plan it runs the documented fix through typed tool calls only,
verifies the post-state, auto-restores the pre-state snapshot on failure, and records the
executed fix with provenance in a hash-chained audit log. A Jira write-behind queues a ticket
note without ever blocking the loop.
```
