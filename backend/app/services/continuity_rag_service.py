"""
Continuity RAG Service for NarraForge 2.0

RAG (Retrieval-Augmented Generation) based continuity system.
Detects and fixes contradictions in real-time using vector search.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import logging

from app.services.ai_service import AIService
from app.config import settings

logger = logging.getLogger(__name__)


class FactType(str, Enum):
    """Types of facts tracked for continuity"""
    CHARACTER_APPEARANCE = "character_appearance"
    CHARACTER_TRAIT = "character_trait"
    CHARACTER_KNOWLEDGE = "character_knowledge"
    LOCATION_GEOGRAPHY = "location_geography"
    WORLD_RULE = "world_rule"
    TIMELINE_EVENT = "timeline_event"
    RELATIONSHIP = "relationship"
    OBJECT_STATE = "object_state"


@dataclass
class Fact:
    """A single fact extracted from content"""
    id: str
    text: str
    type: FactType
    source: str  # "world_bible", "character", "chapter_1", etc.
    entities: List[str]  # Names/objects involved
    timestamp_in_story: Optional[str] = None  # Timeline position
    confidence: float = 1.0
    is_immutable: bool = False  # Cannot change (e.g., birth date)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "text": self.text,
            "type": self.type.value,
            "source": self.source,
            "entities": self.entities,
            "timestamp_in_story": self.timestamp_in_story,
            "confidence": self.confidence,
            "is_immutable": self.is_immutable
        }


@dataclass
class Contradiction:
    """A detected contradiction between facts"""
    new_fact: Fact
    existing_fact: Fact
    type: str  # "direct", "temporal", "logical"
    severity: str  # "critical", "major", "minor"
    suggestion: str  # How to fix
    auto_fixable: bool = False


@dataclass
class ConsistencyReport:
    """Report of consistency check"""
    is_consistent: bool
    contradictions: List[Contradiction]
    warnings: List[str]
    facts_added: int
    auto_fix_available: bool


# Fact type configurations
FACT_TYPE_CONFIG = {
    FactType.CHARACTER_APPEARANCE: {
        "description": "Wygląd postaci",
        "examples": ["Ma niebieskie oczy", "Jest wysoka", "Ma bliznę na policzku"],
        "immutable": True,  # Cannot change
        "extraction_prompt": "cechy fizyczne, wygląd, kolor oczu/włosów, wzrost, znaki szczególne"
    },
    FactType.CHARACTER_TRAIT: {
        "description": "Cecha charakteru",
        "examples": ["Jest odważna", "Boi się wysokości"],
        "immutable": False,  # Can change with character development
        "extraction_prompt": "cechy charakteru, osobowość, zachowania, nawyki"
    },
    FactType.CHARACTER_KNOWLEDGE: {
        "description": "Co postać wie",
        "examples": ["Wie o zdradzie brata", "Nie zna prawdy o ojcu"],
        "immutable": False,
        "extraction_prompt": "wiedza postaci, sekrety, informacje znane/nieznane"
    },
    FactType.LOCATION_GEOGRAPHY: {
        "description": "Geografia miejsca",
        "examples": ["Zamek stoi na wzgórzu", "Rzeka płynie na wschód"],
        "immutable": True,
        "extraction_prompt": "położenie, geografia, kierunki, odległości, opis miejsc"
    },
    FactType.WORLD_RULE: {
        "description": "Zasada świata",
        "examples": ["Magia wymaga krwi", "Smoki są wymarłe"],
        "immutable": True,
        "extraction_prompt": "zasady świata, prawa magii/fizyki, ograniczenia"
    },
    FactType.TIMELINE_EVENT: {
        "description": "Wydarzenie w czasie",
        "examples": ["Wojna skończyła się 10 lat temu", "Spotkali się w środę"],
        "immutable": True,
        "extraction_prompt": "daty, linie czasowe, kolejność wydarzeń, kiedy coś się stało"
    },
    FactType.RELATIONSHIP: {
        "description": "Relacja między postaciami",
        "examples": ["Są braćmi", "Nienawidzą się"],
        "immutable": False,  # Relationships can change
        "extraction_prompt": "relacje między postaciami, rodzina, przyjaciele, wrogowie"
    },
    FactType.OBJECT_STATE: {
        "description": "Stan obiektu",
        "examples": ["Miecz jest złamany", "Klucz jest u Anny"],
        "immutable": False,
        "extraction_prompt": "stan przedmiotów, posiadanie, lokalizacja rzeczy"
    }
}


class ContinuityRAGService:
    """
    RAG-based continuity system.
    Extracts facts, stores them, and checks for contradictions.
    """

    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or AIService()
        # In-memory fact store (in production, use pgvector)
        self.fact_stores: Dict[str, List[Fact]] = {}

    async def initialize_for_project(self, project_id: str):
        """Initialize fact store for a project."""
        if project_id not in self.fact_stores:
            self.fact_stores[project_id] = []
            logger.info(f"Initialized fact store for project {project_id}")

    async def extract_and_store_facts(
        self,
        project_id: str,
        content: str,
        source: str
    ) -> int:
        """
        Extract facts from content and store them.

        Args:
            project_id: Project ID
            content: Text content to extract facts from
            source: Source identifier (e.g., "world_bible", "chapter_1")

        Returns:
            Number of facts extracted
        """
        await self.initialize_for_project(project_id)

        facts = await self._extract_facts(content, source)

        # Store facts
        for fact in facts:
            # Check if similar fact already exists
            existing = self._find_similar_fact(project_id, fact)
            if not existing:
                self.fact_stores[project_id].append(fact)

        logger.info(f"Extracted {len(facts)} facts from {source} for project {project_id}")
        return len(facts)

    async def check_consistency(
        self,
        project_id: str,
        new_content: str,
        source: str
    ) -> ConsistencyReport:
        """
        Check if new content is consistent with existing facts.

        Args:
            project_id: Project ID
            new_content: New content to check
            source: Source of new content

        Returns:
            ConsistencyReport with contradictions and warnings
        """
        await self.initialize_for_project(project_id)

        # Extract facts from new content
        new_facts = await self._extract_facts(new_content, source)

        contradictions = []
        warnings = []

        for new_fact in new_facts:
            # Find related existing facts
            related = self._find_related_facts(project_id, new_fact)

            for existing in related:
                # Check for contradiction
                contradiction = await self._check_contradiction(new_fact, existing)
                if contradiction:
                    contradictions.append(contradiction)

        return ConsistencyReport(
            is_consistent=len(contradictions) == 0,
            contradictions=contradictions,
            warnings=warnings,
            facts_added=len(new_facts),
            auto_fix_available=all(c.auto_fixable for c in contradictions)
        )

    async def auto_fix_contradictions(
        self,
        content: str,
        contradictions: List[Contradiction]
    ) -> str:
        """
        Automatically fix contradictions in content.

        Args:
            content: Content with contradictions
            contradictions: List of detected contradictions

        Returns:
            Fixed content
        """
        fixed_content = content

        for contradiction in contradictions:
            if not contradiction.auto_fixable:
                continue

            fix_prompt = f"""
