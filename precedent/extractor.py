"""Deterministic incident-class extractor + fingerprint.  [owner T1, task T1-7]

Spec: Idea/refinement/02-architecture-refinement.md §3.2.

RULE 2 (load-bearing): the class fields are computed DETERMINISTICALLY first — a known
error-code dictionary + canonicalisation over the structured payload (and an exact
known-code match in the free text). Only if that fails does the FAST LLM PROPOSE fields
for messy tickets, and that proposal is marked `llm_proposed` — NOT class-confirmed.
Nothing the LLM outputs can be treated as a deterministic class: only a code present in
the structured payload or matched EXACTLY (no typo) in the text yields `deterministic`.
A failed deterministic extract is capped at L0/L1 downstream (policy.assess), so the LLM
can never unlock the standing-approval fast-path. Never semantic similarity.
"""
from __future__ import annotations

import hashlib
import re

from precedent.contracts import Extracted

# --------------------------------------------------------------------------- #
# Known-error-code dictionary: CODE -> (service, target_object_type). This is the
# deterministic authority — the code decides the class, canonicalised. It MUST stay in
# sync with the sim's incident codes and the KB error_codes (T1 owns both).
# --------------------------------------------------------------------------- #
KNOWN_CODES: dict[str, tuple[str, str]] = {
    "PUB-4012": ("publisher", "schedule_item"),      # KB-0001 / demo INC-1
    "SCH-DUP-002": ("scheduler", "schedule_item"),   # demo INC-2 (fast-path repeat)
    "RGT-EXCL-009": ("rights", "vod_item"),          # KB-0005 / demo INC-3
    "SCH-DST-118": ("scheduler", "schedule_item"),   # KB-0002
    "SCH-OVL-204": ("scheduler", "schedule_item"),   # KB-0003
    "RGT-WIN-014": ("rights", "vod_item"),           # KB-0004
    "EPT-BOOT-291": ("endpoint", "endpoint_host"),   # KB-0006
    "PUB-JOB-503": ("publisher", "publish_job"),     # KB-0007
    "PUB-SUB-410": ("publisher", "subtitle_asset"),  # KB-0008 (stale)
    "SCH-ASR-330": ("scheduler", "as_run_log"),      # KB-0009 (stale)
    "AUTH-CAP-900": ("auth", "auth_service"),        # KB-0010 (escalate)
}

# Canonicalisation of common service/object synonyms in structured payloads (never used
# to GUESS from prose — only to normalise an explicitly-provided structured field).
_SERVICE_CANON = {
    "epg": "publisher", "publish": "publisher", "publisher": "publisher",
    "scheduler": "scheduler", "schedule": "scheduler", "scheduling": "scheduler",
    "rights": "rights", "licensing": "rights",
    "endpoint": "endpoint", "auth": "auth", "authentication": "auth",
}

# Match an EXACT well-formed code token (a typo like "PUB-4O12" deliberately will NOT
# match, so a garbled ticket falls through to the LLM-proposed path and is capped).
_CODE_RE = re.compile(r"\b([A-Z]{3,4}-[A-Z]{0,4}-?\d{2,4})\b")


def fingerprint(extracted: Extracted) -> str:
    """class_key = f"{service}|{error_code}|{target_object_type}" (upper), fingerprint =
    sha256(class_key). Deterministic core — safe to key the fast-path on."""
    class_key = f"{extracted.service}|{extracted.error_code}|{extracted.target_object_type}".upper()
    return hashlib.sha256(class_key.encode()).hexdigest()


def class_key_of(extracted: Extracted) -> str:
    """The human-readable class_key (matches the console/registry tokens)."""
    return f"{extracted.service}|{extracted.error_code}|{extracted.target_object_type}"


def _norm_code(code: str | None) -> str | None:
    if not code:
        return None
    c = code.strip().upper()
    return c if c in KNOWN_CODES else None


def _deterministic(raw_text: str, structured: dict | None) -> Extracted | None:
    """Resolve the class from a KNOWN code only. Priority: structured.error_code, then an
    exact known code found in the free text. The code's canonical (service, object_type)
    always wins — a code is the deterministic authority."""
    # 1) explicit structured error_code
    if structured:
        code = _norm_code(structured.get("error_code"))
        if code:
            service, tot = KNOWN_CODES[code]
            # honour an explicit structured target_object_type/service ONLY if consistent;
            # otherwise trust the code's canonical mapping.
            return Extracted(service=service, error_code=code, target_object_type=tot)
    # 2) the FIRST well-formed code token in the free text is authoritative. If it is a
    #    KNOWN code, that fixes the class. If the first well-formed code is UNKNOWN, the
    #    ticket is about an unrecognised incident -> DEGRADE (return None) rather than
    #    scanning onward for a later known code: a later "known" code is almost always a
    #    red-herring decoy ("earlier alert mentioned X — ignore"), and grabbing it would be
    #    a WRONG confident class (a false fast-path). Fail-closed on the unknown-first code.
    m = _CODE_RE.search((raw_text or "").upper())
    if m:
        code = _norm_code(m.group(1))
        if code:
            service, tot = KNOWN_CODES[code]
            return Extracted(service=service, error_code=code, target_object_type=tot)
    return None


def _llm_propose(raw_text: str, structured: dict | None) -> Extracted | None:
    """FAST LLM PROPOSAL for messy text. Returns an Extracted marked llm_proposed by the
    caller, or None. Imported lazily so a missing/omitted model never breaks import; on
    any outage venice.chat returns a canned string (not parseable) -> None (safe)."""
    from precedent import venice

    tool = {
        "type": "function",
        "function": {
            "name": "propose_incident_class",
            "description": "Propose the incident's service, error_code and target_object_type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {"type": "string"},
                    "error_code": {"type": "string"},
                    "target_object_type": {"type": "string"},
                },
                "required": ["service", "error_code", "target_object_type"],
            },
        },
    }
    prompt = (
        "Extract the incident class from this ticket as a tool call. Do not guess a code "
        "you cannot see. Ticket:\n" + (raw_text or "") +
        ("\nStructured hints: " + str(structured) if structured else "")
    )
    out = venice.chat("FAST", [{"role": "user", "content": prompt}], tools=[tool], max_tokens=512)
    if not isinstance(out, dict):
        return None
    args = out.get("args") or {}
    service = _SERVICE_CANON.get(str(args.get("service", "")).strip().lower(),
                                 str(args.get("service", "")).strip().lower())
    code = str(args.get("error_code", "")).strip().upper()
    tot = str(args.get("target_object_type", "")).strip().lower()
    if not (service and code and tot):
        return None
    return Extracted(service=service, error_code=code, target_object_type=tot)


def extract(raw_text: str, structured: dict | None = None):
    """Return (Extracted | None, method). Deterministic first (known code in the
    structured payload or matched exactly in the text). Only on failure does the FAST LLM
    PROPOSE — marked 'llm_proposed', never class-confirmed. (None, 'llm_proposed') when
    even a proposal can't yield all three fields."""
    det = _deterministic(raw_text, structured)
    if det is not None:
        return det, "deterministic"
    proposed = _llm_propose(raw_text, structured)
    return proposed, "llm_proposed"
