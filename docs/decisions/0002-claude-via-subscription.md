# 0002 — Call Claude through the Claude Code CLI on our subscription, not the API

Date: 2026-09-23 · Status: accepted

## Context

The first scaffold called Claude with the Anthropic Python SDK, which needs an API key and bills per token. The project owner wants all AI work to run on their own Claude subscription instead.

## Decision

- `llm/client.py` runs `claude -p --output-format json --allowedTools Read` as a subprocess. The Claude Code CLI is logged in with the owner's Claude account, so usage counts against the subscription.
- Images are passed as absolute file paths (plus `--add-dir` for their folders); Claude opens them with the read-only Read tool.
- `ANTHROPIC_API_KEY` is removed from the subprocess environment so the CLI cannot fall back to API billing.
- The `anthropic` SDK dependency is removed.

## Consequences

- No API key or API billing. Throughput is bounded by the subscription's usage limits, so runs on long manuals may need to pause and resume (stages are re-runnable).
- Each call starts a CLI process, which is slower than a direct API call; fine for a hackathon-sized batch.
- Tests use a fake `claude` executable, so CI needs no Claude access.
