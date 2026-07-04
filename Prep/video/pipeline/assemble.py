#!/usr/bin/env python3
"""V5/V6 assembler — build the master + 90s + 30s from ONE edit-manifest.json. [Prompts/08]

Pipeline (ffmpeg has NO libass/drawtext here, so captions burn as transparent PNG overlays):
  1. render each caption → transparent 1920x1080 PNG (render_caption.mjs)
  2. author captions.srt (global timestamps) + run the bracket guard BEFORE burn-in
  3. per-shot video segments at slot duration (card→loop / video→trim|speed|slow / montage→concat),
     captions overlaid via overlay=enable='between(t,a,b)'
  4. concat segments → master video track
  5. audio: VO stems placed at global shot starts (adelay) + a soft self-generated ambient bed
     ducked under the VO (sidechaincompress), loudnorm to the manifest target
  6. mux → exports/precedent-full-v{n}.mp4 ; then derive the 90s + 30s cuts from the same sources

Usage: python assemble.py [master|cut90s|cut30s|all] [version]
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DROP = ROOT / "precedent-video-drop"
MAN = json.loads((DROP / "manifest/edit-manifest.json").read_text())
CARDS, RAW, VO, CAP, SEG, EXPORTS, SCR = (DROP / "cards", DROP / "raw", DROP / "vo",
    DROP / "scratch/captions", DROP / "scratch/seg", DROP / "exports", DROP / "scratch")
for d in (CAP, SEG, EXPORTS):
    d.mkdir(parents=True, exist_ok=True)

W, H, FPS = MAN["width"], MAN["height"], MAN["fps"]
RENDER_CAP = ROOT / "Prep/video/pipeline/render_caption.mjs"


def run(cmd: list, quiet=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("CMD FAILED:", " ".join(str(c) for c in cmd[:6]), "…")
        print(r.stderr[-1400:])
        raise SystemExit(1)
    return r


def dur(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def cap_png(text: str) -> Path:
    h = hashlib.sha1(text.encode()).hexdigest()[:12]
    out = CAP / f"cap-{h}.png"
    if not out.exists():
        run(["node", str(RENDER_CAP), str(out), text])
    return out


def resolve_still(spec: str) -> Path:
    """card:NAME.png | frame:VIDEO@T  → a 1920x1080 PNG path."""
    if spec.startswith("card:"):
        return CARDS / spec.split(":", 1)[1]
    if spec.startswith("frame:"):
        ref = spec.split(":", 1)[1]
        vid, t = ref.split("@")
        out = SCR / f"frame_{vid.replace('.', '_')}_{t}.png"
        if not out.exists():
            run(["ffmpeg", "-y", "-loglevel", "error", "-ss", t, "-i", str(RAW / vid),
                 "-frames:v", "1", "-vf", f"scale={W}:{H}", str(out)])
        return out
    raise ValueError(spec)


def overlay_filter(n_caps: int, caps: list) -> str:
    """Build a filter chain that scales the base then overlays each caption in its window."""
    chain = f"[0:v]scale={W}:{H}:flags=lanczos,format=yuv420p,fps={FPS}[b0];"
    prev = "b0"
    for i, c in enumerate(caps):
        idx = i + 1
        nxt = f"v{i}"
        chain += f"[{prev}][{idx}:v]overlay=0:0:enable='between(t,{c['t0']},{c['t1']})'[{nxt}];"
        prev = nxt
    chain = chain.rstrip(";")
    return chain, prev


def build_segment(shot: dict) -> Path:
    sid, slot = shot["id"], shot["slot"]
    out = SEG / f"seg-{sid:02d}.mp4"
    caps = shot.get("captions", [])
    cap_inputs = [cap_png(c["text"]) for c in caps]

    # ---- construct the base video input(s) at exactly `slot` seconds ----
    kind = shot["kind"]
    base = SCR / f"base-{sid:02d}.mp4"
    if kind == "card":
        still = resolve_still(shot["src"])
        run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(still),
             "-t", str(slot), "-r", str(FPS), "-vf", f"scale={W}:{H},format=yuv420p",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", str(base)])
    elif kind == "montage":
        frames = shot["montage"]
        per = slot / len(frames)
        parts = []
        for j, spec in enumerate(frames):
            still = resolve_still(spec)
            pj = SCR / f"mont-{sid}-{j}.mp4"
            run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(still),
                 "-t", f"{per:.3f}", "-r", str(FPS), "-vf", f"scale={W}:{H},format=yuv420p",
                 "-c:v", "libx264", "-preset", "medium", "-crf", "18", str(pj)])
            parts.append(pj)
        concat_list = SCR / f"mont-{sid}.txt"
        concat_list.write_text("".join(f"file '{p}'\n" for p in parts))
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", str(concat_list), "-c", "copy", str(base)])
    elif kind == "pan":
        # slow vertical pan over a tall still (e.g. the ASI:One conversation) across the whole slot.
        still = resolve_still(shot["src"])
        ch = shot.get("card_height", H)
        ymax = max(0, ch - H)
        yexpr = f"min({ymax}*t/{slot},{ymax})" if ymax > 0 else "0"
        run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(still), "-t", str(slot),
             "-vf", f"scale={W}:{ch}:flags=lanczos,crop={W}:{H}:0:'{yexpr}',format=yuv420p",
             "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18", str(base)])
    elif kind == "seq":
        parts = []
        for j, s in enumerate(shot["seq"]):
            d, pj = s["dur"], SCR / f"seq-{sid}-{j}.mp4"
            if s["src"].startswith("card:"):
                still = resolve_still(s["src"])
                run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(still),
                     "-t", str(d), "-r", str(FPS), "-vf", f"scale={W}:{H},format=yuv420p",
                     "-c:v", "libx264", "-preset", "medium", "-crf", "18", str(pj)])
            else:  # video:
                vid = RAW / s["src"].split(":", 1)[1]
                run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", str(vid),
                     "-t", str(d), "-r", str(FPS), "-vf", f"scale={W}:{H},format=yuv420p",
                     "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(pj)])
            parts.append(pj)
        concat_list = SCR / f"seq-{sid}.txt"
        concat_list.write_text("".join(f"file '{p}'\n" for p in parts))
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", str(concat_list), "-c", "copy", str(base)])
    elif kind == "video":
        vid = RAW / shot["src"].split(":", 1)[1]
        srcdur = dur(vid)
        vf = f"scale={W}:{H}:flags=lanczos,format=yuv420p,fps={FPS}"
        args = ["ffmpeg", "-y", "-loglevel", "error"]
        if shot.get("loop"):
            args += ["-stream_loop", "-1", "-i", str(vid), "-t", str(slot), "-vf", vf]
        else:
            fit = shot.get("fit", "trim")
            if fit == "speed" or (fit == "fit" and abs(srcdur - slot) > 0.4):
                ratio = srcdur / slot                       # >1 speed up, <1 slow down
                args += ["-i", str(vid), "-vf", f"setpts=PTS/{ratio:.5f},{vf}", "-t", str(slot)]
            else:
                args += ["-i", str(vid), "-t", str(slot), "-vf", vf]
        args += ["-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", str(base)]
        run(args)
    else:
        raise ValueError(kind)

    # ---- overlay captions ----
    if cap_inputs:
        inputs = ["-i", str(base)]
        for p in cap_inputs:
            inputs += ["-i", str(p)]
        chain, last = overlay_filter(len(cap_inputs), caps)
        run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", chain,
             "-map", f"[{last}]", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium",
             "-crf", "18", "-t", str(slot), str(out)])
    else:
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(base), "-c", "copy", str(out)])
    return out


def write_srt(shots: list) -> Path:
    """Author captions.srt with GLOBAL timestamps and run the bracket guard."""
    def ts(sec):
        ms = int(round(sec * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000); return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    starts, acc = {}, 0
    for sh in shots:
        starts[sh["id"]] = acc; acc += sh["slot"]
    lines, i = [], 1
    for sh in shots:
        base = starts[sh["id"]]
        for c in sh.get("captions", []):
            lines.append(f"{i}\n{ts(base + c['t0'])} --> {ts(base + c['t1'])}\n{c['text']}\n")
            i += 1
    srt = DROP / "captions/captions.srt"
    srt.parent.mkdir(parents=True, exist_ok=True)
    srt.write_text("\n".join(lines))
    # bracket guard BEFORE burn-in
    import re
    bad = re.findall(r"\[measured\]|\[repo\]|‹|<FILL", srt.read_text())
    if bad:
        print("BRACKET GUARD FAILED on captions.srt:", bad); raise SystemExit(1)
    print(f"captions.srt: {i-1} cues, bracket guard clean ✓")
    return srt


def build_audio(shots: list, total: float) -> Path:
    """VO stems at global starts + soft ambient bed ducked under VO, loudnorm."""
    starts, acc = {}, 0
    for sh in shots:
        starts[sh["id"]] = acc; acc += sh["slot"]
    vo_inputs, delays = [], []
    for sh in shots:
        if sh.get("vo"):
            wav = VO / sh["vo"]
            if wav.exists():
                vo_inputs.append(str(wav)); delays.append(int(starts[sh["id"]] * 1000))
    # inputs: [0..n-1] VO stems ; ambient bed generated via lavfi
    inputs = []
    for w in vo_inputs:
        inputs += ["-i", w]
    bed_idx = len(vo_inputs)
    inputs += ["-f", "lavfi", "-t", f"{total:.2f}",
               "-i", "sine=frequency=98:sample_rate=48000,volume=0.5"]
    fc = ""
    volabels = []
    for i, dly in enumerate(delays):
        fc += f"[{i}:a]adelay={dly}:all=1,aformat=sample_rates=48000:channel_layouts=mono[v{i}];"
        volabels.append(f"[v{i}]")
    fc += f"{''.join(volabels)}amix=inputs={len(volabels)}:normalize=0:duration=longest[vo];"
    fc += "[vo]asplit=2[vo_out][vo_sc];"
    # soft evolving bed: the sine, lowpassed + tremolo, low level
    fc += (f"[{bed_idx}:a]lowpass=f=320,tremolo=f=0.12:d=0.7,volume=0.10,"
           "aformat=sample_rates=48000:channel_layouts=mono[bed];")
    fc += "[bed][vo_sc]sidechaincompress=threshold=0.05:ratio=6:attack=8:release=320[bedduck];"
    fc += (f"[vo_out][bedduck]amix=inputs=2:normalize=0:duration=longest,"
           f"loudnorm=I={MAN['loudness_target_lufs']}:TP={MAN['true_peak_max_dbtp']}:LRA=11,"
           "aformat=sample_rates=48000:channel_layouts=stereo[aout]")
    out = SCR / "master_audio.m4a"
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc,
         "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", str(out)])
    return out


def assemble_master(version="1"):
    shots = MAN["shots"]
    total = sum(sh["slot"] for sh in shots)
    print(f"=== master: {len(shots)} shots, {total}s target ===")
    write_srt(shots)
    segs = [build_segment(sh) for sh in shots]
    concat_list = SCR / "master_concat.txt"
    concat_list.write_text("".join(f"file '{p}'\n" for p in segs))
    vtrack = SCR / "master_video.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(concat_list), "-c", "copy", str(vtrack)])
    atrack = build_audio(shots, dur(vtrack))
    out = EXPORTS / f"precedent-full-v{version}.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(vtrack), "-i", str(atrack),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
         "-shortest", str(out)])
    print(f"MASTER → {out}  ({dur(out):.1f}s)")
    return out


def _still_seg(spec, secs, caption, tag):
    """A caption'd still segment (for the 30s teaser). Returns an mp4 path."""
    still = resolve_still(spec)
    base = SCR / f"tz-base-{tag}.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(still), "-t", str(secs),
         "-r", str(FPS), "-vf", f"scale={W}:{H},format=yuv420p", "-c:v", "libx264",
         "-preset", "medium", "-crf", "18", str(base)])
    out = SCR / f"tz-{tag}.mp4"
    png = cap_png(caption)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(base), "-i", str(png), "-filter_complex",
         f"[0:v][1:v]overlay=0:0:enable='between(t,0.3,{secs-0.2})'", "-r", str(FPS),
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-t", str(secs), str(out)])
    return out


