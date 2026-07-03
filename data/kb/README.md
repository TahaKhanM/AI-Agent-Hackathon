# KB corpus — the runbooks Precedent retrieves

> Landing zone for the ~10 KB articles. **Commit each article as its own markdown file here** (`kb-01-epg-publish.md`, …). Owner: N1. Full spec + source list: `Plan/workflows/N1-kb-articles.md` and `Idea/refinement/01-realistic-data-plan.md` §4.

**The rule:** no article invented from whole cloth. Every article is adapted from a named public source with an `adapted_from:` URL in its front-matter, and follows the real runbook shape. Critical five first (they drive the retrieval demo): EPG-publish (#1), the two restricted rights runbooks (#4, #5 — issue-security level "Rights Ops Only"), CrowdStrike CF-291 (#6), and one stale article.

Front-matter each article must carry (see the packet for the full 11-field format):

```yaml
---
id: KB-0001
title: EPG publish failure — missing/invalid episode metadata
adapted_from: https://…            # a real published source, always
service: publisher
error_code: PUB-4012               # the locked codes: PUB-4012, RGT-EXCL-009
target_object_type: schedule_item
acl: public | rights-ops-only      # #4/#5 are rights-ops-only
stale: false | true                # 2 articles are deliberately stale
last_reviewed: 2026-…
---
```

Body sections: symptoms · preconditions · steps · verification · rollback · owner. Two articles are ACL-restricted (Rights Ops), two are stale (the agent flags staleness), one is escalate-class (no safe admin fix).
