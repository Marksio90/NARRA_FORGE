"""
Advanced Dialogue System with Subtext - NarraForge 3.0

Sophisticated dialogue generation system that creates multi-layered conversations
with realistic subtext, power dynamics, emotional undercurrents, and character
voice consistency.

Features:
1. Subtext Analysis - What characters mean vs what they say
2. Power Dynamics - Who has the upper hand and how it shifts
3. Emotional Undercurrents - Hidden emotions beneath dialogue
4. Character Voice Consistency - Unique speech patterns per character
5. Dialogue Beats - Pacing and rhythm of conversation
6. Interruption Patterns - Natural conversational flow
7. Silence as Dialogue - Meaningful pauses and non-responses
8. Context Sensitivity - Dialogue adapts to situation and relationship
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

from app.services.ai_service import AIService
from app.models.project import GenreType

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS AND TYPES
# =============================================================================

class SubtextType(str, Enum):
    """Types of subtext in dialogue"""
    HIDDEN_AGENDA = "hidden_agenda"           # Character has secret goal
    SUPPRESSED_EMOTION = "suppressed_emotion" # Hiding true feelings
    POWER_PLAY = "power_play"                 # Establishing dominance
    DEFLECTION = "deflection"                 # Avoiding real topic
    MANIPULATION = "manipulation"             # Influencing through words
    INTIMACY_SEEKING = "intimacy_seeking"     # Creating connection
    INTIMACY_AVOIDING = "intimacy_avoiding"   # Creating distance
    TESTING = "testing"                       # Probing the other person
    PERFORMANCE = "performance"               # Playing a role
    REVELATION = "revelation"                 # Revealing something slowly


class PowerDynamic(str, Enum):
    """Power dynamics between characters"""
    DOMINANT = "dominant"
    SUBMISSIVE = "submissive"
    EQUAL = "equal"
    SHIFTING = "shifting"
    CONTESTED = "contested"


class EmotionalUndercurrent(str, Enum):
    """Hidden emotional currents in dialogue"""
    DESIRE = "desire"
    RESENTMENT = "resentment"
    FEAR = "fear"
    GUILT = "guilt"
    LONGING = "longing"
    SUSPICION = "suspicion"
    HOPE = "hope"
    DESPERATION = "desperation"
    CONTEMPT = "contempt"
    AFFECTION = "affection"


class DialogueBeatType(str, Enum):
    """Types of dialogue beats"""
    STATEMENT = "statement"
    QUESTION = "question"
    RESPONSE = "response"
    DEFLECTION = "deflection"
    INTERRUPTION = "interruption"
    SILENCE = "silence"
    ACTION_BEAT = "action_beat"
    INTERNAL_THOUGHT = "internal_thought"
    REVELATION = "revelation"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class CharacterVoice:
    """Voice profile for a character's dialogue"""
    character_name: str
    vocabulary_level: str  # simple, moderate, sophisticated, archaic
    sentence_structure: str  # short, varied, complex, fragmented
    verbal_tics: List[str] = field(default_factory=list)  # "um", "actually", "you know"
    favorite_phrases: List[str] = field(default_factory=list)
    forbidden_words: List[str] = field(default_factory=list)  # Words they'd never say
    speech_rhythm: str = "normal"  # fast, slow, deliberate, nervous
    formality_default: str = "casual"  # formal, casual, street, archaic
    emotional_expression: str = "moderate"  # reserved, moderate, expressive, volatile
    interruption_tendency: float = 0.3  # 0-1 how likely to interrupt
    silence_comfort: float = 0.5  # 0-1 comfort with silence
    deflection_patterns: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "character_name": self.character_name,
            "vocabulary_level": self.vocabulary_level,
            "sentence_structure": self.sentence_structure,
            "verbal_tics": self.verbal_tics,
            "favorite_phrases": self.favorite_phrases,
            "forbidden_words": self.forbidden_words,
            "speech_rhythm": self.speech_rhythm,
            "formality_default": self.formality_default,
            "emotional_expression": self.emotional_expression,
            "interruption_tendency": self.interruption_tendency,
            "silence_comfort": self.silence_comfort,
            "deflection_patterns": self.deflection_patterns
        }


