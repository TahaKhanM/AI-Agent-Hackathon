"""WP-REFACTOR — DOM-EQUIVALENCE guard.

The demo page was extracted out of a raw Python string (`console.app._PAGE`) into a
Jinja2 template + external CSS/JS. This test proves the extraction did not change the
rendered DOM: the `<body>` the browser receives today is structurally identical to the
`<body>` the old `_PAGE` string produced, modulo the ONE legitimate substitution the
refactor makes — the inline `<script>…</script>` becomes `<script src="…/demo.js">`
(mirrored in the head, where the inline `<style>` became an external stylesheet link).

The golden reference in tests/golden/demo_body.html was captured from the original
`_PAGE` body BEFORE `_PAGE` was deleted.
"""
from __future__ import annotations

import re
from pathlib import Path

from fastapi.testclient import TestClient

import console.app as app_mod

GOLDEN = Path(__file__).parent / "golden" / "demo_body.html"

_SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.DOTALL | re.IGNORECASE)
_BODY_RE = re.compile(r"<body\b[^>]*>(.*)</body>", re.DOTALL | re.IGNORECASE)
_HEAD_RE = re.compile(r"<head\b[^>]*>(.*)</head>", re.DOTALL | re.IGNORECASE)


def _body_inner(html: str) -> str:
    m = _BODY_RE.search(html)
    assert m, "no <body>…</body> found"
    return m.group(1)


def _normalise(fragment: str) -> str:
    """Drop <script> elements (the one legitimate inline→external substitution) and
    collapse insignificant inter-tag whitespace, so only the structural DOM remains."""
    fragment = _SCRIPT_RE.sub("", fragment)
    fragment = re.sub(r">\s+<", "><", fragment)
    return fragment.strip()


def test_rendered_body_matches_golden():
    client = TestClient(app_mod.app)
    resp = client.get("/")
    assert resp.status_code == 200

    golden_body = GOLDEN.read_text()
    rendered_body = _body_inner(resp.text)

    assert _normalise(rendered_body) == _normalise(golden_body), (
        "rendered <body> DOM diverged from the golden _PAGE body"
    )


def test_page_wires_external_assets():
    client = TestClient(app_mod.app)
    html = client.get("/").text

    head = _HEAD_RE.search(html)
    assert head, "no <head>…</head> found"
    assert '/static/css/precedent.css' in head.group(1), "head does not link the shared CSS"

    body = _body_inner(html)
    # The body must END with a classic script tag referencing the external demo.js.
    tail = _normalise(re.sub(_SCRIPT_RE, "<!--SCRIPT-->", body))  # keep everything else
    # Assert the external classic script is present just before </body>.
    assert re.search(
        r'<script\s+src="/static/js/demo\.js"\s*>\s*</script>\s*$',
        body.strip(),
    ), "body does not end with a <script src=/static/js/demo.js> tag"
    assert tail  # sanity: body is non-empty


def test_static_assets_and_favicon_resolve():
    client = TestClient(app_mod.app)
    for path in (
        "/static/css/precedent.css",
        "/static/js/demo.js",
        "/static/favicon.svg",
    ):
        assert client.get(path).status_code == 200, f"{path} did not return 200"


def test_page_no_raw_string_remains():
    # The extraction acceptance: no raw-string page literal survives in the module.
    assert not hasattr(app_mod, "_PAGE"), "_PAGE raw-string page still present in console.app"
