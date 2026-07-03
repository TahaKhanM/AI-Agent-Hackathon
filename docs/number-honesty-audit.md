# Number-honesty audit (B10) — every shipped number → source + caveat

Cross-checks every number on a shippable surface against `Prep/final-numbers.md` (which in turn traces
to `Research/00-verified-claims.md`, `data/analysis/uci-baseline-results.md`,
`precedent_memory/bench/RESULTS.md`, and `extractor_robustness.json`). Run 2026-07-04 over: the deck
PDF (`docs/submission/precedent-deck.pdf`), `Prep/submissions/*`, `Prep/video/*`, `Prep/crib-sheets/*`,
`Prep/run-of-show.md` & the other demo-prep docs, `docs/data-provenance.md`.

## Number → source → caveat map

| Number (as shipped) | Source | Caveat enforced on every surface |
|---|---|---|
| 8.85 business hrs / "8h 51m" | MetricNet/HDI | labelled **business**; the Baseline Bar + video anchor; **never blended with 18.2h** |
| 18.2 h (repeat median) | UCI corpus (ours) | labelled **calendar**; a separate label from 8.85h; never averaged |
| 94.4% precedent | UCI corpus (ours) | **fix-class EXISTENCE** (closed_code known at resolution); 98.6% is the arrival-knowable symptom class — not swapped |
| 59.4% / 87.7% | UCI corpus (ours) | naive **FLOOR** (frequency baseline, coarse fields) — never stated as product accuracy (A-depth/Q&A only) |
| 141,712 events / 24,918 incidents | UCI #498 | provenance line; the **store is a "25k-record store"** — never "P99 over 141k events" |
| P99 0.445 µs / FNR 0/5,219 / FPR 0/4,781 / 6/6 | bench/RESULTS.md (seed 4207) | independent-oracle graded; latency is measured-live (correctness is seed-deterministic) |
| 0 false-fast-paths / 100 · 25/25 decoys resisted | extractor_robustness.json | identical on chip/slide/README/BUIDL; the eligibility number |
| $600B/yr + ≈$200M/company | Splunk 2026 / Oxford Economics/Splunk 2024 | always paired; **never "$400B" bare** |
| >60% repeats | ServiceNow KCS | verified 3–0 |
| $2.85B Moveworks / $22→$69→$104 | ServiceNow newsroom / MetricNet | MetricNet vintage ~2019–20 (not relabelled 2024) |
| Encompass 1,200+ / Amagi 5,000+ / PagerDuty 99%/50% / Moveworks 50–88% | vendor marketing | carry **"(vendor-claimed)"** |
| NeuBird alert-fatigue stats | NeuBird 2026 | carry **"(2026 vendor-sponsored survey)"** |

## Sweep results (all shippable surfaces)

| Check | Result |
|---|---|
| Refuted claims present ($400B combined; Komodor "no autonomous"/K8s-only; Klaudia RAG-low-hallucination) | **none** ✅ |
| NEVER-BLEND — 18.2h calendar averaged/equated with 8.85h/8h51m business | **none** ✅ |
| Vendor-claimed / vendor-sponsored labels present where required | present ✅ (deck slide 11 + A1, N1/T3 crib sheets, final-numbers) |
| "25k-record store" used; "P99 over 141k events" | correct usage; the forbidden phrase appears **only** inside "never say …" honesty prose ✅ |
| 94.4% (existence) vs 98.6% (arrival) not swapped; 59.4%/87.7% labelled as floor | correct ✅ |
| L3 labelled "Standing Approval", never "Autonomous" | correct on every surface (the word "Autonomous" appears only in negations / "do-NOT" lists) ✅ |
| Closed-model ids on any shipped surface | **none** ✅ (open-weight framing only; ids only in models.py / PR-README) |
| Unfilled `‹…›` tokens on a shippable surface | **none** ✅ |
| Exported deck PDF: `‹` / `[[WAIT` / "Autonomous" L3 / closed-model id | 0 / 0 / none / none ✅ |
| TMDB/IMDb reintroduced as a data source | no — explicitly rejected on the provenance surfaces ✅ |
| Engineered ~15s presented as measured latency | no — flagged "engineered/paced (real ~6–8s)" on every surface ✅ |

## Logged-out link-sweep checklist (for the human, pre-submit)

Incognito, logged out, before each submit:
- [ ] Public repo README renders; `precedent_memory/bench/RESULTS.md` + `extractor_robustness.json` paths resolve.
- [ ] Deck PDF opens; every number matches `Prep/final-numbers.md`; zero `‹` / `[[WAIT`.
- [ ] Video plays; ASI:One shared-chat URL loads; the three Agentverse profiles load with both badges.
- [ ] BasedAI PR link loads; DoraHacks BUIDL page: Ctrl-F finds no `‹`, no `XX`, no `TODO`, no `TBD`.
- [ ] No secret, token, real name, or internal URL visible on any public surface.

**Verdict: zero refuted claims, NEVER-BLEND enforced, every number traces to a source with its caveat,
zero placeholders on any shippable surface.**
