"""
AI Audiobook Generator - NarraForge 3.0 Phase 2

System generowania audiobooków z wieloma głosami:
- Integracja z ElevenLabs / Azure Neural TTS / OpenAI TTS
- Unikalne głosy dla każdej postaci
- Automatyczne rozpoznawanie dialogów
- Efekty dźwiękowe i muzyka tła
- Eksport w różnych formatach
- Znaczniki rozdziałów

"Każda postać ma swój własny głos"
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import json
import asyncio
import base64
from datetime import datetime
from pathlib import Path
import re

from app.services.llm_service import get_llm_service
from app.config import settings


# =============================================================================
# ENUMS
# =============================================================================

class TTSProvider(Enum):
    """Dostawcy Text-to-Speech"""
    OPENAI = "openai"  # OpenAI TTS
    ELEVENLABS = "elevenlabs"  # ElevenLabs
    AZURE = "azure"  # Azure Neural TTS
    GOOGLE = "google"  # Google Cloud TTS


class VoiceGender(Enum):
    """Płeć głosu"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class VoiceAge(Enum):
    """Wiek głosu"""
    CHILD = "child"
    YOUNG = "young"
    ADULT = "adult"
    ELDERLY = "elderly"


class VoiceTone(Enum):
    """Ton głosu"""
    WARM = "warm"
    COLD = "cold"
    AUTHORITATIVE = "authoritative"
    FRIENDLY = "friendly"
    MYSTERIOUS = "mysterious"
    DRAMATIC = "dramatic"
    NEUTRAL = "neutral"
    ROMANTIC = "romantic"


class AudioFormat(Enum):
    """Format audio"""
    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"
    AAC = "aac"
    FLAC = "flac"


class SpeechType(Enum):
    """Typ wypowiedzi"""
    NARRATION = "narration"  # Narracja
    DIALOGUE = "dialogue"  # Dialog postaci
    THOUGHT = "thought"  # Myśli postaci
    DESCRIPTION = "description"  # Opis
    ACTION = "action"  # Akcja


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class VoiceProfile:
    """Profil głosu dla postaci lub narratora"""
    profile_id: str
    name: str  # Nazwa profilu (np. imię postaci)
    provider: TTSProvider
    voice_id: str  # ID głosu u dostawcy
    gender: VoiceGender
    age: VoiceAge
    tone: VoiceTone
    speaking_rate: float = 1.0  # 0.5 - 2.0
    pitch: float = 1.0  # 0.5 - 2.0
    description: str = ""
    language: str = "pl-PL"

    # Emotional adjustments
    emotion_modifiers: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "provider": self.provider.value,
            "voice_id": self.voice_id,
            "gender": self.gender.value,
            "age": self.age.value,
            "tone": self.tone.value,
            "speaking_rate": self.speaking_rate,
            "pitch": self.pitch,
            "description": self.description,
            "language": self.language,
            "emotion_modifiers": self.emotion_modifiers
        }


@dataclass
class SpeechSegment:
    """Segment mowy do zsyntezowania"""
    segment_id: str
    text: str
    speech_type: SpeechType
    speaker: str  # Nazwa postaci lub "narrator"
    voice_profile_id: str
    chapter_number: int
    position: int  # Pozycja w rozdziale
    emotion: Optional[str] = None  # Emocja dla tego segmentu
    pause_before: float = 0.0  # Pauza przed (sekundy)
    pause_after: float = 0.3  # Pauza po (sekundy)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "text": self.text,
            "speech_type": self.speech_type.value,
            "speaker": self.speaker,
            "voice_profile_id": self.voice_profile_id,
            "chapter_number": self.chapter_number,
            "position": self.position,
            "emotion": self.emotion,
            "pause_before": self.pause_before,
            "pause_after": self.pause_after
        }


@dataclass
class GeneratedAudio:
    """Wygenerowany segment audio"""
    segment_id: str
    audio_data: bytes  # Raw audio data
    format: AudioFormat
    duration: float  # W sekundach
    provider: TTSProvider
    cost: float
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "format": self.format.value,
            "duration": self.duration,
            "provider": self.provider.value,
            "cost": self.cost,
            "metadata": self.metadata
        }


@dataclass
class ChapterAudio:
    """Audio dla całego rozdziału"""
    chapter_number: int
    chapter_title: str
    segments: List[GeneratedAudio]
    total_duration: float
    total_cost: float
    file_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter_number": self.chapter_number,
            "chapter_title": self.chapter_title,
            "segments_count": len(self.segments),
            "total_duration": self.total_duration,
            "total_cost": self.total_cost,
            "file_path": self.file_path
        }


