"""Stage 2: understand each step (new parts, visual change, milestones) and compute diff masks.

Inputs:  01_steps_raw.json, 01_steps/*.png
Outputs: 02_understanding.json (Understanding), 02_masks/mask_NNN.png
"""

from __future__ import annotations

from pathlib import Path

from lego_builder.jsonio import read_model, write_model
from lego_builder.llm.client import ask_json, load_prompt
from lego_builder.models import StepsRaw, StepUnderstanding, Understanding
from lego_builder.stages.base import StageContext


def diff_mask(prev_img: Path, img: Path, out: Path) -> float:
    """Write a binary mask of pixels that changed between two step images; return changed fraction.

    TODO: align the two images first (ORB feature matching + homography), because camera
    angle and scale can change between steps. Without alignment the mask is noisy.
    """
    import cv2
    import numpy as np

    a = cv2.imread(str(prev_img))
    b = cv2.imread(str(img))
    a = cv2.resize(a, (b.shape[1], b.shape[0]))
    diff = cv2.cvtColor(cv2.absdiff(a, b), cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(diff, 40, 255, cv2.THRESH_BINARY)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cv2.imwrite(str(out), mask)
    return float((mask > 0).mean())


def run(ctx: StageContext) -> None:
    paths = ctx.paths.ensure()
    raw = read_model(paths.steps_raw, StepsRaw)
    results: list[StepUnderstanding] = []

    for prev, cur in zip([None, *raw.steps[:-1]], raw.steps, strict=True):
        cur_img = paths.root / cur.image
        images = [cur_img] if prev is None else [paths.root / prev.image, cur_img]
        u = ask_json(
            load_prompt(
                "understand_step",
                step=str(cur.step_number),
                prev_step=str(prev.step_number if prev else "0 (empty)"),
            ),
            images,
            StepUnderstanding,
        )
        if prev is not None:
            mask = paths.masks_dir / f"mask_{cur.step_number:03d}.png"
            u.diff_area = diff_mask(paths.root / prev.image, cur_img, mask)
            u.diff_mask = str(mask.relative_to(paths.root))
        results.append(u)

    write_model(paths.understanding, Understanding(steps=results))
