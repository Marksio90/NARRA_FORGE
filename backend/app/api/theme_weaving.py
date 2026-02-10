"""
API Endpoints dla Subconscious Theme Weaving - NarraForge 3.0
Nieświadome wplatanie głębokich tematów w narrację
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum

from app.services.theme_weaving import (
    theme_weaving_service,
    ThemeCategory,
    WeavingIntensity,
    WeavingTechnique
)

router = APIRouter(prefix="/theme-weaving")


class CreateWeavingPlanRequest(BaseModel):
    """Request do tworzenia planu wplatania tematów"""
    project_id: str = Field(..., description="ID projektu")
    theme_ids: List[str] = Field(..., description="Lista ID tematów do wplecenia")
    chapter_count: int = Field(..., ge=1, le=100, description="Liczba rozdziałów")
    primary_theme_id: Optional[str] = Field(None, description="Opcjonalny główny temat")
    intensity: str = Field(
        "moderate",
        description="Intensywność wplatania (subtle, moderate, prominent, dominant)"
    )


class SubconsciousLayerRequest(BaseModel):
    """Request do tworzenia warstwy podświadomej"""
    project_id: str = Field(..., description="ID projektu")
    plan_id: str = Field(..., description="ID planu wplatania")
    depth_level: int = Field(3, ge=1, le=5, description="Poziom głębokości (1-5)")


class AnalyzePresenceRequest(BaseModel):
    """Request do analizy obecności tematów"""
    plan_id: str = Field(..., description="ID planu wplatania")
    chapter_content: str = Field(..., min_length=100, description="Treść rozdziału")
    chapter_number: int = Field(..., ge=1, description="Numer rozdziału")


class WeavingPlanResponse(BaseModel):
    """Response z planem wplatania"""
    success: bool
    plan_id: str
    project_id: str
    primary_theme: Dict[str, Any]
    secondary_themes: List[Dict[str, Any]]
    theme_arcs: Dict[str, Any]
    chapter_distribution_summary: Dict[int, int]
    recommended_techniques: Dict[str, List[str]]


@router.post("/plan/create", response_model=WeavingPlanResponse)
async def create_weaving_plan(request: CreateWeavingPlanRequest):
    """
    Tworzy plan wplatania tematów dla projektu.

    Generuje kompletny plan z łukami tematycznymi, dystrybucją
    w rozdziałach i rekomendowanymi technikami.
    """
    try:
        # Walidacja intensywności
        try:
            intensity = WeavingIntensity(request.intensity.lower())
        except ValueError:
            intensity = WeavingIntensity.MODERATE

        plan = await theme_weaving_service.create_weaving_plan(
            project_id=request.project_id,
            theme_ids=request.theme_ids,
            chapter_count=request.chapter_count,
            primary_theme_id=request.primary_theme_id,
            intensity_preference=intensity
        )

        # Przygotuj podsumowanie dystrybucji
        distribution_summary = {
            chapter: len(occurrences)
            for chapter, occurrences in plan.chapter_distribution.items()
        }

        # Konwertuj łuki tematyczne
        theme_arcs_dict = {}
        for theme_id, arc in plan.theme_arcs.items():
            theme_arcs_dict[theme_id] = {
                "introduction_chapter": arc.introduction_chapter,
                "climax_chapter": arc.climax_chapter,
                "resolution_type": arc.resolution_type,
                "total_occurrences": arc.total_occurrences,
                "development_points": [
                    {"chapter": dp[0], "description": dp[1]}
                    for dp in arc.development_points
                ]
            }

        return WeavingPlanResponse(
            success=True,
            plan_id=plan.plan_id,
            project_id=plan.project_id,
            primary_theme={
                "theme_id": plan.primary_theme.theme_id,
                "name": plan.primary_theme.name,
                "category": plan.primary_theme.category.value,
                "description": plan.primary_theme.description
            },
            secondary_themes=[
                {
                    "theme_id": t.theme_id,
                    "name": t.name,
                    "category": t.category.value
                }
                for t in plan.secondary_themes
            ],
            theme_arcs=theme_arcs_dict,
            chapter_distribution_summary=distribution_summary,
            recommended_techniques={
                tid: [tech.value for tech in techs]
                for tid, techs in plan.recommended_techniques.items()
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/themes")
async def get_available_themes(
    category: Optional[str] = Query(None, description="Filtruj po kategorii")
):
    """
    Pobiera listę wszystkich dostępnych tematów.

    Opcjonalnie filtruje po kategorii tematycznej.
    """
    try:
        themes = theme_weaving_service.get_available_themes()

        if category:
            try:
                cat = ThemeCategory(category.lower())
                themes = [t for t in themes if t["category"] == cat.value]
            except ValueError:
                pass

        return {
            "success": True,
            "themes": themes,
            "total_count": len(themes),
            "categories": [c.value for c in ThemeCategory]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/themes/{theme_id}")
async def get_theme_details(theme_id: str):
    """
    Pobiera szczegóły konkretnego tematu.
    """
    themes = theme_weaving_service.get_available_themes()
    theme = next((t for t in themes if t["theme_id"] == theme_id), None)

    if not theme:
        raise HTTPException(status_code=404, detail=f"Temat nie znaleziony: {theme_id}")

    return {
        "success": True,
        "theme": theme
    }


@router.get("/plan/{plan_id}")
async def get_weaving_plan(plan_id: str):
    """
    Pobiera szczegóły planu wplatania.
    """
    plan = theme_weaving_service.get_active_plan(plan_id)

    if not plan:
        raise HTTPException(status_code=404, detail=f"Plan nie znaleziony: {plan_id}")

    return {
        "success": True,
        "plan": {
            "plan_id": plan.plan_id,
            "project_id": plan.project_id,
            "created_at": plan.created_at.isoformat(),
            "themes": [
                {
                    "theme_id": t.theme_id,
                    "name": t.name,
                    "category": t.category.value,
                    "core_concepts": t.core_concepts,
                    "symbols": t.related_symbols
                }
                for t in plan.themes
            ],
            "primary_theme": {
                "theme_id": plan.primary_theme.theme_id,
                "name": plan.primary_theme.name
            },
            "theme_arcs": {
                tid: {
                    "introduction_chapter": arc.introduction_chapter,
                    "climax_chapter": arc.climax_chapter,
                    "resolution_type": arc.resolution_type,
                    "total_occurrences": arc.total_occurrences,
                    "intensity_curve": arc.intensity_curve
                }
                for tid, arc in plan.theme_arcs.items()
            }
        }
    }


@router.get("/plans")
async def list_weaving_plans(
    project_id: Optional[str] = Query(None, description="Filtruj po projekcie"),
    skip: int = 0,
    limit: int = 100
):
    """
    Listuje wszystkie aktywne plany wplatania.
    """
    try:
        plans = theme_weaving_service.list_active_plans()

        if project_id:
            plans = [p for p in plans if p["project_id"] == project_id]

        paginated = plans[skip:skip + limit]

        return {
            "success": True,
            "plans": paginated,
            "total_count": len(plans)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subconscious-layer")
async def create_subconscious_layer(request: SubconsciousLayerRequest):
    """
    Tworzy warstwę podświadomą dla narracji.

    Generuje ukryte znaczenia, sieci symboli i efekty
    na podświadomość czytelnika.
    """
    try:
        layer = await theme_weaving_service.create_subconscious_layer(
            project_id=request.project_id,
            plan_id=request.plan_id,
            depth_level=request.depth_level
        )

        return {
            "success": True,
            "layer": {
                "layer_id": layer.layer_id,
                "depth_level": layer.depth_level,
                "hidden_meanings": layer.hidden_meanings,
                "symbol_network": layer.symbol_network,
                "emotional_undercurrent": layer.emotional_undercurrent,
                "psychological_triggers": layer.psychological_triggers,
                "reader_subconscious_effects": layer.reader_subconscious_effects
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_theme_presence(request: AnalyzePresenceRequest):
    """
    Analizuje obecność tematów w treści rozdziału.

    Sprawdza czy tematy są odpowiednio reprezentowane
    i daje rekomendacje dotyczące poprawek.
    """
    try:
        analysis = await theme_weaving_service.analyze_theme_presence(
            plan_id=request.plan_id,
            chapter_content=request.chapter_content,
            chapter_number=request.chapter_number
        )

        return {
            "success": True,
            "analysis": analysis
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plan/{plan_id}/chapter/{chapter_number}")
async def get_chapter_guidance(plan_id: str, chapter_number: int):
    """
    Pobiera wytyczne dla konkretnego rozdziału.

    Zwraca oczekiwane wystąpienia tematów i rekomendowane
    techniki dla danego rozdziału.
    """
    plan = theme_weaving_service.get_active_plan(plan_id)

    if not plan:
        raise HTTPException(status_code=404, detail=f"Plan nie znaleziony: {plan_id}")

    occurrences = plan.chapter_distribution.get(chapter_number, [])

    return {
        "success": True,
        "chapter": chapter_number,
        "expected_occurrences": [
            {
                "theme_id": o.theme_id,
                "technique": o.technique.value,
                "intensity": o.intensity.value,
                "manifestation": o.manifestation,
                "context": o.context,
                "reader_perception": o.reader_perception
            }
            for o in occurrences
        ],
        "themes_active": list(set(o.theme_id for o in occurrences)),
        "total_occurrences": len(occurrences)
    }


@router.get("/techniques")
async def get_weaving_techniques():
    """
    Pobiera listę wszystkich technik wplatania.
    """
    techniques = [
        {
            "technique": WeavingTechnique.SYMBOLISM.value,
            "name": "Symbolizm",
            "description": "Używanie symboli do reprezentowania głębszych znaczeń",
            "subtlety": "high",
            "best_for": ["existential", "spiritual", "universal"]
        },
        {
            "technique": WeavingTechnique.DIALOGUE.value,
            "name": "Dialog",
            "description": "Wplatanie tematów przez rozmowy postaci",
            "subtlety": "medium",
            "best_for": ["moral", "social", "philosophical"]
        },
        {
            "technique": WeavingTechnique.IMAGERY.value,
            "name": "Obrazowanie",
            "description": "Tworzenie obrazów ewokujących emocje i znaczenia",
            "subtlety": "high",
            "best_for": ["psychological", "emotional", "spiritual"]
        },
        {
            "technique": WeavingTechnique.MOTIF.value,
            "name": "Motyw przewodni",
            "description": "Powracające elementy wzmacniające temat",
            "subtlety": "medium",
            "best_for": ["universal", "existential"]
        },
        {
            "technique": WeavingTechnique.METAPHOR.value,
            "name": "Metafora",
            "description": "Przenośnie łączące abstrakcyjne koncepty z konkretem",
            "subtlety": "medium",
            "best_for": ["existential", "philosophical"]
        },
        {
            "technique": WeavingTechnique.FORESHADOWING.value,
            "name": "Zapowiedź",
            "description": "Subtelne wskazówki przyszłych wydarzeń tematycznych",
            "subtlety": "high",
            "best_for": ["moral", "existential"]
        },
        {
            "technique": WeavingTechnique.CONTRAST.value,
            "name": "Kontrast",
            "description": "Zestawienie przeciwieństw uwypuklające temat",
            "subtlety": "low",
            "best_for": ["moral", "social"]
        },
        {
            "technique": WeavingTechnique.PARALLEL.value,
            "name": "Paralela",
            "description": "Równoległe wątki odzwierciedlające temat",
            "subtlety": "medium",
            "best_for": ["universal", "psychological"]
        },
        {
            "technique": WeavingTechnique.SUBTEXT.value,
            "name": "Podtekst",
            "description": "Ukryte znaczenia między wierszami",
            "subtlety": "very_high",
            "best_for": ["psychological", "philosophical", "existential"]
        },
        {
            "technique": WeavingTechnique.ATMOSPHERE.value,
            "name": "Atmosfera",
            "description": "Nastrój i ton oddający emocjonalną istotę tematu",
            "subtlety": "high",
            "best_for": ["emotional", "psychological", "spiritual"]
        }
    ]

    return {
        "success": True,
        "techniques": techniques,
        "total_count": len(techniques)
    }


@router.get("/categories")
async def get_theme_categories():
    """
    Pobiera listę kategorii tematycznych z opisami.
    """
    categories = [
        {
            "category": ThemeCategory.EXISTENTIAL.value,
            "name": "Egzystencjalne",
            "description": "Tematy dotyczące istnienia, sensu życia i tożsamości",
            "examples": ["tożsamość", "śmiertelność", "wolność vs przeznaczenie"]
        },
        {
            "category": ThemeCategory.MORAL.value,
            "name": "Moralne",
            "description": "Dylematy etyczne i kwestie dobra i zła",
            "examples": ["dobro i zło", "sprawiedliwość", "odpowiedzialność"]
        },
        {
            "category": ThemeCategory.PSYCHOLOGICAL.value,
            "name": "Psychologiczne",
            "description": "Tematy związane z psychiką i emocjami",
            "examples": ["trauma", "izolacja", "obsesja"]
        },
        {
            "category": ThemeCategory.SOCIAL.value,
            "name": "Społeczne",
            "description": "Tematy dotyczące relacji społecznych i struktur",
            "examples": ["władza", "przynależność", "wykluczenie"]
        },
        {
            "category": ThemeCategory.SPIRITUAL.value,
            "name": "Duchowe",
            "description": "Tematy wiary, transcendencji i duchowości",
            "examples": ["wiara", "odkupienie", "poszukiwanie sensu"]
        },
        {
            "category": ThemeCategory.PHILOSOPHICAL.value,
            "name": "Filozoficzne",
            "description": "Głębokie pytania o naturę rzeczywistości",
            "examples": ["prawda", "wolna wola", "natura ludzkości"]
        },
        {
            "category": ThemeCategory.EMOTIONAL.value,
            "name": "Emocjonalne",
            "description": "Tematy związane z uczuciami i relacjami",
            "examples": ["miłość", "strata", "nadzieja"]
        },
        {
            "category": ThemeCategory.UNIVERSAL.value,
            "name": "Uniwersalne",
            "description": "Ponadczasowe tematy wspólne dla ludzkości",
            "examples": ["transformacja", "poświęcenie", "poszukiwanie szczęścia"]
        }
    ]

    return {
        "success": True,
        "categories": categories,
        "total_count": len(categories)
    }


@router.get("/intensity-levels")
async def get_intensity_levels():
    """
    Pobiera poziomy intensywności wplatania.
    """
    levels = [
        {
            "level": WeavingIntensity.SUBTLE.value,
            "name": "Subtelny",
            "description": "Delikatne, prawie niewidoczne wplatanie - czytelnik odczuwa podświadomie",
            "reader_awareness": "unconscious",
            "recommended_for": "literatura wysokoartystyczna, subtelne przesłania"
        },
        {
            "level": WeavingIntensity.MODERATE.value,
            "name": "Umiarkowany",
            "description": "Zbalansowane wplatanie - uważny czytelnik zauważy, ale nie przeszkadza",
            "reader_awareness": "semi-conscious",
            "recommended_for": "większość utworów, standardowy poziom"
        },
        {
            "level": WeavingIntensity.PROMINENT.value,
            "name": "Wyraźny",
            "description": "Widoczne tematyczne elementy - czytelnik świadomie je rozpoznaje",
            "reader_awareness": "conscious",
            "recommended_for": "literatura tematyczna, jasne przesłanie"
        },
        {
            "level": WeavingIntensity.DOMINANT.value,
            "name": "Dominujący",
            "description": "Temat jest centralny i oczywisty - całość podporządkowana tematowi",
            "reader_awareness": "fully_conscious",
            "recommended_for": "alegoria, literatura zaangażowana, powieści z tezą"
        }
    ]

    return {
        "success": True,
        "levels": levels
    }
