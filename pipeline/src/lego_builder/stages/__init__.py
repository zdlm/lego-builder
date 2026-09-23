"""Pipeline stages. Each module exposes `run(ctx: StageContext) -> None`.

Stages talk to each other only through files in the run directory (see lego_builder.models).
"""

from __future__ import annotations

from collections.abc import Callable

from lego_builder.stages import (
    s01_extract,
    s02_understand,
    s03_select,
    s04_assets,
    s05_beats,
    s06_timeline,
)
from lego_builder.stages.base import StageContext

STAGES: dict[str, Callable[[StageContext], None]] = {
    "s01_extract": s01_extract.run,
    "s02_understand": s02_understand.run,
    "s03_select": s03_select.run,
    "s04_assets": s04_assets.run,
    "s05_beats": s05_beats.run,
    "s06_timeline": s06_timeline.run,
}

__all__ = ["STAGES", "StageContext"]
