"""Runtime settings, loaded from environment variables / .env."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="LEGO_BUILDER_", extra="ignore")

    # Claude Code CLI (uses your Claude subscription; no API key)
    claude_bin: str = "claude"
    model: str = ""  # optional, e.g. "sonnet" or "opus"; empty = CLI default
    claude_timeout_s: int = 300
    claude_cache: bool = True  # reuse validated replies for identical prompt + images

    data_dir: Path = Path("data")
    pdf_dpi: int = 200


def get_settings() -> Settings:
    return Settings()
