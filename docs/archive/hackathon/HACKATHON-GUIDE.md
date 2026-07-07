# UK AI Agent Hackathon EP5 × Conduct — Complete Guide

> Compiled 2 July 2026 from the official DoraHacks page, the AI Agents Lab event site, and the
> "UK AI Agent Hackathon group 2" WhatsApp chat archive (plus the bounty docs linked from those sources).

---

## 1. Event Overview

| | |
|---|---|
| **Name** | UK AI Agent Hackathon EP5 × Conduct ("Building the Future of Autonomous Agents") |
| **Dates** | 28 June – 4 July 2026 (7 days) |
| **Venue** | Imperial College London — Opening: **CAGB 200, City & Guilds Building** (ground floor, main entrance off Exhibition Road); Hack-week workshops/co-working: **Blackett Laboratory, room BLKT 112**; Demo Day: **Blackett LT1** |
| **Format** | Hybrid-friendly: in-person strongly encouraged (opening day + Demo Day especially), but building remotely is allowed. Workshops streamed on X (quality was patchy). No overnight stays; food & drinks provided daily (~6pm pizza) |
| **Organizers** | Imperial AI Society, Imperial Blockchain & FinTech Society, UK AI Agents Lab |
| **Total prize pool** | **$33,300 USD** (DoraHacks) + £7,500 Cantor8 learner pool counted within it + post-hackathon opportunities |
| **Scale** | Described as one of the largest university-led AI agent hackathons in Europe; ~530 participants received OpenAI credits; 101 registered hackers on DoraHacks at time of writing |
| **Registration** | Luma (event) + DoraHacks (project submission): https://dorahacks.io/hackathon/2272 — event page: https://www.aiagentslab.uk/hackathon/ep5 |
| **Post-hackathon** | 🏛️ **House of Lords Showcase (September 2026)** — selected winning teams present at UK Parliament to sponsors, investors, policymakers |

### Key contacts / channels
- **Organizers in WhatsApp:** ~Ming (main coordinator, TG: @mingthehacked), ~Shafi Maahe, ~margaret (may). Email: aisociety@imperial.ac.uk
- **Discord (main, "make sure you join"):** https://discord.gg/mJNCdXUByr (team-formation channel: https://discord.gg/gZahXh7HA)
- **Conduct track WhatsApp group:** https://chat.whatsapp.com/Ibn3YMi3uHeKeYUNNXu76Y?mode=gi_t
- **Cantor8 support:** dedicated Telegram group (ask Ming for access) — used for chasing £50 payouts and task help
- **Opening-day photos/clips:** https://drive.google.com/drive/folders/1jPazWkBg9F4B8NPn0CKFqI7pFRKRupdb?usp=sharing

---

## 2. Critical Dates & Deadlines

| When | What |
|---|---|
| 28 Jun, 10:00 | Opening Ceremony (CAGB 200) — submissions open on DoraHacks |
| 28 Jun, 12:00 (noon) | **Cutoff that mattered for OpenAI credits** — you had to be Luma-registered with a ChatGPT account on that email before this |
| 29 Jun – 3 Jul | Workshops, mentor sessions, co-working (BLKT 112, ~12:00 → evening) |
| **3 Jul, 18:00 UK** | **Demo Day sign-up form deadline:** https://forms.gle/fnUe3vL24wyJo6pD7 |
| 3 Jul, ~22:00 UK | Selected Demo Day presenters announced |
| **4 Jul, 10:00–16:30** | **Demo Day** at Blackett LT1 (in-person pitches only; kicks off with fireside chat with Simon, COO of EWOR) |
| **4 Jul, 23:59** | **DoraHacks submission deadline** ("by end of Demo Day") |
| 20 Jul | CoralOS/Superteam winners announced (per Superteam listing) |
| September 2026 | House of Lords Showcase for selected winners |

---

## 3. Tracks & Bounties (8 total, on DoraHacks)

