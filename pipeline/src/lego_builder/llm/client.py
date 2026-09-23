"""Call Claude through the local Claude Code CLI (`claude -p`), using your Claude subscription.

No Anthropic API key is used. The CLI must be installed and logged in with your Claude account
(run `claude` once and sign in). ANTHROPIC_API_KEY is removed from the child environment so the
CLI can never fall back to pay-per-use API billing.

Images are passed as file paths; Claude Code opens them with its read-only Read tool.
"""

from __future__ import annotations

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


def ask_json(prompt: str, images: list[Path], schema: type[M], retries: int = 1) -> M:
    """Send prompt + images to Claude (via the CLI) and parse the reply into `schema`.

    Retries once with the validation error appended if the reply isn't valid JSON for the schema.
    """
    last_error: Exception | None = None
    attempt_prompt = prompt
    for _ in range(retries + 1):
        text = _run_cli(attempt_prompt, images)
        try:
            return schema.model_validate(json.loads(_extract_json(text)))
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            attempt_prompt = (
                f"{prompt}\n\nYour previous reply was not valid for the required JSON shape:\n"
                f"{e}\nReply again with corrected JSON only."
            )
    raise ClaudeCLIError(f"Could not get valid JSON from Claude: {last_error}")
