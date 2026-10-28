import numpy as np

from lego_builder.imaging import cut_model, cut_parts
from lego_builder.models import BBox

PAGE = (252, 236, 211)
CALLOUT = (240, 214, 173)


def _step_image() -> np.ndarray:
    img = np.zeros((400, 500, 3), np.uint8)
    img[:] = PAGE
    img[200:350, 250:400] = (0, 0, 0)  # model outline
    img[205:345, 255:395] = (0, 220, 255)  # model fill
    img[260:290, 300:340] = PAGE  # page-coloured gap enclosed by the model
    img[20:140, 20:300] = (60, 60, 60)  # callout border
    img[23:137, 23:297] = CALLOUT
    img[40:90, 50:110] = (180, 100, 255)  # part 1
    img[40:80, 180:260] = (120, 60, 120)  # part 2
    img[105:115, 60:75] = (0, 0, 0)  # "1x" label
    return img


def test_cut_model_makes_background_transparent_but_keeps_enclosed_gaps() -> None:
    found = cut_model(_step_image(), BBox(x=240, y=190, w=120, h=120))
    assert found is not None
    rgba, x, y = found
    assert (x, y) == (250, 200)
    assert rgba.shape[:2] == (150, 150)
    assert rgba[0, 0, 3] == 255 and rgba[75, 75, 3] == 255
    assert rgba[70, 60, 3] == 255  # enclosed gap stays opaque


def test_cut_parts_returns_each_part_left_to_right_without_labels() -> None:
    parts = cut_parts(_step_image(), BBox(x=25, y=25, w=270, h=110))
    assert [p.shape[:2] for p in parts] == [(50, 60), (40, 80)]
    assert all(p[:, :, 3].min() == 255 for p in parts)
