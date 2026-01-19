"""Tests for configuration module."""

import pytest
from pydantic import ValidationError

from core.config import Settings


def test_settings_default_values() -> None:
    """Test that settings have correct default values."""
    settings = Settings()
    assert settings.app_name == "NARRA_FORGE"
    assert settings.app_version == "0.1.0"
    assert settings.environment in ["development", "production", "test"]


def test_settings_model_validation() -> None:
    """Test that settings validate correctly."""
    settings = Settings(environment="production")
    assert settings.environment == "production"

    with pytest.raises(ValidationError):
        Settings(environment="invalid")


def test_model_policy() -> None:
    """Test model policy settings."""
    settings = Settings()
    assert settings.model_mini == "gpt-4o-mini"
    assert settings.model_high == "gpt-4o"


def test_token_budgets() -> None:
    """Test token budget settings."""
    settings = Settings()
    assert settings.token_budget_per_segment == 2000
    assert settings.token_budget_per_job_default == 50000
