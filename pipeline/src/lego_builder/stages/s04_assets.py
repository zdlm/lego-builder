"""Stage 4: build 2D animation assets for each selected step.

Inputs:  01_steps_raw.json, 02_understanding.json, 03_selection.json
Outputs: 04_assets/model_NNN.png, 04_assets/part_NNN_K.png, 04_assets/final_model.png,
         04_assets.json (Assets)

Every instruction step is a fresh 3D render, so diffing consecutive pictures gives messy cut-outs.
Instead we use the clean pieces the instructions already contain: the assembled model of each step
and each new part drawn in the step's parts callout, both with the background made transparent.
Remotion flies the parts onto the previous model and cuts to the new model on the beat.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from lego_builder.imaging import cut_model, cut_parts
from lego_builder.jsonio import read_model, write_model
from lego_builder.models import (
    Assets,
    Picture,
    Selection,
    StepAsset,
    StepsRaw,
    StepUnderstanding,
    Understanding,
)
from lego_builder.stages.base import StageContext


def _save(rgba: Any, out: Path, root: Path) -> Picture:
    import cv2

    cv2.imwrite(str(out), rgba)
    h, w = rgba.shape[:2]
    return Picture(image=str(out.relative_to(root)), width=w, height=h)


def _read(path: Path) -> Any:
    import cv2

    img = cv2.imread(str(path))
    if img is None:
        raise RuntimeError(f"Could not read {path}")
    return img


def landing_fraction(
    u: StepUnderstanding, x: int, y: int, w: int, h: int
) -> tuple[float, float]:
    """Landing point as a fraction of the cut-out model's size (top centre if unknown)."""
    if u.landing is None:
        return 0.5, 0.3
    fx = (u.landing.x - x) / max(w, 1)
    fy = (u.landing.y - y) / max(h, 1)
    return min(max(fx, 0.0), 1.0), min(max(fy, 0.0), 1.0)


def run(ctx: StageContext) -> None:
    paths = ctx.paths.ensure()
    raw_all = read_model(paths.steps_raw, StepsRaw)
    raw = {s.step_number: s for s in raw_all.steps}
    und = {
        u.step_number: u for u in read_model(paths.understanding, Understanding).steps
    }
    sel = read_model(paths.selection, Selection)
    order = sorted(raw)

    models: dict[int, tuple[Picture, int, int] | None] = {}

    def model_of(n: int) -> tuple[Picture, int, int] | None:
        """Model cut-out of step n plus its top-left corner in the step image (cached)."""
        if n not in models:
            u = und.get(n)
            found = cut_model(
                _read(paths.root / raw[n].image), u.model_bbox if u else None
            )
            models[n] = None
            if found is not None:
                rgba, x, y = found
                pic = _save(rgba, paths.assets_dir / f"model_{n:03d}.png", paths.root)
                models[n] = (pic, x, y)
        return models[n]

    assets: list[StepAsset] = []
    for s in sel.selected:
        n = s.step_number
        idx = order.index(n)
        model = model_of(n)
        prev = model_of(order[idx - 1]) if idx > 0 else None
        u = und.get(n)

        parts: list[Picture] = []
        if u is not None and u.callout_bbox is not None:
            img = _read(paths.root / raw[n].image)
            for k, rgba in enumerate(cut_parts(img, u.callout_bbox)):
                parts.append(
                    _save(rgba, paths.assets_dir / f"part_{n:03d}_{k}.png", paths.root)
                )

        lx, ly = 0.5, 0.3
        if model is not None and u is not None:
            pic, x, y = model
            lx, ly = landing_fraction(u, x, y, pic.width, pic.height)

        assets.append(
            StepAsset(
                step_number=n,
                full_image=raw[n].image,
                model=model[0] if model else None,
                prev_model=prev[0] if prev else None,
                parts=parts,
                landing_x=lx,
                landing_y=ly,
            )
        )

    final_model: Picture | None = None
    if raw_all.final_image:
        found = cut_model(_read(paths.root / raw_all.final_image), None)
        if found is not None:
            final_model = _save(
                found[0], paths.assets_dir / "final_model.png", paths.root
            )

    write_model(paths.assets, Assets(assets=assets, final_model=final_model))
