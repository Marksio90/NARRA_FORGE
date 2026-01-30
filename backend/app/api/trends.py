"""
Trends API - NarraForge 3.0 Phase 3

Endpoints for Trend-Adaptive Content Generation.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.trend_adaptive import (
    get_trend_engine,
    MarketSegment,
    TrendCategory
)

router = APIRouter(prefix="/trends", tags=["Trend-Adaptive"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class AnalyzeTrendsRequest(BaseModel):
    """Request for trend analysis"""
    project_id: str
    genre: str
    target_segment: str = "mainstream"
    current_content: Optional[Dict[str, Any]] = None


class GetTrendingRequest(BaseModel):
    """Request for trending elements"""
    genre: str
    category: Optional[str] = None


class AnalyzeContentRequest(BaseModel):
    """Request for content trend analysis"""
    text: str
    genre: str


class SuggestElementsRequest(BaseModel):
    """Request for element suggestions"""
    genre: str
    existing_elements: List[str]


class ForecastRequest(BaseModel):
    """Request for trend forecast"""
    months_ahead: int = 6


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/categories")
async def get_trend_categories() -> Dict[str, Any]:
    """Get all trend categories"""
    return {
        "categories": [
            {"category": "theme", "pl": "Tematy", "description": "Trendy tematyczne"},
            {"category": "genre", "pl": "Gatunek", "description": "Popularność gatunków"},
            {"category": "character", "pl": "Postacie", "description": "Archetypy postaci"},
            {"category": "setting", "pl": "Otoczenie", "description": "Preferencje settingu"},
            {"category": "narrative", "pl": "Narracja", "description": "Techniki narracyjne"},
            {"category": "style", "pl": "Styl", "description": "Trendy stylistyczne"},
            {"category": "format", "pl": "Format", "description": "Trendy formatowe"},
            {"category": "marketing", "pl": "Marketing", "description": "Trendy marketingowe"}
        ]
    }


@router.get("/market-segments")
async def get_market_segments() -> Dict[str, Any]:
    """Get market segments"""
    return {
        "segments": [
            {"segment": "mainstream", "pl": "Mainstream", "description": "Szeroka publiczność"},
            {"segment": "literary", "pl": "Literacki", "description": "Rynek literacki"},
            {"segment": "commercial", "pl": "Komercyjny", "description": "Czysto komercyjny"},
            {"segment": "indie", "pl": "Indie", "description": "Niezależny"},
            {"segment": "academic", "pl": "Akademicki", "description": "Rynek akademicki"},
            {"segment": "young_adult", "pl": "Young Adult", "description": "Młodzi dorośli"},
            {"segment": "new_adult", "pl": "New Adult", "description": "Nowi dorośli"},
            {"segment": "children", "pl": "Dziecięcy", "description": "Dla dzieci"}
        ]
    }


@router.get("/trend-strengths")
async def get_trend_strengths() -> Dict[str, Any]:
    """Get trend strength levels"""
    return {
        "strengths": [
            {"strength": "emerging", "pl": "Wschodzący", "description": "Dopiero się pojawia"},
            {"strength": "growing", "pl": "Rosnący", "description": "Zyskuje popularność"},
            {"strength": "peak", "pl": "Szczyt", "description": "Maksymalna popularność"},
            {"strength": "stable", "pl": "Stabilny", "description": "Stała popularność"},
            {"strength": "declining", "pl": "Spadający", "description": "Traci popularność"},
            {"strength": "fading", "pl": "Zanikający", "description": "Prawie zniknął"}
        ]
    }


@router.get("/all")
async def list_all_trends() -> Dict[str, Any]:
    """List all tracked trends"""
    engine = get_trend_engine()
    return {"trends": engine.list_all_trends()}


@router.get("/trend/{trend_id}")
async def get_trend(trend_id: str) -> Dict[str, Any]:
    """Get a specific trend by ID"""
    engine = get_trend_engine()
    trend = engine.get_trend(trend_id)

    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")

    return {"trend": trend.to_dict()}


@router.get("/genre/{genre}")
async def get_genre_profile(genre: str) -> Dict[str, Any]:
    """Get a complete trend profile for a genre"""
    engine = get_trend_engine()
    return {"profile": engine.get_genre_profile(genre)}


@router.post("/analyze-project")
async def analyze_trends_for_project(request: AnalyzeTrendsRequest) -> Dict[str, Any]:
    """
    Analyze current trends and generate recommendations for a project.
    """
    engine = get_trend_engine()

    try:
        segment = MarketSegment(request.target_segment)
    except ValueError:
        segment = MarketSegment.MAINSTREAM

    report = await engine.analyze_trends_for_project(
        project_id=request.project_id,
        genre=request.genre,
        target_segment=segment,
        current_content=request.current_content
    )

    return {
        "success": True,
        "report": report.to_dict()
    }


@router.post("/trending-elements")
async def get_trending_elements(request: GetTrendingRequest) -> Dict[str, Any]:
    """
    Get currently trending elements for a genre.
    """
    engine = get_trend_engine()

    category = None
    if request.category:
        try:
            category = TrendCategory(request.category)
        except ValueError:
            pass

    result = await engine.get_trending_elements(
        genre=request.genre,
        category=category
    )

    return {
        "success": True,
        "trending": result
    }


@router.post("/analyze-content")
async def analyze_content_trends(request: AnalyzeContentRequest) -> Dict[str, Any]:
    """
    Analyze how well content aligns with current trends.
    """
    engine = get_trend_engine()

    result = await engine.analyze_content_trends(
        text=request.text,
        genre=request.genre
    )

    return {
        "success": True,
        "analysis": result
    }


@router.post("/suggest-elements")
async def suggest_trending_elements(request: SuggestElementsRequest) -> Dict[str, Any]:
    """
    Suggest trending elements to add to content.
    """
    engine = get_trend_engine()

    result = await engine.suggest_trending_elements(
        genre=request.genre,
        existing_elements=request.existing_elements
    )

    return {
        "success": True,
        "suggestions": result
    }


@router.post("/forecast")
async def forecast_trends(request: ForecastRequest) -> Dict[str, Any]:
    """
    Forecast trend trajectories.
    """
    engine = get_trend_engine()

    result = await engine.forecast_trends(
        months_ahead=request.months_ahead
    )

    return {
        "success": True,
        "forecast": result
    }


@router.get("/tropes")
async def get_popular_tropes() -> Dict[str, Any]:
    """Get popular tropes database"""
    from app.services.trend_adaptive import POPULAR_TROPES

    return {
        "tropes": [
            {
                "id": trope_id,
                "name": data["name"],
                "popularity": data["popularity"],
                "genres": data["genres"],
                "description": data["description"]
            }
            for trope_id, data in POPULAR_TROPES.items()
        ]
    }


@router.get("/report/{report_id}")
async def get_report(report_id: str) -> Dict[str, Any]:
    """Get a trend report by ID"""
    engine = get_trend_engine()
    report = engine.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {"report": report.to_dict()}


@router.get("/reports")
async def list_reports(project_id: Optional[str] = None) -> Dict[str, Any]:
    """List all trend reports"""
    engine = get_trend_engine()
    return {"reports": engine.list_reports(project_id)}
