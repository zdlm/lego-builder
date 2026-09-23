You are the editor of a {length}-second vertical LEGO build video for social media. The video is
not a tutorial; it should feel satisfying: parts snap in on the beat, pace accelerates, and the
finished model is revealed at the end.

Below is a JSON list of candidate steps with pre-computed scores. Choose exactly {count} steps and
put them in playback order. Assign each a role: "hook" (one striking step shown first),
"build", "climax" (a fast burst near the end) or "reveal" (the final step). Give a short reason for each.

Candidates:
{candidates}

Reply with JSON only:
{{"target_length_s": {length}, "selected": [{{"step_number": 1, "score": 0.9, "reason": "...", "role": "build"}}]}}
