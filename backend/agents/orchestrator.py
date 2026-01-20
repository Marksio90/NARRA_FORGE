"""
Orchestrator dla NarraForge - koordynator pipeline'u generowania książki.

Używa LangGraph StateGraph do zarządzania przepływem między agentami:
1. World_Architect → budowanie świata
2. Character_Smith → tworzenie postaci
3. Plot_Master → projektowanie fabuły
4. Prose_Weaver → generowanie scen (w pętli)

Pipeline zarządza:
- Kolejnością wykonania agentów
- Przekazywaniem danych między etapami
- Obsługą błędów i retry
- Śledzeniem postępu
"""

import uuid
from typing import Any, Callable, Optional

from langgraph.graph import END, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import TypedDict

from agents.character_smith import CharacterSmith
from agents.plot_master import PlotMaster
from agents.prose_weaver import ProseWeaver
from agents.world_architect import WorldArchitect
from core.exceptions import AgentError
from core.logging import get_logger
from models.schema import Job

logger = get_logger(__name__)


class StanPipeline(TypedDict, total=False):
    """
    Stan pipeline'u generowania książki.

    Przechowuje wszystkie dane przepływające między agentami.
    """

    # Parametry wejściowe
    job_id: str
    gatunek: str
    inspiracja: str
    liczba_glownych_postaci: int
    docelowa_dlugosc: str  # "krótka"|"srednia"|"długa"
    styl_narracji: str
    dodatkowe_wskazowki: Optional[str]

    # Wyniki agentów
    swiat_data: Optional[dict[str, Any]]
    world_id: Optional[str]
    postacie_data: Optional[list[dict[str, Any]]]
    character_ids: Optional[list[str]]
    fabula_data: Optional[dict[str, Any]]
    plot_id: Optional[str]
    proza_chunks: Optional[list[dict[str, Any]]]

    # Kontrola przepływu
    aktualny_etap: str
    scena_index: int  # Dla pętli generowania scen
    liczba_scen: int
    bledy: list[dict[str, str]]
    sukces: bool

    # Callback do śledzenia postępu
    progress_callback: Optional[Callable[[str, float, Optional[str]], None]]


