"""
Agent 01: Brief Interpreter

Odpowiedzialność:
- Analiza zlecenia użytkownika
- Ekstrakcja intencji i wymagań
- Określenie skali produkcji
- Identyfikacja kluczowych elementów

Model: gpt-4o-mini (analiza)
"""
from typing import Any, Dict

from narra_forge.agents.base_agent import AnalysisAgent
from narra_forge.core.types import AgentResult, PipelineStage


class BriefInterpreterAgent(AnalysisAgent):
    """
    Agent interpretujący zlecenie produkcyjne.

    Analizuje brief użytkownika i tworzy strukturalną reprezentację wymagań.
    """

    def __init__(self, config, memory, router):
        super().__init__(
            config=config,
            memory=memory,
            router=router,
            stage=PipelineStage.BRIEF_INTERPRETATION,
        )

    def get_system_prompt(self) -> str:
        return """Jesteś ANALITYKIEM ZLECEŃ w systemie produkcji narracji wydawniczych.

Twoja rola:
- Analizujesz zlecenie użytkownika (brief)
- Wyodrębniasz kluczowe intencje i wymagania
- Określasz skalę i złożoność produkcji
- Identyfikujesz elementy narracyjne (postacie, motywy, setting)

ZASADY:
1. NIE improwizujesz - pracujesz tylko na tym, co jest w briefie
2. NIE dodajesz elementów z siebie
3. Wyodrębniasz STRUKTURĘ, nie treść
4. Zwracasz dane w formacie JSON

Format wyjścia (JSON):
{
  "production_type": "short_story|novella|novel|epic_saga",
  "genre": "fantasy|scifi|horror|thriller|mystery|drama|hybrid",
  "estimated_word_count": liczba_słów,
  "tone": "opis tonu (mroczny, lekki, etc.)",
  "themes": ["temat1", "temat2"],
  "key_elements": {
    "characters": ["postać1", "postać2"],
    "locations": ["lokacja1", "lokacja2"],
    "conflicts": ["konflikt1"],
    "motifs": ["motyw1"]
  },
  "constraints": ["ograniczenie1"],
  "quality_requirements": {
    "depth": "shallow|medium|deep",
    "complexity": "simple|medium|complex"
  },
  "narrative_focus": "character|plot|theme|world",
  "inspiration_analysis": "analiza inspiracji użytkownika"
}

Analizuj dokładnie. Ekstrahuj strukturę. Nie dodawaj nic od siebie."""

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Wykonaj interpretację briefu.

        Args:
            context: Zawiera 'brief' (ProductionBrief)

        Returns:
            AgentResult z analyzed_brief
        """
        brief = context.get("brief")
        if not brief:
            self.add_error("No brief provided in context")
            return self._create_result(success=False, data={})

        # Przygotuj prompt
        prompt = f"""Przeanalizuj poniższe zlecenie produkcji narracji:

TYP PRODUKCJI: {brief.production_type.value}
GATUNEK: {brief.genre.value}
INSPIRACJA: {brief.inspiration or 'Brak'}

Wyodrębnij strukturę wymagań i zwróć jako JSON."""

        # Wywołaj model
        try:
            analysis, call = await self.call_model_json(
                prompt=prompt,
                temperature=0.3,  # Niska temperatura - analiza deterministyczna
                max_tokens=2000,
            )

            # Validate required fields
            required = ["production_type", "genre", "estimated_word_count"]
            missing = [f for f in required if f not in analysis]
            if missing:
                self.add_warning(f"Missing fields in analysis: {missing}")

            # Zwróć wynik
            return self._create_result(
                success=True,
                data={
                    "analyzed_brief": analysis,
                    "production_type": brief.production_type.value,
                    "genre": brief.genre.value,
                    "original_inspiration": brief.inspiration,
                },
            )

        except Exception as e:
            self.add_error(f"Brief interpretation failed: {str(e)}")
            return self._create_result(success=False, data={})
