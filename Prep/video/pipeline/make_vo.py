#!/usr/bin/env python3
"""V4 VO synthesis — scratch narration from the canonical script via macOS `say`. [Prompts/08]

No ELEVENLABS_API_KEY → this produces a `say`-based scratch track (for timing + a watchable
master) AND the human recording kit is written separately. The TTS input is the canonical VO
text VERBATIM (vo_canonical.json), so it can never drift from the reconciled script.

Per shot: say -> AIFF -> loudnorm'd mono 48k WAV in precedent-video-drop/vo/. Reports each
stem's duration against the shot's slot budget (±1.5s tolerance the harness checks).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = json.loads((ROOT / "Prep/video/pipeline/vo_canonical.json").read_text())
VO = CANON["shots"]
SLOTS = CANON["slot_seconds"]
OUT = ROOT / "precedent-video-drop/vo"
SCRATCH = ROOT / "precedent-video-drop/scratch/vo-aiff"
VOICE = sys.argv[1] if len(sys.argv) > 1 else "Daniel"
RATE = sys.argv[2] if len(sys.argv) > 2 else "162"   # wpm — calm


def dur(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    print(f"voice={VOICE} rate={RATE}wpm  (canonical VO fed verbatim → no drift possible)")
    rows = []
    for n in map(str, range(1, 9)):
        text = VO[n].strip()
        if not text:
            continue
        aiff = SCRATCH / f"vo-shot{n}.aiff"
        wav = OUT / f"vo-shot{n}.wav"
        subprocess.run(["say", "-v", VOICE, "-r", RATE, "-o", str(aiff), text], check=True)
        # loudnorm to broadcast-ish target, mono 48k
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(aiff),
                        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "1",
                        str(wav)], check=True)
        d, slot = dur(wav), SLOTS[n]
        fit = "OK " if d <= slot + 1.5 else "OVER"   # VO may be shorter than slot (picture fills)
        rows.append((n, round(d, 1), slot, fit))
        print(f"  shot {n}: {d:5.1f}s / slot {slot:>3}s  [{fit}]  '{text[:52]}…'")
    over = [r for r in rows if r[3] == "OVER"]
    print(f"\n{'ALL FIT' if not over else 'OVER slot: ' + str([r[0] for r in over])}"
          f"  (VO shorter than slot is fine — the picture/stopwatch fills the rest)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
