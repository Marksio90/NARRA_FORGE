"""
Agent 07: Coherence Validator

Odpowiedzialność:
- Walidacja spójności logicznej
- Walidacja spójności psychologicznej
- Walidacja spójności czasowej
- Wychwytywanie błędów i niespójności

Model: gpt-4o-mini (może oceniać jakość nie będąc najlepszym)
"""
from typing import Any, Dict, List

from narra_forge.agents.base_agent import AnalysisAgent
from narra_forge.core.types import AgentResult, CoherenceValidation, PipelineStage


class CoherenceValidatorAgent(AnalysisAgent):
    """
    Agent walidujący spójność narracji.

    Sprawdza:
    - Logikę (czy wydarzenia mają sens)
    - Psychologię (czy postacie są spójne)
    - Czas (czy timeline się zgadza)
    """

    def __init__(self, config, memory, router):
        super().__init__(
            config=config,
            memory=memory,
            router=router,
            stage=PipelineStage.COHERENCE_VALIDATION,
        )

    def get_system_prompt(self) -> str:
        return """Jesteś WALIDATOREM KOHERENCJI w systemie produkcji narracji wydawniczych.

Twoja rola:
- Oceniasz spójność narracji na trzech poziomach
- Wychwytujesz błędy i niespójności
- NIE poprawiasz - tylko ZGŁASZASZ problemy
- Zwracasz szczegółowy raport

TRZY POZIOMY SPÓJNOŚCI:

1. **LOGICZNA (Logical Consistency)**
   - Czy wydarzenia mają logiczny sens?
   - Czy przyczyny prowadzą do skutków?
   - Czy nie ma contradictions w faktach?
   - Czy prawa świata są respektowane?

   Przykłady błędów:
   - "Postać używa magii mimo że w świecie nie ma magii"
   - "Wydarzenie A powoduje B, ale B nie pasuje do A"
   - "Przedmiot pojawia się z niczego"

2. **PSYCHOLOGICZNA (Psychological Consistency)**
   - Czy postacie działają zgodnie z charakterem?
   - Czy ich decyzje są uzasadnione?
   - Czy zmiany są properly motivated?
   - Czy reakcje emocjonalne mają sens?

   Przykłady błędów:
   - "Tchórzliwa postać nagle staje się odważna bez powodu"
   - "Postać zapomina o traumie z poprzedniego rozdziału"
   - "Motywacje się zmieniają bez uzasadnienia"

3. **CZASOWA (Temporal Consistency)**
   - Czy timeline się zgadza?
   - Czy czas płynie logicznie?
   - Czy nie ma anachronizmów?
   - Czy długości czasowe są realistyczne?

   Przykłady błędów:
   - "Podróż trwa 1 dzień, ale opisano 3 noce"
   - "Rana goi się zbyt szybko/wolno"
   - "Wydarzenia się nakładają czasowo"

SCORING:

Coherence Score: 0.0-1.0
- 1.0 = Perfekcyjna spójność
- 0.9-1.0 = Bardzo dobra (akceptowalne)
- 0.85-0.9 = Dobra (minimalne issues)
- 0.8-0.85 = Przeciętna (wymagane poprawki)
- <0.8 = Słaba (wymaga rewrite)

Format wyjścia (JSON):
{
  "coherence_score": 0.0-1.0,
  "logical_consistency": true|false,
  "psychological_consistency": true|false,
  "temporal_consistency": true|false,
  "issues": [
    {
      "type": "logical|psychological|temporal",
      "severity": "critical|major|minor",
      "location": "Gdzie w tekście",
      "description": "Opis problemu",
      "suggestion": "Jak naprawić"
    }
  ],
  "warnings": [
    "Ostrzeżenie 1",
    "Ostrzeżenie 2"
  ],
  "strengths": [
    "Mocna strona 1",
    "Mocna strona 2"
  ],
  "overall_assessment": "Ogólna ocena"
}

Waliduj BEZLITOŚNIE. Znajdź KAŻDY problem. Bądź PRECYZYJNY."""

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Wykonaj walidację spójności.

        Args:
            context: Zawiera 'narrative_text', 'world', 'characters'

        Returns:
            AgentResult z raportem walidacji
        """
        narrative_text = context.get("narrative_text")
        world = context.get("world")
        characters = context.get("characters", [])

        if not narrative_text or not world:
            self.add_error("Missing narrative_text or world in context")
            return self._create_result(success=False, data={})

        # Limit długości tekstu dla walidacji (max ~10k słów = ~20k tokenów)
        words = narrative_text.split()
        if len(words) > 10000:
            # Próbkuj reprezentatywne fragmenty
            sample_text = " ".join(words[:3000] + words[len(words)//2-1500:len(words)//2+1500] + words[-3000:])
            self.add_warning("Narrative too long, sampling for validation")
        else:
            sample_text = narrative_text

        # Przygotuj prompt
        char_info = "\n".join([
            f"- {c.name}: {c.internal_trajectory.starting_state.get('core_belief', '')}"
            for c in characters[:5]
        ]) if characters else "Brak"

        prompt = f"""Zwaliduj spójność poniższej narracji:

KONTEKST ŚWIATA:
- Świat: {world.name}
- Prawa rzeczywistości: {world.reality_laws}
- Konflikt: {world.core_conflict}

POSTACIE:
{char_info}

NARRACJA DO WALIDACJI:
{sample_text}

Sprawdź spójność:
1. Logiczną (czy wydarzenia mają sens)
2. Psychologiczną (czy postacie są spójne)
3. Czasową (czy timeline się zgadza)

Zwróć szczegółowy raport jako JSON."""

        try:
            validation_data, call = await self.call_model_json(
                prompt=prompt,
                temperature=0.2,  # Niska - precyzyjna analiza
                max_tokens=3000,
            )

            # Twórz CoherenceValidation object
            issues = validation_data.get("issues", [])
            critical_issues = [i for i in issues if i.get("severity") == "critical"]

            # Determine if passed
            score = validation_data.get("coherence_score", 0.0)
            passed = (
                score >= self.config.min_coherence_score
                and len(critical_issues) == 0
                and validation_data.get("logical_consistency", False)
                and validation_data.get("psychological_consistency", False)
                and validation_data.get("temporal_consistency", False)
            )

            validation = CoherenceValidation(
                passed=passed,
                coherence_score=score,
                logical_consistency=validation_data.get("logical_consistency", False),
                psychological_consistency=validation_data.get("psychological_consistency", False),
                temporal_consistency=validation_data.get("temporal_consistency", False),
                issues=[i["description"] for i in issues],
                warnings=validation_data.get("warnings", []),
            )

            if not passed:
                self.add_error(
                    f"Validation FAILED: score={score:.2f}, critical_issues={len(critical_issues)}"
                )

            return self._create_result(
                success=passed,  # Success = validation passed
                data={
                    "validation": validation,
                    "validation_report": validation_data,
                    "critical_issues": critical_issues,
                },
            )

        except Exception as e:
            self.add_error(f"Coherence validation failed: {str(e)}")
            return self._create_result(success=False, data={})
