from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    API_URL: str = "http://api:8000"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[5] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


config = Config()

