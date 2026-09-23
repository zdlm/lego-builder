# Data contracts

Source of truth: `pipeline/src/lego_builder/models.py` (Pydantic). TypeScript mirror for the video side: `video/src/lib/timeline.ts`. Current `SCHEMA_VERSION`: **0.2.0**.

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

**01_steps_raw.json — `StepsRaw`**: `source_pdf`, `page_count`, `steps[]` of `RawStep {step_number, page, bbox, image}`.

**02_understanding.json — `Understanding`**: `steps[]` of `StepUnderstanding {step_number, new_parts[], visual_change 0–1, is_milestone, milestone_kind, note, diff_mask, diff_area, aligned_image}`. `aligned_image` is the step's image warped onto the previous step's coordinate frame (ORB + homography in `s02_understand.align_image`); it is `None` when there's no previous step or alignment failed for lack of matches.

**03_selection.json — `Selection`**: `target_length_s` (15/30/60), `selected[]` of `SelectedStep {step_number, score, reason, role: hook|build|climax|reveal}` in playback order.

**04_assets.json — `Assets`**: `assets[]` of `StepAsset {step_number, base_image, base_width, base_height, full_image, cutout, cutout_bbox}`. `cutout_bbox` is in `base_image`'s pixel coordinate frame (via `aligned_image` when available), so the video side can position the cutout by scaling `base_width`/`base_height` to the displayed size.

**05_beats.json — `Beats`**: `music`, `tempo_bpm`, `duration_s`, `beats_s[]`, `downbeats_s[]`.

**06_timeline.json — `Timeline`**: `run_id`, `set_name`, `set_number`, `fps`, `width`, `height`, `length_s`, `music`, `total_steps`, `events[]` of `TimelineEvent {kind: hook|snap|reveal|cta, start_s, duration_s, step_number, asset, sfx, text}`.

## Changing a contract

1. Edit `models.py` and bump `SCHEMA_VERSION`.
2. Update `video/src/lib/timeline.ts` if the timeline or anything it embeds changed.
3. Update this file.
4. Run `make test lint`.
