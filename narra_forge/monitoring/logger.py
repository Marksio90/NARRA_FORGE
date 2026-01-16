"""
Structured logging with structlog

Provides consistent, machine-readable logs across the entire platform.
"""
import sys
import logging
from typing import Any, Dict, Optional
import structlog
from pathlib import Path


def configure_logging(
    level: str = "INFO",
    output_file: Optional[Path] = None,
    json_output: bool = False,
) -> None:
    """
    Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        output_file: Optional file path for log output
        json_output: If True, output logs as JSON (for production)
    """
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout if output_file is None else open(output_file, "a"),
        level=getattr(logging, level.upper()),
    )

    # Configure structlog
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_output:
        # Production: JSON output for machine parsing
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Development: Human-readable output with colors
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True),
        ])

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str, **initial_context: Any) -> structlog.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (usually __name__ of the module)
        **initial_context: Initial context to bind to logger

    Returns:
        Configured structlog logger

    Example:
        >>> log = get_logger(__name__, component="orchestrator")
        >>> log.info("starting_pipeline", job_id="job_123")
        2024-01-01T12:00:00 [info] starting_pipeline component=orchestrator job_id=job_123
    """
    logger = structlog.get_logger(name)

    if initial_context:
        logger = logger.bind(**initial_context)

    return logger


class LoggerMixin:
    """
    Mixin to add structured logging to any class.

    Usage:
        class MyComponent(LoggerMixin):
            def __init__(self):
                self.log = self.get_logger()

            def do_something(self):
                self.log.info("doing_something", status="started")
    """

    def get_logger(self, **context: Any) -> structlog.BoundLogger:
        """Get logger for this class with class name as context"""
        return get_logger(
            self.__class__.__module__,
            component=self.__class__.__name__,
            **context
        )


# Common log patterns
def log_agent_start(log: structlog.BoundLogger, agent_id: str, input_data: Dict[str, Any]) -> None:
    """Log agent execution start"""
    log.info(
        "agent_execution_started",
        agent_id=agent_id,
        input_keys=list(input_data.keys()),
    )


def log_agent_complete(
    log: structlog.BoundLogger,
    agent_id: str,
    duration_seconds: float,
    tokens_used: int,
    cost_usd: float,
) -> None:
    """Log agent execution completion"""
    log.info(
        "agent_execution_completed",
        agent_id=agent_id,
        duration_seconds=round(duration_seconds, 2),
        tokens_used=tokens_used,
        cost_usd=round(cost_usd, 4),
    )


def log_agent_error(
    log: structlog.BoundLogger,
    agent_id: str,
    error: Exception,
    retry_attempt: int,
) -> None:
    """Log agent execution error"""
    log.error(
        "agent_execution_failed",
        agent_id=agent_id,
        error_type=type(error).__name__,
        error_message=str(error),
        retry_attempt=retry_attempt,
        exc_info=True,
    )


def log_pipeline_start(
    log: structlog.BoundLogger,
    job_id: str,
    production_type: str,
    genre: str,
) -> None:
    """Log pipeline execution start"""
    log.info(
        "pipeline_started",
        job_id=job_id,
        production_type=production_type,
        genre=genre,
    )


def log_pipeline_complete(
    log: structlog.BoundLogger,
    job_id: str,
    duration_seconds: float,
    total_tokens: int,
    total_cost_usd: float,
    quality_score: float,
) -> None:
    """Log pipeline execution completion"""
    log.info(
        "pipeline_completed",
        job_id=job_id,
        duration_seconds=round(duration_seconds, 2),
        total_tokens=total_tokens,
        total_cost_usd=round(total_cost_usd, 4),
        quality_score=round(quality_score, 3),
    )


def log_api_call(
    log: structlog.BoundLogger,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    duration_seconds: float,
) -> None:
    """Log OpenAI API call"""
    log.debug(
        "openai_api_call",
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        duration_seconds=round(duration_seconds, 3),
    )
