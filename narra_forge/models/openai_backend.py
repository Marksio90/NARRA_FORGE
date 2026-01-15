"""
OpenAI (GPT-4) backend implementation.
"""
from typing import Dict, Any, Optional
import json
from .backend import ModelBackend, ModelResponse


class OpenAIBackend(ModelBackend):
    """OpenAI GPT implementation."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")

        # Lazy import to avoid dependency issues
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "openai package not installed. "
                "Install with: pip install openai"
            )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """Generate text using GPT."""

        temp = temperature if temperature is not None else self.config.get("temperature", 0.7)
        max_tok = max_tokens if max_tokens is not None else self.config.get("max_tokens", 4096)

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        request_params = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tok,
            "temperature": temp,
        }

        # Add any additional kwargs
        request_params.update(kwargs)

        response = self.client.chat.completions.create(**request_params)

        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        # Calculate cost
        cost = tokens_used * self.config.get("cost_per_token", 0.0)

        self.update_metrics(tokens_used, cost)

        return ModelResponse(
            content=content,
            model=self.model_name,
            tokens_used=tokens_used,
            cost=cost,
            metadata={
                "finish_reason": response.choices[0].finish_reason,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens
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


class OpenAIExtendedBackend(OpenAIBackend):
    """
    Extended OpenAI backend with advanced features.
    Supports function calling and other GPT-specific features.
    """

    async def generate_with_functions(
        self,
        prompt: str,
        functions: list,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Generate with function calling capability.
        Useful for structured outputs and tool use.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            functions=functions,
            temperature=self.config.get("temperature", 0.7),
            **kwargs
        )

        content = response.choices[0].message.content or ""
        function_call = response.choices[0].message.function_call

        tokens_used = response.usage.total_tokens
        cost = tokens_used * self.config.get("cost_per_token", 0.0)

        self.update_metrics(tokens_used, cost)

        return ModelResponse(
            content=content,
            model=self.model_name,
            tokens_used=tokens_used,
            cost=cost,
            metadata={
                "finish_reason": response.choices[0].finish_reason,
                "function_call": function_call
            }
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
            max_tokens=min(target_length, 4096),  # GPT-4 limit
            temperature=0.8,  # More creative for narrative
            **kwargs
        )
