# LEGO Builder

Turn a LEGO building-instruction PDF into a beat-synced, vertical short video for social media: bricks snap into place on the beat, and the finished model is revealed at the end.

## Prerequisites

- Python ≥ 3.10 (macOS ships 3.9; install a newer one with Homebrew or mise)
- Node ≥ 18
- ffmpeg (`brew install ffmpeg`)
- GitHub Copilot CLI, signed in (see below)

## Quick start

```bash
cp .env.example .env          # optional settings; no API key needed
make setup                    # Python venv + Node deps
# put an instruction PDF in data/input/ and add a track to assets/music/
make run PDF=data/input/my-set.pdf MUSIC=assets/music/track.mp3
make render RUN=<run_id> LEN=30
```

The rendered video appears in `video/out/`.

## AI access: GitHub Copilot, not a paid API

The AI steps call the model through **GitHub Copilot CLI** (`copilot -p`), on your own GitHub Copilot plan. No API key is used or needed.

1. Install Copilot CLI: `brew install --cask copilot-cli` (or `npm install -g @github/copilot`). See https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli
2. Run `copilot` once and sign in with `/login`. If your organisation manages Copilot, Copilot CLI must be enabled in its policy.
3. Optional: pick a model that can read images with `LEGO_BUILDER_MODEL` in `.env` (default: the CLI's default model).

Each step image is one Copilot request, so a 100-step manual uses roughly 100–150 requests of your plan's allowance. Replies are cached, so re-running a stage on unchanged inputs costs nothing. Claude Code can still be used instead with `LEGO_BUILDER_LLM=claude` (ADR 0004).

## Project structure

- `pipeline/` — Python. Reads the PDF, uses an LLM (via Copilot CLI) to understand and score each step, picks the snap moments, detects beats, and writes `06_timeline.json`.
- `video/` — Remotion (React). Renders the timeline into MP4 videos.
- `docs/` — plan, architecture, data contracts, task board, decision records.

Contributors and AI agents: start with [AGENTS.md](AGENTS.md), then [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/tasks.md](docs/tasks.md). Recipes and debugging tips: [docs/dev-guide.md](docs/dev-guide.md).
