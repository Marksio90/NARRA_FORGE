"""
Cultural Intelligence API - NarraForge 3.0 Phase 3

Endpoints for TITAN Cultural Intelligence System.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.cultural_intelligence import (
    get_cultural_intelligence,
    LocalizationLevel
)

router = APIRouter(prefix="/cultural", tags=["TITAN Cultural Intelligence"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class AnalyzeCulturalRequest(BaseModel):
    """Request for cultural content analysis"""
    project_id: str
    chapters: List[Dict[str, Any]]
    source_culture: str = "PL"
    target_cultures: Optional[List[str]] = None


class CheckSensitivityRequest(BaseModel):
    """Request for sensitivity check"""
    text: str
    target_cultures: Optional[List[str]] = None


class LocalizeContentRequest(BaseModel):
    """Request for content localization"""
    text: str
    source_culture: str
    target_culture: str
    localization_level: str = "moderate"


class ValidateNamesRequest(BaseModel):
    """Request for name validation"""
    names: List[str]
    culture: str


class GenerateNamesRequest(BaseModel):
    """Request for name generation"""
    culture: str
    count: int = 10
    gender: Optional[str] = None


class GetRecommendationsRequest(BaseModel):
    """Request for cultural recommendations"""
    genre: str
    target_culture: str


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/cultures")
async def list_cultures() -> Dict[str, Any]:
    """List all available cultural profiles"""
    intelligence = get_cultural_intelligence()
    return {"cultures": intelligence.list_available_cultures()}


@router.get("/culture/{country_code}")
async def get_culture_profile(country_code: str) -> Dict[str, Any]:
    """Get a specific cultural profile"""
    intelligence = get_cultural_intelligence()
    profile = intelligence.get_cultural_profile(country_code.upper())

    if not profile:
        raise HTTPException(status_code=404, detail="Culture not found")

    return {"profile": profile.to_dict()}


@router.get("/sensitivity-categories")
async def get_sensitivity_categories() -> Dict[str, Any]:
    """Get all sensitivity categories"""
    return {
        "categories": [
            {"category": "religion", "pl": "Religia"},
            {"category": "politics", "pl": "Polityka"},
            {"category": "gender", "pl": "Płeć"},
            {"category": "sexuality", "pl": "Seksualność"},
            {"category": "race_ethnicity", "pl": "Rasa/Etniczność"},
            {"category": "class", "pl": "Klasa społeczna"},
            {"category": "age", "pl": "Wiek"},
            {"category": "disability", "pl": "Niepełnosprawność"},
            {"category": "violence", "pl": "Przemoc"},
            {"category": "death", "pl": "Śmierć"},
            {"category": "family", "pl": "Rodzina"},
            {"category": "food", "pl": "Jedzenie"},
            {"category": "customs", "pl": "Zwyczaje"}
        ]
    }


@router.get("/localization-levels")
async def get_localization_levels() -> Dict[str, Any]:
    """Get localization levels"""
    return {
        "levels": [
            {"level": "none", "pl": "Brak", "description": "Oryginalna treść"},
            {"level": "light", "pl": "Lekka", "description": "Drobne dostosowania"},
            {"level": "moderate", "pl": "Umiarkowana", "description": "Znaczące adaptacje"},
            {"level": "deep", "pl": "Głęboka", "description": "Główne zmiany kulturowe"},
            {"level": "transcreation", "pl": "Transkreacja", "description": "Całkowite przepisanie"}
        ]
    }


@router.post("/analyze")
async def analyze_cultural_content(request: AnalyzeCulturalRequest) -> Dict[str, Any]:
    """
    Perform full cultural analysis of content.

    Checks for sensitivity issues and localization needs.
    """
    intelligence = get_cultural_intelligence()

    report = await intelligence.analyze_cultural_content(
        project_id=request.project_id,
        chapters=request.chapters,
        source_culture=request.source_culture,
        target_cultures=request.target_cultures
    )

    return {
        "success": True,
        "report": report.to_dict()
    }


@router.post("/check-sensitivity")
async def check_text_sensitivity(request: CheckSensitivityRequest) -> Dict[str, Any]:
    """
    Quick sensitivity check on a piece of text.
    """
    intelligence = get_cultural_intelligence()

    result = await intelligence.check_text_sensitivity(
        text=request.text,
        target_cultures=request.target_cultures
    )

    return {
        "success": True,
        "result": result
    }


@router.post("/localize")
async def localize_content(request: LocalizeContentRequest) -> Dict[str, Any]:
    """
    Localize content for a target culture.
    """
    intelligence = get_cultural_intelligence()

    try:
        level = LocalizationLevel(request.localization_level)
    except ValueError:
        level = LocalizationLevel.MODERATE

    result = await intelligence.localize_content(
        text=request.text,
        source_culture=request.source_culture,
        target_culture=request.target_culture,
        localization_level=level
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "success": True,
        "result": result
    }


@router.post("/recommendations")
async def get_cultural_recommendations(request: GetRecommendationsRequest) -> Dict[str, Any]:
    """
    Get cultural recommendations for writing in a genre for a target culture.
    """
    intelligence = get_cultural_intelligence()

    result = await intelligence.get_cultural_recommendations(
        genre=request.genre,
        target_culture=request.target_culture
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "success": True,
        "recommendations": result
    }


@router.post("/validate-names")
async def validate_character_names(request: ValidateNamesRequest) -> Dict[str, Any]:
    """
    Validate character names for cultural appropriateness.
    """
    intelligence = get_cultural_intelligence()

    result = await intelligence.validate_character_names(
        names=request.names,
        culture=request.culture
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "success": True,
        "validation": result
    }


@router.post("/generate-names")
async def generate_culturally_appropriate_names(request: GenerateNamesRequest) -> Dict[str, Any]:
    """
    Generate culturally appropriate character names.
    """
    intelligence = get_cultural_intelligence()

    result = await intelligence.generate_culturally_appropriate_names(
        culture=request.culture,
        count=request.count,
        gender=request.gender
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "success": True,
        "names": result
    }


@router.get("/report/{report_id}")
async def get_report(report_id: str) -> Dict[str, Any]:
    """Get a cultural analysis report by ID"""
    intelligence = get_cultural_intelligence()
    report = intelligence.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {"report": report.to_dict()}


@router.get("/reports")
async def list_reports(project_id: Optional[str] = None) -> Dict[str, Any]:
    """List all cultural analysis reports"""
    intelligence = get_cultural_intelligence()
    return {"reports": intelligence.list_reports(project_id)}
