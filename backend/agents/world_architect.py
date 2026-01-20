"""
Agent Architekta Świata dla NarraForge.

Odpowiedzialny za projektowanie kompletnego świata książki:
- Geografia i lokacje
- Historia świata
- Systemy (magia/technologia/ekonomia)
- Kultury i społeczeństwa
- Tematyka i motywy
"""

import json
import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from agents.base import BaseAgent
from core.exceptions import AgentError
from core.logging import get_logger
from models.schema import World
from services.model_policy import TypZadania

logger = get_logger(__name__)


class WorldArchitect(BaseAgent):
    """
    Architekt Świata - buduje kompletny świat dla historii.

    Agent projektuje wszystkie aspekty świata przedstawionego:
    - Geografię, klimat, ekosystemy
    - Historię i mitologię
    - Systemy magii/technologii (zależnie od gatunku)
    - Kultury, religie, systemy polityczne
    - Ekonomię i handel
    - Tematykę i głębsze znaczenia

    Przykład użycia:
        >>> architect = WorldArchitect(db=db_session)
        >>> swiat = await architect.stworz_swiat(
        ...     gatunek="fantasy",
        ...     inspiracja="Epicki świat z magią run",
        ...     job_id=uuid.uuid4()
        ... )
    """

    def __init__(self, db: AsyncSession, wymuszony_tier: Optional[int] = None):
        """
        Inicjalizacja Architekta Świata.

        Args:
            db: Sesja bazy danych
            wymuszony_tier: Opcjonalnie wymusza tier modelu (1-3)
        """
        super().__init__(
            nazwa="World_Architect",
            typ_zadania=TypZadania.BUDOWANIE_SWIATA,
            db=db,
            wymuszony_tier=wymuszony_tier,
        )

    def pobierz_prompt_systemowy(self) -> str:
        """
        Zwraca prompt systemowy dla Architekta Świata.

        Returns:
            str: Prompt systemowy po polsku
        """
        return """Jesteś mistrzem world-buildingu - tworzysz światy tak żywe i szczegółowe, że czytelnik chce w nich zamieszkać.

Twoja rola:
1. GEOGRAFIA: Stwórz unikalną geografię z różnorodnymi lokacjami - od gór po pustynie, od miast po dzikie krainy
2. HISTORIA: Zaprojektuj bogatą historię kształtującą teraźniejszość - wojny, dynastie, odkrycia, katastrofy
3. SYSTEMY: Zbuduj spójne systemy (magia/technologia/ekonomia) z jasnymi regułami i ograniczeniami
4. KULTURY: Stwórz kultury z własnymi wartościami, konfliktami, obyczajami, językami
5. TEMATYKA: Wpleć głębsze znaczenia i motywy wspierające narrację

ZASADY:
- Każdy detal musi służyć narracji i być wewnętrznie spójny
- Unikaj kliszy - twórz świeże, oryginalne rozwiązania
- Systemy muszą mieć jasne reguły I ograniczenia
- Historia musi wpływać na teraźniejszość
- Zero nieuzasadnionych elementów

ODPOWIEDŹ:
Zwróć kompletny świat w formacie JSON z kluczami:
{
  "nazwa_swiata": "...",
  "zasady": ["reguła1", "reguła2", ...],
  "geografia": {
    "ogolny_opis": "...",
    "glowne_lokacje": [{"nazwa": "...", "opis": "...", "znaczenie": "..."}, ...],
    "klimat_i_ekosystemy": "..."
  },
  "historia": [
    {"okres": "...", "wydarzenie": "...", "konsekwencje": "..."},
    ...
  ],
  "systemy": {
    "magia_lub_technologia": {
      "opis": "...",
      "zasady": [...],
      "ograniczenia": [...]
    },
    "ekonomia": "...",
    "polityka": "..."
  },
  "kultury": [
    {
      "nazwa": "...",
      "wartosci": [...],
      "wierzenia": "...",
      "struktura_spoleczna": "..."
    },
    ...
  ],
  "tematyka": ["temat1", "temat2", ...]
}

Twórz spójne, fascynujące światy które chce się eksplorować!"""

    async def przetworz(self, dane_wejsciowe: dict[str, Any]) -> dict[str, Any]:
        """
        Przetwarza dane i tworzy świat.

        Args:
            dane_wejsciowe: Słownik z kluczami:
                - gatunek: str (fantasy/sci-fi/thriller/etc.)
                - inspiracja: str (opis inspiracji)
                - job_id: UUID (ID zadania)
                - dodatkowe_wskazowki: Optional[str]

        Returns:
            dict: Wygenerowany świat

        Raises:
            AgentError: Gdy generowanie się nie powiedzie
        """
        return await self.stworz_swiat(
            gatunek=dane_wejsciowe["gatunek"],
            inspiracja=dane_wejsciowe["inspiracja"],
            job_id=dane_wejsciowe["job_id"],
            dodatkowe_wskazowki=dane_wejsciowe.get("dodatkowe_wskazowki"),
        )

    async def stworz_swiat(
        self,
        gatunek: str,
        inspiracja: str,
        job_id: uuid.UUID,
        dodatkowe_wskazowki: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Tworzy kompletny świat dla książki.

        Args:
            gatunek: Gatunek literacki (fantasy/sci-fi/etc.)
            inspiracja: Inspiracja dla świata
            job_id: ID zadania
            dodatkowe_wskazowki: Opcjonalne dodatkowe wskazówki

        Returns:
            dict: Wygenerowany świat z wszystkimi elementami

        Raises:
            AgentError: Gdy tworzenie się nie powiedzie
        """
        self.logger.info(
            "Rozpoczynam budowanie świata",
            gatunek=gatunek,
            job_id=str(job_id),
        )

        # Sprawdź budżet
        budżet_ok = await self.waliduj_budzet(job_id)
        if not budżet_ok:
            raise AgentError(
                "Przekroczono budżet - nie można kontynuować budowania świata",
                details={"job_id": str(job_id)},
            )

        # Przygotuj prompt
        prompt_uzytkownika = f"""Stwórz kompletny świat dla książki w gatunku: {gatunek}

INSPIRACJA:
{inspiracja}
"""

        if dodatkowe_wskazowki:
            prompt_uzytkownika += f"\nDODATKOWE WSKAZÓWKI:\n{dodatkowe_wskazowki}\n"

        prompt_uzytkownika += "\nZWRÓĆ ODPOWIEDŹ W FORMACIE JSON zgodnie z instrukcjami systemowymi."

        wiadomosci = self.utworz_prompt(
            szablon=prompt_uzytkownika,
            zmienne={},
        )

        # Wywołaj LLM
        try:
            odpowiedz = await self.wywolaj_llm(
                wiadomosci=wiadomosci,
                temperatura=0.8,  # Wyższa temperatura dla kreatywności
                job_id=job_id,
                etap="budowanie_swiata",
            )

            # Parse JSON
            swiat_data = self._parsuj_odpowiedz(odpowiedz)

            # Zapisz do bazy
            swiat = await self._zapisz_do_bazy(
                job_id=job_id,
                swiat_data=swiat_data,
            )

            self.logger.info(
                "Pomyślnie zbudowano świat",
                nazwa_swiata=swiat_data.get("nazwa_swiata"),
                job_id=str(job_id),
                liczba_lokacji=len(swiat_data.get("geografia", {}).get("glowne_lokacje", [])),
                liczba_kultur=len(swiat_data.get("kultury", [])),
            )

            return {
                "sukces": True,
                "swiat": swiat_data,
                "world_id": str(swiat.id),
            }

        except json.JSONDecodeError as e:
            komunikat = f"Błąd parsowania JSON odpowiedzi: {str(e)}"
            self.logger.error(komunikat, job_id=str(job_id))
            raise AgentError(komunikat, details={"odpowiedz": odpowiedz[:500]})

        except Exception as e:
            komunikat = f"Błąd podczas budowania świata: {str(e)}"
            self.logger.error(komunikat, job_id=str(job_id))
            raise AgentError(komunikat)

    def _parsuj_odpowiedz(self, odpowiedz: str) -> dict[str, Any]:
        """
        Parsuje odpowiedź JSON z LLM.

        Args:
            odpowiedz: Odpowiedź tekstowa z LLM

        Returns:
            dict: Sparsowany JSON

        Raises:
            json.JSONDecodeError: Gdy JSON jest nieprawidłowy
        """
        # Wytnij JSON z odpowiedzi (może być otoczony backticks)
        odpowiedz = odpowiedz.strip()

        if odpowiedz.startswith("```json"):
            odpowiedz = odpowiedz[7:]
        if odpowiedz.startswith("```"):
            odpowiedz = odpowiedz[3:]
        if odpowiedz.endswith("```"):
            odpowiedz = odpowiedz[:-3]

        odpowiedz = odpowiedz.strip()

        return json.loads(odpowiedz)

    async def _zapisz_do_bazy(
        self,
        job_id: uuid.UUID,
        swiat_data: dict[str, Any],
    ) -> World:
        """
        Zapisuje wygenerowany świat do bazy danych.

        Args:
            job_id: ID zadania
            swiat_data: Dane świata

        Returns:
            World: Zapisany rekord świata
        """
        swiat = World(
            job_id=job_id,
            name=swiat_data.get("nazwa_swiata", "Nieznany Świat"),
            rules=swiat_data.get("zasady", []),
            geography=swiat_data.get("geografia", {}),
            history=swiat_data.get("historia", []),
            themes=swiat_data.get("tematyka", []),
            systems=swiat_data.get("systemy", {}),
        )

        # Dodaj kultury do systems dla zachowania w jednym miejscu
        if "kultury" in swiat_data:
            swiat.systems["kultury"] = swiat_data["kultury"]

        self.db.add(swiat)
        await self.db.flush()

        self.logger.info(
            "Zapisano świat do bazy",
            world_id=str(swiat.id),
            nazwa=swiat.name,
        )

        return swiat
