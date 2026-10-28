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

SCHEMA_VERSION = "0.4.0"


class BBox(BaseModel):
    """Axis-aligned box in page pixel coordinates."""

    x: int
    y: int
    w: int
    h: int


class Point(BaseModel):
    x: int
    y: int


# ---------- s01_extract ----------


class RawStep(BaseModel):
    step_number: int = Field(description="Step number as printed in the instructions")
    page: int = Field(description="1-based PDF page index")
    bbox: BBox = Field(description="Where the step sits on the page image")
    image: str = Field(
        description="Path to the cropped step image, relative to the run dir"
    )


class StepsRaw(BaseModel):
    schema_version: str = SCHEMA_VERSION
    source_pdf: str
    page_count: int
    steps: list[RawStep]
    final_image: str | None = Field(
        default=None,
        description="Crop of the finished-model picture (a page without a step number), if found",
    )


# ---------- s02_understand ----------


class StepUnderstanding(BaseModel):
    step_number: int
    new_parts: list[str] = Field(
        default_factory=list, description="e.g. '1x4 red plate x2'"
    )
    visual_change: float = Field(
        ge=0, le=1, description="0 = barely visible, 1 = huge change"
    )
    is_milestone: bool = Field(
        description="Shape comes together, sub-assemblies join, etc."
    )
    milestone_kind: (
        Literal["shape_forms", "color_block", "mechanism", "subassembly_join", "final"]
        | None
    ) = None
    note: str = Field(default="", description="One-line description of what happens")
    diff_mask: str | None = Field(
        default=None, description="Path to mask of newly added region"
    )
    diff_area: float | None = Field(
        default=None, ge=0, le=1, description="Fraction of pixels"
    )
    aligned_image: str | None = Field(
        default=None,
        description=(
            "This step's image warped onto the previous step's coordinate frame (ORB + "
            "homography), so diff_mask/cutouts line up with the previous step's pixels"
        ),
    )
    model_bbox: BBox | None = Field(
        default=None, description="Assembled model in this step's image (pixels)"
    )
    callout_bbox: BBox | None = Field(
        default=None, description="Parts callout box in this step's image (pixels)"
    )
    landing: Point | None = Field(
        default=None, description="Where the new parts end up on the model (pixels)"
    )


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


class Picture(BaseModel):
    """An RGBA image with a transparent background, relative to the run dir."""

    image: str
    width: int
    height: int


class StepAsset(BaseModel):
    step_number: int
    full_image: str = Field(description="This step's full panel image (fallback)")
    model: Picture | None = Field(default=None, description="Model after this step")
    prev_model: Picture | None = Field(
        default=None, description="Model before this step"
    )
    parts: list[Picture] = Field(
        default_factory=list, description="New parts cut from the callout"
    )
    landing_x: float = Field(
        default=0.5, ge=0, le=1, description="Fraction of model width"
    )
    landing_y: float = Field(
        default=0.3, ge=0, le=1, description="Fraction of model height"
    )


class Assets(BaseModel):
    schema_version: str = SCHEMA_VERSION
    assets: list[StepAsset]
    final_model: Picture | None = Field(
        default=None, description="Finished model with a transparent background"
    )


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
    impact_s: float | None = Field(
        default=None,
        description="Snap only: when the parts land (on a beat), in video time",
    )
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
    music_start_s: float = Field(
        default=0.0,
        ge=0,
        description="Where in the track playback starts (skips beatless intros)",
    )
    total_steps: int
    final_image: str | None = Field(
        default=None,
        description="Finished-model image for the reveal, relative to the run dir",
    )
    final_model: Picture | None = Field(
        default=None, description="Finished model with a transparent background"
    )
    events: list[TimelineEvent]
