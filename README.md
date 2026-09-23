# LEGO Builder

Turn a LEGO building-instruction PDF into a beat-synced, vertical short video for social media: bricks snap into place on the beat, and the finished model is revealed at the end.

## Quick start

```bash
cp .env.example .env          # optional settings; no API key needed
make setup                    # Python venv + Node deps
# put an instruction PDF in data/input/ and add a track to assets/music/
make run PDF=data/input/my-set.pdf MUSIC=assets/music/track.mp3
make render RUN=<run_id> LEN=30
```

The rendered video appears in `video/out/`.

## Claude access: your subscription, not the API

The AI steps call Claude through the **Claude Code CLI** (`claude -p`), which runs on your Claude Pro/Max subscription. No Anthropic API key is used or needed.

1. Install Claude Code: https://docs.claude.com/en/docs/claude-code
2. Run `claude` once and sign in with your Claude account.
3. Make sure `ANTHROPIC_API_KEY` is **not** set in your shell (the pipeline also removes it before calling the CLI).

Each step image is one Claude call, so a 100-step manual uses roughly 100–150 messages of your subscription's usage allowance.

## Project structure

- `pipeline/` — Python. Reads the PDF, uses Claude to understand and score each step, picks the snap moments, detects beats, and writes `06_timeline.json`.
- `video/` — Remotion (React). Renders the timeline into MP4 videos.
- `docs/` — plan, architecture, data contracts, task board, decision records.

Contributors and AI agents: start with [AGENTS.md](AGENTS.md).