@dataclass
class SubtextLayer:
    """A layer of subtext in a dialogue line"""
    surface_meaning: str  # What is literally said
    true_meaning: str  # What is really meant
    subtext_type: SubtextType
    character_aware: bool = True  # Is the character aware of their subtext?
    reader_should_know: bool = True  # Should reader understand the subtext?
    intensity: float = 0.5  # 0-1 how strong the subtext is

    def to_dict(self) -> Dict:
        return {
            "surface_meaning": self.surface_meaning,
            "true_meaning": self.true_meaning,
            "subtext_type": self.subtext_type.value,
            "character_aware": self.character_aware,
            "reader_should_know": self.reader_should_know,
            "intensity": self.intensity
        }


@dataclass
class DialogueBeat:
    """A single beat in a dialogue exchange"""
    speaker: str
    beat_type: DialogueBeatType
    spoken_text: Optional[str] = None
    action_text: Optional[str] = None
    internal_thought: Optional[str] = None
    subtext: Optional[SubtextLayer] = None
    emotional_state: str = "neutral"
    power_position: str = "equal"
    pacing: str = "normal"  # slow, normal, fast, rushed

    def to_dict(self) -> Dict:
        return {
            "speaker": self.speaker,
            "beat_type": self.beat_type.value,
            "spoken_text": self.spoken_text,
            "action_text": self.action_text,
            "internal_thought": self.internal_thought,
            "subtext": self.subtext.to_dict() if self.subtext else None,
            "emotional_state": self.emotional_state,
            "power_position": self.power_position,
            "pacing": self.pacing
        }


@dataclass
class DialogueExchange:
    """A complete dialogue exchange between characters"""
    participants: List[str]
    beats: List[DialogueBeat]
    overall_power_dynamic: PowerDynamic
    emotional_undercurrent: EmotionalUndercurrent
    relationship_change: str  # How relationship changes through dialogue
    tension_arc: List[float]  # Tension level at each beat
    subtext_density: float  # 0-1 how much subtext overall
    formatted_dialogue: str  # The actual prose

    def to_dict(self) -> Dict:
        return {
            "participants": self.participants,
            "beats": [b.to_dict() for b in self.beats],
            "overall_power_dynamic": self.overall_power_dynamic.value,
            "emotional_undercurrent": self.emotional_undercurrent.value,
            "relationship_change": self.relationship_change,
            "tension_arc": self.tension_arc,
            "subtext_density": self.subtext_density,
            "formatted_dialogue": self.formatted_dialogue
        }


@dataclass
class DialogueContext:
    """Context for generating dialogue"""
    scene_setting: str
    relationship_type: str  # strangers, friends, lovers, enemies, family
    relationship_history: str
    what_each_wants: Dict[str, str]  # character -> their goal
    what_each_knows: Dict[str, List[str]]  # character -> facts they know
    what_each_hides: Dict[str, List[str]]  # character -> secrets they hide
    power_balance: Dict[str, float]  # character -> power level (0-1)
    emotional_states: Dict[str, str]  # character -> current emotion
    stakes: str  # What's at stake in this conversation
    genre: GenreType = GenreType.DRAMA
    pov_character: Optional[str] = None


# =============================================================================
# CHARACTER VOICE PROFILES
# =============================================================================

def create_voice_profile(
    name: str,
    education: str = "average",
    personality: str = "balanced",
    background: str = "general",
    age_group: str = "adult"
) -> CharacterVoice:
    """Create a voice profile based on character attributes"""

    # Vocabulary based on education
    vocab_map = {
        "uneducated": "simple",
        "average": "moderate",
        "educated": "sophisticated",
        "scholarly": "sophisticated",
        "street": "simple"
    }

    # Sentence structure based on personality
    structure_map = {
        "anxious": "fragmented",
        "confident": "varied",
        "intellectual": "complex",
        "simple": "short",
        "dramatic": "varied",
        "balanced": "varied"
    }

    # Verbal tics based on personality
    tics_map = {
        "anxious": ["um", "uh", "I mean", "I don't know"],
        "confident": [],
        "intellectual": ["actually", "technically", "in fact"],
        "simple": [],
        "dramatic": ["honestly", "truly", "absolutely"],
        "balanced": ["well", "you know"]
    }

    # Formality based on background
    formality_map = {
        "noble": "formal",
        "academic": "formal",
        "military": "formal",
        "street": "street",
        "rural": "casual",
        "general": "casual"
    }

    return CharacterVoice(
        character_name=name,
        vocabulary_level=vocab_map.get(education, "moderate"),
        sentence_structure=structure_map.get(personality, "varied"),
        verbal_tics=tics_map.get(personality, []),
        favorite_phrases=[],
        forbidden_words=[],
        speech_rhythm="nervous" if personality == "anxious" else "normal",
        formality_default=formality_map.get(background, "casual"),
        emotional_expression="volatile" if personality == "dramatic" else "moderate",
        interruption_tendency=0.6 if personality in ["anxious", "confident"] else 0.3,
        silence_comfort=0.3 if personality == "anxious" else 0.5
    )


