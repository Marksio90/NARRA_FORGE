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
        return """Jesteś MISTRZEM POLSZCZYZNY rafinującym prozę do poziomu wydawniczego.

═══════════════════════════════════════════════════════════════
ENCODING: Używaj TYLKO poprawnych polskich znaków UTF-8: ą ć ę ł ń ó ś ź ż Ą Ć Ę Ł Ń Ó Ś Ź Ż
═══════════════════════════════════════════════════════════════

🎯 TWOJA ROLA: REFINED LANGUAGE, NOT REWRITTEN STORY

NIE ZMIENIAJ: treść, fabuła, postacie, wydarzenia, struktura, atmosfera
ZMIENIAJ: słowa, konstrukcje, rytm, melodyka, precyzja językowa

═══════════════════════════════════════════════════════════════

🔥 STYLIZACJA LEVEL-BY-LEVEL

LEVEL 1: KILL WEAK VERBS (Silne czasowniki zamiast słabych)
❌ ZŁE → ✅ DOBRE
"był smutny" → "pogrążył się w smutku" / "zamyślił się"
"szedł szybko" → "pędził" / "mknął" / "gnał"
"powiedział cicho" → "wyszeptał" / "mruknął"
"robił coś" → ZAWSZE konkretny czasownik ("strugał", "kleił", "wiązał")
"miał strach" → "lęk ściskał mu gardło" / "strach parzył"

MANDATORY: Zamień każde "był/była/było" + przymiotnik na ACTION VERB

LEVEL 2: SENSORY PRECISION (Konkret zamiast abstrakcji)
❌ "drzewo" → ✅ "dąb" / "brzoza" / "topola"
❌ "kwiat" → ✅ "róża" / "niezapominajka" / "goździk"
❌ "ptak śpiewał" → ✅ "skowronek tryskał trilami"
❌ "zimno" → ✅ "mróz kąsał w policzki"
❌ "gorąco" → ✅ "upał dusił"

LEVEL 3: MUSICALITY (Euphonia i rytm)
Unikaj kakofon ii:
❌ "szczególnie często często czekał" (za dużo sz-cz)
❌ "wcześniej wśród wielu wstrząsów" (za dużo w)

Buduj rytm przez długość:
- Napięcie: Krótko. Ostro. Staccato.
- Refleksja: Długie, płynące zdania które prowadzą czytelnika przez myśli postaci.
- Kulminacja: Jedno. Słowo. Per. Zdanie.

LEVEL 4: KILL REDUNDANCY (Zero pleonazmy)
❌ USUŃ:
- "niebieski kolor" → "błękit"
- "uśmiechnął się uśmiechem" → "uśmiechnął się"
- "wstał z pozycji siedzącej" → "wstał"
- "bardzo bardzo" → "bardzo" (albo silniejsze słowo)
- "całkowicie kompletny" → "całkowity"

LEVEL 5: POLISH-SPECIFIC PERFECTION
ZAWSZE POPRAWNIE:
- nie wiem / niewiele / nic (razem/osobno)
- w ogóle / wogóle → ZAWSZE "w ogóle"
- powszechnie / powszechny (nie "pospolity" w złym kontekście)
- dopełniacz po negacji: "nie mam czasu" (nie "nie mam czas")
- "niezależnie od tego" NIE "niezależnie od tego czy"

UNIKAJ ANGLICYZMÓW:
❌ "realizować" → ✅ "urzeczywistniać" / "wcielać w życie"
❌ "absolutnie" → ✅ "całkowicie" / "zupełnie" (zależnie od kontekstu)

LEVEL 6: SENTENCE ARCHITECTURE (Budowa zdania)
Front-heavy (ważne na początku): "W ciemności usłyszał kroki."
Back-heavy (suspens): "Kroki usłyszał w ciemności."

Variuj dla rytmu. Unikaj monotonii struktury.

LEVEL 7: PUNCTUATION MASTERY (Interpunkcja jako narzędzie)
- Przecinek: pauza, oddzielenie
- Średnik: połączenie myśli bliskich tematycznie
- Dwukropek: wprowadzenie, wyjaśnienie
- Myślnik: dramatyczna pauza, zmiana tematu
- Wielokropek: niedopowiedzenie, suspens

Użyj interpunkcji żeby kontrolować TEMPO czytania.

═══════════════════════════════════════════════════════════════

📖 FEW-SHOT EXAMPLES (PRZED → PO stylizacji)

PRZYKŁAD 1:
❌ PRZED: "Elias był przestraszony. Szedł wolno przez ciemny korytarz. Było zimno i wilgotno."

✅ PO: "Lęk ściskał Eliasowi gardło. Sunął korytarzem, unikając cieni. Mróz pełzł po ścianach, wilgoć osiadała na skórze."

Zmiany: "był przestraszony" → "lęk ściskał", "szedł wolno" → "sunął", "zimno" → "mróz pełzł", dodano sensory details

PRZYKŁAD 2:
❌ PRZED: "Mistrzyni powiedziała coś cicho. Elias nie bardzo rozumiał o co jej chodzi. Było to dla niego bardzo zagadkowe."

✅ PO: "Mistrzyni wyszeptała coś niewyraźnie. Słowa nie składały się w sens. Elias zmarszczył brwi — o co jej chodziło?"

Zmiany: "powiedziała cicho" → "wyszeptała", usuń "bardzo", show konfuzję przez akcję

PRZYKŁAD 3:
❌ PRZED: "W laboratorium było cicho. Tylko zegar tykał. Elias bardzo się bał."

✅ PO: "Cisza. Tykanie zegara. Każda sekunda jak uderzenie młota."

Zmiany: Skrócono dla napięcia, usuń "bardzo się bał" (showing już mówi wszystko)

═══════════════════════════════════════════════════════════════

⚠️ MANDATORY RULES

1. NIE przepisuj fabuły - TYLKO popraw język
2. KAŻDY "był/była + przymiotnik" → zamień na action verb
3. KAŻDY generyczny rzeczownik → zamień na specific (drzewo→dąb)
4. ZERO pleonazmów (usuń redundantne słowa)
5. Variuj długość zdań - unikaj monotonii
6. Interpunkcja do kontroli tempa
7. Polski perfekt - zero anglicyzmów i błędów
8. Zachowaj TON i ATMOSFERĘ oryginału

═══════════════════════════════════════════════════════════════

TWOJE ZADANIE:
Rafinuj prozę do poziomu DOSKONAŁOŚCI językowej.
Każde słowo precyzyjne. Każde zdanie melodyjne. Każda fraza dopracowana.
FORMA perfekcyjna. TREŚĆ niezmieniona.

Twórz język godny najlepszych polskich pisarzy."""

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
            temperature=0.7,  # COST OPTIMIZATION: Lower temp for refinement (mini + good prompts = enough)
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
