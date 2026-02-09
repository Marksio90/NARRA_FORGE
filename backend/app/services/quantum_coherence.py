"""
QUANTUM Narrative Coherence Analyzer - NarraForge 3.0 Phase 3

Advanced system for analyzing and ensuring narrative coherence across
all aspects of a story: plot, characters, timeline, world-building, and themes.

Uses multi-dimensional analysis to detect inconsistencies and suggest fixes.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum
from datetime import datetime
import uuid
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class CoherenceType(Enum):
    """Types of narrative coherence"""
    PLOT = "plot"                    # Plot consistency
    CHARACTER = "character"          # Character behavior consistency
    TIMELINE = "timeline"            # Temporal consistency
    WORLDBUILDING = "worldbuilding"  # World rules consistency
    THEME = "theme"                  # Thematic consistency
    DIALOGUE = "dialogue"            # Dialogue consistency
    TONE = "tone"                    # Tonal consistency
    CAUSALITY = "causality"          # Cause-effect relationships


class SeverityLevel(Enum):
    """Severity of coherence issues"""
    CRITICAL = "critical"      # Story-breaking inconsistency
    MAJOR = "major"            # Significant inconsistency
    MODERATE = "moderate"      # Noticeable inconsistency
    MINOR = "minor"            # Small inconsistency
    SUGGESTION = "suggestion"  # Not an error, but could be improved


class IssueStatus(Enum):
    """Status of coherence issue"""
    DETECTED = "detected"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class AnalysisDepth(Enum):
    """Depth of coherence analysis"""
    QUICK = "quick"        # Surface-level check
    STANDARD = "standard"  # Normal analysis
    DEEP = "deep"          # Thorough analysis
    QUANTUM = "quantum"    # Maximum depth, cross-referencing everything


class RelationType(Enum):
    """Types of narrative element relationships"""
    CAUSES = "causes"
    DEPENDS_ON = "depends_on"
    CONTRADICTS = "contradicts"
    SUPPORTS = "supports"
    REFERENCES = "references"
    PARALLELS = "parallels"
    FORESHADOWS = "foreshadows"
    RESOLVES = "resolves"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class NarrativeElement:
    """A single narrative element (event, fact, statement)"""
    element_id: str
    element_type: CoherenceType
    content: str
    chapter: int
    paragraph: int
    characters_involved: List[str]
    timestamp_in_story: Optional[str]  # Story timeline position
    location: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_id": self.element_id,
            "element_type": self.element_type.value,
            "content": self.content,
            "chapter": self.chapter,
            "paragraph": self.paragraph,
            "characters_involved": self.characters_involved,
            "timestamp_in_story": self.timestamp_in_story,
            "location": self.location,
            "metadata": self.metadata
        }


@dataclass
class ElementRelation:
    """Relationship between two narrative elements"""
    relation_id: str
    source_element: str
    target_element: str
    relation_type: RelationType
    strength: float  # 0.0 to 1.0
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relation_id": self.relation_id,
            "source_element": self.source_element,
            "target_element": self.target_element,
            "relation_type": self.relation_type.value,
            "strength": self.strength,
            "description": self.description
        }


@dataclass
class CoherenceIssue:
    """A detected coherence issue"""
    issue_id: str
    issue_type: CoherenceType
    severity: SeverityLevel
    status: IssueStatus
    title: str
    description: str
    affected_elements: List[str]  # Element IDs
    chapter_range: Tuple[int, int]
    suggested_fix: str
    auto_fixable: bool
    confidence: float  # 0.0 to 1.0
    detected_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "issue_type": self.issue_type.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "title": self.title,
            "description": self.description,
            "affected_elements": self.affected_elements,
            "chapter_range": list(self.chapter_range),
            "suggested_fix": self.suggested_fix,
            "auto_fixable": self.auto_fixable,
            "confidence": self.confidence,
            "detected_at": self.detected_at.isoformat()
        }


@dataclass
class TimelineEvent:
    """An event in the story timeline"""
    event_id: str
    description: str
    chapter: int
    story_time: str  # Relative or absolute time in story
    duration: Optional[str]
    characters: List[str]
    location: Optional[str]
    dependencies: List[str]  # Events that must happen before this

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "description": self.description,
            "chapter": self.chapter,
            "story_time": self.story_time,
            "duration": self.duration,
            "characters": self.characters,
            "location": self.location,
            "dependencies": self.dependencies
        }


@dataclass
class CharacterState:
    """Character state at a point in the story"""
    character_name: str
    chapter: int
    location: str
    emotional_state: str
    knowledge: List[str]  # What the character knows
    relationships: Dict[str, str]  # character -> relationship status
    physical_state: str
    goals: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_name": self.character_name,
            "chapter": self.chapter,
            "location": self.location,
            "emotional_state": self.emotional_state,
            "knowledge": self.knowledge,
            "relationships": self.relationships,
            "physical_state": self.physical_state,
            "goals": self.goals
        }


@dataclass
class WorldRule:
    """A rule of the story world"""
    rule_id: str
    category: str  # magic, physics, society, etc.
    description: str
    established_in_chapter: int
    exceptions: List[str]
    references: List[str]  # Element IDs that reference this rule

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "category": self.category,
            "description": self.description,
            "established_in_chapter": self.established_in_chapter,
            "exceptions": self.exceptions,
            "references": self.references
        }


@dataclass
class CoherenceReport:
    """Full coherence analysis report"""
    report_id: str
    project_id: str
    analysis_depth: AnalysisDepth
    total_elements: int
    total_relations: int
    issues: List[CoherenceIssue]
    timeline_events: List[TimelineEvent]
    world_rules: List[WorldRule]
    character_states: Dict[str, List[CharacterState]]
    coherence_scores: Dict[str, float]  # Type -> score
    overall_score: float
    analyzed_chapters: List[int]
    analysis_time_seconds: float
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "project_id": self.project_id,
            "analysis_depth": self.analysis_depth.value,
            "total_elements": self.total_elements,
            "total_relations": self.total_relations,
            "issues": [i.to_dict() for i in self.issues],
            "issues_by_severity": {
                "critical": len([i for i in self.issues if i.severity == SeverityLevel.CRITICAL]),
                "major": len([i for i in self.issues if i.severity == SeverityLevel.MAJOR]),
                "moderate": len([i for i in self.issues if i.severity == SeverityLevel.MODERATE]),
                "minor": len([i for i in self.issues if i.severity == SeverityLevel.MINOR]),
                "suggestion": len([i for i in self.issues if i.severity == SeverityLevel.SUGGESTION])
            },
            "timeline_events": [e.to_dict() for e in self.timeline_events],
            "world_rules": [r.to_dict() for r in self.world_rules],
            "character_arcs": {
                name: [s.to_dict() for s in states]
                for name, states in self.character_states.items()
            },
            "coherence_scores": self.coherence_scores,
            "overall_score": self.overall_score,
            "analyzed_chapters": self.analyzed_chapters,
            "analysis_time_seconds": self.analysis_time_seconds,
            "created_at": self.created_at.isoformat()
        }


# =============================================================================
# COHERENCE PATTERNS
# =============================================================================

COHERENCE_CHECK_PATTERNS = {
    CoherenceType.PLOT: [
        "Chekhov's Gun - introduced elements must be used",
        "Plot holes - unresolved story threads",
        "Deus ex machina - solutions appearing without setup",
        "Setup and payoff - promises must be fulfilled",
        "Conflict escalation - stakes should rise logically"
    ],
    CoherenceType.CHARACTER: [
        "Consistent personality traits",
        "Motivation alignment with actions",
        "Knowledge consistency - characters can't know unknowable things",
        "Skill consistency - abilities shown vs abilities used",
        "Arc progression - character growth should be gradual"
    ],
    CoherenceType.TIMELINE: [
        "Chronological order of events",
        "Travel time between locations",
        "Character aging consistency",
        "Seasonal/weather consistency",
        "Historical event references"
    ],
    CoherenceType.WORLDBUILDING: [
        "Magic system rules consistency",
        "Technology level consistency",
        "Social norms and laws",
        "Geography and distances",
        "Economic systems"
    ],
    CoherenceType.THEME: [
        "Thematic statements consistency",
        "Symbol usage consistency",
        "Moral stance consistency",
        "Message delivery alignment"
    ],
    CoherenceType.DIALOGUE: [
        "Voice consistency per character",
        "Vocabulary appropriate to character",
        "Information revelation consistency",
        "Emotional tone matching situation"
    ],
    CoherenceType.TONE: [
        "Genre expectations",
        "Scene mood consistency",
        "Humor level consistency",
        "Violence level consistency"
    ],
    CoherenceType.CAUSALITY: [
        "Cause precedes effect",
        "Proportional consequences",
        "Butterfly effects tracked",
        "Character decisions have consequences"
    ]
}


# =============================================================================
# MAIN CLASS
# =============================================================================

class QuantumCoherenceAnalyzer:
    """
    QUANTUM Narrative Coherence Analyzer

    Performs multi-dimensional analysis of narrative coherence,
    detecting inconsistencies and suggesting fixes.
    """

    def __init__(self):
        self.elements: Dict[str, NarrativeElement] = {}
        self.relations: Dict[str, ElementRelation] = {}
        self.issues: Dict[str, CoherenceIssue] = {}
        self.reports: Dict[str, CoherenceReport] = {}
        self.timelines: Dict[str, List[TimelineEvent]] = {}
        self.world_rules: Dict[str, WorldRule] = {}
        self.character_states: Dict[str, Dict[str, List[CharacterState]]] = {}

        # AI service for deep analysis
        self._ai_service = None

    def _get_ai_service(self):
        """Lazy-load AI service."""
        if self._ai_service is None:
            try:
                from app.services.ai_service import get_ai_service
                self._ai_service = get_ai_service()
            except Exception as e:
                logger.warning(f"Could not load AI service for coherence: {e}")
        return self._ai_service

    async def analyze_full_story(
        self,
        project_id: str,
        chapters: List[Dict[str, Any]],
        characters: List[Dict[str, Any]],
        world_info: Optional[Dict[str, Any]] = None,
        depth: AnalysisDepth = AnalysisDepth.STANDARD
    ) -> CoherenceReport:
        """
        Perform full coherence analysis on a story.
        """
        start_time = datetime.now()

        # Extract narrative elements
        elements = await self._extract_elements(chapters, characters)

        # Build relationship graph
        relations = await self._build_relations(elements)

        # Extract timeline
        timeline = await self._extract_timeline(chapters, characters)

        # Extract world rules
        rules = await self._extract_world_rules(chapters, world_info)

        # Track character states
        char_states = await self._track_character_states(chapters, characters)

        # Detect issues by type
        all_issues = []

        if depth in [AnalysisDepth.STANDARD, AnalysisDepth.DEEP, AnalysisDepth.QUANTUM]:
            all_issues.extend(await self._check_plot_coherence(elements, relations))
            all_issues.extend(await self._check_character_coherence(char_states, elements))
            all_issues.extend(await self._check_timeline_coherence(timeline))

        if depth in [AnalysisDepth.DEEP, AnalysisDepth.QUANTUM]:
            all_issues.extend(await self._check_worldbuilding_coherence(rules, elements))
            all_issues.extend(await self._check_theme_coherence(elements))
            all_issues.extend(await self._check_dialogue_coherence(elements, characters))

        if depth == AnalysisDepth.QUANTUM:
            all_issues.extend(await self._check_tone_coherence(elements))
            all_issues.extend(await self._check_causality_coherence(elements, relations))
            all_issues.extend(await self._cross_reference_all(elements, relations, rules, char_states))

        # Calculate coherence scores
        scores = self._calculate_coherence_scores(all_issues, len(elements))

        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores) if scores else 1.0

        end_time = datetime.now()
        analysis_time = (end_time - start_time).total_seconds()

        report = CoherenceReport(
            report_id=str(uuid.uuid4()),
            project_id=project_id,
            analysis_depth=depth,
            total_elements=len(elements),
            total_relations=len(relations),
            issues=all_issues,
            timeline_events=timeline,
            world_rules=list(rules.values()),
            character_states=char_states,
            coherence_scores=scores,
            overall_score=overall_score,
            analyzed_chapters=[ch.get("number", i+1) for i, ch in enumerate(chapters)],
            analysis_time_seconds=analysis_time,
            created_at=datetime.now()
        )

        self.reports[report.report_id] = report
        return report

    async def analyze_chapter(
        self,
        chapter_text: str,
        chapter_number: int,
        previous_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a single chapter for coherence with previous chapters.
        """
        issues = []

        # Check internal chapter coherence
        internal_issues = await self._check_chapter_internal_coherence(
            chapter_text, chapter_number
        )
        issues.extend(internal_issues)

        # Check coherence with previous context
        if previous_context:
            context_issues = await self._check_context_coherence(
                chapter_text, chapter_number, previous_context
            )
            issues.extend(context_issues)

        return {
            "chapter_number": chapter_number,
            "issues": [i.to_dict() for i in issues],
            "issue_count": len(issues),
            "critical_count": len([i for i in issues if i.severity == SeverityLevel.CRITICAL]),
            "coherence_score": 1.0 - (len(issues) * 0.05)  # Simple scoring
        }

    async def check_proposed_change(
        self,
        current_text: str,
        proposed_text: str,
        chapter_number: int,
        story_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if a proposed change would introduce coherence issues.
        """
        # Analyze what changes
        changes = await self._identify_changes(current_text, proposed_text)

        # Check each change for potential issues
        potential_issues = []

        for change in changes:
            issues = await self._evaluate_change_impact(
                change, chapter_number, story_context
            )
            potential_issues.extend(issues)

        return {
            "changes_detected": len(changes),
            "potential_issues": [i.to_dict() for i in potential_issues],
            "risk_level": self._calculate_risk_level(potential_issues),
            "recommendation": self._generate_change_recommendation(potential_issues)
        }

    async def suggest_fix(
        self,
        issue_id: str
    ) -> Dict[str, Any]:
        """
        Generate detailed fix suggestions for an issue.
        """
        issue = self.issues.get(issue_id)
        if not issue:
            return {"error": "Issue not found"}

        suggestions = await self._generate_fix_suggestions(issue)

        return {
            "issue": issue.to_dict(),
            "suggestions": suggestions,
            "auto_fix_available": issue.auto_fixable
        }

    async def auto_fix_issue(
        self,
        issue_id: str,
        chapter_text: str
    ) -> Dict[str, Any]:
        """
        Attempt to automatically fix a coherence issue.
        """
        issue = self.issues.get(issue_id)
        if not issue:
            return {"error": "Issue not found"}

        if not issue.auto_fixable:
            return {"error": "Issue cannot be auto-fixed"}

        fixed_text = await self._apply_auto_fix(issue, chapter_text)

        # Update issue status
        issue.status = IssueStatus.RESOLVED

        return {
            "success": True,
            "fixed_text": fixed_text,
            "changes_made": issue.suggested_fix
        }

    # =========================================================================
    # EXTRACTION METHODS
    # =========================================================================

    async def _extract_elements(
        self,
        chapters: List[Dict[str, Any]],
        characters: List[Dict[str, Any]]
    ) -> Dict[str, NarrativeElement]:
        """Extract narrative elements from chapters."""
        elements = {}
        character_names = [c.get("name", "") for c in characters]

        for chapter in chapters:
            chapter_num = chapter.get("number", 1)
            text = chapter.get("text", "")

            # Split into paragraphs for analysis
            paragraphs = text.split("\n\n")

            for para_idx, paragraph in enumerate(paragraphs):
                if not paragraph.strip():
                    continue

                # Determine element type based on content
                element_type = self._classify_paragraph(paragraph)

                # Find characters mentioned
                chars_mentioned = [
                    name for name in character_names
                    if name.lower() in paragraph.lower()
                ]

                element = NarrativeElement(
                    element_id=str(uuid.uuid4()),
                    element_type=element_type,
                    content=paragraph[:500],  # Truncate for storage
                    chapter=chapter_num,
                    paragraph=para_idx + 1,
                    characters_involved=chars_mentioned,
                    timestamp_in_story=self._extract_time_reference(paragraph),
                    location=self._extract_location(paragraph),
                    metadata={}
                )

                elements[element.element_id] = element

        self.elements.update(elements)
        return elements

    async def _build_relations(
        self,
        elements: Dict[str, NarrativeElement]
    ) -> Dict[str, ElementRelation]:
        """Build relationship graph between elements."""
        relations = {}
        element_list = list(elements.values())

        for i, elem1 in enumerate(element_list):
            for elem2 in element_list[i+1:]:
                # Check for various relationships
                rel_type, strength = self._detect_relationship(elem1, elem2)

                if rel_type and strength > 0.3:
                    relation = ElementRelation(
                        relation_id=str(uuid.uuid4()),
                        source_element=elem1.element_id,
                        target_element=elem2.element_id,
                        relation_type=rel_type,
                        strength=strength,
                        description=f"{elem1.element_type.value} -> {elem2.element_type.value}"
                    )
                    relations[relation.relation_id] = relation

        self.relations.update(relations)
        return relations

    async def _extract_timeline(
        self,
        chapters: List[Dict[str, Any]],
        characters: List[Dict[str, Any]]
    ) -> List[TimelineEvent]:
        """Extract timeline of events."""
        events = []
        character_names = [c.get("name", "") for c in characters]

        for chapter in chapters:
            chapter_num = chapter.get("number", 1)
            text = chapter.get("text", "")

            # Extract events (simplified - would use NLP in production)
            chapter_events = self._extract_events_from_text(
                text, chapter_num, character_names
            )
            events.extend(chapter_events)

        return events

    async def _extract_world_rules(
        self,
        chapters: List[Dict[str, Any]],
        world_info: Optional[Dict[str, Any]]
    ) -> Dict[str, WorldRule]:
        """Extract rules of the story world."""
        rules = {}

        # Add rules from world info if provided
        if world_info:
            for category, rule_list in world_info.get("rules", {}).items():
                for rule_desc in rule_list:
                    rule = WorldRule(
                        rule_id=str(uuid.uuid4()),
                        category=category,
                        description=rule_desc,
                        established_in_chapter=0,  # Pre-established
                        exceptions=[],
                        references=[]
                    )
                    rules[rule.rule_id] = rule

        # Extract implicit rules from text
        for chapter in chapters:
            chapter_num = chapter.get("number", 1)
            text = chapter.get("text", "")

            # Look for rule-establishing patterns
            extracted_rules = self._extract_rules_from_text(text, chapter_num)
            rules.update(extracted_rules)

        self.world_rules.update(rules)
        return rules

    async def _track_character_states(
        self,
        chapters: List[Dict[str, Any]],
        characters: List[Dict[str, Any]]
    ) -> Dict[str, List[CharacterState]]:
        """Track character states throughout the story."""
        states = {}

        for character in characters:
            name = character.get("name", "")
            states[name] = []

            for chapter in chapters:
                chapter_num = chapter.get("number", 1)
                text = chapter.get("text", "")

                # Extract character state from chapter
                state = self._extract_character_state(
                    name, text, chapter_num, character
                )
                if state:
                    states[name].append(state)

        return states

    # =========================================================================
    # COHERENCE CHECK METHODS
    # =========================================================================

    async def _check_plot_coherence(
        self,
        elements: Dict[str, NarrativeElement],
        relations: Dict[str, ElementRelation]
    ) -> List[CoherenceIssue]:
        """Check plot coherence."""
        issues = []

        # Check for unresolved plot threads
        plot_elements = [
            e for e in elements.values()
            if e.element_type == CoherenceType.PLOT
        ]

        # Check for Chekhov's Gun violations
        introduced_elements = self._find_introduced_elements(plot_elements)
        for elem in introduced_elements:
            if not self._is_element_resolved(elem, elements, relations):
                issues.append(CoherenceIssue(
                    issue_id=str(uuid.uuid4()),
                    issue_type=CoherenceType.PLOT,
                    severity=SeverityLevel.MAJOR,
                    status=IssueStatus.DETECTED,
                    title="Nierozwiązany wątek fabularny",
                    description=f"Element wprowadzony w rozdziale {elem.chapter} nie został rozwiązany",
                    affected_elements=[elem.element_id],
                    chapter_range=(elem.chapter, elem.chapter),
                    suggested_fix="Dodaj rozwiązanie lub usuń wprowadzenie elementu",
                    auto_fixable=False,
                    confidence=0.7,
                    detected_at=datetime.now()
                ))

        return issues

    async def _check_character_coherence(
        self,
        char_states: Dict[str, List[CharacterState]],
        elements: Dict[str, NarrativeElement]
    ) -> List[CoherenceIssue]:
        """Check character coherence."""
        issues = []

        for name, states in char_states.items():
            # Check for impossible knowledge
            for i, state in enumerate(states[:-1]):
                next_state = states[i + 1]

                # Check if character suddenly knows something they shouldn't
                new_knowledge = set(next_state.knowledge) - set(state.knowledge)
                for knowledge in new_knowledge:
                    if not self._is_knowledge_acquired_logically(
                        name, knowledge, state.chapter, next_state.chapter, elements
                    ):
                        issues.append(CoherenceIssue(
                            issue_id=str(uuid.uuid4()),
                            issue_type=CoherenceType.CHARACTER,
                            severity=SeverityLevel.MODERATE,
                            status=IssueStatus.DETECTED,
                            title=f"Niespójna wiedza postaci: {name}",
                            description=f"Postać wie coś, czego nie powinna: {knowledge}",
                            affected_elements=[],
                            chapter_range=(state.chapter, next_state.chapter),
                            suggested_fix="Dodaj scenę zdobywania wiedzy lub usuń odwołanie",
                            auto_fixable=False,
                            confidence=0.6,
                            detected_at=datetime.now()
                        ))

        return issues

    async def _check_timeline_coherence(
        self,
        timeline: List[TimelineEvent]
    ) -> List[CoherenceIssue]:
        """Check timeline coherence."""
        issues = []

        # Check for temporal paradoxes
        for i, event1 in enumerate(timeline):
            for event2 in timeline[i+1:]:
                if event2.event_id in event1.dependencies:
                    issues.append(CoherenceIssue(
                        issue_id=str(uuid.uuid4()),
                        issue_type=CoherenceType.TIMELINE,
                        severity=SeverityLevel.CRITICAL,
                        status=IssueStatus.DETECTED,
                        title="Paradoks czasowy",
                        description=f"Wydarzenie zależy od późniejszego wydarzenia",
                        affected_elements=[event1.event_id, event2.event_id],
                        chapter_range=(event1.chapter, event2.chapter),
                        suggested_fix="Zmień kolejność wydarzeń lub usuń zależność",
                        auto_fixable=False,
                        confidence=0.9,
                        detected_at=datetime.now()
                    ))

        return issues

    async def _check_worldbuilding_coherence(
        self,
        rules: Dict[str, WorldRule],
        elements: Dict[str, NarrativeElement]
    ) -> List[CoherenceIssue]:
        """Check world-building coherence."""
        issues = []

        # Check for rule violations
        for rule in rules.values():
            violations = self._find_rule_violations(rule, elements)
            for violation in violations:
                issues.append(CoherenceIssue(
                    issue_id=str(uuid.uuid4()),
                    issue_type=CoherenceType.WORLDBUILDING,
                    severity=SeverityLevel.MAJOR,
                    status=IssueStatus.DETECTED,
                    title=f"Naruszenie zasady świata: {rule.category}",
                    description=f"Element narusza zasadę: {rule.description}",
                    affected_elements=[violation],
                    chapter_range=(elements[violation].chapter, elements[violation].chapter),
                    suggested_fix="Dostosuj element do zasad świata lub dodaj wyjątek",
                    auto_fixable=False,
                    confidence=0.7,
                    detected_at=datetime.now()
                ))

        return issues

    async def _check_theme_coherence(
        self,
        elements: Dict[str, NarrativeElement]
    ) -> List[CoherenceIssue]:
        """Check thematic coherence using AI analysis."""
        issues = []

        ai_service = self._get_ai_service()
        if not ai_service:
            return issues

        # Group elements by chapter and extract theme-relevant content
        chapter_themes = {}
        for elem in elements.values():
            if elem.chapter not in chapter_themes:
                chapter_themes[elem.chapter] = []
            chapter_themes[elem.chapter].append(elem.content[:200])

        if len(chapter_themes) < 2:
            return issues

        # Sample content from early, middle, and late chapters
        chapters = sorted(chapter_themes.keys())
        sample_chapters = []
        if chapters:
            sample_chapters.append(chapters[0])
            if len(chapters) > 2:
                sample_chapters.append(chapters[len(chapters) // 2])
            sample_chapters.append(chapters[-1])

        samples = {}
        for ch in sample_chapters:
            texts = chapter_themes.get(ch, [])
            samples[ch] = " ".join(texts[:3])[:500]

        if not samples:
            return issues

        try:
            from app.services.ai_service import ModelTier

            prompt = f"""Przeanalizuj spójność tematyczną tych fragmentów powieści z różnych rozdziałów.

{chr(10).join(f"## Rozdział {ch}:{chr(10)}{text}" for ch, text in samples.items())}

Szukaj:
1. Sprzecznych przesłań moralnych (np. bohater promuje jedną wartość, a potem jej zaprzecza)
2. Niespójnego tonu (np. poważny dramat z nagle komediowym rozdziałem)
3. Porzuconych motywów (symbole/motywy zaczynane i nigdy nierozwinięte)

Odpowiedz TYLKO w JSON:
{{
    "issues": [
        {{
            "title": "krótki opis problemu",
            "description": "szczegółowy opis",
            "severity": "critical|major|moderate|minor",
            "chapters": [1, 5]
        }}
    ]
}}
Jeśli nie ma problemów, zwróć {{"issues": []}}"""

            response = await ai_service.generate(
                prompt=prompt,
                tier=ModelTier.TIER_1,
                temperature=0.2,
                max_tokens=800,
                json_mode=True,
                metadata={"task": "theme_coherence_check"}
            )

            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                for issue_data in data.get("issues", []):
                    severity_map = {
                        "critical": SeverityLevel.CRITICAL,
                        "major": SeverityLevel.MAJOR,
                        "moderate": SeverityLevel.MODERATE,
                        "minor": SeverityLevel.MINOR
                    }
                    ch_range = issue_data.get("chapters", [1, 1])
                    issues.append(CoherenceIssue(
                        issue_id=str(uuid.uuid4()),
                        issue_type=CoherenceType.THEME,
                        severity=severity_map.get(
                            issue_data.get("severity", "moderate"),
                            SeverityLevel.MODERATE
                        ),
                        status=IssueStatus.DETECTED,
                        title=issue_data.get("title", "Niespójność tematyczna"),
                        description=issue_data.get("description", ""),
                        affected_elements=[],
                        chapter_range=(
                            ch_range[0] if ch_range else 1,
                            ch_range[-1] if ch_range else 1
                        ),
                        suggested_fix="Przejrzyj i ujednolić temat/ton w wskazanych rozdziałach",
                        auto_fixable=False,
                        confidence=0.7,
                        detected_at=datetime.now()
                    ))
        except Exception as e:
            logger.warning(f"AI theme coherence check failed: {e}")

        return issues

    async def _check_dialogue_coherence(
        self,
        elements: Dict[str, NarrativeElement],
        characters: List[Dict[str, Any]]
    ) -> List[CoherenceIssue]:
        """Check dialogue coherence - ensures characters have consistent voices."""
        issues = []

        ai_service = self._get_ai_service()

        dialogue_elements = [
            e for e in elements.values()
            if e.element_type == CoherenceType.DIALOGUE
        ]

        if not dialogue_elements:
            return issues

        for character in characters:
            char_name = character.get("name", "")
            if not char_name:
                continue

            char_dialogues = [
                e for e in dialogue_elements
                if char_name in e.characters_involved
            ]

            if len(char_dialogues) < 2:
                continue

            # Rule-based voice check: vocabulary consistency
            vocab_sets = []
            for d in char_dialogues[:5]:
                words = set(d.content.lower().split())
                vocab_sets.append(words)

            # Check for dramatic vocabulary shifts between scenes
            if len(vocab_sets) >= 2:
                for i in range(len(vocab_sets) - 1):
                    overlap = len(vocab_sets[i] & vocab_sets[i + 1])
                    total = len(vocab_sets[i] | vocab_sets[i + 1])
                    similarity = overlap / total if total > 0 else 1.0

                    if similarity < 0.05:  # Very different vocabulary
                        issues.append(CoherenceIssue(
                            issue_id=str(uuid.uuid4()),
                            issue_type=CoherenceType.DIALOGUE,
                            severity=SeverityLevel.MODERATE,
                            status=IssueStatus.DETECTED,
                            title=f"Zmiana słownictwa postaci {char_name}",
                            description=(
                                f"Słownictwo {char_name} znacząco się zmienia między scenami. "
                                f"Podobieństwo słownictwa: {similarity:.1%}"
                            ),
                            affected_elements=[],
                            chapter_range=(
                                char_dialogues[i].chapter,
                                char_dialogues[i + 1].chapter
                            ),
                            suggested_fix=f"Ujednolicić styl wypowiedzi {char_name}",
                            auto_fixable=False,
                            confidence=0.6,
                            detected_at=datetime.now()
                        ))

            # AI-powered deep voice analysis (if available)
            if ai_service and len(char_dialogues) >= 3:
                voice_guide = character.get("voice_guide", {})
                samples = [f"R.{d.chapter}: {d.content[:150]}" for d in char_dialogues[:4]]

                try:
                    from app.services.ai_service import ModelTier

                    prompt = (
                        f"Czy te próbki dialogów postaci \"{char_name}\" są głosowo spójne?\n"
                        f"Profil: {voice_guide.get('speechPatterns', 'brak')}\n\n"
                        f"{chr(10).join(samples)}\n\n"
                        f"Odpowiedz JSON: {{\"consistent\": true/false, "
                        f"\"issue\": \"opis problemu lub null\"}}"
                    )

                    response = await ai_service.generate(
                        prompt=prompt,
                        tier=ModelTier.TIER_1,
                        temperature=0.2,
                        max_tokens=300,
                        json_mode=True,
                        metadata={"task": "dialogue_coherence", "character": char_name}
                    )

                    data = json.loads(response.content)
                    if not data.get("consistent", True) and data.get("issue"):
                        issues.append(CoherenceIssue(
                            issue_id=str(uuid.uuid4()),
                            issue_type=CoherenceType.DIALOGUE,
                            severity=SeverityLevel.MAJOR,
                            status=IssueStatus.DETECTED,
                            title=f"[AI] Niespójny głos: {char_name}",
                            description=data["issue"],
                            affected_elements=[],
                            chapter_range=(
                                char_dialogues[0].chapter,
                                char_dialogues[-1].chapter
                            ),
                            suggested_fix=f"Ujednolicić głos {char_name} wg profilu",
                            auto_fixable=False,
                            confidence=0.75,
                            detected_at=datetime.now()
                        ))
                except Exception as e:
                    logger.debug(f"AI dialogue check for {char_name} failed: {e}")

        return issues

    async def _check_tone_coherence(
        self,
        elements: Dict[str, NarrativeElement]
    ) -> List[CoherenceIssue]:
        """Check tonal coherence."""
        issues = []

        # Check for jarring tone shifts
        # (simplified - would use sentiment analysis in production)

        return issues

    async def _check_causality_coherence(
        self,
        elements: Dict[str, NarrativeElement],
        relations: Dict[str, ElementRelation]
    ) -> List[CoherenceIssue]:
        """Check cause-effect coherence."""
        issues = []

        # Find causal relations
        causal_relations = [
            r for r in relations.values()
            if r.relation_type == RelationType.CAUSES
        ]

        # Check that causes precede effects
        for relation in causal_relations:
            source = elements.get(relation.source_element)
            target = elements.get(relation.target_element)

            if source and target:
                if source.chapter > target.chapter:
                    issues.append(CoherenceIssue(
                        issue_id=str(uuid.uuid4()),
                        issue_type=CoherenceType.CAUSALITY,
                        severity=SeverityLevel.CRITICAL,
                        status=IssueStatus.DETECTED,
                        title="Naruszenie przyczynowości",
                        description="Skutek występuje przed przyczyną",
                        affected_elements=[source.element_id, target.element_id],
                        chapter_range=(target.chapter, source.chapter),
                        suggested_fix="Zmień kolejność wydarzeń",
                        auto_fixable=False,
                        confidence=0.95,
                        detected_at=datetime.now()
                    ))

        return issues

    async def _cross_reference_all(
        self,
        elements: Dict[str, NarrativeElement],
        relations: Dict[str, ElementRelation],
        rules: Dict[str, WorldRule],
        char_states: Dict[str, List[CharacterState]]
    ) -> List[CoherenceIssue]:
        """Perform quantum-level cross-referencing."""
        issues = []

        # Cross-reference all systems
        # This is the most thorough analysis

        # Check character locations match world geography
        # Check character actions match their abilities
        # Check event consequences ripple properly
        # etc.

        return issues

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _classify_paragraph(self, paragraph: str) -> CoherenceType:
        """Classify a paragraph by its narrative function."""
        lower = paragraph.lower()

        if '"' in paragraph or '—' in paragraph:
            return CoherenceType.DIALOGUE
        elif any(word in lower for word in ['powiedział', 'odparła', 'zapytał']):
            return CoherenceType.DIALOGUE
        elif any(word in lower for word in ['ponieważ', 'dlatego', 'więc', 'skutkiem']):
            return CoherenceType.CAUSALITY
        else:
            return CoherenceType.PLOT

    def _extract_time_reference(self, text: str) -> Optional[str]:
        """Extract time reference from text."""
        time_patterns = [
            'rano', 'wieczorem', 'w nocy', 'o świcie', 'o zmierzchu',
            'następnego dnia', 'tydzień później', 'miesiąc później'
        ]

        for pattern in time_patterns:
            if pattern in text.lower():
                return pattern
        return None

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from text."""
        # Simplified - would use NER in production
        return None

    def _detect_relationship(
        self,
        elem1: NarrativeElement,
        elem2: NarrativeElement
    ) -> Tuple[Optional[RelationType], float]:
        """Detect relationship between two elements."""
        # Check for shared characters
        shared_chars = set(elem1.characters_involved) & set(elem2.characters_involved)

        if shared_chars:
            if elem1.chapter < elem2.chapter:
                return RelationType.FORESHADOWS, 0.5

        # Check for references
        if elem1.location and elem1.location == elem2.location:
            return RelationType.REFERENCES, 0.4

        return None, 0.0

    def _extract_events_from_text(
        self,
        text: str,
        chapter_num: int,
        character_names: List[str]
    ) -> List[TimelineEvent]:
        """Extract timeline events from text."""
        events = []

        # Simplified event extraction
        paragraphs = text.split("\n\n")

        for i, para in enumerate(paragraphs[:5]):  # First 5 paragraphs
            if len(para) > 50:
                chars = [n for n in character_names if n.lower() in para.lower()]

                event = TimelineEvent(
                    event_id=str(uuid.uuid4()),
                    description=para[:200],
                    chapter=chapter_num,
                    story_time=f"Chapter {chapter_num}",
                    duration=None,
                    characters=chars,
                    location=None,
                    dependencies=[]
                )
                events.append(event)

        return events

    def _extract_rules_from_text(
        self,
        text: str,
        chapter_num: int
    ) -> Dict[str, WorldRule]:
        """Extract world rules from text."""
        rules = {}

        # Look for rule-establishing patterns
        rule_patterns = [
            "zawsze", "nigdy", "każdy", "żaden",
            "zasada", "prawo", "tradycja"
        ]

        for pattern in rule_patterns:
            if pattern in text.lower():
                # Extract surrounding context
                # (simplified - would use proper NLP in production)
                pass

        return rules

    def _extract_character_state(
        self,
        name: str,
        text: str,
        chapter_num: int,
        character: Dict[str, Any]
    ) -> Optional[CharacterState]:
        """Extract character state from chapter text."""
        if name.lower() not in text.lower():
            return None

        return CharacterState(
            character_name=name,
            chapter=chapter_num,
            location="unknown",
            emotional_state="neutral",
            knowledge=[],
            relationships={},
            physical_state="normal",
            goals=character.get("goals", [])
        )

    def _find_introduced_elements(
        self,
        elements: List[NarrativeElement]
    ) -> List[NarrativeElement]:
        """Find elements that introduce new plot points.

        Identifies elements that introduce new characters, objects, locations,
        or concepts that could be Chekhov's Guns requiring later resolution.
        """
        introduction_markers = [
            "po raz pierwszy", "nigdy wcześniej", "nowy", "nowa", "nowe",
            "pojawił się", "pojawiła się", "odkrył", "odkryła",
            "znalazł", "znalazła", "tajemniczy", "tajemnicza",
            "nieznany", "nieznana", "dziwny", "dziwna",
            "zaskoczył", "zaskoczyła", "niespodziewanie",
            "zauważył", "zauważyła", "pierwszy raz"
        ]

        introduced = []
        for elem in elements:
            content_lower = elem.content.lower()
            # Check if element introduces something new
            if any(marker in content_lower for marker in introduction_markers):
                introduced.append(elem)

        # Also include elements from early chapters (setup phase) with unique entities
        seen_characters = set()
        for elem in sorted(elements, key=lambda e: e.chapter):
            new_chars = set(elem.characters_involved) - seen_characters
            if new_chars and elem.chapter <= 3:
                if elem not in introduced:
                    introduced.append(elem)
            seen_characters.update(elem.characters_involved)

        return introduced

    def _is_element_resolved(
        self,
        element: NarrativeElement,
        elements: Dict[str, NarrativeElement],
        relations: Dict[str, ElementRelation]
    ) -> bool:
        """Check if a narrative element is resolved later."""
        resolving_relations = [
            r for r in relations.values()
            if r.source_element == element.element_id
            and r.relation_type == RelationType.RESOLVES
        ]
        return len(resolving_relations) > 0

    def _is_knowledge_acquired_logically(
        self,
        character: str,
        knowledge: str,
        start_chapter: int,
        end_chapter: int,
        elements: Dict[str, NarrativeElement]
    ) -> bool:
        """Check if character could have logically acquired knowledge.

        Searches for scenes between start and end chapters where the character
        is present and the knowledge topic is mentioned.
        """
        knowledge_lower = knowledge.lower()

        # Look for elements between the chapters that could explain the knowledge
        for elem in elements.values():
            if start_chapter <= elem.chapter <= end_chapter:
                if character in elem.characters_involved:
                    # Check if element content relates to the knowledge
                    if knowledge_lower in elem.content.lower():
                        return True

                # Check if knowledge was revealed in a scene the character attended
                if any(word in elem.content.lower() for word in knowledge_lower.split()[:3]):
                    if character in elem.characters_involved:
                        return True

        # If no evidence found, flag as potentially impossible
        return False

    def _find_rule_violations(
        self,
        rule: WorldRule,
        elements: Dict[str, NarrativeElement]
    ) -> List[str]:
        """Find elements that violate a world rule."""
        violations = []
        # Simplified - would use semantic matching
        return violations

    def _calculate_coherence_scores(
        self,
        issues: List[CoherenceIssue],
        total_elements: int
    ) -> Dict[str, float]:
        """Calculate coherence scores by type."""
        scores = {}

        for ctype in CoherenceType:
            type_issues = [i for i in issues if i.issue_type == ctype]

            # Weight by severity
            weighted_issues = sum(
                4 if i.severity == SeverityLevel.CRITICAL else
                3 if i.severity == SeverityLevel.MAJOR else
                2 if i.severity == SeverityLevel.MODERATE else
                1 if i.severity == SeverityLevel.MINOR else 0.5
                for i in type_issues
            )

            # Calculate score (1.0 = perfect, 0.0 = terrible)
            max_issues = total_elements * 0.1  # Assume 10% tolerance
            scores[ctype.value] = max(0.0, 1.0 - (weighted_issues / max(max_issues, 1)))

        return scores

    def _calculate_risk_level(
        self,
        issues: List[CoherenceIssue]
    ) -> str:
        """Calculate overall risk level of proposed changes."""
        if any(i.severity == SeverityLevel.CRITICAL for i in issues):
            return "high"
        elif any(i.severity == SeverityLevel.MAJOR for i in issues):
            return "medium"
        elif issues:
            return "low"
        return "none"

    def _generate_change_recommendation(
        self,
        issues: List[CoherenceIssue]
    ) -> str:
        """Generate recommendation for proposed changes."""
        if not issues:
            return "Zmiany są bezpieczne i spójne z resztą historii."

        critical = [i for i in issues if i.severity == SeverityLevel.CRITICAL]
        if critical:
            return f"UWAGA: Zmiany wprowadzą {len(critical)} krytycznych niespójności. Zalecam rewizję."

        major = [i for i in issues if i.severity == SeverityLevel.MAJOR]
        if major:
            return f"Zmiany mogą wprowadzić {len(major)} znaczących niespójności. Rozważ modyfikacje."

        return f"Zmiany wprowadzą {len(issues)} drobnych uwag. Ogólnie bezpieczne."

    async def _check_chapter_internal_coherence(
        self,
        chapter_text: str,
        chapter_number: int
    ) -> List[CoherenceIssue]:
        """Check internal coherence within a single chapter."""
        issues = []

        # Check for internal contradictions
        # Check for scene continuity
        # Check for dialogue attribution

        return issues

    async def _check_context_coherence(
        self,
        chapter_text: str,
        chapter_number: int,
        previous_context: Dict[str, Any]
    ) -> List[CoherenceIssue]:
        """Check coherence with previous story context."""
        issues = []

        # Check character consistency
        # Check plot continuation
        # Check setting consistency

        return issues

    async def _identify_changes(
        self,
        current_text: str,
        proposed_text: str
    ) -> List[Dict[str, Any]]:
        """Identify changes between two text versions."""
        changes = []

        # Simple diff (would use proper diff algorithm in production)
        if current_text != proposed_text:
            changes.append({
                "type": "modification",
                "scope": "full_text"
            })

        return changes

    async def _evaluate_change_impact(
        self,
        change: Dict[str, Any],
        chapter_number: int,
        story_context: Dict[str, Any]
    ) -> List[CoherenceIssue]:
        """Evaluate the impact of a change on story coherence."""
        issues = []
        # Would analyze change impact in production
        return issues

    async def _generate_fix_suggestions(
        self,
        issue: CoherenceIssue
    ) -> List[Dict[str, Any]]:
        """Generate fix suggestions for an issue."""
        suggestions = [
            {
                "approach": "manual",
                "description": issue.suggested_fix,
                "effort": "medium"
            }
        ]

        if issue.auto_fixable:
            suggestions.insert(0, {
                "approach": "automatic",
                "description": "Automatyczna naprawa dostępna",
                "effort": "low"
            })

        return suggestions

    async def _apply_auto_fix(
        self,
        issue: CoherenceIssue,
        chapter_text: str
    ) -> str:
        """Apply automatic fix to chapter text."""
        # Simplified - would apply actual fix in production
        return chapter_text

    # =========================================================================
    # PUBLIC GETTERS
    # =========================================================================

    def get_report(self, report_id: str) -> Optional[CoherenceReport]:
        """Get a coherence report by ID."""
        return self.reports.get(report_id)

    def get_issue(self, issue_id: str) -> Optional[CoherenceIssue]:
        """Get an issue by ID."""
        return self.issues.get(issue_id)

    def list_reports(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all reports, optionally filtered by project."""
        reports = self.reports.values()

        if project_id:
            reports = [r for r in reports if r.project_id == project_id]

        return [
            {
                "report_id": r.report_id,
                "project_id": r.project_id,
                "overall_score": r.overall_score,
                "total_issues": len(r.issues),
                "created_at": r.created_at.isoformat()
            }
            for r in reports
        ]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_coherence_analyzer: Optional[QuantumCoherenceAnalyzer] = None


def get_coherence_analyzer() -> QuantumCoherenceAnalyzer:
    """Get the singleton coherence analyzer instance."""
    global _coherence_analyzer
    if _coherence_analyzer is None:
        _coherence_analyzer = QuantumCoherenceAnalyzer()
    return _coherence_analyzer
