"""
OpenAI Backend (GPT-4, GPT-3.5-turbo, etc.)
"""

from typing import Dict, List, Optional
from narra_forge.models.backend import ModelBackend
from narra_forge.core.types import ModelConfig
import asyncio


class OpenAIBackend(ModelBackend):
    """Backend dla modeli OpenAI (GPT-4, GPT-3.5-turbo)"""

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Inicjalizuj klienta OpenAI"""
        try:
            import openai
            if self.api_key:
                self.client = openai.AsyncOpenAI(api_key=self.api_key)
            else:
                print(f"⚠️ WARNING: No API key for OpenAI. Set {self.config.api_key_env}")
        except ImportError:
            print("⚠️ WARNING: 'openai' package not installed. Run: pip install openai")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
        **kwargs
    ) -> str:
        """
        Generuj odpowiedź z OpenAI

        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Temperature (0.0-2.0)
            max_tokens: Max tokens to generate
            json_mode: Force JSON output
            **kwargs: Additional OpenAI params

        Returns:
            Generated text
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        # Parametry
        params = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": self._get_temperature(temperature),
            "max_tokens": self._get_max_tokens(max_tokens),
            "top_p": self.config.top_p,
        }

        # JSON mode (tylko dla niektórych modeli)
        if json_mode and self.config.supports_json_mode:
            params["response_format"] = {"type": "json_object"}
            # Dodaj instrukcję JSON do systemu
            if not system_prompt:
                params["messages"].insert(0, {
                    "role": "system",
                    "content": "You must respond with valid JSON."
                })

        # Dodatkowe parametry
        params.update(kwargs)

        try:
            response = await self.client.chat.completions.create(**params)
            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    async def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generuj z historią konwersacji

        Args:
            messages: Lista [{"role": "user/assistant/system", "content": "..."}]
            temperature: Temperature override
            max_tokens: Max tokens override

        Returns:
            Generated text
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")

        params = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": self._get_temperature(temperature),
            "max_tokens": self._get_max_tokens(max_tokens),
            "top_p": self.config.top_p,
        }

        params.update(kwargs)

        try:
            response = await self.client.chat.completions.create(**params)
            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")
