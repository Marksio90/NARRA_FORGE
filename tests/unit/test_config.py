"""
Tests for configuration system
"""
import pytest
from pydantic import ValidationError

from narra_forge.core.config import NarraForgeConfig, create_default_config


def test_config_requires_api_key():
    """Test that API key is required"""
    with pytest.raises(ValidationError):
        NarraForgeConfig(openai_api_key="sk-proj-your-key-here")


def test_config_with_valid_key():
    """Test config with valid API key"""
    config = create_default_config(
        openai_api_key="sk-test-key-12345",
        environment="testing"
    )
    assert config.openai_api_key == "sk-test-key-12345"
    assert config.environment == "testing"


def test_config_defaults():
    """Test default configuration values"""
    config = create_default_config(
        openai_api_key="sk-test-key",
        environment="testing"
    )

    assert config.default_mini_model == "gpt-4o-mini"
    assert config.default_gpt4_model == "gpt-4o"
    assert config.max_cost_per_job == 10.0
    assert config.min_coherence_score == 0.85


def test_model_routing():
    """Test model selection for stages"""
    config = create_default_config(
        openai_api_key="sk-test-key",
        environment="testing"
    )

    # Analysis stages should use mini
    assert config.get_model_for_stage("01_brief_interpretation") == "gpt-4o-mini"
    assert config.get_model_for_stage("02_world_architecture") == "gpt-4o-mini"

    # Generation stages should use gpt-4o
    assert config.get_model_for_stage("06_sequential_generation") == "gpt-4o"
    assert config.get_model_for_stage("08_language_stylization") == "gpt-4o"


def test_word_count_ranges():
    """Test word count range retrieval"""
    config = create_default_config(
        openai_api_key="sk-test-key",
        environment="testing"
    )

    short_story_range = config.get_word_count_range("short_story")
    assert short_story_range == (5000, 10000)

    novel_range = config.get_word_count_range("novel")
    assert novel_range == (40000, 120000)


def test_environment_validation():
    """Test environment validation"""
    # Valid environments
    for env in ["development", "staging", "production", "testing"]:
        config = create_default_config(
            openai_api_key="sk-test-key",
            environment=env
        )
        assert config.environment == env

    # Invalid environment
    with pytest.raises(ValidationError):
        create_default_config(
            openai_api_key="sk-test-key",
            environment="invalid"
        )


def test_cost_thresholds():
    """Test cost threshold configuration"""
    config = create_default_config(
        openai_api_key="sk-test-key",
        max_cost_per_job=5.0,
        warn_cost_threshold=2.5,
    )

    assert config.max_cost_per_job == 5.0
    assert config.warn_cost_threshold == 2.5


def test_quality_thresholds():
    """Test quality threshold configuration"""
    config = create_default_config(
        openai_api_key="sk-test-key",
        min_coherence_score=0.9,
        min_language_quality=0.85,
    )

    assert config.min_coherence_score == 0.9
    assert config.min_language_quality == 0.85
