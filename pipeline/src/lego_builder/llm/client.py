"""Thin wrapper around the Anthropic API for vision prompts that return validated JSON."""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from lego_builder.config import get_settings

M = TypeVar("M", bound=BaseModel)
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(name: str, **kwargs: str) -> str:
    """Load prompts/<name>.md and fill {placeholders}."""
    text = (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")
    return text.format(**kwargs) if kwargs else text


def _image_block(path: Path) -> dict[str, object]:
    media = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    data = base64.standard_b64encode(path.read_bytes()).decode()
    return {"type": "image", "source": {"type": "base64", "media_type": media, "data": data}}


def _extract_json(text: str) -> str:
    match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    return match.group(1) if match else text


def ask_json(prompt: str, images: list[Path], schema: type[M], max_tokens: int = 4096) -> M:
    """Send prompt + images to Claude and parse the reply into `schema`."""
    import anthropic  # imported lazily so tests don't need the SDK configured

    settings = get_settings()
    if not settings.model:
        raise RuntimeError("Set LEGO_BUILDER_MODEL in .env")
    client = anthropic.Anthropic()
    content: list[Any] = [_image_block(p) for p in images]
    content.append({"type": "text", "text": prompt})
    reply = client.messages.create(
        model=settings.model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": content}],
    )
    text = "".join(b.text for b in reply.content if b.type == "text")
    return schema.model_validate(json.loads(_extract_json(text)))
