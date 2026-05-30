import argparse
import os
import subprocess
import sys
from pathlib import Path

TEMPLATES = [
    # FFmpeg templates
    ("spinner", "default", False),
    ("fade", "default", False),
    ("static", "default", False),
    ("vertical", "instagram", False),
    ("minimal", "default", False), 
    ("cinematic", "youtube", False),
    ("waveformbar", "default", False),
    ("vertical_wave", "instagram", False),
    ("reel", "instagram", False),
    ("spinner_story", "default", False),
    # Remotion templates
    ("pulse_reel", "instagram", True),
    ("gallery_square", "default", True),
    ("record_square", "default", True),
    ("fluid_scene", "default", True),
    ("metal_vhs", "default", True),
    ("premium_card", "default", True)
]

def run_test(template: str, platform: str, is_remotion: bool, src: Path, tests_dir: Path, genre: str) -> bool:
    print(f"\n--- Testing Template: {template} ({platform}) ---")
    
    engine_subfolder = "remotion" if is_remotion else "ffmpeg"
    out_dir = tests_dir / "videos" / engine_subfolder
    out_dir.mkdir(parents=True, exist_ok=True)
    # Format clean template name prefix
    words = template.replace("_", " ").split()
    formatted_words = [w.upper() if w.lower() == "vhs" else w.capitalize() for w in words]
    prefix = " ".join(formatted_words)
    
    out_path = out_dir / f"{prefix} ⋅ {src.stem} [smoke_test].mp4"

    cmd = [
        "./bin/clipped",
        "video",
        str(src),
        "--template", template, 
        "--platform", platform,
        "--output", str(out_path)
    ]
    
    # If using eksternal (symlinks to full tracks), clip a short section
    if genre == "eksternal":
        cmd += ["--start", "60", "--end", "75"]
    
    if is_remotion:
        cmd += ["--captions", "lyrics"]
    
    # Set up environment
    env = os.environ.copy()
    env["PYTHONPATH"] = str(tests_dir.parent / "src")

    try:
        # Run and capture output
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            print(f"✅ {template}: Success")
            return True
        else:
            print(f"❌ {template}: Failed (Exit {result.returncode})")
            print("--- STDERR ---")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {template}: Error: {e}")
        return False

def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke test all video templates.")
    parser.add_argument("-g", "--genre", choices=["hip-hop", "metal", "eksternal"], default="hip-hop",
                        help="Choose the genre folder to use for tests (default: hip-hop)")
    args = parser.parse_args()

    tests_dir = Path(__file__).resolve().parents[1]
    genre_dir = tests_dir / "audio-templates" / args.genre
    
    # Locate all mp3 files, including those in artist subfolders
    audio_files = list(genre_dir.rglob("*.mp3"))
    if not audio_files:
        print(f"Error: No MP3 audio file found in {genre_dir}")
        sys.exit(1)
    
    import random
    src = random.choice(audio_files)
        
    failed = []
    for template, platform, is_remotion in TEMPLATES:
        if not run_test(template, platform, is_remotion, src, tests_dir, args.genre):
            failed.append(template)
    
    print("\n" + "="*40)
    if not failed:
        print("🎉 ALL TEMPLATES PASSED")
    else:
        print(f"💀 FAILED TEMPLATES: {', '.join(failed)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
