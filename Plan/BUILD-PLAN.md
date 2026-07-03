# Precedent — BUILD PLAN (Friday 3 July → Saturday 4 July 23:59 BST)

> Written Friday 3 July 2026, ~06:15–08:00 BST (anchored with `date`). Assembled by a multi-agent pass (2 workstream planners + 5 document writers), then **adversarially red-teamed by a feasibility judge and a schedule red-team** whose fixes are folded in below (changelog at the end). The gate *order* is locked; the times are set from the 06:15 anchor and are **tight, not guaranteed** — the 18:00 vertical-slice gate has near-zero buffer, so the 13:00/17:00 checkpoints are **mandatory cut-fire points**, not advisory.
> Companion files: N1/N2 packets in [`Plan/workflows/`](workflows/) · build-independent prep drafts in [`Prep/`](../Prep/) · build-dependent prep spec in [`Plan/prep-spec.md`](prep-spec.md) · **starter code already written this session** (see §0.1).

---

## 0. ASSUMPTIONS BOX (the team corrects numbers HERE; if any change, re-run the §3 hour-math)

| Assumption | Value |
|---|---|
| Plan anchor | Fri 3 Jul 06:15 BST; team starts **09:00 Fri** |
| T1/T2/T3 availability | ~12 h Friday (net of breaks) + ~5 h Saturday outside Demo Day (06:30–~09:15 and ~17:00–19:00) |
| N1 availability | 8 h Friday (**10:00–18:00**) + 4 h Saturday. ⚠️ The Fri 19:30 table read is a **~25-min phone-in past N1's 18:00 end** — flagged; async fallback in §7 if N1 can't stay |
| N2 availability | 8 h Friday (**13:30–21:30**, late-shifted to cover the freeze/recording window) + 4 h Saturday |
| Demo Day | All five at Blackett LT1 Sat 10:00–16:30. Venue is on-campus (hack week ran in the same Blackett building) → travel ~10 min; the "~1 h" is mostly setup/buffer, so **build can run to ~09:15 Sat**, then pack + walk |
| Seats | T1+T2 = Claude Max 20× + ChatGPT Pro/Codex (to 7 Jul). **T1's Max seat ran the overnight refinement/planning sessions → part of its weekly budget is already spent.** The two biggest agentic sessions go to **T2**; T1 gets many medium sessions; heaviest blocks staggered (T2 heavy 09:30–12:30 & 16:15–19:30; T1 heavy 09:45–12:30 & 13:45–17:30) |
| T3 seat | Claude Pro (lower caps). All T3 work is bounded ≤2 h **and re-runnable or human clickwork** — nothing on the critical path dies if a Pro session caps mid-task |
| N1/N2 claude.ai plan | **FREE tier assumed.** Packets are sized to fit (≤3 small attachments/chat, separate chats, chunked, documented cap-hit escalation). **Red-team checked this and it holds.** T3 bundles+sends packets and receives+commits outputs |
| Usage ritual | 13:00 and 19:00: T1+T2 check Claude usage. **Concrete overflow (not generic):** if T2 is near cap at 13:00/19:00, T2-4 wiring + T2-3 polish move to **Codex** (non-agentic edits) and any remaining backend hands to **T1's next 5-h window using the kickoff spec in this plan**; T3 Pro is second-opinion review only |
| Generated visuals | Higgsfield MCP connected but **free plan, ~8 credits left (2/still, video unaffordable)** → optional, ≤4 stills, cannot block the video gate. Venice `/image/generate` **works** (`venice-sd35` tested live this morning). **Primary video = clean screen-recording cut** |
| GitHub | **No token configured → repo publication + BasedAI fork/PR are HUMAN tasks (owner T3)**, packet `workflows/T3-github-publication.md`. Secrets state **verified this session**: `.env` never committed, gitignored from the first commit, no secret values anywhere in history — the scrub re-confirms, it isn't discovering |

**Already DONE — do not re-plan (committed evidence):** Venice open-weight verification incl. `/models` dumps + all four pinned IDs vs public HF weights (`docs/compliance/`) — *this closed the 00-panel-verdicts "Venice ID verification" fatal.* Jira **Standard** verified: roles 10007/10008, live-scheme grant flips, issue-security scheme 10000 (levels 10000/10001) associated to MEDIA, enforcement timed **≤5 s**, auditing API live (06 §1) — *this closed the "Jira tier/role-flip verification" fatal.* UCI corpus measured incl. arrival-time precision (`data/analysis/`). ASI:One + Agentverse keys verified. All five refinement specs + prep drafts + 10 N-packets + prep-spec written.

