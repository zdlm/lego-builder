You are analysing LEGO building instructions to make a satisfying, beat-synced social media video.

Image 1 is step {prev_step}. Image 2 is step {step}. Describe what changes in step {step}.

Return JSON only, with these fields:
- "step_number": {step}
- "new_parts": list of short part descriptions, e.g. "1x4 red plate x2"
- "visual_change": 0–1, how much the model visibly changes (0 = tiny hidden piece, 1 = dramatic)
- "is_milestone": true if this is a memorable moment: the overall shape forms, a big block of colour
  appears, a mechanism or moving part is added, sub-assemblies are joined, or the model is finished
- "milestone_kind": one of "shape_forms", "color_block", "mechanism", "subassembly_join", "final", or null
- "note": one short sentence describing the moment
