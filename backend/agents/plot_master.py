"""
Agent Mistrza Fabuły dla NarraForge.

Odpowiedzialny za projektowanie struktury narracyjnej:
- Wybór struktury (3-act, Hero's Journey, Save the Cat)
- Główny konflikt i stawka
- Zwroty akcji i punkty kulminacyjne
- Wątki poboczne
- Timeline wydarzeń
- Breakdown scen
"""

import json
import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from agents.base import BaseAgent
from core.exceptions import AgentError
from core.logging import get_logger
from models.schema import Plot
from services.model_policy import TypZadania

logger = get_logger(__name__)


class PlotMaster(BaseAgent):
    """
    Mistrz Fabuły - projektuje strukturę narracyjną z precyzją.

    Agent tworzy:
    - Spójną strukturę fabularną (3-akt/Hero's Journey)
    - Główny konflikt ze staw ką rosnącą z każdym aktem
    - Zwroty akcji i zaskoczenia
    - Wątki poboczne wspierające tematykę
    - Szczegółowy breakdown scen

    Przykład użycia:
        >>> master = PlotMaster(db=db_session)
        >>> fabuła = await master.zaprojektuj_fabule(
        ...     swiat_data={...},
        ...     postacie_data={...},
        ...     gatunek="fantasy",
        ...     job_id=uuid.uuid4()
        ... )
    """

    def __init__(self, db: AsyncSession, wymuszony_tier: Optional[int] = None):
        """
        Inicjalizacja Mistrza Fabuły.

        Args:
            db: Sesja bazy danych
            wymuszony_tier: Opcjonalnie wymusza tier modelu (1-3)
        """
        super().__init__(
            nazwa="Plot_Master",
            typ_zadania=TypZadania.PROJEKTOWANIE_FABULY,
            db=db,
            wymuszony_tier=wymuszony_tier,
        )

    def pobierz_prompt_systemowy(self) -> str:
        """
        Zwraca prompt systemowy dla Mistrza Fabuły.

        Returns:
            str: Prompt systemowy po polsku
        """
        return """Jesteś architektem fabuły - tworzysz struktury narracyjne precyzyjne jak mechanizm zegarka i porywające jak rollercoaster.

Twoja rola:
1. STRUKTURA: Wybierz optymalną strukturę (3-akt, Hero's Journey, Save the Cat) dla gatunku
2. KONFLIKT: Zdefiniuj główny konflikt ze stawką rosnącą z każdym aktem
3. ZWROTY AKCJI: Zaplanuj zaskakujące zwroty i revelacje
4. WĄTKI POBOCZNE: Stwórz B-story i C-story wzbogacające tematykę
5. PACING: Zaprojektuj tempo - kiedy akcja, kiedy refleksja
6. SCENY: Rozpisz każdą scenę z celem narracyjnym

ZASADY:
- Każda scena musi przesuwać fabułę LUB rozwijać postać
- Zero filler content - każdy element ma cel
- Stawka musi rosnąć - nie może być monotonnie
- Zwroty akcji muszą być zakorzenione w wcześniejszych elementach (foreshadowing)
- Cliffhangery na końcach aktów/rozdziałów

STRUKTURY DO WYBORU:
- 3-AKT: Setup (25%) → Confrontation (50%) → Resolution (25%)
- HERO'S JOURNEY: Ordinary World → Call to Adventure → Tests → Ordeal → Return
- SAVE THE CAT: Opening Image → Theme Stated → Catalyst → B Story → Midpoint → All is Lost → Finale

ODPOWIEDŹ:
Zwróć fabułę w formacie JSON:
{
  "struktura": "3-akt|hero-journey|save-the-cat",
  "glowny_konflikt": {
    "opis": "...",
    "protagonista": "Imię głównej postaci",
    "antagonista": "Imię/opis antagonisty",
    "stawka": "Co jest zagrożone",
    "temat": "Głębsze znaczenie konfliktu"
  },
  "akty": [
    {
      "numer": 1,
      "nazwa": "Setup/Journey Begins/etc",
      "opis": "Co się dzieje w tym akcie",
      "cel_narracyjny": "...",
      "zwrot_akcji_na_koncu": "..."
    },
    {
      "numer": 2,
      "nazwa": "...",
      "opis": "...",
      "cel_narracyjny": "...",
      "punkt_srodkowy": "Midpoint - zwrot w połowie",
      "zwrot_akcji_na_koncu": "..."
    },
    {
      "numer": 3,
      "nazwa": "...",
      "opis": "...",
      "cel_narracyjny": "...",
      "kulminacja": "Szczytowy moment",
      "rozwiazanie": "Jak się kończy"
    }
  ],
  "watki_poboczne": [
    {
      "nazwa": "B-Story: ...",
      "opis": "...",
      "powiazane_postacie": ["...", "..."],
      "cel_tematyczny": "Jak wspiera główny temat"
    }
  ],
  "sceny": [
    {
      "numer": 1,
      "akt": 1,
      "tytul": "...",
      "lokacja": "...",
      "postacie": ["...", "..."],
      "pov": "Z czyjej perspektywy",
      "cel": "Co ta scena osiąga",
      "konflikt": "Konkretny konflikt w scenie",
      "emocjonalny_beat": "Jaka emocja dominuje",
      "co_sie_dzieje": "Szczegółowy opis akcji",
      "hook_lub_cliffhanger": "Jak scena się kończy"
    },
    ... (minimum 8-12 scen)
  ],
  "foreshadowing": [
    {
      "element": "Co jest zapowiedziane",
      "scena_wprowadzenia": 1,
      "scena_objawienia": 10
    }
  ]
}

Projektuj fabularne perfekcje!"""

    async def przetworz(self, dane_wejsciowe: dict[str, Any]) -> dict[str, Any]:
        """
        Przetwarza dane i projektuje fabułę.

        Args:
            dane_wejsciowe: Słownik z kluczami:
                - swiat_data: dict
                - postacie_data: list
                - gatunek: str
                - job_id: UUID
                - docelowa_dlugosc: Optional[str] ("krótka"|"srednia"|"długa")

        Returns:
            dict: Zaprojektowana fabuła

        Raises:
            AgentError: Gdy projektowanie się nie powiedzie
        """
        return await self.zaprojektuj_fabule(
            swiat_data=dane_wejsciowe["swiat_data"],
            postacie_data=dane_wejsciowe["postacie_data"],
            gatunek=dane_wejsciowe["gatunek"],
            job_id=dane_wejsciowe["job_id"],
            docelowa_dlugosc=dane_wejsciowe.get("docelowa_dlugosc", "srednia"),
            dodatkowe_wskazowki=dane_wejsciowe.get("dodatkowe_wskazowki"),
        )

    async def zaprojektuj_fabule(
        self,
        swiat_data: dict[str, Any],
        postacie_data: list[dict[str, Any]],
        gatunek: str,
        job_id: uuid.UUID,
        docelowa_dlugosc: str = "srednia",
        dodatkowe_wskazowki: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Projektuje strukturę fabularną książki.

        Args:
            swiat_data: Dane świata
            postacie_data: Lista postaci
            gatunek: Gatunek literacki
            job_id: ID zadania
            docelowa_dlugosc: Długość ("krótka"|"srednia"|"długa")
            dodatkowe_wskazowki: Opcjonalne wskazówki

        Returns:
            dict: Zaprojektowana fabuła

        Raises:
            AgentError: Gdy projektowanie się nie powiedzie
        """
        self.logger.info(
            "Rozpoczynam projektowanie fabuły",
            gatunek=gatunek,
            dlugosc=docelowa_dlugosc,
            job_id=str(job_id),
        )

        # Sprawdź budżet
        budżet_ok = await self.waliduj_budzet(job_id)
        if not budżet_ok:
            raise AgentError(
                "Przekroczono budżet - nie można kontynuować projektowania fabuły",
                details={"job_id": str(job_id)},
            )

        # Przygotuj konteksty
        kontekst_swiata = self._przygotuj_kontekst_swiata(swiat_data)
        kontekst_postaci = self._przygotuj_kontekst_postaci(postacie_data)

        # Określ liczbę scen
        liczba_scen = {"krótka": 8, "srednia": 12, "długa": 20}.get(docelowa_dlugosc, 12)

        # Przygotuj prompt
        prompt_uzytkownika = f"""Zaprojektuj fabułę dla książki w gatunku: {gatunek}

KONTEKST ŚWIATA:
{kontekst_swiata}

POSTACIE:
{kontekst_postaci}

WYMAGANIA:
- Długość: {docelowa_dlugosc} (~{liczba_scen} scen)
- Struktura dopasowana do gatunku {gatunek}
- Główny protagonista: {postacie_data[0].get('imie', 'Nieznany') if postacie_data else 'Nieznany'}
- Wszystkie główne postacie muszą mieć znaczącą rolę w fabule
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
                temperatura=0.75,  # Balans między kreatywnością a precyzją
                job_id=job_id,
                etap="projektowanie_fabuly",
            )

            # Parse JSON
            fabula_data = self._parsuj_odpowiedz(odpowiedz)

            # Zapisz do bazy
            plot = await self._zapisz_do_bazy(
                job_id=job_id,
                fabula_data=fabula_data,
            )

            self.logger.info(
                "Pomyślnie zaprojektowano fabułę",
                struktura=fabula_data.get("struktura"),
                liczba_scen=len(fabula_data.get("sceny", [])),
                job_id=str(job_id),
            )

            return {
                "sukces": True,
                "fabula": fabula_data,
                "plot_id": str(plot.id),
            }

        except json.JSONDecodeError as e:
            komunikat = f"Błąd parsowania JSON odpowiedzi: {str(e)}"
            self.logger.error(komunikat, job_id=str(job_id))
            raise AgentError(komunikat, details={"odpowiedz": odpowiedz[:500]})

        except Exception as e:
            komunikat = f"Błąd podczas projektowania fabuły: {str(e)}"
            self.logger.error(komunikat, job_id=str(job_id))
            raise AgentError(komunikat)

    def _przygotuj_kontekst_swiata(self, swiat_data: dict[str, Any]) -> str:
        """Przygotowuje skrócony kontekst świata."""
        return f"""Świat: {swiat_data.get('nazwa_swiata', 'Nieznany')}
Tematyka: {', '.join(swiat_data.get('tematyka', []))}
Systemy: {swiat_data.get('systemy', {}).get('magia_lub_technologia', {}).get('opis', 'Brak')[:200]}"""

    def _przygotuj_kontekst_postaci(self, postacie_data: list[dict[str, Any]]) -> str:
        """Przygotowuje skrócony kontekst postaci."""
        kontekst = ""
        for postac in postacie_data[:5]:  # Max 5 postaci
            arc = postac.get("arc_rozwojowy", {})
            kontekst += f"\n- {postac.get('imie', 'Nieznany')} ({postac.get('rola', 'unknown')}): "
            kontekst += f"Need: {arc.get('need', 'N/A')}, Want: {arc.get('want', 'N/A')}"
        return kontekst

    def _parsuj_odpowiedz(self, odpowiedz: str) -> dict[str, Any]:
        """Parsuje odpowiedź JSON z LLM."""
        odpowiedz = odpowiedz.strip()
        if odpowiedz.startswith("```json"):
            odpowiedz = odpowiedz[7:]
        if odpowiedz.startswith("```"):
            odpowiedz = odpowiedz[3:]
        if odpowiedz.endswith("```"):
            odpowiedz = odpowiedz[:-3]
        return json.loads(odpowiedz.strip())

    async def _zapisz_do_bazy(
        self,
        job_id: uuid.UUID,
        fabula_data: dict[str, Any],
    ) -> Plot:
        """Zapisuje fabułę do bazy danych."""
        plot = Plot(
            job_id=job_id,
            structure=fabula_data.get("struktura", "3-akt"),
            acts=fabula_data.get("akty", []),
            scenes=fabula_data.get("sceny", []),
            conflicts={
                "glowny": fabula_data.get("glowny_konflikt", {}),
                "watki_poboczne": fabula_data.get("watki_poboczne", []),
                "foreshadowing": fabula_data.get("foreshadowing", []),
            },
            main_conflict=fabula_data.get("glowny_konflikt", {}).get("opis"),
            stakes=fabula_data.get("glowny_konflikt", {}).get("stawka", {}),
            turning_points=[
                akt.get("zwrot_akcji_na_koncu", "") for akt in fabula_data.get("akty", [])
            ],
        )

        self.db.add(plot)
        await self.db.flush()

        self.logger.info(
            "Zapisano fabułę do bazy",
            plot_id=str(plot.id),
            struktura=plot.structure,
        )

        return plot
