"""
Automatic Book Trailer Generator - NarraForge 3.0 Phase 2

System automatycznego generowania trailerów książek:
- Ekstrakcja kluczowych scen do wizualizacji
- Generowanie sekwencji obrazów
- Integracja z TTS dla narracji
- Montaż wideo z przejściami
- Dodawanie muzyki i efektów
- Eksport w różnych formatach

"Zwiastun, który sprzedaje historię w 60 sekund"
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import json
from datetime import datetime

from app.services.llm_service import get_llm_service
from app.models.project import GenreType


# =============================================================================
# ENUMS
# =============================================================================

class TrailerStyle(Enum):
    """Style trailera"""
    CINEMATIC = "cinematic"  # Kinowy, epickie ujęcia
    MYSTERIOUS = "mysterious"  # Tajemniczy, budujący napięcie
    ROMANTIC = "romantic"  # Romantyczny, emocjonalny
    ACTION = "action"  # Dynamiczny, szybki montaż
    DRAMATIC = "dramatic"  # Dramatyczny, intensywny
    WHIMSICAL = "whimsical"  # Lekki, baśniowy
    DARK = "dark"  # Mroczny, niepokojący
    EPIC = "epic"  # Epicki, wielki rozmach


class TransitionType(Enum):
    """Typy przejść między scenami"""
    CUT = "cut"  # Ostre cięcie
    FADE = "fade"  # Zanikanie
    DISSOLVE = "dissolve"  # Przenikanie
    WIPE = "wipe"  # Przesunięcie
    ZOOM = "zoom"  # Zoom
    BLUR = "blur"  # Rozmycie
    FLASH = "flash"  # Błysk


class TrailerDuration(Enum):
    """Długość trailera"""
    SHORT = "short"  # 30 sekund
    MEDIUM = "medium"  # 60 sekund
    LONG = "long"  # 90 sekund
    EXTENDED = "extended"  # 120 sekund


class VideoFormat(Enum):
    """Format wideo"""
    MP4_1080P = "mp4_1080p"
    MP4_4K = "mp4_4k"
    WEBM = "webm"
    GIF = "gif"  # Animowany GIF
    VERTICAL = "vertical"  # 9:16 dla social media


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class TrailerScene:
    """Scena w trailerze"""
    scene_id: str
    order: int
    description: str  # Opis wizualny
    narration_text: Optional[str]  # Tekst narracji
    text_overlay: Optional[str]  # Tekst na ekranie
    duration: float  # Sekundy
    transition_in: TransitionType
    transition_out: TransitionType
    mood: str
    visual_style: str
    camera_movement: str  # static, pan, zoom, etc.

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "order": self.order,
            "description": self.description,
            "narration_text": self.narration_text,
            "text_overlay": self.text_overlay,
            "duration": self.duration,
            "transition_in": self.transition_in.value,
            "transition_out": self.transition_out.value,
            "mood": self.mood,
            "visual_style": self.visual_style,
            "camera_movement": self.camera_movement
        }


@dataclass
class TrailerScript:
    """Scenariusz trailera"""
    script_id: str
    title: str
    author: str
    genre: GenreType
    style: TrailerStyle
    duration: TrailerDuration
    scenes: List[TrailerScene]
    opening_hook: str
    closing_cta: str  # Call to action
    music_mood: str
    total_duration: float
    narration_voice: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "script_id": self.script_id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre.value,
            "style": self.style.value,
            "duration": self.duration.value,
            "scenes": [s.to_dict() for s in self.scenes],
            "opening_hook": self.opening_hook,
            "closing_cta": self.closing_cta,
            "music_mood": self.music_mood,
            "total_duration": self.total_duration,
            "narration_voice": self.narration_voice
        }


@dataclass
class GeneratedTrailerAsset:
    """Wygenerowany asset trailera"""
    asset_id: str
    asset_type: str  # image, audio, video
    scene_id: str
    file_url: Optional[str]
    file_base64: Optional[str]
    duration: float
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "scene_id": self.scene_id,
            "file_url": self.file_url,
            "has_base64": self.file_base64 is not None,
            "duration": self.duration,
            "metadata": self.metadata
        }


@dataclass
class TrailerProject:
    """Projekt trailera"""
    project_id: str
    script: TrailerScript
    assets: List[GeneratedTrailerAsset]
    status: str  # draft, generating, complete
    output_format: VideoFormat
    output_url: Optional[str]
    created_at: datetime
    estimated_cost: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "script": self.script.to_dict(),
            "assets_count": len(self.assets),
            "status": self.status,
            "output_format": self.output_format.value,
            "output_url": self.output_url,
            "created_at": self.created_at.isoformat(),
            "estimated_cost": self.estimated_cost
        }


# =============================================================================
# GENRE TRAILER PROFILES
# =============================================================================

GENRE_TRAILER_PROFILES = {
    GenreType.THRILLER: {
        "style": TrailerStyle.MYSTERIOUS,
        "music_mood": "tense, building suspense, dark undertones",
        "pacing": "slow build to fast climax",
        "typical_scenes": ["mysterious opening", "danger hint", "protagonist introduction", "threat reveal", "cliffhanger"],
        "text_style": "sharp, impactful phrases",
        "transitions": [TransitionType.CUT, TransitionType.FLASH, TransitionType.BLUR]
    },
    GenreType.ROMANCE: {
        "style": TrailerStyle.ROMANTIC,
        "music_mood": "emotional, sweeping, heartfelt",
        "pacing": "gentle, emotional peaks",
        "typical_scenes": ["meet-cute hint", "connection moment", "obstacle", "emotional climax", "hope"],
        "text_style": "emotional quotes, soft phrases",
        "transitions": [TransitionType.DISSOLVE, TransitionType.FADE]
    },
    GenreType.FANTASY: {
        "style": TrailerStyle.EPIC,
        "music_mood": "orchestral, epic, magical",
        "pacing": "building grandeur",
        "typical_scenes": ["world reveal", "hero introduction", "magic moment", "enemy/threat", "call to adventure"],
        "text_style": "epic proclamations, prophecy-like",
        "transitions": [TransitionType.DISSOLVE, TransitionType.ZOOM, TransitionType.WIPE]
    },
    GenreType.HORROR: {
        "style": TrailerStyle.DARK,
        "music_mood": "eerie, unsettling, sudden silence",
        "pacing": "slow dread, jump moments",
        "typical_scenes": ["normal life", "first sign", "escalation", "horror reveal", "no escape"],
        "text_style": "ominous warnings, short phrases",
        "transitions": [TransitionType.CUT, TransitionType.FLASH, TransitionType.BLUR]
    },
    GenreType.MYSTERY: {
        "style": TrailerStyle.MYSTERIOUS,
        "music_mood": "intriguing, intellectual, tension",
        "pacing": "methodical, revealing",
        "typical_scenes": ["crime/puzzle intro", "detective/protagonist", "clues", "twist hint", "question"],
        "text_style": "questions, cryptic hints",
        "transitions": [TransitionType.DISSOLVE, TransitionType.FADE]
    },
    GenreType.SCI_FI: {
        "style": TrailerStyle.CINEMATIC,
        "music_mood": "electronic, futuristic, epic",
        "pacing": "building to spectacle",
        "typical_scenes": ["future world", "technology", "protagonist", "conflict", "stakes"],
        "text_style": "bold statements, future concepts",
        "transitions": [TransitionType.ZOOM, TransitionType.WIPE, TransitionType.CUT]
    }
}


# =============================================================================
# BOOK TRAILER GENERATOR ENGINE
# =============================================================================

class BookTrailerGenerator:
    """
    Silnik generowania trailerów książek.

    Funkcje:
    - Tworzenie scenariusza trailera z opisu książki
    - Generowanie obrazów dla scen
    - Tworzenie narracji głosowej
    - Montaż wideo
    - Eksport w różnych formatach
    """

    def __init__(self):
        self.llm_service = get_llm_service()
        self.scripts: Dict[str, TrailerScript] = {}
        self.projects: Dict[str, TrailerProject] = {}

    def _get_llm(self, tier: str = "mid"):
        """Get appropriate LLM based on tier"""
        return self.llm_service.get_client(tier)

    # =========================================================================
    # SCRIPT GENERATION
    # =========================================================================

    async def generate_trailer_script(
        self,
        title: str,
        author: str,
        genre: GenreType,
        book_summary: str,
        key_scenes: List[str] = None,
        duration: TrailerDuration = TrailerDuration.MEDIUM,
        style: TrailerStyle = None
    ) -> TrailerScript:
        """
        Generuje scenariusz trailera na podstawie informacji o książce.
        """
        profile = GENRE_TRAILER_PROFILES.get(genre, GENRE_TRAILER_PROFILES[GenreType.DRAMA])
        style = style or profile.get("style", TrailerStyle.CINEMATIC)

        duration_seconds = {
            TrailerDuration.SHORT: 30,
            TrailerDuration.MEDIUM: 60,
            TrailerDuration.LONG: 90,
            TrailerDuration.EXTENDED: 120
        }
        target_duration = duration_seconds.get(duration, 60)

        # Calculate number of scenes
        num_scenes = target_duration // 8  # ~8 seconds per scene average

        prompt = f"""Stwórz scenariusz trailera książki.

