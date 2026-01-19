"""
Typy danych dla NARRA_FORGE - Uniwersalny System Generowania Narracji

Wszystkie podstawowe dataclass i enum dla całego systemu.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime


# ==================== ENUMS ====================

class NarrativeForm(Enum):
    """Forma narracyjna - automatycznie determinuje długość i strukturę"""
    SHORT_STORY = "short_story"          # 5,000-15,000 słów
    NOVELLA = "novella"                  # 15,000-40,000 słów
    NOVEL = "novel"                      # 40,000-120,000 słów
    EPIC_SAGA = "epic_saga"              # 120,000+ słów (wielotomowa)
    FLASH_FICTION = "flash_fiction"      # <1,000 słów
    AUTO = "auto"                        # System sam określi na podstawie treści


class Genre(Enum):
    """Gatunek literacki - wpływa na styl, ton i konwencje"""
    FANTASY = "fantasy"
    SCI_FI = "sci_fi"
    HORROR = "horror"
    THRILLER = "thriller"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    LITERARY = "literary"
    HISTORICAL = "historical"
    DYSTOPIA = "dystopia"
    URBAN_FANTASY = "urban_fantasy"
    SPACE_OPERA = "space_opera"
    CYBERPUNK = "cyberpunk"
    NOIR = "noir"
    PSYCHOLOGICAL = "psychological"
    DRAMA = "drama"
    ADVENTURE = "adventure"
    HYBRID = "hybrid"                    # Mieszanka gatunków
    AUTO = "auto"                        # System sam określi


class Tone(Enum):
    """Ton narracyjny"""
    DARK = "dark"                        # Mroczny
    LIGHT = "light"                      # Lekki
    POETIC = "poetic"                    # Poetycki
    DYNAMIC = "dynamic"                  # Dynamiczny
    PHILOSOPHICAL = "philosophical"      # Filozoficzny
    HUMOROUS = "humorous"                # Humorystyczny
    NOIR = "noir"                        # Noir
    LYRICAL = "lyrical"                  # Liryczny
    AUTO = "auto"                        # System sam określi


class POVStyle(Enum):
    """Styl narracji (punkt widzenia)"""
    FIRST_PERSON = "first_person"        # 1. osoba
    THIRD_LIMITED = "third_limited"      # 3. osoba ograniczona
    THIRD_OMNISCIENT = "third_omniscient" # 3. osoba wszechwiedzący
    MULTIPLE_POV = "multiple_pov"        # Wieloperspektywiczny
    AUTO = "auto"                        # System sam wybierze


class PipelineStage(Enum):
    """10 etapów pipeline'u produkcji narracji"""
    BRIEF_INTERPRETATION = 1
    WORLD_ARCHITECTURE = 2
    CHARACTER_ARCHITECTURE = 3
    NARRATIVE_STRUCTURE = 4
    SEGMENT_PLANNING = 5
    SEQUENTIAL_GENERATION = 6
    COHERENCE_VALIDATION = 7
    LANGUAGE_STYLIZATION = 8
    EDITORIAL_REVIEW = 9
    FINAL_OUTPUT = 10


# ==================== PROJECT BRIEF ====================

