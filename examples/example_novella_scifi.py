#!/usr/bin/env python3
"""
Example: Novella Production (Sci-Fi)

Demonstracja produkcji noweli science fiction (10k-40k słów).
"""
import asyncio

from narra_forge import BatchOrchestrator, NarraForgeConfig
from narra_forge.core.types import Genre, ProductionBrief, ProductionType


async def main():
    """Produce a sci-fi novella"""

    config = NarraForgeConfig()
    orchestrator = BatchOrchestrator(config)
    await orchestrator._ensure_memory_initialized()

    brief = ProductionBrief(
        production_type=ProductionType.NOVELLA,
        genre=Genre.SCIFI,
        inspiration="""
        Rok 2247. Pierwszy kontakt z obcą inteligencją nie przyszedł
        przez radio ani statki kosmiczne. Przyszedł przez algorytm.

        Dr Eva Chen odkrywa, że kwantowy komputer w CERN nie tylko
        rozwiązuje równania - komunikuje się z czymś z drugiej strony
        rzeczywistości. Odpowiedzi, które generuje, są zbyt precyzyjne.
        Zbyt dobre. Jakby ktoś... pomagał.

        Ale każda odpowiedź kosztuje. Każde zapytanie otwiera granicę
        odrobinę szerzej. I coś zaczyna przenikać.
        """,
    )

    print("\n" + "="*60)
    print("  NARRA_FORGE - Example: Novella Production (Sci-Fi)")
    print("="*60)
    print(f"\nProdukcja: {brief.production_type.value}")
    print(f"Gatunek: {brief.genre.value}")
    print(f"Target: 10k-40k words")
    print("\nUruchamiam produkcję...")
    print("[dim]To może potrwać 5-15 minut...[/]\n")

    # Run production
    output = await orchestrator.produce_narrative(
        brief=brief,
        show_progress=True
    )

    # Results
    print("\n" + "="*60)
    print("  PRODUKCJA ZAKOŃCZONA")
    print("="*60)
    print(f"\nJob ID: {output.job_id}")
    print(f"Word count: {output.word_count:,}")
    print(f"Cost: ${output.total_cost_usd:.2f} USD")
    print(f"Time: {output.generation_time_seconds/60:.1f} minutes")
    print(f"\nSwiat: {output.world.name if output.world else 'N/A'}")
    print(f"Postacie: {len(output.characters)}")
    print(f"Segmenty: {len(output.segments)}")
    print(f"\nOutput: {output.output_dir}")

    print("\n✓ Novella gotowa!\n")


if __name__ == "__main__":
    asyncio.run(main())
