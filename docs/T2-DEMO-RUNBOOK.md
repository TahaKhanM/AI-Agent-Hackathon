# T2 Demo Runbook (console)

> Standalone, offline, no T1 / no live Jira required. If Wi-Fi dies, this still runs.
> Terminology: say **"Standing Approval"**, never "Autonomous". The permission flip is
> a **local Jira-shaped source** — say so; do not claim it hits real Jira.

## Setup (once)
```bash
make install                 # creates .venv (py3.13) + installs deps  [first time only]
python3 -m pytest -q         # expect: 56 passed   (proof the layer is real)
```

## Launch
```bash
make console                 # uvicorn on :8000   (or:)
PYTHONPATH=. python3 -m uvicorn console.app:app --reload --port 8000
```
Open **http://localhost:8000**. To reset between rehearsals: click **Reset demo**
(or `curl -XPOST localhost:8000/api/demo/reset`).

## Click sequence — what to do, see, and say

| # | Action | Expected on screen | Say |
|---|---|---|---|
| 1 | Click **Reset demo** | 3 incidents (INC-1/2/3), audit "seeded", timer starts ticking | "Fresh state — every fix here is real public data." |
| 2 | Look at the **Baseline** panel | grey **8h 51m** bar + a live **Precedent elapsed** stopwatch counting up; caveat line visible | "Manual baseline is 8h 51m business-hours MTTR — labelled, not this run." |
| 3 | On **INC-1**, click **Triage** | trace: detect → permission_check → retrieve; status → fix_found (1 hit) | "It retrieved the documented fix — permitted." |
| 4 | Click **Approve** | audit feed gains `approval_recorded` (your principal) | "One human approves." |
| 5 | Click **Promote to Standing Approval** | badge → **Standing Approval**; audit `promoted_standing_approval` | "She pre-approves the class — Standing Approval, not autonomous." |
| 6 | Glance at **Audit** panel | chain status **intact**; events accumulating | "Every step is in a hash-chained log." |
| 7 | On **INC-3**, click **Triage** | status → **refused**; "restricted — owner: Rights Ops"; **no fix text** | "It found a fix it isn't allowed to read — so it refuses and routes it." |
| 8 | (INC-3 refusal stays on screen) | denied count + owner team only | "It discloses only who owns it, never the content." |
| 9 | Click **Flip Jira permission (local-demo)** | INC-2 access **permitted → denied** (owner Rights Ops) | "A permission tightens in our local Jira-shaped source…" |
| 10 | Look at INC-2 | memory now **dark** for the scheduling principal | "…and the memory goes dark — conjunction, enforced." |
| 11 | Click **Revoke** (on a promoted class) | badge → **L1**; audit `revoked_standing_approval` | "One click takes the approval back." |
| 12 | Glance at **Audit** panel | chain status still **intact** | "The audit chain still verifies end to end." |

## What NOT to say
- ❌ "Verified against real Jira" / "real Jira flip" — it's a **local Jira-shaped source**.
- ❌ "Fully autonomous" — it's **Standing Approval** (a human clicked Promote).
- ❌ "Impossible to leak" / "production-grade" — say "test-proven, fails closed".

## Fallbacks
- **Live Jira unavailable:** expected — the demo never needs it. The flip uses the local source.
- **Console fails to start:** `python3 -m pytest tests/test_console.py -q` still proves the
  behaviour (12 tests); show that + the evidence ledger.
- **Wi-Fi down:** everything above runs offline.

## Proof commands (after the demo, if asked)
```bash
python3 -m pytest -q                 # 56 passed
make check-open-weight               # open-weight guard OK
git diff --quiet HEAD -- precedent/contracts.py precedent/models.py precedent_memory/schema.sql && echo frozen-clean
```
Full claim→evidence map: [`docs/evidence/T2-EVIDENCE-LEDGER.md`](evidence/T2-EVIDENCE-LEDGER.md).
