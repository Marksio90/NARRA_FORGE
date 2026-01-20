"""
Configuration management for NarraForge using Pydantic Settings.

Settings are loaded from environment variables and .env file.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==================== Environment ====================
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development", description="Application environment"
    )
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # ==================== Database ====================
    DATABASE_URL: str = Field(..., description="PostgreSQL connection URL")
    POSTGRES_USER: str = Field(default="narraforge")
    POSTGRES_PASSWORD: str = Field(default="")
    POSTGRES_DB: str = Field(default="narraforge")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)

    # ==================== Redis ====================
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)

    # ==================== Celery ====================
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")
    CELERY_TASK_TRACK_STARTED: bool = Field(default=True)
    CELERY_TASK_TIME_LIMIT: int = Field(default=3600, description="Task timeout in seconds")

    # ==================== OpenAI ====================
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    OPENAI_TIMEOUT: int = Field(default=180, description="OpenAI API timeout in seconds")
    DEFAULT_MODEL_TIER: int = Field(default=1, ge=1, le=3, description="Default model tier (1=mini, 2=4o, 3=4)")

    # ==================== FastAPI ====================
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    API_WORKERS: int = Field(default=1, ge=1)
    API_RELOAD: bool = Field(default=True)
    SECRET_KEY: str = Field(default="dev_secret_key_change_in_production")

    # ==================== CORS ====================
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins",
    )

    # ==================== Application ====================
    MAX_COST_PER_PROJECT: float = Field(default=50.0, gt=0, description="Maximum cost per project in USD")
    DEFAULT_BUDGET_LIMIT: float = Field(default=10.0, gt=0, description="Default budget limit for jobs")
    MAX_CONCURRENT_JOBS: int = Field(default=5, ge=1, description="Maximum concurrent jobs")

    # ==================== File Storage ====================
    ARTIFACTS_DIR: str = Field(default="/app/artifacts", description="Directory for generated artifacts")
    LOGS_DIR: str = Field(default="/app/logs", description="Directory for logs")

    # ==================== Model Pricing (USD per 1M tokens) ====================
    # GPT-4o-mini
    GPT_4O_MINI_INPUT_PRICE: float = Field(default=0.150)
    GPT_4O_MINI_OUTPUT_PRICE: float = Field(default=0.600)

    # GPT-4o
    GPT_4O_INPUT_PRICE: float = Field(default=2.50)
    GPT_4O_OUTPUT_PRICE: float = Field(default=10.00)

    # GPT-4 (reserved for premium tier)
    GPT_4_INPUT_PRICE: float = Field(default=30.00)
    GPT_4_OUTPUT_PRICE: float = Field(default=60.00)

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_key(cls, v: str) -> str:
        """Validate OpenAI API key format."""
        if not v or v == "sk-your-openai-api-key-here":
            raise ValueError("OPENAI_API_KEY must be set to a valid API key")
        if not v.startswith("sk-"):
            raise ValueError("OPENAI_API_KEY must start with 'sk-'")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v_upper

    def get_model_cost(self, model: str, tokens_input: int, tokens_output: int) -> float:
        """
        Calculate cost for a model based on token usage.

        Args:
            model: Model name (e.g., "gpt-4o-mini", "gpt-4o")
            tokens_input: Number of input tokens
            tokens_output: Number of output tokens

        Returns:
            Cost in USD
        """
        pricing = {
            "gpt-4o-mini": (self.GPT_4O_MINI_INPUT_PRICE, self.GPT_4O_MINI_OUTPUT_PRICE),
            "gpt-4o": (self.GPT_4O_INPUT_PRICE, self.GPT_4O_OUTPUT_PRICE),
            "gpt-4": (self.GPT_4_INPUT_PRICE, self.GPT_4_OUTPUT_PRICE),
        }

        if model not in pricing:
            raise ValueError(f"Unknown model: {model}")

        input_price, output_price = pricing[model]
        cost = (tokens_input * input_price + tokens_output * output_price) / 1_000_000
        return cost


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    This function is cached to avoid reading environment variables multiple times.
    """
    return Settings()
