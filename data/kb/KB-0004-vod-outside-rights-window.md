---
id: KB-0004
title: "VOD item published outside its licence window — takedown and republish"
service: rights
error_codes: [RGT-WIN-014]
target_object_type: vod_item
adapted_from: "https://www.ofcom.org.uk/siteassets/resources/documents/tv-radio-and-on-demand/reviews-and-investigations/broadcast-incidents/incident-review-red-bee-media.pdf"
adapted_from_note: "takedown + republish / as-run reconciliation duties adapted from the Ofcom Red Bee review; failure mode references the publicly reported MGM/Starz exclusivity-window case as industry context only"
source_licence: "public regulator report"
acl: rights-ops-only
stale: false
owner: "MediaCo Rights Ops"
last_reviewed: 2026-05-09
---

# VOD item published outside its licence window — takedown and republish

## Symptoms
A VOD item is available on-demand while its rights record shows the licence window as not-yet-open or already-expired. The Rights service raises `RGT-WIN-014` when a catalogue item's `availability_start`/`availability_end` no longer bracket the current time but the item is still `state: live` in the publisher. The Rights catalogue browser flags the item with a red "outside window" badge; the as-run availability log shows the item served after `availability_end`. This is the failure mode publicly reported in the MGM/Starz exclusivity-window case, where 244 titles were reportedly streamable past their contracted windows — used here only as industry context, not a MediaCo incident.

## Preconditions
- You hold a `rights-ops` role (this runbook is ACL-restricted; the item's rights record is Rights Ops-only).
- The rights record carries an authoritative window; confirm it is not itself stale before acting on it.
- You have the `vod_item` id, its `title_id`, and the licensing counterparty from the `RGT-WIN-014` event payload.

## Steps
1. Open the item in the Rights catalogue browser and confirm the current time falls outside `[availability_start, availability_end]`. Record the licence window and the counterparty from the rights record (source analogue: as-run reconciliation of playout against the licensing schedule, §4.5).
2. Capture the current published state to the rollback note: `GET /publisher/vod_item/{id}` and store the returned manifest, `state`, and CDN edge status (MediaCo-specific).
3. Take the item down: `POST /publisher/vod_item/{id}/takedown` with `reason=RGT-WIN-014`. This unpublishes the manifest and purges CDN edges so the item stops serving immediately (source analogue: removal of non-compliant on-demand content, Table 1, 26 Sep entry).
4. Confirm the item is no longer reachable on any distribution surface via the Publisher availability console (source analogue: verifying output was actually removed across platforms, §5.18–5.20).
5. If the window has not yet opened, schedule republish for `availability_start` in the Rights catalogue browser rather than republishing now. If the window has genuinely re-opened (corrected rights record), continue.
6. Republish only inside a valid window: `POST /publisher/republish` with the corrected `availability_start`/`availability_end` from the rights record so the publisher re-derives the on-demand schedule (source analogue: re-adding compliant content and reconciling it against the schedule retrospectively, Table 1, 22 Nov entry).

## Verification
Green is: the item shows `state: live` **only** when the current time is inside the licence window, `RGT-WIN-014` clears in the Rights service, and the as-run availability log for the item contains no served requests after `availability_end` (or before `availability_start`). The Rights catalogue browser badge returns to green. If the window is not yet open, green is the item absent from all surfaces with a scheduled republish pending at `availability_start`.

## Rollback
Prepared before step 3 executes. If takedown or republish causes a worse state (e.g. an in-window item wrongly pulled), restore the captured state from step 2: `POST /publisher/republish` with the stored manifest and the original `availability_start`/`availability_end`, then purge and re-warm CDN edges. Because rollback republishes only the previously-served, in-window manifest, it cannot re-expose an item outside its window. Confirm via the Publisher availability console that the item's served state matches the pre-change capture (source analogue: escalation back-up plan should the primary process fail, §5.16).

## Owner & escalation
Owner: MediaCo Rights Ops. If the rights record itself is contradictory or the counterparty window is disputed, do not republish — escalate to the Rights Ops on-call lead and the Rights Legal duty contact, who join the incident bridge to confirm the authoritative window before any republish (source analogue: Incident Manager contacts stakeholders and convenes the DR playout conference, §5.15). No safe automated republish exists while the window is disputed; hold the item down and fail closed.
