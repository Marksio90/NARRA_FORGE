"""
Coherence API - NarraForge 3.0 Phase 3

Endpoints for QUANTUM Narrative Coherence Analyzer.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.quantum_coherence import (
    get_coherence_analyzer,
    AnalysisDepth,
    CoherenceType
)

router = APIRouter(prefix="/coherence", tags=["QUANTUM Coherence"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class AnalyzeStoryRequest(BaseModel):
    """Request for full story analysis"""
    project_id: str
    chapters: List[Dict[str, Any]]
    characters: List[Dict[str, Any]]
    world_info: Optional[Dict[str, Any]] = None
    depth: str = "standard"


class AnalyzeChapterRequest(BaseModel):
    """Request for chapter analysis"""
    chapter_text: str
    chapter_number: int
    previous_context: Optional[Dict[str, Any]] = None


class CheckChangeRequest(BaseModel):
    """Request for checking proposed changes"""
    current_text: str
    proposed_text: str
    chapter_number: int
    story_context: Dict[str, Any]


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/types")
async def get_coherence_types() -> Dict[str, Any]:
    """Get all coherence check types"""
    return {
        "types": [
            {"type": "plot", "pl": "Fabuła", "description": "Spójność wątków fabularnych"},
            {"type": "character", "pl": "Postacie", "description": "Spójność zachowań postaci"},
            {"type": "timeline", "pl": "Oś czasu", "description": "Spójność chronologiczna"},
            {"type": "worldbuilding", "pl": "Świat", "description": "Spójność zasad świata"},
            {"type": "theme", "pl": "Tematy", "description": "Spójność tematyczna"},
            {"type": "dialogue", "pl": "Dialog", "description": "Spójność głosów postaci"},
            {"type": "tone", "pl": "Ton", "description": "Spójność tonalna"},
            {"type": "causality", "pl": "Przyczynowość", "description": "Spójność przyczynowo-skutkowa"}
        ]
    }


@router.get("/depths")
async def get_analysis_depths() -> Dict[str, Any]:
    """Get available analysis depths"""
    return {
        "depths": [
            {"depth": "quick", "pl": "Szybka", "description": "Podstawowa analiza powierzchniowa"},
            {"depth": "standard", "pl": "Standardowa", "description": "Normalna analiza"},
            {"depth": "deep", "pl": "Głęboka", "description": "Dokładna analiza"},
            {"depth": "quantum", "pl": "QUANTUM", "description": "Maksymalna głębokość z krzyżowym odniesieniem"}
        ]
    }


@router.get("/severity-levels")
async def get_severity_levels() -> Dict[str, Any]:
    """Get issue severity levels"""
    return {
        "levels": [
            {"level": "critical", "pl": "Krytyczny", "description": "Łamie historię"},
            {"level": "major", "pl": "Poważny", "description": "Znacząca niespójność"},
            {"level": "moderate", "pl": "Umiarkowany", "description": "Zauważalna niespójność"},
            {"level": "minor", "pl": "Drobny", "description": "Mała niespójność"},
            {"level": "suggestion", "pl": "Sugestia", "description": "Można poprawić"}
        ]
    }


@router.post("/analyze-story")
async def analyze_story(request: AnalyzeStoryRequest) -> Dict[str, Any]:
    """
    Perform full coherence analysis on a story.

    Analyzes all aspects of narrative coherence across the entire book.
    """
    analyzer = get_coherence_analyzer()

    try:
        depth = AnalysisDepth(request.depth)
    except ValueError:
        depth = AnalysisDepth.STANDARD

    report = await analyzer.analyze_full_story(
        project_id=request.project_id,
        chapters=request.chapters,
        characters=request.characters,
        world_info=request.world_info,
        depth=depth
    )

    return {
        "success": True,
        "report": report.to_dict()
    }


@router.post("/analyze-chapter")
async def analyze_chapter(request: AnalyzeChapterRequest) -> Dict[str, Any]:
    """
    Analyze coherence of a single chapter.

    Can check against previous context for continuity.
    """
    analyzer = get_coherence_analyzer()

    result = await analyzer.analyze_chapter(
        chapter_text=request.chapter_text,
        chapter_number=request.chapter_number,
        previous_context=request.previous_context
    )

    return {
        "success": True,
        "analysis": result
    }


@router.post("/check-change")
async def check_proposed_change(request: CheckChangeRequest) -> Dict[str, Any]:
    """
    Check if a proposed change would introduce coherence issues.
    """
    analyzer = get_coherence_analyzer()

    result = await analyzer.check_proposed_change(
        current_text=request.current_text,
        proposed_text=request.proposed_text,
        chapter_number=request.chapter_number,
        story_context=request.story_context
    )

    return {
        "success": True,
        "check_result": result
    }


@router.get("/report/{report_id}")
async def get_report(report_id: str) -> Dict[str, Any]:
    """Get a coherence report by ID"""
    analyzer = get_coherence_analyzer()
    report = analyzer.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {"report": report.to_dict()}


@router.get("/issue/{issue_id}/fix")
async def get_fix_suggestion(issue_id: str) -> Dict[str, Any]:
    """Get fix suggestions for an issue"""
    analyzer = get_coherence_analyzer()
    result = await analyzer.suggest_fix(issue_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/reports")
async def list_reports(project_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
    """List all coherence reports"""
    analyzer = get_coherence_analyzer()
    reports = analyzer.list_reports(project_id)
    paginated = reports[skip:skip + limit]
    return {"reports": paginated, "total": len(reports)}
