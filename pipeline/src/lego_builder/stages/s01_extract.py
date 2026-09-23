"""Stage 1: rasterise the PDF and crop each build step into its own image.

Inputs:  ctx.pdf
Outputs: 01_pages/page_NNN.png, 01_steps/step_NNN.png, 01_steps_raw.json (StepsRaw)
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from lego_builder.config import get_settings
from lego_builder.jsonio import write_model
from lego_builder.llm.client import ask_json, load_prompt
from lego_builder.models import BBox, RawStep, StepsRaw
from lego_builder.stages.base import StageContext


class _PageSteps(BaseModel):
    class _Item(BaseModel):
        step_number: int
        bbox: BBox

    steps: list[_Item]


def render_pages(pdf: Path, out_dir: Path, dpi: int) -> list[Path]:
    import fitz  # PyMuPDF

    out: list[Path] = []
    with fitz.open(pdf) as doc:
        for i, page in enumerate(doc, start=1):
            path = out_dir / f"page_{i:03d}.png"
            page.get_pixmap(dpi=dpi).save(path)
            out.append(path)
    return out


def crop(image: Path, bbox: BBox, out: Path) -> None:
    import cv2

    img = cv2.imread(str(image))
    cv2.imwrite(str(out), img[bbox.y : bbox.y + bbox.h, bbox.x : bbox.x + bbox.w])


def run(ctx: StageContext) -> None:
    if ctx.pdf is None:
        raise ValueError("s01_extract needs --pdf")
    settings = get_settings()
    paths = ctx.paths.ensure()
    pages = render_pages(ctx.pdf, paths.pages_dir, settings.pdf_dpi)

    import cv2

    steps: list[RawStep] = []
    for page_no, page_img in enumerate(pages, start=1):
        h, w = cv2.imread(str(page_img)).shape[:2]
        found = ask_json(
            load_prompt("segment_page", width=str(w), height=str(h)), [page_img], _PageSteps
        )
        for item in found.steps:
            out = paths.steps_dir / f"step_{item.step_number:03d}.png"
            crop(page_img, item.bbox, out)
            steps.append(
                RawStep(
                    step_number=item.step_number,
                    page=page_no,
                    bbox=item.bbox,
                    image=str(out.relative_to(paths.root)),
                )
            )

    steps.sort(key=lambda s: s.step_number)
    write_model(
        paths.steps_raw, StepsRaw(source_pdf=str(ctx.pdf), page_count=len(pages), steps=steps)
    )
