#!/usr/bin/env python3
"""Extract frames from rendered template test videos for visual inspection.

Respects display_aspect_ratio — frames are scaled to correct display
dimensions so they match visual playback, not raw pixel dimensions.

Usage: python3 tests/scripts/extract_template_frames.py

Output:
  tests/frames/<template_name>/NNs.jpg
  tests/frames/<template_name>/final.jpg
  tests/frames/all_templates.jpg  (contact sheet)
  tests/frames/template_frames.zip
  tests/frames/logs/
"""

import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent.parent
VIDEO_DIR = TESTS_DIR / "videos" / "ffmpeg"
FRAMES_DIR = TESTS_DIR / "frames"
LOGS_DIR = FRAMES_DIR / "logs"
CONTACT_SHEET = FRAMES_DIR / "all_templates.jpg"
ZIP_PATH = FRAMES_DIR / "template_frames.zip"

FFMPEG = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
FFPROBE = shutil.which("ffprobe") or "/opt/homebrew/bin/ffprobe"
MONTAGE = shutil.which("montage") or "/opt/homebrew/bin/montage"

BASE_TIMESTAMPS = [
    1, 3, 5, 8, 11, 13, 16, 18, 20,
    22, 25, 28, 30, 33, 36, 38, 40,
    43, 46, 48, 50,
]


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_duration(video_path):
    cmd = [FFPROBE, "-v", "quiet", "-print_format", "json",
           "-show_format", str(video_path)]
    try:
        return float(json.loads(subprocess.check_output(cmd).decode())["format"]["duration"])
    except Exception as e:
        eprint(f"  ERROR getting duration: {e}")
        return None


def get_display_dims(video_path):
    """Return (display_w, display_h, vf_string) respecting DAR.

    If DAR matches pixel aspect (SAR=1), vf_string is '' (no filter).
    If DAR differs (e.g. 1080x1080 pixels with DAR 9:16), vf_string
    contains a scale filter to produce the correct display dimensions.
    """
    cmd = [FFPROBE, "-v", "quiet", "-print_format", "json",
           "-select_streams", "v:0",
           "-show_entries", "stream=width,height,sample_aspect_ratio,display_aspect_ratio",
           str(video_path)]
    try:
        s = json.loads(subprocess.check_output(cmd).decode())["streams"][0]
    except Exception as e:
        eprint(f"  ERROR reading stream info: {e}")
        return None, None, ""

    pix_w = int(s["width"])
    pix_h = int(s["height"])

    dar_str = s.get("display_aspect_ratio", "1:1")
    sar_str = s.get("sample_aspect_ratio", "1:1")

    def parse_ratio(r):
        if ":" in r:
            a, b = r.split(":")
            return int(a), int(b)
        return 1, 1

    dar_w, dar_h = parse_ratio(dar_str)
    sar_w, sar_h = parse_ratio(sar_str)

    # If SAR is already 1:1 and pixel WxH matches DAR conceptually, no filter needed
    if sar_w == 1 and sar_h == 1:
        return pix_w, pix_h, "setsar=1"

    # SAR is non-1:1 (e.g. 9:16 on 1080x1080) — scale to display dimensions
    dar_ratio = dar_w / dar_h

    if dar_ratio >= 1:  # landscape or square
        disp_w = round(pix_h * dar_ratio)
        disp_h = pix_h
    else:  # portrait / vertical
        disp_w = pix_w
        disp_h = round(pix_w / dar_ratio)

    vf = f"scale={disp_w}:{disp_h},setsar=1"
    return disp_w, disp_h, vf


