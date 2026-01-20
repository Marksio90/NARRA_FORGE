"""
Structured logging configuration for NarraForge using structlog.

This module provides:
- Structured JSON logging for production
- Human-readable logging for development
- Consistent log formatting across services
"""

import logging
import sys
from typing import Any

import structlog

from core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """
    Configure structured logging for the application.

    In development: Human-readable colored output
    In production: JSON-formatted logs for parsing
    """
    # Determine log level
    log_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Determine processors based on environment
    if settings.ENVIRONMENT == "development":
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Structured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started", job_id="123", stage="world_building")
    """
    return structlog.get_logger(name)


# Setup logging on module import
setup_logging()
