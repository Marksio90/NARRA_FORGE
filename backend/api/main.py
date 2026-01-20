"""
FastAPI main application for NarraForge.

This module sets up:
- FastAPI app with CORS middleware
- Health check endpoint
- API routers
- Startup/shutdown events
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import get_settings
from core.logging import get_logger
from models.database import check_db_connection, init_db

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Lifespan context manager for startup and shutdown events.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    # Startup
    logger.info("Starting NarraForge API", environment=settings.ENVIRONMENT)

    # Initialize database
    try:
        logger.info("Initializing database connection")
        await init_db()
        db_healthy = await check_db_connection()
        if db_healthy:
            logger.info("Database connection established")
        else:
            logger.error("Database connection failed")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))

    yield

    # Shutdown
    logger.info("Shutting down NarraForge API")


# Create FastAPI app
app = FastAPI(
    title="NarraForge API",
    description="Multi-agent AI platform for autonomous book generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Health status and database connection status
    """
    db_healthy = await check_db_connection()

    return JSONResponse(
        status_code=200 if db_healthy else 503,
        content={
            "status": "healthy" if db_healthy else "unhealthy",
            "database": "connected" if db_healthy else "disconnected",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
        },
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.

    Returns:
        dict: Welcome message and API information
    """
    return {
        "message": "Welcome to NarraForge API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Register API routers
from api.routers import jobs, ws

app.include_router(jobs.router, prefix="/api", tags=["Jobs"])
app.include_router(ws.router, prefix="/api", tags=["WebSocket"])
