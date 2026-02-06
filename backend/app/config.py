"""
Configuration module for NarraForge
Loads environment variables and provides configuration classes
"""

from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "NarraForge"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    SECRET_KEY: str  # REQUIRED - No default for security (set in .env)

    # Database
    POSTGRES_USER: str = "narraforge"
    POSTGRES_PASSWORD: str = "narraforge_password"
    POSTGRES_DB: str = "narraforge"
    POSTGRES_HOST: str = "narraforge-postgres"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    # Redis
    REDIS_HOST: str = "narraforge-redis"
    REDIS_PORT: int = 6379
    REDIS_URL: Optional[str] = None

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # OpenAI (REQUIRED)
    OPENAI_API_KEY: str  # REQUIRED - No default (set in .env)
    GPT_4O_MINI: str = "gpt-4o-mini"
    GPT_4O: str = "gpt-4o"
    GPT_4: str = "gpt-4-turbo"
    GPT_O1: str = "o1"
    DEFAULT_MODEL_TIER: int = 1

    # Anthropic (optional)
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_OPUS_4_5: str = "claude-opus-4-5-20251101"
    CLAUDE_SONNET_4_5: str = "claude-sonnet-4-5-20250929"
    
    # Cost Management
    MAX_COST_PER_PROJECT: float = 100.0
    COST_ALERT_THRESHOLD: float = 0.8
    
    # Model Pricing (per 1M tokens)
    TIER1_INPUT_COST: float = 0.15
    TIER1_OUTPUT_COST: float = 0.60
    TIER2_INPUT_COST: float = 2.50
    TIER2_OUTPUT_COST: float = 10.0
    TIER3_INPUT_COST: float = 10.0   # gpt-4-turbo pricing per 1M tokens
    TIER3_OUTPUT_COST: float = 30.0  # gpt-4-turbo pricing per 1M tokens
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # File Storage
    OUTPUT_DIR: str = "/app/output"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    
    # Generation Defaults
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 4000
    
    # RAG Configuration
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536
    RAG_TOP_K: int = 5

    @model_validator(mode='after')
    def build_urls(self):
        """Build URLs from components if not provided"""
        # Build DATABASE_URL if not provided
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        # Build REDIS_URL if not provided
        if not self.REDIS_URL:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

        # Build Celery URLs if not provided
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"

        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/2"

        return self

    class Config:
        env_file = ".env"
        case_sensitive = True


class ModelTierConfig:
    """Configuration for model tier selection and escalation"""
    
    TIER_1_TASKS = [
        "initialization",
        "validation",
        "formatting",
        "extraction",
        "simple_outline",
        "metadata",
    ]
    
    TIER_2_TASKS = [
        "world_building",
        "character_creation",
        "plot_structure",
        "prose_writing",
        "dialogue",
        "description",
        "style_polish",
    ]
    
    TIER_3_TASKS = [
        "climax_scene",
        "complex_resolution",
        "multi_character_scene",
        "critical_turning_point",
        "final_polish",
    ]
    
    @classmethod
    def get_tier_for_task(cls, task_type: str) -> int:
        """Determine appropriate model tier for a given task type"""
        if task_type in cls.TIER_1_TASKS:
            return 1
        elif task_type in cls.TIER_2_TASKS:
            return 2
        elif task_type in cls.TIER_3_TASKS:
            return 3
        return 1  # Default to tier 1


