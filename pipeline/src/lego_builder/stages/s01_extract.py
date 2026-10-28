"""Stage 1: rasterise the PDF and crop each build step into its own image.

Inputs:  ctx.pdf
Outputs: 01_pages/page_NNN.png, 01_steps/step_NNN.png, 01_steps/final.png, 01_steps_raw.json

Claude gives a rough box per step; `imaging.expand_to_content` then grows it to cover every
drawing it touches (Claude's pixel boxes tend to be too tight), stopping above the page footer.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from lego_builder.config import get_settings
from lego_builder.imaging import expand_to_content
from lego_builder.jsonio import write_model
from lego_builder.llm.client import ask_json, load_prompt
from lego_builder.models import BBox, RawStep, StepsRaw
from lego_builder.stages.base import StageContext


class _Item(BaseModel):
    step_number: int
    bbox: BBox


class _Final(BaseModel):
    bbox: BBox


class _PageSteps(BaseModel):
    steps: list[_Item]
    final_model: _Final | None = None


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
    finals: list[tuple[int, Path, BBox]] = []
    for page_no, page_img in enumerate(pages, start=1):
        img = cv2.imread(str(page_img))
        if img is None:
            raise RuntimeError(f"Could not read rendered page {page_img}")
        h, w = img.shape[:2]
        found = ask_json(
            load_prompt("segment_page", width=str(w), height=str(h)),
            [page_img],
            _PageSteps,
        )
        seen = max((s.step_number for s in steps), default=0)
        for item in found.steps:
            # Numbers that go back are sub-steps inside a step panel (e.g. 1-5 of a sub-build).
            if item.step_number <= seen:
                print(f"s01: page {page_no}: skipped step {item.step_number} (after step {seen})")
                continue
            bbox = expand_to_content(img, item.bbox)
            out = paths.steps_dir / f"step_{item.step_number:03d}.png"
            crop(page_img, bbox, out)
            steps.append(
                RawStep(
                    step_number=item.step_number,
                    page=page_no,
                    bbox=bbox,
                    image=str(out.relative_to(paths.root)),
                )
            )
        if found.final_model and not found.steps:
            finals.append((page_no, page_img, found.final_model.bbox))

    # The finished model follows the last step; later "models" are usually ads for other sets.
    last_step_page = max((s.page for s in steps), default=0)
    after = [f for f in finals if f[0] > last_step_page]
    chosen = after[0] if after else (finals[-1] if finals else None)
    final_image: str | None = None
    if chosen is not None:
        page_no, page_img, bbox = chosen
        out = paths.steps_dir / "final.png"
        crop(page_img, expand_to_content(cv2.imread(str(page_img)), bbox), out)
        final_image = str(out.relative_to(paths.root))
        print(f"s01: finished model from page {page_no}")

    steps.sort(key=lambda s: s.step_number)
    write_model(
        paths.steps_raw,
        StepsRaw(
            source_pdf=str(ctx.pdf),
            page_count=len(pages),
            steps=steps,
            final_image=final_image,
        ),
    )
