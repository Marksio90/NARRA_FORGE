"""
Book Trailer API - NarraForge 3.0 Phase 2

Endpoints for automatic book trailer generation.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.trailer_generator import (
    get_trailer_generator,
    TrailerStyle,
    TrailerDuration,
    VideoFormat
)
from app.models.project import GenreType

router = APIRouter(prefix="/trailer", tags=["Book Trailer"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class GenerateScriptRequest(BaseModel):
    """Request for generating trailer script"""
    title: str
    author: str
    genre: str
    book_summary: str
    key_scenes: Optional[List[str]] = None
    duration: str = "medium"
    style: Optional[str] = None


class CreateProjectRequest(BaseModel):
    """Request for creating trailer project"""
    script_id: str
    output_format: str = "mp4_1080p"
    generate_assets: bool = True


class EstimateCostRequest(BaseModel):
    """Request for cost estimation"""
    num_scenes: int
    with_narration: bool = True
    duration: str = "medium"


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/styles")
async def get_trailer_styles() -> Dict[str, Any]:
    """Get all trailer styles"""
    return {
        "styles": [
            {"style": "cinematic", "pl": "Kinowy", "description": "Epickie, filmowe ujęcia"},
            {"style": "mysterious", "pl": "Tajemniczy", "description": "Budujący napięcie"},
            {"style": "romantic", "pl": "Romantyczny", "description": "Emocjonalny, ciepły"},
            {"style": "action", "pl": "Akcji", "description": "Dynamiczny, szybki montaż"},
            {"style": "dramatic", "pl": "Dramatyczny", "description": "Intensywny, emocjonalny"},
            {"style": "whimsical", "pl": "Baśniowy", "description": "Lekki, magiczny"},
            {"style": "dark", "pl": "Mroczny", "description": "Ciemny, niepokojący"},
            {"style": "epic", "pl": "Epicki", "description": "Wielki rozmach"}
        ]
    }


@router.get("/durations")
async def get_trailer_durations() -> Dict[str, Any]:
    """Get trailer duration options"""
    return {
        "durations": [
            {"duration": "short", "seconds": 30, "scenes": 4, "description": "Krótki teaser"},
            {"duration": "medium", "seconds": 60, "scenes": 7, "description": "Standardowy trailer"},
            {"duration": "long", "seconds": 90, "scenes": 10, "description": "Rozszerzony trailer"},
            {"duration": "extended", "seconds": 120, "scenes": 14, "description": "Pełny trailer"}
        ]
    }


@router.get("/formats")
async def get_video_formats() -> Dict[str, Any]:
    """Get video output formats"""
    return {
        "formats": [
            {"format": "mp4_1080p", "resolution": "1920x1080", "description": "Full HD"},
            {"format": "mp4_4k", "resolution": "3840x2160", "description": "4K Ultra HD"},
            {"format": "webm", "resolution": "1920x1080", "description": "Web format"},
            {"format": "gif", "resolution": "800x450", "description": "Animated GIF"},
            {"format": "vertical", "resolution": "1080x1920", "description": "Social media (9:16)"}
        ]
    }


@router.get("/genre-profiles/{genre}")
async def get_genre_profile(genre: str) -> Dict[str, Any]:
    """Get trailer profile for a genre"""
    from app.services.trailer_generator import GENRE_TRAILER_PROFILES

    try:
        genre_type = GenreType(genre.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid genre: {genre}")

    profile = GENRE_TRAILER_PROFILES.get(genre_type, {})

    return {
        "genre": genre,
        "style": profile.get("style", TrailerStyle.CINEMATIC).value,
        "music_mood": profile.get("music_mood", ""),
        "pacing": profile.get("pacing", ""),
        "typical_scenes": profile.get("typical_scenes", []),
        "text_style": profile.get("text_style", "")
    }


@router.post("/script/generate")
async def generate_script(request: GenerateScriptRequest) -> Dict[str, Any]:
    """
    Generate a trailer script from book information.

    Returns a complete script with scenes, narration, and timings.
    """
    generator = get_trailer_generator()

    try:
        genre = GenreType(request.genre.upper())
    except ValueError:
        genre = GenreType.DRAMA

    try:
        duration = TrailerDuration(request.duration)
    except ValueError:
        duration = TrailerDuration.MEDIUM

    style = None
    if request.style:
        try:
            style = TrailerStyle(request.style)
        except ValueError:
            pass

    script = await generator.generate_trailer_script(
        title=request.title,
        author=request.author,
        genre=genre,
        book_summary=request.book_summary,
        key_scenes=request.key_scenes,
        duration=duration,
        style=style
    )

    return {
        "success": True,
        "script": script.to_dict()
    }


@router.get("/script/{script_id}")
async def get_script(script_id: str) -> Dict[str, Any]:
    """Get a specific trailer script"""
    generator = get_trailer_generator()
    script = generator.get_script(script_id)

    if not script:
        raise HTTPException(status_code=404, detail=f"Script not found: {script_id}")

    return {
        "script": script.to_dict()
    }


@router.post("/project/create")
async def create_project(request: CreateProjectRequest) -> Dict[str, Any]:
    """
    Create a trailer project and optionally generate assets.
    """
    generator = get_trailer_generator()

    script = generator.get_script(request.script_id)
    if not script:
        raise HTTPException(status_code=404, detail=f"Script not found: {request.script_id}")

    try:
        output_format = VideoFormat(request.output_format)
    except ValueError:
        output_format = VideoFormat.MP4_1080P

    project = await generator.create_trailer_project(
        script=script,
        output_format=output_format,
        generate_assets=request.generate_assets
    )

    return {
        "success": True,
        "project": project.to_dict()
    }


@router.get("/project/{project_id}")
async def get_project(project_id: str) -> Dict[str, Any]:
    """Get a specific trailer project"""
    generator = get_trailer_generator()
    project = generator.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")

    return {
        "project": project.to_dict()
    }


@router.post("/estimate")
async def estimate_cost(request: EstimateCostRequest) -> Dict[str, Any]:
    """Estimate cost for trailer generation"""
    generator = get_trailer_generator()

    try:
        duration = TrailerDuration(request.duration)
    except ValueError:
        duration = TrailerDuration.MEDIUM

    estimate = await generator.estimate_trailer_cost(
        num_scenes=request.num_scenes,
        with_narration=request.with_narration,
        duration=duration
    )

    return {
        "success": True,
        "estimate": estimate
    }


@router.get("/scripts")
async def list_scripts() -> Dict[str, Any]:
    """List all trailer scripts"""
    generator = get_trailer_generator()
    return {"scripts": generator.list_scripts()}


@router.get("/projects")
async def list_projects() -> Dict[str, Any]:
    """List all trailer projects"""
    generator = get_trailer_generator()
    return {"projects": generator.list_projects()}