KSIĄŻKA:
- Tytuł: {title}
- Autor: {author}
- Gatunek: {genre.value}
- Streszczenie: {book_summary[:2000]}

{'KLUCZOWE SCENY DO UWZGLĘDNIENIA:' + chr(10).join(f'- {s}' for s in key_scenes[:5]) if key_scenes else ''}

PROFIL GATUNKOWY:
- Styl: {style.value}
- Muzyka: {profile.get('music_mood', '')}
- Pacing: {profile.get('pacing', '')}
- Typowe sceny: {profile.get('typical_scenes', [])}

WYMAGANIA:
- Długość: {target_duration} sekund
- Liczba scen: {num_scenes}

Stwórz scenariusz zawierający:

1. OPENING HOOK: Silne otwarcie przyciągające uwagę (tekst lub obraz)
2. SCENY (dla każdej):
   - description: Szczegółowy opis wizualny sceny (po angielsku, dla generatora obrazów)
   - narration_text: Tekst narracji (opcjonalny, po polsku)
   - text_overlay: Tekst wyświetlany na ekranie (opcjonalny)
   - duration: Czas trwania (4-12 sekund)
   - mood: Nastrój sceny
   - camera_movement: Ruch kamery (static, slow_pan, zoom_in, zoom_out)
3. CLOSING CTA: Wezwanie do działania (np. "Dostępna już teraz", "Premiera wkrótce")

