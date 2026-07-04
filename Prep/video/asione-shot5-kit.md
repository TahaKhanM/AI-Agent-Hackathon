# Shot 5 — ASI:One human capture kit (the ONE account-bound take)

> Everything else in the video is captured and assembled from the frozen seed-4207 build (see
> `Prep/video/pipeline/`). **Shot 5 is the only human-required capture** — it must be recorded from a
> real ASI:One session under a real account (account-bound; a machine can't log in for you). This kit
> reduces it to a **paste-and-record** action with a rehearsed splice. Budget: one clean take + the
> shared-chat URL. Do it Friday ~21:00 against the frozen agents (per `04 §7`).

## Before you hit record (2-minute setup)

- [ ] ASI:One open in a clean browser window, **maximised, no console anywhere on screen**, no other
      tabs visible, notifications off. Cursor visible.
- [ ] The three Agentverse agent profile tabs **pre-opened** (gateway / retrieval / execution) with
      their **addresses visible** and the **Innovation Lab + hackathon badges** on screen — for the
      2-second cut-away at the end.
- [ ] A **stopwatch** visible somewhere on screen (phone clock in a corner is fine) for the ~15s
      standing-approval beat — timestamp-anchored proof.
- [ ] Screen recorder at **1920×1080, 30fps** (QuickTime/OBS). Save the take as
      `precedent-video-drop/raw/shot5-{take}.mov` (highest take number wins; never overwrite).

## The script — paste these EXACT messages, in order

**Turn 1 (you type):**
```
our EPG publish to the evening slot failed, error 4012 i think — can you fix it?
```
→ *Agent replies with ONE well-formatted message:* triage → matched precedent → **risk class LOW** →
execution plan + rollback plan → "reply **approve** to execute". (Let it settle; don't rush.)

**Turn 2 (you type):**
```
approve
```
→ *Agent streams:* executing → verified → **Jira ticket link** (let it cut ~2s to the ticket closing)
→ audit-trail link, **approver recorded as your chat-sender address**.

**Turn 3 (same session — the repeat, "three days later"):**
```
same class of publish just failed again on tomorrow's 8pm film — can you sort it?
```
→ *Agent resolves it under **Standing Approval** in **~15 seconds**, the timer quoted in the reply,
nobody approving.* This is **"the second time is free."** Watch the stopwatch hit ~15s.

**Then:** brief cut-away to the three Agentverse profile tabs (addresses + badges).

> Do NOT type the refusal here — the refusal beat lives in shot 6 (the console take), already captured.
> Shot 5 stays clean: report → plan → approve → close → repeat-in-15s. (This is the V1 fork fix.)

## Capture the artifacts THE SAME NIGHT (before you close the tab)

- [ ] **Public shared-chat URL** — copy it immediately. Paste into the DoraHacks/Devpost drafts and
      the README, pointing to the exact turn where the 15s standing-approval run happens
      ("jump to the incident-2 turn"). (One is already on file:
      `asi1.ai/invite?channelInviteKey=…` in `docs/evidence/LIVE-PROOFS.md` — replace only if you
      re-record.)
- [ ] Screenshot the 3 Agentverse profiles (addresses + `tag:innovationlab` + `tag:hackathon`).

## Splice — one command, rehearsed with a placeholder

The master currently uses an on-brand **placeholder card** in shot 5's 80-second slot
(`asset_asione_placeholder.png`). When your `.mov` lands:

1. Drop it at `precedent-video-drop/raw/shot5-{take}.mov`.
2. In `precedent-video-drop/manifest/edit-manifest.json`, change shot 5 from the placeholder card to
   the take — set `"kind":"video"`, `"src":"video:shot5-{take}.mov"`, `"fit":"fit"` (keep
   `"slot":80`; if the raw take is longer, set an `"in"/"out"` window that keeps the report→plan→
   approve→close→repeat beats and the 15s stopwatch).
3. Re-run the whole pipeline (regenerates captions.srt, re-assembles, re-derives the cuts):
   ```bash
   source precedent-video-drop/scratch/env.sh
   .venv/bin/python Prep/video/pipeline/assemble.py all 2      # bumps to v2
   ```
4. Re-run the gates (`export-gates` workflow) and confirm: master ∈ [4:15,4:45], **shot-5 segment
   ≥ 78 s**, the **approver-principal frame (chat sender address) legible at 1080p**, both memorable
   lines still present. Record the shipped version in `docs/evidence/` (see the ship kit).

**Rehearsed:** the placeholder already occupies the exact 80-second slot, so the splice is a source
swap + one re-run — the timeline, captions, VO, and cuts all re-derive from the one manifest.