### 0.1 Starter code written THIS session (T1/T2 begin from these, not a blank file)

The red-team's top de-risk — "pre-write the memory test skeletons and models.py tonight" — is **done and committed**:
- [`precedent/models.py`](../precedent/models.py) — the open-weight registry (4 pinned IDs + HF-URL startup guard + verified fallback bench). **Tested: the guard passes against the committed live catalog and rejects a closed model.** T1-1 shrinks to wiring, not authoring.
- [`precedent_memory/schema.sql`](../precedent_memory/schema.sql) — the full schema from 02 §2.3. **Executes cleanly against SQLite.**
- [`precedent_memory/tests/`](../precedent_memory/tests/) — 9 spec-encoding test skeletons (`test_conjunction` incl. the incident-3 multi-source counterexample, `test_fail_closed`, `test_concurrency`). **Collect green as skips.** T2-1 starts from RED tests — remove the skip marks and implement to pass.

---

## 1. Gates (order locked; times set from the 06:15 anchor; 18:00 is tight → checkpoints are mandatory)

| Gate | Time | Rule |
|---|---|---|
| **G0 stand-up** | Fri 09:00–09:30 | Confirm the Demo Day form went in (due 18:00 TODAY; if not, N2 submits at 09:00 — forms.gle/fnUe3vL24wyJo6pD7). Map names→profiles; **assign the presenter roster (§4.0)**. Ratify in writing: the checkpoint cut-rules, the demo-mode gate (04 §4.3), the selection branch, the slide-10 degraded rule, the one-shot-answer freeze. Invite 2nd Jira agent seat → `.env`. **Declare T3-5's mutation corpus + its seed the single canonical source** (one seed → one number → four surfaces) |
| **G1 checkpoint** | **Fri 13:00 (mandatory)** | `precedent_memory` + core loop integrated (M-1 merged)? **NO → fire cut-lines 1–2 (C-flow demo, temporal extras) and collapse the third Fetch agent in-process** (E1 two-agent answer + the 0.5 h "three agents" doc sweep). This is not optional — a slow morning must be paid for here, not silently at 18:00 |
| **G2 checkpoint** | Fri 17:00 | Vertical slice running headless? NO → incident 3 goes video-only; console audit view stays a JSON tail; **the LIVE Tier-A2 demo surfaces die** (they are gated on G2 green). Note: the *offline* bench harness is A1/unconditional — see §3 crosswalk |
| **G3 VERTICAL SLICE** | **Fri 18:00 (immovable)** | Incidents 1+2+recovery end-to-end on seeded real data; **Baseline Bar + Approve/Promote/Revoke clickable** (feed/trace/JSON-tail may lag to 20:00). 18:30–19:00: first full two-presenter run-through + the 100-mutation extractor bench runs (fixed slot — chip numbers must exist before the 20:00 second pass and the 21:00 recording) |
| **G4 CODE FREEZE** | Fri 21:00 | Freeze → T2 raw screen-capture 21:00–22:30 (labelled clips) + ASI:One shared-chat final capture + hosted Watcher deploy + BasedAI PR bench-numbers commit |
| **G5 selection branch** | Fri ~22:00 | N2 monitors the announcement; **T1 calls SELECTED / NOT-SELECTED** per the pre-ratified rule; both checklists armed by N2 at 21:15 (§7 branch) |
| **G6 BasedAI PR FINAL-READY** | **Sat 08:45** (before judging) | Video link pushed + UCI realism numbers as PR comment + headings verbatim + no secrets. The **video link is the single Sat-morning critical-path item** — see the §5 chain |
| **G7 rehearsal go/no-go** | Sat 08:45–09:15 | SELECTED branch: run 04 §4.3's gates mechanically; two failures flip the default to narrated-recording + one live Approve click. No debate — ratified at G0. Includes the cross-assignment Q&A drill |
| **G8 DoraHacks final** | Sat ~17:30 | Draft BUIDL submitted 08:30 (entries editable; **organizer-question answers are ONE-SHOT — frozen text pasted verbatim**); final after a logged-out link sweep. Platform hard deadline 22:59 UTC — we finish ~5 h early |

## 2. Critical path (plain sentences)

