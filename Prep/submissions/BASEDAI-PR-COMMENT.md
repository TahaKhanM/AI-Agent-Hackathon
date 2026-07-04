# BasedAI PR comment — PREPARED, DO NOT POST (human posts this on the open PR)

Post the block below verbatim as a comment on the BasedAI fork PR once the mentor deadline
answer is in. Every number traces to `precedent_memory/bench/RESULTS.md`,
`docs/evidence/LIVE-PROOFS.md`, or `precedent_memory/bench/extractor_robustness.json`. Nothing
here is a placeholder.

---

**Measured results — live against the real accounts (2026-07-04)**

The synthetic conformance bench (seed 4207) in the README is now complemented by live runs.

Realism run — UCI **25k-record store** (`make bench-uci`, dataset #498, 24,918 incidents, 70 real
`assignment_group` ACL boundaries; caption "25k-record store", never "141k events"):

| Metric | Measured | Threshold |
|---|---|---|
| FNR (leak) | 0 / 7,529 deny-expected = 0.000% | < 0.1% |
| FPR (outage) | 0 / 2,471 allow-expected = 0.000% | < 2% |
| P99 permitted() over the 25k-record store | 0.590 µs | < 200 ms |

Live ACL drift / time-to-consistency — a **3-flip, 2-issue Jira liveness proof** (`make
live-drift`, MEDIA-2 / MEDIA-3, security "Rights Ops Only"; a liveness proof of the path, **not** a
25k-store figure):

| Metric | Measured | Threshold |
|---|---|---|
| Time-to-consistency (flip → deny) | 0.24 s median | < 5 min |
| ACL drift (stale-allow fraction) | 0.000% | < 0.5% |

**Two updates to the README's scope, for accuracy:**

- **Temporal-embargo constraints are implemented and oracle-graded** (they were listed under
  "what's next"). A record with a future `unlock_at` is withheld from everyone until then — even a
  cleared or public record; fail-closed on an unparseable timestamp. No schema change; deny-before
  / allow-after graded in `precedent_memory/tests/test_temporal_embargo.py`; conformance
  correctness byte-identical (a no-op on the bench records).
- **Query-time inference prevention added** (deterministic, zero-LLM, oracle-graded):
  `precedent_memory/probing_detection.py` — (1) per-principal denial-burst / probing-pattern
  detection over the hash-chained audit_log (window + threshold → flag + throttle + audit), and
  (2) a bundle-level cross-boundary co-occurrence check before context assembly (a result set may
  not mix records from disjoint restricted boundaries — deny + audit, even for a principal cleared
  for both). Additional labelled bench section
  (`python -m precedent_memory.bench.inference_prevention` → `inference_prevention.json`); the
  10-metric `results.json` is unchanged. `precedent_memory/retrieve.py` stays LLM-import-free.

Extractor robustness (unchanged, for reference): **0 false-fast-paths / 100** seed-4207 mutations ·
**25/25** red-herring decoys resisted (`extractor_robustness.json`).
