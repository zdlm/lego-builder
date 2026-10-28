import numpy as np

from lego_builder.imaging import expand_to_content
from lego_builder.models import BBox

BG = (252, 236, 211)


def _page() -> np.ndarray:
    img = np.zeros((600, 800, 3), np.uint8)
    img[:] = BG
    img[100:450, 300:500] = (0, 200, 255)  # model drawing
    img[300:560, 650:700] = (0, 0, 0)  # unrelated drawing elsewhere on the page
    img[540:552, 0:800] = (150, 80, 0)  # footer progress bar
    img[520:560, 20:50] = (0, 0, 0)  # page number
    return img


def test_expands_tight_box_to_whole_drawing() -> None:
    out = expand_to_content(_page(), BBox(x=280, y=80, w=150, h=300))
    assert out.x <= 300 and out.y <= 100
    assert out.x + out.w >= 500 and out.y + out.h >= 450


def test_stops_above_footer_and_ignores_unrelated_drawings() -> None:
    out = expand_to_content(_page(), BBox(x=280, y=80, w=150, h=500))
    assert out.y + out.h <= 540
    assert out.x + out.w < 650
