from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = Field(..., validation_alias="DATABASE_URL")
    github_token: Optional[str] = Field(None, validation_alias="GITHUB_TOKEN")
    github_api_base: str = Field(
        "https://api.github.com", validation_alias="GITHUB_API_BASE"
    )
    external_api_timeout: int = Field(10, validation_alias="EXTERNAL_API_TIMEOUT")


settings = Settings()
