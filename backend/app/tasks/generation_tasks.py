"""
Celery tasks for book generation pipeline

NOW WITH REAL AI AGENTS!
Uses the complete multi-agent system for professional book generation.
"""

from celery import Task
from sqlalchemy.orm import Session
import logging
import asyncio
from datetime import datetime

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.project import Project, ProjectStatus
from app.services.agent_orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session"""
    _db = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db


@celery_app.task(base=DatabaseTask, bind=True)
def run_full_pipeline(self, project_id: int):
    """
    Run the complete 15-step book generation pipeline

    NOW WITH REAL AI AGENTS - NOT A MOCK!

    This uses the complete multi-agent system:
    - World Builder Agent (creates rich, consistent worlds)
    - Character Creator Agent (psychologically deep characters)
    - Plot Architect Agent (compelling story structure)
    - Prose Writer Agent (publication-quality prose)
    - Quality Control Agent (professional validation)

    All powered by:
    - OpenAI (GPT-4o, GPT-4o-mini, GPT-4, o1)
    - Anthropic Claude (Opus 4.5, Sonnet 4.5)
    - Advanced prompt engineering
    - Real-time cost tracking
    - Professional writing frameworks
    """
    db = self.db

    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"success": False, "error": "Project not found"}

        logger.info(f"🚀 Starting AI-POWERED generation for project {project_id}: {project.name}")

        # Create orchestrator
        orchestrator = AgentOrchestrator(db, project)

        # Run async generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            report = loop.run_until_complete(
                orchestrator.generate_complete_book()
            )
        finally:
            loop.close()

        if report['success']:
            logger.info(
                f"✅ AI GENERATION COMPLETE for project {project_id}!\n"
                f"   📚 Generated: {report['statistics']['chapters']} chapters, "
                f"{report['statistics']['total_words']:,} words\n"
                f"   👥 Characters: {report['statistics']['characters']}\n"
                f"   💰 AI Cost: ${report['ai_metrics']['total_cost']:.2f}\n"
                f"   🤖 API Calls: {report['ai_metrics']['api_calls']}\n"
                f"   📊 Quality: {report['quality_scores']['average_chapter_quality']:.1f}/100"
            )

        return report

    except Exception as e:
        logger.error(f"❌ AI generation pipeline failed for project {project_id}: {e}", exc_info=True)

        # Mark project as failed
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.status = ProjectStatus.FAILED
                project.current_activity = f"Błąd AI: {str(e)}"
                db.commit()
        except:
            pass

        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
    finally:
        db.close()


# Legacy compatibility - old mock task removed
# All generation now uses real AI agents!
