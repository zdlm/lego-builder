"""Tell main-model steps from sub-assembly steps; shared by s03 (selection) and s04 (assets)."""

from __future__ import annotations

from lego_builder.models import StepUnderstanding

SUB_RATIO = 0.65  # a model under this share of the largest so far is a sub-assembly


def anchor_steps(order: list[int], und: dict[int, StepUnderstanding]) -> dict[int, int | None]:
    """For each sub-assembly step, the last earlier step that showed the main model.

    A step is a sub-assembly when its model box is under SUB_RATIO of the largest box so far.
    Main-model steps (and steps with no model box) are not in the result.
    """
    largest, last_main = 0, None
    out: dict[int, int | None] = {}
    for n in order:
        u = und.get(n)
        box = u.model_bbox if u else None
        if box is None:
            continue
        area = box.w * box.h
        largest = max(largest, area)
        if area >= SUB_RATIO * largest:
            last_main = n
        else:
            out[n] = last_main
    return out
