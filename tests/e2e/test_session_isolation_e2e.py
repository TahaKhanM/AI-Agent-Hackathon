"""WP-HOST-SESSION — two REAL concurrent browser sessions never interfere (Playwright e2e).

This is the browser-level companion to ``tests/test_session_isolation.py`` (the authoritative
pure-Python TestClient gate). Here two independent Chromium *contexts* — two real cookie jars,
i.e. two distinct ``precedent_sid`` sessions — drive the served console over HTTP and prove the
three shared-state axes a hosted visitor can observe stay per-session:

  * MEMORY / ladder — A promoting INC-1's class to STANDING never lifts B off L1;
  * MEMORY / audit  — A tampering its audit chain never breaks B's;
  * close ledger    — A resolving INC-1 leaves B's closed-count at 0, and B can still fix its own.

Driving is done with in-page ``fetch`` so the browser's own (HTTP-only) session cookie
authenticates every call exactly as the demo's front-end JS does — the true end-to-end path.

Guarded by the collection guard in ``tests/conftest.py``: absent Playwright/Chromium, the whole
``tests/e2e`` dir is dropped from collection, so a bare checkout stays green with zero skips.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.browser

PUBLISHER_CLASS = "publisher|PUB-4012|schedule_item"   # INC-1's class — cold-open L1 (slow-path)

_GET = """async (p) => {
  const r = await fetch(p);
  return {status: r.status, json: await r.json()};
}"""
_POST = """async ([p, body]) => {
  const opts = {method: 'POST', headers: {'content-type': 'application/json'}};
  if (body !== null) opts.body = JSON.stringify(body);
  const r = await fetch(p, opts);
  return {status: r.status, json: await r.json()};
}"""


def _get(page, path):
    return page.evaluate(_GET, path)["json"]


def _post(page, path, body=None):
    return page.evaluate(_POST, [path, body])["json"]


def _inc(state, incident_id):
    return next(i for i in state["incidents"] if i["incident_id"] == incident_id)


def _sid(context):
    for c in context.cookies():
        if c["name"] == "precedent_sid":
            return c["value"]
    return None


def _open(browser, base):
    """A fresh isolated browser context (its own cookie jar) with an established session."""
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto(base + "/", wait_until="load")   # middleware stamps this context's session cookie
    return ctx, page


def test_two_browser_sessions_are_isolated(browser, live_server):
    ctxA, A = _open(browser, live_server)
    ctxB, B = _open(browser, live_server)
    try:
        sidA, sidB = _sid(ctxA), _sid(ctxB)
        assert sidA and sidB and sidA != sidB, "each browser context must get its own session id"

        # B's cold open: INC-1 sits at L1, chain intact, nothing closed — asserted BEFORE A acts.
        sb0 = _get(B, "/api/state")
        assert _inc(sb0, "INC-1")["ladder_level"] == "L1"
        assert sb0["status"]["audit_chain"] == "intact"
        assert sb0["closed_count"] == 0

        # A drives the tour in ITS session: tamper the audit chain, EARN then promote INC-1's class
        # to STANDING (WP-DEMO §b: /api/promote is eligibility-gated — no raw-upsert bypass), then
        # resolve INC-1 through the zero-LLM fast path.
        assert _post(A, "/api/audit/tamper")["verified"] is False
        for _ in range(6):                          # verified recurrences on distinct targets
            if _post(A, "/api/recur", {"class_key": PUBLISHER_CLASS}).get("eligible"):
                break
        assert _post(A, "/api/promote", {"class_key": PUBLISHER_CLASS})["level"] == "STANDING"
        d = _post(A, "/api/drive/1")
        assert d["verified"] is True and d["outcome"] == "resolved"

        sa = _get(A, "/api/state")
        sb = _get(B, "/api/state")

        # ---- ladder axis: A's promote is A-only ----
        assert _inc(sa, "INC-1")["ladder_level"] == "STANDING"
        assert _inc(sb, "INC-1")["ladder_level"] == "L1", "A's promote must NOT leak to B"

        # ---- audit axis: A's tamper is A-only ----
        assert sa["status"]["audit_chain"] == "BROKEN"
        assert sb["status"]["audit_chain"] == "intact", "A's tamper must NOT leak to B"

        # ---- close ledger: A closed one; B still zero and can still fix its OWN INC-1 ----
        assert sa["closed_count"] == 1 and sb["closed_count"] == 0
        assert _post(B, "/api/drive/1")["verified"] is True, "B's world was never consumed by A"
        assert _get(B, "/api/state")["closed_count"] == 1

        # Airplane mode held: the fast path made zero model calls (slow paths fell back to canned).
        assert _get(A, "/api/model-calls")["model_calls"] == 0
    finally:
        ctxA.close()
        ctxB.close()


def test_held_approval_never_leaks_across_browser_sessions(browser, live_server):
    """The permanent cross-session regression: a held approval in A is invisible to B, and B
    cannot reach A's held plan — a fail-closed non-action (would FAIL under the old global map)."""
    ctxA, A = _open(browser, live_server)
    ctxB, B = _open(browser, live_server)
    try:
        held = _post(A, "/api/drive/1?hold=true")
        assert held["status"] == "pending_approval"
        assert len(_get(A, "/api/gate/pending")["pending"]) == 1

        # B sees nothing, and B "approving" INC-1 reaches no live plan — nothing executes.
        assert _get(B, "/api/gate/pending")["pending"] == []
        rb = _post(B, "/api/gate/1/decide?text=approve")
        assert rb["verdict"] == "approve" and rb["status"] == "no_live_approval"
        assert _get(B, "/api/state")["closed_count"] == 0

        # A's own hold is intact and A can still approve its OWN change.
        ra = _post(A, "/api/gate/1/decide?text=approve&principal=Priya")
        assert ra["verdict"] == "approve" and ra["verified"] is True
    finally:
        ctxA.close()
        ctxB.close()