def assemble_cut30s(version="1"):
    frames = MAN["cuts"]["cut30s"]["frames"]
    print("=== 30s teaser ===")
    segs = [_still_seg(f["src"], f["dur"], f["text"], i) for i, f in enumerate(frames)]
    total = sum(f["dur"] for f in frames)
    lst = SCR / "tz_concat.txt"; lst.write_text("".join(f"file '{p}'\n" for p in segs))
    vtrack = SCR / "tz_video.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(vtrack)])
    # music bed only (no VO — captioned), loudnorm
    aud = SCR / "tz_audio.m4a"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-t", f"{total}",
         "-i", "sine=frequency=98:sample_rate=48000", "-af",
         f"lowpass=f=320,tremolo=f=0.12:d=0.7,volume=0.16,loudnorm=I={MAN['loudness_target_lufs']}:TP={MAN['true_peak_max_dbtp']}:LRA=11,aformat=channel_layouts=stereo",
         "-c:a", "aac", "-b:a", "192k", str(aud)])
    out = EXPORTS / f"precedent-30s-v{version}.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(vtrack), "-i", str(aud),
         "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(out)])
    print(f"30s TEASER → {out}  ({dur(out):.1f}s)")
    return out


# The two memorable lines, added as burned captions in the 90s cut so they survive by construction.
MEM_TSF = "The second time is free."
MEM_KNOWS = "It knows what it's not allowed to touch."


