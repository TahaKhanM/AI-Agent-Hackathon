"""Tests for the MediaCo sim (sim/).

Proves: loader counts land in the required bands; the real data's messiness (null
metadata, duplicate titles) is preserved; the three demo incidents return the canonical
structured classes and BYTE-IDENTICAL payloads across calls; object snapshot roundtrip;
execute -> healthy; verify true after a clean execute; restore rolls back; the one-shot
flake fails exactly one verification then recovers; and the incident payload builds the
frozen precedent.contracts types.

Each test uses a fresh temp DB (via PRECEDENT_SIM_DB) so runs are isolated and the loader
counts are asserted on a clean build.
"""
from __future__ import annotations

import importlib
import json

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """A TestClient backed by a fresh sim DB, rebuilt on app startup."""
    db_file = tmp_path / "sim_test.db"
    monkeypatch.setenv("PRECEDENT_SIM_DB", str(db_file))

    # Re-import the sim modules so the DB-path env var is picked up cleanly per test.
    import sim.app as app_module

    importlib.reload(app_module)
    with TestClient(app_module.app) as c:  # triggers startup -> build_sim
        yield c


# --------------------------------------------------------------------------- #
# Loader counts + messiness preservation
# --------------------------------------------------------------------------- #
def test_loader_counts_in_required_bands(client):
    counts = client.get("/health").json()["counts"]
    assert 6 <= counts["channel"] <= 10
    assert counts["schedule_slot"] > 50
    assert counts["rights_record"] > 100
    assert counts["kb_article"] == 10


def test_messiness_preserved_null_and_duplicate(client):
    # A REAL null episode summary survives (not backfilled at load time).
    slots = client.get("/sim/scheduler/slots").json()
    assert any(s["summary"] is None for s in slots), "expected a null episode summary"
    # A REAL null in a numeric metadata field survives too (null runtime).
    assert any(s["runtime"] is None for s in slots), "expected a null runtime"

    # A duplicate title survives across the loaded rights catalog (cross-catalog dup).
    rights = client.get("/sim/rights/records").json()
    titles = [r["title"] for r in rights]
    seen: set[str] = set()
    dups = {t for t in titles if t in seen or seen.add(t)}
    assert dups, "expected at least one duplicate rights title"


def test_kb_articles_include_acl_and_stale_for_browsing(client):
    """kb_article carries acl/stale for browsing/provenance — but the sim never enforces
    it (no permission logic here)."""
    articles = client.get("/sim/kb/articles").json()
    assert len(articles) == 10
    assert any(a["acl"] != "public" for a in articles)  # rights-ops-only articles exist
    assert any(a["stale"] for a in articles)             # at least one stale runbook


# --------------------------------------------------------------------------- #
# Incident fixtures — canonical classes + byte-identical replay
# --------------------------------------------------------------------------- #
CANONICAL = {
    1: {"service": "publisher", "error_code": "PUB-4012", "target_object_type": "schedule_item"},
    2: {"service": "scheduler", "error_code": "SCH-DUP-002", "target_object_type": "schedule_item"},
    3: {"service": "rights", "error_code": "RGT-EXCL-009", "target_object_type": "vod_item"},
}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_incident_structured_class_is_canonical(client, n):
    payload = client.get(f"/sim/incident/{n}").json()
    assert payload["incident_id"] == f"INC-{n}"
    assert payload["source"] == "sim"
    structured = payload["structured"]
    for key, value in CANONICAL[n].items():
        assert structured[key] == value
    assert structured["object_id"]  # a concrete object is referenced


@pytest.mark.parametrize("n", [1, 2, 3])
def test_incident_payload_byte_identical_across_calls(client, n):
    a = client.get(f"/sim/incident/{n}").json()
    b = client.get(f"/sim/incident/{n}").json()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_incident1_reads_like_garbled_9pm_ticket(client):
    raw = client.get("/sim/incident/1").json()["raw_text"].lower()
    assert "blank" in raw
    # "9pm" appears colloquially ("9pm", "9 o clock", "nine pm", "the 9pm slot").
    assert any(tok in raw for tok in ("9pm", "9 o clock", "9 o'clock", "nine pm"))


