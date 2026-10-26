# video/ — agent notes

Read the root [AGENTS.md](../AGENTS.md) first. This file only adds what is specific to the Remotion side.

- Input is one file: `06_timeline.json`, typed in `src/lib/timeline.ts` (a hand-kept mirror of `pipeline/src/lego_builder/models.py`). Do not read other pipeline files and do not decide *what* or *when* here; only *how it looks*.
- Spec: 1080×1920, 30 fps, 15/30/60 s. Take fps, size and length from the timeline, never hard-code them in components.
- Convert seconds to frames with `Math.round(seconds * fps)`.
- One component per event kind in `src/components/`; `src/compositions/BuildReel.tsx` maps events to `<Sequence>`s.
- Media must come from `assets/` or the run directory, served via the symlinks `public/assets` and `public/runs` (created by `scripts/link-run.mjs`). No remote URLs, no unlicensed fonts or music.
- Style: TypeScript strict, React function components, no `any`, `PascalCase.tsx` for components.
- Check: `cd video && npx tsc --noEmit` (needs `npm install` first). Preview with `make preview RUN=<run_id>`.
- If you need a new field from the pipeline, request a contract change (root AGENTS.md rule 4) instead of inventing it locally.
