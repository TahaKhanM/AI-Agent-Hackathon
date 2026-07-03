"""Deterministic retrieval path — A enforced via B.  [STUB — owner T2, task T2-1]

Spec: Idea/refinement/02-architecture-refinement.md §2.4.

RULE 2 — THIS FILE MUST HAVE ZERO LLM IMPORTS. permitted() is one bitmask AND over an
indexed effective_policy row (sub-microsecond, the P99 story). Candidate generation
(vector/BM25) may surface a record internally, but NOTHING is returned — not a snippet,
not a title — without permitted() passing on the record row.

RULE 3 — fail-closed: if the record is restricted AND its ACL freshness is uncertain
(fallback mode / stale), DENY. A stale cache narrows access, never widens it.

TOCTOU: check + fetch happen in one SQLite transaction; compare the fetched row's
policy_version to the checked one; mismatch -> recheck.
"""
from __future__ import annotations


def stale(min_source_freshness: str, mode: str) -> bool:
    """TODO T2-1: live mode -> older than 60s is stale; fallback mode -> always treat
    restricted records as stale (deny). See §2.5."""
    raise NotImplementedError("T2-1: freshness rule — see 02 §2.5")


def permitted(principal, record_policy, mode) -> bool:
    """TODO T2-1: fail-closed bitmask AND. If record_policy.is_restricted and
    stale(...): audit('retrieval_denied', reason='acl_freshness_uncertain'); return
    False. Else return bits_superset(principal.grant_bits, record_policy.required_bits).
    NO LLM anywhere in this function."""
    raise NotImplementedError("T2-1: permitted() — see 02 §2.4")


def retrieve(principal, query, mode="live"):
    """TODO T2-1: candidate-generate, then return only records where permitted() passes,
    in one transaction. Surface denied_count + owning team only (documented disclosure)."""
    raise NotImplementedError("T2-1: retrieve() — see 02 §2.4")
