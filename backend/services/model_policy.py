"""
Polityka wyboru modelu OpenAI dla NarraForge.

Moduł zawiera logikę inteligentnego skalowania modeli:
- TIER 1 (GPT-4o-mini): Proste zadania, strukturalne, walidacja
- TIER 2 (GPT-4o): Twórcza proza, postacie, dialogi
- TIER 3 (GPT-4): Zarezerwowane dla przyszłości (premium)
"""

from enum import Enum
from typing import Literal, Optional

from core.logging import get_logger

logger = get_logger(__name__)


class ModelTier(str, Enum):
    """Poziomy modeli OpenAI."""

    MINI = "gpt-4o-mini"  # Tier 1: Podstawowy, tani
    STANDARD = "gpt-4o"  # Tier 2: Standardowy, kreatywny
    PREMIUM = "gpt-4"  # Tier 3: Premium, zarezerwowany


class TypZadania(str, Enum):
    """Typy zadań wykonywanych przez agentów."""

    # Tier 1 - Proste zadania strukturalne
    WALIDACJA = "walidacja"
    FORMATOWANIE = "formatowanie"
    EKSTRAKCJA = "ekstrakcja"
    PODSUMOWANIE = "podsumowanie"

    # Tier 2 - Kreatywne zadania
    BUDOWANIE_SWIATA = "budowanie_swiata"
    TWORZENIE_POSTACI = "tworzenie_postaci"
    PROJEKTOWANIE_FABULY = "projektowanie_fabuly"
    PISANIE_PROZY = "pisanie_prozy"
    PISANIE_DIALOGOW = "pisanie_dialogow"
    OPISY_SCEN = "opisy_scen"

    # Tier 3 - Krytyczne zadania (zarezerwowane)
    SCENA_KULMINACYJNA = "scena_kulminacyjna"
    FINALNA_REDAKCJA = "finalna_redakcja"


class ModelPolicy:
    """
    Polityka wyboru modelu dla różnych typów zadań.

    Przykład użycia:
        >>> policy = ModelPolicy()
        >>> model = policy.wybierz_model(TypZadania.PISANIE_PROZY)
        >>> print(model)  # "gpt-4o"
    """

    def __init__(self):
        """Inicjalizacja polityki modeli."""
        # Mapowanie typów zadań na tier modelu
        self._mapowanie: dict[TypZadania, ModelTier] = {
            # Tier 1: GPT-4o-mini
            TypZadania.WALIDACJA: ModelTier.MINI,
            TypZadania.FORMATOWANIE: ModelTier.MINI,
            TypZadania.EKSTRAKCJA: ModelTier.MINI,
            TypZadania.PODSUMOWANIE: ModelTier.MINI,
            # Tier 2: GPT-4o
            TypZadania.BUDOWANIE_SWIATA: ModelTier.STANDARD,
            TypZadania.TWORZENIE_POSTACI: ModelTier.STANDARD,
            TypZadania.PROJEKTOWANIE_FABULY: ModelTier.STANDARD,
            TypZadania.PISANIE_PROZY: ModelTier.STANDARD,
            TypZadania.PISANIE_DIALOGOW: ModelTier.STANDARD,
            TypZadania.OPISY_SCEN: ModelTier.STANDARD,
            # Tier 3: GPT-4 (zarezerwowane)
            TypZadania.SCENA_KULMINACYJNA: ModelTier.PREMIUM,
            TypZadania.FINALNA_REDAKCJA: ModelTier.PREMIUM,
        }

        logger.info(
            "Zainicjalizowano politykę modeli",
            tier1_zadania=sum(1 for t in self._mapowanie.values() if t == ModelTier.MINI),
            tier2_zadania=sum(1 for t in self._mapowanie.values() if t == ModelTier.STANDARD),
            tier3_zadania=sum(1 for t in self._mapowanie.values() if t == ModelTier.PREMIUM),
        )

    def wybierz_model(
        self,
        typ_zadania: TypZadania,
        wymuszony_tier: Optional[int] = None,
    ) -> str:
        """
        Wybiera odpowiedni model dla zadania.

        Args:
            typ_zadania: Typ zadania do wykonania
            wymuszony_tier: Opcjonalnie wymusza konkretny tier (1-3)

        Returns:
            str: Nazwa modelu OpenAI

        Raises:
            ValueError: Gdy wymuszony tier jest nieprawidłowy
        """
        if wymuszony_tier is not None:
            if wymuszony_tier == 1:
                model = ModelTier.MINI.value
            elif wymuszony_tier == 2:
                model = ModelTier.STANDARD.value
            elif wymuszony_tier == 3:
                model = ModelTier.PREMIUM.value
            else:
                raise ValueError(f"Nieprawidłowy tier: {wymuszony_tier}. Dozwolone: 1, 2, 3")

            logger.info(
                "Użyto wymuszonego tier",
                typ_zadania=typ_zadania.value,
                wymuszony_tier=wymuszony_tier,
                wybrany_model=model,
            )
        else:
            tier = self._mapowanie.get(typ_zadania, ModelTier.STANDARD)
            model = tier.value

            logger.debug(
                "Automatyczny wybór modelu",
                typ_zadania=typ_zadania.value,
                tier=tier.value,
                model=model,
            )

        return model

    def pobierz_opis_tier(self, tier: int) -> str:
        """
        Zwraca opis tier modelu.

        Args:
            tier: Numer tier (1-3)

        Returns:
            str: Opis tier
        """
        opisy = {
            1: "Tier 1 (GPT-4o-mini): Zadania strukturalne, walidacja, formatowanie",
            2: "Tier 2 (GPT-4o): Twórcze zadania, proza, postacie, fabuła",
            3: "Tier 3 (GPT-4): Premium - sceny kulminacyjne, finalna redakcja",
        }
        return opisy.get(tier, "Nieznany tier")

    def pobierz_szacowany_koszt_tier(self, tier: int, tokeny: int = 1000) -> dict[str, float]:
        """
        Zwraca szacowany koszt dla tier.

        Args:
            tier: Numer tier (1-3)
            tokeny: Liczba tokenów (domyślnie 1000 in + 1000 out)

        Returns:
            dict: Słownik z kosztami
        """
        ceny = {
            1: {"input": 0.150, "output": 0.600},  # GPT-4o-mini per 1M tokens
            2: {"input": 2.50, "output": 10.00},  # GPT-4o
            3: {"input": 30.00, "output": 60.00},  # GPT-4
        }

        if tier not in ceny:
            return {"blad": "Nieprawidłowy tier"}

        cena = ceny[tier]
        koszt_input = (tokeny * cena["input"]) / 1_000_000
        koszt_output = (tokeny * cena["output"]) / 1_000_000

        return {
            "tier": tier,
            "tokeny": tokeny,
            "koszt_input_usd": round(koszt_input, 6),
            "koszt_output_usd": round(koszt_output, 6),
            "koszt_razem_usd": round(koszt_input + koszt_output, 6),
        }


# Singleton instance
_polityka: Optional[ModelPolicy] = None


def pobierz_polityke() -> ModelPolicy:
    """
    Pobiera singleton instancję polityki modeli.

    Returns:
        ModelPolicy: Instancja polityki
    """
    global _polityka
    if _polityka is None:
        _polityka = ModelPolicy()
    return _polityka
