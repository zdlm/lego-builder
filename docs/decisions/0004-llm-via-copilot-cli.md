# 0004 — Call the LLM through GitHub Copilot CLI (supersedes 0002)

Date: 2026-10-28 · Status: accepted

## Context

ADR 0002 routed every model call through the Claude Code CLI on the owner's Claude subscription. The team now works with GitHub Copilot, and everyone has a Copilot plan, so the pipeline should use that instead of a separate Claude subscription. The rule stays the same: no API keys, no pay-per-use APIs.

## Decision

- `llm/client.py::ask_json` runs GitHub Copilot CLI non-interactively: `copilot -p <prompt> --silent --attachment <image> … --no-custom-instructions --disable-builtin-mcps --no-ask-user --available-tools=view`.
  - Images are sent as attachments, so the selected model (`LEGO_BUILDER_MODEL`, default: CLI default) must support vision and the organisation policy must allow image input.
  - `--no-custom-instructions` keeps this repo's `AGENTS.md` out of the model context; the prompts in `llm/prompts/` are the only instructions.
  - The CLI is signed in once with `/login` (or `COPILOT_GITHUB_TOKEN` in the shell for headless use); the pipeline never stores a token.
- Claude Code stays available as an alternative backend with `LEGO_BUILDER_LLM=claude`; it keeps stripping `ANTHROPIC_API_KEY` as in ADR 0002.
- Replies are validated with Pydantic and cached per backend + model + prompt + image bytes in `data/cache/llm/`.

## Consequences

- One request of the user's Copilot plan per step image; caching keeps re-runs free.
- Copilot CLI must be enabled for the user (organisation policy) and a vision-capable model selected.
- Replies may differ from Claude Code's; prompt tweaks should be checked on a few real steps (task 3 / task 5 workflow).
- Tests use fake `copilot` and `claude` executables, so CI needs no LLM access.
