"""
Cover Art API - NarraForge 3.0 Phase 2

Endpoints for AI cover art generation and branding.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.cover_art_generator import (
    get_cover_art_generator,
    CoverStyle,
    CoverMood,
    CoverFormat,
    ColorPalette
)
from app.models.project import GenreType

router = APIRouter(prefix="/covers", tags=["AI Cover Art"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class GenerateConceptRequest(BaseModel):
    """Request for generating cover concept"""
    title: str
    author: str
    genre: str
    book_summary: str
    target_audience: str = "adult readers"
    style_preference: Optional[str] = None


class GeneratePromptRequest(BaseModel):
    """Request for generating cover prompt"""
    concept_id: str
    format: str = "ebook"
    include_text: bool = False


class GenerateCoverRequest(BaseModel):
    """Request for generating cover"""
    concept_id: str
    format: str = "ebook"
    variant: str = "A"


class GenerateVariantsRequest(BaseModel):
    """Request for generating cover variants"""
    concept_id: str
    num_variants: int = 3
    format: str = "ebook"


class QuickGenerateRequest(BaseModel):
    """Request for quick cover generation"""
    title: str
    author: str
    genre: str
    book_summary: str
    format: str = "ebook"


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/styles")
async def get_cover_styles() -> Dict[str, Any]:
    """Get all available cover styles"""
    return {
        "styles": [
            {"style": "illustrated", "pl": "Ilustrowana", "description": "Artystyczna ilustracja"},
            {"style": "photographic", "pl": "Fotograficzna", "description": "Realistyczna fotografia"},
            {"style": "abstract", "pl": "Abstrakcyjna", "description": "Abstrakcyjne formy i kolory"},
            {"style": "minimalist", "pl": "Minimalistyczna", "description": "Proste, czyste linie"},
            {"style": "typographic", "pl": "Typograficzna", "description": "Dominacja tekstu i czcionek"},
            {"style": "symbolic", "pl": "Symboliczna", "description": "Symboliczne przedstawienie"},
            {"style": "character_focused", "pl": "Postać", "description": "Skupienie na postaci"},
            {"style": "landscape", "pl": "Krajobraz", "description": "Sceneria i pejzaż"},
            {"style": "object_focused", "pl": "Przedmiot", "description": "Kluczowy przedmiot"},
            {"style": "collage", "pl": "Kolaż", "description": "Połączenie elementów"}
        ]
    }


@router.get("/moods")
async def get_cover_moods() -> Dict[str, Any]:
    """Get all cover moods"""
    return {
        "moods": [
            {"mood": "dark", "pl": "Ciemny"},
            {"mood": "light", "pl": "Jasny"},
            {"mood": "mysterious", "pl": "Tajemniczy"},
            {"mood": "romantic", "pl": "Romantyczny"},
            {"mood": "dramatic", "pl": "Dramatyczny"},
            {"mood": "whimsical", "pl": "Kapryśny"},
            {"mood": "elegant", "pl": "Elegancki"},
            {"mood": "intense", "pl": "Intensywny"},
            {"mood": "serene", "pl": "Spokojny"},
            {"mood": "ominous", "pl": "Złowieszczy"}
        ]
    }


@router.get("/formats")
async def get_cover_formats() -> Dict[str, Any]:
    """Get all cover formats"""
    return {
        "formats": [
            {"format": "ebook", "dimensions": "1600x2560", "description": "Format e-book"},
            {"format": "paperback", "dimensions": "1800x2700", "description": "Miękka oprawa (6x9 inch)"},
            {"format": "hardcover", "dimensions": "1800x2700", "description": "Twarda oprawa"},
            {"format": "audiobook", "dimensions": "3000x3000", "description": "Kwadratowy format audiobooka"},
            {"format": "social_media", "dimensions": "1200x1200", "description": "Media społecznościowe"},
            {"format": "print_ready", "dimensions": "1875x2625", "description": "Gotowy do druku (300 DPI)"}
        ]
    }


@router.get("/palettes")
async def get_color_palettes() -> Dict[str, Any]:
    """Get all color palettes"""
    return {
        "palettes": [
            {"palette": "warm", "pl": "Ciepła", "colors": ["#FF6B6B", "#FFA500", "#FFD700"]},
            {"palette": "cool", "pl": "Chłodna", "colors": ["#4ECDC4", "#45B7D1", "#96CEB4"]},
            {"palette": "monochrome", "pl": "Monochromatyczna", "colors": ["#2C3E50", "#7F8C8D", "#ECF0F1"]},
            {"palette": "complementary", "pl": "Dopełniająca", "colors": ["#E74C3C", "#3498DB"]},
            {"palette": "dark_academia", "pl": "Dark Academia", "colors": ["#2C1810", "#8B4513", "#D2691E"]},
            {"palette": "pastel", "pl": "Pastelowa", "colors": ["#FFB6C1", "#E6E6FA", "#B0E0E6"]},
            {"palette": "neon", "pl": "Neonowa", "colors": ["#FF00FF", "#00FFFF", "#FFFF00"]},
            {"palette": "earthy", "pl": "Ziemista", "colors": ["#8B7355", "#556B2F", "#A0522D"]}
        ]
    }


@router.get("/genre-recommendations/{genre}")
async def get_genre_recommendations(genre: str) -> Dict[str, Any]:
    """Get cover recommendations for a specific genre"""
    from app.services.cover_art_generator import GENRE_COVER_PROFILES

    try:
        genre_type = GenreType(genre.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid genre: {genre}")

    profile = GENRE_COVER_PROFILES.get(genre_type, {})

    return {
        "genre": genre,
        "recommended_styles": [s.value for s in profile.get("recommended_styles", [])],
        "moods": [m.value for m in profile.get("moods", [])],
        "color_palettes": [p.value for p in profile.get("color_palettes", [])],
        "typical_elements": profile.get("typical_elements", []),
        "typography": profile.get("typography", "")
    }


@router.post("/concept/generate")
async def generate_concept(request: GenerateConceptRequest) -> Dict[str, Any]:
    """
    Generate a cover concept based on book information.

    Returns a detailed concept including visual elements, style, colors, etc.
    """
    generator = get_cover_art_generator()

    try:
        genre = GenreType(request.genre.upper())
    except ValueError:
        genre = GenreType.DRAMA

    style_preference = None
    if request.style_preference:
        try:
            style_preference = CoverStyle(request.style_preference)
        except ValueError:
            pass

    concept = await generator.generate_cover_concept(
        title=request.title,
        author=request.author,
        genre=genre,
        book_summary=request.book_summary,
        target_audience=request.target_audience,
        style_preference=style_preference
    )

    return {
        "success": True,
        "concept": concept.to_dict()
    }


@router.get("/concept/{concept_id}")
async def get_concept(concept_id: str) -> Dict[str, Any]:
    """Get a specific cover concept"""
    generator = get_cover_art_generator()
    concept = generator.get_concept(concept_id)

    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept not found: {concept_id}")

    return {
        "concept": concept.to_dict()
    }


@router.post("/prompt/generate")
async def generate_prompt(request: GeneratePromptRequest) -> Dict[str, Any]:
    """
    Generate a cover generation prompt from a concept.
    """
    generator = get_cover_art_generator()

    concept = generator.get_concept(request.concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept not found: {request.concept_id}")

    try:
        format = CoverFormat(request.format)
    except ValueError:
        format = CoverFormat.EBOOK

    prompt = await generator.generate_cover_prompt(
        concept=concept,
        format=format,
        include_text=request.include_text
    )

    return {
        "success": True,
        "prompt": prompt.to_dict()
    }


@router.post("/generate")
async def generate_cover(request: GenerateCoverRequest) -> Dict[str, Any]:
    """
    Generate a cover image from a concept.
    """
    generator = get_cover_art_generator()

    concept = generator.get_concept(request.concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept not found: {request.concept_id}")

    try:
        format = CoverFormat(request.format)
    except ValueError:
        format = CoverFormat.EBOOK

    prompt = await generator.generate_cover_prompt(concept, format)
    cover = await generator.generate_cover(prompt, request.variant)

    return {
        "success": True,
        "cover": cover.to_dict()
    }


@router.post("/generate-variants")
async def generate_variants(request: GenerateVariantsRequest) -> Dict[str, Any]:
    """
    Generate multiple cover variants for a concept.
    """
    generator = get_cover_art_generator()

    concept = generator.get_concept(request.concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept not found: {request.concept_id}")

    try:
        format = CoverFormat(request.format)
    except ValueError:
        format = CoverFormat.EBOOK

    covers = await generator.generate_cover_variants(
        concept=concept,
        num_variants=request.num_variants,
        format=format
    )

    return {
        "success": True,
        "covers": [cover.to_dict() for cover in covers]
    }


@router.post("/quick-generate")
async def quick_generate(request: QuickGenerateRequest) -> Dict[str, Any]:
    """
    Quick generation - from book info to cover in one call.

    Generates concept, prompt, and cover in a single operation.
    """
    generator = get_cover_art_generator()

    try:
        format = CoverFormat(request.format)
    except ValueError:
        format = CoverFormat.EBOOK

    cover = await generator.quick_generate(
        title=request.title,
        author=request.author,
        genre=request.genre,
        book_summary=request.book_summary,
        format=format
    )

    return {
        "success": True,
        "cover": cover.to_dict()
    }


@router.get("/cover/{cover_id}")
async def get_cover(cover_id: str) -> Dict[str, Any]:
    """Get a specific generated cover"""
    generator = get_cover_art_generator()
    cover = generator.get_cover(cover_id)

    if not cover:
        raise HTTPException(status_code=404, detail=f"Cover not found: {cover_id}")

    return {
        "cover": cover.to_dict()
    }


@router.get("/concepts")
async def list_concepts(skip: int = 0, limit: int = 100) -> Dict[str, Any]:
    """List all cover concepts"""
    generator = get_cover_art_generator()
    concepts = generator.list_concepts()
    paginated = concepts[skip:skip + limit]

    return {
        "concepts": paginated,
        "total": len(concepts)
    }


@router.get("/covers")
async def list_covers(skip: int = 0, limit: int = 100) -> Dict[str, Any]:
    """List all generated covers"""
    generator = get_cover_art_generator()
    covers = generator.list_covers()
    paginated = covers[skip:skip + limit]

    return {
        "covers": paginated,
        "total": len(covers)
    }
