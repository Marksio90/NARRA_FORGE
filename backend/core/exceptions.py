"""
Custom exceptions for NarraForge.

This module defines application-specific exceptions for better error handling.
"""

from typing import Any, Optional


class NarraForgeException(Exception):
    """Base exception for all NarraForge errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class DatabaseError(NarraForgeException):
    """Database operation failed."""

    pass


class JobNotFoundError(NarraForgeException):
    """Job not found in database."""

    pass


class JobAlreadyRunningError(NarraForgeException):
    """Job is already running and cannot be started again."""

    pass


class BudgetExceededError(NarraForgeException):
    """Job exceeded budget limit."""

    pass


class OpenAIError(NarraForgeException):
    """OpenAI API call failed."""

    pass


class ModelSelectionError(NarraForgeException):
    """Failed to select appropriate model."""

    pass


class AgentError(NarraForgeException):
    """Agent execution failed."""

    pass


class OrchestrationError(NarraForgeException):
    """Pipeline orchestration failed."""

    pass


class ValidationError(NarraForgeException):
    """Data validation failed."""

    pass


class ExportError(NarraForgeException):
    """Export operation failed."""

    pass


class ConfigurationError(NarraForgeException):
    """Configuration error."""

    pass
