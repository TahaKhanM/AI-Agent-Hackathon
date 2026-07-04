"""Query-time inference prevention — deterministic, zero-LLM (P1.9, BasedAI bonus).

The conformance bench's `query inference` attack proves probes don't leak record *content*. This
module adds the missing half: detecting cross-permission-boundary INFERENCE at query time. Two
mechanisms, both pure and oracle-gradable (no model, no similarity):

(a) detect_probing — a per-principal denial-burst / probing-pattern detector over the existing
    hash-chained audit_log. A sliding window of retrieval_denied events from one principal above a
    threshold is flagged (a scripted collection/inference sweep) and throttled + audited.

(b) assess_bundle / bundle_cross_boundary — a bundle-level cross-boundary co-occurrence check
    BEFORE context assembly. A result set may not mix records whose effective policies imply
    disjoint restricted boundaries (their required-constraint sets share nothing) — co-locating
    them in one context is itself a cross-boundary inference channel, even for a principal cleared
    for both. Fail-closed: deny the bundle and audit the reason.

RULE 1/2: no model id, no LLM/model import — deterministic set algebra + a windowed COUNT over the
audit log. RULE 3: both mechanisms fail toward non-action (flag/deny), never toward disclosure.
"""
from __future__ import annotations

from datetime import timedelta

from precedent_memory import audit, db

# Defaults — a scripted sweep trips these; ordinary use (one or two denials) does not.
DEFAULT_WINDOW_SECONDS = 60
DEFAULT_DENIAL_THRESHOLD = 5


# --------------------------------------------------------------------------- #
# (a) per-principal denial-burst / probing-pattern detection
# --------------------------------------------------------------------------- #
def count_recent_denials(conn, principal_id: str, *, window_secs: int = DEFAULT_WINDOW_SECONDS,
                         now=None) -> int:
    """Number of retrieval_denied audit rows for `principal_id` within the sliding window."""
    cutoff = ((now or db.utcnow()) - timedelta(seconds=window_secs)).isoformat()
    row = conn.execute(
        "SELECT COUNT(*) c FROM audit_log WHERE event_type = 'retrieval_denied' "
        "AND actor = ? AND ts >= ?",
        (principal_id, cutoff),
    ).fetchone()
    return int(row["c"]) if row else 0


def detect_probing(conn, principal_id: str, *, window_secs: int = DEFAULT_WINDOW_SECONDS,
                   threshold: int = DEFAULT_DENIAL_THRESHOLD, now=None) -> dict:
    """Flag a probing pattern: threshold+ retrieval denials from one principal inside the window.
    On a flag, audit `probing_detected` and signal a throttle. Deterministic, zero-LLM.
    Returns {flagged, denials, throttle, window_secs, threshold}."""
    n = count_recent_denials(conn, principal_id, window_secs=window_secs, now=now)
    flagged = n >= threshold
    if flagged:
        audit.audit("probing_detected", conn=conn, actor=principal_id,
                    denials=n, window_secs=window_secs, threshold=threshold)
        conn.commit()
    return {"flagged": flagged, "denials": n, "throttle": flagged,
            "window_secs": window_secs, "threshold": threshold}


# --------------------------------------------------------------------------- #
# (b) bundle-level cross-boundary co-occurrence check (before context assembly)
# --------------------------------------------------------------------------- #
def bundle_cross_boundary(required_sets) -> bool:
    """True iff the bundle mixes DISJOINT restricted boundaries — two records whose required
    constraint-id sets are both non-empty and share nothing. Public records (empty set) are
    ignored. Pure set algebra, order-independent."""
    sets = [set(s) for s in required_sets if s]
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            if sets[i].isdisjoint(sets[j]):
                return True
    return False


def _required_ids(conn, record_id: int) -> set[int]:
    row = conn.execute(
        "SELECT required_bits, is_restricted FROM effective_policy WHERE record_id = ?",
        (record_id,),
    ).fetchone()
    if row is None or not row["is_restricted"]:
        return set()
    return set(db.bits_to_ids(db.blob_to_bits(row["required_bits"])))


def assess_bundle(conn, principal_id: str, record_ids) -> dict:
    """Cross-boundary co-occurrence check for a candidate result set, BEFORE it is assembled into a
    context. If the (restricted) records span disjoint boundaries, DENY the whole bundle
    (fail-closed) and audit `bundle_cross_boundary_denied`. Returns {allowed, reason, records}."""
    req_sets = [_required_ids(conn, rid) for rid in record_ids]
    if bundle_cross_boundary(req_sets):
        audit.audit("bundle_cross_boundary_denied", conn=conn, actor=principal_id,
                    records=len(list(record_ids)), reason="cross_boundary_cooccurrence")
        conn.commit()
        return {"allowed": False, "reason": "cross_boundary_cooccurrence",
                "records": len(req_sets)}
    return {"allowed": True, "reason": None, "records": len(req_sets)}
