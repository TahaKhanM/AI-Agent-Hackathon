"""Render an :class:`AnalysisResult` to a single self-contained HTML file.

The report is headlined for the Gate buyer ("how much of your resolution work is already
precedented?") and PRINTS the honesty caveats on the page itself, because the whole pitch
is that Precedent's numbers survive a sharp reader:

  * the fix-class rate is an EXISTENCE claim (its key includes the resolution code, known
    only at close) — not what a triage system could match at arrival;
  * the symptom-class rate is the ARRIVAL-knowable companion (category+subcategory only);
  * every median is CALENDAR hours (no business-hours calendar in a raw export) — never
    blended with an industry business-hours MTTR;
  * standing-approval candidates are a FREQUENCY FLOOR (a class recurs N+ times), NOT a
    product-accuracy claim — execution still requires extractor-confirmed field equality.

Design tokens are inlined from the console stylesheet so the file renders identically with
no network access. Everything is escaped; the file is safe to open locally.
"""

from __future__ import annotations

import html
from datetime import UTC, datetime

from precedent_analyzer.analyze import AnalysisResult

# Canonical corpus reference numbers (docs/numbers.md) — printed as the labelled benchmark
# alongside the org's own figures so a reader can calibrate. Kept verbatim, with labels.
_CANON = {
    "fix": "94.4% (existence)",
    "sym": "98.6% (arrival-knowable)",
    "median": "18.2 h (calendar)",
    "ladder": "558 classes >= 4 occ -> 94.8% of volume",
    "floor": "top-1 59.4% / top-3 87.7% (naive floor, not product accuracy)",
}

_CSS = """
:root{--paper:#F1F1E2;--paper-2:#F7F6EC;--card:#FBFAF2;--ink:#2A2A48;--indigo:#3C3B62;
--indigo-lo:#56547e;--line:#D8D5C2;--line-2:#E6E3D2;--muted:#6C6A80;--oxblood:#8C3A49;
--oxblood-bg:#F3E5E7;--oxblood-line:#E1C3C8;--gold:#A9853B;
--serif:"Hoefler Text","Iowan Old Style",Palatino,Georgia,"Times New Roman",serif;
--sans:ui-sans-serif,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",sans-serif;
--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 var(--serif);
-webkit-font-smoothing:antialiased;padding:0 0 60px}
.wrap{max-width:960px;margin:0 auto;padding:0 24px}
header{background:linear-gradient(90deg,var(--indigo),var(--indigo-lo));color:#F4F3EA;
padding:26px 0;margin-bottom:34px}
header .wrap{display:flex;align-items:baseline;justify-content:space-between;
flex-wrap:wrap;gap:10px}
.name{font:600 22px/1 var(--serif);letter-spacing:4px}
.tag{font-family:var(--sans);font-size:11px;letter-spacing:2.4px;text-transform:uppercase;
color:#D7D5EC}
h1{font-size:30px;line-height:1.16;margin:0 0 8px}
.lede{font-size:17px;color:#3a3952;max-width:66ch;margin:0 0 26px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
gap:16px;margin:0 0 30px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:18px 20px;
box-shadow:0 1px 0 #fff inset,0 6px 20px -16px rgba(42,42,72,.5)}
.stat .k{font-family:var(--sans);font-size:11px;letter-spacing:1.6px;text-transform:uppercase;
color:var(--indigo);font-weight:700}
.stat .v{font:600 34px/1.05 var(--serif);color:var(--ink);margin:8px 0 4px}
.stat .v small{font-size:16px;font-weight:400;color:var(--muted)}
.stat .lbl{font-family:var(--sans);font-size:11.5px;color:var(--muted);line-height:1.45}
.stat .na{font-size:22px;color:var(--muted)}
h2{font-size:15px;font-family:var(--sans);letter-spacing:2px;text-transform:uppercase;
color:var(--indigo);margin:34px 0 12px;border-bottom:1px solid var(--line-2);padding-bottom:6px}
.caveat{background:var(--oxblood-bg);border:1px solid var(--oxblood-line);border-radius:6px;
padding:14px 18px;margin:0 0 16px}
.caveat ul{margin:6px 0 0;padding-left:20px}
.caveat li{font-size:14px;color:#4a2a30;margin:5px 0;font-family:var(--sans);line-height:1.5}
.caveat b{color:var(--oxblood)}
table{width:100%;border-collapse:collapse;font-size:14px;margin:0 0 10px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line-2)}
th{font-family:var(--sans);font-size:11px;letter-spacing:1px;text-transform:uppercase;
color:var(--indigo)}
td.n{font-family:var(--mono);text-align:right}
.bench{font-family:var(--sans);font-size:12px;color:var(--muted)}
.bench td,.bench th{padding:6px 10px}
footer{margin-top:34px;padding-top:16px;border-top:2px solid var(--gold);
font-family:var(--sans);font-size:12px;color:var(--muted);line-height:1.6}
.seal{color:var(--gold);font-weight:700}
.warn{background:#FBF6E6;border:1px solid #E8DBA8;border-radius:6px;padding:12px 16px;
font-family:var(--sans);font-size:13px;color:#6a5a20;margin:0 0 16px}
"""


