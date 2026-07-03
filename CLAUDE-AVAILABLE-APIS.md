# APIs and tools available to Claude

Do not commit `.env` or print secret values. Load local credentials with:

```bash
set -a
source .env
set +a
```

## Ready now

- Jira Service Management Cloud
  - Site: `https://precedentlabs.atlassian.net`
  - Cloud ID: `05c417c1-4d11-41ff-862f-ed360c3342ed`
  - Auth mode: `basic_site` using Atlassian account email + API token.
  - Project: `MEDIA`
  - Project ID: `10001`
  - Service desk ID: `1`
  - Incident request type: `16` (`Report a system problem`)
  - Required request fields: `summary`, `description`
  - Optional fields: affected services `customfield_10044`, urgency `customfield_10049`, impact `customfield_10004`
  - Verified: auth works, request type fields work, and test issue `MEDIA-1` was created.
  - **Tier: JSM STANDARD (upgraded 3 Jul, verified live — `instance/license` → `PAID`).** The Free-tier enforcement caveat is gone. Full ACL-source surface verified via API across both sessions: project role create (roles `precedent-rights-ops`=10007 and `precedent-scheduling-ops`=10008 exist), role membership add/read/remove on MEDIA (200/200/204), permission scheme grant add/delete **on the live assigned scheme 10000** (201/204), scheme read (126 grants).
  - **NEW (Standard-only, created + verified 3 Jul): issue security.** Scheme **"Precedent Restricted Runbooks" (id 10000)** created and **associated with MEDIA**; levels: **"Rights Ops Only"=10000** (member: role 10007), **"Scheduling Ops Only"=10001** (member: role 10008). Setting/unsetting `security` on issues via `PUT /rest/api/3/issue/{key}` works (204); `SET_ISSUE_SECURITY` is already granted to Administrators/Service Desk Team. IDs recorded in `.env`. ⚠️ Enforcement propagation: role-membership changes take seconds to reflect in issue visibility (permission cache) — see working notes for the measured window.
  - **NEW (Standard, verified): Jira audit records API** — `GET /rest/api/3/auditing/record` returns the site audit log (593 records; permission-scheme and role events with ms timestamps). Use as the independent external clock for the drift/TTC bench and as audit-trail corroboration.
  - Site has ONE human user (Taha). For the two-principal ACL demo: invite a 2nd agent seat (covered by the Standard trial) or flip the single account between roles 10007/10008.

- Venice AI inference API
  - Base URL: `https://api.venice.ai/api/v1`
  - Key type: inference-only
  - Admin/key-management endpoints disabled.
  - Verified: `GET /models` returned `200` and 89 models.
  - **Open-weight verification DONE (3 Jul session)** — all four pinned models present on Venice AND have public, ungated Hugging Face weight repos (checked live). Evidence dumps committed: `docs/compliance/venice-models-2026-07-03.json`, `venice-models-all-2026-07-03.json`, `venice-models-embedding-2026-07-03.json`.
  - Pinned models (verified):
    - FAST: `qwen3-5-35b-a3b` (Qwen/Qwen3.5-35B-A3B, Apache-2.0)
    - SMART: `deepseek-v4-flash` (deepseek-ai/DeepSeek-V4-Flash, MIT)
    - HEAVY: `deepseek-v4-pro` (deepseek-ai/DeepSeek-V4-Pro, MIT)
    - EMBED: `text-embedding-bge-m3` (BAAI/bge-m3, MIT) — embedding models only appear under `GET /models?type=embedding`
  - Caution (verified live): Venice also serves closed models incl. `claude-fable-5`, `grok-4-3`, `gemini-3-5-flash`, and closed embedders `text-embedding-3-small/large` + `gemini-embedding-2-preview`. NOTE: closed models do NOT reliably have `modelSource = null` (grok/gemini/qwen-plus carry vendor-doc URLs) — the safe guard is asserting `modelSource` is a `huggingface.co` URL; the registry whitelist must cover embeddings too.
  - Fallback bench corrections: `llama-4-maverick` does NOT exist on Venice; `qwen-3-6-27b` is actually `qwen3-6-27b`. Verified present: `zai-org-glm-5-2` (MIT), `kimi-k2-7-code` (Moonshot licence "other"), `text-embedding-qwen3-0-6b`, `text-embedding-qwen3-8b`.