Morning unblockers (models wiring + hello Watcher; the memory package; sim + loaders; skeleton PR; agent pre-registrations) feed the **12:30 merge**, which forks into the core loop and the Jira sync; the loop's fast-path plus the console's **Baseline-Bar-and-three-buttons** are the entire 18:00 vertical slice; the 18:30 mutation bench makes the robustness chip real; the Fetch rails go live 19:00–21:00 behind pre-registered addresses; the **21:00 freeze** releases the capture session that feeds every downstream artifact (video, teaser, backup, GIF, PR video link). **The single most loaded person is T2** (memory → Jira → console → capture); **the tightest hour is Friday 17:00–18:00** — T2's console must deliver Bar+buttons in the ~45 min after the 17:00 merge, which is why 16:15–17:00 is spent on *merge-independent scaffolding* (static Bar + button shells) and only the wiring waits for the merge. Real slack lives in T2's Saturday (~3 h) and both T-Saturday evening blocks — that is the contingency pool, and it sits *after* the freeze where slip can be absorbed by the video/PR/polish lanes without touching the demo.

## 3. Hour-math (recomputed directly from the §4 task times — the red-team's figures, not rounded claims)

| Person | Friday booked / avail | Saturday booked / avail | Notes |
|---|---|---|---|
| T1 | **12.25 / 12** ⚠️ | 2.5 / 5 | +0.25 over; ~0.75 h of real gaps (18:00–18:30, 21:30–22:00) mean *effective* load ~11.5 h. 22:15 branch call is a 15-min tail |
| T2 | **12.0 / 12** | 1.75 / 5 | M-2 (17:00–17:15) nested inside the console block; capture ends 22:30 (+0.5 tail, offset by Sat slack) |
| T3 | **12.0 / 12** ⚠️ | 2.75 / 5 | Serial morning (G0→PR→agents→bundle→bench) is tight; T3-6/T3-7 are the flex if the 18:00 bench slot is threatened. All re-runnable |
| N1 | **8.0 / 8** + 0.4 phone ⚠️ | 2.0 / 4 | Friday fits 10:00–18:00 exactly; the 19:30 table read is a phone-in past hours (flagged; async fallback) |
| N2 | **7.7 / 8** | 3.0 / 4 | Late shift 13:30–21:30 |
| **Total** | **≈52.4 / 52** | **≈12.0 / 23** | Friday saturated (+0.4 across T1/T3/N1, each flagged); Saturday holds ~11 h slack = the contingency pool |

**If it doesn't fit, cut in this order (Conduct demo + rubric win every conflict):** (1) LIVE A2 demo surfaces, (2) generated visuals, (3) incident 3 → video-only, (4) the 5 non-critical KB articles, (5) BasedAI Tier-C. **Never** cut: incidents 1+2, the Fetch hard gates, the capture session, the offline bench harness.

### 3.1 Ledger crosswalk — where each committed Tier-A1 line (06 §7) is funded

| 06 §7 Tier-A1 item | ph | Absorbed by |
|---|---|---|
| Conformance bench + independent oracle | 4.5 | T3-3 (topology 1.75) + T3-6 (oracle+harness 2.0) + T3-8 run (0.75 of 1.5) |
| 6/6 adversarial suite | 3.5 | T3-7 (1.75) + T3-8 (0.75) + skeletons pre-written intent (1.0 saved → folded) |
| Audit-coverage test | 1.0 | inside T3-7 block |
| Extractor 100-mutation measurement + robustness chip | 2.5 | T3-5 corpus (1.0) + T1-7 bench (0.5) + T2-4 chip wiring (0.5) + T1-5 generator seed-consume (0.5) |
| Console 5→6 ph, server-rendered+SSE | 1.0 | inside T2-3 (3.25 h block already sized at 6 ph cap incl. polish T2-4) |
| Agent-hop trail footer | 1.5 | inside T1-8 Fetch rails block |
| Hosted degraded-L0 Watcher (promoted to A1) | 1.5 | T1-9 (0.5) + T3-2 pre-registration reuse (1.0) |
| BasedAPIs portability note + Q&A line | 0.25 | inside N2 PR-README packet |
| No-stage submission-surface package | 4.5 | N2-5 BUIDL copy (1.75) + N1 caption layer (0.75) + N2-9 teaser (0.5) + README first-screen in T3-9 window (1.0) + PDF captions N1 Sat (0.5) |
| **The independent FNR/FPR oracle** (round-2 fix) | 1.5 | explicitly inside T3-6 (the "zero imports from the compiler under test" clause) |

Everything in 06 §7 maps to a scheduled task; nothing is silently unfunded. The one place the red-team flagged as at-risk — **T2-1 memory in 3 h** — is de-risked by the §0.1 starter schema + red tests (T2 implements to green rather than designing from scratch), and by the descope rule in §4 (store+retrieve+fail-closed+audit for the 12:30 merge; C-flow stub + full README after).

