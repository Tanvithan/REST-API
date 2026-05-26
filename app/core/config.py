from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = Field(..., env="DATABASE_URL")
    github_token: Optional[str] = Field(None, env="GITHUB_TOKEN")
    github_api_base: str = Field("https://api.github.com", env="GITHUB_API_BASE")
    external_api_timeout: int = Field(10, env="EXTERNAL_API_TIMEOUT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
