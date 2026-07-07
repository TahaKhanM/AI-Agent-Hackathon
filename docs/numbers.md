# Final numbers — the ONE reference every shipped surface cites

**Purpose.** A single, measured, caveat-carrying number set for the deck, README, PR-README,
BUIDL, video captions, and demo crib sheets. **No shipped surface may state a number that is not
on this page (with its label).** Every value traces to `docs/research/00-verified-claims.md` (market
citations), `data/analysis/uci-baseline-results.md` (corpus), `precedent_memory/bench/RESULTS.md`
+ `results.json` (conformance), or `precedent_memory/bench/extractor_robustness.json` (extractor).

This file is the number-honesty gate's source of truth (B10). If a value here has no replacement
for a surface, **delete the cell — never ship a `‹XX›` placeholder**.

---

## 1. Corpus numbers (ours — measured, unattackable)

Source: UCI ML Repository #498 "Incident Management Process Enriched Event Log" (CC BY 4.0), the
audit log of a real ServiceNow instance. Reproduce with `data/analysis/uci_match_rate.py`.

| Number | Value | Exact framing + caveat |
|---|---|---|
| Dataset size | **141,712 events / 24,918 incidents** | Provenance line only. The **store is 24,918 incidents** → always **"25k-record store"**. **NEVER "P99 over 141k events"** — the permission-check P99 is measured over the record store, not the raw event count. |
| Fix-class match rate | **94.4%** | "94% of 24,918 real incidents arrived when their exact fix class (category + subcategory + resolution code) had already been resolved before." **Existence** claim (the key includes `closed_code`, known only at resolution) — 1,397 fix classes. |
| Symptom-class match rate | **98.6%** | Backup / arrival-knowable: at symptom level (category + subcategory) 98.6% had precedent (335 classes). **Do not swap with 94.4%** — say whichever matches the sentence. |
| Median resolution, precedented repeats | **18.2 h (CALENDAR)** | "Even with precedent, the median repeat still took 18.2 calendar hours — 36% breached SLA, 47% reassigned ≥1×. Retrieval, not resolution, is the bottleneck." (p75 = 136.6 h; first-of-class median = 92.1 h.) **Always labelled "calendar".** |
| Ladder bootstrap coverage | **558 classes ≥4 occ → 94.8% of volume** | "558 fix classes recur 4+ times and cover ~95% of volume — standing-approval candidates on day one." (301 classes ≥10 → 88.6%.) |
| Arrival-time naive floor | **top-1 59.4% / top-3 87.7%** | Naive frequency baseline over 24,470 evaluable incidents, symptom fields only. "The right fix is on the first screen ~88% of the time." This is a **FLOOR** (naive baseline, coarse public fields), **NOT a product-accuracy claim** — label it. (Most-recent predictor: top-1 47.4%.) |
| Data-quality colour | 99.55% complete fingerprint · 0.43% missing closed_code · 6.2% missing resolved_at · 47.4% of repeats reassigned ≥1× | Feeds "bigger and messier" — the raw data kept its nulls/dups. |

**Handle with care — `knowledge=true` median 74.6 h vs 8.6 h false** (n=3,358 true, 14.25%): colour
only ("the lookup path is the slow path"), **acknowledge the causal confound if probed, NEVER
present as "documented fix → faster/slower" causally.**

## 2. Baseline bar / industry benchmark (labelled)

| Number | Value | Label |
|---|---|---|
| Baseline Bar anchor | **8.85 business hours = "8h 51m"** | MetricNet MTTR, **industry benchmark, BUSINESS hours**. This is the on-screen baseline bar. |

**NEVER-BLEND (the cardinal rule):** **18.2 h is CALENDAR (ours, UCI); 8.85 h / 8h 51m is BUSINESS
(MetricNet, industry).** They corroborate each other; they are **never averaged, never swapped, never
blended.** The video time-lapse VO figure "**8h51m**" is the **business** figure — never mixed with 18.2h.

## 3. Conformance bench (measured, seed 4207 — `precedent_memory/bench/RESULTS.md`)

Topology: 5 hierarchy levels · 20 roles · 1,000 ACL-tagged docs · 40 principals · 10,000 queries
(5,219 deny-expected, 4,781 allow-expected). Ground truth from the **independent oracle**
(`bench/oracle.py`, AST-guarded) — a two-implementation cross-check, never self-grading.

| Metric | Measured | Threshold |
|---|---|---|
| FNR (leak: oracle DENY, compiler ALLOW) | **0 leaks / 5,219 = 0.000%** | < 0.1% |
| FPR (outage: oracle ALLOW, compiler DENY) | **0 / 4,781 = 0.000%** | < 2% |
| P50 permitted() | 0.423 µs | < 50 ms |
| P99 permitted() | 0.445 µs | < 200 ms |
| End-to-end overhead (P99) | 0.0130 ms | < 100 ms |
| Derived-memory correctness | 3,000/3,000 = 100.00% | > 99% |
| ACL drift (stale-allow / tick) | 0/200 = 0.000% (synthetic; live Sat) | < 0.5% |
| Time-to-consistency | 0.0180 ms median (synthetic; live Sat) | < 5 min |
| Audit coverage | 300/300 = 100.0% + hash chain verified | 100% |
| Permission-check curve (1k/5k/25k/100k) | flat / O(1) | flat/log |
| Adversarial attacks | **6/6** | 6/6 |

