"""
Anthropic Backend (Claude Opus, Sonnet, Haiku)
"""

from typing import Dict, List, Optional
from narra_forge.models.backend import ModelBackend
from narra_forge.core.types import ModelConfig


class AnthropicBackend(ModelBackend):
    """Backend dla modeli Claude (Opus, Sonnet, Haiku)"""

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Inicjalizuj klienta Anthropic"""
        try:
            import anthropic
            if self.api_key:
                self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
            else:
                print(f"⚠️ WARNING: No API key for Anthropic. Set {self.config.api_key_env}")
        except ImportError:
            print("⚠️ WARNING: 'anthropic' package not installed. Run: pip install anthropic")

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
        Generuj odpowiedź z Claude

        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Temperature (0.0-1.0)
            max_tokens: Max tokens to generate
            json_mode: Force JSON output (via prompt)
            **kwargs: Additional Anthropic params

        Returns:
            Generated text
        """
        if not self.client:
            raise RuntimeError("Anthropic client not initialized. Check API key.")

        # Claude używa messages format
        messages = [{"role": "user", "content": prompt}]

        # Parametry
        params = {
            "model": self.config.model_name,
            "max_tokens": self._get_max_tokens(max_tokens),
            "temperature": self._get_temperature(temperature),
            "messages": messages,
        }

        # System prompt (Claude ma dedykowane pole)
        if system_prompt:
            system_content = system_prompt
            if json_mode:
                system_content += "\n\nYou MUST respond with valid JSON only."
            params["system"] = system_content
        elif json_mode:
            params["system"] = "You MUST respond with valid JSON only."

        # Dodatkowe parametry
        params.update(kwargs)

        try:
            response = await self.client.messages.create(**params)
            return response.content[0].text

        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")

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
            messages: Lista [{"role": "user/assistant", "content": "..."}]
                     (Claude nie używa "system" w messages, tylko w params)
            temperature: Temperature override
            max_tokens: Max tokens override

        Returns:
            Generated text
        """
        if not self.client:
            raise RuntimeError("Anthropic client not initialized. Check API key.")

        # Wyodrębnij system message jeśli istnieje
        system_prompt = None
        filtered_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                filtered_messages.append(msg)

        params = {
            "model": self.config.model_name,
            "max_tokens": self._get_max_tokens(max_tokens),
            "temperature": self._get_temperature(temperature),
            "messages": filtered_messages,
        }

        if system_prompt:
            params["system"] = system_prompt

        params.update(kwargs)

        try:
            response = await self.client.messages.create(**params)
            return response.content[0].text

        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")
