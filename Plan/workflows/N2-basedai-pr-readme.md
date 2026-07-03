# PACKET N2-BASEDAI — Draft the BasedAI PR README (+ Venice-only .env.example + PR description)

> **WHO OWNS THIS:** **N2**. You have repo access and a capable AI coding tool. You draft the README, the Venice-only `.env.example`, and the PR description; you commit them on your own branch/worktree.
> **WHO COMMITS TO THE PR:** **T3** owns the BasedAI fork/PR (the fork + PR itself is a human GitHub task — no token is wired). Once your drafts are on a branch, T3 merges them into the fork's team folder and pushes to the PR. Open a PR into the fork or hand T3 the branch per the team's convention — either way the words are yours, the PR mechanics are T3's.
> **WHERE THIS FITS:** In **Phase 0**, open the skeleton with T3 so the README frame exists early. Draft the full README + `.env.example` + PR description across **Phases 0–2** so they are commit-ready before the **G2 freeze**. The two bench cells fill **once T3's conformance numbers land** (before the freeze, G4). The video link and any late realism number are additive Saturday pushes — no fresh session needed for those.

---

## 0. What you are making and why it matters

The BasedAI track is entered by **PR only** (a pull request into the BasedAI hackathons repo — DoraHacks alone does not enter it). The skeleton PR opens in Phase 0 (T3's GitHub task); your job is the **content**: the README that the BasedAI judges actually read, a Venice-only `.env.example` (the track template's generic one lists ANTHROPIC/OPENAI keys — ours must not), and the PR description text. Deadline pressure is real: the track repo says "3 Jul end of day" in one place and "4 Jul before judging" in another, so content must be commit-ready before the freeze, with only additive pushes on Saturday.

Two things are disqualifiers if wrong: (1) the **open-weight models declaration** (required, verbatim, prominent); (2) any hint of a closed/proprietary model in the loop. Copy, don't compose, everywhere this packet says "verbatim".

**The ambition here (from BUILD-PLAN §5, stretch item 1):** the README is where the *complete BasedAI green-tick table* lands — all 10 published metrics measured vs threshold with T3's independent oracle, and **6/6** named adversarial attacks (not the 4/6 fallback) + derived-memory-correctness + the O(1)/O(log-n) latency-vs-size curve. This table, filled in green against a **live Jira ACL source** the purpose-built competitor can't match, is how the entry decisively wins the track. Build the table structure so every one of those rows exists and is waiting for T3's number — a full green table is the target, a partial one is the honest fallback.

## 1. Source files you work from (all in the repo — you have access)

| # | Repo path | What it gives you |
|---|---|---|
| 1 | `Idea/Idea-Development.md` | Product concept (§2: the closed loop, the ladder, A/B/C memory semantics, the open-weight registry) — the README's substance |
| 2 | `docs/evidence/README.md` | The evidence index — every claim's proof link, and which rows are still pending (⏳) |
| 3 | `CLAUDE-AVAILABLE-APIS.md` | The verified environment facts, including the pinned-models block you copy verbatim |
| 4 | The BasedAI track template (`_TEMPLATE` in the fork T3 opens) | The canonical heading order — confirm it against the live template, it wins over §2 if it has drifted |

## 2. Fixed content you must use exactly (embedded here so nothing depends on memory)

**Template headings — verbatim, in this order, nothing renamed** (confirm against the live track template):

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

**The open-weight models declaration — copy VERBATIM from `CLAUDE-AVAILABLE-APIS.md`** (reproduced here; if the file differs, the file wins):

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

**The six adversarial attacks — always named in full, verbatim:** query inference · metadata bypass · timing · collection · prompt injection · derived-memory. The ambition target is **6/6 passing** — the table names all six whether or not a run is in yet.

**Attribution discipline (locked):** credit the public track-Discord thread for the A/B/C semantics; NEVER write that the sponsor "endorsed our design". Safe sentence: "The A/B/C semantics follow the model worked out publicly in the track Discord (2 Jul); the implementation, live-Jira ACL sync, fail-closed cache, and the working product around it are ours."

