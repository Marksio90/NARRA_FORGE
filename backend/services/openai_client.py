"""OpenAI API client with retry logic and cost tracking."""

import logging
import time
import uuid
from typing import Any

import openai
from openai import AsyncOpenAI

from core.config import settings
from core.exceptions import TokenBudgetExceededError

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI API client with retry logic, timeout handling, and cost tracking."""

    # Model-specific timeouts (seconds)
    TIMEOUT_MINI = 30
    TIMEOUT_HIGH = 120

    # Retry configuration
    MAX_RETRIES = 3
    INITIAL_BACKOFF = 1.0  # seconds
    MAX_BACKOFF = 60.0  # seconds

    # Cost per 1M tokens (as of 2026-01, approximate values)
    COST_PER_1M_TOKENS = {
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4o": {"input": 2.50, "output": 10.00},
    }

    def __init__(self) -> None:
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    def _get_timeout(self, model: str) -> int:
        """Get timeout based on model type."""
        if "mini" in model:
            return self.TIMEOUT_MINI
        return self.TIMEOUT_HIGH

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD for a request."""
        if model not in self.COST_PER_1M_TOKENS:
            logger.warning(f"Unknown model for cost calculation: {model}")
            return 0.0

        costs = self.COST_PER_1M_TOKENS[model]
        input_cost = (input_tokens / 1_000_000) * costs["input"]
        output_cost = (output_tokens / 1_000_000) * costs["output"]
        return input_cost + output_cost

    async def chat_completion(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        token_budget: int | None = None,
    ) -> dict[str, Any]:
        """
        Send chat completion request with retry logic and cost tracking.

        Args:
            model: Model name (e.g., "gpt-4o-mini", "gpt-4o")
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            token_budget: Maximum allowed tokens for this request

        Returns:
            Dictionary with:
                - content: Generated text
                - usage: Token usage dict (prompt_tokens, completion_tokens, total_tokens)
                - cost: Estimated cost in USD
                - model: Model used
                - request_id: Unique request identifier

        Raises:
            TokenBudgetExceededError: If token usage exceeds budget
            openai.OpenAIError: If API request fails after retries
        """
        request_id = str(uuid.uuid4())
        timeout = self._get_timeout(model)
        backoff = self.INITIAL_BACKOFF

        logger.info(
            "OpenAI request started",
            extra={
                "request_id": request_id,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "token_budget": token_budget,
            },
        )

        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,  # type: ignore[arg-type]  # OpenAI SDK type is too strict
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout,
                    extra_headers={"X-Request-ID": request_id},
                )

                # Extract response data
                choice = response.choices[0]
                content = choice.message.content or ""
                usage = response.usage

                if usage is None:
                    logger.warning(f"No usage data returned for request {request_id}")
                    prompt_tokens = 0
                    completion_tokens = 0
                    total_tokens = 0
                else:
                    prompt_tokens = usage.prompt_tokens
                    completion_tokens = usage.completion_tokens
                    total_tokens = usage.total_tokens

                # Check token budget
                if token_budget is not None and total_tokens > token_budget:
                    logger.error(
                        f"Token budget exceeded: {total_tokens} > {token_budget}",
                        extra={"request_id": request_id},
                    )
                    raise TokenBudgetExceededError(
                        f"Token usage {total_tokens} exceeds budget {token_budget}"
                    )

                # Calculate cost
                cost = self._calculate_cost(model, prompt_tokens, completion_tokens)

                logger.info(
                    "OpenAI request successful",
                    extra={
                        "request_id": request_id,
                        "model": model,
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                        "cost_usd": round(cost, 6),
                    },
                )

                return {
                    "content": content,
                    "usage": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                    },
                    "cost": cost,
                    "model": model,
                    "request_id": request_id,
                }

            except openai.RateLimitError as e:
                logger.warning(
                    f"Rate limit error (attempt {attempt + 1}/{self.MAX_RETRIES})",
                    extra={"request_id": request_id, "error": str(e)},
                )
                if attempt < self.MAX_RETRIES - 1:
                    sleep_time = min(backoff, self.MAX_BACKOFF)
                    logger.info(f"Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                    backoff *= 2
                else:
                    logger.error(f"Max retries exceeded for request {request_id}")
                    raise

            except openai.APITimeoutError:
                logger.warning(
                    f"Timeout error (attempt {attempt + 1}/{self.MAX_RETRIES})",
                    extra={"request_id": request_id, "timeout": timeout},
                )
                if attempt < self.MAX_RETRIES - 1:
                    sleep_time = min(backoff, self.MAX_BACKOFF)
                    logger.info(f"Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                    backoff *= 2
                else:
                    logger.error(f"Max retries exceeded for request {request_id}")
                    raise

            except openai.APIConnectionError as e:
                logger.warning(
                    f"Connection error (attempt {attempt + 1}/{self.MAX_RETRIES})",
                    extra={"request_id": request_id, "error": str(e)},
                )
                if attempt < self.MAX_RETRIES - 1:
                    sleep_time = min(backoff, self.MAX_BACKOFF)
                    logger.info(f"Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                    backoff *= 2
                else:
                    logger.error(f"Max retries exceeded for request {request_id}")
                    raise

            except openai.OpenAIError as e:
                logger.error(
                    "OpenAI API error",
                    extra={"request_id": request_id, "error": str(e), "type": type(e).__name__},
                )
                raise

        # Should never reach here due to raise in last attempt
        raise openai.OpenAIError("Unexpected: retries exhausted without raising")
