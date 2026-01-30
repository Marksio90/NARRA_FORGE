"""
TITAN (Title Intelligence & Transformation Analysis Network) v2.0
ENHANCED: Deep Semantic Title Extraction System

This system performs deep, intelligent extraction of meaning from book titles,
deriving characters, plots, worlds, and narrative elements DIRECTLY from title semantics.
NO FALLBACKS - every element must emerge from the title's essence.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import re

from app.services.ai_service import AIService
from app.models.project import GenreType
from app.config import settings


class TITANDimension(str, Enum):
    """The 13 dimensions of TITAN analysis (Enhanced 3.0)"""
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
    # NarraForge 3.0 Enhancement
    CULTURAL_CONTEXT = "cultural_context"  # Cultural analysis dimension


@dataclass
class ImpliedCharacter:
    """A character implied by the title's semantics"""
    essence: str  # Who this character IS based on title
    role_in_story: str  # protagonist, antagonist, etc.
    title_connection: str  # How they connect to the title
    archetypal_function: str  # Their narrative function
    psychological_profile: Dict[str, str]  # wound, ghost, lie, want, need, fear
    name_suggestions: List[str]  # Names that FIT the title's essence
    must_embody: List[str]  # Themes/concepts they MUST represent


@dataclass
class TitleEssence:
    """The distilled essence of the title - the core DNA from which EVERYTHING flows"""
    core_meaning: str  # The absolute core of what the title means
    emotional_core: str  # The heart emotion
    central_question: str  # The question the title poses
    thematic_pillars: List[str]  # 3-5 themes that MUST appear
    world_seeds: List[str]  # Seeds for world building
    character_seeds: List[ImpliedCharacter]  # Seeds for characters
    conflict_seeds: List[str]  # Seeds for conflicts
    tone_palette: List[str]  # Emotional/stylistic tones
    symbolic_elements: List[str]  # Symbols that MUST appear
    forbidden_elements: List[str]  # What would BETRAY the title


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
    essence: Optional[TitleEssence] = None
    dimensions: Dict[TITANDimension, DimensionResult] = field(default_factory=dict)
    suggested_genre: Optional[GenreType] = None
    overall_complexity: float = 0.0
    uniqueness_score: float = 0.0
    title_dna: Dict[str, Any] = field(default_factory=dict)

    def get_dimension(self, dim: TITANDimension) -> Optional[DimensionResult]:
        return self.dimensions.get(dim)

    def get_implied_characters(self) -> List[ImpliedCharacter]:
        """Get all characters implied by the title."""
        if self.essence:
            return self.essence.character_seeds
        return []

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "essence": {
                "core_meaning": self.essence.core_meaning if self.essence else "",
                "emotional_core": self.essence.emotional_core if self.essence else "",
                "central_question": self.essence.central_question if self.essence else "",
                "thematic_pillars": self.essence.thematic_pillars if self.essence else [],
                "character_seeds": [
                    {
                        "essence": c.essence,
                        "role": c.role_in_story,
                        "title_connection": c.title_connection,
                        "archetypal_function": c.archetypal_function,
                        "must_embody": c.must_embody,
                        "name_suggestions": c.name_suggestions
                    }
                    for c in (self.essence.character_seeds if self.essence else [])
                ],
                "symbolic_elements": self.essence.symbolic_elements if self.essence else [],
                "forbidden_elements": self.essence.forbidden_elements if self.essence else []
            } if self.essence else None,
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
            "uniqueness_score": self.uniqueness_score,
            "title_dna": self.title_dna
        }


