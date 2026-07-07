# Glossary — Terms a Judge Might Use Back at Us

> One crisp sentence per term, plus an optional analogy. Alphabetical. Skim once tonight; keep open during Q&A prep. Cross-check any number against `Prep/industry-primer.md` before quoting.

**ACL (Access Control List)** — The explicit list attached to a resource saying which identities may read or write it; our retrieval layer enforces ACLs *before* documents ever reach the model.
*Analogy: the guest list at the door — if you're not on it, you don't even see inside the room.*

**BXF / as-run** — BXF (SMPTE ST 2021, 2008) is the broadcast industry's XML standard for exchanging schedules, content metadata and **as-run logs** (the record of what actually aired) between traffic, automation and playout systems — in practice often implemented as file drops rather than real-time messaging.
*Analogy: the flight plan (schedule out) and the flight recorder (as-run back).*

**Deterministic policy engine** — A rules-based component whose allow/deny decision for a given input is always the same and never produced by a model — so permission enforcement is provable, not probabilistic.
*Analogy: a circuit breaker, not a security guard's judgement call.*

**Embedding** — A fixed-length vector of numbers representing a text's meaning, so "similar meaning" becomes "nearby in vector space" and can be searched mathematically.
*Analogy: GPS coordinates for ideas — nearby points are related topics.*

**EPG (Electronic Programme Guide)** — The viewer-facing channel/listings grid, fed from scheduling metadata; when upstream metadata desyncs, viewers see wrong listings and record the wrong shows — a classic silent media-ops failure.

**Fail-closed** — When a check errors out or times out, the system denies the action instead of allowing it; we fail closed on permissions and on fingerprint matching, accepting missed automation over a wrong execution.
*Analogy: a fire door that locks shut, not swings open, when the power dies.*

**Fingerprint fast-path** — Our shortcut: when the extractor confirms a new incident's fingerprint (its exact fix-class key) *equals* one with a standing-approved fix, execution can skip full retrieval-and-review — equality, never rank-1 similarity, is the bar.
*Analogy: a pharmacist refilling an existing prescription versus diagnosing a new patient.*

**FNR / FPR (False Negative Rate / False Positive Rate)** — FNR is the share of true matches we miss (lost automation); FPR is the share of non-matches we wrongly declare matches (wrong fix executed) — our extractor bench optimises FPR toward zero because a false positive spends trust we can't refund.
*Analogy: a smoke alarm that stays silent in a fire (FNR) vs one that screams at toast (FPR) — for us, silent-in-fire is annoying, screaming-at-toast is disqualifying, so we invert the usual tolerance.*

**Idempotent** — An operation that produces the same end-state whether run once or five times, which makes retries and re-runs safe; we prefer idempotent remediation steps so a retry can't double-apply a fix.
*Analogy: pressing a lift button repeatedly — the lift still comes once.*

**Issue security level** — A Jira mechanism that restricts *who can see an individual issue* (beyond project permissions); our demo uses a live issue-security scheme so the agent's retrieval visibly respects per-issue confidentiality.
*Analogy: a classification stamp on a single file inside an already-locked cabinet.*

**ITIL standard change** — A pre-authorised, low-risk, documented-procedure change (password reset, cert renewal, config toggle) that skips per-instance CAB approval by design — the legal on-ramp for agent execution: our standing approvals *are* standard-change templates.
*Analogy: a pre-approved expense category — no meeting needed for each coffee, just an audit trail.*

**KCS (Knowledge-Centered Service)** — The dominant methodology for capturing fixes as reusable knowledge articles *in the workflow* while tickets are solved; ServiceNow's own KCS adoption is the source of our 60%-repeats and 52%-faster numbers.
*Analogy: writing the recipe down while cooking, not from memory a week later.*

**KEDB (Known Error Database)** — ITIL's registry of problems with a documented root cause and workaround, which service desks are supposed to check *first*; in practice a manually curated graveyard — we make its contents executable.
*Analogy: the garage's binder of known faults for your car model — invaluable, if anyone opens it.*

**Lineage** — The recorded chain of where a piece of data or a decision came from (source document, version, transformations); every fix our agent proposes carries lineage back to the KB article and incident that justify it.
*Analogy: the chain of custody on courtroom evidence.*

**MSP / NOC** — A Managed Service Provider runs operations (e.g. playout) for many client companies under SLA contracts; a Network Operations Centre is the 24/7 room of humans watching alerts and following runbooks — MSP NOCs are our natural first buyer because automated incidents become pure margin.

**MTTR — business vs calendar hours (do not mix!)** — Mean Time To Resolve measured only within working hours (MetricNet's 8.85 **business** hours) versus wall-clock time including nights and weekends (our UCI corpus 18.2 **calendar** hours); the two corroborate each other but must never be averaged or swapped.
*Analogy: "three working days" vs "72 hours" — same courier, different promise.*

**Open-weight model** — A model whose weights are published so anyone can inspect, self-host or fine-tune it (our Venice-served models, with pinned IDs committed in `docs/compliance/`); contrast with closed APIs where the model is a black box you rent.

**P50 / P95 / P99** — Percentile latencies: the time under which 50%, 95%, 99% of requests complete; we quote P99 for enforcement latency because tail cases, not averages, are where guarantees break.
*Analogy: don't tell me the average queue time, tell me the worst queue the 99th customer saw.*

**RAG (Retrieval-Augmented Generation)** — Fetching relevant documents first and letting the model answer *grounded in them*, instead of from parametric memory; we go one step further — we retrieve **executed fixes with provenance**, not just text ("isn't this just RAG?" → retrieval is a component; the product is the execute-verify-learn loop).
*Analogy: an open-book exam versus reciting from memory.*

**SoD (Segregation of Duties)** — The SOX-era control that the identity requesting/performing a change cannot be the one approving it; our approval gate is the SoD control — agent proposes, a different human identity approves, immutably logged.
*Analogy: the person writing the cheque isn't the person signing it.*

**Standing approval** — A one-time human authorisation for a specific, well-evidenced fix class (ITIL standard-change style), letting future *exact-fingerprint* recurrences execute without per-incident sign-off — granted after verified successes, revocable in one click.
*Analogy: a standing order at the bank — set up once, runs on match, cancel any time.*

**Time-to-consistency** — How long after a permission or policy change until every enforcement point actually behaves per the new rule (we measured our Jira grant flips enforcing in ≤5s); the window in between is where stale-permission leaks live.
*Analogy: revoking a keycard vs waiting for every door in the building to hear about it.*

**TOCTOU (Time-Of-Check to Time-Of-Use)** — The race condition where permissions are checked at retrieval time but have changed by execution time; we re-check at the moment of action, not just at the moment of lookup.
*Analogy: your ticket was valid when you queued — the gate still scans it again at boarding.*

**uAgents / Agentverse / Chat Protocol / ASI:One** — The Fetch.ai stack: **uAgents** is the Python framework our agents are written in; **Agentverse** is the registry/hosting where they're discoverable; **Chat Protocol** is the standard message format agents speak; **ASI:One** is the agentic LLM front-end that can discover and converse with Agentverse agents — our hosted Watcher is registered there.
*Analogy: the programming language, the phone book, the shared language, and the switchboard operator.*

**Write-behind cache** — A cache that accepts writes immediately and flushes them to the backing store later; fast, but a hazard for permission data because the source of truth briefly lags — one reason we enforce against live state, fail-closed, rather than trusting cached ACLs.
*Analogy: jotting a sale in a notebook and updating the till at closing time — fine for stock counts, dangerous for door keys.*
