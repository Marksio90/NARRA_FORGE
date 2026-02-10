"""
Main FastAPI application for NarraForge
Autonomous book generation platform with multi-agent orchestration
"""

from contextlib import asynccontextmanager
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
from app.api import trailer  # Book Trailer Generator - NarraForge 3.0 Phase 2
from app.api import interactive  # Interactive Reading - NarraForge 3.0 Phase 2
from app.api import soundtrack  # Ambient Soundtrack - NarraForge 3.0 Phase 2
from app.api import coherence  # QUANTUM Coherence Analyzer - NarraForge 3.0 Phase 3
from app.api import psychology  # Reader Psychology Engine - NarraForge 3.0 Phase 3
from app.api import cultural  # TITAN Cultural Intelligence - NarraForge 3.0 Phase 3
from app.api import complexity  # Dynamic Complexity Adjustment - NarraForge 3.0 Phase 3
from app.api import trends  # Trend-Adaptive Content - NarraForge 3.0 Phase 3
from app.api import multilanguage  # Multi-Language Generation - NarraForge 3.0 Phase 4
from app.api import collaborative  # Collaborative Writing - NarraForge 3.0 Phase 4
from app.api import coach  # AI Writing Coach - NarraForge 3.0 Phase 4
from app.api import platforms  # Publishing Integration - NarraForge 3.0 Phase 4
from app.api import analytics  # Analytics Dashboard - NarraForge 3.0 Phase 4
from app.api import gateway  # API Gateway - NarraForge 3.0 Phase 5
from app.api import orchestrator  # Service Orchestrator - NarraForge 3.0 Phase 5
from app.api import events  # Event Bus - NarraForge 3.0 Phase 5
from app.api import cache  # Cache Layer - NarraForge 3.0 Phase 5
from app.api import monitoring  # Monitoring & Health - NarraForge 3.0 Phase 5
from app.api import genre_blending  # Dynamic Genre Blending - NarraForge 3.0 Advanced
from app.api import theme_weaving  # Subconscious Theme Weaving - NarraForge 3.0 Advanced
from app.api import style_marketplace  # Style Marketplace - NarraForge 3.0 Advanced

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan handler (replaces deprecated on_event)"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-Agentowa Platforma do Tworzenia Pełnometrażowych Książek",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Configure CORS with explicit methods and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler - never leaks internals in production"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    content = {
        "success": False,
        "error": "Internal server error",
    }
    if settings.DEBUG:
        content["detail"] = str(exc)
    return JSONResponse(status_code=500, content=content)


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

# Book Trailer Generator - NarraForge 3.0 Phase 2
app.include_router(
    trailer.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Book Trailer"]
)

# Interactive Reading Experience - NarraForge 3.0 Phase 2
app.include_router(
    interactive.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Interactive Reading"]
)

# Ambient Soundtrack Generator - NarraForge 3.0 Phase 2
app.include_router(
    soundtrack.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Ambient Soundtrack"]
)

# QUANTUM Narrative Coherence Analyzer - NarraForge 3.0 Phase 3
app.include_router(
    coherence.router,
    prefix=settings.API_V1_PREFIX,
    tags=["QUANTUM Coherence"]
)

# Predictive Reader Psychology Engine - NarraForge 3.0 Phase 3
app.include_router(
    psychology.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Reader Psychology"]
)

# TITAN Cultural Intelligence System - NarraForge 3.0 Phase 3
app.include_router(
    cultural.router,
    prefix=settings.API_V1_PREFIX,
    tags=["TITAN Cultural Intelligence"]
)

# Dynamic Complexity Adjustment - NarraForge 3.0 Phase 3
app.include_router(
    complexity.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Dynamic Complexity"]
)

# Trend-Adaptive Content Generation - NarraForge 3.0 Phase 3
app.include_router(
    trends.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Trend-Adaptive"]
)

# Multi-Language Generation - NarraForge 3.0 Phase 4
app.include_router(
    multilanguage.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Multi-Language"]
)

# Collaborative Writing Tools - NarraForge 3.0 Phase 4
app.include_router(
    collaborative.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Collaborative Writing"]
)

# AI Writing Coach - NarraForge 3.0 Phase 4
app.include_router(
    coach.router,
    prefix=settings.API_V1_PREFIX,
    tags=["AI Writing Coach"]
)

# Publishing Platform Integration - NarraForge 3.0 Phase 4
app.include_router(
    platforms.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Publishing Platforms"]
)

# Analytics Dashboard - NarraForge 3.0 Phase 4
app.include_router(
    analytics.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Analytics"]
)

# API Gateway - NarraForge 3.0 Phase 5
app.include_router(
    gateway.router,
    prefix=settings.API_V1_PREFIX,
    tags=["API Gateway"]
)

# Service Orchestrator - NarraForge 3.0 Phase 5
app.include_router(
    orchestrator.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Service Orchestrator"]
)

# Event Bus - NarraForge 3.0 Phase 5
app.include_router(
    events.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Event Bus"]
)

# Cache Layer - NarraForge 3.0 Phase 5
app.include_router(
    cache.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Cache"]
)

# Monitoring & Health - NarraForge 3.0 Phase 5
app.include_router(
    monitoring.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Monitoring"]
)

# Dynamic Genre Blending - NarraForge 3.0 Advanced
app.include_router(
    genre_blending.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Genre Blending"]
)

# Subconscious Theme Weaving - NarraForge 3.0 Advanced
app.include_router(
    theme_weaving.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Theme Weaving"]
)

# Style Marketplace - NarraForge 3.0 Advanced
app.include_router(
    style_marketplace.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Style Marketplace"]
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
