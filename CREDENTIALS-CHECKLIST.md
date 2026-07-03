# Precedent credentials and hackathon credits checklist

As of 3 July 2026. This file is for briefing a coding agent such as Claude. Do not paste actual secret values into this file or commit a filled `.env`.

## Build target

The project plan targets three tracks:

- Conduct: primary product/demo track. No sponsor API key required.
- Fetch.ai: must register agents on Agentverse, use Agent Chat Protocol, and show the workflow in ASI:One.
- BasedAI: must use open-weight models only and ship the permission-aware memory layer. Do not use OpenAI, Anthropic, Gemini, Grok, or other closed/proprietary runtime models in the submitted pipeline.

## Required for Claude to build the project

### 1. Venice AI model API

Use this for hosted open-weight LLM and embedding calls.

Claim:

- API credits: sign up at https://venice.ai/settings/api and redeem the hackathon code from the guide: `IMPERIAL50X` (older code listed: `IMPERIAL50`).
- Optional Venice Pro: redeem `IMPERIAL` after claiming API credits.

Give Claude these values locally in `.env`:

```env
VENICE_API_KEY=
VENICE_BASE_URL=https://api.venice.ai/api/v1
PRECEDENT_MODEL_BACKEND=venice
PRECEDENT_DEV_MODELS=
```

Claude should first call `GET /models`, verify the selected model IDs exist, and keep a committed evidence dump/screenshot for BasedAI. The code should whitelist open-weight IDs in one registry file and reject closed model IDs.

Do not give Claude an OpenAI or Anthropic API key for the runtime. Claude can be the builder, but the submitted product should not call Claude/OpenAI models.

### 2. Jira Service Management Standard trial

Use this for live tickets, approval identity, project roles, and permission-scheme/ACL sync. The project notes require JSM Standard, not Free, because the ACL demo needs permission-scheme/project-role APIs.

Claim:

- Start a Jira Service Management Standard 14-day trial.
- Create a project for the demo, for example `MEDIA`.
- Create at least two roles/groups/principals: scheduling ops and rights ops.
- Create a bot/service user with API access.

Give Claude:

```env
JIRA_BASE_URL=https://YOUR-SITE.atlassian.net
JIRA_EMAIL=
JIRA_API_TOKEN=
JIRA_PROJECT_KEY=MEDIA
JIRA_SERVICE_DESK_ID=
JIRA_REQUEST_TYPE_ID=
JIRA_SCHEDULING_OPS_ACCOUNT_ID=
JIRA_RIGHTS_OPS_ACCOUNT_ID=
```

Prefer a dedicated Atlassian service account. Do not give Claude your primary Atlassian password. Use an API token.

### 3. Fetch.ai Agentverse and ASI:One

Use this to satisfy Fetch eligibility: hosted agents, Agent Chat Protocol, Agentverse profile URLs, and public ASI:One shared-chat URL.

Claim:

- Use the Fetch hackpack / Innovation Lab flow.
- Hackathon offer: one month ASI:One Pro + Agentverse Premium. The local guide records the code as `UKAIAGENTUKAIAGENTAV`; the official Fetch page renders it as `UKAIAGENT UKAIAGENTAV`. Try the exact code copy shown in the redemption flow first.

Give Claude whichever credentials the Fetch portal issues:

```env
AGENTVERSE_API_KEY=
ASI_ONE_API_KEY=
FETCH_AGENT_MAILBOX_KEY=
FETCH_AGENT_SEED=
WATCHER_AGENT_ADDRESS=
LIBRARIAN_AGENT_ADDRESS=
OPERATOR_AGENT_ADDRESS=
```

Exact names may differ by SDK; Claude should adapt them to the Fetch/uAgents examples and document the final `.env.example`.

Do not commit agent seeds or mailbox keys. Agent addresses and public profile URLs are safe to put in the README/submission.

### 4. GitHub account/token

Needed only if Claude is expected to push code or open the BasedAI submission PR.

Give Claude, if you want it to perform GitHub actions:

```env
GITHUB_TOKEN=
GITHUB_REPO=
BASEDAI_HACKATHONS_FORK=
```

BasedAI requires a PR into `BasedAICo/hackathons` under the team folder, with no secrets committed.

### 5. Data-source credentials

Most data sources in the plan do not need API keys:

- TVmaze API: no auth.
- UCI incident dataset: no auth.
- Freeview-EPG XMLTV snapshot: no auth.

Kaggle may require credentials if downloading through the Kaggle API:

```env
KAGGLE_USERNAME=
KAGGLE_KEY=
```

Alternative: download the CC0 Kaggle CSVs manually and place them under `data/raw/`, then Claude does not need Kaggle credentials.

## Useful but not required for Precedent

### OpenAI ChatGPT Pro / Codex boost

The hackathon guide says eligible registered participants received a ChatGPT Pro/Codex boost on the Luma registration email, valid until 7 July 2026. This is useful for building, not for the product runtime. Do not add `OPENAI_API_KEY` to the submitted pipeline if targeting BasedAI.

### BasedAI credits / Hirebase

The BasedAI credits are listed as prize awards, not a general pre-build credit grant:

- 1st: USD 2,000 credits + 1 year Hirebase mid tier.
- 2nd: USD 1,000 credits + 1 year Hirebase entry tier.
- 3rd: USD 500 credits + 6 months Hirebase entry tier.
- Honorable mentions: USD 100 credits.

No BasedAI API key is required unless the team explicitly chooses to build against BasedAPIs.

### Cantor8 learner bounty

Available, but not part of Precedent. Requires Canton/Keycloak credentials from the task doc, a JWT bearer token flow, a PartyId, and possibly Canton Coin transfer details. Do not give these to Claude unless doing the Cantor8 lab.

### CoralOS / Superteam

Not part of the selected build. Would require Solana/devnet wallet credentials and escrow/payment setup if pursuing that track. Do not give Claude wallet private keys or seed phrases.

### Bittensor / Apex

Not part of the selected build. Would require Apex account/CLI setup and potentially wallet/miner credentials.

### Kaspa

Not part of the selected build. Would require wallet/testnet setup only if adding Kaspa-based coordination/payments.

## Minimum `.env` to hand Claude first

```env
VENICE_API_KEY=
VENICE_BASE_URL=https://api.venice.ai/api/v1
PRECEDENT_MODEL_BACKEND=venice

JIRA_BASE_URL=
JIRA_EMAIL=
JIRA_API_TOKEN=
JIRA_PROJECT_KEY=MEDIA
JIRA_SERVICE_DESK_ID=
JIRA_REQUEST_TYPE_ID=

AGENTVERSE_API_KEY=
ASI_ONE_API_KEY=
FETCH_AGENT_MAILBOX_KEY=
```

Add optional Kaggle and GitHub credentials only if Claude is actually doing those steps.

## Do not provide to Claude

- Personal account passwords.
- Production credentials.
- Billing/payment card details.
- Crypto wallet private keys or seed phrases.
- OpenAI/Anthropic/Gemini runtime API keys for the submitted pipeline.
- Any real customer data or confidential enterprise runbooks.

## Sources in this repo

- `Hackathon Information/HACKATHON-GUIDE.md`
- `Hackathon Information/based-ai-general.txt`
- `Hackathon Information/fetch-ai-general.txt`
- `Hackathon Information/fetch-ai.txt`
- `Idea/Idea-Development.md`
- `Idea/refinement/01-realistic-data-plan.md`
- `Idea/refinement/02-architecture-refinement.md`
- `Idea/refinement/04-demo-and-video-script.md`