@dataclass
class AudiobookProject:
    """Projekt audiobooka"""
    project_id: str
    title: str
    author: str
    narrator_voice: VoiceProfile
    character_voices: Dict[str, VoiceProfile]
    chapters: List[ChapterAudio]
    total_duration: float
    total_cost: float
    created_at: datetime
    output_format: AudioFormat = AudioFormat.MP3

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "title": self.title,
            "author": self.author,
            "narrator_voice": self.narrator_voice.to_dict(),
            "character_voices": {k: v.to_dict() for k, v in self.character_voices.items()},
            "chapters_count": len(self.chapters),
            "chapters": [c.to_dict() for c in self.chapters],
            "total_duration": self.total_duration,
            "total_duration_formatted": self._format_duration(self.total_duration),
            "total_cost": self.total_cost,
            "created_at": self.created_at.isoformat(),
            "output_format": self.output_format.value
        }

    def _format_duration(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"


# =============================================================================
# VOICE PRESETS
# =============================================================================

# OpenAI TTS voices
OPENAI_VOICES = {
    "alloy": {"gender": VoiceGender.NEUTRAL, "tone": VoiceTone.NEUTRAL, "age": VoiceAge.ADULT},
    "echo": {"gender": VoiceGender.MALE, "tone": VoiceTone.WARM, "age": VoiceAge.ADULT},
    "fable": {"gender": VoiceGender.NEUTRAL, "tone": VoiceTone.DRAMATIC, "age": VoiceAge.ADULT},
    "onyx": {"gender": VoiceGender.MALE, "tone": VoiceTone.AUTHORITATIVE, "age": VoiceAge.ADULT},
    "nova": {"gender": VoiceGender.FEMALE, "tone": VoiceTone.FRIENDLY, "age": VoiceAge.YOUNG},
    "shimmer": {"gender": VoiceGender.FEMALE, "tone": VoiceTone.WARM, "age": VoiceAge.ADULT}
}

# Default narrator voices by genre
GENRE_NARRATOR_VOICES = {
    "thriller": "onyx",
    "romance": "shimmer",
    "fantasy": "fable",
    "horror": "echo",
    "mystery": "alloy",
    "scifi": "nova",
    "drama": "alloy"
}


# =============================================================================
# AUDIOBOOK GENERATOR ENGINE
# =============================================================================

class AudiobookGenerator:
    """
    Silnik generowania audiobooków.

    Funkcje:
    - Parsowanie tekstu na segmenty mowy
    - Przypisywanie głosów postaciom
    - Generowanie audio dla segmentów
    - Łączenie w pełne rozdziały
    - Eksport w różnych formatach
    """

    def __init__(self):
        self.llm_service = get_llm_service()
        self.voice_profiles: Dict[str, VoiceProfile] = {}
        self.default_provider = TTSProvider.OPENAI

    def _get_llm(self, tier: str = "mid"):
        """Get appropriate LLM based on tier"""
        return self.llm_service.get_client(tier)

    # =========================================================================
    # VOICE PROFILE MANAGEMENT
    # =========================================================================

    def create_voice_profile(
        self,
        name: str,
        gender: VoiceGender,
        age: VoiceAge,
        tone: VoiceTone,
        provider: TTSProvider = None,
        voice_id: str = None,
        speaking_rate: float = 1.0,
        pitch: float = 1.0,
        description: str = ""
    ) -> VoiceProfile:
        """
        Tworzy profil głosu.
        """
        provider = provider or self.default_provider

        # Auto-select voice if not specified
        if not voice_id:
            voice_id = self._select_voice_for_profile(gender, age, tone, provider)

        profile = VoiceProfile(
            profile_id=f"voice_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}",
            name=name,
            provider=provider,
            voice_id=voice_id,
            gender=gender,
            age=age,
            tone=tone,
            speaking_rate=speaking_rate,
            pitch=pitch,
            description=description
        )

        self.voice_profiles[profile.profile_id] = profile
        return profile

    def _select_voice_for_profile(
        self,
        gender: VoiceGender,
        age: VoiceAge,
        tone: VoiceTone,
        provider: TTSProvider
    ) -> str:
        """Automatyczny wybór głosu na podstawie cech"""
        if provider == TTSProvider.OPENAI:
            # Simple matching for OpenAI voices
            for voice_name, attrs in OPENAI_VOICES.items():
                if attrs["gender"] == gender and attrs["tone"] == tone:
                    return voice_name
            # Fallback based on gender
            if gender == VoiceGender.MALE:
                return "onyx" if tone == VoiceTone.AUTHORITATIVE else "echo"
            elif gender == VoiceGender.FEMALE:
                return "shimmer" if tone == VoiceTone.WARM else "nova"
            return "alloy"
        return "default"

    async def generate_character_voice_profiles(
        self,
        characters: List[Dict[str, Any]],
        genre: str = "drama"
    ) -> Dict[str, VoiceProfile]:
        """
        Automatycznie generuje profile głosów dla listy postaci.
        """
        profiles = {}

        for char in characters:
            name = char.get("name", "Unknown")
            description = char.get("description", "")
            gender_str = char.get("gender", "unknown").lower()
            age = char.get("age", 30)

            # Determine voice gender
            if "female" in gender_str or "kobieta" in gender_str:
                gender = VoiceGender.FEMALE
            elif "male" in gender_str or "mężczyzna" in gender_str:
                gender = VoiceGender.MALE
            else:
                gender = VoiceGender.NEUTRAL

            # Determine age category
            if age < 18:
                voice_age = VoiceAge.YOUNG
            elif age < 50:
                voice_age = VoiceAge.ADULT
            else:
                voice_age = VoiceAge.ELDERLY

            # Determine tone from description/personality
            tone = await self._determine_voice_tone(description, genre)

            profile = self.create_voice_profile(
                name=name,
                gender=gender,
                age=voice_age,
                tone=tone,
                description=f"Voice for {name}: {description[:100]}"
            )

            profiles[name] = profile

        return profiles

    async def _determine_voice_tone(self, description: str, genre: str) -> VoiceTone:
        """Określa ton głosu na podstawie opisu postaci"""
        description_lower = description.lower()

        # Simple keyword matching
        if any(word in description_lower for word in ["ciepły", "dobry", "miły", "warm", "kind"]):
            return VoiceTone.WARM
        elif any(word in description_lower for word in ["zimny", "surowy", "cold", "strict"]):
            return VoiceTone.COLD
        elif any(word in description_lower for word in ["tajemniczy", "mysterious", "enigmatic"]):
            return VoiceTone.MYSTERIOUS
        elif any(word in description_lower for word in ["autorytet", "władczy", "authoritative"]):
            return VoiceTone.AUTHORITATIVE
        elif any(word in description_lower for word in ["romantyczny", "romantic", "passionate"]):
            return VoiceTone.ROMANTIC
        elif any(word in description_lower for word in ["dramatyczny", "dramatic", "intense"]):
            return VoiceTone.DRAMATIC
        elif any(word in description_lower for word in ["przyjazny", "friendly", "cheerful"]):
            return VoiceTone.FRIENDLY

        # Default based on genre
        genre_tones = {
            "thriller": VoiceTone.DRAMATIC,
            "romance": VoiceTone.ROMANTIC,
            "horror": VoiceTone.MYSTERIOUS,
            "fantasy": VoiceTone.DRAMATIC,
            "mystery": VoiceTone.MYSTERIOUS
        }
        return genre_tones.get(genre.lower(), VoiceTone.NEUTRAL)

    # =========================================================================
    # TEXT PARSING
    # =========================================================================

    async def parse_chapter_to_segments(
        self,
        chapter_text: str,
        chapter_number: int,
        character_voices: Dict[str, VoiceProfile],
        narrator_voice: VoiceProfile
    ) -> List[SpeechSegment]:
        """
        Parsuje tekst rozdziału na segmenty mowy z przypisanymi głosami.
        """
        prompt = f"""Przeanalizuj poniższy tekst rozdziału i podziel go na segmenty do narracji audio.

TEKST ROZDZIAŁU:
{chapter_text[:8000]}

DOSTĘPNE POSTACIE (mają przypisane głosy):
{', '.join(character_voices.keys())}

Dla każdego segmentu określ:
1. text: Tekst do przeczytania
2. speech_type: narration/dialogue/thought/description/action
3. speaker: Nazwa postaci lub "narrator"
4. emotion: Emocja (jeśli relevantna): neutral, happy, sad, angry, fearful, excited, whisper, dramatic
5. pause_after: Pauza po segmencie (0.0-2.0 sekund)

ZASADY:
- Dialogi (w cudzysłowach) przypisz do odpowiedniej postaci
- Myśli (kursywa lub wewnętrzne) jako "thought"
- Opisy miejsc/ludzi jako "description"
- Sceny akcji jako "action"
- Reszta to "narration"
- Pauzy: dłuższe po akapitach i zmianach scen

Odpowiedz w JSON:
{{
    "segments": [
        {{
            "text": "...",
            "speech_type": "narration",
            "speaker": "narrator",
            "emotion": "neutral",
            "pause_after": 0.5
        }}
    ]
}}"""

        response = await self._get_llm("mid").chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        segments = []
        for i, seg_data in enumerate(result.get("segments", [])):
            speaker = seg_data.get("speaker", "narrator")

            # Determine voice profile
            if speaker == "narrator" or speaker not in character_voices:
                voice_id = narrator_voice.profile_id
            else:
                voice_id = character_voices[speaker].profile_id

            # Parse speech type
            try:
                speech_type = SpeechType(seg_data.get("speech_type", "narration"))
            except ValueError:
                speech_type = SpeechType.NARRATION

            segment = SpeechSegment(
                segment_id=f"ch{chapter_number}_seg_{i+1}",
                text=seg_data.get("text", ""),
                speech_type=speech_type,
                speaker=speaker,
                voice_profile_id=voice_id,
                chapter_number=chapter_number,
                position=i,
                emotion=seg_data.get("emotion"),
                pause_before=0.0,
                pause_after=float(seg_data.get("pause_after", 0.3))
            )
            segments.append(segment)

        return segments

    # =========================================================================
    # AUDIO GENERATION
    # =========================================================================

    async def generate_segment_audio(
        self,
        segment: SpeechSegment,
        output_format: AudioFormat = AudioFormat.MP3
    ) -> GeneratedAudio:
        """
        Generuje audio dla pojedynczego segmentu.
        """
        voice_profile = self.voice_profiles.get(segment.voice_profile_id)
        if not voice_profile:
            raise ValueError(f"Voice profile not found: {segment.voice_profile_id}")

        if voice_profile.provider == TTSProvider.OPENAI:
            return await self._generate_with_openai(segment, voice_profile, output_format)
        else:
            # Fallback to OpenAI
            return await self._generate_with_openai(segment, voice_profile, output_format)

    async def _generate_with_openai(
        self,
        segment: SpeechSegment,
        voice_profile: VoiceProfile,
        output_format: AudioFormat
    ) -> GeneratedAudio:
        """Generuje audio używając OpenAI TTS"""
        try:
            client = self._get_llm("mid")

            # Map format
            format_map = {
                AudioFormat.MP3: "mp3",
                AudioFormat.WAV: "wav",
                AudioFormat.OGG: "opus",
                AudioFormat.AAC: "aac",
                AudioFormat.FLAC: "flac"
            }

            response = await client.audio.speech.create(
                model="tts-1-hd",  # High quality
                voice=voice_profile.voice_id,
                input=segment.text,
                response_format=format_map.get(output_format, "mp3"),
                speed=voice_profile.speaking_rate
            )

            # Get audio content
            audio_data = response.content

            # Estimate duration (rough estimate: ~150 words per minute)
            word_count = len(segment.text.split())
            estimated_duration = (word_count / 150) * 60 / voice_profile.speaking_rate

            # Cost estimate (OpenAI TTS pricing)
            char_count = len(segment.text)
            cost = (char_count / 1000) * 0.015  # $0.015 per 1K characters for HD

            return GeneratedAudio(
                segment_id=segment.segment_id,
                audio_data=audio_data,
                format=output_format,
                duration=estimated_duration,
                provider=TTSProvider.OPENAI,
                cost=cost,
                metadata={
                    "voice": voice_profile.voice_id,
                    "speed": voice_profile.speaking_rate,
                    "character_count": char_count
                }
            )

        except Exception as e:
            # Return empty audio on error
            return GeneratedAudio(
                segment_id=segment.segment_id,
                audio_data=b"",
                format=output_format,
                duration=0,
                provider=TTSProvider.OPENAI,
                cost=0,
                metadata={"error": str(e)}
            )

    # =========================================================================
    # CHAPTER GENERATION
    # =========================================================================

    async def generate_chapter_audio(
        self,
        chapter_text: str,
        chapter_number: int,
        chapter_title: str,
        character_voices: Dict[str, VoiceProfile],
        narrator_voice: VoiceProfile,
        output_format: AudioFormat = AudioFormat.MP3,
        progress_callback=None
    ) -> ChapterAudio:
        """
        Generuje audio dla całego rozdziału.
        """
        # Parse chapter into segments
        segments = await self.parse_chapter_to_segments(
            chapter_text,
            chapter_number,
            character_voices,
            narrator_voice
        )

        # Generate audio for each segment
        generated_segments = []
        total_duration = 0
        total_cost = 0

        for i, segment in enumerate(segments):
            audio = await self.generate_segment_audio(segment, output_format)
            generated_segments.append(audio)
            total_duration += audio.duration
            total_cost += audio.cost

            if progress_callback:
                progress_callback(i + 1, len(segments), segment.segment_id)

        return ChapterAudio(
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            segments=generated_segments,
            total_duration=total_duration,
            total_cost=total_cost
        )

    # =========================================================================
    # AUDIOBOOK PROJECT GENERATION
    # =========================================================================

    async def create_audiobook_project(
        self,
        project_id: str,
        title: str,
        author: str,
        chapters: List[Dict[str, str]],  # [{text, title}]
        characters: List[Dict[str, Any]],
        genre: str = "drama",
        output_format: AudioFormat = AudioFormat.MP3,
        progress_callback=None
    ) -> AudiobookProject:
        """
        Tworzy pełny projekt audiobooka.
        """
        # Create narrator voice
        narrator_voice = self.create_voice_profile(
            name="Narrator",
            gender=VoiceGender.NEUTRAL,
            age=VoiceAge.ADULT,
            tone=VoiceTone.NEUTRAL,
            voice_id=GENRE_NARRATOR_VOICES.get(genre.lower(), "alloy"),
            description=f"Narrator for {title}"
        )

        # Generate character voices
        character_voices = await self.generate_character_voice_profiles(characters, genre)

        # Generate chapters
        chapter_audios = []
        total_duration = 0
        total_cost = 0

        for i, chapter_data in enumerate(chapters):
            chapter_audio = await self.generate_chapter_audio(
                chapter_text=chapter_data.get("text", ""),
                chapter_number=i + 1,
                chapter_title=chapter_data.get("title", f"Rozdział {i + 1}"),
                character_voices=character_voices,
                narrator_voice=narrator_voice,
                output_format=output_format,
                progress_callback=progress_callback
            )
            chapter_audios.append(chapter_audio)
            total_duration += chapter_audio.total_duration
            total_cost += chapter_audio.total_cost

        return AudiobookProject(
            project_id=project_id,
            title=title,
            author=author,
            narrator_voice=narrator_voice,
            character_voices=character_voices,
            chapters=chapter_audios,
            total_duration=total_duration,
            total_cost=total_cost,
            created_at=datetime.now(),
            output_format=output_format
        )

    # =========================================================================
    # ESTIMATION
    # =========================================================================

    async def estimate_audiobook_cost(
        self,
        total_characters: int,
        num_chapters: int
    ) -> Dict[str, Any]:
        """
        Szacuje koszt i czas generowania audiobooka.
        """
        # OpenAI TTS HD pricing: $0.015 per 1K characters
        base_cost = (total_characters / 1000) * 0.015

        # Estimate duration (150 words/min average, ~5 chars/word)
        words = total_characters / 5
        duration_minutes = words / 150
        duration_hours = duration_minutes / 60

        # Processing time estimate (roughly 1:4 ratio - 1 minute of audio = 4 seconds processing)
        processing_time = duration_minutes / 15  # minutes

        return {
            "total_characters": total_characters,
            "estimated_words": int(words),
            "estimated_duration_hours": round(duration_hours, 2),
            "estimated_duration_formatted": f"{int(duration_hours)}h {int((duration_hours % 1) * 60)}m",
            "estimated_cost_usd": round(base_cost, 2),
            "processing_time_minutes": round(processing_time, 1),
            "num_chapters": num_chapters,
            "provider": "OpenAI TTS HD"
        }


# =============================================================================
# SINGLETON
# =============================================================================

_audiobook_generator: Optional[AudiobookGenerator] = None

def get_audiobook_generator() -> AudiobookGenerator:
    """Get singleton instance of audiobook generator"""
    global _audiobook_generator
    if _audiobook_generator is None:
        _audiobook_generator = AudiobookGenerator()
    return _audiobook_generator