class Orchestrator:
    """
    Orchestrator - koordynator całego pipeline'u generowania książki.

    Używa LangGraph StateGraph do zarządzania przepływem między agentami.

    Przykład użycia:
        >>> orchestrator = Orchestrator(db=db_session)
        >>> wynik = await orchestrator.uruchom_pipeline(
        ...     job_id=uuid.uuid4(),
        ...     gatunek="fantasy",
        ...     inspiracja="Epicki świat z magią run",
        ...     liczba_glownych_postaci=3
        ... )
    """

    def __init__(
        self,
        db: AsyncSession,
        progress_callback: Optional[Callable[[str, float, Optional[str]], None]] = None,
    ):
        """
        Inicjalizacja Orchestratora.

        Args:
            db: Sesja bazy danych
            progress_callback: Opcjonalna funkcja callback(etap, procent, szczegoly)
        """
        self.db = db
        self.progress_callback = progress_callback
        self.logger = get_logger("agents.Orchestrator")

        # Inicjalizacja agentów
        self.world_architect = WorldArchitect(db=db)
        self.character_smith = CharacterSmith(db=db)
        self.plot_master = PlotMaster(db=db)
        self.prose_weaver = ProseWeaver(db=db)

        # Budowa grafu
        self.graph = self._zbuduj_graph()

        self.logger.info("Zainicjalizowano Orchestrator z LangGraph StateGraph")

    def _zbuduj_graph(self) -> StateGraph:
        """
        Buduje LangGraph StateGraph dla pipeline'u.

        Returns:
            StateGraph: Skompilowany graf przepływu
        """
        workflow = StateGraph(StanPipeline)

        # Dodaj węzły (nodes)
        workflow.add_node("buduj_swiat", self._node_buduj_swiat)
        workflow.add_node("stworz_postacie", self._node_stworz_postacie)
        workflow.add_node("zaprojektuj_fabule", self._node_zaprojektuj_fabule)
        workflow.add_node("generuj_sceny", self._node_generuj_sceny)
        workflow.add_node("finalizuj", self._node_finalizuj)

        # Definiuj przepływ (edges)
        workflow.set_entry_point("buduj_swiat")

        workflow.add_edge("buduj_swiat", "stworz_postacie")
        workflow.add_edge("stworz_postacie", "zaprojektuj_fabule")
        workflow.add_edge("zaprojektuj_fabule", "generuj_sceny")

        # Conditional edge - pętla generowania scen
        workflow.add_conditional_edges(
            "generuj_sceny",
            self._decyzja_wiecej_scen,
            {
                "kontynuuj": "generuj_sceny",  # Pętla - jeszcze są sceny
                "zakonczono": "finalizuj",  # Wszystkie sceny gotowe
            },
        )

        workflow.add_edge("finalizuj", END)

        # Kompiluj graf
        return workflow.compile()

    async def _node_buduj_swiat(self, stan: StanPipeline) -> dict[str, Any]:
        """
        Node: Budowanie świata przez World_Architect.

        Args:
            stan: Aktualny stan pipeline'u

        Returns:
            dict: Aktualizacje stanu
        """
        self.logger.info("NODE: Budowanie świata", job_id=stan["job_id"])
        self._powiadom_postep("Budowanie świata", 10.0, "🌍 AI analizuje gatunek i tworzy unikalny świat...")

        try:
            wynik = await self.world_architect.stworz_swiat(
                gatunek=stan["gatunek"],
                inspiracja=stan["inspiracja"],
                job_id=uuid.UUID(stan["job_id"]),
                dodatkowe_wskazowki=stan.get("dodatkowe_wskazowki"),
            )

            # Ekstrakcja kluczowych detali ze świata
            swiat = wynik["swiat"]
            nazwa_swiata = swiat.get("nazwa", "Nieznany Świat")
            setting = swiat.get("setting", "")
            magia = swiat.get("system_magii", "")

            szczegoly = f"✅ Stworzono świat: {nazwa_swiata}\n"
            if setting:
                szczegoly += f"→ Setting: {setting[:100]}...\n"
            if magia:
                szczegoly += f"→ System magii/technologii: {magia[:100]}..."

            self._powiadom_postep("Świat zbudowany", 20.0, szczegoly)

            return {
                "swiat_data": wynik["swiat"],
                "world_id": wynik["world_id"],
                "aktualny_etap": "buduj_swiat_zakonczone",
            }

        except Exception as e:
            self.logger.error("Błąd podczas budowania świata", error=str(e))
            return {
                "bledy": stan.get("bledy", [])
                + [{"etap": "buduj_swiat", "komunikat": str(e)}],
                "sukces": False,
            }

    async def _node_stworz_postacie(self, stan: StanPipeline) -> dict[str, Any]:
        """
        Node: Tworzenie postaci przez Character_Smith.

        Args:
            stan: Aktualny stan pipeline'u

        Returns:
            dict: Aktualizacje stanu
        """
        self.logger.info("NODE: Tworzenie postaci", job_id=stan["job_id"])
        liczba = stan.get("liczba_glownych_postaci", 3)
        self._powiadom_postep(
            "Tworzenie postaci",
            25.0,
            f"👥 AI projektuje {liczba} głównych bohaterów..."
        )

        try:
            wynik = await self.character_smith.stworz_postacie(
                swiat_data=stan["swiat_data"],
                gatunek=stan["gatunek"],
                liczba_glownych=liczba,
                job_id=uuid.UUID(stan["job_id"]),
                world_id=uuid.UUID(stan["world_id"]) if stan.get("world_id") else None,
                dodatkowe_wskazowki=stan.get("dodatkowe_wskazowki"),
            )

            # Ekstrakcja kluczowych detali o postaciach
            postacie = wynik["postacie"]
            szczegoly = f"✅ Stworzono {len(postacie)} postaci:\n"

            for i, postac in enumerate(postacie[:5], 1):  # Max 5 postaci
                imie = postac.get("imie", "Nieznana")
                rola = postac.get("rola", "")
                szczegoly += f"→ {imie}"
                if rola:
                    szczegoly += f" ({rola[:40]}{'...' if len(rola) > 40 else ''})"
                szczegoly += "\n"

            self._powiadom_postep("Postacie stworzone", 35.0, szczegoly.strip())

            return {
                "postacie_data": wynik["postacie"],
                "character_ids": wynik["character_ids"],
                "aktualny_etap": "stworz_postacie_zakonczone",
            }

        except Exception as e:
            self.logger.error("Błąd podczas tworzenia postaci", error=str(e))
            return {
                "bledy": stan.get("bledy", [])
                + [{"etap": "stworz_postacie", "komunikat": str(e)}],
                "sukces": False,
            }

    async def _node_zaprojektuj_fabule(self, stan: StanPipeline) -> dict[str, Any]:
        """
        Node: Projektowanie fabuły przez Plot_Master.

        Args:
            stan: Aktualny stan pipeline'u

        Returns:
            dict: Aktualizacje stanu
        """
        self.logger.info("NODE: Projektowanie fabuły", job_id=stan["job_id"])
        self._powiadom_postep(
            "Projektowanie fabuły",
            40.0,
            "📖 AI układa fabułę, akty i zwroty akcji..."
        )

        try:
            wynik = await self.plot_master.zaprojektuj_fabule(
                swiat_data=stan["swiat_data"],
                postacie_data=stan["postacie_data"],
                gatunek=stan["gatunek"],
                job_id=uuid.UUID(stan["job_id"]),
                docelowa_dlugosc=stan.get("docelowa_dlugosc", "srednia"),
                dodatkowe_wskazowki=stan.get("dodatkowe_wskazowki"),
            )

            # Ekstrakcja kluczowych detali o fabule
            fabula = wynik["fabula"]
            liczba_scen = len(fabula.get("sceny", []))
            temat = fabula.get("centralny_temat", "")
            konflikt = fabula.get("glowny_konflikt", "")

            szczegoly = f"✅ Fabuła zaprojektowana:\n"
            szczegoly += f"→ Liczba scen: {liczba_scen}\n"
            if temat:
                szczegoly += f"→ Temat: {temat[:80]}...\n"
            if konflikt:
                szczegoly += f"→ Konflikt: {konflikt[:80]}..."

            self._powiadom_postep("Fabuła zaprojektowana", 50.0, szczegoly)

            return {
                "fabula_data": wynik["fabula"],
                "plot_id": wynik["plot_id"],
                "liczba_scen": liczba_scen,
                "scena_index": 0,  # Start pętli generowania scen
                "proza_chunks": [],
                "aktualny_etap": "zaprojektuj_fabule_zakonczone",
            }

        except Exception as e:
            self.logger.error("Błąd podczas projektowania fabuły", error=str(e))
            return {
                "bledy": stan.get("bledy", [])
                + [{"etap": "zaprojektuj_fabule", "komunikat": str(e)}],
                "sukces": False,
            }

    async def _node_generuj_sceny(self, stan: StanPipeline) -> dict[str, Any]:
        """
        Node: Generowanie pojedynczej sceny przez Prose_Weaver.

        Ten node wykonuje się w pętli dla każdej sceny.

        Args:
            stan: Aktualny stan pipeline'u

        Returns:
            dict: Aktualizacje stanu
        """
        scena_index = stan["scena_index"]
        liczba_scen = stan["liczba_scen"]
        sceny = stan["fabula_data"]["sceny"]

        self.logger.info(
            "NODE: Generowanie sceny",
            job_id=stan["job_id"],
            scena=f"{scena_index + 1}/{liczba_scen}",
        )

        # Oblicz procent postępu (50% -> 95% dla scen)
        procent_bazowy = 50.0
        procent_scen = 45.0
        procent = procent_bazowy + (procent_scen * (scena_index + 1) / liczba_scen)

        # Ekstrakcja detali o scenie przed generowaniem
        scena_data = sceny[scena_index]
        tytul_sceny = scena_data.get("tytul", f"Scena {scena_index + 1}")
        styl = stan.get("styl_narracji", "literacki")

        szczegoly_przed = f"✍️ Piszę scenę {scena_index + 1}/{liczba_scen}\n"
        szczegoly_przed += f"→ '{tytul_sceny}'\n"
        szczegoly_przed += f"→ Styl: {styl}"

        self._powiadom_postep(
            f"Piszę scenę {scena_index + 1}/{liczba_scen}",
            procent,
            szczegoly_przed
        )

        try:
            # Pobierz poprzednią prozę dla kontynuacji
            poprzednia_proza = None
            if scena_index > 0 and stan["proza_chunks"]:
                poprzednia_proza = stan["proza_chunks"][-1].get("proza")

            # Generuj scenę
            wynik = await self.prose_weaver.wygeneruj_scene(
                scena_data=scena_data,
                postacie_data=stan["postacie_data"],
                styl=styl,
                job_id=uuid.UUID(stan["job_id"]),
                numer_rozdzialu=scena_data.get("akt"),
                poprzednia_scena=poprzednia_proza,
                swiat_data=stan["swiat_data"],
            )

            # Dodaj chunk do wyników
            nowe_chunks = stan.get("proza_chunks", []) + [
                {
                    "scena_numer": scena_data.get("numer"),
                    "proza": wynik["proza"],
                    "liczba_slow": wynik["liczba_slow"],
                    "chunk_id": wynik["chunk_id"],
                }
            ]

            # Szczegóły po ukończeniu sceny
            liczba_slow = wynik["liczba_slow"]
            laczna_liczba_slow = sum(ch["liczba_slow"] for ch in nowe_chunks)

            szczegoly_po = f"✅ Scena {scena_index + 1}/{liczba_scen} ukończona\n"
            szczegoly_po += f"→ Wygenerowano: {liczba_slow} słów\n"
            szczegoly_po += f"→ Łącznie: {laczna_liczba_slow} słów"

            # Progress update po ukończeniu sceny
            self._powiadom_postep(
                f"Scena {scena_index + 1}/{liczba_scen} gotowa",
                procent,
                szczegoly_po
            )

            return {
                "proza_chunks": nowe_chunks,
                "scena_index": scena_index + 1,  # Następna scena
                "aktualny_etap": f"generuj_sceny_{scena_index + 1}",
            }

        except Exception as e:
            self.logger.error(
                "Błąd podczas generowania sceny",
                error=str(e),
                scena_index=scena_index,
            )
            return {
                "bledy": stan.get("bledy", [])
                + [{"etap": f"generuj_sceny_{scena_index}", "komunikat": str(e)}],
                "sukces": False,
            }

    async def _node_finalizuj(self, stan: StanPipeline) -> dict[str, Any]:
        """
        Node: Finalizacja - aktualizacja statusu joba.

        Args:
            stan: Aktualny stan pipeline'u

        Returns:
            dict: Aktualizacje stanu
        """
        self.logger.info("NODE: Finalizacja", job_id=stan["job_id"])
        self._powiadom_postep("Finalizacja", 98.0, "🎯 Zapisywanie wyników...")

        try:
            # Aktualizuj status joba na completed
            job = await self.db.get(Job, uuid.UUID(stan["job_id"]))
            if job:
                # Sprawdź czy były błędy
                if stan.get("bledy") and len(stan["bledy"]) > 0:
                    job.status = "failed"
                    job.result = {
                        "blad": "Pipeline zakończony z błędami",
                        "bledy": stan["bledy"],
                    }
                else:
                    job.status = "completed"
                    liczba_slow_razem = sum(
                        chunk["liczba_slow"] for chunk in stan.get("proza_chunks", [])
                    )
                    job.result = {
                        "world_id": stan.get("world_id"),
                        "character_ids": stan.get("character_ids"),
                        "plot_id": stan.get("plot_id"),
                        "liczba_scen": stan.get("liczba_scen"),
                        "liczba_slow_razem": liczba_slow_razem,
                    }

                await self.db.flush()
                await self.db.commit()

                self.logger.info(
                    "Job zakończony",
                    job_id=stan["job_id"],
                    status=job.status,
                )

                # Szczegóły finalizacji
                if job.status == "completed":
                    liczba_scen = stan.get("liczba_scen", 0)
                    liczba_slow = sum(
                        chunk["liczba_slow"] for chunk in stan.get("proza_chunks", [])
                    )
                    szczegoly = f"🎉 Książka ukończona!\n"
                    szczegoly += f"→ {liczba_scen} scen\n"
                    szczegoly += f"→ {liczba_slow} słów"

                    self._powiadom_postep("Ukończono", 100.0, szczegoly)
                else:
                    self._powiadom_postep("Błąd", 100.0, "❌ Generowanie nie powiodło się")

            return {
                "aktualny_etap": "zakonczono",
                "sukces": True if not stan.get("bledy") else False,
            }

        except Exception as e:
            self.logger.error("Błąd podczas finalizacji", error=str(e))
            return {
                "bledy": stan.get("bledy", [])
                + [{"etap": "finalizuj", "komunikat": str(e)}],
                "sukces": False,
            }

    def _decyzja_wiecej_scen(self, stan: StanPipeline) -> str:
        """
        Funkcja decyzyjna: Czy generować więcej scen?

        Args:
            stan: Aktualny stan pipeline'u

        Returns:
            str: "kontynuuj" lub "zakonczono"
        """
        scena_index = stan.get("scena_index", 0)
        liczba_scen = stan.get("liczba_scen", 0)

        # Jeśli były błędy, przerwij
        if stan.get("bledy") and len(stan["bledy"]) > 0:
            self.logger.warning("Przerwano generowanie scen z powodu błędów")
            return "zakonczono"

        # Sprawdź czy są jeszcze sceny do wygenerowania
        if scena_index < liczba_scen:
            return "kontynuuj"
        else:
            return "zakonczono"

    def _powiadom_postep(
        self, etap: str, procent: float, szczegoly: Optional[str] = None
    ) -> None:
        """
        Wywołuje callback postępu jeśli jest zdefiniowany.

        Args:
            etap: Nazwa aktualnego etapu
            procent: Procent ukończenia (0-100)
            szczegoly: Opcjonalne szczegółowe informacje o tym co AI tworzy
        """
        if self.progress_callback:
            try:
                self.progress_callback(etap, procent, szczegoly)
            except Exception as e:
                self.logger.warning("Błąd callback postępu", error=str(e))

    async def uruchom_pipeline(
        self,
        job_id: uuid.UUID,
        gatunek: str,
        inspiracja: str,
        liczba_glownych_postaci: int = 3,
        docelowa_dlugosc: str = "srednia",
        styl_narracji: str = "literacki",
        dodatkowe_wskazowki: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Uruchamia pełną pipeline generowania książki.

        Args:
            job_id: ID zadania
            gatunek: Gatunek literacki
            inspiracja: Inspiracja dla świata
            liczba_glownych_postaci: Liczba głównych postaci (2-5)
            docelowa_dlugosc: Długość ("krótka"|"srednia"|"długa")
            styl_narracji: Styl ("literacki"|"poetycki"|"dynamiczny"|"noir")
            dodatkowe_wskazowki: Opcjonalne wskazówki

        Returns:
            dict: Wynik pipeline'u

        Raises:
            AgentError: Gdy pipeline się nie powiedzie
        """
        self.logger.info(
            "Uruchamianie pipeline'u generowania książki",
            job_id=str(job_id),
            gatunek=gatunek,
        )

        # Aktualizuj status joba na running
        job = await self.db.get(Job, job_id)
        if job:
            job.status = "running"
            await self.db.flush()

        # Inicjalizuj stan
        stan_poczatkowy: StanPipeline = {
            "job_id": str(job_id),
            "gatunek": gatunek,
            "inspiracja": inspiracja,
            "liczba_glownych_postaci": liczba_glownych_postaci,
            "docelowa_dlugosc": docelowa_dlugosc,
            "styl_narracji": styl_narracji,
            "dodatkowe_wskazowki": dodatkowe_wskazowki,
            "aktualny_etap": "start",
            "scena_index": 0,
            "liczba_scen": 0,
            "bledy": [],
            "sukces": False,
            "progress_callback": None,  # Callback ustawiony podczas __init__
        }

        try:
            # Uruchom graf LangGraph
            wynik_koncowy = await self.graph.ainvoke(stan_poczatkowy)

            self.logger.info(
                "Pipeline zakończony",
                job_id=str(job_id),
                sukces=wynik_koncowy.get("sukces"),
            )

            return {
                "sukces": wynik_koncowy.get("sukces"),
                "world_id": wynik_koncowy.get("world_id"),
                "character_ids": wynik_koncowy.get("character_ids"),
                "plot_id": wynik_koncowy.get("plot_id"),
                "liczba_scen": wynik_koncowy.get("liczba_scen"),
                "liczba_slow_razem": sum(
                    chunk["liczba_slow"]
                    for chunk in wynik_koncowy.get("proza_chunks", [])
                ),
                "bledy": wynik_koncowy.get("bledy", []),
            }

        except Exception as e:
            komunikat = f"Błąd podczas wykonywania pipeline'u: {str(e)}"
            self.logger.error(komunikat, job_id=str(job_id))

            # Aktualizuj status joba na failed
            if job:
                job.status = "failed"
                job.result = {"blad": komunikat}
                await self.db.flush()
                await self.db.commit()

            raise AgentError(komunikat, details={"job_id": str(job_id)})


async def utworz_orchestrator(
    db: AsyncSession,
    progress_callback: Optional[Callable[[str, float, Optional[str]], None]] = None,
) -> Orchestrator:
    """
    Tworzy instancję Orchestratora.

    Args:
        db: Sesja bazy danych
        progress_callback: Opcjonalna funkcja callback(etap, procent, szczegoly)

    Returns:
        Orchestrator: Instancja orchestratora
    """
    return Orchestrator(db=db, progress_callback=progress_callback)
