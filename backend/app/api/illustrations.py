"""
Illustrations API - NarraForge 3.0 Phase 2

Endpoints for AI illustration generation and character visual consistency.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.illustration_pipeline import (
    get_illustration_pipeline,
    IllustrationStyle,
    IllustrationType,
    AspectRatio,
    ImageProvider
)
from app.services.character_visual_system import (
    get_character_visual_system,
    AppearanceChangeType
)
from app.models.project import GenreType

router = APIRouter(prefix="/illustrations", tags=["AI Illustrations"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class ExtractScenesRequest(BaseModel):
    """Request for extracting illustratable scenes"""
    chapter_text: str
    chapter_number: int
    max_scenes: int = 3
    genre: str = "drama"


class GeneratePromptRequest(BaseModel):
    """Request for generating illustration prompt"""
    scene_description: Dict[str, Any]
    style_name: str
    illustration_type: str = "scene"
    character_appearances: Optional[Dict[str, str]] = None


class CreateStyleRequest(BaseModel):
    """Request for creating visual style"""
    name: str
    genre: str = "drama"
    customizations: Optional[Dict[str, Any]] = None


class GenerateIllustrationRequest(BaseModel):
    """Request for generating illustration"""
    prompt_id: str
    provider: str = "openai_dalle"


class CreatePlanRequest(BaseModel):
    """Request for creating illustration plan"""
    project_id: str
    chapters: List[str]
    genre: str = "drama"
    illustrations_per_chapter: int = 2
    include_character_portraits: bool = True
    include_maps: bool = False
    include_chapter_headers: bool = False
    character_list: Optional[List[str]] = None


class GenerateVisualProfileRequest(BaseModel):
    """Request for generating character visual profile"""
    character_name: str
    character_description: str
    genre: str = "drama"


class RegisterAppearanceChangeRequest(BaseModel):
    """Request for registering appearance change"""
    character_name: str
    change_type: str
    chapter_number: int
    description: str
    affected_features: List[str]
    is_permanent: bool = True
    revert_chapter: Optional[int] = None


class GetPromptRequest(BaseModel):
    """Request for getting character illustration prompt"""
    character_name: str
    chapter_number: int
    emotional_state: Optional[str] = None
    specific_outfit: Optional[str] = None
    action: Optional[str] = None


class ValidateConsistencyRequest(BaseModel):
    """Request for validating scene consistency"""
    scene_description: str
    characters_in_scene: List[str]
    chapter_number: int


# =============================================================================
# ILLUSTRATION PIPELINE ENDPOINTS
# =============================================================================

@router.get("/styles")
async def get_illustration_styles() -> Dict[str, Any]:
    """Get all available illustration styles"""
    return {
        "styles": [
            {"style": "realistic", "pl": "Realistyczny", "description": "Fotorealistyczne ilustracje"},
            {"style": "painterly", "pl": "Malarski", "description": "Styl olejny, malarskie pociągnięcia"},
            {"style": "watercolor", "pl": "Akwarela", "description": "Miękkie krawędzie, płynne kolory"},
            {"style": "digital_art", "pl": "Grafika cyfrowa", "description": "Żywe kolory, ostre detale"},
            {"style": "manga", "pl": "Manga", "description": "Styl manga/anime"},
            {"style": "comic", "pl": "Komiks", "description": "Styl komiksowy zachodni"},
            {"style": "sketch", "pl": "Szkic", "description": "Szkic ołówkiem"},
            {"style": "fantasy_art", "pl": "Fantasy Art", "description": "Epicka sztuka fantasy"},
            {"style": "noir", "pl": "Noir", "description": "Ciemny, wysoki kontrast"},
            {"style": "vintage", "pl": "Vintage", "description": "Retro estetyka"},
            {"style": "minimalist", "pl": "Minimalistyczny", "description": "Czyste linie, prosta kompozycja"},
            {"style": "children_book", "pl": "Książka dla dzieci", "description": "Kolorowy, kapryśny styl"}
        ]
    }


@router.get("/types")
async def get_illustration_types() -> Dict[str, Any]:
    """Get all illustration types"""
    return {
        "types": [
            {"type": "scene", "pl": "Scena", "description": "Ilustracja sceny fabularnej"},
            {"type": "character_portrait", "pl": "Portret postaci", "description": "Portret pojedynczej postaci"},
            {"type": "landscape", "pl": "Krajobraz", "description": "Pejzaż, sceneria"},
            {"type": "object", "pl": "Przedmiot", "description": "Artefakt, ważny przedmiot"},
            {"type": "map", "pl": "Mapa", "description": "Mapa świata/lokacji"},
            {"type": "chapter_header", "pl": "Nagłówek rozdziału", "description": "Dekoracyjny nagłówek"},
            {"type": "spot_illustration", "pl": "Wstawka", "description": "Mała ilustracja dekoracyjna"},
            {"type": "full_page", "pl": "Pełna strona", "description": "Ilustracja na całą stronę"},
            {"type": "cover", "pl": "Okładka", "description": "Projekt okładki"}
        ]
    }


@router.get("/providers")
async def get_image_providers() -> Dict[str, Any]:
    """Get available image generation providers"""
    return {
        "providers": [
            {"provider": "openai_dalle", "name": "DALL-E 3", "status": "active"},
            {"provider": "stability_ai", "name": "Stability AI", "status": "coming_soon"},
            {"provider": "midjourney", "name": "Midjourney", "status": "coming_soon"},
            {"provider": "replicate", "name": "Replicate", "status": "coming_soon"}
        ]
    }


@router.post("/extract-scenes")
async def extract_scenes(request: ExtractScenesRequest) -> Dict[str, Any]:
    """
    Extract illustratable scenes from a chapter.

    Returns scenes ranked by visual interest and narrative importance.
    """
    pipeline = get_illustration_pipeline()

    try:
        genre = GenreType(request.genre.upper())
    except ValueError:
        genre = GenreType.DRAMA

    scenes = await pipeline.extract_illustratable_scenes(
        chapter_text=request.chapter_text,
        chapter_number=request.chapter_number,
        max_scenes=request.max_scenes,
        genre=genre
    )

    return {
        "success": True,
        "chapter_number": request.chapter_number,
        "scenes": [s.to_dict() for s in scenes]
    }


@router.post("/styles/create")
async def create_style(request: CreateStyleRequest) -> Dict[str, Any]:
    """
    Create a visual style for a project based on genre.
    """
    pipeline = get_illustration_pipeline()

    try:
        genre = GenreType(request.genre.upper())
    except ValueError:
        genre = GenreType.DRAMA

    style = pipeline.create_visual_style(
        name=request.name,
        genre=genre,
        customizations=request.customizations
    )

    return {
        "success": True,
        "style": style.to_dict()
    }


@router.get("/styles/{style_name}")
async def get_style(style_name: str) -> Dict[str, Any]:
    """Get a specific visual style"""
    pipeline = get_illustration_pipeline()
    style = pipeline.get_style(style_name)

    if not style:
        raise HTTPException(status_code=404, detail=f"Style not found: {style_name}")

    return {
        "style": style.to_dict()
    }


@router.post("/plan/create")
async def create_illustration_plan(request: CreatePlanRequest) -> Dict[str, Any]:
    """
    Create an illustration plan for an entire book.

    Returns estimated costs, time, and list of scenes to illustrate.
    """
    pipeline = get_illustration_pipeline()

    try:
        genre = GenreType(request.genre.upper())
    except ValueError:
        genre = GenreType.DRAMA

    plan = await pipeline.create_illustration_plan(
        project_id=request.project_id,
        chapters=request.chapters,
        genre=genre,
        illustrations_per_chapter=request.illustrations_per_chapter,
        include_character_portraits=request.include_character_portraits,
        include_maps=request.include_maps,
        include_chapter_headers=request.include_chapter_headers,
        character_list=request.character_list
    )

    return {
        "success": True,
        "plan": plan.to_dict()
    }


# =============================================================================
# CHARACTER VISUAL SYSTEM ENDPOINTS
# =============================================================================

@router.post("/characters/visual-profile")
async def generate_visual_profile(request: GenerateVisualProfileRequest) -> Dict[str, Any]:
    """
    Generate a detailed visual profile for a character.

    Creates comprehensive appearance description for consistent illustrations.
    """
    system = get_character_visual_system()

    try:
        genre = GenreType(request.genre.upper())
    except ValueError:
        genre = GenreType.DRAMA

    profile = await system.generate_visual_profile(
        character_name=request.character_name,
        character_description=request.character_description,
        genre=genre
    )

    return {
        "success": True,
        "profile": profile.to_dict(),
        "full_description": profile.get_full_description()
    }


@router.get("/characters/{character_name}/profile")
async def get_character_profile(character_name: str) -> Dict[str, Any]:
    """Get visual profile for a character"""
    system = get_character_visual_system()
    profile = system.get_profile(character_name)

    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile not found: {character_name}")

    return {
        "profile": profile.to_dict(),
        "full_description": profile.get_full_description()
    }


@router.get("/characters")
async def list_character_profiles(skip: int = 0, limit: int = 100) -> Dict[str, Any]:
    """List all character visual profiles"""
    system = get_character_visual_system()
    profiles = system.list_profiles()
    paginated = profiles[skip:skip + limit]

    return {
        "characters": paginated,
        "count": len(paginated),
        "total": len(profiles)
    }


@router.post("/characters/appearance-change")
async def register_appearance_change(request: RegisterAppearanceChangeRequest) -> Dict[str, Any]:
    """
    Register an appearance change for a character.

    Use this when a character's appearance changes (injury, aging, transformation, etc.)
    """
    system = get_character_visual_system()

    try:
        change_type = AppearanceChangeType(request.change_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid change type: {request.change_type}")

    success = system.register_appearance_change(
        character_name=request.character_name,
        change_type=change_type,
        chapter_number=request.chapter_number,
        description=request.description,
        affected_features=request.affected_features,
        is_permanent=request.is_permanent,
        revert_chapter=request.revert_chapter
    )

    if not success:
        raise HTTPException(status_code=404, detail=f"Character not found: {request.character_name}")

    return {
        "success": True,
        "message": f"Appearance change registered for {request.character_name}"
    }


@router.post("/characters/prompt")
async def get_character_prompt(request: GetPromptRequest) -> Dict[str, Any]:
    """
    Get illustration prompt for a character at a specific chapter.

    Automatically applies appearance changes up to that chapter.
    """
    system = get_character_visual_system()

    prompt = system.get_illustration_prompt(
        character_name=request.character_name,
        chapter_number=request.chapter_number,
        emotional_state=request.emotional_state,
        specific_outfit=request.specific_outfit,
        action=request.action
    )

    if prompt is None:
        raise HTTPException(status_code=404, detail=f"Character not found: {request.character_name}")

    return {
        "character_name": request.character_name,
        "chapter_number": request.chapter_number,
        "prompt": prompt
    }


@router.get("/characters/{character_name}/reference-sheets")
async def get_reference_sheet_prompts(character_name: str) -> Dict[str, Any]:
    """
    Get prompts for generating a character reference sheet.

    Returns prompts for: front view, side profile, full body, expressions, outfits.
    """
    system = get_character_visual_system()

    sheets = await system.generate_reference_sheet_prompts(character_name)

    if not sheets:
        raise HTTPException(status_code=404, detail=f"Character not found: {character_name}")

    return {
        "character_name": character_name,
        "reference_sheets": sheets
    }


@router.post("/characters/validate-consistency")
async def validate_consistency(request: ValidateConsistencyRequest) -> Dict[str, Any]:
    """
    Validate that a scene description is consistent with character visual profiles.
    """
    system = get_character_visual_system()

    result = await system.validate_scene_consistency(
        scene_description=request.scene_description,
        characters_in_scene=request.characters_in_scene,
        chapter_number=request.chapter_number
    )

    return {
        "success": True,
        "validation": result
    }


@router.get("/characters/export-all")
async def export_all_profiles() -> Dict[str, Any]:
    """Export all character visual profiles"""
    system = get_character_visual_system()

    return {
        "profiles": system.export_all_profiles()
    }


@router.get("/appearance-change-types")
async def get_appearance_change_types() -> Dict[str, Any]:
    """Get all appearance change types"""
    return {
        "change_types": [
            {"type": "injury", "pl": "Rana", "description": "Blizna, rana, obrażenie"},
            {"type": "aging", "pl": "Starzenie", "description": "Zmiany związane z wiekiem"},
            {"type": "transformation", "pl": "Transformacja", "description": "Magiczna lub fizyczna przemiana"},
            {"type": "disguise", "pl": "Przebranie", "description": "Tymczasowa zmiana wyglądu"},
            {"type": "emotional_state", "pl": "Stan emocjonalny", "description": "Zmiana wyrazu twarzy"},
            {"type": "clothing_change", "pl": "Zmiana ubioru", "description": "Nowy strój"},
            {"type": "hair_change", "pl": "Zmiana fryzury", "description": "Nowa fryzura lub kolor włosów"},
            {"type": "weight_change", "pl": "Zmiana wagi", "description": "Przybranie lub utrata wagi"}
        ]
    }