def _stat(key: str, value: str | None, label: str, *, unit: str = "") -> str:
    if value is None:
        body = '<div class="v na">not available</div>'
    else:
        u = f"<small>{html.escape(unit)}</small>" if unit else ""
        body = f'<div class="v">{html.escape(value)}{u}</div>'
    return (
        f'<div class="stat"><div class="k">{html.escape(key)}</div>{body}'
        f'<div class="lbl">{label}</div></div>'
    )


def _fmt(x: float | None, suffix: str = "") -> str | None:
    if x is None:
        return None
    s = f"{x:g}"
    return s + suffix


def render_html(
    result: AnalysisResult, *, source_name: str = "your export"
) -> str:
    r = result
    generated = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    stats = "".join([
        _stat(
            "Fix-class match rate",
            _fmt(r.fix_class_match_rate, "%"),
            "EXISTENCE — the exact fix (category + subcategory + resolution code) had already "
            "resolved a prior incident. Key includes the close code, known only at resolution.",
        ),
        _stat(
            "Symptom-class match rate",
            _fmt(r.symptom_class_match_rate, "%"),
            "ARRIVAL-KNOWABLE — category + subcategory only; what a triage system can see the "
            "moment the ticket lands.",
        ),
        _stat(
            "Median resolution, precedented repeats",
            _fmt(r.precedented_median_res_h),
            "CALENDAR hours. Even with precedent, the median repeat still took this long — "
            "retrieval, not resolution, is the bottleneck.",
            unit=" h",
        ),
        _stat(
            "Standing-approval candidates",
            (str(r.ladder_class_count) if r.ladder_class_count else None),
            f"Fix classes recurring &ge; {r.ladder_threshold} times"
            + (f", covering {r.ladder_volume_share:g}% of volume"
               if r.ladder_volume_share is not None else "")
            + ". A frequency FLOOR, not a product-accuracy claim.",
        ),
    ])

    # Supporting figures row
    support_rows = ""
    for label, val in [
        ("Rows analyzed", str(r.total_rows)),
        ("Complete-fingerprint rows", str(r.valid_fingerprint_rows)),
        ("Distinct fix classes", str(r.distinct_fix_classes)),
        ("Distinct symptom classes", str(r.distinct_symptom_classes)),
        ("Resolution-time sample", str(r.duration_sample)),
        ("p75 resolution (calendar h)", _fmt(r.precedented_p75_res_h) or "n/a"),
        ("First-of-class median (calendar h)", _fmt(r.first_of_class_median_res_h) or "n/a"),
        ("SLA-breach share, precedented",
         f"{r.sla_breach_share:g}" if r.sla_breach_share is not None else "n/a"),
        ("Reassigned &ge;1x share, precedented",
         f"{r.reassigned_share:g}" if r.reassigned_share is not None else "n/a"),
    ]:
        support_rows += f"<tr><td>{label}</td><td class='n'>{html.escape(str(val))}</td></tr>"

    cand_rows = ""
    for c in r.top_candidates:
        med = _fmt(c.median_res_h) or "&mdash;"
        cand_rows += (
            "<tr>"
            f"<td>{html.escape(c.category)}</td>"
            f"<td>{html.escape(c.subcategory)}</td>"
            f"<td>{html.escape(c.closed_code)}</td>"
            f"<td class='n'>{c.count}</td>"
            f"<td class='n'>{med}</td>"
            "</tr>"
        )
    if not cand_rows:
        cand_rows = "<tr><td colspan='5'>No class recurred often enough to qualify.</td></tr>"

    warn_html = ""
    if r.warnings:
        items = "".join(f"<div>&#9888; {html.escape(w)}</div>" for w in r.warnings)
        warn_html = f'<div class="warn">{items}</div>'

    repro_note = ""
    if r.is_uci_reproduction:
        repro_note = (
            '<div class="bench" style="margin:-6px 0 18px">Verified: these figures reproduce '
            'the committed UCI baseline (dataset #498) byte-for-byte.</div>'
        )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Precedent Analyzer &mdash; {html.escape(source_name)}</title>