@dataclass
class ProjectBrief:
    """
    Rezultat Etapu 1: Interpretacja zlecenia użytkownika
    Zawiera pełną interpretację wymagań w formie strukturalnej
    """
    # Podstawowe parametry
    form: NarrativeForm
    genre: Genre
    tone: Tone
    pov_style: POVStyle

    # Skala i zakres
    target_word_count: int                # Docelowa liczba słów
    target_chapter_count: int             # Szacowana liczba rozdziałów

    # Główna koncepcja
    core_concept: str                     # Esencja historii (2-5 zdań)
    central_conflict: str                 # Główny konflikt
    thematic_question: str                # Pytanie tematyczne

    # Świat i setting
    world_type: str                       # Typ świata (współczesny, fantasy, etc.)
    setting_scale: str                    # Skala (miasto, planeta, galaktyka)

    # Postacie
    protagonist_archetype: str            # Archetyp bohatera
    antagonist_type: str                  # Typ antagonisty
    supporting_count: int                 # Liczba postaci drugoplanowych

    # Struktura
    narrative_structure: str              # Typ struktury (3-act, hero's journey, etc.)
    subplot_count: int                    # Liczba wątków pobocznych

    # Metadane
    project_id: str = field(default_factory=lambda: f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    original_request: str = ""            # Oryginalny request użytkownika
    special_requirements: List[str] = field(default_factory=list)

    # Potencjał rozwojowy
    is_expandable: bool = True            # Czy może być rozwijane (seria, saga)
    universe_potential: str = "medium"    # low/medium/high - potencjał na uniwersum


# ==================== WORLD BIBLE ====================

@dataclass
class WorldBible:
    """
    Rezultat Etapu 2: Architektura Świata
    Kompletna definicja świata jako IP (Intellectual Property)
    """
    # Identyfikacja
    world_id: str
    name: str
    genre: Genre

    # Rdzenna esencja świata
    core_concept: str                     # 1-2 zdaniowa esencja
    existential_theme: str                # Dlaczego ten świat istnieje (filozofia)
    central_mystery: str                  # Główna tajemnica/paradoks świata

    # Prawa rzeczywistości
    laws_of_reality: Dict[str, Any]       # Jak działa ten świat
    boundaries: Dict[str, Any]            # Granice (przestrzeń, czas, wymiary)
    anomalies: List[str]                  # Celowe wyjątki od reguł

    # Geografia i lokacje (minimum 5)
    locations: List[Dict[str, Any]]       # Każda z nazwą, opisem, znaczeniem

    # Systemy (magia/technologia/społeczeństwo)
    primary_system: Dict[str, Any]        # Główny system (magia/tech/etc.)
    system_limitations: List[str]         # Ograniczenia systemu
    system_consequences: List[str]        # Konsekwencje użycia

    # Struktura społeczna
    factions: List[Dict[str, Any]]        # Grupy społeczne/frakcje (min 3)

    # Historia świata
    historical_events: List[Dict[str, Any]] # Kluczowe wydarzenia (3-5)
    current_state: str                    # Obecny stan świata

    # Unikalne elementy
    unique_elements: List[str]            # Co odróżnia TEN świat (min 3)

    # Konflikt nadrzędny
    core_conflict: str                    # Główny konflikt świata
    conflict_sources: List[str]           # Źródła konfliktów

    # System archetypów
    archetype_system: Dict[str, Any]      # Archetypy ról w tym świecie

    # Metadane
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    is_active: bool = True


# ==================== CHARACTER ====================

@dataclass
class Character:
    """
    Rezultat Etapu 3: Architektura Postaci
    Postać jako PROCES psychologiczny, nie statyczny opis
    """
    # Identyfikacja
    character_id: str
    name: str
    role: str                             # protagonist/antagonist/supporting

    # Rdzeń psychologiczny
    conscious_goal: str                   # Co postać MYŚLI, że chce
    unconscious_need: str                 # Czego NAPRAWDĘ potrzebuje
    ghost_trauma: str                     # Trauma z przeszłości definiująca postać
    internal_conflict: str                # Wewnętrzny konflikt wartości
    fatal_flaw: str                       # Wada, która może ją zniszczyć

    # Charakterystyka fizyczna i społeczna
    age: int
    physical_description: str
    social_status: str
    origin: str                           # Skąd pochodzi

    # Umiejętności i ograniczenia
    skills: List[str]                     # 3-5 umiejętności Z OGRANICZENIAMI
    cognitive_limits: List[str]           # Czego nie może pojąć

    # Sposób komunikacji
    speech_pattern: str                   # Jak mówi (dialekt, słownictwo, maniery)
    internal_voice: str                   # Jak myśli (styl wewnętrznych monologów)

    # Relacje
    relationships: Dict[str, Dict[str, Any]] # character_id -> {nature, history, dynamic}

    # Motywacja i stawka
    story_goal: str                       # Konkretny, mierzalny cel w fabule
    stakes: str                           # Co straci, jeśli nie osiągnie celu

    # Arka transformacji
    arc_start: str                        # Kim jest na początku
    arc_midpoint: str                     # Kluczowa zmiana w środku
    arc_end: str                          # Kim będzie na końcu
    transformation_catalyst: str          # Co musi się wydarzyć, żeby się zmienił

    # Dynamika (postać jako proces)
    internal_trajectory: str              # Dokąd zmierza psychologicznie
    contradictions: List[str]             # Wewnętrzne sprzeczności
    evolution_capacity: float             # Zdolność zmiany (0.0-1.0)
    evolution_history: List[Dict[str, Any]] = field(default_factory=list) # Historia zmian

    # Funkcja tematyczna
    thematic_function: str                # Co reprezentuje w centralnym temacie

    # Dla antagonisty (jeśli role == "antagonist")
    philosophy: Optional[str] = None      # Światopogląd (dlaczego ma rację Z JEGO perspektywy)
    methods: Optional[List[str]] = None   # Jakie środki jest gotów użyć
    line_wont_cross: Optional[str] = None # Czego NIE zrobi (granica moralności)
    human_element: Optional[str] = None   # Co czyni go ludzkim, nie karykaturą

    # Metadane
    created_at: datetime = field(default_factory=datetime.now)
    world_id: Optional[str] = None


# ==================== NARRATIVE STRUCTURE ====================

@dataclass
class NarrativeStructure:
    """
    Rezultat Etapu 4: Struktura Narracyjna
    Wielowarstwowa struktura fabularna
    """
    # Identyfikacja
    structure_id: str
    structure_type: str                   # 3-act, 7-point, hero's journey, etc.

    # 7-Point Story Structure
    hook: str                             # Status quo
    plot_point_1: str                     # Incydent rozpoczynający
    pinch_point_1: str                    # Pierwsza komplikacja
    midpoint: str                         # Fałszywe zwycięstwo/porażka
    pinch_point_2: str                    # Druga komplikacja
    plot_point_3: str                     # Moment decyzji
    resolution: str                       # Rozwiązanie

    # Subploty (2-4)
    subplots: List[Dict[str, Any]]        # Każdy z własnym arc i tematyczną funkcją

    # Temat
    central_theme: str                    # O czym NAPRAWDĘ jest historia
    thematic_question: str                # Pytanie dla czytelnika
    thesis: str                           # Co historia twierdzi o temacie

    # Pacing
    pacing_map: List[Dict[str, Any]]      # Mapa tempa dla sekcji

    # Plot twists
    plot_twists: List[Dict[str, Any]]     # Zwroty akcji z lokacją i foreshadowingiem

    # Metadane
    project_id: str
    created_at: datetime = field(default_factory=datetime.now)


# ==================== NARRATIVE SEGMENT ====================

@dataclass
class NarrativeSegment:
    """
    Rezultat Etapu 5: Segment (rozdział/scena)
    Każdy segment z precyzyjną funkcją narracyjną
    """
    # Identyfikacja
    segment_id: str
    segment_number: int
    title: Optional[str] = None

    # Cel i funkcja
    goal: str                             # Co musi się wydarzyć
    narrative_function: str               # exposition/rising_action/climax/etc.
    narrative_weight: float               # Ważność (0.0-1.0)

    # POV
    pov_character: str                    # Kto jest narratorem
    pov_rationale: str                    # Dlaczego ta perspektywa

    # Struktura scen
    scenes: List[Dict[str, Any]]          # 2-4 sceny z celami i kluczowymi momentami

    # Łuk emocjonalny
    emotional_arc: str                    # start: [emocja] → end: [emocja]
    tone: str                             # Ton emocjonalny rozdziału

    # Worldbuilding
    worldbuilding_elements: List[str]     # Nowe elementy świata do wprowadzenia

    # Zakończenie
    closing_hook: str                     # Jak kończymy (hook dla następnego)

    # Rozwój tematyczny
    theme_development: str                # Jak rozwija główny temat

    # Docelowa długość
    target_word_count: int                # Szacowana długość

    # Wygenerowana treść (wypełniane w Etapie 6)
    content: str = ""
    actual_word_count: int = 0

    # Połączenia
    involved_characters: List[str] = field(default_factory=list)
    world_impact: List[str] = field(default_factory=list)

    # Metadane
    project_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)


