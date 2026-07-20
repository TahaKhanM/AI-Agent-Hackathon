"""Evidence Pack v1 — per-incident, self-authenticating audit bundles.  [WP-PACK]

An Evidence Pack is a single per-incident bundle that lets an auditor confirm, OFFLINE and
with no secret key, that what Precedent did to a MediaCo object is exactly what the tamper-
evident audit log records — nothing added, dropped, reordered, or edited.

Each pack carries, for ONE incident:
  * the incident event + its deterministic structured extraction,
  * the retrieved precedent + provenance (documented-fix lineage + ACL/freshness state),
  * the gate decision + the deterministic policy-pack version,
  * the named human principal(s) — proposer and, if any, approver,
  * the typed execution transcript (the ordered audit narrative for the incident),
  * the verification result and the rollback record (if any),
  * the CHAIN PROOF: the full hash-chained audit log recomputable from GENESIS, plus the
    expected-length and tail-hash anchors that make TAIL TRUNCATION detectable, and
  * a sha256 MANIFEST over the pack's canonical bytes.

"Signed" here means SELF-AUTHENTICATING WITHOUT A SECRET KEY — see ``verify_pack.py`` and the
honest limitation documented there and in ``docs`` (registry delta): a bare hash chain plus a
sha256 manifest proves internal consistency and catches any isolated tamper, but the strongest
guarantee comes from checking the pack's tail-hash anchor against a tail hash re-derived
INDEPENDENTLY from the live audit database. Every pack states, verbatim, that it is
``evidence support, not a compliance determination``.

RULE 1/2: no model id and no LLM anywhere in this package — deterministic evidence plumbing.
RULE 3: the pack only ever REPORTS what the fail-closed pipeline already decided; it never
decides anything.
"""
from __future__ import annotations

from precedent_pack.builder import (
    DISCLAIMER,
    GENESIS_HASH,
    PACK_KIND,
    PACK_VERSION,
    build_pack,
    canonical_json,
    generate_demo_packs,
    manifest_digest,
    render_html,
    write_pack,
)

__all__ = [
    "DISCLAIMER",
    "GENESIS_HASH",
    "PACK_KIND",
    "PACK_VERSION",
    "build_pack",
    "canonical_json",
    "generate_demo_packs",
    "manifest_digest",
    "render_html",
    "write_pack",
]
