# Copilot instructions

All project instructions live in [AGENTS.md](../AGENTS.md). Read it fully before changing anything, then follow [CONTRIBUTING.md](../CONTRIBUTING.md) and claim a task in [docs/tasks.md](../docs/tasks.md).

Key rules in one place:

- Python side decides what and when; Remotion decides only how it looks. They meet only at `06_timeline.json`.
- `pipeline/src/lego_builder/models.py` is the source of truth for data contracts; changing it means bumping `SCHEMA_VERSION` and updating `docs/data-contracts.md` and `video/src/lib/timeline.ts`.
- Claude is called only through `llm/client.py` (Claude Code CLI on the owner's subscription). Never add the `anthropic` SDK or API keys.
- Prompts live in `llm/prompts/*.md`, not inline.
- Run `make test` and `make lint` before finishing. Never commit secrets or anything under `data/`.
