"""Data contracts shared by all pipeline stages and the Remotion video app.

This module is the SOURCE OF TRUTH for every JSON file in a run directory.
If you change anything here:
  1. bump SCHEMA_VERSION,
  2. update docs/data-contracts.md,
  3. update the mirrored types in video/src/lib/timeline.ts.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SCHEMA_VERSION = "0.1.0"


class BBox(BaseModel):
    """Axis-aligned box in page pixel coordinates."""

    x: int
    y: int
    w: int
    h: int


# ---------- s01_extract ----------


class RawStep(BaseModel):
    step_number: int = Field(description="Step number as printed in the instructions")
    page: int = Field(description="1-based PDF page index")
    bbox: BBox = Field(description="Where the step sits on the page image")
    image: str = Field(description="Path to the cropped step image, relative to the run dir")


class StepsRaw(BaseModel):
    schema_version: str = SCHEMA_VERSION
    source_pdf: str
    page_count: int
    steps: list[RawStep]


# ---------- s02_understand ----------


class StepUnderstanding(BaseModel):
    step_number: int
    new_parts: list[str] = Field(default_factory=list, description="e.g. '1x4 red plate x2'")
    visual_change: float = Field(ge=0, le=1, description="0 = barely visible, 1 = huge change")
    is_milestone: bool = Field(description="Shape comes together, sub-assemblies join, etc.")
    milestone_kind: (
        Literal["shape_forms", "color_block", "mechanism", "subassembly_join", "final"] | None
    ) = None
    note: str = Field(default="", description="One-line description of what happens")
    diff_mask: str | None = Field(default=None, description="Path to mask of newly added region")
    diff_area: float | None = Field(default=None, ge=0, le=1, description="Fraction of pixels")


class Understanding(BaseModel):
    schema_version: str = SCHEMA_VERSION
    steps: list[StepUnderstanding]


# ---------- s03_select ----------


class SelectedStep(BaseModel):
    step_number: int
    score: float = Field(ge=0, le=1, description="Satisfaction score")
    reason: str
    role: Literal["hook", "build", "climax", "reveal"] = "build"


class Selection(BaseModel):
    schema_version: str = SCHEMA_VERSION
    target_length_s: Literal[15, 30, 60]
    selected: list[SelectedStep] = Field(description="In playback order")


# ---------- s04_assets ----------


class StepAsset(BaseModel):
    step_number: int
    base_image: str = Field(description="Previous-step image the part drops onto")
    full_image: str = Field(description="This step's full image (end state)")
    cutout: str | None = Field(default=None, description="RGBA cutout of the new parts")
    cutout_bbox: BBox | None = None


class Assets(BaseModel):
    schema_version: str = SCHEMA_VERSION
    assets: list[StepAsset]


# ---------- s05_beats ----------


class Beats(BaseModel):
    schema_version: str = SCHEMA_VERSION
    music: str
    tempo_bpm: float
    duration_s: float
    beats_s: list[float] = Field(description="Beat times in seconds")
    downbeats_s: list[float] = Field(default_factory=list)


# ---------- s06_timeline (handed to Remotion) ----------


class TimelineEvent(BaseModel):
    kind: Literal["hook", "snap", "reveal", "cta"]
    start_s: float
    duration_s: float
    step_number: int | None = None
    asset: StepAsset | None = None
    sfx: str | None = Field(default=None, description="Path of the click sound to play")
    text: str | None = None


class Timeline(BaseModel):
    schema_version: str = SCHEMA_VERSION
    run_id: str
    set_name: str
    set_number: str | None = None
    fps: int = 30
    width: int = 1080
    height: int = 1920
    length_s: Literal[15, 30, 60]
    music: str
    total_steps: int
    events: list[TimelineEvent]
