---
id: KB-0003
title: "Schedule slot overlap after a late change"
service: scheduler
error_codes: [SCH-OVL-204]
target_object_type: schedule_item
adapted_from: "https://www.ofcom.org.uk/siteassets/resources/documents/tv-radio-and-on-demand/reviews-and-investigations/broadcast-incidents/incident-review-red-bee-media.pdf"
adapted_from_note: "late-change / overrun cascade handling adapted from the Ofcom Red Bee incident review; runbook structure follows GitLab public runbooks"
source_licence: "public regulator report"
acl: public
stale: false
owner: "MediaCo Scheduling Ops"
last_reviewed: 2026-05-02
---

# Schedule slot overlap after a late change

## Symptoms

- The scheduler rejects a publish with error code `SCH-OVL-204` ("slot overlap") and the affected `schedule_item` rows are flagged `conflict`.
- Two or more items on the same channel resolve to overlapping start/end windows after a late edit — typically an overrun on the preceding programme, or a manual runtime change pushed close to air.
- Downstream EPG feeds show a duplicated or missing slot; viewer-facing metadata for the disputed window is inaccurate. As in the Ofcom review, inaccurate schedule/EPG data after a disruption is treated as a viewer-impacting fault, not a cosmetic one.
- The overlap cascades: fixing the first collision shifts the following item into the next, so several consecutive slots are affected.

## Preconditions

- You are operating on a single channel schedule for one broadcast day; confirm the channel and date before touching anything.
- The overlap originates from a **late change** (an edit made after the schedule was locked) or a **programme overrun**, not from a corrupt import.
- You hold Scheduling Ops write access and the channel is not currently in a Disaster Recovery / failover state (if it is, escalate — do not hand-edit).
- A schedule snapshot exists for this channel/day (auto-captured on lock). If none exists, capture one before proceeding (Step 1 covers this).

## Steps

1. Open the affected day in the **Scheduler admin console** and export the current locked schedule as a rollback snapshot via `POST /scheduler/snapshots` (records the pre-change state so recovery is deterministic).
2. In the console, run the overlap report for the channel/day to list every `schedule_item` with a `conflict` flag and identify the originating late change or overrun.
3. Freeze automated re-publish for this channel with `POST /scheduler/publish/hold` so the cascade is not pushed to distribution while you work (MediaCo-specific).
4. Correct the originating item first: adjust its end time (or trim the overrun) via `PATCH /scheduler/items/{id}` so it no longer overlaps its successor.
5. Re-sequence the following items in the console using the ripple-adjust action, working forward until no item carries a `conflict` flag. Confirm each corrected slot against the rights window for that item (MediaCo-specific).
6. Regenerate downstream EPG/schedule metadata for the corrected window via `POST /scheduler/epg/rebuild` so viewer-facing data matches the on-air sequence — the Ofcom review specifically calls for restored schedule/EPG data to be accurate.
7. Release the publish hold with `POST /scheduler/publish/resume` and republish the corrected day.

## Verification

Green looks like: the overlap report for the channel/day returns **zero** `conflict`-flagged `schedule_item` rows, the re-published schedule shows `status: published` for every slot, and `GET /scheduler/epg/preview?channel=&date=` renders a contiguous, gap-free, non-overlapping sequence for the full broadcast day. Distribution confirms `SCH-OVL-204` is cleared.

## Rollback

Prepared **before** the fix is attempted (Step 1 captured the snapshot). If any step produces a worse state — new conflicts, a gap, or wrong EPG data — restore immediately with `POST /scheduler/snapshots/{snapshot_id}/restore`, which reverts every `schedule_item` on the channel/day to the locked pre-change state, then release the hold with `POST /scheduler/publish/resume`. The channel returns to its last-known-good published schedule; re-open the incident and escalate rather than re-attempting hand edits.

## Owner & escalation

Owner: **MediaCo Scheduling Ops**. Escalate to the **Scheduling Ops on-call lead** if the cascade spans more than one channel, if a corrected slot has no valid rights window, or if the channel is in DR/failover — in line with the Ofcom recommendation that late-change and DR recovery be handled by trained operators following tested procedures, with viewer communications prepared for any service interruption.
