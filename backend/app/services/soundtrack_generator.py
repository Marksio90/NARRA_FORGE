"""
Ambient Soundtrack Generation - NarraForge 3.0 Phase 2

System generowania ścieżek dźwiękowych do książek:
- Analiza emocjonalna rozdziałów
- Generowanie ambient music per rozdział
- Pętle muzyczne dla scen
- Integracja z audiobookami
- Efekty dźwiękowe dla atmosfery
- Eksport playlist

"Każdy rozdział ma swoją melodię"
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

class MusicMood(Enum):
    """Nastroje muzyczne"""
    PEACEFUL = "peaceful"  # Spokojny, relaksujący
    TENSE = "tense"  # Napięty, niepokojący
    DRAMATIC = "dramatic"  # Dramatyczny, intensywny
    ROMANTIC = "romantic"  # Romantyczny, ciepły
    MYSTERIOUS = "mysterious"  # Tajemniczy, enigmatyczny
    ACTION = "action"  # Akcja, energia
    SAD = "sad"  # Smutny, melancholijny
    JOYFUL = "joyful"  # Radosny, wesoły
    EPIC = "epic"  # Epicki, monumentalny
    HORROR = "horror"  # Przerażający, mroczny
    ADVENTURE = "adventure"  # Przygodowy, ekscytujący
    CONTEMPLATIVE = "contemplative"  # Kontemplacyjny, refleksyjny


class MusicGenre(Enum):
    """Gatunki muzyczne"""
    ORCHESTRAL = "orchestral"
    AMBIENT = "ambient"
    ELECTRONIC = "electronic"
    PIANO = "piano"
    ACOUSTIC = "acoustic"
    CINEMATIC = "cinematic"
    FOLK = "folk"
    JAZZ = "jazz"
    WORLD = "world"
    SYNTH = "synth"
    CHORAL = "choral"


class Instrument(Enum):
    """Główne instrumenty"""
    STRINGS = "strings"
    PIANO = "piano"
    SYNTH = "synth"
    GUITAR = "guitar"
    FLUTE = "flute"
    DRUMS = "drums"
    CHOIR = "choir"
    HARP = "harp"
    CELLO = "cello"
    VIOLIN = "violin"
    BELLS = "bells"
    PAD = "pad"


class SoundEffectType(Enum):
    """Typy efektów dźwiękowych"""
    NATURE = "nature"  # Przyroda (wiatr, deszcz, ptaki)
    URBAN = "urban"  # Miejskie (ulica, tłum)
    WEATHER = "weather"  # Pogoda
    INTERIOR = "interior"  # Wnętrze (ogień, zegar)
    HORROR = "horror"  # Horror (skrzypienie, szepty)
    FANTASY = "fantasy"  # Fantasy (magia, portale)
    SCIFI = "scifi"  # SciFi (komputery, statki)
    COMBAT = "combat"  # Walka (miecze, strzały)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class MusicParameters:
    """Parametry utworu muzycznego"""
    mood: MusicMood
    genre: MusicGenre
    tempo_bpm: int  # 60-180
    key: str  # C major, A minor, etc.
    primary_instruments: List[Instrument]
    intensity: float  # 0.0 - 1.0
    duration_seconds: int
    loop: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mood": self.mood.value,
            "genre": self.genre.value,
            "tempo_bpm": self.tempo_bpm,
            "key": self.key,
            "primary_instruments": [i.value for i in self.primary_instruments],
            "intensity": self.intensity,
            "duration_seconds": self.duration_seconds,
            "loop": self.loop
        }

    def to_prompt(self) -> str:
        """Konwertuje parametry na prompt dla generatora muzyki"""
        instruments = ", ".join(i.value for i in self.primary_instruments)
        return f"""{self.mood.value} {self.genre.value} music,
{self.tempo_bpm} BPM, key of {self.key},
featuring {instruments},
intensity level {int(self.intensity * 10)}/10,
{'loopable' if self.loop else 'with natural ending'},
duration {self.duration_seconds} seconds"""


@dataclass
class SoundEffect:
    """Efekt dźwiękowy"""
    effect_id: str
    effect_type: SoundEffectType
    description: str
    duration_seconds: float
    volume: float  # 0.0 - 1.0
    loop: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "effect_id": self.effect_id,
            "effect_type": self.effect_type.value,
            "description": self.description,
            "duration_seconds": self.duration_seconds,
            "volume": self.volume,
            "loop": self.loop
        }


@dataclass
class ChapterSoundscape:
    """Pejzaż dźwiękowy dla rozdziału"""
    chapter_number: int
    chapter_title: str
    music_parameters: MusicParameters
    ambient_effects: List[SoundEffect]
    emotional_arc: List[float]  # Intensity over time
    key_moments: List[Dict[str, Any]]  # Moments requiring special audio

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter_number": self.chapter_number,
            "chapter_title": self.chapter_title,
            "music_parameters": self.music_parameters.to_dict(),
            "ambient_effects": [e.to_dict() for e in self.ambient_effects],
            "emotional_arc": self.emotional_arc,
            "key_moments": self.key_moments
        }


@dataclass
class GeneratedTrack:
    """Wygenerowany utwór"""
    track_id: str
    chapter_number: int
    parameters: MusicParameters
    audio_url: Optional[str]
    duration: float
    metadata: Dict[str, Any]
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "track_id": self.track_id,
            "chapter_number": self.chapter_number,
            "parameters": self.parameters.to_dict(),
            "audio_url": self.audio_url,
            "duration": self.duration,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class BookSoundtrack:
    """Ścieżka dźwiękowa całej książki"""
    soundtrack_id: str
    book_title: str
    genre: GenreType
    chapter_soundscapes: List[ChapterSoundscape]
    generated_tracks: List[GeneratedTrack]
    total_duration: float
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "soundtrack_id": self.soundtrack_id,
            "book_title": self.book_title,
            "genre": self.genre.value,
            "chapters_count": len(self.chapter_soundscapes),
            "tracks_count": len(self.generated_tracks),
            "total_duration": self.total_duration,
            "total_duration_formatted": f"{int(self.total_duration // 60)}:{int(self.total_duration % 60):02d}",
            "created_at": self.created_at.isoformat()
        }


# =============================================================================
# GENRE MUSIC PROFILES
# =============================================================================

GENRE_MUSIC_PROFILES = {
    GenreType.THRILLER: {
        "primary_genres": [MusicGenre.CINEMATIC, MusicGenre.ELECTRONIC],
        "primary_moods": [MusicMood.TENSE, MusicMood.MYSTERIOUS, MusicMood.ACTION],
        "instruments": [Instrument.STRINGS, Instrument.SYNTH, Instrument.DRUMS],
        "tempo_range": (70, 140),
        "typical_effects": [SoundEffectType.URBAN, SoundEffectType.WEATHER],
        "keys": ["D minor", "E minor", "B minor"]
    },
    GenreType.ROMANCE: {
        "primary_genres": [MusicGenre.PIANO, MusicGenre.ACOUSTIC, MusicGenre.ORCHESTRAL],
        "primary_moods": [MusicMood.ROMANTIC, MusicMood.PEACEFUL, MusicMood.JOYFUL],
        "instruments": [Instrument.PIANO, Instrument.STRINGS, Instrument.GUITAR],
        "tempo_range": (60, 100),
        "typical_effects": [SoundEffectType.NATURE, SoundEffectType.INTERIOR],
        "keys": ["C major", "G major", "F major", "A major"]
    },
    GenreType.FANTASY: {
        "primary_genres": [MusicGenre.ORCHESTRAL, MusicGenre.CINEMATIC, MusicGenre.FOLK],
        "primary_moods": [MusicMood.EPIC, MusicMood.ADVENTURE, MusicMood.MYSTERIOUS],
        "instruments": [Instrument.STRINGS, Instrument.CHOIR, Instrument.FLUTE, Instrument.HARP],
        "tempo_range": (80, 150),
        "typical_effects": [SoundEffectType.NATURE, SoundEffectType.FANTASY],
        "keys": ["D major", "E minor", "C major", "A minor"]
    },
    GenreType.HORROR: {
        "primary_genres": [MusicGenre.AMBIENT, MusicGenre.CINEMATIC],
        "primary_moods": [MusicMood.HORROR, MusicMood.TENSE, MusicMood.MYSTERIOUS],
        "instruments": [Instrument.STRINGS, Instrument.SYNTH, Instrument.BELLS],
        "tempo_range": (50, 90),
        "typical_effects": [SoundEffectType.HORROR, SoundEffectType.WEATHER],
        "keys": ["D minor", "B minor", "F minor", "C minor"]
    },
    GenreType.SCIFI: {
        "primary_genres": [MusicGenre.ELECTRONIC, MusicGenre.SYNTH, MusicGenre.CINEMATIC],
        "primary_moods": [MusicMood.EPIC, MusicMood.MYSTERIOUS, MusicMood.ACTION],
        "instruments": [Instrument.SYNTH, Instrument.PAD, Instrument.DRUMS],
        "tempo_range": (80, 140),
        "typical_effects": [SoundEffectType.SCIFI],
        "keys": ["A minor", "E minor", "D minor"]
    },
    GenreType.MYSTERY: {
        "primary_genres": [MusicGenre.JAZZ, MusicGenre.PIANO, MusicGenre.AMBIENT],
        "primary_moods": [MusicMood.MYSTERIOUS, MusicMood.CONTEMPLATIVE, MusicMood.TENSE],
        "instruments": [Instrument.PIANO, Instrument.STRINGS, Instrument.SYNTH],
        "tempo_range": (60, 100),
        "typical_effects": [SoundEffectType.URBAN, SoundEffectType.INTERIOR],
        "keys": ["D minor", "G minor", "A minor"]
    }
}


# =============================================================================
# SOUNDTRACK GENERATOR ENGINE
# =============================================================================

class SoundtrackGenerator:
    """
    Silnik generowania ścieżek dźwiękowych.

    Funkcje:
    - Analiza emocjonalna tekstu
    - Generowanie parametrów muzycznych
    - Tworzenie pejzażu dźwiękowego per rozdział
    - Integracja z generatorami muzyki AI
    - Zarządzanie playlistami
    """

    def __init__(self):
        self.llm_service = get_llm_service()
        self.soundtracks: Dict[str, BookSoundtrack] = {}

    def _get_llm(self, tier: str = "mid"):
        """Get appropriate LLM based on tier"""
        return self.llm_service.get_client(tier)

    # =========================================================================
    # ANALYSIS
    # =========================================================================

    async def analyze_chapter_mood(
        self,
        chapter_text: str,
        chapter_number: int,
        genre: GenreType
    ) -> ChapterSoundscape:
        """
        Analizuje rozdział i tworzy pejzaż dźwiękowy.
        """
        profile = GENRE_MUSIC_PROFILES.get(genre, GENRE_MUSIC_PROFILES[GenreType.DRAMA])

        prompt = f"""Przeanalizuj poniższy rozdział pod kątem muzyki i dźwięków.