NAPRAWA SPRZECZNOŚCI:

ISTNIEJĄCY FAKT (KANONICZNY):
{contradiction.existing_fact.text}
Źródło: {contradiction.existing_fact.source}

SPRZECZNOŚĆ W NOWYM TEKŚCIE:
{contradiction.new_fact.text}

TYP SPRZECZNOŚCI: {contradiction.type}
SUGESTIA NAPRAWY: {contradiction.suggestion}

TEKST DO NAPRAWY:
{fixed_content}

Popraw tekst tak, by był zgodny z kanonicznym faktem.
Zachowaj styl i ton oryginału.
Zmień TYLKO to, co jest konieczne.

Zwróć TYLKO poprawiony tekst, bez komentarzy.
"""

            try:
                fixed_content = await self.ai_service.generate(
                    prompt=fix_prompt,
                    model_tier=1,
                    max_tokens=len(fixed_content.split()) * 2,
                    temperature=0.3
                )
            except Exception as e:
                logger.error(f"Failed to auto-fix contradiction: {e}")

        return fixed_content

    async def _extract_facts(self, content: str, source: str) -> List[Fact]:
        """Extract facts from content using AI."""
        extraction_prompt = f"""
Przeanalizuj poniższy tekst i wyekstrahuj WSZYSTKIE fakty, które należy zapamiętać dla spójności fabuły.

TEKST:
{content[:3000]}  # Limit for context

KATEGORIE FAKTÓW:
1. CHARACTER_APPEARANCE - wygląd postaci (kolor oczu, włosów, wzrost, znaki szczególne)
2. CHARACTER_TRAIT - cechy charakteru
3. CHARACTER_KNOWLEDGE - co postać wie/nie wie
4. LOCATION_GEOGRAPHY - geografia miejsc
5. WORLD_RULE - zasady świata (magia, technologia, prawa)
6. TIMELINE_EVENT - wydarzenia z datami/kolejnością
7. RELATIONSHIP - relacje między postaciami
8. OBJECT_STATE - stan przedmiotów

Dla każdego faktu podaj:
- text: dokładny fakt
- type: kategoria z listy powyżej
- entities: nazwy osób/miejsc/rzeczy
- is_immutable: true jeśli fakt nie może się zmienić (np. kolor oczu)

Odpowiedz w formacie JSON:
{{
    "facts": [
        {{
            "text": "Anna ma niebieskie oczy",
            "type": "CHARACTER_APPEARANCE",
            "entities": ["Anna"],
            "is_immutable": true
        }},
        ...
    ]
}}

