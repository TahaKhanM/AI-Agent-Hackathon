"""Deterministic risk-policy engine.  [owner T1, task T1-8]

Spec: Idea/refinement/02-architecture-refinement.md §3.2-§3.3.

RULE 2: the risk CLASS, policy_rule_id and ladder ceiling are decided HERE by the YAML
pack — NEVER by an LLM. If the triage was not deterministic-confirmed
(extraction_method != 'deterministic' or extracted is None), the ladder level is FORCED
to L1 (the L0/L1 cap) regardless of the class's ceiling, so an LLM proposal can never
unlock the standing-approval fast-path. The SMART model may later fill rationale_text
PROSE only — it can touch neither risk_class nor ladder_level. Evaluation cost is
corpus-size-independent (a per-tenant YAML tree lookup).
"""
from __future__ import annotations

import functools
from pathlib import Path

import yaml

from precedent import extractor
from precedent.contracts import RiskAssessment, TriageResult

_PACK_PATH = Path(__file__).with_name("policy_pack.yaml")


@functools.lru_cache(maxsize=1)
def load_pack() -> dict:
    with open(_PACK_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# --------------------------------------------------------------------------- #
# Authoring-kit constants (WP-POLICY). ADDITIVE — assess()/rule_for() do not read these.
# Only `precedent policy lint` (precedent/policy_lint.py) consumes them. Kept here so the
# deterministic-gate module remains the single source of truth for what "executable" and
# "irreversible" mean, and so the lint never has to re-derive policy semantics.
# --------------------------------------------------------------------------- #

# An action_type that means "no typed mutation is performed" — these classes never execute
# (escalate / stale-runbook / degrade), so the lint does not require an inverse or probe.
NON_EXECUTABLE_ACTIONS: frozenset[str] = frozenset({"", "none"})

# §2.5 rollback-precedes-execution: actions that DESTROY the prior state and therefore have
# no TRUE inverse (you cannot un-rotate a live credential or restore an old password hash).
# A class whose action_type is here is REJECTED by lint regardless of any declared inverse.
IRREVERSIBLE_ACTIONS: frozenset[str] = frozenset({
    "password_reset", "reset_password",
    "credential_rotation", "rotate_credential", "rotate_secret",
    "key_rotation", "rotate_key", "api_key_rotation",
})

# Inverse strategies that describe a REAL rollback mechanism (a true inverse). `none` (or any
# other value) is not a true inverse and is rejected.
TRUE_INVERSE_STRATEGIES: frozenset[str] = frozenset({"restore_snapshot", "typed_inverse"})

# Verification-probe strategies the sim can actually run (deterministic, no LLM).
PROBE_STRATEGIES: frozenset[str] = frozenset({"object_health", "field_equals"})


def is_executable_action(action_type) -> bool:
    """True when a class's action_type denotes a real typed mutation (so it needs an inverse
    + probe under the authoring contract)."""
    return str(action_type or "").strip().lower() not in NON_EXECUTABLE_ACTIONS


def iter_action_classes(pack: dict):
    """Yield (class_key, rule) for every class entry in a loaded pack dict. Safe on a pack
    with no `classes` section."""
    yield from (pack.get("classes") or {}).items()


def rule_for(class_key: str) -> dict:
    """The pack rule for a class_key (or the `default` degrade rule). Includes
    action_type + lineage_refs the orchestrator needs to build the ExecutionPlan."""
    pack = load_pack()
    return pack.get("classes", {}).get(class_key) or pack["default"]


def assess(triage: TriageResult) -> RiskAssessment:
    """Deterministic risk assessment. No LLM in this function."""
    pack = load_pack()
    extracted = triage.extracted
    method = triage.extraction_method

    # RULE 2 cap: a non-deterministic extract can never reach the fast-path / STANDING.
    if extracted is None or method != "deterministic":
        cap = pack["degraded_cap"]
        return RiskAssessment(
            incident_id=triage.incident_id,
            risk_class=cap["risk_class"],
            policy_rule_id=cap["policy_rule_id"],
            ladder_level=cap["ladder_ceiling"],   # L1
            rationale_text=(f"capped at L0/L1: extraction method={method!r} is not "
                            "deterministic-confirmed — human classification required."),
        )

    class_key = extractor.class_key_of(extracted)
    rule = rule_for(class_key)
    return RiskAssessment(
        incident_id=triage.incident_id,
        risk_class=rule["risk_class"],
        policy_rule_id=rule["policy_rule_id"],
        ladder_level=rule["ladder_ceiling"],
        rationale_text="",   # SMART may fill this PROSE later; never the class/level.
    )
