"""
Sentry Error Tracking Configuration.

Integrates Sentry for error monitoring and performance tracking.
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

from api.config import settings


def init_sentry():
    """
    Initialize Sentry SDK with FastAPI integration.

    Configures error tracking, performance monitoring, and integrations.
    """
    if not settings.enable_sentry or not settings.sentry_dsn:
        print("Sentry disabled or DSN not configured")
        return

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        traces_sample_rate=settings.sentry_traces_sample_rate,

        # Integrations
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
        ],

        # Performance monitoring
        enable_tracing=True,

        # Release tracking
        release=f"{settings.app_name}@{settings.app_version}",

        # Sampling
        profiles_sample_rate=0.1,  # 10% of transactions

        # Before send hook to filter sensitive data
        before_send=filter_sensitive_data,

        # Breadcrumbs
        max_breadcrumbs=50,

        # Attach stacktrace
        attach_stacktrace=True,
    )

    print(f"Sentry initialized for {settings.sentry_environment}")


def filter_sensitive_data(event, hint):
    """
    Filter sensitive data from Sentry events.

    Args:
        event: Sentry event dictionary
        hint: Additional context

    Returns:
        Modified event or None to drop event
    """
    # Remove sensitive headers
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]
        sensitive_headers = ["Authorization", "Cookie", "X-API-Key"]

        for header in sensitive_headers:
            if header in headers:
                headers[header] = "[Filtered]"

    # Remove sensitive query params
    if "request" in event and "query_string" in event["request"]:
        query = event["request"]["query_string"]
        if "password" in query.lower() or "token" in query.lower():
            event["request"]["query_string"] = "[Filtered]"

    # Remove sensitive data from extra context
    if "extra" in event:
        for key in list(event["extra"].keys()):
            if any(sensitive in key.lower() for sensitive in ["password", "secret", "token", "key"]):
                event["extra"][key] = "[Filtered]"

    return event


def capture_exception(exc: Exception, **kwargs):
    """
    Capture exception with Sentry.

    Args:
        exc: Exception to capture
        **kwargs: Additional context
    """
    if settings.enable_sentry:
        sentry_sdk.capture_exception(exc, **kwargs)


def capture_message(message: str, level: str = "info", **kwargs):
    """
    Capture message with Sentry.

    Args:
        message: Message to capture
        level: Severity level (debug, info, warning, error, fatal)
        **kwargs: Additional context
    """
    if settings.enable_sentry:
        sentry_sdk.capture_message(message, level=level, **kwargs)


def set_user_context(user_id: str, email: str = None, **kwargs):
    """
    Set user context for Sentry events.

    Args:
        user_id: User ID
        email: User email
        **kwargs: Additional user data
    """
    if settings.enable_sentry:
        sentry_sdk.set_user({
            "id": user_id,
            "email": email,
            **kwargs
        })


def set_context(name: str, context: dict):
    """
    Set custom context for Sentry events.

    Args:
        name: Context name
        context: Context data dictionary
    """
    if settings.enable_sentry:
        sentry_sdk.set_context(name, context)
