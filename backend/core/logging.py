"""JSON logging configuration."""

import logging
import sys
from typing import Any

from pythonjsonlogger import jsonlogger

from core.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):  # type: ignore[misc]
    """Custom JSON formatter with additional fields."""

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        log_record["app_name"] = settings.app_name
        log_record["app_version"] = settings.app_version
        log_record["environment"] = settings.environment
        log_record["level"] = record.levelname


def setup_logging(level: str = "INFO") -> None:
    """Setup JSON logging for the application."""
    logger = logging.getLogger()
    logger.setLevel(level)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s",
        rename_fields={
            "timestamp": "asctime",
        },
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# Setup logging on module import
setup_logging()
