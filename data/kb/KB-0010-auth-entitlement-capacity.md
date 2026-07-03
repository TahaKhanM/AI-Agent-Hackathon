---
id: KB-0010
title: "Authentication / entitlement backend capacity error"
service: auth
error_codes: [AUTH-CAP-900]
target_object_type: auth_service
adapted_from: "https://www.ofcom.org.uk/siteassets/resources/documents/tv-radio-and-on-demand/reviews-and-investigations/broadcast-incidents/incident-review-red-bee-media.pdf"
adapted_from_note: "escalation-duty structure adapted from the Ofcom review; the failure mode is the publicly reported Disney+ launch-day authentication/entitlement capacity incident"
source_licence: "public regulator report"
acl: public
stale: false
owner: "MediaCo Platform Engineering"
last_reviewed: 2026-05-13
---

# Authentication / entitlement backend capacity error

## Symptoms
- Viewers cannot sign in or resume playback: the service returns `AUTH-CAP-900` ("backend at capacity") on token issuance and entitlement checks, while unauthenticated pages still load.
- The failure is **load-driven**, not content-driven: onset correlates with a demand spike (a launch, a live event, a marketing push), matching the publicly reported Disney+ launch-day authentication/entitlement capacity incident, where sign-in demand exceeded provisioned capacity.
- The MediaCo Auth console shows the `auth_service` at or above its concurrency ceiling, with a rising 5xx/timeout rate on `POST /auth/token` and `GET /auth/entitlements`.
- The originating ticket is often vague ("nobody can log in"); confirm `AUTH-CAP-900` and the saturation metric before acting.

## Preconditions
- You can read the `auth_service`, its concurrency ceiling, and live request/error rates in the MediaCo Auth console.
- You have read access to the auth gateway logs to confirm `AUTH-CAP-900` and rule out a bad deploy, expired signing key, or dependency outage as the true root cause.
- The MediaCo Platform Engineering on-call rota and incident bridge are reachable (MediaCo-specific).

## Steps
This is an **escalate-class** article: there is **no safe admin fix**. Capacity cannot be safely raised by an unattended admin change — capacity moves touch signing, session, and entitlement integrity — so the agent's job is to **triage, snapshot, and hand to a human**.

1. In the **MediaCo Auth console**, open the affected `auth_service` and confirm `AUTH-CAP-900` with concurrency at or above the ceiling.
2. Rule out a non-capacity cause via **GET /auth/health**: confirm the signing key is valid, the identity and entitlement stores are reachable, and no auth deploy landed in the incident window. If any is the real fault, **stop — this runbook does not apply**; route to that KB.
3. Capture the diagnostic snapshot (checklist below) (MediaCo-specific).
4. **Do not** raise the ceiling, restart the pool, or flush sessions from this runbook — each risks mass forced re-authentication or entitlement mis-grants under load (MediaCo-specific).
5. Invoke the escalation process: page **MediaCo Platform Engineering** on-call and open the incident bridge so all owning stakeholders join one updates channel (adapted from the Ofcom review's agreed operational escalation process, §5.15).
6. Attach the snapshot, state explicitly that no admin fix was attempted, and hand control to the responder (MediaCo-specific).

Diagnostic checklist: (a) `auth_service` id + region; (b) current vs. ceiling concurrency; (c) `AUTH-CAP-900` rate on `/auth/token` and `/auth/entitlements`; (d) `/auth/health` result; (e) onset time and correlated demand event; (f) confirmation that no capacity change was made by the agent.

## Verification
There is no admin-side "green" here — remediation is owned by the human responder. The agent's step is "green" when the incident is open on the bridge with **MediaCo Platform Engineering** engaged, the snapshot and checklist are attached, and the record explicitly states **no admin change was attempted**. Viewer-facing recovery (`AUTH-CAP-900` clearing and login success restored on the Auth console) is verified by the responder after their capacity action, not by this runbook.

## Rollback
No admin change is executed, so there is nothing to reverse — itself the safe state this runbook guarantees. Capture the rollback posture **before** escalating (our agent writes rollback plans pre-execution):
1. Record that the pre-escalation `auth_service` configuration is **unchanged**, so any responder capacity action starts from a known baseline (MediaCo-specific).
2. If a triage step is later found to have mutated state (it must not), restore the recorded baseline via the Auth console and note it on the incident.
3. Because no fix was applied, "rollback" reduces to closing the incident if `AUTH-CAP-900` clears as demand subsides — the responder's call.

## Owner & escalation
Owned by **MediaCo Platform Engineering**. This runbook always terminates in human escalation: page on-call, open the incident bridge, and hand over the snapshot and checklist. Adapted from the Ofcom review's finding that owning parties operate an agreed operational escalation process with a back-up plan should escalation fail (§5.15–5.16): if on-call does not acknowledge within the incident SLA, follow the secondary path to the Platform Engineering lead. Do not let an agent raise auth capacity, restart the pool, or flush sessions — those actions sit above the autonomy ladder floor and require a human owner.
