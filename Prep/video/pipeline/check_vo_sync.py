#!/usr/bin/env python3
"""V1 cross-check: prove the voice-over never forks again.  [Prompts/08 video pipeline]

Asserts, for every shot 1-8, that the narration is word-identical across THREE surfaces:
  - Prep/video/pipeline/vo_canonical.json   (the source of truth)
  - Prep/video/shot-list.md                 (the picture-paired VO cues)
  - Prep/video/vo-script.md                 (the narration read by a human / TTS)
"Word-identical" = equal after typography + whitespace normalisation (curly quotes,
dashes, ellipses collapsed; runs of whitespace → one space). This is the mechanical guard
behind KNOWN DEFECT 1 (the vo-script ↔ shot-list fork).

Also enforces, on the canonical VO:
  - banned words absent:  "Watcher" (04 §0 stage-language), "autonomous" (L3 rename)
  - both memorable lines present verbatim ("the second time is free" / "it knows what it's
    not allowed to touch")
  - no pinned model id (rule 1) — read live from precedent/models.py, never hard-coded here

Exit 0 = all green; exit 1 = a fork/violation (prints the offending shot). No network, no LLM.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "Prep/video/pipeline/vo_canonical.json"
SHOTLIST = ROOT / "Prep/video/shot-list.md"
VOSCRIPT = ROOT / "Prep/video/vo-script.md"
MODELS = ROOT / "precedent/models.py"

SHOTS = [str(n) for n in range(1, 9)]  # shot 0 has no VO


def norm(s: str) -> str:
    """Typography + whitespace normalisation. Words must survive; punctuation drift must not."""
    if s is None:
        return ""
    s = s.replace("’", "'").replace("‘", "'")          # curly single → '
    s = s.replace("“", '"').replace("”", '"')          # curly double → "
    s = s.replace("—", "-").replace("–", "-")          # em/en dash → -
    s = s.replace("…", "...")                                # ellipsis → ...
    s = s.strip().strip('"').strip()
    s = re.sub(r"\s+", " ", s)
    return s


def extract_shotlist_vo(text: str) -> dict[str, str]:
    """VO cues are single lines: - **VO cue (`VO_shotN`):** "text"  (text may hold inline **bold**)."""
    out: dict[str, str] = {}
    for m in re.finditer(r"`VO_shot(\d)`\)\:\*\*\s*(.+)", text):
        n, body = m.group(1), m.group(2)
        body = body.replace("**", "")            # drop inline bold emphasis
        out[n] = norm(body)
    return out


def extract_voscript_vo(text: str) -> dict[str, str]:
    """Each `## Shot N …` heading is followed by the VO as consecutive `>` blockquote lines."""
    out: dict[str, str] = {}
    cur: str | None = None
    buf: list[str] = []

    def flush() -> None:
        nonlocal cur, buf
        if cur is not None and cur in SHOTS:
            joined = " ".join(buf)
            joined = joined.replace("**", "")
            out[cur] = norm(joined)
        cur, buf = None, []

    for line in text.splitlines():
        h = re.match(r"^##\s+Shot\s+(\d)\b", line)
        if h:
            flush()
            cur = h.group(1)
            continue
        if cur is not None and line.lstrip().startswith(">"):
            frag = line.lstrip()[1:].strip()
            # drop pure stage-direction lines like *(time-lapse begins…)*
            if re.fullmatch(r"\*\(.*\)\*", frag):
                continue
            buf.append(frag)
    flush()
    return out


def pinned_model_ids() -> list[str]:
    if not MODELS.exists():
        return []
    txt = MODELS.read_text(encoding="utf-8")
    # heuristic: quoted lowercase tokens with a digit and a '-'/':'/'/' separator — the shape of a
    # served model id (qwen3-6-27b, deepseek-v4-flash, qwen3:8b, text-embedding-qwen3-0-6b, …).
    # URLs/paths excluded. Over-collecting only makes the "must NOT appear in VO" guard stricter.
    ids = set()
    for m in re.finditer(r"""["']([a-z0-9][a-z0-9_.:\-/]{3,39})["']""", txt):
        cand = m.group(1)
        if "://" in cand or cand.startswith(("http", "/", "./")) or cand.endswith((".py", ".json")):
            continue
        if not re.search(r"\d", cand):          # a served id carries a version digit
            continue
        if not re.search(r"[:\-/]", cand):        # …and a separator
            continue
        ids.add(cand)
    return sorted(ids)


def main() -> int:
    canon = json.loads(CANON.read_text(encoding="utf-8"))["shots"]
    sl = extract_shotlist_vo(SHOTLIST.read_text(encoding="utf-8"))
    vs = extract_voscript_vo(VOSCRIPT.read_text(encoding="utf-8"))

    fails: list[str] = []
    print("=== VO sync (canonical ≡ shot-list ≡ vo-script), per shot ===")
    for n in SHOTS:
        c, a, b = norm(canon.get(n, "")), sl.get(n, "<MISSING>"), vs.get(n, "<MISSING>")
        ok = (c == a == b)
        print(f"  shot {n}: {'OK ' if ok else 'FAIL'}  "
              f"[canon={len(c)}c shot-list={'∥' if a==c else '≠'} vo-script={'∥' if b==c else '≠'}]")
        if not ok:
            fails.append(n)
            if a != c:
                print(f"      shot-list≠canon:\n        canon: {c[:160]}\n        list : {a[:160]}")
            if b != c:
                print(f"      vo-script≠canon:\n        canon: {c[:160]}\n        vo   : {b[:160]}")

    print("\n=== banned words in canonical VO ===")
    joined = " ".join(canon.values()).lower()
    for word in ("watcher", "autonomous"):
        hit = re.search(rf"\b{word}\b", joined)
        print(f"  '{word}': {'FOUND ✗' if hit else 'absent ✓'}")
        if hit:
            fails.append(f"banned:{word}")

    print("\n=== memorable lines present (verbatim, normalised) ===")
    alltext = norm(" ".join(canon.values())).lower()
    for line in ("the second time is free", "it knows what it's not allowed to touch"):
        present = norm(line).lower() in alltext
        print(f"  '{line}': {'present ✓' if present else 'MISSING ✗'}")
        if not present:
            fails.append(f"memorable:{line}")

    print("\n=== pinned model ids absent from VO (rule 1) ===")
    ids = pinned_model_ids()
    print(f"  ids pinned in precedent/models.py: {ids or '(none parsed)'}")
    for mid in ids:
        if mid.lower() in alltext:
            print(f"  model id LEAKED into VO: {mid} ✗")
            fails.append(f"modelid:{mid}")
    if all(mid.lower() not in alltext for mid in ids):
        print("  no pinned model id appears in any VO ✓")

    print()
    if fails:
        print(f"RESULT: FAIL ({len(fails)} issue(s): {fails})")
        return 1
    print(f"RESULT: PASS — all {len(SHOTS)} shots in sync; banned words clean; both memorable lines present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