- ASI:One API
  - Base URL: `https://api.asi1.ai/v1`
  - Chat endpoint: `https://api.asi1.ai/v1/chat/completions`
  - Model configured: `asi1`
  - Key present in `.env`.
  - **Verified (3 Jul session): live chat completion succeeded** (model `asi1` responded).

- Fetch.ai Agentverse
  - Base URL: `https://agentverse.ai`
  - Network: `mainnet`
  - Agentverse token present in `.env` under the configured aliases.
  - **Verified (3 Jul session): token authenticates** (`GET /v1/hosting/agents` → 200; zero agents hosted — registration remains the front-loaded Friday task).
  - Planned agents:
    - `precedent-watcher`
    - `precedent-librarian`
    - `precedent-operator`
  - Still needed: create/register the agents, then fill seeds, addresses, profile URLs, mailbox key, and shared chat URL.

- Kaggle
  - API token present in `.env`.
  - Dataset slugs:
    - `shivamb/netflix-shows`
    - `shivamb/disney-movies-and-tv-shows`
  - Kaggle CLI is not installed in the local shell right now.
  - If using older Kaggle tooling, also fill `KAGGLE_USERNAME` and `KAGGLE_KEY`.

## Local dev tooling (set up + verified 3 Jul)

- Repo scaffolded: `pyproject.toml` (uv), `Makefile`, `.env.example` (Venice-only), `LICENSE` (MIT), `scripts/check_open_weight.sh`, package skeletons (`precedent/`, `precedent_memory/`, `sim/`, `console/`, `agents/`) with spec-pointing stubs, and `precedent/models.py` + `precedent_memory/schema.sql` + spec test skeletons already implemented.
- `uv` 0.11 present; `.venv` created (Python 3.13). `uv pip install -e ".[dev]"` resolves; `uv pip install -e ".[dev,agents]"` adds the Fetch rails.
- **`uagents` 0.25.2 verified on Python 3.13** — the Chat Protocol canonical import works; the agents worktree needs no separate runtime.
- `gitleaks` 8.30.1 installed; full-history scan run — **clean, no leaks** (repo safe to make public after the scrub gate).
- `make` targets: `check-open-weight` (rule-1 CI guard — passing), `test` (4 smoke pass / 9 spec skip), `secrets-scan`, `lint` (ruff clean); `sim`/`demo-reset`/`bench` are TODO stubs for the build teams.
- Project skill at `.claude/skills/precedent/SKILL.md` (the four hard rules + layout + gate discipline).
- MCP note: the MCP registry returned no matching connectors for github/jira here, and new authenticated MCPs can't be connected from a non-interactive session. The Playwright MCP is already connected (useful for console UI testing). If the team wants GitHub automation for the BasedAI PR, connect a GitHub MCP/token via an interactive `claude mcp` session — otherwise the PR stays a human task (owner T3, packet `Plan/workflows/T3-github-publication.md`).

## No-key public data/tools

- TVmaze schedule API: no auth required.
- UCI Incident Management Process Enriched Event Log: no auth required.
- Freeview-EPG XMLTV snapshot: no auth required.

## Missing or optional

- ~~`VENICE_EMBED_MODEL`~~ — pinned 3 Jul: `text-embedding-bge-m3` (verified open-weight, in `.env`).
- `JIRA_CHANGE_REQUEST_TYPE_ID`: optional unless demoing changes separately.
- `JIRA_RIGHTS_OPS_ROLE_ID=10007`, `JIRA_SCHEDULING_OPS_ROLE_ID=10008` — filled 3 Jul (roles created live).
- `JIRA_SCHEDULING_OPS_ACCOUNT_ID` and `JIRA_RIGHTS_OPS_ACCOUNT_ID`: still empty — requires inviting a 2nd user (15-min human task) or using the single-account role-flip fallback.
- Fetch agent seeds/mailbox key/profile URLs: needed after Agentverse agent setup.
- `ASI_ONE_SHARED_CHAT_URL`: capture after the final ASI:One demo conversation.
- GitHub token: not configured; only needed if Claude must push/open PRs (the BasedAI PR can be opened by a human instead).
