"""
Cost Estimation Analysis - NarraForge

PROBLEM: Symulacja zaniża koszty o 2-3x z powodu:
1. Błędnego przelicznika tokeny/słowo dla polskiego (1.33 zamiast 1.5)
2. Zaniżonego input per chapter (5000 zamiast 12000)
3. Ignorowania architektury scene-by-scene (5 scen × 2 API calls)
4. Braku Beat Sheet calls

PRAWIDŁOWA KALKULACJA:
"""

from dataclasses import dataclass
from typing import Dict

# Ceny z config.py
TIER1_INPUT = 0.15   # $/1M tokens
TIER1_OUTPUT = 0.60  # $/1M tokens
TIER2_INPUT = 2.50   # $/1M tokens
TIER2_OUTPUT = 10.0  # $/1M tokens

@dataclass
class CostEstimate:
    """Szczegółowa kalkulacja kosztów"""

    # Parametry wejściowe
    target_words: int = 100_000  # Fantasy: 90-140k słów
    chapter_count: int = 33
    scenes_per_chapter: int = 5
    use_beat_sheet: bool = True

    # Przeliczniki
    TOKENS_PER_WORD_POLISH: float = 1.5  # Polski = więcej tokenów niż angielski

    # Context sizes (tokens)
    SYSTEM_PROMPT: int = 2000
    CONTEXT_PACK: int = 8000
    BEAT_SHEET_CONTENT: int = 500
    PREVIOUS_CONTENT: int = 500

    def calculate(self) -> Dict:
        """Oblicz realistyczne koszty"""

        total_scenes = self.chapter_count * self.scenes_per_chapter

        # =====================================================
        # PROSE GENERATION (TIER 2)
        # =====================================================

        # Output: słowa → tokeny
        prose_output_tokens = int(self.target_words * self.TOKENS_PER_WORD_POLISH)

        # Input: każda scena potrzebuje pełnego kontekstu
        input_per_scene = (
            self.SYSTEM_PROMPT +
            self.CONTEXT_PACK +
            self.BEAT_SHEET_CONTENT +
            self.PREVIOUS_CONTENT
        )  # ~11,000 tokens per scene

        prose_input_tokens = total_scenes * input_per_scene

        prose_cost = (
            (prose_input_tokens / 1_000_000) * TIER2_INPUT +
            (prose_output_tokens / 1_000_000) * TIER2_OUTPUT
        )

        # =====================================================
        # BEAT SHEET GENERATION (TIER 1) - jeśli włączone
        # =====================================================

        beat_sheet_cost = 0.0
        beat_sheet_input = 0
        beat_sheet_output = 0

        if self.use_beat_sheet:
            beat_sheet_input = total_scenes * 2000  # prompt + context
            beat_sheet_output = total_scenes * 1500  # ~5 beats × 300 tokens

            beat_sheet_cost = (
                (beat_sheet_input / 1_000_000) * TIER1_INPUT +
                (beat_sheet_output / 1_000_000) * TIER1_OUTPUT
            )

        # =====================================================
        # OTHER STEPS (World Bible, Characters, Plot, etc.)
        # =====================================================

        other_steps_cost = 0.75  # ~$0.75 dla pozostałych kroków

        # =====================================================
        # TOTAL
        # =====================================================

        total_cost = prose_cost + beat_sheet_cost + other_steps_cost

        return {
            "summary": {
                "total_cost": round(total_cost, 2),
                "prose_cost": round(prose_cost, 2),
                "beat_sheet_cost": round(beat_sheet_cost, 2),
                "other_steps_cost": round(other_steps_cost, 2),
            },
            "prose_generation": {
                "total_scenes": total_scenes,
                "input_tokens": prose_input_tokens,
                "output_tokens": prose_output_tokens,
                "input_cost": round((prose_input_tokens / 1_000_000) * TIER2_INPUT, 2),
                "output_cost": round((prose_output_tokens / 1_000_000) * TIER2_OUTPUT, 2),
            },
            "beat_sheets": {
                "enabled": self.use_beat_sheet,
                "input_tokens": beat_sheet_input,
                "output_tokens": beat_sheet_output,
                "cost": round(beat_sheet_cost, 2),
            },
            "comparison": {
                "current_simulation": 2.71,
                "realistic_estimate": round(total_cost, 2),
                "underestimate_factor": round(total_cost / 2.71, 2),
            }
        }


