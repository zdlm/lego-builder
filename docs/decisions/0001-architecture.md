# 0001 — Two-part architecture: Python pipeline + Remotion renderer

Date: 2026-09-23 · Status: accepted

## Context

We need PDF processing, computer vision, LLM calls and audio analysis (strongest in Python), and frame-accurate, beat-synced motion graphics (strongest in Remotion/React). Several people and AI models will work in parallel during a hackathon.

## Decision

- Split the project into `pipeline/` (Python) and `video/` (Remotion), connected only by `06_timeline.json`.
- Break the pipeline into numbered stages that communicate through files in a run directory.
- Define every file with Pydantic models in `models.py`; mirror the timeline in TypeScript.
- Keep LLM prompts in Markdown files and always validate replies against the models.

## Consequences

- People can work on any stage or on the video side independently, using saved run folders as fixtures.
- Any stage can be re-run alone, which makes iteration on scoring and animation fast.
- The TypeScript mirror must be kept in sync by hand (rule in AGENTS.md).
