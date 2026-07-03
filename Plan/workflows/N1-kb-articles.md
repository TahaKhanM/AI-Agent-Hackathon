# PACKET N1-KB — Write the 10 MediaCo KB runbook articles (adapted from real published procedures)

> WHO RUNS THIS: **N1** — you own the data & content lane. You have repo access and a capable AI coding tool with a decent model. You write the articles **straight into the repo** and commit them yourself.
> WHERE THE FILES LAND: `data/kb/KB-00NN-<slug>.md`. Confirm the exact loader path with **T2** (whose memory package parses these) before you commit the first one; then batch the rest to the same path.
> WHERE THIS FITS: **Phase 0 → Phase 1**, and this is your FIRST job. The articles are demo-critical — incident 1 retrieves article #1; incident 3 refuses on articles #4/#5. **The critical five (KB-0001, 0004, 0005, 0006, plus one stale — 0008) must be committed early** so the retrieval demo has something real to retrieve at the first merge / Checkpoint A. The remaining five follow before the freeze (G2).

---

## 0. What you are making and why it matters

MediaCo's knowledge base is ~10 runbooks. The locked rule (Conduct judge's #1 finding): **no article invented from whole cloth** — every article is adapted clause-by-clause from a named public source, carries an `adapted_from:` URL in its front-matter, and follows the real runbook shape. When the demo retrieves article #6, a real CrowdStrike URL is visible on stage. Two articles are ACL-restricted (the refusal demo), two are deliberately stale (the agent flags staleness).

## 1. Source material you work from

The real sources you adapt from live in the data plan and on the public web. You have repo access, so read them directly:

| Source | Feeds | Where |
|---|---|---|
| `Idea/refinement/01-realistic-data-plan.md` (its §4 is the article table + source list) | all | repo |
| CrowdStrike public Channel File 291 bulletin ("Falcon update for Windows hosts — technical details") + the intro of the falcon-windows-host-recovery GitHub README | KB-0006 | web (URL in §3) |
| Infomir "EPG shift / time zones and DST" fix page | KB-0002 | web (URL in §3) |
| Ofcom Red Bee Media incident review PDF — the remediation/escalation-duties portion (2–3 pages) | KB-0003/4/5/8/9 | web (URL in §3) |
| One real GitLab runbook page (any sidekiq/job-queue one) as a structure exemplar | KB-0007, KB-0003 | web (URL in §3) |

Pull the source text yourself (WebFetch, or read the pages in a browser and paste the relevant remediation steps into your working context). You do not need anyone to send you extracts.

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
- All other codes: propose in the same style (`SCH-`, `PUB-`, `RGT-`, `EPT-`, `AUTH-` prefix + number) and FLAG them in your commit message / a note to T2 — T2 reconciles every non-locked code with the sim's error dictionary before seeding. Note for T2: the data plan flags #4 as "demo incident 3" but the demo script's fingerprint (`RGT-EXCL-009`, exclusivity conflict) matches #5's subject — both are rights-ops-restricted so the refusal works either way; T2 decides which article incident 3's retrieval hits.

