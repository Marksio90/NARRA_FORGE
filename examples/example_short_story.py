#!/usr/bin/env python3
"""
Example: Short Story Production

Demonstracja produkcji krótkiego opowiadania (5k-10k słów).
"""
import asyncio

from narra_forge import BatchOrchestrator, NarraForgeConfig
from narra_forge.core.types import Genre, ProductionBrief, ProductionType


async def main():
    """Produce a short fantasy story"""

    # Load configuration (requires OPENAI_API_KEY in .env)
    config = NarraForgeConfig()

    # Create orchestrator
    orchestrator = BatchOrchestrator(config)
    await orchestrator._ensure_memory_initialized()

    # Define production brief
    brief = ProductionBrief(
        production_type=ProductionType.SHORT_STORY,
        genre=Genre.FANTASY,
        inspiration="""
        Młody alchemik odkrywa, że jego mistrz przez lata kradł
        życiową esencję swoich uczniów. Musi uciec, ale transmutacja
        już się rozpoczęła.
        """,
    )

    print("\n" + "="*60)
    print("  NARRA_FORGE - Example: Short Story Production")
    print("="*60)
    print(f"\nProdukcja: {brief.production_type.value}")
    print(f"Gatunek: {brief.genre.value}")
    print(f"Inspiracja: {brief.inspiration.strip()[:80]}...")
    print("\nUruchamiam produkcję...\n")

    # Run batch production
    output = await orchestrator.produce_narrative(
        brief=brief,
        show_progress=True
    )

    # Display results
    print("\n" + "="*60)
    print("  PRODUKCJA ZAKOŃCZONA")
    print("="*60)
    print(f"\nJob ID: {output.job_id}")
    print(f"Word count: {output.word_count:,}")
    print(f"Cost: ${output.total_cost_usd:.2f} USD")
    print(f"Time: {output.generation_time_seconds:.1f}s")
    print(f"Quality: {output.quality_metrics.get('coherence_score', 0):.2f}/1.0")
    print(f"\nOutput directory: {output.output_dir}")
    print("\nPliki:")
    for name, path in output.files.items():
        print(f"  - {name}: {path}")

    # Show narrative preview
    if output.narrative_text:
        preview = output.narrative_text[:500]
        print(f"\nPodgląd (pierwsze 500 znaków):")
        print("-" * 60)
        print(preview)
        print("-" * 60)

    print("\n✓ Gotowe!\n")


if __name__ == "__main__":
    asyncio.run(main())
