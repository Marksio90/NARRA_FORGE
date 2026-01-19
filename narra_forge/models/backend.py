"""
Abstrakcyjna warstwa dla LLM backends

Model-agnostic architecture - łatwo dodać nowe modele (OpenAI, Anthropic, lokalne, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from narra_forge.core.types import ModelConfig
import json


class ModelBackend(ABC):
    """
    Abstrakcyjna klasa bazowa dla wszystkich backends LLM

    Każdy provider (OpenAI, Anthropic, lokalny) implementuje tę klasę.
    """

    def __init__(self, config: ModelConfig):
        self.config = config
        self.api_key = self._load_api_key()

    @abstractmethod
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
        Generuj odpowiedź z modelu

        Args:
            prompt: Główny prompt użytkownika
            system_prompt: System prompt (opcjonalny)
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            json_mode: Czy wymagać JSON output
            **kwargs: Dodatkowe parametry specyficzne dla providera

        Returns:
            Wygenerowany tekst
        """
        pass

    @abstractmethod
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
            messages: Lista wiadomości [{"role": "user/assistant", "content": "..."}]
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            Wygenerowany tekst
        """
        pass

    def _load_api_key(self) -> Optional[str]:
        """Załaduj klucz API ze zmiennej środowiskowej"""
        import os
        return os.getenv(self.config.api_key_env)

    def _get_temperature(self, override: Optional[float] = None) -> float:
        """Zwróć temperature (override lub default)"""
        return override if override is not None else self.config.temperature

    def _get_max_tokens(self, override: Optional[int] = None) -> int:
        """Zwróć max_tokens (override lub default)"""
        return override if override is not None else self.config.max_tokens

    def validate_api_key(self) -> bool:
        """Sprawdź, czy klucz API jest dostępny"""
        return self.api_key is not None and len(self.api_key) > 0

    async def test_connection(self) -> bool:
        """
        Testuj połączenie z API

        Returns:
            True jeśli działa, False w przeciwnym razie
        """
        try:
            result = await self.generate("Test", max_tokens=10)
            return len(result) > 0
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


class DummyBackend(ModelBackend):
    """
    Dummy backend do testów (bez wywołań API)
    """

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
        **kwargs
    ) -> str:
        """Zwraca dummy response"""
        if json_mode:
            return json.dumps({"result": "dummy", "prompt_length": len(prompt)})
        return f"[DUMMY RESPONSE to prompt of {len(prompt)} chars]"

    async def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Zwraca dummy response"""
        return f"[DUMMY RESPONSE to {len(messages)} messages]"
