"""
Monitoring & Observability

Provides:
- Structured logging (structlog)
- Metrics collection (Prometheus)
- Error tracking (Sentry)
"""
from narra_forge.monitoring.logger import get_logger, configure_logging
from narra_forge.monitoring.metrics import (
    MetricsCollector,
    track_agent_execution,
    track_pipeline_execution,
    track_api_call,
)
from narra_forge.monitoring.sentry import (
    init_sentry,
    set_context,
    set_tag,
    set_user,
    capture_exception,
    capture_message,
    SentryTransaction,
    SentrySpan,
    add_breadcrumb,
)

__all__ = [
    # Logging
    "get_logger",
    "configure_logging",
    # Metrics
    "MetricsCollector",
    "track_agent_execution",
    "track_pipeline_execution",
    "track_api_call",
    # Error tracking (Sentry)
    "init_sentry",
    "set_context",
    "set_tag",
    "set_user",
    "capture_exception",
    "capture_message",
    "SentryTransaction",
    "SentrySpan",
    "add_breadcrumb",
]
