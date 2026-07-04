# Precedent — recorded-video voice-over script

> Paired shot-for-shot with `Prep/video/shot-list.md` (shots 0–8). **Reconciled (V1):** this file and
> the shot-list VO cues are both derived from `Prep/video/pipeline/vo_canonical.json` and are kept
> word-identical by `Prep/video/pipeline/check_vo_sync.py` — do not hand-edit one without the other.
> The **two memorable lines must survive any cut**: *"the second time is free"* (shot 5) and *"it
> knows what it's not allowed to touch"* (shot 6). Timings are the reconciled slot durations
> (cumulative timeline in the shot-list). Read calm, unhurried; **let the stopwatch do the drama.**
>
> Honesty (from `Prep/final-numbers.md`, enforced by CAPTION-AUDITOR): **8h51m is BUSINESS** (MetricNet,
> shot 2) and **18 hours is CALENDAR** (UCI, shot 7) — labelled in speech, never blended. "141k-event
> log" is a **provenance** line (shot 3), never a P99 denominator. L3 is **Standing Approval**, never
> autonomous. No model id is ever spoken — "open-weight models" only.

## Shot 0 — Results-first cold open (0:14) — NO VO
Music/beat only over the three payoff frames (58s-vs-8h51m bar · 15s stopwatch · refusal card).
`VO_shot0` does not exist by design — captions carry it.

## Shot 1 — Cold-open narrative (0:15)
> When the CrowdStrike outage took broadcasters off air, the fix was already documented — humans
> applied it by hand, thousands of times. One of us watched that loop every day inside Disney+
> operations.

_Note: the picture is a **built text-card** (no Sky News still — V2), then the staged manual-loop
time-lapse. "Disney+ operations" is the approved phrasing (a role, not a product the operator ran)._

## Shot 2 — The manual loop + the 8× time-lapse (0:26)
> Read the ticket, hunt the runbook, click through a legacy admin console, wait in an approval queue.
> The industry average: eight hours fifty-one minutes — MetricNet's business-hours benchmark. And at
> ServiceNow's own support desk, over sixty percent of incidents were repeats — the fix already
> existed, and nobody could find it. Precedent remembers every fix your organisation has ever applied,
> and applies it again: risk-classified, approval-gated, audited, reversible.

_Note: "8h51m" is the **business-hours** figure (labelled in-speech). Never blended with shot 7's
18-**calendar**-hour median._

## Shot 3 — Console home (0:08, trimmed per PLAN-CRITIC)
> This is MediaCo, our simulated broadcaster — seeded entirely with real public data, running on a real
> Jira Service Management instance.

_Note: PLAN-CRITIC trim adopted — shot 3 is ~8s and the full provenance list (141k-event UCI log,
runbooks, programme metadata, licences) folds into a **caption over shot 4**, not the VO, tightening the
pre-hero-click runway. "141k" thus lives only in captions (shot-4 provenance window + shot-7A), never a
P99 denominator. TMDB/BBC-programmes never named. The "mangled ticket" tee-up now lives in shot 4's VO
("filed with typos and the wrong error code")._

## Shot 4 — Incident 1: messy ticket → one human click (0:40)
> A publish failure — filed with typos and the wrong error code; the inputs are mutated every run.
> Precedent triages it, retrieves the organisation's own documented fix, classifies the risk, and
> writes the rollback before asking. One human click approves. It executes, verifies, and closes the
> real Jira ticket with the evidence attached. Then the operations lead pre-approves this fix class —
> a standing approval she can revoke at any time.

## Shot 5 — ★ ASI:One segment (80s — Fetch centrepiece, never shortened)
> Everything you just saw needs no custom frontend at all. Precedent's agents live on Fetch.ai's
> Agentverse and speak the Chat Protocol — the gateway agent, the retrieval agent and the execution
> agent are separate Agentverse agents passing messages between themselves. Here's the whole loop
> inside one ASI:One conversation: report the incident in plain English… get the plan and the
> rollback… type 'approve' — that approval is bound to the chat sender's address and logged as the
> authorising principal… and the real Jira ticket closes. Same session, second occurrence: fifteen
> seconds, standing approval — the second time is free. The agents stay registered and running on
> Agentverse after this hackathon.

_Note: the refusal narration does NOT live here — it stays with shot 6's picture (fixing the V1 fork).
"the gateway agent", never "the Watcher". The "approve" is a human typing; the permission decision is
the deterministic gate keyed on the chat-sender identity, never the model. The 15s is this session's
on-screen timer, never a general benchmark._

## Shot 6 — Recovery + refusal, back-to-back (0:28)
> When a remembered fix fails, verification catches it, the pre-written rollback restores the system,
> and the class is demoted — it must earn approval again. And when the only documented fix is one it
> isn't permitted to read — here, a rights runbook restricted to another team — it refuses, and routes
> a dossier to the humans who are. It knows what it's not allowed to touch — down to the permissions on
> the runbook itself.

_Note: the refusal card discloses only that a fix exists + the owning team (fail-closed) — never the
restricted runbook's title/body. Demotion is mechanical (any rollback demotes), not an LLM decision.
Contains the verbatim memorable line "it knows what it's not allowed to touch"._

## Shot 7 — Scale artifact (0:27 — squeeze to 15s if needed; dropped entirely in the 90s cut)
> Does it hold at scale? Twenty-five thousand real incidents, seeded as day-one memory: ninety-four
> percent arrived with their fix already precedented — and those repeats still took a median of
> eighteen calendar hours by hand. Permission-checked retrieval over that store leaks nothing: zero
> leaks across five thousand two hundred and nineteen deny-expected queries, six of six attacks, graded
> by an independent oracle. It runs entirely on open-weight models.

_Note: THE never-blend crux. "25k store", never "141k". "eighteen calendar hours" (labelled) — the UCI
repeat-median, kept apart from shot 2's 8h51m business MTTR. "94%" = fix-class existence, not accuracy.
No model id — "open-weight models". If squeezed to 15s, drop the bench sentence (keep 94% / 18-calendar
/ open-weight)._

## Shot 8 — Close + links (0:30)
> AI SREs fix broken code — but in real enterprises the fix is almost never code. It's a documented
> change, waiting to be remembered. ServiceNow paid two-point-eight-five billion dollars for Moveworks;
> the memory layer is worth buying. We're Precedent — every incident resolved becomes precedent. Repo,
> live agents and the ASI:One chat are linked below.

_Note: the end-card CAPTION carries the tagline "Precedent — the second time is free". "$2.85 billion
for Moveworks" is a public deal comp. No secrets/real names on the links card (a role-flagged team
card, "Disney+ alum")._
