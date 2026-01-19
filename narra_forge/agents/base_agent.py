"""
Bazowy Agent dla wszystkich wyspecjalizowanych agentów narracyjnych

Każdy z 10 agentów dziedziczy po tej klasie.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from narra_forge.core.types import ModelConfig, PipelineStage
from narra_forge.core.config import SystemConfig
from narra_forge.models.backend import ModelBackend
from narra_forge.models.factory import ModelFactory
import logging


class BaseAgent(ABC):
    """
    Abstrakcyjna klasa bazowa dla wszystkich agentów narracyjnych

    Każdy agent:
    - Ma jedną odpowiedzialność (jeden etap pipeline)
    - Działa w swoim zakresie poznawczym
    - Nie przekracza swoich kompetencji
    - Używa dedykowanego modelu LLM
    """

    def __init__(
        self,
        config: SystemConfig,
        stage: PipelineStage,
        preferred_model: Optional[str] = None
    ):
        """
        Args:
            config: Główna konfiguracja systemu
            stage: Etap pipeline, za który agent odpowiada
            preferred_model: Preferowany model (jeśli None, użyje domyślnego dla etapu)
        """
        self.config = config
        self.stage = stage
        self.logger = logging.getLogger(f"Agent.{self.__class__.__name__}")

        # Wybierz model
        stage_name = stage.name.lower()
        self.model_name = (
            preferred_model
            or config.stage_model_mapping.get(stage_name)
            or config.default_model
        )

        # Utwórz backend
        model_config = config.models.get(self.model_name)
        if not model_config:
            raise ValueError(f"Model {self.model_name} not found in config")

        self.backend: ModelBackend = ModelFactory.create_backend(model_config)

        self.logger.info(
            f"Initialized {self.__class__.__name__} with model {self.model_name}"
        )

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wykonaj zadanie agenta

        Args:
            context: Kontekst z poprzednich etapów (wszystkie dane dotychczas wygenerowane)

        Returns:
            Wynik działania agenta (zostanie dodany do kontekstu)

        Raises:
            Exception: Jeśli nie może wykonać zadania
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Zwróć system prompt dla tego agenta

        To jest "tożsamość" agenta - definiuje jego rolę i odpowiedzialność.

        Returns:
            System prompt (po polsku!)
        """
        pass

    async def _generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> str:
        """
        Wygeneruj odpowiedź z modelu

        Args:
            prompt: Prompt dla modelu
            temperature: Temperature override
            max_tokens: Max tokens override
            json_mode: Czy wymagać JSON

        Returns:
            Wygenerowany tekst
        """
        system_prompt = self.get_system_prompt()

        try:
            result = await self.backend.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode,
            )
            return result

        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            raise

    def _extract_from_context(
        self,
        context: Dict[str, Any],
        key: str,
        required: bool = True
    ) -> Any:
        """
        Wyciągnij wartość z kontekstu z walidacją

        Args:
            context: Kontekst
            key: Klucz do wyciągnięcia
            required: Czy klucz jest wymagany

        Returns:
            Wartość lub None (jeśli not required)

        Raises:
            ValueError: Jeśli required=True i klucz nie istnieje
        """
        if key not in context:
            if required:
                raise ValueError(
                    f"{self.__class__.__name__} requires '{key}' in context, "
                    f"but it was not found. Available keys: {list(context.keys())}"
                )
            return None

        return context[key]

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Waliduj output agenta (override w subklasach jeśli potrzeba)

        Args:
            output: Output do walidacji

        Returns:
            True jeśli valid, False w przeciwnym razie
        """
        return output is not None and len(output) > 0
