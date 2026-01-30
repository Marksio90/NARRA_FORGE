"""
Character Consciousness API - NarraForge 3.0

Endpoints for character consciousness simulation and psychological profiling.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.character_consciousness import (
    get_consciousness_simulator,
    EmotionalState
)

router = APIRouter(prefix="/consciousness", tags=["Character Consciousness"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class CreateConsciousnessRequest(BaseModel):
    """Request for creating consciousness profile"""
    character_name: str
    character_data: Dict[str, Any]


class SimulateThoughtRequest(BaseModel):
    """Request for simulating thought process"""
    character_name: str
    situation: str
    available_actions: Optional[List[str]] = None
    other_characters_present: Optional[List[str]] = None


class InternalMonologueRequest(BaseModel):
    """Request for generating internal monologue"""
    character_name: str
    situation: str
    length: str = "medium"  # short, medium, long
    style: str = "stream_of_consciousness"  # stream_of_consciousness, reflective, anxious


class PredictReactionRequest(BaseModel):
    """Request for predicting character reaction"""
    character_name: str
    stimulus: str
    stimulus_source: Optional[str] = None


class UpdateRelationshipRequest(BaseModel):
    """Request for updating relationship perception"""
    character_name: str
    other_character: str
    event: str
    event_type: str = "neutral"  # positive, negative, neutral, betrayal, intimacy


class TrackGrowthRequest(BaseModel):
    """Request for tracking character growth"""
    character_name: str
    chapter_events: List[str]
    chapter_number: int


class ValidateDialogueRequest(BaseModel):
    """Request for validating dialogue authenticity"""
    character_name: str
    dialogue_line: str
    context: str


class UpdateEmotionRequest(BaseModel):
    """Request for updating emotional state"""
    character_name: str
    emotion: str
    intensity: float
    trigger: str


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """Get consciousness simulator status"""
    simulator = get_consciousness_simulator()
    return {
        "status": "active",
        "characters_with_profiles": simulator.get_all_characters(),
        "total_profiles": len(simulator.consciousnesses)
    }


@router.get("/emotional-states")
async def get_emotional_states() -> Dict[str, Any]:
    """Get all available emotional states"""
    return {
        "emotional_states": [
            {"state": "neutral", "pl": "Neutralny"},
            {"state": "happy", "pl": "Szczęśliwy"},
            {"state": "sad", "pl": "Smutny"},
            {"state": "angry", "pl": "Zły"},
            {"state": "fearful", "pl": "Przestraszony"},
            {"state": "surprised", "pl": "Zaskoczony"},
            {"state": "disgusted", "pl": "Zniesmaczony"},
            {"state": "anxious", "pl": "Niespokojny"},
            {"state": "hopeful", "pl": "Pełen nadziei"},
            {"state": "desperate", "pl": "Zdesperowany"},
            {"state": "conflicted", "pl": "Rozdarty"}
        ]
    }


@router.get("/defense-mechanisms")
async def get_defense_mechanisms() -> Dict[str, Any]:
    """Get all defense mechanisms"""
    return {
        "defense_mechanisms": [
            {"mechanism": "denial", "pl": "Zaprzeczanie", "description": "Odrzucanie rzeczywistości"},
            {"mechanism": "projection", "pl": "Projekcja", "description": "Przypisywanie własnych uczuć innym"},
            {"mechanism": "rationalization", "pl": "Racjonalizacja", "description": "Logiczne uzasadnianie"},
            {"mechanism": "displacement", "pl": "Przemieszczenie", "description": "Przeniesienie uczuć na inny obiekt"},
            {"mechanism": "sublimation", "pl": "Sublimacja", "description": "Przekształcenie w akceptowalne działanie"},
            {"mechanism": "repression", "pl": "Wyparcie", "description": "Nieświadome usunięcie z pamięci"},
            {"mechanism": "regression", "pl": "Regresja", "description": "Powrót do wcześniejszych zachowań"},
            {"mechanism": "intellectualization", "pl": "Intelektualizacja", "description": "Analiza zamiast odczuwania"},
            {"mechanism": "reaction_formation", "pl": "Reakcja przeciwna", "description": "Zachowanie przeciwne do uczuć"},
            {"mechanism": "humor", "pl": "Humor", "description": "Rozładowanie przez żart"}
        ]
    }


@router.get("/attachment-styles")
async def get_attachment_styles() -> Dict[str, Any]:
    """Get attachment styles"""
    return {
        "attachment_styles": [
            {"style": "secure", "pl": "Bezpieczny", "description": "Zdrowe, zrównoważone relacje"},
            {"style": "anxious", "pl": "Lękowy", "description": "Strach przed odrzuceniem, potrzeba potwierdzenia"},
            {"style": "avoidant", "pl": "Unikający", "description": "Dystans emocjonalny, niezależność"},
            {"style": "disorganized", "pl": "Zdezorganizowany", "description": "Nieprzewidywalne wzorce"}
        ]
    }


@router.get("/character-arc-stages")
async def get_character_arc_stages() -> Dict[str, Any]:
    """Get character arc stages (Hero's Journey)"""
    return {
        "stages": [
            {"stage": "ordinary_world", "pl": "Zwykły świat", "order": 1},
            {"stage": "call_to_adventure", "pl": "Wezwanie do przygody", "order": 2},
            {"stage": "refusal", "pl": "Odmowa", "order": 3},
            {"stage": "meeting_mentor", "pl": "Spotkanie z mentorem", "order": 4},
            {"stage": "crossing_threshold", "pl": "Przekroczenie progu", "order": 5},
            {"stage": "tests_allies_enemies", "pl": "Próby, sojusznicy, wrogowie", "order": 6},
            {"stage": "approach", "pl": "Zbliżanie się", "order": 7},
            {"stage": "ordeal", "pl": "Ordalia", "order": 8},
            {"stage": "reward", "pl": "Nagroda", "order": 9},
            {"stage": "road_back", "pl": "Droga powrotna", "order": 10},
            {"stage": "resurrection", "pl": "Zmartwychwstanie", "order": 11},
            {"stage": "return_with_elixir", "pl": "Powrót z eliksirem", "order": 12}
        ]
    }


@router.post("/create")
async def create_consciousness(request: CreateConsciousnessRequest) -> Dict[str, Any]:
    """
    Create a consciousness profile for a character.

    Analyzes character data and creates a deep psychological profile including:
    - Big Five personality traits
    - Core beliefs
    - Internal conflicts
    - Motivations (conscious and unconscious)
    - Fears and desires
    - Attachment style
    - Defense mechanisms
    - Coping strategies
    """
    simulator = get_consciousness_simulator()

    consciousness = await simulator.create_consciousness_from_character(
        character_name=request.character_name,
        character_data=request.character_data
    )

    return {
        "success": True,
        "message": f"Consciousness profile created for {request.character_name}",
        "profile": consciousness.to_dict()
    }


@router.get("/profile/{character_name}")
async def get_consciousness_profile(character_name: str) -> Dict[str, Any]:
    """Get the consciousness profile for a character"""
    simulator = get_consciousness_simulator()
    consciousness = simulator.get_consciousness(character_name)

    if not consciousness:
        raise HTTPException(status_code=404, detail=f"No consciousness profile for {character_name}")

    return {
        "character_name": character_name,
        "profile": consciousness.to_dict()
    }


@router.post("/simulate-thought")
async def simulate_thought_process(request: SimulateThoughtRequest) -> Dict[str, Any]:
    """
    Simulate the thought process of a character in a situation.

    Returns detailed analysis of:
    - Immediate reaction
    - Emotional response
    - Triggered beliefs and fears
    - Considered and eliminated options
    - Chosen action and rationalization
    - Suppressed thoughts
    """
    simulator = get_consciousness_simulator()

    try:
        thought_process = await simulator.simulate_thought_process(
            character_name=request.character_name,
            situation=request.situation,
            available_actions=request.available_actions,
            other_characters_present=request.other_characters_present
        )

        return {
            "success": True,
            "thought_process": thought_process.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/internal-monologue")
async def generate_internal_monologue(request: InternalMonologueRequest) -> Dict[str, Any]:
    """
    Generate an internal monologue for a character.

    Useful for deep POV scenes showing character's thoughts.
    Styles: stream_of_consciousness, reflective, anxious
    """
    simulator = get_consciousness_simulator()

    try:
        monologue = await simulator.generate_internal_monologue(
            character_name=request.character_name,
            situation=request.situation,
            length=request.length,
            style=request.style
        )

        return {
            "success": True,
            "character_name": request.character_name,
            "style": request.style,
            "monologue": monologue
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/predict-reaction")
async def predict_reaction(request: PredictReactionRequest) -> Dict[str, Any]:
    """
    Predict how a character will react to a stimulus.

    Useful for planning scenes and ensuring consistency.
    """
    simulator = get_consciousness_simulator()

    try:
        prediction = await simulator.predict_reaction(
            character_name=request.character_name,
            stimulus=request.stimulus,
            stimulus_source=request.stimulus_source
        )

        return {
            "success": True,
            "character_name": request.character_name,
            "stimulus": request.stimulus,
            "prediction": prediction
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/update-relationship")
async def update_relationship(request: UpdateRelationshipRequest) -> Dict[str, Any]:
    """
    Update a character's perception of their relationship with another character.

    Event types: positive, negative, neutral, betrayal, intimacy
    """
    simulator = get_consciousness_simulator()

    try:
        relationship = await simulator.update_relationship(
            character_name=request.character_name,
            other_character=request.other_character,
            event=request.event,
            event_type=request.event_type
        )

        return {
            "success": True,
            "character_name": request.character_name,
            "other_character": request.other_character,
            "updated_relationship": relationship.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/track-growth")
async def track_character_growth(request: TrackGrowthRequest) -> Dict[str, Any]:
    """
    Track character growth through chapter events.

    Updates:
    - Character arc stage
    - Growth points
    - Belief strengths
    - Internal conflict leanings
    """
    simulator = get_consciousness_simulator()

    try:
        growth_data = await simulator.track_character_growth(
            character_name=request.character_name,
            chapter_events=request.chapter_events,
            chapter_number=request.chapter_number
        )

        return {
            "success": True,
            "character_name": request.character_name,
            "chapter_number": request.chapter_number,
            "growth_analysis": growth_data
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/validate-dialogue")
async def validate_dialogue(request: ValidateDialogueRequest) -> Dict[str, Any]:
    """
    Validate if a dialogue line is psychologically authentic for a character.

    Returns:
    - Authenticity score (0-1)
    - Problems detected
    - Suggestions for improvement
    - Hidden subtext analysis
    """
    simulator = get_consciousness_simulator()

    validation = await simulator.validate_dialogue_authenticity(
        character_name=request.character_name,
        dialogue_line=request.dialogue_line,
        context=request.context
    )

    return {
        "success": True,
        "character_name": request.character_name,
        "dialogue_line": request.dialogue_line,
        "validation": validation
    }


@router.post("/update-emotion")
async def update_emotional_state(request: UpdateEmotionRequest) -> Dict[str, Any]:
    """
    Manually update a character's emotional state.
    """
    simulator = get_consciousness_simulator()

    try:
        emotion = EmotionalState(request.emotion)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid emotion: {request.emotion}")

    simulator.update_emotional_state(
        character_name=request.character_name,
        emotion=emotion,
        intensity=request.intensity,
        trigger=request.trigger
    )

    return {
        "success": True,
        "character_name": request.character_name,
        "new_emotion": request.emotion,
        "intensity": request.intensity,
        "trigger": request.trigger
    }


@router.get("/export/{character_name}")
async def export_consciousness(character_name: str) -> Dict[str, Any]:
    """Export full consciousness profile as JSON"""
    simulator = get_consciousness_simulator()

    export_data = simulator.export_consciousness(character_name)

    if not export_data:
        raise HTTPException(status_code=404, detail=f"No consciousness profile for {character_name}")

    return {
        "success": True,
        "export": export_data
    }
