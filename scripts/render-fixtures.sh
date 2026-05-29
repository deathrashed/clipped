#!/bin/sh
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REMOTION_DIR="$SCRIPT_DIR/../remotion"
QA_DIR="$SCRIPT_DIR/../.qa/phase-3-art-direction"
mkdir -p "$QA_DIR"

render() {
  local comp=$1
  local fixture=$2
  local label=$3
  echo "Rendering $label ($comp ← $fixture)..."
  cd "$REMOTION_DIR"
  npx remotion still src/index.ts "$comp" "$QA_DIR/$label.png" \
    --frame=60 \
    --props "src/fixtures/$fixture.json" \
    --log=warn 2>/dev/null
}

render "gallery-square" "qa-hiphop" "gallery-square_hiphop"
render "record-square" "qa-vinyl" "record-square_vinyl"
render "pulse-reel" "qa-hiphop" "pulse-reel_hiphop"
render "metal-vhs" "qa-metal" "metal-vhs_metal"
render "premium-card" "qa-clean" "premium-card_clean"
render "gallery-square" "qa-metal" "gallery-square_metal"
render "gallery-square" "qa-clean" "gallery-square_editorial"
render "record-square" "qa-metal" "record-square_metal"
render "metal-vhs" "qa-vhs" "metal-vhs_vhs-no-assets"
render "premium-card" "qa-vinyl" "premium-card_vinyl-no-logo"

echo "Done. $QA_DIR"
ls -lh "$QA_DIR"
