---
id: KB-0009
title: "As-run log reconciliation mismatch"
service: scheduler
error_codes: [SCH-ASR-330]
target_object_type: as_run_log
adapted_from: "https://www.ofcom.org.uk/siteassets/resources/documents/tv-radio-and-on-demand/reviews-and-investigations/broadcast-incidents/incident-review-red-bee-media.pdf"
adapted_from_note: "as-run reconciliation duties adapted from the Ofcom Red Bee review; no source extract used — real runbook structure only"
source_licence: "public regulator report"
acl: public
stale: true
owner: "MediaCo Traffic & Playout"
last_reviewed: 2022-09-20
---

# As-run log reconciliation mismatch

## Symptoms

- The scheduler raises `SCH-ASR-330` ("as-run reconciliation mismatch") for one channel/broadcast-day: the ingested as-run log does not agree with the planned schedule.
- The affected `as_run_log` rows are flagged `unreconciled` — a programme was transmitted at a different time or duration than planned, an item is missing from the as-run, or an unplanned item (slate, filler, promo) appears with no matching `schedule_item`.
- Reconciliation counts commonly spike after a playout disruption or a Disaster Recovery switchover, where the sequence actually transmitted diverges from the locked plan and a backlog of corrections builds up — the pattern the Ofcom Red Bee review describes when transmitted output and scheduled programming fall out of step.
- Downstream billing/airtime reports and access-service (subtitle/audio-description) records for the day are inaccurate until the log is reconciled.

## Preconditions

- You hold Traffic & Playout write access and are reconciling **one channel for one broadcast day**; confirm the channel and date before touching anything.
- The playout system is out of any active DR/failover state — reconcile only against a stable as-run feed, never mid-incident.
- A trusted as-run source is reachable. NOTE (stale): older revisions of this runbook pulled the raw as-run drop from `/mnt/asrun-dropbox/` — that file-drop directory was **retired** and no longer exists; do not rely on it. Confirm the current as-run ingest path with Playout Ops before starting.
- The planned schedule for the channel/day is locked and available as the reconciliation baseline.

## Steps

1. Open the affected day in the **Scheduler admin console** and export the current `as_run_log` plus the locked schedule as a rollback snapshot via `POST /scheduler/snapshots` (records the pre-reconciliation state so recovery is deterministic).
2. Re-ingest the as-run feed from the **current** ingest path via `POST /scheduler/asrun/ingest` and confirm the row count matches the transmitted item count for the day (do not use the retired dropbox path). (MediaCo-specific)
3. In the console, run the reconciliation report for the channel/day to list every `as_run_log` row flagged `unreconciled` and its mismatch reason (time shift, duration delta, missing, or unplanned).
4. Freeze automated airtime/billing export for this channel/day with `POST /scheduler/export/hold` so unreconciled data is not pushed downstream while you work. (MediaCo-specific)
5. Resolve each mismatch against the locked schedule: match shifted or re-timed items to their planned `schedule_item` and accept the actual transmitted times via `PATCH /scheduler/asrun/{id}`; tag genuinely unplanned items (slate, filler, DR promo) with a reason code rather than forcing a false match.
6. For a transmitted item that carried access services differently than planned, correct the access-service fields on the `as_run_log` row so EPG and compliance records reflect what actually aired — the Ofcom review stresses that access-service information after a disruption must be accurate.
7. Re-run the reconciliation report until zero rows remain `unreconciled`, then release the export hold with `POST /scheduler/export/resume` and re-emit the day's airtime/access-service records.

## Verification

Green looks like: the reconciliation report for the channel/day returns **zero** `unreconciled` `as_run_log` rows, every row is either matched to a `schedule_item` or tagged with an accepted reason code, and `GET /scheduler/asrun/report?channel=&date=` shows planned-vs-actual variance within the agreed tolerance for the full broadcast day. The re-emitted airtime and access-service exports confirm `SCH-ASR-330` is cleared.

## Rollback

Prepared **before** any change (Step 1 captured the snapshot). If reconciliation produces a worse state — wrong matches, corrupted times, or a broken export — restore immediately with `POST /scheduler/snapshots/{snapshot_id}/restore`, which reverts every `as_run_log` row for the channel/day to the pre-reconciliation state, then release the hold with `POST /scheduler/export/resume`. The day returns to its last-known-good as-run; re-open the incident and escalate rather than re-attempting hand edits.

## Owner & escalation

Owner: **MediaCo Traffic & Playout**. Escalate to the **Playout Ops on-call lead** if the mismatch spans more than one channel or day, if the as-run source cannot be confirmed (or still points at the retired dropbox path), or if the divergence traces to an unresolved DR/playout incident — consistent with the Ofcom recommendation that transmitted-output and access-service records after a disruption be reconciled accurately by trained operators following tested procedures.
