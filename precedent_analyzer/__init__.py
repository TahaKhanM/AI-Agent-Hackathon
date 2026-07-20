"""Precedent Analyzer — read an org's OWN incident export and measure how much of its
resolution work is *already precedented*, entirely on the local machine.

It generalises two committed, deterministic assets into a reusable library:

  * ``precedent.extractor.fingerprint`` — the sha256 class-key hash (RULE 2: a class
    match is field EQUALITY, never semantic similarity; no LLM is ever consulted here).
  * ``data/analysis/uci_match_rate.py`` — the chronological match-rate / precedented-median
    / standing-approval-coverage computation that produced the canonical corpus numbers.

Public surface:
  * :func:`precedent_analyzer.mapping.detect_and_map` — CSV → canonical records (+ source guess).
  * :func:`precedent_analyzer.analyze.analyze` — canonical records → :class:`AnalysisResult`.
  * :func:`precedent_analyzer.report.render_html` — result → self-contained local HTML.

DATA NEVER LEAVES THE MACHINE. Nothing in this package opens a socket; the sockets-disabled
test in tests/test_analyzer.py runs a full analysis with ``socket.socket`` monkeypatched to
raise and asserts it completes. There is NO funnel/telemetry instrumentation, by design.
"""

from precedent_analyzer.analyze import AnalysisResult, analyze
from precedent_analyzer.mapping import ColumnMapping, MappingError, detect_and_map

__all__ = [
    "AnalysisResult",
    "ColumnMapping",
    "MappingError",
    "analyze",
    "detect_and_map",
]
