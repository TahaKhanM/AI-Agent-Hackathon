"""Column mapping + auto-detection for ServiceNow, Jira and generic incident exports.

The analyzer works on a small set of CANONICAL fields:

    incident_id, category, subcategory, closed_code, opened_at, resolved_at
    (+ optional: team, made_sla, reassignment_count)

``detect_and_map`` reads a CSV header, guesses the source flavour and a column mapping by
name (synonym match, case/spacing/punctuation-insensitive), and returns canonicalised
records. The caller may override any mapping explicitly (``--map canonical=Header``). All
parsing is local, deterministic and LLM-free — a header the analyzer cannot understand
raises :class:`MappingError` with a helpful message, never a traceback.
"""

from __future__ import annotations

import csv
import io
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime

# Canonical fields the analysis core understands.
REQUIRED_FIELDS = ("category", "subcategory", "closed_code", "opened_at", "resolved_at")
OPTIONAL_FIELDS = ("incident_id", "team", "made_sla", "reassignment_count")
CANONICAL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS

# Synonyms per canonical field. Order matters only for reporting the chosen header; the
# match itself is exact (after normalisation), so a Jira "Components" maps to category and
# a ServiceNow "category" maps to category without either stealing the other's rows.
_SYNONYMS: dict[str, tuple[str, ...]] = {
    "category": ("category", "components", "component", "issue type", "issuetype",
                 "type", "service", "ci class"),
    "subcategory": ("subcategory", "sub category", "labels", "label", "module",
                    "u symptom", "symptom", "area"),
    "closed_code": ("closed code", "close code", "resolution", "resolution code",
                    "root cause", "cause code", "cause", "close notes code"),
    "opened_at": ("opened at", "opened", "created", "created date", "open time",
                  "reported", "sys created at", "date opened"),
    "resolved_at": ("resolved at", "resolved", "resolved date", "resolution date",
                    "closed at", "closed", "date resolved", "end time"),
    "incident_id": ("number", "issue key", "key", "id", "incident id", "ticket",
                    "ticket id", "sys id"),
    "team": ("assignment group", "assigned team", "assignment_group", "project",
             "team", "group", "queue"),
    "made_sla": ("made sla", "sla met", "sla", "met sla"),
    "reassignment_count": ("reassignment count", "reassignments", "reassignment_count",
                           "times reassigned"),
}

# Date formats tried in order (deterministic). UCI/ServiceNow use day-first "%d/%m/%Y %H:%M".
_DATE_FORMATS = (
    "%d/%m/%Y %H:%M",
    "%d/%m/%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
    "%m/%d/%Y %H:%M",
    "%d/%m/%Y",
)

_NULLISH = {"", "?", "nan", "none", "null", "n/a", "na", "-", "unknown"}


class MappingError(ValueError):
    """Raised for a CSV the analyzer cannot understand. Message is user-facing."""


@dataclass
class ColumnMapping:
    """Resolved canonical-field -> source-header mapping, plus the detected source name."""

    source: str
    columns: dict[str, str] = field(default_factory=dict)

    def describe(self) -> str:
        rows = [f"  {k:<20} <- {v!r}" for k, v in self.columns.items()]
        return f"source detected: {self.source}\n" + "\n".join(rows)


def _norm_header(h: str) -> str:
    """Lowercase, strip, collapse punctuation/space so 'Closed_Code' == 'closed code'."""
    return re.sub(r"[\s_\-./]+", " ", (h or "").strip().lower()).strip()


def _nullish(v: object) -> bool:
    return v is None or (isinstance(v, str) and v.strip().lower() in _NULLISH)


def _detect_source(headers: list[str]) -> str:
    norm = {_norm_header(h) for h in headers}
    if {"issue key", "issue type"} & norm or "issuetype" in norm:
        return "jira"
    if {"sys id", "number"} & norm and ("closed code" in norm or "u symptom" in norm):
        return "servicenow"
    if "number" in norm and "category" in norm:
        return "servicenow"
    return "generic"


