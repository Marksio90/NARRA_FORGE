#!/usr/bin/env python3
"""
Basic usage example for NARRA_FORGE V2

This demonstrates the batch production engine.

NOTE: This is a FOUNDATION version. Agents are placeholders.
The full system will be implemented in next iterations.
"""
import asyncio
import os

from narra_forge import BatchOrchestrator, NarraForgeConfig
from narra_forge.core import Genre, ProductionBrief, ProductionType


async def main():
    """
    Example: Produce a narrative in batch mode.
    """

    # 1. Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-proj-your-key-here":
        print("❌ Error: OPENAI_API_KEY not set")
        print("   Copy .env.example to .env and add your key")
        return

    print("═══════════════════════════════════════════")
    print("  NARRA_FORGE V2 - Basic Example")
    print("═══════════════════════════════════════════\n")

    # 2. Create config
    print("⚙ Loading configuration...")
    config = NarraForgeConfig()
    print(f"✓ Config loaded (model: {config.default_mini_model})\n")

    # 3. Create orchestrator
    print("⚙ Initializing orchestrator...")
    orchestrator = BatchOrchestrator(config)
    await orchestrator._ensure_memory_initialized()
    print("✓ Orchestrator ready\n")

    # 4. Create production brief
    brief = ProductionBrief(
        production_type=ProductionType.SHORT_STORY,
        genre=Genre.FANTASY,
        inspiration="A young alchemist discovers a terrible secret about their master.",
    )

    print("📝 Production Brief:")
    print(f"   Type: {brief.production_type.value}")
    print(f"   Genre: {brief.genre.value}")
    print(f"   Inspiration: {brief.inspiration}\n")

    # 5. BATCH PRODUCTION
    print("🚀 Starting batch production...\n")
    print("NOTE: Agents are placeholders in this foundation version.")
    print("      Real narrative generation will be added in next iteration.\n")

    output = await orchestrator.produce_narrative(brief, show_progress=True)

    # 6. Results
    print("\n✅ Production complete!")
    print(f"\nOutput directory: {output.output_dir}")
    print(f"Files:")
    for name, path in output.files.items():
        print(f"  - {name}: {path}")

    print(f"\nCost: ${output.total_cost_usd:.2f} USD")
    print(f"Tokens: {output.total_tokens:,}")
    print(f"Time: {output.generation_time_seconds:.1f}s")

    print("\n═══════════════════════════════════════════")


if __name__ == "__main__":
    # Run batch production
    asyncio.run(main())
