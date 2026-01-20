"""
Project service - core business logic for project management
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from app.models.project import Project, ProjectStatus, GenreType
from app.models.world_bible import WorldBible
from app.models.character import Character
from app.models.plot_structure import PlotStructure
from app.models.chapter import Chapter
from app.schemas.project import ProjectCreate, ProjectSimulation
from app.config import settings, genre_config, model_tier_config

logger = logging.getLogger(__name__)


def create_project(db: Session, project_data: ProjectCreate) -> Project:
    """
    Create a new project
    
    User provides ONLY genre.
    AI will decide everything else in the simulation step.
    """
    # Generate default name if not provided
    name = project_data.name or f"{project_data.genre.value.title()} Story - {datetime.now().strftime('%Y%m%d_%H%M')}"
    
    project = Project(
        name=name,
        genre=GenreType(project_data.genre.value),
        status=ProjectStatus.INITIALIZING,
        parameters={},  # Will be filled by AI in simulation
        estimated_cost=0.0,
        actual_cost=0.0,
        current_step=0,
        progress_percentage=0.0,
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)

    logger.info(f"Created project {project.id}: {project.name} ({project.genre})")

    return project


def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    """Get list of projects with pagination"""
    return db.query(Project).order_by(Project.created_at.desc()).offset(skip).limit(limit).all()


def count_projects(db: Session) -> int:
    """Count total projects"""
    return db.query(Project).count()


def get_project(db: Session, project_id: int) -> Optional[Project]:
    """Get project by ID"""
    return db.query(Project).filter(Project.id == project_id).first()


async def simulate_generation(db: Session, project: Project) -> ProjectSimulation:
    """
    INTELLIGENT SIMULATION - AI decides ALL parameters

    Based on genre, AI determines:
    - Target word count (e.g., 85,000 - 120,000 words)
    - Number of chapters (e.g., 25-35)
    - Main character count (e.g., 4-7)
    - Supporting character count (e.g., 8-15)
    - Subplot count (e.g., 2-4)
    - World detail level (high/medium for genre)
    - Structure type (Hero's Journey, 7-Point, etc.)

    Then calculates cost for each of 15 steps based on:
    - Complexity of step
    - Model tier required
    - Estimated token usage
    """
    logger.info(f"Running intelligent simulation for project {project.id}")

    # Update status to SIMULATING
    project.status = ProjectStatus.SIMULATING
    db.commit()
    
    # Get genre-specific config
    genre_cfg = genre_config.get_genre_config(project.genre.value)
    
    # AI DECISIONS (in production, this would call GPT-4o-mini for intelligent decisions)
    # For now, using intelligent defaults based on genre
    
    # Determine word count based on genre defaults
    word_count_ranges = {
        "sci-fi": (85000, 120000),
        "fantasy": (95000, 140000),
        "thriller": (70000, 90000),
        "horror": (70000, 90000),
        "romance": (70000, 90000),
        "drama": (80000, 100000),
        "comedy": (70000, 85000),
        "mystery": (70000, 90000),
    }
    
    min_words, max_words = word_count_ranges.get(project.genre.value, (80000, 100000))
    target_word_count = (min_words + max_words) // 2
    
    # Calculate chapter count (avg 3000-4000 words per chapter)
    avg_words_per_chapter = 3500
    chapter_count = target_word_count // avg_words_per_chapter
    
    # Character counts by genre
    main_char_count = 5 if project.genre.value in ["fantasy", "sci-fi"] else 4
    supporting_count = 12 if project.genre.value in ["fantasy", "sci-fi"] else 8
    minor_count = 20 if project.genre.value in ["fantasy", "sci-fi"] else 15
    
    # Subplot count
    subplot_count = 3 if project.genre.value in ["fantasy", "thriller"] else 2
    
    # World detail
    world_detail = "high" if project.genre.value in ["fantasy", "sci-fi"] else "medium"
    
    # AI-determined parameters
    ai_decisions = {
        "target_word_count": target_word_count,
        "planned_volumes": 1,
        "chapter_count": chapter_count,
        "main_characters": main_char_count,
        "supporting_characters": supporting_count,
        "minor_characters": minor_count,
        "subplot_count": subplot_count,
        "world_detail_level": world_detail,
        "structure_type": genre_cfg["structure"],
        "style_guidelines": genre_cfg["style"],
    }
    
    # Save parameters to project
    project.parameters = ai_decisions
    db.commit()
    
    # Calculate cost for each step
    estimated_steps = _calculate_step_costs(ai_decisions, project.genre.value)
    
    # Total cost and duration
    total_cost = sum(step["estimated_cost"] for step in estimated_steps)
    total_duration = sum(step["estimated_duration_minutes"] for step in estimated_steps)
    
    project.estimated_cost = total_cost
    db.commit()
    
    simulation = ProjectSimulation(
        estimated_steps=estimated_steps,
        estimated_total_cost=total_cost,
        estimated_duration_minutes=total_duration,
        ai_decisions=ai_decisions
    )
    
    logger.info(f"Simulation complete for project {project.id}: ${total_cost:.2f}, {total_duration} min")
    
    return simulation


def _calculate_step_costs(ai_decisions: dict, genre: str) -> List[dict]:
    """
    Calculate estimated cost and duration for each of 15 pipeline steps
    
    Uses model tier config to determine which model for each step,
    then estimates token usage and calculates cost.
    """
    steps = [
        {
            "step": 1,
            "name": "Inicjalizacja Projektu",
            "task_type": "initialization",
            "estimated_tokens_in": 500,
            "estimated_tokens_out": 200,
        },
        {
            "step": 2,
            "name": "Parametryzacja (AI)",
            "task_type": "initialization",
            "estimated_tokens_in": 1000,
            "estimated_tokens_out": 500,
        },
        {
            "step": 3,
            "name": "Generowanie World Bible",
            "task_type": "world_building",
            "estimated_tokens_in": 2000,
            "estimated_tokens_out": 4000,
        },
        {
            "step": 4,
            "name": "Kreacja Postaci Głównych",
            "task_type": "character_creation",
            "estimated_tokens_in": 1500,
            "estimated_tokens_out": 3000 * ai_decisions.get("main_characters", 5),
        },
        {
            "step": 5,
            "name": "Kreacja Postaci Pobocznych",
            "task_type": "character_creation",
            "estimated_tokens_in": 1000,
            "estimated_tokens_out": 1500 * ai_decisions.get("supporting_characters", 10),
        },
        {
            "step": 6,
            "name": "Projektowanie Głównej Osi Fabularnej",
            "task_type": "plot_structure",
            "estimated_tokens_in": 3000,
            "estimated_tokens_out": 5000,
        },
        {
            "step": 7,
            "name": "Projektowanie Wątków Pobocznych",
            "task_type": "plot_structure",
            "estimated_tokens_in": 2000,
            "estimated_tokens_out": 3000 * ai_decisions.get("subplot_count", 3),
        },
        {
            "step": 8,
            "name": "Chapter Breakdown",
            "task_type": "plot_structure",
            "estimated_tokens_in": 2500,
            "estimated_tokens_out": 500 * ai_decisions.get("chapter_count", 25),
        },
        {
            "step": 9,
            "name": "Scene Detailing",
            "task_type": "simple_outline",
            "estimated_tokens_in": 2000,
            "estimated_tokens_out": 300 * ai_decisions.get("chapter_count", 25) * 3,  # ~3 scenes per chapter
        },
        {
            "step": 10,
            "name": "Pre-Writing Validation",
            "task_type": "validation",
            "estimated_tokens_in": 5000,
            "estimated_tokens_out": 2000,
        },
        {
            "step": 11,
            "name": "Prose Generation - Wszystkie Rozdziały",
            "task_type": "prose_writing",
            "estimated_tokens_in": 2000 * ai_decisions.get("chapter_count", 25),  # Context per chapter
            "estimated_tokens_out": (ai_decisions.get("target_word_count", 90000) / 0.75),  # Words to tokens ~1.33
        },
        {
            "step": 12,
            "name": "Continuity Check (wszystkie rozdziały)",
            "task_type": "validation",
            "estimated_tokens_in": 10000 * ai_decisions.get("chapter_count", 25) // 5,  # Sample checking
            "estimated_tokens_out": 500 * ai_decisions.get("chapter_count", 25),
        },
        {
            "step": 13,
            "name": "Style Polishing (wszystkie rozdziały)",
            "task_type": "style_polish",
            "estimated_tokens_in": (ai_decisions.get("target_word_count", 90000) / 0.75) * 1.1,
            "estimated_tokens_out": (ai_decisions.get("target_word_count", 90000) / 0.75) * 0.3,
        },
        {
            "step": 14,
            "name": "Genre Compliance Audit",
            "task_type": "validation",
            "estimated_tokens_in": 15000,
            "estimated_tokens_out": 3000,
        },
        {
            "step": 15,
            "name": "Final Assembly & Export",
            "task_type": "formatting",
            "estimated_tokens_in": 2000,
            "estimated_tokens_out": 1000,
        },
    ]
    
    estimated_steps = []
    
    for step_data in steps:
        # Determine model tier
        tier = model_tier_config.get_tier_for_task(step_data["task_type"])
        
        # Get model costs
        if tier == 1:
            input_cost = settings.TIER1_INPUT_COST
            output_cost = settings.TIER1_OUTPUT_COST
            model_name = settings.GPT_4O_MINI
        elif tier == 2:
            input_cost = settings.TIER2_INPUT_COST
            output_cost = settings.TIER2_OUTPUT_COST
            model_name = settings.GPT_4O
        else:  # tier 3
            input_cost = settings.TIER3_INPUT_COST
            output_cost = settings.TIER3_OUTPUT_COST
            model_name = settings.GPT_4
        
        # Calculate cost
        cost = (
            (step_data["estimated_tokens_in"] / 1_000_000) * input_cost +
            (step_data["estimated_tokens_out"] / 1_000_000) * output_cost
        )
        
        # Estimate duration (rough approximation)
        # Tier 1: ~10k tokens/min, Tier 2: ~8k tokens/min, Tier 3: ~5k tokens/min
        tokens_per_min = {1: 10000, 2: 8000, 3: 5000}[tier]
        duration = max(1, int((step_data["estimated_tokens_in"] + step_data["estimated_tokens_out"]) / tokens_per_min))
        
        estimated_steps.append({
            "step": step_data["step"],
            "name": step_data["name"],
            "estimated_cost": round(cost, 4),
            "model_tier": f"tier{tier}",
            "model_name": model_name,
            "estimated_duration_minutes": duration,
            "description": f"Model: {model_name} | ~{step_data['estimated_tokens_out']//1000}K tokens output"
        })
    
    return estimated_steps


def start_generation_task(project_id: int) -> str:
    """
    Start the generation task in background (Celery)
    
    Returns task ID for tracking
    """
    # Import here to avoid circular dependency
    from app.tasks.generation_tasks import run_full_pipeline
    
    task = run_full_pipeline.delay(project_id)
    logger.info(f"Started generation task {task.id} for project {project_id}")
    
    return task.id


def get_project_status(db: Session, project: Project) -> dict:
    """
    Get real-time status of project generation
    """
    eta = None
    if project.started_at and project.estimated_cost > 0:
        # Rough ETA based on cost progress
        if project.actual_cost > 0:
            progress_ratio = project.actual_cost / project.estimated_cost
            # This is a simplified calculation
            eta = datetime.now() + timedelta(minutes=30)  # Placeholder
    
    return {
        "project_id": project.id,
        "status": project.status,
        "current_step": project.current_step,
        "total_steps": 15,
        "progress_percentage": project.progress_percentage,
        "current_activity": project.current_activity,
        "estimated_cost": project.estimated_cost,
        "actual_cost": project.actual_cost,
        "started_at": project.started_at,
        "estimated_completion": eta,
    }


def get_world_bible(db: Session, project_id: int) -> Optional[WorldBible]:
    """Get World Bible for project"""
    return db.query(WorldBible).filter(WorldBible.project_id == project_id).first()


def get_characters(db: Session, project_id: int) -> List[Character]:
    """Get all characters for project"""
    return db.query(Character).filter(Character.project_id == project_id).all()


def get_character(db: Session, character_id: int) -> Optional[Character]:
    """Get character by ID"""
    return db.query(Character).filter(Character.id == character_id).first()


def get_plot_structure(db: Session, project_id: int) -> Optional[PlotStructure]:
    """Get plot structure for project"""
    return db.query(PlotStructure).filter(PlotStructure.project_id == project_id).first()


def get_chapters(db: Session, project_id: int) -> List[Chapter]:
    """Get all chapters for project"""
    return db.query(Chapter).filter(Chapter.project_id == project_id).order_by(Chapter.number).all()


def get_chapter_by_number(db: Session, project_id: int, chapter_number: int) -> Optional[Chapter]:
    """Get specific chapter by number"""
    return db.query(Chapter).filter(
        Chapter.project_id == project_id,
        Chapter.number == chapter_number
    ).first()


async def export_project(db: Session, project_id: int, format: str) -> str:
    """
    Export project to specified format
    
    Returns path to exported file
    """
    # Import export service
    from app.services.export_service import export_to_format
    
    file_path = await export_to_format(db, project_id, format)
    logger.info(f"Exported project {project_id} to {format}: {file_path}")
    
    return file_path


def delete_project(db: Session, project_id: int):
    """Delete project and all associated data"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        db.delete(project)
        db.commit()
        logger.info(f"Deleted project {project_id}")
