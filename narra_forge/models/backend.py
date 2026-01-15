"""
Model backend abstraction layer.
Provides unified interface for different LLM providers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time


@dataclass
class ModelResponse:
    """Standardized response from any model."""
    content: str
    model: str
    tokens_used: int
    cost: float
    metadata: Dict[str, Any]


class ModelBackend(ABC):
    """Abstract base class for all model backends."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get("provider")
        self.model_name = config.get("model_name")
        self.total_tokens = 0
        self.total_cost = 0.0

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Generate text from the model.

        Args:
            prompt: User prompt
            system_prompt: System prompt for instruction
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model-specific parameters

        Returns:
            ModelResponse with generated content
        """
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured output (JSON) matching a schema.

        Args:
            prompt: User prompt
            schema: Expected output schema
            system_prompt: System prompt
            **kwargs: Additional parameters

        Returns:
            Parsed structured data
        """
        pass

    def update_metrics(self, tokens: int, cost: float):
        """Track usage metrics."""
        self.total_tokens += tokens
        self.total_cost += cost

    def get_metrics(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "provider": self.provider,
            "model": self.model_name
        }


class ModelOrchestrator:
    """
    Orchestrates multiple model backends.
    Handles selection, fallback, and cost optimization.
    """

    def __init__(self, backends: Dict[str, ModelBackend], default: str):
        self.backends = backends
        self.default_backend = default
        self.request_count = 0

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        preferred_model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        retry_on_failure: bool = True,
        **kwargs
    ) -> ModelResponse:
        """
        Generate using preferred model with automatic fallback.

        Args:
            prompt: User prompt
            system_prompt: System instruction
            preferred_model: Preferred backend name
            temperature: Sampling temperature
            max_tokens: Max tokens
            retry_on_failure: Enable fallback on failure
            **kwargs: Additional parameters

        Returns:
            ModelResponse from successful backend
        """
        model_name = preferred_model or self.default_backend

        if model_name not in self.backends:
            model_name = self.default_backend

        backend = self.backends[model_name]
        self.request_count += 1

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                response = await backend.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                return response

            except Exception as e:
                retry_count += 1
                print(f"Error with {model_name} (attempt {retry_count}): {e}")

                if retry_on_failure and retry_count < max_retries:
                    # Try fallback model if configured
                    fallback = backend.config.get("fallback_to")
                    if fallback and fallback in self.backends:
                        print(f"Falling back to {fallback}")
                        backend = self.backends[fallback]
                        model_name = fallback
                    else:
                        # Wait before retry
                        time.sleep(2 ** retry_count)
                else:
                    raise

        raise Exception(f"Failed after {max_retries} attempts")

    async def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        preferred_model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate structured output with fallback."""
        model_name = preferred_model or self.default_backend

        if model_name not in self.backends:
            model_name = self.default_backend

        backend = self.backends[model_name]

        try:
            return await backend.generate_structured(
                prompt=prompt,
                schema=schema,
                system_prompt=system_prompt,
                **kwargs
            )
        except Exception as e:
            # Fallback logic
            fallback = backend.config.get("fallback_to")
            if fallback and fallback in self.backends:
                print(f"Structured generation failed, trying {fallback}")
                return await self.backends[fallback].generate_structured(
                    prompt=prompt,
                    schema=schema,
                    system_prompt=system_prompt,
                    **kwargs
                )
            raise

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics from all backends."""
        return {
            name: backend.get_metrics()
            for name, backend in self.backends.items()
        }

    def select_optimal_model(
        self,
        task_complexity: str,
        cost_priority: bool = False
    ) -> str:
        """
        Select optimal model based on task requirements.

        Args:
            task_complexity: "low", "medium", "high", "critical"
            cost_priority: Prefer cheaper models

        Returns:
            Model backend name
        """
        if task_complexity == "critical":
            return "claude-opus"
        elif task_complexity == "high":
            return "claude-sonnet"
        elif task_complexity == "medium":
            return "claude-sonnet" if not cost_priority else "claude-haiku"
        else:  # low
            return "claude-haiku"
