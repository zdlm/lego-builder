"""Runtime settings, loaded from environment variables / .env."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="LEGO_BUILDER_", extra="ignore")

    # LLM via a signed-in agent CLI on your own subscription (no API keys)
    llm: Literal["copilot", "claude"] = "copilot"
    copilot_bin: str = "copilot"
    claude_bin: str = "claude"
    model: str = ""  # optional --model value for the chosen CLI; empty = CLI default
    llm_timeout_s: int = 300
    llm_cli_retries: int = 3  # extra attempts after a failed or timed-out CLI call
    llm_cache: bool = True  # reuse validated replies for identical prompt + images

    data_dir: Path = Path("data")
    pdf_dpi: int = 200


def get_settings() -> Settings:
    return Settings()
