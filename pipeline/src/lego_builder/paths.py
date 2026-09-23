"""Run-directory layout. Every stage uses these helpers so paths stay consistent."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunPaths:
    root: Path

    @property
    def pages_dir(self) -> Path:
        return self.root / "01_pages"

    @property
    def steps_dir(self) -> Path:
        return self.root / "01_steps"

    @property
    def steps_raw(self) -> Path:
        return self.root / "01_steps_raw.json"

    @property
    def masks_dir(self) -> Path:
        return self.root / "02_masks"

    @property
    def understanding(self) -> Path:
        return self.root / "02_understanding.json"

    @property
    def selection(self) -> Path:
        return self.root / "03_selection.json"

    @property
    def assets_dir(self) -> Path:
        return self.root / "04_assets"

    @property
    def assets(self) -> Path:
        return self.root / "04_assets.json"

    @property
    def beats(self) -> Path:
        return self.root / "05_beats.json"

    @property
    def timeline(self) -> Path:
        return self.root / "06_timeline.json"

    def ensure(self) -> RunPaths:
        for d in (self.root, self.pages_dir, self.steps_dir, self.masks_dir, self.assets_dir):
            d.mkdir(parents=True, exist_ok=True)
        return self


def run_paths(data_dir: Path, run_id: str) -> RunPaths:
    return RunPaths(data_dir / "runs" / run_id)
