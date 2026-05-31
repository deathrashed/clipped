#!/usr/bin/env bash
# Generate a frame sheet for Phase 6 Remotion templates.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTION_DIR="$ROOT/src/remotion"
OUT_DIR="$ROOT/tests/frames/remotion"
PROPS_TEMPLATE="$REMOTION_DIR/src/test-simple-props.json"
PYGEN="$REMOTION_DIR/src/gen_frame_props.py"

# Ensure test assets in public root
echo "=== Preparing test assets ==="
ASSET_SRC="$ROOT/tests/audio-templates"
for f in test_cover.jpg test_logo.png test_artist.jpg test_audio.mp3; do
  [ -f "$REMOTION_DIR/public/$f" ] || {
    case "$f" in
      test_cover.jpg)  cp "$ASSET_SRC/metal/deicide/cover.jpg" "$REMOTION_DIR/public/$f" ;;
      test_logo.png)   cp "$ASSET_SRC/metal/logo.png"          "$REMOTION_DIR/public/$f" ;;
      test_artist.jpg) cp "$ASSET_SRC/metal/artist.jpg"        "$REMOTION_DIR/public/$f" ;;
      test_audio.mp3)  cp "$ASSET_SRC/metal/deicide/Deicide - They Are the Children of the Underworld (0.50 - 1.20).mp3" "$REMOTION_DIR/public/$f" ;;
    esac
  }
done
echo "  Assets ready"

mkdir -p "$OUT_DIR"

TEMPLATES=(
  "vinyl-sleeve-pro:1080:1920:VinylSleevePro"
  "artist-focus-pro:1080:1920:ArtistFocusPro"
  "metadata-card-pro:1080:1920:MetadataCardPro"
  "waveform-stage-pro:1080:1920:WaveformStagePro"
  "glass-card-pro:1080:1920:GlassCardPro"
  "neon-pulse-pro:1080:1920:NeonPulsePro"
  "cinematic-pro:1080:1920:CinematicPro"
  "concert-poster-pro:1080:1350:ConcertPosterPro"
  "spinner-pro:1080:1080:SpinnerPro"
  "collector-card:1080:1080:CollectorCard"
  "band-intro:1080:1080:BandIntro"
  "audio-orb:1080:1080:AudioOrb"
  "metal-vhs-pro:1080:1080:MetalVHSPro"
)

# Use only the phase arg: "mid" for primary, "early" for logo check, "late" for outro
PHASES=("early" "mid" "late")

for entry in "${TEMPLATES[@]}"; do
  IFS=':' read -r comp_id width height label <<< "$entry"
  echo "[${label}] (${width}x${height})"

  for phase in "${PHASES[@]}"; do
    case "$phase" in
      early) frame=30  ;;
      mid)   frame=150 ;;
      late)  frame=210 ;;
    esac

    out="$OUT_DIR/${label}_${phase}.png"
    [ -f "$out" ] && { echo "    ✓ (cached) ${phase}"; continue; }

    props=$(python3 "$PYGEN" "$PROPS_TEMPLATE" "$comp_id" "$label" "$width" "$height")
    cd "$REMOTION_DIR"
    if npx remotion still src/index.ts "$comp_id" "$out" \
      --props="$props" \
      --frame="$frame" \
      --log=error 2>/dev/null; then
      dims=$(magick identify -format "%wx%h" "$out" 2>/dev/null || echo "?")
      echo "    ✓ ${phase} (${dims})"
    else
      echo "    ✗ ${phase} FAILED"
    fi
  done
  echo ""
done

echo "=== Contact sheets ==="
cd "$OUT_DIR"
for aspect in "1080x1920" "1080x1350" "1080x1080"; do
  short="${aspect/x/_}"
  maps=()
  for f in *_mid.png; do
    [ -f "$f" ] || continue
    dims=$(magick identify -format "%wx%h" "$f" 2>/dev/null || echo "")
    [ "$dims" = "$aspect" ] && maps+=("$f")
  done
  if [ ${#maps[@]} -gt 0 ]; then
    echo "  ${short}: ${#maps[@]} frames"
    magick montage "${maps[@]}" -tile 4x2 -geometry "360x640>+4+4" \
      -title "$short" -pointsize 14 -background "#111" -fill "#ccc" -label "%f" \
      "contact_${short}.png" 2>/dev/null && echo "  ✓ contact_${short}.png"
  fi
done

echo ""
echo "=== Done ==="
ls "$OUT_DIR"/*.png 2>/dev/null | wc -l | xargs echo "Total PNGs:"
