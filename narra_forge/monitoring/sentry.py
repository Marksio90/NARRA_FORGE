"""
Sentry integration for NARRA_FORGE error tracking and performance monitoring.

This module provides:
- Error tracking (exceptions, crashes)
- Performance monitoring (traces, transactions)
- Release tracking
- Environment configuration
- Custom context and tags
"""

import os
from typing import Any, Dict, Optional

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def init_sentry(
    dsn: Optional[str] = None,
    environment: str = "development",
    release: Optional[str] = None,
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1,
    enable_logging: bool = True,
    debug: bool = False,
) -> None:
    """
    Initialize Sentry SDK for error tracking and performance monitoring.

    Args:
        dsn: Sentry DSN (Data Source Name). If None, reads from SENTRY_DSN env var.
        environment: Environment name (development, staging, production)
        release: Release version (e.g., "narra-forge@2.0.0")
        traces_sample_rate: Percentage of transactions to send (0.0-1.0)
        profiles_sample_rate: Percentage of profiles to send (0.0-1.0)
        enable_logging: Enable logging integration
        debug: Enable Sentry debug mode

    Example:
        >>> init_sentry(
        ...     dsn="https://abc123@o123.ingest.sentry.io/456",
        ...     environment="production",
        ...     release="narra-forge@2.0.0",
        ...     traces_sample_rate=0.2
        ... )
    """
    # Get DSN from environment if not provided
    if dsn is None:
        dsn = os.getenv("SENTRY_DSN")

    # Don't initialize if no DSN provided
    if not dsn:
        print("⚠️  Sentry DSN not provided. Error tracking disabled.")
        return

    # Configure integrations
    integrations = []

    if enable_logging:
        integrations.append(
            LoggingIntegration(
                level=None,  # Capture all logs
                event_level=None,  # Don't send logs as events (only breadcrumbs)
            )
        )

    # Initialize Sentry
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        integrations=integrations,
        debug=debug,
        # Before send hook to filter events
        before_send=before_send_hook,
        # Attach stacktrace to messages
        attach_stacktrace=True,
        # Send default PII (personally identifiable information)
        send_default_pii=False,
        # Max breadcrumbs
        max_breadcrumbs=50,
    )

    print(f"✓ Sentry initialized (env: {environment}, sample rate: {traces_sample_rate})")


