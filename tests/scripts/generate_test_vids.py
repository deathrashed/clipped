import argparse
import os
import subprocess
import sys
from pathlib import Path

TEMPLATES = [
    # Remotion templates
    ("pulse_reel", "instagram", True),
    ("gallery_square", "default", True),
    ("record_square", "default", True),
    ("fluid_scene", "default", True),
    ("metal_vhs", "default", True),
    ("premium_card", "default", True),
    # FFmpeg templates
    ("cinematic", "youtube", False),
    ("fade", "default", False),
    ("minimal", "default", False),
    ("reel", "instagram", False),
    ("spinner", "default", False),
    ("spinner_story", "default", False),
    ("static", "default", False),
    ("vertical", "instagram", False),
    ("vertical_wave", "instagram", False),
    ("waveformbar", "default", False),
]

def main():
    parser = argparse.ArgumentParser(description="Generate visual test videos for templates.")
    parser.add_argument("templates", nargs="*", help="Optional specific template name(s) to run.")
    parser.add_argument("-g", "--genre", choices=["hip-hop", "metal"], default="hip-hop",
                        help="Choose the genre folder to use for tests (default: hip-hop)")
    args = parser.parse_args()

    tests_dir = Path(__file__).resolve().parents[1]
    media_tests_dir = tests_dir.parent / "media" / "tests"
    genre_dir = media_tests_dir / "audio-templates" / args.genre
    
    # Locate the mp3 file
    audio_files = list(genre_dir.glob("*.mp3"))
    if not audio_files:
        print(f"Error: No MP3 audio file found in {genre_dir}")
        sys.exit(1)
    audio_path = audio_files[0]
    
    # Allow filtering by templates passed as arguments
    to_run = TEMPLATES
    if args.templates:
        to_run = [t for t in TEMPLATES if t[0] in args.templates]
        if not to_run:
            print(f"Error: None of the requested templates {args.templates} match available templates.")
            print(f"Available: {[t[0] for t in TEMPLATES]}")
            sys.exit(1)
        print(f"Starting test video generation for genre '{args.genre}' using: {[t[0] for t in to_run]}...")
    else:
        print(f"Starting test video generation for genre '{args.genre}' for ALL templates...")

    # Set up environment
    env = os.environ.copy()
    env["PYTHONPATH"] = str(tests_dir.parent / "src")

    failed = []
    for template, platform, is_remotion in to_run:
        engine_subfolder = "remotion" if is_remotion else "ffmpeg"
        out_dir = media_tests_dir / "videos" / engine_subfolder
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # Format clean template name prefix
        words = template.replace("_", " ").split()
        formatted_words = [w.upper() if w.lower() == "vhs" else w.capitalize() for w in words]
        prefix = " ".join(formatted_words)

        out_name = f"{prefix} ⋅ {audio_path.stem}.mp4"
        out_path = out_dir / out_name
        
        print(f"\n==========================================")
        print(f"Rendering: {template} ({platform}) -> {out_name}")
        print(f"==========================================")

        cmd = [
            "./bin/clipped",
            "video",
            str(audio_path),
            "--template", template,
            "--platform", platform,
            "--output", str(out_path),
        ]

        if is_remotion:
            cmd += ["--captions", "lyrics"]

        print("Command:", " ".join(cmd))
        try:
            res = subprocess.run(cmd, env=env)
            if res.returncode == 0:
                print(f"✅ SUCCESS: {template}")
            else:
                print(f"❌ FAILED: {template} (exit {res.returncode})")
                failed.append(template)
        except Exception as e:
            print(f"❌ ERROR rendering {template}: {e}")
            failed.append(template)

    print("\n" + "="*50)
    if failed:
        print(f"💀 FAILED TEMPLATES: {', '.join(failed)}")
        sys.exit(1)
    else:
        print(f"🎉 GENERATION COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    main()
