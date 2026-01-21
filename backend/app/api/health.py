"""
Health check endpoint for monitoring system status
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import settings
import redis
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive health check endpoint

    Returns:
    - Overall system health status
    - Database connectivity
    - Redis connectivity
    - API key configuration
    - Service availability
    """
    status = {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "services": {}
    }

    # Check database
    try:
        db.execute(text("SELECT 1"))
        status["services"]["database"] = {
            "status": "connected",
            "type": "postgresql"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        status["services"]["database"] = {
            "status": "disconnected",
            "error": str(e)
        }
        status["status"] = "unhealthy"

    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        status["services"]["redis"] = {
            "status": "connected",
            "used_for": "celery_broker"
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        status["services"]["redis"] = {
            "status": "disconnected",
            "error": str(e)
        }
        status["status"] = "degraded"

    # Check API key configuration (without exposing keys)
    openai_configured = bool(
        settings.OPENAI_API_KEY and
        settings.OPENAI_API_KEY != "sk-placeholder-add-your-key"
    )
    anthropic_configured = bool(
        hasattr(settings, 'ANTHROPIC_API_KEY') and
        settings.ANTHROPIC_API_KEY and
        settings.ANTHROPIC_API_KEY != "sk-placeholder-add-your-key"
    )

    status["services"]["openai"] = {
        "status": "configured" if openai_configured else "not_configured",
        "available": openai_configured,
        "required": True
    }

    status["services"]["anthropic"] = {
        "status": "configured" if anthropic_configured else "not_configured",
        "available": anthropic_configured,
        "required": False
    }

    # If OpenAI is not configured, mark as unhealthy
    if not openai_configured:
        status["status"] = "unhealthy"
        status["error"] = "OpenAI API key not configured (required for AI generation)"

    return status


@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check - is the system ready to process requests?

    Returns 200 if ready, shows issues if not ready
    """
    try:
        # Check database
        db.execute(text("SELECT 1"))

        # Check OpenAI configuration
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-placeholder-add-your-key":
            return {
                "ready": False,
                "reason": "OpenAI API key not configured"
            }

        # Check Redis
        try:
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
        except Exception as e:
            logger.error(f"Redis connection failed during readiness check: {e}")
            return {
                "ready": False,
                "reason": "Redis not available (required for background tasks)"
            }

        return {
            "ready": True,
            "message": "System is ready to process requests"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "ready": False,
            "reason": str(e)
        }


@router.get("/health/live")
async def liveness_check():
    """
    Liveness check - is the application running?

    Simple check that just returns 200 if the application is alive
    Used by orchestrators like Kubernetes to know if the app should be restarted
    """
    return {
        "alive": True,
        "message": "Application is running"
    }