# ==================== VALIDATION REPORT ====================

@dataclass
class CoherenceReport:
    """
    Rezultat Etapu 7: Raport walidacji koherencji
    """
    # Ogólny wynik
    overall_score: float                  # 0.0-1.0
    passed: bool                          # Czy przeszedł próg minimalny

    # Szczegółowe wyniki
    character_consistency: float          # Spójność postaci
    world_consistency: float              # Spójność świata
    plot_consistency: float               # Spójność fabuły
    language_consistency: float           # Spójność językowa
    timeline_consistency: float           # Spójność czasowa

    # Znalezione problemy
    issues: List[Dict[str, Any]]          # type, severity, description, location, fix

    # Zalecenia
    recommendations: List[str]

    # Metadane
    project_id: str
    validated_at: datetime = field(default_factory=datetime.now)


# ==================== GENERATION RESULT ====================

@dataclass
class GenerationResult:
    """
    Rezultat Etapu 10: Finalne wyjście produkcji
    """
    # Status
    success: bool
    project_id: str

    # Brief i metadane
    brief: ProjectBrief
    world: WorldBible
    characters: List[Character]
    structure: NarrativeStructure

    # Wygenerowana narracja
    segments: List[NarrativeSegment]
    full_text: str                        # Pełny tekst

    # Statystyki
    total_word_count: int
    total_chapters: int
    generation_time_seconds: float

    # Jakość
    coherence_report: CoherenceReport
    quality_score: float                  # Łączny wynik jakości

    # Pliki wyjściowe
    output_files: Dict[str, str]          # text_file, audiobook_file, metadata_file, etc.

    # Ekspansja
    expansion_data: Dict[str, Any]        # Dane do kontynuacji (sequel, prequels, etc.)

    # Błędy (jeśli success=False)
    errors: List[str] = field(default_factory=list)

    # Metadane
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "3.0.0"