## 4. Per-profile tracks

### 4.0 Presenter roster (assigned at G0; from 03 §1.1)

**On stage: P1 = T1 (speaks the script), P2 = T2 (drives the console, performs the two hero clicks).** The two builders run their own demo — safest for a live run, and P2≠P1 clicking approvals *is* the segregation-of-duties story on screen. **Q&A owners (all five in the room):** numbers/market → N1; deep tech (A3/A4/A6) → T1 & T2; story/moat/liability (A5/A8) → T3; the human/team question → whoever the team designates (human-only answer). N2 owns the phone party-trick and the backup-video keyboard.

### T1 (Max seat — medium staggered sessions)

| # | Time | Task | Claude Code session strategy |
|---|---|---|---|
| T1-1 | 09:00–09:45 | Wire `precedent/models.py` (**already written+tested, §0.1** — add the live `/models` startup call + Ollama profile) + **register the hello-world Chat-Protocol Watcher** (both badges) | Context: `precedent/models.py`, 02 §1.3. Verify: startup guard runs against a live `/models` call; one ASI:One echo round-trip; CI grep clean |
| T1-2 | 09:45–12:30 | Sim app (one FastAPI, 4 routers, one SQLite) + loaders from committed raw + fixed-seed fixtures + `flake?once=true` + **2 restricted runbook issues seeded with security level 10000** | Subagents per loader. Context: 01 §1–2/§6 (keep the nulls), 02 §4.3, `.env` level IDs. Verify: loader counts vs raw; two identical fixture replays; restricted issues carry the level |
| M-1 | 12:30–13:00 | Merge #1 with T2; **freeze the contracts boundary** (contracts.py, memory public API, SSE event schema); **G1 verdict** | — |
| T1-3 | 13:00–13:45 | UCI ingest via the memory API (fingerprints, `assignment_group` ACL tags, ladder bootstrap) + background embeddings + BM25 fallback | Context: 01 §3, 02 §2.3; reuse `data/analysis` collapse. Verify: ~24.9k records; one BM25-only retrieval; embed job non-blocking |
| T1-4 | 13:45–16:00 | Core loop pt 1: contracts, deterministic extractor + canonicalisation + fingerprint, YAML policy engine, ladder table | Context: 02 §3.1–3.3. Verify: failed extraction caps at L0/L1 with the reason in the trace; risk class only from YAML |
| T1-5 | 16:00–17:30 | Orchestrator + standing-approval fast-path (zero LLM) + snapshot/rollback/demotion + **generator mutation layer that consumes T3-5's canonical seed** | Verify: headless incidents 1/2/R; fast-path trace shows zero LLM calls; **same seed as T3-5 ⇒ identical mutated payloads** |
| DT | 17:30–18:00 | **Dirty-take insurance**: OBS-capture the run end-to-end → `00-raw/` (not a Claude session) | — |
| T1-7 | 18:30–19:00 | **Fixed slot: 100-mutation extractor bench** (T3-5 corpus) → commit correct/degrade/false-fast-path rates. ⚠️ Individual false-fast-path inspection may spill; if so, commit the rates and inspect after 21:00 | — |
| T1-8 | 19:00–21:00 | Fetch rails: real handlers behind the 3 pre-registered addresses, PrecedentProtocol, ASI:One approval flow (sender=principal, 10-min TTL), **hop-trail footer**, TVmaze snapshot quote (A2, G2-green only). **Pause 19:30–19:55 for the table read.** Sign off one-shot answers at 20:00 (5 min) | Verify: fresh ASI:One session end-to-end incl. standing-approval repeat; capture the FINAL shared-chat URL |
| T1-9 | 21:00–21:30 | Hosted degraded-L0 Watcher deploy (with T3); README degraded line → factual | Verify: hosted agent answers a triage chat with the lid closed |
| G5 | 22:00–22:15 | Read the announcement; **call the branch**; tell T2 before capture ends | — |
| Sat | 06:30–08:00 | Airplane-mode rehearsal (incidents 1+2, Wi-Fi off) + hosted-Watcher health + 08:00 fresh-session discoverability re-test | — |
| Sat | 08:00–08:30 | PREP-2: generate the demo run-of-show (both mode variants) per `prep-spec.md` | — |
| Sat | 08:45–09:15 | **G7 rehearsal (presents P1)** | — |

### T2 (Max seat, fresh budget — the two biggest sessions)