**Waiting-cell tokens:** mark cells that wait on late numbers with `[[WAIT:...]]` (ASCII, greppable). Final-ready rule: a search for `[[WAIT` and for `‹` must return zero before submit.

## 3. Driving your AI tool

You have a good model — you don't need a locked script, but the README has enough hard constraints that a tight brief saves a rewrite. Point your tool at the four source files in §1 and drive it with something like the brief below. After it drafts, **you** paste the verbatim models block yourself (never let the model retype the pinned IDs — a hallucinated version string is a disqualifier). Then make the tool **verify**: grep the draft for `[[WAIT` and `‹`, confirm the eight headings appear verbatim in order, confirm the six attack names all appear, confirm "endorsed our design" does NOT appear, and confirm no number exists that isn't in a source file or a `[[WAIT]]` token.

### The README brief (drive your tool with this — adapt freely)

```
Draft a hackathon submission README for "Precedent" — an incident-resolution agent whose
permission-aware memory library is our entry to the BasedAI track ("memory that respects
permissions"). Audience: BasedAI's technical judges, skim-reading many submissions. Tone:
precise, evidence-first, zero marketing fluff. Length: it must read in under 3 minutes.

Use EXACTLY these headings, in this order, renaming only <Project Name> to Precedent:
# <Project Name> / ## What it does / ## Demo / ## How to run it / ## How it works /
## Tech & sponsor APIs used / ## What's next / ## License

Content requirements, all grounded in the source files (do not invent anything):
1. "What it does": the thesis and closed loop from Idea-Development.md section 2, compressed to
   ~6 lines, plus one line that the memory governance ships as a standalone importable library
   (precedent_memory) that the product consumes.
2. "Demo": a placeholder video link written exactly as [[WAIT:VIDEO-LINK]], plus one sentence
   each for the three demo beats (approve->fix, standing-approval repeat, permission refusal)
   and the dual-enforcement revocation moment (one Jira security-level flip makes both Jira AND
   every derived memory record go dark within seconds, two independent audit logs).
3. "How to run it": a short numbered quickstart (clone, create .env from .env.example, seed
   data, run) matching the repo's actual Makefile targets and pyproject setup — verify each
   command against the repo before committing; mark any you cannot confirm "(maintainers:
   confirm command)".
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
5. A "Benchmarks & evidence" subsection under "How it works": the FULL metric table (see §3.1
   below) — all 10 published metrics as rows, columns "measured / published threshold / pass-fail",
   the independent-oracle note, the six attacks line, and the evidence links. Fill "measured"
   with the [[WAIT]] tokens named in §3.1 until the numbers land.
6. "Tech & sponsor APIs used": FIRST a subsection titled "Open-weight models (required
   declaration)" — output the marker line <<PASTE-MODELS-BLOCK-HERE>> (I paste the exact block
   myself) followed by the two locked sentences from §2, then the rest of the stack (Venice API
   base URL, SQLite, Jira Service Management as live ACL source, uAgents/Agentverse for the agent
   rails) in one short list. Include this portability line: "the pipeline runs against any
   OpenAI-compatible open-weight endpoint; an Ollama-local profile (qwen3:8b + bge-m3) is the
   offline fallback."
7. "What's next": 3 bullets max, durable-artifact framing (standalone library, conformance bench,
   hosted Watcher stays running) — no grand roadmap.
8. "License": "Code: MIT (maintainers: confirm). Data: per-source licences — see the Data
   provenance section of the main repo README (UCI CC BY 4.0, TVmaze CC BY-SA, Kaggle CC0)."

Honesty rules: every number must come from a source file or be a [[WAIT:...]] token; the
C-flow is "designed + stubbed"; the 94.4% / 18.2h numbers from the evidence index MAY be quoted
(they are measured) with their exact framing including the word "calendar" for the 18.2h.
```

