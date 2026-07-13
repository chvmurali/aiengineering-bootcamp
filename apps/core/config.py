from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


config = Config()