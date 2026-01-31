"""
Multi-Language Generation System - NarraForge 3.0 Phase 4

Advanced system for generating and translating narrative content
across multiple languages while preserving literary quality,
cultural nuances, and stylistic consistency.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class Language(Enum):
    """Supported languages"""
    POLISH = "pl"
    ENGLISH = "en"
    GERMAN = "de"
    FRENCH = "fr"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DUTCH = "nl"
    RUSSIAN = "ru"
    UKRAINIAN = "uk"
    CZECH = "cs"
    JAPANESE = "ja"
    CHINESE = "zh"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"
    SWEDISH = "sv"
    NORWEGIAN = "no"
    DANISH = "da"
    FINNISH = "fi"


class TranslationMode(Enum):
    """Translation approach modes"""
    LITERAL = "literal"              # Close to source
    LITERARY = "literary"            # Preserve literary quality
    LOCALIZED = "localized"          # Adapt to target culture
    TRANSCREATION = "transcreation"  # Creative adaptation


class ContentType(Enum):
    """Types of content for translation"""
    NARRATIVE = "narrative"
    DIALOGUE = "dialogue"
    DESCRIPTION = "description"
    INTERNAL_MONOLOGUE = "internal_monologue"
    POETRY = "poetry"
    TITLE = "title"
    CHAPTER_TITLE = "chapter_title"


class QualityLevel(Enum):
    """Translation quality levels"""
    DRAFT = "draft"
    STANDARD = "standard"
    PREMIUM = "premium"
    LITERARY = "literary"


class GrammaticalFeature(Enum):
    """Grammatical features that vary by language"""
    GENDER = "gender"
    FORMALITY = "formality"
    PLURALITY = "plurality"
    TENSE = "tense"
    ASPECT = "aspect"
    HONORIFICS = "honorifics"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class LanguageProfile:
    """Profile for a language"""
    code: str
    name: str
    native_name: str
    script: str
    direction: str  # "ltr" or "rtl"
    grammatical_features: List[GrammaticalFeature]
    formality_levels: int
    has_gender: bool
    has_honorifics: bool
    avg_word_expansion: float  # vs English
    special_characters: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "native_name": self.native_name,
            "script": self.script,
            "direction": self.direction,
            "grammatical_features": [f.value for f in self.grammatical_features],
            "formality_levels": self.formality_levels,
            "has_gender": self.has_gender,
            "has_honorifics": self.has_honorifics,
            "avg_word_expansion": self.avg_word_expansion,
            "special_characters": self.special_characters
        }


@dataclass
class TranslationSegment:
    """A segment of translated text"""
    segment_id: str
    source_text: str
    translated_text: str
    content_type: ContentType
    confidence: float
    alternatives: List[str]
    notes: str
    requires_review: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "source_text": self.source_text,
            "translated_text": self.translated_text,
            "content_type": self.content_type.value,
            "confidence": self.confidence,
            "alternatives": self.alternatives,
            "notes": self.notes,
            "requires_review": self.requires_review
        }


@dataclass
class TranslationMemory:
    """Translation memory entry"""
    memory_id: str
    source_language: Language
    target_language: Language
    source_text: str
    translated_text: str
    context: str
    domain: str  # genre/topic
    usage_count: int
    last_used: datetime
    approved: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "source_language": self.source_language.value,
            "target_language": self.target_language.value,
            "source_text": self.source_text,
            "translated_text": self.translated_text,
            "context": self.context,
            "domain": self.domain,
            "usage_count": self.usage_count,
            "last_used": self.last_used.isoformat(),
            "approved": self.approved
        }


@dataclass
class Glossary:
    """Translation glossary"""
    glossary_id: str
    name: str
    source_language: Language
    target_language: Language
    domain: str
    entries: Dict[str, str]  # source -> target
    notes: Dict[str, str]  # term -> note
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "glossary_id": self.glossary_id,
            "name": self.name,
            "source_language": self.source_language.value,
            "target_language": self.target_language.value,
            "domain": self.domain,
            "entries": self.entries,
            "notes": self.notes,
            "entry_count": len(self.entries),
            "created_at": self.created_at.isoformat()
        }


@dataclass
class CharacterNameMapping:
    """Mapping of character names across languages"""
    character_id: str
    original_name: str
    translations: Dict[str, str]  # language code -> translated name
    pronunciation_guides: Dict[str, str]
    cultural_notes: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "original_name": self.original_name,
            "translations": self.translations,
            "pronunciation_guides": self.pronunciation_guides,
            "cultural_notes": self.cultural_notes
        }


@dataclass
class ChapterTranslation:
    """Translation of a chapter"""
    chapter_number: int
    source_language: Language
    target_language: Language
    segments: List[TranslationSegment]
    word_count_source: int
    word_count_target: int
    quality_score: float
    review_status: str
    translator_notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter_number": self.chapter_number,
            "source_language": self.source_language.value,
            "target_language": self.target_language.value,
            "segments": [s.to_dict() for s in self.segments],
            "word_count_source": self.word_count_source,
            "word_count_target": self.word_count_target,
            "expansion_ratio": self.word_count_target / max(self.word_count_source, 1),
            "quality_score": self.quality_score,
            "review_status": self.review_status,
            "translator_notes": self.translator_notes
        }


@dataclass
class TranslationProject:
    """A full translation project"""
    project_id: str
    book_id: str
    source_language: Language
    target_languages: List[Language]
    translation_mode: TranslationMode
    quality_level: QualityLevel
    glossaries: List[str]  # Glossary IDs
    character_mappings: List[CharacterNameMapping]
    chapter_translations: Dict[str, List[ChapterTranslation]]  # lang -> chapters
    progress: Dict[str, float]  # lang -> progress percentage
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "book_id": self.book_id,
            "source_language": self.source_language.value,
            "target_languages": [l.value for l in self.target_languages],
            "translation_mode": self.translation_mode.value,
            "quality_level": self.quality_level.value,
            "glossaries": self.glossaries,
            "character_mappings": [m.to_dict() for m in self.character_mappings],
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class GenerationConfig:
    """Configuration for multi-language generation"""
    primary_language: Language
    additional_languages: List[Language]
    sync_generation: bool  # Generate all languages simultaneously
    auto_glossary: bool
    preserve_formatting: bool
    cultural_adaptation_level: str  # "none", "light", "full"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_language": self.primary_language.value,
            "additional_languages": [l.value for l in self.additional_languages],
            "sync_generation": self.sync_generation,
            "auto_glossary": self.auto_glossary,
            "preserve_formatting": self.preserve_formatting,
            "cultural_adaptation_level": self.cultural_adaptation_level
        }


# =============================================================================
# LANGUAGE PROFILES DATABASE
# =============================================================================

LANGUAGE_PROFILES = {
    Language.POLISH: LanguageProfile(
        code="pl",
        name="Polish",
        native_name="Polski",
        script="Latin",
        direction="ltr",
        grammatical_features=[GrammaticalFeature.GENDER, GrammaticalFeature.FORMALITY],
        formality_levels=2,
        has_gender=True,
        has_honorifics=False,
        avg_word_expansion=1.1,
        special_characters=["ą", "ć", "ę", "ł", "ń", "ó", "ś", "ź", "ż"]
    ),
    Language.ENGLISH: LanguageProfile(
        code="en",
        name="English",
        native_name="English",
        script="Latin",
        direction="ltr",
        grammatical_features=[],
        formality_levels=1,
        has_gender=False,
        has_honorifics=False,
        avg_word_expansion=1.0,
        special_characters=[]
    ),
    Language.GERMAN: LanguageProfile(
        code="de",
        name="German",
        native_name="Deutsch",
        script="Latin",
        direction="ltr",
        grammatical_features=[GrammaticalFeature.GENDER, GrammaticalFeature.FORMALITY],
        formality_levels=2,
        has_gender=True,
        has_honorifics=False,
        avg_word_expansion=1.2,
        special_characters=["ä", "ö", "ü", "ß"]
    ),
    Language.FRENCH: LanguageProfile(
        code="fr",
        name="French",
        native_name="Français",
        script="Latin",
        direction="ltr",
        grammatical_features=[GrammaticalFeature.GENDER, GrammaticalFeature.FORMALITY],
        formality_levels=2,
        has_gender=True,
        has_honorifics=False,
        avg_word_expansion=1.15,
        special_characters=["à", "â", "ç", "é", "è", "ê", "ë", "î", "ï", "ô", "ù", "û", "ü", "ÿ", "œ"]
    ),
    Language.SPANISH: LanguageProfile(
        code="es",
        name="Spanish",
        native_name="Español",
        script="Latin",
        direction="ltr",
        grammatical_features=[GrammaticalFeature.GENDER, GrammaticalFeature.FORMALITY],
        formality_levels=2,
        has_gender=True,
        has_honorifics=False,
        avg_word_expansion=1.25,
        special_characters=["á", "é", "í", "ó", "ú", "ü", "ñ", "¿", "¡"]
    ),
    Language.JAPANESE: LanguageProfile(
        code="ja",
        name="Japanese",
        native_name="日本語",
        script="Japanese",
        direction="ltr",
        grammatical_features=[GrammaticalFeature.FORMALITY, GrammaticalFeature.HONORIFICS],
        formality_levels=5,
        has_gender=False,
        has_honorifics=True,
        avg_word_expansion=0.5,
        special_characters=[]
    ),
    Language.CHINESE: LanguageProfile(
        code="zh",
        name="Chinese",
        native_name="中文",
        script="Chinese",
        direction="ltr",
        grammatical_features=[],
        formality_levels=2,
        has_gender=False,
        has_honorifics=True,
        avg_word_expansion=0.5,
        special_characters=[]
    ),
    Language.ARABIC: LanguageProfile(
        code="ar",
        name="Arabic",
        native_name="العربية",
        script="Arabic",
        direction="rtl",
        grammatical_features=[GrammaticalFeature.GENDER, GrammaticalFeature.FORMALITY],
        formality_levels=3,
        has_gender=True,
        has_honorifics=True,
        avg_word_expansion=0.9,
        special_characters=[]
    ),
    Language.RUSSIAN: LanguageProfile(
        code="ru",
        name="Russian",
        native_name="Русский",
        script="Cyrillic",
        direction="ltr",
        grammatical_features=[GrammaticalFeature.GENDER, GrammaticalFeature.FORMALITY],
        formality_levels=2,
        has_gender=True,
        has_honorifics=False,
        avg_word_expansion=1.1,
        special_characters=[]
    ),
    Language.KOREAN: LanguageProfile(
        code="ko",
        name="Korean",
        native_name="한국어",
        script="Hangul",
        direction="ltr",
        grammatical_features=[GrammaticalFeature.FORMALITY, GrammaticalFeature.HONORIFICS],
        formality_levels=7,
        has_gender=False,
        has_honorifics=True,
        avg_word_expansion=0.8,
        special_characters=[]
    )
}


# =============================================================================
# LITERARY TRANSLATION PATTERNS
# =============================================================================

LITERARY_PATTERNS = {
    "metaphor": {
        "description": "Preserve metaphorical meaning, adapt cultural references",
        "example_en": "It was raining cats and dogs",
        "example_pl": "Lało jak z cebra"
    },
    "idiom": {
        "description": "Find equivalent idiom in target language",
        "example_en": "Break a leg",
        "example_pl": "Połamania nóg"
    },
    "wordplay": {
        "description": "Recreate wordplay effect, may require creative adaptation",
        "note": "Often requires transcreation"
    },
    "cultural_reference": {
        "description": "Adapt or explain cultural references",
        "options": ["keep_with_note", "adapt", "generalize"]
    },
    "rhythm": {
        "description": "Preserve rhythmic patterns in prose",
        "importance": "high_for_literary"
    },
    "register": {
        "description": "Maintain appropriate formality level",
        "considerations": ["character_voice", "setting", "relationship"]
    }
}


# =============================================================================
# MAIN CLASS
# =============================================================================

class MultiLanguageGenerator:
    """
    Multi-Language Generation System

    Generates and translates narrative content across multiple languages
    while preserving literary quality and cultural appropriateness.
    """

    def __init__(self):
        self.projects: Dict[str, TranslationProject] = {}
        self.glossaries: Dict[str, Glossary] = {}
        self.translation_memory: Dict[str, List[TranslationMemory]] = {}
        self.language_profiles = LANGUAGE_PROFILES.copy()

    async def create_translation_project(
        self,
        book_id: str,
        source_language: Language,
        target_languages: List[Language],
        mode: TranslationMode = TranslationMode.LITERARY,
        quality: QualityLevel = QualityLevel.STANDARD
    ) -> TranslationProject:
        """
        Create a new translation project.
        """
        project = TranslationProject(
            project_id=str(uuid.uuid4()),
            book_id=book_id,
            source_language=source_language,
            target_languages=target_languages,
            translation_mode=mode,
            quality_level=quality,
            glossaries=[],
            character_mappings=[],
            chapter_translations={lang.value: [] for lang in target_languages},
            progress={lang.value: 0.0 for lang in target_languages},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.projects[project.project_id] = project
        return project

    async def translate_chapter(
        self,
        project_id: str,
        chapter_text: str,
        chapter_number: int,
        target_language: Language
    ) -> ChapterTranslation:
        """
        Translate a chapter to target language.
        """
        project = self.projects.get(project_id)
        if not project:
            raise ValueError("Project not found")

        # Segment the text
        segments = self._segment_text(chapter_text)

        # Translate each segment
        translated_segments = []
        for segment_text, content_type in segments:
            translated = await self._translate_segment(
                segment_text,
                project.source_language,
                target_language,
                content_type,
                project.translation_mode,
                project.glossaries
            )
            translated_segments.append(translated)

        # Calculate metrics
        source_words = len(chapter_text.split())
        target_text = " ".join(s.translated_text for s in translated_segments)
        target_words = len(target_text.split())

        # Calculate quality score
        quality_score = self._calculate_quality_score(translated_segments)

        translation = ChapterTranslation(
            chapter_number=chapter_number,
            source_language=project.source_language,
            target_language=target_language,
            segments=translated_segments,
            word_count_source=source_words,
            word_count_target=target_words,
            quality_score=quality_score,
            review_status="pending",
            translator_notes=[]
        )

        # Store in project
        if target_language.value not in project.chapter_translations:
            project.chapter_translations[target_language.value] = []
        project.chapter_translations[target_language.value].append(translation)

        # Update progress
        project.progress[target_language.value] = len(
            project.chapter_translations[target_language.value]
        ) / 10.0 * 100  # Assume 10 chapters

        project.updated_at = datetime.now()

        return translation

    async def generate_multilingual(
        self,
        prompt: str,
        config: GenerationConfig,
        genre: str
    ) -> Dict[str, str]:
        """
        Generate content in multiple languages simultaneously.
        """
        results = {}

        # Generate in primary language first
        primary_text = await self._generate_in_language(
            prompt, config.primary_language, genre
        )
        results[config.primary_language.value] = primary_text

        # Generate or translate to additional languages
        for lang in config.additional_languages:
            if config.sync_generation:
                # Generate directly in target language
                text = await self._generate_in_language(prompt, lang, genre)
            else:
                # Translate from primary
                text = await self._translate_text(
                    primary_text,
                    config.primary_language,
                    lang,
                    TranslationMode.LITERARY
                )
            results[lang.value] = text

        return results

    async def create_glossary(
        self,
        name: str,
        source_language: Language,
        target_language: Language,
        domain: str,
        entries: Dict[str, str]
    ) -> Glossary:
        """
        Create a translation glossary.
        """
        glossary = Glossary(
            glossary_id=str(uuid.uuid4()),
            name=name,
            source_language=source_language,
            target_language=target_language,
            domain=domain,
            entries=entries,
            notes={},
            created_at=datetime.now()
        )

        self.glossaries[glossary.glossary_id] = glossary
        return glossary

    async def add_character_mapping(
        self,
        project_id: str,
        original_name: str,
        translations: Dict[str, str]
    ) -> CharacterNameMapping:
        """
        Add character name mapping for translation.
        """
        project = self.projects.get(project_id)
        if not project:
            raise ValueError("Project not found")

        mapping = CharacterNameMapping(
            character_id=str(uuid.uuid4()),
            original_name=original_name,
            translations=translations,
            pronunciation_guides={},
            cultural_notes={}
        )

        project.character_mappings.append(mapping)
        return mapping

    async def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of a text.
        """
        # Simplified detection based on character patterns
        detected = self._detect_language_simple(text)

        return {
            "detected_language": detected.value,
            "language_name": self.language_profiles[detected].name,
            "confidence": 0.85,
            "script": self.language_profiles[detected].script
        }

    async def get_translation_suggestions(
        self,
        source_text: str,
        source_language: Language,
        target_language: Language,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get translation suggestions from memory and AI.
        """
        suggestions = []

        # Check translation memory
        memory_matches = self._search_translation_memory(
            source_text, source_language, target_language
        )

        for match in memory_matches[:3]:
            suggestions.append({
                "source": "memory",
                "text": match.translated_text,
                "confidence": 0.9 if match.approved else 0.7,
                "usage_count": match.usage_count
            })

        # Generate AI suggestion
        ai_translation = await self._translate_text(
            source_text, source_language, target_language, TranslationMode.LITERARY
        )
        suggestions.append({
            "source": "ai",
            "text": ai_translation,
            "confidence": 0.8
        })

        return {
            "source_text": source_text,
            "source_language": source_language.value,
            "target_language": target_language.value,
            "suggestions": suggestions
        }

    async def analyze_translation_quality(
        self,
        source_text: str,
        translated_text: str,
        source_language: Language,
        target_language: Language
    ) -> Dict[str, Any]:
        """
        Analyze the quality of a translation.
        """
        analysis = {
            "source_language": source_language.value,
            "target_language": target_language.value,
            "metrics": {}
        }

        # Check word count ratio
        source_words = len(source_text.split())
        target_words = len(translated_text.split())
        expected_ratio = self.language_profiles[target_language].avg_word_expansion

        actual_ratio = target_words / max(source_words, 1)
        ratio_score = 1.0 - abs(actual_ratio - expected_ratio) / expected_ratio
        analysis["metrics"]["length_ratio"] = {
            "score": max(0, ratio_score),
            "actual": actual_ratio,
            "expected": expected_ratio
        }

        # Check for untranslated segments
        untranslated = self._find_untranslated(source_text, translated_text)
        analysis["metrics"]["completeness"] = {
            "score": 1.0 - len(untranslated) * 0.1,
            "untranslated_segments": untranslated
        }

        # Overall score
        analysis["overall_score"] = sum(
            m["score"] for m in analysis["metrics"].values()
        ) / len(analysis["metrics"])

        # Issues
        analysis["issues"] = []
        if ratio_score < 0.7:
            analysis["issues"].append("Translation length differs significantly from expected")
        if untranslated:
            analysis["issues"].append(f"Found {len(untranslated)} potentially untranslated segments")

        return analysis

    def get_language_info(self, language: Language) -> Dict[str, Any]:
        """
        Get detailed information about a language.
        """
        profile = self.language_profiles.get(language)
        if not profile:
            return {"error": "Language not found"}

        return {
            "profile": profile.to_dict(),
            "literary_considerations": self._get_literary_considerations(language),
            "common_challenges": self._get_translation_challenges(language)
        }

    def list_supported_languages(self) -> List[Dict[str, Any]]:
        """
        List all supported languages.
        """
        return [
            {
                "code": lang.value,
                "name": profile.name,
                "native_name": profile.native_name,
                "script": profile.script
            }
            for lang, profile in self.language_profiles.items()
        ]

    # =========================================================================
    # TRANSLATION HELPERS
    # =========================================================================

    def _segment_text(self, text: str) -> List[Tuple[str, ContentType]]:
        """Segment text into translatable units."""
        segments = []
        paragraphs = text.split("\n\n")

        for para in paragraphs:
            if not para.strip():
                continue

            # Detect content type
            if '"' in para or '—' in para:
                content_type = ContentType.DIALOGUE
            elif para.startswith("#"):
                content_type = ContentType.CHAPTER_TITLE
            else:
                content_type = ContentType.NARRATIVE

            segments.append((para, content_type))

        return segments

    async def _translate_segment(
        self,
        text: str,
        source: Language,
        target: Language,
        content_type: ContentType,
        mode: TranslationMode,
        glossary_ids: List[str]
    ) -> TranslationSegment:
        """Translate a single segment."""
        # Apply glossaries
        text_with_glossary = self._apply_glossaries(text, glossary_ids, source, target)

        # Translate
        translated = await self._translate_text(text_with_glossary, source, target, mode)

        # Check quality
        confidence = self._estimate_confidence(text, translated, mode)
        requires_review = confidence < 0.8 or content_type == ContentType.DIALOGUE

        # Generate alternatives for low confidence
        alternatives = []
        if confidence < 0.9:
            alt = await self._translate_text(text, source, target, TranslationMode.LITERAL)
            if alt != translated:
                alternatives.append(alt)

        return TranslationSegment(
            segment_id=str(uuid.uuid4()),
            source_text=text,
            translated_text=translated,
            content_type=content_type,
            confidence=confidence,
            alternatives=alternatives,
            notes="",
            requires_review=requires_review
        )

    async def _translate_text(
        self,
        text: str,
        source: Language,
        target: Language,
        mode: TranslationMode
    ) -> str:
        """
        Translate text using AI.
        This is a placeholder - would use actual translation API/model.
        """
        # In production, this would call Claude or a translation API
        # For now, return a placeholder indicating translation would happen

        if source == target:
            return text

        # Simulate translation by marking the text
        # In production, this would be actual translation
        return f"[Tłumaczenie {source.value}->{target.value}]: {text}"

    async def _generate_in_language(
        self,
        prompt: str,
        language: Language,
        genre: str
    ) -> str:
        """
        Generate content directly in a target language.
        """
        # In production, this would use Claude with language-specific instructions
        # For now, return a placeholder

        return f"[Wygenerowano w {language.value}]: {prompt}"

    def _apply_glossaries(
        self,
        text: str,
        glossary_ids: List[str],
        source: Language,
        target: Language
    ) -> str:
        """Apply glossary entries to text."""
        result = text

        for gid in glossary_ids:
            glossary = self.glossaries.get(gid)
            if glossary and glossary.source_language == source and glossary.target_language == target:
                for source_term, target_term in glossary.entries.items():
                    # Mark glossary terms for translation
                    result = result.replace(source_term, f"[[{target_term}]]")

        return result

    def _estimate_confidence(
        self,
        source: str,
        translated: str,
        mode: TranslationMode
    ) -> float:
        """Estimate translation confidence."""
        # Simplified confidence estimation
        base_confidence = 0.85

        # Adjust based on mode
        if mode == TranslationMode.TRANSCREATION:
            base_confidence -= 0.1
        elif mode == TranslationMode.LITERAL:
            base_confidence += 0.05

        # Adjust based on length ratio
        source_len = len(source)
        trans_len = len(translated)
        ratio = trans_len / max(source_len, 1)

        if 0.5 < ratio < 2.0:
            base_confidence += 0.05
        else:
            base_confidence -= 0.1

        return max(0.0, min(1.0, base_confidence))

    def _calculate_quality_score(
        self,
        segments: List[TranslationSegment]
    ) -> float:
        """Calculate overall quality score."""
        if not segments:
            return 0.0

        avg_confidence = sum(s.confidence for s in segments) / len(segments)
        review_ratio = sum(1 for s in segments if s.requires_review) / len(segments)

        return avg_confidence * (1 - review_ratio * 0.3)

    def _detect_language_simple(self, text: str) -> Language:
        """Simple language detection based on character patterns."""
        # Check for specific character sets
        if any(c in text for c in "ąćęłńóśźż"):
            return Language.POLISH
        elif any(c in text for c in "äöüß"):
            return Language.GERMAN
        elif any(c in text for c in "àâçéèêëîïôùûüÿœ"):
            return Language.FRENCH
        elif any(c in text for c in "áéíóúüñ¿¡"):
            return Language.SPANISH
        elif any("\u4e00" <= c <= "\u9fff" for c in text):
            return Language.CHINESE
        elif any("\u3040" <= c <= "\u309f" or "\u30a0" <= c <= "\u30ff" for c in text):
            return Language.JAPANESE
        elif any("\uac00" <= c <= "\ud7af" for c in text):
            return Language.KOREAN
        elif any("\u0400" <= c <= "\u04ff" for c in text):
            return Language.RUSSIAN
        elif any("\u0600" <= c <= "\u06ff" for c in text):
            return Language.ARABIC
        else:
            return Language.ENGLISH

    def _search_translation_memory(
        self,
        text: str,
        source: Language,
        target: Language
    ) -> List[TranslationMemory]:
        """Search translation memory for matches."""
        key = f"{source.value}_{target.value}"
        memories = self.translation_memory.get(key, [])

        # Find similar translations
        matches = []
        text_lower = text.lower()

        for memory in memories:
            if memory.source_text.lower() in text_lower or text_lower in memory.source_text.lower():
                matches.append(memory)

        return sorted(matches, key=lambda m: m.usage_count, reverse=True)

    def _find_untranslated(self, source: str, translated: str) -> List[str]:
        """Find potentially untranslated segments."""
        untranslated = []

        # Check for source language words in translation
        source_words = set(source.lower().split())
        translated_words = set(translated.lower().split())

        # Words that appear in both might be untranslated
        common = source_words & translated_words

        # Filter out proper nouns and numbers
        for word in common:
            if len(word) > 3 and not word[0].isupper() and not word.isdigit():
                untranslated.append(word)

        return untranslated[:5]  # Return max 5

    def _get_literary_considerations(self, language: Language) -> List[str]:
        """Get literary considerations for a language."""
        considerations = {
            Language.POLISH: [
                "Zachowaj bogactwo przypadków w opisach",
                "Uwzględnij genderowe formy czasowników",
                "Dbaj o melodię języka w dialogach"
            ],
            Language.ENGLISH: [
                "Balance between formal and casual register",
                "Consider regional variations (US/UK)",
                "Preserve rhythm and flow"
            ],
            Language.JAPANESE: [
                "Maintain appropriate keigo (honorific levels)",
                "Consider sentence-final particles for character voice",
                "Adapt cultural references carefully"
            ],
            Language.GERMAN: [
                "Handle compound words appropriately",
                "Maintain Sie/du formality distinctions",
                "Consider sentence structure differences"
            ],
            Language.FRENCH: [
                "Preserve literary tenses (passé simple)",
                "Handle tu/vous distinctions",
                "Maintain stylistic register"
            ]
        }

        return considerations.get(language, ["Consider cultural and grammatical differences"])

    def _get_translation_challenges(self, language: Language) -> List[str]:
        """Get common translation challenges for a language."""
        challenges = {
            Language.POLISH: [
                "Complex case system",
                "Aspect distinctions in verbs",
                "Word order flexibility"
            ],
            Language.ENGLISH: [
                "Lack of grammatical gender",
                "Limited formality markers",
                "Phrasal verbs"
            ],
            Language.JAPANESE: [
                "Multiple writing systems",
                "Complex honorific system",
                "Topic-comment structure"
            ],
            Language.ARABIC: [
                "Right-to-left script",
                "Root-based morphology",
                "Dialectal variations"
            ],
            Language.CHINESE: [
                "Character-based writing",
                "Lack of grammatical markers",
                "Contextual meaning"
            ]
        }

        return challenges.get(language, ["General grammatical and cultural differences"])

    # =========================================================================
    # PUBLIC GETTERS
    # =========================================================================

    def get_project(self, project_id: str) -> Optional[TranslationProject]:
        """Get a translation project by ID."""
        return self.projects.get(project_id)

    def get_glossary(self, glossary_id: str) -> Optional[Glossary]:
        """Get a glossary by ID."""
        return self.glossaries.get(glossary_id)

    def list_projects(self, book_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List translation projects."""
        projects = self.projects.values()

        if book_id:
            projects = [p for p in projects if p.book_id == book_id]

        return [
            {
                "project_id": p.project_id,
                "book_id": p.book_id,
                "source": p.source_language.value,
                "targets": [t.value for t in p.target_languages],
                "progress": p.progress,
                "updated_at": p.updated_at.isoformat()
            }
            for p in projects
        ]

    def list_glossaries(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """List glossaries."""
        glossaries = self.glossaries.values()

        if domain:
            glossaries = [g for g in glossaries if g.domain == domain]

        return [
            {
                "glossary_id": g.glossary_id,
                "name": g.name,
                "source": g.source_language.value,
                "target": g.target_language.value,
                "entries": len(g.entries)
            }
            for g in glossaries
        ]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_multilang_generator: Optional[MultiLanguageGenerator] = None


def get_multilang_generator() -> MultiLanguageGenerator:
    """Get the singleton multi-language generator instance."""
    global _multilang_generator
    if _multilang_generator is None:
        _multilang_generator = MultiLanguageGenerator()
    return _multilang_generator
