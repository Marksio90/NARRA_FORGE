"""
Advanced Dialogue System API - NarraForge 3.0

Endpoints for generating and analyzing dialogue with subtext.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.advanced_dialogue_system import (
    get_advanced_dialogue_system,
    DialogueContext,
    CharacterVoice,
    SubtextType,
    PowerDynamic,
    EmotionalUndercurrent
)
from app.models.project import GenreType

router = APIRouter(prefix="/dialogue", tags=["Advanced Dialogue"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class VoiceProfileRequest(BaseModel):
    """Request for generating voice profile"""
    character_name: str
    character_data: Dict[str, Any]


class DialogueContextModel(BaseModel):
    """Model for dialogue context"""
    scene_setting: str
    relationship_type: str
    relationship_history: str = ""
    what_each_wants: Dict[str, str]
    what_each_knows: Dict[str, List[str]] = {}
    what_each_hides: Dict[str, List[str]] = {}
    power_balance: Dict[str, float] = {}
    emotional_states: Dict[str, str] = {}
    stakes: str
    genre: str = "drama"
    pov_character: Optional[str] = None


class GenerateDialogueRequest(BaseModel):
    """Request for generating dialogue"""
    context: DialogueContextModel
    num_beats: int = 8
    subtext_density: float = 0.6


class EnhanceDialogueRequest(BaseModel):
    """Request for enhancing existing dialogue"""
    dialogue_text: str
    character_a: str
    character_b: str
    context: DialogueContextModel
    enhancement_focus: str = "subtext"


class ConfrontationRequest(BaseModel):
    """Request for generating confrontation dialogue"""
    character_a: str
    character_b: str
    conflict_topic: str
    context: DialogueContextModel
    escalation_level: float = 0.7


class InterrogationRequest(BaseModel):
    """Request for generating interrogation dialogue"""
    interrogator: str
    subject: str
    secret: str
    context: DialogueContextModel


class SubtextAnalysisRequest(BaseModel):
    """Request for analyzing subtext"""
    dialogue_line: str
    speaker: str
    context: DialogueContextModel


class VoiceValidationRequest(BaseModel):
    """Request for validating dialogue voices"""
    dialogue_text: str
    character_voices: Dict[str, Dict[str, Any]]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def model_to_context(model: DialogueContextModel) -> DialogueContext:
    """Convert Pydantic model to DialogueContext"""
    try:
        genre = GenreType(model.genre.upper())
    except ValueError:
        genre = GenreType.DRAMA

    return DialogueContext(
        scene_setting=model.scene_setting,
        relationship_type=model.relationship_type,
        relationship_history=model.relationship_history,
        what_each_wants=model.what_each_wants,
        what_each_knows=model.what_each_knows,
        what_each_hides=model.what_each_hides,
        power_balance=model.power_balance,
        emotional_states=model.emotional_states,
        stakes=model.stakes,
        genre=genre,
        pov_character=model.pov_character
    )


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/subtext-types")
async def get_subtext_types() -> Dict[str, Any]:
    """Get all available subtext types with descriptions"""
    return {
        "subtext_types": [
            {"type": "hidden_agenda", "description": "Postać ma ukryty cel", "pl": "Ukryta agenda"},
            {"type": "suppressed_emotion", "description": "Tłumione prawdziwe uczucia", "pl": "Tłumione emocje"},
            {"type": "power_play", "description": "Ustanawianie dominacji", "pl": "Gra o władzę"},
            {"type": "deflection", "description": "Unikanie prawdziwego tematu", "pl": "Unik"},
            {"type": "manipulation", "description": "Wpływanie przez słowa", "pl": "Manipulacja"},
            {"type": "intimacy_seeking", "description": "Tworzenie bliskości", "pl": "Szukanie bliskości"},
            {"type": "intimacy_avoiding", "description": "Tworzenie dystansu", "pl": "Unikanie bliskości"},
            {"type": "testing", "description": "Testowanie drugiej osoby", "pl": "Testowanie"},
            {"type": "performance", "description": "Odgrywanie roli", "pl": "Gra aktorska"},
            {"type": "revelation", "description": "Powolne ujawnianie", "pl": "Objawienie"}
        ]
    }


@router.get("/power-dynamics")
async def get_power_dynamics() -> Dict[str, Any]:
    """Get all power dynamic types"""
    return {
        "power_dynamics": [
            {"type": "dominant", "description": "Jedna strona dominuje", "pl": "Dominacja"},
            {"type": "submissive", "description": "Jedna strona ulega", "pl": "Uległość"},
            {"type": "equal", "description": "Równowaga sił", "pl": "Równowaga"},
            {"type": "shifting", "description": "Dynamika się zmienia", "pl": "Zmienna"},
            {"type": "contested", "description": "Walka o władzę", "pl": "Rywalizacja"}
        ]
    }


@router.get("/emotional-undercurrents")
async def get_emotional_undercurrents() -> Dict[str, Any]:
    """Get all emotional undercurrent types"""
    return {
        "emotional_undercurrents": [
            {"type": "desire", "pl": "Pożądanie"},
            {"type": "resentment", "pl": "Uraza"},
            {"type": "fear", "pl": "Strach"},
            {"type": "guilt", "pl": "Poczucie winy"},
            {"type": "longing", "pl": "Tęsknota"},
            {"type": "suspicion", "pl": "Podejrzliwość"},
            {"type": "hope", "pl": "Nadzieja"},
            {"type": "desperation", "pl": "Desperacja"},
            {"type": "contempt", "pl": "Pogarda"},
            {"type": "affection", "pl": "Czułość"}
        ]
    }


@router.post("/voice-profile/generate")
async def generate_voice_profile(request: VoiceProfileRequest) -> Dict[str, Any]:
    """Generate a voice profile for a character"""
    system = get_advanced_dialogue_system()

    profile = await system.generate_voice_profile(
        character_name=request.character_name,
        character_data=request.character_data
    )

    return {
        "success": True,
        "profile": profile.to_dict()
    }


@router.post("/voice-profile/register")
async def register_voice_profile(
    character_name: str,
    vocabulary_level: str = "moderate",
    sentence_structure: str = "varied",
    verbal_tics: List[str] = [],
    favorite_phrases: List[str] = [],
    forbidden_words: List[str] = [],
    speech_rhythm: str = "normal",
    formality_default: str = "casual",
    emotional_expression: str = "moderate"
) -> Dict[str, Any]:
    """Register a custom voice profile"""
    system = get_advanced_dialogue_system()

    profile = CharacterVoice(
        character_name=character_name,
        vocabulary_level=vocabulary_level,
        sentence_structure=sentence_structure,
        verbal_tics=verbal_tics,
        favorite_phrases=favorite_phrases,
        forbidden_words=forbidden_words,
        speech_rhythm=speech_rhythm,
        formality_default=formality_default,
        emotional_expression=emotional_expression
    )

    system.register_voice(profile)

    return {
        "success": True,
        "message": f"Voice profile registered for {character_name}",
        "profile": profile.to_dict()
    }


@router.post("/generate")
async def generate_dialogue(request: GenerateDialogueRequest) -> Dict[str, Any]:
    """Generate a dialogue exchange with subtext"""
    system = get_advanced_dialogue_system()
    context = model_to_context(request.context)

    exchange = await system.generate_dialogue_exchange(
        context=context,
        num_beats=request.num_beats,
        subtext_density=request.subtext_density
    )

    return exchange.to_dict()


@router.post("/enhance")
async def enhance_dialogue(request: EnhanceDialogueRequest) -> Dict[str, Any]:
    """Enhance existing dialogue with more subtext, power dynamics, or voice"""
    system = get_advanced_dialogue_system()
    context = model_to_context(request.context)

    enhanced = await system.enhance_existing_dialogue(
        dialogue_text=request.dialogue_text,
        character_a=request.character_a,
        character_b=request.character_b,
        context=context,
        enhancement_focus=request.enhancement_focus
    )

    return {
        "original": request.dialogue_text,
        "enhanced": enhanced,
        "enhancement_focus": request.enhancement_focus
    }


@router.post("/generate/confrontation")
async def generate_confrontation(request: ConfrontationRequest) -> Dict[str, Any]:
    """Generate a confrontational dialogue with escalating tension"""
    system = get_advanced_dialogue_system()
    context = model_to_context(request.context)

    exchange = await system.generate_confrontation_dialogue(
        character_a=request.character_a,
        character_b=request.character_b,
        conflict_topic=request.conflict_topic,
        context=context,
        escalation_level=request.escalation_level
    )

    return {
        "type": "confrontation",
        "topic": request.conflict_topic,
        "escalation_level": request.escalation_level,
        "exchange": exchange.to_dict()
    }


@router.post("/generate/interrogation")
async def generate_interrogation(request: InterrogationRequest) -> Dict[str, Any]:
    """Generate an interrogation-style dialogue"""
    system = get_advanced_dialogue_system()
    context = model_to_context(request.context)

    exchange = await system.generate_interrogation_dialogue(
        interrogator=request.interrogator,
        subject=request.subject,
        secret=request.secret,
        context=context
    )

    return {
        "type": "interrogation",
        "secret": request.secret,
        "exchange": exchange.to_dict()
    }


@router.post("/analyze-subtext")
async def analyze_subtext(request: SubtextAnalysisRequest) -> Dict[str, Any]:
    """Analyze the subtext of a dialogue line"""
    system = get_advanced_dialogue_system()
    context = model_to_context(request.context)

    subtext = await system.analyze_subtext(
        dialogue_line=request.dialogue_line,
        speaker=request.speaker,
        context=context
    )

    return {
        "dialogue_line": request.dialogue_line,
        "speaker": request.speaker,
        "subtext": subtext.to_dict()
    }


@router.post("/validate-voices")
async def validate_voices(request: VoiceValidationRequest) -> Dict[str, Any]:
    """Validate that dialogue maintains consistent character voices"""
    system = get_advanced_dialogue_system()

    # Convert dict to CharacterVoice objects
    voices = {}
    for name, data in request.character_voices.items():
        voices[name] = CharacterVoice(
            character_name=name,
            vocabulary_level=data.get("vocabulary_level", "moderate"),
            sentence_structure=data.get("sentence_structure", "varied"),
            verbal_tics=data.get("verbal_tics", []),
            favorite_phrases=data.get("favorite_phrases", []),
            forbidden_words=data.get("forbidden_words", []),
            speech_rhythm=data.get("speech_rhythm", "normal"),
            formality_default=data.get("formality_default", "casual"),
            emotional_expression=data.get("emotional_expression", "moderate")
        )

    result = await system.validate_dialogue_voices(
        dialogue_text=request.dialogue_text,
        characters=voices
    )

    return result
