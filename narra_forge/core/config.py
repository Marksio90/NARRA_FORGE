"""
Configuration management for NARRA_FORGE.
Supports multiple LLM backends and system-wide settings.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import os
from pathlib import Path


@dataclass
class ModelConfig:
    """Configuration for a specific model backend."""
    provider: str  # "anthropic", "openai", "local", etc.
    model_name: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None

    # Model parameters
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0

    # Cost optimization
    cost_per_token: float = 0.0
    priority: int = 1  # Lower = higher priority

    # Fallback
    fallback_to: Optional[str] = None


@dataclass
class SystemConfig:
    """System-wide configuration."""

    # Model backends
    models: Dict[str, ModelConfig] = field(default_factory=dict)
    default_model: str = "claude-sonnet"

    # Memory system
    memory_db_path: Path = Path("./data/memory.db")
    vector_db_path: Path = Path("./data/vectors")
    max_memory_items: int = 10000

    # Pipeline settings
    enable_parallel_agents: bool = True
    max_retries: int = 3
    validation_threshold: float = 0.8

    # Quality control
    min_coherence_score: float = 0.85
    enable_strict_validation: bool = True

    # Output settings
    output_dir: Path = Path("./output")
    enable_audiobook_format: bool = True

    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = Path("./logs/narra_forge.log")

    def __post_init__(self):
        """Ensure directories exist."""
        self.memory_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)


def get_default_config() -> SystemConfig:
    """Returns default system configuration."""
    config = SystemConfig()

    # Configure Claude Sonnet as default
    config.models["claude-sonnet"] = ModelConfig(
        provider="anthropic",
        model_name="claude-sonnet-4-5-20250929",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.7,
        cost_per_token=0.000003,
        priority=1
    )

    # Configure Claude Opus for critical stages
    config.models["claude-opus"] = ModelConfig(
        provider="anthropic",
        model_name="claude-opus-4-5-20251101",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.8,
        cost_per_token=0.000015,
        priority=2,
        fallback_to="claude-sonnet"
    )

    # Configure GPT-4 as alternative
    config.models["gpt-4"] = ModelConfig(
        provider="openai",
        model_name="gpt-4-turbo-preview",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
        cost_per_token=0.00001,
        priority=3,
        fallback_to="claude-sonnet"
    )

    # Configure Haiku for lightweight operations
    config.models["claude-haiku"] = ModelConfig(
        provider="anthropic",
        model_name="claude-3-5-haiku-20241022",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.6,
        cost_per_token=0.000001,
        priority=4
    )

    config.default_model = "claude-sonnet"

    return config
