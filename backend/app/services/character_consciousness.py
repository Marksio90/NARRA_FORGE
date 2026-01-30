"""
Character Consciousness Simulation - NarraForge 3.0

System symulacji świadomości postaci zapewniający:
- Spójność psychologiczną przez całą narrację
- Modelowanie procesów decyzyjnych postaci
- Symulację wewnętrznego dialogu
- Śledzenie motywacji i celów
- Pamięć emocjonalną i relacyjną
- Ewolucję charakteru w czasie

Każda postać zyskuje "wirtualną świadomość" która determinuje jej reakcje,
decyzje i rozwój w sposób spójny z jej profilem psychologicznym.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
import json
import asyncio

from app.services.llm_service import get_llm_service


# =============================================================================
# ENUMS
# =============================================================================

class PersonalityDimension(Enum):
    """Big Five + dodatkowe wymiary istotne dla narracji"""
    OPENNESS = "openness"  # Otwartość na doświadczenia
    CONSCIENTIOUSNESS = "conscientiousness"  # Sumienność
    EXTRAVERSION = "extraversion"  # Ekstrawersja
    AGREEABLENESS = "agreeableness"  # Ugodowość
    NEUROTICISM = "neuroticism"  # Neurotyzm
    # Dodatkowe wymiary narracyjne
    MORAL_FLEXIBILITY = "moral_flexibility"  # Elastyczność moralna
    RISK_TOLERANCE = "risk_tolerance"  # Tolerancja ryzyka
    ATTACHMENT_STYLE = "attachment_style"  # Styl przywiązania


class EmotionalState(Enum):
    """Podstawowe stany emocjonalne"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    SURPRISED = "surprised"
    DISGUSTED = "disgusted"
    ANXIOUS = "anxious"
    HOPEFUL = "hopeful"
    DESPERATE = "desperate"
    CONFLICTED = "conflicted"


class DefenseMechanism(Enum):
    """Mechanizmy obronne psychologiczne"""
    DENIAL = "denial"  # Zaprzeczanie
    PROJECTION = "projection"  # Projekcja
    RATIONALIZATION = "rationalization"  # Racjonalizacja
    DISPLACEMENT = "displacement"  # Przemieszczenie
    SUBLIMATION = "sublimation"  # Sublimacja
    REPRESSION = "repression"  # Wyparcie
    REGRESSION = "regression"  # Regresja
    INTELLECTUALIZATION = "intellectualization"  # Intelektualizacja
    REACTION_FORMATION = "reaction_formation"  # Tworzenie reakcji przeciwnej
    HUMOR = "humor"  # Humor jako obrona


class AttachmentStyle(Enum):
    """Style przywiązania wpływające na relacje"""
    SECURE = "secure"  # Bezpieczny
    ANXIOUS = "anxious"  # Lękowy
    AVOIDANT = "avoidant"  # Unikający
    DISORGANIZED = "disorganized"  # Zdezorganizowany


class CopingStrategy(Enum):
    """Strategie radzenia sobie ze stresem"""
    PROBLEM_FOCUSED = "problem_focused"  # Skupienie na problemie
    EMOTION_FOCUSED = "emotion_focused"  # Skupienie na emocjach
    AVOIDANCE = "avoidance"  # Unikanie
    SOCIAL_SUPPORT = "social_support"  # Szukanie wsparcia
    CONFRONTATION = "confrontation"  # Konfrontacja
    ACCEPTANCE = "acceptance"  # Akceptacja


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class CoreBelief:
    """Podstawowe przekonanie postaci"""
    belief: str  # Treść przekonania
    strength: float  # Siła przekonania 0-1
    origin: str  # Źródło (trauma, wychowanie, doświadczenie)
    can_be_challenged: bool = True  # Czy może być zakwestionowane
    related_fears: List[str] = field(default_factory=list)
    related_desires: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "belief": self.belief,
            "strength": self.strength,
            "origin": self.origin,
            "can_be_challenged": self.can_be_challenged,
            "related_fears": self.related_fears,
            "related_desires": self.related_desires
        }


@dataclass
class InternalConflict:
    """Wewnętrzny konflikt postaci"""
    conflict_type: str  # np. "duty_vs_desire", "loyalty_vs_truth"
    side_a: str  # Jedna strona konfliktu
    side_b: str  # Druga strona konfliktu
    current_lean: float  # -1.0 (side_a) do 1.0 (side_b)
    intensity: float  # Intensywność konfliktu 0-1
    triggers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_type": self.conflict_type,
            "side_a": self.side_a,
            "side_b": self.side_b,
            "current_lean": self.current_lean,
            "intensity": self.intensity,
            "triggers": self.triggers
        }


