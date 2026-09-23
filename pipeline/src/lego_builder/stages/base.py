"""Shared context passed to every stage."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from lego_builder.paths import RunPaths


@dataclass
class StageContext:
    run_id: str
    paths: RunPaths
    pdf: Path | None = None
    music: Path | None = None
    set_name: str = "LEGO Set"
    set_number: str | None = None
    length_s: Literal[15, 30, 60] = 30
    sfx: list[Path] = field(default_factory=list)
    use_llm_ranking: bool = True
