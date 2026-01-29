"""
TITAN (Title Intelligence & Transformation Analysis Network)
12-dimensional title analysis system for NarraForge 2.0

This system analyzes book titles across 12 dimensions to extract
deep semantic meaning and generate unique, tailored book parameters.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import random
import json

from app.services.ai_service import AIService
from app.models.project import GenreType
from app.config import settings


class TITANDimension(str, Enum):
    """The 12 dimensions of TITAN analysis"""
    SEMANTIC_DEPTH = "semantic_depth"
    EMOTIONAL_RESONANCE = "emotional_resonance"
    TEMPORALITY = "temporality"
    SPATIAL_WORLD = "spatial_world"
    IMPLIED_CHARACTERS = "implied_characters"
    CENTRAL_CONFLICT = "central_conflict"
    NARRATIVE_PROMISE = "narrative_promise"
    STYLE_TONE = "style_tone"
    DEEP_PSYCHOLOGY = "deep_psychology"
    INTERTEXTUALITY = "intertextuality"
    COMMERCIAL_POTENTIAL = "commercial_potential"
    TRANSCENDENCE = "transcendence"


@dataclass
class DimensionResult:
    """Result of analyzing a single dimension"""
    dimension: TITANDimension
    output: Dict[str, Any]
    impact_on_book: Dict[str, Any]
    confidence: float = 0.0


@dataclass
class TITANAnalysis:
    """Complete TITAN analysis result for a title"""
    title: str
    dimensions: Dict[TITANDimension, DimensionResult] = field(default_factory=dict)
    suggested_genre: Optional[GenreType] = None
    overall_complexity: float = 0.0
    uniqueness_score: float = 0.0

    def get_dimension(self, dim: TITANDimension) -> Optional[DimensionResult]:
        return self.dimensions.get(dim)

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "dimensions": {
                k.value: {
                    "output": v.output,
                    "impact_on_book": v.impact_on_book,
                    "confidence": v.confidence
                }
                for k, v in self.dimensions.items()
            },
            "suggested_genre": self.suggested_genre.value if self.suggested_genre else None,
            "overall_complexity": self.overall_complexity,
            "uniqueness_score": self.uniqueness_score
        }


# Dimension configurations with prompts and output schemas
DIMENSION_CONFIGS = {
    TITANDimension.SEMANTIC_DEPTH: {
        "description": "Wielowarstwowe znaczenia ukryte w tytule",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem GŁĘBOKIEJ SEMANTYKI:

1. PRIMARY_MEANING: Co tytuł dosłownie oznacza?
2. SECONDARY_MEANINGS: Jakie metafory, alegorie są ukryte? (lista)
3. HIDDEN_SYMBOLS: Jakie symbole można odczytać? (lista)
4. CULTURAL_REFERENCES: Jakie odniesienia kulturowe zawiera? (lista)
5. UNIVERSAL_THEMES: Jakie uniwersalne tematy porusza? (lista)

Odpowiedz w formacie JSON:
{{
    "primary_meaning": "...",
    "secondary_meanings": ["...", "..."],
    "hidden_symbols": ["...", "..."],
    "cultural_references": ["...", "..."],
    "universal_themes": ["...", "..."]
}}""",
        "impact_mapping": {
            "thematic_layers": "Ilość warstw tematycznych (1-5)",
            "symbol_density": "Gęstość symboliki w tekście",
            "interpretation_depth": "Głębokość możliwych interpretacji"
        }
    },

    TITANDimension.EMOTIONAL_RESONANCE: {
        "description": "Jakie emocje wywołuje tytuł",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem EMOCJONALNEJ REZONANCJI:

1. PRIMARY_EMOTION: Jaka główna emocja dominuje?
2. EMOTIONAL_SPECTRUM: Jakie spektrum emocji wywołuje? (lista)
3. INTENSITY_LEVEL: Jak intensywne są te emocje? (1-10)
4. CATHARSIS_POTENTIAL: Jaki potencjał katarsis oferuje?
5. READER_HOOK: Co emocjonalnie przyciąga czytelnika?

Odpowiedz w formacie JSON:
{{
    "primary_emotion": "...",
    "emotional_spectrum": ["...", "..."],
    "intensity_level": 7,
    "catharsis_potential": "...",
    "reader_hook": "..."
}}""",
        "impact_mapping": {
            "emotional_arc_complexity": "Złożoność łuku emocjonalnego",
            "tear_jerker_moments": "Ilość momentów wzruszających",
            "tension_peaks": "Ilość szczytów napięcia"
        }
    },

    TITANDimension.TEMPORALITY: {
        "description": "Wymiar czasowy zawarty w tytule",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem TEMPORALNOŚCI:

1. TIME_PERIOD: Jaki okres czasowy sugeruje? (przeszłość/teraźniejszość/przyszłość/ponadczasowy)
2. TIME_SPAN: Jak długi okres obejmuje historia?
3. TEMPORAL_COMPLEXITY: Jaka jest struktura czasowa? (linearny/nielinearny/wielowątkowy)
4. URGENCY_LEVEL: Jak pilna jest historia? (1-10)
5. NOSTALGIA_FACTOR: Ile nostalgii zawiera? (1-10)

Odpowiedz w formacie JSON:
{{
    "time_period": "...",
    "time_span": "...",
    "temporal_complexity": "...",
    "urgency_level": 5,
    "nostalgia_factor": 3
}}""",
        "impact_mapping": {
            "chapter_time_jumps": "Czy i ile skoków czasowych",
            "flashback_frequency": "Ilość retrospekcji",
            "pacing_style": "Tempo narracji"
        }
    },

    TITANDimension.SPATIAL_WORLD: {
        "description": "Geografia i świat sugerowany przez tytuł",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem PRZESTRZENI I ŚWIATA:

1. WORLD_TYPE: Jaki typ świata? (realny/fantastyczny/mieszany/science-fiction)
2. SCALE: Jaka skala? (intymny/lokalny/regionalny/globalny/kosmiczny)
3. LOCATION_HINTS: Jakie lokalizacje sugeruje tytuł? (lista - NIE zakładaj domyślnie Europy!)
4. ATMOSPHERE: Jaka atmosfera miejsca?
5. WORLD_UNIQUENESS: Jak unikalny jest świat? (1-10)

WAŻNE: Nie zakładaj domyślnie Europy. Rozważ Azję, Afrykę, Ameryki, Oceanię lub całkowicie fantastyczne lokacje.

Odpowiedz w formacie JSON:
{{
    "world_type": "...",
    "scale": "...",
    "location_hints": ["...", "..."],
    "atmosphere": "...",
    "world_uniqueness": 7
}}""",
        "impact_mapping": {
            "locations_count": "Ilość unikalnych lokacji",
            "world_building_depth": "Głębokość budowania świata",
            "travel_narrative": "Czy jest motyw podróży"
        }
    },

    TITANDimension.IMPLIED_CHARACTERS: {
        "description": "Postacie sugerowane przez tytuł",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem IMPLIKOWANYCH POSTACI:

1. PROTAGONIST_ARCHETYPE: Jaki archetyp bohatera sugeruje tytuł?
2. ANTAGONIST_TYPE: Jaki typ antagonisty?
3. RELATIONSHIP_DYNAMICS: Jakie dynamiki relacji? (lista)
4. CHARACTER_COUNT_SUGGESTION: Ilu głównych bohaterów sugeruje? (liczba)
5. ENSEMBLE_VS_SOLO: Historia zespołowa czy o samotnym bohaterze?

Odpowiedz w formacie JSON:
{{
    "protagonist_archetype": "...",
    "antagonist_type": "...",
    "relationship_dynamics": ["...", "..."],
    "character_count_suggestion": 4,
    "ensemble_vs_solo": "..."
}}""",
        "impact_mapping": {
            "main_characters": "Ilość głównych postaci",
            "supporting_cast": "Wielkość obsady drugoplanowej",
            "character_depth": "Głębokość charakteryzacji"
        }
    },

    TITANDimension.CENTRAL_CONFLICT: {
        "description": "Rodzaj konfliktu sugerowany przez tytuł",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem CENTRALNEGO KONFLIKTU:

1. CONFLICT_TYPE: Jaki typ konfliktu? (wewnętrzny/zewnętrzny/oba)
2. CONFLICT_SCALE: Jaka skala? (osobisty/rodzinny/społeczny/globalny/kosmiczny)
3. STAKES_LEVEL: Jak wysokie stawki? (1-10)
4. MORAL_COMPLEXITY: Jak złożony moralnie? (1-10)
5. RESOLUTION_TYPE: Jaki typ rozwiązania? (jednoznaczne/ambiwalentne/otwarte)

Odpowiedz w formacie JSON:
{{
    "conflict_type": "...",
    "conflict_scale": "...",
    "stakes_level": 7,
    "moral_complexity": 6,
    "resolution_type": "..."
}}""",
        "impact_mapping": {
            "subplot_count": "Ilość wątków pobocznych",
            "conflict_layers": "Ilość warstw konfliktu",
            "climax_intensity": "Intensywność kulminacji"
        }
    },

    TITANDimension.NARRATIVE_PROMISE: {
        "description": "Co tytuł obiecuje czytelnikowi",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem NARRACYJNEJ OBIETNICY:

1. GENRE_SIGNALS: Jakie gatunki sugeruje? (lista)
2. READER_EXPECTATIONS: Czego czytelnik oczekuje? (lista)
3. HOOK_STRENGTH: Jak silny jest hak? (1-10)
4. MYSTERY_QUOTIENT: Ile tajemnicy zawiera? (1-10)
5. SATISFACTION_TYPE: Jaki rodzaj satysfakcji oferuje?

Odpowiedz w formacie JSON:
{{
    "genre_signals": ["...", "..."],
    "reader_expectations": ["...", "..."],
    "hook_strength": 8,
    "mystery_quotient": 6,
    "satisfaction_type": "..."
}}""",
        "impact_mapping": {
            "twist_count": "Ilość zwrotów akcji",
            "mystery_depth": "Głębokość zagadki",
            "payoff_magnitude": "Wielkość wypłaty narracyjnej"
        }
    },

    TITANDimension.STYLE_TONE: {
        "description": "Styl i ton sugerowany przez tytuł",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem STYLU I TONU:

1. FORMALITY_LEVEL: Jaki poziom formalności? (formalny/nieformalny/mieszany)
2. PROSE_STYLE: Jaki styl prozy? (poetycki/surowy/barokowy/minimalistyczny/klasyczny)
3. HUMOR_QUOTIENT: Ile humoru? (0-10)
4. DARKNESS_LEVEL: Jak mroczny? (0-10)
5. LITERARY_AMBITION: Jak literacko ambitny? (1-10)

Odpowiedz w formacie JSON:
{{
    "formality_level": "...",
    "prose_style": "...",
    "humor_quotient": 3,
    "darkness_level": 5,
    "literary_ambition": 7
}}""",
        "impact_mapping": {
            "vocabulary_complexity": "Złożoność słownictwa",
            "sentence_structure": "Struktura zdań",
            "descriptive_density": "Gęstość opisów"
        }
    },

    TITANDimension.DEEP_PSYCHOLOGY: {
        "description": "Psychologiczne warstwy w tytule",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem GŁĘBOKIEJ PSYCHOLOGII:

1. PSYCHOLOGICAL_THEMES: Jakie tematy psychologiczne? (lista)
2. TRAUMA_INDICATORS: Jakie traumy mogą być eksplorowane? (lista)
3. GROWTH_ARC_TYPE: Jaki typ łuku rozwoju postaci?
4. SHADOW_WORK: Jakie jungowskie cienie mogą być eksplorowane?
5. COLLECTIVE_UNCONSCIOUS: Jakie archetypy zbiorowej nieświadomości? (lista)

Odpowiedz w formacie JSON:
{{
    "psychological_themes": ["...", "..."],
    "trauma_indicators": ["...", "..."],
    "growth_arc_type": "...",
    "shadow_work": "...",
    "collective_unconscious": ["...", "..."]
}}""",
        "impact_mapping": {
            "internal_monologue_depth": "Głębokość monologu wewnętrznego",
            "psychological_realism": "Realizm psychologiczny",
            "character_transformation": "Skala transformacji postaci"
        }
    },

    TITANDimension.INTERTEXTUALITY: {
        "description": "Odniesienia do innych dzieł",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem INTERTEKSTUALNOŚCI:

1. LITERARY_ECHOES: Jakie echa innych dzieł literackich? (lista)
2. MYTHOLOGICAL_ROOTS: Jakie korzenie mitologiczne? (lista)
3. ARCHETYPAL_PATTERNS: Jakie wzorce archetypowe? (lista)
4. GENRE_CONVENTIONS: Jakie konwencje gatunkowe? (lista)
5. SUBVERSION_POTENTIAL: Potencjał do subwersji konwencji? (1-10)

Odpowiedz w formacie JSON:
{{
    "literary_echoes": ["...", "..."],
    "mythological_roots": ["...", "..."],
    "archetypal_patterns": ["...", "..."],
    "genre_conventions": ["...", "..."],
    "subversion_potential": 5
}}""",
        "impact_mapping": {
            "homage_elements": "Elementy hołdu",
            "genre_innovation": "Innowacja gatunkowa",
            "meta_narrative": "Elementy metanarracyjne"
        }
    },

    TITANDimension.COMMERCIAL_POTENTIAL: {
        "description": "Potencjał rynkowy tytułu",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem POTENCJAŁU KOMERCYJNEGO:

1. TARGET_AUDIENCE: Jaka grupa docelowa? (lista)
2. MARKET_POSITIONING: Jakie pozycjonowanie rynkowe?
3. SERIES_POTENTIAL: Potencjał na serię? (1-10)
4. ADAPTATION_POTENTIAL: Potencjał adaptacji? (film/serial/gra)
5. VIRAL_HOOKS: Jakie wirusowe haki? (lista)

Odpowiedz w formacie JSON:
{{
    "target_audience": ["...", "..."],
    "market_positioning": "...",
    "series_potential": 7,
    "adaptation_potential": "...",
    "viral_hooks": ["...", "..."]
}}""",
        "impact_mapping": {
            "accessibility_level": "Poziom dostępności",
            "page_turner_quotient": "Współczynnik 'nie mogę odłożyć'",
            "sequel_setup": "Przygotowanie pod kontynuację"
        }
    },

    TITANDimension.TRANSCENDENCE: {
        "description": "Wymiar duchowy i transcendentny",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem TRANSCENDENCJI:

1. SPIRITUAL_DIMENSION: Jaki wymiar duchowy?
2. EXISTENTIAL_QUESTIONS: Jakie pytania egzystencjalne podnosi? (lista)
3. MEANING_OF_LIFE_TOUCH: Jak bardzo dotyka sensu życia? (1-10)
4. HOPE_VS_DESPAIR: Więcej nadziei czy rozpaczy?
5. LEGACY_THEME: Jaki temat dziedzictwa?

Odpowiedz w formacie JSON:
{{
    "spiritual_dimension": "...",
    "existential_questions": ["...", "..."],
    "meaning_of_life_touch": 6,
    "hope_vs_despair": "...",
    "legacy_theme": "..."
}}""",
        "impact_mapping": {
            "philosophical_depth": "Głębokość filozoficzna",
            "spiritual_journey": "Czy jest podróż duchowa",
            "redemption_arc": "Czy jest łuk odkupienia"
        }
    }
}


class TITANAnalyzer:
    """
    12-dimensional title analysis system.
    Each dimension generates specific book parameters.
    """

    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or AIService()

    async def analyze_title(
        self,
        title: str,
        genre_hint: Optional[GenreType] = None,
        full_analysis: bool = True
    ) -> TITANAnalysis:
        """
        Perform full TITAN analysis on a title.

        Args:
            title: The book title to analyze
            genre_hint: Optional genre hint to guide analysis
            full_analysis: If True, analyze all 12 dimensions. If False, only key dimensions.

        Returns:
            TITANAnalysis with all dimension results
        """
        analysis = TITANAnalysis(title=title)

        # Determine which dimensions to analyze
        dimensions_to_analyze = list(TITANDimension)
        if not full_analysis:
            # Quick analysis - only core dimensions
            dimensions_to_analyze = [
                TITANDimension.SEMANTIC_DEPTH,
                TITANDimension.EMOTIONAL_RESONANCE,
                TITANDimension.SPATIAL_WORLD,
                TITANDimension.IMPLIED_CHARACTERS,
                TITANDimension.NARRATIVE_PROMISE,
                TITANDimension.STYLE_TONE
            ]

        # Analyze each dimension
        for dimension in dimensions_to_analyze:
            result = await self._analyze_dimension(title, dimension, genre_hint)
            analysis.dimensions[dimension] = result

        # Calculate overall metrics
        analysis.overall_complexity = self._calculate_complexity(analysis)
        analysis.uniqueness_score = self._calculate_uniqueness(analysis)

        # Suggest genre if not provided
        if not genre_hint:
            analysis.suggested_genre = self._suggest_genre(analysis)
        else:
            analysis.suggested_genre = genre_hint

        return analysis

    async def _analyze_dimension(
        self,
        title: str,
        dimension: TITANDimension,
        genre_hint: Optional[GenreType]
    ) -> DimensionResult:
        """Analyze a single dimension of the title."""
        config = DIMENSION_CONFIGS[dimension]

        prompt = config["prompt_template"].format(title=title)
        if genre_hint:
            prompt += f"\n\nKontekst gatunkowy: {genre_hint.value}"

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                model_tier=1,  # Use Tier 1 for analysis (fast & cheap)
                max_tokens=1000,
                temperature=0.7
            )

            # Parse JSON response
            output = self._parse_json_response(response)

            # Calculate impact on book parameters
            impact = self._calculate_dimension_impact(dimension, output)

            return DimensionResult(
                dimension=dimension,
                output=output,
                impact_on_book=impact,
                confidence=0.85  # Base confidence
            )

        except Exception as e:
            # Return empty result on error
            return DimensionResult(
                dimension=dimension,
                output={},
                impact_on_book={},
                confidence=0.0
            )

    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from AI response, handling potential formatting issues."""
        # Try to find JSON in response
        try:
            # First, try direct parse
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from markdown code block
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find raw JSON object
        json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Return empty dict if all parsing fails
        return {}

    def _calculate_dimension_impact(
        self,
        dimension: TITANDimension,
        output: Dict
    ) -> Dict[str, Any]:
        """Calculate the impact of dimension analysis on book parameters."""
        impact = {}

        if dimension == TITANDimension.SEMANTIC_DEPTH:
            secondary = output.get("secondary_meanings", [])
            symbols = output.get("hidden_symbols", [])
            impact["thematic_layers"] = min(5, len(secondary) + 1)
            impact["symbol_density"] = min(10, len(symbols) * 2) / 10
            impact["interpretation_depth"] = len(output.get("universal_themes", [])) + 1

        elif dimension == TITANDimension.EMOTIONAL_RESONANCE:
            intensity = output.get("intensity_level", 5)
            impact["emotional_arc_complexity"] = "complex" if intensity > 7 else "moderate" if intensity > 4 else "simple"
            impact["tear_jerker_moments"] = max(2, intensity - 3)
            impact["tension_peaks"] = max(3, intensity - 2)

        elif dimension == TITANDimension.TEMPORALITY:
            complexity = output.get("temporal_complexity", "linear")
            impact["chapter_time_jumps"] = 5 if complexity == "nielinearny" else 2 if complexity == "wielowątkowy" else 0
            impact["flashback_frequency"] = output.get("nostalgia_factor", 3)
            urgency = output.get("urgency_level", 5)
            impact["pacing_style"] = "fast" if urgency > 7 else "moderate" if urgency > 4 else "contemplative"

        elif dimension == TITANDimension.SPATIAL_WORLD:
            uniqueness = output.get("world_uniqueness", 5)
            scale = output.get("scale", "local")
            scale_map = {"intymny": 3, "lokalny": 8, "regionalny": 15, "globalny": 30, "kosmiczny": 50}
            impact["locations_count"] = scale_map.get(scale, 10) + uniqueness
            impact["world_building_depth"] = "extensive" if uniqueness > 7 else "moderate" if uniqueness > 4 else "minimal"
            impact["travel_narrative"] = scale in ["regionalny", "globalny", "kosmiczny"]

        elif dimension == TITANDimension.IMPLIED_CHARACTERS:
            char_count = output.get("character_count_suggestion", 4)
            ensemble = output.get("ensemble_vs_solo", "")
            impact["main_characters"] = char_count
            impact["supporting_cast"] = char_count * 3
            impact["character_depth"] = "deep" if char_count <= 5 else "moderate" if char_count <= 8 else "varying"

        elif dimension == TITANDimension.CENTRAL_CONFLICT:
            moral_complexity = output.get("moral_complexity", 5)
            stakes = output.get("stakes_level", 5)
            impact["subplot_count"] = max(2, moral_complexity - 2)
            impact["conflict_layers"] = min(5, moral_complexity // 2 + 1)
            impact["climax_intensity"] = "explosive" if stakes > 7 else "emotional" if stakes > 4 else "quiet"

        elif dimension == TITANDimension.NARRATIVE_PROMISE:
            mystery = output.get("mystery_quotient", 5)
            hook = output.get("hook_strength", 5)
            impact["twist_count"] = max(2, mystery - 2)
            impact["mystery_depth"] = "labyrinthine" if mystery > 7 else "moderate" if mystery > 4 else "straightforward"
            impact["payoff_magnitude"] = "epic" if hook > 7 else "satisfying" if hook > 4 else "subtle"

        elif dimension == TITANDimension.STYLE_TONE:
            prose_style = output.get("prose_style", "klasyczny")
            literary_ambition = output.get("literary_ambition", 5)
            impact["vocabulary_complexity"] = "high" if literary_ambition > 7 else "moderate" if literary_ambition > 4 else "accessible"
            impact["sentence_structure"] = prose_style
            impact["descriptive_density"] = "rich" if prose_style in ["poetycki", "barokowy"] else "sparse" if prose_style == "minimalistyczny" else "balanced"

        elif dimension == TITANDimension.DEEP_PSYCHOLOGY:
            themes = output.get("psychological_themes", [])
            growth_type = output.get("growth_arc_type", "")
            impact["internal_monologue_depth"] = "profound" if len(themes) > 3 else "moderate" if themes else "minimal"
            impact["psychological_realism"] = len(themes) > 0
            impact["character_transformation"] = "radical" if "trauma" in str(themes).lower() else "significant" if growth_type else "subtle"

        elif dimension == TITANDimension.INTERTEXTUALITY:
            subversion = output.get("subversion_potential", 5)
            echoes = output.get("literary_echoes", [])
            impact["homage_elements"] = len(echoes)
            impact["genre_innovation"] = "innovative" if subversion > 7 else "fresh" if subversion > 4 else "traditional"
            impact["meta_narrative"] = subversion > 6

        elif dimension == TITANDimension.COMMERCIAL_POTENTIAL:
            series = output.get("series_potential", 5)
            audience = output.get("target_audience", [])
            impact["accessibility_level"] = "broad" if len(audience) > 2 else "niche"
            impact["page_turner_quotient"] = series > 6
            impact["sequel_setup"] = series > 7

        elif dimension == TITANDimension.TRANSCENDENCE:
            meaning = output.get("meaning_of_life_touch", 5)
            hope = output.get("hope_vs_despair", "balanced")
            impact["philosophical_depth"] = "profound" if meaning > 7 else "present" if meaning > 4 else "light"
            impact["spiritual_journey"] = meaning > 5
            impact["redemption_arc"] = "hope" in str(hope).lower() or meaning > 6

        return impact

    def _calculate_complexity(self, analysis: TITANAnalysis) -> float:
        """Calculate overall complexity score from all dimensions."""
        complexity_factors = []

        for dim, result in analysis.dimensions.items():
            output = result.output

            if dim == TITANDimension.SEMANTIC_DEPTH:
                complexity_factors.append(len(output.get("secondary_meanings", [])) / 5)
            elif dim == TITANDimension.EMOTIONAL_RESONANCE:
                complexity_factors.append(output.get("intensity_level", 5) / 10)
            elif dim == TITANDimension.CENTRAL_CONFLICT:
                complexity_factors.append(output.get("moral_complexity", 5) / 10)
            elif dim == TITANDimension.STYLE_TONE:
                complexity_factors.append(output.get("literary_ambition", 5) / 10)
            elif dim == TITANDimension.DEEP_PSYCHOLOGY:
                complexity_factors.append(len(output.get("psychological_themes", [])) / 5)

        if complexity_factors:
            return sum(complexity_factors) / len(complexity_factors)
        return 0.5

    def _calculate_uniqueness(self, analysis: TITANAnalysis) -> float:
        """Calculate uniqueness score based on analysis."""
        uniqueness_factors = []

        for dim, result in analysis.dimensions.items():
            output = result.output

            if dim == TITANDimension.SPATIAL_WORLD:
                uniqueness_factors.append(output.get("world_uniqueness", 5) / 10)
            elif dim == TITANDimension.INTERTEXTUALITY:
                uniqueness_factors.append(output.get("subversion_potential", 5) / 10)
            elif dim == TITANDimension.NARRATIVE_PROMISE:
                uniqueness_factors.append(output.get("mystery_quotient", 5) / 10)

        if uniqueness_factors:
            return sum(uniqueness_factors) / len(uniqueness_factors)
        return 0.5

    def _suggest_genre(self, analysis: TITANAnalysis) -> GenreType:
        """Suggest the best genre based on TITAN analysis."""
        scores = {genre: 0.0 for genre in GenreType}

        # Analyze narrative promise signals
        narrative = analysis.dimensions.get(TITANDimension.NARRATIVE_PROMISE)
        if narrative:
            signals = narrative.output.get("genre_signals", [])
            for signal in signals:
                signal_lower = signal.lower()
                if "sci" in signal_lower or "fiction" in signal_lower or "tech" in signal_lower or "space" in signal_lower:
                    scores[GenreType.SCI_FI] += 2
                if "fanta" in signal_lower or "magic" in signal_lower or "epic" in signal_lower:
                    scores[GenreType.FANTASY] += 2
                if "thriller" in signal_lower or "suspense" in signal_lower or "tension" in signal_lower:
                    scores[GenreType.THRILLER] += 2
                if "horror" in signal_lower or "strach" in signal_lower or "groza" in signal_lower:
                    scores[GenreType.HORROR] += 2
                if "romans" in signal_lower or "miłość" in signal_lower or "love" in signal_lower:
                    scores[GenreType.ROMANCE] += 2
                if "drama" in signal_lower or "famil" in signal_lower:
                    scores[GenreType.DRAMA] += 2
                if "komed" in signal_lower or "humor" in signal_lower or "śmiech" in signal_lower:
                    scores[GenreType.COMEDY] += 2
                if "mystery" in signal_lower or "detekt" in signal_lower or "krymi" in signal_lower:
                    scores[GenreType.MYSTERY] += 2
                if "relig" in signal_lower or "duchow" in signal_lower or "wiara" in signal_lower or "bóg" in signal_lower:
                    scores[GenreType.RELIGIOUS] += 2

        # Analyze style/tone
        style = analysis.dimensions.get(TITANDimension.STYLE_TONE)
        if style:
            darkness = style.output.get("darkness_level", 5)
            humor = style.output.get("humor_quotient", 3)

            if darkness > 7:
                scores[GenreType.HORROR] += 1
                scores[GenreType.THRILLER] += 1
            if humor > 6:
                scores[GenreType.COMEDY] += 2

        # Analyze transcendence
        transcendence = analysis.dimensions.get(TITANDimension.TRANSCENDENCE)
        if transcendence:
            spiritual = transcendence.output.get("spiritual_dimension", "")
            meaning = transcendence.output.get("meaning_of_life_touch", 5)

            if spiritual and meaning > 6:
                scores[GenreType.RELIGIOUS] += 2
                scores[GenreType.DRAMA] += 1

        # Analyze spatial world
        spatial = analysis.dimensions.get(TITANDimension.SPATIAL_WORLD)
        if spatial:
            world_type = spatial.output.get("world_type", "")

            if "fanta" in world_type.lower():
                scores[GenreType.FANTASY] += 2
            if "science" in world_type.lower() or "sci-fi" in world_type.lower():
                scores[GenreType.SCI_FI] += 2

        # Return genre with highest score, default to DRAMA
        max_genre = max(scores, key=scores.get)
        return max_genre if scores[max_genre] > 0 else GenreType.DRAMA


# Singleton instance
_titan_analyzer: Optional[TITANAnalyzer] = None


def get_titan_analyzer() -> TITANAnalyzer:
    """Get or create TITAN analyzer instance."""
    global _titan_analyzer
    if _titan_analyzer is None:
        _titan_analyzer = TITANAnalyzer()
    return _titan_analyzer
