"""Fixtures for the copy-lint honesty gate.

Every rule gets a BAD string (must be flagged) and a GOOD string (must pass). The linter is
pure, so these exercise the raw rules with no allowlist. Source of truth for the labels is
docs/numbers.md (NEVER-BLEND: 18.2 h CALENDAR/ours vs 8.85 h / 8h 51m BUSINESS/MetricNet).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from copy_lint import lint_text  # noqa: E402


def _rules(text: str, *, hosted: bool = False) -> set[str]:
    return {f["rule"] for f in lint_text(text, hosted=hosted)}


# ------------------------------------------------------------------ banned vocabulary

def test_r1_autonomous_label_flagged():
    assert "R1" in _rules("L3 = Autonomous")


def test_r1_standing_approval_passes():
    assert "R1" not in _rules("L3 = Standing Approval")


def test_r1_lowercase_graduated_autonomy_passes():
    assert "R1" not in _rules("we offer graduated autonomy")


def test_r2_control_plane_flagged():
    assert "R2" in _rules("our control plane decides")


def test_r2_control_plane_case_insensitive():
    assert "R2" in _rules("The Control Plane")


def test_r2_the_gate_passes():
    assert "R2" not in _rules("the gate decides")


def test_r3_azure_fails_open_flagged():
    assert "R3" in _rules("Azure fails open.")


def test_r3_permitted_sentence_passes():
    good = "Azure Managed Identity fails open unless failMode is set and the Stop-hook denies."
    assert "R3" not in _rules(good)


def test_r3_azure_without_failopen_passes():
    assert "R3" not in _rules("Azure hosts the model.")


def test_r4_placeholder_flagged():
    assert "R4" in _rules("median ‹XX› hours")


def test_r4_no_placeholder_passes():
    assert "R4" not in _rules("median 18.2 calendar hours")


def test_r5_offline_flagged_in_hosted():
    assert "R5" in _rules("runs airplane-mode", hosted=True)


def test_r5_offline_ok_when_not_hosted():
    assert "R5" not in _rules("runs airplane-mode", hosted=False)


def test_r5_hosted_good_copy_passes():
    assert "R5" not in _rules("kernel-hash verified; model-calls: 0", hosted=True)


# --------------------------------------------------------------------- adjacency A1/A2

def test_a1_18_2_business_flagged():
    assert "A1" in _rules("median 18.2 h business")


def test_a1_18_2_calendar_passes():
    assert "A1" not in _rules("18.2 calendar hours")


def test_a2_8h51m_business_passes():
    assert "A2" not in _rules("8h 51m business hours (MetricNet)")


def test_a2_885_calendar_flagged():
    assert "A2" in _rules("8.85 calendar hours")


def test_a2_8h51m_missing_business_flagged():
    assert "A2" in _rules("the baseline bar reads 8h 51m")


# --------------------------------------------------------------------- adjacency A3/A4

def test_a3_naive_floor_passes():
    assert "A3" not in _rules("naive floor top-3 87.7%")


def test_a3_missing_floor_flagged():
    assert "A3" in _rules("accuracy is 87.7%")


def test_a3_missing_floor_no_percent_flagged():
    # '%' is optional: a bare 87.7 without the floor/naive label evades honesty too.
    assert "A3" in _rules("top-3 accuracy is 87.7 on the first screen")


def test_a3_bare_number_not_matched_inside_longer_number():
    # 87.72 / 187.7 must NOT trip A3 (the negative look-arounds).
    assert "A3" not in _rules("build 187.7 shipped; ratio 87.72 held")


def test_a4_safety_number_passes():
    assert "A4" not in _rules("0/100 false-fast-paths — a SAFETY number")


def test_a4_missing_safety_flagged():
    assert "A4" in _rules("0 false fast-paths on the corpus")


def test_a4_labelled_recall_flagged():
    assert "A4" in _rules("0/100 false-fast-paths — a safety recall number")


# --------------------------------------------------------------------- adjacency A5/A6

def test_a5_existence_passes():
    assert "A5" not in _rules("94.4% — an existence claim")


def test_a5_missing_existence_flagged():
    assert "A5" in _rules("94.4% of incidents matched")


def test_a6_arrival_passes():
    assert "A6" not in _rules("98.6% arrival-knowable")


def test_a6_missing_arrival_flagged():
    assert "A6" in _rules("98.6% had precedent")


def test_a5_no_percent_missing_existence_flagged():
    assert "A5" in _rules("94.4 of incidents matched")


def test_a6_no_percent_missing_arrival_flagged():
    assert "A6" in _rules("98.6 had precedent")


def test_a5_a6_swap_flagged():
    # numbers.md §7 "don't swap": 94.4 = existence, 98.6 = arrival. A pair carrying each
    # other's label (each number next to the WRONG one) must trip A5 AND A6 via forbids —
    # this is the specific hole plain requires-only left open.
    rules = _rules("94.4% arrival-knowable and 98.6% existence claim")
    assert "A5" in rules and "A6" in rules


# ------------------------------------------------------------------------- vendor V1

def test_v1_vendor_claimed_passes():
    assert "V1" not in _rules("PagerDuty 99% faster (vendor-claimed)")


def test_v1_missing_vendor_claimed_flagged():
    assert "V1" in _rules("PagerDuty is 99% faster")


def test_v2_kcs_faster_unattributed_flagged():
    # The ServiceNow KCS "% faster" case-study figures must carry their source.
    assert "V2" in _rules("cases resolve 52% faster")
    assert "V2" in _rules("KB-attached cases resolve 66% faster")


def test_v2_kcs_faster_attributed_passes():
    assert "V2" not in _rules("52% faster (ServiceNow KCS case study)")


# ---------------------------------------------------------- never-blend co-occurrence

def test_never_blend_disclaimer_trips_raw_rules():
    # The canonical disclaimer names both figures with correct labels in one line; the
    # mechanical rule can't tell it apart, so the RAW linter flags it (A1 sees 'business'
    # near 18.2, A2 sees 'calendar' near 8h 51m). main()'s allowlist suppresses it.
    disclaimer = (
        "The baseline bar, 8h 51m, is MetricNet business-hours MTTR — never blended "
        "with the 18.2 calendar-hour figure above."
    )
    rules = _rules(disclaimer)
    assert "A1" in rules and "A2" in rules
