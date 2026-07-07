# Precedent — startup direction (decided 6 Jul 2026)

> Output of a three-stage multi-agent development run on 6 Jul 2026:
> (1) a 19-agent web-research fleet (5 lenses, 14 adversarial claim-verifications);
> (2) four independent strategy thinkers, each steelmanning a different direction;
> (3) four evaluator lenses (UK seed VC, composite buyer, skeptical staff engineer,
> GTM operator) judging all four comparatively, then a synthesis pass; final
> judgment applied by the orchestrating session with first-hand access to all inputs.
> Full transcripts and scores are in the session workspace; the market claims below
> carry the verification labels from the adversarial pass.

## The decision

**Precedent Gate — change control for AI agents — sold through two doors that
converge on one product and one POC shape.**

> "Your team already built an agent that CAN act. Precedent makes it ALLOWED to
> act — and proves it."

- **Door 1 (primary ICP):** platform-engineering / SRE leads at UK/EU digital
  natives (150–2,000 staff) whose homegrown agent works in staging but is blocked
  at change management, security review, or operational-resilience sign-off. They
  hold £20–50k team-level signature authority and feel the pain personally.
- **Door 2 (the founders' warm network; fixes Door 1's "must already have a blocked
  agent" prerequisite):** streaming/broadcast ops leads with heavy repeat-incident
  load. Here Precedent supplies **both the agent and the gate** — the existing
  retrieve-the-documented-fix loop over their runbooks, executed through the same
  ladder. First-hand streaming-ops credibility opens these rooms.

What the product is, in one breath: the deterministic, fail-closed gate between
any agent and the systems it touches — sha256 class-keyed risk classification with
**zero LLM in any permission or risk decision** (CI-enforced, verifiable in source),
a graduated approval ladder (L0 observe → L1 recommend → L2 human-approved →
L3 **Standing Approval** — human-promoted, always revocable, auto-demoting on
verification failure, never marketed as "autonomous"), **pre-state snapshot +
pre-generated inverse before every execution**, and a **hash-chained evidence pack**
any auditor can verify with a standalone script and no vendor licence.

Investor story: what Gartner began calling **guardian agents** (first Market Guide
Feb 2026). Sales conversation: never "control plane" — a team-priced product.

## Why this direction (and what the market looks like, July 2026)

Verified landscape (adversarially checked 6 Jul; labels kept):
- **ServiceNow** shipped the closest thing to Precedent's pattern inside its own
  universe: Autonomous Workforce / L1 Service Desk AI Specialist (announced
  26 Feb 2026; vendor-claimed "99% faster", not independently audited), repackaged
  9 Apr 2026 into AI-native tiers where autonomous ITSM agents sit only in the top
  **Prime** tier and every agentic action burns metered "Assists" (~150 per large
  action; per partner/secondary sources). The old line "they monetise the workflow;
  we delete it" is **stale**; the 2026-true version is a **price/complexity umbrella**
  plus cross-vendor coverage they don't attempt.
- **Resolve AI** ($125M Series A at $1B, 4 Feb 2026, Lightspeed — TechCrunch/
  Bloomberg-confirmed) executes with human oversight on the infra/code plane. The
  hackathon claim "AI SREs stop before execution" must be scoped: **before execution
  in business applications**.
- **Nobody funded ships the precise combination**: retrieve the org's OWN documented
  fix → deterministic no-LLM risk classing → graduated standing approvals → typed
  execution in business apps → verify/auto-rollback → provenance that compounds.
  PagerDuty is closest and runs only pre-built automation jobs (the RPA pattern).
- **Trust is the named bottleneck** buyers and analysts keep citing (Gartner's
  >40%-cancellation prediction over missing risk controls; read-only-by-design
  competitors). Precedent's deterministic gate + fail-closed memory + hash-chained
  audit is aimed at exactly the blocker the market names.
- **Regulatory tailwind, labelled:** EU AI Act Article 12 record-keeping lands
  2 Aug 2026 (whether incident-remediation agents fall in Annex III high-risk needs
  legal review — do not overclaim); UK FCA/PRA operational-resilience regime live.
  Evidence packs say "evidence support, not a compliance determination."

Evaluator votes split C (VC 62), C (GTM 66), A (Buyer 62), B (Engineer 78) — resolved
by asking what each lens measured: reachability beats economics at zero signal
(A's MSP wedge dies on no channel network), buildability constraints from B are
adopted wholesale without B's company, and D's evidence pack becomes a Gate feature
rather than a compliance-first company.

## What was explicitly killed (and why)

- **MSP-first GTM as the primary wedge** — no channel network; ~37% assumed cold
  conversion vs 3–5% reality. **Parked as wave 2**, unlocked after 2 paying logos.
- **Real-environment execution tools in this window** (password resets, DNS writes)
  — a password reset has no pre-generated inverse, violating the rollback-precedes-
  execution hard rule; and no buyer grants write access to an uninsured seed vendor
  (post-Kaseya-VSA reality). Execution stays sim/staging until insurance + contracts.
- **Per-verified-fix billing now** — metering revenue off a single-writer SQLite
  audit log is a billing-integrity defect; revisit after the Postgres option.
- **Standalone memory-company motion; Apache-2.0 of the full library** — ~$492M
  2026 standalone-governance market (research-cited), Credal non-breakout, and an
  acquisition-shaped ceiling; irreversible OSS of the crown jewel before pricing
  signal forecloses the option. **OSS the THIN gate/MCP server only.**
- **"Principal from MCP client identity"** — no robust MCP identity standard in
  2026; principals are registered out-of-band and documented honestly.
- **FS-compliance-first ICP** — 3–6-month procurement inside a 90-day window is
  self-refuting; regulated-ops language becomes expansion collateral, not the wedge.
- **Analyzer as cold hook / free pilots** — cold prospects don't run a stranger's
  binary on ticket data. Funnel order: **conversation → analyzer → POC**. Paid POCs
  are the only accepted buyer signal.

## Pricing (anchored)

- **POC:** £10,000 fixed, 8 weeks, capped at 5 concurrent, 100% credited to year-1.
  Shadow/staging-first; written success criteria: ≥3 real action classes gated,
  ≥1 standing-approval promotion clicked by THEIR human, 1 injected-failure rollback
  demonstrated, evidence pack accepted by their risk/change stakeholder, and a
  documented head-to-head vs their hypothetical internal Slack-bot build. Match-rate
  criteria are re-based on the prospect's own analyzer numbers — never signed blind.
- **Optional rung:** £3,000 signed analyzer findings readout (a document = consulting
  spend = clears procurement with no vendor-risk review); credited into the POC.
- **Team tier:** £1,750/month (£21k/yr) — 10 registered agents, 25 gated action
  classes, unlimited approvers, Slack approvals, audit export.
- **Growth tier:** £48k/yr — SSO/SCIM, self-hosted/VPC deploy, evidence-pack
  templates, custom action-class support.
- Wave-2 (MSP motion, parked): per-verified-fix economics — "the invoice is the
  audit log" — after Postgres and insurance.

## The 90-day motion

Funnel: warm conversation → local analyzer run on their ticket export (data never
leaves; the report is the qualification instrument AND our extractor-coverage
calibration) → £10k POC scoped from their own standing-approval-candidate list.

~4 conversations/week for 10 weeks (40 total) across both doors, warm-first
(streaming ops: DAZN, Sky/NOW, ITV, BBC iPlayer, Channel 4, Red Bee, Arqiva;
platform eng: Ocado Technology, Monzo, Starling; bench: Zopa, Tide, Checkout.com,
Cleo, Wise; one MSP design-partner slot reserved, Claranet/Littlefish class).

**Day-90 kill gate (pre-committed):** fewer than 2 paid POCs signed by end-Sep 2026
falsifies the "teams will pay for agent change control" hypothesis → formal
direction review (wave-2 MSP economics and the evidence-first motion are the
on-file alternatives). Believe the doors, not the deck.

No fundraise conversation before 2 paid POCs; Feb 2027 raise/no-raise decision
(£500–750k pre-seed on design-partner evidence, or default-alive on POC revenue).

## Build scope

The software for the next 2–3 agent-accelerated weeks is ~90% direction-invariant
(all four thinkers converged on the same three atoms: local-first analyzer,
evidence pack + verifier, trust-moment demo). The full prioritised scope with
acceptance criteria lives in [`ULTRACODE-PROMPT.md`](../ULTRACODE-PROMPT.md);
summary:

- **P0:** Gate API + MCP server (typed proposals → deterministic decisions);
  Evidence Pack v1 + standalone zero-dependency verifier; Precedent Analyzer CLI
  (local-only, byte-reproduces the UCI numbers, honesty labels printed on the
  report); hosted demo repointed to the gate story (three-pane, visitor-as-approver,
  rollback + fail-closed beats, evidence-pack download, two CTAs); policy-pack
  authoring kit with 8–10 sim-executable action classes; the trust-story defect
  ledger burned down.
- **P1:** real Slack approvals; Python/TypeScript SDKs + Claude Agent SDK/LangGraph
  middleware (15-minute gated-agent quickstart, CI-timed); thin-gate OSS release
  prep (separate repo); streaming-ops scenario pack (Door 2); weekly gate report.
- **P2:** design-partner deploy kit (compose + Postgres option); analyzer PSA
  formats (keeps wave-2 open); regulatory field mapping (only after legal review);
  probing-detection wiring; Teams approvals (only if a partner pays for it).

## Founder actions (software cannot do these)

1. Incorporate the Ltd; bank account; POC contract template with liability cap.
2. Start E&O/cyber insurance binding in week 1 — certificate required before any
   non-sim execution; brokers take weeks.
3. Private GitHub org for commercial code/customer artifacts — this public repo
   auto-pushes `main`; committing IS publishing. Trust-fatal if botched.
4. Write the 30-name warm-intro list; first 10 intros this week; 4 conversations/
   week cadence; funnel order enforced.
5. Calendly with 5 visible design-partner slots + the POC one-pager.
6. Rehearse the 90-second DIY answer (what the weekend Slack bot lacks: inverse-
   before-execute contract, standing-approval lifecycle with auto-demotion,
   hash-chained evidence + standalone verifier).
7. Slack workspace + app registration (P1 approvals). Decide Jira tier before the
   trial expires ~17 Jul (demo already passes airplane-mode without it).
8. Trademark/name screen on "Precedent"; secure the domain.
9. Do NOT open a fundraise before 2 paid POCs.

## Six-month line

- **End Jul 2026:** Ultracode P0 shipped green; hosted demo live; Ltd formed;
  insurance application in; first 10 warm conversations booked.
- **End Aug:** 25+ conversations; ≥8 analyzer runs on real exports; 2 paid POCs
  signed (≥1 per door); thin-gate OSS + MCP directory listing; Slack approvals live.
- **End Sep — DAY-90 KILL GATE:** ≥40 conversations; <2 paid POCs ⇒ direction review.
- **End Oct:** first POC completes written criteria (partner's human promotes a
  standing approval; injected-failure rollback shown; evidence pack accepted).
- **End Nov:** 3 paying customers; £40–60k signed/committed; 25+ policy classes
  (≥1 partner-contributed); analyzer corpus at 3+ real schemas.
- **Dec–Jan:** ≥1 annual conversion; £60–100k total; seed materials grounded in
  logos + measured data + multi-dataset generalisation of the 94.4% claim.
  **Feb 2027: raise/no-raise.**

## Risk register (top of)

- **Zero recorded buyer signal is the master risk** — the 90-day plan is designed
  as a falsification engine, not a hope engine.
- **DIY objection** ("our Slack bot does this") — first-meeting answer rehearsed;
  head-to-head contractually inside every POC. If buyers keep choosing DIY, the
  kill gate reads it.
- **The "rail" is really an SDK today** — typed proposals don't exist in third-party
  agents natively; honest product positioning + middleware adapters + MCP server.
- **Extractor recall is a safety property, not capability** (8/100 recovered on the
  deliberately-adversarial corpus; failure mode is silence). The analyzer doubles
  as the per-prospect coverage instrument; never sell recall we haven't measured
  on their data.
- **Interception-point commoditisation** (first-party permission prompts, Entra
  Agent ID, open MCP gateways) — we open-source the thin gateway ourselves and
  monetise the lifecycle: standing-approval semantics, verification/rollback
  contract, evidence packs.
- **Single-writer SQLite** — fine for POCs; Postgres before any usage-billed or
  multi-tenant production contract.
- Full register in the session record; every market claim above carries its
  verification label, and anything unlabelled is internal measurement
  (see [`docs/numbers.md`](numbers.md)).