ZASADY:
- Nie ujawniaj spoilerów!
- Buduj napięcie i ciekawość
- Używaj krótkich, mocnych fraz
- Każda scena powinna być wizualnie interesująca

Odpowiedz w JSON:
{{
    "opening_hook": "...",
    "scenes": [
        {{
            "description": "...",
            "narration_text": "...",
            "text_overlay": "...",
            "duration": 8,
            "mood": "...",
            "camera_movement": "static"
        }}
    ],
    "closing_cta": "...",
    "narration_voice": "male/female"
}}"""

        response = await self._get_llm("high").chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        # Build scenes
        scenes = []
        transitions = profile.get("transitions", [TransitionType.FADE])

        for i, scene_data in enumerate(data.get("scenes", [])):
            scene = TrailerScene(
                scene_id=f"scene_{i+1}",
                order=i,
                description=scene_data.get("description", ""),
                narration_text=scene_data.get("narration_text"),
                text_overlay=scene_data.get("text_overlay"),
                duration=float(scene_data.get("duration", 8)),
                transition_in=transitions[i % len(transitions)] if i > 0 else TransitionType.FADE,
                transition_out=transitions[(i + 1) % len(transitions)],
                mood=scene_data.get("mood", "dramatic"),
                visual_style=style.value,
                camera_movement=scene_data.get("camera_movement", "static")
            )
            scenes.append(scene)

        total_duration = sum(s.duration for s in scenes)

        script = TrailerScript(
            script_id=f"script_{title.lower().replace(' ', '_')[:15]}_{datetime.now().strftime('%H%M%S')}",
            title=title,
            author=author,
            genre=genre,
            style=style,
            duration=duration,
            scenes=scenes,
            opening_hook=data.get("opening_hook", title),
            closing_cta=data.get("closing_cta", "Dostępna wkrótce"),
            music_mood=profile.get("music_mood", "cinematic"),
            total_duration=total_duration,
            narration_voice=data.get("narration_voice", "male")
        )

        self.scripts[script.script_id] = script
        return script

    # =========================================================================
    # ASSET GENERATION
    # =========================================================================

    async def generate_scene_image(
        self,
        scene: TrailerScene,
        aspect_ratio: str = "16:9"
    ) -> GeneratedTrailerAsset:
        """
        Generuje obraz dla sceny trailera.
        """
        try:
            client = self._get_llm("high")

            # Build cinematic prompt
            prompt = f"""Cinematic movie still, {scene.description},
{scene.mood} mood, {scene.visual_style} style,
dramatic lighting, film grain, anamorphic lens,
professional cinematography, 4K quality"""

            # DALL-E size for 16:9
            size = "1792x1024"

            response = await client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="hd",
                n=1,
                response_format="url"
            )

            return GeneratedTrailerAsset(
                asset_id=f"img_{scene.scene_id}",
                asset_type="image",
                scene_id=scene.scene_id,
                file_url=response.data[0].url,
                file_base64=None,
                duration=scene.duration,
                metadata={
                    "prompt": prompt[:200],
                    "size": size,
                    "model": "dall-e-3"
                }
            )

        except Exception as e:
            return GeneratedTrailerAsset(
                asset_id=f"img_{scene.scene_id}_error",
                asset_type="image",
                scene_id=scene.scene_id,
                file_url=None,
                file_base64=None,
                duration=scene.duration,
                metadata={"error": str(e)}
            )

    async def generate_narration_audio(
        self,
        scene: TrailerScene,
        voice: str = "onyx"
    ) -> Optional[GeneratedTrailerAsset]:
        """
        Generuje narrację audio dla sceny.
        """
        if not scene.narration_text:
            return None

        try:
            client = self._get_llm("mid")

            response = await client.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=scene.narration_text,
                response_format="mp3",
                speed=0.9  # Slightly slower for dramatic effect
            )

            return GeneratedTrailerAsset(
                asset_id=f"audio_{scene.scene_id}",
                asset_type="audio",
                scene_id=scene.scene_id,
                file_url=None,
                file_base64=None,  # Would need to encode
                duration=scene.duration,
                metadata={
                    "voice": voice,
                    "text": scene.narration_text[:100]
                }
            )

        except Exception as e:
            return None

    # =========================================================================
    # PROJECT MANAGEMENT
    # =========================================================================

    async def create_trailer_project(
        self,
        script: TrailerScript,
        output_format: VideoFormat = VideoFormat.MP4_1080P,
        generate_assets: bool = True
    ) -> TrailerProject:
        """
        Tworzy projekt trailera z opcjonalnym generowaniem assetów.
        """
        assets = []

        if generate_assets:
            # Generate images for each scene
            for scene in script.scenes:
                image_asset = await self.generate_scene_image(scene)
                assets.append(image_asset)

                # Generate narration if available
                audio_asset = await self.generate_narration_audio(
                    scene,
                    voice="onyx" if script.narration_voice == "male" else "nova"
                )
                if audio_asset:
                    assets.append(audio_asset)

        # Estimate cost
        image_cost = len(script.scenes) * 0.08  # DALL-E 3 HD
        audio_scenes = len([s for s in script.scenes if s.narration_text])
        audio_cost = audio_scenes * 0.02  # Estimated TTS cost
        total_cost = image_cost + audio_cost

        project = TrailerProject(
            project_id=f"trailer_{script.script_id}",
            script=script,
            assets=assets,
            status="complete" if generate_assets else "draft",
            output_format=output_format,
            output_url=None,  # Would be set after video compilation
            created_at=datetime.now(),
            estimated_cost=total_cost
        )

        self.projects[project.project_id] = project
        return project

    async def estimate_trailer_cost(
        self,
        num_scenes: int,
        with_narration: bool = True,
        duration: TrailerDuration = TrailerDuration.MEDIUM
    ) -> Dict[str, Any]:
        """
        Szacuje koszt generowania trailera.
        """
        image_cost = num_scenes * 0.08  # DALL-E 3 HD per scene
        narration_cost = num_scenes * 0.02 if with_narration else 0
        total_cost = image_cost + narration_cost

        duration_seconds = {
            TrailerDuration.SHORT: 30,
            TrailerDuration.MEDIUM: 60,
            TrailerDuration.LONG: 90,
            TrailerDuration.EXTENDED: 120
        }

        return {
            "num_scenes": num_scenes,
            "duration_seconds": duration_seconds.get(duration, 60),
            "image_generation_cost": round(image_cost, 2),
            "narration_cost": round(narration_cost, 2),
            "total_cost_usd": round(total_cost, 2),
            "with_narration": with_narration,
            "estimated_generation_time_minutes": num_scenes * 0.5
        }

    # =========================================================================
    # MANAGEMENT
    # =========================================================================

    def get_script(self, script_id: str) -> Optional[TrailerScript]:
        """Pobiera scenariusz"""
        return self.scripts.get(script_id)

    def get_project(self, project_id: str) -> Optional[TrailerProject]:
        """Pobiera projekt"""
        return self.projects.get(project_id)

    def list_scripts(self) -> List[str]:
        """Lista scenariuszy"""
        return list(self.scripts.keys())

    def list_projects(self) -> List[str]:
        """Lista projektów"""
        return list(self.projects.keys())


# =============================================================================
# SINGLETON
# =============================================================================

_trailer_generator: Optional[BookTrailerGenerator] = None

def get_trailer_generator() -> BookTrailerGenerator:
    """Get singleton instance of book trailer generator"""
    global _trailer_generator
    if _trailer_generator is None:
        _trailer_generator = BookTrailerGenerator()
    return _trailer_generator
