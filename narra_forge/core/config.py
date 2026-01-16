"""
Configuration system for NARRA_FORGE V2
Uses pydantic-settings for environment variable loading
"""
from pathlib import Path
from typing import Dict, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class NarraForgeConfig(BaseSettings):
    """
    Main configuration for NARRA_FORGE.
    Loads from environment variables and .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ═══════════════════════════════════════════
    # OPENAI API (REQUIRED)
    # ═══════════════════════════════════════════

    openai_api_key: str = Field(
        ...,  # Required
        description="OpenAI API key (REQUIRED)",
    )

    # ═══════════════════════════════════════════
    # MODEL CONFIGURATION
    # ═══════════════════════════════════════════

    default_mini_model: str = Field(
        default="gpt-4o-mini",
        description="Model for analysis, planning, validation (COST-OPTIMIZED)",
    )

    default_gpt4_model: str = Field(
        default="gpt-4o",
        description="Model for narrative generation (HIGH-QUALITY)",
    )

    # Model selection rules
    use_mini_for_analysis: bool = Field(
        default=True,
        description="Use mini model for all analytical tasks",
    )

    use_gpt4_for_narrative: bool = Field(
        default=True,
        description="Use GPT-4 for narrative generation",
    )

    # ═══════════════════════════════════════════
    # COST LIMITS
    # ═══════════════════════════════════════════

    max_cost_per_job: float = Field(
        default=10.0,
        description="Maximum cost per production job (USD)",
    )

    warn_cost_threshold: float = Field(
        default=5.0,
        description="Warn when job cost exceeds this (USD)",
    )

    # ═══════════════════════════════════════════
    # QUALITY THRESHOLDS
    # ═══════════════════════════════════════════

    min_coherence_score: float = Field(
        default=0.90,  # QUALITY-FIRST: Raised for bestseller-level output
        ge=0.0,
        le=1.0,
        description="Minimum coherence score (0.0-1.0)",
    )

    min_language_quality: float = Field(
        default=0.85,  # QUALITY-FIRST: Raised for literary quality
        ge=0.0,
        le=1.0,
        description="Minimum language quality score",
    )

    min_narrative_weight: float = Field(
        default=0.70,  # Lowered from 0.75 for initial testing
        ge=0.0,
        le=1.0,
        description="Minimum narrative weight score",
    )

    enable_strict_validation: bool = Field(
        default=True,
        description="Enable strict validation (fail on quality issues)",
    )

    # ═══════════════════════════════════════════
    # PATHS
    # ═══════════════════════════════════════════

    db_path: Path = Field(
        default=Path("data/narra_forge.db"),
        description="SQLite database path",
    )

    output_dir: Path = Field(
        default=Path("output"),
        description="Output directory for generated narratives",
    )

    log_dir: Path = Field(
        default=Path("logs"),
        description="Log directory",
    )

    # ═══════════════════════════════════════════
    # ENVIRONMENT
    # ═══════════════════════════════════════════

    environment: str = Field(
        default="development",
        description="Environment: development, staging, production",
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR",
    )

    # ═══════════════════════════════════════════
    # RETRY & TIMEOUT
    # ═══════════════════════════════════════════

    max_retries: int = Field(
        default=3,
        description="Maximum retries for failed operations",
    )

    api_timeout_seconds: int = Field(
        default=120,
        description="API call timeout (seconds)",
    )

    # ═══════════════════════════════════════════
    # RATE LIMITING
    # ═══════════════════════════════════════════

    mini_rpm_limit: int = Field(
        default=500,
        description="gpt-4o-mini requests per minute limit",
    )

    mini_tpm_limit: int = Field(
        default=200000,
        description="gpt-4o-mini tokens per minute limit",
    )

    gpt4_rpm_limit: int = Field(
        default=100,
        description="gpt-4o requests per minute limit",
    )

    gpt4_tpm_limit: int = Field(
        default=80000,
        description="gpt-4o tokens per minute limit",
    )

    # ═══════════════════════════════════════════
    # PRODUCTION DEFAULTS
    # ═══════════════════════════════════════════

    default_word_counts: Dict[str, tuple] = Field(
        default={
            "short_story": (5000, 10000),
            "novella": (10000, 40000),
            "novel": (40000, 120000),
            "epic_saga": (120000, 500000),
        },
        description="Default word count ranges for production types",
    )

    # ═══════════════════════════════════════════
    # VALIDATORS
    # ═══════════════════════════════════════════

    @field_validator("openai_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate OpenAI API key format"""
        if not v or v == "sk-proj-your-key-here":
            raise ValueError(
                "OPENAI_API_KEY not set. "
                "Copy .env.example to .env and add your key."
            )
        if not v.startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format (must start with 'sk-')")
        return v

    @field_validator("db_path", "output_dir", "log_dir")
    @classmethod
    def ensure_dirs_exist(cls, v: Path) -> Path:
        """Ensure directories exist"""
        v.parent.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment"""
        valid = ["development", "staging", "production", "testing"]
        if v not in valid:
            raise ValueError(f"Invalid environment. Must be one of: {valid}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        valid = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid:
            raise ValueError(f"Invalid log level. Must be one of: {valid}")
        return v_upper

    # ═══════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════

    def get_model_for_stage(self, stage: str) -> str:
        """
        Get appropriate model for a pipeline stage.

        Rules:
        - Analysis/Planning/Validation: mini (cost-optimized)
        - Narrative generation: gpt-4 (quality-optimized)
        """
        narrative_stages = [
            "06_sequential_generation",
            "08_language_stylization",
        ]

        if stage in narrative_stages and self.use_gpt4_for_narrative:
            return self.default_gpt4_model
        else:
            return self.default_mini_model

    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"

    def get_word_count_range(self, production_type: str) -> tuple[int, int]:
        """Get word count range for production type"""
        return self.default_word_counts.get(production_type, (5000, 10000))


# ═══════════════════════════════════════════
# SINGLETON PATTERN
# ═══════════════════════════════════════════

_config_instance: Optional[NarraForgeConfig] = None


def get_config() -> NarraForgeConfig:
    """
    Get global config instance (singleton).
    Loads from .env file on first call.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = NarraForgeConfig()
    return _config_instance


def reload_config() -> NarraForgeConfig:
    """
    Reload configuration (useful for testing).
    """
    global _config_instance
    _config_instance = NarraForgeConfig()
    return _config_instance


# ═══════════════════════════════════════════
# CONVENIENCE FUNCTION
# ═══════════════════════════════════════════


def create_default_config(
    openai_api_key: str,
    environment: str = "development",
    **overrides,
) -> NarraForgeConfig:
    """
    Create config with defaults (useful for programmatic usage).

    Example:
        config = create_default_config(
            openai_api_key="sk-...",
            max_cost_per_job=20.0
        )
    """
    config_dict = {
        "openai_api_key": openai_api_key,
        "environment": environment,
        **overrides,
    }

    return NarraForgeConfig(**config_dict)
