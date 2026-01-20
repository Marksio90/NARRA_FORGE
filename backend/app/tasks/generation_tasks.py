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

    MOCK IMPLEMENTATION - demonstrates progress tracking
    In production, this would call actual AI models for each step
    """
    import time

    db = self.db

    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"success": False, "error": "Project not found"}

        project.status = ProjectStatus.GENERATING
        project.started_at = datetime.utcnow()
        db.commit()

        logger.info(f"Starting MOCK pipeline for project {project_id}: {project.name}")

        # 15-step pipeline (matching the simulation steps)
        # DEMO MODE: Using shorter durations for testing (3-5 seconds per step)
        # In production, these would be much longer (minutes to hours)
        pipeline_steps = [
            {"step": 1, "name": "Inicjalizacja Projektu", "duration": 3},
            {"step": 2, "name": "Analiza Gatunku i Parametrów", "duration": 4},
            {"step": 3, "name": "Kreacja Głównych Bohaterów", "duration": 5},
            {"step": 4, "name": "Kreacja Bohaterów Drugoplanowych", "duration": 4},
            {"step": 5, "name": "Projektowanie Świata", "duration": 5},
            {"step": 6, "name": "Struktura Fabuły", "duration": 4},
            {"step": 7, "name": "Szczegółowy Zarys Rozdziałów", "duration": 5},
            {"step": 8, "name": "Generowanie Rozdziału 1-5", "duration": 5},
            {"step": 9, "name": "Generowanie Rozdziału 6-10", "duration": 5},
            {"step": 10, "name": "Generowanie Rozdziału 11-15", "duration": 5},
            {"step": 11, "name": "Generowanie Rozdziału 16-20", "duration": 5},
            {"step": 12, "name": "Generowanie Rozdziału 21-25", "duration": 5},
            {"step": 13, "name": "Kontrola Spójności", "duration": 4},
            {"step": 14, "name": "Poprawa i Edycja", "duration": 4},
            {"step": 15, "name": "Finalizacja", "duration": 3},
        ]

        total_steps = len(pipeline_steps)

        for step_info in pipeline_steps:
            step_num = step_info["step"]
            step_name = step_info["name"]
            duration = step_info["duration"]

            # Update project status
            project.current_step = step_num
            project.progress_percentage = (step_num / total_steps) * 100
            project.current_activity = step_name
            db.commit()
            db.refresh(project)

            logger.info(f"Project {project_id} - Step {step_num}/15: {step_name}")

            # MOCK: Simulate work (in production, this would be actual AI generation)
            time.sleep(duration)

        # Mark as completed
        project.status = ProjectStatus.COMPLETED
        project.progress_percentage = 100.0
        project.current_step = 15
        project.current_activity = "Zakończone"
        project.completed_at = datetime.utcnow()
        db.commit()

        logger.info(f"MOCK pipeline completed for project {project_id}")

        return {"success": True, "project_id": project_id, "message": "MOCK generation completed"}

    except Exception as e:
        logger.error(f"Pipeline failed for project {project_id}: {e}", exc_info=True)

        # Mark project as failed
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.status = ProjectStatus.FAILED
                project.current_activity = f"Błąd: {str(e)}"
                db.commit()
        except:
            pass

        return {"success": False, "error": str(e)}
    finally:
        db.close()
