"""The TypeScript mirror in video/src/lib/timeline.ts must match models.py field for field."""

import re
from pathlib import Path

from pydantic import BaseModel

from lego_builder import models

TS = Path(__file__).resolve().parents[2] / "video" / "src" / "lib" / "timeline.ts"
MIRRORED: list[type[BaseModel]] = [
    models.BBox,
    models.Picture,
    models.StepAsset,
    models.TimelineEvent,
    models.Timeline,
]


def _ts_fields(source: str, name: str) -> set[str]:
    match = re.search(rf"export type {name} = \{{(.*?)\}};", source, re.DOTALL)
    assert match, f"type {name} not found in {TS.name}"
    body = re.sub(r"//[^\n]*", "", match.group(1))
    return set(re.findall(r"(\w+)\s*:", body))


def test_ts_types_mirror_pydantic_models() -> None:
    source = TS.read_text(encoding="utf-8")
    for model in MIRRORED:
        assert _ts_fields(source, model.__name__) == set(model.model_fields), model.__name__


def test_schema_version_matches() -> None:
    source = TS.read_text(encoding="utf-8")
    assert f'SCHEMA_VERSION = "{models.SCHEMA_VERSION}"' in source
