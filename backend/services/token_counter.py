"""Token counting utilities using tiktoken."""

import logging
from functools import lru_cache

import tiktoken

logger = logging.getLogger(__name__)


class TokenCounter:
    """Utility for counting tokens using tiktoken."""

    # Model to encoding mapping (as of 2026-01)
    MODEL_ENCODINGS = {
        "gpt-4o": "o200k_base",
        "gpt-4o-mini": "o200k_base",
        "gpt-4": "cl100k_base",
        "gpt-4-turbo": "cl100k_base",
        "gpt-3.5-turbo": "cl100k_base",
    }

    @staticmethod
    @lru_cache(maxsize=8)
    def _get_encoding(model: str) -> tiktoken.Encoding:
        """
        Get tiktoken encoding for a model.

        Args:
            model: Model name

        Returns:
            tiktoken.Encoding instance

        Note:
            Results are cached for performance
        """
        encoding_name = TokenCounter.MODEL_ENCODINGS.get(model, "o200k_base")
        logger.debug(f"Using encoding '{encoding_name}' for model '{model}'")
        return tiktoken.get_encoding(encoding_name)

    @staticmethod
    def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
        """
        Count tokens in a text string.

        Args:
            text: Text to count tokens for
            model: Model name (for selecting appropriate encoding)

        Returns:
            Number of tokens
        """
        encoding = TokenCounter._get_encoding(model)
        return len(encoding.encode(text))

    @staticmethod
    def count_message_tokens(messages: list[dict[str, str]], model: str = "gpt-4o-mini") -> int:
        """
        Count tokens in a list of chat messages.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name

        Returns:
            Estimated number of tokens

        Note:
            This is an approximation based on OpenAI's token counting.
            The actual token count may vary slightly.
        """
        encoding = TokenCounter._get_encoding(model)
        num_tokens = 0

        # Base tokens per message
        tokens_per_message = 3  # <|start|>role<|message|>content<|end|>
        tokens_per_name = 1  # If name is present

        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(str(value)))
                if key == "name":
                    num_tokens += tokens_per_name

        # Add base tokens for completion
        num_tokens += 3  # <|start|>assistant<|message|>

        return num_tokens

    @staticmethod
    def estimate_cost(prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """
        Estimate cost for a request.

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            model: Model name

        Returns:
            Estimated cost in USD

        Note:
            Cost rates are hardcoded and may become outdated.
            For production, consider fetching rates from a configuration service.
        """
        # Cost per 1M tokens (as of 2026-01)
        COST_PER_1M = {
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4o": {"input": 2.50, "output": 10.00},
        }

        if model not in COST_PER_1M:
            logger.warning(f"Unknown model for cost estimation: {model}")
            return 0.0

        costs = COST_PER_1M[model]
        input_cost = (prompt_tokens / 1_000_000) * costs["input"]
        output_cost = (completion_tokens / 1_000_000) * costs["output"]

        return input_cost + output_cost

    @staticmethod
    def check_budget(
        text: str,
        budget: int,
        model: str = "gpt-4o-mini",
        allow_margin: float = 0.1,
    ) -> tuple[bool, int]:
        """
        Check if text fits within token budget.

        Args:
            text: Text to check
            budget: Token budget
            model: Model name
            allow_margin: Safety margin (0.1 = 10%)

        Returns:
            Tuple of (fits_within_budget, actual_token_count)
        """
        token_count = TokenCounter.count_tokens(text, model)
        effective_budget = int(budget * (1 - allow_margin))
        fits = token_count <= effective_budget

        if not fits:
            logger.warning(
                f"Text exceeds budget: {token_count} tokens > {effective_budget} "
                f"(budget={budget}, margin={allow_margin})"
            )

        return fits, token_count
