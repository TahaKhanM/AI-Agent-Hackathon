# Precedent Gate API (`/v1/gate`)

The versioned HTTP spine of Precedent. Every other surface — the console, the Fetch.ai
rails, a future MCP shim — is a *client* of this API. The console dogfoods it over HTTP.

It exposes the deterministic approval gate as three operations and **adds no decision logic
of its own**: verdicts come from `precedent.policy` + `precedent.ladder`, execution from
`precedent.orchestrator`. The model may propose prose elsewhere; it never touches this path.

## Operations

| Method | Path | Purpose |
|---|---|---|
| `GET`  | `/v1/gate` | Honest self-description of the gate's trust posture. |
| `POST` | `/v1/gate/propose` | Submit a typed proposal (incident + structured extraction + intended action). Runs extractor/fingerprint → `policy.assess` → ladder. Returns `deny` \| `needs-approval(ref, expires_at)` \| `allow-standing`. |
| `GET`  | `/v1/gate/decision/{ref}` | Current state of a held decision: `pending` \| `approved` \| `denied` \| `expired`. |
| `POST` | `/v1/gate/outcome` | Approve (or reject) a held `ref`, execute-in-sim through `commit_execution`, and record the verified/rolled_back outcome + audit rows. |

- A class at **Standing Approval** ⇒ `allow-standing` (the zero-LLM fast path).
- A policy-permitted, non-standing class ⇒ `needs-approval` with a 10-minute TTL reference
  (recorded through `agents.approval.record_pending`, the same ledger the demo server uses).
- A policy-denied / uninvertible class, or a fix the caller's principal cannot access
  (ACL-restricted), ⇒ `deny`.

## Trust posture (read before wiring a client)

**No LLM in the decision path.** `gate/service.py`, `gate/api.py`, `gate/models.py` and
`gate/world.py` import no model backend and make no inference call. `propose` runs
`orchestrator.prepare(..., defer_rationale=True)` and never calls `fill_rationale`, so the
slow-path prose network call cannot fire inside a decision. An unrecognised `error_code` is
denied *before* the pipeline runs, so the extractor's LLM-proposal branch is unreachable from
the gate. `tests/test_gate_api.py` proves a full propose→decide→outcome cycle makes **0**
model calls, and stubbing an LLM into the path fails that test.

**Principals are registered OUT-OF-BAND.** `principal` (proposer) and `approver_principal`
(approver) are supplied in the request body and are expected to have been registered through
config/API. The gate **does not trust an MCP client's self-asserted identity** — there is no
robust MCP client-identity standard in 2026, so binding execution authority to a client claim
would be unsafe. A `GateWorld` may carry a registered-principal set; an unregistered
proposer/approver is a non-action.

**Fail-closed.** An expired or absent `ref` is a non-action: `get_decision` reports `expired`
and `report_outcome` refuses to execute, each writing a fail-closed audit row. The pending
registry is in-process by design — a restart drops held decisions to non-action rather than
resurrecting a stale approval. The plan-hash tamper check inside `commit_execution` binds the
approved hash to the exact plan that runs.

**No usage-metering from the audit log.** The SQLite hash-chained audit log is an integrity
and provenance record, **not** a billing meter (a DIRECTION prohibition). Any
usage/metering feature must be built on a separate store (Postgres option first), never
derived from the audit rows.

**Terminology.** The top ladder level is **Standing Approval**, never "Autonomous".

## Backing world (injectable)

The gate operates on an injectable `GateWorld` (`gate/world.py`): a permission-aware memory
connection + a typed tool client (`SimTools`-shaped) + a single-writer lock + the pending
registry. This makes the router both independently `TestClient`-testable against a freshly
seeded world (`build_seeded_world`) and mountable into the deployed console, where the world
is the current browser session's private db + in-process sim. A real deployment points `conn`
at a persistent store and `tools` at the live typed-tool endpoints.

## Mounting

One deploy. `console/app.py` mounts the router into the served app:

```python
from gate.api import make_gate_router
from gate.world import gate_world_from_session
app.include_router(
    make_gate_router(lambda request: gate_world_from_session(_session(request))),
    prefix="/v1/gate",
)
```

For an isolated single-tenant app: `create_gate_app(world)` returns a standalone FastAPI with
the router mounted at `/v1/gate`.
