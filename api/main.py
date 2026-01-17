"""
NARRA_FORGE FastAPI Application.

Main application entry point for the API server.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api.config import settings
from api.middleware import setup_middleware
from api.models.base import async_engine, Base
from api.routes import health
from api.routes import auth, projects, jobs, narratives


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.sentry_environment}")
    print(f"Debug mode: {settings.debug}")

    # Create database tables (in development)
    if settings.debug:
        print("Creating database tables...")
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created")

    # TODO: Initialize Sentry
    # TODO: Initialize Redis connection pool
    # TODO: Initialize metrics server

    yield

    # Shutdown
    print(f"Shutting down {settings.app_name}")
    await async_engine.dispose()
    print("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url,
    lifespan=lifespan,
    debug=settings.debug,
)


# Setup middleware
setup_middleware(app)


# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(jobs.router)
app.include_router(narratives.router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    API root endpoint.

    Returns basic API information and available endpoints.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "docs": settings.docs_url,
        "health": "/health",
        "endpoints": {
            "auth": "/auth",
            "projects": "/projects",
            "jobs": "/jobs",
            "narratives": "/narratives",
        }
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.

    Args:
        request: FastAPI request
        exc: Exception that was raised

    Returns:
        JSONResponse: Error response
    """
    # Get request ID if available
    request_id = getattr(request.state, "request_id", "unknown")

    # Log error (TODO: integrate with Sentry)
    print(f"[ERROR] {request_id}: {type(exc).__name__}: {str(exc)}")

    # Return error response
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
            "error_type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="debug" if settings.debug else "info"
    )
