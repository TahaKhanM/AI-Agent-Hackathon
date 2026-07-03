# Submissions prep — everything reduced to one human click/paste

T3 prepared these so each human submission step is a copy/paste or a one-click. Nothing here holds
a secret or a closed-model id. Verify with `make freeze-check` before use.

| File | What the human does with it | When |
|---|---|---|
| [`BASEDAI-PR-README.md`](BASEDAI-PR-README.md) | Commit as `UK-AI-Agent-EP5/submissions/<team>/README.md` in the BasedAI fork. 8 verbatim template headings; open-weight declaration with the 4 pinned ids byte-for-byte; six attacks named; measured bench table; `docs/compliance/` cites. Replace `[[WAIT:VIDEO-LINK]]` (Sat) + `[[WAIT:MENTOR-ANSWER]]` (G0). | G0 draft → G2 numbers → G4 video |
| **`.env.example` (repo root)** | Copy the repo-root `.env.example` to `submissions/<team>/.env.example`. It is **already Venice-only** — the generic template's `ANTHROPIC`/`OPENAI` keys are absent; do not add them. | G0 |
| [`SCRUB-AND-PUBLISH-CHECKLIST.md`](SCRUB-AND-PUBLISH-CHECKLIST.md) | Run the A–E secrets scrub, the repo-public pre-flight, flip visibility, verify logged-out, write the evidence line. | G1→G2 |
| [`DORAHACKS-WORKSHEET.md`](DORAHACKS-WORKSHEET.md) | Fill the BUIDL for event 2272, tick bounties 1370/1367/1364, enter the locked one-shot answers verbatim with T1 sign-off. | G3 |
| [`../../docs/evidence/T3-AGENTS-VERIFICATION.md`](../../docs/evidence/T3-AGENTS-VERIFICATION.md) | Paste-ready Agentverse profile blocks (badges + description) per agent; the registration runbook is in `agents/README.md`. | G0 |
| [`../../docs/MUTATION-CORPUS-HANDOFF.md`](../../docs/MUTATION-CORPUS-HANDOFF.md) | Hand the seed-4207 mutation corpus to T1 (~18:30); record the one robustness number for chip/slide 10/README/BUIDL. | G1 |

## Number-honesty reminders (the caveats every surface must carry)

- The bench numbers (FNR/FPR/latency/etc.) are **measured** by `make bench` at seed 4207, graded by
  an **independent oracle** — state that explicitly (FNR = 0 is a cross-check result, not a
  tautology). The FNR row states **deny-expected N + leak count**, never a bare %.
- UCI realism is always the "**25k-record store**", never "P99 over 141k events".
- Extractor robustness is one measured number (T1's bench over T3's corpus) reused on all four
  surfaces — do not re-derive per surface.
- Re-run `make bench` against merged main at the G2 freeze to refresh the table before the PR commit.
