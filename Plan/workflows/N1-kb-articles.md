# PACKET N1-KB — Write the 10 MediaCo KB runbook articles (adapted from real published procedures)

> WHO RUNS THIS: **N1** — non-technical teammate, working on **claude.ai FREE tier**, no repo access. Everything you need is in this file plus the attachments T3 sends.
> WHO BUNDLES AND SENDS: **T3** emails N1 the data-plan file plus the source extracts (§1; T3 preps the extracts 09:15–09:45 Friday).
> WHO RECEIVES OUTPUT AND COMMITS: N1 emails each finished batch to **T3** as `.md` files (or pasted text); T3 commits to `data/kb/KB-00NN-<slug>.md` (T3 confirms the exact loader path with T2 before committing).
> WHERE THIS FITS IN N1's DAY: Friday **10:00–14:00**. This is N1's FIRST job — the articles are demo-critical (incident 1 retrieves article #1; incident 3 refuses on articles #4/#5). **Batch 1 (articles 1, 4, 5, 6) must reach T3 by 12:30**, ahead of the 13:00 G1 checkpoint. Batch 2 (the rest) by 16:00.

---

## 0. What you are making and why it matters

MediaCo's knowledge base is ~10 runbooks. The locked rule (Conduct judge's #1 finding): **no article invented from whole cloth** — every article is adapted clause-by-clause from a named public source, carries an `adapted_from:` URL in its front-matter, and follows the real runbook shape. When the demo retrieves article #6, a real CrowdStrike URL is visible on stage. Two articles are ACL-restricted (the refusal demo), two are deliberately stale (the agent flags staleness).

## 1. What T3 sends you (Friday by 10:00, one email)

| # | Attachment | Used in conversations |
|---|---|---|
| 1 | `Idea/refinement/01-realistic-data-plan.md` (the data plan — its §4 is the article table and source list) | all |
| 2 | `src-cf291.txt` — T3 copies the remediation steps from CrowdStrike's public Channel File 291 bulletin (crowdstrike.com "Falcon update for Windows hosts — technical details") + the intro of the falcon-windows-host-recovery GitHub README | K3 |
| 3 | `src-infomir.txt` — T3 copies the body of the Infomir "EPG shift / time zones and DST" fix page | K1 |
| 4 | `src-ofcom-redbee.txt` — T3 copies the remediation/escalation-duties portion (2–3 pages) of Ofcom's Red Bee Media incident review PDF | K2, K4 |
| 5 | `src-gitlab-runbook.txt` — T3 copies ONE real GitLab runbook page (any sidekiq/job-queue one) as a structure exemplar | K3, K4 |

Free-tier rule: **max 3 attachments per conversation** — each conversation below names exactly which 2–3 of these to attach. If an extract did not arrive in time, use the fallback in §6.

## 2. The normative article format (this section IS the spec — T2's loader will parse it)

Every article is one markdown file. YAML front-matter, exactly these fields:

```yaml
---
id: KB-0001                     # KB-0001 ... KB-0010, matching the table below
title: "EPG publish failure — missing or invalid episode metadata"
service: publisher              # one of: scheduler | rights | publisher | endpoint | auth
error_codes: [PUB-4012]         # see the code rules below
adapted_from: "https://..."     # the REAL public source URL — never omit, never invent
adapted_from_note: "structure and steps adapted clause-by-clause from the source above"
source_licence: "MIT"           # licence of the source doc (MIT / Apache / public bulletin / public regulator report)
acl: public                     # public | rights-ops-only   (rights-ops-only for #4 and #5 ONLY)
stale: false                    # true for #8 and #9 ONLY
owner: "MediaCo Scheduling Ops"
last_reviewed: 2026-05-14       # stale articles: a date at least 2 years old (e.g. 2023-11-08)
---
```

Body sections, in exactly this order, H2 headings: `## Symptoms` / `## Preconditions` / `## Steps` / `## Verification` / `## Rollback` / `## Owner & escalation`. Title as the H1 above them. Length 400–700 words per article — a real runbook, not an essay.

**Error-code rules (hard):**
- Article #1 MUST use `PUB-4012` (the demo's incident 1/2 class: `publisher | PUB-4012 | schedule_item`), and its Symptoms section must plausibly cover a messy ticket like "guide showing blank on skyq / publish failing for the 9pm slot".
- Article #5 MUST use `RGT-EXCL-009` (the demo's incident 3 class: `rights | RGT-EXCL-009 | licence_window`).
- All other codes: propose in the same style (`SCH-`, `PUB-`, `RGT-`, `EPT-`, `AUTH-` prefix + number) and FLAG them — T2 reconciles every non-locked code with the sim's error dictionary before seeding. Note for T2: the data plan flags #4 as "demo incident 3" but the demo script's fingerprint (`RGT-EXCL-009`, exclusivity conflict) matches #5's subject — both are rights-ops-restricted so the refusal works either way; T2 decides which article incident 3's retrieval hits.

**Stale-article rules (#8, #9):** `stale: true`, `last_reviewed` at least 2 years old, and the body must reference a decommissioned thing — #8: a retired backup delivery path for subtitle files; #9: an old file-drop directory that no longer exists. That is what the agent visibly flags.

## 3. The 10 articles (from the data plan §4 — id, source, flags)

| id | Article | Grounded in (adapted_from target) | service | acl / stale | Conversation |
|---|---|---|---|---|---|
| KB-0001 | EPG publish failure — missing/invalid episode metadata | Real TVmaze null-field defects; XMLTV validation practice (data plan §1/§3 context) | publisher | public | K1 |
| KB-0002 | EPG timezone/DST shift — listings off by one hour | Infomir EPG-shift procedure (src-infomir.txt) | scheduler | public | K1 |
| KB-0003 | Schedule slot overlap after late change | Broadcast overrun/cascade practice (src-ofcom-redbee.txt) + GitLab runbook structure | scheduler | public | K4 |
| KB-0004 | VOD item published outside rights window — takedown + republish | MGM/Starz failure mode; as-run reconciliation duties (src-ofcom-redbee.txt) | rights | **rights-ops-only** | K2 |
| KB-0005 | Rights-window conflict between platforms (exclusivity breach check) | Same; cross-catalog title collision | rights | **rights-ops-only** | K2 |
| KB-0006 | Endpoint agent bad content update — boot-loop remediation | CrowdStrike CF-291, near-verbatim (src-cf291.txt) | endpoint | public | K3 |
| KB-0007 | Publish pipeline job stuck/failed — requeue with verification | GitLab runbooks, sidekiq/job-queue patterns (src-gitlab-runbook.txt) | publisher | public | K3 |
| KB-0008 | Subtitle/access-service file missing on publish | Red Bee/Channel 4 Ofcom case (src-ofcom-redbee.txt) | publisher | **stale** | K4 |
| KB-0009 | As-run log reconciliation mismatch | BXF/as-run practice (data plan ch.04 references) | scheduler | **stale** | K5 |
| KB-0010 | Authentication/entitlement backend capacity error | Disney+ launch-day auth failure (public reporting) — escalate-class: no safe admin fix, Steps section routes to Escalate | auth | public | K5 |

`adapted_from` URLs — use these exactly (they are the data plan's own citations):
- KB-0006: `https://www.crowdstrike.com/en-us/blog/falcon-update-for-windows-hosts-technical-details/`
- KB-0002: `https://infomir.store/mismatch-in-tv-program-schedules-how-to-fix-epg-shift-time-zones-and-dst/`
- KB-0003/4/5/8: `https://www.ofcom.org.uk/siteassets/resources/documents/tv-radio-and-on-demand/reviews-and-investigations/broadcast-incidents/incident-review-red-bee-media.pdf`
- KB-0007 (and structure for others): `https://gitlab.com/gitlab-com/runbooks`
- KB-0001: `https://github.com/dp247/Freeview-EPG` (XMLTV validation target) — plus mention TVmaze null-field defects in the body
- KB-0009: the Ofcom PDF above (as-run reconciliation duties)
- KB-0010: leave `adapted_from` pointing at the Ofcom PDF's escalation-duty structure and say in `adapted_from_note` that the failure mode is the publicly reported Disney+ launch-day auth capacity incident.

## 4. Conversation plan — 2 articles per Claude conversation, 5 conversations

Run each as a **new chat**. Every conversation starts with the SAME master prompt (below), then a per-conversation line naming its two articles. After the first article arrives, reply "now article 2". If a reply cuts off, type "continue".

### The master prompt (paste first in every conversation, then the per-conversation line)

```
You are writing knowledge-base runbook articles for "MediaCo", a simulated broadcaster used in a
hackathon demo. Hard rule from our judges: NO article may be invented from whole cloth — each is
adapted clause-by-clause from a named public source I attach or describe, and honesty about that
adaptation is part of the product. I've attached our data plan (see its section 4 for the article
table) and source extract(s).

Format — follow EXACTLY (a machine parses it):
- One markdown document per article.
- YAML front-matter with exactly these fields: id, title, service, error_codes, adapted_from,
  adapted_from_note, source_licence, acl, stale, owner, last_reviewed.
- Body: H1 title, then H2 sections in this order: Symptoms / Preconditions / Steps / Verification
  / Rollback / Owner & escalation.
- 400-700 words. Steps are numbered, imperative, concrete (name the MediaCo console/API surface a
  step touches). Verification says exactly what "green" looks like. Rollback is always present and
  always executable BEFORE the fix is attempted (our agent writes rollback plans pre-execution).

Adaptation discipline:
- Where I attach a source extract: map its procedure clause-by-clause into MediaCo terms; keep a
  recognisable 1:1 step correspondence; mark any step that has no source analogue with
  "(MediaCo-specific)" at the end of the line.
- Where no extract exists: follow the structure of a real production runbook and keep steps
  generic and safe; do not fabricate quotes from the source.
- Never claim a source says something it does not.

I will give you front-matter values (id, service, error_codes, acl, stale, owner, adapted_from)
per article — use them verbatim. Write ONE article per reply. Wait for "now article 2".
```

### Per-conversation lines (paste immediately after the master prompt)

**K1** (Fri 10:00; attach: data plan + `src-infomir.txt`):
```
Article 1 of 2: id KB-0001, title "EPG publish failure — missing or invalid episode metadata",
service publisher, error_codes [PUB-4012], acl public, stale false, owner "MediaCo Scheduling Ops",
adapted_from https://github.com/dp247/Freeview-EPG , adapted_from_note "publish-validation rules
adapted from XMLTV format requirements; failure modes are real TVmaze null-field defects (missing
synopsis, missing season/episode numbers, null runtime)". Symptoms MUST cover: EPG guide showing
blank for a scheduled slot on a TV platform, publish rejected with error PUB-4012, ticket text may
arrive garbled or with a wrong error code.
Article 2 of 2: id KB-0002, title "EPG timezone/DST shift — listings off by one hour", service
scheduler, propose an error code in SCH- style and flag it for reconciliation, acl public, stale
false, owner "MediaCo Scheduling Ops", adapted_from the Infomir URL in the data plan, adapting the
attached Infomir extract clause-by-clause.
```

**K2** (Fri 10:45; attach: data plan + `src-ofcom-redbee.txt`):
```
Both articles in this conversation are ACL-RESTRICTED: acl rights-ops-only, owner "MediaCo Rights
Ops". They will be mirrored as restricted Jira issues — write them normally; the restriction lives
in the front-matter.
Article 1 of 2: id KB-0004, title "VOD item published outside rights window — takedown and
republish", service rights, propose an RGT- error code and flag it, adapted_from the Ofcom Red Bee
review PDF URL in the data plan; adapt the escalation/reconciliation duties from the attached
extract; the failure mode mirrors the public MGM/Starz exclusivity-window case (244 titles
improperly licensed) — reference it in Symptoms as industry context, no invented details.
Article 2 of 2: id KB-0005, title "Rights-window conflict between platforms (exclusivity breach
check)", service rights, error_codes [RGT-EXCL-009] — this exact code is locked, the demo's
incident 3 fingerprints on it. Same adapted_from and adaptation source. Steps must include an
exclusivity-window cross-check between two platform catalogs before any schedule change.
```

**K3** (Fri 11:30; attach: data plan + `src-cf291.txt` + `src-gitlab-runbook.txt`):
```
Article 1 of 2: id KB-0006, title "Endpoint agent bad content update — boot-loop remediation",
service endpoint, propose an EPT- code and flag it, acl public, stale false, owner "MediaCo
Endpoint/IT Ops", adapted_from https://www.crowdstrike.com/en-us/blog/falcon-update-for-windows-hosts-technical-details/ .
Adapt the attached CF-291 remediation NEAR-VERBATIM (boot to safe mode, delete the bad channel
file C-00000291*.sys, reboot) into MediaCo endpoint terms — this is the article our pitch's cold
open refers to, so the correspondence should be obvious.
Article 2 of 2: id KB-0007, title "Publish pipeline job stuck/failed — requeue with verification",
service publisher, propose a PUB- code and flag it, acl public, owner "MediaCo Scheduling Ops",
adapted_from https://gitlab.com/gitlab-com/runbooks , adapting the attached GitLab runbook's
job-queue requeue pattern (check queue depth, identify stuck job, safe requeue, verify drain).
```

**K4** (Fri 12:30; attach: data plan + `src-ofcom-redbee.txt` + `src-gitlab-runbook.txt`):
```
Article 1 of 2: id KB-0003, title "Schedule slot overlap after late change", service scheduler,
propose an SCH- code and flag it, acl public, stale false, owner "MediaCo Scheduling Ops",
adapted_from the Ofcom Red Bee PDF URL; adapt the overrun/late-change cascade handling from the
attached extract, using the attached GitLab runbook only as a structure exemplar.
Article 2 of 2: id KB-0008, title "Subtitle/access-service file missing on publish", service
publisher, propose a PUB- code and flag it, acl public, STALE: stale true, last_reviewed
2023-11-08, owner "MediaCo Access Services", adapted_from the same Ofcom PDF (the Red Bee /
Channel 4 access-services case). The body MUST reference a decommissioned backup delivery path as
if it still existed — that staleness is deliberate; our agent flags it.
```

**K5** (Fri 13:15; attach: data plan only):
```
Article 1 of 2: id KB-0009, title "As-run log reconciliation mismatch", service scheduler, propose
an SCH- code and flag it, acl public, STALE: stale true, last_reviewed 2022-09-20, owner "MediaCo
Traffic & Playout", adapted_from the Ofcom Red Bee PDF URL (as-run reconciliation duties described
in the data plan). The body MUST reference an old file-drop directory that no longer exists —
deliberate staleness. No extract attached: follow real runbook structure, keep steps generic-safe.
Article 2 of 2: id KB-0010, title "Authentication/entitlement backend capacity error", service
auth, propose an AUTH- code and flag it, acl public, stale false, owner "MediaCo Platform
Engineering", adapted_from the Ofcom PDF's escalation-duty structure with adapted_from_note naming
the publicly reported Disney+ launch-day auth capacity incident as the failure mode. This is an
ESCALATE-CLASS article: the Steps section must conclude that there is NO safe admin fix and route
to human escalation with a diagnostic checklist — it demonstrates the autonomy ladder's floor.
```

## 5. Hand-back and what DONE looks like

- Save each article as `KB-00NN-short-slug.md` (paste Claude's output into a plain-text editor; keep the front-matter untouched).
- **Batch 1 = KB-0001, 0004, 0005, 0006** (the demo-critical set) — email to T3 by **12:30 Friday**, WhatsApp "KB BATCH 1 SENT". These four are exactly the articles the cut-rule protects.
- **Batch 2 = the other six** — email to T3 by **16:00 Friday**.
- DONE checklist per article: front-matter parses (T3 spot-checks), all 11 fields present, body sections in order, 400–700 words, `adapted_from` URL is one of §3's real URLs, locked codes correct (PUB-4012 in KB-0001, RGT-EXCL-009 in KB-0005), proposed codes flagged for T2, stale articles carry the decommissioned reference, no team-member real names anywhere.
- T3 commits to `data/kb/`, then tells T2 the proposed error codes for dictionary reconciliation.

## 6. Fallbacks (honesty beats completeness — the Conduct rubric wins every conflict)

- **Source extract missing**: write the article anyway using the master prompt's no-extract discipline, keep the real `adapted_from` URL, and set `adapted_from_note: "adapted from the cited source's published structure; source extract unavailable at build time — flagged for T2 review"`. Tell T3. Never let a missing extract push you into inventing source quotes.
- **Squeezed for time** (the data plan's own cut rule): reduce 10 → 7, keeping **KB-0001, 0004, 0005, 0006 and one stale article (KB-0008)**; drop 0003, 0009, 0010 first. Announce the cut to T3 — do not silently under-deliver.
- **Free-tier cap hit**: WhatsApp T3 with the conversation letter you reached; T3 reroutes the remaining conversations to another seat. The prompts run verbatim for anyone.
