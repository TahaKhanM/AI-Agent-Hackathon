# Precedent — the 60-second demo

**One presenter · one browser tab · one terminal · airplane-mode OK.**

Everything you speak lands in ~60 seconds when you pace normally. The console is at
`http://127.0.0.1:8000/`. Use `scripts/run_one_min_demo.sh` in one terminal — it
prints the spoken cue for each beat and pauses on `Enter`, so you fire beats at
your speaking pace, not a stopwatch.

---

## The six beats

| # | Time | Say (verbatim) | Do | What appears |
|---|---|---|---|---|
| 1 | **0:00–0:07** | *"IT incidents take 8 hours 51 minutes on average. The fix is usually a few clicks — once you find it."* | Point at the amber banner and the Before/After strip | 8h 51m baseline, 8 human steps vs 8 Precedent steps |
| 2 | **0:07–0:25** | *"Watch what Precedent does. Messy publisher ticket lands — extractor pulls the class fingerprint from mangled fields. Deterministic policy says L2. Plan on the left, rollback on the right. One human click."* | Hit `Enter` (fires INC-1 with hold) → click **Approve** in the browser | Gate card with plan + rollback + plan_hash → green resolved banner → **Promote** appears |
| 3 | **0:25–0:32** | *"Trust this fix class — Standing Approval. Approval moves earlier in time."* | Click **Promote to Standing Approval** on INC-1 | Ladder flips to STANDING for `publisher\|PUB-4012\|schedule_item` |
| 4 | **0:32–0:42** | *"Second time the same fingerprint arrives, no human is asked. Zero LLM calls. **The second time is free.** And when a runbook is restricted, the system refuses — fail-closed. **It knows what it's not allowed to touch.**"* | Hit `Enter` (fires INC-2 fast-path) → hit `Enter` (fires INC-3 refusal) | INC-2 resolves ~15s stopwatch draw; INC-3 shows `restricted — owner: Rights Ops` |
| 5 | **0:42–0:53** | *"No LLM in the permission decision — ever. 100 adversarial probes against restricted records: zero leaks. Chain verified over on-disk audit rows. Kernel hash matches the committed manifest."* | In the browser, scroll to the BasedAI strip → click **Run 100 adversarial probes now** → click **Verify chain (real)** | `0 / 40 leaked · P99 ~40µs`; `✓ VERIFIED · rows 15+ · tail …` |
| 6 | **0:53–1:00** | *"Same loop lives on Agentverse and inside ASI:One. Every fix your org has ever applied, applied again — approval-gated, audited, reversible. That's Precedent."* | Point at the Fetch strip (agent pills + ASI:One shot + QR) | Watcher / Librarian / Operator pills all green |

---

## The two lines the room must remember

> **"The second time is free."** — automation payoff (Beat 4)
>
> **"It knows what it's not allowed to touch."** — trust story (Beat 4)

Both land in the same breath in Beat 4. If nothing else survives, those two lines do.

---

## Pre-flight (T-minus 3 minutes)

1. Terminal 1 open, cwd = `/Users/tahakhan/Documents/Work/Projects/AI-Agent-Hackathon`, venv active.
2. Verify: `curl -s http://127.0.0.1:8000/api/kernel-hash` returns `matches_manifest: true`.
3. Browser tab open on `http://127.0.0.1:8000/`, refreshed — Baseline Bar reads **8h 51m**, header shows `kernel bf0cfad5fc9e ✓ matches manifest`, ladder shows one class already STANDING (pre-seeded).
4. Terminal 2 open at the same cwd, run `bash scripts/run_one_min_demo.sh`. It prints the first cue and waits.
5. Wi-Fi OFF. Do Not Disturb ON.

---

## If it breaks

- **Console dead:** `lsof -ti:8000 -ti:8100 | xargs kill -9 && make sim &` — takes ~5 s.
- **Wrong state:** Ctrl-C the helper, `bash scripts/run_one_min_demo.sh --reset` starts over.
- **Approve button won't fire:** `curl -s -XPOST http://127.0.0.1:8000/api/drive/1/approve && echo` in Terminal 1.
- **Time gone:** cut Beat 5 to one sentence — *"Zero LLM in the gate, zero leaks, chain-verified."* — and skip Beat 6.

Everything else the presenter needs (numbers with their labels, trap wording,
Q&A) is in `Prep/PRESENTATION-PREP-GUIDE.pdf`. The full stage playbook (2:50 slot
+ video cue) is in `Prep/DEMO-DAY-RUN-PLAYBOOK.pdf`. This card is the 60-second
speed-run version.
