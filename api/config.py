"""
API Configuration Settings.

Manages FastAPI-specific configuration separate from core NarraForge config.
"""

import os
from functools import lru_cache
from typing import List

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


@lru_cache()
def get_settings() -> APISettings:
    """
    Get cached API settings.

    Uses lru_cache to ensure settings are only loaded once.
    """
    return APISettings()


# Global settings instance
settings = get_settings()
