"""
OpenAI API client wrapper.
"""
from openai import AsyncOpenAI
from app.config import settings
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class OpenAIResponse:
    """OpenAI response wrapper."""

    def __init__(self, content: str, input_tokens: int, output_tokens: int, model: str):
        self.content = content
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.model = model


class OpenAIClient:
    """
    Wrapper for OpenAI API calls.
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def complete(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> OpenAIResponse:
        """
        Complete a chat request.

        Args:
            model: Model to use (e.g., 'gpt-4o-mini', 'gpt-4o', 'o1', 'o1-pro')
            system_prompt: System instruction
            user_prompt: User message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            OpenAIResponse with content and token counts
        """
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            logger.debug(f"OpenAI request: model={model}, temperature={temperature}")

            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens

            logger.debug(
                f"OpenAI response: input_tokens={input_tokens}, "
                f"output_tokens={output_tokens}"
            )

            return OpenAIResponse(
                content=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=model
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (1536 dimensions)
        """
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise
