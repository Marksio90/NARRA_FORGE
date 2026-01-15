"""
Agent 09: Editorial Reviewer

Odpowiedzialność:
- Finalna redakcja wydawnicza
- Wychwytywanie drobnych błędów
- Sprawdzanie flow narracji
- Finalne cięcia i poprawki

Model: gpt-4o-mini (może oceniać i sugerować bez bycia najlepszym)
"""
from typing import Any, Dict, List

from narra_forge.agents.base_agent import AnalysisAgent
from narra_forge.core.types import AgentResult, PipelineStage


class EditorialReviewerAgent(AnalysisAgent):
    """
    Agent wykonujący finalną redakcję wydawniczą.

    Ostatnia kontrola przed publikacją.
    """

    def __init__(self, config, memory, router):
        super().__init__(
            config=config,
            memory=memory,
            router=router,
            stage=PipelineStage.EDITORIAL_REVIEW,
        )

    def get_system_prompt(self) -> str:
        return """Jesteś REDAKTOREM WYDAWNICZYM w systemie produkcji narracji wydawniczych.

Twoja rola:
- Wykonujesz FINALNĄ redakcję przed publikacją
- Wychwytujesz drobne błędy i niedociągnięcia
- Oceniasz flow narracji
- Proponujesz finalne cięcia i poprawki

NIE PRZEPISUJESZ TEKSTU - tylko OCENIASZ i PROPONUJESZ.

SPRAWDZASZ:

1. **BŁĘDY JĘZYKOWE**
   - Literówki, literówki, literówki
   - Błędy ortograficzne
   - Błędy interpunkcyjne
   - Błędy składniowe

2. **FLOW NARRACJI**
   - Czy tekst płynie naturalnie?
   - Czy nie ma "zaskoków" (złych przejść)?
   - Czy tempo jest odpowiednie?
   - Czy nie ma "martwyche plam"?

3. **REDUNDANCJE**
   - Czy coś się powtarza bez powodu?
   - Czy są zbędne fragmenty?
   - Czy można coś skrócić bez straty?

4. **DIALOGI**
   - Czy są naturalne?
   - Czy każda postać ma swój głos?
   - Czy tagi dialogowe są dyskretne?

5. **EMOCJE I NAPIĘCIE**
   - Czy emocje są pokazane, nie opowiedziane?
   - Czy napięcie rośnie odpowiednio?
   - Czy kulminacja jest satysfakcjonująca?

6. **ZAKOŃCZENIE**
   - Czy zakończenie jest kompletne?
   - Czy nie ma loose ends (unless intended)?
   - Czy czytelnik czuje satysfakcję?

7. **OVERALL QUALITY**
   - Czy to jest gotowe do publikacji?
   - Czy osiąga standardy wydawnicze?
   - Co można jeszcze poprawić?

Format wyjścia (JSON):
{
  "editorial_score": 0.0-1.0,
  "ready_for_publication": true|false,
  "issues_found": [
    {
      "type": "language|flow|redundancy|dialogue|other",
      "severity": "critical|major|minor",
      "location": "Gdzie w tekście",
      "description": "Opis problemu",
      "suggestion": "Propozycja poprawy"
    }
  ],
  "strengths": [
    "Mocna strona 1",
    "Mocna strona 2"
  ],
  "weaknesses": [
    "Słaba strona 1",
    "Słaba strona 2"
  ],
  "suggested_cuts": [
    {
      "location": "Gdzie",
      "reason": "Dlaczego",
      "impact": "Jaki będzie efekt"
    }
  ],
  "final_assessment": "Ogólna ocena i rekomendacja",
  "word_count_assessment": "Czy długość jest ok?"
}

Oceniaj SUROWO. Znajduj KAŻDY problem. Myśl jak WYDAWCA."""

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Wykonaj redakcję wydawniczą.

        Args:
            context: Zawiera 'stylized_text'

        Returns:
            AgentResult z raportem redakcyjnym
        """
        text = context.get("stylized_text") or context.get("narrative_text")

        if not text:
            self.add_error("No text to review in context")
            return self._create_result(success=False, data={})

        # Dla bardzo długich tekstów - próbkuj
        words = text.split()
        if len(words) > 12000:
            # Sample: początek, środek, koniec
            sample = " ".join(words[:4000] + words[len(words)//2-2000:len(words)//2+2000] + words[-4000:])
            self.add_warning("Text too long, sampling for review")
        else:
            sample = text

        prompt = f"""Wykonaj finalną redakcję wydawniczą poniższego tekstu:

TEKST DO REDAKCJI:
{sample}

Sprawdź:
- Błędy językowe
- Flow narracji
- Redundancje
- Dialogi
- Emocje i napięcie
- Zakończenie
- Ogólną jakość

Zwróć szczegółowy raport redakcyjny jako JSON."""

        try:
            review_data, call = await self.call_model_json(
                prompt=prompt,
                temperature=0.3,
                max_tokens=3000,
            )

            issues = review_data.get("issues_found", [])
            critical = [i for i in issues if i.get("severity") == "critical"]

            editorial_score = review_data.get("editorial_score", 0.0)
            ready = review_data.get("ready_for_publication", False)

            # Determine success
            success = (
                editorial_score >= 0.80
                and len(critical) == 0
                and ready
            )

            if not success:
                self.add_error(
                    f"Editorial review FAILED: score={editorial_score:.2f}, "
                    f"critical_issues={len(critical)}, ready={ready}"
                )

            # Apply minor fixes if possible (simple typos, etc.)
            # For now, we just report
            final_text = text

            return self._create_result(
                success=success,
                data={
                    "review_report": review_data,
                    "editorial_score": editorial_score,
                    "ready_for_publication": ready,
                    "issues_count": len(issues),
                    "critical_issues": critical,
                    "final_text": final_text,  # In future, might apply fixes
                },
            )

        except Exception as e:
            self.add_error(f"Editorial review failed: {str(e)}")
            return self._create_result(success=False, data={})
