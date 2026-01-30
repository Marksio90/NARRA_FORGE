"""
Complexity API - NarraForge 3.0 Phase 3

Endpoints for Dynamic Complexity Adjustment System.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.complexity_adjustment import (
    get_complexity_adjuster,
    ReadingLevel
)

router = APIRouter(prefix="/complexity", tags=["Dynamic Complexity"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class AnalyzeComplexityRequest(BaseModel):
    """Request for complexity analysis"""
    project_id: str
    chapters: List[Dict[str, Any]]
    target_level: str
    genre: Optional[str] = None


class AnalyzeTextRequest(BaseModel):
    """Request for text analysis"""
    text: str
    target_level: Optional[str] = None


class SimplifyTextRequest(BaseModel):
    """Request for text simplification"""
    text: str
    target_level: str


class EnhanceTextRequest(BaseModel):
    """Request for text enhancement"""
    text: str
    target_level: str


class CreateProfileRequest(BaseModel):
    """Request for creating custom profile"""
    profile_data: Dict[str, Any]


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/reading-levels")
async def get_reading_levels() -> Dict[str, Any]:
    """Get all reading levels with descriptions"""
    adjuster = get_complexity_adjuster()
    return {"levels": adjuster.list_reading_levels()}


@router.get("/vocabulary-levels")
async def get_vocabulary_levels() -> Dict[str, Any]:
    """Get vocabulary complexity levels"""
    return {
        "levels": [
            {"level": "basic", "pl": "Podstawowy", "description": "Codzienne słowa"},
            {"level": "intermediate", "pl": "Średni", "description": "Trochę zaawansowane"},
            {"level": "advanced", "pl": "Zaawansowany", "description": "Bogaty słownik"},
            {"level": "literary", "pl": "Literacki", "description": "Artystyczne słownictwo"},
            {"level": "specialized", "pl": "Specjalistyczny", "description": "Terminy dziedzinowe"}
        ]
    }


@router.get("/sentence-complexity")
async def get_sentence_complexity_levels() -> Dict[str, Any]:
    """Get sentence structure complexity levels"""
    return {
        "levels": [
            {"level": "simple", "pl": "Proste", "description": "Podmiot-orzeczenie-dopełnienie"},
            {"level": "compound", "pl": "Złożone", "description": "Wiele klauzul"},
            {"level": "complex", "pl": "Skomplikowane", "description": "Zdania podrzędne"},
            {"level": "sophisticated", "pl": "Wyrafinowane", "description": "Struktury literackie"}
        ]
    }


@router.get("/genre-modifiers")
async def get_genre_modifiers() -> Dict[str, Any]:
    """Get genre-specific complexity modifiers"""
    return {
        "modifiers": {
            "thriller": {"sentence_mod": -2, "paragraph_mod": -2, "description": "Krótsze dla tempa"},
            "romance": {"sentence_mod": 0, "paragraph_mod": 1, "description": "Standardowe"},
            "fantasy": {"sentence_mod": 2, "paragraph_mod": 2, "description": "Dłuższe dla worldbuildingu"},
            "literary": {"sentence_mod": 3, "paragraph_mod": 3, "description": "Najbardziej złożone"},
            "mystery": {"sentence_mod": 0, "paragraph_mod": 0, "description": "Zbalansowane"},
            "horror": {"sentence_mod": -1, "paragraph_mod": -1, "description": "Krótsze dla napięcia"},
            "scifi": {"sentence_mod": 1, "paragraph_mod": 1, "description": "Trochę dłuższe"}
        }
    }


@router.post("/analyze")
async def analyze_complexity(request: AnalyzeComplexityRequest) -> Dict[str, Any]:
    """
    Analyze text complexity against target reading level.
    """
    adjuster = get_complexity_adjuster()

    try:
        target = ReadingLevel(request.target_level)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid reading level")

    report = await adjuster.analyze_complexity(
        project_id=request.project_id,
        chapters=request.chapters,
        target_level=target,
        genre=request.genre
    )

    return {
        "success": True,
        "report": report.to_dict()
    }


@router.post("/analyze-text")
async def analyze_text(request: AnalyzeTextRequest) -> Dict[str, Any]:
    """
    Quick complexity analysis of a text.
    """
    adjuster = get_complexity_adjuster()

    target = None
    if request.target_level:
        try:
            target = ReadingLevel(request.target_level)
        except ValueError:
            pass

    result = await adjuster.analyze_text(
        text=request.text,
        target_level=target
    )

    return {
        "success": True,
        "analysis": result
    }


@router.post("/simplify")
async def simplify_text(request: SimplifyTextRequest) -> Dict[str, Any]:
    """
    Simplify text to match target reading level.
    """
    adjuster = get_complexity_adjuster()

    try:
        target = ReadingLevel(request.target_level)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid reading level")

    result = await adjuster.simplify_text(
        text=request.text,
        target_level=target
    )

    return {
        "success": True,
        "result": result
    }


@router.post("/enhance")
async def enhance_text(request: EnhanceTextRequest) -> Dict[str, Any]:
    """
    Enhance text complexity for more sophisticated audience.
    """
    adjuster = get_complexity_adjuster()

    try:
        target = ReadingLevel(request.target_level)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid reading level")

    result = await adjuster.enhance_complexity(
        text=request.text,
        target_level=target
    )

    return {
        "success": True,
        "result": result
    }


@router.post("/readability")
async def get_readability_scores(text: str) -> Dict[str, Any]:
    """
    Get comprehensive readability scores for text.
    """
    adjuster = get_complexity_adjuster()

    result = await adjuster.get_readability_scores(text)

    return {
        "success": True,
        "scores": result
    }


@router.post("/profile/create")
async def create_custom_profile(request: CreateProfileRequest) -> Dict[str, Any]:
    """
    Create a custom complexity profile.
    """
    adjuster = get_complexity_adjuster()

    profile = adjuster.create_custom_profile(request.profile_data)

    return {
        "success": True,
        "profile": profile.to_dict()
    }


@router.get("/report/{report_id}")
async def get_report(report_id: str) -> Dict[str, Any]:
    """Get a complexity report by ID"""
    adjuster = get_complexity_adjuster()
    report = adjuster.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {"report": report.to_dict()}


@router.get("/profile/{profile_id}")
async def get_profile(profile_id: str) -> Dict[str, Any]:
    """Get a complexity profile by ID"""
    adjuster = get_complexity_adjuster()
    profile = adjuster.get_profile(profile_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {"profile": profile.to_dict()}