ROZDZIAŁ {chapter_number}:
{chapter_text[:3000]}

GATUNEK: {genre.value}
DOSTĘPNE NASTROJE: {[m.value for m in profile['primary_moods']]}
DOSTĘPNE GATUNKI MUZYCZNE: {[g.value for g in profile['primary_genres']]}

Określ:
1. DOMINUJĄCY NASTRÓJ (mood): peaceful/tense/dramatic/romantic/mysterious/action/sad/joyful/epic/horror/adventure/contemplative
2. GATUNEK MUZYCZNY (genre): orchestral/ambient/electronic/piano/acoustic/cinematic/folk/jazz/world/synth/choral
3. TEMPO (tempo_bpm): 60-180
4. TONACJA (key): np. "C major", "A minor"
5. INSTRUMENTY (instruments): strings/piano/synth/guitar/flute/drums/choir/harp/cello/violin/bells/pad
6. INTENSYWNOŚĆ (intensity): 0.0-1.0
7. EFEKTY AMBIENT (effects): nature/urban/weather/interior/horror/fantasy/scifi/combat
8. ARC EMOCJONALNY (emotional_arc): lista 5-10 wartości intensywności przez rozdział
9. KLUCZOWE MOMENTY (key_moments): momenty wymagające specjalnego traktowania