Wyekstrahuj TYLKO konkretne, sprawdzalne fakty. Unikaj interpretacji.
"""

        try:
            response = await self.ai_service.generate(
                prompt=extraction_prompt,
                model_tier=1,
                max_tokens=2000,
                temperature=0.2
            )

            # Parse response
            facts_data = self._parse_facts_json(response)

            facts = []
            for fd in facts_data:
                fact_type = self._parse_fact_type(fd.get("type", ""))
                if fact_type:
                    fact_id = hashlib.md5(
                        f"{source}:{fd['text']}".encode()
                    ).hexdigest()[:12]

                    facts.append(Fact(
                        id=fact_id,
                        text=fd["text"],
                        type=fact_type,
                        source=source,
                        entities=fd.get("entities", []),
                        is_immutable=fd.get("is_immutable", FACT_TYPE_CONFIG[fact_type]["immutable"]),
                        confidence=0.9
                    ))

            return facts

        except Exception as e:
            logger.error(f"Failed to extract facts: {e}")
            return []

    def _parse_facts_json(self, response: str) -> List[Dict]:
        """Parse facts JSON from AI response."""
        import re

        try:
            data = json.loads(response)
            return data.get("facts", [])
        except:
            pass

        # Try to find JSON in response
        json_match = re.search(r'\{[^{}]*"facts"[^{}]*\[.*?\]\s*\}', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                return data.get("facts", [])
            except:
                pass

        return []

    def _parse_fact_type(self, type_str: str) -> Optional[FactType]:
        """Parse fact type from string."""
        type_map = {
            "CHARACTER_APPEARANCE": FactType.CHARACTER_APPEARANCE,
            "CHARACTER_TRAIT": FactType.CHARACTER_TRAIT,
            "CHARACTER_KNOWLEDGE": FactType.CHARACTER_KNOWLEDGE,
            "LOCATION_GEOGRAPHY": FactType.LOCATION_GEOGRAPHY,
            "WORLD_RULE": FactType.WORLD_RULE,
            "TIMELINE_EVENT": FactType.TIMELINE_EVENT,
            "RELATIONSHIP": FactType.RELATIONSHIP,
            "OBJECT_STATE": FactType.OBJECT_STATE,
        }
        return type_map.get(type_str.upper())

    def _find_similar_fact(self, project_id: str, fact: Fact) -> Optional[Fact]:
        """Find similar existing fact."""
        facts = self.fact_stores.get(project_id, [])

        for existing in facts:
            # Same type and overlapping entities
            if existing.type == fact.type:
                entity_overlap = set(existing.entities) & set(fact.entities)
                if entity_overlap:
                    # Simple text similarity check
                    if self._text_similarity(existing.text, fact.text) > 0.8:
                        return existing

        return None

    def _find_related_facts(self, project_id: str, fact: Fact) -> List[Fact]:
        """Find facts related to the given fact."""
        facts = self.fact_stores.get(project_id, [])
        related = []

        for existing in facts:
            # Same type and overlapping entities
            if existing.type == fact.type:
                entity_overlap = set(existing.entities) & set(fact.entities)
                if entity_overlap:
                    related.append(existing)

        return related

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    async def _check_contradiction(self, new_fact: Fact, existing: Fact) -> Optional[Contradiction]:
        """Check if two facts contradict each other."""
        # Quick check: if texts are very similar, no contradiction
        similarity = self._text_similarity(new_fact.text, existing.text)
        if similarity > 0.8:
            return None

        # Use AI to check for contradiction
        check_prompt = f"""
Sprawdź czy te dwa fakty są ze sobą SPRZECZNE:

FAKT 1 (ustalony wcześniej):
"{existing.text}"

FAKT 2 (nowy):
"{new_fact.text}"

Oba dotyczą: {', '.join(set(existing.entities) & set(new_fact.entities))}
Kategoria: {existing.type.value}

Odpowiedz TYLKO w formacie JSON:
{{
    "is_contradiction": true/false,
    "type": "direct/temporal/logical/none",
    "severity": "critical/major/minor/none",
    "explanation": "krótkie wyjaśnienie",
    "suggestion": "jak naprawić (jeśli sprzeczność)",
    "auto_fixable": true/false
}}
"""

        try:
            response = await self.ai_service.generate(
                prompt=check_prompt,
                model_tier=1,
                max_tokens=500,
                temperature=0.1
            )

            # Parse response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))

                if data.get("is_contradiction"):
                    return Contradiction(
                        new_fact=new_fact,
                        existing_fact=existing,
                        type=data.get("type", "direct"),
                        severity=data.get("severity", "minor"),
                        suggestion=data.get("suggestion", ""),
                        auto_fixable=data.get("auto_fixable", False)
                    )

        except Exception as e:
            logger.error(f"Failed to check contradiction: {e}")

        return None

    def get_all_facts(self, project_id: str) -> List[Dict]:
        """Get all facts for a project."""
        facts = self.fact_stores.get(project_id, [])
        return [f.to_dict() for f in facts]

    def clear_facts(self, project_id: str):
        """Clear all facts for a project."""
        if project_id in self.fact_stores:
            del self.fact_stores[project_id]


# Singleton instance
_continuity_service: Optional[ContinuityRAGService] = None


def get_continuity_service() -> ContinuityRAGService:
    """Get or create continuity service instance."""
    global _continuity_service
    if _continuity_service is None:
        _continuity_service = ContinuityRAGService()
    return _continuity_service
