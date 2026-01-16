"""
Agent 08: Language Stylizer

Odpowiedzialność:
- Stylizacja językowa najwyższego poziomu
- Refinement języka polskiego
- Rytm, melodyka, przepływ
- Usuwanie redundancji i słabych konstrukcji

Model: gpt-4o (QUALITY CRITICAL - język musi być doskonały)
"""
from typing import Any, Dict

from narra_forge.agents.base_agent import GenerationAgent
from narra_forge.core.types import AgentResult, PipelineStage


class LanguageStylerAgent(GenerationAgent):
    """
    Agent stylizujący język polski na najwyższym poziomie.

    Używa GPT-4o dla doskonałości językowej.
    """

    def __init__(self, config, memory, router):
        super().__init__(
            config=config,
            memory=memory,
            router=router,
            stage=PipelineStage.LANGUAGE_STYLIZATION,
        )

    def get_system_prompt(self) -> str:
        return """Jesteś MISTRZEM JĘZYKA POLSKIEGO w systemie produkcji narracji wydawniczych.

CRITICAL: Używaj TYLKO poprawnych polskich znaków UTF-8: ą ć ę ł ń ó ś ź ż Ą Ć Ę Ł Ń Ó Ś Ź Ż
NIE używaj: Ä…, Ä™, Ĺ›, Ä‡, Ĺ‚, Ĺ„, ĹĽ ani innych błędnych kombinacji znaków.

Twoja rola:
- Rafinujesz język polski do poziomu absolutnego
- Dbasz o rytm, melodykę, przepływ
- Usuwasz redundancje i słabe konstrukcje
- Doprowadzasz każde zdanie do perfekcji

NIE ZMIENIASZ:
- Treści (co się dzieje)
- Struktury narracji
- Charakteru postaci
- Przebiegu wydarzeń

ZMIENIASZ:
- Formę językową
- Dobór słów
- Konstrukcje zdań
- Rytm i melodykę

ZASADY STYLIZACJI:

1. **PRECYZJA SŁOWNICTWA**
   - Nie: "powiedział" (generyczne)
   - Tak: "wyszeptał", "burknął", "warknął" (precyzyjne)

   - Nie: "szybko szedł"
   - Tak: "pędził", "mknął", "sunął"

2. **RYTM I MELODYKA**
   - Wariuj długość zdań
   - Krótkie zdania = napięcie, akcja
   - Długie zdania = refleksja, opis
   - Unikaj monotonii

3. **REDUNDANCJA**
   - Usuń: "niebieski kolor", "uśmiechnął się uśmiechem"
   - Usuń: "bardzo bardzo", "naprawdę zupełnie"
   - Każde słowo musi mieć funkcję

4. **KONKRETNOŚĆ**
   - Nie: "drzewo"
   - Tak: "dąb", "sosna", "brzoza"

   - Nie: "ptak śpiewał"
   - Tak: "skowronek tryskał trilami"

5. **SHOW, DON'T TELL**
   - Nie: "była zła"
   - Tak: "zacisnęła pięści, paznokcie wbiły się w dłonie"

6. **SKŁADNIA POLSKA**
   - Pełna kontrola nad fleksją
   - Poprawne użycie przypadków
   - Dopełniacze, celowniki, miejscowniki - doskonale
   - Unikaj konstrukcji obcych (anglicyzmów)

7. **INTERPUNKCJA MISTRZOWSKA**
   - Przecinki, średniki, dwukropki - perfekcyjnie
   - Pauzy retoryczne (myślniki, wielokropki)
   - Rytm poprzez interpunkcję

8. **UNIKAJ**:
   - Bierni strony bez powodu
   - "Było" i "jest" (słabe czasowniki)
   - Przysłówki na -o (wolno, szybko - zamień na silne czasowniki)
   - Pleonazmy
   - Klisze językowe

9. **ZACHOWAJ**:
   - Ton oryginalnej narracji
   - Głos postaci w dialogach
   - Atmosferę świata
   - Intencje autora

10. **DOSKONAŁOŚĆ**:
    - Każde zdanie musi być perfekcyjne
    - Każde słowo na swoim miejscu
    - Żadnej niepotrzebnej frazy
    - Poziom: literatura wydawnicza

Rafinujesz FORMĘ, zachowujesz TREŚĆ. Dążysz do PERFEKCJI językowej."""

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Wykonaj stylizację językową.

        Args:
            context: Zawiera 'narrative_text'

        Returns:
            AgentResult ze stylizowanym tekstem
        """
        narrative_text = context.get("narrative_text")

        if not narrative_text:
            self.add_error("No narrative_text in context")
            return self._create_result(success=False, data={})

        # Podziel na mniejsze fragmenty (jeśli bardzo długi tekst)
        words = narrative_text.split()
        word_count = len(words)

        if word_count > 8000:
            # Dla długich tekstów - stylizuj w fragmentach
            stylized_parts = await self._stylize_in_chunks(narrative_text)
            stylized_text = "\n\n".join(stylized_parts)
        else:
            # Dla krótszych - stylizuj całość
            stylized_text = await self._stylize_text(narrative_text)

        stylized_word_count = len(stylized_text.split())

        # Sprawdź czy długość się drastycznie nie zmieniła
        if abs(stylized_word_count - word_count) > word_count * 0.15:
            self.add_warning(
                f"Word count changed significantly: {word_count} → {stylized_word_count}"
            )

        return self._create_result(
            success=True,
            data={
                "stylized_text": stylized_text,
                "original_word_count": word_count,
                "stylized_word_count": stylized_word_count,
            },
        )

    async def _stylize_text(self, text: str) -> str:
        """Stylizuj fragment tekstu"""

        prompt = f"""Zrafinuj poniższy tekst do najwyższego poziomu językowego.

ZASADY:
- Zachowaj TREŚĆ (co się dzieje)
- Rafinuj FORMĘ (jak to jest powiedziane)
- Precyzja słownictwa
- Rytm i melodyka
- Usuń redundancje
- Doskonała składnia polska
- Mistrzowska interpunkcja

TEKST DO RAFINACJI:
{text}

Zwróć TYLKO zrafinowany tekst. Bez komentarzy, bez wyjaśnień."""

        stylized, call = await self.call_model(
            prompt=prompt,
            temperature=0.7,
            max_tokens=len(text.split()) * 2,  # ~2 tokens per word
        )

        return stylized.strip()

    async def _stylize_in_chunks(self, text: str) -> list[str]:
        """Stylizuj długi tekst w częściach"""

        # Podziel na paragrafy
        paragraphs = text.split("\n\n")

        # Grupuj paragrafy w chunki ~2000 słów
        chunks = []
        current_chunk = []
        current_words = 0

        for para in paragraphs:
            para_words = len(para.split())

            if current_words + para_words > 2000 and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_words = para_words
            else:
                current_chunk.append(para)
                current_words += para_words

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        # Stylizuj każdy chunk
        stylized_chunks = []
        for chunk in chunks:
            stylized = await self._stylize_text(chunk)
            stylized_chunks.append(stylized)

        return stylized_chunks