Submission portal: https://dorahacks.io/hackathon/2272/bounties — **you may apply to up to 10 bounties per BUIDL** (one project can target multiple tracks; you pitch once and tick every bounty you want to be judged for). Teams reported targeting ~6 tracks with one project.

### 3.1 Conduct Track: "Make Legacy Move" — **£8,000 GBP** (biggest single track)
- **Sponsor:** Conduct AI (title sponsor) — agentic AI for enterprise legacy systems (starting with SAP): reads code, maps dependencies, captures institutional knowledge, speeds planning/dev/testing of system changes. Recently raised a $60M Series A (Index & ICONIQ).
- **Mission:** Pick a slow, inefficient process at large enterprises today and build a tool that lets a user do it **far faster with AI while staying in control**. Start with the process — use industry knowledge, articles, or practitioners to find a task enterprise teams spend weeks on, then build something that does it in hours.
- **Context:** Enterprises run on decades-old custom software, millions of lines deep, little documentation; changes that should take days take months and millions in consultant fees.
- **Their submission wishes:** GitHub repo (code + setup + docs), pitch deck (problem, solution, product, tech, use case, demo flow), demo/pitch video — "short and snappy; we want the problem and the **wow moment for enterprise teams**".
- **Support:** Discord https://discord.gg/xyrUj2XFv + dedicated WhatsApp group (link above).
- Bounty page: https://dorahacks.io/hackathon/bounty/1370

### 3.2 CoralOS & Superteam UK — "Build the Agent Economy" — **5,000 USDT / USDG**
- **Sponsor:** CoralOS — zero-trust coordination infrastructure for multi-agent systems; framework-agnostic, MCP-native (Solana ecosystem, with Superteam UK).
- **Build:** "Agents that earn" — LLM seller agents competing in a shared marketplace, paid via **Solana escrow smart contracts** (trustless settlement: release on delivery, refund on failure). Reference stack: Vite+React auction dashboard, `deliverService()` service layer, configurable seller personas, LLM buyer logic, Solana Pay + escrow (Rust program, devnet, SOL/USDC), optional arbiter/reseller/oracle agents. All components are yours to change.
- **Prize split (Superteam listing):** 1st 3,000 / 2nd 500 / 3rd 500 / 4th 500 / 5th 500 USDG. **UK-restricted.** Winners announced 20 July.
- ⚠️ **Separate submission process:** submit on **Superteam Earn**, *not* the general DoraHacks flow: https://superteam.fun/earn/listing/imperial-ai-agent-hackathon-build-the-agent-economy
- **Resources:** Track brief: https://xforce-decentralised-protocols.gitbook.io/solanaxcoralos/the-build/main-track-build-the-agent-economy • Starter kit: https://github.com/trilltino/solana_coralOS • Skill set: https://github.com/Coral-Protocol/coral-skill-set • 1:1 builder support: https://discord.gg/tRnC3YjMV
- Bounty page: https://dorahacks.io/hackathon/bounty/1371

### 3.3 Cantor8 "Learner Bounty for everyone" — **£7,500 (£50 × first 150 people)**
- **Sponsor:** Cantor8 — building on the **Canton Network** (permissioned blockchain; validators require approval; actors are "Parties" hosted on validators; C8 runs a non-custodial wallet).
- **Task ("Touching the Ledger: A Canton Low-Level Lab")** — all via a validator's low-level Admin/Ledger APIs on DevNet:
  1. Register (allocate) a new internal party via C8's DevNet node (`/v0/admin/external-party/topology/{generate,submit}` — *not* `setup-proposal`), note the PartyId
  2. Set up a PreApproval DAML contract instance; verify the TX in the public explorer
  3. Tell the team your PartyId → they send you Canton Coins (CC)
  4. Check balance by indexing the Active Contracts Set (ACS) / Holding interface
  5. (Stretch) Make a Token Standard transfer to another Party
