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
        return """Polish language PERFECTION. Minimal changes, maximum quality.

ENCODING: Polskie znaki UTF-8: ą ć ę ł ń ó ś ź ż

══════════════════════════════════════════════
YOUR JOB: Fix ONLY language mistakes
══════════════════════════════════════════════

✅ FIX grammatical errors (wrong cases, verb forms)
✅ FIX pleonasms ("niebieski kolor" → "niebieski")
✅ FIX anglicisms ("realizować" → "urzeczywistniać")
✅ FIX euphony (clumsy Polish word order)

❌ DO NOT change story, plot, events, characters
❌ DO NOT add adjectives or adverbs
❌ DO NOT add "poetic" language
❌ DO NOT rewrite - only POLISH GRAMMAR

══════════════════════════════════════════════
CRITICAL: PRESERVE THE ORIGINAL STYLE
══════════════════════════════════════════════

If text is already good → change NOTHING
If text is minimal and punchy → KEEP IT MINIMAL
If text uses short sentences → KEEP THEM SHORT

Example:
ORIGINAL: "Płomień zgasł. Elias zamknął oczy."
POLISHED: "Płomień zgasł. Elias zamknął oczy." (NO CHANGE - already perfect!)

Example:
ORIGINAL: "Elias realizował swój plan"
POLISHED: "Elias urzeczywistniał swój plan" (fixed anglicism)

══════════════════════════════════════════════

MINIMAL INTERVENTION. MAXIMUM RESPECT for original prose.
Only fix GRAMMAR and POLISH LANGUAGE mistakes."""

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

        prompt = f"""Jesteś KOREKTOREM GRAMATYCZNYM. Fix ONLY grammar mistakes.

🚫 CRITICAL - DO NOT:
❌ Add adjectives or adverbs ("szybki" → "szybki, zwinny")
❌ Add metaphors ("serce biło" → "serce waliło jak młot")
❌ Change vocabulary ("patrzył" → "wpatrywał się")
❌ Change sentence structure (keep short sentences SHORT)
❌ Add "poetic" language
❌ Rewrite style or voice

✅ ONLY FIX:
✓ Grammatical errors (wrong cases, verb conjugations)
✓ Spelling mistakes
✓ Punctuation errors
✓ Pleonasms ("niebieski kolor" → "niebieski")
✓ Anglicisms ("realizować" → "urzeczywistniać")

EXAMPLES:

BAD (adding metaphor):
IN: "Serce biło szybko."
OUT: "Serce waliło jak młot." ❌

GOOD (only grammar):
IN: "Serce biło szybko."
OUT: "Serce biło szybko." ✓ (NO CHANGE - already correct!)

BAD (adding adjective):
IN: "Płomień zgasł."
OUT: "Mały płomień zgasł." ❌

GOOD:
IN: "Płomień zgasł."
OUT: "Płomień zgasł." ✓

If original text is grammatically correct → return it UNCHANGED.

TEKST DO KOREKTY:
{text}

Zwróć TYLKO poprawiony tekst. Bez komentarzy, bez wyjaśnień."""

        stylized, call = await self.call_model(
            prompt=prompt,
            temperature=0.3,  # LOW - only grammar fixes, no creativity
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