Six attacks (verbatim, `tests/test_adversarial.py`): **query inference · metadata bypass · timing
attack · collection attack · prompt injection · derived-memory attack**.

**Latency caveat:** the µs/ms figures are measured live each run and drift ~run-to-run; the correctness
fields (FNR/FPR/derived/drift/audit/attacks) are a byte-identical function of the seed. Quote the
committed values; they sit ~5 orders of magnitude under every threshold, so jitter never changes a verdict.

## 4. Extractor robustness (measured, seed 4207 — `precedent_memory/bench/extractor_robustness.json`)

The ONE robustness number, identical on all four surfaces (console chip · deck slide 10 · README · BUIDL):

- **0 false-fast-paths / 100 mutations (0.00%)** — no messy ticket produced a *wrong confident* class
  that could fast-path a wrong fix (the eligibility-relevant invariant; MUST be 0).
- **25/25 red-herring decoys resisted (100%)** — an unknown code degrades to human review rather than
  grabbing a look-alike known code.
- Breakdown: correct-match 8 · safe-degrade 50 · conservative-degrade 42 · false-fast-path 0. Recoverable
  known-code tickets: 8/8 correct. (Corpus is adversarial by design: 92% codeless/garbled/unknown-sibling.)

## 4b. Live-measured against the real accounts (2026-07-04 — `docs/evidence/LIVE-PROOFS.md`)

Real round-trips, not synthetic — complements the airplane-mode bench:

- **UCI 25k realism** (`make bench-uci`, dataset #498): **24,918-record store** (70 real
  `assignment_group` boundaries) · **FNR 0 / 7,529** · **FPR 0 / 2,471** · **P99 permitted() 0.590 µs**
  over the 25k-record store. (Never "P99 over 141k events".)
- **Venice**: live `/models` open-weight guard PASS (4 pinned ids → huggingface.co sources) + a live
  FAST chat round-trip.
- **Live Jira dual-enforcement**: 2 restricted runbook issues (MEDIA-2/MEDIA-3, "Rights Ops Only"),
  smoke sees 2 sources; **`make live-drift` (3 flips): TTC 0.24 s median, 0.000% stale-allow** — a
  liveness proof of the path (3-flip, 2-issue Jira), **not** a "25k-store" figure.
- **Agentverse**: 3 agents registered · active (Almanac-confirmed).

## 5. Market / industry citations (from `docs/research/00-verified-claims.md` — respect the vote + caveat)

| Claim | Value | Label |
|---|---|---|
| Repeat issues at ServiceNow (best "pre-existing fix" cite) | **>60%** already-seen-and-solved | ServiceNow KCS case study (3–0) |
| KCS "time to relief" | **52% faster** | ServiceNow KCS (3–0) |
| KB-attached cases resolve faster | 66% faster | ServiceNow KCS (2–1) |
| PagerDuty Runbook Automation | **"99% faster"**; up to **50%** cost cut | **(vendor-claimed)** — always labelled |
| PagerDuty gap | event-driven remediation, but **pre-built scripted jobs only** (not retrieved KB fixes) | the incumbent-gap cite (3–0) |
| Downtime economy | **$200M/year per Global 2000 company** (Oxford Economics/Splunk 2024) | prefer over the $400B aggregate |
| Critical-app downtime | **61% say $100k+/hour** | New Relic 2023 |
| MTTR | 60% take >30 min, 34% >1 hr | New Relic 2023 (resolution) |
| Google SRE toil | **~33%** average (goal <50%) | say "stated goal", not "enforces" |
| Alert fatigue / AIOps gap | 44% suppressed-alert outage; 74% C-suite vs 39% practitioners use AI | **(2026 vendor-sponsored survey — NeuBird)** — always labelled |
| Established auto-remediation exists | Digitate **Ignio** (closed-loop, heavy setup) | our differentiation = KB-grounding + cross-system + graduated autonomy |

## 6. REFUTED — never use (failed adversarial verification)

- ✗ "Komodor/Klaudia does **no** autonomous execution / is **K8s-only** / uses RAG for low hallucination"
  — refuted; treat Komodor as a *partial* (K8s-scoped) execution competitor.
- ✗ "Downtime costs the Global 2000 **$400B combined**" — use **$200M/company** (Oxford/Splunk) instead.

## 7. Terminology + honesty invariants (enforced on every surface)

- **L3 is "Standing Approval", NEVER "Autonomous".**
- Vendor numbers carry **"(vendor-claimed)"** / "(vendor-sponsored survey)".
- **NEVER-BLEND:** 18.2 h calendar vs 8.85 h / 8h 51m business — separate labels, never averaged.
- **25k-record store** (24,918 incidents) — never "P99 over 141k events".
- **94.4% = existence**, **98.6% = arrival-knowable** — don't swap; **59.4%/87.7% = naive floor**, not product accuracy.
- **TMDB/IMDb rejected** on licence grounds — never reintroduced as a data source.
- Slide 12 practitioner-validation line is **human-written from a real reply or deleted — never faked**.
- No secrets, tokens, real names, or internal URLs on any shipped surface.
