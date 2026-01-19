"""Custom exceptions for NARRA_FORGE."""


class NarraForgeException(Exception):
    """Base exception for NARRA_FORGE."""

    pass


class ValidationError(NarraForgeException):
    """Raised when data validation fails."""

    pass


class QAGateError(NarraForgeException):
    """Raised when QA gate fails."""

    pass


class ModelPolicyError(NarraForgeException):
    """Raised when model policy is violated."""

    pass


class TokenBudgetExceededError(NarraForgeException):
    """Raised when token budget is exceeded."""

    pass


class WorldRuleViolationError(NarraForgeException):
    """Raised when world rules are violated."""

    pass
