---
id: KB-0007
title: "Publish pipeline job stuck or failed — requeue with verification"
service: publisher
error_codes: [PUB-JOB-503]
target_object_type: publish_job
adapted_from: "https://gitlab.com/gitlab-com/runbooks"
adapted_from_note: "job-queue requeue-with-verification pattern adapted from GitLab public runbooks (sidekiq/job-queue style)"
source_licence: "MIT"
acl: public
stale: false
owner: "MediaCo Scheduling Ops"
last_reviewed: 2026-05-06
---

# Publish pipeline job stuck or failed — requeue with verification

## Symptoms

- A `publish_job` that was moving titles to air at a normal rate is no longer draining; downstream schedule slots stay in `pending_publish`.
- The publisher worker returns `PUB-JOB-503` (job accepted but not completing) on retry, or the job sits in `running` with no progress for longer than its expected runtime.
- The `PublishQueueNoLongerBeingProcessed` alert has fired, and the publisher queue-depth panel is climbing while the processing rate has dropped to zero.

## Preconditions

- You can reach the Publisher admin console and hold the `publisher.job.requeue` capability.
- The publisher queue metrics are actually reporting (a missing-metrics case is a different incident — confirm data is present, not just flat).
- The stuck job is genuinely idle, not mid-write to the CDN. Confirm no in-flight egress before touching it.
- You know the affected `publish_job` id and its `schedule_item` targets so the requeue is scoped, not a blanket flush.

## Steps

1. Open the Publisher admin console and read the queue-depth and processing-rate panels; record current depth and the timestamp throughput dropped.
2. `GET /publisher/jobs?state=running,failed` to enumerate live jobs. Sort by runtime to surface the longest-running job — the stuck one — and capture its `job_id`, `class`, `created_at`, and `enqueued_at`.
3. Inspect the candidate: `GET /publisher/jobs/{job_id}`. Confirm it is stalled (runtime far exceeds expected, no progress cursor movement) and note its `schedule_item` targets.
4. Write the rollback record (see Rollback) to the audit log BEFORE any mutation. (MediaCo-specific)
5. Quiesce the stuck job: `POST /publisher/jobs/{job_id}/kill` to remove it from the running set. Verify it leaves `running`.
6. Safely requeue by id: `POST /publisher/republish` with the recorded `job_id` and its scoped `schedule_item` list, `idempotency_key` set to the original `job_id`, so a duplicate submission cannot double-publish. (MediaCo-specific)
7. Watch the new job enter `running` in the console and confirm the queue-depth panel begins to fall.

## Verification

"Green" is concrete: within one poll interval (approx 60 s) the publisher processing-rate panel is non-zero again, queue depth is strictly decreasing, and `GET /publisher/jobs/{new_job_id}` reports `state=succeeded` with every requeued `schedule_item` moved out of `pending_publish` to `on_air`. No new `PUB-JOB-503` on the requeued job, and the `PublishQueueNoLongerBeingProcessed` alert has cleared.

## Rollback

Written and executable BEFORE the fix runs:

1. Capture the pre-change snapshot: the stuck job's full record, its `schedule_item` states, and the queue depth, to the audit log.
2. If the requeue double-publishes or targets the wrong slots, `POST /publisher/republish/{new_job_id}/cancel` to halt it, then `POST /publisher/jobs/restore` with the captured snapshot to return the affected `schedule_item`s to `pending_publish`. (MediaCo-specific)
3. Because step 6 pins `idempotency_key` to the original `job_id`, re-running the original job is a no-op rather than a second publish — the safe default if in doubt is to do nothing further and escalate.

## Owner & escalation

Primary owner: MediaCo Scheduling Ops. If the requeued job also fails `PUB-JOB-503`, if queue depth keeps climbing after two requeue attempts, or if the metrics are missing rather than zero, escalate to the Publisher Platform on-call — do not blanket-flush the queue. This runbook covers a single stuck or failed job; a broad queue stall with healthy workers is a separate incident.
