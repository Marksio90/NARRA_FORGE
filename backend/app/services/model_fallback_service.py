"""
Model Fallback Service for NarraForge 2.0

Automatic failover between AI providers.
If OpenAI fails - switch to Anthropic and vice versa.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class ProviderName(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class ProviderStatus:
    """Status of an AI provider"""
    is_down: bool = False
    is_rate_limited: bool = False
    retry_after: Optional[datetime] = None
    failure_count: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None


@dataclass
class AIResponse:
    """Response from AI provider"""
    content: str
    provider: ProviderName
    model: str
    tokens_used: int
    cost: float
    latency_ms: int


class RateLimitError(Exception):
    """Rate limit error with retry info"""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class ProviderUnavailableError(Exception):
    """Provider is unavailable"""
    pass


class AllProvidersFailedError(Exception):
    """All providers failed"""
    def __init__(self, message: str, last_error: Optional[Exception], tried_providers: List[str]):
        super().__init__(message)
        self.last_error = last_error
        self.tried_providers = tried_providers


class ModelFallbackService:
    """
    Automatic fallback between AI providers.
    If OpenAI fails - switch to Anthropic and vice versa.
    """

    # Provider priority order
    PROVIDER_PRIORITY: List[Tuple[ProviderName, str, int]] = [
        # (provider, model, tier)
        (ProviderName.OPENAI, "gpt-4o", 2),
        (ProviderName.ANTHROPIC, "claude-sonnet-4-5-20250929", 2),
        (ProviderName.OPENAI, "gpt-4-turbo", 2),
        (ProviderName.ANTHROPIC, "claude-opus-4-5-20251101", 3),
        (ProviderName.OPENAI, "gpt-4o-mini", 1),  # Last resort
    ]

    # Tier-specific models
    TIER_MODELS = {
        1: [
            (ProviderName.OPENAI, "gpt-4o-mini"),
            (ProviderName.ANTHROPIC, "claude-sonnet-4-5-20250929"),
        ],
        2: [
            (ProviderName.OPENAI, "gpt-4o"),
            (ProviderName.ANTHROPIC, "claude-sonnet-4-5-20250929"),
            (ProviderName.OPENAI, "gpt-4-turbo"),
        ],
        3: [
            (ProviderName.ANTHROPIC, "claude-opus-4-5-20251101"),
            (ProviderName.OPENAI, "gpt-4"),
            (ProviderName.OPENAI, "gpt-4o"),
        ]
    }

    def __init__(self):
        self.provider_status: Dict[ProviderName, ProviderStatus] = {
            ProviderName.OPENAI: ProviderStatus(),
            ProviderName.ANTHROPIC: ProviderStatus()
        }
        self.last_health_check: Optional[datetime] = None
        self._openai_client = None
        self._anthropic_client = None

    async def generate_with_fallback(
        self,
        prompt: str,
        preferred_tier: int = 2,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """
        Generate with automatic fallback between providers.

        Args:
            prompt: The generation prompt
            preferred_tier: Preferred model tier (1, 2, or 3)
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature

        Returns:
            AIResponse with generated content

        Raises:
            AllProvidersFailedError: If all providers fail
        """
        providers_to_try = self._get_providers_for_tier(preferred_tier)
        last_error = None

        for provider, model in providers_to_try:
            # Skip if provider is down
            if self._is_provider_down(provider):
                logger.debug(f"Skipping {provider.value} - marked as down")
                continue

            try:
                start_time = datetime.now()

                response = await self._call_provider(
                    provider=provider,
                    model=model,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )

                # Calculate latency
                latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)

                # Mark provider as healthy
                self._mark_provider_healthy(provider)

                return AIResponse(
                    content=response["content"],
                    provider=provider,
                    model=model,
                    tokens_used=response.get("tokens", 0),
                    cost=response.get("cost", 0.0),
                    latency_ms=latency_ms
                )

            except RateLimitError as e:
                logger.warning(f"Rate limit on {provider.value}: {e}")

                # If retry is quick, wait and retry
                if e.retry_after and e.retry_after < 60:
                    logger.info(f"Waiting {e.retry_after}s for rate limit on {provider.value}")
                    await asyncio.sleep(e.retry_after)
                    continue
                else:
                    self._mark_provider_rate_limited(provider, e.retry_after)
                    last_error = e

            except ProviderUnavailableError as e:
                logger.error(f"Provider {provider.value} unavailable: {e}")
                self._mark_provider_down(provider)
                last_error = e

            except Exception as e:
                logger.error(f"Error with {provider.value}: {e}")
                last_error = e
                continue

        # All providers failed
        raise AllProvidersFailedError(
            message="Wszystkie providery AI są niedostępne",
            last_error=last_error,
            tried_providers=[p[0].value for p in providers_to_try]
        )

    def _get_providers_for_tier(self, tier: int) -> List[Tuple[ProviderName, str]]:
        """Get ordered list of providers for given tier."""
        return self.TIER_MODELS.get(tier, self.TIER_MODELS[2])

    def _is_provider_down(self, provider: ProviderName) -> bool:
        """Check if provider is marked as unavailable."""
        status = self.provider_status.get(provider)
        if not status:
            return False

        if status.is_down or status.is_rate_limited:
            # Check if cooldown period has passed
            if status.retry_after and datetime.now() > status.retry_after:
                # Reset status
                status.is_down = False
                status.is_rate_limited = False
                return False
            return True

        return False

    def _mark_provider_down(self, provider: ProviderName):
        """Mark provider as unavailable."""
        status = self.provider_status[provider]
        status.is_down = True
        status.failure_count += 1
        status.last_failure = datetime.now()

        # Exponential backoff for retry
        cooldown_minutes = min(30, 5 * (2 ** min(status.failure_count - 1, 3)))
        status.retry_after = datetime.now() + timedelta(minutes=cooldown_minutes)

        logger.warning(
            f"Provider {provider.value} marked as DOWN. "
            f"Retry after {cooldown_minutes} minutes. "
            f"Failure count: {status.failure_count}"
        )

    def _mark_provider_rate_limited(self, provider: ProviderName, retry_after: Optional[int]):
        """Mark provider as rate limited."""
        status = self.provider_status[provider]
        status.is_rate_limited = True

        if retry_after:
            status.retry_after = datetime.now() + timedelta(seconds=retry_after)
        else:
            status.retry_after = datetime.now() + timedelta(minutes=5)

        logger.warning(f"Provider {provider.value} rate limited. Retry after: {status.retry_after}")

    def _mark_provider_healthy(self, provider: ProviderName):
        """Mark provider as healthy after successful call."""
        status = self.provider_status[provider]
        status.is_down = False
        status.is_rate_limited = False
        status.last_success = datetime.now()
        # Reset failure count on success
        status.failure_count = max(0, status.failure_count - 1)

    async def _call_provider(
        self,
        provider: ProviderName,
        model: str,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Call specific AI provider."""
        if provider == ProviderName.OPENAI:
            return await self._call_openai(model, prompt, system_prompt, max_tokens, temperature)
        elif provider == ProviderName.ANTHROPIC:
            return await self._call_anthropic(model, prompt, system_prompt, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _call_openai(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Call OpenAI API."""
        try:
            from openai import AsyncOpenAI, RateLimitError as OpenAIRateLimitError, APIError

            if self._openai_client is None:
                self._openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await self._openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            content = response.choices[0].message.content
            tokens = response.usage.total_tokens if response.usage else 0

            # Calculate cost
            cost = self._calculate_openai_cost(model, response.usage) if response.usage else 0

            return {
                "content": content,
                "tokens": tokens,
                "cost": cost
            }

        except OpenAIRateLimitError as e:
            # Extract retry-after if available
            retry_after = getattr(e, 'retry_after', None)
            raise RateLimitError(str(e), retry_after)

        except APIError as e:
            if e.status_code and e.status_code >= 500:
                raise ProviderUnavailableError(f"OpenAI server error: {e}")
            raise

    async def _call_anthropic(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Call Anthropic API."""
        try:
            from anthropic import AsyncAnthropic, RateLimitError as AnthropicRateLimitError, APIError

            if not settings.ANTHROPIC_API_KEY:
                raise ProviderUnavailableError("Anthropic API key not configured")

            if self._anthropic_client is None:
                self._anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

            kwargs = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            # Anthropic doesn't support temperature > 1
            if temperature <= 1:
                kwargs["temperature"] = temperature

            response = await self._anthropic_client.messages.create(**kwargs)

            content = response.content[0].text if response.content else ""
            tokens = (response.usage.input_tokens + response.usage.output_tokens) if response.usage else 0

            # Calculate cost
            cost = self._calculate_anthropic_cost(model, response.usage) if response.usage else 0

            return {
                "content": content,
                "tokens": tokens,
                "cost": cost
            }

        except AnthropicRateLimitError as e:
            raise RateLimitError(str(e))

        except APIError as e:
            if hasattr(e, 'status_code') and e.status_code and e.status_code >= 500:
                raise ProviderUnavailableError(f"Anthropic server error: {e}")
            raise

    def _calculate_openai_cost(self, model: str, usage) -> float:
        """Calculate OpenAI cost."""
        # Pricing per 1M tokens
        pricing = {
            "gpt-4o": {"input": 2.50, "output": 10.0},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4-turbo": {"input": 10.0, "output": 30.0},
            "gpt-4": {"input": 30.0, "output": 60.0},
        }

        prices = pricing.get(model, pricing["gpt-4o"])
        input_cost = (usage.prompt_tokens / 1_000_000) * prices["input"]
        output_cost = (usage.completion_tokens / 1_000_000) * prices["output"]

        return input_cost + output_cost

    def _calculate_anthropic_cost(self, model: str, usage) -> float:
        """Calculate Anthropic cost."""
        # Pricing per 1M tokens
        pricing = {
            "claude-opus-4-5-20251101": {"input": 15.0, "output": 75.0},
            "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0},
        }

        prices = pricing.get(model, pricing["claude-sonnet-4-5-20250929"])
        input_cost = (usage.input_tokens / 1_000_000) * prices["input"]
        output_cost = (usage.output_tokens / 1_000_000) * prices["output"]

        return input_cost + output_cost

    async def health_check_all_providers(self) -> Dict[ProviderName, bool]:
        """Check health of all providers."""
        results = {}

        for provider in ProviderName:
            try:
                model = self.TIER_MODELS[1][0][1] if provider == ProviderName.OPENAI else self.TIER_MODELS[1][1][1]

                await self._call_provider(
                    provider=provider,
                    model=model,
                    prompt="Hello",
                    system_prompt=None,
                    max_tokens=5,
                    temperature=0.0
                )

                self._mark_provider_healthy(provider)
                results[provider] = True

            except Exception as e:
                logger.warning(f"Health check failed for {provider.value}: {e}")
                results[provider] = False

        self.last_health_check = datetime.now()
        return results

    def get_provider_status(self) -> Dict[str, Any]:
        """Get current status of all providers."""
        return {
            provider.value: {
                "is_down": status.is_down,
                "is_rate_limited": status.is_rate_limited,
                "retry_after": status.retry_after.isoformat() if status.retry_after else None,
                "failure_count": status.failure_count,
                "last_success": status.last_success.isoformat() if status.last_success else None,
                "last_failure": status.last_failure.isoformat() if status.last_failure else None
            }
            for provider, status in self.provider_status.items()
        }


# Singleton instance
_fallback_service: Optional[ModelFallbackService] = None


def get_fallback_service() -> ModelFallbackService:
    """Get or create fallback service instance."""
    global _fallback_service
    if _fallback_service is None:
        _fallback_service = ModelFallbackService()
    return _fallback_service
