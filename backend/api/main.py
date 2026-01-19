"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="NARRA FORGE - Autonomous Literary Production Platform",
)


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