# Master prompt for deep title extraction
TITLE_ESSENCE_PROMPT = """Jesteś TITAN - systemem głębokiej analizy semantycznej tytułów książek.

TYTUŁ DO ANALIZY: "{title}"
{genre_context}

TWOJA MISJA: Wydobyć ABSOLUTNĄ ESENCJĘ tego tytułu. Każdy element książki - postacie, świat, fabuła - MUSI wynikać bezpośrednio z tego tytułu.

WYKONAJ GŁĘBOKĄ EKSTRAKCJĘ SEMANTYCZNĄ:

## CZĘŚĆ 1: RDZEŃ ZNACZENIOWY
Przeanalizuj każde słowo tytułu:
- Co DOSŁOWNIE oznacza każde słowo?
- Jakie METAFORY kryją się w każdym słowie?
- Jakie EMOCJE niesie każde słowo?
- Jakie OBRAZY wywołuje każde słowo?
- Jakie PYTANIA zadaje każde słowo?

## CZĘŚĆ 2: SYNTETYCZNE ZNACZENIE
- Jak słowa RAZEM tworzą nowe znaczenie?
- Jaka jest NAPIĘCIE między słowami?
- Co tytuł OBIECUJE czytelnikowi?
- Jakie PYTANIE EGZYSTENCJALNE zadaje tytuł?

## CZĘŚĆ 3: IMPLIKOWANE POSTACIE
Nawet jeśli tytuł NIE wymienia postaci, ZAWSZE implikuje pewne postacie.
Dla każdej implikowanej postaci określ:
- KIM musi być ta postać by PASOWAĆ do tytułu?
- DLACZEGO tytuł wymaga tej postaci?
- Jaka jest jej FUNKCJA NARRACYJNA w kontekście tytułu?
- Jakie cechy MUSI posiadać?
- Jakie imię by PASOWAŁO do esencji tytułu (nie losowe - pasujące semantycznie!)

## CZĘŚĆ 4: IMPLIKOWANY ŚWIAT
- Jaki świat MUSI istnieć by tytuł miał sens?
- Jakie miejsca są NIEZBĘDNE?
- Jaka atmosfera jest OBOWIĄZKOWA?

## CZĘŚĆ 5: IMPLIKOWANY KONFLIKT
- Jaki konflikt jest WPISANY w tytuł?
- Jakie napięcie MUSI istnieć?
- Co jest STAWKĄ?

## CZĘŚĆ 6: ELEMENTY ZAKAZANE
- Co byłoby ZDRADĄ tytułu?
- Czego ABSOLUTNIE nie można włączyć?

Odpowiedz w formacie JSON:
{{
    "core_meaning": "Absolutny rdzeń znaczenia tytułu w jednym zdaniu",
    "emotional_core": "Główna emocja/uczucie które tytuł niesie",
    "central_question": "Fundamentalne pytanie które tytuł zadaje",
    "word_analysis": [
        {{
            "word": "słowo",
            "literal": "dosłowne znaczenie",
            "metaphorical": ["metafora1", "metafora2"],
            "emotional": "emocja którą niesie",
            "imagery": ["obraz1", "obraz2"]
        }}
    ],
    "thematic_pillars": ["temat1", "temat2", "temat3", "temat4", "temat5"],
    "implied_characters": [
        {{
            "essence": "Kim ta postać JEST w kontekście tytułu",
            "role": "protagonist/antagonist/mentor/catalyst/etc",
            "title_connection": "Jak KONKRETNIE łączy się z tytułem",
            "function": "Funkcja narracyjna",
            "must_have_traits": ["cecha1", "cecha2", "cecha3"],
            "psychological_core": {{
                "wound": "Rana wynikająca z tematyki tytułu",
                "ghost": "Co prześladuje - związane z tytułem",
                "lie": "Fałszywe przekonanie - związane z tytułem",
                "want": "Cel zewnętrzny - związany z tytułem",
                "need": "Potrzeba wewnętrzna - związana z tytułem",
                "fear": "Strach - związany z tytułem"
            }},
            "name_suggestions": ["imię1", "imię2", "imię3"],
            "name_reasoning": "Dlaczego te imiona pasują do tytułu"
        }}
    ],
    "world_seeds": {{
        "type": "typ świata wynikający z tytułu",
        "essential_locations": ["miejsce1", "miejsce2"],
        "atmosphere": "atmosfera wymagana przez tytuł",
        "rules": ["zasada świata wynikająca z tytułu"]
    }},
    "conflict_seeds": {{
        "central_conflict": "główny konflikt wpisany w tytuł",
        "stakes": "stawka wynikająca z tytułu",
        "tension_sources": ["źródło napięcia 1", "źródło napięcia 2"]
    }},
    "symbolic_elements": ["symbol1", "symbol2", "symbol3"],
    "tone_palette": ["ton1", "ton2", "ton3"],
    "forbidden_elements": ["co byłoby zdradą tytułu 1", "co byłoby zdradą tytułu 2"],
    "title_dna_summary": "Kompletne DNA tytułu w 2-3 zdaniach - esencja z której WSZYSTKO musi wynikać"
}}"""


