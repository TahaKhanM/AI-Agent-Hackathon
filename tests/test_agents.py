"""Fetch-rails construction tests — offline (PRECEDENT_AGENTS_OFFLINE=1, no mailbox).
Proves the Watcher is registerable: stable address from an env seed, Chat Protocol
included, both README badges present. Live registration is a human step.
"""
from __future__ import annotations

import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    monkeypatch.setenv("PRECEDENT_AGENTS_OFFLINE", "1")
    yield


def test_watcher_address_is_stable_from_env_seed(monkeypatch):
    monkeypatch.setenv("WATCHER_AGENT_SEED", "unit-test-stable-seed-value")
    from agents import watcher as w1
    a1 = w1.build_watcher()
    a2 = w1.build_watcher()
    assert a1.address == a2.address  # deterministic → survives a handler swap
    assert a1.address.startswith("agent")


def test_watcher_includes_chat_protocol(monkeypatch):
    monkeypatch.setenv("WATCHER_AGENT_SEED", "unit-test-stable-seed-value")
    from agents import watcher as w
    agent = w.build_watcher()
    manifests = agent.protocols  # dict of digest -> protocol
    assert manifests, "watcher must include at least one protocol"
    # The Chat Protocol spec name is present among included protocols.
    names = []
    for proto in manifests.values():
        name = getattr(proto, "name", None) or getattr(getattr(proto, "spec", None), "name", None)
        if name:
            names.append(name)
    assert any("chat" in (n or "").lower() for n in names), f"chat protocol missing: {names}"


def test_watcher_reply_swaps_without_changing_address(monkeypatch):
    monkeypatch.setenv("WATCHER_AGENT_SEED", "unit-test-stable-seed-value")
    from agents import watcher as w
    hello = w.build_watcher()
    custom = w.build_watcher(reply=lambda t: f"triaged: {t}")
    assert hello.address == custom.address  # same seed → same identity


def test_agents_readme_has_both_badges():
    readme = (REPO / "agents" / "README.md").read_text()
    assert "innovationlab" in readme
    assert "hackathon" in readme
