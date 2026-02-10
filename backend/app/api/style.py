"""
Style Adaptation API - NarraForge 3.0

Endpoints for style analysis, profile creation, and text adaptation.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.style_adaptation_engine import (
    get_style_adaptation_engine,
    SceneType
)

router = APIRouter(prefix="/style", tags=["Style Adaptation"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class AnalyzeStyleRequest(BaseModel):
    """Request for style analysis"""
    text: str


class CreateProfileRequest(BaseModel):
    """Request for creating a style profile"""
    profile_name: str
    sample_texts: List[str]
    author_name: Optional[str] = None
    genre: Optional[str] = None


class AdaptTextRequest(BaseModel):
    """Request for adapting text to a style"""
    text: str
    profile_name: str
    scene_type: str = "dialogue"
    preserve_meaning: bool = True


class AdaptationInstructionsRequest(BaseModel):
    """Request for getting adaptation instructions"""
    profile_name: str
    scene_type: str = "dialogue"


class ConsistencyCheckRequest(BaseModel):
    """Request for checking style consistency"""
    texts: List[str]
    profile_name: str


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/profiles")
async def list_profiles(skip: int = 0, limit: int = 100) -> Dict[str, Any]:
    """List all available style profiles"""
    engine = get_style_adaptation_engine()
    profiles = engine.list_profiles()
    paginated = profiles[skip:skip + limit]

    return {
        "profiles": paginated,
        "count": len(paginated),
        "total": len(profiles),
        "active_profile": engine.active_profile
    }


@router.get("/profiles/{profile_name}")
async def get_profile(profile_name: str) -> Dict[str, Any]:
    """Get details of a specific style profile"""
    engine = get_style_adaptation_engine()
    profile = engine.get_profile(profile_name)

    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile not found: {profile_name}")

    return {
        "profile": profile.to_dict()
    }


@router.get("/scene-types")
async def get_scene_types() -> Dict[str, Any]:
    """Get all available scene types"""
    return {
        "scene_types": [
            {"type": "action", "pl": "Akcja", "description": "Sceny dynamiczne, walki, pościgi"},
            {"type": "dialogue", "pl": "Dialog", "description": "Rozmowy między postaciami"},
            {"type": "introspection", "pl": "Introspekcja", "description": "Wewnętrzne przemyślenia"},
            {"type": "description", "pl": "Opis", "description": "Opisy miejsc, ludzi, przedmiotów"},
            {"type": "romance", "pl": "Romans", "description": "Sceny romantyczne, intymne"},
            {"type": "suspense", "pl": "Suspens", "description": "Budowanie napięcia"},
            {"type": "revelation", "pl": "Objawienie", "description": "Ujawnienie tajemnicy"},
            {"type": "transition", "pl": "Przejście", "description": "Sceny łączące"},
            {"type": "climax", "pl": "Kulminacja", "description": "Punkty kulminacyjne"},
            {"type": "resolution", "pl": "Rozwiązanie", "description": "Sceny po kulminacji"}
        ]
    }


@router.get("/dimensions")
async def get_style_dimensions() -> Dict[str, Any]:
    """Get all style dimensions"""
    return {
        "dimensions": [
            {"name": "sentence_length", "pl": "Długość zdań", "range": "krótkie (0) - długie (1)"},
            {"name": "vocabulary_richness", "pl": "Bogactwo słownictwa", "range": "proste (0) - bogate (1)"},
            {"name": "formality", "pl": "Formalność", "range": "potoczny (0) - formalny (1)"},
            {"name": "imagery_density", "pl": "Gęstość obrazowania", "range": "mało (0) - dużo (1)"},
            {"name": "dialogue_ratio", "pl": "Stosunek dialogu", "range": "mało (0) - dużo (1)"},
            {"name": "description_detail", "pl": "Szczegółowość", "range": "ogólne (0) - szczegółowe (1)"},
            {"name": "pacing", "pl": "Tempo", "range": "wolne (0) - szybkie (1)"},
            {"name": "emotional_intensity", "pl": "Intensywność emocji", "range": "chłodne (0) - gorące (1)"},
            {"name": "showing_vs_telling", "pl": "Show vs Tell", "range": "telling (0) - showing (1)"},
            {"name": "metaphor_frequency", "pl": "Częstość metafor", "range": "rzadkie (0) - częste (1)"},
            {"name": "sentence_variety", "pl": "Różnorodność zdań", "range": "monotonne (0) - zróżnicowane (1)"},
            {"name": "pov_depth", "pl": "Głębokość POV", "range": "płytki (0) - głęboki (1)"}
        ]
    }


@router.get("/voice-types")
async def get_voice_types() -> Dict[str, Any]:
    """Get all narrative voice types"""
    return {
        "voice_types": [
            {"type": "first_person_intimate", "pl": "Pierwsza osoba - intymna"},
            {"type": "first_person_unreliable", "pl": "Pierwsza osoba - niewiarygodny narrator"},
            {"type": "third_person_limited", "pl": "Trzecia osoba - ograniczona"},
            {"type": "third_person_omniscient", "pl": "Trzecia osoba - wszechwiedzący narrator"},
            {"type": "third_person_objective", "pl": "Trzecia osoba - obiektywna"},
            {"type": "second_person", "pl": "Druga osoba"}
        ]
    }


@router.post("/analyze")
async def analyze_style(request: AnalyzeStyleRequest) -> Dict[str, Any]:
    """
    Analyze the style of a text.

    Returns:
    - 12 style dimensions scored 0-1
    - Detected techniques
    - Vocabulary statistics
    - Sentence statistics
    - Identified patterns
    """
    engine = get_style_adaptation_engine()

    analysis = await engine.analyze_text_style(request.text)

    return {
        "success": True,
        "analysis": analysis.to_dict()
    }


@router.post("/profiles/create")
async def create_profile(request: CreateProfileRequest) -> Dict[str, Any]:
    """
    Create a new style profile from sample texts.

    Provide 2-5 sample texts for best results.
    """
    if len(request.sample_texts) < 1:
        raise HTTPException(status_code=400, detail="At least one sample text required")

    engine = get_style_adaptation_engine()

    profile = await engine.create_profile_from_samples(
        profile_name=request.profile_name,
        sample_texts=request.sample_texts,
        author_name=request.author_name,
        genre=request.genre
    )

    return {
        "success": True,
        "message": f"Profile '{request.profile_name}' created successfully",
        "profile": profile.to_dict()
    }


@router.post("/adapt")
async def adapt_text(request: AdaptTextRequest) -> Dict[str, Any]:
    """
    Adapt text to match a style profile.

    Returns the styled text along with information about changes made.
    """
    engine = get_style_adaptation_engine()

    try:
        scene_type = SceneType(request.scene_type)
    except ValueError:
        scene_type = SceneType.DIALOGUE

    try:
        styled = await engine.adapt_text_to_style(
            text=request.text,
            profile_name=request.profile_name,
            scene_type=scene_type,
            preserve_meaning=request.preserve_meaning
        )

        return {
            "success": True,
            "result": styled.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/instructions")
async def get_adaptation_instructions(request: AdaptationInstructionsRequest) -> Dict[str, Any]:
    """
    Get style adaptation instructions for text generation.

    Use these instructions to guide the LLM during text generation.
    """
    engine = get_style_adaptation_engine()

    try:
        scene_type = SceneType(request.scene_type)
    except ValueError:
        scene_type = SceneType.DIALOGUE

    try:
        instructions = await engine.get_style_adaptation_instructions(
            profile_name=request.profile_name,
            scene_type=scene_type
        )

        return {
            "success": True,
            "instructions": instructions.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/check-consistency")
async def check_consistency(request: ConsistencyCheckRequest) -> Dict[str, Any]:
    """
    Check style consistency across multiple text fragments.

    Useful for ensuring consistent style throughout a book.
    """
    if len(request.texts) < 2:
        raise HTTPException(status_code=400, detail="At least 2 texts required for consistency check")

    engine = get_style_adaptation_engine()

    try:
        result = await engine.check_style_consistency(
            texts=request.texts,
            profile_name=request.profile_name
        )

        return {
            "success": True,
            "consistency_report": result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/profiles/{profile_name}/activate")
async def activate_profile(profile_name: str) -> Dict[str, Any]:
    """Set a profile as the active style profile"""
    engine = get_style_adaptation_engine()

    success = engine.set_active_profile(profile_name)

    if not success:
        raise HTTPException(status_code=404, detail=f"Profile not found: {profile_name}")

    return {
        "success": True,
        "active_profile": profile_name
    }


@router.get("/profiles/{profile_name}/export")
async def export_profile(profile_name: str) -> Dict[str, Any]:
    """Export a style profile as JSON"""
    engine = get_style_adaptation_engine()

    export_data = engine.export_profile(profile_name)

    if not export_data:
        raise HTTPException(status_code=404, detail=f"Profile not found: {profile_name}")

    return {
        "success": True,
        "export": export_data
    }
