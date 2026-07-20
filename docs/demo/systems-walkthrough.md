# Precedent — systems walkthrough

> How the pieces connect, with the REAL commands each proves. For the presenter and any judge who asks
> "show me it's real." Everything runs airplane-mode (Wi-Fi off) from the committed seed. Seed **4207**.

## The two processes + one shared DB

```
ASI:One chat ──▶ Watcher (Agentverse mailbox agent, Agent Chat Protocol)
                     │  serve_chat_turn: full deterministic loop
                     ▼
[ demo server :8000 ]  ◀── console (server-rendered + 1.5s polling) — the judge console
   │  runs T1's orchestrator IN-PROCESS (prepare / commit_execution)
   │  writes the SHARED memory file DB  (data/precedent.db)   ← only ONE writer, no contention
   ▼
[ MediaCo sim :8100 ]  ── its own DB (data/sim.db) — scheduler / rights / publisher / KB
   reached only through the Operator's TYPED tool calls (never free-form shell)
```

- **Deterministic kernel** (`precedent/orchestrator.py`): DETECT → TRIAGE → RETRIEVE (ACL-filtered) →
  RISK-CLASSIFY (deterministic policy, no LLM) → GATE → EXECUTE (typed tools) → VERIFY (auto-rollback)
  → MEMORISE. `prepare()` runs up to the gate; `commit_execution()` runs execute→verify→memorise. The
  SAME kernel drives the console path AND the live ASI:One chat path (Watcher `serve_chat_turn`).
- **Permission memory** (`precedent_memory/`): a derived record inherits the **conjunction** of every
  source's constraints, compiled to a bitmap so a retrieval touches one indexed row (the P99 fast
  path); fail-closed retrieval; hash-chained audit; versioned Jira ACL sync via a write-behind cache
  (polling, no webhooks). Ships as a standalone importable library.
- **No LLM in the decision:** the class match is extractor-confirmed fingerprint equality; the STANDING
  fast-path makes zero `venice.chat`/`venice.embed` calls; the model only proposes fields / rationale
  prose.

## What each command proves

| Command | Proves |
|---|---|
| `make demo-reset` | resets sim + memory DB in <30s; pre-seeds the repeat class to STANDING (seed 4207) |
| `make sim` | boots sim :8100 + console :8000 sharing the file DB; drive with `curl -XPOST /api/drive/{1,2,3}` |
| `make dryrun-watcher` | the LIVE Watcher chat handler drives the full loop offline: report → ONE approval message → approve → execute → audit-hash reply; STANDING repeat is zero-LLM |
| `make bench` | conformance: FNR 0/5,219, FPR 0/4,781, 6/6 attacks, P99 0.445 µs — graded by an independent oracle (byte-identical correctness at seed 4207) |
| `make bench-extractor` | extractor robustness (a **safety** number) over the 100-mutation corpus: **0 false-fast-paths / 100**, 25/25 red-herring decoys resisted |
| `make check-open-weight` | the open-weight guard: closed-model ids appear only in `precedent/models.py` |
| `make secrets-scan` | gitleaks full-history: no secrets committed |
| `make test` | the full suite (178 tests) green |

## The dual-enforcement / refusal story (incident 3)

Flip a runbook issue's security level in Jira → two independent layers react to the same change: Jira
itself starts hiding the runbook from the non-cleared principal, AND within one poll tick Precedent
denies every memory derived from it (summaries, fix records, embeddings), with denial audit events in
BOTH logs. The refusal on stage discloses **only** the denied count + owning team — never a title,
body, or secret. That is the enterprise's purchase criterion: *it knows what it's not allowed to touch.*
