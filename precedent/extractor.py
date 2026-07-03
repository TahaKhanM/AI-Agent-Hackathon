"""Deterministic incident-class extractor + fingerprint.  [STUB — owner T1, task T1-4]

Spec: Idea/refinement/02-architecture-refinement.md §3.2.

RULE 2 (load-bearing): the fingerprint is computed from structured fields by regex +
canonicalisation tables over the incident payload and a known-error-code dictionary.
The FAST LLM may PROPOSE fields for messy free-text, but a class match counts only on
extractor-confirmed field equality — never semantic similarity. If deterministic
extraction fails, cap the incident at L0/L1 regardless of the class's ladder level and
put the reason in the trace ("error code not in known dictionary — escalating").
"""
from __future__ import annotations

import hashlib

from precedent.contracts import Extracted


def fingerprint(extracted: Extracted) -> str:
    """class_key = f"{service}|{error_code}|{target_object_type}" (canonicalised),
    fingerprint = sha256(class_key). This helper is safe to keep — it's the
    deterministic core; the extraction that produces `extracted` is the TODO below."""
    class_key = f"{extracted.service}|{extracted.error_code}|{extracted.target_object_type}".upper()
    return hashlib.sha256(class_key.encode()).hexdigest()


def extract(raw_text: str, structured: dict | None = None):
    """Return (Extracted | None, method). TODO T1-4: regex/canonicalisation over
    structured fields first; FAST-LLM proposal only for messy text; confirm equality."""
    raise NotImplementedError("T1-4: deterministic extractor — see 02 §3.2")
