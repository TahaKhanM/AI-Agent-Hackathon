---
id: KB-0001
title: "EPG publish failure — missing or invalid episode metadata"
service: publisher
error_codes: [PUB-4012]
target_object_type: schedule_item
adapted_from: "https://github.com/dp247/Freeview-EPG"
adapted_from_note: "publish-validation rules adapted from XMLTV format requirements; failure modes are real TVmaze null-field defects (missing synopsis, missing season/episode numbers, null runtime)"
source_licence: "GPL-3.0"
acl: public
stale: false
owner: "MediaCo Scheduling Ops"
last_reviewed: 2026-05-14
---

# EPG publish failure — missing or invalid episode metadata

## Symptoms
- The electronic programme guide (EPG) shows a **blank slot** on one or more TV platforms — e.g. the 9pm slot renders empty on Sky Q, Freeview, or Virgin while surrounding programmes display normally.
- The publish job for the affected `schedule_item` is **rejected with error `PUB-4012`** ("invalid episode metadata") in the Publisher job log; the XMLTV document is never emitted for that slot.
- The slot exists and is correctly timed in the Scheduler, but one or more required programme fields are missing or null: **synopsis/description, season number, episode number, or runtime**.
- The originating ticket may arrive **garbled, colloquial, or with a wrong description** — e.g. "the guide thingy is blank for the 9pm slot" — with no error code, channel, or programme id. Do not act on the ticket wording alone; confirm the failing `schedule_item` from the Publisher log before proceeding.

## Preconditions
- You can identify the affected `schedule_item` id, channel, and transmission date/time from the Publisher job log or the Scheduler admin console.
- You have write access to the schedule item's metadata via the Scheduler admin console (role: Scheduling Ops).
- The upstream metadata source (TVmaze-derived catalogue) is reachable, or a manually-verified synopsis/season/episode/runtime is available.
- No downstream freeze window is active for the target platform.

## Steps
1. Open the failed job in the **Publisher job log** and confirm the error is `PUB-4012`; record the exact `schedule_item` id, channel, and slot time it names.
2. Fetch the current metadata for that item via **GET /publisher/schedule_item/{id}** and note which required fields validate as missing or null: `synopsis`, `season_number`, `episode_number`, `runtime_minutes`.
3. In the **Scheduler admin console**, open the schedule item and cross-check its linked programme record for the same gaps (TVmaze null fields are the common root cause).
4. Populate every missing required field: enter the synopsis (non-empty), the integer season and episode numbers, and a positive integer `runtime_minutes` that matches the slot duration. Do not invent values — copy them from the verified source record.
5. If runtime must be derived from the slot rather than the source, set `runtime_minutes` to the slot's scheduled duration and flag the item for catalogue backfill. (MediaCo-specific)
6. Save the metadata in the Scheduler admin console, then re-validate without publishing via **POST /publisher/validate** for the `schedule_item`.
7. When validation returns no `PUB-4012`, re-emit the guide entry via **POST /publisher/republish** for that `schedule_item` and channel.

## Verification
Publish is "green" when: **POST /publisher/republish** returns HTTP 200 with no `PUB-4012`; the Publisher job log shows the item as `PUBLISHED`; and the regenerated XMLTV entry for the slot contains non-empty `<desc>`, an `<episode-num>` carrying both season and episode, and a positive `<length>`. Confirm the previously blank slot now renders the programme title and synopsis on the affected platform's EPG preview (e.g. the Sky Q guide preview).

## Rollback
Prepare this rollback **before** editing any metadata:
1. Before step 4, capture the current metadata snapshot via **GET /publisher/schedule_item/{id}** and save the JSON as the pre-change baseline. (MediaCo-specific)
2. If re-publish fails validation differently, worsens the guide, or the edited values prove wrong, restore the snapshot via **PUT /publisher/schedule_item/{id}** with the saved baseline body.
3. Re-run **POST /publisher/republish** for the item to return the guide to its prior (blank-but-known) state, then re-escalate.
Rolling back restores the last known state; the slot may remain blank until correct metadata is sourced, which is the safe outcome versus emitting wrong episode data.

## Owner & escalation
Owner: **MediaCo Scheduling Ops**. If the required metadata cannot be sourced (upstream catalogue record itself is null and no verified value exists), or if `PUB-4012` persists after valid fields are supplied, escalate to the **Publisher platform on-call** with the `schedule_item` id, channel, slot time, and the validation output. Do not leave a blank slot in the guide past the next 12-hour EPG rebuild without an escalation on record.
