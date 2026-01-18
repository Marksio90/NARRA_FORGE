"""
Custom FastAPI Middleware.

Provides request/response processing, logging, error handling, etc.
"""

import time
import uuid
from typing import Callable, Dict
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from api.config import settings


# Simple in-memory rate limiter (for production use Redis)
class RateLimiter:
    """Simple sliding window rate limiter."""

    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Check if request is allowed under rate limit.

        Args:
            key: Unique identifier (e.g., IP address or user ID)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            True if allowed, False if rate limited
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)

        # Remove old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key] if req_time > cutoff
        ]

        # Check limit
        if len(self.requests[key]) >= max_requests:
            return False

        # Add current request
        self.requests[key].append(now)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Add unique request ID to each request.

    Sets X-Request-ID header for request tracing.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with unique ID."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Add request timing information.

    Sets X-Process-Time header with request duration.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with timing."""
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.

    Protects API from abuse by limiting requests per IP address.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Get client IP (consider X-Forwarded-For for proxied requests)
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        # Different limits for different endpoints
        path = request.url.path
        if path.startswith("/auth"):
            max_requests = 5
            window = 60  # 5 requests per minute for auth
        else:
            max_requests = settings.rate_limit_per_minute
            window = 60

        # Check rate limit
        if not rate_limiter.is_allowed(client_ip, max_requests, window):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": window
                },
                headers={
                    "Retry-After": str(window),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0"
                }
            )

        response = await call_next(request)
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Global error handling middleware.

    Catches unhandled exceptions and returns proper error responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with error handling."""
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Log error (TODO: integrate with logging system)
            request_id = getattr(request.state, "request_id", "unknown")

            # TODO: Send to Sentry in production
            import traceback
            error_trace = traceback.format_exc()
            print(f"[ERROR] {request_id}: {type(exc).__name__}: {str(exc)}")
            print(f"[TRACE] {error_trace}")

            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "request_id": request_id,
                    "error_type": type(exc).__name__
                }
            )


def setup_cors(app) -> None:
    """
    Configure CORS middleware.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )


def setup_middleware(app) -> None:
    """
    Configure all middleware for the application.

    Args:
        app: FastAPI application instance
    """
    # Add custom middleware (in reverse order - they wrap each other)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RateLimitMiddleware)  # Rate limiting before request ID
    app.add_middleware(RequestIDMiddleware)

    # Add CORS
    setup_cors(app)
