# Precedent — Idea Development v4 (panel-refined, 3 July 2026)

> **Precedent: every incident resolved becomes precedent.**
> v3 (locked decisions) was scored by a simulated 5-judge panel against the tracks' **published** criteria, refined by 5 specialist builders, and re-scored: Conduct 73→**79**, Fetch 68→**80**, BasedAI 58 (borderline-ineligible)→**80**, Technical 59→**80**, VC 77→**79**. Verdicts and remaining fixes: [refinement/00-panel-verdicts.md](refinement/00-panel-verdicts.md). The five build-ready specs in [refinement/](refinement/) are the authoritative detail; this document is the master summary.
>
> Clock: Demo Day sign-up closes **today, 3 July 18:00** ([form](https://forms.gle/fnUe3vL24wyJo6pD7)); DoraHacks submission **4 July 23:59**; BasedAI additionally requires a **separate PR** into [BasedAICo/hackathons](https://github.com/BasedAICo/hackathons) before Demo Day judging.

---

## 1. The thesis

> **AI SREs fix broken code. In real enterprises, the fix is almost never code — it's a documented admin change. Precedent is the agent that remembers every fix your organisation has ever applied and applies it again: risk-classified, approval-gated, audited, reversible.**

Conduct framing: **Conduct makes legacy legible; Precedent makes legacy operable.** The slow enterprise process: *incident resolution by manual lookup* — a human reads a ticket, searches the KB, follows a runbook in a legacy admin console, waits for approvals, and types resolution notes nobody will find next time. Average MTTR 8.85 business hours for what is often minutes of keystrokes once the fix is known.

**Headline stat (locked):** "$600B/yr for the Global 2000, up 50% in two years" (Splunk 2026 refresh) — delivered in the same breath as the verified **$200M/company** (Oxford Economics 2024, verified 3–0) so the pushback has nowhere to land. **Origin story (locked):** Disney+ named outright; never assert "Disney runs WHATS'ON" as vendor fact.

Why it wins (research-backed, unchanged from v3): (1) the Disney+ observation is ITIL's codified norm — >60% of ServiceNow's own support incidents were repeats with existing fixes (verified 3–0); (2) $340M+ of AI-SRE VC points at code/infra diagnosis and stops before execution in business apps; (3) the trust envelope (gates/audit/rollback) is the moat — Gartner's 40%-cancellation prediction is about *missing* risk controls; (4) the media wedge is demo-rich and Netflix-proved but unproductised; (5) the memory unit is an **executed fix with provenance**, not RAG-over-runbooks.

---

## 2. Product concept (post-panel)

### The closed loop
DETECT → TRIAGE → RETRIEVE (KB + memory, ACL-filtered) → RISK-CLASSIFY (deterministic policy engine — no LLM in the decision) → GATE → EXECUTE (typed tools) → VERIFY (auto-rollback on failure) → MEMORISE (executed-fix-with-provenance).

### Graduated approval ladder — **"Standing Approval", never "Autonomous"** (panel-mandated rename)
Conduct's rubric says verbatim "a fully autonomous agent is a non-starter" — the substance was compliant, the label wasn't. Locked wording:

| Level | Behaviour | Example |
|---|---|---|
| L0 Observe | Diagnose + link the documented fix; human does everything | New/unknown incident class |
| L1 Recommend | Prepared plan + rollback; human clicks approve | First occurrence of a known fix |
| L2 Approval-gated execute | Executes after one human approval, fully logged | Fix seen before, medium risk |
| **L3 Standing Approval** | Pre-approved standard change: a **human clicked "Promote to standing approval"** after watching the class succeed; executes on recurrence, self-verifies, auto-rollback; **Revoke button always visible** | Same fix class, N=3 clean successes, low risk — ITIL standard change |
| Escalate | Full investigation dossier routed to the right team | Code-level / novel / high-risk / permission-denied |

Stage line: *"No one approved this ticket — because the operations lead pre-approved this fix class after watching it succeed. Approval moved earlier in time; it never left the loop."*

**Incident-class key (now engineered, not hand-waved):** deterministic fingerprint `sha256(service | error_code | target_object_type)` — the LLM may propose fields, but only extractor-confirmed equality counts; failed extraction ⇒ no fast-path, degrade to L0/L1. Graduation N=3 clean successes; any verification failure or rollback **demotes the class** and requires re-promotion by a human.

### Permission-aware memory — sponsor-endorsed A/B/C semantics (BasedAI)
Implemented exactly as BasedAI's team endorsed in their own Discord exchange: **(A)** semantic rule — reading a derived artifact requires satisfying **all** source lineage constraints (conjunction, not a single "strictest label"); **(B)** implementation — precompiled effective-policy bitmaps so retrieval-layer checks are one indexed lookup (this *is* the sub-200ms P99 story, benchmarked); **(C)** deliberately redacted/declassified derivatives only as new governed objects with attestation, explicit approval, lineage + revocation still propagating. Admin-defined policy templates, safest default automatic, deterministic enforcement, fail-**closed** when ACL freshness is uncertain. Jira permission schemes are the synced source of truth (2–3s versioned idempotent polling; disjunctive Jira role grants compiled to principal grant-bits at sync time). **RESTRICT** (ACL change → deny via recompiled policy, reversible — this is the live demo moment) vs **REVOKE/DELETE** (source removal → quarantine + hard-delete of derivatives) are distinct, documented paths. Full schema: [refinement/02-architecture-refinement.md](refinement/02-architecture-refinement.md).

### Open-weight-only model registry (BasedAI eligibility — replaces v3's "any keys" line)
One enforced module pins Venice-served **open-weight** models (fast model for Watcher triage, stronger model for Librarian/Assessor, heavy model for dossiers only, bge-m3 embeddings precomputed) with a local Ollama fallback profile. **No OpenAI/Anthropic/closed models anywhere in the loop.** Caution: Venice also hosts closed models — the registry must whitelist, and the exact IDs must be **verified via GET /models + Hugging Face weights check before any pipeline code** (30 min, fallback bench listed in the architecture doc); commit the /models dump to the repo as evidence.

---

## 3. Demo & build (post-panel)

### Real data through simulated services (resolves the Conduct realistic-data violation)
The locked "full media-vertical demo" survives **only** because the *content* becomes real; the services stay ours. Licence-checked plan ([refinement/01-realistic-data-plan.md](refinement/01-realistic-data-plan.md)):
- **Scheduler/EPG**: TVmaze GB schedule (CC BY-SA, no-auth JSON) + committed Freeview-EPG XMLTV snapshot as offline backup. (TMDB/IMDb **rejected on licence grounds** — TMDB's terms prohibit AI/ML use; say why on the provenance slide.)
- **Rights DB**: real titles/regions/dates from CC0 Kaggle streaming catalogs; only window terms synthesised, by a rule stated in the README.
- **Day-one memory**: the **UCI ServiceNow incident event log — 141k events / ~25k incidents (CC BY 4.0)** — bootstraps the ladder credibly and *is* the scale artifact (retrieval + ACL-filter P99 and match-rate measured over it). Honest framing: it's IT-company data, not broadcast data — never imply otherwise.
- **KB**: ~10 articles adapted clause-by-clause from **real published runbooks** (CrowdStrike Channel File 291 remediation, GitLab runbooks, kube-prometheus runbooks, Ofcom's Red Bee review).
- **Messiness by design**: real null-metadata rows and duplicate titles trigger incidents; mutated ticket text (typos, colloquial symptoms, wrong error codes) makes triage visibly robust; the word **"unscripted"** is spoken on stage, with a standing offer for a judge to file a ticket from their phone.

### The demo (full scripts: [refinement/04-demo-and-video-script.md](refinement/04-demo-and-video-script.md))
2:42 live script (18s buffer): 25s manual-loop **before** with the persistent **Baseline Bar** (manual 8h51m vs live stopwatch bars) → incident 1 (messy ticket, approve, fix, Jira closes itself, human clicks **Promote**) → incident 2 (**15s standing-approval** run — "the second time is free") → **live recovery beat** (injected 503 → verification fails → rollback fires → class demoted) → incident 3 (rights conflict: high-risk + ACL-denied runbook → dossier + escalate — "it knows what it's not allowed to touch"). Demo-mode decision rule (§4.3 of the script): rehearsal gates at Sat 09:00 decide live-local-first vs narrated recording + one live Approve click. 4-min video gives ASI:One 80 seconds (the full loop chat-only, approval bound to sender address); 30s teaser cut for the deck.

### Build order & cut-lines (technical judge's pre-executed cuts included)
**Vertical-slice gate: by Friday 18:00, incidents 1+2+recovery run end-to-end on seeded real data with Baseline Bar and Promote/Revoke — everything else waits.** Pre-executed cuts: rights+publisher collapsed into one service; C-flow (redacted-derivative) demo cut to Q&A; temporal-embargo rule cut; third Fetch agent in-process; ROI ticker static; benchmark corpus 8k→2k. **Fetch gates are non-cuttable** (track committed — round-1 fatal contradiction resolved) and **front-loaded**: Agentverse registration + Chat Protocol echo + fresh-account ASI:One discovery test first thing, before product code; Watcher deployed as a true hosted agent so "keeps running post-hackathon" is honest. Contingency order if catastrophically behind: BasedAI extras → (never Fetch gates) → Jira degrades to cached fallback (never mock-only) → incident 3 — **never incident 2**.

### Jira (locked, with a panel-caught trap)
**JSM STANDARD 14-day trial, not Free** — the Free tier cannot edit permission schemes, which the ACL-sync story depends on. Verify within the first hour: create two project roles, read scheme membership via API, flip a role and watch the sync. Write-behind cache + replay for stage safety.

---

## 4. Pitch (deck spec: [refinement/03-pitch-deck.md](refinement/03-pitch-deck.md); Q&A bank: [refinement/05-scale-story-and-qa.md](refinement/05-scale-story-and-qa.md))

12 slides + 8 Q&A appendix slides; stage cut rehearsed to 2:40 covering slides 1–7, 11, 12 (tech/competition/moat ship in the deck but are Q&A-only). Jargon purge: agent names, YAML, ACL, P99 banned from core slides. The two takeaway lines: **"the second time is free"** and **"it knows what it's not allowed to touch."** Slide 6 carries the data-provenance strip; slide 10 carries the measured 141k-corpus numbers (run the match-rate computation **before** committing the framing); slide 12 needs the human layer (credentials, post-Saturday intent, practitioner-validation line) — **write it honestly or delete it, never fake it**. The scale story is the four-tier integration pattern (REST → BXF/file-drop → checklist-plus-verify, same gate/audit/rollback at every tier) with the MSP channel as multiplier, and RPA reframed as a pluggable executor *under* Precedent's approval-and-memory layer.

---

## 5. Submissions & track strategy (locked + panel-corrected)

| Track | Status | Panel-critical notes |
|---|---|---|
| **Conduct £8,000** | Primary | Realistic data + unscripted beat + Standing Approval rename + Baseline Bar are what moved 73→79; the remaining fatal is **scope** — hold the vertical-slice gate |
| **Fetch.ai** | Committed, gates front-loaded & non-cuttable | Agentverse ×3 mailbox agents, Chat Protocol, ASI:One shared-chat URL captured early (not at Fri 21:00 freeze); hosted Watcher for the post-hackathon bonus |
| **BasedAI** | Aligned & now genuinely eligible | **Open-weight-only** enforced by the model registry (verify Venice IDs first); A/B/C semantics + fail-closed cache + live RESTRICT demo + committed benchmark; **separate draft PR into BasedAICo/hackathons Friday night** — DoraHacks alone does not enter this track |
| Others | Skip | — |

**Deliverables:** DoraHacks (repo, deck, ~5-min video, bounty ticks: Conduct + Fetch.ai + BasedAI) ▪ Demo Day form **today 18:00** ▪ Fetch: ASI:One chat URL + Agentverse profile URLs ▪ BasedAI: PR with team folder + README (architecture, open-weight model list, video link).

## 6. Human action items the documents cannot do (no role assignments here — the team decides who)

1. Submit the Demo Day form **before 18:00 today** (do it this morning regardless of build state).
2. Verify Venice open-weight model IDs (30 min) before any pipeline code.
3. Provision the **JSM Standard** trial and run the permission-scheme API check within the first hour.
4. Run the UCI match-rate computation (~30 min) before the slide framing is committed.
5. Name a BasedAI PR owner; open the draft PR Friday night.
6. Write the three one-line team credentials + honest post-Saturday-intent sentence; do the ~2h practitioner outreach or delete the validation line.
7. Ratify the demo-mode decision rule (rehearsal gates, Sat 09:00) in writing so it isn't debated on the day.

## 7. Decision record

Locked 3 Jul (user): Precedent ▪ media-vertical demo ▪ live Jira SM ▪ Fetch committed ▪ BasedAI-aligned ▪ $600B headline ▪ Disney+ named. Panel-adopted (within unlocked space): Standing-Approval rename ▪ real-data seeding ▪ open-weight-only registry ▪ A/B/C permission semantics ▪ front-loaded Fetch gates ▪ pre-executed scope cuts ▪ JSM Standard trial ▪ demo-mode rehearsal gate. Team-role assignment deliberately excluded from this document.
