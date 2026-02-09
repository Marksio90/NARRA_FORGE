"""
Context Pack Builder - 3-Layer Memory System

Layer 1: CANON DB (Truth)
    - Atomic facts about world, characters, events
    - Immutable once established
    - Used for continuity checking

Layer 2: RECAP (Summary)
    - 1-2 page summary of "what happened so far"
    - Updated after each chapter
    - Provides narrative context

Layer 3: CONTEXT PACK (Dynamic)
    - Per-chapter context tailored to scenes
    - Only what's needed for current chapter
    - Hard token limit (8-12k tokens)

KEY PRINCIPLE: Don't pump 100k context.
Retrieve only what's needed for current chapter.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# Token limits for context pack
MAX_CONTEXT_TOKENS = 10000  # ~7500 words
MAX_CANON_FACTS = 30
MAX_RECAP_LENGTH = 800  # words
MAX_CHARACTER_CONTEXT = 500  # words per character


@dataclass
class ContextPack:
    """Context pack for chapter generation"""
    canon_facts: List[Dict[str, Any]]  # Relevant facts from Canon DB
    recap: str  # Summary of story so far
    characters: List[Dict[str, Any]]  # Characters in this chapter (trimmed)
    world_context: Dict[str, Any]  # Relevant world info
    plot_context: Dict[str, Any]  # Relevant plot info
    foreshadowing: List[Dict[str, Any]]  # Active foreshadowing
    previous_chapter_summary: str  # Direct previous chapter
    estimated_tokens: int  # Estimated token count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "canon_facts": self.canon_facts,
            "recap": self.recap,
            "characters": self.characters,
            "world_context": self.world_context,
            "plot_context": self.plot_context,
            "foreshadowing": self.foreshadowing,
            "previous_chapter_summary": self.previous_chapter_summary,
            "estimated_tokens": self.estimated_tokens
        }


class ContextPackBuilder:
    """
    Builds optimized context packs for chapter generation

    Instead of loading everything, loads only what's needed:
    1. Characters present in the chapter
    2. Relevant world facts (locations, rules mentioned)
    3. Active plot threads
    4. Foreshadowing setups/payoffs
    5. Previous chapter summary
    """

    def __init__(self):
        self.name = "Context Pack Builder"

    def build_chapter_context(
        self,
        chapter_number: int,
        chapter_outline: Dict[str, Any],
        all_characters: List[Dict[str, Any]],
        world_bible: Dict[str, Any],
        plot_structure: Dict[str, Any],
        canon_facts: List[Dict[str, Any]],
        chapter_summaries: Dict[int, str],  # {chapter_num: summary}
        recap: Optional[str] = None
    ) -> ContextPack:
        """
        Build optimized context pack for a chapter

        Args:
            chapter_number: Current chapter number
            chapter_outline: Outline with scenes, characters, setting
            all_characters: All characters in the book
            world_bible: Full world bible
            plot_structure: Full plot structure
            canon_facts: All established facts
            chapter_summaries: Previous chapter summaries
            recap: Optional overall story recap

        Returns:
            ContextPack with only relevant context
        """
        logger.info(f"📦 Building context pack for Chapter {chapter_number}")

        # 1. Get characters present in this chapter
        characters_present = self._get_chapter_characters(
            chapter_outline,
            all_characters
        )

        # 2. Get relevant world context (setting, rules)
        world_context = self._get_relevant_world(
            chapter_outline,
            world_bible
        )

        # 3. Get relevant plot context (current act, threads)
        plot_context = self._get_relevant_plot(
            chapter_number,
            chapter_outline,
            plot_structure
        )

        # 4. Get active foreshadowing
        foreshadowing = self._get_active_foreshadowing(
            chapter_number,
            plot_structure
        )

        # 5. Filter relevant canon facts
        relevant_facts = self._filter_relevant_facts(
            chapter_outline,
            characters_present,
            canon_facts
        )

        # 6. Get previous chapter summary
        prev_summary = chapter_summaries.get(chapter_number - 1, "")

        # 7. Build or use recap
        if not recap:
            recap = self._build_recap(chapter_summaries, chapter_number)

        # Estimate tokens
        estimated_tokens = self._estimate_tokens(
            relevant_facts,
            recap,
            characters_present,
            world_context,
            plot_context,
            foreshadowing,
            prev_summary
        )

        logger.info(f"📦 Context pack built: ~{estimated_tokens} tokens")

        return ContextPack(
            canon_facts=relevant_facts,
            recap=recap,
            characters=characters_present,
            world_context=world_context,
            plot_context=plot_context,
            foreshadowing=foreshadowing,
            previous_chapter_summary=prev_summary,
            estimated_tokens=estimated_tokens
        )

    def _get_chapter_characters(
        self,
        chapter_outline: Dict[str, Any],
        all_characters: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get characters present in chapter, trimmed to essentials"""
        characters_present_names = chapter_outline.get('characters_present', [])

        # Get full character data for those present
        characters = []
        for char in all_characters:
            if char.get('name') in characters_present_names:
                # Trim to essential fields
                trimmed = self._trim_character(char)
                characters.append(trimmed)

        # Limit to MAX_CHARACTER_CONTEXT per character
        return characters[:8]  # Max 8 characters per chapter

    def _trim_character(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Trim character to essential context"""
        profile = character.get('profile', {})
        psychology = profile.get('psychology', {})
        voice = character.get('voice_guide', {})

        return {
            "name": character.get('name', 'Unknown'),
            "role": character.get('role', 'unknown'),
            # Psychology essentials
            "wound": psychology.get('wound', psychology.get('ghost', '')),
            "want": psychology.get('want', ''),
            "need": psychology.get('need', ''),
            "fear": psychology.get('fears', [''])[0] if psychology.get('fears') else '',
            "lie": psychology.get('lie_believed', ''),
            "traits": psychology.get('traits', [])[:3],
            # Voice essentials
            "speechPatterns": voice.get('speechPatterns', ''),
            "vocabularyLevel": voice.get('vocabularyLevel', ''),
            "verbalTics": voice.get('verbalTics', ''),
            "signaturePhrases": voice.get('signaturePhrases', [])[:2],
            # Relationships (trimmed)
            "relationships": self._trim_relationships(character.get('relationships', {}))
        }

    def _trim_relationships(self, relationships: Dict[str, Any]) -> Dict[str, str]:
        """Trim relationships to just type"""
        if not relationships:
            return {}
        return {
            name: rel.get('type', 'unknown') if isinstance(rel, dict) else str(rel)
            for name, rel in list(relationships.items())[:5]
        }

    def _get_relevant_world(
        self,
        chapter_outline: Dict[str, Any],
        world_bible: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get world context relevant to chapter setting"""
        setting = chapter_outline.get('setting', '')

        # Get matching location from world bible
        geography = world_bible.get('geography', {})
        locations = geography.get('locations', [])

        relevant_location = None
        for loc in locations:
            if loc.get('name', '').lower() in setting.lower():
                relevant_location = loc
                break

        # Get relevant rules/systems
        systems = world_bible.get('systems', {})

        return {
            "world_type": geography.get('world_type', 'standard'),
            "setting": setting,
            "location": relevant_location,
            "technology_level": systems.get('technology_level', ''),
            "magic_system": systems.get('magic_system', {}).get('name', '') if systems.get('magic_system') else '',
            "key_rules": world_bible.get('rules', {}).get('physics', '')
        }

    def _get_relevant_plot(
        self,
        chapter_number: int,
        chapter_outline: Dict[str, Any],
        plot_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get plot context for current chapter"""
        # Determine which act we're in
        acts = plot_structure.get('acts', [])
        current_act = None
        for act in acts:
            # Handle case where act might be a string instead of a dict
            if isinstance(act, str):
                logger.warning(f"Act is a string instead of dict: {act[:100]}")
                continue
            if not isinstance(act, dict):
                logger.warning(f"Act is not a dict: {type(act)}")
                continue
            chapters = act.get('chapters', [])
            if chapter_number in chapters:
                current_act = act
                break

        # Get tension level
        tension_graph = plot_structure.get('tension_graph', [])
        tension = 5  # default
        for idx, point in enumerate(tension_graph):
            # Handle both dict format {"chapter": 1, "tension": 5} and plain int format
            if isinstance(point, dict):
                if point.get('chapter') == chapter_number:
                    tension = point.get('tension', 5)
                    break
            elif isinstance(point, (int, float)):
                # If it's a list of ints, treat index+1 as chapter and value as tension
                if idx + 1 == chapter_number:
                    tension = int(point)
                    break

        # Get main conflict - handle both dict and string formats
        main_conflict = plot_structure.get('main_conflict', {})
        if isinstance(main_conflict, str):
            central_conflict = main_conflict
        elif isinstance(main_conflict, dict):
            central_conflict = main_conflict.get('central_conflict', '')
        else:
            central_conflict = ''

        return {
            "act": current_act.get('name', 'Unknown') if current_act else 'Unknown',
            "act_goal": current_act.get('goal', '') if current_act else '',
            "tension_level": tension,
            "chapter_goal": chapter_outline.get('goal', ''),
            "emotional_beat": chapter_outline.get('emotional_beat', ''),
            "central_conflict": central_conflict
        }

    def _get_active_foreshadowing(
        self,
        chapter_number: int,
        plot_structure: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get foreshadowing to plant or pay off"""
        foreshadowing = plot_structure.get('foreshadowing', [])

        active = []
        for f in foreshadowing:
            # Handle case where foreshadowing item might not be a dict
            if not isinstance(f, dict):
                logger.warning(f"Foreshadowing item is not a dict: {type(f)}")
                continue
            setup_ch = f.get('setup_chapter', 0)
            payoff_ch = f.get('payoff_chapter', 0)

            if setup_ch == chapter_number:
                active.append({
                    "type": "plant",
                    "description": f.get('setup_description', ''),
                    "payoff_chapter": payoff_ch
                })
            elif payoff_ch == chapter_number:
                active.append({
                    "type": "payoff",
                    "description": f.get('payoff_description', ''),
                    "setup_chapter": setup_ch
                })

        return active

    def _filter_relevant_facts(
        self,
        chapter_outline: Dict[str, Any],
        characters: List[Dict[str, Any]],
        canon_facts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter canon facts relevant to this chapter"""
        if not canon_facts:
            return []

        # Keywords to match
        keywords = set()

        # Add character names
        for char in characters:
            keywords.add(char.get('name', '').lower())

        # Add setting
        setting = chapter_outline.get('setting', '').lower()
        keywords.update(setting.split())

        # Filter facts
        relevant = []
        for fact in canon_facts:
            fact_text = fact.get('fact', '').lower()
            related = fact.get('related_entity', '').lower()

            if any(kw in fact_text or kw in related for kw in keywords if len(kw) > 2):
                relevant.append({
                    "fact": fact.get('fact', ''),
                    "type": fact.get('fact_type', ''),
                    "entity": fact.get('related_entity', '')
                })

            if len(relevant) >= MAX_CANON_FACTS:
                break

        return relevant

    def _build_recap(
        self,
        chapter_summaries: Dict[int, str],
        current_chapter: int
    ) -> str:
        """Build a recap from previous chapter summaries"""
        if not chapter_summaries:
            return "To jest pierwszy rozdział."

        # Get last 5 chapter summaries
        recap_parts = []
        for ch_num in range(max(1, current_chapter - 5), current_chapter):
            if ch_num in chapter_summaries:
                recap_parts.append(f"R{ch_num}: {chapter_summaries[ch_num]}")

        recap = "\n".join(recap_parts)

        # Trim if too long
        words = recap.split()
        if len(words) > MAX_RECAP_LENGTH:
            recap = " ".join(words[:MAX_RECAP_LENGTH]) + "..."

        return recap

    def _estimate_tokens(
        self,
        facts: List[Dict[str, Any]],
        recap: str,
        characters: List[Dict[str, Any]],
        world: Dict[str, Any],
        plot: Dict[str, Any],
        foreshadowing: List[Dict[str, Any]],
        prev_summary: str
    ) -> int:
        """Estimate token count for context pack using tiktoken when available."""
        # Concatenate all text for accurate counting
        parts = [
            str(facts) if facts else "",
            recap or "",
            str(characters) if characters else "",
            str(world) if world else "",
            str(plot) if plot else "",
            str(foreshadowing) if foreshadowing else "",
            prev_summary or "",
        ]
        full_text = " ".join(parts)

        try:
            import tiktoken
            enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(full_text))
        except (ImportError, Exception):
            # Fallback: Polish text ≈ 3 chars/token
            return len(full_text) // 3

    def format_for_prompt(self, context_pack: ContextPack) -> str:
        """Format context pack for inclusion in prompt"""
        sections = []

        # Previous chapter
        if context_pack.previous_chapter_summary:
            sections.append(f"## POPRZEDNI ROZDZIAŁ\n{context_pack.previous_chapter_summary}")

        # Characters present
        if context_pack.characters:
            chars = []
            for c in context_pack.characters:
                char_str = f"**{c['name']}** ({c['role']})"
                if c.get('wound'):
                    char_str += f" | Rana: {c['wound']}"
                if c.get('speechPatterns'):
                    char_str += f" | Mowa: {c['speechPatterns']}"
                chars.append(char_str)
            sections.append("## POSTACIE W ROZDZIALE\n" + "\n".join(chars))

        # Plot context
        if context_pack.plot_context:
            pc = context_pack.plot_context
            sections.append(
                f"## KONTEKST FABULARNY\n"
                f"Akt: {pc.get('act', '?')} | Napięcie: {pc.get('tension_level', 5)}/10\n"
                f"Cel: {pc.get('chapter_goal', '')}\n"
                f"Emocja: {pc.get('emotional_beat', '')}"
            )

        # Foreshadowing
        if context_pack.foreshadowing:
            fore = []
            for f in context_pack.foreshadowing:
                if f['type'] == 'plant':
                    fore.append(f"🌱 ZASIEJ: {f['description']}")
                else:
                    fore.append(f"💥 PAYOFF: {f['description']}")
            sections.append("## FORESHADOWING\n" + "\n".join(fore))

        # Canon facts (only most important)
        if context_pack.canon_facts:
            facts = [f"• {f['fact']}" for f in context_pack.canon_facts[:10]]
            sections.append("## FAKTY KANONICZNE\n" + "\n".join(facts))

        return "\n\n".join(sections)


def get_context_pack_builder() -> ContextPackBuilder:
    """Get Context Pack Builder instance"""
    return ContextPackBuilder()
