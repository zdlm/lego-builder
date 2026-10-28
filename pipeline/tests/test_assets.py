from pathlib import Path

import cv2
import numpy as np

from lego_builder.jsonio import read_model, write_model
from lego_builder.models import (
    Assets,
    BBox,
    Point,
    RawStep,
    SelectedStep,
    Selection,
    StepsRaw,
    StepUnderstanding,
    Understanding,
)
from lego_builder.paths import run_paths
from lego_builder.stages import s04_assets
from lego_builder.stages.base import StageContext

PAGE = (252, 236, 211)


def _step(path: Path, with_callout: bool) -> None:
    img = np.zeros((400, 500, 3), np.uint8)
    img[:] = PAGE
    img[200:350, 250:400] = (0, 0, 0)
    img[205:345, 255:395] = (0, 220, 255)
    if with_callout:
        img[20:140, 20:300] = (60, 60, 60)
        img[23:137, 23:297] = (240, 214, 173)
        img[40:90, 50:110] = (180, 100, 255)
        img[40:80, 180:260] = (120, 60, 120)
    cv2.imwrite(str(path), img)


def test_s04_handles_first_step_missing_callout_unknown_step_and_no_final(tmp_path: Path) -> None:
    paths = run_paths(tmp_path, "r").ensure()
    for n, callout in ((1, True), (2, False)):
        _step(paths.steps_dir / f"step_{n:03d}.png", callout)
    write_model(
        paths.steps_raw,
        StepsRaw(
            source_pdf="x.pdf",
            page_count=2,
            steps=[
                RawStep(
                    step_number=n,
                    page=n,
                    bbox=BBox(x=0, y=0, w=500, h=400),
                    image=f"01_steps/step_{n:03d}.png",
                )
                for n in (1, 2)
            ],
        ),
    )
    write_model(
        paths.understanding,
        Understanding(
            steps=[
                StepUnderstanding(
                    step_number=1,
                    visual_change=0.5,
                    is_milestone=False,
                    model_bbox=BBox(x=240, y=190, w=120, h=120),
                    callout_bbox=BBox(x=25, y=25, w=270, h=110),
                    landing=Point(x=325, y=230),
                ),
                StepUnderstanding(step_number=2, visual_change=0.5, is_milestone=False),
            ]
        ),
    )
    write_model(
        paths.selection,
        Selection(
            target_length_s=15,
            selected=[
                SelectedStep(step_number=n, score=0.5, reason="", role="build") for n in (1, 2, 99)
            ],
        ),
    )

    s04_assets.run(StageContext(run_id="r", paths=paths))

    out = read_model(paths.assets, Assets)
    by_step = {a.step_number: a for a in out.assets}
    assert set(by_step) == {1, 2}
    first, second = by_step[1], by_step[2]
    assert first.prev_model is None and first.model is not None
    assert len(first.parts) == 2
    assert abs(first.landing_x - 0.5) < 0.05 and abs(first.landing_y - 0.2) < 0.05
    assert second.model is not None and second.parts == []
    assert second.prev_model == first.model
    assert out.final_model is None