# --------------------------------------------------------------------------- #
# Object snapshot roundtrip + execute -> healthy + verify + restore
# --------------------------------------------------------------------------- #
def test_object_snapshot_roundtrip_and_execute_verify_restore(client):
    inc = client.get("/sim/incident/1").json()
    oid = inc["structured"]["object_id"]

    before = client.get(f"/sim/object/publisher/schedule_item/{oid}").json()
    assert before["healthy"] is False
    assert before["fields"]["missing_metadata"] == 1
    snapshot = dict(before["fields"])  # capture for rollback

    # execute -> object becomes healthy
    ex = client.post(
        "/sim/execute",
        json={"tool": "republish_epg", "args": {"schedule_slot_id": int(oid)}},
    ).json()
    assert ex["ok"] is True
    assert ex["object_ref"]["object_id"] == oid
    after = client.get(f"/sim/object/publisher/schedule_item/{oid}").json()
    assert after["healthy"] is True

    # verify true after a clean execute
    v = client.post(
        "/sim/verify",
        json={"service": "publisher", "object_type": "schedule_item", "object_id": oid},
    ).json()
    assert v["verified"] is True

    # restore rolls the object back to the captured (unhealthy) snapshot
    r = client.post(
        "/sim/restore",
        json={
            "service": "publisher",
            "object_type": "schedule_item",
            "object_id": oid,
            "snapshot": snapshot,
        },
    ).json()
    assert r["ok"] is True
    restored = client.get(f"/sim/object/publisher/schedule_item/{oid}").json()
    assert restored["healthy"] is False


def test_dedupe_and_takedown_reach_healthy(client):
    # INC-2 (scheduler / dedupe_slot)
    o2 = client.get("/sim/incident/2").json()["structured"]["object_id"]
    assert client.get(f"/sim/object/scheduler/schedule_item/{o2}").json()["healthy"] is False
    client.post("/sim/execute", json={"tool": "dedupe_slot", "args": {"schedule_slot_id": int(o2)}})
    assert client.get(f"/sim/object/scheduler/schedule_item/{o2}").json()["healthy"] is True

    # INC-3 (rights / rights_takedown)
    o3 = client.get("/sim/incident/3").json()["structured"]["object_id"]
    assert client.get(f"/sim/object/rights/vod_item/{o3}").json()["healthy"] is False
    client.post("/sim/execute", json={"tool": "rights_takedown", "args": {"vod_item_id": int(o3)}})
    assert client.get(f"/sim/object/rights/vod_item/{o3}").json()["healthy"] is True


# --------------------------------------------------------------------------- #
# One-shot flake semantics
# --------------------------------------------------------------------------- #
def test_flake_once_fails_exactly_once_then_recovers(client):
    # Make INC-3's object healthy so verification would otherwise pass.
    o3 = client.get("/sim/incident/3").json()["structured"]["object_id"]
    client.post("/sim/execute", json={"tool": "rights_takedown", "args": {"vod_item_id": int(o3)}})
    ref = {"service": "rights", "object_type": "vod_item", "object_id": o3}

    armed = client.post("/sim/publisher/flake?once=true").json()
    assert armed["armed"] is True

    first = client.post("/sim/verify", json=ref).json()
    assert first["verified"] is False  # the one-shot flake fires

    second = client.post("/sim/verify", json=ref).json()
    assert second["verified"] is True  # disarmed — recovers


# --------------------------------------------------------------------------- #
# Contract construction — incident payload builds the frozen precedent types
# --------------------------------------------------------------------------- #
def test_incident_payload_builds_precedent_contracts(client):
    from precedent.contracts import Extracted, IncidentEvent

    payload = client.get("/sim/incident/1").json()
    event = IncidentEvent(
        incident_id=payload["incident_id"],
        raw_text=payload["raw_text"],
        source=payload["source"],
        observed_at=payload["observed_at"],
    )
    assert event.source == "sim"
    assert event.incident_id == "INC-1"

    structured = payload["structured"]
    extracted = Extracted(
        service=structured["service"],
        error_code=structured["error_code"],
        target_object_type=structured["target_object_type"],
    )
    assert extracted.service == "publisher"
    assert extracted.error_code == "PUB-4012"
    assert extracted.target_object_type == "schedule_item"


def test_reset_is_idempotent_and_fast(client, monkeypatch):
    """reset() DROP+rebuilds; a second build_sim is a no-op (counts stable)."""
    import time

    from sim import core, db

    conn = db.connect()
    try:
        t0 = time.monotonic()
        core.reset(conn)
        elapsed = time.monotonic() - t0
        assert elapsed < 30
        first = db.counts(conn)
        core.build_sim(conn)  # idempotent no-op on a seeded DB
        assert db.counts(conn) == first
    finally:
        conn.close()
