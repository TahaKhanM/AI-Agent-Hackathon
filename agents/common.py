"""Shared Fetch-rails helpers.  [owner T1, task T1-2 / T1-11]

Spec: 02 §3.4 + 05 §E.

RULE 4: agent seeds, mailbox keys and tokens are read from the environment by NAME —
never inlined. When an env seed is absent (local dev only), a clearly-labelled
DETERMINISTIC dev placeholder is used so an address is still stable across a handler
swap; the production address comes from the env seed and is NEVER committed.

RULE 1: this file names no model. The agents wrap the deterministic loop; the only
model calls happen inside precedent.venice via roles.
"""
from __future__ import annotations

import os
from datetime import UTC, datetime
from uuid import uuid4

from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
)

# Both badges are MANDATORY on every agent README (hackpack, verified live 3 Jul).
BADGE_INNOVATIONLAB = "![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)"
BADGE_HACKATHON = "![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)"
BADGES = f"{BADGE_INNOVATIONLAB}\n{BADGE_HACKATHON}"

# The Agentverse profile README (carries BOTH mandatory badges above). Each agent passes
# it as Agent(readme_path=README_PATH, publish_agent_details=True) so a plain re-run
# publishes the badges to that agent's profile (Fetch hard gate). Absolute path — stable
# regardless of the directory the agent is launched from.
README_PATH = os.path.join(os.path.dirname(__file__), "README.md")

# Env var names holding the STABLE production seeds (filled at registration; never committed).
SEED_ENV = {
    "watcher": "WATCHER_AGENT_SEED",
    "librarian": "LIBRARIAN_AGENT_SEED",
    "operator": "OPERATOR_AGENT_SEED",
}


def resolve_seed(name: str) -> str:
    """Stable seed for an agent. Production: the env var in SEED_ENV. Local dev: a
    deterministic, obviously-non-secret placeholder so the address is still stable
    across handler swaps (the real address is derived from the env seed)."""
    env = SEED_ENV.get(name)
    if env and os.environ.get(env):
        return os.environ[env]
    # Local-dev placeholder — NOT a registered secret; documented in agents/README.md.
    return f"precedent-{name}-local-dev-seed-set-{env or 'SEED'}-for-production"


def use_mailbox() -> bool:
    """Mailbox agents connect outbound to Agentverse (survive venue NAT). Disabled in
    tests/CI (no network) via PRECEDENT_AGENTS_OFFLINE=1."""
    return os.environ.get("PRECEDENT_AGENTS_OFFLINE") != "1"


def now() -> datetime:
    return datetime.now(UTC)


def text_of(msg: ChatMessage) -> str:
    """Concatenate the TextContent parts of an inbound ChatMessage."""
    return " ".join(c.text for c in msg.content if isinstance(c, TextContent)).strip()


def text_message(text: str) -> ChatMessage:
    """Build a one-part text ChatMessage (fresh id + timestamp)."""
    return ChatMessage(timestamp=now(), msg_id=uuid4(),
                       content=[TextContent(type="text", text=text)])


def ack_for(msg: ChatMessage) -> ChatAcknowledgement:
    return ChatAcknowledgement(timestamp=now(), acknowledged_msg_id=msg.msg_id)
