#!/usr/bin/env bash
set -euo pipefail

# Determine REPO_DIR correctly whether run from root or from showcase/
if [ -d "showcase" ]; then
  REPO_DIR="$(pwd)"
else
  REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
fi

DIST="$REPO_DIR/showcase/dist"

echo "==> Syncing showcase database..."
cd "$REPO_DIR"
# Use whichever python tool is available
if command -v uv >/dev/null 2>&1; then
  uv run scripts/sync_showcase.py || true
else
  python3 scripts/sync_showcase.py || true
fi

echo "==> Staging dist..."
rm -rf "$DIST"
mkdir -p "$DIST" "$DIST/_video" "$DIST/_audio" "$DIST/assets" "$DIST/tests/videos/remotion" "$DIST/tests/videos/ffmpeg"

cp -r showcase/public/* "$DIST/" || true
cp -r assets/*   "$DIST/assets/"          2>/dev/null || true
cp -r _video/*   "$DIST/_video/"          2>/dev/null || true
cp -r _audio/*   "$DIST/_audio/"          2>/dev/null || true
cp -r tests/videos/remotion/* "$DIST/tests/videos/remotion/" 2>/dev/null || true
cp -r tests/videos/ffmpeg/*   "$DIST/tests/videos/ffmpeg/"   2>/dev/null || true

echo "==> Build complete in $DIST"
