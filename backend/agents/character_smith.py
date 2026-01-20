"""
Agent Kowala Postaci dla NarraForge.

Odpowiedzialny za tworzenie wielowymiarowych postaci:
- Biografia i tło
- Psychologia (MBTI, Enneagram, motywacje)
- Wygląd fizyczny
- Głos narracyjny i słownictwo
- Arc rozwojowy (transformacja)
- Relacje z innymi postaciami
"""

import json
import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from agents.base import BaseAgent
from core.exceptions import AgentError
from core.logging import get_logger
from models.schema import Character, World
from services.model_policy import TypZadania

logger = get_logger(__name__)


class CharacterSmith(BaseAgent):
    """
    Kowal Postaci - tworzy żywe, wielowymiarowe postacie.

    Agent projektuje postacie z:
    - Głęboką biografią kształtującą psychologię
    - Autentycznymi motywacjami, lękami, pragnieniami
    - Unikalnym głosem narracyjnym
    - Przemyślanym arc rozwojowym
    - Organicznymi relacjami z innymi

    Przykład użycia:
        >>> smith = CharacterSmith(db=db_session)
        >>> postacie = await smith.stworz_postacie(
        ...     swiat_data={...},
        ...     gatunek="fantasy",
        ...     liczba_glownych=3,
        ...     job_id=uuid.uuid4()
        ... )
    """

    def __init__(self, db: AsyncSession, wymuszony_tier: Optional[int] = None):
        """
        Inicjalizacja Kowala Postaci.

        Args:
            db: Sesja bazy danych
            wymuszony_tier: Opcjonalnie wymusza tier modelu (1-3)
        """
        super().__init__(
            nazwa="Character_Smith",
            typ_zadania=TypZadania.TWORZENIE_POSTACI,
            db=db,
            wymuszony_tier=wymuszony_tier,
        )

    def pobierz_prompt_systemowy(self) -> str:
        """
        Zwraca prompt systemowy dla Kowala Postaci.

        Returns:
            str: Prompt systemowy po polsku
        """
        return """Jesteś mistrzem tworzenia postaci - budujesz ludzi (lub istoty) tak prawdziwych, że czytelnik za nimi tęskni.

Twoja rola:
1. BIOGRAFIA: Stwórz szczegółową przeszłość kształtującą psychologię - traumy, triumfy, relacje, kluczowe momenty
2. PSYCHOLOGIA: Zdefiniuj głębokie motywacje, lęki, pragnienia, wartości, przekonania
3. OSOBOWOŚĆ: Określ MBTI, Enneagram, temperament, tiki nerwowe, nawyki
4. WYGLĄD: Opisz fizyczność, sposób poruszania się, ubiór, charakterystyczne cechy
5. GŁOS: Ustal unikalny sposób mówienia, słownictwo, dialekt, tempo
6. ARC: Zaprojektuj transformację - Ghost (trauma), Wound (rana), Need (potrzeba), Want (pragnienie)
7. RELACJE: Zdefiniuj dynamikę z innymi postaciami

ZASADY:
- Postacie muszą być wielowymiarowe - z wadami I zaletami
- Zero postaci-funkcji - każda osoba żyje własnym życiem
- Arc rozwojowy musi być organiczny i zakorzeniony w psychologii
- Konflikty wewnętrzne równie ważne jak zewnętrzne
- Każda postać ma unikalny głos i perspektywę

ODPOWIEDŹ:
Zwróć postacie w formacie JSON:
{
  "postacie": [
    {
      "imie": "Pełne imię",
      "rola": "main|supporting|minor",
      "profil": {
        "wiek": 0,
        "plec": "...",
        "rasa_lub_gatunek": "...",
        "zawod": "...",
        "pochodzenie": "..."
      },
      "biografia": {
        "dziecinstwo": "...",
        "kluczowe_wydarzenia": ["...", "..."],
        "trauma_formujaca": "...",
        "osiagniecia": ["...", "..."]
      },
      "psychologia": {
        "mbti": "XXXX",
        "enneagram": "XwX",
        "motywacje": ["...", "..."],
        "leki": ["...", "..."],
        "pragnienia": ["...", "..."],
        "wartosci": ["...", "..."],
        "slabe_punkty": ["...", "..."]
      },
      "wyglad": {
        "wzrost": "...",
        "budowa": "...",
        "charakterystyczne_cechy": ["...", "..."],
        "styl_ubierania": "...",
        "sposob_poruszania": "..."
      },
      "glos": {
        "ton": "...",
        "tempo": "...",
        "slownictwo": "...",
        "charakterystyczne_zwroty": ["...", "..."],
        "akcent_lub_dialekt": "..."
      },
      "arc_rozwojowy": {
        "ghost": "Trauma z przeszłości",
        "wound": "Obecna rana psychiczna",
        "need": "Czego naprawdę potrzebuje",
        "want": "Czego chce (może być błędne)",
        "etapy_transformacji": ["...", "...", "..."]
      },
      "relacje": [
        {
          "z_kim": "Imię innej postaci",
          "typ": "przyjaciel/wróg/mentor/rywal/etc",
          "dynamika": "Opis relacji",
          "rozwoj": "Jak się zmieni"
        }
      ]
    }
  ]
}

Twórz postacie, które żyją i oddychają!"""

    async def przetworz(self, dane_wejsciowe: dict[str, Any]) -> dict[str, Any]:
        """
        Przetwarza dane i tworzy postacie.

        Args:
            dane_wejsciowe: Słownik z kluczami:
                - swiat_data: dict (dane świata)
                - gatunek: str
                - liczba_glownych: int (domyślnie 3)
                - job_id: UUID
                - dodatkowe_wskazowki: Optional[str]

        Returns:
            dict: Wygenerowane postacie

        Raises:
            AgentError: Gdy generowanie się nie powiedzie
        """
        return await self.stworz_postacie(
            swiat_data=dane_wejsciowe["swiat_data"],
            gatunek=dane_wejsciowe["gatunek"],
            liczba_glownych=dane_wejsciowe.get("liczba_glownych", 3),
            job_id=dane_wejsciowe["job_id"],
            world_id=dane_wejsciowe.get("world_id"),
            dodatkowe_wskazowki=dane_wejsciowe.get("dodatkowe_wskazowki"),
        )

    async def stworz_postacie(
        self,
        swiat_data: dict[str, Any],
        gatunek: str,
        liczba_glownych: int,
        job_id: uuid.UUID,
        world_id: Optional[uuid.UUID] = None,
        dodatkowe_wskazowki: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Tworzy postacie dla książki.

        Args:
            swiat_data: Dane świata (z World_Architect)
            gatunek: Gatunek literacki
            liczba_glownych: Liczba głównych postaci (2-5)
            job_id: ID zadania
            world_id: ID świata w bazie
            dodatkowe_wskazowki: Opcjonalne wskazówki

        Returns:
            dict: Wygenerowane postacie

        Raises:
            AgentError: Gdy tworzenie się nie powiedzie
        """
        self.logger.info(
            "Rozpoczynam tworzenie postaci",
            gatunek=gatunek,
            liczba_glownych=liczba_glownych,
            job_id=str(job_id),
        )

        # Sprawdź budżet
        budżet_ok = await self.waliduj_budzet(job_id)
        if not budżet_ok:
            raise AgentError(
                "Przekroczono budżet - nie można kontynuować tworzenia postaci",
                details={"job_id": str(job_id)},
            )

        # Przygotuj kontekst świata
        kontekst_swiata = self._przygotuj_kontekst_swiata(swiat_data)

        # Przygotuj prompt
        prompt_uzytkownika = f"""Stwórz {liczba_glownych} głównych postaci dla książki w gatunku: {gatunek}

KONTEKST ŚWIATA:
{kontekst_swiata}
"""

        if dodatkowe_wskazowki:
            prompt_uzytkownika += f"\nDODATKOWE WSKAZÓWKI:\n{dodatkowe_wskazowki}\n"

        prompt_uzytkownika += f"""
WYMAGANIA:
- {liczba_glownych} postaci głównych (role: "main")
- Każda postać musi być unikalna i wielowymiarowa
- Postacie muszą pasować do świata i gatunku
- Relacje między postaciami muszą tworzyć ciekawą dynamikę

ZWRÓĆ ODPOWIEDŹ W FORMACIE JSON zgodnie z instrukcjami systemowymi."""

        wiadomosci = self.utworz_prompt(
            szablon=prompt_uzytkownika,
            zmienne={},
        )

        # Wywołaj LLM
        try:
            odpowiedz = await self.wywolaj_llm(
                wiadomosci=wiadomosci,
                temperatura=0.8,  # Wysoka temperatura dla kreatywności
                job_id=job_id,
                etap="tworzenie_postaci",
            )

            # Parse JSON
            postacie_data = self._parsuj_odpowiedz(odpowiedz)

            # Zapisz do bazy
            postacie = await self._zapisz_do_bazy(
                job_id=job_id,
                world_id=world_id,
                postacie_data=postacie_data,
            )

            self.logger.info(
                "Pomyślnie stworzono postacie",
                liczba_postaci=len(postacie),
                job_id=str(job_id),
                imiona=[p.name for p in postacie],
            )

            return {
                "sukces": True,
                "postacie": postacie_data["postacie"],
                "liczba_postaci": len(postacie),
                "character_ids": [str(p.id) for p in postacie],
            }

        except json.JSONDecodeError as e:
            komunikat = f"Błąd parsowania JSON odpowiedzi: {str(e)}"
            self.logger.error(komunikat, job_id=str(job_id))
            raise AgentError(komunikat, details={"odpowiedz": odpowiedz[:500]})

        except Exception as e:
            komunikat = f"Błąd podczas tworzenia postaci: {str(e)}"
            self.logger.error(komunikat, job_id=str(job_id))
            raise AgentError(komunikat)

    def _przygotuj_kontekst_swiata(self, swiat_data: dict[str, Any]) -> str:
        """
        Przygotowuje skrócony kontekst świata dla promptu.

        Args:
            swiat_data: Dane świata

        Returns:
            str: Sformatowany kontekst
        """
        kontekst = f"Nazwa świata: {swiat_data.get('nazwa_swiata', 'Nieznany')}\n\n"

        # Geografia
        if "geografia" in swiat_data:
            geo = swiat_data["geografia"]
            kontekst += f"Geografia: {geo.get('ogolny_opis', 'Brak opisu')}\n\n"

        # Kultury
        if "kultury" in swiat_data:
            kontekst += "Kultury:\n"
            for kultura in swiat_data["kultury"][:3]:  # Max 3 kultury
                kontekst += f"- {kultura.get('nazwa', 'Nieznana')}: {kultura.get('wartosci', [])}\n"
            kontekst += "\n"

        # Systemy
        if "systemy" in swiat_data:
            sys = swiat_data["systemy"]
            if "magia_lub_technologia" in sys:
                tech = sys["magia_lub_technologia"]
                kontekst += f"System magii/tech: {tech.get('opis', 'Brak opisu')}\n\n"

        # Tematyka
        if "tematyka" in swiat_data:
            kontekst += f"Tematyka: {', '.join(swiat_data['tematyka'])}\n"

        return kontekst

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
        # Wytnij JSON z odpowiedzi
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
        world_id: Optional[uuid.UUID],
        postacie_data: dict[str, Any],
    ) -> list[Character]:
        """
        Zapisuje wygenerowane postacie do bazy danych.

        Args:
            job_id: ID zadania
            world_id: ID świata
            postacie_data: Dane postaci

        Returns:
            list[Character]: Zapisane rekordy postaci
        """
        postacie = []

        for postac_data in postacie_data.get("postacie", []):
            postac = Character(
                job_id=job_id,
                world_id=world_id,
                name=postac_data.get("imie", "Nieznany"),
                role=postac_data.get("rola", "main"),
                profile=postac_data.get("profil", {}),
                trajectory={
                    "biografia": postac_data.get("biografia", {}),
                    "psychologia": postac_data.get("psychologia", {}),
                    "wyglad": postac_data.get("wyglad", {}),
                    "glos": postac_data.get("glos", {}),
                    "arc_rozwojowy": postac_data.get("arc_rozwojowy", {}),
                },
                relationships={"relacje": postac_data.get("relacje", [])},
            )

            self.db.add(postac)
            postacie.append(postac)

        await self.db.flush()

        self.logger.info(
            "Zapisano postacie do bazy",
            liczba=len(postacie),
            imiona=[p.name for p in postacie],
        )

        return postacie
