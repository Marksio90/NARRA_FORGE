"""
Consistency Guardian - ensures no contradictions or hallucinations.
"""
from app.core.openai_client import OpenAIClient
from app.core.cost_optimizer import CostOptimizer
from app.core.cost_tracker import CostTracker
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class IssueSeverity(Enum):
    """Severity of consistency issues."""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class IssueType(Enum):
    """Type of consistency issue."""
    CHARACTER = "character"
    WORLD = "world"
    PLOT = "plot"
    HALLUCINATION = "hallucination"
    TIMELINE = "timeline"


@dataclass
class ConsistencyIssue:
    """Consistency issue data."""
    type: IssueType
    severity: IssueSeverity
    description: str
    location: str
    suggestion: str


@dataclass
class ConsistencyResult:
    """Result of consistency check."""
    is_consistent: bool
    issues: List[ConsistencyIssue]


class ConsistencyGuardian:
    """
    Consistency Guardian - Strażnik Spójności.
    Weryfikuje każdy fragment tekstu pod kątem zgodności z kanonem.
    """

    def __init__(self):
        self.openai = OpenAIClient()

    async def verify(
        self,
        new_chapter: Dict[str, Any],
        world: Dict[str, Any],
        characters: List[Dict[str, Any]],
        previous_chapters: List[Dict[str, Any]],
        cost_optimizer: CostOptimizer,
        cost_tracker: CostTracker,
    ) -> ConsistencyResult:
        """
        Verify chapter consistency.

        Args:
            new_chapter: Chapter to verify
            world: World data
            characters: Characters data
            previous_chapters: Previous chapters
            cost_optimizer: Cost optimizer
            cost_tracker: Cost tracker

        Returns:
            ConsistencyResult with issues found
        """
        logger.info(f"Verifying consistency of chapter {new_chapter.get('number')}")

        # Select model
        model = cost_optimizer.select_model_for_task('consistency_check')

        # Prepare context
        world_bible = self._prepare_world_context(world)
        character_bible = self._prepare_character_context(characters)
        plot_context = self._prepare_plot_context(previous_chapters)

        # Build prompt
        prompt = f"""BAZA WIEDZY O ŚWIECIE:
{world_bible}

BAZA WIEDZY O POSTACIACH:
{character_bible}

DOTYCHCZASOWA FABUŁA:
{plot_context}

NOWY TEKST DO WERYFIKACJI:
---
{new_chapter.get('content', '')[:5000]}
---

Przeanalizuj tekst i zgłoś wszystkie problemy ze spójnością."""

        response = await self.openai.complete(
            model=model.value['model'],
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=prompt,
            temperature=0.3,
        )

        # Log cost
        cost_tracker.log_usage(
            model=model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            phase='consistency_checks'
        )

        # Parse response
        result = self._parse_response(response.content)

        logger.info(
            f"Consistency check complete: {'✅ Consistent' if result.is_consistent else f'❌ {len(result.issues)} issues'}"
        )

        return result

    SYSTEM_PROMPT = """Jesteś STRAŻNIKIEM SPÓJNOŚCI - Twoim zadaniem jest wyłapanie
KAŻDEJ nieścisłości, błędu i halucynacji w tekście.

Twoja analiza musi być:
- DOKŁADNA: Sprawdź każdy szczegół
- KOMPLETNA: Nie pomiń żadnego problemu
- KONSTRUKTYWNA: Zaproponuj rozwiązanie każdego problemu

ODPOWIEDZ W FORMACIE JSON:
{
    "is_consistent": true/false,
    "issues": [
        {
            "type": "character|world|plot|hallucination|timeline",
            "severity": "critical|major|minor",
            "description": "opis problemu",
            "location": "cytat z tekstu",
            "suggestion": "jak naprawić"
        }
    ]
}

ZASADY:
- CRITICAL: Poważny błąd fabularny (np. martwy bohater żyje)
- MAJOR: Istotna nieścisłość (np. zmiana wyglądu)
- MINOR: Drobny błąd (np. literówka w imieniu)"""

    def _prepare_world_context(self, world: Dict[str, Any]) -> str:
        """Prepare world context."""
        return f"""Nazwa: {world.get('name', 'Unknown')}
Opis: {world.get('description', '')}

ZASADY ŚWIATA:
{json.dumps(world.get('rules', {}), indent=2, ensure_ascii=False)}"""

    def _prepare_character_context(self, characters: List[Dict[str, Any]]) -> str:
        """Prepare characters context."""
        parts = []
        for char in characters:
            parts.append(f"""=== {char.get('name', 'Unknown')} ({char.get('role', '')}) ===
Wygląd: {json.dumps(char.get('appearance', {}), ensure_ascii=False)}
Osobowość: {json.dumps(char.get('personality', {}), ensure_ascii=False)}""")
        return "\n\n".join(parts)

    def _prepare_plot_context(self, previous_chapters: List[Dict[str, Any]]) -> str:
        """Prepare plot context."""
        summaries = []
        for chapter in previous_chapters[-5:]:  # Last 5 chapters
            summaries.append(
                f"Rozdział {chapter.get('number')}: {chapter.get('outline_summary', '')}"
            )
        return "\n".join(summaries)

    def _parse_response(self, response: str) -> ConsistencyResult:
        """Parse consistency check response."""
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
            else:
                data = json.loads(response)

            issues = []
            for issue_data in data.get('issues', []):
                issues.append(ConsistencyIssue(
                    type=IssueType(issue_data['type']),
                    severity=IssueSeverity(issue_data['severity']),
                    description=issue_data['description'],
                    location=issue_data['location'],
                    suggestion=issue_data['suggestion']
                ))

            return ConsistencyResult(
                is_consistent=data.get('is_consistent', True),
                issues=issues
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse consistency response: {e}")
            return ConsistencyResult(is_consistent=True, issues=[])
