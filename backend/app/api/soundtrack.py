"""
Soundtrack API - NarraForge 3.0 Phase 2

Endpoints for ambient soundtrack generation.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.soundtrack_generator import (
    get_soundtrack_generator,
    MusicMood,
    MusicGenre,
    Instrument
)
from app.models.project import GenreType

router = APIRouter(prefix="/soundtrack", tags=["Ambient Soundtrack"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class AnalyzeChapterRequest(BaseModel):
    """Request for analyzing chapter mood"""
    chapter_text: str
    chapter_number: int
    genre: str = "drama"


class GenerateSoundtrackRequest(BaseModel):
    """Request for generating book soundtrack"""
    book_title: str
    genre: str
    chapters: List[str]
    chapter_titles: Optional[List[str]] = None


class GetMusicPromptRequest(BaseModel):
    """Request for getting music generation prompt"""
    soundtrack_id: str
    chapter_number: int


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/moods")
async def get_music_moods() -> Dict[str, Any]:
    """Get all music moods"""
    return {
        "moods": [
            {"mood": "peaceful", "pl": "Spokojny", "description": "Relaksujący, medytacyjny"},
            {"mood": "tense", "pl": "Napięty", "description": "Niepokojący, budujący suspens"},
            {"mood": "dramatic", "pl": "Dramatyczny", "description": "Intensywny, emocjonalny"},
            {"mood": "romantic", "pl": "Romantyczny", "description": "Ciepły, emocjonalny"},
            {"mood": "mysterious", "pl": "Tajemniczy", "description": "Enigmatyczny, intrygujący"},
            {"mood": "action", "pl": "Akcja", "description": "Energiczny, dynamiczny"},
            {"mood": "sad", "pl": "Smutny", "description": "Melancholijny"},
            {"mood": "joyful", "pl": "Radosny", "description": "Wesoły, optymistyczny"},
            {"mood": "epic", "pl": "Epicki", "description": "Monumentalny, wielki"},
            {"mood": "horror", "pl": "Horror", "description": "Przerażający, mroczny"},
            {"mood": "adventure", "pl": "Przygodowy", "description": "Ekscytujący"},
            {"mood": "contemplative", "pl": "Kontemplacyjny", "description": "Refleksyjny"}
        ]
    }


@router.get("/genres")
async def get_music_genres() -> Dict[str, Any]:
    """Get all music genres"""
    return {
        "genres": [
            {"genre": "orchestral", "pl": "Orkiestrowy", "description": "Pełna orkiestra"},
            {"genre": "ambient", "pl": "Ambient", "description": "Atmosferyczny"},
            {"genre": "electronic", "pl": "Elektroniczny", "description": "Syntezatory"},
            {"genre": "piano", "pl": "Fortepian", "description": "Solo piano"},
            {"genre": "acoustic", "pl": "Akustyczny", "description": "Instrumenty akustyczne"},
            {"genre": "cinematic", "pl": "Filmowy", "description": "Muzyka filmowa"},
            {"genre": "folk", "pl": "Folk", "description": "Muzyka ludowa"},
            {"genre": "jazz", "pl": "Jazz", "description": "Jazzowy"},
            {"genre": "world", "pl": "World", "description": "Muzyka świata"},
            {"genre": "synth", "pl": "Synth", "description": "Syntezatorowy"},
            {"genre": "choral", "pl": "Chóralny", "description": "Chór"}
        ]
    }


@router.get("/instruments")
async def get_instruments() -> Dict[str, Any]:
    """Get all instruments"""
    return {
        "instruments": [
            {"instrument": "strings", "pl": "Smyczki"},
            {"instrument": "piano", "pl": "Fortepian"},
            {"instrument": "synth", "pl": "Syntezator"},
            {"instrument": "guitar", "pl": "Gitara"},
            {"instrument": "flute", "pl": "Flet"},
            {"instrument": "drums", "pl": "Perkusja"},
            {"instrument": "choir", "pl": "Chór"},
            {"instrument": "harp", "pl": "Harfa"},
            {"instrument": "cello", "pl": "Wiolonczela"},
            {"instrument": "violin", "pl": "Skrzypce"},
            {"instrument": "bells", "pl": "Dzwonki"},
            {"instrument": "pad", "pl": "Pad syntezatorowy"}
        ]
    }


@router.get("/effects")
async def get_sound_effects() -> Dict[str, Any]:
    """Get all sound effect types"""
    return {
        "effects": [
            {"type": "nature", "pl": "Przyroda", "examples": ["wiatr", "deszcz", "ptaki", "strumień"]},
            {"type": "urban", "pl": "Miejskie", "examples": ["ulica", "tłum", "ruch"]},
            {"type": "weather", "pl": "Pogoda", "examples": ["burza", "deszcz", "wiatr"]},
            {"type": "interior", "pl": "Wnętrze", "examples": ["ogień", "zegar", "kroki"]},
            {"type": "horror", "pl": "Horror", "examples": ["skrzypienie", "szepty", "jęki"]},
            {"type": "fantasy", "pl": "Fantasy", "examples": ["magia", "portale", "zaklęcia"]},
            {"type": "scifi", "pl": "SciFi", "examples": ["komputery", "statki", "lasery"]},
            {"type": "combat", "pl": "Walka", "examples": ["miecze", "strzały", "eksplozje"]}
        ]
    }


@router.get("/genre-profiles/{genre}")
async def get_genre_profile(genre: str) -> Dict[str, Any]:
    """Get music profile for a genre"""
    from app.services.soundtrack_generator import GENRE_MUSIC_PROFILES

    try:
        genre_type = GenreType(genre.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid genre: {genre}")

    profile = GENRE_MUSIC_PROFILES.get(genre_type, {})

    return {
        "genre": genre,
        "primary_genres": [g.value for g in profile.get("primary_genres", [])],
        "primary_moods": [m.value for m in profile.get("primary_moods", [])],
        "instruments": [i.value for i in profile.get("instruments", [])],
        "tempo_range": profile.get("tempo_range", (60, 120)),
        "typical_effects": [e.value for e in profile.get("typical_effects", [])],
        "keys": profile.get("keys", [])
    }


@router.post("/analyze-chapter")
async def analyze_chapter(request: AnalyzeChapterRequest) -> Dict[str, Any]:
    """
    Analyze a chapter and create a soundscape.

    Returns music parameters and ambient effect suggestions.
    """
    generator = get_soundtrack_generator()

    try:
        genre = GenreType(request.genre.upper())
    except ValueError:
        genre = GenreType.DRAMA

    soundscape = await generator.analyze_chapter_mood(
        chapter_text=request.chapter_text,
        chapter_number=request.chapter_number,
        genre=genre
    )

    return {
        "success": True,
        "soundscape": soundscape.to_dict()
    }


@router.post("/generate")
async def generate_soundtrack(request: GenerateSoundtrackRequest) -> Dict[str, Any]:
    """
    Generate a complete soundtrack for a book.

    Analyzes all chapters and creates music parameters.
    """
    generator = get_soundtrack_generator()

    try:
        genre = GenreType(request.genre.upper())
    except ValueError:
        genre = GenreType.DRAMA

    soundtrack = await generator.generate_book_soundtrack(
        book_title=request.book_title,
        genre=genre,
        chapters=request.chapters,
        chapter_titles=request.chapter_titles
    )

    return {
        "success": True,
        "soundtrack": soundtrack.to_dict()
    }


@router.get("/soundtrack/{soundtrack_id}")
async def get_soundtrack(soundtrack_id: str) -> Dict[str, Any]:
    """Get a specific soundtrack"""
    generator = get_soundtrack_generator()
    soundtrack = generator.get_soundtrack(soundtrack_id)

    if not soundtrack:
        raise HTTPException(status_code=404, detail=f"Soundtrack not found: {soundtrack_id}")

    return {
        "soundtrack": soundtrack.to_dict()
    }


@router.get("/soundtrack/{soundtrack_id}/chapter/{chapter_number}")
async def get_chapter_soundscape(soundtrack_id: str, chapter_number: int) -> Dict[str, Any]:
    """Get soundscape for a specific chapter"""
    generator = get_soundtrack_generator()
    soundtrack = generator.get_soundtrack(soundtrack_id)

    if not soundtrack:
        raise HTTPException(status_code=404, detail=f"Soundtrack not found: {soundtrack_id}")

    for soundscape in soundtrack.chapter_soundscapes:
        if soundscape.chapter_number == chapter_number:
            return {
                "soundscape": soundscape.to_dict(),
                "music_prompt": generator.get_music_prompt(soundscape)
            }

    raise HTTPException(status_code=404, detail=f"Chapter {chapter_number} not found")


@router.get("/soundtrack/{soundtrack_id}/spotify-queries")
async def get_spotify_queries(soundtrack_id: str) -> Dict[str, Any]:
    """Get Spotify search queries for finding similar music"""
    generator = get_soundtrack_generator()
    soundtrack = generator.get_soundtrack(soundtrack_id)

    if not soundtrack:
        raise HTTPException(status_code=404, detail=f"Soundtrack not found: {soundtrack_id}")

    queries = generator.generate_spotify_search_queries(soundtrack)

    return {
        "soundtrack_id": soundtrack_id,
        "spotify_queries": queries
    }


@router.get("/soundtrack/{soundtrack_id}/export")
async def export_soundtrack(soundtrack_id: str) -> Dict[str, Any]:
    """Export full soundtrack data"""
    generator = get_soundtrack_generator()
    export_data = generator.export_soundtrack(soundtrack_id)

    if not export_data:
        raise HTTPException(status_code=404, detail=f"Soundtrack not found: {soundtrack_id}")

    return {
        "success": True,
        "export": export_data
    }


@router.get("/soundtracks")
async def list_soundtracks() -> Dict[str, Any]:
    """List all soundtracks"""
    generator = get_soundtrack_generator()
    return {"soundtracks": generator.list_soundtracks()}
