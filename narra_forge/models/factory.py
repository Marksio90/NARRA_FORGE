"""
Factory do tworzenia model backends

Automatycznie wybiera odpowiedni backend na podstawie providera.
"""

from typing import Dict
from narra_forge.core.types import ModelConfig
from narra_forge.models.backend import ModelBackend, DummyBackend
from narra_forge.models.openai_backend import OpenAIBackend
from narra_forge.models.anthropic_backend import AnthropicBackend


class ModelFactory:
    """
    Factory do tworzenia backends dla różnych providerów

    Automatycznie wybiera odpowiednią implementację na podstawie providera.
    """

    _backends: Dict[str, type] = {
        "openai": OpenAIBackend,
        "anthropic": AnthropicBackend,
        "dummy": DummyBackend,
    }

    @classmethod
    def create_backend(cls, config: ModelConfig) -> ModelBackend:
        """
        Utwórz backend dla danego modelu

        Args:
            config: Konfiguracja modelu

        Returns:
            Zainicjalizowany backend

        Raises:
            ValueError: Jeśli provider nie jest wspierany
        """
        provider = config.provider.lower()

        if provider not in cls._backends:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported: {list(cls._backends.keys())}"
            )

        backend_class = cls._backends[provider]
        return backend_class(config)

    @classmethod
    def register_backend(cls, provider: str, backend_class: type):
        """
        Zarejestruj nowy backend (dla custom providerów)

        Args:
            provider: Nazwa providera (np. "local", "huggingface")
            backend_class: Klasa implementująca ModelBackend

        Example:
            ModelFactory.register_backend("local", LocalLLMBackend)
        """
        if not issubclass(backend_class, ModelBackend):
            raise ValueError("backend_class must inherit from ModelBackend")

        cls._backends[provider] = backend_class
        print(f"✅ Registered backend: {provider} -> {backend_class.__name__}")

    @classmethod
    def list_providers(cls) -> list:
        """Zwróć listę wspieranych providerów"""
        return list(cls._backends.keys())
