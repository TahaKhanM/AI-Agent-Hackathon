---
id: KB-0008
title: "Subtitle / access-service file missing on publish"
service: publisher
error_codes: [PUB-SUB-410]
target_object_type: subtitle_asset
adapted_from: "https://www.ofcom.org.uk/siteassets/resources/documents/tv-radio-and-on-demand/reviews-and-investigations/broadcast-incidents/incident-review-red-bee-media.pdf"
adapted_from_note: "subtitle/access-service delivery failure adapted from the Ofcom Red Bee / Channel 4 access-services case; the report's finding that access services were lost from the point a disaster-recovery facility carried the programme but not its access-service origination path is mapped into MediaCo publisher terms"
source_licence: "public regulator report"
acl: public
stale: true
owner: "MediaCo Access Services"
last_reviewed: 2023-11-08
---

# Subtitle / access-service file missing on publish

## Symptoms
- A programme publishes and plays out with vision and sound, but its **access services are absent**: no subtitles, and where applicable no audio description or signing track, on one or more platforms (Freeview, Sky, Freesat, Virgin, on-demand/catch-up).
- The Publisher job log raises **`PUB-SUB-410`** ("access-service asset missing") against the affected `subtitle_asset`; the programme's video/audio publish succeeds, so the slot is not blank — only the access layer is gone.
- Onset correlates with a **failover to a disaster-recovery (DR) playout path** for the channel: the DR path carries the programme but not the subtitle/access-service origination or insertion feed.
- On-demand and catch-up items ingested during the window are added **without** subtitling or audio description and are flagged for retrospective backfill.

## Preconditions
- You can identify the affected `subtitle_asset` id, its parent programme, channel, and transmission window from the Publisher job log.
- The channel is currently running on, or has recently failed back from, a DR playout path.
- You have write access to the access-service pipeline via the Publisher console (role: Access Services).
- A verified source access-service file (`.stl`/`.ttml` subtitle, audio-description mix, or signing asset) exists in the origination store, or can be re-requested from the access-services supplier.

## Steps
1. In the **Publisher job log**, open the failed job and confirm the error is `PUB-SUB-410`; record the exact `subtitle_asset` id, parent programme, channel, and window.
2. Query the asset's binding via **GET /publisher/subtitle_asset/{id}** and confirm whether the access-service file reference is null, points at the DR path, or points at a store the current playout path cannot read.
3. In the **Publisher console**, confirm which playout path the channel is on and whether that path is wired to the **access-services origination/insertion feed** — the DR path commonly omits it. (MediaCo-specific)
4. Retrieve the verified source access-service file from the **access-services backup NAS** (`access-svc-backup-nas:/origination/{channel}/{programme}`), the standing retained copy of every originated subtitle/AD/signing asset. (MediaCo-specific)
5. Re-point the asset at a store the live path can read and re-attach it via **PUT /publisher/subtitle_asset/{id}** with the recovered file reference.
6. Re-insert the access service into the programme via **POST /publisher/republish** for that `subtitle_asset`, channel, and window, so subtitles/AD/signing are muxed back onto the live playout path.
7. For on-demand/catch-up items published without access services during the window, queue them for retrospective backfill via **POST /publisher/access-service/backfill**. (MediaCo-specific)

## Verification
"Green" is: **POST /publisher/republish** returns HTTP 200 with no `PUB-SUB-410`; the Publisher job log shows the `subtitle_asset` as `PUBLISHED` and bound to the live (not DR) path; and a platform decode of the affected programme shows subtitles rendering (plus audio description / signing where scheduled). Confirm the on-demand copy carries the access-service track and no item remains in the backfill queue for that window.

## Rollback
Prepare this rollback **before** re-attaching or republishing anything (our agent writes the rollback plan pre-execution):
1. Before step 5, capture the current asset binding via **GET /publisher/subtitle_asset/{id}** and save the JSON as the pre-change baseline. (MediaCo-specific)
2. If republish attaches the wrong-language or mistimed track, or degrades a track that was previously correct, restore the saved binding via **PUT /publisher/subtitle_asset/{id}**.
3. Re-run **POST /publisher/republish** to return the programme to its prior state, then escalate. A programme carried with no subtitles is the safe fallback versus one carrying wrong or badly-timed subtitles.

## Owner & escalation
Owner: **MediaCo Access Services**. Escalate to the **Publisher platform on-call** if the DR playout path cannot be wired to the access-services origination feed, if the recovered file will not mux onto the live path, or if `PUB-SUB-410` persists after a verified file is re-attached. Per the Ofcom Red Bee finding, DR paths must carry the full access-service suite, not just vision and sound; if a channel is running a DR path that structurally omits access services, raise it as a service-continuity incident and drive the backfill of every affected on-demand item to completion.
