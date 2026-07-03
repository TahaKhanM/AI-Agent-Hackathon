"""Core-loop unit tests: extractor (rule 2 deterministic-first), policy (deterministic
gate + L0/L1 cap), ladder (graduation, anti-gaming, demotion, canonical STANDING token).
No network; venice.chat is monkeypatched where the LLM-propose path is exercised.
"""
from __future__ import annotations

import pytest

from precedent import extractor, ladder, policy, venice
from precedent.contracts import TriageResult
from precedent_memory import audit, db


# --------------------------------------------------------------------------- #
# Extractor
# --------------------------------------------------------------------------- #
def test_clean_structured_payload_is_deterministic():
    ext, method = extractor.extract("EPG publish failed",
                                    {"service": "publisher", "error_code": "PUB-4012",
                                     "target_object_type": "schedule_item"})
    assert method == "deterministic"
    assert (ext.service, ext.error_code, ext.target_object_type) == \
        ("publisher", "PUB-4012", "schedule_item")
    assert extractor.class_key_of(ext) == "publisher|PUB-4012|schedule_item"


def test_known_code_in_free_text_is_deterministic():
    ext, method = extractor.extract("ticket: slot dup, code SCH-DUP-002 on the 9pm", None)
    assert method == "deterministic"
    assert extractor.class_key_of(ext) == "scheduler|SCH-DUP-002|schedule_item"


def test_typo_code_falls_to_llm_and_is_not_class_confirmed(monkeypatch):
    # A garbled code must NOT match deterministically; the LLM proposal is llm_proposed.
    monkeypatch.setattr(venice, "chat",
                        lambda *a, **k: {"__tool__": "propose_incident_class",
                                         "args": {"service": "publisher",
                                                  "error_code": "PUB-4012",
                                                  "target_object_type": "schedule_item"}})
    ext, method = extractor.extract("the guide thingy is blank, code PUB-4O12 maybe", None)
    assert method == "llm_proposed"   # even though the LLM guessed a real code
    assert ext is not None


def test_unparseable_llm_yields_none(monkeypatch):
    monkeypatch.setattr(venice, "chat", lambda *a, **k: venice.CANNED_FALLBACK)
    ext, method = extractor.extract("something totally vague and codeless", None)
    assert ext is None and method == "llm_proposed"


# --------------------------------------------------------------------------- #
# Policy
# --------------------------------------------------------------------------- #
def _triage(ext, method, iid="INC-x"):
    return TriageResult(incident_id=iid, extracted=ext, extraction_method=method)


def test_deterministic_known_class_gets_expected_assessment():
    ext, m = extractor.extract("", {"error_code": "SCH-DUP-002"})
    ra = policy.assess(_triage(ext, m))
    assert ra.risk_class == "standard_change"
    assert ra.policy_rule_id == "SCH-DUP-002-DEDUPE"
    assert ra.ladder_level == "STANDING"   # the fast-path repeat class's policy ceiling


def test_llm_proposed_is_capped_regardless_of_class(monkeypatch):
    # LLM proposes the STANDING-ceiling scheduler class, but method=llm_proposed -> cap L1.
    ext, m = extractor.Extracted(service="scheduler", error_code="SCH-DUP-002",
                                 target_object_type="schedule_item"), "llm_proposed"
    ra = policy.assess(_triage(ext, m))
    assert ra.ladder_level == "L1"          # capped, NOT STANDING
    assert ra.risk_class == "unverified_extraction"


def test_none_extraction_caps_at_l1():
    ra = policy.assess(_triage(None, "llm_proposed"))
    assert ra.ladder_level == "L1"
    assert ra.policy_rule_id == "DEGRADE-CAP-L1"


def test_chat_output_cannot_change_risk_class():
    # The deterministic class is fixed by the code; no LLM field can move it.
    ext, m = extractor.extract("", {"error_code": "PUB-4012"})
    ra1 = policy.assess(_triage(ext, m))
    # deterministic assessment keys on the class_key; a tampered (LLM-style) class_key that
    # isn't in the pack degrades to L1 — no LLM whim can conjure a graduated class.
    assert ra1.risk_class == "standard_change"
    assert policy.rule_for("rights|PUB-4012|vod_item")["policy_rule_id"] == "DEGRADE-DEFAULT-L1"


# --------------------------------------------------------------------------- #
# Ladder
# --------------------------------------------------------------------------- #
@pytest.fixture
def conn():
    c = db.connect(":memory:")
    yield c
    c.close()


CK = "scheduler|SCH-DUP-002|schedule_item"


def test_is_standing_false_by_default(conn):
    assert ladder.is_standing(CK, conn=conn) is False


def test_three_verifies_at_l2_make_eligible_then_promote_writes_canonical_standing(conn):
    ladder._upsert(conn, CK, level="L2", count=0)
    for tgt in ("slotA", "slotB", "slotC"):
        r = ladder.on_verification_result(CK, True, False, conn=conn, target_ref=tgt, source="sim")
        assert r["counted"] is True
    assert ladder.eligible(CK, conn=conn) is True
    res = ladder.promote(CK, "ops-lead", conn=conn)
    assert res["ok"] is True
    lvl = conn.execute("SELECT level, promoted_by FROM class_ladder WHERE class_key=?",
                       (CK,)).fetchone()
    assert lvl["level"] == "STANDING"                 # canonical token, not display text
    assert lvl["level"] != "Standing Approval"
    assert lvl["promoted_by"] == "ops-lead"


def test_anti_gaming_same_object_within_hour_counts_once(conn):
    ladder._upsert(conn, CK, level="L2", count=0)
    ladder.on_verification_result(CK, True, False, conn=conn, target_ref="slotA", source="sim")
    ladder.on_verification_result(CK, True, False, conn=conn, target_ref="slotA", source="sim")
    assert ladder.consecutive_verified(conn, CK) == 1   # the repeat did not count


def test_unmonitored_source_does_not_count(conn):
    ladder._upsert(conn, CK, level="L2", count=0)
    r = ladder.on_verification_result(CK, True, False, conn=conn, target_ref="x", source="email")
    assert r["counted"] is False
    assert ladder.consecutive_verified(conn, CK) == 0


def test_failure_demotes_immediately_and_resets_counter(conn):
    ladder._upsert(conn, CK, level="STANDING", count=5, promoted_by="ops-lead")
    r = ladder.on_verification_result(CK, verified=False, rolled_back=True, conn=conn,
                                      target_ref="slotA", source="sim")
    assert r["level"] == "L1" and r["demoted"] is True
    assert ladder.consecutive_verified(conn, CK) == 0
    kinds = [a["event_type"] for a in conn.execute(
        "SELECT event_type FROM audit_log").fetchall()]
    assert "class_demoted" in kinds


def test_promote_requires_eligibility_unless_forced(conn):
    ladder._upsert(conn, CK, level="L1", count=0)
    assert ladder.promote(CK, "ops-lead", conn=conn)["ok"] is False     # not eligible
    assert ladder.promote(CK, "ops-lead", conn=conn, force=True)["ok"] is True  # demo pre-seed
    assert ladder.is_standing(CK, conn=conn) is True


def test_audit_chain_stays_intact_through_ladder_writes(conn):
    ladder._upsert(conn, CK, level="L2", count=0)
    ladder.on_verification_result(CK, True, False, conn=conn, target_ref="s1", source="sim")
    ladder.demote(conn=conn, class_key=CK)
    assert audit.verify_chain(conn=conn) is True
