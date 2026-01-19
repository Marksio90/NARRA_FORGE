"""
API Configuration Settings.

Manages FastAPI-specific configuration separate from core NarraForge config.
"""

import os
from functools import lru_cache
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    """
    API configuration settings.

    Loads from environment variables and .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # API Info
    app_name: str = "NARRA_FORGE API"
    app_version: str = "2.0.0"
    app_description: str = "Professional AI-powered narrative generation platform"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """
        Parse CORS origins from string or list.

        Handles:
        - Empty string -> default list
        - Comma-separated string -> list
        - List -> pass through
        """
        if isinstance(v, str):
            # Empty string or whitespace only -> use default
            if not v or not v.strip():
                return ["http://localhost:3000", "http://localhost:8080"]
            # Comma-separated -> split
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Database
    database_url: str = ""
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_pre_ping: bool = True
    db_echo: bool = False

    # Authentication
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    def validate_jwt_secret(self) -> None:
        """
        Validate JWT secret key strength.

        Raises:
            ValueError: If JWT secret is too weak or missing
        """
        if not self.jwt_secret_key:
            raise ValueError("JWT_SECRET_KEY is required and cannot be empty")

        if len(self.jwt_secret_key) < 32:
            raise ValueError(
                f"JWT_SECRET_KEY must be at least 32 characters long (current: {len(self.jwt_secret_key)})"
            )

        # Check for common weak secrets
        weak_secrets = [
            "change-this-secret",
            "changeme",
            "secret",
            "your-secret-key",
            "your_secret_key",
            "change-this-secret-key-in-production",
        ]
        if self.jwt_secret_key.lower() in weak_secrets:
            raise ValueError(
                f"JWT_SECRET_KEY is using a weak/default value. Please use a strong random key."
            )

    # OAuth2 (Google)
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""

    # OAuth2 (GitHub)
    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = ""

    # Redis (for Celery & caching)
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 3600  # 1 hour

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    celery_task_track_started: bool = True
    celery_task_time_limit: int = 7200  # 2 hours

    # WebSocket
    ws_heartbeat_interval: int = 30  # seconds
    ws_max_connections: int = 1000

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 100

    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    enable_sentry: bool = False
    sentry_dsn: str = ""
    sentry_environment: str = "development"
    sentry_traces_sample_rate: float = 0.1

    # API Keys (for external services)
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # File Upload
    max_upload_size_mb: int = 10
    allowed_upload_types: List[str] = ["txt", "pdf", "docx"]

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    # Documentation
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"

    @property
    def database_url_async(self) -> str:
        """Get async database URL (asyncpg)."""
        if not self.database_url:
            # Build from components
            user = os.getenv("DB_USER", "narra_forge")
            password = os.getenv("DB_PASSWORD", "")
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "5432")
            name = os.getenv("DB_NAME", "narra_forge")
            return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"

        # Ensure asyncpg driver
        if "postgresql://" in self.database_url:
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        return self.database_url

    @property
    def database_url_sync(self) -> str:
        """Get sync database URL (psycopg2)."""
        async_url = self.database_url_async
        return async_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from string if needed."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins

    def validate_required_settings(self) -> None:
        """
        Validate that all critical settings are properly configured.

        Raises:
            ValueError: If critical settings are missing or invalid
        """
        errors = []

        # Database URL
        if not self.database_url and not all([
            os.getenv("DB_USER"),
            os.getenv("DB_PASSWORD"),
            os.getenv("DB_HOST"),
            os.getenv("DB_NAME")
        ]):
            errors.append("DATABASE_URL or DB_* components must be set")

        # Redis URL
        if not self.redis_url:
            errors.append("REDIS_URL must be set")

        # API Keys (at least one required)
        if not self.openai_api_key and not self.anthropic_api_key:
            errors.append("At least one AI API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) must be set")

        # Production-specific checks
        if not self.debug:
            # CORS origins should not include localhost in production
            if any("localhost" in origin or "127.0.0.1" in origin for origin in self.cors_origins_list):
                errors.append("CORS_ORIGINS should not include localhost in production")

            # Sentry DSN recommended in production
            if self.enable_sentry and not self.sentry_dsn:
                errors.append("SENTRY_DSN should be set when ENABLE_SENTRY is true")

        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
            raise ValueError(error_msg)


@lru_cache()
def get_settings() -> APISettings:
    """
    Get cached API settings.

    Uses lru_cache to ensure settings are only loaded once.

    Raises:
        ValueError: If critical settings are invalid or missing
    """
    settings = APISettings()

    # Validate critical settings
    settings.validate_jwt_secret()
    settings.validate_required_settings()

    return settings


# Global settings instance
settings = get_settings()
