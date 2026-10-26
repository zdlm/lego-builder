#!/usr/bin/env bash
# Install all dependencies for LEGO Builder.
set -euo pipefail
cd "$(dirname "$0")/.."

PY=""
for c in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$c" >/dev/null && "$c" -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then PY="$c"; break; fi
done
[ -n "$PY" ] || { echo "Python >= 3.10 required (try: brew install python@3.12)"; exit 1; }

echo "==> Python pipeline ($PY)"
"$PY" -m venv pipeline/.venv
pipeline/.venv/bin/pip install --upgrade pip
pipeline/.venv/bin/pip install -e "pipeline[dev]"

echo "==> Remotion video"
(cd video && npm install)

[ -f .env ] || { cp .env.example .env; echo "Created .env"; }
command -v claude >/dev/null || echo "Note: Claude Code CLI not found — install it and run \`claude\` once to sign in with your Claude subscription"
command -v ffmpeg >/dev/null || echo "Note: ffmpeg not found (brew install ffmpeg) — needed for audio handling"
echo "Done."
