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

    # =====================================================================
    # GŁÓWNY MODEL: GPT-4 Turbo (OpenAI)
    # Skuteczny, szybki i 3x tańszy niż Claude Opus
    # =====================================================================
    config.models["gpt-4-turbo"] = ModelConfig(
        provider="openai",
        model_name="gpt-4-turbo-preview",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
        cost_per_token=0.00002,  # ~$0.02/1K tokens (średnia input+output)
        priority=1,
        fallback_to="gpt-3.5-turbo"
    )

    # GPT-3.5 Turbo - Szybki i bardzo tani fallback
    config.models["gpt-3.5-turbo"] = ModelConfig(
        provider="openai",
        model_name="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
        cost_per_token=0.000001,  # ~$0.001/1K tokens (bardzo tani!)
        priority=2
    )

    # GPT-4 standard (dla zadań wymagających najwyższej jakości)
    config.models["gpt-4"] = ModelConfig(
        provider="openai",
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.8,
        cost_per_token=0.00003,  # Droższy ale najlepsza jakość
        priority=3,
        fallback_to="gpt-4-turbo"
    )

    # =====================================================================
    # OPCJONALNE: Claude (Anthropic) jako backup
    # =====================================================================
    config.models["claude-sonnet"] = ModelConfig(
        provider="anthropic",
        model_name="claude-sonnet-4-5-20250929",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.7,
        cost_per_token=0.000009,  # ~$0.009/1K tokens
        priority=4,
        fallback_to="gpt-4-turbo"
    )

    config.models["claude-opus"] = ModelConfig(
        provider="anthropic",
        model_name="claude-opus-4-5-20251101",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.8,
        cost_per_token=0.000045,  # ~$0.045/1K tokens (najdroższy)
        priority=5,
        fallback_to="gpt-4"
    )

    # DOMYŚLNY MODEL: GPT-4 Turbo
    config.default_model = "gpt-4-turbo"

    return config
