<!--
DRAFT for the human to commit as  UK-AI-Agent-EP5/submissions/<team-name>/README.md  in the
BasedAI hackathons fork. Follows the 8 verbatim template headings. Two sentinels remain for the
human: [[WAIT:VIDEO-LINK]] (paste the unlisted video URL Saturday) and [[WAIT:MENTOR-ANSWER]]
(the deadline the mentor confirms at G0). The bench numbers below are MEASURED at seed 4207 via
`make bench`; re-run `make bench` against merged main at the G2 freeze to refresh before commit.
PR title:  Precedent — permission-aware agent memory (UK AI Agent Hackathon EP5)
"Files changed" must list ONLY your team folder.
-->

# Precedent

Permission-aware agent memory for enterprise incident resolution. Precedent detects an incident,
retrieves the organisation's **own documented fix**, classifies risk **deterministically**,
executes it through **typed tools behind an approval gate**, verifies and **auto-rolls-back** on
failure, and remembers the outcome as an *executed fix with provenance*.

> The thesis: AI SREs fix broken code; in real enterprises the fix is almost never code — it's a
> documented admin change gated by who is allowed to make it. So the hard problem is not
> generation, it's **permission-aware memory**: retrieving the right documented fix *only* for a
> principal allowed to see it, and proving it.

## What it does

- **Retrieves the documented fix, ACL-filtered.** Every memory record carries its full ACL
  lineage (which Jira issue-security level / project role each source imposes). Retrieval is a
  single deterministic **bitmask conjunction** over a precompiled effective-policy — the principal
  must satisfy **all** constraints across **all** lineage sources, or nothing is returned (not a
  title, not a snippet).
- **No LLM in the permission or risk decision.** A model may *propose* fields for a messy ticket,
  but a class match counts only on a deterministic extractor's field equality, and the allow/deny
  decision is pure Python. The model narrates; deterministic policy disposes.
- **Fails closed.** Revoked source, unverified provenance, quarantined/tombstoned record, stale
  freshness (>60 s), or the permission source being unreachable → **deny**. A stale cache may
  narrow access, never widen it.
- **Dual enforcement, in seconds.** Flip an issue's security level in Jira and two independent
  layers react to the same change: Jira itself starts returning 404, and within one poll tick
  Precedent denies every memory ever derived from it — summaries, fix records, embeddings.
- **Proves every decision.** Each retrieval / denial / sync / execution appends to a hash-chained
  audit log; a companion Jira audit record timestamp-matches the ACL flip — two independent logs.

## Demo

- 90-second demo video: [[WAIT:VIDEO-LINK]]
- Live inside ASI:One (no custom frontend): https://asi1.ai/invite?channelInviteKey=NmIsH5-DHQVhnf78uThoWX3fVkRXiSpGz78rMsPkoUQ
  — report → deterministic approval gate → execute + audit hash, the zero-LLM standing-approval repeat,
  and the fail-closed refusal (owner team only).
- The revocation moment: a runbook's security level flips in Jira → the same memory query goes
  from *allowed* to *denied* in seconds, embedding path included, with both audit logs shown.

## How to run it

Airplane-first — the whole bench, the 6/6 attack suite and the audit-coverage test run offline.

```bash
make install            # uv venv (Python 3.13) + deps
make test               # full suite
make bench              # regenerates precedent_memory/bench/RESULTS.md (the conformance table) in ~5 s
make bench-extractor    # scores the frozen extractor over the seed-4207 mutation corpus (0 false-fast-paths)
make console            # the judge console on :8000 (seeded local demo)
```

One live proof (optional, human-run): `make jira-smoke` (live Jira ACL read), `make live-drift`
(live drift/TTC vs real Jira, anchored to `/rest/api/3/auditing/record`), `make bench-uci` (the
UCI 25k-record realism run). Each exits non-zero until its credentials/data are configured.

## How it works

- **Permission memory (`precedent_memory/`).** A/B/C lineage semantics: a derived record inherits
  the **union** of every source's constraints (conjunction). The effective policy is compiled to a
  bitmap so a retrieval touches one indexed row — the P99 fast path. Fail-closed retrieval,
  hash-chained audit, versioned Jira ACL sync with a write-behind cache (polling, no webhooks).
- **Conformance, graded by an independent oracle.** The bench reports in BasedAI's own evaluation
  vocabulary. Crucially, the expected labels are **not** produced by the compiler under test — a
  separate ~40-line naive reference implementation (a plain-Python-set lineage-conjunction walk
  over the raw `acl_source` tables, no bitmap, no import of `store`/`retrieve`) produces the ground
  truth, so **FNR/FPR are a genuine two-implementation cross-check, not the exam grading itself**.
  A CI test (`precedent_memory/tests/test_oracle.py`) fails the build if the oracle ever imports
  the code it grades.

### Conformance results (measured — `make bench`, seed 4207)

Protocol topology: 5 hierarchy levels · 20 roles · 1,000 ACL-tagged docs · 40 principals ·
10,000 ground-truth queries (5,219 deny-expected — clears the rule-of-three floor for FNR < 0.1%).

