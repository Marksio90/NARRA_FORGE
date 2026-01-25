"""
Scene Writer Agent - Advanced scene-by-scene chapter generation with Beat Sheet Architecture

ARCHITEKTURA TRZECH MODUŁÓW (Divine Prompt System):
1. ARCHITEKT - planuje strukturę sceny (Beat Sheet) przed pisaniem
2. WIRTUOZ PIÓRA - generuje prozę na podstawie Beat Sheet
3. REDAKTOR - weryfikuje i naprawia (opcjonalnie)

ROZWIĄZANE PROBLEMY:
- Pętle narracyjne ("Wieczne Otwarcie") - Beat Sheet wymusza postęp
- Halucynacje postaci - Character Lock blokuje nieautoryzowane postacie
- Purple Prose - Burstiness/Perplexity controls
- Brak spójności - Chain of Thought planning

Bazuje na analizie "Algorytmiczna Architektura Narracji".
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from app.services.ai_service import get_ai_service, ModelTier
from app.models.chapter import ChapterStatus
from app.agents.beat_sheet_architect import (
    BeatSheetArchitect,
    BeatSheet,
    get_beat_sheet_architect
)
from app.prompts.divine_prompts import (
    get_writer_system_prompt,
    get_writer_prompt,
    get_editor_prompt,
    EDITOR_SYSTEM_PROMPT
)
from app.prompts.narrative_anti_patterns import (
    NarrativeAntiPatternValidator,
    get_full_anti_pattern_prompt,
    FORBIDDEN_TROPES
)

logger = logging.getLogger(__name__)


@dataclass
class SceneResult:
    """Result of scene generation"""
    scene_number: int
    content: str
    word_count: int
    cost: float
    model_used: str


@dataclass
class ChapterResult:
    """Result of chapter generation"""
    chapter_number: int
    scenes: List[SceneResult]
    full_content: str
    total_word_count: int
    status: ChapterStatus
    qa_scores: Dict[str, float]
    total_cost: float
    repair_count: int


class SceneWriterAgent:
    """
    Advanced Scene Writer with Beat Sheet Architecture

    Architektura trzech modułów:
    1. ARCHITEKT - planuje Beat Sheet (Chain of Thought)
    2. WIRTUOZ - generuje prozę realizującą Beat Sheet
    3. WALIDATOR - sprawdza anty-wzorce (post-generation)

    Rozwiązuje problemy:
    - Pętle narracyjne przez wymuszony postęp w Beat Sheet
    - Halucynacje postaci przez Character Lock
    - Purple Prose przez Burstiness/Perplexity controls
    """

    def __init__(self, use_beat_sheet: bool = True, validate_output: bool = True):
        """
        Args:
            use_beat_sheet: Czy używać Beat Sheet Architect (Chain of Thought)
            validate_output: Czy walidować wygenerowany tekst
        """
        self.ai_service = get_ai_service()
        self.name = "Scene Writer Agent (Divine)"
        self.use_beat_sheet = use_beat_sheet
        self.validate_output = validate_output

        # Komponenty Divine Prompt System
        self.beat_sheet_architect = get_beat_sheet_architect() if use_beat_sheet else None
        self.anti_pattern_validator = NarrativeAntiPatternValidator() if validate_output else None

        # Default forbidden tropes
        self.default_forbidden_tropes = [
            "spotkanie tajemniczego nieznajomego",
            "wewnętrzny monolog o ucieczce",
            "sen/wizja jako źródło informacji",
            "powrót do punktu wyjścia"
        ]

    async def write_chapter(
        self,
        chapter_number: int,
        chapter_outline: Dict[str, Any],
        genre: str,
        pov_character: Dict[str, Any],
        context_pack: Any,  # ContextPack - but we just use it for formatting
        target_word_count: int,
        book_title: str,
        tier: ModelTier = ModelTier.TIER_2,  # Default to GPT-4o for quality
        on_scene_complete: Optional[callable] = None,
        all_characters: Optional[List[Dict[str, Any]]] = None,
        world_bible: Optional[Dict[str, Any]] = None
    ) -> ChapterResult:
        """
        Generuj rozdział z architekturą Beat Sheet (Chain of Thought).

        Flow:
        1. Dla każdej sceny: ARCHITEKT tworzy Beat Sheet
        2. WIRTUOZ PIÓRA generuje prozę realizującą Beat Sheet
        3. WALIDATOR sprawdza anty-wzorce (opcjonalnie)
        """
        logger.info(f"✍️ {self.name}: Generating Chapter {chapter_number} (~{target_word_count} words)")
        if self.use_beat_sheet:
            logger.info("📐 Using Beat Sheet Architecture (Chain of Thought)")

        # Plan scenes - 5 scen na rozdział
        num_scenes = 5
        words_per_scene = target_word_count // num_scenes

        scene_results: List[SceneResult] = []
        total_cost = 0.0
        validation_scores = []

        # Extract context for prompt
        context_text = self._format_context(context_pack, pov_character)

        # Prepare active characters list
        active_characters = self._prepare_active_characters(
            pov_character, all_characters, chapter_outline
        )

        # Get current location from context
        current_location = self._get_current_location(context_pack, chapter_outline)

        # Previous scene content and summary for continuity
        previous_content = ""
        previous_scene_summary = ""

        for scene_num in range(1, num_scenes + 1):
            logger.info(f"🎬 Processing scene {scene_num}/{num_scenes}...")

            # KROK 1: ARCHITEKT - stwórz Beat Sheet (jeśli włączony)
            beat_sheet = None
            beat_sheet_text = ""
            architect_cost = 0.0

            if self.use_beat_sheet and self.beat_sheet_architect:
                logger.info(f"📐 Creating Beat Sheet for scene {scene_num}...")
                beat_sheet = await self.beat_sheet_architect.create_beat_sheet(
                    scene_number=scene_num,
                    total_scenes=num_scenes,
                    chapter_number=chapter_number,
                    chapter_outline=chapter_outline,
                    pov_character=pov_character,
                    active_characters=active_characters,
                    previous_scene_summary=previous_scene_summary,
                    current_location=current_location,
                    scene_goal=chapter_outline.get('goal', 'Rozwinąć fabułę'),
                    forbidden_tropes=self.default_forbidden_tropes,
                    tier=ModelTier.TIER_1  # Beat Sheet can use cheaper model
                )
                beat_sheet_text = self.beat_sheet_architect.format_beat_sheet_for_writer(beat_sheet)
                logger.info(f"✅ Beat Sheet created: {beat_sheet.total_beats} beats")

            # KROK 2: WIRTUOZ PIÓRA - generuj scenę
            scene_result = await self._generate_scene_with_divine_prompt(
                chapter_number=chapter_number,
                scene_number=scene_num,
                total_scenes=num_scenes,
                genre=genre,
                pov_character=pov_character,
                book_title=book_title,
                target_words=words_per_scene,
                context_text=context_text,
                previous_content=previous_content,
                chapter_outline=chapter_outline,
                beat_sheet_text=beat_sheet_text,
                active_characters=active_characters,
                tier=tier
            )

            # KROK 3: WALIDATOR - sprawdź anty-wzorce (jeśli włączony)
            if self.validate_output and self.anti_pattern_validator:
                validation = self.anti_pattern_validator.validate(scene_result.content)
                validation_scores.append(validation['score'])
                if not validation['passed']:
                    logger.warning(
                        f"⚠️ Scene {scene_num} validation: {validation['score']}/100, "
                        f"{validation['critical_count']} critical, {validation['warning_count']} warnings"
                    )
                else:
                    logger.info(f"✅ Scene {scene_num} validated: {validation['score']}/100")

            scene_results.append(scene_result)
            total_cost += scene_result.cost + architect_cost
            previous_content = scene_result.content[-500:]  # Last 500 chars for continuity
            previous_scene_summary = self._summarize_scene(scene_result.content)

            # Update location if beat_sheet indicates change
            if beat_sheet and beat_sheet.beats:
                for beat in beat_sheet.beats:
                    if beat.change_type == "location":
                        current_location = beat.change_description

            logger.info(f"✅ Scene {scene_num}: {scene_result.word_count} words, ${scene_result.cost:.4f}")

            # Progress callback
            if on_scene_complete:
                try:
                    await on_scene_complete(scene_num, num_scenes, scene_result)
                except:
                    pass  # Don't let callback errors break generation

        # Assemble full chapter
        full_content = self._assemble_chapter(chapter_number, scene_results)
        total_words = sum(s.word_count for s in scene_results)

        # Calculate average validation score
        avg_validation = sum(validation_scores) / len(validation_scores) if validation_scores else 85.0

        logger.info(f"✅ Chapter {chapter_number} COMPLETE: {total_words} words, ${total_cost:.4f}")
        if validation_scores:
            logger.info(f"📊 Average validation score: {avg_validation:.1f}/100")

        return ChapterResult(
            chapter_number=chapter_number,
            scenes=scene_results,
            full_content=full_content,
            total_word_count=total_words,
            status=ChapterStatus.DRAFTED,
            qa_scores={
                "total": avg_validation,
                "anti_pattern_validation": avg_validation,
                "beat_sheet_used": self.use_beat_sheet
            },
            total_cost=total_cost,
            repair_count=0
        )

    def _prepare_active_characters(
        self,
        pov_character: Dict[str, Any],
        all_characters: Optional[List[Dict[str, Any]]],
        chapter_outline: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Przygotowuje listę aktywnych postaci dla sceny"""
        active = [pov_character]

        # Get characters mentioned in chapter outline
        if all_characters and chapter_outline:
            outline_text = str(chapter_outline).lower()
            for char in all_characters:
                char_name = char.get('name', '').lower()
                if char_name and char_name in outline_text:
                    if char not in active:
                        active.append(char)

        # Limit to 5 characters max
        return active[:5]

    def _get_current_location(
        self,
        context_pack: Any,
        chapter_outline: Dict[str, Any]
    ) -> str:
        """Pobiera aktualną lokalizację z kontekstu"""
        if hasattr(context_pack, 'world_context') and context_pack.world_context:
            return context_pack.world_context.get('current_location', 'Nieznana lokalizacja')
        if chapter_outline:
            return chapter_outline.get('setting', 'Nieznana lokalizacja')
        return "Nieznana lokalizacja"

    def _summarize_scene(self, content: str) -> str:
        """Tworzy krótkie streszczenie sceny dla kontekstu następnej"""
        # Simple extraction - last 200 words
        words = content.split()
        if len(words) > 200:
            return " ".join(words[-200:])
        return content

    async def _generate_scene_with_divine_prompt(
        self,
        chapter_number: int,
        scene_number: int,
        total_scenes: int,
        genre: str,
        pov_character: Dict[str, Any],
        book_title: str,
        target_words: int,
        context_text: str,
        previous_content: str,
        chapter_outline: Dict[str, Any],
        beat_sheet_text: str,
        active_characters: List[Dict[str, Any]],
        tier: ModelTier
    ) -> SceneResult:
        """Generuje scenę używając Divine Prompt System"""

        # Get character details
        char_name = pov_character.get('name', 'protagonist')
        char_wound = pov_character.get('wound', pov_character.get('ghost_wound', {}).get('wound', ''))
        char_voice = pov_character.get('speechPatterns', pov_character.get('voice_guide', {}).get('speechPatterns', ''))

        # Get active character names for Character Lock
        char_names = [c.get('name', 'Unknown') for c in active_characters]

        # Build Divine Prompt
        system_prompt = get_writer_system_prompt(genre)

        # If no beat sheet, create a simple structure
        if not beat_sheet_text:
            beat_sheet_text = self._create_simple_beat_sheet(scene_number, total_scenes, chapter_outline)

        prompt = get_writer_prompt(
            scene_number=scene_number,
            total_scenes=total_scenes,
            chapter_number=chapter_number,
            book_title=book_title,
            genre=genre,
            pov_character=char_name,
            pov_wound=char_wound,
            pov_voice=char_voice,
            beat_sheet=beat_sheet_text,
            context_text=context_text,
            previous_content=previous_content,
            target_words=target_words,
            active_characters=char_names
        )

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                tier=tier,
                temperature=0.85,
                max_tokens=target_words * 2,  # Double for safety
                json_mode=False,
                prefer_anthropic=False,
                metadata={
                    "agent": self.name,
                    "task": "scene_generation_divine",
                    "chapter": chapter_number,
                    "scene": scene_number,
                    "beat_sheet_used": bool(beat_sheet_text)
                }
            )

            content = response.content.strip()
            word_count = len(content.split())

            return SceneResult(
                scene_number=scene_number,
                content=content,
                word_count=word_count,
                cost=response.cost,
                model_used=response.model
            )

        except Exception as e:
            logger.error(f"❌ Scene {scene_number} generation FAILED: {e}", exc_info=True)
            raise RuntimeError(f"Scene {scene_number} generation failed: {e}")

    def _create_simple_beat_sheet(
        self,
        scene_number: int,
        total_scenes: int,
        chapter_outline: Dict[str, Any]
    ) -> str:
        """Tworzy prosty Beat Sheet gdy Architekt nie jest używany"""
        scene_goal = chapter_outline.get('goal', 'Rozwinąć fabułę')

        if scene_number == 1:
            scene_type = "OTWARCIE - mocny hook, wprowadzenie konfliktu"
        elif scene_number == total_scenes:
            scene_type = "FINAŁ - kulminacja, cliffhanger na koniec rozdziału"
        elif scene_number == total_scenes // 2:
            scene_type = "PUNKT ZWROTNY - zmiana kierunku, rewelacja"
        else:
            scene_type = "ROZWÓJ - pogłębienie konfliktu, napięcie rośnie"

        return f"""## STRUKTURA SCENY (bez pełnego Beat Sheet)

**Typ**: {scene_type}
**Cel**: {scene_goal}

### Wymagania minimalne:
1. Mocne otwarcie (akcja/dialog, NIE opis pogody)
2. Eskalacja napięcia
3. Punkt zwrotny lub odkrycie
4. Zmiana stanu (lokalizacja/wiedza/relacja/decyzja)
5. Hak na następną scenę

### WYMÓG: Scena MUSI kończyć się ZMIANĄ - nie może wrócić do punktu wyjścia!
"""

    async def _generate_scene(
        self,
        chapter_number: int,
        scene_number: int,
        total_scenes: int,
        genre: str,
        pov_character: Dict[str, Any],
        book_title: str,
        target_words: int,
        context_text: str,
        previous_content: str,
        chapter_outline: Dict[str, Any],
        tier: ModelTier
    ) -> SceneResult:
        """Generate a single scene - SIMPLE and RELIABLE"""

        # Determine scene type based on position
        if scene_number == 1:
            scene_type = "OTWARCIE - mocny hook, wprowadzenie konfliktu"
        elif scene_number == total_scenes:
            scene_type = "FINAŁ - kulminacja, cliffhanger na koniec rozdziału"
        elif scene_number == total_scenes // 2:
            scene_type = "PUNKT ZWROTNY - zmiana kierunku, rewelacja"
        else:
            scene_type = "ROZWÓJ - pogłębienie konfliktu, napięcie rośnie"

        # Get character info
        char_name = pov_character.get('name', 'protagonist')
        char_wound = pov_character.get('wound', '')
        char_voice = pov_character.get('speechPatterns', '')

        prompt = f"""# SCENA {scene_number}/{total_scenes} - Rozdział {chapter_number}

## KSIĄŻKA: "{book_title}" ({genre})

## TYP SCENY: {scene_type}

## POV: {char_name}
Rana wewnętrzna: {char_wound}
Sposób mówienia: {char_voice}

## CEL SCENY
{chapter_outline.get('goal', 'Rozwinąć fabułę i pogłębić postacie')}

## KONTEKST
{context_text}

{f"## POPRZEDNIA SCENA (kontynuuj)" if previous_content else ""}
{previous_content if previous_content else ""}

## WYMAGANIA TECHNICZNE
• **MINIMUM {target_words} słów** - to absolutny wymóg!
• Dialogi z PAUZĄ (—), nigdy cudzysłowami
• 100% po polsku
• Deep POV przez {char_name}
• Min. 3 zmysły (zapach, dźwięk, dotyk)
• Mikro-napięcie w każdym akapicie
• Dialog = 3 warstwy (słowa / intencja / ciało)

## STRUKTURA SCENY
1. Mocne otwarcie (akcja/dialog/obraz - NIE opis pogody!)
2. Rozwój z napięciem w każdym akapicie
3. Punkt kulminacyjny sceny
4. Hak na następną scenę

Napisz scenę. MINIMUM {target_words} słów. Zacznij od akcji lub dialogu."""

        system_prompt = f"""Jesteś mistrzem prozy {genre} na poziomie Sapkowskiego, Kinga, Sandersona.

TWOJE ZASADY:
• ZAWSZE piszesz PEŁNE sceny - nigdy nie skracasz
• Deep POV przez {char_name} - świat widziany JEGO oczami
• Rana postaci KOLORUJE percepcję
• Ciało = emocje (zaciśnięte pięści, suche gardło, zimny pot)
• Dialogi z PODTEKSTEM - co NIE jest powiedziane
• Każdy akapit ma mikro-napięcie
• Zmysły budują atmosferę (szczególnie ZAPACH = pamięć)

FORMAT:
• Dialogi z pauzą (—), nigdy cudzysłowy
• 100% po polsku
• Naturalny, płynny język"""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                tier=tier,
                temperature=0.85,
                max_tokens=target_words * 2,  # Double for safety
                json_mode=False,
                prefer_anthropic=False,
                metadata={
                    "agent": self.name,
                    "task": "scene_generation",
                    "chapter": chapter_number,
                    "scene": scene_number
                }
            )

            content = response.content.strip()
            word_count = len(content.split())

            return SceneResult(
                scene_number=scene_number,
                content=content,
                word_count=word_count,
                cost=response.cost,
                model_used=response.model
            )

        except Exception as e:
            logger.error(f"❌ Scene {scene_number} generation FAILED: {e}", exc_info=True)
            # NIGDY nie zwracaj pustego contentu - rzuć wyjątek!
            raise RuntimeError(f"Scene {scene_number} generation failed: {e}")

    def _format_context(self, context_pack: Any, pov_character: Dict[str, Any]) -> str:
        """Format context for prompt"""
        if context_pack is None:
            return f"POV: {pov_character.get('name', 'protagonist')}"

        try:
            # Try to use context_pack's format method if available
            if hasattr(context_pack, 'previous_chapter_summary'):
                parts = []
                if context_pack.previous_chapter_summary:
                    parts.append(f"Poprzednio: {context_pack.previous_chapter_summary[:300]}")
                if hasattr(context_pack, 'plot_context') and context_pack.plot_context:
                    pc = context_pack.plot_context
                    parts.append(f"Napięcie: {pc.get('tension_level', 5)}/10")
                return "\n".join(parts) if parts else ""
            else:
                return str(context_pack)[:500]
        except:
            return ""

    def _assemble_chapter(self, chapter_number: int, scenes: List[SceneResult]) -> str:
        """Assemble full chapter from scenes"""
        parts = [f"Rozdział {chapter_number}\n"]

        for scene in scenes:
            parts.append(scene.content)
            parts.append("")  # Empty line between scenes

        return "\n\n".join(parts)


def get_scene_writer(
    use_beat_sheet: bool = True,
    validate_output: bool = True
) -> SceneWriterAgent:
    """
    Get Scene Writer instance with Divine Prompt System.

    Args:
        use_beat_sheet: Enable Beat Sheet Architect (Chain of Thought planning)
        validate_output: Enable anti-pattern validation post-generation

    Returns:
        SceneWriterAgent configured with specified options
    """
    return SceneWriterAgent(
        use_beat_sheet=use_beat_sheet,
        validate_output=validate_output
    )


def get_simple_scene_writer() -> SceneWriterAgent:
    """
    Get simplified Scene Writer without Beat Sheet architecture.
    Faster but less sophisticated narrative control.
    """
    return SceneWriterAgent(use_beat_sheet=False, validate_output=False)


__all__ = [
    'SceneResult',
    'ChapterResult',
    'SceneWriterAgent',
    'get_scene_writer',
    'get_simple_scene_writer',
]
