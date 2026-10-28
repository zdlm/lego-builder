"""Call Claude through the local Claude Code CLI (`claude -p`), using your Claude subscription.

No Anthropic API key is used. The CLI must be installed and logged in with your Claude account
(run `claude` once and sign in). ANTHROPIC_API_KEY is removed from the child environment so the
CLI can never fall back to pay-per-use API billing.

Images are passed as file paths; Claude Code opens them with its read-only Read tool.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from lego_builder.config import get_settings

M = TypeVar("M", bound=BaseModel)
PROMPTS_DIR = Path(__file__).parent / "prompts"


class ClaudeCLIError(RuntimeError):
    pass


def load_prompt(name: str, **kwargs: str) -> str:
    """Load prompts/<name>.md and fill {placeholders}."""
    text = (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")
    return text.format(**kwargs) if kwargs else text


def _extract_json(text: str) -> str:
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        return fenced.group(1)
    start, end = text.find("{"), text.rfind("}")
    return text[start : end + 1] if start != -1 and end > start else text


def _build_prompt(prompt: str, images: list[Path]) -> str:
    if not images:
        return prompt
    listing = "\n".join(f"Image {i}: {p.resolve()}" for i, p in enumerate(images, start=1))
    return (
        "Open each of these image files with the Read tool and look at them carefully:\n"
        f"{listing}\n\n{prompt}\n\nYour final message must be the JSON only."
    )


def _run_cli(prompt: str, images: list[Path]) -> str:
    settings = get_settings()
    binary = shutil.which(settings.claude_bin)
    if binary is None:
        raise ClaudeCLIError(
            f"'{settings.claude_bin}' not found. Install Claude Code and log in with your "
            "Claude subscription (see README)."
        )
    cmd = [binary, "-p", "--output-format", "json", "--allowedTools", "Read"]
    if settings.model:
        cmd += ["--model", settings.model]
    for d in sorted({str(p.resolve().parent) for p in images}):
        cmd += ["--add-dir", d]

    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    proc = subprocess.run(
        cmd,
        input=_build_prompt(prompt, images),
        capture_output=True,
        text=True,
        env=env,
        timeout=settings.claude_timeout_s,
    )
    if proc.returncode != 0:
        raise ClaudeCLIError(f"claude exited {proc.returncode}: {proc.stderr.strip()[:500]}")
    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise ClaudeCLIError(f"Unexpected CLI output: {proc.stdout[:500]}") from e
    if envelope.get("is_error"):
        raise ClaudeCLIError(f"Claude reported an error: {envelope.get('result')}")
    return str(envelope.get("result", ""))


def _cache_path(prompt: str, images: list[Path]) -> Path | None:
    """Where a validated reply for exactly this prompt, these image bytes and model is stored."""
    settings = get_settings()
    if not settings.claude_cache:
        return None
    h = hashlib.sha256(f"{settings.model}|{prompt}".encode())
    for p in images:
        h.update(hashlib.sha256(p.read_bytes()).digest())
    return settings.data_dir / "cache" / "claude" / f"{h.hexdigest()}.txt"


def ask_json(prompt: str, images: list[Path], schema: type[M], retries: int = 1) -> M:
    """Send prompt + images to Claude (via the CLI) and parse the reply into `schema`.

    Retries once with the validation error appended if the reply isn't valid JSON for the schema.
    Valid replies are cached (see `_cache_path`), so re-running a stage on unchanged inputs makes
    no Claude calls. Set LEGO_BUILDER_CLAUDE_CACHE=false to always ask again.
    """
    last_error: Exception | None = None
    attempt_prompt = prompt
    for _ in range(retries + 1):
        cache = _cache_path(attempt_prompt, images)
        cached = cache is not None and cache.exists()
        text = cache.read_text(encoding="utf-8") if cache and cached else ""
        if not cached:
            text = _run_cli(attempt_prompt, images)
        try:
            reply = schema.model_validate(json.loads(_extract_json(text)))
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            attempt_prompt = (
                f"{prompt}\n\nYour previous reply was not valid for the required JSON shape:\n"
                f"{e}\nReply again with corrected JSON only."
            )
            continue
        if cache is not None and not cached:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(text, encoding="utf-8")
        return reply
    raise ClaudeCLIError(f"Could not get valid JSON from Claude: {last_error}")
