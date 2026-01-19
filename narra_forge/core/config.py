"""
Uniwersalna konfiguracja systemu NARRA_FORGE

System automatycznie adaptuje się do:
- Wszystkich długości (flash fiction → saga)
- Wszystkich gatunków (fantasy → literary)
- Wszystkich tonów (dark → light)
- Wszystkich modeli LLM (GPT-4, Claude, lokalne)
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional
from narra_forge.core.types import ModelConfig, NarrativeForm, Genre


@dataclass
class SystemConfig:
    """
    Główna konfiguracja systemu NARRA_FORGE

    UNIWERSALNOŚĆ: Jeden config działa dla WSZYSTKICH scenariuszy.
    System SAM dostosowuje parametry na podstawie inputu użytkownika.
    """

    # ==================== MODEL BACKENDS ====================

    models: Dict[str, ModelConfig] = field(default_factory=lambda: {
        # OpenAI GPT-4 (domyślny główny model)
        "gpt-4-turbo": ModelConfig(
            model_name="gpt-4-turbo-2024-04-09",
            provider="openai",
            api_key_env="OPENAI_API_KEY",
            temperature=0.8,
            max_tokens=4096,
            cost_per_1k_tokens=0.01,
            max_requests_per_minute=500,
            supports_long_context=True,
            max_context_length=128000,
            supports_json_mode=True,
            best_for=["generation", "creativity", "polish"]
        ),

        # OpenAI GPT-4 (dla najwyższej jakości)
        "gpt-4": ModelConfig(
            model_name="gpt-4",
            provider="openai",
            api_key_env="OPENAI_API_KEY",
            temperature=0.7,
            max_tokens=8192,
            cost_per_1k_tokens=0.03,
            max_requests_per_minute=200,
            supports_long_context=False,
            max_context_length=8192,
            supports_json_mode=False,
            best_for=["quality", "creativity"]
        ),

        # OpenAI GPT-3.5 (dla szybkich analiz)
        "gpt-3.5-turbo": ModelConfig(
            model_name="gpt-3.5-turbo",
            provider="openai",
            api_key_env="OPENAI_API_KEY",
            temperature=0.5,
            max_tokens=4096,
            cost_per_1k_tokens=0.0005,
            max_requests_per_minute=3500,
            supports_long_context=True,
            max_context_length=16385,
            supports_json_mode=True,
            best_for=["analysis", "validation", "speed"]
        ),

        # Claude Opus 4.5 (premium alternatywa)
        "claude-opus": ModelConfig(
            model_name="claude-opus-4-5-20251101",
            provider="anthropic",
            api_key_env="ANTHROPIC_API_KEY",
            temperature=0.8,
            max_tokens=4096,
            cost_per_1k_tokens=0.015,
            max_requests_per_minute=1000,
            supports_long_context=True,
            max_context_length=200000,
            supports_json_mode=True,
            best_for=["generation", "quality", "polish", "long_context"]
        ),

        # Claude Sonnet 4.5 (zbalansowany)
        "claude-sonnet": ModelConfig(
            model_name="claude-sonnet-4-5-20250929",
            provider="anthropic",
            api_key_env="ANTHROPIC_API_KEY",
            temperature=0.7,
            max_tokens=8192,
            cost_per_1k_tokens=0.003,
            max_requests_per_minute=2000,
            supports_long_context=True,
            max_context_length=200000,
            supports_json_mode=True,
            best_for=["generation", "analysis", "balanced"]
        ),

        # Claude Haiku (szybki)
        "claude-haiku": ModelConfig(
            model_name="claude-haiku-4-20250514",
            provider="anthropic",
            api_key_env="ANTHROPIC_API_KEY",
            temperature=0.5,
            max_tokens=4096,
            cost_per_1k_tokens=0.00025,
            max_requests_per_minute=5000,
            supports_long_context=True,
            max_context_length=200000,
            supports_json_mode=True,
            best_for=["speed", "analysis", "validation"]
        ),
    })

    # Domyślny model (używany, jeśli agent nie określi inaczej)
    default_model: str = "gpt-4-turbo"

    # Mapowanie: etap pipeline -> preferowany model
    stage_model_mapping: Dict[str, str] = field(default_factory=lambda: {
        "brief_interpretation": "gpt-3.5-turbo",     # Szybka analiza
        "world_architecture": "gpt-4-turbo",         # Kreatywność
        "character_architecture": "gpt-4-turbo",     # Głębia psychologiczna
        "narrative_structure": "gpt-4-turbo",        # Architektura
        "segment_planning": "gpt-3.5-turbo",         # Planowanie
        "sequential_generation": "gpt-4-turbo",      # GŁÓWNA GENERACJA
        "coherence_validation": "gpt-3.5-turbo",     # Precyzyjna walidacja
        "language_stylization": "gpt-4-turbo",       # Styl i polszczyzna
        "editorial_review": "gpt-4-turbo",           # Finalna jakość
        "final_output": "gpt-3.5-turbo",             # Proste formatowanie
    })

    # ==================== PAMIĘĆ ====================

    # Ścieżki
    memory_db_path: Path = Path("./data/memory/narra_forge.db")
    revision_path: Path = Path("./data/revisions")
    output_path: Path = Path("./data/output")

    # Limity
    max_memory_items: int = 100000         # Maksymalna liczba elementów w pamięci
    memory_relevance_threshold: float = 0.3 # Próg relevance dla retrieval

    # ==================== PIPELINE ====================

    # Równoległość
    enable_parallel_agents: bool = True    # Czy agenty mogą działać równolegle
    max_parallel_agents: int = 3           # Max równoległych agentów

    # Retry i odporność na błędy
    max_retries: int = 3                   # Max liczba prób dla każdego etapu
    retry_delay_seconds: float = 2.0       # Opóźnienie między próbami

    # ==================== QUALITY CONTROL ====================

    # Progi jakości (UNIWERSALNE - działają dla wszystkich długości!)
    min_coherence_score: float = 0.85      # Minimum ogólnej koherencji
    min_character_consistency: float = 0.90 # Minimum spójności postaci
    min_world_consistency: float = 0.88    # Minimum spójności świata
    min_plot_consistency: float = 0.85     # Minimum spójności fabuły
    min_language_quality: float = 0.92     # Minimum jakości językowej

    # Walidacja
    enable_strict_validation: bool = True  # Czy stosować ostre quality gates
    auto_fix_issues: bool = True           # Czy automatycznie naprawiać problemy

    # ==================== ADAPTIVE PARAMETERS ====================

    # Automatyczna adaptacja długości do formy
    form_word_count_ranges: Dict[NarrativeForm, tuple] = field(default_factory=lambda: {
        NarrativeForm.FLASH_FICTION: (500, 1000),
        NarrativeForm.SHORT_STORY: (5000, 15000),
        NarrativeForm.NOVELLA: (15000, 40000),
        NarrativeForm.NOVEL: (40000, 120000),
        NarrativeForm.EPIC_SAGA: (120000, 500000),
    })

    # Automatyczna adaptacja liczby rozdziałów
    words_per_chapter_range: tuple = (2000, 4000)

    # Automatyczna adaptacja subplot count
    form_subplot_count: Dict[NarrativeForm, int] = field(default_factory=lambda: {
        NarrativeForm.FLASH_FICTION: 0,
        NarrativeForm.SHORT_STORY: 1,
        NarrativeForm.NOVELLA: 2,
        NarrativeForm.NOVEL: 3,
        NarrativeForm.EPIC_SAGA: 5,
    })

    # Automatyczna adaptacja liczby postaci drugoplanowych
    form_supporting_char_count: Dict[NarrativeForm, int] = field(default_factory=lambda: {
        NarrativeForm.FLASH_FICTION: 1,
        NarrativeForm.SHORT_STORY: 2,
        NarrativeForm.NOVELLA: 3,
        NarrativeForm.NOVEL: 5,
        NarrativeForm.EPIC_SAGA: 8,
    })

    # ==================== GENRE TEMPLATES ====================

    # Szablony gatunkowe (automatyczne dopasowanie konwencji)
    genre_conventions: Dict[Genre, Dict[str, any]] = field(default_factory=lambda: {
        Genre.FANTASY: {
            "typical_structure": "hero_journey",
            "typical_tone": "epic_poetic",
            "worldbuilding_depth": "very_high",
            "magic_system_required": True,
            "language_style": "elevated_metaphorical",
        },
        Genre.SCI_FI: {
            "typical_structure": "exploration",
            "typical_tone": "speculative",
            "worldbuilding_depth": "very_high",
            "tech_system_required": True,
            "language_style": "precise_technical",
        },
        Genre.THRILLER: {
            "typical_structure": "3_act_tight",
            "typical_tone": "suspenseful",
            "worldbuilding_depth": "low",
            "pacing": "fast",
            "language_style": "lean_punchy",
        },
        Genre.HORROR: {
            "typical_structure": "escalating_dread",
            "typical_tone": "dark_atmospheric",
            "worldbuilding_depth": "medium",
            "pacing": "variable_with_tension",
            "language_style": "sensory_visceral",
        },
        Genre.ROMANCE: {
            "typical_structure": "emotional_arc",
            "typical_tone": "emotionally_rich",
            "worldbuilding_depth": "low",
            "relationship_focus": True,
            "language_style": "emotionally_evocative",
        },
        Genre.LITERARY: {
            "typical_structure": "flexible_experimental",
            "typical_tone": "contemplative",
            "worldbuilding_depth": "varies",
            "character_depth": "very_high",
            "language_style": "sophisticated_layered",
        },
        Genre.MYSTERY: {
            "typical_structure": "investigation",
            "typical_tone": "methodical_intriguing",
            "worldbuilding_depth": "medium",
            "clue_planting_required": True,
            "language_style": "precise_observational",
        },
    })

    # ==================== OUTPUT ====================

    # Formaty eksportu
    enable_epub_export: bool = True
    enable_pdf_export: bool = True
    enable_audiobook_format: bool = True

    # Metadane
    include_metadata: bool = True
    include_expansion_data: bool = True     # Dane do kontynuacji

    # ==================== LOGGING & MONITORING ====================

    log_level: str = "INFO"                # DEBUG/INFO/WARNING/ERROR
    enable_progress_tracking: bool = True   # Real-time progress
    enable_websocket_updates: bool = True   # WebSocket dla UI

    # ==================== ADVANCED ====================

    # Caching
    enable_prompt_caching: bool = True      # Cache'owanie promptów
    cache_ttl_seconds: int = 3600           # TTL cache (1h)

    # Embeddings (dla przyszłej vector search)
    enable_embeddings: bool = False         # Obecnie wyłączone
    embedding_model: str = "text-embedding-3-small"

    # Multi-world
    enable_world_linking: bool = True       # Czy światy mogą się przenikać
    max_active_worlds: int = 10             # Max równocześnie aktywnych światów


def get_default_config() -> SystemConfig:
    """
    Zwraca domyślną konfigurację z wartościami ze środowiska
    """
    config = SystemConfig()

    # Override z environment variables
    if os.getenv("MIN_COHERENCE_SCORE"):
        config.min_coherence_score = float(os.getenv("MIN_COHERENCE_SCORE"))

    if os.getenv("DEFAULT_MODEL"):
        config.default_model = os.getenv("DEFAULT_MODEL")

    if os.getenv("MAX_RETRIES"):
        config.max_retries = int(os.getenv("MAX_RETRIES"))

    if os.getenv("LOG_LEVEL"):
        config.log_level = os.getenv("LOG_LEVEL")

    # Utwórz wymagane foldery
    config.memory_db_path.parent.mkdir(parents=True, exist_ok=True)
    config.revision_path.mkdir(parents=True, exist_ok=True)
    config.output_path.mkdir(parents=True, exist_ok=True)

    return config


def get_adaptive_config(
    form: Optional[NarrativeForm] = None,
    genre: Optional[Genre] = None,
    base_config: Optional[SystemConfig] = None
) -> SystemConfig:
    """
    Zwraca config adaptowany do konkretnej formy i gatunku

    KLUCZOWA FUNKCJA: Automatycznie dostosowuje parametry!

    Args:
        form: Forma narracyjna (jeśli None, używa wartości domyślnych)
        genre: Gatunek (jeśli None, używa wartości domyślnych)
        base_config: Bazowa konfiguracja (jeśli None, używa default)

    Returns:
        Dostosowana konfiguracja
    """
    config = base_config or get_default_config()

    # Adaptacja do gatunku
    if genre and genre in config.genre_conventions:
        conventions = config.genre_conventions[genre]

        # Możesz tutaj dodać automatyczne przełączanie modeli,
        # np. dla literary fiction użyj bardziej wyrafinowanych modeli
        if genre == Genre.LITERARY:
            config.stage_model_mapping["sequential_generation"] = "claude-opus"
            config.stage_model_mapping["language_stylization"] = "claude-opus"

        # Dla thriller - szybsze modele dla tempa
        elif genre == Genre.THRILLER:
            config.stage_model_mapping["segment_planning"] = "gpt-4-turbo"

    # Adaptacja do formy
    if form:
        # Dla bardzo długich form - zwiększ timeout i retries
        if form in [NarrativeForm.NOVEL, NarrativeForm.EPIC_SAGA]:
            config.max_retries = 5

        # Dla bardzo krótkich - możesz użyć szybszych modeli
        elif form == NarrativeForm.FLASH_FICTION:
            config.stage_model_mapping["sequential_generation"] = "gpt-3.5-turbo"

    return config


# ==================== HELPER FUNCTIONS ====================

def get_model_for_stage(stage: str, config: SystemConfig) -> str:
    """Zwraca najlepszy model dla danego etapu pipeline"""
    return config.stage_model_mapping.get(stage, config.default_model)


def calculate_target_word_count(form: NarrativeForm, config: SystemConfig) -> int:
    """Oblicza docelową liczbę słów na podstawie formy"""
    if form == NarrativeForm.AUTO:
        return 50000  # Medium default

    range_tuple = config.form_word_count_ranges.get(form, (40000, 80000))
    # Zwróć średnią z zakresu
    return (range_tuple[0] + range_tuple[1]) // 2


def calculate_chapter_count(target_words: int, config: SystemConfig) -> int:
    """Oblicza szacowaną liczbę rozdziałów"""
    avg_words_per_chapter = sum(config.words_per_chapter_range) // 2
    return max(1, target_words // avg_words_per_chapter)


def get_subplot_count(form: NarrativeForm, config: SystemConfig) -> int:
    """Zwraca odpowiednią liczbę subplotów dla danej formy"""
    return config.form_subplot_count.get(form, 2)


def get_supporting_char_count(form: NarrativeForm, config: SystemConfig) -> int:
    """Zwraca odpowiednią liczbę postaci drugoplanowych"""
    return config.form_supporting_char_count.get(form, 3)
