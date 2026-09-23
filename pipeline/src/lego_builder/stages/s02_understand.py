"""Stage 2: understand each step (new parts, visual change, milestones) and compute diff masks.

Inputs:  01_steps_raw.json, 01_steps/*.png
Outputs: 02_understanding.json (Understanding), 02_masks/mask_NNN.png
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from lego_builder.jsonio import read_model, write_model
from lego_builder.llm.client import ask_json, load_prompt
from lego_builder.models import StepsRaw, StepUnderstanding, Understanding
from lego_builder.stages.base import StageContext

MIN_MATCHES = 10


def align_image(prev_img: Path, cur_img: Path) -> Any | None:
    """Warp the current step image onto the previous step's coordinate frame (ORB + homography).

    Camera angle and scale can drift between consecutive instruction pages; without alignment
    the diff mask (and anything cropped from it) would not line up with the previous image's
    pixels. Returns None if there aren't enough good matches for a reliable homography.
    """
    import cv2
    import numpy as np

    prev = cv2.imread(str(prev_img))
    cur = cv2.imread(str(cur_img))
    orb = cv2.ORB_create(nfeatures=2000)
    kp1, des1 = orb.detectAndCompute(prev, None)
    kp2, des2 = orb.detectAndCompute(cur, None)
    if des1 is None or des2 is None or len(kp1) < MIN_MATCHES or len(kp2) < MIN_MATCHES:
        return None

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = matcher.knnMatch(des2, des1, k=2)
    good = [m for m, n in matches if m.distance < 0.75 * n.distance]
    if len(good) < MIN_MATCHES:
        return None

    src = np.float32([kp2[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([kp1[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    h_mat, inliers = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    if h_mat is None or inliers is None or int(inliers.sum()) < MIN_MATCHES:
        return None

    h, w = prev.shape[:2]
    return cv2.warpPerspective(cur, h_mat, (w, h))


def diff_mask(prev: Any, cur: Any, out: Path) -> float:
    """Write a mask of pixels changed between two same-sized images; return the changed fraction."""
    import cv2
    import numpy as np

    diff = cv2.cvtColor(cv2.absdiff(prev, cur), cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(diff, 40, 255, cv2.THRESH_BINARY)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cv2.imwrite(str(out), mask)
    return float((mask > 0).mean())


def run(ctx: StageContext) -> None:
    import cv2

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
            prev_path = paths.root / prev.image
            aligned = align_image(prev_path, cur_img)
            if aligned is None:
                prev_arr = cv2.imread(str(prev_path))
                cur_arr = cv2.imread(str(cur_img))
                aligned = cv2.resize(cur_arr, (prev_arr.shape[1], prev_arr.shape[0]))
            else:
                aligned_path = paths.masks_dir / f"aligned_{cur.step_number:03d}.png"
                cv2.imwrite(str(aligned_path), aligned)
                u.aligned_image = str(aligned_path.relative_to(paths.root))

            mask = paths.masks_dir / f"mask_{cur.step_number:03d}.png"
            u.diff_area = diff_mask(cv2.imread(str(prev_path)), aligned, mask)
            u.diff_mask = str(mask.relative_to(paths.root))
        results.append(u)

    write_model(paths.understanding, Understanding(steps=results))
