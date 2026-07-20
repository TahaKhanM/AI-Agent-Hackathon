"""WP-POLICY authoring-kit tests (TDD).

Covers:
- the lint runs GREEN on every shipped pack (policy_pack.yaml + policy_pack_actions.yaml);
- every executable action class in the shipped action-class pack has its INVERSE and
  VERIFICATION PROBE exercised end-to-end against the sim (execute -> probe -> inverse ->
  confirm rollback), reusing sim/factory + the real SimTools client;
- the individual lint rules (missing/fake inverse, missing/invalid probe, irreversible
  action, missing approver role);
- a deliberately-broken pack fixture FAILS lint with clear, coded messages — and password
  resets + credential rotations STAY rejected (§2.5);
- the `precedent policy lint` CLI exit codes.

No network, no LLM. The sim runs in-process over a per-test temp db via sim.factory.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from precedent import policy, policy_lint
from precedent.cli import policy as policy_cli
from precedent.tools import SimTools
from sim import core, db, factory

_HERE = Path(__file__).parent
_BROKEN_PACK = _HERE / "data" / "broken_action_pack.yaml"
_ACTIONS_PACK = Path(policy.__file__).with_name("policy_pack_actions.yaml")
_MAIN_PACK = Path(policy.__file__).with_name("policy_pack.yaml")


def _load(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# --------------------------------------------------------------------------- #
# Shipped packs lint clean
# --------------------------------------------------------------------------- #
def test_shipped_packs_lint_clean():
    for path in policy_lint.default_pack_paths():
        violations = policy_lint.lint_file(path)
        assert violations == [], (
            f"{path.name} should lint clean, got: "
            + "; ".join(f"{v.code}@{v.class_key}" for v in violations))


def test_action_pack_has_8_to_10_executable_classes():
    pack = _load(_ACTIONS_PACK)
    executable = [ck for ck, r in policy.iter_action_classes(pack)
                  if policy.is_executable_action(r.get("action_type"))]
    assert 8 <= len(executable) <= 10, executable


def test_action_pack_classes_carry_uci_precedent_ref():
    pack = _load(_ACTIONS_PACK)
    for ck, rule in policy.iter_action_classes(pack):
        ref = rule.get("precedent_ref")
        assert isinstance(ref, dict), ck
        assert ref.get("corpus") == "UCI-498", ck
        assert "|" in str(ref.get("fix_class", "")), ck


def test_action_pack_asserts_no_unverified_occurrence_number():
    # Number-honesty: per-class occurrence counts are NOT measured/published (not in
    # docs/numbers.md), so no precedent_ref may present one as a measured corpus fact.
    pack = _load(_ACTIONS_PACK)
    for ck, rule in policy.iter_action_classes(pack):
        assert "occurrences" not in rule.get("precedent_ref", {}), (
            f"{ck}: precedent_ref carries an unverified `occurrences` count")
    # and the raw YAML text must not smuggle it back in as a key anywhere.
    assert "occurrences:" not in _ACTIONS_PACK.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Every shipped action class's INVERSE + PROBE exercised against the sim
# --------------------------------------------------------------------------- #
# Map (action_type, target_object_type) -> a seeded UNHEALTHY sim object to drive the fix on.
_SEED_OBJECT = {
    ("republish_epg", "schedule_item"): ("publisher", "schedule_item", "18"),
    ("dedupe_slot", "schedule_item"): ("scheduler", "schedule_item", "114"),
    ("rights_takedown", "vod_item"): ("rights", "vod_item", "1"),
}


def _sim_client(tmp_path) -> TestClient:
    db_path = str(tmp_path / "sim.db")
    conn = db.connect(db_path)
    core.build_sim(conn)
    conn.close()
    return TestClient(factory.make_sim_app(db_path))


def _executable_classes_across_shipped_packs():
    """Every EXECUTABLE (action_type is a real mutation) class in EVERY shipped pack —
    the action-class pack AND the core policy_pack.yaml. This is what fix 3 requires the sim
    round-trip to cover in full (reconciling the actions-pack / core-pack gap)."""
    for pack_path in (_ACTIONS_PACK, _MAIN_PACK):
        pack = _load(pack_path)
        for class_key, rule in policy.iter_action_classes(pack):
            if policy.is_executable_action(rule.get("action_type")):
                yield pack_path.name, class_key, rule


def test_every_executable_class_inverse_and_probe_run_against_sim(tmp_path):
    exercised = 0
    with _sim_client(tmp_path) as sc:
        tools = SimTools(client=sc)
        for pack_name, class_key, rule in _executable_classes_across_shipped_packs():
            action_type = rule["action_type"]
            _, _, target = class_key.split("|")
            seed = _SEED_OBJECT.get((action_type, target))
            # fix 3: no executable class may target a sim object type with no table — every one
            # must round-trip. A missing mapping here means the class cannot be exercised (the
            # PUB-JOB-503 / publish_job trap), which must be fixed in the pack, not skipped.
            assert seed is not None, (
                f"{pack_name}::{class_key}: executable class has no sim object mapping — its "
                f"action ({action_type}) targets object type {target!r}, which the sim cannot "
                f"snapshot/verify/restore. Make it non-executable or map it.")
            service, object_type, object_id = seed

            # snapshot pre-state (the inverse generator's rollback baseline)
            snap = tools.snapshot(service, object_type, object_id)
            pre_state = snap["fields"]
            assert snap["healthy"] is False, f"{class_key}: seed object should start unhealthy"

            # execute the class's typed action
            exec_arg = {"schedule_slot_id": object_id} if object_type == "schedule_item" \
                else {"vod_item_id": object_id}
            assert tools.execute(action_type, exec_arg)["ok"] is True, class_key

            # VERIFICATION PROBE (object_health) — must read healthy post-fix
            probe = rule["verification_probe"]
            assert probe["strategy"] == "object_health"
            assert tools.verify(service, object_type, object_id)["verified"] is True, class_key

            # INVERSE GENERATOR (restore_snapshot) — roll back to pre-state, confirm reverted
            inverse = rule["inverse"]
            assert inverse["reversible"] is True and inverse["tool"] == "restore"
            assert tools.restore(service, object_type, object_id, pre_state)["ok"] is True
            assert tools.snapshot(service, object_type, object_id)["healthy"] is False, \
                f"{class_key}: inverse did not restore the pre-state"
            exercised += 1
    # 9 in the action-class pack + the executable classes in the core pack, all round-tripped.
    assert exercised >= 14


def test_no_executable_class_targets_a_tableless_sim_object_type():
    # fix 3 (PUB-JOB-503 trap): `publish_job` has no sim table, so an executable class targeting
    # it could never round-trip its inverse. Guard that no shipped executable class does.
    tableful = {"schedule_item", "vod_item"}   # object types with a real sim table (_TABLE_FOR)
    for pack_name, class_key, _ in _executable_classes_across_shipped_packs():
        _, _, target = class_key.split("|")
        assert target in tableful, (
            f"{pack_name}::{class_key} is executable but targets {target!r}, which the sim "
            f"cannot restore/verify — its declared inverse would be a no-op.")


def test_inverse_tool_registry_is_grounded_in_the_sim(tmp_path):
    # The lint's rollback-tool registry must not drift from what the sim can ACTUALLY run.
    # `restore` is a real sim rollback callable; each forward typed tool is recognised by the
    # sim executor (a bogus name is not) — so a class naming a real tool is genuinely runnable.
    from sim import core
    assert callable(getattr(core, "restore", None))
    for tool in policy_lint._ROLLBACK_TOOLS:
        assert tool == "restore" and callable(getattr(core, tool, None))
    db_path = str(tmp_path / "sim.db")
    conn = db.connect(db_path)
    db.create_tables(conn)
    for tool in policy_lint._FORWARD_TYPED_TOOLS:
        # a recognised tool dispatches to its handler (detail is not the unknown-tool sentinel)
        assert "unknown tool" not in core.execute(conn, tool, {})["detail"], tool
    assert "unknown tool" in core.execute(conn, "definitely_not_a_tool", {})["detail"]
    conn.close()


# --------------------------------------------------------------------------- #
# Individual lint rules
# --------------------------------------------------------------------------- #
def _lint_one(rule: dict, class_key: str = "svc|CODE|obj") -> list[str]:
    return [v.code for v in policy_lint.lint_pack({"classes": {class_key: rule}})]


_GOOD = {
    "risk_class": "standard_change", "policy_rule_id": "X", "ladder_ceiling": "L2",
    "action_type": "republish_epg", "required_approver_role": "publishing-ops",
    "inverse": {"strategy": "restore_snapshot", "reversible": True, "tool": "restore"},
    "verification_probe": {"strategy": "object_health", "expect_healthy": True},
}


def test_good_class_passes():
    assert _lint_one(dict(_GOOD)) == []


def test_missing_inverse_rejected():
    r = dict(_GOOD)
    r.pop("inverse")
    assert "MISSING_INVERSE" in _lint_one(r)


def test_non_reversible_inverse_rejected():
    r = dict(_GOOD)
    r["inverse"] = {"strategy": "none", "reversible": False}
    assert "NO_TRUE_INVERSE" in _lint_one(r)


def test_typed_inverse_without_tool_rejected():
    r = dict(_GOOD)
    r["inverse"] = {"strategy": "typed_inverse", "reversible": True}
    assert "NO_TRUE_INVERSE" in _lint_one(r)


def test_missing_probe_rejected():
    r = dict(_GOOD)
    r.pop("verification_probe")
    assert "MISSING_PROBE" in _lint_one(r)


def test_invalid_field_equals_probe_rejected():
    r = dict(_GOOD)
    r["verification_probe"] = {"strategy": "field_equals"}
    assert "INVALID_PROBE" in _lint_one(r)


def test_inverse_naming_a_nonexistent_tool_rejected():
    # fix 4: structural well-formedness is not enough — the named inverse tool must actually
    # resolve to a real rollback in the typed-tool registry.
    r = dict(_GOOD)
    r["inverse"] = {"strategy": "restore_snapshot", "reversible": True, "tool": "make_it_good"}
    assert _lint_one(r) == ["NO_TRUE_INVERSE"]


def test_credential_rotation_stays_rejected():
    # No name denylist: rejected because it cannot name a real inverse tool (§2.5). Here it
    # claims reversible + a plausible tool name that does not exist in the registry.
    r = dict(_GOOD)
    r["action_type"] = "rotate_credential"
    r["risk_class"] = "restricted_change"
    r["inverse"] = {"strategy": "restore_snapshot", "reversible": True,
                    "tool": "unrotate_credential"}
    assert _lint_one(r) == ["NO_TRUE_INVERSE"]


def test_password_reset_stays_rejected():
    r = dict(_GOOD)
    r["action_type"] = "password_reset"
    r["risk_class"] = "restricted_change"
    r["inverse"] = {"strategy": "none", "reversible": False}   # no genuine rollback exists
    assert _lint_one(r) == ["NO_TRUE_INVERSE"]


def test_arbitrary_irreversible_synonym_rejected():
    # An action nobody put on a denylist ("wipe_x") is still rejected — its inverse cannot name
    # a real rollback tool. This is exactly what a positive requirement buys over a name list.
    for name, tool in [("wipe_datastore", "undelete_everything"),
                       ("obliterate_ledger", "un_obliterate"),
                       ("shred_backups", "unshred")]:
        r = dict(_GOOD)
        r["action_type"] = name
        r["risk_class"] = "restricted_change"
        r["inverse"] = {"strategy": "restore_snapshot", "reversible": True, "tool": tool}
        assert _lint_one(r) == ["NO_TRUE_INVERSE"], name


def test_shipped_executable_classes_have_resolvable_inverses():
    # The flip side: every shipped executable class DOES name a real inverse tool and passes.
    for path in (_MAIN_PACK, _ACTIONS_PACK):
        for ck, rule in policy.iter_action_classes(_load(path)):
            if policy.is_executable_action(rule.get("action_type")):
                assert _lint_one(rule, ck) == [], (path.name, ck)


def test_non_executable_class_is_exempt():
    r = {"risk_class": "standard_change", "policy_rule_id": "Y", "ladder_ceiling": "L1",
         "action_type": "none", "lineage_refs": []}
    assert _lint_one(r) == []


def test_restricted_change_requires_approver_role():
    r = dict(_GOOD)
    r["risk_class"] = "restricted_change"
    r.pop("required_approver_role")
    assert "MISSING_APPROVER_ROLE" in _lint_one(r)


# --------------------------------------------------------------------------- #
# Broken fixture fails lint with clear, coded messages
# --------------------------------------------------------------------------- #
def test_broken_pack_fails_lint_with_all_expected_codes():
    violations = policy_lint.lint_file(_BROKEN_PACK)
    codes = {v.code for v in violations}
    assert {"MISSING_INVERSE", "NO_TRUE_INVERSE", "MISSING_PROBE"} <= codes, codes
    # No IRREVERSIBLE_ACTION code exists any more — irreversibility is caught positively.
    assert "IRREVERSIBLE_ACTION" not in codes
    # The credential rotation, password reset AND an arbitrary irreversible synonym are all
    # rejected — every one via NO_TRUE_INVERSE (no real inverse tool exists for them, §2.5).
    no_true = {v.class_key for v in violations if v.code == "NO_TRUE_INVERSE"}
    assert "auth|SEC-ROT-001|credential" in no_true
    assert "auth|SEC-PWD-002|user_account" in no_true
    assert "storage|STG-WIPE-006|datastore" in no_true
    # messages are human-readable and name the class
    for v in violations:
        assert v.class_key in v.render()
        assert v.message


# --------------------------------------------------------------------------- #
# CLI exit codes
# --------------------------------------------------------------------------- #
def test_cli_lint_clean_packs_exit_zero(capsys):
    rc = policy_cli.main(["policy", "lint", str(_MAIN_PACK), str(_ACTIONS_PACK)])
    assert rc == 0
    assert "OK" in capsys.readouterr().out


def test_cli_lint_broken_pack_exit_one(capsys):
    rc = policy_cli.main(["policy", "lint", str(_BROKEN_PACK)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "NO_TRUE_INVERSE" in err and "FAIL" in err


def test_cli_default_targets_shipped_packs(capsys):
    rc = policy_cli.main(["policy", "lint"])
    assert rc == 0
    assert "clean" in capsys.readouterr().out


def test_cli_bare_policy_token_stripped(capsys):
    # entry point may invoke as `precedent policy lint` OR bare `lint ...`; both work.
    assert policy_cli.main(["lint", str(_ACTIONS_PACK)]) == 0
    capsys.readouterr()