def main():
    """Porównanie kalkulacji"""

    print("=" * 60)
    print("ANALIZA KOSZTÓW - NarraForge")
    print("=" * 60)

    # Scenariusz 1: Z Beat Sheet (nowy system Divine Prompt)
    estimate_with_beat = CostEstimate(
        target_words=100_000,
        chapter_count=33,
        scenes_per_chapter=5,
        use_beat_sheet=True
    )
    result1 = estimate_with_beat.calculate()

    print("\n📐 SCENARIUSZ 1: Z Beat Sheet Architecture")
    print("-" * 60)
    print(f"  Target words:     {estimate_with_beat.target_words:,}")
    print(f"  Chapters:         {estimate_with_beat.chapter_count}")
    print(f"  Scenes:           {result1['prose_generation']['total_scenes']}")
    print()
    print(f"  PROSE (TIER2):")
    print(f"    Input tokens:   {result1['prose_generation']['input_tokens']:,}")
    print(f"    Output tokens:  {result1['prose_generation']['output_tokens']:,}")
    print(f"    Input cost:     ${result1['prose_generation']['input_cost']}")
    print(f"    Output cost:    ${result1['prose_generation']['output_cost']}")
    print(f"    Subtotal:       ${result1['summary']['prose_cost']}")
    print()
    print(f"  BEAT SHEETS (TIER1):")
    print(f"    Cost:           ${result1['beat_sheets']['cost']}")
    print()
    print(f"  OTHER STEPS:      ${result1['summary']['other_steps_cost']}")
    print()
    print(f"  ════════════════════════════════════════")
    print(f"  TOTAL:            ${result1['summary']['total_cost']}")
    print(f"  ════════════════════════════════════════")

    # Scenariusz 2: Bez Beat Sheet (prostsza architektura)
    estimate_simple = CostEstimate(
        target_words=100_000,
        chapter_count=33,
        scenes_per_chapter=5,
        use_beat_sheet=False
    )
    result2 = estimate_simple.calculate()

    print("\n📝 SCENARIUSZ 2: Bez Beat Sheet (simple)")
    print("-" * 60)
    print(f"  TOTAL:            ${result2['summary']['total_cost']}")

    # Porównanie z symulacją
    print("\n⚠️  PORÓWNANIE Z OBECNĄ SYMULACJĄ")
    print("-" * 60)
    print(f"  Symulacja pokazuje:     $2.71")
    print(f"  Realistyczny koszt:     ${result1['summary']['total_cost']}")
    print(f"  Niedoszacowanie:        {result1['comparison']['underestimate_factor']}x")

    print("\n🔧 WYMAGANE POPRAWKI w _calculate_step_costs():")
    print("-" * 60)
    print("""
    1. Zmień przelicznik tokeny/słowo:
       PRZED: target_word_count / 0.75  (~1.33 tok/word)
       PO:    target_word_count * 1.5   (~1.5 tok/word dla polskiego)

    2. Uwzględnij scene-by-scene:
       PRZED: 5000 * chapter_count
       PO:    12000 * chapter_count * scenes_per_chapter

    3. Dodaj Beat Sheet costs (jeśli używane):
       beat_sheet_cost = scenes * 3500 * TIER1_OUTPUT / 1M

    4. Dodaj margines błędu (+15%):
       final_cost = calculated_cost * 1.15
    """)


if __name__ == "__main__":
    main()
