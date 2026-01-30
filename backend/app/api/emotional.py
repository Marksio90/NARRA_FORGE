"""
Emotional Resonance API - NarraForge 3.0

Endpoints for emotional analysis and optimization of narrative content.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.emotional_resonance_engine import (
    get_emotional_resonance_engine,
    EmotionDimension
)
from app.models.project import GenreType

router = APIRouter(prefix="/emotional", tags=["Emotional Resonance"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class AnalyzeRequest(BaseModel):
    """Request model for emotional analysis"""
    content: str
    genre: str = "drama"
    chapter_number: Optional[int] = None
    is_climax: bool = False


class ParagraphAnalyzeRequest(BaseModel):
    """Request for single paragraph analysis"""
    paragraph: str
    genre: str = "drama"


class ReaderStateRequest(BaseModel):
    """Request for reader state prediction"""
    paragraphs: List[str]
    genre: str = "drama"


class OptimizeRequest(BaseModel):
    """Request for optimization recommendations"""
    content: str
    genre: str = "drama"
    target_emotion: Optional[str] = None
    target_intensity: Optional[float] = None


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/dimensions")
async def get_emotion_dimensions() -> Dict[str, Any]:
    """
    Get list of all 12 emotion dimensions with descriptions.
    """
    return {
        "dimensions": [
            {"name": "fear", "description": "Strach, lęk, niepokój", "pl": "Strach"},
            {"name": "hope", "description": "Nadzieja, optymizm, wiara w przyszłość", "pl": "Nadzieja"},
            {"name": "sadness", "description": "Smutek, żal, melancholia", "pl": "Smutek"},
            {"name": "joy", "description": "Radość, szczęście, triumf", "pl": "Radość"},
            {"name": "anger", "description": "Gniew, frustracja, złość", "pl": "Gniew"},
            {"name": "surprise", "description": "Zaskoczenie, szok, niedowierzanie", "pl": "Zaskoczenie"},
            {"name": "shame", "description": "Wstyd, poczucie winy, żenada", "pl": "Wstyd"},
            {"name": "pride", "description": "Duma, godność, honor", "pl": "Duma"},
            {"name": "longing", "description": "Tęsknota, pragnienie, nostalgia", "pl": "Tęsknota"},
            {"name": "relief", "description": "Ulga, ukojenie, bezpieczeństwo", "pl": "Ulga"},
            {"name": "tension", "description": "Napięcie, suspens, oczekiwanie", "pl": "Napięcie"},
            {"name": "catharsis", "description": "Katharsis, emocjonalne oczyszczenie", "pl": "Katharsis"}
        ],
        "count": 12
    }


@router.get("/genre-profiles")
async def get_genre_profiles() -> Dict[str, Any]:
    """
    Get emotional profiles for each genre.
    """
    engine = get_emotional_resonance_engine()
    return {
        "profiles": engine._genre_profiles,
        "available_genres": list(engine._genre_profiles.keys())
    }


@router.post("/analyze")
async def analyze_emotional_resonance(request: AnalyzeRequest) -> Dict[str, Any]:
    """
    Comprehensive emotional analysis of text content.

    Returns:
    - 12-dimensional emotion vectors per paragraph
    - Emotional trajectory
    - Cathartic moments
    - Issues detected
    - Recommendations
    - Bestseller emotional score
    """
    engine = get_emotional_resonance_engine()

    try:
        genre = GenreType(request.genre.upper())
    except ValueError:
        genre = GenreType.DRAMA

    report = await engine.analyze_emotional_resonance(
        content=request.content,
        genre=genre,
        chapter_number=request.chapter_number,
        is_climax=request.is_climax
    )

    return report.to_dict()


@router.post("/analyze-paragraph")
async def analyze_paragraph(request: ParagraphAnalyzeRequest) -> Dict[str, Any]:
    """
    Analyze a single paragraph for its emotion vector.
    """
    engine = get_emotional_resonance_engine()

    vector = await engine.analyze_paragraph_vector(
        paragraph=request.paragraph,
        genre=request.genre
    )

    return {
        "emotion_vector": vector.to_dict(),
        "dominant_emotion": vector.dominant_emotion,
        "magnitude": round(vector.magnitude, 3),
        "valence": round(vector.valence, 3)
    }


@router.post("/predict-reader-state")
async def predict_reader_state(request: ReaderStateRequest) -> Dict[str, Any]:
    """
    Predict the reader's emotional state at this point in the narrative.

    Based on the paragraphs read so far, predicts:
    - Current dominant emotion
    - Tension level
    - Engagement level
    - What reader expects next
    - What would hit reader hard emotionally
    """
    engine = get_emotional_resonance_engine()

    state = await engine.predict_reader_state(
        paragraphs_so_far=request.paragraphs,
        genre=request.genre
    )

    return state


@router.post("/optimize")
async def optimize_emotional_impact(request: OptimizeRequest) -> Dict[str, Any]:
    """
    Get specific recommendations to optimize emotional impact.

    Optionally target a specific emotion and intensity level.
    """
    engine = get_emotional_resonance_engine()

    try:
        genre = GenreType(request.genre.upper())
    except ValueError:
        genre = GenreType.DRAMA

    optimizations = await engine.optimize_emotional_impact(
        content=request.content,
        genre=genre,
        target_emotion=request.target_emotion,
        target_intensity=request.target_intensity
    )

    return optimizations


@router.get("/issue-types")
async def get_issue_types() -> Dict[str, Any]:
    """
    Get list of emotional issue types that can be detected.
    """
    return {
        "issue_types": [
            {
                "type": "flat_sequence",
                "description": "Sekwencja z zbyt małą emocjonalną wariacją",
                "severity_range": ["minor", "major"]
            },
            {
                "type": "jarring_transition",
                "description": "Nagłe przejście emocjonalne bez przygotowania",
                "severity_range": ["major", "critical"]
            },
            {
                "type": "missing_buildup",
                "description": "Kulminacja bez odpowiedniego przygotowania",
                "severity_range": ["major", "critical"]
            },
            {
                "type": "unearned_emotion",
                "description": "Emocja bez uzasadnienia w narracji",
                "severity_range": ["minor", "major"]
            },
            {
                "type": "emotional_whiplash",
                "description": "Zbyt wiele szybkich zmian emocjonalnych",
                "severity_range": ["major"]
            },
            {
                "type": "monotonous_tone",
                "description": "Ta sama emocja przez zbyt długi czas",
                "severity_range": ["minor", "major"]
            },
            {
                "type": "weak_catharsis",
                "description": "Niesatysfakcjonująca kulminacja emocjonalna",
                "severity_range": ["major"]
            },
            {
                "type": "pacing_mismatch",
                "description": "Tempo nie pasuje do emocji lub gatunku",
                "severity_range": ["minor", "major"]
            }
        ]
    }


@router.get("/arc-types")
async def get_arc_types() -> Dict[str, Any]:
    """
    Get list of emotional arc types.
    """
    return {
        "arc_types": [
            {"type": "rise", "description": "Budowanie pozytywnych emocji", "pl": "Wzrost"},
            {"type": "fall", "description": "Spadek w negatywne emocje", "pl": "Spadek"},
            {"type": "rise_fall", "description": "Klasyczny łuk tragedii", "pl": "Wzrost-Spadek"},
            {"type": "fall_rise", "description": "Łuk odkupienia/triumfu", "pl": "Spadek-Wzrost"},
            {"type": "oscillation", "description": "Naprzemienne wzloty i upadki", "pl": "Oscylacja"},
            {"type": "plateau", "description": "Utrzymany stan emocjonalny", "pl": "Plateau"},
            {"type": "crescendo", "description": "Budowanie do klimaksu", "pl": "Crescendo"},
            {"type": "resolution", "description": "Uspokojenie po klimaksie", "pl": "Rozwiązanie"}
        ]
    }
