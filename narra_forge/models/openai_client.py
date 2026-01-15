"""
OpenAI API Client for NARRA_FORGE V2

This is the ONLY AI backend for the system.
NO Anthropic, NO Claude, ONLY OpenAI.

Models used:
- gpt-4o-mini: Analysis, planning, validation (COST-OPTIMIZED)
- gpt-4o: Narrative generation (QUALITY-OPTIMIZED)
"""
import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

import tiktoken
from openai import AsyncOpenAI, OpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from narra_forge.core.config import NarraForgeConfig
from narra_forge.core.types import ModelCall


class OpenAIClient:
    """
    OpenAI API client with rate limiting, retries, and cost tracking.

    Features:
    - Automatic retry with exponential backoff
    - Token counting with tiktoken
    - Cost calculation
    - Rate limiting
    - Both sync and async support
    """

    # OpenAI pricing (as of 2026-01, adjust as needed)
    PRICING = {
        "gpt-4o-mini": {
            "prompt": 0.00015 / 1000,  # $0.15 per 1M tokens
            "completion": 0.0006 / 1000,  # $0.60 per 1M tokens
        },
        "gpt-4o": {
            "prompt": 0.0025 / 1000,  # $2.50 per 1M tokens
            "completion": 0.01 / 1000,  # $10.00 per 1M tokens
        },
    }

    def __init__(self, config: NarraForgeConfig):
        """
        Initialize OpenAI client.

        Args:
            config: NarraForgeConfig instance
        """
        self.config = config

        # Initialize OpenAI clients
        self.client = OpenAI(
            api_key=config.openai_api_key,
            timeout=config.api_timeout_seconds,
        )
        self.async_client = AsyncOpenAI(
            api_key=config.openai_api_key,
            timeout=config.api_timeout_seconds,
        )

        # Rate limiting state
        self._mini_calls: List[float] = []
        self._mini_tokens: List[tuple[float, int]] = []
        self._gpt4_calls: List[float] = []
        self._gpt4_tokens: List[tuple[float, int]] = []

        # Tokenizers
        self._tokenizers: Dict[str, Any] = {}

    def _get_tokenizer(self, model: str) -> Any:
        """Get tiktoken encoder for model"""
        if model not in self._tokenizers:
            try:
                self._tokenizers[model] = tiktoken.encoding_for_model(model)
            except Exception:
                # Fallback to cl100k_base (GPT-4 encoding)
                self._tokenizers[model] = tiktoken.get_encoding("cl100k_base")
        return self._tokenizers[model]

    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text for given model"""
        encoder = self._get_tokenizer(model)
        return len(encoder.encode(text))

    def calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """Calculate cost in USD"""
        if model not in self.PRICING:
            # Default to gpt-4o pricing for unknown models
            pricing = self.PRICING["gpt-4o"]
        else:
            pricing = self.PRICING[model]

        prompt_cost = prompt_tokens * pricing["prompt"]
        completion_cost = completion_tokens * pricing["completion"]
        return prompt_cost + completion_cost

    def _check_rate_limit(self, model: str, estimated_tokens: int) -> None:
        """
        Check if we're within rate limits.
        Raises ValueError if limit would be exceeded.
        """
        now = time.time()
        minute_ago = now - 60

        if "mini" in model:
            # Clean old entries
            self._mini_calls = [t for t in self._mini_calls if t > minute_ago]
            self._mini_tokens = [(t, n) for t, n in self._mini_tokens if t > minute_ago]

            # Check limits
            if len(self._mini_calls) >= self.config.mini_rpm_limit:
                raise ValueError(f"Rate limit: {self.config.mini_rpm_limit} RPM for mini")

            total_tokens = sum(n for _, n in self._mini_tokens) + estimated_tokens
            if total_tokens >= self.config.mini_tpm_limit:
                raise ValueError(f"Rate limit: {self.config.mini_tpm_limit} TPM for mini")

            # Record this call
            self._mini_calls.append(now)
            self._mini_tokens.append((now, estimated_tokens))

        else:  # gpt-4o
            # Clean old entries
            self._gpt4_calls = [t for t in self._gpt4_calls if t > minute_ago]
            self._gpt4_tokens = [(t, n) for t, n in self._gpt4_tokens if t > minute_ago]

            # Check limits
            if len(self._gpt4_calls) >= self.config.gpt4_rpm_limit:
                raise ValueError(f"Rate limit: {self.config.gpt4_rpm_limit} RPM for gpt-4o")

            total_tokens = sum(n for _, n in self._gpt4_tokens) + estimated_tokens
            if total_tokens >= self.config.gpt4_tpm_limit:
                raise ValueError(f"Rate limit: {self.config.gpt4_tpm_limit} TPM for gpt-4o")

            # Record this call
            self._gpt4_calls.append(now)
            self._gpt4_tokens.append((now, estimated_tokens))

    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        purpose: str = "generation",
        **kwargs,
    ) -> tuple[str, ModelCall]:
        """
        Synchronous generation with OpenAI.

        Args:
            prompt: User prompt
            model: Model name (defaults to config)
            system_prompt: System prompt (optional)
            temperature: Sampling temperature
            max_tokens: Max completion tokens
            purpose: What this is for (for tracking)
            **kwargs: Additional OpenAI API parameters

        Returns:
            (generated_text, model_call_record)
        """
        if model is None:
            model = self.config.default_mini_model

        # Estimate tokens for rate limiting
        estimated_tokens = self.count_tokens(prompt, model)
        if system_prompt:
            estimated_tokens += self.count_tokens(system_prompt, model)

        # Check rate limits
        self._check_rate_limit(model, estimated_tokens)

        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Call API
        start_time = time.time()

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        latency = time.time() - start_time

        # Extract response
        generated_text = response.choices[0].message.content or ""

        # Create ModelCall record
        prompt_tokens = response.usage.prompt_tokens if response.usage else 0
        completion_tokens = response.usage.completion_tokens if response.usage else 0
        total_tokens = response.usage.total_tokens if response.usage else 0

        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)

        model_call = ModelCall(
            call_id=f"call_{uuid4().hex[:12]}",
            model_name=model,
            purpose=purpose,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            latency_seconds=latency,
        )

        return generated_text, model_call

    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def generate_async(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        purpose: str = "generation",
        **kwargs,
    ) -> tuple[str, ModelCall]:
        """
        Asynchronous generation with OpenAI.
        Same as generate() but async.
        """
        if model is None:
            model = self.config.default_mini_model

        # Estimate tokens for rate limiting
        estimated_tokens = self.count_tokens(prompt, model)
        if system_prompt:
            estimated_tokens += self.count_tokens(system_prompt, model)

        # Check rate limits
        self._check_rate_limit(model, estimated_tokens)

        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Call API
        start_time = time.time()

        response = await self.async_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        latency = time.time() - start_time

        # Extract response
        generated_text = response.choices[0].message.content or ""

        # Create ModelCall record
        prompt_tokens = response.usage.prompt_tokens if response.usage else 0
        completion_tokens = response.usage.completion_tokens if response.usage else 0
        total_tokens = response.usage.total_tokens if response.usage else 0

        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)

        model_call = ModelCall(
            call_id=f"call_{uuid4().hex[:12]}",
            model_name=model,
            purpose=purpose,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            latency_seconds=latency,
        )

        return generated_text, model_call

    def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        purpose: str = "json_generation",
        **kwargs,
    ) -> tuple[Dict[str, Any], ModelCall]:
        """
        Generate structured JSON output.

        Uses OpenAI's JSON mode for reliable structured output.
        """
        text, model_call = self.generate(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            response_format={"type": "json_object"},
            purpose=purpose,
            **kwargs,
        )

        # Parse JSON
        import json

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\n\nResponse: {text}")

        return data, model_call

    async def generate_json_async(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        purpose: str = "json_generation",
        **kwargs,
    ) -> tuple[Dict[str, Any], ModelCall]:
        """
        Async version of generate_json().
        """
        text, model_call = await self.generate_async(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            response_format={"type": "json_object"},
            purpose=purpose,
            **kwargs,
        )

        # Parse JSON
        import json

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\n\nResponse: {text}")

        return data, model_call

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        now = time.time()
        minute_ago = now - 60

        mini_calls_recent = [t for t in self._mini_calls if t > minute_ago]
        mini_tokens_recent = sum(n for t, n in self._mini_tokens if t > minute_ago)
        gpt4_calls_recent = [t for t in self._gpt4_calls if t > minute_ago]
        gpt4_tokens_recent = sum(n for t, n in self._gpt4_tokens if t > minute_ago)

        return {
            "mini": {
                "calls_last_minute": len(mini_calls_recent),
                "tokens_last_minute": mini_tokens_recent,
                "rpm_limit": self.config.mini_rpm_limit,
                "tpm_limit": self.config.mini_tpm_limit,
            },
            "gpt4": {
                "calls_last_minute": len(gpt4_calls_recent),
                "tokens_last_minute": gpt4_tokens_recent,
                "rpm_limit": self.config.gpt4_rpm_limit,
                "tpm_limit": self.config.gpt4_tpm_limit,
            },
        }
