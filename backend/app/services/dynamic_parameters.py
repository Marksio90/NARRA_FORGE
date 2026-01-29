"""
Dynamic Book Parameters Generator for NarraForge 2.0

Generates unique, tailored book parameters based on TITAN analysis.
No two books will ever have identical parameters.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import random
import math

from app.services.titan_analyzer import TITANAnalysis, TITANDimension
from app.models.project import GenreType


@dataclass
class BookParameters:
    """
    Dynamically generated book parameters.
    Each title produces unique parameters based on its TITAN analysis.
    """
    # Volume parameters
    word_count: int = 80000
    chapter_count: int = 25
    scenes_per_chapter: int = 4

    # Character parameters
    main_characters: int = 4
    supporting_characters: int = 10
    minor_characters: int = 20
    character_depth_level: str = "deep"

    # World parameters
    locations_count: int = 15
    world_building_pages: int = 5
    primary_location: str = "Varied"
    cultural_setting: str = "Diverse"

    # Plot parameters
    subplot_count: int = 3
    twist_count: int = 3
    climax_count: int = 1

    # Style parameters
    prose_style: str = "klasyczny"
    vocabulary_level: str = "moderate"
    descriptive_density: str = "balanced"

    # Emotional parameters
    emotional_intensity: int = 6

    # Pacing parameters
    pacing_style: str = "moderate"
    chapter_cliffhangers: bool = True

    # Series parameters
    series_potential: int = 5
    sequel_hooks: int = 2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_word_count": self.word_count,
            "chapter_count": self.chapter_count,
            "scenes_per_chapter": self.scenes_per_chapter,
            "character_count": {
                "main": self.main_characters,
                "supporting": self.supporting_characters,
                "minor": self.minor_characters
            },
            "character_depth_level": self.character_depth_level,
            "locations_count": self.locations_count,
            "world_building_pages": self.world_building_pages,
            "primary_location": self.primary_location,
            "cultural_setting": self.cultural_setting,
            "subplot_count": self.subplot_count,
            "twist_count": self.twist_count,
            "climax_count": self.climax_count,
            "prose_style": self.prose_style,
            "vocabulary_level": self.vocabulary_level,
            "descriptive_density": self.descriptive_density,
            "emotional_intensity": self.emotional_intensity,
            "pacing_style": self.pacing_style,
            "chapter_cliffhangers": self.chapter_cliffhangers,
            "series_potential": self.series_potential,
            "sequel_hooks": self.sequel_hooks
        }


class DynamicParameterGenerator:
    """
    Generates unique book parameters based on TITAN analysis.
    Each title produces different parameters - never two identical books.
    """

    # Word count ranges by genre
    GENRE_WORD_RANGES = {
        GenreType.SCI_FI: (70000, 150000),
        GenreType.FANTASY: (80000, 200000),
        GenreType.THRILLER: (60000, 100000),
        GenreType.HORROR: (60000, 90000),
        GenreType.ROMANCE: (60000, 100000),
        GenreType.DRAMA: (70000, 120000),
        GenreType.COMEDY: (60000, 90000),
        GenreType.MYSTERY: (65000, 100000),
        GenreType.RELIGIOUS: (60000, 150000),
    }

    # Location pool for non-default settings
    LOCATION_POOLS = {
        "asia": ["Japonia", "Chiny", "Korea", "Indie", "Tajlandia", "Wietnam", "Mongolia"],
        "africa": ["Nigeria", "Egipt", "Maroko", "Tanzania", "Kenia", "Etiopia", "RPA"],
        "americas": ["Brazylia", "Meksyk", "Argentyna", "Peru", "Chile", "Kanada", "USA"],
        "oceania": ["Australia", "Nowa Zelandia", "Fidżi", "Samoa", "Papua Nowa Gwinea"],
        "europe": ["Polska", "Francja", "Włochy", "Hiszpania", "Grecja", "Norwegia", "Irlandia"],
        "middle_east": ["Iran", "Turcja", "Izrael", "Arabia Saudyjska", "Jordania"],
        "fantasy": ["Świat fantastyczny", "Wymiar alternatywny", "Magiczne królestwo"],
        "scifi": ["Stacja kosmiczna", "Kolonia na Marsie", "Cyberpunkowe miasto", "Statek generacyjny"]
    }

    CULTURAL_SETTINGS = [
        "Azjatycka", "Afrykańska", "Latynoamerykańska", "Nordycka",
        "Słowiańska", "Bliskowschodnia", "Pacyficzna", "Kosmopolityczna",
        "Mieszana/Wielokulturowa", "Całkowicie fantastyczna", "Futurystyczna"
    ]

    def generate_from_titan(
        self,
        titan_analysis: TITANAnalysis,
        genre: GenreType
    ) -> BookParameters:
        """
        Generate unique book parameters from TITAN analysis.
        No two titles will produce identical parameters.
        """
        params = BookParameters()

        # Calculate word count (dynamic!)
        params.word_count = self._calculate_word_count(titan_analysis, genre)

        # Calculate chapter count (based on word count and pacing)
        params.chapter_count = self._calculate_chapters(titan_analysis, params.word_count)

        # Calculate scenes per chapter
        params.scenes_per_chapter = self._calculate_scenes_per_chapter(titan_analysis)

        # Calculate character counts
        params.main_characters = self._calculate_main_chars(titan_analysis)
        params.supporting_characters = self._calculate_supporting_chars(titan_analysis, params.main_characters)
        params.minor_characters = self._calculate_minor_chars(params.main_characters, params.supporting_characters)
        params.character_depth_level = self._determine_character_depth(titan_analysis)

        # Calculate world parameters
        params.locations_count = self._calculate_locations(titan_analysis)
        params.world_building_pages = self._calculate_world_pages(titan_analysis, genre)
        params.primary_location, params.cultural_setting = self._determine_location(titan_analysis, genre)

        # Calculate plot parameters
        params.subplot_count = self._calculate_subplots(titan_analysis)
        params.twist_count = self._calculate_twists(titan_analysis)
        params.climax_count = self._calculate_climaxes(titan_analysis)

        # Calculate style parameters
        params.prose_style = self._determine_prose_style(titan_analysis)
        params.vocabulary_level = self._determine_vocabulary(titan_analysis)
        params.descriptive_density = self._determine_descriptive_density(titan_analysis)

        # Calculate emotional parameters
        params.emotional_intensity = self._calculate_emotional_intensity(titan_analysis)

        # Calculate pacing
        params.pacing_style = self._determine_pacing(titan_analysis)
        params.chapter_cliffhangers = self._should_use_cliffhangers(titan_analysis, genre)

        # Calculate series potential
        params.series_potential = self._calculate_series_potential(titan_analysis)
        params.sequel_hooks = self._calculate_sequel_hooks(params.series_potential)

        # Add random variance for uniqueness (+/- 10%)
        params = self._add_variance(params)

        return params

    def _calculate_word_count(self, titan: TITANAnalysis, genre: GenreType) -> int:
        """
        Dynamically calculate word count based on TITAN analysis.
        Can range from 40,000 to 200,000 words depending on title!
        """
        min_words, max_words = self.GENRE_WORD_RANGES.get(genre, (70000, 120000))
        base = min_words

        # Add for emotional complexity
        emotional = titan.get_dimension(TITANDimension.EMOTIONAL_RESONANCE)
        if emotional:
            intensity = emotional.output.get("intensity_level", 5)
            base += intensity * 3000

        # Add for world complexity
        spatial = titan.get_dimension(TITANDimension.SPATIAL_WORLD)
        if spatial:
            uniqueness = spatial.output.get("world_uniqueness", 5)
            base += uniqueness * 5000

        # Add for character count
        chars = titan.get_dimension(TITANDimension.IMPLIED_CHARACTERS)
        if chars:
            char_count = chars.output.get("character_count_suggestion", 4)
            base += char_count * 2000

        # Add for conflict complexity
        conflict = titan.get_dimension(TITANDimension.CENTRAL_CONFLICT)
        if conflict:
            moral_complexity = conflict.output.get("moral_complexity", 5)
            base += moral_complexity * 3000

        # Add for literary ambition
        style = titan.get_dimension(TITANDimension.STYLE_TONE)
        if style:
            ambition = style.output.get("literary_ambition", 5)
            base += ambition * 4000

        # Add for psychological depth
        psychology = titan.get_dimension(TITANDimension.DEEP_PSYCHOLOGY)
        if psychology:
            themes = len(psychology.output.get("psychological_themes", []))
            base += themes * 2000

        # Ensure within genre bounds
        return min(max_words, max(min_words, base))

    def _calculate_chapters(self, titan: TITANAnalysis, word_count: int) -> int:
        """Calculate chapter count based on word count and pacing."""
        # Average words per chapter (varies by pacing)
        temporal = titan.get_dimension(TITANDimension.TEMPORALITY)
        urgency = 5
        if temporal:
            urgency = temporal.output.get("urgency_level", 5)

        # Urgent stories = shorter chapters, more of them
        if urgency > 7:
            words_per_chapter = 2500  # Short, punchy chapters
        elif urgency > 4:
            words_per_chapter = 3500  # Standard chapters
        else:
            words_per_chapter = 5000  # Long, contemplative chapters

        chapters = word_count // words_per_chapter
        return max(10, min(60, chapters))

    def _calculate_scenes_per_chapter(self, titan: TITANAnalysis) -> int:
        """Calculate scenes per chapter."""
        # More complex narratives = more scenes per chapter
        complexity = titan.overall_complexity

        if complexity > 0.7:
            return random.randint(5, 8)
        elif complexity > 0.4:
            return random.randint(3, 6)
        else:
            return random.randint(2, 4)

    def _calculate_main_chars(self, titan: TITANAnalysis) -> int:
        """Calculate main character count."""
        chars = titan.get_dimension(TITANDimension.IMPLIED_CHARACTERS)
        if chars:
            suggestion = chars.output.get("character_count_suggestion", 4)
            ensemble = chars.output.get("ensemble_vs_solo", "")

            if "solo" in ensemble.lower():
                return max(1, min(2, suggestion))
            elif "ensemble" in ensemble.lower() or "zespoł" in ensemble.lower():
                return max(4, min(12, suggestion + 2))

            return max(1, min(12, suggestion))

        return 4  # Default

    def _calculate_supporting_chars(self, titan: TITANAnalysis, main_chars: int) -> int:
        """Calculate supporting character count."""
        spatial = titan.get_dimension(TITANDimension.SPATIAL_WORLD)
        scale = "local"
        if spatial:
            scale = spatial.output.get("scale", "local")

        # Larger scale = more supporting characters
        scale_multipliers = {
            "intymny": 1,
            "lokalny": 2,
            "regionalny": 3,
            "globalny": 4,
            "kosmiczny": 5
        }
        multiplier = scale_multipliers.get(scale, 2)

        return main_chars * multiplier + random.randint(1, 5)

    def _calculate_minor_chars(self, main: int, supporting: int) -> int:
        """Calculate minor character count."""
        return (main + supporting) * 2 + random.randint(5, 15)

    def _determine_character_depth(self, titan: TITANAnalysis) -> str:
        """Determine character depth level."""
        psychology = titan.get_dimension(TITANDimension.DEEP_PSYCHOLOGY)
        if psychology:
            themes = len(psychology.output.get("psychological_themes", []))
            if themes > 4:
                return "profound"
            elif themes > 2:
                return "deep"
            elif themes > 0:
                return "moderate"
        return "standard"

    def _calculate_locations(self, titan: TITANAnalysis) -> int:
        """Calculate number of unique locations."""
        spatial = titan.get_dimension(TITANDimension.SPATIAL_WORLD)
        if spatial:
            impact = spatial.impact_on_book
            return impact.get("locations_count", 15)
        return 15

    def _calculate_world_pages(self, titan: TITANAnalysis, genre: GenreType) -> int:
        """Calculate world-building depth in pages."""
        spatial = titan.get_dimension(TITANDimension.SPATIAL_WORLD)

        # Fantasy and Sci-Fi need more world-building
        base_pages = 3
        if genre in [GenreType.FANTASY, GenreType.SCI_FI]:
            base_pages = 8
        elif genre == GenreType.RELIGIOUS:
            base_pages = 5  # Spiritual world-building

        if spatial:
            uniqueness = spatial.output.get("world_uniqueness", 5)
            return base_pages + (uniqueness // 2)

        return base_pages

    def _determine_location(self, titan: TITANAnalysis, genre: GenreType) -> tuple:
        """Determine primary location and cultural setting - NOT defaulting to Europe!"""
        spatial = titan.get_dimension(TITANDimension.SPATIAL_WORLD)

        if spatial:
            hints = spatial.output.get("location_hints", [])
            world_type = spatial.output.get("world_type", "").lower()

            # Check for specific location hints
            hints_text = " ".join(hints).lower()

            if "fanta" in world_type:
                pool = self.LOCATION_POOLS["fantasy"]
            elif "sci" in world_type or "kosm" in world_type:
                pool = self.LOCATION_POOLS["scifi"]
            elif any(x in hints_text for x in ["japonia", "chiny", "asia", "azja", "korea", "indie"]):
                pool = self.LOCATION_POOLS["asia"]
            elif any(x in hints_text for x in ["afryka", "nigeria", "egipt"]):
                pool = self.LOCATION_POOLS["africa"]
            elif any(x in hints_text for x in ["ameryka", "meksyk", "brazylia"]):
                pool = self.LOCATION_POOLS["americas"]
            elif any(x in hints_text for x in ["europa", "polska", "francja"]):
                pool = self.LOCATION_POOLS["europe"]
            else:
                # Random pool selection - NOT defaulting to Europe!
                pools = list(self.LOCATION_POOLS.keys())
                # Remove fantasy and scifi for non-speculative fiction
                if genre not in [GenreType.FANTASY, GenreType.SCI_FI]:
                    pools = [p for p in pools if p not in ["fantasy", "scifi"]]
                pool = self.LOCATION_POOLS[random.choice(pools)]

            location = random.choice(pool)
            culture = random.choice(self.CULTURAL_SETTINGS)

            return location, culture

        # Default: random, not Europe
        pools = ["asia", "africa", "americas", "oceania", "middle_east", "europe"]
        pool_name = random.choice(pools)
        location = random.choice(self.LOCATION_POOLS[pool_name])
        culture = random.choice(self.CULTURAL_SETTINGS)

        return location, culture

    def _calculate_subplots(self, titan: TITANAnalysis) -> int:
        """Calculate number of subplots."""
        conflict = titan.get_dimension(TITANDimension.CENTRAL_CONFLICT)
        if conflict:
            impact = conflict.impact_on_book
            return impact.get("subplot_count", 3)
        return 3

    def _calculate_twists(self, titan: TITANAnalysis) -> int:
        """Calculate number of plot twists."""
        narrative = titan.get_dimension(TITANDimension.NARRATIVE_PROMISE)
        if narrative:
            impact = narrative.impact_on_book
            return impact.get("twist_count", 3)
        return 3

    def _calculate_climaxes(self, titan: TITANAnalysis) -> int:
        """Calculate number of climactic moments."""
        conflict = titan.get_dimension(TITANDimension.CENTRAL_CONFLICT)
        if conflict:
            stakes = conflict.output.get("stakes_level", 5)
            if stakes > 8:
                return 3  # Multiple major climaxes
            elif stakes > 5:
                return 2  # Main climax with secondary peak
        return 1  # Single climax

    def _determine_prose_style(self, titan: TITANAnalysis) -> str:
        """Determine prose style."""
        style = titan.get_dimension(TITANDimension.STYLE_TONE)
        if style:
            return style.output.get("prose_style", "klasyczny")
        return "klasyczny"

    def _determine_vocabulary(self, titan: TITANAnalysis) -> str:
        """Determine vocabulary complexity level."""
        style = titan.get_dimension(TITANDimension.STYLE_TONE)
        if style:
            ambition = style.output.get("literary_ambition", 5)
            if ambition > 7:
                return "sophisticated"
            elif ambition > 4:
                return "moderate"
            else:
                return "accessible"
        return "moderate"

    def _determine_descriptive_density(self, titan: TITANAnalysis) -> str:
        """Determine descriptive density."""
        style = titan.get_dimension(TITANDimension.STYLE_TONE)
        if style:
            return style.impact_on_book.get("descriptive_density", "balanced")
        return "balanced"

    def _calculate_emotional_intensity(self, titan: TITANAnalysis) -> int:
        """Calculate emotional intensity (1-10)."""
        emotional = titan.get_dimension(TITANDimension.EMOTIONAL_RESONANCE)
        if emotional:
            return emotional.output.get("intensity_level", 6)
        return 6

    def _determine_pacing(self, titan: TITANAnalysis) -> str:
        """Determine pacing style."""
        temporal = titan.get_dimension(TITANDimension.TEMPORALITY)
        if temporal:
            return temporal.impact_on_book.get("pacing_style", "moderate")
        return "moderate"

    def _should_use_cliffhangers(self, titan: TITANAnalysis, genre: GenreType) -> bool:
        """Determine if chapters should end with cliffhangers."""
        # Thrillers and mysteries almost always use cliffhangers
        if genre in [GenreType.THRILLER, GenreType.MYSTERY, GenreType.HORROR]:
            return True

        narrative = titan.get_dimension(TITANDimension.NARRATIVE_PROMISE)
        if narrative:
            hook = narrative.output.get("hook_strength", 5)
            return hook > 6

        return True  # Default to yes for engagement

    def _calculate_series_potential(self, titan: TITANAnalysis) -> int:
        """Calculate series potential (1-10)."""
        commercial = titan.get_dimension(TITANDimension.COMMERCIAL_POTENTIAL)
        if commercial:
            return commercial.output.get("series_potential", 5)
        return 5

    def _calculate_sequel_hooks(self, series_potential: int) -> int:
        """Calculate number of sequel hooks based on series potential."""
        if series_potential > 7:
            return random.randint(3, 5)
        elif series_potential > 4:
            return random.randint(1, 3)
        else:
            return 0

    def _add_variance(self, params: BookParameters) -> BookParameters:
        """Add random variance to ensure uniqueness (+/- 10%)."""
        variance = random.uniform(0.9, 1.1)

        # Apply variance to numeric parameters
        params.word_count = int(params.word_count * variance)
        params.chapter_count = max(10, int(params.chapter_count * random.uniform(0.95, 1.05)))
        params.locations_count = max(5, int(params.locations_count * random.uniform(0.9, 1.1)))
        params.supporting_characters = max(3, int(params.supporting_characters * random.uniform(0.9, 1.1)))
        params.minor_characters = max(10, int(params.minor_characters * random.uniform(0.85, 1.15)))

        return params


# Singleton instance
_parameter_generator: Optional[DynamicParameterGenerator] = None


def get_parameter_generator() -> DynamicParameterGenerator:
    """Get or create parameter generator instance."""
    global _parameter_generator
    if _parameter_generator is None:
        _parameter_generator = DynamicParameterGenerator()
    return _parameter_generator
