# PACKET N2-BASEDAI — Draft the BasedAI PR README (+ Venice-only .env.example + PR description)

> WHO RUNS THIS: **N2** — non-technical teammate, working on **claude.ai FREE tier**, no repo access. Everything you need is in this file plus the three attachments.
> WHO BUNDLES AND SENDS: **T3** emails N2 the three files in §1 by 13:30 Friday.
> WHO RECEIVES OUTPUT AND COMMITS: N2 emails the drafts to **T3**; T3 commits them into the team folder of the BasedAI fork (the skeleton PR opened at Friday stand-up — the fork/PR itself is a HUMAN task owned by T3, since no GitHub token is configured).
> WHERE THIS FITS IN N2's DAY: Friday **14:30–17:00** (draft), then a 30-minute callback when bench numbers arrive (**~19:30–20:45**, before the 21:00 freeze). Saturday morning T3 pastes in the final video link and realism numbers — that part needs no Claude session.

---

## 0. What you are making and why it matters

The BasedAI track is entered by **PR only** (a pull request into the BasedAI hackathons repo — DoraHacks alone does not enter it). The skeleton PR opens at Friday stand-up; your job is the **content**: the README that the BasedAI judges actually read, a Venice-only `.env.example` (the track template's generic one lists ANTHROPIC/OPENAI keys — ours must not), and the PR description text. Deadline pressure is real: the track repo says "3 Jul end of day" in one place and "4 Jul before judging" in another, so content must be commit-ready Friday evening, with only additive pushes Saturday.

Two things are disqualifiers if wrong: (1) the **open-weight models declaration** (required, verbatim, prominent); (2) any hint of a closed/proprietary model in the loop. Copy, don't compose, everywhere this packet says "verbatim".

## 1. What T3 sends you (Friday by 13:30 — exactly 3 attachments, the free-tier max)

| # | Repo path | What it gives you |
|---|---|---|
| 1 | `Idea/Idea-Development.md` | Product concept (§2: the closed loop, the ladder, A/B/C memory semantics, the open-weight registry) — the README's substance |
| 2 | `docs/evidence/README.md` | The evidence index — every claim's proof link, and which rows are still pending (⏳) |
| 3 | `CLAUDE-AVAILABLE-APIS.md` | The verified environment facts, including the pinned-models block you must copy verbatim |

## 2. Fixed content you must use exactly (embedded here so nothing depends on memory)

**Template headings — verbatim, in this order, nothing renamed** (fetched live from the track template):

```
# <Project Name>
## What it does
## Demo
## How to run it
## How it works
## Tech & sponsor APIs used
## What's next
## License
```

**The open-weight models declaration — copy VERBATIM from CLAUDE-AVAILABLE-APIS.md** (reproduced here; if the attachment differs, the attachment wins):

```
- Pinned models (verified):
  - FAST: `qwen3-5-35b-a3b` (Qwen/Qwen3.5-35B-A3B, Apache-2.0)
  - SMART: `deepseek-v4-flash` (deepseek-ai/DeepSeek-V4-Flash, MIT)
  - HEAVY: `deepseek-v4-pro` (deepseek-ai/DeepSeek-V4-Pro, MIT)
  - EMBED: `text-embedding-bge-m3` (BAAI/bge-m3, MIT) — embedding models only appear under `GET /models?type=embedding`
```

This block sits in its own prominent subsection **"Open-weight models (required declaration)"** at the top of "Tech & sponsor APIs used", followed by these two locked sentences:

> "No closed or proprietary model is called anywhere in the pipeline; the only file that may name a model is `precedent/models.py`, and CI greps for violations."
> "Verification evidence: Venice `/models` dumps committed to `docs/compliance/` (2026-07-03), each pinned ID carrying its public huggingface.co weights URL."

**The six adversarial attacks — always named in full, verbatim:** query inference · metadata bypass · timing · collection · prompt injection · derived-memory.

**Attribution discipline (locked):** credit the public track-Discord thread for the A/B/C semantics; NEVER write that the sponsor "endorsed our design". Safe sentence: "The A/B/C semantics follow the model worked out publicly in the track Discord (2 Jul); the implementation, live-Jira ACL sync, fail-closed cache, and the working product around it are ours."

**Waiting-cell tokens:** mark cells that wait on late numbers with `[[WAIT:...]]` (ASCII, greppable). The final-ready rule (G6, Sat 08:45): a search for `[[WAIT` and for `‹` must return zero.

## 3. Conversation plan (copy-paste verbatim)

### Conversation B1 (Fri ~14:30) — the README draft
Attach all 3 files from §1. Paste:

```
Draft a hackathon submission README for "Precedent" — an incident-resolution agent whose
permission-aware memory library is our entry to the BasedAI track ("memory that respects
permissions"). Audience: BasedAI's technical judges, skim-reading many submissions. Tone:
precise, evidence-first, zero marketing fluff. Length: it must read in under 3 minutes.

Use EXACTLY these headings, in this order, renaming only <Project Name> to Precedent:
# <Project Name> / ## What it does / ## Demo / ## How to run it / ## How it works /
## Tech & sponsor APIs used / ## What's next / ## License

Content requirements, all grounded in the three attached files (do not invent anything):
1. "What it does": the thesis and closed loop from Idea-Development.md section 2, compressed to
   ~6 lines, plus one line that the memory governance ships as a standalone importable library
   (precedent_memory) that the product consumes.
2. "Demo": a placeholder video link written exactly as [[WAIT:VIDEO-LINK]], plus one sentence
   each for the three demo beats (approve->fix, 15s standing-approval repeat, permission refusal)
   and the dual-enforcement revocation moment (one Jira security-level flip makes both Jira AND
   every derived memory record go dark within seconds, two independent audit logs).
3. "How to run it": a short numbered quickstart skeleton (clone, create .env from .env.example,
   seed data, run) with any step you cannot know marked "(maintainers: confirm command)" — my
   technical teammates will correct commands before commit.
4. "How it works": (a) the A/B/C permission semantics — A: reading a derived artifact requires
   satisfying ALL source lineage constraints (conjunction, not one strictest label); B:
   precompiled effective-policy bitmaps make the check one indexed lookup; C: redacted derivatives
   only as new governed objects with attestation and lineage (designed + stubbed — say so
   honestly). Name them "A/B/C" explicitly. (b) fail-CLOSED on stale ACLs. (c) the deterministic
   fingerprint rule: the LLM proposes, only extractor-confirmed equality counts — no LLM in any
   authorisation path. (d) live Jira as the real ACL source (roles, permission-scheme grants,
   issue-security levels; 2-3s versioned polling). (e) credit line: the A/B/C semantics follow
   the model worked out publicly in the track Discord (2 Jul); the implementation, live-Jira ACL
   sync, fail-closed cache, and the working product around it are ours. Never say the sponsor
   endorsed our design.
5. A "Benchmarks & evidence" subsection under "How it works": a table with the sponsor's own
   published metric vocabulary as rows — FNR, FPR, P50, P99, end-to-end overhead, ACL drift,
   time-to-consistency, audit coverage — with columns "measured", "published threshold",
   "pass/fail". Fill "measured" with [[WAIT:BENCH-SYNTH]] for the synthetic-protocol run and add
   one row "P99 over the 25k-record real-incident (UCI) store" filled with [[WAIT:BENCH-UCI]].
   State that expected labels come from an independent naive oracle, not the compiler being
   measured. Below the table: one line naming all six adversarial attack tests verbatim (query
   inference, metadata bypass, timing, collection, prompt injection, derived-memory) with a
   pointer to tests/test_adversarial.py, and a link line to the evidence index
   (docs/evidence/README.md) and the committed Venice /models dumps (docs/compliance/).
6. "Tech & sponsor APIs used": FIRST a subsection titled "Open-weight models (required
   declaration)" — I will paste its exact content myself, so output the marker line
   <<PASTE-MODELS-BLOCK-HERE>> followed by the two sentences I give you below, then the rest of
   the stack (Venice API base URL, SQLite, Jira Service Management as live ACL source, uAgents/
   Agentverse for the agent rails) in one short list. Include this portability line: "the
   pipeline runs against any OpenAI-compatible open-weight endpoint; an Ollama-local profile
   (qwen3:8b + bge-m3) is the offline fallback."
   The two sentences: "No closed or proprietary model is called anywhere in the pipeline; the
   only file that may name a model is precedent/models.py, and CI greps for violations." and
   "Verification evidence: Venice /models dumps committed to docs/compliance/ (2026-07-03), each
   pinned ID carrying its public huggingface.co weights URL."
7. "What's next": 3 bullets max, durable-artifact framing (standalone library, conformance bench,
   hosted Watcher stays running) — no grand roadmap.
8. "License": "Code: MIT (maintainers: confirm). Data: per-source licences — see the Data
   provenance section of the main repo README (UCI CC BY 4.0, TVmaze CC BY-SA, Kaggle CC0)."

Honesty rules: every number must come from the attached files or be a [[WAIT:...]] token; the
C-flow is "designed + stubbed"; the 94.4% / 18.2h numbers from the evidence index MAY be quoted
(they are measured) with their exact framing including the word "calendar" for the 18.2h.
Output the complete README in one message if you can; if it is getting long, stop at the end of
"How it works" and wait for me to say "continue".
```

After it responds: replace `<<PASTE-MODELS-BLOCK-HERE>>` with the verbatim models block from §2 yourself (copy from CLAUDE-AVAILABLE-APIS.md — do not let the model retype it).

### Conversation B2 (Fri ~16:00) — .env.example + PR description
New chat. Attach `CLAUDE-AVAILABLE-APIS.md` only. Paste:

```
Two small artifacts for the same submission. No secrets may appear anywhere — variable names and
public URLs only.

1. A Venice-only .env.example for the submission folder. It must NOT contain ANTHROPIC or OPENAI
   variables (the track forbids closed models; the track template's generic example is being
   overridden on purpose). Include, values empty unless shown:
   VENICE_API_KEY=
   VENICE_BASE_URL=https://api.venice.ai/api/v1
   VENICE_EMBED_MODEL=text-embedding-bge-m3
   PRECEDENT_MODEL_BACKEND=venice   # or "local" for the Ollama fallback
   plus Jira placeholders (JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY=MEDIA) and
   the two issue-security level comments from the attached file if useful. Add a one-line header
   comment: "Open-weight only — see README 'Open-weight models (required declaration)'."
   Mark anything you are unsure about with "(maintainers: confirm variable name)".

2. A PR description (the text box of the pull request itself), under 200 words:
   - one-paragraph summary of the entry (permission-aware memory library + working product);
   - a "Submission timeline" note: "Skeleton opened at stand-up 3 Jul; synthetic bench + attack
     results committed before the 21:00 freeze on 3 Jul; UCI realism run and demo-video link
     pushed 4 Jul morning with a PR comment.";
   - a line: "Deadline note: the repo README says 3 Jul EOD, the track brief says 4 Jul before
     judging — we asked a track mentor which governs and will record the answer here: [[WAIT:
     MENTOR-ANSWER]]";
   - a checklist: open-weight declaration in README, /models dumps committed, no secrets, only
     our team folder touched.
```

### Conversation B3 (Fri ~19:45, when T3 sends the bench block) — fill the two bench cells
T3 will email/WhatsApp a **BENCH BLOCK** as soon as the synthetic conformance run finishes (target 19:30–20:30; format below). New chat, no attachments. Paste:

```
Here is my README's "Benchmarks & evidence" table with [[WAIT:BENCH-SYNTH]] tokens, and the
measured results block my team just sent. Rewrite ONLY the table with real values, keeping the
"measured / published threshold / pass/fail" columns, marking any metric the block does not
contain as "not yet measured — realism run lands 4 Jul" (never an empty cell, never a bracket).
The [[WAIT:BENCH-UCI]] row stays as-is (it fills Saturday).

MY TABLE:
[paste the table from your B1 draft]

BENCH BLOCK FROM THE TEAM:
[paste T3's block]
```

Email the updated table to T3 by **20:45** — it must be committed before the 21:00 freeze (G4). If the bench slips past 20:45, apply the pre-ratified degraded rule: the table ships with threshold rows and the note "synthetic run committed by PR comment", and T3 commits what exists — a late number is additive, a broken table is not.

**BENCH BLOCK template (T3: copy from here):**

```
BENCH BLOCK — synthetic conformance run (from T3)
FNR_pct = (deny-expected queries = N, leaks = N)
FPR_pct =
P50_ms =
P99_ms =
end_to_end_overhead_ms =
acl_drift_pct =
time_to_consistency_s =
audit_coverage = (pass/fail from tests/test_audit_coverage.py)
attacks_passing = N of 6 (list any declared non-claims)
```

## 4. The two cells that wait for bench numbers (the explicit list)

| Cell | Token | Arrives | Who fills |
|---|---|---|---|
| Benchmarks table, synthetic-protocol row values (FNR/FPR/P50/P99/overhead/drift/TTC) | `[[WAIT:BENCH-SYNTH]]` | Fri 19:30–20:45, BENCH BLOCK from T3 | N2 via Conversation B3, committed pre-freeze |
| "P99 over the 25k-record UCI store" row | `[[WAIT:BENCH-UCI]]` | Sat morning realism run | **T3 directly** (paste value + PR comment) — no N2 session needed |

Also waiting but NOT bench numbers: `[[WAIT:VIDEO-LINK]]` (Sat ~08:30, T3 pastes — before G6 08:45) and `[[WAIT:MENTOR-ANSWER]]` in the PR description (whenever the mentor replies; if never, T3 replaces it with "no answer received; we satisfied the earlier reading").

## 5. What DONE looks like

- [ ] README uses the eight template headings verbatim, in order.
- [ ] Models declaration block byte-identical to CLAUDE-AVAILABLE-APIS.md, in its own prominent subsection, with the two locked sentences.
- [ ] Six attacks named in full; A/B/C named explicitly; fail-closed stated; oracle-independence stated; C-flow marked "designed + stubbed".
- [ ] Discord credit line present; the words "endorsed our design" absent.
- [ ] 94.4% / 18.2h quoted with the word "calendar"; no other number outside the attachments or a `[[WAIT]]` token.
- [ ] .env.example has zero ANTHROPIC/OPENAI variables and zero secret values.
- [ ] README + .env.example + PR description emailed to T3 by **17:00 Friday**; B3 table update by **20:45**.
- [ ] Final-ready check is T3's (G6): `[[WAIT` and `‹` both grep to zero in the team folder.

## 6. Fallbacks

- Free-tier cap mid-draft: WhatsApp T3 with which numbered requirement you reached; T3 reruns the remaining prompt on another seat (the prompts are owner-independent by design).
- If Conversation B1's output drifts into invented numbers or roadmap fluff, reply: "Strip every claim not grounded in the attachments; replace with [[WAIT]] tokens or delete." Honesty outranks completeness — a shorter true README beats a longer embellished one, and the track judges reward the visible evidence discipline.
