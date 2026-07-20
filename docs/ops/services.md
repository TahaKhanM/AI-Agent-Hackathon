# Services, accounts & environment

> Post-hackathon operations map (updated 6 Jul 2026, supersedes the old
> `CLAUDE-AVAILABLE-APIS.md` / `CREDENTIALS-CHECKLIST.md`). Never commit `.env`
> (gitignored, verified clean via `make secrets-scan`); template in
> [`.env.example`](../../.env.example). Load locally with `set -a; source .env; set +a`.

## Live services

### Venice AI (inference — the open-weight model host)
- Base URL `https://api.venice.ai/api/v1`, OpenAI-compatible; inference-only key in `.env`.
- Pinned models (the ONLY file that may name them is [`precedent/models.py`](../../precedent/models.py)):
  FAST `qwen3-5-35b-a3b` (Apache-2.0) · SMART `deepseek-v4-flash` (MIT) ·
  HEAVY `deepseek-v4-pro` (MIT) · EMBED `text-embedding-bge-m3` (MIT).
  All verified live 3 Jul 2026 with public Hugging Face weights — dumps in
  [`docs/compliance/`](../compliance/).
- ⚠️ Venice also proxies **closed** models (`claude-*`, `grok-*`, closed embedders).
  "It runs on Venice" is not an open-weight argument; the registry asserts every
  entry's `modelSource` is a huggingface.co URL. Guard: `make check-open-weight`.
- Hackathon credit code (`IMPERIAL50X`) was a one-off; check remaining credit at
  https://venice.ai/settings/api before demo sessions. Ollama local profile
  (`PRECEDENT_MODEL_BACKEND=local`) remains the offline fallback.

### Jira Service Management (the live ACL source + ticket rail)
- Site `https://precedentlabs.atlassian.net`, project `MEDIA` (id 10001), service desk 1,
  incident request type 16.
- **Tier: JSM Standard 14-day trial, started ~3 Jul 2026 → expires ~17 Jul 2026.**
  After expiry the site drops to Free tier: issue-security schemes (the dual-enforcement
  demo beat) stop working; role membership + permission-scheme sync still work.
  Decide before expiry: pay, re-trial on a new site, or rely on the local Jira-shaped source.
- Provisioned and verified live: roles `precedent-rights-ops`=10007 /
  `precedent-scheduling-ops`=10008; permission scheme 10000; issue-security scheme
  "Precedent Restricted Runbooks" (levels 10000/10001); restricted runbook issues
  MEDIA-2/MEDIA-3; audit records API (`/rest/api/3/auditing/record`).
- One human seat (Taha). The two-principal demo needs a 2nd seat invite or the
  single-account role flip.

### Fetch.ai Agentverse + ASI:One
- **Three mailbox agents registered and Almanac-confirmed live (4 Jul):**
  `precedent-watcher`, `precedent-librarian`, `precedent-operator`
  (addresses + proofs in [`docs/evidence/LIVE-PROOFS.md`](../evidence/LIVE-PROOFS.md)).
  They run only while the local process runs; the "hosted Watcher" is not deployed.
- Agent identities derive from the per-agent seeds `WATCHER_AGENT_SEED`,
  `LIBRARIAN_AGENT_SEED`, `OPERATOR_AGENT_SEED`. **If a seed is unset in a public context the
  code now FAILS CLOSED** (refuses rather than deriving a forgeable identity from a committed
  placeholder); set the real seeds for anything public, or `PRECEDENT_ENV=dev` /
  `PRECEDENT_AGENTS_OFFLINE=1` for local rehearsal (see `agents/common.resolve_seed`). The
  rails sender allowlist may pin public addresses via `WATCHER_ADDRESS`, `LIBRARIAN_ADDRESS`,
  `OPERATOR_ADDRESS` (derivable from the seed, so public — not secret).
- ASI:One chat API key in `.env` (model `asi1`, verified). The shared-chat link captured
  for the submission is an *invite* link — may expire; re-capture from a fresh session
  if it's needed again.

### Kaggle / public data (no auth needed at runtime)
- Seed CSVs are committed under `data/raw/kaggle/` (CC0). TVmaze snapshot committed
  (CC BY-SA). UCI incident log #498 (CC BY 4.0) is downloaded on demand for
  `make bench-uci` — see [`data/raw/SOURCES.md`](../../data/raw/SOURCES.md).

## Environment variables (`.env`)

| Group | Variables |
|---|---|
| Venice | `VENICE_API_KEY`, `VENICE_BASE_URL`, `PRECEDENT_MODEL_BACKEND` (`venice`\|`local`), `PRECEDENT_DEV_MODELS` (proprietary escape hatch — refused unless `PRECEDENT_ENV=dev` is ALSO set) |
| Dev | `PRECEDENT_ENV=dev` (arms dev-only escape hatches: proprietary models + placeholder agent seeds), `PRECEDENT_AGENTS_OFFLINE` (`1` = offline rehearsal, no mailbox) |
| Jira | `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`, `JIRA_SERVICE_DESK_ID`, `JIRA_REQUEST_TYPE_ID`, `JIRA_RIGHTS_OPS_ROLE_ID`, `JIRA_SCHEDULING_OPS_ROLE_ID`, `JIRA_*_ACCOUNT_ID` |
| Fetch | `AGENTVERSE_API_KEY`, `ASI_ONE_API_KEY`, `FETCH_AGENT_MAILBOX_KEY`, `WATCHER_AGENT_SEED`, `LIBRARIAN_AGENT_SEED`, `OPERATOR_AGENT_SEED`, `WATCHER_ADDRESS`, `LIBRARIAN_ADDRESS`, `OPERATOR_ADDRESS` |
| Data | `KAGGLE_USERNAME`, `KAGGLE_KEY` (only to re-fetch source datasets) |

## Hosted demo (kit recovered onto main, not yet deployed)
- `Dockerfile` + `render.yaml`: one-container sim+console image, **offline by design** —
  no `VENICE_API_KEY` baked in, so model calls use canned fallbacks; zero external
  calls, zero secrets in the image. Deploy: Render → New → Blueprint → this repo.
- `scripts/serve_public.sh` for ad-hoc tunnels; `console/showcase.py` is the guided tour.
- Known limitation (pre-multi-tenancy): one process-wide demo state — concurrent
  public visitors share one session until session scoping lands.
