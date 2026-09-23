"""Stage 3: score every step for "satisfaction" and pick the snap moments.

Inputs:  02_understanding.json
Outputs: 03_selection.json (Selection)

The scoring is a plain function (`score_step`) so it can be unit-tested and tuned without the LLM.
An optional Claude pass re-ranks the shortlist and explains each pick.
"""

from __future__ import annotations

import json
from typing import Literal

from lego_builder.jsonio import read_model, write_model
from lego_builder.llm.client import ask_json, load_prompt
from lego_builder.models import SelectedStep, Selection, StepUnderstanding, Understanding
from lego_builder.stages.base import StageContext

Role = Literal["hook", "build", "climax", "reveal"]

# How many snap steps each video length holds (tuned by eye; s06 fits them to the beats).
TARGET_COUNTS: dict[int, int] = {15: 10, 30: 22, 60: 45}

MILESTONE_BONUS: dict[str, float] = {
    "final": 0.5,
    "subassembly_join": 0.35,
    "shape_forms": 0.3,
    "mechanism": 0.25,
    "color_block": 0.2,
}


def score_step(u: StepUnderstanding) -> float:
    """Satisfaction score in [0, 1]."""
    s = 0.6 * u.visual_change
    if u.diff_area is not None:
        s += 0.2 * min(u.diff_area * 5, 1.0)
    if u.is_milestone:
        s += MILESTONE_BONUS.get(u.milestone_kind or "", 0.2)
    return max(0.0, min(s, 1.0))


def pick(steps: list[StepUnderstanding], count: int) -> list[SelectedStep]:
    """Pick `count` steps: always the final step, the best-scoring others, kept in build order.

    Picks are spread across the build by taking the best step from each of `count` equal buckets,
    so the video shows the whole build progressing rather than clustering on one section.
    """
    if not steps:
        return []
    count = min(count, len(steps))
    ordered = sorted(steps, key=lambda u: u.step_number)
    final = ordered[-1]
    rest = ordered[:-1]
    chosen: list[StepUnderstanding] = []
    buckets = max(count - 1, 1)
    for i in range(buckets):
        lo = i * len(rest) // buckets
        hi = (i + 1) * len(rest) // buckets
        if lo < hi:
            chosen.append(max(rest[lo:hi], key=score_step))
    chosen.append(final)

    hook = max(chosen[:-1] or chosen, key=score_step)
    climax_from = int(len(chosen) * 0.75)
    out: list[SelectedStep] = [
        SelectedStep(
            step_number=hook.step_number,
            score=score_step(hook),
            reason="Most striking step",
            role="hook",
        )
    ]
    for i, u in enumerate(chosen):
        role: Role = "reveal" if u is final else ("climax" if i >= climax_from else "build")
        out.append(
            SelectedStep(step_number=u.step_number, score=score_step(u), reason=u.note, role=role)
        )
    return out


def run(ctx: StageContext) -> None:
    paths = ctx.paths.ensure()
    und = read_model(paths.understanding, Understanding)
    count = TARGET_COUNTS[ctx.length_s]
    selected = pick(und.steps, count)

    if ctx.use_llm_ranking:
        shortlist = sorted(und.steps, key=score_step, reverse=True)[: count * 2]
        candidates = json.dumps(
            [
                {
                    **u.model_dump(include={"step_number", "note", "milestone_kind"}),
                    "score": round(score_step(u), 3),
                }
                for u in shortlist
            ],
            indent=1,
        )
        selection = ask_json(
            load_prompt(
                "rank_steps", length=str(ctx.length_s), count=str(count), candidates=candidates
            ),
            [],
            Selection,
        )
    else:
        selection = Selection(target_length_s=ctx.length_s, selected=selected)

    write_model(paths.selection, selection)