- **Auth:** every Ledger API request needs a JWT bearer token from Keycloak (`client_credentials` grant). IdP: https://auth.dev.digik.cantor8.tech (realm `master`); client id `hackathon`, secret in the task doc. Admin API: https://api.validator.dev.digik.cantor8.tech/api/validator ; Ledger API JSON: .../api/ledger (ws for async), gRPC: api.validator.dev.digik.cantor8.tech/api/rpc_ledger
- **Docs:** https://docs.canton.network (Admin API, Ledger API, Token Standard deep-dive)
- **Task doc:** https://docs.google.com/document/d/1fMDNbHDdH6JqfKjnTVPN3PbADJyh23v6k-hjZqEmy8Y • **Slides:** https://docs.google.com/presentation/d/1nUS6Po8882UuAeFr15gy25fMZF5z7VaoQtAC_6L87Zg • **Submit:** https://forms.gle/YMEr9rpZzq5fqxJDA
- ⚠️ Chat reality-check (2 Jul): several people completed it but **hadn't been paid yet**; payouts being chased via the Cantor8 Telegram group. Originally pitched as an onboarding task at the 28 Jun Cantor8 dinner (first 150 finishers get £50).
- Bounty page: https://dorahacks.io/hackathon/bounty/1368

### 3.4 BasedAI Bounty — **$3,800 worth of credits**
- **Sponsor:** BasedAI — commercialization layer for open-source AI (open-weight models as production APIs / AI workforces).
- **Challenge — build a permission-aware memory layer that:**
  - Stays synchronized with source ACLs under concurrent updates
  - Enforces access **at the retrieval layer** (not application layer), with **no LLM call in the permission decision** — classification may use an LLM at write time, but final enforcement must be deterministic
  - Produces audit logs meeting regulatory standards
  - Maintains **sub-200ms P99 latency** for permission checks
  - Governs derived memory **by lineage**: summaries/embeddings/notes inherit source access constraints; revoking a source propagates to derivatives
- **Bonus challenges:** temporal access rules (e.g. "leadership call notes unlock after 30 days"); query-time inference prevention (detect cross-permission-boundary context leaks)
- **Support:** Discord https://discord.gg/xVhZHub8U • Bounty page: https://dorahacks.io/hackathon/bounty/1364

