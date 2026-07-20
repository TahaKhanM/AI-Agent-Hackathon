/* Precedent landing bundle — WP-LANDING.
 *
 * Kernel-free, framework-free. It wires the two CTAs to the consent-gated, anonymous funnel
 * counter (reusing /api/funnel — the same day-90 kill-gate instrument the demo uses) and copies
 * the analyzer command to the clipboard. No inline handlers: one delegated click listener reads
 * data-act attributes. No visitor or session id ever leaves the browser — we send only the event
 * name, and ONLY after the visitor opts in. Consent defaults to OFF and is remembered locally.
 */
(function () {
  "use strict";

  function post(url, body) {
    try {
      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        keepalive: true,
      });
    } catch (e) { /* a counter that fails is a non-event */ }
  }

  // ---- privacy-preserving funnel (consent-gated, hosted-only) --------------
  function funnelConsent() {
    try { return localStorage.getItem("precedent_funnel_consent") === "yes"; }
    catch (e) { return false; }
  }
  function funnel(event) {
    if (!funnelConsent()) return;
    post("/api/funnel", { event: event, consent: true });
  }
  function setConsent(yes) {
    try { localStorage.setItem("precedent_funnel_consent", yes ? "yes" : "no"); }
    catch (e) { /* private mode: honour OFF */ }
    var el = document.getElementById("consent");
    if (el) el.remove();
  }
  function initConsent() {
    try { if (localStorage.getItem("precedent_funnel_consent") != null) return; }
    catch (e) { return; }
    var bar = document.createElement("div");
    bar.id = "consent";
    bar.className = "consent";
    bar.innerHTML =
      "<span>Count this visit anonymously? We record only that a step happened — never who you " +
      "are, never your session. It helps us decide if this earns its keep.</span>" +
      '<button data-act="consent-yes">Allow anonymous counts</button>' +
      '<button class="ghost" data-act="consent-no">No thanks</button>';
    document.body.appendChild(bar);
  }

  function copyCommand(btn) {
    var text = "precedent-analyze <export.csv>";
    var done = function () {
      var old = btn.textContent;
      btn.textContent = "Copied";
      setTimeout(function () { btn.textContent = old; }, 1400);
    };
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, done);
        return;
      }
    } catch (e) { /* fall through */ }
    done();
  }

  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-act]");
    if (!t) return;
    var act = t.getAttribute("data-act");
    if (act === "consent-yes") { setConsent(true); return; }
    if (act === "consent-no") { setConsent(false); return; }
    if (act === "cta-analyzer") { funnel("cta_click"); copyCommand(t); return; }
    if (act === "cta-book") { funnel("cta_click"); /* let the link/href proceed */ return; }
  });

  initConsent();
})();