def extract_frame(video_path, timestamp, output_path, vf_filter):
    if vf_filter:
        cmd = [FFMPEG, "-y", "-v", "warning",
               "-ss", str(timestamp),
               "-i", str(video_path),
               "-vf", vf_filter,
               "-frames:v", "1", "-q:v", "2",
               str(output_path)]
    else:
        cmd = [FFMPEG, "-y", "-v", "warning",
               "-ss", str(timestamp),
               "-i", str(video_path),
               "-frames:v", "1", "-q:v", "2",
               str(output_path)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        eprint(f"  ERROR at {timestamp}s: {e.stderr.strip()}")
        return False


def generate_timestamps(duration):
    dur = int(duration)
    ts = [t for t in BASE_TIMESTAMPS if t < dur]
    steps = [2, 2, 3, 3]
    current = ts[-1] if ts else 0
    idx = 0
    while current + steps[idx % 4] < dur:
        current += steps[idx % 4]
        if current not in ts:
            ts.append(current)
        idx += 1
    return ts


def find_template_videos():
    videos = sorted(VIDEO_DIR.glob("*.mp4"))
    if not videos:
        eprint("ERROR: No mp4 files found in " + str(VIDEO_DIR))
        sys.exit(1)
    groups = {}
    for v in videos:
        name = v.stem
        if " ⋅ " in name:
            continue
        groups[name.replace("_", " ")] = v
    return groups


def extract_all_frames(template_videos):
    results = {}
    for tname, vpath in sorted(template_videos.items()):
        out_dir = FRAMES_DIR / tname
        out_dir.mkdir(parents=True, exist_ok=True)

        eprint(f"\n{'='*60}")
        eprint(f"Template: {tname}")
        eprint(f"Video:    {vpath.name}")

        duration = get_duration(vpath)
        if duration is None:
            eprint("  SKIPPING (no duration)")
            continue

        disp_w, disp_h, vf = get_display_dims(vpath)
        if disp_w is None:
            eprint("  SKIPPING (no display dims)")
            continue

        if vf:
            eprint(f"DAR-adjusted:   {disp_w}x{disp_h}  [{vf}]")
        else:
            eprint(f"Native:         {disp_w}x{disp_h}  (SAR=1, no scale)")

        timestamps = generate_timestamps(duration)
        extracted = {}
        for ts in timestamps:
            out_name = f"{ts:02d}s.jpg"
            out_path = out_dir / out_name
            eprint(f"  {out_name} @ {ts}s")
            ok = extract_frame(vpath, ts, out_path, vf)
            extracted[str(ts)] = ok

        results[tname] = {
            "video": str(vpath),
            "duration": duration,
            "width": disp_w,
            "height": disp_h,
            "vf_filter": vf,
            "frames": extracted,
        }
    return results


def create_contact_sheet(results):
    frame_paths = []
    for tname in sorted(results.keys()):
        tdir = FRAMES_DIR / tname
        if not tdir.exists():
            continue
        for f in sorted(tdir.glob("*.jpg")):
            frame_paths.append((str(f), f"{tname} {f.stem}"))

    if not frame_paths:
        eprint("No frames for contact sheet")
        return False

    eprint(f"\nCreating contact sheet ({len(frame_paths)} frames)...")

    font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
    montage_cmd = [
        MONTAGE,
        "-geometry", "320x320+8+8",
        "-tile", "8x",
        "-title", f"Template Frames ({len(results)} templates)",
        "-pointsize", "12",
        "-font", font_path if os.path.exists(font_path) else "ArialMT",
        "-background", "#222222",
        "-fill", "#cccccc",
        "-label", "%t",
    ]
    for fpath, _ in frame_paths:
        montage_cmd.append(fpath)
    montage_cmd.append(str(CONTACT_SHEET))

    try:
        subprocess.run(montage_cmd, check=True, capture_output=True, text=True)
        eprint(f"Contact sheet: {CONTACT_SHEET}")
        return True
    except subprocess.CalledProcessError as e:
        eprint(f"WARNING: montage failed: {e.stderr.strip()}")
        return False


def save_summary(results):
    summary_path = LOGS_DIR / "summary.txt"
    lines = ["Template Frame Extraction Summary", "=" * 50, ""]
    for tname, info in sorted(results.items()):
        w, h = info["width"], info["height"]
        vf = info.get("vf_filter", "")
        lines.append(f"{tname}  ({info['duration']:.1f}s  {w}x{h})")
        if vf:
            lines.append(f"  DAR-adjust: {vf}")
        for ts, ok in sorted(info["frames"].items()):
            lines.append(f"  {int(ts):02d}s  [{'OK' if ok else 'FAIL'}]")
        lines.append("")
    with open(summary_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def create_zip():
    count = 0
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for tdir in sorted(FRAMES_DIR.iterdir()):
            if not tdir.is_dir():
                continue
            for f in sorted(tdir.glob("*.jpg")):
                zf.write(f, f"{tdir.name}/{f.name}")
                count += 1
        for extra in [CONTACT_SHEET]:
            if extra.exists():
                zf.write(extra, extra.name)
        if LOGS_DIR.exists():
            for lf in LOGS_DIR.glob("*"):
                zf.write(lf, f"logs/{lf.name}")
    eprint(f"Zip: {ZIP_PATH} ({count} frames)")


def main():
    eprint(f"FFmpeg:  {FFMPEG}")
    eprint(f"Video:   {VIDEO_DIR}")
    eprint(f"Output:  {FRAMES_DIR}")

    if FRAMES_DIR.exists():
        shutil.rmtree(FRAMES_DIR)
    FRAMES_DIR.mkdir(parents=True)
    LOGS_DIR.mkdir(parents=True)

    template_videos = find_template_videos()
    if not template_videos:
        eprint("ERROR: No clean template videos found")
        eprint(f"  Looked in {VIDEO_DIR}")
        sys.exit(1)

    eprint(f"\nFound {len(template_videos)} templates:")
    for name, path in sorted(template_videos.items()):
        eprint(f"  {name:22s} → {path.name}")

    results = extract_all_frames(template_videos)

    with open(LOGS_DIR / "extract_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    save_summary(results)

    total_ok = sum(1 for r in results.values() for ok in r["frames"].values() if ok)
    total_fail = sum(1 for r in results.values() for ok in r["frames"].values() if not ok)
    eprint(f"\nFrames: {total_ok} OK, {total_fail} FAIL")

    create_contact_sheet(results)
    create_zip()
    eprint(f"\nDone → {FRAMES_DIR}")


if __name__ == "__main__":
    main()
