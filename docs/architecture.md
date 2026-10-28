# Architecture

## Overview

LEGO Builder has two halves joined by one JSON file.

```
          ┌──────────────── pipeline/ (Python) ────────────────┐        ┌── video/ (Remotion) ──┐
PDF ──▶ s01_extract ─▶ s02_understand ─▶ s03_select ─▶ s04_assets ─┐
                                                                    ├─▶ s06_timeline ─▶ 06_timeline.json ─▶ BuildReel ─▶ MP4
music ──────────────────────────────────────────────▶ s05_beats ───┘
```

- **pipeline/** decides *what* is shown and *when*: which steps, in which order, on which beat.
- **video/** decides *how it looks*: animation curves, flashes, overlays, typography.

Neither side imports the other. The only coupling is `06_timeline.json`, whose shape is defined in `pipeline/src/lego_builder/models.py` and mirrored in `video/src/lib/timeline.ts`.

## Run directory

Every run lives in `data/runs/<run_id>/`. Stages write numbered files so the order is obvious and any stage can be re-run on its own (`make stage STAGE=... RUN=...`).

| File | Written by | Model |
|---|---|---|
| `01_pages/page_NNN.png` | s01_extract | – |
| `01_steps/step_NNN.png` | s01_extract | – |
| `01_steps_raw.json` | s01_extract | `StepsRaw` |
| `02_masks/mask_NNN.png` | s02_understand | – |
| `02_understanding.json` | s02_understand | `Understanding` |
| `03_selection.json` | s03_select | `Selection` |
| `04_assets/model_NNN.png`, `part_NNN_K.png`, `final_model.png` | s04_assets | – |
| `04_assets.json` | s04_assets | `Assets` |
| `05_beats.json` | s05_beats | `Beats` |
| `06_timeline.json` | s06_timeline | `Timeline` |

Image paths inside JSON are relative to the run directory. Music and SFX paths are repo-relative and must live under `assets/` so Remotion can serve them.

## Stages

Claude is called only through `pipeline/src/lego_builder/llm/client.py`, which runs the Claude Code CLI (`claude -p --output-format json --allowedTools Read`) on the owner's Claude subscription. Images are passed as file paths that Claude opens with its Read tool. See ADR 0002.

| Stage | Job | Uses Claude? | Status |
|---|---|---|---|
| s01_extract | Rasterise PDF, find and crop each numbered step and the finished-model picture | Yes (segmentation) | Implemented; boxes refined with OpenCV |
| s02_understand | New parts, visual change, milestone; model / callout boxes and landing point; OpenCV diff (scoring only) | Yes | Implemented |
| s03_select | Satisfaction score + pick N steps with pacing; optional Claude re-rank; stops at the "final" step | Optional | Heuristic implemented + tested |
| s04_assets | Transparent model per step + part cut-outs from the callout (ADR 0003) | No | Implemented + tested |
| s05_beats | Beat detection with librosa | No | Implemented; downbeats approximate |
| s06_timeline | Put steps on beats (impact on the beat, fly-in lead); hook / snaps / reveal / CTA; music offset | No | Implemented + tested |

## Video composition (Remotion)

`BuildReel` maps each timeline event to a component inside a `<Sequence>`:

| Event | Component | Effect |
|---|---|---|
| hook | `Hook` | Punch-in on the finished model |
| snap | `SnapStep` | New parts fall onto the previous model; on the beat, cut to the new model with squash, ring burst, shake, click SFX |
| reveal | `Reveal` | Finished model with a glow, set name and number |
| cta | `Cta` | Call to action card |
| (always) | `Overlays` | Step counter and progress bar |

`public/assets` and `public/runs` are symlinks created by `video/scripts/link-run.mjs`.

## Extension points

- **3D rendering:** replace s04_assets with a Blender + LDraw renderer that outputs a short clip per step; add a `clip` field to `StepAsset` and a `SnapClip` component.
- **Web UI:** `web/` can call the CLI and let a person edit `03_selection.json` before rendering.
- **Style templates:** add alternative compositions (e.g. `BuildReelNeon`) that read the same timeline.