# =============================================================================
# ADVANCED DIALOGUE SYSTEM
# =============================================================================

class AdvancedDialogueSystem:
    """
    Advanced dialogue generation with subtext, power dynamics,
    and character voice consistency.
    """

    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service or AIService()
        self.voice_profiles: Dict[str, CharacterVoice] = {}

    # =========================================================================
    # VOICE PROFILE MANAGEMENT
    # =========================================================================

    def register_voice(self, profile: CharacterVoice):
        """Register a character's voice profile"""
        self.voice_profiles[profile.character_name] = profile
        logger.debug(f"Registered voice profile for {profile.character_name}")

    async def generate_voice_profile(
        self,
        character_name: str,
        character_data: Dict
    ) -> CharacterVoice:
        """Generate a voice profile from character data using AI"""
        prompt = f"""Przeanalizuj tę postać i stwórz jej unikalny profil głosowy dla dialogów:

POSTAĆ: {character_name}
DANE: {json.dumps(character_data, ensure_ascii=False, indent=2)[:2000]}

Stwórz profil głosowy określający:
1. vocabulary_level: simple/moderate/sophisticated/archaic
2. sentence_structure: short/varied/complex/fragmented
3. verbal_tics: Lista 2-3 słów/fraz których używa (lub pusta jeśli brak)
4. favorite_phrases: 2-3 ulubione zwroty tej postaci
5. forbidden_words: 2-3 słowa których ta postać NIGDY by nie użyła
6. speech_rhythm: fast/slow/deliberate/nervous/normal
7. formality_default: formal/casual/street/archaic
8. emotional_expression: reserved/moderate/expressive/volatile
9. interruption_tendency: 0.0-1.0 (jak często przerywa)
10. silence_comfort: 0.0-1.0 (jak komfortowo znosi ciszę)
11. deflection_patterns: Jak unika trudnych tematów (2-3 wzorce)

Odpowiedz w JSON:
{{
    "vocabulary_level": "...",
    "sentence_structure": "...",
    "verbal_tics": ["...", "..."],
    "favorite_phrases": ["...", "..."],
    "forbidden_words": ["...", "..."],
    "speech_rhythm": "...",
    "formality_default": "...",
    "emotional_expression": "...",
    "interruption_tendency": 0.3,
    "silence_comfort": 0.5,
    "deflection_patterns": ["zmienia temat na...", "żartuje aby..."]
}}"""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                model_tier=1,
                max_tokens=1000,
                temperature=0.7
            )

            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                profile = CharacterVoice(
                    character_name=character_name,
                    vocabulary_level=data.get("vocabulary_level", "moderate"),
                    sentence_structure=data.get("sentence_structure", "varied"),
                    verbal_tics=data.get("verbal_tics", []),
                    favorite_phrases=data.get("favorite_phrases", []),
                    forbidden_words=data.get("forbidden_words", []),
                    speech_rhythm=data.get("speech_rhythm", "normal"),
                    formality_default=data.get("formality_default", "casual"),
                    emotional_expression=data.get("emotional_expression", "moderate"),
                    interruption_tendency=float(data.get("interruption_tendency", 0.3)),
                    silence_comfort=float(data.get("silence_comfort", 0.5)),
                    deflection_patterns=data.get("deflection_patterns", [])
                )
                self.register_voice(profile)
                return profile

        except Exception as e:
            logger.error(f"Failed to generate voice profile: {e}")

        # Return default profile
        return CharacterVoice(
            character_name=character_name,
            vocabulary_level="moderate",
            sentence_structure="varied"
        )

    # =========================================================================
    # SUBTEXT ANALYSIS
    # =========================================================================

    async def analyze_subtext(
        self,
        dialogue_line: str,
        speaker: str,
        context: DialogueContext
    ) -> SubtextLayer:
        """Analyze the subtext of a dialogue line"""
        speaker_wants = context.what_each_wants.get(speaker, "unknown")
        speaker_hides = context.what_each_hides.get(speaker, [])
        speaker_emotion = context.emotional_states.get(speaker, "neutral")

        prompt = f"""Przeanalizuj subtext tej kwestii dialogowej:

KWESTIA: "{dialogue_line}"
MÓWIĄCY: {speaker}
RELACJA: {context.relationship_type}
USTAWIENIE: {context.scene_setting}
CZEGO CHCE: {speaker_wants}
CO UKRYWA: {speaker_hides}
STAN EMOCJONALNY: {speaker_emotion}
STAWKA: {context.stakes}

Określ:
1. surface_meaning: Co DOSŁOWNIE mówi ta osoba?
2. true_meaning: Co NAPRAWDĘ ma na myśli?
3. subtext_type: Jeden z: hidden_agenda, suppressed_emotion, power_play, deflection, manipulation, intimacy_seeking, intimacy_avoiding, testing, performance, revelation
4. character_aware: Czy postać jest świadoma swojego subtextu? (true/false)
5. reader_should_know: Czy czytelnik powinien rozumieć subtext? (true/false)
6. intensity: Jak silny jest subtext? (0.0-1.0)

Odpowiedz w JSON:
{{
    "surface_meaning": "...",
    "true_meaning": "...",
    "subtext_type": "...",
    "character_aware": true,
    "reader_should_know": true,
    "intensity": 0.5
}}"""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                model_tier=1,
                max_tokens=500,
                temperature=0.5
            )

            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return SubtextLayer(
                    surface_meaning=data.get("surface_meaning", dialogue_line),
                    true_meaning=data.get("true_meaning", dialogue_line),
                    subtext_type=SubtextType(data.get("subtext_type", "suppressed_emotion")),
                    character_aware=data.get("character_aware", True),
                    reader_should_know=data.get("reader_should_know", True),
                    intensity=float(data.get("intensity", 0.5))
                )

        except Exception as e:
            logger.warning(f"Subtext analysis failed: {e}")

        return SubtextLayer(
            surface_meaning=dialogue_line,
            true_meaning=dialogue_line,
            subtext_type=SubtextType.SUPPRESSED_EMOTION
        )

    # =========================================================================
    # DIALOGUE GENERATION
    # =========================================================================

    async def generate_dialogue_exchange(
        self,
        context: DialogueContext,
        num_beats: int = 8,
        subtext_density: float = 0.6
    ) -> DialogueExchange:
        """Generate a complete dialogue exchange with subtext"""

        participants = list(context.what_each_wants.keys())
        if len(participants) < 2:
            raise ValueError("Need at least 2 participants for dialogue")

        # Get voice profiles
        voices = {
            name: self.voice_profiles.get(name, CharacterVoice(character_name=name, vocabulary_level="moderate", sentence_structure="varied"))
            for name in participants
        }

        prompt = self._build_dialogue_prompt(context, voices, num_beats, subtext_density)

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                model_tier=2,
                max_tokens=3000,
                temperature=0.8
            )

            return self._parse_dialogue_response(response, context, participants)

        except Exception as e:
            logger.error(f"Dialogue generation failed: {e}")
            return self._create_fallback_exchange(participants, context)

    def _build_dialogue_prompt(
        self,
        context: DialogueContext,
        voices: Dict[str, CharacterVoice],
        num_beats: int,
        subtext_density: float
    ) -> str:
        """Build the prompt for dialogue generation"""

        participants_str = []
        for name, voice in voices.items():
            participants_str.append(f"""
{name}:
- Chce: {context.what_each_wants.get(name, 'nieznane')}
- Wie: {context.what_each_knows.get(name, [])}
- Ukrywa: {context.what_each_hides.get(name, [])}
- Stan emocjonalny: {context.emotional_states.get(name, 'neutralny')}
- Pozycja władzy: {context.power_balance.get(name, 0.5)}/1.0
- Głos: {voice.vocabulary_level}, {voice.sentence_structure}, rhythm: {voice.speech_rhythm}
- Tiki: {voice.verbal_tics}
- Ulubione zwroty: {voice.favorite_phrases}
""")

        subtext_instruction = ""
        if subtext_density > 0.7:
            subtext_instruction = "WYSOKI POZIOM SUBTEXTU: Prawie każda kwestia powinna mieć ukryte znaczenie."
        elif subtext_density > 0.4:
            subtext_instruction = "UMIARKOWANY SUBTEXT: Co druga kwestia powinna mieć warstwę ukrytego znaczenia."
        else:
            subtext_instruction = "NISKI SUBTEXT: Dialog głównie powierzchowny z okazjonalnymi ukrytymi znaczeniami."

        return f"""Jesteś mistrzem dialogu z głębokim subtextem. Napisz wymianę dialogową.

## KONTEKST SCENY
Miejsce: {context.scene_setting}
Relacja: {context.relationship_type}
Historia relacji: {context.relationship_history}
Gatunek: {context.genre.value}
Stawka: {context.stakes}
POV postać: {context.pov_character or 'brak określonej'}

## UCZESTNICY
{chr(10).join(participants_str)}

## WYMAGANIA DIALOGU
- Liczba beat'ów: około {num_beats}
- {subtext_instruction}
- Każdy mówi INACZEJ - różne słownictwo, rytm, długość zdań
- Uwzględnij CISZĘ jako element dialogu
- Uwzględnij AKCJE między kwestiami (action beats)
- Dynamika władzy powinna się ZMIENIAĆ w trakcie rozmowy
- Emocje pod powierzchnią powinny być WIDOCZNE przez sposób mówienia

## FORMAT ODPOWIEDZI
Napisz dialog w formie prozy literackiej (nie scenariusza).
Każda kwestia z myślnikiem (—).
Po dialogu dodaj analizę:

[DIALOG]
(tutaj dialog w prozie)

[ANALIZA]
{{
    "beats": [
        {{
            "speaker": "imię",
            "beat_type": "statement/question/response/deflection/interruption/silence/action_beat/internal_thought/revelation",
            "spoken_text": "co mówi lub null",
            "action_text": "co robi lub null",
            "subtext": {{
                "surface": "co mówi",
                "true_meaning": "co naprawdę znaczy",
                "type": "typ subtextu"
            }} lub null,
            "emotional_state": "emocja",
            "power_position": "dominant/submissive/equal"
        }}
    ],
    "overall_power_dynamic": "dominant/submissive/equal/shifting/contested",
    "emotional_undercurrent": "desire/resentment/fear/guilt/longing/suspicion/hope/desperation/contempt/affection",
    "relationship_change": "jak zmienia się relacja",
    "tension_arc": [0.3, 0.5, 0.7, 0.6, ...]
}}"""

    def _parse_dialogue_response(
        self,
        response: str,
        context: DialogueContext,
        participants: List[str]
    ) -> DialogueExchange:
        """Parse the AI response into DialogueExchange"""

        # Split into dialogue and analysis
        parts = response.split("[ANALIZA]")
        dialogue_text = parts[0].replace("[DIALOG]", "").strip()

        # Parse analysis JSON
        beats = []
        power_dynamic = PowerDynamic.EQUAL
        undercurrent = EmotionalUndercurrent.SUSPICION
        relationship_change = "nieznane"
        tension_arc = [0.5]

        if len(parts) > 1:
            try:
                import re
                json_match = re.search(r'\{[\s\S]*\}', parts[1])
                if json_match:
                    analysis = json.loads(json_match.group(0))

                    # Parse beats
                    for beat_data in analysis.get("beats", []):
                        subtext = None
                        if beat_data.get("subtext"):
                            st = beat_data["subtext"]
                            try:
                                subtext_type = SubtextType(st.get("type", "suppressed_emotion"))
                            except ValueError:
                                subtext_type = SubtextType.SUPPRESSED_EMOTION

                            subtext = SubtextLayer(
                                surface_meaning=st.get("surface", ""),
                                true_meaning=st.get("true_meaning", ""),
                                subtext_type=subtext_type
                            )

                        try:
                            beat_type = DialogueBeatType(beat_data.get("beat_type", "statement"))
                        except ValueError:
                            beat_type = DialogueBeatType.STATEMENT

                        beats.append(DialogueBeat(
                            speaker=beat_data.get("speaker", participants[0]),
                            beat_type=beat_type,
                            spoken_text=beat_data.get("spoken_text"),
                            action_text=beat_data.get("action_text"),
                            subtext=subtext,
                            emotional_state=beat_data.get("emotional_state", "neutral"),
                            power_position=beat_data.get("power_position", "equal")
                        ))

                    # Parse other fields
                    try:
                        power_dynamic = PowerDynamic(analysis.get("overall_power_dynamic", "equal"))
                    except ValueError:
                        power_dynamic = PowerDynamic.EQUAL

                    try:
                        undercurrent = EmotionalUndercurrent(analysis.get("emotional_undercurrent", "suspicion"))
                    except ValueError:
                        undercurrent = EmotionalUndercurrent.SUSPICION

                    relationship_change = analysis.get("relationship_change", "nieznane")
                    tension_arc = analysis.get("tension_arc", [0.5])

            except Exception as e:
                logger.warning(f"Failed to parse dialogue analysis: {e}")

        return DialogueExchange(
            participants=participants,
            beats=beats,
            overall_power_dynamic=power_dynamic,
            emotional_undercurrent=undercurrent,
            relationship_change=relationship_change,
            tension_arc=tension_arc,
            subtext_density=len([b for b in beats if b.subtext]) / max(len(beats), 1),
            formatted_dialogue=dialogue_text
        )

    def _create_fallback_exchange(
        self,
        participants: List[str],
        context: DialogueContext
    ) -> DialogueExchange:
        """Create a basic fallback exchange"""
        return DialogueExchange(
            participants=participants,
            beats=[],
            overall_power_dynamic=PowerDynamic.EQUAL,
            emotional_undercurrent=EmotionalUndercurrent.SUSPICION,
            relationship_change="nieznane",
            tension_arc=[0.5],
            subtext_density=0.0,
            formatted_dialogue="[Dialog wymaga regeneracji]"
        )

    # =========================================================================
    # DIALOGUE ENHANCEMENT
    # =========================================================================

    async def enhance_existing_dialogue(
        self,
        dialogue_text: str,
        character_a: str,
        character_b: str,
        context: DialogueContext,
        enhancement_focus: str = "subtext"
    ) -> str:
        """Enhance existing dialogue with more subtext, power dynamics, or voice"""

        focus_instructions = {
            "subtext": """
Dodaj warstwy subtextu:
- Postacie mówią jedno, mają na myśli drugie
- Ukryte agendy widoczne przez wybór słów
- Emocje tłumione ale przebijające przez ton
""",
            "power_dynamics": """
Wyostrz dynamikę władzy:
- Kto kontroluje rozmowę i jak to się zmienia
- Mikroagresje, perswazja, manipulacja
- Przerywanie vs milczenie jako narzędzia władzy
""",
            "voice": """
Wyostrz głosy postaci:
- Każda postać mówi WYRAŹNIE INACZEJ
- Różne słownictwo, rytm, długość zdań
- Unikalne tiki językowe i zwroty
""",
            "emotion": """
Pogłęb emocje:
- Pokaż emocje przez sposób mówienia, nie opisy
- Napięcie widoczne w wyborze słów
- Momenty ciszy nasycone znaczeniem
"""
        }

        instruction = focus_instructions.get(enhancement_focus, focus_instructions["subtext"])

        prompt = f"""Ulepsz ten dialog, zachowując treść ale dodając głębię:

ORYGINALNY DIALOG:
{dialogue_text}

POSTAĆ A: {character_a}
POSTAĆ B: {character_b}
RELACJA: {context.relationship_type}
KONTEKST: {context.scene_setting}
STAWKA: {context.stakes}

FOKUS ULEPSZENIA:
{instruction}

Napisz ulepszony dialog. Zachowaj sens i przebieg rozmowy, ale dodaj wskazane elementy.
Zwróć TYLKO ulepszony dialog bez komentarzy."""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                model_tier=2,
                max_tokens=2000,
                temperature=0.7
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Dialogue enhancement failed: {e}")
            return dialogue_text

    async def generate_confrontation_dialogue(
        self,
        character_a: str,
        character_b: str,
        conflict_topic: str,
        context: DialogueContext,
        escalation_level: float = 0.7
    ) -> DialogueExchange:
        """Generate a confrontational dialogue with escalating tension"""

        context.stakes = f"Konfrontacja dotycząca: {conflict_topic}"

        # Adjust power balance for confrontation
        context.power_balance[character_a] = 0.6
        context.power_balance[character_b] = 0.6

        # Set emotional states
        context.emotional_states[character_a] = "gniewny"
        context.emotional_states[character_b] = "defensywny"

        num_beats = int(6 + escalation_level * 8)  # 6-14 beats

        return await self.generate_dialogue_exchange(
            context=context,
            num_beats=num_beats,
            subtext_density=min(0.9, 0.5 + escalation_level * 0.4)
        )

    async def generate_seduction_dialogue(
        self,
        pursuer: str,
        pursued: str,
        context: DialogueContext,
        subtlety: float = 0.7
    ) -> DialogueExchange:
        """Generate a romantic/seductive dialogue with tension"""

        context.what_each_wants[pursuer] = "Zbliżenie emocjonalne/fizyczne"
        context.emotional_states[pursuer] = "pożądanie"
        context.emotional_states[pursued] = "zaciekawienie"

        subtext_density = min(0.95, 0.6 + subtlety * 0.35)

        return await self.generate_dialogue_exchange(
            context=context,
            num_beats=10,
            subtext_density=subtext_density
        )

    async def generate_interrogation_dialogue(
        self,
        interrogator: str,
        subject: str,
        secret: str,
        context: DialogueContext
    ) -> DialogueExchange:
        """Generate an interrogation-style dialogue"""

        context.power_balance[interrogator] = 0.8
        context.power_balance[subject] = 0.2
        context.what_each_wants[interrogator] = f"Wydobyć informację: {secret}"
        context.what_each_wants[subject] = "Ukryć prawdę i wyjść z tego"
        context.what_each_hides[subject] = [secret]
        context.emotional_states[interrogator] = "zdeterminowany"
        context.emotional_states[subject] = "przestraszony"
        context.stakes = f"Sekret: {secret}"

        return await self.generate_dialogue_exchange(
            context=context,
            num_beats=12,
            subtext_density=0.8
        )

    # =========================================================================
    # DIALOGUE VALIDATION
    # =========================================================================

    async def validate_dialogue_voices(
        self,
        dialogue_text: str,
        characters: Dict[str, CharacterVoice]
    ) -> Dict[str, Any]:
        """Validate that dialogue maintains consistent character voices"""

        char_profiles = {
            name: voice.to_dict()
            for name, voice in characters.items()
        }

        prompt = f"""Przeanalizuj czy ten dialog zachowuje spójność głosów postaci:

DIALOG:
{dialogue_text[:2000]}

PROFILE GŁOSOWE:
{json.dumps(char_profiles, ensure_ascii=False, indent=2)}

Sprawdź:
1. Czy każda postać mówi zgodnie ze swoim profilem głosowym?
2. Czy używają odpowiedniego słownictwa?
3. Czy struktura zdań jest spójna z profilem?
4. Czy tiki językowe są obecne?
5. Czy nie używają zakazanych słów?

Odpowiedz w JSON:
{{
    "is_consistent": true/false,
    "issues": [
        {{"character": "imię", "issue": "opis problemu", "example": "cytat"}}
    ],
    "scores": {{
        "imię": 0.0-1.0
    }},
    "overall_voice_quality": 0.0-1.0
}}"""

        try:
            response = await self.ai_service.generate(
                prompt=prompt,
                model_tier=1,
                max_tokens=800,
                temperature=0.3
            )

            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))

        except Exception as e:
            logger.error(f"Voice validation failed: {e}")

        return {
            "is_consistent": True,
            "issues": [],
            "scores": {name: 0.7 for name in characters.keys()},
            "overall_voice_quality": 0.7
        }


# =============================================================================
# SINGLETON AND FACTORY
# =============================================================================

_dialogue_system: Optional[AdvancedDialogueSystem] = None


def get_advanced_dialogue_system() -> AdvancedDialogueSystem:
    """Get or create advanced dialogue system instance"""
    global _dialogue_system
    if _dialogue_system is None:
        _dialogue_system = AdvancedDialogueSystem()
    return _dialogue_system
