# AGENTS.md — Guide for AI agents working in this repo

This file is the single source of truth for any AI model (Claude, GPT, Gemini, Copilot, etc.) or human contributor working on this project. Read it fully before making changes. `CLAUDE.md` simply imports this file.

## What we are building

LEGO Builder turns a LEGO building-instruction PDF into a vertical (9:16), beat-synced short video for social media marketing. Bricks snap into place on the music's beats ("click, click, click"), the pace accelerates, and the finished model is revealed at the end. It is a showcase video, not a tutorial: rhythm and satisfaction matter more than showing every step.

Full product plan: `docs/plan.md`. Architecture: `docs/architecture.md`. Data contracts: `docs/data-contracts.md`.

## Repository layout

```
lego-builder/
├── AGENTS.md              ← you are here (rules for agents)
├── CLAUDE.md              ← imports AGENTS.md
├── README.md              ← human quick start
├── Makefile               ← all common commands
├── .env.example           ← required environment variables
├── docs/
│   ├── plan.md            ← product plan (goals, priorities, schedule)
│   ├── architecture.md    ← pipeline design and module boundaries
│   ├── data-contracts.md  ← JSON files passed between stages
│   ├── tasks.md           ← shared task board (claim tasks here)
│   └── decisions/         ← architecture decision records (ADRs)
├── pipeline/              ← Python: PDF → timeline.json
│   ├── pyproject.toml
│   ├── src/lego_builder/
│   │   ├── cli.py         ← `lego-builder` command (Typer)
│   │   ├── config.py      ← settings loaded from env
│   │   ├── models.py      ← Pydantic data contracts (source of truth)
│   │   ├── paths.py       ← run-directory layout helpers
│   │   ├── llm/           ← Claude Code CLI wrapper + prompt files
│   │   └── stages/        ← one module per pipeline stage
│   └── tests/
├── video/                 ← TypeScript/Remotion: timeline.json → MP4
│   └── src/
│       ├── compositions/  ← top-level videos (BuildReel)
│       ├── components/    ← Hook, SnapStep, Reveal, overlays
│       └── lib/           ← timeline types + loading
├── web/                   ← optional Next.js UI (not started)
├── assets/                ← music, sfx, fonts (check licences!)
├── scripts/               ← setup and helper scripts
└── data/                  ← gitignored: input PDFs and run outputs
```

## How the system fits together

The pipeline is a chain of stages. Each stage reads files from a run directory and writes new files into it. Stages never call each other directly; they communicate only through files whose shapes are defined in `pipeline/src/lego_builder/models.py`.

```
data/input/<set>.pdf
  s01_extract    → runs/<run_id>/01_pages/*.png, 01_steps/*.png, steps_raw.json
  s02_understand → runs/<run_id>/02_understanding.json   (+ 02_masks/*.png)
  s03_select     → runs/<run_id>/03_selection.json
  s04_assets     → runs/<run_id>/04_assets/*.png          (cutouts for animation)
  s05_beats      → runs/<run_id>/05_beats.json
  s06_timeline   → runs/<run_id>/06_timeline.json         ← handed to video/
video/ (Remotion) reads 06_timeline.json + assets → out/<run_id>_<len>s.mp4
```

The Python side decides *what* happens and *when*. The Remotion side decides only *how it looks*. Keep that boundary.

## Rules for agents

1. **Read before writing.** Check `docs/tasks.md` for what is in progress, and read the modules you will touch.
2. **Claim your task.** Before starting, add your name/model and the date next to the task in `docs/tasks.md`. Mark it done when finished. Don't work on a task someone else has claimed.
3. **Stay in your lane.** Keep changes inside the module or stage you are working on. If you need to change a data contract, see rule 4.
4. **Data contracts are shared.** `models.py` is the source of truth. If you change a model: update `docs/data-contracts.md`, update the mirrored TypeScript types in `video/src/lib/timeline.ts`, bump `SCHEMA_VERSION` in `models.py`, and note it in your commit message.
5. **Stages are pure and re-runnable.** A stage reads its inputs from the run directory, writes its outputs there, and can be re-run without side effects. No hidden global state.
6. **Claude runs on the owner's subscription, never the API.** All model calls go through `llm/client.py`, which shells out to the Claude Code CLI (`claude -p`). Do not add the `anthropic` SDK, API keys or any other paid model API.
7. **Prompts live in files.** LLM prompts go in `pipeline/src/lego_builder/llm/prompts/*.md`, never inline in Python. Always ask the model for JSON and validate it with the Pydantic models.
8. **Record decisions.** Any significant technical choice (new library, changed approach) gets a short ADR in `docs/decisions/NNNN-title.md`.
9. **Test what you add.** Add or update tests in `pipeline/tests/`. Run `make test` and `make lint` before finishing.
10. **Never commit secrets or data.** Local settings belong in `.env` (gitignored). PDFs, renders and run outputs belong in `data/` (gitignored).
11. **Licensing.** Only add music, sound effects or fonts whose licence allows commercial social media use; record the source in `assets/README.md`.

## Commands

```
make setup        # install Python + Node dependencies
make run PDF=data/input/<set>.pdf    # run the whole pipeline
make stage STAGE=s03_select RUN=<run_id>   # re-run one stage
make preview RUN=<run_id>             # open Remotion Studio on a run
make render RUN=<run_id> LEN=30       # render MP4 (15 / 30 / 60)
make test         # Python tests
make lint         # ruff + mypy + tsc
```

## Conventions

- Python ≥ 3.10, formatted and linted with `ruff`, type-checked with `mypy`. Use type hints everywhere.
- TypeScript strict mode; React function components; no `any`.
- Filenames: `snake_case.py`, `PascalCase.tsx` for components, `camelCase.ts` for helpers.
- Commit messages: `<area>: <what changed>` e.g. `pipeline/s03: weight milestones higher`. Areas: `pipeline`, `video`, `web`, `docs`, `assets`, `build`.
- Video spec: 1080×1920, 30 fps, lengths 15 / 30 / 60 s.
- All times in timeline files are in **seconds (float)**; Remotion converts to frames.
