"""FastAPI application entry point."""

import logging
import subprocess
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings

logger = logging.getLogger(__name__)

# Import routers after logging setup
from api.routers.jobs import router as jobs_router  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Run database migrations
    logger.info("Running database migrations...")
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True,
        )
        logger.info(f"Migrations completed: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Migration failed: {e.stderr}")
        # Don't fail startup - migrations might already be applied

    yield

    # Shutdown
    logger.info("Application shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="NARRA FORGE - Autonomous Literary Production Platform",
    lifespan=lifespan,
)

# CORS middleware for UI communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(jobs_router, prefix="/api/v1", tags=["jobs"])


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        },
    )


@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "message": "NARRA FORGE - Literary Production Platform",
            "version": settings.app_version,
            "docs": "/docs",
        },
    )
