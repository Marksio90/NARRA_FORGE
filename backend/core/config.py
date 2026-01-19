"""Configuration management using Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "NARRA_FORGE"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", pattern="^(development|production|test)$")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/narra_forge"
    )
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")

    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/1")
    celery_result_backend: str = Field(default="redis://localhost:6379/2")

    # OpenAI
    openai_api_key: str = Field(default="")

    # Model Policy
    model_mini: str = "gpt-4o-mini"
    model_high: str = "gpt-4o"

    # Token Budgets
    token_budget_per_segment: int = 2000
    token_budget_per_job_default: int = 50000

    # Observability
    otel_exporter_otlp_endpoint: str = Field(default="")


settings = Settings()