def before_send_hook(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Hook called before sending event to Sentry.
    Can be used to filter or modify events.

    Args:
        event: Event data
        hint: Additional context

    Returns:
        Modified event or None to drop the event
    """
    # Filter out known non-critical errors
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]

        # Don't send KeyboardInterrupt
        if exc_type == KeyboardInterrupt:
            return None

        # Don't send expected OpenAI rate limits (already handled by retry logic)
        if exc_type.__name__ == "RateLimitError":
            # Only send if retry logic failed
            if "retry_attempt" not in event.get("extra", {}):
                return None

    return event


def set_context(key: str, value: Dict[str, Any]) -> None:
    """
    Set custom context for Sentry events.

    Args:
        key: Context key (e.g., "job", "pipeline")
        value: Context data

    Example:
        >>> set_context("job", {
        ...     "job_id": "job_123",
        ...     "production_type": "short_story",
        ...     "genre": "fantasy"
        ... })
    """
    sentry_sdk.set_context(key, value)


def set_tag(key: str, value: str) -> None:
    """
    Set tag for Sentry events.
    Tags are searchable in Sentry UI.

    Args:
        key: Tag key
        value: Tag value

    Example:
        >>> set_tag("production_type", "short_story")
        >>> set_tag("agent_id", "a06_sequential_generator")
    """
    sentry_sdk.set_tag(key, value)


def set_user(user_id: Optional[str] = None, **kwargs) -> None:
    """
    Set user information for Sentry events.

    Args:
        user_id: User ID
        **kwargs: Additional user info (email, username, etc.)

    Example:
        >>> set_user(
        ...     user_id="user_123",
        ...     email="user@example.com",
        ...     username="john_doe"
        ... )
    """
    user_data = {}
    if user_id:
        user_data["id"] = user_id
    user_data.update(kwargs)
    sentry_sdk.set_user(user_data)


def capture_exception(error: Exception, **kwargs) -> str:
    """
    Manually capture an exception and send to Sentry.

    Args:
        error: Exception to capture
        **kwargs: Additional context (tags, extras, etc.)

    Returns:
        Event ID

    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     event_id = capture_exception(
        ...         e,
        ...         tags={"agent_id": "a06"},
        ...         extras={"input_data": data}
        ...     )
    """
    # Set tags if provided
    if "tags" in kwargs:
        for key, value in kwargs["tags"].items():
            set_tag(key, value)

    # Set extras if provided
    if "extras" in kwargs:
        for key, value in kwargs["extras"].items():
            sentry_sdk.set_extra(key, value)

    return sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", **kwargs) -> str:
    """
    Manually capture a message and send to Sentry.

    Args:
        message: Message to capture
        level: Severity level (debug, info, warning, error, fatal)
        **kwargs: Additional context

    Returns:
        Event ID

    Example:
        >>> capture_message(
        ...     "Pipeline completed with warnings",
        ...     level="warning",
        ...     tags={"job_id": "job_123"}
        ... )
    """
    # Set tags if provided
    if "tags" in kwargs:
        for key, value in kwargs["tags"].items():
            set_tag(key, value)

    return sentry_sdk.capture_message(message, level=level)


class SentryTransaction:
    """
    Context manager for Sentry performance monitoring.

    Example:
        >>> with SentryTransaction(
        ...     op="pipeline.execute",
        ...     name="short_story_generation",
        ...     description="Generate short story (fantasy)"
        ... ) as transaction:
        ...     # Your code here
        ...     transaction.set_tag("production_type", "short_story")
        ...     transaction.set_data("word_count", 5000)
    """

    def __init__(
        self,
        op: str,
        name: str,
        description: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize transaction.

        Args:
            op: Operation type (e.g., "pipeline.execute", "agent.run")
            name: Transaction name
            description: Optional description
            **kwargs: Additional transaction data
        """
        self.op = op
        self.name = name
        self.description = description
        self.kwargs = kwargs
        self.transaction = None

    def __enter__(self):
        """Start transaction."""
        self.transaction = sentry_sdk.start_transaction(
            op=self.op,
            name=self.name,
            description=self.description,
            **self.kwargs
        )
        self.transaction.__enter__()
        return self.transaction

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End transaction."""
        if self.transaction:
            self.transaction.__exit__(exc_type, exc_val, exc_tb)


class SentrySpan:
    """
    Context manager for Sentry spans (sub-operations).

    Example:
        >>> with SentryTransaction(...) as transaction:
        ...     with SentrySpan(op="agent.execute", description="Run agent A06"):
        ...         # Agent execution code
        ...         pass
    """

    def __init__(self, op: str, description: Optional[str] = None, **kwargs):
        """
        Initialize span.

        Args:
            op: Operation type
            description: Optional description
            **kwargs: Additional span data
        """
        self.op = op
        self.description = description
        self.kwargs = kwargs
        self.span = None

    def __enter__(self):
        """Start span."""
        self.span = sentry_sdk.start_span(
            op=self.op,
            description=self.description,
            **self.kwargs
        )
        self.span.__enter__()
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End span."""
        if self.span:
            self.span.__exit__(exc_type, exc_val, exc_tb)


def add_breadcrumb(
    message: str,
    category: str = "default",
    level: str = "info",
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Add breadcrumb (trail of events leading to error).

    Args:
        message: Breadcrumb message
        category: Category (e.g., "pipeline", "agent", "api")
        level: Severity level
        data: Additional data

    Example:
        >>> add_breadcrumb(
        ...     message="Starting pipeline execution",
        ...     category="pipeline",
        ...     level="info",
        ...     data={"production_type": "short_story"}
        ... )
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {},
    )


__all__ = [
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
