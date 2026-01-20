"""
Bazowa klasa dla agentów AI w NarraForge.

Zapewnia wspólną funkcjonalność dla wszystkich agentów:
- Integracja z LangChain
- Automatyczne liczenie tokenów
- Automatyczny tracking kosztów
- Strukturalne logi
"""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.exceptions import AgentError
from core.logging import get_logger
from services.cost_tracker import CostTracker
from services.model_policy import ModelPolicy, TypZadania
from services.token_counter import TokenCounter

settings = get_settings()


class BaseAgent(ABC):
    """
    Bazowa klasa dla wszystkich agentów AI.

    Każdy agent dziedziczy po tej klasie i implementuje:
    - pobierz_prompt_systemowy(): Zwraca prompt systemowy
    - przetworz(): Wykonuje główną logikę agenta

    Przykład użycia:
        >>> class MojAgent(BaseAgent):
        ...     def pobierz_prompt_systemowy(self) -> str:
        ...         return "Jesteś pomocnym asystentem."
        ...
        ...     async def przetworz(self, dane_wejsciowe: dict) -> dict:
        ...         wynik = await self.wywolaj_llm(
        ...             wiadomosci=[{"role": "user", "content": "Cześć!"}]
        ...         )
        ...         return {"odpowiedz": wynik}
    """

    def __init__(
        self,
        nazwa: str,
        typ_zadania: TypZadania,
        db: Optional[AsyncSession] = None,
        wymuszony_tier: Optional[int] = None,
    ):
        """
        Inicjalizacja agenta.

        Args:
            nazwa: Nazwa agenta (do logów)
            typ_zadania: Typ zadania wykonyw

anego przez agenta
            db: Sesja bazy danych (opcjonalna, potrzebna dla cost tracking)
            wymuszony_tier: Opcjonalnie wymusza konkretny tier modelu (1-3)
        """
        self.nazwa = nazwa
        self.typ_zadania = typ_zadania
        self.db = db
        self.logger = get_logger(f"agents.{nazwa}")

        # Inicjalizacja policy i licznika
        self.policy = ModelPolicy()
        self.licznik = TokenCounter()

        # Wybór modelu
        self.model = self.policy.wybierz_model(typ_zadania, wymuszony_tier)

        # Inicjalizacja LangChain LLM
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY,
            timeout=settings.OPENAI_TIMEOUT,
        )

        # Inicjalizacja cost trackera jeśli jest db
        self.cost_tracker = CostTracker(db) if db else None

        self.logger.info(
            "Zainicjalizowano agenta",
            nazwa=nazwa,
            typ_zadania=typ_zadania.value,
            model=self.model,
        )

    @abstractmethod
    def pobierz_prompt_systemowy(self) -> str:
        """
        Zwraca prompt systemowy dla agenta.

        Musi być zaimplementowany przez każdą klasę pochodną.

        Returns:
            str: Prompt systemowy
        """
        pass

    @abstractmethod
    async def przetworz(self, dane_wejsciowe: dict[str, Any]) -> dict[str, Any]:
        """
        Główna logika przetwarzania agenta.

        Musi być zaimplementowana przez każdą klasę pochodną.

        Args:
            dane_wejsciowe: Dane wejściowe dla agenta

        Returns:
            dict: Wynik przetwarzania

        Raises:
            AgentError: Gdy przetwarzanie się nie powiedzie
        """
        pass

    async def wywolaj_llm(
        self,
        wiadomosci: list[dict[str, str]],
        temperatura: Optional[float] = None,
        max_tokeny: Optional[int] = None,
        job_id: Optional[uuid.UUID] = None,
        etap: Optional[str] = None,
    ) -> str:
        """
        Wywołuje LLM z automatycznym trackiniem kosztów.

        Args:
            wiadomosci: Lista wiadomości w formacie OpenAI
            temperatura: Opcjonalna temperatura (nadpisuje domyślną)
            max_tokeny: Maksymalna liczba tokenów wyjściowych
            job_id: ID joba (dla cost trackingu)
            etap: Nazwa etapu (dla cost trackingu)

        Returns:
            str: Odpowiedź z LLM

        Raises:
            AgentError: Gdy wywołanie się nie powiedzie
        """
        try:
            # Policz tokeny wejściowe
            info_tokenow = self.licznik.policz_tokeny_wiadomosci(wiadomosci, self.model)
            tokeny_input = info_tokenow["tokeny_razem"]

            self.logger.info(
                "Wysyłanie żądania do LLM",
                model=self.model,
                tokeny_input=tokeny_input,
                liczba_wiadomosci=len(wiadomosci),
            )

            # Wywołanie LLM przez LangChain
            if temperatura is not None:
                llm = self.llm.bind(temperature=temperatura)
            else:
                llm = self.llm

            if max_tokeny is not None:
                llm = llm.bind(max_tokens=max_tokeny)

            # Invoke LLM
            from langchain_core.messages import HumanMessage, SystemMessage

            lc_messages = []
            for msg in wiadomosci:
                if msg["role"] == "system":
                    lc_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    lc_messages.append(HumanMessage(content=msg["content"]))

            odpowiedz = await llm.ainvoke(lc_messages)
            tresc = odpowiedz.content

            # Policz tokeny wyjściowe (przybliżenie)
            tokeny_output = self.licznik.policz_tokeny(tresc, self.model)

            # Oblicz koszt
            koszt = settings.get_model_cost(self.model, tokeny_input, tokeny_output)

            self.logger.info(
                "Otrzymano odpowiedź z LLM",
                model=self.model,
                tokeny_input=tokeny_input,
                tokeny_output=tokeny_output,
                koszt_usd=koszt,
            )

            # Zapisz koszt jeśli mamy tracker i job_id
            if self.cost_tracker and job_id and etap:
                await self.cost_tracker.zapisz_koszt(
                    job_id=job_id,
                    etap=etap,
                    model=self.model,
                    tokeny_input=tokeny_input,
                    tokeny_output=tokeny_output,
                    koszt_usd=koszt,
                )

                await self.cost_tracker.aktualizuj_koszt_joba(
                    job_id=job_id,
                    dodatkowy_koszt=koszt,
                    dodatkowe_tokeny=tokeny_input + tokeny_output,
                )

            return tresc

        except Exception as e:
            komunikat = f"Błąd podczas wywołania LLM: {str(e)}"
            self.logger.error(komunikat, agent=self.nazwa, model=self.model)
            raise AgentError(komunikat, details={"agent": self.nazwa, "model": self.model})

    def utworz_prompt(
        self,
        szablon: str,
        zmienne: dict[str, Any],
    ) -> list[dict[str, str]]:
        """
        Tworzy prompt z szablonu i zmiennych.

        Args:
            szablon: Szablon promptu (z placeholderami {zmienna})
            zmienne: Słownik zmiennych do podstawienia

        Returns:
            list: Lista wiadomości gotowa do wysłania do LLM
        """
        prompt_systemowy = self.pobierz_prompt_systemowy()
        prompt_uzytkownika = szablon.format(**zmienne)

        return [
            {"role": "system", "content": prompt_systemowy},
            {"role": "user", "content": prompt_uzytkownika},
        ]

    async def waliduj_budzet(self, job_id: uuid.UUID) -> bool:
        """
        Sprawdza czy job nie przekroczył budżetu.

        Args:
            job_id: ID joba

        Returns:
            bool: True jeśli budżet OK, False jeśli przekroczony

        Raises:
            AgentError: Gdy nie można sprawdzić budżetu
        """
        if not self.cost_tracker:
            self.logger.warning("Brak cost trackera - nie można sprawdzić budżetu")
            return True

        try:
            status = await self.cost_tracker.sprawdz_budzet(job_id)
            if status.get("przekroczony"):
                self.logger.error(
                    "Przekroczono budżet!",
                    job_id=str(job_id),
                    koszt=status["koszt_aktualny_usd"],
                    limit=status["limit_usd"],
                )
                return False
            return True
        except Exception as e:
            komunikat = f"Błąd podczas sprawdzania budżetu: {str(e)}"
            self.logger.error(komunikat, job_id=str(job_id))
            raise AgentError(komunikat)