@dataclass
class Motivation:
    """Motywacja postaci"""
    goal: str  # Cel
    type: str  # "conscious" lub "unconscious"
    priority: float  # Priorytet 0-1
    obstacles: List[str] = field(default_factory=list)
    progress: float = 0.0  # Postęp 0-1
    deadline_pressure: float = 0.0  # Presja czasowa 0-1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "type": self.type,
            "priority": self.priority,
            "obstacles": self.obstacles,
            "progress": self.progress,
            "deadline_pressure": self.deadline_pressure
        }


@dataclass
class EmotionalMemory:
    """Wspomnienie emocjonalne"""
    event: str
    emotion: EmotionalState
    intensity: float
    chapter: int
    related_characters: List[str]
    impact_on_beliefs: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": self.event,
            "emotion": self.emotion.value,
            "intensity": self.intensity,
            "chapter": self.chapter,
            "related_characters": self.related_characters,
            "impact_on_beliefs": self.impact_on_beliefs
        }


@dataclass
class RelationshipPerception:
    """Percepcja relacji z inną postacią"""
    other_character: str
    trust_level: float  # -1.0 do 1.0
    emotional_bond: float  # 0 do 1.0
    perceived_threat: float  # 0 do 1.0
    perceived_utility: float  # 0 do 1.0
    unresolved_issues: List[str] = field(default_factory=list)
    positive_memories: List[str] = field(default_factory=list)
    negative_memories: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "other_character": self.other_character,
            "trust_level": self.trust_level,
            "emotional_bond": self.emotional_bond,
            "perceived_threat": self.perceived_threat,
            "perceived_utility": self.perceived_utility,
            "unresolved_issues": self.unresolved_issues,
            "positive_memories": self.positive_memories,
            "negative_memories": self.negative_memories
        }


@dataclass
class ThoughtProcess:
    """Proces myślowy postaci w danej sytuacji"""
    situation: str
    immediate_reaction: str
    emotional_response: EmotionalState
    triggered_beliefs: List[str]
    triggered_fears: List[str]
    considered_options: List[str]
    eliminated_options: List[Tuple[str, str]]  # (opcja, powód)
    chosen_action: str
    rationalization: str  # Jak postać uzasadnia decyzję
    suppressed_thoughts: List[str]  # Myśli, które postać tłumi

    def to_dict(self) -> Dict[str, Any]:
        return {
            "situation": self.situation,
            "immediate_reaction": self.immediate_reaction,
            "emotional_response": self.emotional_response.value,
            "triggered_beliefs": self.triggered_beliefs,
            "triggered_fears": self.triggered_fears,
            "considered_options": self.considered_options,
            "eliminated_options": [{"option": o, "reason": r} for o, r in self.eliminated_options],
            "chosen_action": self.chosen_action,
            "rationalization": self.rationalization,
            "suppressed_thoughts": self.suppressed_thoughts
        }


@dataclass
class ConsciousnessState:
    """Bieżący stan świadomości postaci"""
    character_name: str
    current_emotion: EmotionalState
    emotion_intensity: float
    active_motivations: List[Motivation]
    active_conflicts: List[InternalConflict]
    current_stress_level: float
    cognitive_load: float  # Ile "przetwarza" umysłowo
    active_defense_mechanisms: List[DefenseMechanism]
    current_coping_strategy: CopingStrategy

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_name": self.character_name,
            "current_emotion": self.current_emotion.value,
            "emotion_intensity": self.emotion_intensity,
            "active_motivations": [m.to_dict() for m in self.active_motivations],
            "active_conflicts": [c.to_dict() for c in self.active_conflicts],
            "current_stress_level": self.current_stress_level,
            "cognitive_load": self.cognitive_load,
            "active_defense_mechanisms": [d.value for d in self.active_defense_mechanisms],
            "current_coping_strategy": self.current_coping_strategy.value
        }


# =============================================================================
# CHARACTER CONSCIOUSNESS
# =============================================================================