# ==================== MODEL CONFIG ====================

@dataclass
class ModelConfig:
    """Konfiguracja dla konkretnego modelu LLM"""
    model_name: str                       # np. "gpt-4-turbo", "claude-opus-4.5"
    provider: str                         # "openai", "anthropic", "local"
    api_key_env: str                      # Nazwa zmiennej środowiskowej z kluczem

    # Parametry generacji
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9

    # Limity i koszty
    cost_per_1k_tokens: float = 0.0
    max_requests_per_minute: int = 100

    # Możliwości
    supports_long_context: bool = True
    max_context_length: int = 128000
    supports_json_mode: bool = True

    # Preferowane zastosowania
    best_for: List[str] = field(default_factory=list) # ["analysis", "generation", "validation"]


# ==================== MEMORY TYPES ====================

@dataclass
class MemoryItem:
    """Pojedynczy element pamięci"""
    memory_id: str
    memory_type: str                      # structural/semantic/evolutionary
    content: Dict[str, Any]
    world_id: Optional[str] = None
    project_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    relevance_score: float = 1.0


# ==================== REVISION TYPES ====================

@dataclass
class RevisionSnapshot:
    """Snapshot stanu dla systemu rewizji"""
    snapshot_id: str
    project_id: str
    stage: PipelineStage
    version: int
    data: Dict[str, Any]                  # Pełny stan na tym etapie
    created_at: datetime = field(default_factory=datetime.now)
