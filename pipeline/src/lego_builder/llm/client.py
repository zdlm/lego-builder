"""Call the LLM through a locally signed-in agent CLI, on the user's own subscription (no API keys).

Default backend: GitHub Copilot CLI (`copilot -p`), signed in with the user's GitHub account that
has a Copilot plan (run `copilot` once and `/login`, or set COPILOT_GITHUB_TOKEN / GH_TOKEN).
Images are sent as `--attachment`s, so the chosen model must support vision.

Optional backend: Claude Code CLI (`claude -p`) on a Claude subscription, selected with
LEGO_BUILDER_LLM=claude. ANTHROPIC_API_KEY is removed from its environment so it can never fall
back to pay-per-use API billing.

Either way, stages only call `ask_json`, which validates the reply against a Pydantic model.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from lego_builder.config import get_settings

M = TypeVar("M", bound=BaseModel)
PROMPTS_DIR = Path(__file__).parent / "prompts"
RETRY_WAIT_S = 20


class LLMCLIError(RuntimeError):
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


def _build_prompt(prompt: str, images: list[Path], how: str) -> str:
    if not images:
        return f"{prompt}\n\nReply with the JSON only."
    listing = "\n".join(f"Image {i}: {p.resolve()}" for i, p in enumerate(images, start=1))
    return f"{how}\n{listing}\n\n{prompt}\n\nYour final message must be the JSON only."


def _find(binary_name: str, hint: str) -> str:
    binary = shutil.which(binary_name)
    if binary is None:
        raise LLMCLIError(f"'{binary_name}' not found. {hint} (see README).")
    return binary


def _run(cmd: list[str], stdin: str | None, env: dict[str, str] | None) -> str:
    """Run the CLI, retrying failures and timeouts (transient service errors are common)."""
    settings = get_settings()
    error = ""
    for attempt in range(settings.llm_cli_retries + 1):
        if attempt:
            time.sleep(RETRY_WAIT_S * attempt)
        try:
            proc = _run_once(cmd, stdin, env, settings.llm_timeout_s)
        except subprocess.TimeoutExpired:
            error = f"timed out after {settings.llm_timeout_s} s"
            continue
        if proc.returncode == 0:
            return proc.stdout
        error = f"exited {proc.returncode}: {proc.stderr.strip()[:500]}"
    raise LLMCLIError(f"{Path(cmd[0]).name} {error}")


def _run_once(
    cmd: list[str], stdin: str | None, env: dict[str, str] | None, timeout: int
) -> subprocess.CompletedProcess[str]:
    if stdin is None:
        # Never let the CLI wait on (or read a prompt from) our own stdin.
        return subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout,
        )
    return subprocess.run(
        cmd, input=stdin, capture_output=True, text=True, env=env, timeout=timeout
    )


def _run_copilot(prompt: str, images: list[Path]) -> str:
    settings = get_settings()
    binary = _find(settings.copilot_bin, "Install GitHub Copilot CLI and sign in")
    cmd = [
        binary,
        "-p",
        _build_prompt(prompt, images, "The following images are attached, in this order:"),
        "--silent",
        "--no-color",
        "--no-ask-user",
        "--no-custom-instructions",
        "--disable-builtin-mcps",
        "--available-tools=view",
    ]
    for p in images:
        cmd += ["--attachment", str(p.resolve())]
    for d in sorted({str(p.resolve().parent) for p in images}):
        cmd += ["--add-dir", d]
    if settings.model:
        cmd += ["--model", settings.model]
    return _run(cmd, None, None)


def _run_claude(prompt: str, images: list[Path]) -> str:
    settings = get_settings()
    binary = _find(settings.claude_bin, "Install Claude Code and sign in")
    cmd = [binary, "-p", "--output-format", "json", "--allowedTools", "Read"]
    if settings.model:
        cmd += ["--model", settings.model]
    for d in sorted({str(p.resolve().parent) for p in images}):
        cmd += ["--add-dir", d]
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    how = "Open each of these image files with the Read tool and look at them carefully:"
    out = _run(cmd, _build_prompt(prompt, images, how), env)
    try:
        envelope = json.loads(out)
    except json.JSONDecodeError as e:
        raise LLMCLIError(f"Unexpected Claude CLI output: {out[:500]}") from e
    if envelope.get("is_error"):
        raise LLMCLIError(f"Claude reported an error: {envelope.get('result')}")
    return str(envelope.get("result", ""))


def _run_cli(prompt: str, images: list[Path]) -> str:
    if get_settings().llm == "claude":
        return _run_claude(prompt, images)
    return _run_copilot(prompt, images)


def _cache_path(prompt: str, images: list[Path]) -> Path | None:
    """Where a validated reply for this backend, model, prompt and image bytes is stored."""
    settings = get_settings()
    if not settings.llm_cache:
        return None
    h = hashlib.sha256(f"{settings.llm}|{settings.model}|{prompt}".encode())
    for p in images:
        h.update(hashlib.sha256(p.read_bytes()).digest())
    return settings.data_dir / "cache" / "llm" / f"{h.hexdigest()}.txt"


def ask_json(prompt: str, images: list[Path], schema: type[M], retries: int = 1) -> M:
    """Send prompt + images to the LLM (via its CLI) and parse the reply into `schema`.

    Retries once with the validation error appended if the reply isn't valid JSON for the schema.
    Valid replies are cached (see `_cache_path`), so re-running a stage on unchanged inputs makes
    no LLM calls. Set LEGO_BUILDER_LLM_CACHE=false to always ask again.
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
    raise LLMCLIError(f"Could not get valid JSON from the LLM: {last_error}")
