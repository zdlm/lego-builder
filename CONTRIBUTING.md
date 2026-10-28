# Contributing

For humans and AI agents alike. Technical rules are in [AGENTS.md](AGENTS.md); this file covers how we work together. Chat in any language, but keep everything in the repo (code, docs, commits) in English.

## Onboarding in 10 minutes

1. Install prerequisites: Python ≥ 3.10, Node ≥ 18, ffmpeg, and GitHub Copilot CLI (signed in; see README).
2. `make setup`, then `make test`.
3. Read, in order: [AGENTS.md](AGENTS.md) → [docs/architecture.md](docs/architecture.md) → [docs/data-contracts.md](docs/data-contracts.md) → [docs/glossary.md](docs/glossary.md).
4. Pick a task from [docs/tasks.md](docs/tasks.md). Recipes for common changes are in [docs/dev-guide.md](docs/dev-guide.md).

## Working in parallel

- **One task, one branch, one owner.** Branch name: `<area>/<short-task>` (e.g. `pipeline/s03-weights`, `video/hook-polish`).
- **Claim before you start.** Edit the Owner column in `docs/tasks.md` and push that single-line change to `main` first (or open a tiny PR), so nobody else picks the same task.
- **Several agents on one machine?** Give each its own checkout: `git worktree add ../lego-builder-<task> -b <branch>`. Never let two agents edit the same working tree.
- **Stay in your area.** `pipeline/` and `video/` meet only at `06_timeline.json`. If you need a contract change, make it in its own small PR first and tell the others (see "Changing a contract" in `docs/data-contracts.md`).
- **Don't edit someone else's in-progress files** without asking the owner.
- **Run directories are local.** `data/` is gitignored. Everyone has their own runs and their own Copilot login (usage is per person, see ADR 0004).

## Sharing inputs and outputs

PDFs, music, renders and run folders are not committed. Share them through the team drive and say in the task which file you used (name and version). When a run is useful to others (for example a good `06_timeline.json` for video work), zip `data/runs/<run_id>/` and share the zip.

Only commit assets whose licence allows commercial social use, and log them in `assets/README.md`.

## Commits and pull requests

- Commit message: `<area>: <what changed>` (areas: `pipeline`, `video`, `web`, `docs`, `assets`, `build`). Mention `SCHEMA_VERSION` bumps.
- Keep PRs small and about one thing. Fill in the PR template.
- Before opening a PR: `make test` and `make lint`. `make lint` currently has known mypy errors from OpenCV stubs (task 14); don't add new ones.
- Update docs in the same PR as the code change. Stale docs are bugs.

## Definition of done

- Code works on a real run, not only in unit tests (say which run you tried).
- Tests added or updated in `pipeline/tests/` for pipeline logic.
- Docs updated: `docs/architecture.md` stage status, `docs/data-contracts.md` if a model changed, ADR if a technical decision was made.
- Task moved to Done in `docs/tasks.md`, with a note of anything left over.

## Handing work over

If you stop mid-task (human or agent), leave a short note under your task in `docs/tasks.md`: what is done, what is not, how to reproduce, known problems. The next person must be able to continue from the note alone.
