<p align="center">
  <img src="assets/brand/precedent-logo.png" alt="Precedent" width="240">
</p>

<h3 align="center">Every incident resolved becomes precedent.</h3>

<p align="center">
  <em>AI SREs fix broken code. In real enterprises the fix is almost never code —
  it's a documented admin change. Precedent is the agent that remembers every fix
  your organisation has ever applied and applies it again: risk-classified,
  approval-gated, audited, reversible.</em>
</p>

---

**Precedent** detects an enterprise incident, retrieves the **documented fix from the
organisation's own knowledge** (KB articles + a permission-aware memory of previously
*executed* fixes), classifies its risk **deterministically — no LLM in any permission or
risk decision** — executes it through **typed tools behind a graduated human-approval
ladder**, verifies the result, **auto-rolls-back on failure**, and records the outcome as
an *executed fix with provenance*. Each resolution makes the next one cheaper: **the
second time is free**.

```
DETECT → TRIAGE → RETRIEVE (KB + memory, ACL-filtered) → RISK-CLASSIFY (deterministic)
      → GATE (human approval / standing approval) → EXECUTE (typed tools) → VERIFY
      → (auto-rollback on failure) → MEMORISE (executed-fix-with-provenance)
```

## Why this problem is real — measured, not asserted

We ingested the public UCI event log of a real ServiceNow instance
(141,712 events / 24,918 incidents, CC BY 4.0) and measured it
([analysis + scripts](data/analysis/), [canonical numbers](docs/numbers.md)):

| Measured | Value | Label that keeps it honest |
|---|---|---|
| Incidents whose **exact fix class** had already been resolved before | **94.4%** | *existence* claim (fix class includes the resolution code) |
| Incidents whose **symptom class** had precedent at arrival | **98.6%** | arrival-knowable |
| Median time to resolve a **precedented repeat** by hand | **18.2 h** | *calendar* hours; 36% breached SLA, 47% reassigned ≥1× |
| Recurring fix classes covering ~95% of volume | **558 classes** | standing-approval candidates from day one |
| Naive baseline ranking the true fix top-3 at arrival | **87.7%** | a *floor*, not a product-accuracy claim |

The industry corroboration: before adopting KCS, **>60%** of ServiceNow's own support
incidents were repeats with existing fixes (ServiceNow case study), against an
**8.85 business-hour** industry MTTR benchmark (MetricNet). The two datasets carry
different clock semantics and are never blended.
The bottleneck is not knowing the fix — it's *finding and safely executing* it.

## The trust architecture (this is the product)

1. **The model narrates; deterministic policy disposes.** The incident-class key is a
   computed fingerprint — `sha256(service | error_code | target_object_type)` — from a
   deterministic extractor. An LLM may *propose* fields for a messy ticket, but execution
   unlocks only on extractor-confirmed field **equality**, never semantic similarity.
   Measured on a 100-ticket adversarial mutation corpus: **0 false fast-paths**, 25/25
   red-herring decoys resisted ([bench artifact](precedent_memory/bench/extractor_robustness.json)).
2. **Approval never leaves the loop.** L0 observe → L1 recommend → L2 approval-gated →
   L3 **Standing Approval**: after 3 consecutive verified successes a *human* clicks
   Promote (audited), a Revoke button stays visible, and any verification failure
   auto-demotes the class. A standing-approval run makes **zero LLM calls**.
3. **Rollback precedes execution.** No plan executes without a pre-state snapshot and a
   pre-generated inverse; failed verification fires the rollback and demotes the class.
4. **Permission-aware memory, fail-closed.** Fix records derived from restricted sources
   require satisfying **all** source constraints (lineage conjunction). ACLs sync live
   from Jira; when freshness is uncertain, restricted memory is **denied, never served**.
   Refusals disclose only a count and the owning team — never content.
5. **Hash-chained audit.** Every retrieval, denial, approval, execution, promotion and
   rollback is an append-only, hash-chained record naming a human principal.
6. **Open-weight models only.** The entire loop (triage, synthesis, audit prose, and
   the embedder) runs on open-weight models pinned in
   [`precedent/models.py`](precedent/models.py) — the only file allowed to name a model,
   enforced by CI grep ([evidence](docs/compliance/)). Nothing closed, nothing
   unauditable, sits anywhere near the decision path.

### The memory layer is benchmarked, not vibes

[`precedent_memory/`](precedent_memory/) is a standalone permission-aware memory library
(SQLite, zero LLM imports in the retrieval path) with a conformance bench graded by an
**independent oracle** — never the compiler under test
([RESULTS.md](precedent_memory/bench/RESULTS.md), seed 4207, reproduce with `make bench`):

