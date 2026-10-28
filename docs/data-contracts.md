# Data contracts

Source of truth: `pipeline/src/lego_builder/models.py` (Pydantic). TypeScript mirror for the video side: `video/src/lib/timeline.ts`. Current `SCHEMA_VERSION`: **0.4.0**.

To see the exact JSON Schema of any model:

```bash
pipeline/.venv/bin/python -c "from lego_builder.models import Timeline; import json; print(json.dumps(Timeline.model_json_schema(), indent=2))"
```

## Conventions

- Times are in seconds (float). Remotion converts to frames.
- Image paths are relative to the run directory; music/SFX paths are repo-relative under `assets/`.
- Step numbers are the numbers printed in the instructions, not list indexes.
- Every top-level file carries `schema_version`.

## Files

**01_steps_raw.json — `StepsRaw`**: `source_pdf`, `page_count`, `steps[]` of `RawStep {step_number, page, bbox, image}`, `final_image`. `bbox` is Claude's box grown to the drawn content and clipped above the page footer. `final_image` is a crop of the finished-model picture (a page with no step number), or `None` if the booklet has none.

**02_understanding.json — `Understanding`**: `steps[]` of `StepUnderstanding {step_number, new_parts[], visual_change 0–1, is_milestone, milestone_kind, note, diff_mask, diff_area, aligned_image, model_bbox, callout_bbox, landing}`. `aligned_image` is the step's image warped onto the previous step's coordinate frame (ORB + homography in `s02_understand.align_image`); it is `None` when there's no previous step or alignment failed for lack of matches. `model_bbox` (main model only), `callout_bbox` (parts callout) and `landing` (`Point {x, y}`, where the new parts end up) are from Claude, in pixels of the step image; any of them may be `None`. `milestone_kind: "final"` marks the step that completes the main model; later steps (e.g. a display stand) are left out by s03.

**03_selection.json — `Selection`**: `target_length_s` (15/30/60), `selected[]` of `SelectedStep {step_number, score, reason, role: hook|build|climax|reveal}` in playback order.

**04_assets.json — `Assets`**: `assets[]` of `StepAsset {step_number, full_image, model, prev_model, parts[], landing_x, landing_y}`, plus `final_model`. `model`, `prev_model`, `parts[]` and `final_model` are `Picture {image, width, height}`: PNGs with a transparent background (`04_assets/model_NNN.png`, `part_NNN_K.png`, `final_model.png`). `model` is the model after this step, `prev_model` before it; `parts` are the new parts cut from the callout, left to right; `landing_x`/`landing_y` (0–1) say where on `model` the parts land. All pictures keep the instruction drawing's pixel scale, so one display scale fits every step. See ADR 0003.

**05_beats.json — `Beats`**: `music`, `tempo_bpm`, `duration_s`, `beats_s[]`, `downbeats_s[]`.

**06_timeline.json — `Timeline`**: `run_id`, `set_name`, `set_number`, `fps`, `width`, `height`, `length_s`, `music`, `music_start_s`, `total_steps`, `final_image`, `final_model`, `events[]` of `TimelineEvent {kind: hook|snap|reveal|cta, start_s, duration_s, step_number, asset, impact_s, sfx, text}`. `music_start_s` is how far into the track playback starts (chosen so the first downbeat lands when the snaps begin); all event times are already in video time. Snap events start a little before their beat so parts can fly in; `impact_s` is the beat on which they land (play the click then). Events are contiguous. Hook and reveal show `final_model` when set, else `final_image`, else the step's own picture.

## Changing a contract

1. Edit `models.py` and bump `SCHEMA_VERSION`.
2. Update `video/src/lib/timeline.ts` if the timeline or anything it embeds changed.
3. Update this file.
4. Run `make test lint`.
