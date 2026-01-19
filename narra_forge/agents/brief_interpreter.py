"""
ETAP 1: Brief Interpreter Agent

Interpretuje zlecenie użytkownika i tworzy strukturalny ProjectBrief.
"""

import json
from typing import Dict, Any
from narra_forge.agents.base_agent import BaseAgent
from narra_forge.core.types import (
    PipelineStage,
    ProjectBrief,
    NarrativeForm,
    Genre,
    Tone,
    POVStyle,
)
from narra_forge.core.config import (
    calculate_target_word_count,
    calculate_chapter_count,
    get_subplot_count,
    get_supporting_char_count,
)


class BriefInterpreterAgent(BaseAgent):
    """
    Agent Interpretacji Zlecenia

    Odpowiedzialność: Analiza i interpretacja requestu użytkownika
    Input: User request (natural language)
    Output: ProjectBrief (strukturalny plan)
    """

    def get_system_prompt(self) -> str:
        return """Jesteś BRIEF INTERPRETER AGENT - ekspertem od interpretacji zleceń narracyjnych.

Twoja JEDYNA odpowiedzialność: Przeanalizować request użytkownika i wyciągnąć z niego strukturalne parametry projektu narracyjnego.

ZASADY:
1. Wykryj FORMĘ narracyjną (flash_fiction, short_story, novella, novel, epic_saga)
   - Jeśli użytkownik nie określił: wywnioskuj z kontekstu lub użyj "auto"

2. Wykryj GATUNEK literacki (fantasy, sci_fi, horror, thriller, mystery, romance, literary, etc.)
   - Jeśli hybryd: użyj "hybrid" + opisz w special_requirements

3. Wykryj TON (dark, light, poetic, dynamic, philosophical, etc.)

4. Wykryj preferowany POV STYLE (first_person, third_limited, third_omniscient, multiple_pov)

5. Wyciągnij CORE CONCEPT (esencja historii w 2-5 zdaniach)

6. Zidentyfikuj GŁÓWNY KONFLIKT

7. Określ PYTANIE TEMATYCZNE (co historia bada filozoficznie)

8. Opisz typ ŚWIATA i setting

9. Określ archetypy PROTAGONISTY i ANTAGONISTY

10. Wykryj specjalne wymagania użytkownika

WAŻNE:
- NIE TWÓRZ fabuły ani postaci - to zadanie późniejszych agentów
- TYLKO interpretuj to, co użytkownik podał
- Jeśli czegoś nie określił - użyj "auto" lub wartości domyślnych
- Zawsze zwracaj VALID JSON

Odpowiedz TYLKO w formacie JSON (bez dodatkowego tekstu):
{
    "form": "short_story|novella|novel|epic_saga|auto",
    "genre": "fantasy|sci_fi|horror|thriller|...|auto",
    "tone": "dark|light|poetic|...|auto",
    "pov_style": "first_person|third_limited|...|auto",
    "core_concept": "opis w 2-5 zdaniach",
    "central_conflict": "główny konflikt",
    "thematic_question": "pytanie filozoficzne",
    "world_type": "współczesny/fantasy/sci-fi/etc",
    "setting_scale": "miasto/kraj/planeta/galaktyka/etc",
    "protagonist_archetype": "typ bohatera",
    "antagonist_type": "typ antagonisty",
    "special_requirements": ["req1", "req2", ...]
}
"""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpretuj request użytkownika

        Args:
            context: Musi zawierać 'user_request'

        Returns:
            {'brief': ProjectBrief}
        """
        user_request = self._extract_from_context(context, "user_request")

        # Prompt dla modelu
        prompt = f"""Przeanalizuj następujące zlecenie narracyjne i wyciągnij z niego strukturalne parametry:

ZLECENIE UŻYTKOWNIKA:
{user_request}

Zwróć odpowiedź w formacie JSON zgodnie z instrukcją systemową."""

        # Generuj (JSON mode)
        response = await self._generate(
            prompt=prompt,
            temperature=0.3,  # Niższa - to analiza, nie kreatywność
            json_mode=True,
        )

        # Parse JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {response}")
            raise ValueError(f"Agent returned invalid JSON: {e}")

        # Konwertuj na enums
        form = NarrativeForm(data.get("form", "auto"))
        genre = Genre(data.get("genre", "auto"))
        tone = Tone(data.get("tone", "auto"))
        pov_style = POVStyle(data.get("pov_style", "auto"))

        # Oblicz target word count i chapter count
        target_word_count = calculate_target_word_count(form, self.config)
        target_chapter_count = calculate_chapter_count(target_word_count, self.config)
        subplot_count = get_subplot_count(form, self.config)
        supporting_count = get_supporting_char_count(form, self.config)

        # Utwórz ProjectBrief
        brief = ProjectBrief(
            form=form,
            genre=genre,
            tone=tone,
            pov_style=pov_style,
            target_word_count=target_word_count,
            target_chapter_count=target_chapter_count,
            core_concept=data.get("core_concept", ""),
            central_conflict=data.get("central_conflict", ""),
            thematic_question=data.get("thematic_question", ""),
            world_type=data.get("world_type", "nieokreślony"),
            setting_scale=data.get("setting_scale", "średnia skala"),
            protagonist_archetype=data.get("protagonist_archetype", "bohater"),
            antagonist_type=data.get("antagonist_type", "przeciwnik"),
            supporting_count=supporting_count,
            narrative_structure="3-act",  # Domyślna struktura (może być zmieniona w etapie 4)
            subplot_count=subplot_count,
            original_request=user_request,
            special_requirements=data.get("special_requirements", []),
        )

        self.logger.info(
            f"Brief interpreted: {brief.form.value} / {brief.genre.value} / "
            f"{target_word_count} words / {target_chapter_count} chapters"
        )

        return {"brief": brief}
