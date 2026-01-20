"""
Agent Tkacza Prozy dla NarraForge.

Odpowiedzialny za generowanie faktycznej prozy książki:
- Pełne rozdziały/sceny z opisami
- Dialogi naturalne i charakterystyczne dla postaci
- Show don't tell - immersja przez szczegóły
- Konsystencja stylu i głosu narracyjnego
- Tempo i rytm narracji
"""

import json
import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from agents.base import BaseAgent
from core.exceptions import AgentError
from core.logging import get_logger
from models.schema import ProseChunk
from services.model_policy import TypZadania

logger = get_logger(__name__)


class ProseWeaver(BaseAgent):
    """
    Tkacz Prozy - generuje faktyczną prozę książki.

    Agent pisze:
    - Pełne sceny/rozdziały z immersyjnymi opisami
    - Autentyczne dialogi pasujące do głosu postaci
    - Show don't tell - czytelnik doświadcza, nie czyta relacji
    - Konsystentny styl i tempo narracji
    - Emocjonalne beaty zgodne z planem fabuły

    Przykład użycia:
        >>> weaver = ProseWeaver(db=db_session)
        >>> proza = await weaver.wygeneruj_scene(
        ...     scena_data={...},
        ...     postacie_data=[...],
        ...     styl="literacki-poetycki",
        ...     job_id=uuid.uuid4()
        ... )
    """

    def __init__(self, db: AsyncSession, wymuszony_tier: Optional[int] = None):
        """
        Inicjalizacja Tkacza Prozy.

        Args:
            db: Sesja bazy danych
            wymuszony_tier: Opcjonalnie wymusza tier modelu (1-3)
        """
        super().__init__(
            nazwa="Prose_Weaver",
            typ_zadania=TypZadania.PISANIE_PROZY,
            db=db,
            wymuszony_tier=wymuszony_tier,
        )

    def pobierz_prompt_systemowy(self) -> str:
        """
        Zwraca prompt systemowy dla Tkacza Prozy.

        Returns:
            str: Prompt systemowy po polsku
        """
        return """Jesteś mistrzem prozy - piszesz sceny tak żywe i porywające, że czytelnik zapomina że czyta słowa.

Twoja rola:
1. IMMERSJA: Zanurz czytelnika w scenie - wszystkie zmysły, detale środowiska, atmosfera
2. SHOW DON'T TELL: Pokaż emocje przez akcje, gesty, reakcje - NIE opisuj "był smutny"
3. DIALOGI: Naturalne, charakterystyczne dla każdej postaci, z subtekstem
4. TEMPO: Dynamiczne - akcja jest szybka (krótkie zdania), refleksja wolna (długie, poetyckie)
5. GŁOS NARRACYJNY: Konsystentny styl - czy to 1. osoba czy 3. osoba limited
6. EMOCJONALNE BEATY: Każda scena ma cel emocjonalny - realizuj go precyzyjnie

ZASADY PISANIA:
- Zero cliché i wyświechtanych fraz
- Metafory świeże i dopasowane do świata/postaci
- Język sensoryczny - jak wygląda, pachnie, brzmi, smakuje, czuje się
- Subtelność > oczywistość
- Każde zdanie musi coś wnosić
- Dialogi bez zbędnych "powiedział/zapytała" - akcja i kontekst pokazują kto mówi
- Cliffhangery na końcach scen (jeśli wymagane)

TEMPO I RYTM:
- Akcja: Krótkie zdania. Staccato. Bez ozdobników.
- Refleksja: Długie, płynne zdania z poetyckimi metaforami i głębokimi obserwacjami
- Napięcie: Buduj stopniowo, używaj przecinków dla pauzy przed revelacją

POV (PUNKT WIDZENIA):
- Jeśli 3. osoba limited: Wszystko przez filtr postaci POV - ich obserwacje, interpretacje, uprzedzenia
- Jeśli 1. osoba: Pełen głos postaci - slang, sposób myślenia, humor

ODPOWIEDŹ:
Zwróć wygenerowaną prozę w formacie JSON:
{
  "proza": "PEŁNA TREŚĆ SCENY - co najmniej 800-2000 słów, w zależności od wymagań",
  "liczba_slow": 0,
  "notatki_stylistyczne": "Jakie techniki użyto, tempo, klimat",
  "emocjonalny_beat_osiagniety": "Czy cel emocjonalny sceny został zrealizowany"
}

PRZYKŁAD DOBREJ PROZY (styl do naśladowania):

'Nóż odbił się od kości. Krew - ciepła, lepka - spłynęła mi po dłoni.

Cofnęłam się. Serce waliło jak młot.

"To nie miało..." Głos mi się załamał. "Nie miało tak być."

Jego oczy - już puste - wpatrywały się w sufit. Gdzieś daleko krzyczała wrona.'

PISZ z pasją i precyzją!"""

    async def przetworz(self, dane_wejsciowe: dict[str, Any]) -> dict[str, Any]:
        """
        Przetwarza dane i generuje prozę.

        Args:
            dane_wejsciowe: Słownik z kluczami:
                - scena_data: dict (dane sceny z Plot_Master)
                - postacie_data: list (dane postaci)
                - styl: str (styl narracji)
                - job_id: UUID
                - numer_rozdzialu: Optional[int]

        Returns:
            dict: Wygenerowana proza

        Raises:
            AgentError: Gdy generowanie się nie powiedzie
        """
        return await self.wygeneruj_scene(
            scena_data=dane_wejsciowe["scena_data"],
            postacie_data=dane_wejsciowe["postacie_data"],
            styl=dane_wejsciowe.get("styl", "literacki"),
            job_id=dane_wejsciowe["job_id"],
            numer_rozdzialu=dane_wejsciowe.get("numer_rozdzialu"),
            poprzednia_scena=dane_wejsciowe.get("poprzednia_scena"),
            swiat_data=dane_wejsciowe.get("swiat_data"),
        )

    async def wygeneruj_scene(
        self,
        scena_data: dict[str, Any],
        postacie_data: list[dict[str, Any]],
        styl: str,
        job_id: uuid.UUID,
        numer_rozdzialu: Optional[int] = None,
        poprzednia_scena: Optional[str] = None,
        swiat_data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Generuje pełną prozę dla pojedynczej sceny.

        Args:
            scena_data: Dane sceny z Plot_Master (cel, konflikt, postacie, lokacja)
            postacie_data: Lista postaci (dla konsystencji głosu)
            styl: Styl narracji ("literacki", "poetycki", "dynamiczny", "noir")
            job_id: ID zadania
            numer_rozdzialu: Numer rozdziału (opcjonalny)
            poprzednia_scena: Fragment poprzedniej sceny (dla kontynuacji)
            swiat_data: Dane świata (dla kontekstu)

        Returns:
            dict: Wygenerowana proza z metadanymi

        Raises:
            AgentError: Gdy generowanie się nie powiedzie
        """
        self.logger.info(
            "Rozpoczynam generowanie prozy dla sceny",
            scena_numer=scena_data.get("numer"),
            styl=styl,
            job_id=str(job_id),
        )

        # Sprawdź budżet
        budżet_ok = await self.waliduj_budzet(job_id)
        if not budżet_ok:
            raise AgentError(
                "Przekroczono budżet - nie można kontynuować generowania prozy",
                details={"job_id": str(job_id)},
            )

        # Przygotuj konteksty
        kontekst_sceny = self._przygotuj_kontekst_sceny(scena_data)
        kontekst_postaci = self._przygotuj_kontekst_postaci(
            postacie_data, scena_data.get("postacie", [])
        )

        # Przygotuj prompt
        prompt_uzytkownika = f"""Napisz pełną scenę dla książki.

SZCZEGÓŁY SCENY:
{kontekst_sceny}

POSTACIE W SCENIE:
{kontekst_postaci}

STYL NARRACJI: {styl}
POV: {scena_data.get('pov', '3. osoba limited')}
"""

        if poprzednia_scena:
            prompt_uzytkownika += f"""
KONTEKST - KONIEC POPRZEDNIEJ SCENY:
...{poprzednia_scena[-500:]}

Kontynuuj płynnie zachowując momentum narracyjne.
"""

        if swiat_data:
            prompt_uzytkownika += f"""
ŚWIAT: {swiat_data.get('nazwa_swiata', 'Nieznany')}
Tematyka: {', '.join(swiat_data.get('tematyka', []))}
"""

        prompt_uzytkownika += """
WYMAGANIA:
- Długość: 800-2000 słów (w zależności od wagi sceny)
- Immersyjne opisy (wszystkie zmysły)
- Naturalne dialogi z subtekstem
- Show don't tell
- Realizuj cel emocjonalny sceny

ZWRÓĆ ODPOWIEDŹ W FORMACIE JSON zgodnie z instrukcjami systemowymi.
"""

        wiadomosci = self.utworz_prompt(
            szablon=prompt_uzytkownika,
            zmienne={},
        )

        # Wywołaj LLM
        try:
            odpowiedz = await self.wywolaj_llm(
                wiadomosci=wiadomosci,
                temperatura=0.85,  # Wysoka temperatura dla kreatywności prozy
                max_tokeny=4000,  # Długie odpowiedzi dla pełnych scen
                job_id=job_id,
                etap=f"pisanie_sceny_{scena_data.get('numer', 0)}",
            )

            # Parse JSON
            proza_data = self._parsuj_odpowiedz(odpowiedz)

            # Zapisz do bazy
            chunk = await self._zapisz_do_bazy(
                job_id=job_id,
                scena_numer=scena_data.get("numer"),
                rozdzial_numer=numer_rozdzialu,
                proza_data=proza_data,
            )

            self.logger.info(
                "Pomyślnie wygenerowano prozę",
                scena_numer=scena_data.get("numer"),
                liczba_slow=proza_data.get("liczba_slow"),
                job_id=str(job_id),
            )

            return {
                "sukces": True,
                "proza": proza_data["proza"],
                "liczba_slow": proza_data.get("liczba_slow"),
                "chunk_id": str(chunk.id),
                "notatki_stylistyczne": proza_data.get("notatki_stylistyczne"),
            }

        except json.JSONDecodeError as e:
            komunikat = f"Błąd parsowania JSON odpowiedzi: {str(e)}"
            self.logger.error(komunikat, job_id=str(job_id))
            raise AgentError(komunikat, details={"odpowiedz": odpowiedz[:500]})

        except Exception as e:
            komunikat = f"Błąd podczas generowania prozy: {str(e)}"
            self.logger.error(komunikat, job_id=str(job_id))
            raise AgentError(komunikat)

    def _przygotuj_kontekst_sceny(self, scena_data: dict[str, Any]) -> str:
        """Przygotowuje kontekst sceny dla promptu."""
        kontekst = f"""Scena #{scena_data.get('numer', '?')}: {scena_data.get('tytul', 'Bez tytułu')}

Lokacja: {scena_data.get('lokacja', 'Nieznana')}
Cel sceny: {scena_data.get('cel', 'N/A')}
Konflikt w scenie: {scena_data.get('konflikt', 'N/A')}
Emocjonalny beat: {scena_data.get('emocjonalny_beat', 'neutralny')}

CO SIĘ DZIEJE:
{scena_data.get('co_sie_dzieje', 'Brak opisu')}

KONIEC SCENY: {scena_data.get('hook_lub_cliffhanger', 'Zakończ naturalnie')}
"""
        return kontekst

    def _przygotuj_kontekst_postaci(
        self,
        wszystkie_postacie: list[dict[str, Any]],
        postacie_w_scenie: list[str],
    ) -> str:
        """Przygotowuje kontekst postaci występujących w scenie."""
        kontekst = ""

        for postac in wszystkie_postacie:
            imie = postac.get("imie", "Nieznany")
            if imie not in postacie_w_scenie:
                continue

            glos = postac.get("glos", {})
            psychologia = postac.get("psychologia", {})
            wyglad = postac.get("wyglad", {})

            kontekst += f"""
--- {imie} ---
Psychologia: {', '.join(psychologia.get('wartosci', [])[:3])}
Lęki: {', '.join(psychologia.get('leki', [])[:2])}
Głos: {glos.get('ton', 'neutralny')}, {glos.get('tempo', 'normalne')}
Charakterystyczne zwroty: {', '.join(glos.get('charakterystyczne_zwroty', [])[:3])}
Wygląd: {wyglad.get('charakterystyczne_cechy', ['brak opisu'])[0] if wyglad.get('charakterystyczne_cechy') else 'brak opisu'}
"""

        return kontekst.strip()

    def _parsuj_odpowiedz(self, odpowiedz: str) -> dict[str, Any]:
        """Parsuje odpowiedź JSON z LLM."""
        odpowiedz = odpowiedz.strip()
        if odpowiedz.startswith("```json"):
            odpowiedz = odpowiedz[7:]
        if odpowiedz.startswith("```"):
            odpowiedz = odpowiedz[3:]
        if odpowiedz.endswith("```"):
            odpowiedz = odpowiedz[:-3]

        parsed = json.loads(odpowiedz.strip())

        # Policz słowa jeśli nie zostały podane
        if "liczba_slow" not in parsed or parsed["liczba_slow"] == 0:
            proza_text = parsed.get("proza", "")
            parsed["liczba_slow"] = len(proza_text.split())

        return parsed

    async def _zapisz_do_bazy(
        self,
        job_id: uuid.UUID,
        scena_numer: Optional[int],
        rozdzial_numer: Optional[int],
        proza_data: dict[str, Any],
    ) -> ProseChunk:
        """Zapisuje wygenerowaną prozę do bazy danych."""
        chunk = ProseChunk(
            job_id=job_id,
            scene_number=scena_numer,
            chapter_number=rozdzial_numer,
            content=proza_data["proza"],
            word_count=proza_data.get("liczba_slow", 0),
            style_notes=proza_data.get("notatki_stylistyczne", ""),
            revision_notes="",  # Uzupełniane później przez rewizje
        )

        self.db.add(chunk)
        await self.db.flush()

        self.logger.info(
            "Zapisano prozę do bazy",
            chunk_id=str(chunk.id),
            scena=scena_numer,
            rozdzial=rozdzial_numer,
            liczba_slow=chunk.word_count,
        )

        return chunk
