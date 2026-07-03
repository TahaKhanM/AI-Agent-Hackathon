---
id: KB-0005
title: "Rights-window conflict between platforms — exclusivity breach check"
service: rights
error_codes: [RGT-EXCL-009]
target_object_type: vod_item
adapted_from: "https://www.ofcom.org.uk/siteassets/resources/documents/tv-radio-and-on-demand/reviews-and-investigations/broadcast-incidents/incident-review-red-bee-media.pdf"
adapted_from_note: "exclusivity breach cross-check adapted from as-run reconciliation duties (Ofcom Red Bee); cross-catalog title collision mirrors the public MGM/Starz case"
source_licence: "public regulator report"
acl: rights-ops-only
stale: false
owner: "MediaCo Rights Ops"
last_reviewed: 2026-05-11
---

# Rights-window conflict between platforms — exclusivity breach check

## Symptoms

- `RGT-EXCL-009` raised by the rights guard when a `vod_item` is due to go live (or is already live) on one platform catalogue while an **exclusive** licence window for the same underlying title is active on a second platform.
- The Rights catalogue browser shows two active `vod_item` rows for the same `title_id`/`edition_id` with overlapping `window_start`/`window_end` and at least one `exclusivity=exclusive`.
- A distributor or platform partner reports the title appearing where their contract says it should not — the cross-catalog collision pattern seen publicly in the MGM/Starz dispute, where overlapping windows put the same titles on two services at once.

## Preconditions

- You hold **Rights Ops** entitlement (this runbook is `rights-ops-only`; window and exclusivity fields are commercially sensitive).
- The offending `vod_item` id, its `title_id`, and both platform catalogue ids from the `RGT-EXCL-009` payload.
- Confirmation that the collision is a genuine exclusivity breach, not two non-exclusive co-exclusive windows that are contractually permitted to overlap.

## Steps

1. Open the `RGT-EXCL-009` incident in the Rights catalogue browser and record the `vod_item` id, `title_id`, and the two colliding platform catalogue ids.
2. **Run the exclusivity-window cross-check between the two platform catalogues** before changing anything: call `GET /rights/exclusivity/crosscheck?title_id=<id>&catalog_a=<id>&catalog_b=<id>`. This reconciles the as-planned windows on both catalogues (the as-run reconciliation duty adapted from the source) and returns which window is exclusive, the overlap span, and the licence contract id backing each.
3. Confirm which platform holds the **exclusive** window and which holds the conflicting non-exclusive (or later) window. If both claim exclusive, do NOT proceed — go to Owner & escalation.
4. In the Rights catalogue browser, capture the current availability state of the losing `vod_item` (status, `window_start`, `window_end`, storefront visibility) so Rollback has an exact prior snapshot. (MediaCo-specific)
5. Suppress the breaching availability on the non-exclusive catalogue only: `POST /rights/vod/{vod_item_id}/suppress` with `reason="RGT-EXCL-009"` and the contract id from the cross-check. This unpublishes the storefront tile without deleting the licence record.
6. Do NOT touch the exclusive catalogue's `vod_item` — the exclusive window is the source of truth and must remain live.

## Verification

Green = re-run `GET /rights/exclusivity/crosscheck` for the same `title_id` and it returns `conflict: none`; the Rights catalogue browser shows exactly one active availability for the title (on the exclusive catalogue), and the suppressed `vod_item` reads `status: suppressed` with the `RGT-EXCL-009` contract id attached. The storefront tile for the losing platform returns 404/unavailable on a spot check.

## Rollback

**Prepared before Step 5 executes.** Rollback restores the pre-suppression snapshot from Step 4: `POST /rights/vod/{vod_item_id}/restore` with the captured status, `window_start`, `window_end`, and storefront visibility. Because Step 5 only suppresses (never deletes) the availability, restore is a single idempotent call and the licence record is untouched. If the cross-check in Step 2 is later found to have named the wrong catalogue as exclusive, run Rollback immediately and escalate — never suppress the genuinely exclusive window.

## Owner & escalation

Owner: **MediaCo Rights Ops**. Escalate to the **Rights Ops on-call lead** if both catalogues assert an exclusive window, if the cross-check cannot resolve a backing contract id, or if the breach was already visible to viewers (a reportable partner-facing incident). Contract-interpretation disputes go to the **Content Licensing desk**; do not resolve a contested exclusivity claim by admin action.
