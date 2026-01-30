"""
Predictive Pacing API - NarraForge 3.0

Endpoints for pacing analysis, prediction, and optimization.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.predictive_pacing import (
    get_predictive_pacing_engine,
    NarrativePhase,
    PacingLevel
)
from app.models.project import GenreType

router = APIRouter(prefix="/pacing", tags=["Predictive Pacing"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class MeasurePacingRequest(BaseModel):
    """Request for measuring pacing of a text segment"""
    text: str
    segment_id: str = "segment_1"


class AnalyzeChapterRequest(BaseModel):
    """Request for analyzing chapter pacing"""
    chapter_text: str
    chapter_number: int
    total_chapters: int
    genre: str = "drama"
    chapter_summary: Optional[str] = None


class PredictPacingRequest(BaseModel):
    """Request for predicting optimal pacing"""
    chapter_number: int
    total_chapters: int
    genre: str = "drama"
    plot_points: Optional[List[str]] = None
    previous_pacing: Optional[float] = None


class AnalyzeBookRequest(BaseModel):
    """Request for analyzing entire book pacing"""
    chapters: List[str]
    genre: str = "drama"
    chapter_summaries: Optional[List[str]] = None


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/levels")
async def get_pacing_levels() -> Dict[str, Any]:
    """Get all pacing levels"""
    return {
        "pacing_levels": [
            {"level": "very_slow", "score_range": "0.0-0.2", "pl": "Bardzo wolne", "description": "Głęboka refleksja, medytacyjne sceny"},
            {"level": "slow", "score_range": "0.2-0.4", "pl": "Wolne", "description": "Spokojne budowanie, opisy"},
            {"level": "moderate", "score_range": "0.4-0.6", "pl": "Umiarkowane", "description": "Zbalansowane tempo"},
            {"level": "fast", "score_range": "0.6-0.8", "pl": "Szybkie", "description": "Dynamiczne, napięcie"},
            {"level": "very_fast", "score_range": "0.8-1.0", "pl": "Bardzo szybkie", "description": "Akcja, kulminacja"}
        ]
    }


@router.get("/narrative-phases")
async def get_narrative_phases() -> Dict[str, Any]:
    """Get all narrative phases"""
    return {
        "phases": [
            {"phase": "setup", "position": "0-10%", "pl": "Wprowadzenie", "description": "Świat zwykły, przedstawienie bohaterów"},
            {"phase": "inciting_incident", "position": "10-15%", "pl": "Wydarzenie inicjujące", "description": "Coś zakłóca równowagę"},
            {"phase": "rising_action", "position": "15-40%", "pl": "Eskalacja", "description": "Bohater reaguje, stawki rosną"},
            {"phase": "midpoint", "position": "40-50%", "pl": "Punkt środkowy", "description": "Zwrot, nowa informacja"},
            {"phase": "complications", "position": "50-70%", "pl": "Komplikacje", "description": "Przeszkody, konflikty"},
            {"phase": "crisis", "position": "70-80%", "pl": "Kryzys", "description": "Najciemniejszy moment"},
            {"phase": "climax", "position": "80-90%", "pl": "Kulminacja", "description": "Ostateczna konfrontacja"},
            {"phase": "falling_action", "position": "90-95%", "pl": "Opadanie akcji", "description": "Konsekwencje kulminacji"},
            {"phase": "resolution", "position": "95-100%", "pl": "Rozwiązanie", "description": "Nowy status quo"}
        ]
    }


@router.get("/issue-types")
async def get_pacing_issue_types() -> Dict[str, Any]:
    """Get all pacing issue types"""
    return {
        "issue_types": [
            {"type": "too_slow_for_genre", "pl": "Za wolno dla gatunku", "severity": "moderate"},
            {"type": "too_fast_for_phase", "pl": "Za szybko dla fazy", "severity": "moderate"},
            {"type": "monotonous", "pl": "Monotonność", "severity": "minor"},
            {"type": "jarring_transition", "pl": "Nagłe przejście", "severity": "moderate"},
            {"type": "weak_buildup", "pl": "Słabe budowanie", "severity": "major"},
            {"type": "anticlimactic", "pl": "Antykulminacja", "severity": "critical"},
            {"type": "rushed_resolution", "pl": "Pośpieszne rozwiązanie", "severity": "moderate"},
            {"type": "dragging_middle", "pl": "Wlokący się środek", "severity": "major"},
            {"type": "no_breathing_room", "pl": "Brak wytchnienia", "severity": "moderate"},
            {"type": "lost_momentum", "pl": "Utrata rozpędu", "severity": "moderate"}
        ]
    }


@router.get("/genre-profiles")
async def get_genre_pacing_profiles() -> Dict[str, Any]:
    """Get pacing profiles for all genres"""
    engine = get_predictive_pacing_engine()

    profiles = {}
    for genre, profile in engine.genre_profiles.items():
        profiles[genre.value] = {
            "baseline_pacing": profile["baseline_pacing"],
            "pacing_variance": profile["pacing_variance"],
            "tension_floor": profile["tension_floor"],
            "climax_pacing": profile["climax_pacing"],
            "resolution_pacing": profile["resolution_pacing"],
            "breathing_frequency": profile["breathing_frequency"]
        }

    return {
        "genre_profiles": profiles
    }


@router.post("/measure")
async def measure_pacing(request: MeasurePacingRequest) -> Dict[str, Any]:
    """
    Measure the pacing of a text segment.

    Returns:
    - Word and sentence counts
    - Dialogue ratio
    - Action verb density
    - Tension level
    - Overall pacing score (0-1)
    """
    engine = get_predictive_pacing_engine()

    measurement = await engine.measure_pacing(
        text=request.text,
        segment_id=request.segment_id
    )

    return {
        "success": True,
        "measurement": measurement.to_dict()
    }


@router.post("/analyze-chapter")
async def analyze_chapter(request: AnalyzeChapterRequest) -> Dict[str, Any]:
    """
    Analyze the pacing of an entire chapter.

    Returns:
    - Narrative phase
    - Scene weight
    - Target vs actual pacing
    - Segment measurements
    - Tension arc
    - Issues detected
    - Recommendations
    """
    engine = get_predictive_pacing_engine()

    try:
        genre = GenreType(request.genre.upper())
    except ValueError:
        genre = GenreType.DRAMA

    profile = await engine.analyze_chapter_pacing(
        chapter_text=request.chapter_text,
        chapter_number=request.chapter_number,
        total_chapters=request.total_chapters,
        genre=genre,
        chapter_summary=request.chapter_summary
    )

    return {
        "success": True,
        "chapter_profile": profile.to_dict()
    }


@router.post("/predict")
async def predict_pacing(request: PredictPacingRequest) -> Dict[str, Any]:
    """
    Predict optimal pacing for a chapter.

    Returns:
    - Recommended pacing level
    - Pacing range (min-max)
    - Tension targets throughout chapter
    - Scene type distribution
    - Breathing and acceleration points
    - Key moments to consider
    """
    engine = get_predictive_pacing_engine()

    try:
        genre = GenreType(request.genre.upper())
    except ValueError:
        genre = GenreType.DRAMA

    prediction = await engine.predict_optimal_pacing(
        chapter_number=request.chapter_number,
        total_chapters=request.total_chapters,
        genre=genre,
        plot_points=request.plot_points,
        previous_pacing=request.previous_pacing
    )

    return {
        "success": True,
        "prediction": prediction.to_dict()
    }


@router.post("/analyze-book")
async def analyze_book(request: AnalyzeBookRequest) -> Dict[str, Any]:
    """
    Comprehensive pacing analysis of an entire book.

    Returns:
    - Chapter-by-chapter profiles
    - Overall pacing score
    - Consistency score
    - Genre fit score
    - Global issues
    - Pacing and tension curves
    - Recommendations
    - Bestseller pacing score
    """
    engine = get_predictive_pacing_engine()

    if len(request.chapters) < 2:
        raise HTTPException(status_code=400, detail="At least 2 chapters required for book analysis")

    try:
        genre = GenreType(request.genre.upper())
    except ValueError:
        genre = GenreType.DRAMA

    report = await engine.analyze_book_pacing(
        chapters=request.chapters,
        genre=genre,
        chapter_summaries=request.chapter_summaries
    )

    return {
        "success": True,
        "report": report.to_dict()
    }


@router.get("/phase/{chapter_number}/{total_chapters}")
async def get_narrative_phase(chapter_number: int, total_chapters: int) -> Dict[str, Any]:
    """
    Get the narrative phase for a specific chapter position.
    """
    engine = get_predictive_pacing_engine()

    phase = engine._determine_narrative_phase(chapter_number, total_chapters)

    return {
        "chapter_number": chapter_number,
        "total_chapters": total_chapters,
        "position_percentage": round(chapter_number / total_chapters * 100, 1),
        "narrative_phase": phase.value
    }


@router.get("/target/{genre}/{phase}")
async def get_target_pacing(genre: str, phase: str) -> Dict[str, Any]:
    """
    Get target pacing for a specific genre and narrative phase.
    """
    engine = get_predictive_pacing_engine()

    try:
        genre_type = GenreType(genre.upper())
    except ValueError:
        genre_type = GenreType.DRAMA

    try:
        narrative_phase = NarrativePhase(phase)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid phase: {phase}")

    genre_profile = engine._get_genre_profile(genre_type)
    target_score = genre_profile["phase_pacing"].get(narrative_phase, 0.5)
    target_level = engine._score_to_level(target_score)

    return {
        "genre": genre_type.value,
        "phase": narrative_phase.value,
        "target_score": target_score,
        "target_level": target_level.value,
        "acceptable_range": {
            "min": max(0, target_score - genre_profile["pacing_variance"]),
            "max": min(1, target_score + genre_profile["pacing_variance"])
        }
    }
