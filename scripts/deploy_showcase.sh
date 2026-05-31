#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Deploying to Netlify (with build and functions)..."
cd "$REPO_DIR/showcase"

npx netlify deploy --build --prod

echo ""
echo "==> Live: https://clipped-showcase.netlify.app"
