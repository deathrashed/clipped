#!/usr/bin/env bash
set -euo pipefail

# This script packages the showcase and the generated media,
# then deploys it automatically to Netlify.

echo "==> Staging showcase and media for deployment..."
rm -rf dist_showcase
mkdir -p dist_showcase/showcase
mkdir -p dist_showcase/_video
mkdir -p dist_showcase/_audio
mkdir -p dist_showcase/assets

# Copy showcase HTML/CSS
cp -r showcase/* dist_showcase/showcase/

# Copy media files and assets (ignore if directories are empty/missing)
cp -r _video/* dist_showcase/_video/ 2>/dev/null || true
cp -r _audio/* dist_showcase/_audio/ 2>/dev/null || true
cp -r assets/* dist_showcase/assets/ 2>/dev/null || true

# Add a redirect so the root domain points straight to the showcase
echo "/  /showcase/  301" > dist_showcase/_redirects

echo "==> Deploying to Netlify Production..."
npx netlify deploy --dir=dist_showcase --prod

echo ""
echo "==> Done! Your showcase is live at: https://riley-clipped-showcase.netlify.app"
