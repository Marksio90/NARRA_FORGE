"""
Projects API endpoints
Main endpoints for project creation, management, and generation
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectListResponse,
    ProjectStatusResponse,
    ProjectSimulation,
)
from app.schemas.world_bible import WorldBibleResponse
from app.schemas.character import CharacterListResponse
from app.schemas.plot import PlotStructureResponse
from app.schemas.chapter import ChapterListResponse, ChapterContentResponse
from app.schemas.common import SuccessResponse
from app.services import project_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new book project
    
    USER CHOOSES ONLY THE GENRE!
    AI decides everything else:
    - Length (word count, chapter count)
    - World complexity
    - Number of characters
    - Subplot count
    - All creative decisions
    """
    logger.info(f"Creating new project with genre: {project_data.genre}")
    
    try:
        project = project_service.create_project(db, project_data)
        return project
    except Exception as e:
        logger.error(f"Failed to create project: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all projects with pagination
    """
    projects = project_service.get_projects(db, skip=skip, limit=limit)
    total = project_service.count_projects(db)
    
    return ProjectListResponse(projects=projects, total=total)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific project
    """
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


@router.post("/{project_id}/simulate", response_model=ProjectSimulation)
async def simulate_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    INTELLIGENT COST AND STEP SIMULATION
    
    Before starting generation, AI:
    1. Analyzes the genre requirements
    2. Decides on all parameters (length, characters, complexity)
    3. Calculates exact cost for each of 15 steps
    4. Estimates total time
    5. Shows user what will be created
    
    This is the "smart preview" before committing!
    """
    logger.info(f"Running intelligent simulation for project {project_id}")
    
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        simulation = await project_service.simulate_generation(db, project)
        return simulation
    except Exception as e:
        logger.error(f"Simulation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/start", response_model=SuccessResponse)
async def start_generation(
    project_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start the book generation pipeline
    
    Launches the full 15-step autonomous generation process.
    Runs in background via Celery.
    Use WebSocket or /status endpoint for progress updates.
    """
    logger.info(f"Starting generation for project {project_id}")
    
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status != "simulating":
        raise HTTPException(
            status_code=400,
            detail="Project must be in 'simulating' status. Run /simulate first."
        )
    
    try:
        # Launch generation task in background (Celery)
        task_id = project_service.start_generation_task(project_id)
        
        return SuccessResponse(
            message="Generation started successfully",
            data={"project_id": project_id, "task_id": task_id}
        )
    except Exception as e:
        logger.error(f"Failed to start generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/status", response_model=ProjectStatusResponse)
async def get_project_status(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get real-time generation status
    
    Returns:
    - Current step (1-15)
    - Progress percentage
    - Current activity description
    - Cost tracking
    - ETA
    """
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    status = project_service.get_project_status(db, project)
    return status


@router.get("/{project_id}/world", response_model=WorldBibleResponse)
async def get_world_bible(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the complete World Bible for the project
    
    Contains:
    - Geography and locations
    - History and timeline
    - Systems (magic/technology/economy)
    - Cultures and societies
    - Rules and physics
    - Glossary
    """
    world_bible = project_service.get_world_bible(db, project_id)
    if not world_bible:
        raise HTTPException(
            status_code=404,
            detail="World Bible not yet generated for this project"
        )
    
    return world_bible


@router.get("/{project_id}/characters", response_model=CharacterListResponse)
async def get_characters(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all characters for the project
    
    Includes main, supporting, and minor characters with:
    - Full psychological profiles
    - Character arcs
    - Voice guides
    - Relationships
    """
    characters = project_service.get_characters(db, project_id)
    return CharacterListResponse(characters=characters, total=len(characters))


@router.get("/{project_id}/plot", response_model=PlotStructureResponse)
async def get_plot_structure(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the complete plot structure
    
    Contains:
    - Act breakdown
    - Main conflict and stakes
    - Plot points
    - Subplots
    - Tension graph
    - Foreshadowing map
    """
    plot_structure = project_service.get_plot_structure(db, project_id)
    if not plot_structure:
        raise HTTPException(
            status_code=404,
            detail="Plot structure not yet generated for this project"
        )
    
    return plot_structure


@router.get("/{project_id}/chapters", response_model=ChapterListResponse)
async def get_chapters(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all chapters (summaries, no full content)
    """
    chapters = project_service.get_chapters(db, project_id)
    return ChapterListResponse(chapters=chapters, total=len(chapters))


@router.get("/{project_id}/chapters/{chapter_number}", response_model=ChapterContentResponse)
async def get_chapter_content(
    project_id: int,
    chapter_number: int,
    db: Session = Depends(get_db)
):
    """
    Get full content of a specific chapter
    """
    chapter = project_service.get_chapter_by_number(db, project_id, chapter_number)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    # Get POV character name if exists
    pov_name = None
    if chapter.pov_character_id:
        pov_char = project_service.get_character(db, chapter.pov_character_id)
        if pov_char:
            pov_name = pov_char.name
    
    return ChapterContentResponse(
        chapter=chapter,
        pov_character_name=pov_name
    )


@router.get("/{project_id}/export/{format}")
async def export_project(
    project_id: int,
    format: str,  # docx, epub, pdf, markdown
    db: Session = Depends(get_db)
):
    """
    Export the completed book to various formats

    Supported formats:
    - DOCX (Microsoft Word)
    - EPUB (E-book)
    - PDF (Portable Document)
    - Markdown (Plain text with formatting)

    Returns the file as a download (FileResponse)
    """
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Project must be completed before export"
        )

    valid_formats = ["docx", "epub", "pdf", "markdown"]
    if format not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}"
        )

    try:
        file_path = await project_service.export_project(db, project_id, format)

        # Return file as download response
        from fastapi.responses import FileResponse
        import os

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Export file not found")

        # Determine media type
        media_types = {
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "epub": "application/epub+zip",
            "pdf": "application/pdf",
            "markdown": "text/markdown"
        }

        filename = f"{project.name}.{format}"

        return FileResponse(
            path=file_path,
            media_type=media_types.get(format, "application/octet-stream"),
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a project and all associated data
    """
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        project_service.delete_project(db, project_id)
        return SuccessResponse(
            message="Project deleted successfully",
            data={"project_id": project_id}
        )
    except Exception as e:
        logger.error(f"Failed to delete project: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-titles", status_code=200)
async def suggest_improved_titles_endpoint(
    title: str,
    genre: str,
    db: Session = Depends(get_db)
):
    """
    AI-POWERED: Get improved title suggestions

    Takes user's title and returns AI-generated suggestions that:
    - Are clearer and more impactful
    - Work better with AI analysis
    - Have stronger hooks for world/character/plot generation

    Args:
        title: Original title from user
        genre: Book genre (fantasy, sci-fi, thriller, etc.)

    Returns:
        JSON with original issues, 3 improved suggestions, and recommendation
    """
    logger.info(f"🎯 Generating title suggestions for: '{title}' ({genre})")

    try:
        suggestions = await project_service.suggest_improved_titles(title, genre)
        return {
            "success": True,
            "data": suggestions
        }
    except Exception as e:
        logger.error(f"❌ Failed to generate title suggestions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
