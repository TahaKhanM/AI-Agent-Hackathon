"""WP-LANDING — the public landing shell at '/', the demo relocated to '/demo', and the
'Verify our claims' strip + security-posture stub.

These tests pin the routing contract (landing at /, demo at /demo), the instant first paint
(the above-the-fold content is fully server-rendered — no client fetch, and the render itself
opens no socket), the verify-strip links resolving, the two CTAs firing the consent-gated funnel
counter, copy-lint cleanliness of the shipped landing/security surfaces, and the honesty rules
(no 'Autonomous', 'Standing Approval' present).
"""
from __future__ import annotations

import socket
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from console.app import app

REPO = Path(__file__).resolve().parent.parent

POSITIONING = ("Your team built an agent that CAN act. Precedent makes it ALLOWED to act "
               "— and proves it.")


@pytest.fixture
def client():
    return TestClient(app)


# --------------------------------------------------------------------------- routing

def test_landing_served_at_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert POSITIONING in r.text
    # The landing is NOT the demo: it must not ship the demo narrative bundle.
    assert "/static/js/demo.js" not in r.text


def test_demo_relocated_to_slash_demo(client):
    r = client.get("/demo")
    assert r.status_code == 200
    # The demo shell links the narrative bundle and carries the ladder terminology.
    assert "/static/js/demo.js" in r.text
    js = client.get("/static/js/demo.js").text
    surface = r.text + "\n" + js
    assert "Standing Approval" in surface
    assert "autonomous" not in surface.lower()


# --------------------------------------------------------------- instant first paint

def test_landing_first_paint_is_fully_server_rendered(client):
    """All above-the-fold content is present in the single initial response — no client fetch
    is needed to paint the positioning line, the three planks or the demo button."""
    html = client.get("/").text
    assert POSITIONING in html
    # three lead wedge planks (plain-language anchors)
    assert "fingerprint" in html.lower()
    assert "ladder" in html.lower()
    assert "inverse" in html.lower() or "roll" in html.lower()
    # honesty banner + the demo CTA
    assert "honest" in html.lower()
    assert 'href="/demo"' in html


def test_landing_render_opens_no_socket(monkeypatch, client):
    """Instant-paint proxy: rendering '/' performs NO blocking external fetch. We forbid any
    socket connection for the duration of the request; a server-side fetch would raise."""
    def _boom(*a, **k):  # pragma: no cover - only hit on a regression
        raise AssertionError("landing render attempted a network connection")

    monkeypatch.setattr(socket.socket, "connect", _boom)
    r = client.get("/")
    assert r.status_code == 200
    assert POSITIONING in r.text


# ------------------------------------------------------------ verify-our-claims strip

def test_verify_strip_links_resolve(client):
    html = client.get("/").text
    # kernel-hash endpoint linked + the expected MANIFEST value shown, and it resolves.
    assert 'href="/api/kernel-hash"' in html
    from console import showcase
    expected = showcase.manifest_expected_hash()
    assert expected and expected in html
    kh = client.get("/api/kernel-hash")
    assert kh.status_code == 200
    assert kh.json()["manifest_expected"] == expected
    # CI badge is a NON-blocking browser image (not a server-side fetch).
    assert "ci.yml/badge.svg" in html
    # verify_pack.py is linked, and the security posture stub resolves.
    assert "verify_pack.py" in html
    assert 'href="/security"' in html
    assert client.get("/security").status_code == 200


def test_security_stub_has_real_content(client):
    html = client.get("/security").text
    low = html.lower()
    # dependency surface, no-secrets proof, one-slim-container argument — all real, no placeholders
    assert "dependenc" in low
    assert "secret" in low
    assert "container" in low
    # named real runtime deps + the no-secrets proof anchor
    assert "fastapi" in low
    assert ".env" in low
    # NO guillemet placeholders anywhere
    assert "‹" not in html and "›" not in html


# ------------------------------------------------------------------- the two CTAs

def test_landing_shows_analyzer_cta(client):
    html = client.get("/").text
    assert "precedent-analyze" in html
    assert "data never leaves your machine" in html.lower()


def test_landing_booking_cta_graceful_when_unset(monkeypatch, client):
    monkeypatch.delenv("PRECEDENT_BOOKING_URL", raising=False)
    html = client.get("/").text
    # A booking CTA exists; with the env var unset it is gracefully noted, not a broken link.
    assert "book" in html.lower()


def test_landing_booking_cta_uses_env_url(monkeypatch, client):
    monkeypatch.setenv("PRECEDENT_BOOKING_URL", "https://cal.example/precedent")
    html = client.get("/").text
    assert "https://cal.example/precedent" in html


def test_ctas_are_wired_for_funnel(client):
    """The two CTAs carry the delegated data-act hooks the landing bundle listens on to fire the
    consent-gated 'cta_click' funnel counter (no inline onclick)."""
    html = client.get("/").text
    assert "onclick" not in html
    assert "data-act" in html
    js = client.get("/static/js/landing.js").text
    assert "cta_click" in js
    assert "/api/funnel" in js


def test_cta_click_records_funnel_counter(monkeypatch, tmp_path, client):
    """The endpoint the CTA bundle posts to increments the anonymous aggregate — consent-gated."""
    monkeypatch.setenv("PRECEDENT_FUNNEL_DB", str(tmp_path / "funnel.db"))
    from console import funnel
    funnel.reset_for_test()
    # No consent => non-action.
    assert client.post("/api/funnel", json={"event": "cta_click"}).json()["recorded"] is False
    # Consent => counted.
    assert client.post("/api/funnel",
                       json={"event": "cta_click", "consent": True}).json()["recorded"] is True
    totals = client.get("/api/funnel/totals").json()["totals"]
    assert totals.get("cta_click") == 1
    funnel.reset_for_test()


# ----------------------------------------------------------------------- honesty

def test_landing_never_says_autonomous(client):
    html = client.get("/").text
    assert "Autonomous" not in html and "autonomous" not in html
    assert "Standing" in html  # the earned Standing-Approval ladder


def test_landing_surfaces_are_copy_lint_clean():
    """The shipped landing + security templates and the landing bundle pass the honesty linter."""
    from scripts.copy_lint import lint_text
    for rel in ("console/templates/landing.html",
                "console/templates/security.html",
                "console/static/js/landing.js"):
        text = (REPO / rel).read_text(encoding="utf-8")
        findings = lint_text(text, hosted=True)
        assert findings == [], f"{rel} copy-lint: {findings}"
