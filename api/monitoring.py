"""
Performance Monitoring and Metrics.

Provides Prometheus metrics, performance tracking, and monitoring utilities.
"""

import time
from typing import Callable
from functools import wraps

from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware

from api.config import settings


# Prometheus metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests in progress',
    ['method', 'endpoint']
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query latency',
    ['operation']
)

celery_task_duration_seconds = Histogram(
    'celery_task_duration_seconds',
    'Celery task execution time',
    ['task_name']
)

celery_task_status = Counter(
    'celery_task_status',
    'Celery task status',
    ['task_name', 'status']
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

narrative_generation_total = Counter(
    'narrative_generation_total',
    'Total narratives generated',
    ['status']
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics for HTTP requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        if not settings.enable_metrics:
            return await call_next(request)

        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        path = request.url.path

        # Track request in progress
        http_requests_in_progress.labels(method=method, endpoint=path).inc()

        # Track request duration
        start_time = time.time()

        try:
            response = await call_next(request)
            status = response.status_code

            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status=status
            ).inc()

            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method,
                endpoint=path
            ).observe(duration)

            return response

        finally:
            http_requests_in_progress.labels(method=method, endpoint=path).dec()


def track_db_query(operation: str):
    """
    Decorator to track database query performance.

    Args:
        operation: Name of the database operation
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                database_query_duration_seconds.labels(
                    operation=operation
                ).observe(duration)
        return wrapper
    return decorator


def track_celery_task(task_name: str):
    """
    Decorator to track Celery task performance.

    Args:
        task_name: Name of the Celery task
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "failure"
                raise e
            finally:
                duration = time.time() - start_time
                celery_task_duration_seconds.labels(
                    task_name=task_name
                ).observe(duration)
                celery_task_status.labels(
                    task_name=task_name,
                    status=status
                ).inc()

        return wrapper
    return decorator


async def metrics_endpoint():
    """
    Prometheus metrics endpoint.

    Returns:
        Response: Prometheus metrics in text format
    """
    from fastapi.responses import Response

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