**Stale-article rules (#8, #9):** `stale: true`, `last_reviewed` at least 2 years old, and the body must reference a decommissioned thing — #8: a retired backup delivery path for subtitle files; #9: an old file-drop directory that no longer exists. That is what the agent visibly flags.

## 3. The 10 articles (from the data plan §4 — id, source, flags)

| id | Article | Grounded in (adapted_from target) | service | acl / stale |
|---|---|---|---|---|
| KB-0001 | EPG publish failure — missing/invalid episode metadata | Real TVmaze null-field defects; XMLTV validation practice (data plan §1/§3 context) | publisher | public |
| KB-0002 | EPG timezone/DST shift — listings off by one hour | Infomir EPG-shift procedure | scheduler | public |
| KB-0003 | Schedule slot overlap after late change | Broadcast overrun/cascade practice (Ofcom Red Bee) + GitLab runbook structure | scheduler | public |
| KB-0004 | VOD item published outside rights window — takedown + republish | MGM/Starz failure mode; as-run reconciliation duties (Ofcom Red Bee) | rights | **rights-ops-only** |
| KB-0005 | Rights-window conflict between platforms (exclusivity breach check) | Same; cross-catalog title collision | rights | **rights-ops-only** |
| KB-0006 | Endpoint agent bad content update — boot-loop remediation | CrowdStrike CF-291, near-verbatim | endpoint | public |
| KB-0007 | Publish pipeline job stuck/failed — requeue with verification | GitLab runbooks, sidekiq/job-queue patterns | publisher | public |
| KB-0008 | Subtitle/access-service file missing on publish | Red Bee/Channel 4 Ofcom case | publisher | **stale** |
| KB-0009 | As-run log reconciliation mismatch | BXF/as-run practice (data plan ch.04 references) | scheduler | **stale** |
| KB-0010 | Authentication/entitlement backend capacity error | Disney+ launch-day auth failure (public reporting) — escalate-class: no safe admin fix, Steps routes to Escalate | auth | public |

`adapted_from` URLs — use these exactly (they are the data plan's own citations):
- KB-0006: `https://www.crowdstrike.com/en-us/blog/falcon-update-for-windows-hosts-technical-details/`
- KB-0002: `https://infomir.store/mismatch-in-tv-program-schedules-how-to-fix-epg-shift-time-zones-and-dst/`
- KB-0003/4/5/8: `https://www.ofcom.org.uk/siteassets/resources/documents/tv-radio-and-on-demand/reviews-and-investigations/broadcast-incidents/incident-review-red-bee-media.pdf`
- KB-0007 (and structure for others): `https://gitlab.com/gitlab-com/runbooks`
- KB-0001: `https://github.com/dp247/Freeview-EPG` (XMLTV validation target) — plus mention TVmaze null-field defects in the body
- KB-0009: the Ofcom PDF above (as-run reconciliation duties)
- KB-0010: leave `adapted_from` pointing at the Ofcom PDF's escalation-duty structure and say in `adapted_from_note` that the failure mode is the publicly reported Disney+ launch-day auth capacity incident.

## 4. Driving your AI tool

You have a capable model — use it, but you own the flags and the honesty. Point it at the spec and let it draft; you verify every article against §2/§3 before committing.

**What to point it at:** `Idea/refinement/01-realistic-data-plan.md` (§4 table), this file's §2 (the exact YAML shape) and §3 (per-article ids/sources/flags), and the source text you pulled for the article in hand.

**A prompt to drive it (adapt freely — you don't need to run it verbatim):**

```
You are writing knowledge-base runbook articles for "MediaCo", a simulated broadcaster used in a
hackathon demo. Hard rule from our judges: NO article may be invented from whole cloth — each is
adapted clause-by-clause from a named public source I give you, and honesty about that adaptation
is part of the product.

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
- Where I give you a source extract: map its procedure clause-by-clause into MediaCo terms; keep a
  recognisable 1:1 step correspondence; mark any step that has no source analogue with
  "(MediaCo-specific)" at the end of the line.
- Where no extract exists: follow the structure of a real production runbook and keep steps
  generic and safe; do not fabricate quotes from the source.
- Never claim a source says something it does not.

I will give you front-matter values (id, service, error_codes, acl, stale, owner, adapted_from)
per article — use them verbatim.
```

**Per-article front-matter to feed it** (verbatim values; the AI drafts body + verifies structure, you verify the flags):

- **KB-0001** — service `publisher`, `error_codes [PUB-4012]`, acl `public`, stale `false`, owner `"MediaCo Scheduling Ops"`, `adapted_from https://github.com/dp247/Freeview-EPG`, `adapted_from_note "publish-validation rules adapted from XMLTV format requirements; failure modes are real TVmaze null-field defects (missing synopsis, missing season/episode numbers, null runtime)"`. Symptoms MUST cover: EPG guide showing blank for a scheduled slot on a TV platform, publish rejected with error PUB-4012, ticket text may arrive garbled or with a wrong error code.
- **KB-0002** — service `scheduler`, propose an `SCH-` code and flag it, acl `public`, stale `false`, owner `"MediaCo Scheduling Ops"`, `adapted_from` the Infomir URL, adapting the Infomir EPG-shift page clause-by-clause.
- **KB-0003** — service `scheduler`, propose an `SCH-` code and flag it, acl `public`, stale `false`, owner `"MediaCo Scheduling Ops"`, `adapted_from` the Ofcom Red Bee PDF URL; adapt the overrun/late-change cascade handling from the PDF, using a GitLab runbook page only as a structure exemplar.
- **KB-0004** — service `rights`, propose an `RGT-` code and flag it, acl `rights-ops-only`, owner `"MediaCo Rights Ops"`, `adapted_from` the Ofcom Red Bee PDF URL; adapt the escalation/reconciliation duties; the failure mode mirrors the public MGM/Starz exclusivity-window case (244 titles improperly licensed) — reference it in Symptoms as industry context, no invented details. (This article is ACL-restricted; the restriction lives in the front-matter, write the body normally.)
- **KB-0005** — service `rights`, `error_codes [RGT-EXCL-009]` (this exact code is locked — the demo's incident 3 fingerprints on it), acl `rights-ops-only`, owner `"MediaCo Rights Ops"`, same `adapted_from` and adaptation source as KB-0004. Steps MUST include an exclusivity-window cross-check between two platform catalogs before any schedule change.
- **KB-0006** — service `endpoint`, propose an `EPT-` code and flag it, acl `public`, stale `false`, owner `"MediaCo Endpoint/IT Ops"`, `adapted_from https://www.crowdstrike.com/en-us/blog/falcon-update-for-windows-hosts-technical-details/`. Adapt the CF-291 remediation NEAR-VERBATIM (boot to safe mode, delete the bad channel file C-00000291*.sys, reboot) into MediaCo endpoint terms — this is the article our pitch's cold open refers to, so the correspondence should be obvious.
- **KB-0007** — service `publisher`, propose a `PUB-` code and flag it, acl `public`, owner `"MediaCo Scheduling Ops"`, `adapted_from https://gitlab.com/gitlab-com/runbooks`, adapting a GitLab runbook's job-queue requeue pattern (check queue depth, identify stuck job, safe requeue, verify drain).
- **KB-0008** — service `publisher`, propose a `PUB-` code and flag it, acl `public`, **stale `true`**, `last_reviewed 2023-11-08`, owner `"MediaCo Access Services"`, `adapted_from` the Ofcom PDF (Red Bee / Channel 4 access-services case). The body MUST reference a decommissioned backup subtitle-delivery path as if it still existed — that staleness is deliberate; our agent flags it.
- **KB-0009** — service `scheduler`, propose an `SCH-` code and flag it, acl `public`, **stale `true`**, `last_reviewed 2022-09-20`, owner `"MediaCo Traffic & Playout"`, `adapted_from` the Ofcom PDF (as-run reconciliation duties). The body MUST reference an old file-drop directory that no longer exists — deliberate staleness. No extract: follow real runbook structure, keep steps generic-safe.
- **KB-0010** — service `auth`, propose an `AUTH-` code and flag it, acl `public`, stale `false`, owner `"MediaCo Platform Engineering"`, `adapted_from` the Ofcom PDF's escalation-duty structure, with `adapted_from_note` naming the publicly reported Disney+ launch-day auth capacity incident as the failure mode. ESCALATE-CLASS: the Steps section must conclude that there is NO safe admin fix and route to human escalation with a diagnostic checklist — it demonstrates the autonomy ladder's floor.

## 5. Committing and what DONE looks like

- Save each article as `data/kb/KB-00NN-short-slug.md`. Confirm the loader path with T2 before the first commit.
- Work on your branch/worktree; commit as you go and merge/PR per the team's convention. The critical five are demo-critical — get them in before the first merge / Checkpoint A so the retrieval demo has real content.
- **Commit order — critical five first: KB-0001, 0004, 0005, 0006, and one stale article (KB-0008).** These are exactly the articles the cut-rule protects (incident 1 retrieves 0001; incident 3 refuses on 0004/0005; the cold open references 0006; 0008 is the staleness flag). Then commit the other five before the freeze (G2).
- In the commit message (or a short note to T2 alongside the merge), **list the proposed error codes you flagged** so T2 can reconcile them with the sim's error dictionary before seeding.
- DONE checklist per article: front-matter parses, all 11 fields present, body sections in order, 400–700 words, `adapted_from` URL is one of §3's real URLs, locked codes correct (PUB-4012 in KB-0001, RGT-EXCL-009 in KB-0005), proposed codes flagged for T2, stale articles carry the decommissioned reference, no team-member real names anywhere.

## 6. Fallbacks (honesty beats completeness — the Conduct rubric wins every conflict)

- **Source text you can't pull** (page down, PDF unreachable at build time): write the article anyway using the no-extract discipline, keep the real `adapted_from` URL, and set `adapted_from_note: "adapted from the cited source's published structure; source text unavailable at build time — flagged for T2 review"`. Tell T2. Never let a missing source push you into inventing source quotes.
- **Squeezed for time** (the data plan's own cut rule): reduce 10 → 7, keeping **KB-0001, 0004, 0005, 0006 and one stale article (KB-0008)**; drop 0003, 0009, 0010 first. Announce the cut to the team — do not silently under-deliver. The floor (§5 in BUILD-PLAN.md) never loses these five.
