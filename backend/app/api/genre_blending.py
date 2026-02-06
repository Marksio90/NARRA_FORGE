"""
API Endpoints dla Dynamic Genre Blending - NarraForge 3.0
Inteligentne mieszanie gatunków literackich
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum

from app.services.genre_blending import (
    genre_blending_service,
    GenreType,
    BlendedGenreProfile
)

router = APIRouter(prefix="/genre-blending")


class BlendStyle(str, Enum):
    """Dostępne style mieszania gatunków"""
    SEAMLESS = "seamless"
    LAYERED = "layered"
    ALTERNATING = "alternating"
    FUSION = "fusion"


class CreateBlendRequest(BaseModel):
    """Request do tworzenia nowego blendu gatunków"""
    primary_genre: str = Field(..., description="Główny gatunek")
    secondary_genres: List[str] = Field(..., description="Lista gatunków drugorzędnych")
    weights: Optional[Dict[str, float]] = Field(
        None,
        description="Opcjonalne wagi dla gatunków drugorzędnych (0-1)"
    )
    blend_style: BlendStyle = Field(
        BlendStyle.SEAMLESS,
        description="Styl mieszania gatunków"
    )


class GenreTransitionsRequest(BaseModel):
    """Request do generowania przejść między gatunkami"""
    blend_id: str = Field(..., description="ID blendu")
    chapter_count: int = Field(..., ge=1, le=100, description="Liczba rozdziałów")


class SceneBalanceRequest(BaseModel):
    """Request do sugestii balansu gatunków w scenie"""
    blend_id: str = Field(..., description="ID blendu")
    scene_type: str = Field(
        ...,
        description="Typ sceny (action, dialogue, romance, revelation, philosophical)"
    )
    emotional_target: str = Field(
        ...,
        description="Docelowa emocja (hope, fear, joy, sadness, love, wonder, etc.)"
    )


class CoherenceAnalysisRequest(BaseModel):
    """Request do analizy spójności gatunkowej"""
    blend_id: str = Field(..., description="ID blendu")
    chapter_content: str = Field(..., min_length=100, description="Treść rozdziału do analizy")


class BlendResponse(BaseModel):
    """Response z informacjami o blendzie"""
    success: bool
    blend_id: str
    name: str
    description: str
    source_genres: List[str]
    merged_elements: List[str]
    merged_themes: List[str]
    narrative_style: str
    emotional_spectrum: List[str]
    unique_characteristics: List[str]
    recommended_structure: Dict[str, Any]
    conflict_resolution_notes: List[str]


@router.post("/create", response_model=BlendResponse)
async def create_genre_blend(request: CreateBlendRequest):
    """
    Tworzy nowy blend gatunków literackich.

    Umożliwia łączenie wielu gatunków w unikalne hybrydy z automatycznym
    generowaniem rekomendacji dotyczących struktury narracyjnej.
    """
    try:
        # Walidacja gatunków
        try:
            primary = GenreType(request.primary_genre.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Nieznany gatunek: {request.primary_genre}"
            )

        secondary_genres = []
        for genre_str in request.secondary_genres:
            try:
                secondary_genres.append(GenreType(genre_str.lower()))
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Nieznany gatunek: {genre_str}"
                )

        # Konwertuj wagi
        weights = None
        if request.weights:
            weights = {}
            for genre_str, weight in request.weights.items():
                try:
                    genre = GenreType(genre_str.lower())
                    weights[genre] = weight
                except ValueError:
                    pass

        # Utwórz blend
        blend = await genre_blending_service.create_genre_blend(
            primary_genre=primary,
            secondary_genres=secondary_genres,
            weights=weights,
            blend_style=request.blend_style.value
        )

        return BlendResponse(
            success=True,
            blend_id=blend.blend_id,
            name=blend.name,
            description=blend.description,
            source_genres=[g.value for g in blend.source_genres],
            merged_elements=blend.merged_elements,
            merged_themes=blend.merged_themes,
            narrative_style=blend.narrative_style,
            emotional_spectrum=blend.emotional_spectrum,
            unique_characteristics=blend.unique_characteristics,
            recommended_structure=blend.recommended_structure,
            conflict_resolution_notes=blend.conflict_resolution_notes
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/genres")
async def get_available_genres():
    """
    Pobiera listę wszystkich dostępnych gatunków z ich profilami.

    Zwraca informacje o kompatybilności między gatunkami
    i ich charakterystykach.
    """
    try:
        genres = genre_blending_service.get_available_genres()
        return {
            "success": True,
            "genres": genres,
            "total_count": len(genres)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blend/{blend_id}")
async def get_blend(blend_id: str):
    """
    Pobiera szczegóły konkretnego blendu po ID.
    """
    blend = genre_blending_service.get_active_blend(blend_id)

    if not blend:
        raise HTTPException(status_code=404, detail=f"Blend nie znaleziony: {blend_id}")

    return {
        "success": True,
        "blend": {
            "blend_id": blend.blend_id,
            "name": blend.name,
            "description": blend.description,
            "source_genres": [g.value for g in blend.source_genres],
            "ratios": {
                "primary_genre": blend.ratios.primary_genre.value,
                "primary_weight": blend.ratios.primary_weight,
                "secondary_genres": {g.value: w for g, w in blend.ratios.secondary_genres.items()},
                "blend_style": blend.ratios.blend_style,
                "transition_smoothness": blend.ratios.transition_smoothness
            },
            "merged_elements": blend.merged_elements,
            "merged_themes": blend.merged_themes,
            "narrative_style": blend.narrative_style,
            "emotional_spectrum": blend.emotional_spectrum,
            "unique_characteristics": blend.unique_characteristics,
            "recommended_structure": blend.recommended_structure,
            "conflict_resolution_notes": blend.conflict_resolution_notes,
            "created_at": blend.created_at.isoformat()
        }
    }


@router.get("/blends")
async def list_blends():
    """
    Listuje wszystkie aktywne blendy gatunków.
    """
    try:
        blends = genre_blending_service.list_active_blends()
        return {
            "success": True,
            "blends": blends,
            "total_count": len(blends)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transitions")
async def get_genre_transitions(request: GenreTransitionsRequest):
    """
    Generuje plan przejść między gatunkami dla rozdziałów.

    Na podstawie blendu i liczby rozdziałów tworzy mapę
    przejść gatunkowych z rekomendacjami.
    """
    blend = genre_blending_service.get_active_blend(request.blend_id)

    if not blend:
        raise HTTPException(status_code=404, detail=f"Blend nie znaleziony: {request.blend_id}")

    try:
        transitions = await genre_blending_service.get_genre_transitions(
            blend=blend,
            chapter_count=request.chapter_count
        )

        return {
            "success": True,
            "blend_id": request.blend_id,
            "chapter_count": request.chapter_count,
            "transitions": [
                {
                    "from_genre": t.from_genre.value,
                    "to_genre": t.to_genre.value,
                    "transition_type": t.transition_type,
                    "chapter_range": list(t.chapter_range),
                    "trigger_elements": t.trigger_elements,
                    "smoothness_score": t.smoothness_score
                }
                for t in transitions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scene-balance")
async def suggest_scene_balance(request: SceneBalanceRequest):
    """
    Sugeruje balans gatunków dla konkretnej sceny.

    Analizuje typ sceny i docelową emocję, aby zaproponować
    optymalne proporcje elementów gatunkowych.
    """
    blend = genre_blending_service.get_active_blend(request.blend_id)

    if not blend:
        raise HTTPException(status_code=404, detail=f"Blend nie znaleziony: {request.blend_id}")

    try:
        recommendations = await genre_blending_service.suggest_scene_genre_balance(
            blend=blend,
            scene_type=request.scene_type,
            emotional_target=request.emotional_target
        )

        return {
            "success": True,
            "blend_id": request.blend_id,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-coherence")
async def analyze_coherence(request: CoherenceAnalysisRequest):
    """
    Analizuje spójność gatunkową rozdziału.

    Sprawdza czy treść rozdziału zachowuje odpowiedni balans
    między zdefiniowanymi gatunkami w blendzie.
    """
    blend = genre_blending_service.get_active_blend(request.blend_id)

    if not blend:
        raise HTTPException(status_code=404, detail=f"Blend nie znaleziony: {request.blend_id}")

    try:
        analysis = await genre_blending_service.analyze_genre_coherence(
            blend=blend,
            chapter_content=request.chapter_content
        )

        return {
            "success": True,
            "blend_id": request.blend_id,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compatibility")
async def check_compatibility(
    primary: str = Query(..., description="Główny gatunek"),
    secondary: str = Query(..., description="Gatunek do sprawdzenia kompatybilności")
):
    """
    Sprawdza kompatybilność dwóch gatunków.

    Zwraca informacje czy gatunki są kompatybilne,
    konfliktowe, czy neutralne względem siebie.
    """
    try:
        primary_genre = GenreType(primary.lower())
        secondary_genre = GenreType(secondary.lower())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Nieznany gatunek: {e}")

    genres_info = genre_blending_service.get_available_genres()

    primary_info = next((g for g in genres_info if g["type"] == primary_genre.value), None)

    if not primary_info:
        raise HTTPException(status_code=404, detail=f"Brak profilu dla: {primary}")

    is_compatible = secondary_genre.value in primary_info.get("compatible_with", [])
    is_conflicting = secondary_genre.value in primary_info.get("conflicts_with", [])

    if is_compatible:
        relationship = "compatible"
        recommendation = "Doskonałe połączenie - gatunki naturalnie się uzupełniają"
    elif is_conflicting:
        relationship = "conflicting"
        recommendation = "Wymagające połączenie - potrzebne ostrożne przejścia i balansowanie"
    else:
        relationship = "neutral"
        recommendation = "Neutralne połączenie - możliwe do zrealizowania z odpowiednim planowaniem"

    return {
        "success": True,
        "primary_genre": primary_genre.value,
        "secondary_genre": secondary_genre.value,
        "relationship": relationship,
        "is_compatible": is_compatible,
        "is_conflicting": is_conflicting,
        "recommendation": recommendation
    }


@router.get("/suggestions/{primary_genre}")
async def get_blend_suggestions(primary_genre: str):
    """
    Sugeruje najlepsze kombinacje dla danego gatunku głównego.

    Zwraca listę rekomendowanych gatunków do połączenia
    wraz z przewidywanym efektem.
    """
    try:
        genre = GenreType(primary_genre.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Nieznany gatunek: {primary_genre}")

    genres_info = genre_blending_service.get_available_genres()
    primary_info = next((g for g in genres_info if g["type"] == genre.value), None)

    if not primary_info:
        raise HTTPException(status_code=404, detail=f"Brak profilu dla: {primary_genre}")

    suggestions = []

    # Dodaj kompatybilne gatunki jako główne sugestie
    for compatible in primary_info.get("compatible_with", []):
        compatible_info = next((g for g in genres_info if g["type"] == compatible), None)
        if compatible_info:
            suggestions.append({
                "genre": compatible,
                "compatibility": "high",
                "blend_potential": "excellent",
                "suggested_styles": ["seamless", "fusion"],
                "expected_result": f"Harmonijna fuzja {genre.value} i {compatible}"
            })

    # Dodaj neutralne jako średnie sugestie
    all_genres = [g["type"] for g in genres_info]
    compatible_list = primary_info.get("compatible_with", [])
    conflict_list = primary_info.get("conflicts_with", [])

    neutral = [g for g in all_genres if g not in compatible_list and g not in conflict_list and g != genre.value]

    for neutral_genre in neutral[:5]:  # Limit do 5
        suggestions.append({
            "genre": neutral_genre,
            "compatibility": "medium",
            "blend_potential": "good",
            "suggested_styles": ["layered", "alternating"],
            "expected_result": f"Interesujące połączenie {genre.value} i {neutral_genre}"
        })

    # Dodaj konfliktowe jako wyzwania
    for conflicting in primary_info.get("conflicts_with", [])[:3]:  # Limit do 3
        suggestions.append({
            "genre": conflicting,
            "compatibility": "challenging",
            "blend_potential": "experimental",
            "suggested_styles": ["alternating", "layered"],
            "expected_result": f"Eksperymentalne napięcie między {genre.value} i {conflicting}"
        })

    return {
        "success": True,
        "primary_genre": genre.value,
        "suggestions": suggestions,
        "total_count": len(suggestions)
    }
