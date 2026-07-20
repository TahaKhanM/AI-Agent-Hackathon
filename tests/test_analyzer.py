"""Tests for the Precedent Analyzer (WP-ANALYZER).

Run ONLY this file:  .venv/bin/python -m pytest tests/test_analyzer.py -q

Covers:
  * UCI export reproduces 94.4% / 98.6% / 18.2 h / 558 byte-for-byte, WITH labels on the report.
  * DATA NEVER LEAVES THE MACHINE — a full analysis + report render completes with sockets disabled.
  * the synthetic Jira fixture exercises the auto-detecting column mapper end-to-end.
  * a malformed CSV fails with a helpful MappingError, never a traceback.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from precedent_analyzer.analyze import analyze
from precedent_analyzer.cli import run
from precedent_analyzer.mapping import MappingError, detect_and_map
from precedent_analyzer.report import render_html

REPO = Path(__file__).resolve().parents[1]
PKL = REPO / "data" / "analysis" / "uci_per_incident.pkl"
JIRA_FIXTURE = REPO / "tests" / "fixtures" / "jira_sample.csv"


def _uci_records():
    """Build canonical records from the committed per-incident pickle (the raw UCI CSV is
    not committed to the repo, so we reproduce from uci_per_incident.pkl — noted in
    data/analysis/uci-baseline-results.md)."""
    import pandas as pd

    df = pd.read_pickle(PKL)
    recs = []
    for _, r in df.iterrows():
        recs.append(
            {
                "incident_id": r["number"],
                "category": r["category"],
                "subcategory": r["subcategory"],
                "closed_code": r["closed_code"],
                "opened_at": None if pd.isna(r["opened_at"]) else r["opened_at"].to_pydatetime(),
                "resolved_at": (None if pd.isna(r["resolved_at"])
                                else r["resolved_at"].to_pydatetime()),
                "made_sla": bool(r["made_sla"]),
                "reassignment_count": int(r["reassignment_count"]),
                "team": r["assignment_group"],
            }
        )
    return recs


@pytest.mark.skipif(not PKL.exists(), reason="uci_per_incident.pkl not present")
def test_uci_reproduces_canonical_numbers_byte_for_byte():
    res = analyze(_uci_records(), source="servicenow")
    # The four slide-safe numbers, exact.
    assert res.valid_fingerprint_rows == 24805
    assert res.fix_class_match_rate == 94.4        # EXISTENCE
    assert res.symptom_class_match_rate == 98.6    # ARRIVAL-knowable
    assert res.precedented_median_res_h == 18.2    # CALENDAR
    assert res.ladder_class_count == 558
    assert res.ladder_volume_share == 94.8
    # Supporting corpus figures.
    assert res.precedented_p75_res_h == 136.6
    assert res.first_of_class_median_res_h == 92.1
    assert res.distinct_fix_classes == 1397
    assert res.distinct_symptom_classes == 335
    assert res.reassigned_share == 0.474
    assert res.is_uci_reproduction is True


@pytest.mark.skipif(not PKL.exists(), reason="uci_per_incident.pkl not present")
def test_report_prints_labels_and_caveats():
    res = analyze(_uci_records(), source="servicenow")
    html = render_html(res, source_name="incident_event_log.csv")
    # Org's own numbers on the page.
    assert "94.4%" in html and "98.6%" in html and "18.2" in html and "558" in html
    # Existence-vs-arrival caveats PRINTED on the report.
    assert "EXISTENCE" in html
    assert "ARRIVAL-KNOWABLE" in html or "ARRIVAL" in html
    assert "CALENDAR" in html
    assert "FLOOR" in html
    # Reference benchmark, labelled (docs/numbers.md).
    assert "94.4% (existence)" in html
    assert "98.6% (arrival-knowable)" in html
    assert "18.2 h (calendar)" in html
    assert "not product accuracy" in html
    # Local-only promise on the report itself.
    assert "No data left this" in html


def test_sockets_disabled_full_analysis(monkeypatch):
    """DATA NEVER LEAVES THE MACHINE: with socket.socket monkeypatched to raise, a full
    mapper -> analyze -> render pipeline still completes."""

    def _boom(*a, **k):
        raise OSError("network disabled for test")

    monkeypatch.setattr(socket, "socket", _boom)
    # Also block the lower-level connection creator for good measure.
    monkeypatch.setattr(socket, "create_connection", _boom)

    records, mapping = detect_and_map(str(JIRA_FIXTURE))
    result = analyze(records, source=mapping.source)
    html = render_html(result, source_name="jira_sample.csv")
    assert mapping.source == "jira"
    assert result.total_rows == 14
    assert "<html" in html
    # Sanity: sockets really are blocked in this test's context.
    with pytest.raises(OSError):
        socket.socket()


def test_jira_fixture_mapper_end_to_end():
    records, mapping = detect_and_map(str(JIRA_FIXTURE))
    assert mapping.source == "jira"
    # Auto-detected mapping picked Jira headers.
    assert mapping.columns["category"] == "Components"
    assert mapping.columns["subcategory"] == "Labels"
    assert mapping.columns["closed_code"] == "Resolution"
    assert mapping.columns["opened_at"] == "Created"
    assert mapping.columns["resolved_at"] == "Resolved"

    res = analyze(records, source=mapping.source)
    assert res.total_rows == 14
    # MEDIA-114 has no category/subcategory/resolution -> dropped from the fingerprintable set.
    assert res.valid_fingerprint_rows == 13
    # Playout|Fixed|epg-drift recurs 5x -> the one standing-approval candidate at threshold 4.
    assert res.ladder_class_count == 1
    top = res.top_candidates[0]
    assert top.category == "Playout" and top.closed_code == "Fixed" and top.count == 5
    # Fix-class repeats exist, so a match rate is computed.
    assert res.fix_class_match_rate is not None and res.fix_class_match_rate > 0


def test_cli_writes_report(tmp_path):
    out = tmp_path / "report.html"
    code = run([str(JIRA_FIXTURE), "-o", str(out), "--quiet"])
    assert code == 0
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "PRECEDENT" in text
    assert "No data left this" in text


def test_malformed_csv_helpful_error(tmp_path):
    bad = tmp_path / "bad.csv"
    # A CSV whose columns can't be mapped to the required fingerprint fields.
    bad.write_text("foo,bar,baz\n1,2,3\n4,5,6\n", encoding="utf-8")
    with pytest.raises(MappingError) as ei:
        detect_and_map(str(bad))
    msg = str(ei.value)
    assert "required columns" in msg
    assert "closed_code" in msg  # names what's missing, guides the fix
    # And through the CLI it becomes a clean exit code, not a traceback.
    code = run([str(bad), "-o", str(tmp_path / "x.html"), "--quiet"])
    assert code == 2


def _run_cli_subprocess(*argv):
    """Run the analyzer CLI in a child process so an UNCAUGHT exception surfaces as a real
    'Traceback' on stderr — the only faithful way to assert we never emit one."""
    return subprocess.run(
        [sys.executable, "-m", "precedent_analyzer", *argv],
        capture_output=True,
        text=True,
    )


def test_oversized_field_csv_no_traceback(tmp_path):
    """A CSV with a field larger than csv's field-size limit must fail with a HELPFUL
    message and a clean non-zero exit — never a raw Python traceback (regression)."""
    bad = tmp_path / "huge.csv"
    huge = "x" * 200_000  # well over the 131072-byte default field-size limit
    bad.write_text(
        "category,subcategory,closed_code,opened_at,resolved_at\n"
        f'Playout,epg,Fixed,"{huge}",2024-01-01\n',
        encoding="utf-8",
    )
    # Direct API: helpful MappingError, not a bare csv.Error.
    with pytest.raises(MappingError) as ei:
        detect_and_map(str(bad))
    msg = str(ei.value)
    assert "huge.csv" in msg          # names the offending file
    assert "Traceback" not in msg

    # Through the CLI (real child process): clean exit, no traceback text on stderr.
    proc = _run_cli_subprocess(str(bad), "-o", str(tmp_path / "x.html"), "--quiet")
    assert proc.returncode != 0
    assert proc.returncode == 2
    assert "Traceback" not in proc.stderr
    assert "precedent-analyze:" in proc.stderr


def test_empty_and_missing_column_csv_no_traceback(tmp_path):
    """An empty file and a wrong-columns file each give a helpful message + clean exit
    with NO traceback, via the real CLI child process."""
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    proc = _run_cli_subprocess(str(empty), "-o", str(tmp_path / "e.html"), "--quiet")
    assert proc.returncode == 2
    assert "Traceback" not in proc.stderr
    assert "precedent-analyze:" in proc.stderr

    missing = tmp_path / "missing.csv"
    missing.write_text("foo,bar,baz\n1,2,3\n", encoding="utf-8")
    proc = _run_cli_subprocess(str(missing), "-o", str(tmp_path / "m.html"), "--quiet")
    assert proc.returncode == 2
    assert "Traceback" not in proc.stderr
    assert "required columns" in proc.stderr


def test_empty_and_missing_files():
    with pytest.raises(MappingError):
        detect_and_map("/no/such/file/anywhere.csv")
    # header-only file
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        fh.write("category,subcategory,closed_code,opened_at,resolved_at\n")
        name = fh.name
    try:
        with pytest.raises(MappingError):
            detect_and_map(name)
    finally:
        os.unlink(name)