class GenreConfig:
    """Configuration for different literary genres"""
    
    GENRES = {
        "sci-fi": {
            "name": "Science Fiction",
            "description": "Spójny system technologii, implikacje społeczne, sense of wonder",
            "style": "Precyzyjny, techniczny ale przystępny, eksploracyjny",
            "structure": "Hero's Journey",
            "default_length": "novel",  # ~80-120k words
            "key_elements": ["technology_system", "world_building", "scientific_accuracy"],
        },
        "fantasy": {
            "name": "Fantasy",
            "description": "System magii z regułami, epic quest, world-building, mapy",
            "style": "Epicki, poetycki, bogaty w opisy, archetypowy",
            "structure": "Hero's Journey",
            "default_length": "novel",  # ~90-140k words
            "key_elements": ["magic_system", "races", "mythology", "maps"],
        },
        "thriller": {
            "name": "Thriller",
            "description": "Napięcie od pierwszej strony, ticking clock, twists",
            "style": "Szybkie tempo, krótkie rozdziały, cliffhangery",
            "structure": "7-Point Structure",
            "default_length": "novel",  # ~70-90k words
            "key_elements": ["tension", "ticking_clock", "antagonist", "twists"],
        },
        "horror": {
            "name": "Horror",
            "description": "Atmosfera grozy, psychological dread, izolacja",
            "style": "Powolne budowanie napięcia, sugestia, duszna atmosfera",
            "structure": "3-Act",
            "default_length": "novel",  # ~70-90k words
            "key_elements": ["atmosphere", "dread", "isolation", "supernatural"],
        },
        "romance": {
            "name": "Romance",
            "description": "Chemia między postaciami, przeszkody w miłości, HEA/HFN",
            "style": "Emocjonalny, intymny, skupiony na relacjach",
            "structure": "Romance Beat Sheet",
            "default_length": "novel",  # ~70-90k words
            "key_elements": ["chemistry", "obstacles", "emotional_beats", "HEA"],
        },
        "drama": {
            "name": "Drama",
            "description": "Głębokie konflikty wewnętrzne, moralne dylematy",
            "style": "Literacki, introspektywny, bogate dialogi",
            "structure": "3-Act",
            "default_length": "novel",  # ~80-100k words
            "key_elements": ["internal_conflict", "moral_dilemmas", "transformation"],
        },
        "comedy": {
            "name": "Comedy",
            "description": "Timing komediowy, lovable losers, happy ending",
            "style": "Lekki, zabawny, z puentami",
            "structure": "Save the Cat",
            "default_length": "novel",  # ~70-85k words
            "key_elements": ["humor", "timing", "lovable_characters", "happy_ending"],
        },
        "mystery": {
            "name": "Mystery/Crime",
            "description": "Zagadka do rozwiązania, fair play clues, satisfying reveal",
            "style": "Analityczny, obserwacyjny, puzzle-like",
            "structure": "Mystery Structure",
            "default_length": "novel",  # ~70-90k words
            "key_elements": ["puzzle", "clues", "red_herrings", "detective", "reveal"],
        },
        "religious": {
            "name": "Religijne",
            "description": "Literatura religijna oparta na prawdziwych kerygmatach, Piśmie Świętym, nauce Kościoła",
            "style": "Pełen szacunku, dostępny, poruszający serce i intelekt",
            "structure": "Spiritual Journey",
            "default_length": "novel",  # ~60-150k words
            "key_elements": [
                "scripture_references",
                "authentic_spirituality",
                "church_teaching",
                "spiritual_transformation",
                "grace_and_redemption",
                "communion_with_god",
                "theological_accuracy"
            ],
            "tone": "reverent_yet_accessible",
            "pacing": "contemplative_with_moments_of_grace",
            "required_sources": [
                "Biblia (Stary i Nowy Testament)",
                "Katechizm Kościoła Katolickiego",
                "Encykliki papieskie",
                "Pisma Ojców Kościoła",
                "Zatwierdzone cuda",
                "Żywoty świętych"
            ],
            "narrative_beats": [
                "Życie przed wiarą / kryzys",
                "Pierwsze dotknięcie łaski",
                "Opór i wątpliwości",
                "Spotkanie z autentycznym świadectwem",
                "Ciemna noc duszy",
                "Punkt nawrócenia",
                "Próba wiary",
                "Pogłębienie relacji z Bogiem",
                "Misja / dzielenie się wiarą",
                "Owoce Ducha Świętego"
            ]
        },
    }
    
    @classmethod
    def get_genre_config(cls, genre: str) -> dict:
        """Get configuration for a specific genre"""
        return cls.GENRES.get(genre, cls.GENRES["sci-fi"])


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export commonly used instances
settings = get_settings()
model_tier_config = ModelTierConfig()
genre_config = GenreConfig()
