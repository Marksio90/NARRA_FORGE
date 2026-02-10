"""
Real-time Style Adaptation Engine - NarraForge 3.0

System adaptacji stylu pisarskiego w czasie rzeczywistym:
- Analiza próbek stylowych (autorów, gatunków, epok)
- Ekstrakcja cech stylistycznych
- Adaptacja generowanego tekstu do zadanego stylu
- Spójność stylistyczna przez całą książkę
- Różne style dla różnych narratorów/POV
- Dynamiczna adaptacja do typu sceny

"Każde słowo brzmi jak autor, nie jak maszyna"
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import json
import re
import asyncio
import random
import math
from collections import Counter

from app.services.llm_service import get_llm_service


# =============================================================================
# ENUMS
# =============================================================================

class StyleDimension(Enum):
    """Wymiary stylu literackiego"""
    SENTENCE_LENGTH = "sentence_length"  # Długość zdań
    VOCABULARY_RICHNESS = "vocabulary_richness"  # Bogactwo słownictwa
    FORMALITY = "formality"  # Formalność
    IMAGERY_DENSITY = "imagery_density"  # Gęstość obrazowania
    DIALOGUE_RATIO = "dialogue_ratio"  # Stosunek dialogu do narracji
    DESCRIPTION_DETAIL = "description_detail"  # Szczegółowość opisów
    PACING = "pacing"  # Tempo narracji
    EMOTIONAL_INTENSITY = "emotional_intensity"  # Intensywność emocjonalna
    SHOWING_VS_TELLING = "showing_vs_telling"  # Show vs Tell
    METAPHOR_FREQUENCY = "metaphor_frequency"  # Częstość metafor
    SENTENCE_VARIETY = "sentence_variety"  # Różnorodność struktury zdań
    POV_DEPTH = "pov_depth"  # Głębokość POV


class SceneType(Enum):
    """Typy scen wymagające różnych stylów"""
    ACTION = "action"
    DIALOGUE = "dialogue"
    INTROSPECTION = "introspection"
    DESCRIPTION = "description"
    ROMANCE = "romance"
    SUSPENSE = "suspense"
    REVELATION = "revelation"
    TRANSITION = "transition"
    CLIMAX = "climax"
    RESOLUTION = "resolution"


class VoiceType(Enum):
    """Typy głosu narracyjnego"""
    FIRST_PERSON_INTIMATE = "first_person_intimate"
    FIRST_PERSON_UNRELIABLE = "first_person_unreliable"
    THIRD_PERSON_LIMITED = "third_person_limited"
    THIRD_PERSON_OMNISCIENT = "third_person_omniscient"
    THIRD_PERSON_OBJECTIVE = "third_person_objective"
    SECOND_PERSON = "second_person"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class StyleProfile:
    """Profil stylu literackiego"""
    name: str  # Nazwa profilu (np. "Stephen King Horror", "Jane Austen Romance")

    # Wymiary stylu (wartości 0-1)
    dimensions: Dict[StyleDimension, float] = field(default_factory=dict)

    # Charakterystyczne cechy
    signature_techniques: List[str] = field(default_factory=list)  # Charakterystyczne techniki
    favorite_sentence_openers: List[str] = field(default_factory=list)  # Ulubione początki zdań
    characteristic_phrases: List[str] = field(default_factory=list)  # Charakterystyczne frazy
    avoided_constructions: List[str] = field(default_factory=list)  # Unikane konstrukcje

    # Słownictwo
    vocabulary_preferences: Dict[str, List[str]] = field(default_factory=dict)  # Preferencje słownikowe
    word_frequency_patterns: Dict[str, float] = field(default_factory=dict)  # Wzorce częstości słów

    # Struktura
    average_sentence_length: float = 15.0  # Średnia długość zdania
    sentence_length_variance: float = 5.0  # Wariancja długości
    paragraph_length_preference: str = "medium"  # short, medium, long, varied
    chapter_structure: str = "traditional"  # traditional, vignette, fragmented

    # Narracja
    voice_type: VoiceType = VoiceType.THIRD_PERSON_LIMITED
    pov_character_bleed: float = 0.5  # Jak bardzo styl zmienia się z POV (0-1)

    # Adaptacje sceniczne
    scene_style_modifiers: Dict[SceneType, Dict[str, float]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "dimensions": {k.value: v for k, v in self.dimensions.items()},
            "signature_techniques": self.signature_techniques,
            "favorite_sentence_openers": self.favorite_sentence_openers,
            "characteristic_phrases": self.characteristic_phrases,
            "avoided_constructions": self.avoided_constructions,
            "vocabulary_preferences": self.vocabulary_preferences,
            "average_sentence_length": self.average_sentence_length,
            "sentence_length_variance": self.sentence_length_variance,
            "paragraph_length_preference": self.paragraph_length_preference,
            "chapter_structure": self.chapter_structure,
            "voice_type": self.voice_type.value,
            "pov_character_bleed": self.pov_character_bleed,
            "scene_style_modifiers": {
                k.value: v for k, v in self.scene_style_modifiers.items()
            }
        }


@dataclass
class StyleAnalysis:
    """Wynik analizy stylu tekstu"""
    dimension_scores: Dict[StyleDimension, float]
    detected_techniques: List[str]
    vocabulary_stats: Dict[str, Any]
    sentence_stats: Dict[str, Any]
    identified_patterns: List[str]
    style_consistency: float  # Jak spójny jest styl (0-1)
    readability_score: float  # Czytelność (0-1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension_scores": {k.value: v for k, v in self.dimension_scores.items()},
            "detected_techniques": self.detected_techniques,
            "vocabulary_stats": self.vocabulary_stats,
            "sentence_stats": self.sentence_stats,
            "identified_patterns": self.identified_patterns,
            "style_consistency": self.style_consistency,
            "readability_score": self.readability_score
        }


@dataclass
class StyleAdaptation:
    """Instrukcje adaptacji stylu"""
    target_profile: str
    current_scene_type: SceneType
    adaptations: List[str]  # Lista konkretnych zmian do wprowadzenia
    vocabulary_suggestions: Dict[str, List[str]]  # Zamienniki słów
    sentence_restructure_hints: List[str]  # Podpowiedzi do restrukturyzacji
    pacing_adjustment: str  # faster, slower, maintain
    imagery_additions: List[str]  # Sugestie dodania obrazowania

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_profile": self.target_profile,
            "current_scene_type": self.current_scene_type.value,
            "adaptations": self.adaptations,
            "vocabulary_suggestions": self.vocabulary_suggestions,
            "sentence_restructure_hints": self.sentence_restructure_hints,
            "pacing_adjustment": self.pacing_adjustment,
            "imagery_additions": self.imagery_additions
        }


@dataclass
class StyledText:
    """Tekst po adaptacji stylu"""
    original_text: str
    styled_text: str
    applied_adaptations: List[str]
    style_match_score: float  # Jak dobrze pasuje do profilu (0-1)
    changes_made: List[Dict[str, str]]  # Lista zmian

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_text": self.original_text,
            "styled_text": self.styled_text,
            "applied_adaptations": self.applied_adaptations,
            "style_match_score": self.style_match_score,
            "changes_made": self.changes_made
        }


# =============================================================================
# STYLOMETRY & FEW-SHOT INJECTION
# =============================================================================

@dataclass
class StylometricFingerprint:
    """
    Quantitative stylometric fingerprint extracted from text samples.

    Instead of describing style with adjectives ("write darkly"),
    this captures measurable statistical features of the author's writing
    that can be used for Few-Shot prompting.
    """
    # Sentence-level metrics
    avg_sentence_length: float = 0.0      # Words per sentence
    sentence_length_std: float = 0.0      # Standard deviation
    short_sentence_ratio: float = 0.0     # % sentences < 8 words
    long_sentence_ratio: float = 0.0      # % sentences > 25 words

    # Vocabulary metrics
    type_token_ratio: float = 0.0         # Unique words / total words
    avg_word_length: float = 0.0          # Characters per word
    hapax_legomena_ratio: float = 0.0     # Words appearing only once / total unique

    # Punctuation patterns
    comma_density: float = 0.0            # Commas per sentence
    semicolon_density: float = 0.0        # Semicolons per sentence
    dash_density: float = 0.0             # Dashes per sentence
    exclamation_ratio: float = 0.0        # ! endings / total sentences
    question_ratio: float = 0.0           # ? endings / total sentences
    ellipsis_density: float = 0.0         # ... per sentence

    # Dialogue patterns
    dialogue_ratio: float = 0.0           # % text in dialogue
    avg_dialogue_length: float = 0.0      # Words per dialogue turn

    # Paragraph patterns
    avg_paragraph_length: float = 0.0     # Sentences per paragraph
    paragraph_length_std: float = 0.0

    def to_prompt_description(self) -> str:
        """Convert fingerprint to natural-language style instructions."""
        parts = []

        # Sentence length
        if self.avg_sentence_length < 12:
            parts.append("Pisz zwięzłe, krótkie zdania (średnio 8-12 słów)")
        elif self.avg_sentence_length > 20:
            parts.append("Twórz rozbudowane, wielokrotnie złożone zdania (średnio 20+ słów)")
        else:
            parts.append(f"Utrzymuj zróżnicowaną długość zdań (średnio ~{self.avg_sentence_length:.0f} słów)")

        if self.short_sentence_ratio > 0.3:
            parts.append("Często używaj krótkich, urywanych zdań dla efektu")

        if self.sentence_length_std > 8:
            parts.append("Mieszaj bardzo krótkie zdania z długimi - duży kontrast rytmiczny")

        # Vocabulary
        if self.type_token_ratio > 0.65:
            parts.append("Używaj bogatego, zróżnicowanego słownictwa - unikaj powtórzeń")
        elif self.type_token_ratio < 0.45:
            parts.append("Celowo powtarzaj kluczowe słowa - prostota słownictwa")

        # Punctuation
        if self.dash_density > 0.3:
            parts.append("Często używaj myślników i pauz (—) w narracji")
        if self.ellipsis_density > 0.2:
            parts.append("Stosuj wielokropki (...) dla efektu zawieszenia")
        if self.semicolon_density > 0.15:
            parts.append("Łącz zdania średnikami zamiast kropek")

        # Dialogue
        if self.dialogue_ratio > 0.4:
            parts.append("Duży nacisk na dialogi - niech postacie mówią zamiast narracji")
        elif self.dialogue_ratio < 0.15:
            parts.append("Minimalizuj dialog - dominuje narracja i introspekcja")

        # Paragraphs
        if self.avg_paragraph_length < 3:
            parts.append("Krótkie akapity (1-3 zdania) - szybki, dynamiczny rytm")
        elif self.avg_paragraph_length > 6:
            parts.append("Długie, gęste akapity - medytacyjny, refleksyjny styl")

        return "\n".join(f"- {p}" for p in parts)


class StyleSampleBank:
    """
    Bank of author writing samples for Dynamic Few-Shot Injection.

    Instead of describing style with adjectives, stores actual text samples
    from the author and extracts random fragments for injection into prompts.

    This is the "Killer Feature" - the AI mimics the actual writing patterns
    rather than a caricature based on adjective descriptions.
    """

    def __init__(self):
        self._samples: Dict[str, List[str]] = {}  # profile_name -> list of text samples
        self._fingerprints: Dict[str, StylometricFingerprint] = {}

    def add_samples(self, profile_name: str, texts: List[str]):
        """Add writing samples for a profile."""
        if profile_name not in self._samples:
            self._samples[profile_name] = []
        self._samples[profile_name].extend(texts)
        # Recompute fingerprint when samples change
        self._fingerprints[profile_name] = self._compute_fingerprint(
            self._samples[profile_name]
        )

    def get_random_excerpts(
        self,
        profile_name: str,
        count: int = 3,
        min_words: int = 40,
        max_words: int = 200
    ) -> List[str]:
        """
        Extract random excerpts from stored samples for Few-Shot injection.

        Returns fragments of different lengths to show variety in the author's style.
        """
        samples = self._samples.get(profile_name, [])
        if not samples:
            return []

        # Collect all viable fragments from all samples
        all_fragments = []
        for sample in samples:
            paragraphs = [p.strip() for p in sample.split('\n\n') if p.strip()]
            for para in paragraphs:
                word_count = len(para.split())
                if min_words <= word_count <= max_words:
                    all_fragments.append(para)

            # Also extract sentence-level fragments for variety
            sentences = re.split(r'(?<=[.!?])\s+', sample)
            # Group consecutive sentences into fragments
            for i in range(0, len(sentences) - 2, 2):
                fragment = ' '.join(sentences[i:i+3])
                word_count = len(fragment.split())
                if min_words <= word_count <= max_words:
                    all_fragments.append(fragment)

        if not all_fragments:
            # Fallback: take first N chars of each sample
            for sample in samples:
                words = sample.split()[:max_words]
                if len(words) >= min_words:
                    all_fragments.append(' '.join(words))

        if not all_fragments:
            return []

        # Return random selection
        count = min(count, len(all_fragments))
        return random.sample(all_fragments, count)

    def get_fingerprint(self, profile_name: str) -> Optional[StylometricFingerprint]:
        """Get the stylometric fingerprint for a profile."""
        return self._fingerprints.get(profile_name)

    def build_few_shot_prompt(
        self,
        profile_name: str,
        scene_type: Optional[str] = None,
        num_excerpts: int = 3
    ) -> str:
        """
        Build a complete Few-Shot injection block for the generation prompt.

        Returns a prompt section that includes:
        1. Random author excerpts as examples
        2. Stylometric instructions derived from statistical analysis
        """
        excerpts = self.get_random_excerpts(profile_name, count=num_excerpts)
        fingerprint = self.get_fingerprint(profile_name)

        if not excerpts and not fingerprint:
            return ""

        parts = []
        parts.append("=" * 60)
        parts.append("STYL AUTORA - NAŚLADUJ PONIŻSZE WZORCE")
        parts.append("=" * 60)

        if excerpts:
            parts.append("\nPRZYKŁADY PISARSTWA AUTORA:")
            for i, excerpt in enumerate(excerpts, 1):
                parts.append(f"\n--- Przykład {i} ---")
                parts.append(excerpt)

        if fingerprint:
            parts.append("\nINSTRUKCJE STYLOMETRYCZNE (na podstawie analizy statystycznej):")
            parts.append(fingerprint.to_prompt_description())

        parts.append("\nKLUCZOWA ZASADA: Naśladuj długość zdań, użycie interpunkcji, ")
        parts.append("rytm dialogów i proporcje narracja/dialog z powyższych przykładów.")
        parts.append("NIE opisuj stylu - po prostu pisz w tym stylu.")
        parts.append("=" * 60)

        return "\n".join(parts)

    def _compute_fingerprint(self, texts: List[str]) -> StylometricFingerprint:
        """Compute stylometric fingerprint from text samples."""
        fp = StylometricFingerprint()
        if not texts:
            return fp

        all_text = "\n\n".join(texts)

        # Split into sentences
        sentences = re.split(r'[.!?]+', all_text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 3]

        if not sentences:
            return fp

        # Sentence lengths
        sentence_lengths = [len(s.split()) for s in sentences]
        fp.avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)
        if len(sentence_lengths) > 1:
            mean = fp.avg_sentence_length
            fp.sentence_length_std = math.sqrt(
                sum((l - mean) ** 2 for l in sentence_lengths) / (len(sentence_lengths) - 1)
            )

        fp.short_sentence_ratio = sum(1 for l in sentence_lengths if l < 8) / len(sentence_lengths)
        fp.long_sentence_ratio = sum(1 for l in sentence_lengths if l > 25) / len(sentence_lengths)

        # Vocabulary
        words = re.findall(r'\b\w+\b', all_text.lower())
        if words:
            unique_words = set(words)
            fp.type_token_ratio = len(unique_words) / len(words)
            fp.avg_word_length = sum(len(w) for w in words) / len(words)

            word_counts = Counter(words)
            hapax = sum(1 for count in word_counts.values() if count == 1)
            fp.hapax_legomena_ratio = hapax / len(unique_words) if unique_words else 0

        # Punctuation density (per sentence)
        num_sentences = len(sentences)
        fp.comma_density = all_text.count(',') / num_sentences
        fp.semicolon_density = all_text.count(';') / num_sentences
        fp.dash_density = (all_text.count('—') + all_text.count('–') + all_text.count(' - ')) / num_sentences
        fp.ellipsis_density = all_text.count('...') / num_sentences

        # Sentence endings
        all_endings = re.findall(r'[.!?]+', all_text)
        if all_endings:
            fp.exclamation_ratio = sum(1 for e in all_endings if '!' in e) / len(all_endings)
            fp.question_ratio = sum(1 for e in all_endings if '?' in e) / len(all_endings)

        # Dialogue detection (text between quotes)
        dialogue_matches = re.findall(r'[""„]([^""„"]+)["""]', all_text)
        total_words = len(words)
        if total_words > 0 and dialogue_matches:
            dialogue_words = sum(len(d.split()) for d in dialogue_matches)
            fp.dialogue_ratio = dialogue_words / total_words
            fp.avg_dialogue_length = dialogue_words / len(dialogue_matches) if dialogue_matches else 0

        # Paragraph patterns
        paragraphs = [p.strip() for p in all_text.split('\n\n') if p.strip()]
        if paragraphs:
            para_sentence_counts = []
            for para in paragraphs:
                para_sents = re.split(r'[.!?]+', para)
                para_sents = [s for s in para_sents if s.strip()]
                para_sentence_counts.append(len(para_sents))

            if para_sentence_counts:
                fp.avg_paragraph_length = sum(para_sentence_counts) / len(para_sentence_counts)
                if len(para_sentence_counts) > 1:
                    mean = fp.avg_paragraph_length
                    fp.paragraph_length_std = math.sqrt(
                        sum((l - mean) ** 2 for l in para_sentence_counts) / (len(para_sentence_counts) - 1)
                    )

        return fp


