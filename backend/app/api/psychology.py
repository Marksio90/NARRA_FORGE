"""
Reader Psychology API - NarraForge 3.0 Phase 3

Endpoints for Predictive Reader Psychology Engine.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.reader_psychology import (
    get_psychology_engine,
    ReaderType,
    EmotionalState,
    PsychologicalHook
)

router = APIRouter(prefix="/psychology", tags=["Reader Psychology"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class AnalyzeStoryRequest(BaseModel):
    """Request for full story psychology analysis"""
    project_id: str
    chapters: List[Dict[str, Any]]
    genre: str
    target_reader_type: Optional[str] = None


class AnalyzeChapterRequest(BaseModel):
    """Request for chapter psychology analysis"""
    chapter_text: str
    chapter_number: int
    genre: str
    target_reader_type: Optional[str] = None


class OptimizeOpeningRequest(BaseModel):
    """Request for opening optimization"""
    opening_text: str
    genre: str
    target_reader_type: str


class OptimizeEndingRequest(BaseModel):
    """Request for ending optimization"""
    ending_text: str
    genre: str
    is_final_chapter: bool = False


class CreateReaderProfileRequest(BaseModel):
    """Request for creating custom reader profile"""
    reader_type: str
    customizations: Optional[Dict[str, Any]] = None


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/reader-types")
async def get_reader_types() -> Dict[str, Any]:
    """Get all reader archetypes"""
    return {
        "types": [
            {"type": "analytical", "pl": "Analityczny", "description": "Lubi zagadki i szczegóły"},
            {"type": "emotional", "pl": "Emocjonalny", "description": "Szuka połączenia emocjonalnego"},
            {"type": "thrill_seeker", "pl": "Poszukiwacz wrażeń", "description": "Chce akcji i ekscytacji"},
            {"type": "escapist", "pl": "Eskapista", "description": "Szuka zanurzenia w innym świecie"},
            {"type": "intellectual", "pl": "Intelektualista", "description": "Chce idei i koncepcji"},
            {"type": "romantic", "pl": "Romantyk", "description": "Szuka historii o związkach"},
            {"type": "casual", "pl": "Casualowy", "description": "Szuka lekkiej rozrywki"}
        ]
    }


@router.get("/emotional-states")
async def get_emotional_states() -> Dict[str, Any]:
    """Get all reader emotional states"""
    return {
        "states": [
            {"state": "engaged", "pl": "Zaangażowany"},
            {"state": "excited", "pl": "Podekscytowany"},
            {"state": "tense", "pl": "Napięty"},
            {"state": "sad", "pl": "Smutny"},
            {"state": "happy", "pl": "Szczęśliwy"},
            {"state": "anxious", "pl": "Niespokojny"},
            {"state": "curious", "pl": "Zaciekawiony"},
            {"state": "bored", "pl": "Znudzony"},
            {"state": "satisfied", "pl": "Usatysfakcjonowany"},
            {"state": "frustrated", "pl": "Sfrustrowany"},
            {"state": "surprised", "pl": "Zaskoczony"},
            {"state": "nostalgic", "pl": "Nostalgiczny"}
        ]
    }


@router.get("/psychological-hooks")
async def get_psychological_hooks() -> Dict[str, Any]:
    """Get all psychological hooks"""
    return {
        "hooks": [
            {"hook": "cliffhanger", "pl": "Cliffhanger", "description": "Zawieszenie akcji"},
            {"hook": "open_loop", "pl": "Otwarta pętla", "description": "Nierozwiązane pytanie"},
            {"hook": "curiosity_gap", "pl": "Luka ciekawości", "description": "Tworzenie chęci poznania"},
            {"hook": "emotional_investment", "pl": "Inwestycja emocjonalna", "description": "Przywiązanie do postaci"},
            {"hook": "anticipation", "pl": "Antycypacja", "description": "Oczekiwanie na wydarzenie"},
            {"hook": "payoff", "pl": "Wypłata", "description": "Spełnienie obietnicy"},
            {"hook": "pattern_break", "pl": "Złamanie wzorca", "description": "Niespodziewany zwrot"},
            {"hook": "identification", "pl": "Identyfikacja", "description": "Utożsamienie z bohaterem"}
        ]
    }


@router.get("/engagement-levels")
async def get_engagement_levels() -> Dict[str, Any]:
    """Get engagement level definitions"""
    return {
        "levels": [
            {"level": "deep_flow", "pl": "Głęboki flow", "score_range": "0.85-1.0"},
            {"level": "engaged", "pl": "Zaangażowany", "score_range": "0.70-0.85"},
            {"level": "interested", "pl": "Zainteresowany", "score_range": "0.55-0.70"},
            {"level": "passive", "pl": "Pasywny", "score_range": "0.40-0.55"},
            {"level": "distracted", "pl": "Rozproszony", "score_range": "0.25-0.40"},
            {"level": "disengaged", "pl": "Niezaangażowany", "score_range": "0.0-0.25"}
        ]
    }


@router.post("/analyze-story")
async def analyze_story_psychology(request: AnalyzeStoryRequest) -> Dict[str, Any]:
    """
    Perform full psychological analysis of a story.

    Analyzes emotional journey, engagement patterns, and reader satisfaction.
    """
    engine = get_psychology_engine()

    target_type = None
    if request.target_reader_type:
        try:
            target_type = ReaderType(request.target_reader_type)
        except ValueError:
            pass

    report = await engine.analyze_full_story(
        project_id=request.project_id,
        chapters=request.chapters,
        genre=request.genre,
        target_reader_type=target_type
    )

    return {
        "success": True,
        "report": report.to_dict()
    }


@router.post("/analyze-chapter")
async def analyze_chapter_psychology(request: AnalyzeChapterRequest) -> Dict[str, Any]:
    """
    Analyze psychology of a single chapter.
    """
    engine = get_psychology_engine()

    target_type = None
    if request.target_reader_type:
        try:
            target_type = ReaderType(request.target_reader_type)
        except ValueError:
            pass

    analysis = await engine.analyze_chapter(
        chapter_text=request.chapter_text,
        chapter_number=request.chapter_number,
        genre=request.genre,
        target_reader_type=target_type
    )

    return {
        "success": True,
        "analysis": analysis.to_dict()
    }


@router.post("/optimize-opening")
async def optimize_chapter_opening(request: OptimizeOpeningRequest) -> Dict[str, Any]:
    """
    Analyze and suggest optimizations for chapter opening.
    """
    engine = get_psychology_engine()

    try:
        reader_type = ReaderType(request.target_reader_type)
    except ValueError:
        reader_type = ReaderType.CASUAL

    result = await engine.optimize_chapter_opening(
        opening_text=request.opening_text,
        genre=request.genre,
        target_reader_type=reader_type
    )

    return {
        "success": True,
        "optimization": result
    }


@router.post("/optimize-ending")
async def optimize_chapter_ending(request: OptimizeEndingRequest) -> Dict[str, Any]:
    """
    Analyze and suggest optimizations for chapter ending.
    """
    engine = get_psychology_engine()

    result = await engine.optimize_chapter_ending(
        ending_text=request.ending_text,
        genre=request.genre,
        is_final_chapter=request.is_final_chapter
    )

    return {
        "success": True,
        "optimization": result
    }


@router.post("/analyze-pacing")
async def analyze_emotional_pacing(chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze emotional pacing across the story.
    """
    engine = get_psychology_engine()

    result = await engine.analyze_emotional_pacing(chapters)

    return {
        "success": True,
        "pacing_analysis": result
    }


@router.post("/reader-profile/create")
async def create_reader_profile(request: CreateReaderProfileRequest) -> Dict[str, Any]:
    """
    Create a custom reader profile.
    """
    engine = get_psychology_engine()

    try:
        reader_type = ReaderType(request.reader_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid reader type")

    profile = engine.create_reader_profile(
        reader_type=reader_type,
        customizations=request.customizations
    )

    return {
        "success": True,
        "profile": profile.to_dict()
    }


@router.get("/report/{report_id}")
async def get_report(report_id: str) -> Dict[str, Any]:
    """Get a psychology report by ID"""
    engine = get_psychology_engine()
    report = engine.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {"report": report.to_dict()}


@router.get("/reports")
async def list_reports(project_id: Optional[str] = None) -> Dict[str, Any]:
    """List all psychology reports"""
    engine = get_psychology_engine()
    return {"reports": engine.list_reports(project_id)}
