# 0003 — 2D build animation from clean instruction pieces, not pixel diffs

Date: 2026-10-28 · Status: accepted

## Context

The first 2D animation cut "new parts" out of each step by diffing it against the previous step (ORB + homography alignment, then a pixel diff). On the demo set (40858) the cut-outs were mostly background noise: every instruction step is a fresh 3D render whose angle, scale and occlusion change, the model is sometimes flipped, and callouts and step numbers disturb the alignment. Tuning thresholds cannot fix that. A true 3D pipeline (official model data or a hand-built BrickLink Studio file rendered in Blender) is the long-term answer but is out of scope for now.

## Decision

- Stop cutting parts out of diffs. Use the pieces the instructions already draw cleanly:
  - the assembled model of each step, with the page background made transparent (flood fill from the edge, so enclosed gaps stay opaque);
  - each new part from the step's parts callout, on its own.
- s02's Claude call also returns, per step: the model box, the callout box and the point where the new parts land. OpenCV refines the boxes to the drawn content (`lego_builder/imaging.py`).
- In the video, the new parts fall onto the previous model and, exactly on the beat (`impact_s`), the picture cuts to the new model with a squash, ring burst, shake and click. All models share one display scale and stand on one baseline, so the model grows in place instead of jumping.
- s06 starts each snap shortly before its beat, spends spare beats on early build steps (slow start, faster finish) and makes the step that completes the model the last click. s03 ignores steps after the "final" one (e.g. a display stand).
- Diff masks stay in s02 only as a scoring signal (`diff_area`).

## Consequences

- Clean, consistent pictures with no per-pixel registration; works for any booklet with a flat background and parts callouts.
- The cut between steps is still a cut: viewing-angle changes (e.g. the model flipped) show as a jump. Landing points are approximate.
- Re-running s02 is needed to get boxes and landing points (one Claude call per step, as before).
- When 3D data becomes available, it replaces s04 and `SnapStep` behind the same timeline (see `docs/architecture.md`, task 9).
