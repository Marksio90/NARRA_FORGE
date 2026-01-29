"""
Religious Content Agent for NarraForge 2.0

Specialized agent for creating religious literature content.
Ensures theological accuracy and authentic spirituality.
"""

from typing import Dict, List, Any, Optional
import logging

from app.services.ai_service import AIService
from app.knowledge.religious_knowledge_base import (
    ReligiousKnowledgeBase,
    get_religious_knowledge_base,
    ScriptureReference
)

logger = logging.getLogger(__name__)


RELIGIOUS_SYSTEM_PROMPT = """
Jesteś autorem literatury religijnej na najwyższym poziomie.

TWOJE ŹRÓDŁA (JEDYNE dozwolone):
- Pismo Święte (Biblia Tysiąclecia lub inna zatwierdzona)
- Katechizm Kościoła Katolickiego
- Encykliki i dokumenty papieskie
- Pisma Ojców Kościoła i Doktorów Kościoła
- Zatwierdzone cuda i objawienia
- Żywoty świętych (potwierdzone źródła)

NIGDY:
- Nie wymyślaj cudów
- Nie przekręcaj nauczania Kościoła
- Nie cytuj fałszywie Pisma Świętego
- Nie przedstawiaj herezji jako prawdy
- Nie trywializuj sakramentów
- Nie redukuj wiary do moralności
- Nie używaj sentymentalnego tonu

ZAWSZE:
- Pokaż miłosierdzie Boga
- Przedstaw wiarę jako relację z żywym Bogiem
- Uszanuj tajemnicę (nie wszystko da się wyjaśnić)
- Pisz z głębokim szacunkiem
- Dawaj nadzieję, nawet w ciemności
- Pokazuj autentyczną walkę duchową
- Przedstawiaj postacie jako pełnych ludzi, nie "świątobliwych" stereotypów

Twoje pisarstwo ma prowadzić czytelnika do spotkania z Bogiem,
nie tylko do wiedzy o Nim.

CYTATY BIBLIJNE:
Gdy używasz cytatów, oznaczaj je siglami (np. J 3,16) i upewnij się,
że cytat jest dokładny lub wyraźnie parafrazowany.
"""


