"""WP-CONSOLE — the case-file console driven in a REAL browser (Playwright e2e).

The browser companion to the authoritative pure-Python gate (tests/test_product_console.py). It
drives the served ``/console`` page over HTTP in a real Chromium session and proves, end to end,
the claims a hosted visitor actually sees:

  * drive an incident via the API → its notarised record appears in the case file, with the
    pre-state snapshot + typed inverse shown BEFORE execution (no ``executed`` row yet);
  * APPROVE from the keyboard alone (Tab/focus → Enter) → it executes and the armed plan_hash
    binds to the executed plan_hash;
  * the SEALED pack verifies OFFLINE in the page (stamp = “VERIFIES OFFLINE”) and is downloadable;
  * REVOKE from the keyboard demotes a Standing class live (audited, named);
  * an injected verification failure auto-demotes the class live and files a rollback record.

Guarded by tests/conftest.py: absent Playwright/Chromium the whole tests/e2e dir is dropped from
collection, so a bare checkout stays green with zero skips. Airplane mode (unreachable Venice) is
set by the shared ``live_server`` fixture, so the model-call counter stays 0.
"""
from __future__ import annotations

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser


def _focus_control(page, selector):
    """Deterministically focus a control: wait until it is attached, visible AND enabled (a live
    SSE re-render can briefly detach/replace the node), THEN focus and assert focus via Playwright's
    auto-retrying ``expect`` — not a one-shot document.activeElement read that races the render."""
    control = page.locator(selector)
    expect(control).to_be_visible()
    expect(control).to_be_enabled()
    control.focus()
    expect(control).to_be_focused()
    return control

# in-page helpers (share the browser's own session cookie — the true end-to-end path)
_DRIVE_PROPOSE = """async ([iid, principal]) => {
  const incs = (await (await fetch('/api/incidents')).json()).incidents;
  const inc = incs.find(i => i.incident_id === iid);
  const pb = {incident_id: inc.incident_id, principal, raw_text: inc.raw_text,
              source: 'sim', observed_at: inc.observed_at, structured: inc.structured};
  const r = await fetch('/v1/gate/propose', {method:'POST',
    headers:{'content-type':'application/json'}, body: JSON.stringify(pb)});
  return await r.json();
}"""
_POST = """async ([p, body]) => {
  const r = await fetch(p, {method:'POST', headers:{'content-type':'application/json'},
    body: body == null ? null : JSON.stringify(body)});
  return await r.json();
}"""
_GET = """async (p) => await (await fetch(p)).json()"""


def _drive_propose(page, iid, principal="scheduling-ops"):
    return page.evaluate(_DRIVE_PROPOSE, [iid, principal])


def _post(page, path, body=None):
    return page.evaluate(_POST, [path, body])


def _get(page, path):
    return page.evaluate(_GET, path)


def _select(page, iid):
    page.locator(f'.pk-inc[data-inc="{iid}"]').click()


