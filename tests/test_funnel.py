"""Privacy-preserving funnel counters (WP-DEMO §d).

The funnel is the day-90 kill-gate instrument. These tests lock its two hard promises:
  1. It records NOTHING that identifies a visitor or a session — the store has only
     (day, event, count); there is structurally no PII/session column.
  2. It records ONLY after explicit consent — a no-consent call is a fail-closed non-action.

Plus: the analyzer (which runs on a customer's own machine over their own tickets) must never
import the funnel — a customer-side surface emits no telemetry.
"""
from __future__ import annotations

import pathlib

import pytest
from fastapi.testclient import TestClient

from console import funnel


@pytest.fixture(autouse=True)
def _tmp_funnel(tmp_path, monkeypatch):
    monkeypatch.setenv("PRECEDENT_FUNNEL_DB", str(tmp_path / "funnel.db"))
    funnel.reset_for_test()
    yield
    funnel.reset_for_test()


# --------------------------------------------------------------------------- #
# consent gating
# --------------------------------------------------------------------------- #
def test_no_consent_records_nothing():
    r = funnel.record("express_complete", consent=False)
    assert r["recorded"] is False
    assert funnel.totals()["totals"] == {}


def test_consent_records_and_accumulates():
    assert funnel.record("express_complete", consent=True)["recorded"] is True
    funnel.record("express_complete", consent=True)
    funnel.record("pack_download", consent=True)
    t = funnel.totals()["totals"]
    assert t == {"express_complete": 2, "pack_download": 1}


def test_unknown_event_is_a_non_action():
    r = funnel.record("visitor:alice@example.com", consent=True)
    assert r["recorded"] is False and r["reason"] == "unknown_event"
    assert funnel.totals()["totals"] == {}


# --------------------------------------------------------------------------- #
# no PII / no session id — by construction
# --------------------------------------------------------------------------- #
def test_store_schema_has_no_pii_or_session_column():
    funnel.record("cta_click", consent=True)
    conn = funnel._conn()
    cols = {row["name"] for row in conn.execute("PRAGMA table_info(funnel_daily)").fetchall()}
    assert cols == {"day", "event", "count"}
    # No column could ever hold a session id, cookie, ip, or fine timestamp.
    for banned in ("session", "sid", "cookie", "ip", "visitor", "ua", "time", "ts"):
        assert not any(banned in c for c in cols)


def test_date_is_coarse_day_granularity():
    # A day string (YYYY-MM-DD), never a per-second timestamp that could re-identify a visitor.
    day = funnel.record("express_complete", consent=True)["day"]
    assert len(day) == 10 and day.count("-") == 2


# --------------------------------------------------------------------------- #
# endpoint wiring (consent flows through the HTTP body)
# --------------------------------------------------------------------------- #
@pytest.fixture
def client():
    from console.app import app
    with TestClient(app) as c:
        yield c


def test_endpoint_requires_consent(client):
    no_body = client.post("/api/funnel", json={"event": "express_complete"}).json()
    assert no_body["recorded"] is False
    explicit = client.post(
        "/api/funnel", json={"event": "express_complete", "consent": False}).json()
    assert explicit["recorded"] is False
    assert client.get("/api/funnel/totals").json()["totals"] == {}


def test_endpoint_records_with_consent(client):
    r = client.post("/api/funnel", json={"event": "pack_download", "consent": True}).json()
    assert r["recorded"] is True and r["event"] == "pack_download"
    assert client.get("/api/funnel/totals").json()["totals"] == {"pack_download": 1}


# --------------------------------------------------------------------------- #
# the analyzer must not import the funnel (no customer-side telemetry)
# --------------------------------------------------------------------------- #
def test_analyzer_never_imports_funnel():
    root = pathlib.Path(__file__).resolve().parent.parent / "precedent_analyzer"
    for py in root.rglob("*.py"):
        for line in py.read_text().splitlines():
            s = line.strip()
            if s.startswith("#"):
                continue  # a comment/docstring may DOCUMENT the boundary ("no funnel, by design")
            assert not ("import" in s and "funnel" in s), \
                f"{py} imports the funnel — analyzer must emit no telemetry"
