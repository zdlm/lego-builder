"""Runtime settings, loaded from environment variables / .env."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="LEGO_BUILDER_", extra="ignore")

    model: str = ""  # Claude model id; set LEGO_BUILDER_MODEL
    data_dir: Path = Path("data")
    pdf_dpi: int = 200


def get_settings() -> Settings:
    return Settings()
