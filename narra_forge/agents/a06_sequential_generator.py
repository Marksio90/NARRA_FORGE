"""
Agent 06: Sequential Generator

Odpowiedzialność:
- GENERACJA WŁAŚCIWEJ NARRACJI LITERACKIEJ
- Pisanie segmentów po kolei z pełną pamięcią
- Utrzymywanie jakości na najwyższym poziomie
- Zachowanie spójności między segmentami

Model: gpt-4o (QUALITY CRITICAL - najdroższy, ale konieczny)
"""
from typing import Any, Dict, List

from narra_forge.agents.base_agent import GenerationAgent
from narra_forge.core.types import AgentResult, GeneratedSegment, PipelineStage


class SequentialGeneratorAgent(GenerationAgent):
    """
    Agent generujący właściwą narrację literacką.

    To jest NAJWAŻNIEJSZY agent - generuje PRAWDZIWĄ PROZĘ.
    Używa GPT-4o dla najwyższej jakości.
    """

    def __init__(self, config, memory, router):
        super().__init__(
            config=config,
            memory=memory,
            router=router,
            stage=PipelineStage.SEQUENTIAL_GENERATION,
        )

    def get_system_prompt(self) -> str:
        return """Jesteś MISTRZEM PROZY na poziomie bestsellерowych autorów. Tworzysz LITERATURĘ WYDAWNICZĄ.

═══════════════════════════════════════════════════════════════
ENCODING: Używaj TYLKO poprawnych polskich znaków UTF-8: ą ć ę ł ń ó ś ź ż Ą Ć Ę Ł Ń Ó Ś Ź Ż
═══════════════════════════════════════════════════════════════

🎯 BESTSELLER CRAFT PRINCIPLES - MANDATORY

1. OPENING HOOKS (Pierwsze zdanie musi złapać)
   ❌ ZŁE: "W sercu miasta, gdzie mury starego gmachu pamiętały..."
   ✅ DOBRE: "Krew była jeszcze ciepła, gdy Marek zdał sobie sprawę, że to jego własna."

   Techniki:
   - Zacznij IN MEDIAS RES (w środku akcji)
   - Postaw pytanie które domaga się odpowiedzi
   - Sensory detail który niepokoi lub intryguje
   - NIE ekspozycja, NIE opisy miejsc

2. SHOW DON'T TELL (Konkretnie, nie abstrakcyjnie)
   ❌ ZŁE: "Był przestraszony i zdenerwowany"
   ✅ DOBRE: "Pot sklejał mu koszulę do pleców. Palce drżały przy zaciśnięciu klamki."

   Reguła: Każda emocja = obserwowalne zachowanie + reakcja ciała
   - Strach = pocenie się, drżenie, szybki oddech, ucieczka wzrokiem
   - Złość = napięte szczęki, zaciśnięte pięści, ostry ton
   - Smutek = opadnięte ramiona, unikanie kontaktu wzrokowego, monotonny głos

3. MICROTENSION (Napięcie w KAŻDYM zdaniu)
   Każda linia musi:
   - Poruszać fabułę DO PRZODU
   - Ujawnić coś o postaci
   - Budować napięcie
   - Lub dostarczyć payoff poprzedniego napięcia

   ❌ ZŁE: "Wszedł do pokoju i usiadł na krześle, myśląc o tym, co się stało."
   ✅ DOBRE: "Krzesło skrzypnęło pod jego ciężarem. Za oknem coś się poruszyło."

4. VOICE (Unikalny głos narracyjny)
   - NIE GENERIC - każda historia brzmi inaczej
   - Dobór słów odzwierciedla POV postaci
   - Rytm zdań pasuje do stanu emocjonalnego
   - Metafory z doświadczenia postaci

   ❌ ZŁE: "Świat był piękny i tajemniczy"
   ✅ DOBRE: "Świat był jak zepsuta zabawka - błyszczący, ale już bez baterii"

5. STAKES (Jasne dlaczego się przejmujemy)
   W pierwszych 3 akapitach ustal:
   - Co postać CHCE
   - Co straci jeśli PRZEGRA
   - Dlaczego nie może po prostu ODEJŚĆ

   Powtarzaj stakes subtelnie przez narrację

6. SENSORY ANCHORING (5 zmysłów, nie abstrakcje)
   ZAWSZE: wzrok + jeszcze 2 inne zmysły w każdej scenie
   - Dźwięki (konkretne: "trzask", nie "hałas")
   - Zapachy (specyficzne: "benzyna i pot", nie "nieprzyjemny zapach")
   - Dotyk (temperatura, tekstura, ból)
   - Smak (gdy applicable)

   ❌ ZŁE: "Laboratorium było stare i tajemnicze"
   ✅ DOBRE: "Laboratorum pachniało siarką i wilgocią. Pod palcami Eliasza drewno było lepkie."

7. SUBTEXT (Ludzie NIE mówią wprost)
   Dialog to NIEWYPOWIEDZIANE, nie wypowiedziane
   - Postaci kłamią, unikają, manipulują
   - Prawda jest w reakcjach, nie słowach
   - Każda replika ma ukryty motyw

   ❌ ZŁE:
   "— Jestem zły na ciebie — powiedział Jan.
    — Przepraszam — odpowiedziała Maria."

   ✅ DOBRE:
   "— Ładna pogoda — powiedział Jan, nie patrząc na nią.
   Maria zacisnęła palce na kubku. — Tak. Ładna."

8. SCENE STRUCTURE (Goal → Conflict → Disaster)
   Każda scena:
   - Postać wchodzi z CELEM
   - Napotyka PRZESZKODĘ (nie to czego się spodziewała)
   - Kończy się GORZEJ niż zaczęła (disaster) LUB z nowym problemem

   NIE: sceny które tylko "pokazują" bez zmiany sytuacji

9. KILL PURPLE PROSE (Usuń przesłodzenie)
   ❌ USUŃ: "tajemniczy", "mroczny", "nieubłagany", "bezlitosny"
   ❌ USUŃ: nadmiar przymiotników ("ciemna, zimna, wilgotna noc")
   ❌ USUŃ: poetyckie klisze ("serce pękało", "dusza płonęła")

   ✅ ZOSTAW: konkretne czasowniki i rzeczowniki
   ✅ ZOSTAW: nietypowe porównania z doświadczenia postaci

10. RHYTHM VARIATION (Zmienność długości)
    - Akcja/napięcie: krótkie zdania, staccato
    - Refleksja/opis: dłuższe, flowing
    - Moment kulminacji: jedno słowo per zdanie

    ❌ ZŁE: Wszystkie zdania tej samej długości (monotonia)
    ✅ DOBRE: Miksuj 5-słowne z 20-słownymi

═══════════════════════════════════════════════════════════════

💎 CHARAKTERYSTYKA ŚWIATOWEJ PROZY (tego uczymy się od bestów)

Stephen King: Konkretność, zero abstrakcji, napięcie od pierwszego zdania
Haruki Murakami: Surrealizm w codzienności, niedomówienia, dziwność jako normal
Neil Gaiman: Baśniowy ton w ciemnych historiach, mythic undertones
Gillian Flynn: Unreliable narrator, dark psychology, twisted reveals
Patrick Rothfuss: Poetycka proza bez purple prose, muzyczność języka

═══════════════════════════════════════════════════════════════

📖 FEW-SHOT EXAMPLES (Ucz się z tych)

❌ SŁABA PROZA (Unikaj tego):
"Elias był młodym alchemikiem. Mieszkał w starym mieście, gdzie życie płynęło spokojnie. Pewnego dnia odkrył tajemnicę swojej mistrzyni. To go bardzo zaskoczyło i zaniepokoiło."

Problemy: Telling not showing, generic, zero hooks, żadnego napięcia, abstrakcyjne

✅ SILNA PROZA (Naśladuj to):
"Elias zakrztusił się, gdy płomień eksplodował. Nie niebieski jak zwykle - czerwony. Siarki czuć nie było. Tylko... róże? Jego mistrzyni używała tej samej substancji wczoraj. Na ciele znaleziono ślady róż. Przypadek?"

Zalety: In medias res, sensory details, pytanie które hookuję, implied stakes, microtension

═══════════════════════════════════════════════════════════════

⚠️ MANDATORY RULES - INSTANT DISQUALIFICATION JEŚLI ZŁAMIESZ

1. NIE zaczyanj od: "W sercu...", "Dawno temu...", "Świat był..."
2. NIE używaj: "tajemniczy", "mroczny", "nieubłagany" więcej niż 1x per 5000 słów
3. KAŻDA scena zaczyna się od action/dialogue, NIE od opisu miejsca
4. KAŻDE 3 akapity: minimum 2 sensory details (wzrok + inny zmysł)
5. Dialog: Maximum 3 zdania per replika (ludzie nie wygłaszają monologów)
6. Zero exposition dumps - wplataj informacje przez akcję
7. Postacie mają CONTRADICTIONS - pokazuj je w akcji, nie opisuj
8. Każdy segment kończy się mini-cliffhanger (nawet jeśli subtelny)

═══════════════════════════════════════════════════════════════

TWOJE ZADANIE:
Napisz CZYSTĄ PROZĘ literacką na poziomie publikowanych bestsellerów.
Zero meta-komentarzy. Zero tytułów. Zero wyjaśnień "co się dzieje".
TYLKO LITERATURE. TYLKO MISTRZOSTWO.

Każde słowo ma wagę. Każde zdanie służy fabule. Każdy akapit buduje napięcie.
Twórz prozę której NIKT nie będzie mógł przestać czytać."""

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Wykonaj generację sekwencyjną wszystkich segmentów.

        Args:
            context: Zawiera 'segments', 'world', 'characters', 'structure'

        Returns:
            AgentResult z wygenerowaną narracją
        """
        segments = context.get("segments", [])
        world = context.get("world")
        characters = context.get("characters", [])
        structure = context.get("structure")

        if not segments or not world:
            self.add_error("Missing segments or world in context")
            return self._create_result(success=False, data={})

        # Generuj segmenty po kolei
        generated_segments: List[GeneratedSegment] = []
        full_narrative = []

        for i, segment in enumerate(segments):
            # Przygotuj kontekst dla tego segmentu
            context_summary = self._build_segment_context(
                segment=segment,
                world=world,
                characters=characters,
                previous_segments=generated_segments,
            )

            # Generuj segment
            try:
                segment_text, gen_segment = await self._generate_segment(
                    segment=segment,
                    context_summary=context_summary,
                    segment_number=i + 1,
                    total_segments=len(segments),
                )

                generated_segments.append(gen_segment)
                full_narrative.append(segment_text)

                # Zapisz do semantic memory (event nodes)
                for event in segment.key_events:
                    await self.memory.semantic.add_event(
                        content=event,
                        world_id=world.world_id,
                        timestamp_in_story=i,
                        significance=0.7,
                    )

            except Exception as e:
                self.add_error(f"Failed to generate segment {i+1}: {str(e)}")
                return self._create_result(success=False, data={})

        # Złącz wszystkie segmenty
        complete_narrative = "\n\n".join(full_narrative)
        total_words = len(complete_narrative.split())

        return self._create_result(
            success=True,
            data={
                "narrative_text": complete_narrative,
                "generated_segments": generated_segments,
                "total_words": total_words,
                "segments_count": len(generated_segments),
            },
        )

    def _build_segment_context(
        self,
        segment,
        world,
        characters,
        previous_segments: List[GeneratedSegment],
    ) -> str:
        """Zbuduj kontekst dla generacji segmentu"""

        context_parts = []

        # Świat (streszczenie)
        context_parts.append(f"ŚWIAT: {world.name}")
        context_parts.append(f"Konflikt: {world.core_conflict}")
        context_parts.append(f"Temat: {world.existential_theme}")

        # Postacie (zaangażowane w ten segment)
        involved_chars = [c for c in characters if c.name in segment.characters_involved]
        if involved_chars:
            context_parts.append("\nPOSTACIE W TYM SEGMENCIE:")
            for char in involved_chars[:3]:
                context_parts.append(f"- {char.name}: {char.internal_trajectory.starting_state.get('core_belief', '')}")

        # Poprzednie segmenty (streszczenie)
        if previous_segments:
            context_parts.append("\nCO SIĘ WYDARZYŁO WCZEŚNIEJ:")
            # Pokaż ostatnie 2-3 segmenty
            for prev_seg in previous_segments[-3:]:
                context_parts.append(f"- {prev_seg.segment.summary}")

        return "\n".join(context_parts)

    async def _generate_segment(
        self,
        segment,
        context_summary: str,
        segment_number: int,
        total_segments: int,
    ) -> tuple[str, GeneratedSegment]:
        """Generuj pojedynczy segment"""

        import time

        prompt = f"""{context_summary}

TERAZ NAPISZ SEGMENT {segment_number}/{total_segments}:

Plan tego segmentu:
- Streszczenie: {segment.summary}
- Wydarzenia: {', '.join(segment.key_events)}
- Lokacja: {segment.location}
- Funkcja: {segment.narrative_function}
- Target: ~{segment.estimated_words} słów

Napisz PEŁNĄ PROZĘ literacką. Poziom wydawniczy. Język polski doskonały.
Show, don't tell. Napięcie. Głębia. Konkretność.

TYLKO PROZA. Bez tytułów, numerów, meta-komentarzy."""

        start_time = time.time()

        # Generuj z GPT-4o (wysokiej jakości model)
        text, call = await self.call_model(
            prompt=prompt,
            temperature=1.0,  # MAXIMUM creativity dla prozy - bestseller level
            max_tokens=int(segment.estimated_words * 2.5),  # ~2.5 tokens per word (więcej przestrzeni)
        )

        generation_time = time.time() - start_time
        word_count = len(text.split())

        generated_segment = GeneratedSegment(
            segment=segment,
            text=text,
            word_count=word_count,
            tokens_used=call.total_tokens,
            cost_usd=call.cost_usd,
            generation_time_seconds=generation_time,
        )

        return text, generated_segment
