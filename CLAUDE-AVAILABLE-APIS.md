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
  - Project: `MEDIA`
  - Project ID: `10001`
  - Service desk ID: `1`
  - Incident request type: `16` (`Report a system problem`)
  - Required request fields: `summary`, `description`
  - Optional fields: affected services `customfield_10044`, urgency `customfield_10049`, impact `customfield_10004`
  - Verified: auth works, request type fields work, and test issue `MEDIA-1` was created.
  - **Tier + ACL APIs verified (3 Jul session):** the site is on JSM **FREE** (`GET /rest/api/3/instance/license`) — the planned Standard trial was never provisioned, **and it turns out it isn't needed**: on Free, the full ACL-source surface works via API — project role create (roles `precedent-rights-ops`=10007 and `precedent-scheduling-ops`=10008 now created for real), role membership add/read/remove on MEDIA (200/200/204), permission scheme create/grant-add/delete (201/201/204), scheme read (MEDIA scheme id 10000, 126 grants). Caveat: Free may not enforce custom schemes in Jira's own UI — irrelevant to the demo, since Precedent enforces at its own retrieval layer and Jira is only the polled ACL source of truth.
  - Site has ONE human user (Taha). For the two-principal ACL demo: invite a 2nd free agent seat (JSM Free allows 3) or flip the single account between roles 10007/10008.

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
