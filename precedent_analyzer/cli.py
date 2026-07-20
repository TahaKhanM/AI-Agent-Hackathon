"""``precedent-analyze <export.csv>`` — read an incident export, measure the org's own
precedent profile locally, and write a self-contained HTML report.

Runnable via pipx / uv run / ``python -m precedent_analyzer``. No network, no telemetry:
the analysis never opens a socket (enforced by a sockets-disabled test).
"""

from __future__ import annotations

import argparse
import os
import sys

from precedent_analyzer.analyze import DEFAULT_LADDER_THRESHOLD, analyze
from precedent_analyzer.mapping import MappingError, detect_and_map
from precedent_analyzer.report import render_html


def _parse_overrides(pairs: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in pairs:
        if "=" not in p:
            raise MappingError(f"--map expects canonical=Header, got {p!r}")
        canonical, header = p.split("=", 1)
        out[canonical.strip()] = header.strip()
    return out


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="precedent-analyze",
        description="Measure how much of an incident export's resolution work is already "
        "precedented — locally, deterministically, with no data leaving the machine.",
    )
    ap.add_argument("csv", help="path to a ServiceNow / Jira / generic incident export (CSV)")
    ap.add_argument("-o", "--out", default=None,
                    help="output HTML path (default: <csv-basename>.precedent-report.html)")
    ap.add_argument("--map", action="append", default=[], metavar="canonical=Header",
                    help="override a column mapping, e.g. --map closed_code='Resolution' "
                    "(repeatable)")
    ap.add_argument("--ladder-threshold", type=int, default=DEFAULT_LADDER_THRESHOLD,
                    help=f"min occurrences for a standing-approval candidate "
                    f"(default {DEFAULT_LADDER_THRESHOLD})")
    ap.add_argument("--quiet", action="store_true", help="suppress the summary printout")
    return ap


def run(argv: list[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    try:
        overrides = _parse_overrides(args.map)
        records, mapping = detect_and_map(args.csv, overrides=overrides)
        result = analyze(
            records, source=mapping.source, ladder_threshold=args.ladder_threshold
        )
    except MappingError as exc:
        print(f"precedent-analyze: {exc}", file=sys.stderr)
        return 2

    source_name = os.path.basename(args.csv)
    out_path = args.out or (os.path.splitext(args.csv)[0] + ".precedent-report.html")
    html = render_html(result, source_name=source_name)
    try:
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(html)
    except OSError as exc:
        print(f"precedent-analyze: could not write {out_path}: {exc}", file=sys.stderr)
        return 2

    if not args.quiet:
        print(mapping.describe(), file=sys.stderr)
        print(f"\nAnalyzed {result.total_rows} rows "
              f"({result.valid_fingerprint_rows} with a complete fix-class fingerprint).")
        if result.fix_class_match_rate is not None:
            print(f"  Fix-class match rate (existence):     {result.fix_class_match_rate}%")
        if result.symptom_class_match_rate is not None:
            print(f"  Symptom-class match rate (arrival):   {result.symptom_class_match_rate}%")
        if result.precedented_median_res_h is not None:
            print(f"  Median precedented repeat (calendar): {result.precedented_median_res_h} h")
        print(f"  Standing-approval candidates:         {result.ladder_class_count} classes"
              + (f" ({result.ladder_volume_share}% of volume)"
                 if result.ladder_volume_share is not None else ""))
        for w in result.warnings:
            print(f"  ! {w}", file=sys.stderr)
        print(f"\nReport written to {out_path} (no data left this machine).")
    return 0


def main() -> None:  # console_scripts entry point
    raise SystemExit(run())


if __name__ == "__main__":
    main()