def assemble_cut90s(version="1"):
    segdef = MAN["cuts"]["cut90s"]["segments"]
    print("=== 90s cut ===")
    parts, vo_plan, acc = [], [], 0.0
    for k, s in enumerate(segdef):
        seg = SEG / f"seg-{s['shot']:02d}.mp4"
        if not seg.exists():
            print("missing segment (run master first):", seg); raise SystemExit(1)
        piece = SCR / f"c90-{k}.mp4"
        length = s["out"] - s["in"]
        # trim; add the memorable-line caption on shots 5 and 6
        mem = MEM_TSF if s["shot"] == 5 else (MEM_KNOWS if s["shot"] == 6 else None)
        if mem:
            png = cap_png(mem)
            run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(s["in"]), "-i", str(seg),
                 "-i", str(png), "-filter_complex",
                 f"[0:v][1:v]overlay=0:0:enable='between(t,0.3,{length-0.3})'",
                 "-t", str(length), "-r", str(FPS), "-c:v", "libx264", "-preset", "medium",
                 "-crf", "18", "-an", str(piece)])
        else:
            run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(s["in"]), "-i", str(seg),
                 "-t", str(length), "-r", str(FPS), "-c:v", "libx264", "-preset", "medium",
                 "-crf", "18", "-an", str(piece)])
        parts.append(piece)
        vo = MAN["shots"][s["shot"]].get("vo")
        if vo:
            vo_plan.append((VO / vo, acc, length))
        acc += length
    total = acc
    lst = SCR / "c90_concat.txt"; lst.write_text("".join(f"file '{p}'\n" for p in parts))
    vtrack = SCR / "c90_video.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(vtrack)])
    # audio: place each segment's VO stem at its cut position, trimmed to the segment; + bed, loudnorm
    inputs, fc, labels = [], "", []
    for i, (wav, start, length) in enumerate(vo_plan):
        inputs += ["-i", str(wav)]
        fc += (f"[{i}:a]atrim=0:{length},adelay={int(start*1000)}:all=1,"
               f"aformat=sample_rates=48000:channel_layouts=mono[v{i}];")
        labels.append(f"[v{i}]")
    bed_idx = len(vo_plan)
    inputs += ["-f", "lavfi", "-t", f"{total:.2f}", "-i", "sine=frequency=98:sample_rate=48000"]
    fc += f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=longest[vo];[vo]asplit=2[vo_out][vo_sc];"
    fc += f"[{bed_idx}:a]lowpass=f=320,tremolo=f=0.12:d=0.7,volume=0.12[bed];"
    fc += "[bed][vo_sc]sidechaincompress=threshold=0.05:ratio=6:attack=8:release=320[bd];"
    fc += (f"[vo_out][bd]amix=inputs=2:normalize=0:duration=longest,"
           f"loudnorm=I={MAN['loudness_target_lufs']}:TP={MAN['true_peak_max_dbtp']}:LRA=11,aformat=channel_layouts=stereo[aout]")
    aud = SCR / "c90_audio.m4a"
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-map", "[aout]",
         "-c:a", "aac", "-b:a", "192k", str(aud)])
    out = EXPORTS / f"precedent-90s-v{version}.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(vtrack), "-i", str(aud),
         "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(out)])
    print(f"90s CUT → {out}  ({dur(out):.1f}s)")
    return out


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "master"
    ver = sys.argv[2] if len(sys.argv) > 2 else "1"
    if what in ("master", "all"):
        assemble_master(ver)
    if what in ("cut90s", "all"):
        assemble_cut90s(ver)
    if what in ("cut30s", "all"):
        assemble_cut30s(ver)
