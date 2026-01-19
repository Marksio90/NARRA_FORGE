"""Tests for custom exceptions."""

from core.exceptions import (
    ModelPolicyError,
    NarraForgeException,
    QAGateError,
    TokenBudgetExceededError,
    ValidationError,
    WorldRuleViolationError,
)


def test_base_exception() -> None:
    """Test base exception."""
    exc = NarraForgeException("test error")
    assert str(exc) == "test error"
    assert isinstance(exc, Exception)


def test_validation_error() -> None:
    """Test validation error."""
    exc = ValidationError("validation failed")
    assert str(exc) == "validation failed"
    assert isinstance(exc, NarraForgeException)


def test_qa_gate_error() -> None:
    """Test QA gate error."""
    exc = QAGateError("QA gate failed")
    assert str(exc) == "QA gate failed"
    assert isinstance(exc, NarraForgeException)


def test_model_policy_error() -> None:
    """Test model policy error."""
    exc = ModelPolicyError("model policy violated")
    assert str(exc) == "model policy violated"
    assert isinstance(exc, NarraForgeException)


def test_token_budget_exceeded_error() -> None:
    """Test token budget exceeded error."""
    exc = TokenBudgetExceededError("budget exceeded")
    assert str(exc) == "budget exceeded"
    assert isinstance(exc, NarraForgeException)


def test_world_rule_violation_error() -> None:
    """Test world rule violation error."""
    exc = WorldRuleViolationError("world rule violated")
    assert str(exc) == "world rule violated"
    assert isinstance(exc, NarraForgeException)
