# LEGO Builder

Turn a LEGO building-instruction PDF into a beat-synced, vertical short video for social media: bricks snap into place on the beat, and the finished model is revealed at the end.

## Quick start

```bash
cp .env.example .env          # add your ANTHROPIC_API_KEY
make setup                    # Python venv + Node deps
# put an instruction PDF in data/input/ and add a track to assets/music/
make run PDF=data/input/my-set.pdf MUSIC=assets/music/track.mp3
make render RUN=<run_id> LEN=30
```

The rendered video appears in `video/out/`.

## Project structure

- `pipeline/` — Python. Reads the PDF, uses Claude to understand and score each step, picks the snap moments, detects beats, and writes `06_timeline.json`.
- `video/` — Remotion (React). Renders the timeline into MP4 videos.
- `docs/` — plan, architecture, data contracts, task board, decision records.

Contributors and AI agents: start with [AGENTS.md](AGENTS.md).
