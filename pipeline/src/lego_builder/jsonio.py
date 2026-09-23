"""Read/write Pydantic models as JSON files."""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

M = TypeVar("M", bound=BaseModel)


def write_model(path: Path, model: BaseModel) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(model.model_dump_json(indent=2), encoding="utf-8")


def read_model(path: Path, cls: type[M]) -> M:
    if not path.exists():
        raise FileNotFoundError(f"{path} not found — did the previous stage run?")
    return cls.model_validate_json(path.read_text(encoding="utf-8"))