@dataclass
class CharacterConsciousness:
    """
    Pełna reprezentacja świadomości postaci.

    Zawiera wszystkie aspekty psychologiczne potrzebne do
    spójnego modelowania zachowań i rozwoju postaci.
    """
    character_name: str

    # Osobowość (Big Five + extras)
    personality: Dict[PersonalityDimension, float] = field(default_factory=dict)

    # Podstawowe przekonania
    core_beliefs: List[CoreBelief] = field(default_factory=list)

    # Wewnętrzne konflikty
    internal_conflicts: List[InternalConflict] = field(default_factory=list)

    # Motywacje (świadome i nieświadome)
    motivations: List[Motivation] = field(default_factory=list)

    # Lęki i pragnienia
    deepest_fears: List[str] = field(default_factory=list)
    deepest_desires: List[str] = field(default_factory=list)

    # Styl przywiązania
    attachment_style: AttachmentStyle = AttachmentStyle.SECURE

    # Preferowane mechanizmy obronne
    preferred_defenses: List[DefenseMechanism] = field(default_factory=list)

    # Preferowane strategie radzenia sobie
    preferred_coping: List[CopingStrategy] = field(default_factory=list)

    # Wspomnienia emocjonalne
    emotional_memories: List[EmotionalMemory] = field(default_factory=list)

    # Percepcje relacji
    relationships: Dict[str, RelationshipPerception] = field(default_factory=dict)

    # Trauma i rany emocjonalne
    emotional_wounds: List[str] = field(default_factory=list)

    # Wartości (hierarchia)
    values_hierarchy: List[str] = field(default_factory=list)

    # Bieżący stan
    current_state: Optional[ConsciousnessState] = None

    # Historia myśli (dla kontekstu)
    thought_history: List[ThoughtProcess] = field(default_factory=list)

    # Arc postaci
    character_arc_stage: str = "ordinary_world"  # Etap podróży bohatera
    growth_points: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_name": self.character_name,
            "personality": {k.value: v for k, v in self.personality.items()},
            "core_beliefs": [b.to_dict() for b in self.core_beliefs],
            "internal_conflicts": [c.to_dict() for c in self.internal_conflicts],
            "motivations": [m.to_dict() for m in self.motivations],
            "deepest_fears": self.deepest_fears,
            "deepest_desires": self.deepest_desires,
            "attachment_style": self.attachment_style.value,
            "preferred_defenses": [d.value for d in self.preferred_defenses],
            "preferred_coping": [c.value for c in self.preferred_coping],
            "emotional_memories": [m.to_dict() for m in self.emotional_memories],
            "relationships": {k: v.to_dict() for k, v in self.relationships.items()},
            "emotional_wounds": self.emotional_wounds,
            "values_hierarchy": self.values_hierarchy,
            "current_state": self.current_state.to_dict() if self.current_state else None,
            "character_arc_stage": self.character_arc_stage,
            "growth_points": self.growth_points
        }


# =============================================================================
# CONSCIOUSNESS SIMULATION ENGINE
# =============================================================================