After it responds: replace `<<PASTE-MODELS-BLOCK-HERE>>` with the verbatim models block from §2 yourself (copy from `CLAUDE-AVAILABLE-APIS.md` — do not let the model retype it).

### 3.1 The full metric table (the green-table ambition — build ALL of it)

This is stretch item 1 from BUILD-PLAN §5: hand the sponsor **their own rubric, filled in green**. Build every row now; each cell that waits on a number carries a `[[WAIT]]` token until T3's conformance run lands. Do not drop rows to the 4-metric fallback pre-emptively — the target is the complete table.

Columns: **measured · published threshold · pass/fail**. Rows (all 10 published metrics):

| Metric | Waiting token |
|---|---|
| FNR (false-negative / leak rate) | `[[WAIT:BENCH-SYNTH]]` |
| FPR (false-positive rate) | `[[WAIT:BENCH-SYNTH]]` |
| P50 latency | `[[WAIT:BENCH-SYNTH]]` |
| P99 latency | `[[WAIT:BENCH-SYNTH]]` |
| End-to-end overhead | `[[WAIT:BENCH-SYNTH]]` |
| Derived-memory correctness (>99% target) | `[[WAIT:BENCH-SYNTH]]` |
| ACL drift | `[[WAIT:BENCH-SYNTH]]` |
| Time-to-consistency | `[[WAIT:BENCH-SYNTH]]` |
| Audit coverage | `[[WAIT:BENCH-SYNTH]]` |
| P99 over the **25k-record real-incident (UCI) store** | `[[WAIT:BENCH-UCI]]` |

Plus, in the same subsection:
- The **latency-vs-size curve** (O(1)/O(log-n)) as a one-line claim with `[[WAIT:BENCH-CURVE]]` for the figure/number, if T3 produces it.
- **State the oracle-independence explicitly:** expected labels come from an independent naive-conjunction oracle, NOT the compiler being measured — so FNR isn't self-graded.
- A single line naming **all six** adversarial attacks verbatim (query inference, metadata bypass, timing, collection, prompt injection, derived-memory) with the count `[[WAIT:ATTACKS]]` of 6 and a pointer to `tests/test_adversarial.py`.
- A links line to the evidence index (`docs/evidence/README.md`) and the committed Venice `/models` dumps (`docs/compliance/`).

### 3.2 The .env.example + PR description brief

Drive your tool (source: `CLAUDE-AVAILABLE-APIS.md`) with something like:

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
   the two issue-security level comments from the source file if useful. Add a one-line header
   comment: "Open-weight only — see README 'Open-weight models (required declaration)'."
   Mark anything you are unsure about with "(maintainers: confirm variable name)".
   (Cross-check against the repo's own root .env.example, which is already Venice-only — keep them
   consistent.)

2. A PR description (the text box of the pull request itself), under 200 words:
   - one-paragraph summary of the entry (permission-aware memory library + working product);
   - a "Submission timeline" note: "Skeleton opened in Phase 0; synthetic bench + attack results
     committed before the code freeze; UCI realism run and demo-video link pushed Saturday morning
     with a PR comment.";
   - a line: "Deadline note: the repo README says 3 Jul EOD, the track brief says 4 Jul before
     judging — we asked a track mentor which governs and will record the answer here: [[WAIT:
     MENTOR-ANSWER]]";
   - a checklist: open-weight declaration in README, /models dumps committed, no secrets, only
     our team folder touched.
