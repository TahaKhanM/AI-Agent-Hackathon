"""Console trace bridge.  [owner T1, task T1-10]

The orchestrator streams every hop through a `trace(step, detail, incident_id)` callable.
The console's LIVE trace panel is fed by POST /api/trace, which push_trace stores in an
IN-MEMORY list on the STATE singleton — so the live panel only lights up when T1 posts to
the SAME console process (hence the same-process launcher). The durable audit tail / feed
/ baseline panels light up from the shared DB regardless. These helpers provide both.
RULE 1/2: no model id, no LLM here.
"""
from __future__ import annotations


def in_process_trace(state):
    """Trace straight into the console STATE singleton (same process -> live panel)."""
    def _t(step: str, detail: str = "", incident_id: str | None = None) -> None:
        try:
            state.push_trace({"step": step, "detail": detail, "incident_id": incident_id})
        except Exception:  # noqa: BLE001 — tracing is best-effort, never breaks the loop
            pass
    return _t


def http_trace(client_or_base_url):
    """Trace over HTTP to a console on another process. Accepts an httpx.Client-like
    object or a base URL string. Best-effort: a console outage never breaks the loop."""
    import httpx
    client = (client_or_base_url if hasattr(client_or_base_url, "post")
              else httpx.Client(base_url=client_or_base_url, timeout=2.0))

    def _t(step: str, detail: str = "", incident_id: str | None = None) -> None:
        try:
            client.post("/api/trace", json={"step": step, "detail": detail,
                                            "incident_id": incident_id})
        except Exception:  # noqa: BLE001
            pass
    return _t
