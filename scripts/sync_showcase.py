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
    
    # Save database
    json_file = showcase_dir / "clips.json"
    js_file = showcase_dir / "clips-list.js"
    json_file.write_text(json.dumps(clips, indent=2), encoding="utf-8")
    js_file.write_text(f"var userClips = {json.dumps(clips, indent=2)};\n", encoding="utf-8")
    
    # Generate static HTML cards for index.html
    video_html = []
    audio_html = []
    
    for clip in clips:
        t = clip.get("template", "")
        is_remotion = any(k in t for k in ["pulse", "square", "scene", "vhs", "card"])
        engine = "remotion" if is_remotion else "ffmpeg"
        
        platform = clip.get("platform", "default") or "default"
        is_vertical = any(k in platform for k in ["instagram", "tiktok", "vertical", "shorts"])
        is_wide = any(k in platform for k in ["youtube", "twitter"])
        aspect = "vertical" if is_vertical else ("wide" if is_wide else "square")
        aspect_class = "vertical" if is_vertical else ("wide" if is_wide else "")
        
        title_formatted = f"{clip['artist']} - {clip['title']}" if clip['artist'] else (clip['title'] or clip['filename'])
        
        if clip["kind"] == "video":
            cli_command = f"clipped video \\\"{clip['artist'] or 'track'}\\\" --template {clip['template']} --platform {clip['platform']} --start {clip['start']} --end {clip['end']}"
            card = f"""    <!-- Synced Card -->
    <div class="showcase-card" data-engine="{engine}" data-aspect="{aspect}">
      <div class="card-video-container {aspect_class}">
        <video src="{clip['filepath']}" controls muted playsinline loop preload="none"></video>
      </div>
      <div class="card-info">
        <div class="card-title">{title_formatted}</div>
        <div class="card-subtitle">
          <span class="tag">VIDEO</span>
          <span class="tag">{clip['template']}</span>
          <span class="tag">{clip['platform']}</span>
          <span class="tag" style="color: #953ebf;">{clip['timestamp']}</span>
        </div>
      </div>
      <div class="card-code">
        {cli_command}
        <button class="copy-btn" onclick="copyText(this)">Copy</button>
      </div>
    </div>"""
            video_html.append(card)
        else:
            cli_command = f"clipped audio \\\"{clip['artist'] or 'track'}\\\" {clip['start']} {clip['end']}"
            card = f"""    <!-- Synced Card -->
    <div class="showcase-card" data-engine="audio" data-aspect="square">
      <div style="background: rgb(15,15,15); padding: 20px; border-radius: 6px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:10px;">
        <span style="font-size:32px;">🎵</span>
        <audio src="{clip['filepath']}" controls style="width: 100%;"></audio>
      </div>
      <div class="card-info">
        <div class="card-title">{title_formatted}</div>
        <div class="card-subtitle">
          <span class="tag">AUDIO</span>
          <span class="tag">{clip['template']}</span>
          <span class="tag">{clip['platform']}</span>
          <span class="tag" style="color: #953ebf;">{clip['timestamp']}</span>
        </div>
      </div>
      <div class="card-code">
        {cli_command}
        <button class="copy-btn" onclick="copyText(this)">Copy</button>
      </div>
    </div>"""
            audio_html.append(card)
            
    # Read and replace in index.html
    html_file = showcase_dir / "index.html"
    if html_file.exists():
        content = html_file.read_text(encoding="utf-8")
        
        # Replace videos
        v_start = "<!-- INSERT_USER_VIDEOS_HERE -->"
        v_end = "<!-- INSERT_USER_VIDEOS_END -->"
        if v_start in content and v_end in content:
            parts = content.split(v_start, 1)
            rest = parts[1].split(v_end, 1)
            content = parts[0] + v_start + "\n" + "\n".join(video_html) + "\n    " + v_end + rest[1]
            
        # Replace audios
        a_start = "<!-- INSERT_USER_AUDIOS_HERE -->"
        a_end = "<!-- INSERT_USER_AUDIOS_END -->"
        if a_start in content and a_end in content:
            parts = content.split(a_start, 1)
            rest = parts[1].split(a_end, 1)
            content = parts[0] + a_start + "\n" + "\n".join(audio_html) + "\n    " + a_end + rest[1]
            
        html_file.write_text(content, encoding="utf-8")
        
    print(f"Successfully synced {len(clips)} clips to showcase database and pre-rendered index.html.")

if __name__ == "__main__":
    main()
