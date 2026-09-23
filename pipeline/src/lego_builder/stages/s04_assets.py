"""Stage 4: build animation assets for each selected step (base image, end image, part cutout).

Inputs:  01_steps_raw.json, 02_understanding.json, 03_selection.json
Outputs: 04_assets/cutout_NNN.png, 04_assets.json (Assets)

2D MVP: cut the newly added parts out of the step image using the diff mask, so Remotion can drop
them onto the previous step's image. 3D rendering (Blender + LDraw) would replace this stage.
"""

from __future__ import annotations

from pathlib import Path

from lego_builder.jsonio import read_model, write_model
from lego_builder.models import Assets, BBox, Selection, StepAsset, StepsRaw, Understanding
from lego_builder.stages.base import StageContext


def make_cutout(image: Path, mask: Path, out: Path) -> BBox | None:
    """Write an RGBA PNG with only the masked pixels; return the bbox of the cutout."""
    import cv2
    import numpy as np

    img = cv2.imread(str(image))
    m = cv2.imread(str(mask), cv2.IMREAD_GRAYSCALE)
    m = cv2.resize(m, (img.shape[1], img.shape[0]))
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        return None
    x, y, w, h = int(xs.min()), int(ys.min()), int(xs.ptp() + 1), int(ys.ptp() + 1)
    rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = m
    cv2.imwrite(str(out), rgba[y : y + h, x : x + w])
    return BBox(x=x, y=y, w=w, h=h)


def run(ctx: StageContext) -> None:
    import cv2

    paths = ctx.paths.ensure()
    raw = {s.step_number: s for s in read_model(paths.steps_raw, StepsRaw).steps}
    und = {u.step_number: u for u in read_model(paths.understanding, Understanding).steps}
    sel = read_model(paths.selection, Selection)
    order = sorted(raw)

    assets: list[StepAsset] = []
    for s in sel.selected:
        n = s.step_number
        idx = order.index(n)
        prev_img = raw[order[idx - 1]].image if idx > 0 else raw[n].image
        base_h, base_w = cv2.imread(str(paths.root / prev_img)).shape[:2]
        cutout, bbox = None, None
        mask = und[n].diff_mask if n in und else None
        if mask:
            # aligned_image (if present) is warped onto prev_img's frame, matching the mask and
            # keeping cutout_bbox in the same coordinate space as base_image.
            source = und[n].aligned_image or raw[n].image
            out = paths.assets_dir / f"cutout_{n:03d}.png"
            bbox = make_cutout(paths.root / source, paths.root / mask, out)
            cutout = str(out.relative_to(paths.root)) if bbox else None
        assets.append(
            StepAsset(
                step_number=n,
                base_image=prev_img,
                base_width=base_w,
                base_height=base_h,
                full_image=raw[n].image,
                cutout=cutout,
                cutout_bbox=bbox,
            )
        )
    write_model(paths.assets, Assets(assets=assets))
