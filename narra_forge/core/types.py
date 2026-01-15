"""
Podstawowe definicje typów dla systemu NARRA_FORGE.

Ten moduł zawiera wszystkie kluczowe typy danych używane w całym systemie:
- Formy narracyjne i gatunki
- Biblie światów (WorldBible)
- Definicje postaci jako procesów
- Segmenty narracyjne
- Kontekst produkcji
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


class NarrativeForm(Enum):
    """Forma narracyjna / długość utworu."""
    SHORT_STORY = "short_story"   # Opowiadanie (do 10000 słów)
    NOVELLA = "novella"           # Nowela (10000-40000 słów)
    NOVEL = "novel"               # Powieść (40000-120000 słów)
    EPIC_SAGA = "epic_saga"       # Saga epicka (wielotomowa)


class Genre(Enum):
    """Gatunki literackie."""
    FANTASY = "fantasy"           # Fantasy
    SCI_FI = "sci_fi"            # Science fiction
    HORROR = "horror"            # Horror
    THRILLER = "thriller"        # Thriller
    MYSTERY = "mystery"          # Kryminał/tajemnica
    LITERARY = "literary"        # Proza literacka
    HISTORICAL = "historical"    # Powieść historyczna
    ROMANCE = "romance"          # Romans
    HYBRID = "hybrid"            # Hybrydowy (mieszanka gatunków)


class PipelineStage(Enum):
    """10-etapowy pipeline produkcji narracji."""
    BRIEF_INTERPRETATION = 1      # Interpretacja zlecenia
    WORLD_ARCHITECTURE = 2        # Architektura świata
    CHARACTER_ARCHITECTURE = 3    # Architektura postaci
    NARRATIVE_STRUCTURE = 4       # Struktura narracyjna
    SEGMENT_PLANNING = 5          # Planowanie segmentów
    SEQUENTIAL_GENERATION = 6     # Generacja sekwencyjna
    COHERENCE_CONTROL = 7         # Kontrola koherencji
    LANGUAGE_STYLIZATION = 8      # Stylizacja językowa
    EDITORIAL_REVIEW = 9          # Redakcja wydawnicza
    FINAL_OUTPUT = 10             # Finalne wyjście


class MemoryType(Enum):
    """Typy pamięci w potrójnym systemie pamięciowym."""
    STRUCTURAL = "structural"      # Strukturalna: światy, postacie, reguły
    SEMANTIC = "semantic"          # Semantyczna: wydarzenia, motywy, relacje
    EVOLUTIONARY = "evolutionary"  # Ewolucyjna: zmiany w czasie


@dataclass
class WorldBible:
    """
    Kompletna definicja świata narracyjnego - kontener IP.

    Biblia Świata to pełna specyfikacja uniwersum narracyjnego,
    zawierająca prawa rzeczywistości, granice, anomalie i temat egzystencjalny.
    Każdy świat jest traktowany jako intelektualna własność (IP).
    """
    world_id: str                     # Unikalny identyfikator świata
    name: str                         # Nazwa świata
    created_at: datetime              # Data utworzenia

    # Podstawowa definicja świata
    laws_of_reality: Dict[str, Any]   # Prawa fizyczne, magiczne, technologiczne
    boundaries: Dict[str, Any]        # Granice przestrzenne, czasowe, wymiarowe
    anomalies: List[str]              # Wyjątki od reguł

    # Meta-informacje
    core_conflict: str                # Nadrzędny konflikt świata
    existential_theme: str            # Dlaczego ten świat istnieje narracyjnie
    archetype_system: Dict[str, Any]  # System archetypów specyficznych dla świata

    # Śledzenie ewolucji
    timeline: List[Dict[str, Any]]    # Wydarzenia historyczne
    current_state: Dict[str, Any]     # Aktualny stan świata

    # Relacje międzyświatowe
    related_worlds: List[str] = field(default_factory=list)  # Powiązane światy
    isolation_level: str = "isolated"  # isolated, connected, permeable


@dataclass
class Character:
    """
    Postać jako PROCES, nie statyczny byt.

    KLUCZOWE: Postacie są dynamicznymi procesami psychologicznymi,
    nie opisami. Mają wewnętrzne trajektorie, sprzeczności i zdolność ewolucji.
    """
    character_id: str                 # Unikalny identyfikator postaci
    name: str                         # Imię postaci
    world_id: str                     # ID świata, do którego należy

    # Tożsamość podstawowa
    internal_trajectory: str          # Wewnętrzny łuk postaci (dokąd zmierza psychologicznie)
    contradictions: List[str]         # Wewnętrzne konflikty i sprzeczności
    cognitive_limits: List[str]       # Czego nie może zrozumieć/dostrzec
    evolution_capacity: float         # 0.0-1.0: oporność na zmiany vs adaptacyjność

    # Model psychologiczny
    motivations: List[str]            # Co nią/nim kieruje
    fears: List[str]                  # Czego się boi
    blind_spots: List[str]            # Martwe punkty poznawcze

    # Relacje
    relationships: Dict[str, Dict[str, Any]]  # character_id -> dane relacji

    # Śledzenie stanu
    current_state: Dict[str, Any]     # Aktualny stan psychiczny i fizyczny
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)  # Historia ewolucji


@dataclass
class NarrativeSegment:
    """
    Pojedynczy segment narracyjny (rozdział/scena/sekwencja).

    Każdy segment ma określoną funkcję narracyjną i wpływ na świat.
    """
    segment_id: str                   # ID segmentu
    order: int                        # Kolejność w narracji

    # Funkcjonalność
    narrative_function: str           # Funkcja narracyjna segmentu
    narrative_weight: float           # Waga/ważność (0.0-1.0)
    world_impact: List[str]           # Jak zmienia świat

    # Treść
    content: str                      # Wygenerowana treść segmentu
    involved_characters: List[str]    # Zaangażowane postacie
    location: str                     # Lokalizacja
    timestamp: Optional[str] = None   # Znacznik czasowy w świecie

    # Meta
    generated_at: datetime = field(default_factory=datetime.now)  # Kiedy wygenerowano
    validated: bool = False           # Czy przeszedł walidację


@dataclass
class ProjectBrief:
    """
    Interpretacja początkowego zlecenia.

    Zawiera wszystkie wymagania projektu narracyjnego.
    """
    form: NarrativeForm               # Forma narracyjna
    genre: Genre                      # Gatunek
    world_scale: str                  # Skala: intimate, regional, global, cosmic
    expansion_potential: str          # Potencjał: one_shot, series, universe

    # Dodatkowe wymagania
    target_audience: Optional[str] = None        # Grupa docelowa
    length_target: Optional[int] = None          # Przybliżona liczba słów
    special_requirements: List[str] = field(default_factory=list)  # Specjalne wymagania

    # Kierunek kreatywny
    thematic_focus: List[str] = field(default_factory=list)        # Tematy przewodnie
    stylistic_preferences: Dict[str, Any] = field(default_factory=dict)  # Preferencje stylistyczne


@dataclass
class ProductionContext:
    """
    Kompletny kontekst produkcji narracji.

    Przechowuje cały stan produkcji przez wszystkie etapy pipeline'u.
    """
    project_id: str                   # ID projektu
    brief: ProjectBrief               # Brief projektu
    world: WorldBible                 # Świat narracji
    characters: Dict[str, Character]  # Postacie (character_id -> Character)
    segments: List[NarrativeSegment]  # Wygenerowane segmenty

    # Stan pipeline'u
    current_stage: PipelineStage      # Aktualny etap
    stage_outputs: Dict[PipelineStage, Any] = field(default_factory=dict)  # Wyjścia z etapów

    # Metryki jakości
    coherence_score: float = 0.0      # Wynik koherencji (0.0-1.0)
    quality_checks: Dict[str, bool] = field(default_factory=dict)  # Testy jakości

    # Metadane
    created_at: datetime = field(default_factory=datetime.now)       # Data utworzenia
    last_updated: datetime = field(default_factory=datetime.now)     # Ostatnia aktualizacja
