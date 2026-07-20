"""Deterministic, LLM-free analysis of an org's incident history.

Generalises ``data/analysis/uci_match_rate.py`` into a reusable function and keys every
class on ``precedent.extractor.fingerprint`` (RULE 2: a class is FIELD EQUALITY, hashed —
never semantic similarity, never a model call). Given canonical records it computes the
org's OWN:

  * fix-class match rate (EXISTENCE — the key includes the resolution code, known only at
    close; "the exact fix had been applied before");
  * symptom-class match rate (ARRIVAL-KNOWABLE — category+subcategory only);
  * precedented-repeat median resolution time (CALENDAR hours) + first-of-class median;
  * standing-approval candidate classes (recur >= threshold times) and their volume share.

The chronological rule matches the corpus script exactly: a precedent counts only if a
prior incident (earlier ``opened_at``) carried the same fingerprint. Sorting is stable, so
feeding the committed per-incident records reproduces 94.4% / 98.6% / 18.2 h / 558
byte-for-byte.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from statistics import median

import numpy as np

from precedent.contracts import Extracted
from precedent.extractor import fingerprint


def _r1(x: float) -> float:
    """Round to 1 dp exactly as the corpus baseline did (numpy), so 18.15 -> 18.2."""
    return float(np.round(x, 1))


def _r3(x: float) -> float:
    return float(np.round(x, 3))

# Resolution-time outlier window used by the corpus baseline: drop negatives and anything
# over 90 calendar days, so a handful of stuck tickets don't distort the median.
_MAX_RES_H = 24 * 90
# A class needs at least this many resolved occurrences to be a standing-approval candidate.
DEFAULT_LADDER_THRESHOLD = 4


def _fp(category: str, closed_code: str, subcategory: str) -> str:
    """Fix-class fingerprint (EXISTENCE key) via the shared deterministic extractor."""
    return fingerprint(
        Extracted(service=category, error_code=closed_code, target_object_type=subcategory)
    )


def _sfp(category: str, subcategory: str) -> str:
    """Symptom-class fingerprint (ARRIVAL-knowable key): category+subcategory, no code."""
    return fingerprint(
        Extracted(service=category, error_code="", target_object_type=subcategory)
    )


@dataclass
class LadderClass:
    """A standing-approval candidate: a recurring fix class and its volume."""

    category: str
    subcategory: str
    closed_code: str
    count: int
    median_res_h: float | None


@dataclass
class AnalysisResult:
    source: str
    total_rows: int
    valid_fingerprint_rows: int
    distinct_fix_classes: int
    distinct_symptom_classes: int
    fix_class_match_rate: float | None          # EXISTENCE, %
    symptom_class_match_rate: float | None       # ARRIVAL-knowable, %
    precedented_median_res_h: float | None       # CALENDAR hours
    precedented_p75_res_h: float | None
    first_of_class_median_res_h: float | None
    duration_sample: int                         # rows with a usable resolution time
    sla_breach_share: float | None               # among precedented repeats
    reassigned_share: float | None               # among precedented repeats
    ladder_threshold: int
    ladder_class_count: int
    ladder_volume_share: float | None            # % of valid-fingerprint volume
    top_candidates: list[LadderClass] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_uci_reproduction(self) -> bool:
        """True when the four canonical corpus numbers are hit (guards the report caveat)."""
        return (
            self.valid_fingerprint_rows == 24805
            and self.fix_class_match_rate == 94.4
            and self.symptom_class_match_rate == 98.6
            and self.precedented_median_res_h == 18.2
            and self.ladder_class_count == 558
        )


def _field(value: object) -> str | None:
    """Coerce a raw field to a non-empty string, or None. Guards against float NaN (which
    is truthy) so records fed straight from a DataFrame behave like mapper-cleaned ones."""
    if value is None:
        return None
    if isinstance(value, float) and value != value:  # NaN
        return None
    s = str(value).strip()
    return s or None


def _res_hours(opened: datetime | None, resolved: datetime | None) -> float | None:
    if opened is None or resolved is None:
        return None
    return (resolved - opened).total_seconds() / 3600.0


def _pct(numer: int, denom: int) -> float | None:
    return _r1(100.0 * numer / denom) if denom else None


def _p75(values: list[float]) -> float | None:
    if not values:
        return None
    s = sorted(values)
    # linear-interpolation percentile (matches numpy/pandas default) at q=0.75
    idx = 0.75 * (len(s) - 1)
    lo = int(idx)
    frac = idx - lo
    if lo + 1 < len(s):
        return _r1(s[lo] + frac * (s[lo + 1] - s[lo]))
    return _r1(s[lo])


def analyze(
    records: list[dict],
    *,
    source: str = "generic",
    ladder_threshold: int = DEFAULT_LADDER_THRESHOLD,
    top_n: int = 15,
) -> AnalysisResult:
    """Compute the org's precedent profile from canonical records (see mapping.py)."""
    total = len(records)
    warnings: list[str] = []

    # Keep only rows with a complete fix-class fingerprint (category+subcategory+closed_code),
    # then order chronologically. Rows missing opened_at sort last (deterministically) and can
    # never BE a prior precedent, matching the corpus treatment of incomplete rows.
    valid = [
        r for r in records
        if _field(r.get("category")) and _field(r.get("subcategory"))
        and _field(r.get("closed_code"))
    ]
    if not valid:
        warnings.append(
            "No rows had a complete category+subcategory+resolution-code fingerprint; "
            "match rates cannot be computed. Check the column mapping."
        )

    _MAX_DT = datetime.max
    ordered = sorted(valid, key=lambda r: (r.get("opened_at") is None,
                                           r.get("opened_at") or _MAX_DT))

    seen_fp: set[str] = set()
    seen_sfp: set[str] = set()
    fp_matched = 0
    sfp_matched = 0
    fp_counter: Counter[str] = Counter()
    class_meta: dict[str, tuple[str, str, str]] = {}
    class_res: dict[str, list[float]] = {}

    prec_res: list[float] = []          # resolution hours of precedented repeats (in-window)
    firstclass_res: list[float] = []    # resolution hours of first-of-class (in-window)
    prec_sla_breach = 0
    prec_sla_known = 0
    prec_reassigned = 0
    prec_reassign_known = 0
    duration_sample = 0

    for r in ordered:
        cat = _field(r["category"])
        sub = _field(r["subcategory"])
        code = _field(r["closed_code"])
        fkey = _fp(cat, code, sub)
        skey = _sfp(cat, sub)
        is_repeat = fkey in seen_fp
        if is_repeat:
            fp_matched += 1
        if skey in seen_sfp:
            sfp_matched += 1

        rh = _res_hours(r.get("opened_at"), r.get("resolved_at"))
        in_window = rh is not None and 0 <= rh <= _MAX_RES_H
        if in_window:
            duration_sample += 1
            (prec_res if is_repeat else firstclass_res).append(rh)
            class_res.setdefault(fkey, []).append(rh)
            if is_repeat:
                sla = r.get("made_sla")
                if sla is not None:
                    prec_sla_known += 1
                    if sla is False:
                        prec_sla_breach += 1
                rc = r.get("reassignment_count")
                if rc is not None:
                    prec_reassign_known += 1
                    if rc > 0:
                        prec_reassigned += 1

        fp_counter[fkey] += 1
        class_meta[fkey] = (cat, sub, code)
        seen_fp.add(fkey)
        seen_sfp.add(skey)

    n_valid = len(ordered)
    ladder_keys = [k for k, c in fp_counter.items() if c >= ladder_threshold]
    ladder_volume = sum(fp_counter[k] for k in ladder_keys)

    def _class_median(k: str) -> float | None:
        vals = class_res.get(k)
        return _r1(median(vals)) if vals else None

    top = sorted(ladder_keys, key=lambda k: (-fp_counter[k], class_meta[k]))[:top_n]
    top_candidates = [
        LadderClass(*class_meta[k], count=fp_counter[k], median_res_h=_class_median(k))
        for k in top
    ]

    if valid and duration_sample == 0:
        warnings.append(
            "No usable resolution durations (opened_at/resolved_at missing or unparseable); "
            "median resolution time is unavailable."
        )

    return AnalysisResult(
        source=source,
        total_rows=total,
        valid_fingerprint_rows=n_valid,
        distinct_fix_classes=len(fp_counter),
        distinct_symptom_classes=len(seen_sfp),
        fix_class_match_rate=_pct(fp_matched, n_valid),
        symptom_class_match_rate=_pct(sfp_matched, n_valid),
        precedented_median_res_h=_r1(median(prec_res)) if prec_res else None,
        precedented_p75_res_h=_p75(prec_res),
        first_of_class_median_res_h=_r1(median(firstclass_res)) if firstclass_res else None,
        duration_sample=duration_sample,
        sla_breach_share=(_r3(prec_sla_breach / prec_sla_known)
                          if prec_sla_known else None),
        reassigned_share=(_r3(prec_reassigned / prec_reassign_known)
                          if prec_reassign_known else None),
        ladder_threshold=ladder_threshold,
        ladder_class_count=len(ladder_keys),
        ladder_volume_share=_pct(ladder_volume, n_valid),
        top_candidates=top_candidates,
        warnings=warnings,
    )
