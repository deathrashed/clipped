
import os
import subprocess
import sys

DEFAULT_SRC = "/Volumes/Eksternal/Audio/Metal/D/Demolition Hammer/1988 - Skull Fracturing Nightmare/02. Corpse Content (Happy Death).mp3"
TEMPLATES = [
    "spinner", "fade", "static", "vertical", "minimal", 
    "cinematic", "waveformbar", "vertical_wave", "reel"
]


def run_test(template: str, src: str) -> bool:
    print(f"\n--- Testing Template: {template} ---")
    platform = "default"
    if template in ["vertical", "vertical_wave", "reel"]:
        platform = "instagram"
    elif template == "cinematic":
        platform = "youtube"

    cmd = [
        os.path.expanduser("~/Scripts/.config/python/run.sh"), "-m", "clipped_src.main", 
        "video", src,
        "--template", template, 
        "--start", "00:30", 
        "--end", "00:32",
        "--platform", platform
    ]
    
    try:
        # Run and capture output
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
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
    src = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CLIPPED_TEST_AUDIO", DEFAULT_SRC)
    if not os.path.exists(src):
        print(f"Error: Source file not found: {src}")
        print("Pass a sample path as argv[1] or set CLIPPED_TEST_AUDIO.")
        sys.exit(1)
        
    failed = []
    for t in TEMPLATES:
        if not run_test(t, src):
            failed.append(t)
    
    print("\n" + "="*40)
    if not failed:
        print("🎉 ALL TEMPLATES PASSED")
    else:
        print(f"💀 FAILED TEMPLATES: {', '.join(failed)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