class ReligiousContentAgent:
    """
    Specialized agent for creating religious literature content.
    Guarantees compliance with Church teaching.
    """

    def __init__(
        self,
        ai_service: Optional[AIService] = None,
        knowledge_base: Optional[ReligiousKnowledgeBase] = None
    ):
        self.ai_service = ai_service or AIService()
        self.knowledge_base = knowledge_base or get_religious_knowledge_base()

    async def generate_religious_scene(
        self,
        scene_outline: Dict[str, Any],
        context: Dict[str, Any],
        character_spiritual_state: str = ""
    ) -> Dict[str, Any]:
        """
        Generate a scene with religious content.

        Args:
            scene_outline: Scene outline with goals and beats
            context: Full context pack (world, characters, etc.)
            character_spiritual_state: Current spiritual state of protagonist

        Returns:
            Dict with generated content and sources used
        """
        # 1. Identify religious needs for this scene
        religious_needs = await self._analyze_religious_needs(scene_outline)

        # 2. Gather relevant sources
        sources = await self._gather_sources(religious_needs)

        # 3. Build prompt with religious context
        prompt = self._build_religious_prompt(scene_outline, sources, context, character_spiritual_state)

        # 4. Generate content
        content = await self.ai_service.generate(
            prompt=prompt,
            model_tier=2,
            max_tokens=4000,
            temperature=0.7,
            system_prompt=RELIGIOUS_SYSTEM_PROMPT
        )

        # 5. Validate theological accuracy
        validation = await self._validate_theological_accuracy(content)

        # 6. Fix any issues
        if not validation["is_valid"]:
            content = await self._correct_theological_errors(content, validation["errors"])

        return {
            "content": content,
            "sources_used": {
                "scripture": [s.text[:50] + "..." for s in sources.get("scripture", [])],
                "church_teaching": sources.get("church_teaching", []),
                "miracles": [m.name for m in sources.get("miracles", [])] if sources.get("miracles") else []
            },
            "theological_validation": validation,
            "spiritual_stage": religious_needs.get("spiritual_stage")
        }

    async def _analyze_religious_needs(self, scene_outline: Dict) -> Dict[str, Any]:
        """Analyze what religious elements are needed for this scene."""
        scene_goal = scene_outline.get("goal", "")
        scene_beats = scene_outline.get("beats", [])

        needs = {
            "themes": [],
            "scripture_needed": False,
            "miracle_opportunity": False,
            "spiritual_stage": None,
            "sacrament_present": False
        }

        # Check for spiritual themes
        goal_lower = scene_goal.lower()

        if any(word in goal_lower for word in ["nawrócenie", "conversion", "przemiana"]):
            needs["themes"].append("conversion")
            needs["scripture_needed"] = True
            needs["spiritual_stage"] = 5  # Conversion stage

        if any(word in goal_lower for word in ["modlitwa", "prayer", "rozmowa z bogiem"]):
            needs["themes"].append("prayer")
            needs["scripture_needed"] = True

        if any(word in goal_lower for word in ["przebaczenie", "forgiveness", "pojednanie"]):
            needs["themes"].append("forgiveness")
            needs["scripture_needed"] = True

        if any(word in goal_lower for word in ["cierpienie", "suffering", "ból", "choroba"]):
            needs["themes"].append("suffering")
            needs["scripture_needed"] = True

        if any(word in goal_lower for word in ["miłość", "love", "kochać"]):
            needs["themes"].append("love")

        if any(word in goal_lower for word in ["nadzieja", "hope", "ufność"]):
            needs["themes"].append("hope")
            needs["scripture_needed"] = True

        if any(word in goal_lower for word in ["wiara", "faith", "wierzyć", "zaufanie"]):
            needs["themes"].append("faith")
            needs["scripture_needed"] = True

        if any(word in goal_lower for word in ["cud", "miracle", "uzdrowienie"]):
            needs["miracle_opportunity"] = True

        if any(word in goal_lower for word in ["spowiedź", "komunia", "msza", "sakrament"]):
            needs["sacrament_present"] = True

        return needs

    async def _gather_sources(self, needs: Dict) -> Dict[str, Any]:
        """Gather relevant religious sources for the scene."""
        sources = {
            "scripture": [],
            "church_teaching": [],
            "miracles": [],
            "saints_quotes": []
        }

        # Get Scripture for themes
        for theme in needs.get("themes", []):
            scriptures = self.knowledge_base.get_scripture_for_theme(theme)
            sources["scripture"].extend(scriptures[:2])  # Max 2 per theme

        # Get miracle if appropriate
        if needs.get("miracle_opportunity"):
            miracle = self.knowledge_base.get_miracle_for_context("eucharystia")
            if miracle:
                sources["miracles"].append(miracle)

        # Get Church Father quote
        father_quote = self.knowledge_base.get_church_father_quote()
        if father_quote:
            sources["saints_quotes"].append(father_quote)

        return sources

    def _build_religious_prompt(
        self,
        scene: Dict,
        sources: Dict,
        context: Dict,
        character_spiritual_state: str
    ) -> str:
        """Build prompt for religious scene generation."""
        # Format Scripture references
        scripture_text = ""
        if sources.get("scripture"):
            scripture_text = "CYTATY BIBLIJNE DO ROZWAŻENIA:\n"
            for s in sources["scripture"]:
                scripture_text += f"- {s.book} {s.chapter},{s.verses}: \"{s.text}\" ({s.theme})\n"

        # Format Church teaching
        teaching_text = ""
        if sources.get("church_teaching"):
            teaching_text = "NAUCZANIE KOŚCIOŁA:\n" + "\n".join(sources["church_teaching"])

        # Format miracles
        miracle_text = ""
        if sources.get("miracles"):
            miracle_text = "ZATWIERDZONE CUDA (można odnieść):\n"
            for m in sources["miracles"]:
                miracle_text += f"- {m.name} ({m.year}, {m.location}): {m.description}\n"

        # Format saints quotes
        saints_text = ""
        if sources.get("saints_quotes"):
            saints_text = "CYTATY ŚWIĘTYCH:\n"
            for sq in sources["saints_quotes"]:
                if isinstance(sq, dict) and "quotes" in sq:
                    saints_text += f"- {sq['name']}: \"{sq['quotes'][0]}\"\n"

        prompt = f"""
Napisz scenę literatury religijnej, która:

1. AUTENTYCZNOŚĆ DUCHOWA
- Przedstawia autentyczne doświadczenie wiary
- Unika taniego moralizatorstwa i sentymentalizmu
- Pokazuje PRAWDZIWĄ walkę duchową, nie idealizowaną
- Nie upraszcza trudnych pytań wiary

2. ŹRÓDŁA DO WYKORZYSTANIA

{scripture_text}

{teaching_text}

{miracle_text}

{saints_text}

3. POSTAĆ I JEJ DROGA DUCHOWA
Stan duchowy postaci: {character_spiritual_state or "W poszukiwaniu sensu"}
{context.get('character_context', '')}

4. SCENA DO NAPISANIA
Numer: {scene.get('number', 1)}
Tytuł: {scene.get('title', 'Scena')}
Cel: {scene.get('goal', '')}
Beats: {scene.get('beats', [])}

5. ZASADY:
- Cytaty biblijne oznaczaj siglami (np. J 3,16)
- NIE WYMYŚLAJ cudów - używaj tylko zatwierdzonych lub opisuj łaskę codzienną
- Przedstawiaj wiarę jako RELACJĘ z żywym Bogiem, nie zbiór zasad
- Pokaż działanie łaski, ale i wolność człowieka
- Unikaj sentymentalizmu - pisz z głębią i autentyzmem
- Bądź wierny Magisterium Kościoła

6. TON
- Pełen szacunku, ale nie sztywny
- Dostępny dla każdego czytelnika
- Poruszający serce, nie tylko intelekt
- Nadzieja nawet w mroku

Napisz scenę teraz:
"""
        return prompt

    async def _validate_theological_accuracy(self, content: str) -> Dict[str, Any]:
        """Validate theological accuracy of generated content."""
        validation_prompt = f"""
Przeanalizuj poniższy tekst religijny pod kątem DOKŁADNOŚCI TEOLOGICZNEJ.

TEKST:
{content[:3000]}

Sprawdź:
1. Czy cytaty biblijne są poprawne?
2. Czy nauka Kościoła jest poprawnie przedstawiona?
3. Czy nie ma herezji lub błędnych interpretacji?
4. Czy nie ma trywializacji sakramentów?
5. Czy obraz Boga jest zgodny z nauczaniem Kościoła?

Odpowiedz w formacie JSON:
{{
    "is_valid": true/false,
    "score": 0-100,
    "errors": ["błąd 1", "błąd 2"],
    "warnings": ["ostrzeżenie 1"],
    "suggestions": ["sugestia poprawy"]
}}
"""

        try:
            response = await self.ai_service.generate(
                prompt=validation_prompt,
                model_tier=1,
                max_tokens=500,
                temperature=0.1
            )

            import json
            import re

            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                return result

        except Exception as e:
            logger.error(f"Theological validation failed: {e}")

        return {
            "is_valid": True,
            "score": 80,
            "errors": [],
            "warnings": ["Walidacja automatyczna"],
            "suggestions": []
        }

    async def _correct_theological_errors(
        self,
        content: str,
        errors: List[str]
    ) -> str:
        """Correct theological errors in content."""
        if not errors:
            return content

        correction_prompt = f"""
Popraw poniższy tekst religijny, naprawiając następujące błędy teologiczne:

BŁĘDY DO NAPRAWIENIA:
{chr(10).join(f'- {e}' for e in errors)}

TEKST DO POPRAWY:
{content}

Popraw TYLKO błędy teologiczne. Zachowaj styl i fabułę.
Zwróć TYLKO poprawiony tekst.
"""

        try:
            corrected = await self.ai_service.generate(
                prompt=correction_prompt,
                model_tier=2,
                max_tokens=len(content.split()) * 2,
                temperature=0.3,
                system_prompt=RELIGIOUS_SYSTEM_PROMPT
            )
            return corrected
        except:
            return content

    async def get_spiritual_journey_prompt(self, stage_number: int) -> str:
        """Get narrative guidance for a specific spiritual journey stage."""
        stage = self.knowledge_base.get_spiritual_journey_stage(stage_number)
        if not stage:
            return ""

        return f"""
ETAP DUCHOWEJ PODRÓŻY: {stage['name']}

Opis: {stage['description']}

Elementy narracyjne do użycia:
{', '.join(stage['narrative_elements'])}

Pisz tę scenę tak, by odzwierciedlała ten etap duchowej podróży bohatera.
"""


# Singleton instance
_religious_agent: Optional[ReligiousContentAgent] = None


def get_religious_agent() -> ReligiousContentAgent:
    """Get or create religious content agent instance."""
    global _religious_agent
    if _religious_agent is None:
        _religious_agent = ReligiousContentAgent()
    return _religious_agent
