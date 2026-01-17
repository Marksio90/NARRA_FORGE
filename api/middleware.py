"""
Custom FastAPI Middleware.

Provides request/response processing, logging, error handling, etc.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from api.config import settings


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
    app.add_middleware(RequestIDMiddleware)

    # Add CORS
    setup_cors(app)