| # | Time | Task | Session strategy |
|---|---|---|---|
| T2-1 | 09:30–12:30 | **`precedent_memory`** (biggest session #1). **Start from `precedent_memory/schema.sql` + the 3 red test files (§0.1) — implement store/retrieve/audit to green.** For the 12:30 merge, deliver **store + retrieve (`permitted()`+`stale()` fail-closed, zero LLM imports, TOCTOU one-txn) + hash-chained audit**; C-flow stub + full README come after | Subagents finish `test_conjunction`/`test_fail_closed`/`test_concurrency`. Verify: those 3 pass; no unpermitted snippet/title ever returned; chain verifies over 100 writes |
| M-1 | 12:30–13:00 | Merge #1 + contract freeze (with T1) | — |
| T2-2 | 13:15–16:00 | Jira: 2–3 s poller, versioned ACL sync (**roles + live-scheme grants + issue-security field**), revocation fan-out, write-behind + cache replay, fail-closed lock + banner event | Context: 02 §2.5/§4.1, 06 §1.2b. Verify **against the real site**: role-10007 flip ⇒ deny ≤8 s with `acl_sync_applied`; network-kill drill: restricted denied, public served, writes replay |
| T2-3a | 16:15–17:00 | **Console scaffolding (merge-independent)**: static server-rendered page shell + **Baseline Bar (CSS-width animation) + Approve/Promote/Revoke button shells**, no backend wiring yet | Verify: page renders; Bar animates from a hardcoded value; buttons present |
| M-2 | 17:00–17:15 | Merge #2 + **G2 verdict**; T3 unblocked to bench against main | — |
| T2-3b | 17:15–19:30 | **Console wiring (post-merge)**: bind the 3 buttons + Bar to real SSE events so **incidents 1+2 run by click by 18:00 (G3)**; then feed, streamed trace, audit JSON tail, banner, provenance footer, chip slot. **Pause 19:30–19:55 for the table read** | Verify at 18:00: incidents 1+2 driven by clicks, Bar drawing elapsed bars. L3 label = "Standing Approval" everywhere |
| T2-4 | 20:00–21:00 | Freeze prep: wire the measured chip numbers; close strip + rollback proof panel (A2, G2-green only); `make demo-reset` <30 s; placeholder grep | — |
| T2-5 | 21:00–22:30 | **G4 raw capture session** (pinned): shots 3/4/5/6/7, multiple takes reviewed on playback, 15-s standing-approval close-up **with phone-clock PiP**, recovery+refusal, ASI:One fresh-session recording → labelled `00-raw/` clips | Deliverable = labelled raw clips, not an edit |
| Sat | 06:30–07:30 | Demo-laptop prep: model warm-ups, prompt-hash cache covers every beat, `make demo-reset` ×2 | — |
| Sat | 07:30–08:15 | PREP-1: systems-design walkthrough + slide-8 diagram description | — |
| Sat | 08:45–09:15 | **G7 rehearsal (presents P2 — drives the console)** | — |

### T3 (Claude Pro — serial morning; owns all GitHub-human work + bundles all N packets)

| # | Time | Task |
|---|---|---|
| — | 09:00–09:30 | G0 stand-up (confirm Demo Day form) |
| T3-1 | 09:30–10:15 | **Fork BasedAICo/hackathons + open the skeleton draft PR** (packet `T3-github-publication.md`); ask the mentor which deadline governs, note it in the PR |
| T3-2 | 10:15–11:00 | Pre-register Librarian + Operator skeleton mailbox agents (echo, both badges, keyword-rich) so T1's 19:00 slot only swaps handlers. **Bundle+send N1's KB packet now** (deck packet ~11:00, N2 read-in ~13:15) |
| T3-3 | 11:00–12:45 | Conformance bench pt 1 (zero product-code imports, own worktree): protocol topology (5 levels / 20 roles / 1,000 docs) + **10,000 ground-truth queries incl. ≥3,000 deny-expected** |
| T3-4 | 12:45–13:15 | **Insurance ASI:One shared-chat URL** vs the echo Watcher (fresh session, ≥5 chats toward the ≥10 bar) → evidence index |
| T3-5 | 13:15–14:15 | **Canonical 100-mutation corpus + runner** (deterministic seed declared at G0; tagged categories) → handed to T1 before 18:30 |
| T3-6 | 14:15–16:15 | **Independent oracle** (naive lineage-conjunction walk, **zero imports from the compiler under test**) + FNR/FPR harness + `RESULTS.md` emitter + `make bench` one-command (**A1/unconditional — T3-8 depends on it; the A2 tag applies only to the LIVE bench-command demo surface**) |
| T3-7 | 16:15–18:00 | Adversarial suite: six sponsor-named attacks (one pytest each, named verbatim, degradable to 4/6) + `test_audit_coverage` |
| T3-8 | 18:00–19:30 | Run conformance bench + attacks + concurrency invariant **against merged main**; commit synthetic `RESULTS.md` (measured vs threshold vs pass/fail) |
| T3-9 | 19:30–20:30 | **Secrets scrub then repo PUBLIC** (packet steps; `.env` absence already verified this session — re-confirm). ⚠️ Pause ~25 min at 19:30 for the table read if attending; the scrub is semi-manual and flexes |
| T3-10 | 20:30–21:00 | BasedAI PR content commit (bench numbers + 6-attack table + extractor rates + cites); 21:00 pre-export grep `‹` over deck/README/BUIDL copy |
| Sat | 06:30–08:00 | UCI realism bench (25k-record store; **caption discipline: "25k-record store", never "P99 over 141k events"**) + live drift/TTC if A2 green |
| Sat | 08:00–08:45 | **G6: PR FINAL-READY** — video link pushed, realism numbers as PR comment. **08:30 submit the DoraHacks draft BUIDL** (paste frozen one-shot answers verbatim) |
| Sat | 08:45–09:15 | PREP-4 update-pass on the Prep drafts; **G7 rehearsal Q&A owner (story/moat)**; kit check moved to before departure (video LOCAL on the presenter laptop, QRs scan from 3 m, printed A1 ×3) |
| Sat | 17:00–17:30 | **G8 with N2: logged-out link sweep → final DoraHacks submit** |

### N1 (packets in `Plan/workflows/`; no repo access; T3 bundles/commits) — ONE clock, double-book resolved

| # | Time | Task → packet |
|---|---|---|
| N1-1 | 10:00–13:00 | **KB critical five** (#1 EPG-publish, #4+#5 restricted rights, #6 CrowdStrike, one stale) → `N1-kb-articles.md` (2 per chat; hand to T3 by 13:00 — the retrieval demo needs them early afternoon) |
| N1-3 | 13:00–14:00 | **Manual-loop time-lapse**: perform the manual fix against the sim once (surfaces exist post-G1), screen-record, 8× in QuickTime, burn "8 hrs 51 min" → `00-raw/` |
| N1-2 | 14:00–17:15 | **Deck core 12 slides** in Google Slides → `N1-deck-build.md` (design rules + `[[WAIT]]` tokens for Friday-night numbers) |
| N1-4 | 17:15–18:00 | Appendix A1 (the numbers table — the most-used Q&A slide) + start the per-slide caption sentences |
| N1-5 | 19:30–19:55 | **Table read (phone-in)** — quizzed from `Prep/qa-bank.md` incl. the cross-assignment drill. ⚠️ Past N1's 18:00 end; async fallback in §7 |
| Sat | 06:45–07:30 | **VO record** (one pass, numbers ONLY from 04 §5) → `10-vo/` |
| Sat | 07:30–08:00 | Caption/number QA on N2's cut vs the §5 table; deck PDF re-export with captions + final numbers |
| Sat | 08:00–08:45 | PREP-3 crib sheets ×5 (+ remaining appendix if time) |
| Sat | 08:45–09:15 | Run the G7 rehearsal-gate checklist (`N1-rehearsal-runner.md`) + Q&A owner (numbers) |

*(The 5 non-critical KB articles are explicitly CUT unless Saturday slack appears — the retrieval demo needs only the critical five.)*

### N2 (late shift 13:30–21:30 — covers the freeze window)

| # | Time | Task → packet |
|---|---|---|
| N2-1 | 13:30–13:45 | **Higgsfield upgrade-or-skip** (T1 co-signs; default SKIP) |
| N2-2 | 13:45–14:30 | Venice-stills prompt drafts (**consumed only if T1 is ahead**; cannot block anything) |
| N2-3 | 14:30–15:30 | **Practitioner outreach: 10 warm-first sends** → `N2-practitioner-outreach.md` (replies cutoff Sat 07:30 → quotes to slide 12/A9 **or the line is deleted**) |
| N2-4 | 15:30–16:15 | Shared video folder + naming convention live; review dirty take, log segments |
| N2-5 | 16:15–18:00 | **BUIDL page copy (60-s skim) + ONE-SHOT organizer answers drafted verbatim** → `N2-dorahacks-admin.md` (T1 freezes text at 20:00) |
| N2-6 | 18:00–18:30 | QR codes ×2 (party-trick portal; slide-12 contact) scan-tested + scratch-VO insurance over the dirty take |
| N2-7 | 18:30–19:30 | **Demo playtest as naive user**: 5+ awful phone tickets → TRIAGED/DEGRADED/CONFUSED → `N1N2-demo-playtest.md`; feeds the party-trick rehearsal |
| N2-5b | 19:30–19:55 | Table read (in person) |
| N2-8 | 19:55–21:15 | 30-s teaser strip onto the deck; Fetch deliverables sweep (badges, profile URLs, jump-to-turn); **21:15 arm BOTH selection-branch checklists + set T1's 22:00 alert** |
| Sat | 06:30–09:00 | **Video assembly in CapCut** (Mac; iMovie fallback): **picture-lock 07:15 with scratch VO, real VO swapped as it lands** (deliberate picture-first); main ~4:30 cut **handed off 08:15** (T3 pushes the link by 08:35 — see §5); 30-s teaser; chaptered backup export → `N2-video-edit.md` |
| Sat | 09:00–09:15 | Branch extras (NOT-SELECTED → 90-s cut + inserts) or rehearsal support |
| Sat | 17:00–17:30 | G8 link sweep + final submit with T3 |

## 5. Deck & video production (concrete; the Sat video chain is the tight one)

- **Deck: Google Slides** (browser-only for free tier; live co-edit for the number fill; one-click PDF). Numbers arrive as one metrics block from T3 ~21:30. Degraded rule (pre-ratified): if numbers slip, ship measured-only (94.4% / 18.2 h / 558 classes) and **delete** empty cells — T3's 21:00 `‹`-grep is the guard.
- **Video spine = real screen recordings, never faked.** Raw capture = **T2, pinned to G4 (Fri 21:00–22:30)** → labelled clips in `Precedent-Video/00-raw/` (`shotXX_takeN_HHMM_desc.mov`). **Sat chain (single critical item = the video link): N2 picture-locks 07:15 with scratch VO → real VO (N1, ready 07:30) swapped in → main cut handed off 08:15 → T3 uploads unlisted + pushes the link into the BasedAI PR + BUIDL by 08:35, ten minutes before G6 08:45.** Picture-lock-with-scratch-VO is a *shippable* state, so a late real-VO swap never blocks G6.
- **Insurance ladder:** T1's 17:30 dirty take + N2's scratch VO (18:00) mean **a catastrophic evening still yields a submission-legal Fetch video** — this is the SPOF answer (§6).
- **Generated visuals = optional, skip-biased.** Higgsfield test job **completed this morning** (style frame exists) but free plan ⇒ default SKIP (N2+T1 decide 13:45). Venice stills validated (`venice-sd35`); one capped 45-min T1 slot fires **only if T1 is ahead** at 15:00; N2 quality-gates 15:45; <2 usable ⇒ track closed. Nothing downstream depends on a generated asset.
- Every on-screen stat traces to `Research/00-verified-claims.md` or `data/analysis/` with caveat labels; 04 §5 is the only permitted caption source (N1's Sat 07:30 QA enforces it).

## 6. Risk register (trigger → scheduled mitigation → pre-decided fallback)

| Risk | Trigger | Mitigation in schedule | Fallback (pre-decided) |
|---|---|---|---|
| **Live-demo failure** | Beat stalls >8 s twice, or two §4.3 gates fail | Airplane-mode rehearsal Sat 06:30; chaptered backup from the real capture; `make demo-reset` <30 s | Narrated recording + one live Approve click (ratified at G0, no debate) |
| **Venice latency mid-pitch** | First-token >5 s on stage | Fast-path = zero LLM; 5-s timeouts + canned fallbacks; prompt-hash cache; warm-ups Sat 06:30 | Ollama local profile (still 100% open-weight) |
| **Jira / venue Wi-Fi** | Amber banner, or Window B not rendering in 2 s | Write-behind + cache replay (T2-2, network-kill-drilled); phone hotspot; sync-tick gate on every Window B cut | Skip Window B cuts; say the §4.1 line once; fail-closed lock is a visible feature |
| **Claude usage caps** | 13:00/19:00 check shows a Max seat near cap | Seat bias (T2 fresh; T1's spend acknowledged); staggered heavy blocks; **starter code (§0.1) cut T2-1's authoring load** | **Concrete:** T2-4 wiring + T2-3 polish → Codex (non-agentic); remaining backend → T1's next window via this plan's kickoff specs; T3 Pro = review only |
| **Teammate blocked** | Any track stalls >45 min | Written DoD + kickoff spec per task; self-contained packets; fixed merge times | Checkpoint cuts fire early; Sat slack (~11 h) absorbs; the demo path (T1-4/5, T2-1/3) is never reassigned mid-day — cut scope instead |
| **N2 Sat-assembly SPOF** (feeds backup video, Fetch artifact, PR link, BUIDL) | N2 blocked Sat AM | **T3 is the named fallback assembler** (already the hand-off hub); the Fri dirty take + scratch VO is submission-shippable, so a missing assembly still yields a legal Fetch video and a backup clip | Ship the insurance cut; T3 assembles the teaser from T2's raw clips in the 08:00 window |
| **Generated-visual quality** | N2's 15:45 gate: <2 usable | Track optional by construction | Close it; teaser uses real console stills |
| **Not selected to present (~22:00)** | G5 announcement | Both checklists armed 21:15; T1 calls it at 22:00 | **NOT-SELECTED:** Sat rehearsal hours redirect — N2: 90-s cut FIRST on the BUIDL page + RESTRICT/party-trick video inserts; N1: extra deck-PDF + README-first-screen QA; T1: harden hosted-Watcher + ASI:One artifacts (the surfaces async judges see). DoraHacks/BasedAI/Fetch judging unaffected; Demo Day attendance stands (networking + mentors) |

## 7. Prep phase (real scheduled hours)

Written this session (read tonight, ~20 min each): `Prep/industry-primer.md` · `Prep/qa-bank.md` · `Prep/tech-explainer.md` (two depths) · `Prep/glossary.md`. Build-dependent docs specced in `Plan/prep-spec.md` with generator, gate-pinned time, paste-ready prompt: systems walkthrough (T2, Sat 07:30), demo run-of-show both variants (T1, Sat 08:00), crib sheets ×5 (N1, Sat 08:00), update-pass (T3, Sat 08:45).

**Table read — Fri 19:30–19:55 (moved off the 20:15 collision the red-team caught).** All five: three questions each from the bank, **including the deliberate cross-assignment** where a technical question goes to N2, answered via crib sheet + the bridge line. T1 pauses Fetch rails; T3 pauses the scrub; N2 is between playtest and teaser; **N1 joins by phone (past hours).** ⚠️ **Async fallback if N1 can't stay past 18:00:** everyone drafts their three answers into a shared doc during Friday seams, and the synchronous cross-assignment drill folds into the **Sat 08:45 G7 rehearsal window** instead (presenters already gathered). Q&A stage assignments per §4.0.

## 8. What got compressed / cut, said plainly

- **The 18:00 gate has no buffer** — I removed the "CONFIRMED ACHIEVABLE" claim the first draft made; the honest position is that 18:00 is tight and the 13:00/17:00 checkpoints are the mechanical protection. If the morning slips, cut-lines fire at 13:00, not silently at 18:00.
- Friday is saturated (+0.4 h across T1/T3/N1, each flagged in §3); absorbed by light tails and the ~0.75 h of real T1 gaps.
- Generated visuals: opportunistic, zero schedule authority.
- 5 non-critical KB articles: cut unless Saturday slack appears (retrieval demo needs only the critical five).
- Tier C (temporal-embargo, derived-memory correctness bench, O(1) curve, change-record artifact, BasedAPIs venue run): **unfunded** unless the Saturday pool materialises (T3 decides Sat 17:00).
- Payment Protocol: README/Q&A monetization line only (decided in refinement — not worth the hours against Conduct's £8,000 rubric on a 1,000-USDT track).

## 9. Red-team fixes applied (changelog)

Both adversarial reviewers ran on Opus 4.8 after the first pass hit a model limit. Fixes folded in: **(fatal)** removed the "CONFIRMED ACHIEVABLE" overclaim and made G1 a mandatory cut-fire; resolved N1's Friday double-book to one clock (KB→time-lapse→deck-core, appendix to Sat). **(major)** T2 console split into merge-independent scaffolding (16:15) + post-merge wiring (17:15) so it doesn't start before its own merge; table read moved 20:15→19:30 off three live tasks; §3 hours recomputed from actual task times (no more non-reproducing figures); T3 morning serialized (G0→PR→agents→bundle→bench, no overlaps); `make bench` reclassified A2→A1 (T3-8 depends on it); N2 Sat-assembly SPOF given a named fallback assembler + shippable insurance cut; mutation seed declared canonical at G0 (one seed, one number, four surfaces); Sat video chain re-timed (08:15 hand-off → link by 08:35, picture-lock-with-scratch-VO shippable); presenter roster assigned; T2 usage-cap overflow made concrete. **(de-risk)** pre-wrote + tested `models.py`, `schema.sql`, and 9 spec tests so T2 starts the riskiest task from red tests (§0.1).
