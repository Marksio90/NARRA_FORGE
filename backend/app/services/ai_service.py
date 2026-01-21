"""
Professional AI Service for NarraForge
Supports OpenAI (GPT-4o, GPT-4o-mini) and Anthropic (Claude) models
with cost tracking, retry logic, and tier management
"""

import openai
import anthropic
import logging
import time
import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

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
    """Track generation metrics"""
    total_tokens: int = 0
    total_cost: float = 0.0
    calls_made: int = 0
    errors: int = 0


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

        # Initialize OpenAI
        logger.info("✅ Initializing OpenAI client")
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        # Initialize Anthropic (if key is available)
        self.anthropic_client = None
        anthropic_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
        if anthropic_key and anthropic_key != "sk-placeholder-add-your-key":
            logger.info("✅ Initializing Anthropic client")
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
        else:
            logger.warning("⚠️ ANTHROPIC_API_KEY not set - Claude models will not be available")

        # Metrics tracking
        self.metrics = GenerationMetrics()

        logger.info("AI Service initialized")

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
            # Tier 3: Premium quality
            if prefer_anthropic and self.anthropic_client:
                return "claude-opus-4-5-20251101", ModelProvider.ANTHROPIC
            return settings.GPT_4, ModelProvider.OPENAI

    def _calculate_cost(self, tokens_in: int, tokens_out: int, tier: ModelTier) -> float:
        """Calculate cost based on token usage and tier"""
        if tier == ModelTier.TIER_1:
            input_cost = settings.TIER1_INPUT_COST
            output_cost = settings.TIER1_OUTPUT_COST
        elif tier == ModelTier.TIER_2:
            input_cost = settings.TIER2_INPUT_COST
            output_cost = settings.TIER2_OUTPUT_COST
        else:  # TIER_3
            input_cost = settings.TIER3_INPUT_COST
            output_cost = settings.TIER3_OUTPUT_COST

        cost = (tokens_in / 1_000_000) * input_cost + (tokens_out / 1_000_000) * output_cost
        return round(cost, 6)

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
        metadata: Optional[Dict[str, Any]] = None
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

        Returns:
            AIResponse with generated content and metrics
        """
        model, provider = self._get_model_for_tier(tier, prefer_anthropic)

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
                        max_tokens=max_tokens,
                        json_mode=json_mode
                    )
                else:  # Anthropic
                    response = await self._call_anthropic(
                        model=model,
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )

                # Calculate metrics
                latency = time.time() - start_time
                cost = self._calculate_cost(
                    response['tokens_in'],
                    response['tokens_out'],
                    tier
                )

                # Update global metrics
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

            except Exception as e:
                last_error = e
                self.metrics.errors += 1
                logger.warning(
                    f"AI generation attempt {attempt + 1}/{retry_count} failed: {str(e)}"
                )

                if attempt < retry_count - 1:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)  # ✅ FIXED: Non-blocking async sleep

        # All retries failed
        logger.error(f"AI generation failed after {retry_count} attempts: {last_error}")
        raise Exception(f"AI generation failed: {last_error}")

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

        response = self.openai_client.chat.completions.create(**kwargs)

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
        max_tokens: int
    ) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        if not self.anthropic_client:
            raise Exception("Anthropic client not initialized (missing API key)")

        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.anthropic_client.messages.create(**kwargs)

        # Validate response structure
        if not response.content or len(response.content) == 0:
            raise Exception("Anthropic API returned empty response")

        if not hasattr(response.content[0], 'text') or not response.content[0].text:
            raise Exception("Anthropic API returned no text in response")

        return {
            'content': response.content[0].text,
            'tokens_in': response.usage.input_tokens,
            'tokens_out': response.usage.output_tokens,
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
