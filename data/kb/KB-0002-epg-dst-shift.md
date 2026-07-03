---
id: KB-0002
title: "EPG timezone/DST shift — listings off by one hour"
service: scheduler
error_codes: [SCH-DST-118]
target_object_type: schedule_item
adapted_from: "https://infomir.store/mismatch-in-tv-program-schedules-how-to-fix-epg-shift-time-zones-and-dst/"
adapted_from_note: "EPG time-zone/DST shift fix adapted clause-by-clause from the Infomir published procedure"
source_licence: "public bulletin"
acl: public
stale: false
owner: "MediaCo Scheduling Ops"
last_reviewed: 2026-04-22
---

# EPG timezone/DST shift — listings off by one hour

## Symptoms

- Published EPG listings render one hour early or late against the actual broadcast start; viewers report programmes "starting at the wrong time".
- The scheduler emits `SCH-DST-118` on affected `schedule_item` rows, flagging a mismatch between the item's stored start and its resolved local wall-clock time.
- Off-by-one skew clusters around a recent DST transition, or on channels whose feed time zone differs from the publish region. Larger multi-hour shifts usually point to a feed-level offset rather than DST.
- Downstream recording rules and "now/next" banners fire against the wrong slot.

## Preconditions

- You hold Scheduling Ops write access; changes touch `schedule_item` start times for a single channel/day.
- The incident is scoped to one channel and date range (do not batch-correct the whole grid).
- A source of truth for correct local start times is available (broadcaster affiliate sheet or the region's authoritative EPG feed).
- No unrelated freeze/embargo is active on the target channel.

## Steps

1. Open the Scheduler admin console and load the affected channel + date range so the skewed `schedule_item` rows are visible.
2. Verify the scheduler's clock reference: confirm the service is synchronised to the platform NTP source and the item timestamps are stored in UTC (adapts source step "verify device clock"). (MediaCo-specific)
3. Check the channel's configured time zone via `GET /scheduler/channels/{id}/timezone`. Set it explicitly to the correct IANA zone rather than relying on auto-detection, which the source flags as unreliable.
4. Confirm the DST rule for that zone is current for the incident date, so the console derives the right UTC↔local offset across the transition (adapts source step "DST alignment").
5. If the clock and zone are already correct, apply a manual EPG offset to the affected rows: `POST /scheduler/schedule-item/offset` with the signed hour delta and the exact `schedule_item` id range (adapts source step "manually add or subtract hours").
6. Prefer correcting the ingest source over patching output: point the channel at the region-specific EPG feed rather than the global feed, per the source's "use reliable EPG sources" step. (MediaCo-specific)
7. Republish the corrected day to the guide from the Scheduler admin console.

## Verification

Green = every `SCH-DST-118` flag on the corrected channel/date is cleared, and each `schedule_item`'s resolved local start equals the source-of-truth start to the minute (skew = 0). Spot-check the published "now/next" banner and one recording rule against the broadcaster sheet; both must line up. Re-running the scheduler consistency check for that channel/date returns zero DST-shift findings.

## Rollback

Before any change, snapshot the affected rows: `GET /scheduler/schedule-item?channel={id}&date={d}` and store the returned start times and time-zone config as the pre-change baseline (the agent writes this plan before execution). If verification fails or new skew appears, restore by re-applying the saved starts via `POST /scheduler/schedule-item/offset` with the inverse delta (or restoring the snapshot), revert the channel time-zone/feed change, and republish the day. Confirm the grid matches the pre-change baseline before standing down.

## Owner & escalation

Owner: MediaCo Scheduling Ops. If the skew persists after correcting clock, zone, DST rule, and feed — or if it spans multiple channels or an entire region (pointing to a platform NTP or feed-provider fault) — escalate to the Platform Time Services on-call and open a feed-provider ticket. Do not mass-edit the grid to mask an upstream offset.