| Metric | Measured | Threshold |
|---|---|---|
| False-negative rate (leaks) | **0 / 5,219 deny-expected queries** | < 0.1% |
| False-positive rate (outages) | **0 / 4,781** | < 2% |
| Permission check P99 | **~0.4–0.6 µs** (varies per run) | < 200 ms |
| Derived-memory correctness | 3,000/3,000 | > 99% |
| Adversarial attacks resisted | **6/6** (query inference, metadata bypass, timing, collection, prompt injection, derived-memory) | 6/6 |
| Live Jira ACL flip → memory dark | **TTC median 0.24 s**, 0.000% stale-allow (3-flip liveness proof) | < 5 min |

## Try it

```bash
# Setup (Python 3.13; uv recommended)
make install                 # uv venv + editable install with dev extras
cp .env.example .env         # optional — the demo runs fully offline without it

# Run the demo (MediaCo sim + console, seeded with real public data)
make sim                     # sim on :8100 + console on :8000
open http://localhost:8000   # "The Approver's Seat": you take the approver's chair
                             # and drive the real kernel through 8 self-paced chapters

# Prove the claims yourself
make test                    # 256 tests, 0 skipped, ~20 s
make check-open-weight       # model names appear only in precedent/models.py
make bench                   # regenerate the conformance bench RESULTS.md
make freeze-check            # the full release gate
```

**Airplane-mode by design:** with no API keys the demo uses canned model fallbacks,
committed embeddings, and a local Jira-shaped ACL source — every beat still works,
including the permission flip and the rollback. With keys, triage runs live on Venice
(open-weight) and the ACL source is a real Jira project.

**Host it:** the repo ships a one-container image (sim + console, no secrets baked in).
`docker build -t precedent-demo . && docker run -p 8000:8000 precedent-demo`, or deploy
straight to Render via [`render.yaml`](render.yaml). Known limitation: the demo state is
currently single-session — concurrent visitors share it (session isolation is the top
item on the roadmap below).

**Agents:** the Watcher / Librarian / Operator run as Fetch.ai Agentverse mailbox agents
speaking the Chat Protocol; an incident can be reported, approved and resolved entirely
from an ASI:One conversation, with the chat sender address recorded as the authorising
principal ([proofs](docs/evidence/LIVE-PROOFS.md)).

## What's in the box

| Path | What it is |
|---|---|
| [`precedent/`](precedent/) | Core loop: typed contracts, deterministic extractor + fingerprint, YAML policy engine, approval ladder + standing-approval fast-path, orchestrator, model registry |
| [`precedent_memory/`](precedent_memory/) | Permission-aware memory library: lineage-conjunction ACLs, precompiled policy bitmaps, hash-chained audit, fail-closed retrieval, conformance bench + oracle |
| [`sim/`](sim/) | MediaCo simulated broadcast stack (scheduler / rights / publisher / KB) seeded with real public data — real content, simulated services, messiness preserved |
| [`console/`](console/) | Server-rendered demo — "The Approver's Seat" interactive chaptered tour |
| [`agents/`](agents/) | Fetch.ai rails: Watcher / Librarian / Operator mailbox agents |
| [`data/`](data/) | Committed seed data + the UCI baseline analysis ([provenance & licences](docs/data-provenance.md)) |
| [`docs/`](docs/) | [Thesis & specs](docs/idea/), [canonical numbers](docs/numbers.md), [verified market research](docs/research/00-verified-claims.md), [evidence index](docs/evidence/), [ops map](docs/ops/services.md), [demo scripts](docs/demo/), [hackathon record](docs/archive/hackathon/) |

## Data provenance

Real public data through simulated services: the UCI ServiceNow incident log
(CC BY 4.0) as day-one memory; TVmaze GB schedule (CC BY-SA) for the EPG; CC0 Kaggle
catalogs for the rights DB (licence windows synthesised by a stated rule); runbooks
adapted clause-by-clause from real published procedures (CrowdStrike CF-291, GitLab,
kube-prometheus). TMDB/IMDb were rejected on licence grounds. Nulls, duplicates and
messy metadata are kept deliberately. Full table: [docs/data-provenance.md](docs/data-provenance.md).

## Where this is going

Precedent started as a 48-hour entry to the UK AI Agent Hackathon EP5 (July 2026,
three tracks — record preserved in [docs/archive/hackathon/](docs/archive/hackathon/)).
The decided direction ([docs/DIRECTION.md](docs/DIRECTION.md)): **Precedent Gate —
change control for AI agents** — the deterministic, fail-closed gate between any
agent and the systems it touches, with the evidence pack to prove every action.
Two doors: platform teams whose own agents are blocked at change control, and
24/7 ops teams (streaming/broadcast first) where Precedent brings both the agent
and the gate. Near term: a public multi-session hosted demo, a local-first
analyzer that computes *your* repeat-fix numbers from your own ticket export
(data never leaves your machine), and paid design-partner POCs.

## License

MIT (see [LICENSE](LICENSE)). Model weights and datasets carry their own licences,
recorded next to each artifact.
