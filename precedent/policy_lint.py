"""Policy-pack authoring lint — the gate that keeps every executable action class SAFE.

WP-POLICY. Spec: docs/policy-action-class-schema.md; hard rule §2.5 (rollback-precedes-
execution). This is a PURE, deterministic checker (no LLM, no network) so it is directly
unit-testable and CI-cheap.

Contract enforced on every EXECUTABLE action class (action_type is a real typed mutation):
  R1 MISSING_INVERSE        — no `inverse` block.
  R2 NO_TRUE_INVERSE        — inverse is not reversible / strategy is not a real rollback
                              mechanism / no `tool` / the named tool does NOT resolve to a
                              real rollback in the typed-tool registry (fake / no-op / absent).
  R3 MISSING_PROBE          — no `verification_probe` block.
  R4 INVALID_PROBE          — probe strategy unknown, or field_equals without field/expected.
  R5 MISSING_APPROVER_ROLE  — a restricted_change class must name required_approver_role.

Irreversibility is enforced POSITIVELY, not by an action-NAME denylist. There is no list of
"bad" names to keep in sync (which credential-rotation / password-reset SYNONYMS would slip
past). Instead a class is executable ONLY if it declares a TRUE inverse whose named tool
ACTUALLY EXISTS in the typed-tool registry and performs a GENUINE rollback (§2.5 rollback-
precedes-execution). An irreversible action — a credential rotation, password reset, wipe, by
ANY name — is rejected because it cannot honestly name a real inverse tool that restores the
state it destroyed: its inverse is necessarily absent, a no-op, or an invented tool name.

Non-executable classes (action_type none/escalate/stale) are EXEMPT — they never mutate, so
they need neither an inverse nor a probe. The lint reports every violation (it does not stop
at the first) so an author fixes a pack in one pass.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from precedent import policy

# --------------------------------------------------------------------------- #
# POSITIVE inverse-tool requirement (fixes 1 & 4) — replaces the old action-NAME denylist.
#
# The named inverse tools the sim's typed-tool registry can ACTUALLY run, grouped by the
# inverse strategy that may name them. An executable class is accepted ONLY if its declared
# inverse names a tool that EXISTS here AND performs a GENUINE rollback:
#   * restore_snapshot -> `restore`  — sim.core.restore (POST /sim/restore) re-applies the
#     pre-execute field snapshot: a real, verifiable rollback.
#   * typed_inverse    -> a real forward typed tool the sim's executor recognises.
# A tool that is not in this registry is treated as a NO-OP / invented name and rejected — so
# an irreversible action cannot buy an executable class by naming a rollback that does not
# exist. tests/test_policy_kit.py asserts every name here resolves against the real sim.
# --------------------------------------------------------------------------- #
_ROLLBACK_TOOLS: frozenset[str] = frozenset({"restore"})
_FORWARD_TYPED_TOOLS: frozenset[str] = frozenset({
    "republish_epg", "dedupe_slot", "rights_takedown",
})


def _inverse_tool_resolves(strategy: str, tool: str) -> bool:
    """True when `tool` names a real rollback the typed-tool registry can actually run for the
    given inverse strategy. A tool absent from the registry is a no-op / invented name."""
    if strategy == "restore_snapshot":
        return tool in _ROLLBACK_TOOLS
    if strategy == "typed_inverse":
        return tool in _FORWARD_TYPED_TOOLS
    return False


@dataclass(frozen=True)
class Violation:
    pack: str
    class_key: str
    code: str
    message: str

    def render(self) -> str:
        return f"  [{self.code}] {self.pack} :: {self.class_key}\n      {self.message}"


def _check_inverse(rule: dict) -> tuple[str, str] | None:
    """Return (code, message) if the inverse is missing or not a TRUE inverse, else None."""
    inverse = rule.get("inverse")
    if not isinstance(inverse, dict):
        return ("MISSING_INVERSE",
                "executable class declares no `inverse` — every mutation needs a rollback "
                "that is generated BEFORE it executes (§2.5 rollback-precedes-execution).")
    strategy = str(inverse.get("strategy", "")).strip().lower()
    if inverse.get("reversible") is not True:
        return ("NO_TRUE_INVERSE",
                "inverse.reversible is not true — a class with no genuine rollback must not "
                "carry a fake inverse; either give it a real one or make it non-executable.")
    if strategy not in policy.TRUE_INVERSE_STRATEGIES:
        return ("NO_TRUE_INVERSE",
                f"inverse.strategy={strategy!r} is not a real rollback mechanism "
                f"(expected one of {sorted(policy.TRUE_INVERSE_STRATEGIES)}).")
    tool = str(inverse.get("tool", "")).strip()
    if not tool:
        return ("NO_TRUE_INVERSE",
                f"inverse.strategy={strategy} requires a `tool` naming the rollback call — "
                "none was given.")
    # POSITIVE requirement (fixes 1 & 4): the named tool must ACTUALLY EXIST in the typed-tool
    # registry and perform a GENUINE rollback — not a no-op or an invented name. This is how an
    # irreversible action (credential rotation / password reset / wipe, by ANY name) is
    # rejected: it cannot name a real inverse tool that restores the state it destroyed.
    if not _inverse_tool_resolves(strategy, tool):
        return ("NO_TRUE_INVERSE",
                f"inverse.tool={tool!r} does not resolve to a real rollback in the typed-tool "
                "registry — an executable class must name an inverse tool that EXISTS and "
                "genuinely restores the prior state. An irreversible action (by any name) is "
                "rejected here because no such inverse tool exists for it; route it to a human.")
    return None


def _check_probe(rule: dict) -> tuple[str, str] | None:
    probe = rule.get("verification_probe")
    if not isinstance(probe, dict):
        return ("MISSING_PROBE",
                "executable class declares no `verification_probe` — a fix that cannot be "
                "verified cannot be trusted to have worked (and auto-rollback needs the "
                "post-state check).")
    strategy = str(probe.get("strategy", "")).strip().lower()
    if strategy not in policy.PROBE_STRATEGIES:
        return ("INVALID_PROBE",
                f"verification_probe.strategy={strategy!r} is not a runnable probe "
                f"(expected one of {sorted(policy.PROBE_STRATEGIES)}).")
    if strategy == "field_equals":
        if not str(probe.get("field", "")).strip() or "expected" not in probe:
            return ("INVALID_PROBE",
                    "verification_probe.strategy=field_equals requires `field` and "
                    "`expected`.")
    return None


def lint_pack(pack: dict, pack_name: str = "<pack>") -> list[Violation]:
    """Deterministically validate one loaded pack dict. Returns all violations (empty ==
    clean). Pure — no I/O."""
    out: list[Violation] = []
    for class_key, rule in policy.iter_action_classes(pack):
        if not isinstance(rule, dict):
            out.append(Violation(pack_name, str(class_key), "MALFORMED_CLASS",
                                 "class entry is not a mapping."))
            continue
        action_type = str(rule.get("action_type", "")).strip().lower()

        # Non-executable classes are exempt from the inverse/probe contract.
        if not policy.is_executable_action(action_type):
            continue

        # Every executable class — WHATEVER its action_type is named — must positively prove a
        # real inverse (below). An irreversible action cannot, so it is rejected without needing
        # a name denylist (§2.5 rollback-precedes-execution).

        inv = _check_inverse(rule)
        if inv:
            out.append(Violation(pack_name, str(class_key), inv[0], inv[1]))
        prb = _check_probe(rule)
        if prb:
            out.append(Violation(pack_name, str(class_key), prb[0], prb[1]))

        if str(rule.get("risk_class", "")).strip() == "restricted_change" \
                and not str(rule.get("required_approver_role", "")).strip():
            out.append(Violation(
                pack_name, str(class_key), "MISSING_APPROVER_ROLE",
                "restricted_change class must name required_approver_role (a restricted fix "
                "needs a designated human approver)."))
    return out


def lint_file(path: str | Path) -> list[Violation]:
    """Load a YAML pack from disk and lint it. A load/parse error is itself a violation."""
    p = Path(path)
    try:
        with open(p, encoding="utf-8") as fh:
            pack = yaml.safe_load(fh)
    except (OSError, yaml.YAMLError) as exc:
        return [Violation(p.name, "<file>", "LOAD_ERROR", f"could not parse pack: {exc}")]
    if not isinstance(pack, dict):
        return [Violation(p.name, "<file>", "LOAD_ERROR", "pack is not a YAML mapping.")]
    return lint_pack(pack, p.name)


# The packs shipped in the repo that the lint must keep green (the default target).
def default_pack_paths() -> list[Path]:
    here = Path(__file__).parent
    return [here / "policy_pack.yaml", here / "policy_pack_actions.yaml"]
