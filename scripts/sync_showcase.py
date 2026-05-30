#!/usr/bin/env python3
import json
import os
from pathlib import Path
from datetime import datetime

def main():
    repo_root = Path(__file__).resolve().parents[1]
    showcase_dir = repo_root / "showcase"
    audio_dir = repo_root / "_audio"
    video_dir = repo_root / "_video"
    
    clips = []
    
    # Helper to parse filename
    def parse_filename(name, kind):
        template = "clipped_audio" if kind == "audio" else "video"
        artist = ""
        title = name.replace(".mp3", "").replace(".flac", "").replace(".mp4", "").replace(".wav", "")
        
        # Check for template dot separator " ⋅ " (or solid dot " · ")
        dot_seps = [" ⋅ ", " · "]
        for sep in dot_seps:
            if sep in title:
                parts = title.split(sep, 1)
                tpl = parts[0].strip().lower().replace(" ", "_")
                # e.g., "pulse_reel", "reel", "vertical"
                template = tpl
                title = parts[1].strip()
                break
                
        # Split artist and title by " - "
        if " - " in title:
            parts = title.split(" - ", 1)
            artist = parts[0].strip()
            title = parts[1].strip()
            
        return template, artist, title

    # Scan audio
    if audio_dir.exists():
        for f in audio_dir.iterdir():
            if f.is_file() and f.suffix.lower() in [".mp3", ".flac", ".wav", ".m4a"]:
                tpl, artist, title = parse_filename(f.name, "audio")
                rel_path = os.path.relpath(f, start=showcase_dir)
                clips.append({
                    "filepath": rel_path,
                    "filename": f.name,
                    "kind": "audio",
                    "template": tpl,
                    "platform": "default",
                    "start": 0,
                    "end": None,
                    "artist": artist,
                    "title": title,
                    "timestamp": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
                
    # Scan video
    if video_dir.exists():
        for f in video_dir.iterdir():
            if f.is_file() and f.suffix.lower() in [".mp4", ".mov", ".mkv"]:
                tpl, artist, title = parse_filename(f.name, "video")
                # Deduce platform from template (e.g. reels -> instagram, squares -> default)
                platform = "default"
                if tpl in ["pulse_reel", "reel", "vertical", "vertical_wave", "spinner_story"]:
                    platform = "vertical_full"
                rel_path = os.path.relpath(f, start=showcase_dir)
                clips.append({
                    "filepath": rel_path,
                    "filename": f.name,
                    "kind": "video",
                    "template": tpl,
                    "platform": platform,
                    "start": 0,
                    "end": None,
                    "artist": artist,
                    "title": title,
                    "timestamp": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
                
    # Sort by timestamp newest first
    clips.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Save
    json_file = showcase_dir / "clips.json"
    js_file = showcase_dir / "clips-list.js"
    json_file.write_text(json.dumps(clips, indent=2), encoding="utf-8")
    js_file.write_text(f"var userClips = {json.dumps(clips, indent=2)};\n", encoding="utf-8")
    print(f"Successfully synced {len(clips)} clips to showcase database.")

if __name__ == "__main__":
    main()
