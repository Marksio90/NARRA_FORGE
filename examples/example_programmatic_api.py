#!/usr/bin/env python3
"""
Example: Programmatic API Usage

Demonstracja pełnej kontroli nad produkcją - konfiguracja, memory, tracking.
"""
import asyncio
from pathlib import Path

from narra_forge import BatchOrchestrator, NarraForgeConfig
from narra_forge.core.types import Genre, ProductionBrief, ProductionType
from narra_forge.memory import MemorySystem
from narra_forge.models import ModelRouter, OpenAIClient


async def main():
    """Advanced programmatic usage"""

    # 1. Configure with custom settings
    config = NarraForgeConfig()
    config.max_cost_per_job = 5.0  # Limit cost to $5
    config.min_coherence_score = 0.90  # Require high quality
    config.log_level = "DEBUG"  # Verbose logging

    print("Configuration:")
    print(f"  Max cost per job: ${config.max_cost_per_job}")
    print(f"  Min coherence: {config.min_coherence_score}")
    print(f"  Environment: {config.environment}")
    print()

    # 2. Initialize components explicitly
    memory = MemorySystem(config)
    await memory.initialize()

    client = OpenAIClient(config)
    router = ModelRouter(config, client)

    # 3. Create orchestrator with custom components
    orchestrator = BatchOrchestrator(
        config=config,
        memory=memory,
        client=client,
        router=router,
    )

    # 4. Check existing worlds (multi-world support)
    worlds = await memory.structural.list_worlds()
    print(f"Existing worlds in database: {len(worlds)}")

    # 5. Define production
    brief = ProductionBrief(
        production_type=ProductionType.SHORT_STORY,
        genre=Genre.HORROR,
        inspiration="Psycholog odkrywa, że wszyscy jego pacjenci śnią ten sam koszmar",
    )

    # 6. Run with progress disabled (for automation)
    print(f"\nStarting batch production...")
    print(f"  Type: {brief.production_type.value}")
    print(f"  Genre: {brief.genre.value}\n")

    output = await orchestrator.produce_narrative(
        brief=brief,
        show_progress=False  # Disable progress for programmatic use
    )

    # 7. Detailed analysis of results
    print("\n" + "="*60)
    print("  DETAILED ANALYSIS")
    print("="*60)

    print(f"\nProduction:")
    print(f"  Job ID: {output.job_id}")
    print(f"  Success: {output.success}")
    print(f"  Type: {output.production_type.value}")
    print(f"  Genre: {output.genre.value}")

    print(f"\nContent:")
    print(f"  Word count: {output.word_count:,}")
    print(f"  Segments: {len(output.segments)}")
    print(f"  Characters: {len(output.characters)}")

    print(f"\nWorld:")
    if output.world:
        print(f"  ID: {output.world.world_id}")
        print(f"  Name: {output.world.name}")
        print(f"  Conflict: {output.world.core_conflict}")
        print(f"  Theme: {output.world.existential_theme}")

    print(f"\nQuality:")
    for metric, value in output.quality_metrics.items():
        if isinstance(value, float):
            print(f"  {metric}: {value:.3f}")
        else:
            print(f"  {metric}: {value}")

    print(f"\nCost & Performance:")
    print(f"  Total tokens: {output.total_tokens:,}")
    print(f"  Total cost: ${output.total_cost_usd:.4f}")
    print(f"  Time: {output.generation_time_seconds:.1f}s")
    print(f"  Cost per 1k words: ${(output.total_cost_usd / (output.word_count / 1000)):.4f}")

    if output.model_usage:
        print(f"\nModel usage:")
        for model, tokens in output.model_usage.items():
            print(f"  {model}: {tokens:,} tokens")

    print(f"\nFiles:")
    for name, path in output.files.items():
        file_path = Path(path)
        size = file_path.stat().st_size if file_path.exists() else 0
        print(f"  {name}: {path} ({size:,} bytes)")

    # 8. Save world ID for future use
    if output.world:
        print(f"\n💡 Tip: Use world_id='{output.world.world_id}' for sequels!")

    # 9. List all jobs in memory
    all_jobs = await memory.list_jobs(limit=5)
    print(f"\nRecent jobs in database: {len(all_jobs)}")

    print("\n✓ Done!\n")


if __name__ == "__main__":
    asyncio.run(main())