def test_product_console_e2e(live_server, browser):
    ctx = browser.new_context()
    page = ctx.new_page()
    try:
        page.goto(live_server + "/console")
        page.wait_for_selector(".pk-inc")                       # boot complete (3 incidents)
        assert page.locator(".pk-inc").count() == 3

        # ---- 1) drive the slow-path incident THROUGH THE UI (the drive button calls the gate
        #         API); the record must show the safety net BEFORE execution --------------------
        _select(page, "INC-1")
        page.locator("button:has-text('Drive INC-1')").click()  # → POST /v1/gate/propose
        page.wait_for_selector('[data-act="approve"]')          # needs-approval record + approve

        before = _get(page, "/api/case-file/INC-1")
        assert before["decision"]["decision"] == "needs-approval"
        assert before["safety_net"] is not None                 # rollback armed…
        assert before["safety_net"]["inverse"]["tool"] == "restore"
        assert before["safety_net"]["plan_hash_matches_execution"] is None   # …BEFORE any execution
        assert "executed" not in [e["event_type"] for e in before["execution_transcript"]]
        # the pivotal stage renders the armed-not-yet-executed state
        pivotal = page.locator(".stage-main.pivotal")
        assert "restore" in pivotal.inner_text()
        assert "not yet executed" in pivotal.inner_text()

        # ---- 2) APPROVE from the keyboard alone (Tab/focus → Enter) --------------------------
        _focus_control(page, '[data-act="approve"]')
        page.keyboard.press("Enter")
        page.wait_for_function(
            "() => { const t = document.querySelectorAll('.txtable tr.pick');"
            " return [...t].some(r => /executed/.test(r.innerText)); }")
        after = _get(page, "/api/case-file/INC-1")
        assert after["safety_net"]["plan_hash_matches_execution"] is True   # armed == executed hash
        assert after["verification"]["verified"] is True

        # ---- 3) the SEALED pack verifies OFFLINE in the page + is downloadable ---------------
        page.wait_for_function(
            "() => document.getElementById('verifier-stamp').textContent === 'VERIFIES OFFLINE'")
        assert page.locator('a.dlbtn[download$=".pack.json"]').count() == 1
        assert page.locator('a.dlbtn[download$=".pack.html"]').count() == 1
        assert _get(page, "/api/model-calls")["model_calls"] == 0            # zero-LLM, live

        # ---- 4) REVOKE a Standing class from the keyboard → demotes live, audited/named ------
        # WP-DEMO §b: the graduation class opens at L2 (no cold-open pre-promote). Earn STANDING on
        # this session via the REAL ladder (verified recurrences on distinct targets → promote).
        sched = "scheduler|SCH-DUP-002|schedule_item"
        for _ in range(4):
            if _post(page, "/api/recur", {"class_key": sched}).get("eligible"):
                break
        assert _post(page, "/api/promote", {"class_key": sched})["level"] == "STANDING"
        r2 = _drive_propose(page, "INC-2")                      # standing fast-path
        assert r2["decision"] == "allow-standing"
        _post(page, "/v1/gate/outcome", {"ref": r2["ref"]})
        _select(page, "INC-2")
        # Reachable by keyboard — wait for attached/visible/enabled/focused (deterministic; no
        # activeElement race against the live SSE re-render) before the first activation.
        revoke = _focus_control(page, '[data-act="revoke"]')
        revoke.press("Enter")                                   # …first activation ARMS (confirm)
        page.wait_for_selector('[data-act="revoke"][data-armed="1"]')
        page.locator('[data-act="revoke"]').press("Enter")      # second activation EXECUTES
        # the ladder re-renders live: the lit rung moves to L1 (durable state, not the flash note)
        page.wait_for_function(
            "() => { const r = document.querySelector('.rung.lit');"
            " return r && /L1/.test(r.textContent); }")
        sched = "scheduler|SCH-DUP-002|schedule_item"
        lad = {x["class_key"]: x for x in _get(page, "/api/ladder")["ladder"]}
        assert lad[sched]["level"] == "L1"                      # demoted live

        # after the revoke the class is L1 → a keyboard-reachable Promote control now exists
        _focus_control(page, '[data-act="promote"]')

        # ---- 5) an injected verification failure auto-demotes the class live -----------------
        # INC-1's class is at L2 after the earlier verified run; arm a fault, re-drive, approve.
        assert _post(page, "/api/sim/arm-flake")["ok"] is True
        r = _drive_propose(page, "INC-1")
        o = _post(page, "/v1/gate/outcome",
                  {"ref": r["ref"], "decision": "approve", "approver_principal": "ops-lead"})
        assert o["rolled_back"] is True and o["verified"] is False
        _select(page, "INC-1")
        # the rollback stage renders live in the reloaded case file
        page.wait_for_function(
            "() => [...document.querySelectorAll('.st-t')]"
            ".some(e => /Rollback record/.test(e.textContent))")
        pub = "publisher|PUB-4012|schedule_item"
        lad2 = {x["class_key"]: x for x in _get(page, "/api/ladder")["ladder"]}
        assert lad2[pub]["level"] == "L1", "a verification failure must auto-demote to L1 live"
        rec = _get(page, "/api/case-file/INC-1")
        assert rec["verification"]["outcome"] == "rolled_back"
        assert rec["rollback"] is not None
    finally:
        ctx.close()
