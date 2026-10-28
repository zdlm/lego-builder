# Developer guide

Practical recipes. Rules are in [AGENTS.md](AGENTS.md); design is in [architecture.md](architecture.md).

## Environment

- Python ≥ 3.10 is required. macOS ships 3.9, so install a newer one (e.g. `brew install python@3.12` or `mise`). `scripts/setup.sh` picks the newest `python3.x` it finds.
- `make setup` creates `pipeline/.venv` and runs `npm install` in `video/`.
- Without the `claude` CLI you can still run everything except the Claude-backed steps (s01 segmentation, s02 understanding, optional s03 re-ranking). Use `--no-llm-rank` for s03.

## Running without spending Claude usage

- Unit tests never call Claude (`make test`).
- Re-run only the stage you are working on against an existing run: `make stage STAGE=s03_select RUN=<run_id>`. Earlier stages' outputs stay on disk.
- For heuristics (s03, s05, s06), edit/copy a run's JSON by hand and re-run just that stage.
- For the video side you only need a run's `06_timeline.json` plus the images it points to. Ask for a zipped run folder, unzip it into `data/runs/`, then `make preview RUN=<run_id>`.

## Recipe: change a stage

1. Claim the task in `docs/tasks.md`.
2. Read the stage module and the models it reads and writes.
3. Make the change; keep the stage a pure function of its input files (no globals, no hidden state).
4. Add a test in `pipeline/tests/` that builds the input models in memory and asserts on the output models (see `test_select.py` and `test_timeline.py`).
5. Re-run the stage on a real run and check the output by eye.
6. `make test lint`; update `docs/architecture.md` status if it changed.

## Recipe: add a stage

1. Create `pipeline/src/lego_builder/stages/sNN_name.py` exposing `run(ctx: StageContext) -> None`.
2. Register it in `STAGES` in `stages/__init__.py` (order matters; the CLI runs them in dict order).
3. Add its output paths to `RunPaths` in `paths.py` and, if it writes JSON, a Pydantic model in `models.py` (then follow the contract steps below).
4. Document it in `docs/architecture.md` (run-directory table and stage table) and write an ADR if it adds a dependency.

## Recipe: change a data contract

Follow "Changing a contract" in [data-contracts.md](data-contracts.md). Checklist: `models.py` → bump `SCHEMA_VERSION` → `video/src/lib/timeline.ts` → `docs/data-contracts.md` → tests → mention the bump in the commit message and tell the other workers.

## Recipe: add or change an LLM prompt

- Prompts are Markdown files in `pipeline/src/lego_builder/llm/prompts/`. Never inline them in Python.
- Load with `load_prompt(name, **vars)`. It uses `str.format`, so literal braces in JSON examples must be doubled (`{{` and `}}`), and placeholders are single braces (`{width}`).
- Call through `ask_json(prompt, images, SchemaModel)` in `llm/client.py`. It validates the reply with Pydantic and retries once with the error. Always ask for "JSON only".
- Images are file paths that Claude opens itself. Keep images reasonably small; each call is one CLI process on a subscription with usage limits.
- Test prompt changes on 3–5 real steps before running a whole manual, and note the result in your PR.
- Never add the `anthropic` SDK or an API key (ADR 0002).

## Recipe: change the video

- `video/` only reads `06_timeline.json`. If you need new information (for example a colour or a sound name), add it on the pipeline side via a contract change; do not compute it in React.
- Components live in `video/src/components/`, one per event kind. All timing is derived from `start_s` / `duration_s` times `fps`.
- Preview with `make preview RUN=<run_id>`; render with `make render RUN=<run_id> LEN=30`.
- Music, SFX and fonts must come from `assets/` (served through the `public/assets` symlink created by `video/scripts/link-run.mjs`).
- No `any`; run `cd video && npx tsc --noEmit`.

## Debugging checklist

| Symptom | Check |
|---|---|
| `claude not found` / auth errors | Install Claude Code and run `claude` once to sign in. Make sure `LEGO_BUILDER_CLAUDE_BIN` is right. |
| Claude call times out | Raise `LEGO_BUILDER_CLAUDE_TIMEOUT_S`; check your subscription usage limit; re-run the stage (it is re-runnable). |
| Step boxes cut the wrong area | `01_pages/*.png` vs `01_steps_raw.json`; tune `segment_page.md` (task 3). |
| Model / parts cut-outs wrong | `04_assets/model_NNN.png` and `part_NNN_K.png`; check `model_bbox` / `callout_bbox` / `landing` for that step in `02_understanding.json` (they come from Claude, refined in `imaging.py`). |
| Snaps not on beat | `05_beats.json` `beats_s`; tests in `test_timeline.py`. |
| Remotion cannot find a run | `video/public/runs` symlink, and `06_timeline.json` exists under `data/runs/<run_id>/`. |
| Media 404 in Studio | Paths must be under `assets/` or inside the run directory. |

## Before you hand over

`make test`, `make lint` (no new errors), docs updated, task board updated, handoff note written if unfinished.
