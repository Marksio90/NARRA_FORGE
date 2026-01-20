"""
Application configuration.
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "NarraForge"
    VERSION: str = "1.0.0"
    ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql://narraforge:narraforge_secret@localhost:5432/narraforge"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # OpenAI
    OPENAI_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Costs
    MAX_COST_PER_BOOK: float = 10.00
    WARN_COST_THRESHOLD: float = 5.00

    # Paths
    OUTPUTS_DIR: str = "/app/outputs"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def is_development(self) -> bool:
        return self.ENV == "development"

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"


# Global settings instance
settings = Settings()
