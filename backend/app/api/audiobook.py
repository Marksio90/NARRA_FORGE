"""
Audiobook API - NarraForge 3.0 Phase 2

Endpoints for AI audiobook generation with multi-voice support.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.services.audiobook_generator import (
    get_audiobook_generator,
    VoiceGender,
    VoiceAge,
    VoiceTone,
    TTSProvider,
    AudioFormat
)

router = APIRouter(prefix="/audiobook", tags=["AI Audiobook"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class CreateVoiceProfileRequest(BaseModel):
    """Request for creating a voice profile"""
    name: str
    gender: str
    age: str
    tone: str
    provider: str = "openai"
    voice_id: Optional[str] = None
    speaking_rate: float = 1.0
    pitch: float = 1.0
    description: str = ""


class GenerateCharacterVoicesRequest(BaseModel):
    """Request for generating character voice profiles"""
    characters: List[Dict[str, Any]]
    genre: str = "drama"


class ParseChapterRequest(BaseModel):
    """Request for parsing chapter into speech segments"""
    chapter_text: str
    chapter_number: int
    character_names: List[str]


class GenerateChapterAudioRequest(BaseModel):
    """Request for generating chapter audio"""
    chapter_text: str
    chapter_number: int
    chapter_title: str
    output_format: str = "mp3"


class CreateAudiobookRequest(BaseModel):
    """Request for creating full audiobook"""
    project_id: str
    title: str
    author: str
    chapters: List[Dict[str, str]]  # [{text, title}]
    characters: List[Dict[str, Any]]
    genre: str = "drama"
    output_format: str = "mp3"


class EstimateCostRequest(BaseModel):
    """Request for cost estimation"""
    total_characters: int
    num_chapters: int


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/providers")
async def get_tts_providers() -> Dict[str, Any]:
    """Get available TTS providers"""
    return {
        "providers": [
            {"provider": "openai", "name": "OpenAI TTS", "status": "active", "voices": 6},
            {"provider": "elevenlabs", "name": "ElevenLabs", "status": "coming_soon", "voices": 100},
            {"provider": "azure", "name": "Azure Neural TTS", "status": "coming_soon", "voices": 200},
            {"provider": "google", "name": "Google Cloud TTS", "status": "coming_soon", "voices": 150}
        ]
    }


@router.get("/voices/openai")
async def get_openai_voices() -> Dict[str, Any]:
    """Get available OpenAI TTS voices"""
    return {
        "voices": [
            {"id": "alloy", "gender": "neutral", "tone": "neutral", "description": "Versatile, balanced voice"},
            {"id": "echo", "gender": "male", "tone": "warm", "description": "Warm, engaging male voice"},
            {"id": "fable", "gender": "neutral", "tone": "dramatic", "description": "Dramatic, storytelling voice"},
            {"id": "onyx", "gender": "male", "tone": "authoritative", "description": "Deep, authoritative male voice"},
            {"id": "nova", "gender": "female", "tone": "friendly", "description": "Bright, friendly female voice"},
            {"id": "shimmer", "gender": "female", "tone": "warm", "description": "Warm, soothing female voice"}
        ]
    }


@router.get("/voice-options")
async def get_voice_options() -> Dict[str, Any]:
    """Get all voice configuration options"""
    return {
        "genders": [
            {"value": "male", "pl": "Męski"},
            {"value": "female", "pl": "Żeński"},
            {"value": "neutral", "pl": "Neutralny"}
        ],
        "ages": [
            {"value": "child", "pl": "Dziecko"},
            {"value": "young", "pl": "Młody"},
            {"value": "adult", "pl": "Dorosły"},
            {"value": "elderly", "pl": "Starszy"}
        ],
        "tones": [
            {"value": "warm", "pl": "Ciepły"},
            {"value": "cold", "pl": "Chłodny"},
            {"value": "authoritative", "pl": "Autorytatywny"},
            {"value": "friendly", "pl": "Przyjazny"},
            {"value": "mysterious", "pl": "Tajemniczy"},
            {"value": "dramatic", "pl": "Dramatyczny"},
            {"value": "neutral", "pl": "Neutralny"},
            {"value": "romantic", "pl": "Romantyczny"}
        ],
        "formats": [
            {"value": "mp3", "name": "MP3", "description": "Najpopularniejszy format"},
            {"value": "wav", "name": "WAV", "description": "Bezstratna jakość"},
            {"value": "ogg", "name": "OGG", "description": "Otwarty format"},
            {"value": "aac", "name": "AAC", "description": "Dobra kompresja"},
            {"value": "flac", "name": "FLAC", "description": "Bezstratna kompresja"}
        ]
    }


@router.post("/voice-profile/create")
async def create_voice_profile(request: CreateVoiceProfileRequest) -> Dict[str, Any]:
    """
    Create a voice profile for a character or narrator.
    """
    generator = get_audiobook_generator()

    try:
        gender = VoiceGender(request.gender)
        age = VoiceAge(request.age)
        tone = VoiceTone(request.tone)
        provider = TTSProvider(request.provider)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {e}")

    profile = generator.create_voice_profile(
        name=request.name,
        gender=gender,
        age=age,
        tone=tone,
        provider=provider,
        voice_id=request.voice_id,
        speaking_rate=request.speaking_rate,
        pitch=request.pitch,
        description=request.description
    )

    return {
        "success": True,
        "profile": profile.to_dict()
    }


@router.post("/voice-profiles/generate")
async def generate_character_voices(request: GenerateCharacterVoicesRequest) -> Dict[str, Any]:
    """
    Automatically generate voice profiles for a list of characters.

    Analyzes character descriptions to select appropriate voices.
    """
    generator = get_audiobook_generator()

    profiles = await generator.generate_character_voice_profiles(
        characters=request.characters,
        genre=request.genre
    )

    return {
        "success": True,
        "profiles": {name: profile.to_dict() for name, profile in profiles.items()}
    }


@router.get("/voice-profiles")
async def list_voice_profiles() -> Dict[str, Any]:
    """List all created voice profiles"""
    generator = get_audiobook_generator()

    return {
        "profiles": {
            profile_id: profile.to_dict()
            for profile_id, profile in generator.voice_profiles.items()
        }
    }


@router.post("/estimate")
async def estimate_cost(request: EstimateCostRequest) -> Dict[str, Any]:
    """
    Estimate cost and duration for audiobook generation.
    """
    generator = get_audiobook_generator()

    estimate = await generator.estimate_audiobook_cost(
        total_characters=request.total_characters,
        num_chapters=request.num_chapters
    )

    return {
        "success": True,
        "estimate": estimate
    }


@router.get("/speech-types")
async def get_speech_types() -> Dict[str, Any]:
    """Get all speech segment types"""
    return {
        "types": [
            {"type": "narration", "pl": "Narracja", "description": "Tekst narracyjny"},
            {"type": "dialogue", "pl": "Dialog", "description": "Wypowiedzi postaci"},
            {"type": "thought", "pl": "Myśl", "description": "Wewnętrzne myśli postaci"},
            {"type": "description", "pl": "Opis", "description": "Opis miejsca/osoby"},
            {"type": "action", "pl": "Akcja", "description": "Scena akcji"}
        ]
    }


@router.get("/genre-narrators")
async def get_genre_narrators() -> Dict[str, Any]:
    """Get recommended narrator voices by genre"""
    return {
        "recommendations": {
            "thriller": {"voice": "onyx", "description": "Głęboki, dramatyczny głos"},
            "romance": {"voice": "shimmer", "description": "Ciepły, romantyczny głos"},
            "fantasy": {"voice": "fable", "description": "Epicki, baśniowy głos"},
            "horror": {"voice": "echo", "description": "Niepokojący, tajemniczy głos"},
            "mystery": {"voice": "alloy", "description": "Neutralny, budujący napięcie"},
            "scifi": {"voice": "nova", "description": "Nowoczesny, futurystyczny głos"},
            "drama": {"voice": "alloy", "description": "Wszechstronny, zbalansowany"}
        }
    }
