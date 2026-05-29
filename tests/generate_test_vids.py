import os
import subprocess
import sys

AUDIO_SRC = "/Volumes/Eksternal/Audio/Metal/D/Disincarnate/1993 - Dreams of the Carrion Kind/07. Entranced.mp3"
OUT_DIR = "/Users/rd/Scripts/Riley/clipped/_video/tests"

# 5 seconds duration is fast for smoke-testing and visual checking
START_TIME = "01:03"
END_TIME = "01:08"

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
    ("static", "default", False),
    ("vertical", "instagram", False),
    ("vertical_wave", "instagram", False),
    ("waveformbar", "default", False),
]

def main():
    if not os.path.exists(AUDIO_SRC):
        print(f"Error: Audio source file not found at: {AUDIO_SRC}")
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)

    # Allow filtering by templates passed as arguments
    targets = sys.argv[1:]
    to_run = TEMPLATES
    if targets:
        to_run = [t for t in TEMPLATES if t[0] in targets]
        if not to_run:
            print(f"Error: None of the requested templates {targets} match available templates.")
            print(f"Available: {[t[0] for t in TEMPLATES]}")
            sys.exit(1)
        print(f"Starting fast test video generation (5 seconds) for: {[t[0] for t in to_run]}...")
    else:
        print(f"Starting fast test video generation (5 seconds per template) for ALL templates...")
        print(f"Tip: You can pass specific template names as arguments to test one at a time, e.g.:")
        print(f"  python3 tests/generate_test_vids.py premium_card gallery_square")

    # Set up environment to use the right python path
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()

    failed = []
    for template, platform, is_remotion in to_run:
        out_name = f"07. Entranced ({template}) [preview].mp4"
        out_path = os.path.join(OUT_DIR, out_name)
        
        print(f"\n==========================================")
        print(f"Rendering: {template} ({platform}) -> {out_name}")
        print(f"==========================================")

        cmd = [
            "./bin/clipped",
            "video",
            AUDIO_SRC,
            "--template", template,
            "--platform", platform,
            "--start", START_TIME,
            "--end", END_TIME,
            "--output", out_path,
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
        print(f"🎉 GENERATION COMPLETED SUCCESSFULLY (5-SEC PREVIEWS)")

if __name__ == "__main__":
    main()
