# Precedent — recorded-video voice-over script

> Paired shot-for-shot with `Prep/video/shot-list.md` (shots 0–8, ~4:15–4:30). Every number traces to
> `Prep/final-numbers.md` and obeys the shot-list's honesty guardrails. The **two memorable lines must
> survive any cut**: *"the second time is free"* and *"it knows what it's not allowed to touch."*
> Timings are DURATIONS. Read calm, unhurried; let the stopwatch do the drama.

## Shot 0 — Results-first cold open (0:14) — NO VO
Music/beat only over the three payoff frames (58s-vs-8h51m bar · 15s stopwatch · refusal card).

## Shot 1 — Cold-open narrative (0:15)
> "When a broadcaster goes off air, the fix is almost never new code — it's a documented admin
> procedure someone has run a hundred times before. The hard part isn't fixing it. It's finding the
> fix, and being allowed to run it."

## Shot 2 — The manual loop + the 8× time-lapse (0:25)
> "Today that loop is manual: a ticket comes in, someone searches the knowledge base, opens an admin
> console, waits in an approval queue, and resolves it."
>
> *(time-lapse begins — the clock spins 8×)*
>
> "The industry average to resolve one incident is **eight hours, fifty-one minutes** — MetricNet's
> business-hours benchmark. Most of that is queueing and lookup, not fixing. And more than sixty
> percent of incidents are repeats — the fix already exists; nobody can find it."

*(VO note: "8h51m" is the BUSINESS-hours figure. Never blend it with the corpus's 18-hour calendar
median — that number belongs to shot 7 with its own label.)*

## Shot 3 — Console home + provenance (0:15)
> "This is MediaCo — a simulated broadcaster, seeded with real public data: real UK schedules, real
> streaming catalogs, and a public log of a hundred-and-forty-one-thousand real incident events. The
> incident text is deliberately mangled — typos, vague symptoms, missing codes."

## Shot 4 — Incident 1: messy ticket → one human click (0:40)
> "A messy EPG-publish ticket arrives. Precedent triages it deterministically, retrieves the
> organisation's own documented fix, classifies the risk, and shows a plan with a rollback prepared
> before anything runs. A human clicks approve — once. Fixed in about a minute, and the Jira ticket
> closes itself."
>
> "Then the operations lead does something small and important: having watched it succeed, they
> **promote this fix class to Standing Approval** — a pre-approved standard change. Approval moves
> earlier in time; it never leaves the loop."

## Shot 5 — ★ ASI:One segment (80s — Fetch centrepiece, never shortened)
> "Here's the whole thing running inside an ASI:One conversation — no custom app. I report the same
> class of incident in chat. The Watcher agent, live on Agentverse, runs the loop over the Agent Chat
> Protocol: it retrieves the documented fix, and because this class is now under Standing Approval, it
> resolves it in about **fifteen seconds**, with nobody at the keyboard and **zero LLM calls** on the
> fast path. **The second time is free.**"
>
> "Notice two things. The authorising identity is the chat sender's own address — logged in a
> hash-chained audit trail, with the fix's full provenance. And when I report a rights-window
> incident, Precedent **refuses**: a documented fix exists, but this identity isn't permitted to read
> that restricted runbook — so it discloses only that one remediation is hidden and which team owns it,
> and routes a dossier. **It knows what it's not allowed to touch.**"

## Shot 6 — Recovery + refusal, back-to-back (0:25)
> "Control means recovering from failure too. Here a publish step fails verification mid-write — so the
> pre-written rollback fires automatically, the state is restored, and the class is **demoted** back a
> rung. Nothing is left half-done. And the refusal we just saw is the enterprise's real question
> answered: it's why they let an agent in the door."

## Shot 7 — Scale artifact (0:25 — squeeze to 15s if needed)
> "Under the hood, the permission check is a single deterministic lookup — benchmarked in BasedAI's own
> vocabulary against a **twenty-five-thousand-record** incident store: zero leaks across five thousand
> two hundred and nineteen deny-expected queries, six of six adversarial attacks defended, graded by an
> independent oracle. On the messy tickets: zero false fast-paths across a hundred mutations. In that
> corpus, ninety-four percent of incidents arrived with their fix already precedented — and still took
> a median of eighteen **calendar** hours to resolve by hand. Retrieval, not resolution, is the
> bottleneck."

*(VO note: "25k-record store" — never "141k events". 18 hours is CALENDAR — a separate label from
shot 2's 8h51m business figure.)*

## Shot 8 — Close + links (0:30)
> "Precedent remembers every fix your organisation has ever applied — risk-classified, approval-gated,
> audited, reversible — and applies it again. ServiceNow paid two-point-eight-five billion dollars for
> resolution memory. We're building the version that executes. **The second time is free.**"
>
> *(On-screen: repo · deck · Agentverse profiles · ASI:One shared chat — captured at registration.)*