class CharacterConsciousnessSimulator:
    """
    Silnik symulacji świadomości postaci.

    Funkcje:
    - Tworzenie profilu psychologicznego z danych postaci
    - Symulacja procesów myślowych
    - Przewidywanie reakcji na sytuacje
    - Generowanie wewnętrznego dialogu
    - Śledzenie ewolucji postaci
    - Zapewnianie spójności psychologicznej
    """

    def __init__(self):
        self.llm_service = get_llm_service()
        self.consciousnesses: Dict[str, CharacterConsciousness] = {}

    def _get_llm(self, tier: str = "mid"):
        """Get appropriate LLM based on tier"""
        return self.llm_service.get_client(tier)

    # =========================================================================
    # PROFILE CREATION
    # =========================================================================

    async def create_consciousness_from_character(
        self,
        character_name: str,
        character_data: Dict[str, Any]
    ) -> CharacterConsciousness:
        """
        Tworzy pełny profil świadomości na podstawie danych postaci.
        """
        prompt = f"""Jako ekspert psychologii postaci literackich, stwórz głęboki profil
psychologiczny dla postaci na podstawie jej opisu.

DANE POSTACI:
{json.dumps(character_data, ensure_ascii=False, indent=2)}

Stwórz szczegółowy profil zawierający:

1. OSOBOWOŚĆ (Big Five, skala 0-1):
- openness (otwartość na doświadczenia)
- conscientiousness (sumienność)
- extraversion (ekstrawersja)
- agreeableness (ugodowość)
- neuroticism (neurotyzm)
- moral_flexibility (elastyczność moralna)
- risk_tolerance (tolerancja ryzyka)

2. PODSTAWOWE PRZEKONANIA (3-5):
Dla każdego: przekonanie, siła (0-1), źródło, powiązane lęki, powiązane pragnienia

3. WEWNĘTRZNE KONFLIKTY (1-3):
Dla każdego: typ, strona_a, strona_b, intensywność, wyzwalacze

4. MOTYWACJE (świadome i nieświadome):
Dla każdej: cel, typ, priorytet, przeszkody

5. NAJGŁĘBSZE LĘKI (2-3)

6. NAJGŁĘBSZE PRAGNIENIA (2-3)

7. STYL PRZYWIĄZANIA: secure/anxious/avoidant/disorganized

8. PREFEROWANE MECHANIZMY OBRONNE (2-3)

9. STRATEGIE RADZENIA SOBIE (2)

10. RANY EMOCJONALNE (1-2)

11. HIERARCHIA WARTOŚCI (top 5)

Odpowiedz w formacie JSON."""

        response = await self._get_llm("high").chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        profile_data = json.loads(response.choices[0].message.content)

        # Tworzenie obiektu świadomości
        consciousness = CharacterConsciousness(character_name=character_name)

        # Personality
        if "personality" in profile_data:
            for dim_name, value in profile_data["personality"].items():
                try:
                    dim = PersonalityDimension(dim_name)
                    consciousness.personality[dim] = float(value)
                except (ValueError, TypeError):
                    pass

        # Core beliefs
        if "core_beliefs" in profile_data:
            for belief_data in profile_data["core_beliefs"]:
                consciousness.core_beliefs.append(CoreBelief(
                    belief=belief_data.get("belief", ""),
                    strength=float(belief_data.get("strength", 0.5)),
                    origin=belief_data.get("origin", "unknown"),
                    can_be_challenged=belief_data.get("can_be_challenged", True),
                    related_fears=belief_data.get("related_fears", []),
                    related_desires=belief_data.get("related_desires", [])
                ))

        # Internal conflicts
        if "internal_conflicts" in profile_data:
            for conflict_data in profile_data["internal_conflicts"]:
                consciousness.internal_conflicts.append(InternalConflict(
                    conflict_type=conflict_data.get("type", "unknown"),
                    side_a=conflict_data.get("side_a", ""),
                    side_b=conflict_data.get("side_b", ""),
                    current_lean=float(conflict_data.get("current_lean", 0.0)),
                    intensity=float(conflict_data.get("intensity", 0.5)),
                    triggers=conflict_data.get("triggers", [])
                ))

        # Motivations
        if "motivations" in profile_data:
            for mot_data in profile_data["motivations"]:
                consciousness.motivations.append(Motivation(
                    goal=mot_data.get("goal", ""),
                    type=mot_data.get("type", "conscious"),
                    priority=float(mot_data.get("priority", 0.5)),
                    obstacles=mot_data.get("obstacles", [])
                ))

        # Simple lists
        consciousness.deepest_fears = profile_data.get("deepest_fears", [])
        consciousness.deepest_desires = profile_data.get("deepest_desires", [])
        consciousness.emotional_wounds = profile_data.get("emotional_wounds", [])
        consciousness.values_hierarchy = profile_data.get("values_hierarchy", [])

        # Attachment style
        try:
            consciousness.attachment_style = AttachmentStyle(
                profile_data.get("attachment_style", "secure")
            )
        except ValueError:
            consciousness.attachment_style = AttachmentStyle.SECURE

        # Defense mechanisms
        for defense in profile_data.get("preferred_defenses", []):
            try:
                consciousness.preferred_defenses.append(DefenseMechanism(defense))
            except ValueError:
                pass

        # Coping strategies
        for coping in profile_data.get("preferred_coping", []):
            try:
                consciousness.preferred_coping.append(CopingStrategy(coping))
            except ValueError:
                pass

        # Initialize current state
        consciousness.current_state = ConsciousnessState(
            character_name=character_name,
            current_emotion=EmotionalState.NEUTRAL,
            emotion_intensity=0.3,
            active_motivations=consciousness.motivations[:3],
            active_conflicts=consciousness.internal_conflicts,
            current_stress_level=0.2,
            cognitive_load=0.3,
            active_defense_mechanisms=[],
            current_coping_strategy=consciousness.preferred_coping[0] if consciousness.preferred_coping else CopingStrategy.PROBLEM_FOCUSED
        )

        # Store consciousness
        self.consciousnesses[character_name] = consciousness

        return consciousness

    # =========================================================================
    # THOUGHT SIMULATION
    # =========================================================================

    async def simulate_thought_process(
        self,
        character_name: str,
        situation: str,
        available_actions: List[str] = None,
        other_characters_present: List[str] = None
    ) -> ThoughtProcess:
        """
        Symuluje proces myślowy postaci w danej sytuacji.

        Zwraca szczegółowy opis tego, co dzieje się w umyśle postaci,
        włącznie z myślami, których postać nie wypowiada.
        """
        if character_name not in self.consciousnesses:
            raise ValueError(f"Brak profilu świadomości dla: {character_name}")

        consciousness = self.consciousnesses[character_name]

        # Build context
        relationships_context = ""
        if other_characters_present:
            for other in other_characters_present:
                if other in consciousness.relationships:
                    rel = consciousness.relationships[other]
                    relationships_context += f"\n- {other}: zaufanie={rel.trust_level:.2f}, więź={rel.emotional_bond:.2f}"

        prompt = f"""Jako symulator świadomości postaci, przeprowadź szczegółową analizę
procesu myślowego {character_name} w podanej sytuacji.

PROFIL PSYCHOLOGICZNY:
{json.dumps(consciousness.to_dict(), ensure_ascii=False, indent=2)}

SYTUACJA:
{situation}

{'OBECNE POSTACIE I RELACJE:' + relationships_context if relationships_context else ''}

{'DOSTĘPNE DZIAŁANIA:' + chr(10).join(f'- {a}' for a in available_actions) if available_actions else ''}

Przeprowadź symulację procesu myślowego:

1. NATYCHMIASTOWA REAKCJA: Pierwsza, instynktowna reakcja
2. ODPOWIEDŹ EMOCJONALNA: Jaką emocję czuje? (wybierz: neutral, happy, sad, angry, fearful, surprised, disgusted, anxious, hopeful, desperate, conflicted)
3. URUCHOMIONE PRZEKONANIA: Które z podstawowych przekonań się aktywują?
4. URUCHOMIONE LĘKI: Które lęki się pojawiają?
5. ROZWAŻANE OPCJE: Jakie opcje rozważa postać?
6. ODRZUCONE OPCJE: Które opcje odrzuca i dlaczego?
7. WYBRANE DZIAŁANIE: Co ostatecznie wybiera?
8. RACJONALIZACJA: Jak postać uzasadnia swoją decyzję przed sobą?
9. STŁUMIONE MYŚLI: Jakie myśli postać tłumi lub unika?

Odpowiedz w formacie JSON."""

        response = await self._get_llm("high").chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        thought_data = json.loads(response.choices[0].message.content)

        # Parse emotional response
        try:
            emotion = EmotionalState(thought_data.get("emotional_response", "neutral"))
        except ValueError:
            emotion = EmotionalState.NEUTRAL

        thought_process = ThoughtProcess(
            situation=situation,
            immediate_reaction=thought_data.get("immediate_reaction", ""),
            emotional_response=emotion,
            triggered_beliefs=thought_data.get("triggered_beliefs", []),
            triggered_fears=thought_data.get("triggered_fears", []),
            considered_options=thought_data.get("considered_options", []),
            eliminated_options=[
                (opt.get("option", ""), opt.get("reason", ""))
                for opt in thought_data.get("eliminated_options", [])
            ],
            chosen_action=thought_data.get("chosen_action", ""),
            rationalization=thought_data.get("rationalization", ""),
            suppressed_thoughts=thought_data.get("suppressed_thoughts", [])
        )

        # Add to history
        consciousness.thought_history.append(thought_process)

        # Update current state
        if consciousness.current_state:
            consciousness.current_state.current_emotion = emotion
            consciousness.current_state.emotion_intensity = thought_data.get("emotion_intensity", 0.5)

        return thought_process

    # =========================================================================
    # INTERNAL DIALOGUE GENERATION
    # =========================================================================

    async def generate_internal_monologue(
        self,
        character_name: str,
        situation: str,
        length: str = "medium",  # short, medium, long
        style: str = "stream_of_consciousness"  # stream_of_consciousness, reflective, anxious
    ) -> str:
        """
        Generuje wewnętrzny monolog postaci.

        Idealny do scen z głębokim POV gdzie pokazujemy myśli postaci.
        """
        if character_name not in self.consciousnesses:
            raise ValueError(f"Brak profilu świadomości dla: {character_name}")

        consciousness = self.consciousnesses[character_name]

        length_words = {"short": "50-80", "medium": "100-150", "long": "200-300"}

        style_instructions = {
            "stream_of_consciousness": "chaotyczny, przeskakujący, z przerwaniami myśli",
            "reflective": "spokojny, analityczny, z dystansem",
            "anxious": "nerwowy, z powtórzeniami, z katastroficznym myśleniem"
        }

        prompt = f"""Napisz wewnętrzny monolog postaci {character_name}.

PROFIL PSYCHOLOGICZNY (skrót):
- Osobowość: {json.dumps({k.value: v for k, v in consciousness.personality.items()}, ensure_ascii=False)}
- Najgłębsze lęki: {consciousness.deepest_fears}
- Najgłębsze pragnienia: {consciousness.deepest_desires}
- Aktywne konflikty wewnętrzne: {[c.conflict_type for c in consciousness.internal_conflicts]}
- Rany emocjonalne: {consciousness.emotional_wounds}

SYTUACJA:
{situation}

STYL MONOLOGU:
{style_instructions.get(style, style_instructions["stream_of_consciousness"])}

DŁUGOŚĆ: {length_words.get(length, "100-150")} słów

Napisz monolog w pierwszej osobie, po polsku.
Uwzględnij:
- Charakterystyczny sposób myślenia postaci
- Jej lęki i pragnienia przebijające przez myśli
- Mechanizmy obronne, które stosuje
- Myśli, które próbuje od siebie odpychać

Tylko sam monolog, bez komentarzy."""

        response = await self._get_llm("mid").chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )

        return response.choices[0].message.content.strip()

    # =========================================================================
    # REACTION PREDICTION
    # =========================================================================

    async def predict_reaction(
        self,
        character_name: str,
        stimulus: str,
        stimulus_source: str = None
    ) -> Dict[str, Any]:
        """
        Przewiduje reakcję postaci na bodziec.

        Przydatne do planowania scen i zapewniania spójności.
        """
        if character_name not in self.consciousnesses:
            raise ValueError(f"Brak profilu świadomości dla: {character_name}")

        consciousness = self.consciousnesses[character_name]

        # Check relationship if stimulus comes from another character
        relationship_context = ""
        if stimulus_source and stimulus_source in consciousness.relationships:
            rel = consciousness.relationships[stimulus_source]
            relationship_context = f"""
RELACJA Z {stimulus_source}:
- Poziom zaufania: {rel.trust_level}
- Więź emocjonalna: {rel.emotional_bond}
- Postrzegane zagrożenie: {rel.perceived_threat}
- Nierozwiązane kwestie: {rel.unresolved_issues}"""

        prompt = f"""Przewidź reakcję {character_name} na podany bodziec.

PROFIL PSYCHOLOGICZNY:
- Osobowość: {json.dumps({k.value: v for k, v in consciousness.personality.items()}, ensure_ascii=False)}
- Styl przywiązania: {consciousness.attachment_style.value}
- Preferowane mechanizmy obronne: {[d.value for d in consciousness.preferred_defenses]}
- Lęki: {consciousness.deepest_fears}
- Wartości: {consciousness.values_hierarchy}
{relationship_context}

BODZIEC:
{stimulus}

Przewidź:
1. NATYCHMIASTOWA REAKCJA EMOCJONALNA (emotion i intensity 0-1)
2. PRAWDOPODOBNA REAKCJA ZEWNĘTRZNA (co pokaże innym)
3. PRAWDOPODOBNA REAKCJA WEWNĘTRZNA (co naprawdę czuje/myśli)
4. URUCHOMIONE MECHANIZMY OBRONNE
5. POTENCJALNE DZIAŁANIA (lista od najbardziej do najmniej prawdopodobnego)
6. DŁUGOTERMINOWY WPŁYW na postać

Odpowiedz w JSON."""

        response = await self._get_llm("mid").chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    # =========================================================================
    # RELATIONSHIP DYNAMICS
    # =========================================================================

    async def update_relationship(
        self,
        character_name: str,
        other_character: str,
        event: str,
        event_type: str = "neutral"  # positive, negative, neutral, betrayal, intimacy
    ) -> RelationshipPerception:
        """
        Aktualizuje percepcję relacji na podstawie wydarzenia.
        """
        if character_name not in self.consciousnesses:
            raise ValueError(f"Brak profilu świadomości dla: {character_name}")

        consciousness = self.consciousnesses[character_name]

        # Get or create relationship
        if other_character not in consciousness.relationships:
            consciousness.relationships[other_character] = RelationshipPerception(
                other_character=other_character,
                trust_level=0.0,
                emotional_bond=0.0,
                perceived_threat=0.0,
                perceived_utility=0.0
            )

        rel = consciousness.relationships[other_character]

        prompt = f"""Zaktualizuj percepcję relacji {character_name} z {other_character}
po wydarzeniu.

OBECNA PERCEPCJA RELACJI:
{json.dumps(rel.to_dict(), ensure_ascii=False, indent=2)}

PROFIL {character_name}:
- Styl przywiązania: {consciousness.attachment_style.value}
- Rany emocjonalne: {consciousness.emotional_wounds}
- Wartości: {consciousness.values_hierarchy}

WYDARZENIE:
{event}

TYP WYDARZENIA: {event_type}

Zaktualizuj wartości (wszystkie w zakresie -1.0 do 1.0 lub 0 do 1.0):
1. trust_level (nowy poziom zaufania)
2. emotional_bond (nowa siła więzi)
3. perceived_threat (nowe postrzegane zagrożenie)
4. perceived_utility (nowa postrzegana użyteczność)
5. new_unresolved_issues (nowe nierozwiązane kwestie)
6. memory_classification ("positive" lub "negative")
7. memory_summary (krótki opis do zapamiętania)

Odpowiedz w JSON."""

        response = await self._get_llm("mid").chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )

        update_data = json.loads(response.choices[0].message.content)

        # Apply updates
        rel.trust_level = float(update_data.get("trust_level", rel.trust_level))
        rel.emotional_bond = float(update_data.get("emotional_bond", rel.emotional_bond))
        rel.perceived_threat = float(update_data.get("perceived_threat", rel.perceived_threat))
        rel.perceived_utility = float(update_data.get("perceived_utility", rel.perceived_utility))

        if update_data.get("new_unresolved_issues"):
            rel.unresolved_issues.extend(update_data["new_unresolved_issues"])

        memory_summary = update_data.get("memory_summary", event[:100])
        if update_data.get("memory_classification") == "positive":
            rel.positive_memories.append(memory_summary)
        else:
            rel.negative_memories.append(memory_summary)

        return rel

    # =========================================================================
    # CHARACTER ARC TRACKING
    # =========================================================================

    async def track_character_growth(
        self,
        character_name: str,
        chapter_events: List[str],
        chapter_number: int
    ) -> Dict[str, Any]:
        """
        Śledzi rozwój postaci i aktualizuje jej arc.
        """
        if character_name not in self.consciousnesses:
            raise ValueError(f"Brak profilu świadomości dla: {character_name}")

        consciousness = self.consciousnesses[character_name]

        prompt = f"""Przeanalizuj rozwój postaci {character_name} w rozdziale {chapter_number}.

OBECNY STAN POSTACI:
- Etap arc'u: {consciousness.character_arc_stage}
- Dotychczasowe punkty wzrostu: {consciousness.growth_points}
- Wewnętrzne konflikty: {[c.to_dict() for c in consciousness.internal_conflicts]}
- Rany emocjonalne: {consciousness.emotional_wounds}

WYDARZENIA W ROZDZIALE:
{chr(10).join(f'- {e}' for e in chapter_events)}

Przeanalizuj:
1. CZY NASTĄPIŁ WZROST/ZMIANA? (tak/nie)
2. NOWY ETAP ARC'U (jeśli się zmienił):
   ordinary_world -> call_to_adventure -> refusal -> meeting_mentor ->
   crossing_threshold -> tests_allies_enemies -> approach -> ordeal ->
   reward -> road_back -> resurrection -> return_with_elixir
3. NOWE PUNKTY WZROSTU (co postać zrozumiała/nauczyła się)
4. ZMIANY W PRZEKONANIACH (które przekonania się wzmocniły/osłabły)
5. ZMIANY W KONFLIKTACH (jak przesunęły się wewnętrzne konflikty)
6. ZBLIŻENIE DO GOJENIA RAN (czy rany zaczęły się goić)

Odpowiedz w JSON."""

        response = await self._get_llm("mid").chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            response_format={"type": "json_object"}
        )

        growth_data = json.loads(response.choices[0].message.content)

        # Apply updates
        if growth_data.get("new_arc_stage"):
            consciousness.character_arc_stage = growth_data["new_arc_stage"]

        if growth_data.get("new_growth_points"):
            consciousness.growth_points.extend(growth_data["new_growth_points"])

        # Update belief strengths
        if growth_data.get("belief_changes"):
            for change in growth_data["belief_changes"]:
                for belief in consciousness.core_beliefs:
                    if belief.belief == change.get("belief"):
                        belief.strength = float(change.get("new_strength", belief.strength))

        # Update conflict leanings
        if growth_data.get("conflict_changes"):
            for change in growth_data["conflict_changes"]:
                for conflict in consciousness.internal_conflicts:
                    if conflict.conflict_type == change.get("conflict_type"):
                        conflict.current_lean = float(change.get("new_lean", conflict.current_lean))

        return growth_data

    # =========================================================================
    # DIALOGUE CONSISTENCY
    # =========================================================================

    async def validate_dialogue_authenticity(
        self,
        character_name: str,
        dialogue_line: str,
        context: str
    ) -> Dict[str, Any]:
        """
        Sprawdza czy linia dialogowa jest autentyczna dla postaci.
        """
        if character_name not in self.consciousnesses:
            return {"authentic": True, "confidence": 0.5, "no_profile": True}

        consciousness = self.consciousnesses[character_name]

        prompt = f"""Oceń czy ta linia dialogowa jest psychologicznie autentyczna
dla postaci {character_name}.

PROFIL PSYCHOLOGICZNY:
- Osobowość: {json.dumps({k.value: v for k, v in consciousness.personality.items()}, ensure_ascii=False)}
- Wartości: {consciousness.values_hierarchy}
- Mechanizmy obronne: {[d.value for d in consciousness.preferred_defenses]}
- Styl przywiązania: {consciousness.attachment_style.value}
- Obecny stan emocjonalny: {consciousness.current_state.current_emotion.value if consciousness.current_state else 'unknown'}

KONTEKST SCENY:
{context}

LINIA DIALOGOWA:
"{dialogue_line}"

Oceń:
1. AUTENTYCZNOŚĆ (0.0-1.0): Czy to brzmi jak ta postać?
2. PROBLEMY: Lista ewentualnych niezgodności z profilem
3. SUGESTIE: Jak można poprawić dla większej autentyczności
4. UKRYTY TEKST: Co ta linia może ujawniać o wewnętrznym stanie postaci

Odpowiedz w JSON."""

        response = await self._get_llm("mid").chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    # =========================================================================
    # EMOTIONAL STATE MANAGEMENT
    # =========================================================================

    def update_emotional_state(
        self,
        character_name: str,
        emotion: EmotionalState,
        intensity: float,
        trigger: str
    ) -> None:
        """
        Ręcznie aktualizuje stan emocjonalny postaci.
        """
        if character_name not in self.consciousnesses:
            return

        consciousness = self.consciousnesses[character_name]

        if consciousness.current_state:
            consciousness.current_state.current_emotion = emotion
            consciousness.current_state.emotion_intensity = min(1.0, max(0.0, intensity))

    def get_consciousness(self, character_name: str) -> Optional[CharacterConsciousness]:
        """Pobiera świadomość postaci"""
        return self.consciousnesses.get(character_name)

    def get_all_characters(self) -> List[str]:
        """Zwraca listę wszystkich postaci z profilami"""
        return list(self.consciousnesses.keys())

    def export_consciousness(self, character_name: str) -> Optional[Dict[str, Any]]:
        """Eksportuje świadomość do słownika"""
        consciousness = self.consciousnesses.get(character_name)
        if consciousness:
            return consciousness.to_dict()
        return None


# =============================================================================
# SINGLETON
# =============================================================================

_consciousness_simulator: Optional[CharacterConsciousnessSimulator] = None

def get_consciousness_simulator() -> CharacterConsciousnessSimulator:
    """Get singleton instance of consciousness simulator"""
    global _consciousness_simulator
    if _consciousness_simulator is None:
        _consciousness_simulator = CharacterConsciousnessSimulator()
    return _consciousness_simulator
