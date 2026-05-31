#!/usr/bin/env python3
"""
sync_showcase.py — Rebuild showcase/clips.json and clips-list.js.
Stop injecting static HTML cards into showcase/index.html to support SPA views.

Run before deploying:
    uv run scripts/sync_showcase.py
"""
import json
import os
import re
from pathlib import Path
from datetime import datetime


def parse_filename(name: str, kind: str) -> tuple[str, str, str, str | None, str | None]:
    """
    Returns (template, artist, title, clip_start, clip_end).
    """
    stem = re.sub(r'\.(mp3|flac|wav|m4a|mp4|mov|mkv)$', '', name, flags=re.IGNORECASE)

    template = "clipped_audio" if kind == "audio" else "video"

    # Check for template prefix "Reel ⋅ …" or "Vertical ⋅ …"
    for sep in [" ⋅ ", " · "]:
        if sep in stem:
            parts = stem.split(sep, 1)
            template = parts[0].strip().lower().replace(" ", "_")
            stem = parts[1].strip()
            break

    # Parse clip range suffix "(2.41 - 3.06)" or "(0.50 - 1.20)"
    clip_start = clip_end = None
    range_match = re.search(r'\((\d+\.\d+)\s*-\s*(\d+\.\d+)\)\s*$', stem)
    if range_match:
        clip_start = range_match.group(1)
        clip_end = range_match.group(2)
        stem = stem[:range_match.start()].rstrip()

    # Strip smoke test suffix
    stem = re.sub(r'\s*\[smoke_test\]\s*$', '', stem).strip()

    # Split "Artist - Title"
    artist = ""
    title = stem
    if " - " in stem:
        parts = stem.split(" - ", 1)
        artist = parts[0].strip()
        title = parts[1].strip()

    return template, artist, title, clip_start, clip_end


def main():
    repo_root = Path(__file__).resolve().parents[1]
    showcase_base = repo_root / "showcase"
    showcase_public = showcase_base / "public"
    audio_dir = repo_root / "_audio"
    video_dir = repo_root / "_video"
    smoke_dir = repo_root / "tests" / "videos"

    clips = []

    # 1. Audio Clips
    if audio_dir.exists():
        for f in sorted(audio_dir.iterdir()):
            if f.is_file() and f.suffix.lower() in [".mp3", ".flac", ".wav", ".m4a"]:
                if "/tmp/" in str(f) or f.name.startswith("tmp_") or "/tmp/" in str(f.resolve()):
                    print(f"Skipped local path: {f}")
                    continue
                tpl, artist, title, cs, ce = parse_filename(f.name, "audio")
                rel_path = f"_audio/{f.name}"
                clips.append({
                    "filepath": rel_path,
                    "filename": f.name,
                    "kind": "audio",
                    "template": tpl,
                    "engine": "audio",
                    "aspect": "square",
                    "platform": "default",
                    "clip_start": cs,
                    "clip_end": ce,
                    "artist": artist,
                    "title": title,
                    "timestamp": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                })

    # 2. Video Renders
    if video_dir.exists():
        for f in sorted(video_dir.iterdir()):
            if f.is_file() and f.suffix.lower() in [".mp4", ".mov", ".mkv"]:
                if "/tmp/" in str(f) or f.name.startswith("tmp_") or "/tmp/" in str(f.resolve()):
                    print(f"Skipped local path: {f}")
                    continue
                tpl, artist, title, cs, ce = parse_filename(f.name, "video")

                is_remotion = any(k in tpl for k in ["pulse", "square", "scene", "vhs", "card", "fluid", "premium"])
                engine = "remotion" if is_remotion else "ffmpeg"

                platform = "default"
                if tpl in ["pulse_reel", "reel", "vertical", "vertical_wave", "spinner_story"]:
                    platform = "vertical_full"

                is_vertical = any(k in platform for k in ["instagram", "tiktok", "vertical", "shorts"])
                aspect = "9:16" if is_vertical else "1:1"

                rel_path = f"_video/{f.name}"
                clips.append({
                    "filepath": rel_path,
                    "filename": f.name,
                    "kind": "video",
                    "template": tpl,
                    "engine": engine,
                    "aspect": aspect,
                    "platform": platform,
                    "clip_start": cs,
                    "clip_end": ce,
                    "artist": artist,
                    "title": title,
                    "timestamp": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                })

    # 3. Smoke Tests
    if smoke_dir.exists():
        for f in sorted(smoke_dir.rglob("*.mp4")):
            if "[smoke_test]" in f.name:
                if "/tmp/" in str(f) or f.name.startswith("tmp_") or "/tmp/" in str(f.resolve()):
                    print(f"Skipped local path: {f}")
                    continue
                tpl, artist, title, cs, ce = parse_filename(f.name, "video")
                kind = "remotion" if "remotion" in str(f) else "ffmpeg"
                rel_path = str(f.relative_to(repo_root))
                clips.append({
                    "filepath": rel_path,
                    "filename": f.name,
                    "kind": "smoke",
                    "template": tpl,
                    "engine": kind,
                    "aspect": "9:16" if "reel" in tpl or "vertical" in tpl else "1:1",
                    "platform": "default",
                    "artist": "Test",
                    "title": tpl.replace('_', ' ').title(),
                    "timestamp": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                })

    clips.sort(key=lambda x: x["timestamp"], reverse=True)

    # Write JSON + JS
    (showcase_public / "clips.json").write_text(json.dumps(clips, indent=2), encoding="utf-8")
    (showcase_public / "clips-list.js").write_text(
        f"var userClips = {json.dumps(clips, indent=2)};\n", encoding="utf-8"
    )

    # Build audio source options for simulator dropdown
    audio_options = [
        '          <option value="upload">Upload your own audio file...</option>',
    ]
    for c in clips:
        if c["kind"] == "audio":
            label = f"{c['artist']} — {c['title']}" if c['artist'] else (c['title'] or c['filename'])
            audio_options.append(f'          <option value="{c["filepath"]}">{label}</option>')

    # Inject only the options into index.html
    html_file = showcase_public / "index.html"
    if not html_file.exists():
        print(f"WARNING: {html_file} not found, skipping HTML injection.")
        return

    content = html_file.read_text(encoding="utf-8")

    def inject(html: str, start_marker: str, end_marker: str, lines: list[str]) -> str:
        if start_marker not in html or end_marker not in html:
            return html
        pre, rest = html.split(start_marker, 1)
        _, post = rest.split(end_marker, 1)
        return pre + start_marker + "\n" + "\n".join(lines) + "\n    " + end_marker + post

    # Clear previous injections but keep markers
    content = inject(content, "<!-- INSERT_USER_VIDEOS_HERE -->", "<!-- INSERT_USER_VIDEOS_END -->", [])
    content = inject(content, "<!-- INSERT_USER_AUDIOS_HERE -->", "<!-- INSERT_USER_AUDIOS_END -->", [])
    content = inject(content, "<!-- INSERT_SMOKE_TESTS_HERE -->", "<!-- INSERT_SMOKE_TESTS_END -->", [])
    content = inject(content, "<!-- INSERT_AUDIO_OPTIONS_HERE -->", "<!-- INSERT_AUDIO_OPTIONS_END -->", audio_options)

    html_file.write_text(content, encoding="utf-8")
    print(f"Synced {len(clips)} items to clips.json. HTML cards removed for SPA transition.")


if __name__ == "__main__":
    main()
