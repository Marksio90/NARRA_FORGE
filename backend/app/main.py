"""
Main FastAPI application for NarraForge
Autonomous book generation platform with multi-agent orchestration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.config import settings
from app.database import init_db
from app.api import projects, health
from app.api import auth, payments, series, publishing
from app.api import mirix  # MIRIX Memory System - NarraForge 3.0
from app.api import emotional  # Emotional Resonance Engine - NarraForge 3.0
from app.api import dialogue  # Advanced Dialogue System - NarraForge 3.0
from app.api import consciousness  # Character Consciousness - NarraForge 3.0
from app.api import style  # Style Adaptation Engine - NarraForge 3.0
from app.api import pacing  # Predictive Pacing Algorithm - NarraForge 3.0
from app.api import illustrations  # AI Illustrations - NarraForge 3.0 Phase 2
from app.api import audiobook  # AI Audiobook Generator - NarraForge 3.0 Phase 2
from app.api import covers  # AI Cover Art - NarraForge 3.0 Phase 2

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-Agentowa Platforma do Tworzenia Pełnometrażowych Książek",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"Shutting down {settings.APP_NAME}")


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(
    projects.router,
    prefix=f"{settings.API_V1_PREFIX}/projects",
    tags=["Projects"]
)
app.include_router(
    auth.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Authentication"]
)
app.include_router(
    payments.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Payments"]
)
app.include_router(
    series.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Series"]
)
app.include_router(
    publishing.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Publishing"]
)

# MIRIX Memory System - NarraForge 3.0
app.include_router(
    mirix.router,
    prefix=settings.API_V1_PREFIX,
    tags=["MIRIX Memory"]
)

# Emotional Resonance Engine - NarraForge 3.0
app.include_router(
    emotional.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Emotional Resonance"]
)

# Advanced Dialogue System - NarraForge 3.0
app.include_router(
    dialogue.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Advanced Dialogue"]
)

# Character Consciousness Simulation - NarraForge 3.0
app.include_router(
    consciousness.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Character Consciousness"]
)

# Style Adaptation Engine - NarraForge 3.0
app.include_router(
    style.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Style Adaptation"]
)

# Predictive Pacing Algorithm - NarraForge 3.0
app.include_router(
    pacing.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Predictive Pacing"]
)

# AI Illustrations - NarraForge 3.0 Phase 2
app.include_router(
    illustrations.router,
    prefix=settings.API_V1_PREFIX,
    tags=["AI Illustrations"]
)

# AI Audiobook Generator - NarraForge 3.0 Phase 2
app.include_router(
    audiobook.router,
    prefix=settings.API_V1_PREFIX,
    tags=["AI Audiobook"]
)

# AI Cover Art - NarraForge 3.0 Phase 2
app.include_router(
    covers.router,
    prefix=settings.API_V1_PREFIX,
    tags=["AI Cover Art"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Autonomiczna Kuźnia Literacka - Gdzie AI staje się Autorem",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
