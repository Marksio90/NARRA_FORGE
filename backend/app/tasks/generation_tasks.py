"""
Celery tasks for book generation pipeline
"""

from celery import Task
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.project import Project, ProjectStatus

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
    """
    db = self.db
    
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"success": False, "error": "Project not found"}
        
        project.status = ProjectStatus.GENERATING
        project.started_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Starting pipeline for project {project_id}")
        
        # Pipeline steps would be implemented here
        # For now, basic structure
        
        return {"success": True, "project_id": project_id}
    
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
