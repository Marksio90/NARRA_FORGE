"""
Deep Editor Agent - Aggressive quality editing to eliminate AI writing patterns

This agent performs deep editing to achieve bestseller-level prose quality:
- Eliminates word repetitions within close proximity
- Replaces cliches with original expressions
- Improves show vs tell ratio
- Enhances sentence variety
- Strengthens weak verbs
- Ensures dialogue authenticity
"""

from typing import Dict, List, Tuple, Any, Optional
import re
from collections import Counter
import logging

from app.agents.base_agent import BaseAgent
from app.agents.model_tier_manager import model_tier_manager

logger = logging.getLogger(__name__)


class DeepEditorAgent(BaseAgent):
    """
    Agent for deep quality editing of generated prose.
    Eliminates common AI writing patterns and elevates quality to bestseller level.
    """

    # Common cliches to detect and replace
    POLISH_CLICHES = [
        "serce biło szybciej",
        "serce zabiło mocniej",
        "dreszcz przeszedł",
        "pot spływał",
        "krew zastygła",
        "oddech zaparło",
        "czas stanął w miejscu",
        "w jednej chwili",
        "nagle",
        "ciemność otuliła",
        "cisza była grobowa",
        "myśli wirowały",
        "krew pulsowała",
        "napięcie rosło",
        "emocje buzowały",
        "zimny dreszcz",
        "gorące łzy",
        "serce ścisnęło się",
        "ciarki przeszły po plecach",
        "zamarł w bezruchu",
        "nie mógł uwierzyć własnym oczom",
        "jak grom z jasnego nieba",
        "cisza przed burzą",
        "oczy rozszerzyły się ze zdumienia",
        "zacisnął pięści",
        "twarz wykrzywiła się",
    ]

    ENGLISH_CLICHES = [
        "heart pounded",
        "heart raced",
        "shivers ran down",
        "sweat beaded",
        "blood ran cold",
        "breath caught",
        "time stood still",
        "in an instant",
        "suddenly",
        "darkness enveloped",
        "deafening silence",
        "thoughts raced",
        "blood pumped",
        "tension mounted",
        "emotions swirled",
        "cold shiver",
        "hot tears",
        "heart clenched",
        "chills down spine",
        "froze in place",
        "couldn't believe his eyes",
        "like a bolt from the blue",
        "calm before the storm",
        "eyes widened",
        "clenched fists",
        "face contorted",
    ]

    # Weak verbs to replace
    POLISH_WEAK_VERBS = {'był', 'była', 'było', 'byli', 'były', 'mieć', 'miał', 'miała',
                         'czuć', 'czuł', 'czuła', 'widzieć', 'widział', 'widziała',
                         'słyszeć', 'słyszał', 'słyszała', 'iść', 'szedł', 'szła'}

    ENGLISH_WEAK_VERBS = {'was', 'were', 'had', 'have', 'felt', 'feel', 'saw', 'see',
                          'heard', 'hear', 'went', 'go', 'walked', 'walk'}

    def __init__(self):
        super().__init__("deep_editor")
        self.model_manager = model_tier_manager

    def _build_prompt(self, task: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build prompt for deep editing task"""
        text = task.get("text", "")
        edit_type = task.get("edit_type", "full")
        language = context.get("language", "polski") if context else "polski"

        if edit_type == "repetitions":
            return self._build_repetition_prompt(text, language)
        elif edit_type == "cliches":
            return self._build_cliche_prompt(text, language)
        elif edit_type == "show_vs_tell":
            return self._build_show_prompt(text, language)
        elif edit_type == "sentence_variety":
            return self._build_variety_prompt(text, language)
        elif edit_type == "weak_verbs":
            return self._build_verb_prompt(text, language)
        else:
            return self._build_full_edit_prompt(text, language)

    async def analyze_quality_metrics(self, text: str, language: str = "polski") -> Dict[str, Any]:
        """
        Analyze text quality metrics without editing.

        Returns metrics dict with:
        - repetition_score: 0-100 (higher = fewer repetitions)
        - cliche_count: Number of detected cliches
        - show_vs_tell_ratio: 0-1 (higher = more showing)
        - sentence_variety: 0-100 (higher = more variety)
        - weak_verb_ratio: 0-1 (lower = better)
        - paragraph_variance: 0-100 (higher = more variety)
        - dialogue_percentage: 0-1
        - overall_quality: 0-100 weighted average
        """
        words = text.split()
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

        metrics = {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "repetition_score": self._calculate_repetition_score(words),
            "cliche_count": self._count_cliches(text, language),
            "show_vs_tell_ratio": await self._analyze_show_vs_tell(text, language),
            "sentence_variety": self._calculate_sentence_variety(sentences),
            "weak_verb_ratio": self._calculate_weak_verb_ratio(words, language),
            "paragraph_variance": self._calculate_paragraph_variance(text),
            "dialogue_percentage": self._calculate_dialogue_percentage(text),
        }

        # Calculate overall quality score
        metrics["overall_quality"] = self._calculate_overall_quality(metrics)

        return metrics

    def _calculate_repetition_score(self, words: List[str], window_size: int = 50) -> float:
        """
        Calculate repetition score (0-100, higher = fewer repetitions).
        Checks for word repetitions within a sliding window.
        """
        if len(words) < window_size:
            return 100.0

        # Normalize words
        normalized = [w.lower().strip('.,!?;:"\'') for w in words]

        repetitions = 0
        total_windows = len(normalized) - window_size + 1

        for i in range(total_windows):
            window = normalized[i:i + window_size]
            word_counts = Counter(window)
            # Count repeated content words (>4 chars to skip articles)
            for word, count in word_counts.items():
                if len(word) > 4 and count > 1:
                    repetitions += (count - 1)

        # Normalize to 0-100
        max_possible = total_windows * (window_size / 4)  # Rough max
        score = 100 * (1 - min(1, repetitions / max_possible))
        return max(0, min(100, score))

    def _count_cliches(self, text: str, language: str = "polski") -> int:
        """Count occurrences of known cliches in text"""
        text_lower = text.lower()
        cliches = self.POLISH_CLICHES if language == "polski" else self.ENGLISH_CLICHES

        count = 0
        for cliche in cliches:
            count += text_lower.count(cliche.lower())
        return count

    async def _analyze_show_vs_tell(self, text: str, language: str = "polski") -> float:
        """
        Analyze show vs tell ratio using AI.
        Returns ratio 0-1 (higher = more showing).
        """
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        if not paragraphs:
            return 0.5

        # Sample max 10 paragraphs for analysis
        sample = paragraphs[:min(10, len(paragraphs))]
        sample_text = '\n\n'.join([f"{i+1}. {p[:300]}..." for i, p in enumerate(sample)])

        if language == "polski":
            prompt = f"""Przeanalizuj poniższe akapity i określ, czy POKAZUJĄ (SHOW) czy OPOWIADAJĄ (TELL).

SHOW = konkretne obrazy, działania, dialogi, detale sensoryczne
TELL = abstrakcje, stany emocjonalne opisane wprost, podsumowania, wyjaśnienia

Akapity:
{sample_text}

Odpowiedz TYLKO listą numerów i ocen, np:
1: SHOW
2: TELL
3: SHOW
..."""
        else:
            prompt = f"""Analyze these paragraphs and determine if they SHOW or TELL.

SHOW = concrete images, actions, dialogue, sensory details
TELL = abstractions, directly stated emotions, summaries, explanations

Paragraphs:
{sample_text}

Respond ONLY with numbered list, e.g:
1: SHOW
2: TELL
3: SHOW
..."""

        result = await self.model_manager.generate(
            prompt=prompt,
            system_prompt="You are a literary analyst specializing in narrative technique.",
            task_type="validation",
            temperature=0.3,
            max_tokens=500
        )

        if not result.get("success"):
            return 0.5

        # Parse response
        response = result["content"].lower()
        show_count = response.count("show")
        tell_count = response.count("tell")

        total = show_count + tell_count
        if total == 0:
            return 0.5

        return show_count / total

    def _calculate_sentence_variety(self, sentences: List[str]) -> float:
        """
        Calculate sentence length variety (0-100, higher = more variety).
        Uses coefficient of variation of sentence lengths.
        """
        if len(sentences) < 5:
            return 50.0

        lengths = [len(s.split()) for s in sentences]

        mean_length = sum(lengths) / len(lengths)
        if mean_length == 0:
            return 50.0

        variance = sum((x - mean_length) ** 2 for x in lengths) / len(lengths)
        std_dev = variance ** 0.5
        cv = std_dev / mean_length

        # Good variety has CV around 0.5-0.7
        # Normalize: CV of 0.5 = 100, CV of 0 or 1+ = lower score
        score = min(100, cv * 150)
        return max(0, score)

    def _calculate_weak_verb_ratio(self, words: List[str], language: str = "polski") -> float:
        """
        Calculate ratio of weak verbs to total words (0-1, lower = better).
        """
        if not words:
            return 0.0

        weak_verbs = self.POLISH_WEAK_VERBS if language == "polski" else self.ENGLISH_WEAK_VERBS
        normalized = [w.lower().strip('.,!?;:"\'') for w in words]

        weak_count = sum(1 for word in normalized if word in weak_verbs)
        return weak_count / len(words)

    def _calculate_paragraph_variance(self, text: str) -> float:
        """
        Calculate paragraph length variance (0-100, higher = more variety).
        """
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        if len(paragraphs) < 3:
            return 50.0

        lengths = [len(p.split()) for p in paragraphs]

        mean_length = sum(lengths) / len(lengths)
        if mean_length == 0:
            return 50.0

        variance = sum((x - mean_length) ** 2 for x in lengths) / len(lengths)
        std_dev = variance ** 0.5
        cv = std_dev / mean_length

        score = min(100, cv * 150)
        return max(0, score)

    def _calculate_dialogue_percentage(self, text: str) -> float:
        """
        Calculate percentage of text that is dialogue.
        Ideal range: 40-60% for fiction.
        """
        # Match dialogue in various quote styles
        dialogue_patterns = [
            r'[„"]([^""]+)["""]',  # Polish/German quotes
            r'"([^"]+)"',  # Standard quotes
            r"'([^']+)'",  # Single quotes
            r'—\s*([^—\n]+)',  # Em-dash dialogue
        ]

        dialogue_words = 0
        for pattern in dialogue_patterns:
            matches = re.findall(pattern, text)
            dialogue_words += sum(len(m.split()) for m in matches)

        total_words = len(text.split())
        if total_words == 0:
            return 0.0

        return dialogue_words / total_words

    def _calculate_overall_quality(self, metrics: Dict[str, Any]) -> float:
        """
        Calculate weighted overall quality score (0-100).
        """
        weights = {
            "repetition_score": 0.25,
            "show_vs_tell_ratio": 0.20,
            "sentence_variety": 0.20,
            "weak_verb_ratio": 0.15,
            "paragraph_variance": 0.10,
            "dialogue_percentage": 0.10,
        }

        # Normalize metrics to 0-100 scale
        normalized = {
            "repetition_score": metrics["repetition_score"],
            # Show/tell: 0.6 is ideal, convert distance from ideal to score
            "show_vs_tell_ratio": 100 - abs(metrics["show_vs_tell_ratio"] - 0.6) * 200,
            "sentence_variety": metrics["sentence_variety"],
            # Weak verbs: lower is better, invert
            "weak_verb_ratio": (1 - metrics["weak_verb_ratio"]) * 100,
            "paragraph_variance": metrics["paragraph_variance"],
            # Dialogue: 0.5 is ideal
            "dialogue_percentage": 100 - abs(metrics["dialogue_percentage"] - 0.5) * 200,
        }

        # Clamp all normalized values
        for key in normalized:
            normalized[key] = max(0, min(100, normalized[key]))

        # Weighted average
        score = sum(normalized[k] * weights[k] for k in weights)

        # Penalty for cliches
        cliche_penalty = min(20, metrics["cliche_count"] * 2)
        score -= cliche_penalty

        return max(0, min(100, score))

    async def deep_edit(
        self,
        text: str,
        target_quality: float = 85.0,
        language: str = "polski",
        max_iterations: int = 3
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Perform deep editing to achieve target quality.

        Args:
            text: Text to edit
            target_quality: Target quality score (0-100)
            language: Text language
            max_iterations: Maximum editing iterations

        Returns:
            Tuple of (edited_text, final_metrics)
        """
        logger.info(f"Starting deep edit with target quality {target_quality}")

        # Initial analysis
        initial_metrics = await self.analyze_quality_metrics(text, language)
        logger.info(f"Initial quality: {initial_metrics['overall_quality']:.1f}")

        if initial_metrics["overall_quality"] >= target_quality:
            logger.info("Text already meets quality target")
            return text, initial_metrics

        edited_text = text
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            metrics = await self.analyze_quality_metrics(edited_text, language)

            if metrics["overall_quality"] >= target_quality:
                logger.info(f"Quality target reached after {iteration} iterations")
                break

            logger.info(f"Iteration {iteration}: Quality {metrics['overall_quality']:.1f}")

            # Apply edits based on weakest metrics
            if metrics["repetition_score"] < 70:
                edited_text = await self._eliminate_repetitions(edited_text, language)

            if metrics["cliche_count"] > 0:
                edited_text = await self._replace_cliches(edited_text, language)

            if metrics["show_vs_tell_ratio"] < 0.5:
                edited_text = await self._improve_showing(edited_text, language)

            if metrics["sentence_variety"] < 60:
                edited_text = await self._improve_sentence_variety(edited_text, language)

            if metrics["weak_verb_ratio"] > 0.08:
                edited_text = await self._replace_weak_verbs(edited_text, language)

        # Final metrics
        final_metrics = await self.analyze_quality_metrics(edited_text, language)
        final_metrics["improvement"] = final_metrics["overall_quality"] - initial_metrics["overall_quality"]
        final_metrics["iterations"] = iteration

        logger.info(f"Deep edit complete. Final quality: {final_metrics['overall_quality']:.1f} "
                    f"(+{final_metrics['improvement']:.1f})")

        return edited_text, final_metrics

    async def _eliminate_repetitions(self, text: str, language: str) -> str:
        """Eliminate word repetitions using AI"""
        if language == "polski":
            prompt = f"""Zredaguj poniższy tekst eliminując powtórzenia słów w bliskiej odległości (do 50 słów).
Zachowaj znaczenie i styl, ale użyj synonimów lub przeformułuj zdania.
NIE zmieniaj dialogów ani imion własnych.

TEKST:
{text}

ZREDAGOWANY TEKST:"""
        else:
            prompt = f"""Edit this text to eliminate word repetitions within close proximity (50 words).
Preserve meaning and style, but use synonyms or rephrase sentences.
Do NOT change dialogue or proper names.

TEXT:
{text}

EDITED TEXT:"""

        result = await self.model_manager.generate(
            prompt=prompt,
            system_prompt="You are an expert editor specializing in prose polish.",
            task_type="style_polish",
            temperature=0.7,
            max_tokens=len(text.split()) * 3
        )

        return result.get("content", text) if result.get("success") else text

    async def _replace_cliches(self, text: str, language: str) -> str:
        """Replace cliches with original expressions"""
        cliches = self.POLISH_CLICHES if language == "polski" else self.ENGLISH_CLICHES
        cliches_found = [c for c in cliches if c.lower() in text.lower()]

        if not cliches_found:
            return text

        if language == "polski":
            prompt = f"""Znajdź i zamień poniższe KLISZE na oryginalne, konkretne sformułowania:

Klisze do zamiany: {', '.join(cliches_found)}

TEKST:
{text}

Zamień każde kliszowe sformułowanie na coś oryginalnego, konkretnego i obrazowego.
TEKST BEZ KLISZ:"""
        else:
            prompt = f"""Find and replace these CLICHES with original, concrete expressions:

Cliches to replace: {', '.join(cliches_found)}

TEXT:
{text}

Replace each cliche with something original, concrete and evocative.
TEXT WITHOUT CLICHES:"""

        result = await self.model_manager.generate(
            prompt=prompt,
            system_prompt="You are an expert editor specializing in eliminating cliches.",
            task_type="style_polish",
            temperature=0.8,
            max_tokens=len(text.split()) * 3
        )

        return result.get("content", text) if result.get("success") else text

    async def _improve_showing(self, text: str, language: str) -> str:
        """Improve show vs tell ratio"""
        if language == "polski":
            prompt = f"""Przekształć fragmenty "TELLING" w "SHOWING":

Przykłady:
- TELLING: "Był przerażony" -> SHOWING: "Ręce drżały mu tak mocno, że ledwo utrzymał broń"
- TELLING: "Czuła złość" -> SHOWING: "Zacisnęła pięści, paznokcie wbiły się w dłonie"
- TELLING: "Pokój był brudny" -> SHOWING: "Kurz pokrywał meble grubą warstwą, a w kącie leżały sterty starych gazet"

TEKST DO POPRAWY:
{text}

Zamień abstrakcyjne opisy stanów na konkretne działania, dialogi i detale sensoryczne.
TEKST Z POKAZYWANIEM:"""
        else:
            prompt = f"""Transform "TELLING" passages into "SHOWING":

Examples:
- TELLING: "He was terrified" -> SHOWING: "His hands trembled so badly he could barely hold the gun"
- TELLING: "She felt angry" -> SHOWING: "She clenched her fists, nails digging into her palms"
- TELLING: "The room was dirty" -> SHOWING: "Dust covered the furniture in thick layers, and piles of old newspapers filled the corner"

TEXT TO IMPROVE:
{text}

Replace abstract state descriptions with concrete actions, dialogue and sensory details.
TEXT WITH SHOWING:"""

        result = await self.model_manager.generate(
            prompt=prompt,
            system_prompt="You are an expert editor specializing in narrative technique.",
            task_type="style_polish",
            temperature=0.7,
            max_tokens=len(text.split()) * 3
        )

        return result.get("content", text) if result.get("success") else text

    async def _improve_sentence_variety(self, text: str, language: str) -> str:
        """Improve sentence structure variety"""
        if language == "polski":
            prompt = f"""Popraw różnorodność struktury zdań w tym tekście:

- Mieszaj krótkie zdania dramatyczne z dłuższymi opisowymi
- Używaj różnych konstrukcji (pytania retoryczne, wykrzyknienia, zdania podrzędne)
- Unikaj monotonii - różnicuj długość i strukturę
- Krótkie zdania budują napięcie, długie dają oddech

TEKST:
{text}

TEKST Z RÓŻNORODNOŚCIĄ ZDAŃ:"""
        else:
            prompt = f"""Improve sentence structure variety in this text:

- Mix short dramatic sentences with longer descriptive ones
- Use varied constructions (rhetorical questions, exclamations, subordinate clauses)
- Avoid monotony - vary length and structure
- Short sentences build tension, long ones provide breathing room

TEXT:
{text}

TEXT WITH SENTENCE VARIETY:"""

        result = await self.model_manager.generate(
            prompt=prompt,
            system_prompt="You are an expert editor specializing in prose rhythm.",
            task_type="style_polish",
            temperature=0.7,
            max_tokens=len(text.split()) * 3
        )

        return result.get("content", text) if result.get("success") else text

    async def _replace_weak_verbs(self, text: str, language: str) -> str:
        """Replace weak verbs with strong action verbs"""
        if language == "polski":
            prompt = f"""Zastąp SŁABE czasowniki (być, mieć, czuć, widzieć, słyszeć) MOCNYMI czasownikami akcji:

Przykłady:
- "Był zmęczony" -> "Opadł na krzesło"
- "Miała strach" -> "Drżała na całym ciele"
- "Czuł ból" -> "Ból przeszywał mu klatkę piersiową"
- "Widział dom" -> "Dom wyłonił się z mgły"
- "Słyszał krzyki" -> "Krzyki rozdarły ciszę"

TEKST:
{text}

TEKST Z MOCNYMI CZASOWNIKAMI:"""
        else:
            prompt = f"""Replace WEAK verbs (was, had, felt, saw, heard) with STRONG action verbs:

Examples:
- "He was tired" -> "He slumped into the chair"
- "She had fear" -> "She trembled all over"
- "He felt pain" -> "Pain lanced through his chest"
- "She saw the house" -> "The house emerged from the fog"
- "He heard screams" -> "Screams tore through the silence"

TEXT:
{text}

TEXT WITH STRONG VERBS:"""

        result = await self.model_manager.generate(
            prompt=prompt,
            system_prompt="You are an expert editor specializing in active voice.",
            task_type="style_polish",
            temperature=0.7,
            max_tokens=len(text.split()) * 3
        )

        return result.get("content", text) if result.get("success") else text

    def _build_repetition_prompt(self, text: str, language: str) -> str:
        """Build prompt for repetition elimination"""
        if language == "polski":
            return f"""Zredaguj tekst eliminując powtórzenia słów:\n\n{text}"""
        return f"""Edit text to eliminate word repetitions:\n\n{text}"""

    def _build_cliche_prompt(self, text: str, language: str) -> str:
        """Build prompt for cliche replacement"""
        if language == "polski":
            return f"""Zamień klisze na oryginalne wyrażenia:\n\n{text}"""
        return f"""Replace cliches with original expressions:\n\n{text}"""

    def _build_show_prompt(self, text: str, language: str) -> str:
        """Build prompt for show vs tell improvement"""
        if language == "polski":
            return f"""Przekształć telling w showing:\n\n{text}"""
        return f"""Transform telling into showing:\n\n{text}"""

    def _build_variety_prompt(self, text: str, language: str) -> str:
        """Build prompt for sentence variety"""
        if language == "polski":
            return f"""Popraw różnorodność zdań:\n\n{text}"""
        return f"""Improve sentence variety:\n\n{text}"""

    def _build_verb_prompt(self, text: str, language: str) -> str:
        """Build prompt for weak verb replacement"""
        if language == "polski":
            return f"""Zastąp słabe czasowniki mocnymi:\n\n{text}"""
        return f"""Replace weak verbs with strong ones:\n\n{text}"""

    def _build_full_edit_prompt(self, text: str, language: str) -> str:
        """Build prompt for full deep edit"""
        if language == "polski":
            return f"""Wykonaj pełną głęboką redakcję tego tekstu:
1. Eliminuj powtórzenia słów
2. Zamień klisze na oryginalne wyrażenia
3. Zamień telling na showing
4. Popraw różnorodność zdań
5. Zastąp słabe czasowniki mocnymi

TEKST:
{text}

ZREDAGOWANY TEKST:"""
        return f"""Perform full deep edit of this text:
1. Eliminate word repetitions
2. Replace cliches with original expressions
3. Transform telling into showing
4. Improve sentence variety
5. Replace weak verbs with strong ones

TEXT:
{text}

EDITED TEXT:"""


# Singleton instance
deep_editor_agent = DeepEditorAgent()
