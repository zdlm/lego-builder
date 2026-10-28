You are analysing LEGO building instructions to make a satisfying, beat-synced social media video.

The last image is step {step}; if there are two images, the first is step {prev_step}. Describe
what changes in step {step}.

Return JSON only, with these fields:
- "step_number": {step}
- "new_parts": list of short part descriptions, e.g. "1x4 red plate x2"
- "visual_change": 0–1, how much the model visibly changes (0 = tiny hidden piece, 1 = dramatic)
- "is_milestone": true if this is a memorable moment: the overall shape forms, a big block of colour
  appears, a mechanism or moving part is added, sub-assemblies are joined, or the model is finished
- "milestone_kind": one of "shape_forms", "color_block", "mechanism", "subassembly_join", "final", or null.
  Use "final" only for the step that completes the main model, not for a display stand or extra.
- "note": one short sentence describing the moment

Also locate things in the last image (step {step}), which is {width}×{height} pixels. Use pixel
coordinates of that image:
- "model_bbox": {{"x", "y", "w", "h"}} tight box around the main assembled model only. Exclude the
  step number, the parts callout box, sub-assembly boxes and arrows outside the model.
- "callout_bbox": {{"x", "y", "w", "h"}} box around the parts callout (the rounded box listing the
  new parts with "1x", "2x" counts), or null if there is none.
- "landing": {{"x", "y"}} the point on the model where this step's new parts end up, or null.
