"""
Dynamic Genre Blending Service - NarraForge 3.0
Inteligentne mieszanie gatunków literackich z płynną fuzją stylów
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
from datetime import datetime
import json
import random

logger = logging.getLogger(__name__)


class GenreType(str, Enum):
    """Dostępne gatunki literackie"""
    FANTASY = "fantasy"
    SCIENCE_FICTION = "science_fiction"
    ROMANCE = "romance"
    THRILLER = "thriller"
    MYSTERY = "mystery"
    HORROR = "horror"
    LITERARY_FICTION = "literary_fiction"
    HISTORICAL = "historical"
    DYSTOPIAN = "dystopian"
    URBAN_FANTASY = "urban_fantasy"
    PARANORMAL = "paranormal"
    ADVENTURE = "adventure"
    CRIME = "crime"
    PSYCHOLOGICAL = "psychological"
    DARK_FANTASY = "dark_fantasy"
    EPIC_FANTASY = "epic_fantasy"
    SPACE_OPERA = "space_opera"
    CYBERPUNK = "cyberpunk"
    STEAMPUNK = "steampunk"
    POST_APOCALYPTIC = "post_apocalyptic"
    MAGICAL_REALISM = "magical_realism"
    RELIGIOUS = "religious"
    INSPIRATIONAL = "inspirational"
    YOUNG_ADULT = "young_adult"
    NEW_ADULT = "new_adult"


@dataclass
class GenreProfile:
    """Profil gatunku z jego charakterystykami"""
    genre_type: GenreType
    core_elements: List[str]
    typical_themes: List[str]
    narrative_style: str
    pacing_pattern: str
    emotional_tone: List[str]
    world_building_level: float  # 0-1
    character_focus: float  # 0-1
    action_level: float  # 0-1
    romance_level: float  # 0-1
    mystery_level: float  # 0-1
    philosophical_depth: float  # 0-1
    tension_curve: str  # "gradual", "explosive", "wave", "steady"
    typical_tropes: List[str]
    compatible_genres: List[GenreType]
    conflict_genres: List[GenreType]


@dataclass
class BlendingRatio:
    """Proporcje mieszania gatunków"""
    primary_genre: GenreType
    primary_weight: float
    secondary_genres: Dict[GenreType, float]
    blend_style: str  # "seamless", "layered", "alternating", "fusion"
    transition_smoothness: float  # 0-1


@dataclass
class BlendedGenreProfile:
    """Wynikowy profil zmieszanych gatunków"""
    blend_id: str
    name: str
    description: str
    source_genres: List[GenreType]
    ratios: BlendingRatio
    merged_elements: List[str]
    merged_themes: List[str]
    narrative_style: str
    emotional_spectrum: List[str]
    unique_characteristics: List[str]
    recommended_structure: Dict[str, Any]
    conflict_resolution_notes: List[str]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GenreTransition:
    """Przejście między gatunkami w narracji"""
    from_genre: GenreType
    to_genre: GenreType
    transition_type: str  # "gradual", "sharp", "thematic", "character-driven"
    chapter_range: Tuple[int, int]
    trigger_elements: List[str]
    smoothness_score: float


class DynamicGenreBlendingService:
    """
    Serwis do dynamicznego mieszania gatunków literackich.
    Tworzy unikalne hybrydy gatunkowe z płynnymi przejściami.
    """

    def __init__(self):
        self.genre_profiles: Dict[GenreType, GenreProfile] = {}
        self.blend_history: List[BlendedGenreProfile] = []
        self.active_blends: Dict[str, BlendedGenreProfile] = {}
        self._initialize_genre_profiles()
        logger.info("DynamicGenreBlendingService zainicjalizowany")

    def _initialize_genre_profiles(self):
        """Inicjalizuje profile wszystkich gatunków"""

        self.genre_profiles[GenreType.FANTASY] = GenreProfile(
            genre_type=GenreType.FANTASY,
            core_elements=["magia", "mityczne stworzenia", "questy", "wybraniec", "starożytne przepowiednie"],
            typical_themes=["dobro vs zło", "poświęcenie", "przeznaczenie", "moc wewnętrzna"],
            narrative_style="epicka, opisowa",
            pacing_pattern="budowanie do klimaksu",
            emotional_tone=["wonder", "adventure", "hope", "determination"],
            world_building_level=0.95,
            character_focus=0.75,
            action_level=0.7,
            romance_level=0.4,
            mystery_level=0.5,
            philosophical_depth=0.6,
            tension_curve="gradual",
            typical_tropes=["chosen_one", "mentor_death", "dark_lord", "magic_system"],
            compatible_genres=[GenreType.ROMANCE, GenreType.ADVENTURE, GenreType.MYSTERY],
            conflict_genres=[GenreType.SCIENCE_FICTION, GenreType.CRIME]
        )

        self.genre_profiles[GenreType.SCIENCE_FICTION] = GenreProfile(
            genre_type=GenreType.SCIENCE_FICTION,
            core_elements=["technologia", "kosmos", "AI", "przyszłość", "eksperymenty"],
            typical_themes=["ludzkość", "postęp", "etyka technologii", "samotność"],
            narrative_style="spekulatywna, techniczna",
            pacing_pattern="odkrywanie tajemnic",
            emotional_tone=["curiosity", "wonder", "dread", "hope"],
            world_building_level=0.9,
            character_focus=0.65,
            action_level=0.6,
            romance_level=0.3,
            mystery_level=0.7,
            philosophical_depth=0.85,
            tension_curve="wave",
            typical_tropes=["ai_rebellion", "first_contact", "time_travel", "dystopia"],
            compatible_genres=[GenreType.THRILLER, GenreType.MYSTERY, GenreType.DYSTOPIAN],
            conflict_genres=[GenreType.FANTASY, GenreType.HISTORICAL]
        )

        self.genre_profiles[GenreType.ROMANCE] = GenreProfile(
            genre_type=GenreType.ROMANCE,
            core_elements=["miłość", "relacje", "emocje", "przeszkody", "happy ending"],
            typical_themes=["miłość prawdziwa", "przebaczenie", "drugie szanse", "samoakceptacja"],
            narrative_style="emocjonalna, intymna",
            pacing_pattern="wzloty i upadki",
            emotional_tone=["passion", "longing", "joy", "heartbreak"],
            world_building_level=0.3,
            character_focus=0.95,
            action_level=0.2,
            romance_level=1.0,
            mystery_level=0.2,
            philosophical_depth=0.5,
            tension_curve="wave",
            typical_tropes=["enemies_to_lovers", "fake_dating", "second_chance", "forbidden_love"],
            compatible_genres=[GenreType.FANTASY, GenreType.HISTORICAL, GenreType.THRILLER],
            conflict_genres=[GenreType.HORROR, GenreType.CRIME]
        )

        self.genre_profiles[GenreType.THRILLER] = GenreProfile(
            genre_type=GenreType.THRILLER,
            core_elements=["napięcie", "zagrożenie", "wyścig z czasem", "twist", "stawka"],
            typical_themes=["przetrwanie", "sprawiedliwość", "zaufanie", "zdrada"],
            narrative_style="szybka, napięta",
            pacing_pattern="ciągła eskalacja",
            emotional_tone=["tension", "fear", "urgency", "relief"],
            world_building_level=0.5,
            character_focus=0.7,
            action_level=0.85,
            romance_level=0.3,
            mystery_level=0.8,
            philosophical_depth=0.4,
            tension_curve="explosive",
            typical_tropes=["ticking_clock", "unreliable_narrator", "double_cross", "final_confrontation"],
            compatible_genres=[GenreType.MYSTERY, GenreType.CRIME, GenreType.PSYCHOLOGICAL],
            conflict_genres=[GenreType.ROMANCE, GenreType.INSPIRATIONAL]
        )

        self.genre_profiles[GenreType.MYSTERY] = GenreProfile(
            genre_type=GenreType.MYSTERY,
            core_elements=["zagadka", "wskazówki", "detektyw", "rozwiązanie", "red herring"],
            typical_themes=["prawda", "sprawiedliwość", "obsesja", "tajemnice przeszłości"],
            narrative_style="analityczna, suspensowa",
            pacing_pattern="budowanie z rewelacjami",
            emotional_tone=["curiosity", "suspicion", "satisfaction", "shock"],
            world_building_level=0.4,
            character_focus=0.75,
            action_level=0.4,
            romance_level=0.25,
            mystery_level=1.0,
            philosophical_depth=0.55,
            tension_curve="gradual",
            typical_tropes=["locked_room", "unreliable_witness", "hidden_identity", "final_reveal"],
            compatible_genres=[GenreType.THRILLER, GenreType.CRIME, GenreType.PSYCHOLOGICAL],
            conflict_genres=[GenreType.FANTASY, GenreType.ROMANCE]
        )

        self.genre_profiles[GenreType.HORROR] = GenreProfile(
            genre_type=GenreType.HORROR,
            core_elements=["strach", "nadprzyrodzone", "izolacja", "śmierć", "nieznane"],
            typical_themes=["lęk", "przetrwanie", "szaleństwo", "zło"],
            narrative_style="atmosferyczna, niepokojąca",
            pacing_pattern="budowanie grozy",
            emotional_tone=["dread", "terror", "unease", "despair"],
            world_building_level=0.6,
            character_focus=0.65,
            action_level=0.5,
            romance_level=0.15,
            mystery_level=0.7,
            philosophical_depth=0.6,
            tension_curve="steady",
            typical_tropes=["haunted_place", "final_girl", "cosmic_horror", "body_horror"],
            compatible_genres=[GenreType.THRILLER, GenreType.PSYCHOLOGICAL, GenreType.DARK_FANTASY],
            conflict_genres=[GenreType.ROMANCE, GenreType.INSPIRATIONAL]
        )

        self.genre_profiles[GenreType.HISTORICAL] = GenreProfile(
            genre_type=GenreType.HISTORICAL,
            core_elements=["epoka", "autentyczność", "kontekst historyczny", "postacie historyczne"],
            typical_themes=["przemijanie", "tradycja", "zmiana społeczna", "honor"],
            narrative_style="szczegółowa, nostalgiczna",
            pacing_pattern="rozważne tempo",
            emotional_tone=["nostalgia", "gravitas", "passion", "melancholy"],
            world_building_level=0.85,
            character_focus=0.8,
            action_level=0.5,
            romance_level=0.6,
            mystery_level=0.4,
            philosophical_depth=0.7,
            tension_curve="gradual",
            typical_tropes=["class_differences", "war_backdrop", "forbidden_love", "family_saga"],
            compatible_genres=[GenreType.ROMANCE, GenreType.MYSTERY, GenreType.ADVENTURE],
            conflict_genres=[GenreType.SCIENCE_FICTION, GenreType.CYBERPUNK]
        )

        self.genre_profiles[GenreType.PSYCHOLOGICAL] = GenreProfile(
            genre_type=GenreType.PSYCHOLOGICAL,
            core_elements=["psychika", "motywacje", "trauma", "percepcja", "obsesja"],
            typical_themes=["tożsamość", "szaleństwo", "rzeczywistość", "wina"],
            narrative_style="introspektywna, niepewna",
            pacing_pattern="powolne odkrywanie",
            emotional_tone=["unease", "confusion", "dread", "revelation"],
            world_building_level=0.35,
            character_focus=0.95,
            action_level=0.25,
            romance_level=0.3,
            mystery_level=0.85,
            philosophical_depth=0.9,
            tension_curve="steady",
            typical_tropes=["unreliable_narrator", "gaslighting", "split_personality", "repressed_memory"],
            compatible_genres=[GenreType.THRILLER, GenreType.HORROR, GenreType.MYSTERY],
            conflict_genres=[GenreType.ADVENTURE, GenreType.INSPIRATIONAL]
        )

        self.genre_profiles[GenreType.RELIGIOUS] = GenreProfile(
            genre_type=GenreType.RELIGIOUS,
            core_elements=["wiara", "duchowość", "cuda", "modlitwa", "nawrócenie"],
            typical_themes=["zbawienie", "przebaczenie", "łaska", "miłość Boża", "przeznaczenie"],
            narrative_style="refleksyjna, inspirująca",
            pacing_pattern="transformacyjne",
            emotional_tone=["hope", "peace", "awe", "redemption"],
            world_building_level=0.5,
            character_focus=0.85,
            action_level=0.3,
            romance_level=0.4,
            mystery_level=0.5,
            philosophical_depth=0.95,
            tension_curve="gradual",
            typical_tropes=["conversion_arc", "divine_intervention", "martyrdom", "spiritual_journey"],
            compatible_genres=[GenreType.HISTORICAL, GenreType.INSPIRATIONAL, GenreType.LITERARY_FICTION],
            conflict_genres=[GenreType.HORROR, GenreType.CRIME]
        )

        self.genre_profiles[GenreType.INSPIRATIONAL] = GenreProfile(
            genre_type=GenreType.INSPIRATIONAL,
            core_elements=["nadzieja", "transformacja", "pokonywanie przeszkód", "rozwój osobisty"],
            typical_themes=["siła wewnętrzna", "wytrwałość", "miłość", "wdzięczność"],
            narrative_style="pozytywna, motywująca",
            pacing_pattern="wznosząca",
            emotional_tone=["hope", "joy", "determination", "gratitude"],
            world_building_level=0.35,
            character_focus=0.9,
            action_level=0.35,
            romance_level=0.5,
            mystery_level=0.2,
            philosophical_depth=0.75,
            tension_curve="gradual",
            typical_tropes=["underdog_triumph", "healing_journey", "community_support", "life_lessons"],
            compatible_genres=[GenreType.ROMANCE, GenreType.RELIGIOUS, GenreType.HISTORICAL],
            conflict_genres=[GenreType.HORROR, GenreType.CRIME, GenreType.THRILLER]
        )

        self.genre_profiles[GenreType.DARK_FANTASY] = GenreProfile(
            genre_type=GenreType.DARK_FANTASY,
            core_elements=["mroczna magia", "moralna szarość", "brutalna rzeczywistość", "antyherosi"],
            typical_themes=["korupcja władzy", "koszt magii", "przetrwanie", "moralność"],
            narrative_style="ponura, brutalna",
            pacing_pattern="nieprzewidywalne",
            emotional_tone=["dread", "despair", "determination", "grim_hope"],
            world_building_level=0.9,
            character_focus=0.8,
            action_level=0.75,
            romance_level=0.35,
            mystery_level=0.6,
            philosophical_depth=0.8,
            tension_curve="wave",
            typical_tropes=["morally_grey_hero", "blood_magic", "fallen_kingdom", "tragic_past"],
            compatible_genres=[GenreType.HORROR, GenreType.THRILLER, GenreType.EPIC_FANTASY],
            conflict_genres=[GenreType.INSPIRATIONAL, GenreType.ROMANCE]
        )

        self.genre_profiles[GenreType.CYBERPUNK] = GenreProfile(
            genre_type=GenreType.CYBERPUNK,
            core_elements=["high tech low life", "megakorporacje", "cybernetic", "hacking", "neon noir"],
            typical_themes=["tożsamość", "korporacyjna tyrania", "transhumanizm", "bunt"],
            narrative_style="stylowa, cynyczna",
            pacing_pattern="szybkie i napięte",
            emotional_tone=["alienation", "cynicism", "rebellion", "desperation"],
            world_building_level=0.9,
            character_focus=0.7,
            action_level=0.8,
            romance_level=0.35,
            mystery_level=0.65,
            philosophical_depth=0.8,
            tension_curve="explosive",
            typical_tropes=["corporate_espionage", "street_samurai", "ai_consciousness", "virtual_reality"],
            compatible_genres=[GenreType.THRILLER, GenreType.CRIME, GenreType.DYSTOPIAN],
            conflict_genres=[GenreType.FANTASY, GenreType.HISTORICAL, GenreType.INSPIRATIONAL]
        )

        # Dodaj pozostałe gatunki z podstawowymi profilami
        remaining_genres = [
            GenreType.LITERARY_FICTION, GenreType.DYSTOPIAN, GenreType.URBAN_FANTASY,
            GenreType.PARANORMAL, GenreType.ADVENTURE, GenreType.CRIME,
            GenreType.EPIC_FANTASY, GenreType.SPACE_OPERA, GenreType.STEAMPUNK,
            GenreType.POST_APOCALYPTIC, GenreType.MAGICAL_REALISM,
            GenreType.YOUNG_ADULT, GenreType.NEW_ADULT
        ]

        for genre in remaining_genres:
            if genre not in self.genre_profiles:
                self.genre_profiles[genre] = self._create_default_profile(genre)

    def _create_default_profile(self, genre_type: GenreType) -> GenreProfile:
        """Tworzy domyślny profil dla gatunku"""
        return GenreProfile(
            genre_type=genre_type,
            core_elements=[f"{genre_type.value}_element_1", f"{genre_type.value}_element_2"],
            typical_themes=[f"{genre_type.value}_theme_1", f"{genre_type.value}_theme_2"],
            narrative_style="zróżnicowany",
            pacing_pattern="standardowy",
            emotional_tone=["varied"],
            world_building_level=0.5,
            character_focus=0.5,
            action_level=0.5,
            romance_level=0.5,
            mystery_level=0.5,
            philosophical_depth=0.5,
            tension_curve="gradual",
            typical_tropes=[f"{genre_type.value}_trope"],
            compatible_genres=[],
            conflict_genres=[]
        )

    async def create_genre_blend(
        self,
        primary_genre: GenreType,
        secondary_genres: List[GenreType],
        weights: Optional[Dict[GenreType, float]] = None,
        blend_style: str = "seamless"
    ) -> BlendedGenreProfile:
        """
        Tworzy nowy blend gatunków.

        Args:
            primary_genre: Główny gatunek
            secondary_genres: Lista gatunków drugorzędnych
            weights: Wagi dla każdego gatunku (opcjonalne)
            blend_style: Styl mieszania ("seamless", "layered", "alternating", "fusion")

        Returns:
            BlendedGenreProfile z kompletnym profilem zmieszanych gatunków
        """
        logger.info(f"Tworzę blend: {primary_genre.value} + {[g.value for g in secondary_genres]}")

        # Pobierz profile
        primary_profile = self.genre_profiles.get(primary_genre)
        secondary_profiles = [self.genre_profiles.get(g) for g in secondary_genres]

        if not primary_profile:
            raise ValueError(f"Nieznany gatunek: {primary_genre}")

        # Oblicz wagi
        if weights is None:
            total_secondary = len(secondary_genres)
            primary_weight = 0.6
            secondary_weight = 0.4 / total_secondary if total_secondary > 0 else 0
            weights = {g: secondary_weight for g in secondary_genres}
        else:
            primary_weight = 1.0 - sum(weights.values())

        # Sprawdź kompatybilność
        compatibility_score, conflict_notes = self._analyze_compatibility(
            primary_profile, secondary_profiles
        )

        # Połącz elementy
        merged_elements = self._merge_elements(primary_profile, secondary_profiles, weights)
        merged_themes = self._merge_themes(primary_profile, secondary_profiles, weights)

        # Wygeneruj unikalny styl narracyjny
        narrative_style = self._blend_narrative_styles(
            primary_profile, secondary_profiles, weights
        )

        # Połącz spektrum emocjonalne
        emotional_spectrum = self._blend_emotional_tones(
            primary_profile, secondary_profiles, weights
        )

        # Wygeneruj unikalne charakterystyki
        unique_chars = self._generate_unique_characteristics(
            primary_profile, secondary_profiles, blend_style
        )

        # Stwórz rekomendowaną strukturę
        structure = self._create_recommended_structure(
            primary_profile, secondary_profiles, weights, blend_style
        )

        # Utwórz blend ID
        blend_id = f"blend_{primary_genre.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Nazwa blendu
        genre_names = [primary_genre.value] + [g.value for g in secondary_genres]
        blend_name = " x ".join([n.replace("_", " ").title() for n in genre_names])

        # Opis blendu
        description = self._generate_blend_description(
            primary_profile, secondary_profiles, blend_style
        )

        blend = BlendedGenreProfile(
            blend_id=blend_id,
            name=blend_name,
            description=description,
            source_genres=[primary_genre] + secondary_genres,
            ratios=BlendingRatio(
                primary_genre=primary_genre,
                primary_weight=primary_weight,
                secondary_genres=weights,
                blend_style=blend_style,
                transition_smoothness=compatibility_score
            ),
            merged_elements=merged_elements,
            merged_themes=merged_themes,
            narrative_style=narrative_style,
            emotional_spectrum=emotional_spectrum,
            unique_characteristics=unique_chars,
            recommended_structure=structure,
            conflict_resolution_notes=conflict_notes
        )

        # Zapisz blend
        self.active_blends[blend_id] = blend
        self.blend_history.append(blend)

        logger.info(f"Utworzono blend: {blend_name} (kompatybilność: {compatibility_score:.2f})")
        return blend

    def _analyze_compatibility(
        self,
        primary: GenreProfile,
        secondaries: List[GenreProfile]
    ) -> Tuple[float, List[str]]:
        """Analizuje kompatybilność gatunków"""
        score = 1.0
        notes = []

        for secondary in secondaries:
            if secondary is None:
                continue

            # Sprawdź konflikty
            if secondary.genre_type in primary.conflict_genres:
                score -= 0.15
                notes.append(
                    f"Konflikt: {primary.genre_type.value} i {secondary.genre_type.value} "
                    f"- wymagane ostrożne przejścia"
                )

            # Sprawdź kompatybilność
            if secondary.genre_type in primary.compatible_genres:
                score += 0.05
                notes.append(
                    f"Synergia: {primary.genre_type.value} i {secondary.genre_type.value} "
                    f"- naturalne połączenie"
                )

            # Analizuj różnice w poziomach
            world_diff = abs(primary.world_building_level - secondary.world_building_level)
            if world_diff > 0.5:
                notes.append(
                    f"Różnica w world-buildingu między {primary.genre_type.value} "
                    f"i {secondary.genre_type.value} - wyrównaj poziom detali"
                )

            action_diff = abs(primary.action_level - secondary.action_level)
            if action_diff > 0.5:
                notes.append(
                    f"Różnica w poziomie akcji - rozważ płynne przejścia tempa"
                )

        return max(0.0, min(1.0, score)), notes

    def _merge_elements(
        self,
        primary: GenreProfile,
        secondaries: List[GenreProfile],
        weights: Dict[GenreType, float]
    ) -> List[str]:
        """Łączy elementy gatunków"""
        elements = list(primary.core_elements)  # Wszystkie z primary

        for secondary in secondaries:
            if secondary is None:
                continue
            weight = weights.get(secondary.genre_type, 0.2)
            # Dodaj proporcjonalnie elementy
            num_elements = max(1, int(len(secondary.core_elements) * weight * 2))
            elements.extend(secondary.core_elements[:num_elements])

        return list(set(elements))

    def _merge_themes(
        self,
        primary: GenreProfile,
        secondaries: List[GenreProfile],
        weights: Dict[GenreType, float]
    ) -> List[str]:
        """Łączy tematy gatunków"""
        themes = list(primary.typical_themes)

        for secondary in secondaries:
            if secondary is None:
                continue
            weight = weights.get(secondary.genre_type, 0.2)
            num_themes = max(1, int(len(secondary.typical_themes) * weight * 2))
            themes.extend(secondary.typical_themes[:num_themes])

        return list(set(themes))

    def _blend_narrative_styles(
        self,
        primary: GenreProfile,
        secondaries: List[GenreProfile],
        weights: Dict[GenreType, float]
    ) -> str:
        """Tworzy zmieszany styl narracyjny"""
        styles = [primary.narrative_style]

        for secondary in secondaries:
            if secondary is None:
                continue
            weight = weights.get(secondary.genre_type, 0.2)
            if weight > 0.15:
                styles.append(secondary.narrative_style)

        return " z elementami ".join(styles)

    def _blend_emotional_tones(
        self,
        primary: GenreProfile,
        secondaries: List[GenreProfile],
        weights: Dict[GenreType, float]
    ) -> List[str]:
        """Łączy tony emocjonalne"""
        tones = set(primary.emotional_tone)

        for secondary in secondaries:
            if secondary is None:
                continue
            tones.update(secondary.emotional_tone)

        return list(tones)

    def _generate_unique_characteristics(
        self,
        primary: GenreProfile,
        secondaries: List[GenreProfile],
        blend_style: str
    ) -> List[str]:
        """Generuje unikalne charakterystyki blendu"""
        characteristics = []

        # Na podstawie stylu blendowania
        if blend_style == "seamless":
            characteristics.append("Płynne przejścia między elementami gatunków")
            characteristics.append("Zintegrowany świat łączący wszystkie tradycje")

        elif blend_style == "layered":
            characteristics.append("Wielowarstwowa narracja z wyraźnymi poziomami gatunkowymi")
            characteristics.append("Każdy gatunek dominuje w określonych scenach")

        elif blend_style == "alternating":
            characteristics.append("Naprzemienne rozdziały z różnymi dominującymi gatunkami")
            characteristics.append("Kontrastowe przejścia budujące napięcie")

        elif blend_style == "fusion":
            characteristics.append("Głęboka fuzja tworząca zupełnie nowy gatunek")
            characteristics.append("Elementy wszystkich gatunków w każdej scenie")

        # Na podstawie kombinacji gatunków
        genre_types = [primary.genre_type] + [s.genre_type for s in secondaries if s]

        if GenreType.FANTASY in genre_types and GenreType.SCIENCE_FICTION in genre_types:
            characteristics.append("Science-Fantasy: magia spotyka technologię")

        if GenreType.ROMANCE in genre_types and GenreType.THRILLER in genre_types:
            characteristics.append("Romantic Suspense: miłość w cieniu zagrożenia")

        if GenreType.HORROR in genre_types and GenreType.ROMANCE in genre_types:
            characteristics.append("Dark Romance: mroczna miłość z elementami grozy")

        if GenreType.HISTORICAL in genre_types and GenreType.FANTASY in genre_types:
            characteristics.append("Historical Fantasy: magia w autentycznym kontekście historycznym")

        if GenreType.RELIGIOUS in genre_types and GenreType.THRILLER in genre_types:
            characteristics.append("Faith Thriller: duchowa podróż pełna napięcia")

        return characteristics

    def _create_recommended_structure(
        self,
        primary: GenreProfile,
        secondaries: List[GenreProfile],
        weights: Dict[GenreType, float],
        blend_style: str
    ) -> Dict[str, Any]:
        """Tworzy rekomendowaną strukturę narracyjną"""

        # Oblicz średnie wartości
        all_profiles = [primary] + [s for s in secondaries if s]
        all_weights = [1.0 - sum(weights.values())] + [weights.get(s.genre_type, 0.2) for s in secondaries if s]

        avg_action = sum(p.action_level * w for p, w in zip(all_profiles, all_weights))
        avg_world = sum(p.world_building_level * w for p, w in zip(all_profiles, all_weights))
        avg_mystery = sum(p.mystery_level * w for p, w in zip(all_profiles, all_weights))

        structure = {
            "recommended_chapter_count": 25 if avg_world > 0.7 else 20,
            "prologue_recommended": avg_world > 0.6,
            "epilogue_recommended": any(p.genre_type in [GenreType.ROMANCE, GenreType.INSPIRATIONAL] for p in all_profiles),
            "subplot_count": 3 if len(all_profiles) > 2 else 2,
            "act_structure": {
                "act1_percentage": 25,
                "act2_percentage": 50,
                "act3_percentage": 25
            },
            "pacing_recommendations": [],
            "genre_distribution": {}
        }

        # Rekomendacje tempa
        if avg_action > 0.7:
            structure["pacing_recommendations"].append("Krótsze rozdziały dla dynamiki")
        if avg_mystery > 0.6:
            structure["pacing_recommendations"].append("Stopniowe odkrywanie tajemnic")
        if avg_world > 0.7:
            structure["pacing_recommendations"].append("Początkowe rozdziały na world-building")

        # Dystrybucja gatunków
        if blend_style == "layered":
            structure["genre_distribution"] = {
                "beginning": primary.genre_type.value,
                "middle": [s.genre_type.value for s in secondaries[:2] if s],
                "climax": "fusion",
                "ending": primary.genre_type.value
            }
        elif blend_style == "alternating":
            structure["genre_distribution"] = {
                "pattern": "alternating_chapters",
                "primary_chapters": "odd",
                "secondary_chapters": "even"
            }
        else:
            structure["genre_distribution"] = {
                "style": "integrated",
                "all_chapters": "fusion"
            }

        return structure

    def _generate_blend_description(
        self,
        primary: GenreProfile,
        secondaries: List[GenreProfile],
        blend_style: str
    ) -> str:
        """Generuje opis blendu"""
        secondary_names = [s.genre_type.value.replace("_", " ") for s in secondaries if s]
        primary_name = primary.genre_type.value.replace("_", " ")

        if blend_style == "seamless":
            return (
                f"Płynne połączenie {primary_name} z elementami "
                f"{', '.join(secondary_names)}, gdzie wszystkie gatunki "
                f"współistnieją harmonijnie."
            )
        elif blend_style == "layered":
            return (
                f"Wielowarstwowa narracja z fundamentem {primary_name} "
                f"wzbogacona o warstwy {', '.join(secondary_names)}."
            )
        elif blend_style == "alternating":
            return (
                f"Naprzemienne przełączanie między {primary_name} "
                f"a {', '.join(secondary_names)} tworzące dynamiczny kontrast."
            )
        else:  # fusion
            return (
                f"Głęboka fuzja {primary_name} i {', '.join(secondary_names)} "
                f"tworząca zupełnie nową jakość gatunkową."
            )

    async def get_genre_transitions(
        self,
        blend: BlendedGenreProfile,
        chapter_count: int
    ) -> List[GenreTransition]:
        """
        Generuje plan przejść między gatunkami dla rozdziałów.

        Args:
            blend: Profil zmieszanych gatunków
            chapter_count: Liczba rozdziałów

        Returns:
            Lista przejść między gatunkami
        """
        transitions = []
        blend_style = blend.ratios.blend_style

        if blend_style == "alternating":
            # Przejścia co rozdział
            for i in range(1, chapter_count):
                from_genre = blend.source_genres[i % 2]
                to_genre = blend.source_genres[(i + 1) % 2]

                transitions.append(GenreTransition(
                    from_genre=from_genre,
                    to_genre=to_genre,
                    transition_type="sharp",
                    chapter_range=(i, i + 1),
                    trigger_elements=["chapter_break", "scene_change"],
                    smoothness_score=0.6
                ))

        elif blend_style == "layered":
            # Przejścia w kluczowych punktach
            key_points = [
                int(chapter_count * 0.25),
                int(chapter_count * 0.5),
                int(chapter_count * 0.75)
            ]

            for idx, point in enumerate(key_points):
                from_idx = idx % len(blend.source_genres)
                to_idx = (idx + 1) % len(blend.source_genres)

                transitions.append(GenreTransition(
                    from_genre=blend.source_genres[from_idx],
                    to_genre=blend.source_genres[to_idx],
                    transition_type="gradual",
                    chapter_range=(max(1, point - 1), point + 1),
                    trigger_elements=["plot_development", "character_revelation"],
                    smoothness_score=0.8
                ))

        else:  # seamless/fusion - minimalne przejścia
            transitions.append(GenreTransition(
                from_genre=blend.source_genres[0],
                to_genre=blend.source_genres[0],
                transition_type="thematic",
                chapter_range=(1, chapter_count),
                trigger_elements=["continuous_integration"],
                smoothness_score=0.95
            ))

        return transitions

    async def suggest_scene_genre_balance(
        self,
        blend: BlendedGenreProfile,
        scene_type: str,
        emotional_target: str
    ) -> Dict[str, Any]:
        """
        Sugeruje balans gatunków dla konkretnej sceny.

        Args:
            blend: Profil zmieszanych gatunków
            scene_type: Typ sceny (action, dialogue, romance, revelation, etc.)
            emotional_target: Docelowa emocja

        Returns:
            Rekomendacje dotyczące balansu gatunków
        """
        recommendations = {
            "scene_type": scene_type,
            "emotional_target": emotional_target,
            "genre_emphasis": {},
            "elements_to_use": [],
            "elements_to_avoid": [],
            "tone_guidance": "",
            "pacing_notes": ""
        }

        # Analizuj typ sceny
        if scene_type == "action":
            for genre in blend.source_genres:
                profile = self.genre_profiles.get(genre)
                if profile and profile.action_level > 0.6:
                    recommendations["genre_emphasis"][genre.value] = 0.7
                else:
                    recommendations["genre_emphasis"][genre.value] = 0.3

            recommendations["pacing_notes"] = "Szybkie tempo, krótkie zdania"
            recommendations["elements_to_use"] = ["dynamika", "napięcie", "fizyczność"]

        elif scene_type == "romance":
            for genre in blend.source_genres:
                profile = self.genre_profiles.get(genre)
                if profile and profile.romance_level > 0.5:
                    recommendations["genre_emphasis"][genre.value] = 0.8
                else:
                    recommendations["genre_emphasis"][genre.value] = 0.2

            recommendations["pacing_notes"] = "Powolne tempo, skupienie na emocjach"
            recommendations["elements_to_use"] = ["intymność", "emocje", "dialog"]

        elif scene_type == "revelation":
            for genre in blend.source_genres:
                profile = self.genre_profiles.get(genre)
                if profile and profile.mystery_level > 0.5:
                    recommendations["genre_emphasis"][genre.value] = 0.7
                else:
                    recommendations["genre_emphasis"][genre.value] = 0.3

            recommendations["pacing_notes"] = "Budowanie napięcia przed ujawnieniem"
            recommendations["elements_to_use"] = ["tajemnica", "odkrycie", "twist"]

        elif scene_type == "philosophical":
            for genre in blend.source_genres:
                profile = self.genre_profiles.get(genre)
                if profile and profile.philosophical_depth > 0.6:
                    recommendations["genre_emphasis"][genre.value] = 0.8
                else:
                    recommendations["genre_emphasis"][genre.value] = 0.2

            recommendations["pacing_notes"] = "Refleksyjne tempo, głębia myśli"
            recommendations["elements_to_use"] = ["refleksja", "pytania egzystencjalne", "monolog wewnętrzny"]

        # Dopasuj ton do emocji
        recommendations["tone_guidance"] = self._get_tone_for_emotion(
            emotional_target, blend.emotional_spectrum
        )

        return recommendations

    def _get_tone_for_emotion(self, target: str, available: List[str]) -> str:
        """Dobiera ton do emocji"""
        emotion_tones = {
            "hope": "Optymistyczny z nutą realizmu",
            "fear": "Niepokojący, pełen napięcia",
            "joy": "Lekki, radosny, energetyczny",
            "sadness": "Melancholijny, refleksyjny",
            "anger": "Intensywny, dynamiczny",
            "love": "Ciepły, intymny",
            "wonder": "Magiczny, pełen zachwytu",
            "dread": "Ciężki, przytłaczający",
            "peace": "Spokojny, harmonijny",
            "tension": "Napięty, niepewny"
        }

        return emotion_tones.get(target, "Zbalansowany, dostosowany do kontekstu")

    async def analyze_genre_coherence(
        self,
        blend: BlendedGenreProfile,
        chapter_content: str
    ) -> Dict[str, Any]:
        """
        Analizuje spójność gatunkową rozdziału.

        Args:
            blend: Profil zmieszanych gatunków
            chapter_content: Treść rozdziału

        Returns:
            Analiza spójności z rekomendacjami
        """
        analysis = {
            "coherence_score": 0.0,
            "detected_genres": {},
            "balance_assessment": "",
            "issues": [],
            "recommendations": []
        }

        # Słowa kluczowe dla każdego gatunku
        genre_keywords = {
            GenreType.FANTASY: ["magia", "czar", "smok", "elf", "miecz", "przepowiednia", "magiczny"],
            GenreType.SCIENCE_FICTION: ["statek", "kosmos", "robot", "technologia", "planeta", "AI"],
            GenreType.ROMANCE: ["miłość", "serce", "pocałunek", "uczucie", "ramiona", "kochać"],
            GenreType.THRILLER: ["niebezpieczeństwo", "strach", "uciekać", "tropić", "zegar", "śmierć"],
            GenreType.HORROR: ["ciemność", "krew", "krzyk", "potwór", "strach", "cień", "groza"],
            GenreType.RELIGIOUS: ["Bóg", "wiara", "modlitwa", "dusza", "łaska", "zbawienie", "błogosławieństwo"],
            GenreType.MYSTERY: ["zagadka", "wskazówka", "podejrzany", "sekret", "dochodzenie", "tajemnica"]
        }

        content_lower = chapter_content.lower()
        total_matches = 0

        for genre in blend.source_genres:
            keywords = genre_keywords.get(genre, [])
            matches = sum(1 for kw in keywords if kw in content_lower)
            analysis["detected_genres"][genre.value] = matches
            total_matches += matches

        # Oblicz proporcje
        if total_matches > 0:
            for genre in blend.source_genres:
                detected = analysis["detected_genres"].get(genre.value, 0)
                expected = blend.ratios.secondary_genres.get(genre, blend.ratios.primary_weight)
                actual = detected / total_matches

                if abs(actual - expected) > 0.2:
                    if actual < expected:
                        analysis["issues"].append(
                            f"Za mało elementów {genre.value} (oczekiwano {expected:.0%}, wykryto {actual:.0%})"
                        )
                        analysis["recommendations"].append(
                            f"Dodaj więcej elementów charakterystycznych dla {genre.value}"
                        )
                    else:
                        analysis["issues"].append(
                            f"Za dużo elementów {genre.value} (oczekiwano {expected:.0%}, wykryto {actual:.0%})"
                        )

        # Oblicz score
        if not analysis["issues"]:
            analysis["coherence_score"] = 0.95
            analysis["balance_assessment"] = "Doskonały balans gatunkowy"
        elif len(analysis["issues"]) <= 2:
            analysis["coherence_score"] = 0.75
            analysis["balance_assessment"] = "Dobry balans z drobnymi odchyleniami"
        else:
            analysis["coherence_score"] = 0.5
            analysis["balance_assessment"] = "Wymaga poprawy balansu gatunkowego"

        return analysis

    def get_available_genres(self) -> List[Dict[str, Any]]:
        """Zwraca listę dostępnych gatunków z opisami"""
        return [
            {
                "type": genre.value,
                "name": genre.value.replace("_", " ").title(),
                "profile": {
                    "world_building": self.genre_profiles[genre].world_building_level,
                    "character_focus": self.genre_profiles[genre].character_focus,
                    "action_level": self.genre_profiles[genre].action_level,
                    "romance_level": self.genre_profiles[genre].romance_level,
                    "mystery_level": self.genre_profiles[genre].mystery_level,
                    "philosophical_depth": self.genre_profiles[genre].philosophical_depth
                },
                "compatible_with": [g.value for g in self.genre_profiles[genre].compatible_genres],
                "conflicts_with": [g.value for g in self.genre_profiles[genre].conflict_genres]
            }
            for genre in self.genre_profiles.keys()
        ]

    def get_active_blend(self, blend_id: str) -> Optional[BlendedGenreProfile]:
        """Pobiera aktywny blend po ID"""
        return self.active_blends.get(blend_id)

    def list_active_blends(self) -> List[Dict[str, Any]]:
        """Listuje wszystkie aktywne blendy"""
        return [
            {
                "blend_id": b.blend_id,
                "name": b.name,
                "genres": [g.value for g in b.source_genres],
                "style": b.ratios.blend_style,
                "created_at": b.created_at.isoformat()
            }
            for b in self.active_blends.values()
        ]


# Singleton instance
def get_genre_blending_service() -> DynamicGenreBlendingService:
    """Pobiera instancję serwisu Genre Blending"""
    return DynamicGenreBlendingService()


# Export dla API
genre_blending_service = get_genre_blending_service()
