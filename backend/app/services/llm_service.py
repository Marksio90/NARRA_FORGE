"""
LLM Service - Tiered LLM Client Access for NarraForge

Provides a unified interface for accessing OpenAI clients at different tiers:
- low: GPT-4o-mini (fast, cheap)
- mid: GPT-4o (balanced)
- high: GPT-4o (premium quality)

This service wraps the AsyncOpenAI client to provide tier-based model selection
while maintaining the native OpenAI client interface for maximum flexibility.
"""

from typing import Optional
import logging
from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


class TieredOpenAIClient:
    """
    Wrapper around AsyncOpenAI that provides tier-based model defaults.

    Maintains full compatibility with the OpenAI client interface.
    """

    def __init__(self, client: AsyncOpenAI, tier: str):
        self._client = client
        self._tier = tier
        # Determine default model based on tier
        self._default_model = self._get_default_model(tier)

    def _get_default_model(self, tier: str) -> str:
        """Get default model for tier"""
        tier_models = {
            "low": getattr(settings, 'GPT_4O_MINI', 'gpt-4o-mini'),
            "mid": getattr(settings, 'GPT_4O', 'gpt-4o'),
            "high": getattr(settings, 'GPT_4O', 'gpt-4o'),
        }
        return tier_models.get(tier, 'gpt-4o-mini')

    @property
    def chat(self):
        """Return the chat completions interface"""
        return self._client.chat

    @property
    def images(self):
        """Return the images interface for DALL-E"""
        return self._client.images

    @property
    def audio(self):
        """Return the audio interface for TTS/Whisper"""
        return self._client.audio

    @property
    def default_model(self) -> str:
        """Return the default model for this tier"""
        return self._default_model


class LLMService:
    """
    LLM Service providing tiered access to language models.

    Supports three tiers:
    - low: Fast and cheap (gpt-4o-mini)
    - mid: Balanced (gpt-4o)
    - high: Premium quality (gpt-4o)

    Usage:
        llm_service = get_llm_service()
        client = llm_service.get_client("mid")
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello"}]
        )
    """

    def __init__(self):
        """Initialize LLM Service with OpenAI client"""
        # Validate API key
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-placeholder-add-your-key":
            logger.error("❌ OPENAI_API_KEY not set or using placeholder!")
            raise ValueError(
                "OPENAI_API_KEY is required. Please set it in .env file. "
                "See backend/AI_SETUP.md for instructions."
            )

        # Initialize async OpenAI client
        logger.info("✅ Initializing LLM Service with AsyncOpenAI client")
        self._client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=600.0,  # 10 minute timeout for complex prompts
            max_retries=3,
        )

        # Cache tiered clients
        self._tiered_clients: dict[str, TieredOpenAIClient] = {}

        logger.info("LLM Service initialized successfully")

    def get_client(self, tier: str = "mid") -> TieredOpenAIClient:
        """
        Get an OpenAI client for the specified tier.

        Args:
            tier: Quality tier - "low", "mid", or "high"

        Returns:
            TieredOpenAIClient with appropriate default model
        """
        # Normalize tier
        tier = tier.lower()
        if tier not in ["low", "mid", "high"]:
            logger.warning(f"Unknown tier '{tier}', defaulting to 'mid'")
            tier = "mid"

        # Return cached client or create new one
        if tier not in self._tiered_clients:
            self._tiered_clients[tier] = TieredOpenAIClient(self._client, tier)

        return self._tiered_clients[tier]

    @property
    def raw_client(self) -> AsyncOpenAI:
        """Get the raw AsyncOpenAI client for direct access"""
        return self._client


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """
    Get or create LLM service singleton.

    Returns:
        LLMService instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