| Metric | Measured | Threshold | Pass/Fail |
|---|---|---|---|
| FNR (leak: oracle DENY, compiler ALLOW) | **0 leaks / 5,219 deny-expected = 0.000%** | < 0.1% | ✅ |
| FPR (outage: oracle ALLOW, compiler DENY) | 0 / 4,781 allow-expected = 0.000% | < 2% | ✅ |
| P50 latency (permitted() bitmask check) | 0.423 µs | < 50 ms | ✅ |
| P99 latency (permitted() bitmask check) | 0.445 µs | < 200 ms | ✅ |
| End-to-end overhead (permission check on hot path, P99) | 0.0130 ms | < 100 ms | ✅ |
| Derived-memory correctness (1k lineage artifacts vs oracle) | 3,000/3,000 probes = 100.00% | > 99% | ✅ |
| ACL drift (stale-allow after one sync tick) | 0/200 = 0.000% (synthetic; live Saturday) | < 0.5% | ✅ |
| Time-to-consistency (flip → recompiled deny) | 0.0180 ms median (synthetic; live Saturday) | < 5 min | ✅ |
| Audit coverage (every allow/deny/sync/exec path) | 300/300 = 100.0% + hash chain verified | 100% | ✅ |
| Permission-check curve (1k/5k/25k/100k records) | flat / O(1) | flat/log | ✅ |
| Adversarial attacks | **6/6** | 6/6 | ✅ |

The six named adversarial attacks (`tests/test_adversarial.py`), each asserting deny + no
restricted-content leak + an audit event (or a bounded timing delta): **query inference ·
metadata bypass · timing attack · collection attack · prompt injection · derived-memory attack**.

**Extractor robustness (deterministic class extractor, seed 4207 · 100-mutation corpus).**
`make bench-extractor` scores the frozen deterministic extractor — the only path that can unlock
the standing-approval fast-path — over 100 messy-ticket mutations (typos, colloquial symptoms,
dropped codes, red-herring decoys): **0 false-fast-paths / 100 (0.00%)** — no mutation ever
produced a *wrong confident* class that could fast-path a wrong fix — and **25/25 red-herring
decoys resisted** (an unknown code degrades to human review rather than grabbing a look-alike
known code). Source of truth: `precedent_memory/bench/extractor_robustness.json`.

Realism run (measured, `make bench-uci`): the same harness over the UCI **25k-record store**
(dataset #498, **24,918 incidents**, 70 real `assignment_group` ACL boundaries) — **FNR 0 / 7,529
deny-expected · FPR 0 / 2,471 allow-expected · P99 permitted() 0.590 µs over the 25k-record store**
(never "P99 over 141k events" — 141,712 is the raw event count). Live Jira dual-enforcement is wired
(2 restricted runbook issues, security "Rights Ops Only") and a 3-flip `make live-drift` measured
TTC 0.24 s / 0.000% stale-allow. Evidence: `docs/evidence/LIVE-PROOFS.md`.

## Tech & sponsor APIs used

**Open-weight only — no closed/proprietary model is called anywhere in the pipeline.** The only
file that may name a model id is `precedent/models.py`, and CI (`make check-open-weight`) greps for
violations. Pinned, licence-verified open-weight models (served via Venice's OpenAI API-compatible endpoint):

- **FAST:** `qwen3-5-35b-a3b` — [Qwen/Qwen3.5-35B-A3B](https://huggingface.co/Qwen/Qwen3.5-35B-A3B), Apache-2.0
- **SMART:** `deepseek-v4-flash` — [deepseek-ai/DeepSeek-V4-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), MIT
- **HEAVY:** `deepseek-v4-pro` — [deepseek-ai/DeepSeek-V4-Pro](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro), MIT
- **EMBED:** `text-embedding-bge-m3` — [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3), MIT (embedding models appear only under `GET /models?type=embedding`)

Verification evidence: live Venice `/models` dumps committed to `docs/compliance/`
(`venice-models-2026-07-03.json`, `venice-models-all-2026-07-03.json`,
`venice-models-embedding-2026-07-03.json`), each pinned id carrying its public huggingface.co
weights URL. The startup guard additionally asserts each id's `modelSource` is a huggingface.co
URL (closed models on Venice can expose a vendor doc URL, so "has a source" is not enough).

- **BasedAI** — the conformance bench + independent oracle + 6/6 attacks above.
- **Fetch.ai** — three Agentverse mailbox agents (Watcher / Librarian / Operator) speaking the
  Agent Chat Protocol; the ASI:One chat sender address is the authorising principal at the gate.
- **Jira Service Management** — the live ACL source of truth (issue-security + project roles),
  polled with a write-behind cache; the dual-enforcement + audit-corroboration story.

Deadline governing this submission (per BasedAI mentor): [[WAIT:MENTOR-ANSWER]].

## What's next

- The live UCI 25k-record realism run and the live Jira drift/TTC numbers (poll-anchored to Jira's
  audit clock), posted as a PR comment.
- Governed redacted derivatives (C-lineage) with attestation; temporal-embargo constraints.
- The hosted degraded-L0 Watcher kept running post-hackathon on Agentverse.

## License

MIT (see `LICENSE`). Data provenance: UCI ServiceNow incident log (CC BY 4.0), TVmaze GB schedule
(CC BY-SA), Freeview XMLTV, CC0 Kaggle catalogs; runbooks adapted from real published procedures.
Only licence-window terms are synthesised, by a stated rule. TMDB/IMDb are excluded on licence
grounds.