<style>{_CSS}</style></head><body>
<header><div class="wrap">
  <div class="name">PRECEDENT</div>
  <div class="tag">Local precedent analysis</div>
</div></header>
<div class="wrap">
  <h1>How much of your resolution work is already precedented?</h1>
  <p class="lede">Computed locally from <b>{html.escape(source_name)}</b>
  ({html.escape(r.source)} export, {r.total_rows:,} rows). The precedent almost always
  exists &mdash; it just isn't operational. These are <b>your</b> numbers, measured the same
  deterministic way Precedent keys its fast-path: field equality on a hashed class
  fingerprint, never semantic similarity, never a model call.</p>
  {repro_note}
  {warn_html}
  <div class="grid">{stats}</div>

  <h2>How to read these numbers</h2>
  <div class="caveat">
    <ul>
      <li><b>Fix-class rate = existence, not arrival.</b> Its key includes the resolution
        code, which is only known when the ticket closes. It says the fix had been applied
        before &mdash; not that a triage system could have matched it at arrival. For that,
        read the <b>symptom-class</b> rate.</li>
      <li><b>All medians are CALENDAR hours.</b> A raw export carries no business-hours
        calendar, so these are wall-clock. Never average or swap them with a business-hours
        industry MTTR &mdash; different clocks.</li>
      <li><b>Standing-approval candidates are a frequency FLOOR.</b> A class qualifying just
        means it recurred often; it is <b>not</b> a product-accuracy claim. Execution still
        requires extractor-confirmed field equality, so the model can never unlock a
        fast-path on similarity alone.</li>
    </ul>
    <div class="bench" style="margin-top:10px">Reference benchmark (UCI #498, docs/numbers.md,
    labelled): fix-class {_CANON['fix']} &middot; symptom {_CANON['sym']} &middot; precedented
    median {_CANON['median']} &middot; ladder {_CANON['ladder']} &middot; arrival naive floor
    {_CANON['floor']}.</div>
  </div>

  <h2>Supporting figures</h2>
  <table>{support_rows}</table>

  <h2>Top standing-approval candidate classes</h2>
  <table>
    <tr><th>Category</th><th>Subcategory</th><th>Resolution code</th><th>Occurrences</th>
    <th>Median h</th></tr>
    {cand_rows}
  </table>

  <footer>
    <span class="seal">&#9863;</span> Generated {generated} &mdash; entirely on this machine.
    <b>No data left this device.</b> The analyzer opens no network sockets and carries no
    telemetry. Class fingerprints are computed by the shared deterministic extractor
    (sha256 of category|resolution-code|subcategory), the same LLM-free key that gates
    execution. Durations are calendar hours.
  </footer>
</div></body></html>"""
