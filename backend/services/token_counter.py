"""
Licznik tokenów dla NarraForge.

Moduł wykorzystuje tiktoken do precyzyjnego liczenia tokenów
dla różnych modeli OpenAI przed wysłaniem żądania do API.
"""

from functools import lru_cache
from typing import Optional

import tiktoken

from core.logging import get_logger

logger = get_logger(__name__)


class TokenCounter:
    """
    Licznik tokenów dla modeli OpenAI.

    Używa tiktoken do dokładnego oszacowania liczby tokenów
    przed wysłaniem żądania do API.

    Przykład użycia:
        >>> counter = TokenCounter()
        >>> tokeny = counter.policz_tokeny("Cześć, jak się masz?", model="gpt-4o")
        >>> print(tokeny)  # np. 5
    """

    def __init__(self):
        """Inicjalizacja licznika tokenów."""
        self._cache_encoding: dict[str, tiktoken.Encoding] = {}
        logger.info("Zainicjalizowano licznik tokenów")

    @lru_cache(maxsize=10)
    def _pobierz_encoding(self, model: str) -> tiktoken.Encoding:
        """
        Pobiera encoding dla modelu (z cache).

        Args:
            model: Nazwa modelu OpenAI

        Returns:
            tiktoken.Encoding: Encoding dla modelu
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
            logger.debug("Załadowano encoding dla modelu", model=model)
            return encoding
        except KeyError:
            # Fallback dla nieznanych modeli - używamy cl100k_base (GPT-4)
            logger.warning(
                "Nieznany model, używam cl100k_base encoding",
                model=model,
            )
            return tiktoken.get_encoding("cl100k_base")

    def policz_tokeny(
        self,
        tekst: str,
        model: str = "gpt-4o",
    ) -> int:
        """
        Liczy tokeny w tekście dla danego modelu.

        Args:
            tekst: Tekst do policzenia
            model: Nazwa modelu OpenAI

        Returns:
            int: Liczba tokenów
        """
        encoding = self._pobierz_encoding(model)
        tokeny = len(encoding.encode(tekst))

        logger.debug(
            "Policzono tokeny",
            model=model,
            dlugosc_tekstu=len(tekst),
            liczba_tokenow=tokeny,
        )

        return tokeny

    def policz_tokeny_wiadomosci(
        self,
        wiadomosci: list[dict[str, str]],
        model: str = "gpt-4o",
    ) -> dict[str, int]:
        """
        Liczy tokeny w liście wiadomości chat.

        Uwzględnia narzut tokenów dla formatowania wiadomości
        w formacie OpenAI Chat API.

        Args:
            wiadomosci: Lista wiadomości w formacie OpenAI
            model: Nazwa modelu

        Returns:
            dict: Słownik z liczbą tokenów per wiadomość i razem
        """
        encoding = self._pobierz_encoding(model)

        # Bazowa liczba tokenów dla formatowania
        # (różni się między modelami, używamy przybliżenia)
        tokeny_na_wiadomosc = 4  # <|start|>role<|message|>content<|end|>
        tokeny_na_odpowiedz = 3  # <|start|>assistant<|message|>

        liczba_tokenow = 0
        tokeny_per_wiadomosc = []

        for wiadomosc in wiadomosci:
            tokeny_wiadomosci = tokeny_na_wiadomosc
            for klucz, wartosc in wiadomosc.items():
                tokeny_wiadomosci += len(encoding.encode(wartosc))

            liczba_tokenow += tokeny_wiadomosci
            tokeny_per_wiadomosc.append(tokeny_wiadomosci)

        # Dodaj tokeny na odpowiedź
        liczba_tokenow += tokeny_na_odpowiedz

        logger.debug(
            "Policzono tokeny wiadomości",
            model=model,
            liczba_wiadomosci=len(wiadomosci),
            tokeny_razem=liczba_tokenow,
        )

        return {
            "tokeny_razem": liczba_tokenow,
            "tokeny_per_wiadomosc": tokeny_per_wiadomosc,
            "liczba_wiadomosci": len(wiadomosci),
        }

    def szacuj_koszt_tekstu(
        self,
        tekst: str,
        model: str = "gpt-4o",
        cena_za_milion_input: float = 2.50,
        cena_za_milion_output: float = 10.00,
        szacowane_tokeny_output: Optional[int] = None,
    ) -> dict[str, float]:
        """
        Szacuje koszt przetworzenia tekstu.

        Args:
            tekst: Tekst wejściowy
            model: Nazwa modelu
            cena_za_milion_input: Cena za 1M tokenów wejściowych (USD)
            cena_za_milion_output: Cena za 1M tokenów wyjściowych (USD)
            szacowane_tokeny_output: Szacowana liczba tokenów wyjściowych
                (jeśli None, zakładamy tyle samo co input)

        Returns:
            dict: Słownik z szacowanym kosztem
        """
        tokeny_input = self.policz_tokeny(tekst, model)

        if szacowane_tokeny_output is None:
            tokeny_output = tokeny_input
        else:
            tokeny_output = szacowane_tokeny_output

        koszt_input = (tokeny_input * cena_za_milion_input) / 1_000_000
        koszt_output = (tokeny_output * cena_za_milion_output) / 1_000_000
        koszt_razem = koszt_input + koszt_output

        logger.debug(
            "Oszacowano koszt",
            model=model,
            tokeny_input=tokeny_input,
            tokeny_output=tokeny_output,
            koszt_usd=koszt_razem,
        )

        return {
            "tokeny_input": tokeny_input,
            "tokeny_output": tokeny_output,
            "tokeny_razem": tokeny_input + tokeny_output,
            "koszt_input_usd": round(koszt_input, 6),
            "koszt_output_usd": round(koszt_output, 6),
            "koszt_razem_usd": round(koszt_razem, 6),
        }


# Singleton instance
_licznik: Optional[TokenCounter] = None


def pobierz_licznik() -> TokenCounter:
    """
    Pobiera singleton instancję licznika tokenów.

    Returns:
        TokenCounter: Instancja licznika
    """
    global _licznik
    if _licznik is None:
        _licznik = TokenCounter()
    return _licznik
