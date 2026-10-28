"""Image helpers shared by stages: find drawings on a flat background and cut them out.

Instruction pages are flat-coloured illustrations, so "background" is simply the most common
colour along an image's edge (or inside a callout box), and anything clearly different from it is
a drawing.
"""

from __future__ import annotations

from typing import Any

from lego_builder.models import BBox

BG_TOLERANCE = 25  # max channel difference still counted as background
GROUP_PX = 9  # drawings closer than this are treated as one piece
MIN_OVERLAP = 0.3  # a piece joins a box only if this share of it is already inside
PAD_PX = 8
MIN_PIECE = 0.02  # specks smaller than this share of the biggest piece are dropped
MIN_PART = 0.15  # callout pieces smaller than this share of the biggest are count labels ("2x")


def background(img: Any, edge_only: bool = True) -> Any:
    """Most common colour along the image edge (or in the whole image)."""
    import numpy as np

    if edge_only:
        px = np.concatenate([img[0], img[-1], img[:, 0], img[:, -1]]).reshape(-1, 3)
    else:
        px = img.reshape(-1, 3)
    colours, counts = np.unique(px, axis=0, return_counts=True)
    return colours[counts.argmax()].astype(int)


def foreground(img: Any, bg: Any) -> Any:
    """1 where the pixel clearly differs from `bg`, else 0."""
    import numpy as np

    return (np.abs(img.astype(int) - bg).max(axis=2) > BG_TOLERANCE).astype(np.uint8)


def _footer_top(fg: Any) -> int:
    """Top row of the page footer (a long horizontal rule near the bottom), else the height."""
    import cv2
    import numpy as np

    h, w = fg.shape
    start = h - h // 6
    lines = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((1, w // 3), np.uint8))
    rows = np.nonzero(lines[start:].any(axis=1))[0]
    return int(start + rows[0]) - PAD_PX if len(rows) else h


def expand_to_content(img: Any, bbox: BBox, clip_footer: bool = True) -> BBox:
    """Grow `bbox` to cover every drawing it mostly contains, optionally stopping above a footer."""
    import cv2
    import numpy as np

    h, w = img.shape[:2]
    fg = foreground(img, background(img))
    bottom = min(_footer_top(fg), h) if clip_footer else h
    fg[bottom:] = 0
    grouped = cv2.dilate(fg, np.ones((GROUP_PX, GROUP_PX), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(grouped)

    x0, y0 = max(bbox.x, 0), max(bbox.y, 0)
    x1, y1 = min(bbox.x + bbox.w, w), min(bbox.y + bbox.h, bottom)
    inside = labels[y0:y1, x0:x1]
    for i in range(1, n):
        share = float((inside == i).sum()) / float(stats[i, cv2.CC_STAT_AREA])
        if share >= MIN_OVERLAP:
            cx, cy, cw, ch = stats[i, :4]
            x0, y0 = min(x0, int(cx)), min(y0, int(cy))
            x1, y1 = max(x1, int(cx + cw)), max(y1, int(cy + ch))

    x0, y0 = max(x0 - PAD_PX, 0), max(y0 - PAD_PX, 0)
    x1, y1 = min(x1 + PAD_PX, w), min(y1 + PAD_PX, bottom)
    return BBox(x=x0, y=y0, w=x1 - x0, h=y1 - y0)


def transparent_background(img: Any, largest_only: bool = False) -> Any:
    """BGRA copy of `img` where background regions connected to the edge are transparent.

    Background-coloured gaps fully enclosed by the drawing stay opaque, so light parts are safe.
    """
    import cv2
    import numpy as np

    fg = foreground(img, background(img))
    _, labels = cv2.connectedComponents((1 - fg).astype(np.uint8), connectivity=4)
    edge = np.unique(
        np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]])
    )
    alpha = np.where(np.isin(labels, edge) & (fg == 0), 0, 255).astype(np.uint8)

    n, pieces, stats, _ = cv2.connectedComponentsWithStats((alpha > 0).astype(np.uint8))
    if n > 1:
        areas = stats[1:, cv2.CC_STAT_AREA]
        if largest_only:
            keep = [int(areas.argmax()) + 1]
        else:
            keep = [i + 1 for i, a in enumerate(areas) if a >= MIN_PIECE * areas.max()]
        alpha[~np.isin(pieces, keep)] = 0

    rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = alpha
    return rgba


def trim(rgba: Any) -> tuple[Any, int, int] | None:
    """Crop to the opaque pixels; return (image, x offset, y offset), or None if empty."""
    import numpy as np

    ys, xs = np.nonzero(rgba[:, :, 3])
    if len(xs) == 0:
        return None
    x0, y0 = int(xs.min()), int(ys.min())
    return rgba[y0 : int(ys.max()) + 1, x0 : int(xs.max()) + 1], x0, y0


def cut_model(img: Any, box: BBox | None) -> tuple[Any, int, int] | None:
    """Cut the model inside `box` (or the biggest drawing in `img`) with a transparent background.

    Returns (BGRA image, x, y) where x, y is the cut-out's top-left corner in `img`.
    """
    if box is None:
        return trim(transparent_background(img, largest_only=True))
    box = expand_to_content(img, box, clip_footer=False)
    found = trim(
        transparent_background(img[box.y : box.y + box.h, box.x : box.x + box.w])
    )
    if found is None:
        return None
    rgba, dx, dy = found
    return rgba, box.x + dx, box.y + dy


def cut_parts(img: Any, box: BBox) -> list[Any]:
    """Cut each part out of a parts callout box, left to right, dropping the count labels."""
    import cv2
    import numpy as np

    box = expand_to_content(img, box, clip_footer=False)
    inner = img[box.y : box.y + box.h, box.x : box.x + box.w]
    fg = foreground(inner, background(inner, edge_only=False))
    grouped = cv2.dilate(fg, np.ones((7, 7), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(grouped)
    h, w = labels.shape
    edge = set(
        np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]).tolist()
    )
    pieces = [i for i in range(1, n) if i not in edge]
    if not pieces:
        return []
    biggest = max(int(stats[i, cv2.CC_STAT_AREA]) for i in pieces)

    parts: list[Any] = []
    for i in sorted(pieces, key=lambda i: int(stats[i, cv2.CC_STAT_LEFT])):
        if stats[i, cv2.CC_STAT_AREA] < MIN_PART * biggest:
            continue
        x, y, pw, ph = (int(v) for v in stats[i, :4])
        x0, y0 = max(x - 2, 0), max(y - 2, 0)
        crop = inner[y0 : min(y + ph + 2, h), x0 : min(x + pw + 2, w)]
        found = trim(transparent_background(crop, largest_only=True))
        if found is not None:
            parts.append(found[0])
    return parts
