#!/usr/bin/env python3
"""V4 VO synthesis — narration from the canonical script. [Prompts/08]

If ELEVENLABS_API_KEY is set → real TTS via ElevenLabs (default voice: George, British, calm).
Else → a macOS `say` scratch track. Either way the TTS input is the canonical VO text VERBATIM
(vo_canonical.json), so it can never drift from the reconciled script.

Per shot: TTS → loudnorm'd mono 48k WAV in precedent-video-drop/vo/. Reports each stem's duration
against the shot's slot budget. Usage: make_vo.py [voice] [rate_or_model]
  ElevenLabs: voice = a voice_id (default George); arg2 = model_id (default eleven_multilingual_v2)
  say:        voice = a `say` voice name (default Daniel); arg2 = wpm (default 178)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = json.loads((ROOT / "Prep/video/pipeline/vo_canonical.json").read_text())
VO = CANON["shots"]
SLOTS = CANON["slot_seconds"]
OUT = ROOT / "precedent-video-drop/vo"
SCRATCH = ROOT / "precedent-video-drop/scratch/vo-raw"

ELEVEN_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip()
GEORGE = "JBFqnCBsd6RMkjVDRZzb"   # British, warm, calm storyteller
VOICE = sys.argv[1] if len(sys.argv) > 1 else (GEORGE if ELEVEN_KEY else "Daniel")
ARG2 = sys.argv[2] if len(sys.argv) > 2 else ("eleven_multilingual_v2" if ELEVEN_KEY else "178")


def dur(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def eleven_tts(text: str, out_mp3: Path) -> None:
    body = json.dumps({
        "text": text, "model_id": ARG2,
        "voice_settings": {"stability": 0.55, "similarity_boost": 0.75,
                           "style": 0.0, "use_speaker_boost": True},
    }).encode()
    url = (f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}"
           f"?output_format=mp3_44100_128")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310
        out_mp3.write_bytes(r.read())


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    engine = "ElevenLabs" if ELEVEN_KEY else "say"
    print(f"engine={engine} voice={VOICE} arg2={ARG2}  (canonical VO fed verbatim → no drift possible)")
    rows = []
    for n in map(str, range(1, 9)):
        text = VO[n].strip()
        if not text:
            continue
        wav = OUT / f"vo-shot{n}.wav"
        if ELEVEN_KEY:
            raw = SCRATCH / f"vo-shot{n}.mp3"
            eleven_tts(text, raw)
        else:
            raw = SCRATCH / f"vo-shot{n}.aiff"
            subprocess.run(["say", "-v", VOICE, "-r", ARG2, "-o", str(raw), text], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw),
                        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "1",
                        str(wav)], check=True)
        d, slot = dur(wav), SLOTS[n]
        fit = "OK " if d <= slot + 1.5 else "OVER"
        rows.append((n, round(d, 1), slot, fit))
        print(f"  shot {n}: {d:5.1f}s / slot {slot:>3}s  [{fit}]  '{text[:48]}…'")
    over = [r for r in rows if r[3] == "OVER"]
    print(f"\n{'ALL FIT' if not over else 'OVER slot: ' + str([r[0] for r in over])}"
          f"  (VO shorter than slot is fine — the picture/stopwatch fills the rest)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