def _auto_map(headers: list[str], overrides: dict[str, str] | None) -> ColumnMapping:
    overrides = overrides or {}
    source = _detect_source(headers)
    norm_to_original: dict[str, str] = {}
    for h in headers:
        norm_to_original.setdefault(_norm_header(h), h)

    columns: dict[str, str] = {}
    for canonical in CANONICAL_FIELDS:
        if canonical in overrides:
            chosen = overrides[canonical]
            if chosen not in headers:
                raise MappingError(
                    f"--map {canonical}={chosen!r}: no such column. Available columns: "
                    + ", ".join(repr(h) for h in headers)
                )
            columns[canonical] = chosen
            continue
        for syn in _SYNONYMS[canonical]:
            if syn in norm_to_original:
                columns[canonical] = norm_to_original[syn]
                break

    missing = [f for f in REQUIRED_FIELDS if f not in columns]
    if missing:
        raise MappingError(
            "Could not auto-detect these required columns: "
            + ", ".join(missing)
            + ".\nColumns found in the file: "
            + ", ".join(repr(h) for h in headers)
            + "\nMap them explicitly, e.g. --map closed_code='Resolution' "
            "--map opened_at='Created'."
        )
    return ColumnMapping(source=source, columns=columns)


def _parse_dt(value: object) -> datetime | None:
    if _nullish(value):
        return None
    s = str(value).strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    # last resort: ISO-ish fromisoformat (handles fractional seconds / offsets)
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _clean_str(value: object) -> str | None:
    if _nullish(value):
        return None
    return str(value).strip()


def _to_records(rows: Iterable[dict], mapping: ColumnMapping) -> list[dict]:
    cols = mapping.columns
    out: list[dict] = []
    for i, row in enumerate(rows):
        rec = {
            "incident_id": (row.get(cols["incident_id"]).strip()
                            if cols.get("incident_id") and row.get(cols["incident_id"])
                            else f"row-{i}"),
            "category": _clean_str(row.get(cols["category"])),
            "subcategory": _clean_str(row.get(cols["subcategory"])),
            "closed_code": _clean_str(row.get(cols["closed_code"])),
            "opened_at": _parse_dt(row.get(cols["opened_at"])),
            "resolved_at": _parse_dt(row.get(cols["resolved_at"])),
            "team": _clean_str(row.get(cols["team"])) if cols.get("team") else None,
        }
        rec["made_sla"] = _parse_bool(row.get(cols["made_sla"])) if cols.get("made_sla") else None
        rec["reassignment_count"] = (
            _parse_int(row.get(cols["reassignment_count"]))
            if cols.get("reassignment_count") else None
        )
        out.append(rec)
    return out


def _parse_bool(value: object) -> bool | None:
    if _nullish(value):
        return None
    s = str(value).strip().lower()
    if s in {"true", "1", "yes", "y", "met"}:
        return True
    if s in {"false", "0", "no", "n", "breached", "missed"}:
        return False
    return None


def _parse_int(value: object) -> int | None:
    if _nullish(value):
        return None
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return None


def detect_and_map(
    text_or_path: str,
    *,
    is_path: bool = True,
    overrides: dict[str, str] | None = None,
) -> tuple[list[dict], ColumnMapping]:
    """Read a CSV (path or literal text), auto-detect the mapping and return
    (canonical_records, mapping). Raises :class:`MappingError` for anything unusable."""
    if is_path:
        try:
            with open(text_or_path, newline="", encoding="utf-8-sig") as fh:
                raw = fh.read()
        except FileNotFoundError as exc:
            raise MappingError(f"File not found: {text_or_path}") from exc
        except UnicodeDecodeError as exc:
            raise MappingError(
                f"{text_or_path}: not valid UTF-8 text — is this really a CSV export?"
            ) from exc
    else:
        raw = text_or_path

    if not raw.strip():
        raise MappingError("The file is empty — nothing to analyze.")

    where = text_or_path if is_path else "the CSV input"
    reader = csv.DictReader(io.StringIO(raw))
    try:
        fieldnames = reader.fieldnames
    except csv.Error as exc:
        raise MappingError(
            f"{where}: could not parse the CSV header ({exc}). "
            "Is this a valid CSV export, with the right delimiter?"
        ) from exc
    if not fieldnames:
        raise MappingError("Could not read a header row from the file.")
    headers = [h for h in fieldnames if h is not None]
    mapping = _auto_map(headers, overrides)
    try:
        rows = list(reader)
    except csv.Error as exc:
        # e.g. a field larger than csv.field_size_limit(), or an unterminated quote. The
        # reader tracks the physical line it failed on; surface it so the user can fix it.
        raise MappingError(
            f"{where}: could not parse CSV data at line {reader.line_num} ({exc}). "
            "A field may be malformed or larger than the CSV field-size limit."
        ) from exc
    if not rows:
        raise MappingError("The file has a header but no data rows.")
    return _to_records(rows, mapping), mapping
