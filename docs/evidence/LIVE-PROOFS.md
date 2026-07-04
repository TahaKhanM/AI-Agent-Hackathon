# Live proofs — real round-trips run against the configured accounts (2026-07-04)

These are live measurements against the real Venice / Jira / Agentverse accounts (creds in the
gitignored `.env`), not synthetic. They complement the airplane-mode conformance bench (seed 4207).

## Venice — open-weight client + catalog (compliance-critical)

- `GET /models` returned a 98-model catalog; the four pinned ids resolve to huggingface.co sources:
  - FAST `qwen3-5-35b-a3b` → huggingface.co/Qwen/Qwen3.5-35B-A3B
  - SMART `deepseek-v4-flash` → huggingface.co/deepseek-ai/DeepSeek-V4-Flash
  - HEAVY `deepseek-v4-pro` → huggingface.co/deepseek-ai/DeepSeek-V4-Pro
  - EMBED `text-embedding-bge-m3` → huggingface.co/BAAI/bge-m3
- `venice.startup_guard(catalog)` **PASS** — every pinned model has a huggingface.co source (open-weight).
- Live FAST-role chat round-trip returned `PRECEDENT LIVE OK`.
- `PRECEDENT_DEV_MODELS` / `ALLOW_PROPRIETARY_DEV` unset (Rule 1 escape hatch closed).

## Jira Service Management — live ACL source + dual-enforcement

- Project **MEDIA** ("PrecedentLabs", JSM), scheme "Precedent Restricted Runbooks" (id 10000) attached.
- Created two restricted runbook issues, security **"Rights Ops Only"** (level 10000):
  - **MEDIA-2** ← `kb:KB-0004` (VOD takedown + republish runbook)
  - **MEDIA-3** ← `kb:KB-0005` (rights exclusivity runbook)
- `.env`: `JIRA_RUNBOOK_ISSUES=kb:KB-0004=MEDIA-2,kb:KB-0005=MEDIA-3`.
- Read-only smoke (`scripts/jira_smoke.py`): **2 runbook sources, constraints=1 each, revoked=0**.

## Live ACL drift / time-to-consistency (`make live-drift`, 3 flips)

- **TTC median 0.24 s** (threshold < 5 min) — **PASS**.
- **Stale-allow fraction 0.000%** (threshold < 0.5%) — **PASS**.
- Caveat: this run's TTC is client-measured (Jira's `/auditing/record` API returned no rows for the
  flip filter, so the source-clock anchor showed "unknown"). The numbers are real; the audit-clock
  anchoring needs the auditing API to return records (permissions/plan). This is a **3-flip proof**
  over a 2-issue Jira — a liveness proof of the path, **not** a "25k-record store" figure.

## UCI realism run (`make bench-uci`, dataset #498, CC BY 4.0)

- **25k-record store: 24,918 records** (24,918 incidents, 70 real `assignment_group` ACL boundaries).
- **FNR 0 / 7,529 deny-expected · FPR 0 / 2,471 allow-expected.**
- **P99 permitted() = 0.590 µs over the 25k-record store** (never "P99 over 141k events" — 141,712 is
  the raw event count; the store is 24,918 incidents).
- The 46 MB raw CSV is downloaded to `data/raw/incident_event_log.csv` and **gitignored** (not
  committed — size + data honesty), reproducible from the UCI #498 zip.

## Agentverse — three agents registered + active

Confirmed via the Almanac API (`status=active`, endpoints=1) on 2026-07-04:
- Watcher `agent1q2m0gk9wdvs0lyc3nfuyeet4y3nc68m9y24kehun2t70hadwf7qxjcgkldx`
- Librarian `agent1qv760pr29kmy9w5lst4tffr06rv6qqmt0ef74w6ycfezd5hfh0e0kse9xv7`
- Operator `agent1qwesj8x7797jatzt3dwn8gxk2skxsaghrcpa76n548s6a6fz97wvuxna02g`

Still to capture (interactive only): the **ASI:One shared-chat URL** (≥10 discoverability chats).
