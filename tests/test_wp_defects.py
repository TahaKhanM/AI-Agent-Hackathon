"""WP-DEFECTS — §6 P0 items 2, 5, 6, 7, 8.

Each defect is pinned by a failing test first (TDD). Grouped by item so the report can
point at the exact guard for each.

ITEM 2 — agents.common.resolve_seed must NOT silently fall back to a committed dev seed in
         a public rails context (forgeable Watcher identity). It fails closed unless an
         explicit dev context is declared.
ITEM 5 — precedent.models proprietary escape hatch (PRECEDENT_DEV_MODELS) is refused unless
         PRECEDENT_ENV=dev is ALSO set — the demo/container path cannot enable it.
ITEM 6 — the kernel hash fingerprints the DECISION surface (extractor, policy + packs, ladder,
         orchestrator, retrieve, audit), not orphaned tour prose; GET /api/kernel-hash equals
         MANIFEST.json.
ITEM 7 — the fully-dead endpoints (/api/copy, /api/latency) 404 and the orphaned prose is gone;
         the skeptic probes endpoint lives on.
ITEM 8 — .env.example and docs/ops/services.md name the agent seed/address vars identically,
         matching agents.common.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from console.app import app

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture
def client():
    return TestClient(app)


# --------------------------------------------------------------------------- ITEM 2
# resolve_seed: env seed wins; a dev context may use the deterministic placeholder; a public
# context with an unset seed FAILS CLOSED rather than forging identity from a committed seed.

def test_resolve_seed_uses_env_seed_when_set(monkeypatch):
    from agents import common
    monkeypatch.setenv("WATCHER_AGENT_SEED", "prod-seed-xyz")
    monkeypatch.delenv("PRECEDENT_ENV", raising=False)
    monkeypatch.delenv("PRECEDENT_AGENTS_OFFLINE", raising=False)
    assert common.resolve_seed("watcher") == "prod-seed-xyz"


def test_resolve_seed_dev_flag_allows_placeholder(monkeypatch):
    from agents import common
    monkeypatch.delenv("WATCHER_AGENT_SEED", raising=False)
    monkeypatch.setenv("PRECEDENT_ENV", "dev")           # explicit dev flag
    monkeypatch.delenv("PRECEDENT_AGENTS_OFFLINE", raising=False)
    seed = common.resolve_seed("watcher")
    assert "local-dev" in seed                            # deterministic placeholder permitted


def test_resolve_seed_refuses_committed_seed_without_dev_context(monkeypatch):
    from agents import common
    monkeypatch.delenv("WATCHER_AGENT_SEED", raising=False)
    monkeypatch.delenv("PRECEDENT_ENV", raising=False)
    monkeypatch.delenv("PRECEDENT_AGENTS_OFFLINE", raising=False)  # mailbox live => public
    with pytest.raises(RuntimeError):
        common.resolve_seed("watcher")


def test_resolve_seed_offline_rehearsal_permits_placeholder(monkeypatch):
    # Offline (no mailbox => no public identity is registered) is a dev context.
    from agents import common
    monkeypatch.delenv("OPERATOR_AGENT_SEED", raising=False)
    monkeypatch.delenv("PRECEDENT_ENV", raising=False)
    monkeypatch.setenv("PRECEDENT_AGENTS_OFFLINE", "1")
    assert "local-dev" in common.resolve_seed("operator")


# --------------------------------------------------------------------------- ITEM 5
# The proprietary escape hatch requires BOTH PRECEDENT_DEV_MODELS=unsafe-dev-only AND
# PRECEDENT_ENV=dev. The demo/container path (no PRECEDENT_ENV=dev) can never enable it.

def test_proprietary_guard_not_bypassable_in_container(monkeypatch):
    from precedent import models
    monkeypatch.setenv("PRECEDENT_DEV_MODELS", "unsafe-dev-only")
    monkeypatch.delenv("PRECEDENT_ENV", raising=False)   # demo/container: not dev
    # The open-weight guard must STILL fire against a catalog missing the pinned ids.
    with pytest.raises(RuntimeError):
        models.assert_open_weight({})


def test_proprietary_bypass_requires_dev_env(monkeypatch):
    from precedent import models
    monkeypatch.setenv("PRECEDENT_DEV_MODELS", "unsafe-dev-only")
    monkeypatch.setenv("PRECEDENT_ENV", "dev")           # both set => bypass allowed
    # No raise even on an empty catalog.
    assert models.assert_open_weight({}) is None


# --------------------------------------------------------------------------- ITEM 6
# The kernel hash fingerprints the DECISION surface only.

DECISION_FILES = [
    "precedent/extractor.py",
    "precedent/policy.py",
    "precedent/policy_pack.yaml",
    "precedent/policy_pack_actions.yaml",
    "precedent/ladder.py",
    "precedent/orchestrator.py",
    "precedent_memory/retrieve.py",
    "precedent_memory/audit.py",
]


def test_kernel_surface_is_the_decision_files():
    from console import showcase
    files = set(showcase.KERNEL_SURFACE_FILES)
    for rel in DECISION_FILES:
        assert rel in files, f"decision file {rel} not in kernel surface"
        assert (REPO / rel).exists()
    # No VIEW/prose/template files may enter the decision-kernel fingerprint.
    assert all(not f.startswith("console/") for f in files)


def test_editing_tour_prose_does_not_move_kernel_hash(monkeypatch):
    from console import showcase
    h0 = showcase.compute_kernel_hash()
    # A stray edited caption on the VIEW surface must not move the decision-kernel hash.
    monkeypatch.setattr(showcase, "SOME_TOUR_CAPTION", "edited prose", raising=False)
    assert showcase.compute_kernel_hash() == h0


def test_kernel_hash_tracks_decision_file_bytes(tmp_path):
    from console import showcase
    (tmp_path / "precedent").mkdir()
    target = tmp_path / "precedent" / "policy.py"
    target.write_text("x = 1\n")
    h1 = showcase.compute_kernel_hash(files=["precedent/policy.py"], root=tmp_path)
    target.write_text("x = 2\n")
    h2 = showcase.compute_kernel_hash(files=["precedent/policy.py"], root=tmp_path)
    assert h1 != h2


def test_api_kernel_hash_equals_manifest(client):
    from console import showcase
    r = client.get("/api/kernel-hash")
    assert r.status_code == 200
    body = r.json()
    assert body["kernel_hash"] == showcase.manifest_expected_hash()
    assert body["matches_manifest"] is True


# --------------------------------------------------------------------------- ITEM 7
# Dead endpoints 404; the orphaned prose is gone; the skeptic probes endpoint lives on.

def test_dead_copy_endpoint_is_404(client):
    assert client.get("/api/copy").status_code == 404


def test_dead_latency_endpoint_is_404(client):
    assert client.get("/api/latency").status_code == 404


def test_probes_endpoint_still_lives(client):
    r = client.post("/api/probes/run", params={"n": 10})
    assert r.status_code == 200
    assert "leaks" in r.json()


def test_orphaned_prose_and_dead_helpers_removed():
    from console import showcase
    for sym in ("GUIDED_BEATS", "HUMAN_RUNBOOK", "PLAIN_ENGLISH", "TRACK_CALLOUTS",
                "AGENTS_STATIC", "AIRPLANE_BANNER", "HERO_LINE", "SCALE_STORY",
                "TOUR_TOOLTIP", "copy_bundle", "latency_snapshot", "_bench_permission_check"):
        assert not hasattr(showcase, sym), f"{sym} should be removed"


# --------------------------------------------------------------------------- ITEM 8
# .env.example and docs/ops/services.md agree on the agent seed/address variable NAMES,
# and both match the code's canonical set.

def test_env_example_and_services_md_agree_on_agent_var_names():
    from agents import common
    env_txt = (REPO / ".env.example").read_text()
    svc_txt = (REPO / "docs" / "ops" / "services.md").read_text()
    canonical = set(common.SEED_ENV.values()) | set(common.ADDRESS_ENV.values())
    assert canonical  # sanity
    for name in canonical:
        assert name in env_txt, f"{name} missing from .env.example"
        assert name in svc_txt, f"{name} missing from docs/ops/services.md"
    # The old, disagreeing names are gone from BOTH surfaces.
    for stale in ("FETCH_AGENT_SEED", "_AGENT_ADDRESS"):
        assert stale not in env_txt, f"stale {stale} still in .env.example"
        assert stale not in svc_txt, f"stale {stale} still in services.md"
