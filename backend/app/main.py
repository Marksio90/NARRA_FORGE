"""
NarraForge FastAPI application.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.routes import router
from app.api.websockets import ws_manager
from app.db.database import init_db
from app.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management."""
    # Startup
    logger.info("Starting NarraForge application...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down NarraForge application...")


app = FastAPI(
    title="NarraForge API",
    description="Kuźnia Bestsellerów AI - API do generowania profesjonalnych książek",
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "narraforge",
        "version": settings.VERSION
    }


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for live updates."""
    await ws_manager.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages if needed
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        ws_manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        ws_manager.disconnect(session_id)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "🔥 NarraForge API - Kuźnia Bestsellerów AI",
        "version": settings.VERSION,
        "docs": "/docs"
    }
