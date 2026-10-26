# pipeline/ — agent notes

Read the root [AGENTS.md](../AGENTS.md) first. This file only adds what is specific to the Python side.

- Source in `src/lego_builder/`; tests in `tests/`. Run from the repo root with `make test` / `make lint`, or `cd pipeline && .venv/bin/pytest -q`.
- Every stage exposes `run(ctx: StageContext) -> None`, reads files from `ctx.paths` (see `paths.py`) and writes its own outputs. Never import one stage from another; share logic through a neutral module instead.
- Read and write JSON through `jsonio.py`, and always validate against the models in `models.py`.
- LLM calls go through `llm/client.py::ask_json` only. Prompts are `.md` files in `llm/prompts/`; braces in JSON examples are doubled (`{{ }}`) because prompts are filled with `str.format`.
- Tests must not call Claude, read real PDFs from `data/`, or depend on the network. Build models in memory or use small files under `tests/fixtures/`.
- Style: Python ≥ 3.10, type hints everywhere, `ruff` line length 100, mypy strict. Known pre-existing mypy errors come from OpenCV stubs (s01/s02/s04/s05); don't add new ones and don't blanket-suppress.
- Times are seconds (float). Step numbers are the printed numbers, not indexes.
- If you touch `models.py`: bump `SCHEMA_VERSION`, update `docs/data-contracts.md` and `video/src/lib/timeline.ts`.
