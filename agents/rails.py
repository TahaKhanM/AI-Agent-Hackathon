"""Real rail round-trips over PRECEDENT_PROTOCOL (P1.8).

Makes the multi-agent flow TRUE on the wire: the Watcher sends the loop's typed messages —
TriageMsg to the Librarian, PlanMsg to the Operator — via uAgents `ctx.send_and_receive`, and
each hop is timed so the chat footer / dry-run log carries REAL per-hop ms instead of a
hard-coded "(in-process)" string.

These are SHADOW round-trips: the in-process deterministic kernel already produced the
authoritative reply content (so demo latency + determinism are unchanged), and this only
enriches the provenance footer. It is fail-tolerant by construction — a rail hiccup, a slow
peer, or a down agent yields a shorter/empty hop trail, NEVER an exception and never a change to
the answer. RULE 1/2: no model id, no LLM here; it only moves already-decided typed data.
"""
from __future__ import annotations

import asyncio
import time

from agents.protocol import ResultMsg, RetrievalResultMsg

DEFAULT_TIMEOUT = 2.0


async def _timed_send(ctx, name: str, address: str, msg, response_type, timeout: float):
    """One rail hop: send `msg` to `address`, await the typed reply, return (reply, hop) where
    hop is {agent,address,ms} on success or None on any failure/timeout (fail-tolerant)."""
    t0 = time.monotonic()
    try:
        reply, _status = await asyncio.wait_for(
            ctx.send_and_receive(address, msg, response_type=response_type), timeout=timeout)
    except Exception:  # noqa: BLE001 — a rail hiccup only costs the hop, never the answer
        return None, None
    if reply is None:
        return None, None
    hop = {"agent": name, "address": address, "ms": int((time.monotonic() - t0) * 1000)}
    return reply, hop


async def shadow_hops(ctx, *, librarian_address: str, operator_address: str,
                      triage_msg, plan_msg=None, timeout: float = DEFAULT_TIMEOUT) -> list[dict]:
    """Drive the real Watcher→Librarian(→Operator) rail round-trip and return the hop trail
    ([{agent,address,ms}, ...]). Best-effort: the Librarian hop is attempted always; the Operator
    hop only when a `plan_msg` is supplied AND the Librarian permitted retrieval. Any failure
    truncates the trail rather than raising."""
    hops: list[dict] = []
    reply, hop = await _timed_send(ctx, "Librarian", librarian_address, triage_msg,
                                   RetrievalResultMsg, timeout)
    if hop is not None:
        hops.append(hop)
    if plan_msg is not None and reply is not None and getattr(reply, "permitted", False):
        _res, hop2 = await _timed_send(ctx, "Operator", operator_address, plan_msg,
                                       ResultMsg, timeout)
        if hop2 is not None:
            hops.append(hop2)
    return hops