```

## 4. Filling the bench cells (once T3's numbers land)

T3 runs the conformance bench + independent oracle + full adversarial suite (BUILD-PLAN §4, T3 item 3) against merged main **before the freeze**, and produces a results block in roughly the shape below. When it lands, rewrite ONLY the table with real values — keep the three columns, mark any metric the block does not contain as "not yet measured — realism run lands Saturday" (never an empty cell, never a bracket). The `[[WAIT:BENCH-UCI]]` row stays until the Saturday realism run.

Because you both have the repo, this is a quick edit on your branch, not a relay — take T3's committed `RESULTS.md` (or block) directly and update the table. If the synthetic run slips past the freeze, apply the pre-ratified degraded rule: the table ships with threshold rows and the note "synthetic run committed by PR comment" — a late number is additive, a broken table is not.

**Results-block shape (what T3's bench emits / what you read from `RESULTS.md`):**

```
synthetic conformance run
FNR_pct = (deny-expected queries = N, leaks = N)
FPR_pct =
P50_ms =
P99_ms =
end_to_end_overhead_ms =
derived_memory_correctness_pct =
acl_drift_pct =
time_to_consistency_s =
audit_coverage = (pass/fail from tests/test_audit_coverage.py)
latency_vs_size = (curve fit / points, if produced)
attacks_passing = N of 6 (list any declared non-claims)
```

### The cells that wait, and who fills them

| Cell | Token | Arrives | Who fills |
|---|---|---|---|
| Benchmarks table, synthetic-protocol rows (FNR/FPR/P50/P99/overhead/derived-correctness/drift/TTC/audit) | `[[WAIT:BENCH-SYNTH]]` | Before the freeze, from T3's conformance run | **N2** — edit the table on your branch, committed pre-freeze |
| Latency-vs-size curve | `[[WAIT:BENCH-CURVE]]` | With the conformance run, if T3 produces it | **N2** — same edit; if absent, delete the line |
| Six-attacks pass count | `[[WAIT:ATTACKS]]` | With the conformance run | **N2** — "N of 6", list any declared non-claims |
| "P99 over the 25k-record UCI store" row | `[[WAIT:BENCH-UCI]]` | Saturday morning realism run | **T3 directly** (paste value + PR comment) — no N2 session needed |
| Demo video link | `[[WAIT:VIDEO-LINK]]` | Saturday, once the video is assembled | **T3 or N2** pastes before G6 |
| Mentor deadline answer | `[[WAIT:MENTOR-ANSWER]]` | Whenever the mentor replies | **T3** — if never, replace with "no answer received; we satisfied the earlier reading" |

## 5. What DONE looks like

- [ ] README uses the eight template headings verbatim, in order.
- [ ] Models declaration block byte-identical to `CLAUDE-AVAILABLE-APIS.md`, in its own prominent subsection, with the two locked sentences.
- [ ] The **full 10-metric table** exists (all rows present) with the measured/threshold/pass-fail columns; oracle-independence stated; the latency-vs-size curve line present.
- [ ] Six attacks named in full; A/B/C named explicitly; fail-closed stated; C-flow marked "designed + stubbed".
- [ ] Discord credit line present; the words "endorsed our design" absent.
- [ ] 94.4% / 18.2h quoted with the word "calendar"; no other number outside the source files or a `[[WAIT]]` token.
- [ ] `.env.example` has zero ANTHROPIC/OPENAI variables and zero secret values; consistent with the repo root `.env.example`.
- [ ] README + `.env.example` + PR description on your branch and handed to / merged by T3 before the **G2 freeze**; bench-cell edit committed before the freeze once T3's numbers land.
- [ ] Final-ready check (with T3, at G4): `[[WAIT` and `‹` both grep to zero in the team folder.

## 6. Fallbacks

- If your model rate-limits mid-draft, switch to your alternate tool — every requirement here is spec'd well enough that any capable model can run it. Nothing is blocked on a single seat.
- If the draft drifts into invented numbers or roadmap fluff, tell your tool: "Strip every claim not grounded in the source files; replace with `[[WAIT]]` tokens or delete." Honesty outranks completeness — a shorter true README beats a longer embellished one, and the track judges reward the visible evidence discipline.
- If the conformance run slips past the freeze, the table ships with threshold rows only + "synthetic run committed by PR comment"; T3 pushes the numbers as an additive PR comment. Never a broken table.
