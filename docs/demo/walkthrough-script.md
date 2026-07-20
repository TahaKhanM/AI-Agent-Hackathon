# Precedent — the 60-second live walk-through

**You are walking the audience through the working product in your own voice — not reading a slide.**
The paragraphs in **quotes** are a complete, sayable script if your mind blanks; the one-line *why* under
each lets you say it your own way. Don't read the on-screen boxes out loud — talk to the room and let the
screen back you up. This is five clicks, top to bottom, in about a minute. Nothing is faked; every click
runs the real system.

The only two lines you must land cleanly are **"the second time is free"** and **"it knows what it's not
allowed to touch."** Say each slowly and let it sit for a beat.

---

## Before you start (a glance, off-stage)

Browser full-screen on **http://127.0.0.1:8000**. Check the top bar reads **8h 51m** (business-hours MTTR), the top-right says
**✓ matches manifest**, and you can see **INC-1, INC-2, INC-3**. Wi-Fi can be off. If it looks half-used
from a rehearsal: `make demo-reset && make sim &`, wait five seconds, refresh.

---

## Beat 1 — Something breaks, and it asks first *(click "Hold & review" on INC-1, then "Approve")*

*Why: a messy real ticket comes in, it finds your org's documented fix, and it stops for a human before
touching anything — showing the exact change and the exact undo.*

> "This is Precedent, live — a media company's incident console, all on this laptop. A messy ticket just
> landed; by hand this takes almost nine hours. Watch."

*Click **Hold & review** on INC-1. The approval panel opens.*

> "It found the documented fix, then stopped to ask me — here's the change, here's the undo. I approve."

*Click the green **Approve** button. It resolves.*

> "Resolved. Seconds, not hours."

---

## Beat 2 — Trust it once, and the second time is free *(click "Promote", then "Hold & review" on INC-2)*

*Why: the human promotes this class of fix to standing approval, so when that kind of fix recurs it
resolves with nobody at the keyboard — still fully audited.*

> "Now I tell it: this kind of fix, I trust it."

*Click **Promote to Standing Approval** on INC-1.*

> "So when it comes back —"

*Click **Hold & review** on INC-2. It resolves instantly, no gate.*

> "— nobody's at the keyboard. Fifteen seconds, done, fully recorded. The first time costs a minute; the
> second time is free."

*(Pause.)*

---

## Beat 3 — It refuses what it's not allowed to touch *(click "Hold & review" on INC-3)*

*Why: a restricted incident — the fix exists, but this operator isn't cleared. It refuses, routes it to
the right team, and that decision is made by a deterministic rulebook, not by the AI guessing.*

> "This one touches restricted content the operator isn't cleared for. The fix exists — but watch."

*Click **Hold & review** on INC-3. It refuses and names the owning team.*

> "It refuses, and routes it to the team that is allowed — decided by a deterministic rulebook, not an AI
> guessing. It knows what it's not allowed to touch."

*(Pause.)*

---

## Beat 4 — Close and hand back

> "Every fix your organisation has ever made, remembered and applied again — human in control, audited,
> reversible. That's Precedent. Back to you, [name]."

---

## Your muscle-memory line

Hold & review on INC-1 → **Approve** → **Promote** → Hold & review on INC-2 → Hold & review on INC-3.

## If it slips

If the page looks stuck, refresh once — your place is saved on the server. If one incident won't fire,
say the line and move on; the story survives a dropped click. If it's truly broken, say a calm "let me
reset that," run `make demo-reset && make sim &`, wait five seconds, refresh, resume from Beat 1.

## Numbers, said safely

Say **"almost nine hours by hand."** Don't quote a microsecond figure for the speed — if anyone asks, it's
**"thousands of times under the two-hundred-millisecond enterprise bar."** If you have 20 seconds spare
and want the proof, scroll to the green panel and click **Run 100 adversarial probes** ("zero got through")
and **Verify chain** ("the audit trail checks out") — otherwise skip it to stay inside the minute.
