"""
Professional AI Service for NarraForge
Supports OpenAI (GPT-4o, GPT-4o-mini) and Anthropic (Claude) models
with cost tracking, retry logic, and tier management
"""

import openai
from openai import AsyncOpenAI
import anthropic
from anthropic import AsyncAnthropic
from anthropic import (
    RateLimitError as AnthropicRateLimit,
    APIConnectionError as AnthropicAPIConnectionError,
    APITimeoutError as AnthropicAPITimeoutError,
    AuthenticationError as AnthropicAuthenticationError,
    PermissionDeniedError as AnthropicPermissionDeniedError,
    BadRequestError as AnthropicBadRequestError,
)
import logging
import time
import asyncio
import threading
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    import tiktoken
    _TIKTOKEN_AVAILABLE = True
except ImportError:
    tiktoken = None
    _TIKTOKEN_AVAILABLE = False

from app.config import settings

logger = logging.getLogger(__name__)


class ModelProvider(str, Enum):
    """AI Model Providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class ModelTier(int, Enum):
    """Model tiers for cost management"""
    TIER_1 = 1  # Fast, cheap - GPT-4o-mini
    TIER_2 = 2  # Balanced - GPT-4o, Claude Sonnet
    TIER_3 = 3  # Premium - GPT-4, Claude Opus


# Model context limits (total tokens including prompt + completion)
MODEL_CONTEXT_LIMITS = {
    "gpt-4o-mini": 128000,  # Actually 128k, not 8k
    "gpt-4o": 128000,
    "gpt-4": 8192,
    "gpt-4-turbo": 128000,
    "claude-sonnet-4-5-20250929": 200000,
    "claude-opus-4-5-20251101": 200000,
}


@dataclass
class AIResponse:
    """Standardized AI response"""
    content: str
    model: str
    provider: ModelProvider
    tokens_used: Dict[str, int]
    cost: float
    latency: float
    metadata: Dict[str, Any]


@dataclass
class GenerationMetrics:
    """Thread-safe generation metrics"""
    total_tokens: int = 0
    total_cost: float = 0.0
    calls_made: int = 0
    errors: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)


class AIService:
    """
    Professional AI Service with multi-model support

    Features:
    - OpenAI GPT-4o, GPT-4o-mini, GPT-4
    - Anthropic Claude Opus, Sonnet
    - Automatic retry with exponential backoff
    - Cost tracking per project
    - Tier-based model selection
    - Structured output support
    - Prompt caching for efficiency
    """

    def __init__(self):
        """Initialize AI Service with API clients"""
        # Validate OpenAI API key (required)
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-placeholder-add-your-key":
            logger.error("❌ OPENAI_API_KEY not set or using placeholder!")
            raise ValueError(
                "OPENAI_API_KEY is required. Please set it in .env file. "
                "See backend/AI_SETUP.md for instructions."
            )

        # Initialize OpenAI (Async client for non-blocking API calls)
        logger.info("✅ Initializing AsyncOpenAI client")
        self.openai_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=600.0,  # 10 minute timeout for complex prompts (plot structure needs 5+ min)
            max_retries=0,  # We handle retries ourselves in generate()
        )

        # Initialize Anthropic (if key is available - Async client)
        self.anthropic_client = None
        anthropic_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
        if anthropic_key and anthropic_key != "sk-placeholder-add-your-key":
            logger.info("✅ Initializing AsyncAnthropic client")
            self.anthropic_client = AsyncAnthropic(
                api_key=anthropic_key,
                timeout=600.0,  # 10 minute timeout for complex prompts
                max_retries=0,  # We handle retries ourselves in generate()
            )
        else:
            logger.warning("⚠️ ANTHROPIC_API_KEY not set - Claude models will not be available")

        # Metrics tracking
        self.metrics = GenerationMetrics()

        logger.info("AI Service initialized")

    # ---- Accurate token counting via tiktoken ----

    _tiktoken_encodings: Dict[str, Any] = {}
    _tiktoken_lock = threading.Lock()

    def count_tokens(self, text: str, model: str = "gpt-4o") -> int:
        """Count tokens accurately using tiktoken (falls back to chars//4).

        Args:
            text: Text to count tokens for
            model: Model name to use for encoding

        Returns:
            Token count
        """
        if not _TIKTOKEN_AVAILABLE:
            # Fallback: rough estimation (Polish text ≈ 3 chars/token)
            return len(text) // 3

        try:
            # Thread-safe cache of tiktoken encodings
            if model not in self._tiktoken_encodings:
                with self._tiktoken_lock:
                    if model not in self._tiktoken_encodings:  # Double-checked locking
                        try:
                            self._tiktoken_encodings[model] = tiktoken.encoding_for_model(model)
                        except KeyError:
                            self._tiktoken_encodings[model] = tiktoken.get_encoding("cl100k_base")

            enc = self._tiktoken_encodings[model]
            return len(enc.encode(text))
        except Exception:
            return len(text) // 3

    def _get_model_for_tier(self, tier: ModelTier, prefer_anthropic: bool = False) -> Tuple[str, ModelProvider]:
        """Get model name and provider for a given tier"""
        if tier == ModelTier.TIER_1:
            # Tier 1: Fast and cheap
            return settings.GPT_4O_MINI, ModelProvider.OPENAI

        elif tier == ModelTier.TIER_2:
            # Tier 2: Balanced - prefer Claude Sonnet if available
            if prefer_anthropic and self.anthropic_client:
                return "claude-sonnet-4-5-20250929", ModelProvider.ANTHROPIC
            return settings.GPT_4O, ModelProvider.OPENAI

        else:  # TIER_3
            # Tier 3: Premium quality (128k context)
            if prefer_anthropic and self.anthropic_client:
                return "claude-opus-4-5-20251101", ModelProvider.ANTHROPIC
            # Use gpt-4-turbo (128k context) instead of gpt-4 (8k context)
            # This prevents context overflow errors on long chapters
            return "gpt-4-turbo", ModelProvider.OPENAI

    def _calculate_cost(self, tokens_in: int, tokens_out: int, model: str, provider: ModelProvider) -> float:
        """
        Calculate cost based on token usage and actual model used

        Args:
            tokens_in: Input tokens
            tokens_out: Output tokens
            model: Actual model name used
            provider: Model provider (OpenAI or Anthropic)

        Returns:
            Cost in USD
        """
        # Define pricing per model (per 1M tokens)
        # Source: https://openai.com/api/pricing/ and https://anthropic.com/pricing
        pricing = {
            # OpenAI models
            "gpt-4o-mini": (0.15, 0.60),
            "gpt-4o": (2.50, 10.00),
            "gpt-4": (30.00, 60.00),
            "gpt-4-turbo": (10.00, 30.00),
            # Anthropic models
            "claude-sonnet-4-5-20250929": (3.00, 15.00),
            "claude-opus-4-5-20251101": (15.00, 75.00),
        }

        # Get pricing for this model, fallback to tier-based if unknown
        if model in pricing:
            input_cost, output_cost = pricing[model]
        else:
            logger.warning(f"Unknown model '{model}' - using tier-based fallback pricing")
            # Fallback to old tier-based logic
            if "mini" in model.lower():
                input_cost, output_cost = settings.TIER1_INPUT_COST, settings.TIER1_OUTPUT_COST
            elif "4o" in model or "sonnet" in model.lower():
                input_cost, output_cost = settings.TIER2_INPUT_COST, settings.TIER2_OUTPUT_COST
            else:
                input_cost, output_cost = settings.TIER3_INPUT_COST, settings.TIER3_OUTPUT_COST

        cost = (tokens_in / 1_000_000) * input_cost + (tokens_out / 1_000_000) * output_cost
        return round(cost, 6)

    def calculate_safe_max_tokens(
        self,
        model: str,
        estimated_prompt_tokens: int,
        requested_max_tokens: int,
        safety_buffer: int = 500
    ) -> int:
        """
        Calculate a safe max_tokens value that respects model context limits

        Args:
            model: Model name
            estimated_prompt_tokens: Estimated tokens in the prompt
            requested_max_tokens: Desired max_tokens
            safety_buffer: Safety buffer to leave (default 500, was 100 but too small)

        Returns:
            Safe max_tokens value that won't exceed context limit
        """
        # Get model context limit (default to conservative 8192 if unknown)
        context_limit = MODEL_CONTEXT_LIMITS.get(model, 8192)

        # Add 15% margin to estimated_prompt_tokens because tokenization estimation is imprecise
        # Real prompt can be 10-20% larger than estimated due to:
        # - Special tokens
        # - Formatting tokens
        # - System prompt overhead
        conservative_prompt_estimate = int(estimated_prompt_tokens * 1.15)

        # Calculate maximum allowed completion tokens
        max_allowed = context_limit - conservative_prompt_estimate - safety_buffer

        # Ensure it's positive and reasonable
        max_allowed = max(1000, max_allowed)  # Minimum 1000 tokens

        # Return the smaller of requested and max_allowed
        safe_max = min(requested_max_tokens, max_allowed)

        if safe_max < requested_max_tokens:
            logger.warning(
                f"Reduced max_tokens from {requested_max_tokens} to {safe_max} "
                f"to fit within {model} context limit ({context_limit} tokens). "
                f"Estimated prompt: {estimated_prompt_tokens} → conservative: {conservative_prompt_estimate} tokens"
            )

        return safe_max

    async def generate(
        self,
        prompt: str,
        tier: ModelTier = ModelTier.TIER_1,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        prefer_anthropic: bool = False,
        retry_count: int = 3,
        metadata: Optional[Dict[str, Any]] = None,
        enable_cache: bool = False
    ) -> AIResponse:
        """
        Generate content using AI

        Args:
            prompt: User prompt
            tier: Model tier (1=fast, 2=balanced, 3=premium)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system message
            json_mode: Force JSON output (OpenAI only)
            prefer_anthropic: Prefer Claude over GPT when available
            retry_count: Number of retries on failure
            metadata: Additional metadata to track
            enable_cache: Enable prompt caching for system_prompt.
                For Anthropic: uses cache_control with ephemeral type (~90% cost reduction on cached input).
                For OpenAI: system prompt is automatically cached by the API.
                Best used when system_prompt contains large, stable content (World Bible, style guides).

        Returns:
            AIResponse with generated content and metrics
        """
        model, provider = self._get_model_for_tier(tier, prefer_anthropic)

        # Accurate token counting via tiktoken (with fallback)
        full_prompt_text = (system_prompt or "") + prompt
        estimated_prompt_tokens = self.count_tokens(full_prompt_text, model)

        # Calculate safe max_tokens that respects model context limits
        safe_max_tokens = self.calculate_safe_max_tokens(
            model=model,
            estimated_prompt_tokens=estimated_prompt_tokens,
            requested_max_tokens=max_tokens
        )

        start_time = time.time()
        last_error = None

        # Retry logic with exponential backoff
        for attempt in range(retry_count):
            try:
                if provider == ModelProvider.OPENAI:
                    response = await self._call_openai(
                        model=model,
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=safe_max_tokens,
                        json_mode=json_mode
                    )
                else:  # Anthropic
                    response = await self._call_anthropic(
                        model=model,
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=safe_max_tokens,
                        enable_cache=enable_cache
                    )

                # Calculate metrics
                latency = time.time() - start_time
                cost = self._calculate_cost(
                    response['tokens_in'],
                    response['tokens_out'],
                    model,
                    provider
                )

                # Update global metrics (thread-safe)
                with self.metrics._lock:
                    self.metrics.total_tokens += response['tokens_in'] + response['tokens_out']
                    self.metrics.total_cost += cost
                    self.metrics.calls_made += 1

                logger.info(
                    f"AI generation successful: model={model}, "
                    f"tokens={response['tokens_in']}+{response['tokens_out']}, "
                    f"cost=${cost:.4f}, latency={latency:.2f}s"
                )

                return AIResponse(
                    content=response['content'],
                    model=model,
                    provider=provider,
                    tokens_used={
                        'input': response['tokens_in'],
                        'output': response['tokens_out'],
                        'total': response['tokens_in'] + response['tokens_out']
                    },
                    cost=cost,
                    latency=latency,
                    metadata=metadata or {}
                )

            except (openai.RateLimitError, AnthropicRateLimit) as e:
                # Rate limit - check for Retry-After header
                retry_after = None
                if hasattr(e, 'response') and hasattr(e.response, 'headers'):
                    retry_after = e.response.headers.get('retry-after') or e.response.headers.get('Retry-After')

                wait_time = int(retry_after) if retry_after else (2 ** attempt)
                logger.warning(f"Rate limit hit on attempt {attempt + 1}/{retry_count}, retrying after {wait_time}s")

                if attempt < retry_count - 1:
                    await asyncio.sleep(wait_time)
                else:
                    with self.metrics._lock:
                    self.metrics.errors += 1
                    raise Exception(f"Rate limit exceeded after {retry_count} attempts: {e}")

            except (openai.APIConnectionError, AnthropicAPIConnectionError, AnthropicAPITimeoutError) as e:
                # Network errors - retriable
                with self.metrics._lock:
                    self.metrics.errors += 1
                logger.warning(f"Network error on attempt {attempt + 1}/{retry_count}: {str(e)}")

                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise Exception(f"Network error after {retry_count} attempts: {e}")

            except (openai.AuthenticationError, openai.PermissionDeniedError, AnthropicAuthenticationError, AnthropicPermissionDeniedError) as e:
                # Auth/Permission errors - DO NOT retry (fail fast)
                with self.metrics._lock:
                    self.metrics.errors += 1
                logger.error(f"Authentication/Permission error (non-retriable): {e}")
                raise Exception(f"API authentication/permission error: {e}")

            except (openai.BadRequestError, AnthropicBadRequestError) as e:
                # Bad request errors - DO NOT retry (fail fast)
                with self.metrics._lock:
                    self.metrics.errors += 1
                logger.error(f"Bad request error (non-retriable): {e}")
                raise Exception(f"API bad request error: {e}")

            except Exception as e:
                # Unknown errors - retry with caution
                last_error = e
                with self.metrics._lock:
                    self.metrics.errors += 1
                logger.warning(
                    f"Unknown error on attempt {attempt + 1}/{retry_count}: {str(e)}"
                )

                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise Exception(f"AI generation failed after {retry_count} attempts: {last_error}")

    async def _call_openai(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        json_mode: bool
    ) -> Dict[str, Any]:
        """Call OpenAI API"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.openai_client.chat.completions.create(**kwargs)

        # Validate response structure
        if not response.choices or len(response.choices) == 0:
            raise Exception("OpenAI API returned empty response")

        if not response.choices[0].message or not response.choices[0].message.content:
            raise Exception("OpenAI API returned no content in response")

        return {
            'content': response.choices[0].message.content,
            'tokens_in': response.usage.prompt_tokens,
            'tokens_out': response.usage.completion_tokens,
        }

    async def _call_anthropic(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        enable_cache: bool = False
    ) -> Dict[str, Any]:
        """Call Anthropic Claude API with optional prompt caching.

        When enable_cache=True and system_prompt is provided, the system prompt
        is sent with cache_control={"type": "ephemeral"} which enables Anthropic's
        prompt caching. This gives ~90% cost reduction on cached input tokens
        (from $3/$15 to $0.30/$1.50 per 1M tokens for Sonnet).

        The cache is maintained by Anthropic for 5 minutes after last use,
        so consecutive chapter generations reuse the cached World Bible.
        """
        if not self.anthropic_client:
            raise Exception("Anthropic client not initialized (missing API key)")

        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        if system_prompt:
            if enable_cache:
                # Use cache_control for the system prompt block.
                # This tells Anthropic to cache the system prompt content.
                # Subsequent requests with the same system prompt will use cached tokens.
                kwargs["system"] = [
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"}
                    }
                ]
                logger.debug(
                    f"Anthropic prompt caching enabled for system prompt "
                    f"({len(system_prompt)} chars)"
                )
            else:
                kwargs["system"] = system_prompt

        response = await self.anthropic_client.messages.create(**kwargs)

        # Validate response structure
        if not response.content or len(response.content) == 0:
            raise Exception("Anthropic API returned empty response")

        if not hasattr(response.content[0], 'text') or not response.content[0].text:
            raise Exception("Anthropic API returned no text in response")

        # Track cache performance if available
        cache_creation_tokens = getattr(response.usage, 'cache_creation_input_tokens', 0) or 0
        cache_read_tokens = getattr(response.usage, 'cache_read_input_tokens', 0) or 0

        if cache_read_tokens > 0:
            logger.info(
                f"Anthropic cache HIT: {cache_read_tokens} cached tokens "
                f"(~{cache_read_tokens * 0.9 / 1_000_000 * 3.0:.4f}$ saved for Sonnet)"
            )
        elif cache_creation_tokens > 0:
            logger.info(
                f"Anthropic cache WRITE: {cache_creation_tokens} tokens cached for future use"
            )

        return {
            'content': response.content[0].text,
            'tokens_in': response.usage.input_tokens,
            'tokens_out': response.usage.output_tokens,
            'cache_creation_tokens': cache_creation_tokens,
            'cache_read_tokens': cache_read_tokens,
        }

    def get_metrics(self) -> GenerationMetrics:
        """Get current generation metrics"""
        return self.metrics

    def reset_metrics(self):
        """Reset metrics (useful for per-project tracking)"""
        self.metrics = GenerationMetrics()


# Singleton instance
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get or create AI service singleton"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
