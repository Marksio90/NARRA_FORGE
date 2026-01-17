"""
Narrative generation Celery task.

Integrates NarraForge core pipeline with async Celery workers.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any

from celery import Task
from celery.exceptions import SoftTimeLimitExceeded
from sqlalchemy import select

from api.celery_app import celery_app
from api.models.base import AsyncSessionLocal
from api.models.job import GenerationJob, JobStatus
from api.models.narrative import Narrative
from api.models.user import User
from api.models.project import Project

# Import NarraForge core components
from narra_forge.core.types import ProductionBrief, ProductionType, Genre
from narra_forge.core.orchestrator import Orchestrator
from narra_forge.memory.storage import MemoryStore


class NarrativeGenerationTask(Task):
    """Custom Celery task with progress tracking."""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        job_id = args[0] if args else kwargs.get('job_id')
        if job_id:
            asyncio.run(self._mark_job_failed(job_id, str(exc)))
    
    async def _mark_job_failed(self, job_id: str, error_message: str):
        """Mark job as failed in database."""
        async with AsyncSessionLocal() as db:
            stmt = select(GenerationJob).where(GenerationJob.id == job_id)
            result = await db.execute(stmt)
            job = result.scalar_one_or_none()
            
            if job:
                job.status = JobStatus.FAILED
                job.error_message = error_message
                job.completed_at = datetime.utcnow()
                
                if job.started_at:
                    duration = (job.completed_at - job.started_at).total_seconds()
                    job.duration_seconds = int(duration)
                
                await db.commit()


@celery_app.task(
    bind=True,
    base=NarrativeGenerationTask,
    name="api.tasks.narrative.generate_narrative",
    max_retries=3,
    default_retry_delay=60
)
def generate_narrative_task(self, job_id: str) -> Dict[str, Any]:
    """
    Generate narrative using NarraForge pipeline.
    
    Args:
        job_id: GenerationJob ID from database
        
    Returns:
        Dict with narrative_id and status
        
    Raises:
        Exception: If generation fails
    """
    try:
        # Run async task
        return asyncio.run(_generate_narrative_async(self, job_id))
    
    except SoftTimeLimitExceeded:
        # Handle soft time limit (give task time to cleanup)
        asyncio.run(_handle_timeout(job_id))
        raise
    
    except Exception as e:
        # Retry on failure
        raise self.retry(exc=e)


async def _generate_narrative_async(task: Task, job_id: str) -> Dict[str, Any]:
    """
    Async narrative generation implementation.
    
    This function:
    1. Loads job from database
    2. Runs NarraForge pipeline
    3. Saves narrative to database
    4. Updates job status
    """
    async with AsyncSessionLocal() as db:
        # Load job
        stmt = select(GenerationJob).where(GenerationJob.id == job_id)
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Update job status to RUNNING
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        job.current_stage = "Initializing pipeline"
        job.progress_percentage = 0.0
        await db.commit()
        
        try:
            # Parse production brief from JSON
            brief_data = job.production_brief
            production_brief = ProductionBrief(
                production_type=ProductionType(brief_data["production_type"]),
                genre=Genre(brief_data["genre"]),
                subject=brief_data["subject"],
                style_instructions=brief_data.get("style_instructions"),
                character_count=brief_data.get("character_count"),
                target_length=brief_data.get("target_length", 5000)
            )
            
            # Initialize memory store (if world_id provided)
            memory_store = None
            if brief_data.get("world_id"):
                # TODO: Load world from memory system
                pass
            
            # Create orchestrator
            orchestrator = Orchestrator(
                brief=production_brief,
                memory_store=memory_store
            )
            
            # Progress callback
            async def update_progress(stage: str, progress: float):
                """Update job progress in database."""
                job.current_stage = stage
                job.progress_percentage = progress
                if stage not in job.completed_stages:
                    job.completed_stages.append(stage)
                await db.commit()
                
                # Update Celery task state
                task.update_state(
                    state="PROGRESS",
                    meta={
                        "stage": stage,
                        "progress": progress,
                        "job_id": job_id
                    }
                )
            
            # Run pipeline (synchronous - NarraForge is not async yet)
            await update_progress("Starting generation", 5.0)
            
            # Execute in thread pool to not block event loop
            from concurrent.futures import ThreadPoolExecutor
            import asyncio
            
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=1) as executor:
                narrative_output = await loop.run_in_executor(
                    executor,
                    orchestrator.run
                )
            
            await update_progress("Finalizing", 95.0)
            
            # Create Narrative record
            narrative = Narrative(
                id=str(uuid.uuid4()),
                user_id=job.user_id,
                project_id=job.project_id,
                job_id=job.id,
                title=brief_data.get("title", production_brief.subject),
                production_type=production_brief.production_type.value,
                genre=production_brief.genre.value,
                narrative_text=narrative_output.narrative_text,
                word_count=len(narrative_output.narrative_text.split()),
                narrative_metadata={
                    "characters": [c.dict() for c in narrative_output.characters] if narrative_output.characters else [],
                    "structure": narrative_output.structure.dict() if narrative_output.structure else {},
                    "segments": [s.dict() for s in narrative_output.segments] if narrative_output.segments else []
                },
                quality_metrics={
                    "coherence": narrative_output.coherence_score,
                    # Add other quality metrics if available
                },
                overall_quality_score=narrative_output.coherence_score,
                generation_cost_usd=orchestrator.total_cost,
                tokens_used=orchestrator.total_tokens,
                version=1
            )
            
            db.add(narrative)
            
            # Update job
            job.status = JobStatus.COMPLETED
            job.output = {
                "narrative_id": narrative.id,
                "word_count": narrative.word_count,
                "quality_score": narrative.overall_quality_score
            }
            job.actual_cost_usd = orchestrator.total_cost
            job.tokens_used = orchestrator.total_tokens
            job.completed_at = datetime.utcnow()
            job.duration_seconds = int((job.completed_at - job.started_at).total_seconds())
            job.progress_percentage = 100.0
            job.current_stage = "Completed"
            
            # Update project stats
            project_stmt = select(Project).where(Project.id == job.project_id)
            project_result = await db.execute(project_stmt)
            project = project_result.scalar_one_or_none()
            
            if project:
                project.narrative_count += 1
                project.total_word_count += narrative.word_count
                project.total_cost_usd += orchestrator.total_cost
            
            # Update user usage
            user_stmt = select(User).where(User.id == job.user_id)
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            
            if user:
                user.monthly_generations_used += 1
                user.monthly_cost_used_usd += orchestrator.total_cost
            
            await db.commit()
            await update_progress("Complete", 100.0)
            
            return {
                "status": "success",
                "narrative_id": narrative.id,
                "job_id": job.id,
                "word_count": narrative.word_count,
                "cost_usd": orchestrator.total_cost
            }
            
        except Exception as e:
            # Mark job as failed
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            
            if job.started_at:
                duration = (job.completed_at - job.started_at).total_seconds()
                job.duration_seconds = int(duration)
            
            await db.commit()
            raise


async def _handle_timeout(job_id: str):
    """Handle task timeout."""
    async with AsyncSessionLocal() as db:
        stmt = select(GenerationJob).where(GenerationJob.id == job_id)
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()
        
        if job:
            job.status = JobStatus.FAILED
            job.error_message = "Task timed out (exceeded time limit)"
            job.completed_at = datetime.utcnow()
            job.can_resume = True  # Allow resume from checkpoint
            
            if job.started_at:
                duration = (job.completed_at - job.started_at).total_seconds()
                job.duration_seconds = int(duration)
            
            await db.commit()


