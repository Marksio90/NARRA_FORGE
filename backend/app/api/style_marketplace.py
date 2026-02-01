"""
API Endpoints dla Style Marketplace - NarraForge 3.0
Marketplace stylów pisania AI
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

from app.services.style_marketplace import (
    style_marketplace_service,
    StyleCategory,
    StyleTier,
    LicenseType
)

router = APIRouter(prefix="/style-marketplace")


class PurchaseStyleRequest(BaseModel):
    """Request do zakupu stylu"""
    user_id: str = Field(..., description="ID użytkownika")
    style_id: str = Field(..., description="ID stylu do zakupu")
    payment_method: str = Field(..., description="Metoda płatności")


class AddReviewRequest(BaseModel):
    """Request do dodania recenzji"""
    user_id: str = Field(..., description="ID użytkownika")
    user_name: str = Field(..., description="Nazwa użytkownika")
    style_id: str = Field(..., description="ID stylu")
    rating: int = Field(..., ge=1, le=5, description="Ocena (1-5)")
    title: str = Field(..., min_length=3, max_length=100, description="Tytuł recenzji")
    content: str = Field(..., min_length=10, max_length=2000, description="Treść recenzji")


class CreateCustomStyleRequest(BaseModel):
    """Request do tworzenia niestandardowego stylu"""
    creator_id: str = Field(..., description="ID twórcy")
    creator_name: str = Field(..., description="Nazwa twórcy")
    name: str = Field(..., min_length=3, max_length=100, description="Nazwa stylu")
    description: str = Field(..., min_length=20, max_length=500, description="Opis stylu")
    profile: Dict[str, Any] = Field(..., description="Profil stylu")
    sample_text: str = Field(..., min_length=50, max_length=1000, description="Przykładowy tekst")
    price: float = Field(..., ge=0, le=100, description="Cena (0 dla darmowych)")
    tags: List[str] = Field(..., min_items=1, max_items=10, description="Tagi")
    compatibility: List[str] = Field(..., description="Kompatybilne gatunki")


@router.get("/browse")
async def browse_styles(
    category: Optional[str] = Query(None, description="Kategoria stylu"),
    tier: Optional[str] = Query(None, description="Poziom stylu"),
    min_rating: float = Query(0.0, ge=0, le=5, description="Minimalna ocena"),
    max_price: Optional[float] = Query(None, ge=0, description="Maksymalna cena"),
    tags: Optional[str] = Query(None, description="Tagi (oddzielone przecinkami)"),
    search: Optional[str] = Query(None, description="Wyszukiwanie tekstowe"),
    sort_by: str = Query("popularity", description="Sortowanie (popularity, rating, price, newest)"),
    page: int = Query(1, ge=1, description="Strona"),
    page_size: int = Query(20, ge=1, le=100, description="Rozmiar strony")
):
    """
    Przegląda style w marketplace.

    Umożliwia filtrowanie, wyszukiwanie i sortowanie stylów.
    """
    try:
        # Walidacja kategorii
        category_enum = None
        if category:
            try:
                category_enum = StyleCategory(category.lower())
            except ValueError:
                pass

        # Walidacja tier
        tier_enum = None
        if tier:
            try:
                tier_enum = StyleTier(tier.lower())
            except ValueError:
                pass

        # Parse tags
        tags_list = None
        if tags:
            tags_list = [t.strip() for t in tags.split(",")]

        result = await style_marketplace_service.browse_styles(
            category=category_enum,
            tier=tier_enum,
            min_rating=min_rating,
            max_price=max_price,
            tags=tags_list,
            search_query=search,
            sort_by=sort_by,
            page=page,
            page_size=page_size
        )

        return {
            "success": True,
            **result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/featured")
async def get_featured_styles():
    """
    Pobiera wyróżnione style.

    Zwraca listę najlepszych, zweryfikowanych stylów.
    """
    try:
        featured = await style_marketplace_service.get_featured_styles()
        return {
            "success": True,
            "styles": featured,
            "count": len(featured)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/style/{style_id}")
async def get_style_details(style_id: str):
    """
    Pobiera szczegóły konkretnego stylu.
    """
    style = await style_marketplace_service.get_style(style_id)

    if not style:
        raise HTTPException(status_code=404, detail=f"Styl nie znaleziony: {style_id}")

    return {
        "success": True,
        "style": style
    }


@router.post("/purchase")
async def purchase_style(request: PurchaseStyleRequest):
    """
    Realizuje zakup stylu.

    Przetwarza płatność i dodaje styl do biblioteki użytkownika.
    """
    try:
        result = await style_marketplace_service.purchase_style(
            user_id=request.user_id,
            style_id=request.style_id,
            payment_method=request.payment_method
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/library/{user_id}")
async def get_user_library(user_id: str):
    """
    Pobiera bibliotekę stylów użytkownika.

    Zwraca wszystkie zakupione i dostępne style.
    """
    try:
        library = await style_marketplace_service.get_user_library(user_id)
        return {
            "success": True,
            "library": library,
            "count": len(library)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review")
async def add_review(request: AddReviewRequest):
    """
    Dodaje recenzję stylu.

    Użytkownik może ocenić i opisać swoje doświadczenia ze stylem.
    """
    try:
        result = await style_marketplace_service.add_review(
            user_id=request.user_id,
            user_name=request.user_name,
            style_id=request.style_id,
            rating=request.rating,
            title=request.title,
            content=request.content
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/style/{style_id}/reviews")
async def get_style_reviews(
    style_id: str,
    page: int = Query(1, ge=1, description="Strona"),
    page_size: int = Query(10, ge=1, le=50, description="Rozmiar strony")
):
    """
    Pobiera recenzje stylu.
    """
    try:
        result = await style_marketplace_service.get_style_reviews(
            style_id=style_id,
            page=page,
            page_size=page_size
        )
        return {
            "success": True,
            **result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create")
async def create_custom_style(request: CreateCustomStyleRequest):
    """
    Tworzy niestandardowy styl użytkownika.

    Pozwala twórcom stworzyć i opcjonalnie sprzedawać własne style.
    """
    try:
        result = await style_marketplace_service.create_custom_style(
            creator_id=request.creator_id,
            creator_name=request.creator_name,
            name=request.name,
            description=request.description,
            profile=request.profile,
            sample_text=request.sample_text,
            price=request.price,
            tags=request.tags,
            compatibility=request.compatibility
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/style/{style_id}/prompt")
async def get_style_prompt(
    style_id: str,
    user_id: str = Query(..., description="ID użytkownika (dla weryfikacji zakupu)")
):
    """
    Pobiera szablon promptu dla stylu.

    Dostępne tylko dla zakupionych stylów lub darmowych.
    """
    # Sprawdź czy styl istnieje
    style = await style_marketplace_service.get_style(style_id)
    if not style:
        raise HTTPException(status_code=404, detail=f"Styl nie znaleziony: {style_id}")

    # Sprawdź czy darmowy lub zakupiony
    if style["price"] > 0:
        library = await style_marketplace_service.get_user_library(user_id)
        if not any(item["style"]["style_id"] == style_id for item in library):
            raise HTTPException(
                status_code=403,
                detail="Musisz zakupić ten styl, aby uzyskać dostęp do promptu"
            )

    prompt_data = await style_marketplace_service.get_style_prompt(style_id)
    return {
        "success": True,
        "prompt_data": prompt_data
    }


@router.get("/categories")
async def get_categories():
    """
    Pobiera listę kategorii stylów.
    """
    categories = style_marketplace_service.get_categories()
    return {
        "success": True,
        "categories": categories
    }


@router.get("/tiers")
async def get_tiers():
    """
    Pobiera listę poziomów (tier) stylów.
    """
    tiers = style_marketplace_service.get_tiers()
    return {
        "success": True,
        "tiers": tiers
    }


@router.get("/search/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=2, description="Fraza wyszukiwania")
):
    """
    Pobiera sugestie wyszukiwania.
    """
    try:
        # Przeszukaj style
        result = await style_marketplace_service.browse_styles(
            search_query=query,
            page_size=5
        )

        suggestions = [
            {
                "style_id": s["style_id"],
                "name": s["name"],
                "category": s["category"],
                "rating": s["rating"]
            }
            for s in result["styles"]
        ]

        return {
            "success": True,
            "suggestions": suggestions,
            "query": query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending_styles(
    period: str = Query("week", description="Okres (day, week, month)")
):
    """
    Pobiera popularne style z ostatniego okresu.
    """
    try:
        # W pełnej implementacji filtrowanie po dacie
        result = await style_marketplace_service.browse_styles(
            sort_by="popularity",
            page_size=10
        )

        return {
            "success": True,
            "trending": result["styles"],
            "period": period
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-genre/{genre}")
async def get_styles_by_genre(genre: str):
    """
    Pobiera style kompatybilne z danym gatunkiem.
    """
    try:
        result = await style_marketplace_service.browse_styles(
            tags=[genre],
            sort_by="rating",
            page_size=20
        )

        return {
            "success": True,
            "genre": genre,
            "styles": result["styles"],
            "count": result["total_count"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/free")
async def get_free_styles():
    """
    Pobiera wszystkie darmowe style.
    """
    try:
        result = await style_marketplace_service.browse_styles(
            tier=StyleTier.FREE,
            sort_by="rating"
        )

        return {
            "success": True,
            "styles": result["styles"],
            "count": result["total_count"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/premium")
async def get_premium_styles():
    """
    Pobiera style premium i ekskluzywne.
    """
    try:
        premium = await style_marketplace_service.browse_styles(
            tier=StyleTier.PREMIUM,
            sort_by="rating"
        )

        exclusive = await style_marketplace_service.browse_styles(
            tier=StyleTier.EXCLUSIVE,
            sort_by="rating"
        )

        all_premium = premium["styles"] + exclusive["styles"]

        return {
            "success": True,
            "styles": all_premium,
            "count": len(all_premium)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare")
async def compare_styles(
    style_ids: str = Query(..., description="ID stylów do porównania (oddzielone przecinkami)")
):
    """
    Porównuje wybrane style.
    """
    try:
        ids = [sid.strip() for sid in style_ids.split(",")]

        if len(ids) < 2:
            raise HTTPException(status_code=400, detail="Potrzeba minimum 2 stylów do porównania")

        if len(ids) > 5:
            raise HTTPException(status_code=400, detail="Maksymalnie 5 stylów do porównania")

        styles = []
        for sid in ids:
            style = await style_marketplace_service.get_style(sid)
            if style:
                styles.append(style)

        if len(styles) < 2:
            raise HTTPException(status_code=400, detail="Nie znaleziono wystarczającej liczby stylów")

        # Przygotuj porównanie
        comparison = {
            "styles": styles,
            "comparison_matrix": {
                "vocabulary_complexity": [s["profile"]["vocabulary_complexity"] for s in styles],
                "emotional_intensity": [s["profile"]["emotional_intensity"] for s in styles],
                "description_density": [s["profile"]["description_density"] for s in styles],
                "pacing": [s["profile"]["pacing"] for s in styles],
                "dialogue_style": [s["profile"]["dialogue_style"] for s in styles]
            },
            "price_comparison": [s["price"] for s in styles],
            "rating_comparison": [s["rating"] for s in styles]
        }

        return {
            "success": True,
            "comparison": comparison
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
