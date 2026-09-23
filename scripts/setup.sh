#!/usr/bin/env bash
# Install all dependencies for LEGO Builder.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Python pipeline"
python3 -m venv pipeline/.venv
pipeline/.venv/bin/pip install --upgrade pip
pipeline/.venv/bin/pip install -e "pipeline[dev]"

echo "==> Remotion video"
(cd video && npm install)

[ -f .env ] || { cp .env.example .env; echo "Created .env"; }
command -v claude >/dev/null || echo "Note: Claude Code CLI not found — install it and run \`claude\` once to sign in with your Claude subscription"
command -v ffmpeg >/dev/null || echo "Note: ffmpeg not found (brew install ffmpeg) — needed for audio handling"
echo "Done."
