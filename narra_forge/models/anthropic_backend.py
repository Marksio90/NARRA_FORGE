"""
Anthropic (Claude) backend implementation.
"""
from typing import Dict, Any, Optional
import json
from .backend import ModelBackend, ModelResponse


class AnthropicBackend(ModelBackend):
    """Anthropic Claude implementation."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")

        # Lazy import to avoid dependency issues
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "anthropic package not installed. "
                "Install with: pip install anthropic"
            )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """Generate text using Claude."""

        temp = temperature if temperature is not None else self.config.get("temperature", 0.7)
        max_tok = max_tokens if max_tokens is not None else self.config.get("max_tokens", 4096)

        messages = [{"role": "user", "content": prompt}]

        request_params = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tok,
            "temperature": temp,
        }

        if system_prompt:
            request_params["system"] = system_prompt

        # Add any additional kwargs
        request_params.update(kwargs)

        response = self.client.messages.create(**request_params)

        content = response.content[0].text
        tokens_used = response.usage.input_tokens + response.usage.output_tokens

        # Calculate cost
        cost = tokens_used * self.config.get("cost_per_token", 0.0)

        self.update_metrics(tokens_used, cost)

        return ModelResponse(
            content=content,
            model=self.model_name,
            tokens_used=tokens_used,
            cost=cost,
            metadata={
                "stop_reason": response.stop_reason,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        )

    async def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output.
        Uses prompt engineering to enforce schema.
        """

        # Enhance prompt with schema requirements
        structured_prompt = f"""You must respond with valid JSON matching this schema:

{json.dumps(schema, indent=2)}

User request:
{prompt}

Respond with ONLY the JSON object, no additional text."""

        if system_prompt:
            enhanced_system = f"{system_prompt}\n\nIMPORTANT: Your response must be valid JSON matching the provided schema."
        else:
            enhanced_system = "You are a precise assistant that responds with valid JSON."

        response = await self.generate(
            prompt=structured_prompt,
            system_prompt=enhanced_system,
            temperature=0.3,  # Lower temperature for structured output
            **kwargs
        )

        # Parse JSON from response
        try:
            # Try to extract JSON if wrapped in markdown
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            parsed = json.loads(content.strip())
            return parsed

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response.content}")


class AnthropicExtendedBackend(AnthropicBackend):
    """
    Extended Anthropic backend with advanced features.
    Supports long context, caching, and other Claude-specific features.
    """

    async def generate_with_cache(
        self,
        prompt: str,
        cached_context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Generate with prompt caching for long contexts.
        Useful for world bibles and character databases.
        """

        messages = []

        if cached_context:
            # Add cached context as system message
            # (In real implementation, use Claude's cache_control)
            messages.append({
                "role": "user",
                "content": f"Context:\n{cached_context}\n\nRequest:\n{prompt}"
            })
        else:
            messages.append({"role": "user", "content": prompt})

        # Use standard generate for now
        # In production, implement cache_control parameter
        return await self.generate(
            prompt=messages[0]["content"],
            system_prompt=system_prompt,
            **kwargs
        )

    async def generate_long_form(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        target_length: int = 10000,
        **kwargs
    ) -> ModelResponse:
        """
        Generate long-form content with extended output.
        For narrative generation.
        """

        # Use higher max_tokens for long-form generation
        return await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=min(target_length, 8000),  # Claude's limit
            temperature=0.8,  # More creative for narrative
            **kwargs
        )
