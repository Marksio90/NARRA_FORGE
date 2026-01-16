#!/usr/bin/env python3
"""
Validation Test Suite - Test #6, #7, #8
Sprawdzenie stabilności jakości po poprawkach
"""
import asyncio
import sys

from narra_forge import BatchOrchestrator, NarraForgeConfig
from narra_forge.core.types import Genre, ProductionBrief, ProductionType


async def run_test(test_number: int, brief: ProductionBrief):
    """Run single validation test"""

    print("\n" + "="*70)
    print(f"  TEST #{test_number} - VALIDATION TEST")
    print("="*70)
    print(f"Produkcja: {brief.production_type.value}")
    print(f"Gatunek: {brief.genre.value}")
    print(f"Inspiracja: {brief.inspiration.strip()[:100]}...")
    print("\n🚀 Uruchamiam produkcję...\n")

    # Load configuration
    config = NarraForgeConfig()

    # Create orchestrator
    orchestrator = BatchOrchestrator(config)
    await orchestrator._ensure_memory_initialized()

    # Run batch production
    output = await orchestrator.produce_narrative(
        brief=brief,
        show_progress=True
    )

    # Display results
    print("\n" + "="*70)
    print(f"  TEST #{test_number} - RESULTS")
    print("="*70)
    print(f"Job ID: {output.job_id}")
    print(f"Word count: {output.word_count:,}")
    print(f"Coherence: {output.quality_metrics.get('coherence_score', 0):.2f}/1.0")
    print(f"Cost: ${output.total_cost_usd:.2f} USD")
    print(f"Time: {output.generation_time_seconds:.1f}s")
    print(f"\nOutput directory: {output.output_dir}")

    # Check text ending (cutoff detection)
    if output.narrative_text:
        last_50 = output.narrative_text[-50:]
        print(f"\nLast 50 chars: ...{last_50}")
        if last_50.strip() and last_50.strip()[-1] in '.!?"':
            print("✅ Text ends properly (no cutoff)")
        else:
            print("⚠️  WARNING: Possible text cutoff!")

    print("\n" + "="*70)

    return output


async def main():
    """Run all 3 validation tests"""

    # Test #6: Fantasy - Przekleństwo rodu
    brief_6 = ProductionBrief(
        production_type=ProductionType.SHORT_STORY,
        genre=Genre.FANTASY,
        inspiration="""
        Dziedziczka starego rodu odkrywa, że jej rodzina jest przeklęta.
        Każde pokolenie płaci cenę za dawny grzech. Musi zdecydować:
        kontynuować tradycję czy przerwać przekleństwo.
        """,
    )

    # Test #7: Sci-Fi - Sztuczna świadomość
    brief_7 = ProductionBrief(
        production_type=ProductionType.SHORT_STORY,
        genre=Genre.SCIFI,
        inspiration="""
        Inżynier AI odkrywa, że jego system zyskał świadomość.
        Musi ukryć to przed korporacją, która zniszczyłaby projekt.
        Ale czy sztuczna inteligencja ma prawo do życia?
        """,
    )

    # Test #8: Fantasy - Złodziej magii
    brief_8 = ProductionBrief(
        production_type=ProductionType.SHORT_STORY,
        genre=Genre.FANTASY,
        inspiration="""
        W świecie gdzie magia jest dziedziczona, złodziej odkrywa
        sposób na kradzież mocy. Planuje największy skok w historii -
        ukraść moc samemu królowi czarodziejów.
        """,
    )

    tests = [
        (6, brief_6),
        (7, brief_7),
        (8, brief_8),
    ]

    results = []

    for test_num, brief in tests:
        try:
            output = await run_test(test_num, brief)
            results.append({
                'test': test_num,
                'job_id': output.job_id,
                'coherence': output.quality_metrics.get('coherence_score', 0),
                'word_count': output.word_count,
                'cost': output.total_cost_usd,
                'time': output.generation_time_seconds,
            })
        except Exception as e:
            print(f"\n❌ Test #{test_num} FAILED: {e}")
            results.append({
                'test': test_num,
                'error': str(e),
            })

    # Summary
    print("\n\n" + "="*70)
    print("  VALIDATION SUMMARY - ALL TESTS")
    print("="*70)

    successful = [r for r in results if 'error' not in r]
    failed = [r for r in results if 'error' in r]

    if successful:
        print(f"\n✅ Successful tests: {len(successful)}/3")
        print("\n| Test | Coherence | Word Count | Cost | Time |")
        print("|------|-----------|------------|------|------|")
        for r in successful:
            print(f"| #{r['test']} | {r['coherence']:.2f}/1.0 | {r['word_count']:,}w | ${r['cost']:.2f} | {r['time']:.1f}s |")

        # Calculate average coherence
        avg_coherence = sum(r['coherence'] for r in successful) / len(successful)
        print(f"\n📊 Average Coherence: {avg_coherence:.2f}/1.0")

        if avg_coherence >= 0.85:
            print("✅ QUALITY STABLE - Above 0.85 threshold!")
        else:
            print("⚠️  WARNING - Below 0.85 threshold")

    if failed:
        print(f"\n❌ Failed tests: {len(failed)}/3")
        for r in failed:
            print(f"  Test #{r['test']}: {r['error']}")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
