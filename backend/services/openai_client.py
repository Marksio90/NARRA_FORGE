"""
Klient OpenAI API dla NarraForge.

Moduł zapewnia wrapper dla OpenAI API z:
- Automatycznym retry przy błędach
- Obsługą timeout
- Liczeniem tokenów
- Kalkulacją kosztów
- Polskimi komunikatami błędów
"""

import asyncio
from typing import Any, Optional

from openai import AsyncOpenAI, OpenAIError, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from core.config import get_settings
from core.exceptions import OpenAIError as NarraForgeOpenAIError
from core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class OpenAIClient:
    """
    Wrapper dla OpenAI API z automatycznym retry i obsługą błędów.

    Przykład użycia:
        >>> client = OpenAIClient()
        >>> odpowiedz = await client.chat_completion(
        ...     model="gpt-4o-mini",
        ...     wiadomosci=[{"role": "user", "content": "Napisz krótką historię"}]
        ... )
    """

    def __init__(self):
        """Inicjalizacja klienta OpenAI."""
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.OPENAI_TIMEOUT,
        )
        logger.info("Zainicjalizowano klienta OpenAI", timeout=settings.OPENAI_TIMEOUT)

    @retry(
        retry=retry_if_exception_type((RateLimitError, asyncio.TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def chat_completion(
        self,
        model: str,
        wiadomosci: list[dict[str, str]],
        temperatura: float = 0.7,
        max_tokeny: Optional[int] = None,
        **dodatkowe_parametry: Any,
    ) -> dict[str, Any]:
        """
        Wywołanie chat completion z automatycznym retry.

        Args:
            model: Nazwa modelu (np. "gpt-4o-mini", "gpt-4o")
            wiadomosci: Lista wiadomości w formacie OpenAI
            temperatura: Temperatura generowania (0.0-2.0)
            max_tokeny: Maksymalna liczba tokenów wyjściowych
            **dodatkowe_parametry: Dodatkowe parametry dla API

        Returns:
            dict: Odpowiedź z OpenAI API

        Raises:
            NarraForgeOpenAIError: Gdy wywołanie API się nie powiedzie
        """
        try:
            logger.info(
                "Wysyłanie żądania do OpenAI",
                model=model,
                liczba_wiadomosci=len(wiadomosci),
                temperatura=temperatura,
            )

            odpowiedz = await self.client.chat.completions.create(
                model=model,
                messages=wiadomosci,
                temperature=temperatura,
                max_tokens=max_tokeny,
                **dodatkowe_parametry,
            )

            logger.info(
                "Otrzymano odpowiedź z OpenAI",
                model=model,
                tokeny_wejsciowe=odpowiedz.usage.prompt_tokens,
                tokeny_wyjsciowe=odpowiedz.usage.completion_tokens,
                tokeny_razem=odpowiedz.usage.total_tokens,
            )

            return {
                "tresc": odpowiedz.choices[0].message.content,
                "model": odpowiedz.model,
                "tokeny_wejsciowe": odpowiedz.usage.prompt_tokens,
                "tokeny_wyjsciowe": odpowiedz.usage.completion_tokens,
                "tokeny_razem": odpowiedz.usage.total_tokens,
                "pelna_odpowiedz": odpowiedz,
            }

        except RateLimitError as e:
            logger.error(
                "Przekroczono limit żądań OpenAI - retry",
                model=model,
                error=str(e),
            )
            raise  # Retry przez tenacity

        except asyncio.TimeoutError as e:
            logger.error(
                "Timeout podczas żądania OpenAI - retry",
                model=model,
                timeout=settings.OPENAI_TIMEOUT,
            )
            raise  # Retry przez tenacity

        except OpenAIError as e:
            komunikat = f"Błąd OpenAI API: {str(e)}"
            logger.error(komunikat, model=model, typ_bledu=type(e).__name__)
            raise NarraForgeOpenAIError(
                komunikat, details={"model": model, "oryginalny_blad": str(e)}
            )

        except Exception as e:
            komunikat = f"Nieoczekiwany błąd podczas wywołania OpenAI: {str(e)}"
            logger.error(komunikat, model=model, typ_bledu=type(e).__name__)
            raise NarraForgeOpenAIError(komunikat, details={"model": model})

    async def oblicz_koszt(
        self,
        model: str,
        tokeny_wejsciowe: int,
        tokeny_wyjsciowe: int,
    ) -> float:
        """
        Oblicz koszt wywołania API.

        Args:
            model: Nazwa modelu
            tokeny_wejsciowe: Liczba tokenów wejściowych
            tokeny_wyjsciowe: Liczba tokenów wyjściowych

        Returns:
            float: Koszt w USD

        Raises:
            ValueError: Gdy model nie jest rozpoznany
        """
        try:
            koszt = settings.get_model_cost(model, tokeny_wejsciowe, tokeny_wyjsciowe)
            logger.debug(
                "Obliczono koszt",
                model=model,
                tokeny_in=tokeny_wejsciowe,
                tokeny_out=tokeny_wyjsciowe,
                koszt_usd=koszt,
            )
            return koszt
        except ValueError as e:
            logger.error("Nieznany model podczas obliczania kosztu", model=model)
            raise

    async def test_polaczenia(self) -> bool:
        """
        Testuje połączenie z OpenAI API.

        Returns:
            bool: True jeśli połączenie działa, False w przeciwnym razie
        """
        try:
            await self.chat_completion(
                model="gpt-4o-mini",
                wiadomosci=[{"role": "user", "content": "Test"}],
                max_tokeny=5,
            )
            logger.info("Test połączenia z OpenAI zakończony sukcesem")
            return True
        except Exception as e:
            logger.error("Test połączenia z OpenAI nieudany", error=str(e))
            return False


# Singleton instance
_klient: Optional[OpenAIClient] = None


def pobierz_klienta() -> OpenAIClient:
    """
    Pobiera singleton instancję klienta OpenAI.

    Returns:
        OpenAIClient: Instancja klienta
    """
    global _klient
    if _klient is None:
        _klient = OpenAIClient()
    return _klient