### 3.5 Bittensor Bounty — **$1,500 USD**
- **Sponsor:** Bittensor / Opentensor Foundation — decentralized incentive network for machine intelligence (128 subnet companies: inference, pre-training, RL, confidential compute, storage…).
- **Challenge:** Build agents that compete in the **4 live competitions on Apex** (Macrocosmos' Kaggle-like platform, Subnet 1). Submit solutions via the **Apex CLI**. You compete on **mainnet against non-hackathon participants** — real ongoing monetary rewards if you win (potentially hundreds/thousands of $ per day beyond the bounty).
- **Get started:** registration form https://docs.google.com/forms/d/1asV_Vye3IauOWqplcCyTN7MjI_AubE_8ktQt9EboUXw • competitions: https://apex.macrocosmos.ai/ • miner setup docs: https://docs.macrocosmos.ai/subnets/subnet-1-apex/subnet-1-base-miner-setup
- **Info doc:** https://docs.google.com/document/d/13q7LPrbEOQBAruznMiFYtqOOWS_9TMtBA6VABlmzt6o • Bounty page: https://dorahacks.io/hackathon/bounty/1365

### 3.6 Fetch.ai Bounty — **1,000 USDT** (cash: 1st £500, 2nd £350, 3rd £150 + internship interview opportunities)
- **Sponsor:** Fetch.ai (headline sponsor).
- **Challenge:** Build a single- or multi-agent system that solves a clearly defined real-world problem; performs multi-step planning/decision-making/orchestration; uses tools, APIs, data sources or other agents to produce an executable outcome — beyond a chatbot.
- **Mandatory for prize eligibility:**
  - ≥1 agent registered on **Agentverse**
  - Implements the **Agent Chat Protocol**
  - Discoverable & usable through **ASI:One**, with the core use case demonstrable **inside an ASI:One conversation**
  - Meaningful tool execution or multi-agent orchestration; primary workflow must complete **without a custom frontend**
  - Public GitHub repo with run instructions
- **Any framework allowed:** uAgents, Google ADK, LangGraph, CrewAI, OpenAI Agents SDK, Claude Agent SDK, or plain Python.
- **Judging weights:** Functionality & technical implementation 25% • Fetch.ai tech integration 25% • Innovation & creativity 20% • Real-world impact 20% • UX & presentation 10%
- **Bonus points:** multi-agent collaboration, **Payment Protocol (FET/Skyfire) monetization**, reliability/error handling, creative real-time data use, agents that keep running post-hackathon.
- **Deliverables:** public ASI:One shared chat URL demoing the full workflow, Agentverse agent profile URL(s), GitHub repo, 3–5 min demo video, brief problem/user/outcome description.
- **Judges:** Sana Wajid (CDO), Attila Bagoly (CAO) + 7 mentors (dev advocates, AI engineers).
- **Hackpack (full details):** https://www.fetch.ai/events/hackathons/uk-ai-agent-hack-ep5-x-conduct-ai/hackpack • Bounty page: https://dorahacks.io/hackathon/bounty/1367

### 3.7 GCC & ETH Bounty — **1,000 USDT**
- **Sponsor:** GCC (Web3 public-goods funding initiative) with Ethereum Foundation.
- **Category 1 — Optimizing Agent Workflows for Public Funding Distribution:** agents that improve how public capital is sourced, evaluated, allocated, measured. Must define and justify metrics (impact estimates, counterfactual reasoning, milestone verification), not optimize game-able proxies. Build adoptable components: modular workflows, portable rubrics, standard interfaces, clear docs.
- **Category 2 — AI for Good:** agents for high-social-value/weak-commercial-incentive problems — privacy, digital rights, open science, civic transparency, environmental monitoring, access to information. Judged on depth of need, credibility of impact, fit of the agentic approach.
- **What they want:** agents that make real decisions (not chat demos), transparent allocation/impact reasoning, work that outlives the hackathon (reusable, forkable, open-source where possible).
- **More:** https://www.gccofficial.org/en • Bounty page: https://dorahacks.io/hackathon/bounty/1366

### 3.8 Kaspa Bounty — **1,000 USDC**
- **Sponsor:** Kaspa — fair-launched proof-of-work **BlockDAG** cryptocurrency (parallel block processing, fast confirmations, decentralized).
- **Challenge — "Build Programmable Agent Interactions with Kaspa":** a novel AI agent or agentic application using Kaspa as a fast, decentralized, **programmable layer for coordination, payments, commitments, or settlement — not merely a simple payment rail**. Single assistant, multi-agent system, dev infrastructure, or coordinating platform all valid, as long as Kaspa is core to the design.
- **Especially encouraged (not required):** upcoming capabilities such as **Covenants (incl. SilverScript)** for conditional payments, pact enforcement, escrow-like flows, on-chain coordination.
- **Support:** Kaspa channel on Discord https://discord.gg/jfQhu6NrC • Bounty page: https://dorahacks.io/hackathon/bounty/1369

---

## 4. API Credits & Free Resources

| Resource | What you get | How to claim | Gotchas |
|---|---|---|---|
| **OpenAI — ChatGPT Pro ("Codex boost")** | ChatGPT **Pro (20×) account** free — advertised as "1 month of Codex", in practice valid **until 7 July 2026** | Automatic: applied to the ChatGPT account whose email matches your **Luma registration email**. No email notification — just check your account | Required a ChatGPT account on that email **before 12:00 on Sun 28 Jun**. 530 got it, 134 missed it; organizers say nothing can be done now. Anecdote: applying a 20× boost to an already-subscribed account has ended badly with OpenAI support before — separate account was the safer play |
| **Venice AI — $50 API credits** | $50 free API credits | Sign up via https://venice.ai/settings/api and redeem code **`IMPERIAL50`** at the bottom of the API page (newer code issued 2 Jul: **`IMPERIAL50X`**) | If hit with a "buy Pro" screen: close it, log back in, scroll to bottom, enter the code. Free-API request form (earlier route): https://forms.gle/hNuZAVT8BPCCTAKd9 . Users reported flaky API reliability — raise issues in the Discord Venice channel |
| **Venice AI — Pro** | 1 month Venice Pro subscription | After claiming credits: profile (bottom-left) → Manage/Upgrade plan → Pro → add code **`IMPERIAL`** | |
| **Fetch.ai — ASI:One Pro + Agentverse Premium** | 1 month free of both | Code **`UKAIAGENTUKAIAGENTAV`** (from the hackpack) | |
| **BasedAI credits** | $3,800 worth of credits | This *is* the BasedAI bounty prize (not a general handout) | |
| **Cantor8 £50 cash** | £50 each for first 150 who complete the Canton onboarding task (see §3.3) | Do the lab task, submit the form | Payouts still pending as of 2 Jul — chase via Telegram group |
| **Cantor8 dinner £7,500 pool** | Cash prizes at the 28 Jun dinner; first 150 in-person participants guaranteed ≥£50 | In-person only, 28 Jun evening (Cantor8 Dinner & Co-working) | Same pool as the Learner Bounty |
| **OpenAI merch + job leads** | "Super exclusive" OpenAI merch, prizes, job opportunities | Regular **in-person** attendance at the daily Microsoft workshops | |
| **Co-founder intro** | 1 curated co-founder introduction + coffee chat paid for | https://1soul.ai/cofounder | |

---

## 5. Rules, Teams & Submission

### Teams
- **No hard team-size limit; solo allowed.** Organizers strongly recommend **1–4 people** (large teams must sort prize-split logistics themselves).
- Form teams any time — at the opening, during the week, via the Discord team-formation channel, or the WhatsApp chat.
- Attendance during the week is flexible; opening conference and Demo Day are the two days worth being on site. Remote building is fine.

### What to submit (general guide — all tracks **except CoralOS/SuperteamUK**)
Submit through DoraHacks: https://dorahacks.io/hackathon/2272/detail — **deadline 4 July 2026, end of Demo Day (23:59 on DoraHacks)**.
1. **Demo / pitch video** — ~5 minutes recommended (longer accepted)
2. **GitHub repository** — code, setup instructions, documentation
3. **Pitch deck** — problem, solution, product, technology, use case, demo flow

Checklist: project name • team name + members • video • repo link • deck • any deployment/demo/product link.

You pitch **once** and select all bounties you're submitting to on DoraHacks (max 10 per BUIDL). **CoralOS/SuperteamUK submissions go through Superteam Earn instead** (§3.2); Cantor8 has its own form (§3.3).

### Demo Day (4 July, Blackett LT1, 10:00–16:30)
- Sign-up form due **18:00, 3 July**: https://forms.gle/fnUe3vL24wyJo6pD7 ; selected presenters announced ~22:00 that night. Not everyone presents — non-presenters can still attend, network, get feedback, and submit on DoraHacks.
- **5 minutes max per team: ~3 min presentation + 2 min Q&A.** Early-stage decks fine.
- **Judges/investors:** LocalGlobe, Antler, an EWOR partner, plus other investors. Day opens with a fireside chat with **Simon, COO of EWOR**.
- **In-person pitching only** (no remote pitch), but remote teams can still submit on DoraHacks.

---

## 6. Schedule & Programming

### Opening Conference — Sat 28 Jun, CAGB 200 (venue 10:00–~22:00)
| Time | Session |
|---|---|
| 10:00–10:30 | Registration & arrival |
| 10:30–11:30 | Keynote — Henry Thompson/Uglow (Conduct AI co-founder & CTO) |
| 11:30–12:00 | Keynote — Sana Wajid (Fetch.ai CDO) |
| 12:00–13:00 | Keynote — Kwadwo Benko (Microsoft AI Transformation Lead) |
| 13:00–14:00 | Lunch & networking |
| 14:00–14:30 | Special keynote — Charlie Muirhead (CogX founder) |
| 14:30–15:00 | Keynote — Thomas Borrel (BasedAI) |
| 15:00–15:30 | Workshop — CoralOS + Superteam UK (Peter Carroll, founder) |
| 15:30–16:00 | Keynote — Bittensor (Etienne Leroy, Opentensor Foundation director) |
| 16:00–16:30 | Break |
| 16:30–17:00 | Keynote — Bart Zuber (Vega) |
| 17:00–17:30 | Special keynote — **Emad Mostaque** (ex-CEO, Stability AI) |
| 17:30–18:00 | Panel — "What to Build in the Age of AI?" (Laura Modiano/OpenAI, Henry Thompson, 10 Downing St representative) |
| 18:00–18:30 | Panel — "How to Build in the Age of AI?" (Harry Uglow — DEX co-founder & a16z scout, Paul Müller — EWOR partner & Adjust co-founder, Albert Phelps — tomoro.ai) |
| 18:30–19:00 | Special panel — GCC × Vega × Kaspa (Hazel Hu, Bart Zuber, Romain Billot) |
| 19:00+ | **Cantor8 Dinner & Co-working** — £7,500 prize pool, first 150 get ≥£50 |

### Hack week (BLKT 112, Blackett Laboratory unless noted)
- **Mon 29 Jun** (Luma: https://luma.com/euc9kb54): workshops from 12:00 — incl. BasedAI Q&A (~15:00) and **Microsoft for Startups: agentic framework** with Christoffer Noring (~17:00). Evening: **Conduct fireside** with CTO Henry (18:00, RSVP https://luma.com/64ed4no2) + pub networking.
- **Tue 30 Jun** (Luma: https://luma.com/i8l969er): 11–12 check-in; 12–13 SuperteamUK; 13–14 CoralOS; 15–16 AAG; 16–17 BasedAI; 17–18 Microsoft; 18:00+ co-working. Microsoft booth 13:00–18:00; workshops: Dan Austin "Taking AI Agents from Concept to Production" (13:00), William Ng/Ray Han/Najmah Mohamed "Building AI Agents with Microsoft Tools: Low-Code, Pro-Code & Enterprise Knowledge" (17:00). **Project Submission Guide released.**
- **Wed 1 Jul** (Luma: https://luma.com/d84r8rfn): 14–15 check-in; 15–16 MuleRun; 16–17 Kaspa; 17–18 Microsoft (Israa Ibrahim — "How AI is Actually Being Used in the Real World"); 18:30–20:00 co-working & mentor support. Mentors: CoralOS (founder Peter), BasedAI, Kaspa, Microsoft. Vega engineers (ex-Goldman/Google/Arm) on site ~15:00 for project feedback (not judging — no downside).
- **Thu 2 Jul** (Luma: https://luma.com/6fj8fvp6): Microsoft from 13:30 (booth 13:00–18:00); 16:00 Kaspa workshop; 17:00 Microsoft workshop (Carolina Braga — "Responsible AI"). Evening: **Conduct office visit** in Fitzrovia, 18:30, buffet + live project feedback, 40 spots: https://luma.com/4dffwgcf
- **Fri 3 Jul**: Microsoft workshop only; booth 17:00–20:00 (Andrea Ngoka-Williams). Final build/submission prep.
- **Sat 4 Jul**: Demo Day (see §5).

### Related side events
- **Tue 8 Jul** — Conduct × Legora engineers' evening in Shoreditch (fireside with Legora CTO Jake Lauritzen, arcade + drinks): https://luma.com/legora-kojr

---

## 7. Sponsors & Partners

| Tier | Sponsors |
|---|---|
| **Title** | Conduct AI |
| **Headline** | Microsoft, Fetch.ai |
| **Gold** | Bittensor, Venice.ai, BasedAI |
| **Silver** | Kaspa, Coral AI / CoralOS (Solana) |
| **Bronze** | GCC, Vega(-alts), MuleRun, Run |
| **Ecosystem & community partners** | OpenAI, Lovable, Hugging Face, Solana Foundation, Ethereum Foundation, Delphi Ventures, Concept Ventures, YZi Labs, AWS, ElevenLabs, Superteam UK, Cantor8 |

**Platform technologies tagged on DoraHacks:** OpenAI, Microsoft, Venice.ai, Bittensor, Solana, Imperial Blockchain.

Note: Vega sponsors the event but does **not** run or judge a track. Anthropic is not a sponsor (participants asked; organizers said "next time").

---

## 8. Strategy Notes (from the chat & docs)

- **Stack bounties:** one strong agent project can plausibly hit Conduct (enterprise process), Fetch.ai (register it on Agentverse/ASI:One), GCC (if public-good angle), Kaspa/CoralOS (if you add a payments/coordination layer) — a single BUIDL can apply to up to 10 bounties.
- **Money-weighted priorities:** Conduct £8,000 > CoralOS 5,000 (top prize 3,000 USDG) > BasedAI $3,800 credits > Bittensor $1,500 > Fetch/GCC/Kaspa $1,000 each. Cantor8's £50 is effectively free money for an afternoon of API work (payout reliability TBD).
- **Fetch.ai has the most prescriptive requirements** — Agentverse registration + Chat Protocol + ASI:One discoverability are hard gates; budget time for them.
- **Judges on Demo Day are VCs** (LocalGlobe, Antler, EWOR) — the pitch matters: problem → solution → wow moment, 3 minutes.
- **In-person presence** was repeatedly rewarded: merch, prizes, job conversations at the Microsoft booth, direct mentor access, and the Cantor8 dinner cash.
- Presentation slides from talks were shared in the chat (e.g. "Imperial — From AI user to AI Founder.pptx" in this folder's WhatsApp archive) and recordings exist for some Microsoft sessions (X streams).

---

## 9. All Key Links (quick reference)

- Event site / full agenda: https://www.aiagentslab.uk/hackathon/ep5
- DoraHacks hackathon: https://dorahacks.io/hackathon/2272/detail • Bounties: https://dorahacks.io/hackathon/2272/bounties
- Demo Day sign-up (due 3 Jul 18:00): https://forms.gle/fnUe3vL24wyJo6pD7
- Main Discord: https://discord.gg/mJNCdXUByr
- Conduct track: Discord https://discord.gg/xyrUj2XFv • WhatsApp https://chat.whatsapp.com/Ibn3YMi3uHeKeYUNNXu76Y?mode=gi_t
- CoralOS: brief https://xforce-decentralised-protocols.gitbook.io/solanaxcoralos/the-build/main-track-build-the-agent-economy • starter https://github.com/trilltino/solana_coralOS • submit https://superteam.fun/earn/listing/imperial-ai-agent-hackathon-build-the-agent-economy
- Fetch.ai hackpack: https://www.fetch.ai/events/hackathons/uk-ai-agent-hack-ep5-x-conduct-ai/hackpack
- Bittensor/Apex: https://apex.macrocosmos.ai/ • setup https://docs.macrocosmos.ai/subnets/subnet-1-apex/subnet-1-base-miner-setup
- Cantor8 task: https://docs.google.com/document/d/1fMDNbHDdH6JqfKjnTVPN3PbADJyh23v6k-hjZqEmy8Y • submit https://forms.gle/YMEr9rpZzq5fqxJDA
- Kaspa Discord: https://discord.gg/jfQhu6NrC • BasedAI Discord: https://discord.gg/xVhZHub8U
- GCC: https://www.gccofficial.org/en
- Venice API/credits: https://venice.ai/settings/api (codes: `IMPERIAL50` / `IMPERIAL50X` for $50 credits; `IMPERIAL` for 1-month Pro)
- Fetch codes: `UKAIAGENTUKAIAGENTAV` (1 month ASI:One Pro + Agentverse Premium)