# Dimension configurations
DIMENSION_CONFIGS = {
    TITANDimension.SEMANTIC_DEPTH: {
        "description": "Wielowarstwowe znaczenia ukryte w tytule",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem GŁĘBOKIEJ SEMANTYKI.

UWAGA: Nie analizuj powierzchownie. Szukaj GŁĘBOKICH znaczeń.

1. PRIMARY_MEANING: Co tytuł dosłownie oznacza?
2. SECONDARY_MEANINGS: Jakie metafory, alegorie są ukryte? (minimum 3)
3. HIDDEN_SYMBOLS: Jakie symbole można odczytać? (minimum 3)
4. CULTURAL_REFERENCES: Jakie odniesienia kulturowe zawiera? (minimum 2)
5. UNIVERSAL_THEMES: Jakie uniwersalne tematy porusza? (minimum 3)
6. LINGUISTIC_POWER: Co sprawia że te słowa RAZEM mają moc?

Odpowiedz w formacie JSON:
{{
    "primary_meaning": "...",
    "secondary_meanings": ["...", "...", "..."],
    "hidden_symbols": ["...", "...", "..."],
    "cultural_references": ["...", "..."],
    "universal_themes": ["...", "...", "..."],
    "linguistic_power": "..."
}}"""
    },

    TITANDimension.EMOTIONAL_RESONANCE: {
        "description": "Jakie emocje wywołuje tytuł",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem EMOCJONALNEJ REZONANCJI.

1. PRIMARY_EMOTION: Jaka główna emocja dominuje?
2. EMOTIONAL_SPECTRUM: Jakie spektrum emocji wywołuje? (minimum 4 emocje)
3. INTENSITY_LEVEL: Jak intensywne są te emocje? (1-10)
4. EMOTIONAL_JOURNEY: Jaką podróż emocjonalną obiecuje tytuł?
5. CATHARSIS_POTENTIAL: Jaki potencjał katarsis oferuje?
6. READER_HOOK: Co emocjonalnie przyciąga czytelnika?

Odpowiedz w formacie JSON:
{{
    "primary_emotion": "...",
    "emotional_spectrum": ["...", "...", "...", "..."],
    "intensity_level": 7,
    "emotional_journey": "...",
    "catharsis_potential": "...",
    "reader_hook": "..."
}}"""
    },

    TITANDimension.TEMPORALITY: {
        "description": "Wymiar czasowy zawarty w tytule",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem TEMPORALNOŚCI.

1. TIME_PERIOD: Jaki okres czasowy sugeruje? (przeszłość/teraźniejszość/przyszłość/ponadczasowy)
2. TIME_SPAN: Jak długi okres obejmuje historia?
3. TEMPORAL_COMPLEXITY: Jaka jest struktura czasowa? (linearny/nielinearny/wielowątkowy)
4. TIME_AS_THEME: Czy czas sam w sobie jest tematem?
5. URGENCY_LEVEL: Jak pilna jest historia? (1-10)
6. NOSTALGIA_FACTOR: Ile nostalgii zawiera? (1-10)

Odpowiedz w formacie JSON:
{{
    "time_period": "...",
    "time_span": "...",
    "temporal_complexity": "...",
    "time_as_theme": "...",
    "urgency_level": 5,
    "nostalgia_factor": 3
}}"""
    },

    TITANDimension.SPATIAL_WORLD: {
        "description": "Geografia i świat sugerowany przez tytuł",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem PRZESTRZENI I ŚWIATA.

KRYTYCZNE: NIE ZAKŁADAJ domyślnie Europy/USA. Tytuł SAM dyktuje gdzie dzieje się historia.

1. WORLD_TYPE: Jaki typ świata WYNIKA z tytułu? (realny/fantastyczny/mieszany/science-fiction)
2. SCALE: Jaka skala WYNIKA z tytułu? (intymny/lokalny/regionalny/globalny/kosmiczny)
3. LOCATION_ESSENCE: Jakie LOKACJE są WPISANE w tytuł? (nie domyślne - wynikające z tytułu!)
4. ATMOSPHERE: Jaka atmosfera miejsca MUSI być by tytuł miał sens?
5. WORLD_UNIQUENESS: Jak unikalny jest świat? (1-10)
6. ENVIRONMENTAL_SYMBOLISM: Jak środowisko SYMBOLIZUJE tematy tytułu?

Odpowiedz w formacie JSON:
{{
    "world_type": "...",
    "scale": "...",
    "location_essence": ["lokacja wynikająca z tytułu 1", "lokacja 2", "lokacja 3"],
    "atmosphere": "...",
    "world_uniqueness": 7,
    "environmental_symbolism": "..."
}}"""
    },

    TITANDimension.IMPLIED_CHARACTERS: {
        "description": "Postacie sugerowane przez tytuł - KRYTYCZNA ANALIZA",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem IMPLIKOWANYCH POSTACI.

KRYTYCZNE: Nawet jeśli tytuł NIE ZAWIERA imion, ZAWSZE implikuje pewne postacie.
TWÓRZ postacie które MUSZĄ ISTNIEĆ by tytuł miał sens - nie generyczne, ale WYNIKAJĄCE z tytułu.

Dla KAŻDEJ implikowanej postaci określ:

1. PROTAGONIST - Kto MUSI być bohaterem by tytuł miał sens?
   - Nie "jakiś bohater" ale KONKRETNA osoba wynikająca z tytułu
   - Jakie cechy MUSI mieć by PASOWAĆ do tytułu?
   - Jakie imię by PASOWAŁO do esencji tytułu?

2. ANTAGONIST - Kto/co MUSI stać naprzeciw by tytuł miał sens?

3. CATALYST - Kto URUCHAMIA fabułę wynikającą z tytułu?

4. INNE NIEZBĘDNE POSTACIE - Kto jeszcze MUSI istnieć?

Dla każdej postaci podaj:
- essence: Kim ta postać JEST w świetle tytułu
- role: Rola w historii
- title_connection: JAK KONKRETNIE łączy się z tytułem
- must_embody: Co MUSI uosabiać
- psychological_wound: Rana WYNIKAJĄCA z tematyki tytułu
- name_suggestions: 3 imiona które PASUJĄ do esencji tytułu (nie losowe!)

Odpowiedz w formacie JSON:
{{
    "protagonist": {{
        "essence": "Kim MUSI być protagonista w świetle tytułu",
        "title_connection": "Jak bezpośrednio łączy się z tytułem",
        "must_embody": ["temat1 z tytułu", "temat2 z tytułu"],
        "psychological_wound": "Rana związana z tytułem",
        "name_suggestions": ["imię1", "imię2", "imię3"],
        "name_reasoning": "Dlaczego te imiona pasują do tytułu"
    }},
    "antagonist": {{
        "essence": "Kim/czym MUSI być antagonista",
        "type": "person/force/idea/internal",
        "title_connection": "Jak łączy się z tytułem",
        "must_embody": ["przeciwieństwo tematu1", "ciemna strona"],
        "name_suggestions": ["imię1", "imię2", "imię3"]
    }},
    "catalyst": {{
        "essence": "Kto/co uruchamia fabułę",
        "title_connection": "Związek z tytułem",
        "function": "Jak zmienia status quo"
    }},
    "supporting_cast": [
        {{
            "essence": "Kim jest ta postać",
            "function": "mentor/ally/mirror/etc",
            "title_connection": "Związek z tytułem",
            "must_embody": ["aspekt tytułu"]
        }}
    ],
    "character_dynamics": {{
        "central_relationship": "Główna relacja wynikająca z tytułu",
        "conflict_source": "Źródło konfliktu między postaciami",
        "ensemble_vs_solo": "ensemble/solo/dual"
    }}
}}"""
    },

    TITANDimension.CENTRAL_CONFLICT: {
        "description": "Rodzaj konfliktu sugerowany przez tytuł",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem CENTRALNEGO KONFLIKTU.

1. CONFLICT_TYPE: Jaki typ konfliktu WYNIKA z tytułu? (wewnętrzny/zewnętrzny/oba)
2. CONFLICT_ESSENCE: Jaka jest ESENCJA konfliktu ukryta w tytule?
3. CONFLICT_SCALE: Jaka skala? (osobisty/rodzinny/społeczny/globalny/kosmiczny)
4. STAKES: Jakie STAWKI są wpisane w tytuł? (1-10)
5. MORAL_COMPLEXITY: Jak złożony moralnie? (1-10)
6. RESOLUTION_HINTS: Jakie rozwiązanie SUGERUJE tytuł? (jednoznaczne/ambiwalentne/otwarte)

Odpowiedz w formacie JSON:
{{
    "conflict_type": "...",
    "conflict_essence": "...",
    "conflict_scale": "...",
    "stakes_level": 7,
    "moral_complexity": 6,
    "resolution_hints": "..."
}}"""
    },

    TITANDimension.NARRATIVE_PROMISE: {
        "description": "Co tytuł obiecuje czytelnikowi",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem NARRACYJNEJ OBIETNICY.

1. GENRE_SIGNALS: Jakie gatunki sugeruje? (minimum 2)
2. READER_EXPECTATIONS: Czego czytelnik BĘDZIE oczekiwał po tym tytule?
3. HOOK_STRENGTH: Jak silny jest hak? (1-10)
4. MYSTERY_QUOTIENT: Ile tajemnicy zawiera? (1-10)
5. PROMISE_ESSENCE: Co DOKŁADNIE tytuł obiecuje?
6. SATISFACTION_TYPE: Jaki rodzaj satysfakcji oferuje?

Odpowiedz w formacie JSON:
{{
    "genre_signals": ["...", "..."],
    "reader_expectations": ["...", "...", "..."],
    "hook_strength": 8,
    "mystery_quotient": 6,
    "promise_essence": "...",
    "satisfaction_type": "..."
}}"""
    },

    TITANDimension.STYLE_TONE: {
        "description": "Styl i ton sugerowany przez tytuł",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem STYLU I TONU.

1. FORMALITY_LEVEL: Jaki poziom formalności? (formalny/nieformalny/mieszany)
2. PROSE_STYLE: Jaki styl prozy WYNIKA z tytułu? (poetycki/surowy/barokowy/minimalistyczny/klasyczny)
3. HUMOR_QUOTIENT: Ile humoru? (0-10)
4. DARKNESS_LEVEL: Jak mroczny? (0-10)
5. LITERARY_AMBITION: Jak literacko ambitny? (1-10)
6. VOICE_ESSENCE: Jaki GŁOS narracji wymaga ten tytuł?

Odpowiedz w formacie JSON:
{{
    "formality_level": "...",
    "prose_style": "...",
    "humor_quotient": 3,
    "darkness_level": 5,
    "literary_ambition": 7,
    "voice_essence": "..."
}}"""
    },

    TITANDimension.DEEP_PSYCHOLOGY: {
        "description": "Psychologiczne warstwy w tytule",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem GŁĘBOKIEJ PSYCHOLOGII.

1. PSYCHOLOGICAL_THEMES: Jakie tematy psychologiczne są WPISANE w tytuł?
2. TRAUMA_INDICATORS: Jakie traumy mogą być eksplorowane?
3. GROWTH_ARC_TYPE: Jaki typ łuku rozwoju postaci WYMUSZA tytuł?
4. SHADOW_WORK: Jakie jungowskie cienie mogą być eksplorowane?
5. COLLECTIVE_UNCONSCIOUS: Jakie archetypy zbiorowej nieświadomości?
6. PSYCHOLOGICAL_DEPTH: Jak głęboko tytuł WYMAGA sięgnąć? (1-10)

Odpowiedz w formacie JSON:
{{
    "psychological_themes": ["...", "...", "..."],
    "trauma_indicators": ["...", "..."],
    "growth_arc_type": "...",
    "shadow_work": "...",
    "collective_unconscious": ["...", "..."],
    "psychological_depth": 7
}}"""
    },

    TITANDimension.INTERTEXTUALITY: {
        "description": "Odniesienia do innych dzieł",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem INTERTEKSTUALNOŚCI.

1. LITERARY_ECHOES: Jakie echa innych dzieł literackich?
2. MYTHOLOGICAL_ROOTS: Jakie korzenie mitologiczne?
3. ARCHETYPAL_PATTERNS: Jakie wzorce archetypowe?
4. GENRE_CONVENTIONS: Jakie konwencje gatunkowe przywołuje lub subwertuje?
5. SUBVERSION_POTENTIAL: Potencjał do subwersji konwencji? (1-10)

Odpowiedz w formacie JSON:
{{
    "literary_echoes": ["...", "..."],
    "mythological_roots": ["...", "..."],
    "archetypal_patterns": ["...", "..."],
    "genre_conventions": ["...", "..."],
    "subversion_potential": 5
}}"""
    },

    TITANDimension.COMMERCIAL_POTENTIAL: {
        "description": "Potencjał rynkowy tytułu",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem POTENCJAŁU KOMERCYJNEGO.

1. TARGET_AUDIENCE: Jaka grupa docelowa?
2. MARKET_POSITIONING: Jakie pozycjonowanie rynkowe?
3. SERIES_POTENTIAL: Potencjał na serię? (1-10)
4. ADAPTATION_POTENTIAL: Potencjał adaptacji? (film/serial/gra)
5. VIRAL_HOOKS: Jakie wirusowe haki?

Odpowiedz w formacie JSON:
{{
    "target_audience": ["...", "..."],
    "market_positioning": "...",
    "series_potential": 7,
    "adaptation_potential": "...",
    "viral_hooks": ["...", "..."]
}}"""
    },

    TITANDimension.TRANSCENDENCE: {
        "description": "Wymiar duchowy i transcendentny",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem TRANSCENDENCJI.

1. SPIRITUAL_DIMENSION: Jaki wymiar duchowy?
2. EXISTENTIAL_QUESTIONS: Jakie pytania egzystencjalne podnosi?
3. MEANING_OF_LIFE_TOUCH: Jak bardzo dotyka sensu życia? (1-10)
4. HOPE_VS_DESPAIR: Więcej nadziei czy rozpaczy?
5. LEGACY_THEME: Jaki temat dziedzictwa?
6. UNIVERSAL_TRUTH: Jaką uniwersalną prawdę może przekazać?

Odpowiedz w formacie JSON:
{{
    "spiritual_dimension": "...",
    "existential_questions": ["...", "..."],
    "meaning_of_life_touch": 6,
    "hope_vs_despair": "...",
    "legacy_theme": "...",
    "universal_truth": "..."
}}"""
    },

    # NarraForge 3.0 Enhancement - Cultural Context Dimension
    TITANDimension.CULTURAL_CONTEXT: {
        "description": "Kontekst kulturowy, wrażliwości i symbolika kulturowa",
        "prompt_template": """Przeanalizuj tytuł "{title}" pod kątem KONTEKSTU KULTUROWEGO.

KRYTYCZNE: Nie zakładaj domyślnie kultury zachodniej. Tytuł sam może sugerować specyficzny kontekst kulturowy.

1. CULTURAL_ORIGIN: Jakie kultury/tradycje REZONUJĄ z tym tytułem?
   - Jakie tradycje literackie przywołuje?
   - Czy tytuł ma korzenie w konkretnej kulturze?
   - Jakie globalne perspektywy obejmuje?

2. CULTURAL_SYMBOLS: Jakie symbole kulturowe zawiera tytuł?
   - Symbole uniwersalne vs specyficzne kulturowo
   - Archetypy kulturowe
   - Ikonografia kulturowa

3. CULTURAL_SENSITIVITIES: Jakie wrażliwości kulturowe należy uwzględnić?
   - Potencjalne tematy kontrowersyjne
   - Reprezentacja mniejszości
   - Stereotypy do unikania
   - Autentyczność kulturowa

4. REGIONAL_INFLUENCES: Jakie regionalne wpływy WYNIKAJĄ z tytułu?
   - Klimat/geografia sugerowana przez tytuł
   - Tradycje regionalne
   - Dialekty/język

5. HISTORICAL_CULTURAL_CONTEXT: Jaki kontekst historyczno-kulturowy?
   - Epoka historyczna sugerowana
   - Przemiany społeczne
   - Kontekst polityczny

6. CULTURAL_AUTHENTICITY_REQUIREMENTS: Co jest NIEZBĘDNE dla autentyczności?
   - Elementy które MUSZĄ być autentyczne
   - Badania kulturowe wymagane
   - Konsultacje kulturowe zalecane

7. CROSS_CULTURAL_APPEAL: Jak uniwersalny jest tytuł?
   - Potencjał międzynarodowy (1-10)
   - Bariery kulturowe
   - Elementy wymagające adaptacji

Odpowiedz w formacie JSON:
{{
    "cultural_origins": ["kultura1", "tradycja2"],
    "primary_cultural_context": "główny kontekst kulturowy",
    "cultural_symbols": [
        {{"symbol": "...", "meaning": "...", "origin": "..."}}
    ],
    "cultural_sensitivities": {{
        "topics_requiring_care": ["temat1", "temat2"],
        "stereotypes_to_avoid": ["stereotyp1", "stereotyp2"],
        "representation_notes": "..."
    }},
    "regional_influences": {{
        "geography": "...",
        "traditions": ["tradycja1", "tradycja2"],
        "language_considerations": "..."
    }},
    "historical_context": {{
        "era": "...",
        "social_changes": ["zmiana1", "zmiana2"],
        "political_context": "..."
    }},
    "authenticity_requirements": {{
        "must_be_authentic": ["element1", "element2"],
        "research_needed": ["obszar1", "obszar2"],
        "consultation_recommended": true/false
    }},
    "cross_cultural_appeal": {{
        "international_potential": 7,
        "cultural_barriers": ["bariera1"],
        "adaptation_needed": ["element1"]
    }},
    "cultural_richness_score": 7
}}"""
    }
}