Odpowiedz w JSON:
{{
    "mood": "...",
    "genre": "...",
    "tempo_bpm": 90,
    "key": "...",
    "instruments": ["..."],
    "intensity": 0.5,
    "effects": [
        {{"type": "...", "description": "...", "volume": 0.3}}
    ],
    "emotional_arc": [0.3, 0.4, 0.5, 0.7, 0.9, 0.6, 0.4],
    "key_moments": [
        {{"position": "opening", "description": "...", "mood_shift": "..."}}
    ]
}}"""

        response = await self._get_llm("mid").chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        # Parse mood
        try:
            mood = MusicMood(data.get("mood", "peaceful"))
        except ValueError:
            mood = profile["primary_moods"][0]

        # Parse genre
        try:
            music_genre = MusicGenre(data.get("genre", "ambient"))
        except ValueError:
            music_genre = profile["primary_genres"][0]

        # Parse instruments
        instruments = []
        for inst_name in data.get("instruments", []):
            try:
                instruments.append(Instrument(inst_name))
            except ValueError:
                pass
        if not instruments:
            instruments = profile["instruments"][:3]

        # Clamp tempo
        tempo_min, tempo_max = profile["tempo_range"]
        tempo = max(tempo_min, min(tempo_max, data.get("tempo_bpm", 90)))

        # Create music parameters
        music_params = MusicParameters(
            mood=mood,
            genre=music_genre,
            tempo_bpm=tempo,
            key=data.get("key", profile["keys"][0]),
            primary_instruments=instruments,
            intensity=max(0.0, min(1.0, data.get("intensity", 0.5))),
            duration_seconds=300,  # 5 minutes default
            loop=True
        )

        # Parse effects
        ambient_effects = []
        for i, effect_data in enumerate(data.get("effects", [])):
            try:
                effect_type = SoundEffectType(effect_data.get("type", "nature"))
            except ValueError:
                continue

            effect = SoundEffect(
                effect_id=f"effect_{chapter_number}_{i+1}",
                effect_type=effect_type,
                description=effect_data.get("description", ""),
                duration_seconds=60,
                volume=max(0.0, min(1.0, effect_data.get("volume", 0.3))),
                loop=True
            )
            ambient_effects.append(effect)

        return ChapterSoundscape(
            chapter_number=chapter_number,
            chapter_title=f"Chapter {chapter_number}",
            music_parameters=music_params,
            ambient_effects=ambient_effects,
            emotional_arc=data.get("emotional_arc", [0.5] * 5),
            key_moments=data.get("key_moments", [])
        )

    # =========================================================================
    # SOUNDTRACK GENERATION
    # =========================================================================

    async def generate_book_soundtrack(
        self,
        book_title: str,
        genre: GenreType,
        chapters: List[str],
        chapter_titles: List[str] = None
    ) -> BookSoundtrack:
        """
        Generuje pełną ścieżkę dźwiękową dla książki.
        """
        chapter_soundscapes = []

        for i, chapter_text in enumerate(chapters):
            title = chapter_titles[i] if chapter_titles and i < len(chapter_titles) else f"Chapter {i+1}"

            soundscape = await self.analyze_chapter_mood(
                chapter_text,
                i + 1,
                genre
            )
            soundscape.chapter_title = title
            chapter_soundscapes.append(soundscape)

        # Calculate total duration (estimate)
        total_duration = len(chapters) * 300  # 5 min per chapter

        soundtrack = BookSoundtrack(
            soundtrack_id=f"soundtrack_{book_title.lower().replace(' ', '_')[:15]}_{datetime.now().strftime('%H%M%S')}",
            book_title=book_title,
            genre=genre,
            chapter_soundscapes=chapter_soundscapes,
            generated_tracks=[],  # Would be populated by music generator
            total_duration=total_duration,
            created_at=datetime.now()
        )

        self.soundtracks[soundtrack.soundtrack_id] = soundtrack
        return soundtrack

    def get_music_prompt(
        self,
        soundscape: ChapterSoundscape
    ) -> str:
        """
        Generuje prompt dla zewnętrznego generatora muzyki (np. Suno, MusicGen).
        """
        params = soundscape.music_parameters
        effects = ", ".join(e.description for e in soundscape.ambient_effects[:3])

        prompt = f"""{params.mood.value} {params.genre.value} background music,
{params.tempo_bpm} BPM, {params.key},
featuring {', '.join(i.value for i in params.primary_instruments)},
intensity {int(params.intensity * 10)}/10,
ambient sounds: {effects if effects else 'subtle atmosphere'},
perfect for reading, loopable, no lyrics"""

        return prompt

    # =========================================================================
    # PLAYLIST GENERATION
    # =========================================================================

    def generate_spotify_search_queries(
        self,
        soundtrack: BookSoundtrack
    ) -> List[Dict[str, str]]:
        """
        Generuje zapytania do wyszukiwania podobnej muzyki na Spotify.
        """
        queries = []

        for soundscape in soundtrack.chapter_soundscapes:
            params = soundscape.music_parameters

            query = f"{params.mood.value} {params.genre.value}"
            if params.genre == MusicGenre.ORCHESTRAL:
                query += " film score"
            elif params.genre == MusicGenre.AMBIENT:
                query += " atmospheric"
            elif params.genre == MusicGenre.PIANO:
                query += " solo piano"

            queries.append({
                "chapter": soundscape.chapter_number,
                "chapter_title": soundscape.chapter_title,
                "search_query": query,
                "mood": params.mood.value,
                "suggested_artists": self._get_suggested_artists(params)
            })

        return queries

    def _get_suggested_artists(self, params: MusicParameters) -> List[str]:
        """Sugeruje artystów na podstawie parametrów"""
        suggestions = {
            MusicMood.PEACEFUL: ["Ludovico Einaudi", "Ólafur Arnalds", "Nils Frahm"],
            MusicMood.TENSE: ["Hans Zimmer", "Clint Mansell", "Trent Reznor"],
            MusicMood.DRAMATIC: ["Two Steps from Hell", "Audiomachine", "Thomas Bergersen"],
            MusicMood.ROMANTIC: ["Yiruma", "Max Richter", "Dustin O'Halloran"],
            MusicMood.MYSTERIOUS: ["Brian Eno", "Sigur Rós", "Godspeed You! Black Emperor"],
            MusicMood.EPIC: ["Immediate Music", "E.S. Posthumus", "Jo Blankenburg"],
            MusicMood.HORROR: ["Akira Yamaoka", "John Carpenter", "Atrium Carceri"],
            MusicMood.SAD: ["Max Richter", "Johann Johannsson", "A Winged Victory"]
        }
        return suggestions.get(params.mood, ["Brian Eno", "Max Richter"])

    # =========================================================================
    # MANAGEMENT
    # =========================================================================

    def get_soundtrack(self, soundtrack_id: str) -> Optional[BookSoundtrack]:
        """Pobiera ścieżkę dźwiękową"""
        return self.soundtracks.get(soundtrack_id)

    def list_soundtracks(self) -> List[str]:
        """Lista ścieżek"""
        return list(self.soundtracks.keys())

    def export_soundtrack(self, soundtrack_id: str) -> Optional[Dict[str, Any]]:
        """Eksportuje ścieżkę dźwiękową"""
        soundtrack = self.soundtracks.get(soundtrack_id)
        if soundtrack:
            return {
                "soundtrack": soundtrack.to_dict(),
                "chapter_details": [cs.to_dict() for cs in soundtrack.chapter_soundscapes]
            }
        return None


# =============================================================================
# SINGLETON
# =============================================================================

_soundtrack_generator: Optional[SoundtrackGenerator] = None

def get_soundtrack_generator() -> SoundtrackGenerator:
    """Get singleton instance of soundtrack generator"""
    global _soundtrack_generator
    if _soundtrack_generator is None:
        _soundtrack_generator = SoundtrackGenerator()
    return _soundtrack_generator