# =============================================================================
# STYLE ADAPTATION ENGINE
# =============================================================================

class StyleAdaptationEngine:
    """
    Silnik adaptacji stylu w czasie rzeczywistym.

    Funkcje:
    - Analiza próbek stylowych
    - Tworzenie profili stylu
    - Adaptacja tekstu do profilu
    - Dynamiczna zmiana stylu na podstawie sceny
    - Utrzymanie spójności przez całą książkę
    """

    def __init__(self):
        self.llm_service = get_llm_service()
        self.style_profiles: Dict[str, StyleProfile] = {}
        self.active_profile: Optional[str] = None
        self.sample_bank = StyleSampleBank()
        self._initialize_default_profiles()

    def _get_llm(self, tier: str = "mid"):
        """Get appropriate LLM based on tier"""
        return self.llm_service.get_client(tier)

    def _initialize_default_profiles(self):
        """Inicjalizacja domyślnych profili stylowych"""

        # Profil: Polski Thriller
        thriller_profile = StyleProfile(
            name="polish_thriller",
            dimensions={
                StyleDimension.SENTENCE_LENGTH: 0.4,  # Krótsze zdania
                StyleDimension.VOCABULARY_RICHNESS: 0.6,
                StyleDimension.FORMALITY: 0.5,
                StyleDimension.IMAGERY_DENSITY: 0.6,
                StyleDimension.DIALOGUE_RATIO: 0.4,
                StyleDimension.DESCRIPTION_DETAIL: 0.5,
                StyleDimension.PACING: 0.8,  # Szybkie tempo
                StyleDimension.EMOTIONAL_INTENSITY: 0.7,
                StyleDimension.SHOWING_VS_TELLING: 0.8,
                StyleDimension.METAPHOR_FREQUENCY: 0.4,
                StyleDimension.SENTENCE_VARIETY: 0.7,
                StyleDimension.POV_DEPTH: 0.7
            },
            signature_techniques=[
                "cliffhangery na końcu rozdziałów",
                "krótkie, urywane zdania w scenach akcji",
                "wewnętrzny monolog w momentach napięcia",
                "red herring'i w dialogach"
            ],
            favorite_sentence_openers=["Nagle", "Wtedy", "Przez chwilę", "Coś"],
            characteristic_phrases=["zimny dreszcz", "serce zabiło szybciej", "cisza była nie do zniesienia"],
            avoided_constructions=["można by powiedzieć, że", "jak wiadomo", "oczywiście"],
            average_sentence_length=12.0,
            sentence_length_variance=8.0,
            paragraph_length_preference="varied",
            voice_type=VoiceType.THIRD_PERSON_LIMITED,
            scene_style_modifiers={
                SceneType.ACTION: {"pacing": 0.95, "sentence_length": 0.3},
                SceneType.SUSPENSE: {"pacing": 0.6, "emotional_intensity": 0.9},
                SceneType.DIALOGUE: {"pacing": 0.7, "showing_vs_telling": 0.9}
            }
        )
        self.style_profiles["polish_thriller"] = thriller_profile

        # Profil: Polski Romans
        romance_profile = StyleProfile(
            name="polish_romance",
            dimensions={
                StyleDimension.SENTENCE_LENGTH: 0.6,
                StyleDimension.VOCABULARY_RICHNESS: 0.7,
                StyleDimension.FORMALITY: 0.5,
                StyleDimension.IMAGERY_DENSITY: 0.8,
                StyleDimension.DIALOGUE_RATIO: 0.5,
                StyleDimension.DESCRIPTION_DETAIL: 0.7,
                StyleDimension.PACING: 0.5,
                StyleDimension.EMOTIONAL_INTENSITY: 0.8,
                StyleDimension.SHOWING_VS_TELLING: 0.7,
                StyleDimension.METAPHOR_FREQUENCY: 0.7,
                StyleDimension.SENTENCE_VARIETY: 0.6,
                StyleDimension.POV_DEPTH: 0.8
            },
            signature_techniques=[
                "zmysłowe opisy",
                "napięcie seksualne w dialogach",
                "wewnętrzne rozterki bohaterki",
                "momenty niemal-pocałunku"
            ],
            favorite_sentence_openers=["Jego", "Jej", "Między nimi", "Spojrzała"],
            characteristic_phrases=["serce zabiło mocniej", "gorący rumieniec", "elektryzujące napięcie"],
            average_sentence_length=18.0,
            voice_type=VoiceType.THIRD_PERSON_LIMITED,
            pov_character_bleed=0.7,
            scene_style_modifiers={
                SceneType.ROMANCE: {"emotional_intensity": 0.95, "imagery_density": 0.9},
                SceneType.DIALOGUE: {"showing_vs_telling": 0.85}
            }
        )
        self.style_profiles["polish_romance"] = romance_profile

        # Profil: Fantasy Epicki
        fantasy_profile = StyleProfile(
            name="epic_fantasy",
            dimensions={
                StyleDimension.SENTENCE_LENGTH: 0.7,
                StyleDimension.VOCABULARY_RICHNESS: 0.9,
                StyleDimension.FORMALITY: 0.7,
                StyleDimension.IMAGERY_DENSITY: 0.9,
                StyleDimension.DIALOGUE_RATIO: 0.35,
                StyleDimension.DESCRIPTION_DETAIL: 0.85,
                StyleDimension.PACING: 0.5,
                StyleDimension.EMOTIONAL_INTENSITY: 0.7,
                StyleDimension.SHOWING_VS_TELLING: 0.6,
                StyleDimension.METAPHOR_FREQUENCY: 0.8,
                StyleDimension.SENTENCE_VARIETY: 0.7,
                StyleDimension.POV_DEPTH: 0.6
            },
            signature_techniques=[
                "bogata mitologia w dialogach",
                "opisy krajobrazów",
                "archaiczne zwroty w mowie postaci",
                "prorocze wstawki"
            ],
            favorite_sentence_openers=["Przed wiekami", "W mroku", "Legenda głosi"],
            average_sentence_length=22.0,
            paragraph_length_preference="long",
            voice_type=VoiceType.THIRD_PERSON_OMNISCIENT,
            scene_style_modifiers={
                SceneType.ACTION: {"pacing": 0.75, "sentence_length": 0.5},
                SceneType.DESCRIPTION: {"imagery_density": 0.95, "vocabulary_richness": 0.95}
            }
        )
        self.style_profiles["epic_fantasy"] = fantasy_profile

        # Profil: Współczesna Proza Literacka
        literary_profile = StyleProfile(
            name="literary_fiction",
            dimensions={
                StyleDimension.SENTENCE_LENGTH: 0.6,
                StyleDimension.VOCABULARY_RICHNESS: 0.85,
                StyleDimension.FORMALITY: 0.6,
                StyleDimension.IMAGERY_DENSITY: 0.75,
                StyleDimension.DIALOGUE_RATIO: 0.4,
                StyleDimension.DESCRIPTION_DETAIL: 0.7,
                StyleDimension.PACING: 0.45,
                StyleDimension.EMOTIONAL_INTENSITY: 0.7,
                StyleDimension.SHOWING_VS_TELLING: 0.85,
                StyleDimension.METAPHOR_FREQUENCY: 0.75,
                StyleDimension.SENTENCE_VARIETY: 0.85,
                StyleDimension.POV_DEPTH: 0.9
            },
            signature_techniques=[
                "głęboka introspekcja",
                "wieloznaczność",
                "symbolika przedmiotów",
                "nielinearna narracja"
            ],
            average_sentence_length=17.0,
            sentence_length_variance=10.0,
            paragraph_length_preference="varied",
            voice_type=VoiceType.FIRST_PERSON_INTIMATE,
            scene_style_modifiers={
                SceneType.INTROSPECTION: {"pov_depth": 0.95, "showing_vs_telling": 0.9}
            }
        )
        self.style_profiles["literary_fiction"] = literary_profile

    # =========================================================================
    # STYLE ANALYSIS
    # =========================================================================

    async def analyze_text_style(self, text: str) -> StyleAnalysis:
        """
        Analizuje styl podanego tekstu.
        """
        # Basic statistical analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        words = text.split()
        unique_words = set(w.lower().strip('.,!?;:') for w in words)

        # Sentence length statistics
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0

        # Use LLM for deeper analysis
        prompt = f"""Przeanalizuj styl literacki poniższego tekstu.

TEKST:
{text[:3000]}

Oceń następujące wymiary (skala 0.0-1.0):
1. sentence_length - krótkie (0) vs długie (1) zdania
2. vocabulary_richness - prosty (0) vs bogaty (1) słownik
3. formality - potoczny (0) vs formalny (1)
4. imagery_density - mało (0) vs dużo (1) obrazowania
5. dialogue_ratio - mało (0) vs dużo (1) dialogu
6. description_detail - ogólnikowe (0) vs szczegółowe (1)
7. pacing - wolne (0) vs szybkie (1) tempo
8. emotional_intensity - chłodne (0) vs intensywne (1)
9. showing_vs_telling - telling (0) vs showing (1)
10. metaphor_frequency - rzadkie (0) vs częste (1) metafory
11. sentence_variety - monotonne (0) vs zróżnicowane (1)
12. pov_depth - płytki (0) vs głęboki (1) POV

Dodatkowo zidentyfikuj:
- detected_techniques: lista wykrytych technik narracyjnych
- identified_patterns: powtarzające się wzorce
- style_consistency: spójność stylu (0-1)
- readability_score: czytelność (0-1)

Odpowiedz w JSON."""

        response = await self._get_llm("mid").chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            response_format={"type": "json_object"}
        )

        analysis_data = json.loads(response.choices[0].message.content)

        # Build dimension scores
        dimension_scores = {}
        for dim in StyleDimension:
            if dim.value in analysis_data:
                dimension_scores[dim] = float(analysis_data[dim.value])
            else:
                dimension_scores[dim] = 0.5

        return StyleAnalysis(
            dimension_scores=dimension_scores,
            detected_techniques=analysis_data.get("detected_techniques", []),
            vocabulary_stats={
                "total_words": len(words),
                "unique_words": len(unique_words),
                "vocabulary_ratio": len(unique_words) / len(words) if words else 0
            },
            sentence_stats={
                "total_sentences": len(sentences),
                "average_length": avg_sentence_length,
                "length_variance": sum((l - avg_sentence_length) ** 2 for l in sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
            },
            identified_patterns=analysis_data.get("identified_patterns", []),
            style_consistency=float(analysis_data.get("style_consistency", 0.5)),
            readability_score=float(analysis_data.get("readability_score", 0.5))
        )

    async def create_profile_from_samples(
        self,
        profile_name: str,
        sample_texts: List[str],
        author_name: Optional[str] = None,
        genre: Optional[str] = None
    ) -> StyleProfile:
        """
        Tworzy profil stylu na podstawie próbek tekstu.
        """
        # Analyze all samples
        analyses = []
        for sample in sample_texts:
            analysis = await self.analyze_text_style(sample)
            analyses.append(analysis)

        # Average dimensions
        avg_dimensions = {}
        for dim in StyleDimension:
            scores = [a.dimension_scores.get(dim, 0.5) for a in analyses]
            avg_dimensions[dim] = sum(scores) / len(scores) if scores else 0.5

        # Collect all techniques and patterns
        all_techniques = []
        all_patterns = []
        for a in analyses:
            all_techniques.extend(a.detected_techniques)
            all_patterns.extend(a.identified_patterns)

        # Get most common
        technique_counter = Counter(all_techniques)
        pattern_counter = Counter(all_patterns)

        # Use LLM to extract characteristic phrases and constructions
        combined_samples = "\n\n---\n\n".join(sample[:1500] for sample in sample_texts[:3])

        prompt = f"""Na podstawie próbek tekstu zidentyfikuj charakterystyczne cechy stylu.

PRÓBKI:
{combined_samples}

{'AUTOR: ' + author_name if author_name else ''}
{'GATUNEK: ' + genre if genre else ''}

Zidentyfikuj:
1. signature_techniques: 4-6 charakterystycznych technik narracyjnych
2. favorite_sentence_openers: 5-7 ulubionych początków zdań
3. characteristic_phrases: 5-8 charakterystycznych fraz/zwrotów
4. avoided_constructions: 3-5 konstrukcji których autor unika
5. vocabulary_preferences: słownik preferencji (emotion_words, action_words, etc.)
6. voice_type: first_person_intimate, first_person_unreliable, third_person_limited,
   third_person_omniscient, third_person_objective, second_person
7. paragraph_length_preference: short, medium, long, varied
8. chapter_structure: traditional, vignette, fragmented

Odpowiedz w JSON."""

        response = await self._get_llm("high").chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )

        style_data = json.loads(response.choices[0].message.content)

        # Parse voice type
        try:
            voice_type = VoiceType(style_data.get("voice_type", "third_person_limited"))
        except ValueError:
            voice_type = VoiceType.THIRD_PERSON_LIMITED

        # Calculate sentence stats
        all_sentences = []
        for sample in sample_texts:
            sentences = re.split(r'[.!?]+', sample)
            all_sentences.extend([s.strip() for s in sentences if s.strip()])

        sentence_lengths = [len(s.split()) for s in all_sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 15
        variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(sentence_lengths) if sentence_lengths else 5

        profile = StyleProfile(
            name=profile_name,
            dimensions=avg_dimensions,
            signature_techniques=style_data.get("signature_techniques", [t for t, _ in technique_counter.most_common(6)]),
            favorite_sentence_openers=style_data.get("favorite_sentence_openers", []),
            characteristic_phrases=style_data.get("characteristic_phrases", []),
            avoided_constructions=style_data.get("avoided_constructions", []),
            vocabulary_preferences=style_data.get("vocabulary_preferences", {}),
            average_sentence_length=avg_length,
            sentence_length_variance=variance ** 0.5,
            paragraph_length_preference=style_data.get("paragraph_length_preference", "medium"),
            voice_type=voice_type
        )

        self.style_profiles[profile_name] = profile
        return profile

    # =========================================================================
    # STYLE ADAPTATION
    # =========================================================================

    async def adapt_text_to_style(
        self,
        text: str,
        profile_name: str,
        scene_type: SceneType = SceneType.DIALOGUE,
        preserve_meaning: bool = True
    ) -> StyledText:
        """
        Adaptuje tekst do zadanego profilu stylu.
        """
        if profile_name not in self.style_profiles:
            raise ValueError(f"Nieznany profil stylu: {profile_name}")

        profile = self.style_profiles[profile_name]

        # Get scene modifiers
        scene_modifiers = profile.scene_style_modifiers.get(scene_type, {})

        # Build effective dimensions
        effective_dims = {}
        for dim, value in profile.dimensions.items():
            modifier = scene_modifiers.get(dim.value, 1.0)
            effective_dims[dim.value] = min(1.0, value * modifier) if modifier > 1.0 else value * modifier

        prompt = f"""Przepisz poniższy tekst, adaptując go do zadanego stylu.

ORYGINALNY TEKST:
{text}

PROFIL STYLU "{profile.name}":
- Wymiary: {json.dumps(effective_dims, ensure_ascii=False)}
- Techniki charakterystyczne: {profile.signature_techniques}
- Ulubione początki zdań: {profile.favorite_sentence_openers}
- Charakterystyczne frazy: {profile.characteristic_phrases}
- Unikane konstrukcje: {profile.avoided_constructions}
- Średnia długość zdania: {profile.average_sentence_length} słów
- Typ głosu: {profile.voice_type.value}

TYP SCENY: {scene_type.value}

INSTRUKCJE:
1. {'Zachowaj dokładne znaczenie i informacje' if preserve_meaning else 'Możesz swobodnie modyfikować'}
2. Dostosuj długość zdań do profilu
3. Użyj charakterystycznych technik i fraz tam, gdzie pasują naturalnie
4. Unikaj konstrukcji z listy unikanych
5. Dostosuj tempo do typu sceny
6. Zachowaj naturalność - nie wymuszaj stylu

Zwróć JSON z:
- styled_text: przepisany tekst
- applied_adaptations: lista zastosowanych zmian
- style_match_score: ocena dopasowania do stylu (0-1)
- changes_made: lista zmian [{{original, changed, reason}}]"""

        response = await self._get_llm("high").chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        return StyledText(
            original_text=text,
            styled_text=result.get("styled_text", text),
            applied_adaptations=result.get("applied_adaptations", []),
            style_match_score=float(result.get("style_match_score", 0.5)),
            changes_made=result.get("changes_made", [])
        )

    async def get_style_adaptation_instructions(
        self,
        profile_name: str,
        scene_type: SceneType,
        current_text_analysis: Optional[StyleAnalysis] = None
    ) -> StyleAdaptation:
        """
        Zwraca instrukcje adaptacji stylu dla generatora tekstu.
        """
        if profile_name not in self.style_profiles:
            raise ValueError(f"Nieznany profil stylu: {profile_name}")

        profile = self.style_profiles[profile_name]

        # Calculate needed adaptations
        adaptations = []
        vocabulary_suggestions = {}

        if current_text_analysis:
            for dim, target_value in profile.dimensions.items():
                current_value = current_text_analysis.dimension_scores.get(dim, 0.5)
                diff = target_value - current_value

                if abs(diff) > 0.2:
                    direction = "zwiększyć" if diff > 0 else "zmniejszyć"
                    adaptations.append(f"{direction} {dim.value}")

        # Scene-specific instructions
        if scene_type == SceneType.ACTION:
            adaptations.extend([
                "Skróć zdania",
                "Użyj czasowników akcji",
                "Minimalizuj przymiotniki"
            ])
        elif scene_type == SceneType.INTROSPECTION:
            adaptations.extend([
                "Pogłęb POV",
                "Dodaj wewnętrzne rozterki",
                "Użyj strumienia świadomości"
            ])
        elif scene_type == SceneType.ROMANCE:
            adaptations.extend([
                "Zwiększ zmysłowość opisów",
                "Buduj napięcie między postaciami",
                "Wykorzystaj opisy ciała i gestów"
            ])
        elif scene_type == SceneType.SUSPENSE:
            adaptations.extend([
                "Stopniuj napięcie",
                "Opóźniaj ujawnienia",
                "Użyj krótkich, urywanych zdań"
            ])

        # Pacing adjustment
        scene_modifiers = profile.scene_style_modifiers.get(scene_type, {})
        pacing_mod = scene_modifiers.get("pacing", profile.dimensions.get(StyleDimension.PACING, 0.5))
        if pacing_mod > 0.7:
            pacing_adjustment = "faster"
        elif pacing_mod < 0.4:
            pacing_adjustment = "slower"
        else:
            pacing_adjustment = "maintain"

        return StyleAdaptation(
            target_profile=profile_name,
            current_scene_type=scene_type,
            adaptations=adaptations,
            vocabulary_suggestions=vocabulary_suggestions,
            sentence_restructure_hints=[
                f"Celuj w średnio {profile.average_sentence_length} słów na zdanie",
                f"Używaj technik: {', '.join(profile.signature_techniques[:3])}"
            ],
            pacing_adjustment=pacing_adjustment,
            imagery_additions=profile.characteristic_phrases[:3] if scene_type in [SceneType.DESCRIPTION, SceneType.ROMANCE] else []
        )

    # =========================================================================
    # DYNAMIC FEW-SHOT STYLE INJECTION
    # =========================================================================

    async def ingest_author_samples(
        self,
        profile_name: str,
        sample_texts: List[str],
        create_profile: bool = True
    ) -> Dict[str, Any]:
        """
        Ingest author writing samples for Few-Shot style injection.

        This is the key method for the "Killer Feature": instead of describing
        style with adjectives, the system learns from actual writing samples
        and injects random excerpts into generation prompts.

        Args:
            profile_name: Name for this style profile
            sample_texts: List of text samples from the author (e.g., 3-10 pages)
            create_profile: Also create/update a StyleProfile from the samples

        Returns:
            Dict with fingerprint data and sample statistics
        """
        # Store samples in the bank
        self.sample_bank.add_samples(profile_name, sample_texts)

        # Get computed fingerprint
        fingerprint = self.sample_bank.get_fingerprint(profile_name)

        # Optionally create a full StyleProfile from samples
        if create_profile and profile_name not in self.style_profiles:
            await self.create_profile_from_samples(
                profile_name=profile_name,
                sample_texts=sample_texts
            )

        total_words = sum(len(t.split()) for t in sample_texts)

        return {
            "profile_name": profile_name,
            "samples_ingested": len(sample_texts),
            "total_words": total_words,
            "fingerprint": {
                "avg_sentence_length": fingerprint.avg_sentence_length,
                "sentence_length_std": fingerprint.sentence_length_std,
                "type_token_ratio": fingerprint.type_token_ratio,
                "dialogue_ratio": fingerprint.dialogue_ratio,
                "short_sentence_ratio": fingerprint.short_sentence_ratio,
                "long_sentence_ratio": fingerprint.long_sentence_ratio,
                "comma_density": fingerprint.comma_density,
                "dash_density": fingerprint.dash_density,
                "avg_paragraph_length": fingerprint.avg_paragraph_length,
            } if fingerprint else {},
            "style_instructions_preview": fingerprint.to_prompt_description() if fingerprint else ""
        }

    def get_generation_style_block(
        self,
        profile_name: str,
        scene_type: Optional[SceneType] = None,
        num_excerpts: int = 3
    ) -> str:
        """
        Get the complete style injection block for a generation prompt.

        This should be appended to the system_prompt or inserted before the
        generation instruction. It includes:
        1. Random author writing excerpts (Few-Shot examples)
        2. Statistical style instructions (stylometry)
        3. Scene-type-specific adjustments

        Returns:
            String block to inject into the generation prompt
        """
        parts = []

        # Few-Shot block from sample bank
        few_shot_block = self.sample_bank.build_few_shot_prompt(
            profile_name=profile_name,
            scene_type=scene_type.value if scene_type else None,
            num_excerpts=num_excerpts
        )

        if few_shot_block:
            parts.append(few_shot_block)

        # Add scene-type modifiers from the StyleProfile if available
        profile = self.style_profiles.get(profile_name)
        if profile and scene_type:
            scene_modifiers = profile.scene_style_modifiers.get(scene_type, {})
            if scene_modifiers:
                modifier_lines = []
                for dim_name, value in scene_modifiers.items():
                    if value > 0.8:
                        modifier_lines.append(f"- MAKSYMALIZUJ: {dim_name}")
                    elif value < 0.3:
                        modifier_lines.append(f"- MINIMALIZUJ: {dim_name}")

                if modifier_lines:
                    parts.append(f"\nDOSTOSOWANIA DLA SCENY TYPU '{scene_type.value.upper()}':")
                    parts.extend(modifier_lines)

            # Add profile-specific techniques
            if profile.signature_techniques:
                parts.append("\nTECHNIKI DO ZASTOSOWANIA:")
                for tech in profile.signature_techniques[:4]:
                    parts.append(f"- {tech}")

            # Add avoided constructions
            if profile.avoided_constructions:
                parts.append("\nUNIKAJ:")
                for avoid in profile.avoided_constructions[:3]:
                    parts.append(f"- {avoid}")

        return "\n".join(parts)

    # =========================================================================
    # CONSISTENCY CHECKING
    # =========================================================================

    async def check_style_consistency(
        self,
        texts: List[str],
        profile_name: str
    ) -> Dict[str, Any]:
        """
        Sprawdza spójność stylu w wielu fragmentach tekstu.
        """
        if profile_name not in self.style_profiles:
            raise ValueError(f"Nieznany profil stylu: {profile_name}")

        profile = self.style_profiles[profile_name]

        # Analyze each text
        analyses = []
        for text in texts:
            analysis = await self.analyze_text_style(text)
            analyses.append(analysis)

        # Calculate consistency across texts
        consistency_scores = {}
        for dim in StyleDimension:
            values = [a.dimension_scores.get(dim, 0.5) for a in analyses]
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            consistency_scores[dim.value] = 1.0 - min(1.0, variance)  # Higher = more consistent

        # Check deviation from profile
        deviation_scores = {}
        for dim in StyleDimension:
            target = profile.dimensions.get(dim, 0.5)
            values = [a.dimension_scores.get(dim, 0.5) for a in analyses]
            mean = sum(values) / len(values)
            deviation_scores[dim.value] = 1.0 - abs(target - mean)

        overall_consistency = sum(consistency_scores.values()) / len(consistency_scores)
        overall_match = sum(deviation_scores.values()) / len(deviation_scores)

        # Identify problematic areas
        issues = []
        for dim_name, score in consistency_scores.items():
            if score < 0.7:
                issues.append(f"Niespójna {dim_name}: {score:.2f}")
        for dim_name, score in deviation_scores.items():
            if score < 0.6:
                issues.append(f"Odchylenie od profilu w {dim_name}: {score:.2f}")

        return {
            "overall_consistency": overall_consistency,
            "profile_match": overall_match,
            "dimension_consistency": consistency_scores,
            "profile_deviation": deviation_scores,
            "issues": issues,
            "recommendation": "Dobre" if overall_consistency > 0.7 and overall_match > 0.6 else "Wymaga poprawy"
        }

    # =========================================================================
    # PROFILE MANAGEMENT
    # =========================================================================

    def set_active_profile(self, profile_name: str) -> bool:
        """Ustawia aktywny profil stylu"""
        if profile_name in self.style_profiles:
            self.active_profile = profile_name
            return True
        return False

    def get_profile(self, profile_name: str) -> Optional[StyleProfile]:
        """Pobiera profil stylu"""
        return self.style_profiles.get(profile_name)

    def list_profiles(self) -> List[str]:
        """Lista dostępnych profili"""
        return list(self.style_profiles.keys())

    def export_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Eksportuje profil do słownika"""
        profile = self.style_profiles.get(profile_name)
        if profile:
            return profile.to_dict()
        return None


# =============================================================================
# SINGLETON
# =============================================================================

_style_engine: Optional[StyleAdaptationEngine] = None

def get_style_adaptation_engine() -> StyleAdaptationEngine:
    """Get singleton instance of style adaptation engine"""
    global _style_engine
    if _style_engine is None:
        _style_engine = StyleAdaptationEngine()
    return _style_engine
