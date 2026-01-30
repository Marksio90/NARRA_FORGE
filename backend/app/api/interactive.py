"""
Interactive Reading API - NarraForge 3.0 Phase 2

Endpoints for interactive reading experience.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.interactive_reading import (
    get_interactive_reading_engine,
    ChoiceType,
    NodeType,
    EndingType
)
from app.models.project import GenreType

router = APIRouter(prefix="/interactive", tags=["Interactive Reading"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class ConvertToInteractiveRequest(BaseModel):
    """Request for converting story to interactive"""
    title: str
    author: str
    genre: str
    chapters: List[str]
    choices_per_chapter: int = 3
    num_endings: int = 3


class CreateGameStateRequest(BaseModel):
    """Request for creating game state"""
    story_id: str


class MakeChoiceRequest(BaseModel):
    """Request for making a choice"""
    state_id: str
    story_id: str
    choice_id: str


class DynamicInputRequest(BaseModel):
    """Request for dynamic player input"""
    state_id: str
    story_id: str
    player_input: str


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/choice-types")
async def get_choice_types() -> Dict[str, Any]:
    """Get all choice types"""
    return {
        "choice_types": [
            {"type": "binary", "pl": "Binarny", "description": "Tak/Nie"},
            {"type": "multiple", "pl": "Wielokrotny", "description": "Wiele opcji"},
            {"type": "timed", "pl": "Czasowy", "description": "Ograniczony czasowo"},
            {"type": "hidden", "pl": "Ukryty", "description": "Ukryte konsekwencje"},
            {"type": "moral", "pl": "Moralny", "description": "Dylemat moralny"},
            {"type": "romance", "pl": "Romantyczny", "description": "Wybór romantyczny"},
            {"type": "combat", "pl": "Walka", "description": "Konfrontacja"},
            {"type": "investigation", "pl": "Śledztwo", "description": "Wybór śledczy"}
        ]
    }


@router.get("/ending-types")
async def get_ending_types() -> Dict[str, Any]:
    """Get all ending types"""
    return {
        "ending_types": [
            {"type": "good", "pl": "Dobre", "description": "Pozytywne zakończenie"},
            {"type": "bad", "pl": "Złe", "description": "Negatywne zakończenie"},
            {"type": "neutral", "pl": "Neutralne", "description": "Otwarte/niejednoznaczne"},
            {"type": "secret", "pl": "Sekretne", "description": "Trudne do odkrycia"},
            {"type": "true", "pl": "Prawdziwe", "description": "Kanoniczne zakończenie"}
        ]
    }


@router.post("/convert")
async def convert_to_interactive(request: ConvertToInteractiveRequest) -> Dict[str, Any]:
    """
    Convert a linear story to an interactive narrative.

    Creates choice points, branches, and multiple endings.
    """
    engine = get_interactive_reading_engine()

    try:
        genre = GenreType(request.genre.upper())
    except ValueError:
        genre = GenreType.DRAMA

    story = await engine.convert_to_interactive(
        title=request.title,
        author=request.author,
        genre=genre,
        chapters=request.chapters,
        choices_per_chapter=request.choices_per_chapter,
        num_endings=request.num_endings
    )

    return {
        "success": True,
        "story": story.to_dict()
    }


@router.get("/story/{story_id}")
async def get_story(story_id: str) -> Dict[str, Any]:
    """Get an interactive story"""
    engine = get_interactive_reading_engine()
    story = engine.get_story(story_id)

    if not story:
        raise HTTPException(status_code=404, detail=f"Story not found: {story_id}")

    return {
        "story": story.to_dict()
    }


@router.get("/story/{story_id}/stats")
async def get_story_stats(story_id: str) -> Dict[str, Any]:
    """Get statistics for an interactive story"""
    engine = get_interactive_reading_engine()
    stats = engine.get_story_stats(story_id)

    if not stats:
        raise HTTPException(status_code=404, detail=f"Story not found: {story_id}")

    return {
        "story_id": story_id,
        "stats": stats
    }


@router.get("/story/{story_id}/node/{node_id}")
async def get_node(story_id: str, node_id: str) -> Dict[str, Any]:
    """Get a specific node from a story"""
    engine = get_interactive_reading_engine()
    story = engine.get_story(story_id)

    if not story:
        raise HTTPException(status_code=404, detail=f"Story not found: {story_id}")

    node = story.nodes.get(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")

    return {
        "node": node.to_dict()
    }


@router.post("/game/start")
async def start_game(request: CreateGameStateRequest) -> Dict[str, Any]:
    """
    Start a new game/reading session.

    Creates a new game state and returns the first node.
    """
    engine = get_interactive_reading_engine()

    try:
        state = engine.create_game_state(request.story_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    story = engine.get_story(request.story_id)
    first_node = story.nodes.get(story.start_node_id)

    return {
        "success": True,
        "state": state.to_dict(),
        "current_node": first_node.to_dict() if first_node else None
    }


@router.get("/game/{state_id}")
async def get_game_state(state_id: str) -> Dict[str, Any]:
    """Get current game state"""
    engine = get_interactive_reading_engine()
    state = engine.get_state(state_id)

    if not state:
        raise HTTPException(status_code=404, detail=f"Game state not found: {state_id}")

    return {
        "state": state.to_dict()
    }


@router.post("/game/choice")
async def make_choice(request: MakeChoiceRequest) -> Dict[str, Any]:
    """
    Make a choice in the interactive story.

    Updates game state and returns the next node.
    """
    engine = get_interactive_reading_engine()

    state = engine.get_state(request.state_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Game state not found: {request.state_id}")

    success, next_node = engine.make_choice(
        state=state,
        story_id=request.story_id,
        choice_id=request.choice_id
    )

    if not success:
        raise HTTPException(status_code=400, detail="Invalid choice or requirements not met")

    # Check for ending
    ending = engine.check_ending(state, request.story_id)

    return {
        "success": True,
        "state": state.to_dict(),
        "next_node": next_node.to_dict() if next_node else None,
        "ending": ending.to_dict() if ending else None
    }


@router.get("/game/{state_id}/choices")
async def get_available_choices(state_id: str, story_id: str) -> Dict[str, Any]:
    """Get available choices for current state"""
    engine = get_interactive_reading_engine()

    state = engine.get_state(state_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Game state not found: {state_id}")

    choices = engine.get_available_choices(state, story_id)

    return {
        "choices": [c.to_dict() for c in choices]
    }


@router.post("/game/dynamic")
async def dynamic_response(request: DynamicInputRequest) -> Dict[str, Any]:
    """
    Get a dynamic response to player input.

    For freeform interactions within the story.
    """
    engine = get_interactive_reading_engine()

    state = engine.get_state(request.state_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Game state not found: {request.state_id}")

    response = await engine.generate_dynamic_response(
        state=state,
        story_id=request.story_id,
        player_input=request.player_input
    )

    return {
        "success": True,
        "response": response
    }


@router.get("/stories")
async def list_stories() -> Dict[str, Any]:
    """List all interactive stories"""
    engine = get_interactive_reading_engine()
    return {"stories": engine.list_stories()}
