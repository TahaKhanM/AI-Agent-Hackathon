# Selection-branch staging (B12, reach) — both branches pre-staged

> BUILD-PLAN §5 marks the attract-mode idle loop + live RESTRICT hotkey as **selection-branch**
> items (build the on-stage versions ONLY if selected to present) and the change-record as a
> reach artifact. The presenter selection is announced **~22:00 Fri**. This file stages BOTH
> outcomes so the human's call is **one switch**. Per §5.1 cut order, these are the first items to
> cut — the floor (incidents 1+2+R+3, Fetch gates, the vertical slice) is never touched.

## The one decision (call after the ~22:00 announcement)

| If… | Then present with… | Not-selected fallback |
|---|---|---|
| **SELECTED to present** | attract-mode idle loop + the live RESTRICT hotkey + (optionally) the change-record on a hotkey | — |
| **NOT selected** | — | the RESTRICT flip becomes a **video insert** (already in the video shot-list dual-enforcement/refusal beat, shot 5–6); the **90-second cut goes FIRST on the BUIDL page** |

Everything below is prepared; the human flips exactly one of these two states.

## ✅ BUILT NOW — the change-record artifact (renders from real audit rows)

`scripts/render_change_record.py` renders any incident's hash-chained audit trail as an ITIL-style
change document — deterministically, no LLM, no network. Verified against real audit rows
(`tests/test_change_record.py`, 2 tests). One command:

```bash
.venv/bin/python scripts/render_change_record.py INC-1 --out /tmp/CHG-INC-1.md   # implemented+verified
.venv/bin/python scripts/render_change_record.py INC-3                            # REFUSED, no restricted body
```

The refusal change-record discloses only the status + owning team — **never the restricted runbook
body** (asserted by the test). Bind it to a console hotkey in the SELECTED branch, or attach the
rendered `.md` as a submission artifact in either branch.

## SELECTED branch — pre-staged wiring (enable if presenting)

Both features reuse mechanisms that already exist; each is a thin, additive console handler behind a
flag, so nothing touches the floor demo:

1. **Attract-mode idle loop.** From doors-open, drive the three seeded incidents on a timer so the
   console is always showing a live resolution when a judge walks up. Ready-to-wire: a small loop that
   POSTs `/api/drive/{1,2,3}` (fast-path incident 2 first — the "second time is free" wow) every N
   seconds against the seeded state, guarded by `PRECEDENT_ATTRACT=1` so it never runs in the scored
   demo. Reset with `make demo-reset` before the real pitch.
2. **Live RESTRICT hotkey → dual-enforcement deny → restore.** The dual-enforcement path already
   exists (the Jira-shaped ACL source + the versioned sync + fail-closed retrieve). Ready-to-wire: a
   keypress that (a) flips KB-0004/KB-0005 to restricted on the **local Jira-shaped source** (the
   single-account role-flip fallback — no live-Jira creds needed on stage), (b) triggers one sync
   tick, (c) shows the same memory query flip from *allowed* to *denied* (owner-team only, no body),
   (d) restores on a second keypress. The **live-Jira** version of this flip is an **account-bound
   human act** (see the closing walkthrough G7/G15) — the local role-flip fallback is what runs on
   stage.

## NOT-SELECTED branch — the RESTRICT flip as a video insert (already staged)

If not selected, no console feature ships; the RESTRICT/dual-enforcement moment is the **refusal +
revocation beat in the recorded video** (`Prep/video/shot-list.md` shots 5–6, ~60 s ASI:One + refusal;
`Prep/video/vo-script.md` shot 6). The **90-second cut** (`Prep/video/cut-plans-30s-90s.md`) goes first
on the BUIDL page. Nothing extra to build — the video plan already carries it.

## Guardrails (both branches)

- The RESTRICT flip is a **local Jira-shaped source** flip on stage, never "a real Jira flip" (the
  live version is the human's account-bound act). Never claim live-Jira on stage.
- The refusal/deny always discloses **only** `denied_count` + owning team — no restricted body, on the
  console, in the video, or in the change-record.
- Attract-mode is gated off (`PRECEDENT_ATTRACT` unset) during the scored demo; `make demo-reset`
  before the real pitch so the elapsed bars are clean.
