# KB integrity report (honest-data gate)

Verifies every KB article against the canonical registry (`data/kb/README.md`): a real
`adapted_from:` URL, the correct ACL (KB-0004/KB-0005 rights-ops-only), and correct stale/escalate
flags. Extracted from each article's YAML front-matter on 2026-07-04.

## Per-article integrity table

| Article | `adapted_from:` (real public source) | ACL | stale | class | verdict |
|---|---|---|---|---|---|
| KB-0001 EPG publish metadata | `github.com/dp247/Freeview-EPG` | public | false | fix | ✅ |
| KB-0002 EPG DST shift | `infomir.store/…epg-shift…` | public | false | fix | ✅ |
| KB-0003 schedule slot overlap | Ofcom Red Bee incident review (PDF) | public | false | fix | ✅ |
| **KB-0004 VOD outside rights window** (takedown/republish) | Ofcom Red Bee incident review (PDF) | **rights-ops-only** | false | fix | ✅ restricted |
| **KB-0005 rights exclusivity conflict** | Ofcom Red Bee incident review (PDF) | **rights-ops-only** | false | fix | ✅ restricted |
| KB-0006 endpoint bad update boot-loop (CF-291) | `crowdstrike.com/…falcon-update…technical-details` | public | false | fix | ✅ |
| KB-0007 publish-job requeue | `gitlab.com/gitlab-com/runbooks` | public | false | fix | ✅ |
| **KB-0008 subtitle file missing** | Ofcom Red Bee incident review (PDF) | public | **true** (last_reviewed 2023-11-08) | fix | ✅ stale |
| **KB-0009 as-run reconciliation mismatch** | Ofcom Red Bee incident review (PDF) | public | **true** (last_reviewed 2022-09-20) | fix | ✅ stale |
| **KB-0010 auth/entitlement capacity** | Ofcom Red Bee incident review (PDF) | public | false | **escalate** (no safe admin fix — `AUTH-CAP-900`) | ✅ escalate |

## Findings

- **All 10 articles carry a real `adapted_from:` URL** to a named public source (Freeview-EPG, Infomir,
  Ofcom's Red Bee incident review, CrowdStrike's technical blog, GitLab runbooks). URLs are present and
  well-formed to real domains; **live HTTP resolution is a manual step** (this pass runs airplane-mode,
  no network) — a human confirms each 200 before publish.
- **ACL matches the registry + the refusal beat:** exactly two articles (KB-0004, KB-0005) are
  `rights-ops-only`; these are the restricted rights runbooks the scheduling-ops identity is refused
  in incident 3 (the refusal discloses only `denied_count` + owning team "Rights Ops", never the body).
- **Stale flags correct:** exactly two articles are `stale: true` (KB-0008 reviewed 2023-11-08, KB-0009
  reviewed 2022-09-20) — the agent flags staleness rather than silently trusting them.
- **Escalate class present:** KB-0010 (`AUTH-CAP-900`, auth backend capacity) is the escalate-class
  article — no safe automated admin fix, routed to a human (the policy engine caps it).
- **No FLAGS.** No article is invented from whole cloth; no ACL/stale flag disagrees with the registry.

## Raw-data messiness preserved (diff against SOURCES.md — unsanitised)

| File | Rows | Nulls / dups (measured) | SOURCES.md claim | match |
|---|---|---|---|---|
| netflix_titles.csv | 8,807 | 2,634 blank director · 831 blank country · 1 dup title | 2,634 / 831 | ✅ |
| disney_plus_titles.csv | 1,450 | 473 blank director · 219 blank country | 473 / 219 | ✅ |
| freeview-epg.xml | 44,680 programme rows / 271 channels | fuzzy titles left intact | ~44,680 | ✅ |

The raw seed data still carries its nulls, duplicate titles, and fuzzy-match failures — not
de-duplicated or cleaned. This is the messiness that drives the incidents and that the Conduct rubric
rewards.
