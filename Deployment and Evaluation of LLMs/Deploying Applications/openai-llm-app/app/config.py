"""Environment-based application configuration."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables or a local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "OpenAI Customer Support Classifier"
    app_env: str = "development"
    log_level: str = "INFO"

    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4.1-mini"
    openai_timeout_seconds: float = Field(default=30.0, gt=0, le=120)
    openai_max_retries: int = Field(default=2, ge=0, le=5)

    max_input_chars: int = Field(default=4000, ge=100, le=20_000)

    @property
    def openai_is_configured(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.get_secret_value())


@lru_cache
def get_settings() -> Settings:
    """Return one cached settings object per process."""

    return Settings()
