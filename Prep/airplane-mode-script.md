# Airplane-mode rehearsal script

> The demo MUST pass with Wi-Fi off — venue Wi-Fi is hostile and the fast-path must be provably
> zero-LLM. This is the exact sequence, with the real commands. Seed **4207**; everything runs from the
> committed snapshot. Point Venice at an unreachable URL so any accidental LLM call fails fast (proving
> the standing fast-path never needs one).

## 0. Turn Wi-Fi OFF. Then:

```bash
cd <repo root>
# hermetic: Venice unreachable → airplane-mode, and the fast-path is provably zero-LLM
export VENICE_BASE_URL="http://127.0.0.1:9/unreachable"
export PRECEDENT_SIM_DB="data/sim.db"
export PRECEDENT_MEMORY_DB="data/precedent.db"
export PRECEDENT_SIM_URL="http://127.0.0.1:8100"

make demo-reset            # <30s; pre-seeds the repeat class to STANDING
make sim                   # sim :8100 + console :8000 (Ctrl-C stops both)
```

## 1. Drive the three incidents (in another shell, same env)

```bash
curl -s -XPOST http://127.0.0.1:8000/api/drive/1 && echo     # slow-path, human-approve → resolved
time curl -s -XPOST http://127.0.0.1:8000/api/drive/2 && echo # STANDING fast-path → resolved, near-instant
curl -s -XPOST http://127.0.0.1:8000/api/drive/3 && echo     # restricted → refused
```

Expected (byte-identical each run):
```
{"incident":1,"verified":true,"rolled_back":false,"outcome":"resolved"}
{"incident":2,"verified":true,"rolled_back":false,"outcome":"resolved"}   # real ~0.02–0.03s
{"incident":3,"verified":false,"rolled_back":false,"outcome":"refused"}
```

## 2. Prove zero-LLM on the standing path + no restricted-body leak

- Incident 2 resolves in ~0.03s with Venice pointed at an unreachable URL → the fast-path made **no LLM
  call** (any call would have hung/failed on the unreachable URL). The committed spy test
  (`tests/test_watcher_live_loop.py::test_chat_standing_fast_path_is_zero_llm` and
  `tests/test_t1_orchestrator.py::test_incident2_fast_path_is_zero_llm`) asserts this structurally.
- Confirm the refusal discloses only the owner team, no body:
  ```bash
  curl -s http://127.0.0.1:8000/api/state | grep -o '"denied_owner_team":"[^"]*"'   # → "Rights Ops"
  # leak probe (all must be ABSENT): takedown · RGT-WIN-014 · republish
  curl -s http://127.0.0.1:8000/api/state | grep -c -E 'takedown|RGT-WIN-014|republish'   # → 0
  ```

## 3. The live Watcher chat loop, offline (optional, proves the ASI:One path without a network)

```bash
make dryrun-watcher   # report → ONE approval message → approve → execute → audit-hash reply; standing = zero-LLM
```

## 4. Recovery beat (optional, for the recovery rehearsal)

```bash
curl -s -XPOST http://127.0.0.1:8000/api/drive/2/flake && echo   # inject verification failure → rollback → demote
```

## Pass criterion

All three drives return the expected outcomes with Wi-Fi OFF; incident 2 is near-instant (zero-LLM);
the refusal shows only "Rights Ops" with the leak probe returning 0. If any of these fails airplane-mode,
STOP — do not present live; the rehearsal gate flips to RECORDED (see `rehearsal-gate-checklist.md`).