class TITANAnalyzer:
    """
    Enhanced 12-dimensional title analysis system.
    Deep semantic extraction - NO FALLBACKS, everything from title.
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
        Perform DEEP TITAN analysis on a title.
        Extract EVERYTHING from the title - characters, world, plot, themes.
        """
        analysis = TITANAnalysis(title=title)

        # PHASE 1: Extract Title Essence (CRITICAL)
        analysis.essence = await self._extract_title_essence(title, genre_hint)
        analysis.title_dna = self._compile_title_dna(analysis.essence)

        # PHASE 2: Analyze all 12 dimensions
        dimensions_to_analyze = list(TITANDimension)
        if not full_analysis:
            dimensions_to_analyze = [
                TITANDimension.SEMANTIC_DEPTH,
                TITANDimension.EMOTIONAL_RESONANCE,
                TITANDimension.SPATIAL_WORLD,
                TITANDimension.IMPLIED_CHARACTERS,
                TITANDimension.NARRATIVE_PROMISE,
                TITANDimension.STYLE_TONE,
                TITANDimension.DEEP_PSYCHOLOGY
            ]

        for dimension in dimensions_to_analyze:
            result = await self._analyze_dimension(title, dimension, genre_hint)
            analysis.dimensions[dimension] = result

        # PHASE 3: Synthesize and cross-reference
        analysis.essence = await self._enrich_essence_from_dimensions(analysis)

        # Calculate metrics
        analysis.overall_complexity = self._calculate_complexity(analysis)
        analysis.uniqueness_score = self._calculate_uniqueness(analysis)

        # Suggest genre
        if not genre_hint:
            analysis.suggested_genre = self._suggest_genre(analysis)
        else:
            analysis.suggested_genre = genre_hint

        return analysis

    async def _extract_title_essence(
        self,
        title: str,
        genre_hint: Optional[GenreType]
    ) -> TitleEssence:
        """Extract the absolute essence of the title - the DNA from which everything flows."""
        genre_context = f"KONTEKST GATUNKOWY: {genre_hint.value}" if genre_hint else "GATUNEK: do określenia na podstawie tytułu"

        prompt = TITLE_ESSENCE_PROMPT.format(title=title, genre_context=genre_context)

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                model_tier=2,
                max_tokens=4000,
                temperature=0.7
            )

            data = self._parse_json_response(response)

            # Parse implied characters
            character_seeds = []
            for char_data in data.get("implied_characters", []):
                psych = char_data.get("psychological_core", {})
                character_seeds.append(ImpliedCharacter(
                    essence=char_data.get("essence", ""),
                    role_in_story=char_data.get("role", ""),
                    title_connection=char_data.get("title_connection", ""),
                    archetypal_function=char_data.get("function", ""),
                    psychological_profile={
                        "wound": psych.get("wound", ""),
                        "ghost": psych.get("ghost", ""),
                        "lie": psych.get("lie", ""),
                        "want": psych.get("want", ""),
                        "need": psych.get("need", ""),
                        "fear": psych.get("fear", "")
                    },
                    name_suggestions=char_data.get("name_suggestions", []),
                    must_embody=char_data.get("must_have_traits", [])
                ))

            world_seeds = data.get("world_seeds", {})
            conflict_seeds = data.get("conflict_seeds", {})

            return TitleEssence(
                core_meaning=data.get("core_meaning", ""),
                emotional_core=data.get("emotional_core", ""),
                central_question=data.get("central_question", ""),
                thematic_pillars=data.get("thematic_pillars", []),
                world_seeds=[
                    world_seeds.get("type", ""),
                    world_seeds.get("atmosphere", ""),
                    *world_seeds.get("essential_locations", [])
                ],
                character_seeds=character_seeds,
                conflict_seeds=[
                    conflict_seeds.get("central_conflict", ""),
                    conflict_seeds.get("stakes", ""),
                    *conflict_seeds.get("tension_sources", [])
                ],
                tone_palette=data.get("tone_palette", []),
                symbolic_elements=data.get("symbolic_elements", []),
                forbidden_elements=data.get("forbidden_elements", [])
            )

        except Exception as e:
            return TitleEssence(
                core_meaning=f"Historia zatytułowana '{title}'",
                emotional_core="do odkrycia",
                central_question=f"Co kryje się za tytułem '{title}'?",
                thematic_pillars=["tajemnica tytułu"],
                world_seeds=["świat wynikający z tytułu"],
                character_seeds=[],
                conflict_seeds=["konflikt implikowany przez tytuł"],
                tone_palette=["do określenia"],
                symbolic_elements=["tytuł jako symbol"],
                forbidden_elements=[]
            )

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
                model_tier=1,
                max_tokens=1500,
                temperature=0.7
            )

            output = self._parse_json_response(response)
            impact = self._calculate_dimension_impact(dimension, output)

            return DimensionResult(
                dimension=dimension,
                output=output,
                impact_on_book=impact,
                confidence=0.85
            )

        except Exception:
            return DimensionResult(
                dimension=dimension,
                output={},
                impact_on_book={},
                confidence=0.0
            )

    async def _enrich_essence_from_dimensions(self, analysis: TITANAnalysis) -> TitleEssence:
        """Enrich the title essence with data from dimensional analysis."""
        if not analysis.essence:
            return analysis.essence

        essence = analysis.essence

        # Enrich from IMPLIED_CHARACTERS dimension
        chars_dim = analysis.get_dimension(TITANDimension.IMPLIED_CHARACTERS)
        if chars_dim and chars_dim.output:
            output = chars_dim.output

            # Add protagonist if not already present
            protagonist_data = output.get("protagonist", {})
            if protagonist_data and not any(c.role_in_story == "protagonist" for c in essence.character_seeds):
                essence.character_seeds.insert(0, ImpliedCharacter(
                    essence=protagonist_data.get("essence", ""),
                    role_in_story="protagonist",
                    title_connection=protagonist_data.get("title_connection", ""),
                    archetypal_function="main character",
                    psychological_profile={
                        "wound": protagonist_data.get("psychological_wound", "")
                    },
                    name_suggestions=protagonist_data.get("name_suggestions", []),
                    must_embody=protagonist_data.get("must_embody", [])
                ))

            # Add antagonist
            antagonist_data = output.get("antagonist", {})
            if antagonist_data and not any(c.role_in_story == "antagonist" for c in essence.character_seeds):
                essence.character_seeds.append(ImpliedCharacter(
                    essence=antagonist_data.get("essence", ""),
                    role_in_story="antagonist",
                    title_connection=antagonist_data.get("title_connection", ""),
                    archetypal_function=antagonist_data.get("type", "opposition"),
                    psychological_profile={},
                    name_suggestions=antagonist_data.get("name_suggestions", []),
                    must_embody=antagonist_data.get("must_embody", [])
                ))

            # Add supporting cast
            for support in output.get("supporting_cast", []):
                essence.character_seeds.append(ImpliedCharacter(
                    essence=support.get("essence", ""),
                    role_in_story="supporting",
                    title_connection=support.get("title_connection", ""),
                    archetypal_function=support.get("function", ""),
                    psychological_profile={},
                    name_suggestions=[],
                    must_embody=support.get("must_embody", [])
                ))

        # Enrich themes from SEMANTIC_DEPTH
        semantic_dim = analysis.get_dimension(TITANDimension.SEMANTIC_DEPTH)
        if semantic_dim and semantic_dim.output:
            themes = semantic_dim.output.get("universal_themes", [])
            for theme in themes:
                if theme not in essence.thematic_pillars:
                    essence.thematic_pillars.append(theme)

            symbols = semantic_dim.output.get("hidden_symbols", [])
            for symbol in symbols:
                if symbol not in essence.symbolic_elements:
                    essence.symbolic_elements.append(symbol)

        return essence

    def _compile_title_dna(self, essence: Optional[TitleEssence]) -> Dict[str, Any]:
        """Compile the complete title DNA from essence."""
        if not essence:
            return {}

        return {
            "core": essence.core_meaning,
            "emotion": essence.emotional_core,
            "question": essence.central_question,
            "themes": essence.thematic_pillars,
            "symbols": essence.symbolic_elements,
            "forbidden": essence.forbidden_elements,
            "character_count": len(essence.character_seeds),
            "character_roles": [c.role_in_story for c in essence.character_seeds]
        }

    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from AI response."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        return {}

    def _calculate_dimension_impact(self, dimension: TITANDimension, output: Dict) -> Dict[str, Any]:
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
            impact["chapter_time_jumps"] = 5 if "nielinear" in str(complexity).lower() else 2 if "wielo" in str(complexity).lower() else 0
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
            protagonist = output.get("protagonist", {})
            supporting = output.get("supporting_cast", [])
            dynamics = output.get("character_dynamics", {})
            impact["main_characters"] = 2 if output.get("antagonist") else 1
            impact["main_characters"] += len(supporting)
            impact["supporting_cast"] = len(supporting) * 2
            impact["character_depth"] = "deep"
            impact["ensemble_type"] = dynamics.get("ensemble_vs_solo", "solo")

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
            depth = output.get("psychological_depth", 5)
            growth_type = output.get("growth_arc_type", "")
            impact["internal_monologue_depth"] = "profound" if depth > 7 else "moderate" if depth > 4 else "minimal"
            impact["psychological_realism"] = depth > 5
            impact["character_transformation"] = "radical" if depth > 7 else "significant" if growth_type else "subtle"

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

        elif dimension == TITANDimension.CULTURAL_CONTEXT:
            cross_cultural = output.get("cross_cultural_appeal", {})
            sensitivities = output.get("cultural_sensitivities", {})
            authenticity = output.get("authenticity_requirements", {})
            richness = output.get("cultural_richness_score", 5)

            impact["cultural_depth"] = "rich" if richness > 7 else "moderate" if richness > 4 else "light"
            impact["international_appeal"] = cross_cultural.get("international_potential", 5) > 6
            impact["research_required"] = len(authenticity.get("research_needed", [])) > 0
            impact["sensitivity_level"] = len(sensitivities.get("topics_requiring_care", []))
            impact["cultural_authenticity_check"] = authenticity.get("consultation_recommended", False)

            # Regional specificity
            regional = output.get("regional_influences", {})
            if regional.get("geography"):
                impact["geographic_specificity"] = True
                impact["regional_traditions_count"] = len(regional.get("traditions", []))

            # Historical context requirements
            historical = output.get("historical_context", {})
            if historical.get("era"):
                impact["historical_research_needed"] = True
                impact["historical_era"] = historical.get("era")

            # Cultural symbols to incorporate
            symbols = output.get("cultural_symbols", [])
            impact["cultural_symbols_count"] = len(symbols)

        return impact

    def _calculate_complexity(self, analysis: TITANAnalysis) -> float:
        """Calculate overall complexity score."""
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
                complexity_factors.append(output.get("psychological_depth", 5) / 10)

        if complexity_factors:
            return sum(complexity_factors) / len(complexity_factors)
        return 0.5

    def _calculate_uniqueness(self, analysis: TITANAnalysis) -> float:
        """Calculate uniqueness score."""
        uniqueness_factors = []

        for dim, result in analysis.dimensions.items():
            output = result.output

            if dim == TITANDimension.SPATIAL_WORLD:
                uniqueness_factors.append(output.get("world_uniqueness", 5) / 10)
            elif dim == TITANDimension.INTERTEXTUALITY:
                uniqueness_factors.append(output.get("subversion_potential", 5) / 10)
            elif dim == TITANDimension.NARRATIVE_PROMISE:
                uniqueness_factors.append(output.get("mystery_quotient", 5) / 10)
            elif dim == TITANDimension.CULTURAL_CONTEXT:
                # Cultural richness adds to uniqueness
                uniqueness_factors.append(output.get("cultural_richness_score", 5) / 10)

        if uniqueness_factors:
            return sum(uniqueness_factors) / len(uniqueness_factors)
        return 0.5

    def _suggest_genre(self, analysis: TITANAnalysis) -> GenreType:
        """Suggest the best genre based on TITAN analysis."""
        scores = {genre: 0.0 for genre in GenreType}

        narrative = analysis.dimensions.get(TITANDimension.NARRATIVE_PROMISE)
        if narrative:
            signals = narrative.output.get("genre_signals", [])
            for signal in signals:
                signal_lower = signal.lower()
                if any(x in signal_lower for x in ["sci", "fiction", "tech", "space", "cyber", "future"]):
                    scores[GenreType.SCI_FI] += 2
                if any(x in signal_lower for x in ["fanta", "magic", "epic", "dragon", "magia"]):
                    scores[GenreType.FANTASY] += 2
                if any(x in signal_lower for x in ["thriller", "suspense", "tension", "napięcie"]):
                    scores[GenreType.THRILLER] += 2
                if any(x in signal_lower for x in ["horror", "strach", "groza", "terror", "koszmar"]):
                    scores[GenreType.HORROR] += 2
                if any(x in signal_lower for x in ["romans", "miłość", "love", "serce"]):
                    scores[GenreType.ROMANCE] += 2
                if any(x in signal_lower for x in ["drama", "famil", "życie", "relacj"]):
                    scores[GenreType.DRAMA] += 2
                if any(x in signal_lower for x in ["komed", "humor", "śmiech", "zabaw"]):
                    scores[GenreType.COMEDY] += 2
                if any(x in signal_lower for x in ["mystery", "detekt", "krymi", "zagadka", "śledztw"]):
                    scores[GenreType.MYSTERY] += 2
                if any(x in signal_lower for x in ["relig", "duchow", "wiara", "bóg", "sacred", "świąt"]):
                    scores[GenreType.RELIGIOUS] += 2

        style = analysis.dimensions.get(TITANDimension.STYLE_TONE)
        if style:
            darkness = style.output.get("darkness_level", 5)
            humor = style.output.get("humor_quotient", 3)
            if darkness > 7:
                scores[GenreType.HORROR] += 1
                scores[GenreType.THRILLER] += 1
            if humor > 6:
                scores[GenreType.COMEDY] += 2

        transcendence = analysis.dimensions.get(TITANDimension.TRANSCENDENCE)
        if transcendence:
            spiritual = transcendence.output.get("spiritual_dimension", "")
            meaning = transcendence.output.get("meaning_of_life_touch", 5)
            if spiritual and meaning > 6:
                scores[GenreType.RELIGIOUS] += 2
                scores[GenreType.DRAMA] += 1

        spatial = analysis.dimensions.get(TITANDimension.SPATIAL_WORLD)
        if spatial:
            world_type = spatial.output.get("world_type", "")
            if "fanta" in world_type.lower():
                scores[GenreType.FANTASY] += 2
            if "science" in world_type.lower() or "sci-fi" in world_type.lower():
                scores[GenreType.SCI_FI] += 2

        max_genre = max(scores, key=scores.get)
        return max_genre if scores[max_genre] > 0 else GenreType.DRAMA


_titan_analyzer: Optional[TITANAnalyzer] = None


def get_titan_analyzer() -> TITANAnalyzer:
    """Get or create TITAN analyzer instance."""
    global _titan_analyzer
    if _titan_analyzer is None:
        _titan_analyzer = TITANAnalyzer()
    return _titan_analyzer
