#!/usr/bin/env python3
"""
NARRA_FORGE CLI - Command Line Interface

Simple, production-focused interface for batch narrative production.

Usage:
    narra-forge                  # Interactive mode
    narra-forge --type novel --genre fantasy --inspiration "..." # Direct mode
    narra-forge --list-jobs      # List production jobs
    narra-forge --help           # Show help
"""
import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from narra_forge import BatchOrchestrator, NarraForgeConfig
from narra_forge.core.types import Genre, ProductionBrief, ProductionType

console = Console()


def print_banner():
    """Print application banner"""
    banner = """
[bold cyan]═══════════════════════════════════════════[/]
[bold cyan]        NARRA_FORGE - Batch Producer[/]
[bold cyan]═══════════════════════════════════════════[/]
[dim]Batch production engine for publishing-grade narratives[/]
[dim]Version: 2.0.0[/]
    """
    console.print(banner)


def get_production_type() -> ProductionType:
    """Interactive selection of production type"""
    console.print("\n[bold]1. TYP PRODUKCJI[/]")

    choices = {
        "1": ("short_story", "Opowiadanie (5k-10k słów)"),
        "2": ("novella", "Nowela (10k-40k słów)"),
        "3": ("novel", "Powieść (40k-120k słów)"),
        "4": ("epic_saga", "Saga (wielotomowa)"),
    }

    for key, (_, desc) in choices.items():
        console.print(f"  [{key}] {desc}")

    choice = Prompt.ask(
        "\nWybierz typ produkcji",
        choices=list(choices.keys()),
        default="1"
    )

    prod_type, _ = choices[choice]
    return ProductionType(prod_type)


def get_genre() -> Genre:
    """Interactive selection of genre"""
    console.print("\n[bold]2. GATUNEK[/]")

    choices = {
        "1": ("fantasy", "Fantasy"),
        "2": ("scifi", "Sci-Fi"),
        "3": ("horror", "Horror"),
        "4": ("thriller", "Thriller"),
        "5": ("mystery", "Mystery"),
        "6": ("drama", "Dramat"),
        "7": ("romance", "Romans"),
        "8": ("hybrid", "Hybryda gatunków"),
    }

    for key, (_, desc) in choices.items():
        console.print(f"  [{key}] {desc}")

    choice = Prompt.ask(
        "\nWybierz gatunek",
        choices=list(choices.keys()),
        default="1"
    )

    genre_val, _ = choices[choice]
    return Genre(genre_val)


def get_inspiration() -> Optional[str]:
    """Get optional inspiration from user"""
    console.print("\n[bold]3. INSPIRACJA (opcjonalnie)[/]")
    console.print("[dim]Możesz podać inspirację, pomysł, temat - lub pozostawić puste[/]")

    inspiration = Prompt.ask(
        "\nInspiracja",
        default=""
    )

    return inspiration if inspiration.strip() else None


async def run_production(
    production_type: ProductionType,
    genre: Genre,
    inspiration: Optional[str],
    config: NarraForgeConfig,
):
    """Run batch production"""

    # Create brief
    brief = ProductionBrief(
        production_type=production_type,
        genre=genre,
        inspiration=inspiration,
    )

    console.print("\n[bold cyan]═══════════════════════════════════════════[/]")
    console.print("[bold cyan]         URUCHAMIAM PRODUKCJĘ[/]")
    console.print("[bold cyan]═══════════════════════════════════════════[/]\n")

    console.print(f"[cyan]Typ:[/] {production_type.value}")
    console.print(f"[cyan]Gatunek:[/] {genre.value}")
    if inspiration:
        console.print(f"[cyan]Inspiracja:[/] {inspiration[:80]}...")
    console.print()

    # Create orchestrator
    orchestrator = await create_orchestrator(config)

    try:
        # Run production
        output = await orchestrator.produce_narrative(
            brief=brief,
            show_progress=True  # Show progress in console
        )

        return output

    except Exception as e:
        console.print(f"\n[bold red]✗ Produkcja nie powiodła się:[/] {e}\n")
        raise


async def create_orchestrator(config: NarraForgeConfig) -> BatchOrchestrator:
    """Create and initialize orchestrator"""
    orchestrator = BatchOrchestrator(config)
    await orchestrator._ensure_memory_initialized()
    return orchestrator


async def list_jobs(config: NarraForgeConfig, status: Optional[str] = None):
    """List production jobs"""
    from narra_forge.memory import MemorySystem

    memory = MemorySystem(config)
    await memory.initialize()

    jobs = await memory.list_jobs(status=status, limit=20)

    if not jobs:
        console.print("\n[dim]Brak zadań do wyświetlenia[/]\n")
        return

    table = Table(title="Historia Produkcji")
    table.add_column("Job ID", style="cyan")
    table.add_column("Typ", style="green")
    table.add_column("Gatunek", style="yellow")
    table.add_column("Status", style="magenta")
    table.add_column("Koszt", style="red")
    table.add_column("Data", style="dim")

    for job in jobs:
        import json
        brief = json.loads(job.get("brief", "{}"))

        table.add_row(
            job["job_id"][:12],
            brief.get("production_type", "unknown"),
            brief.get("genre", "unknown"),
            job["status"],
            f"${job.get('cost_usd', 0):.2f}",
            job.get("created_at", "")[:10],
        )

    console.print()
    console.print(table)
    console.print()


@click.command()
@click.option("--type", "prod_type", type=click.Choice([t.value for t in ProductionType]), help="Typ produkcji")
@click.option("--genre", type=click.Choice([g.value for g in Genre]), help="Gatunek")
@click.option("--inspiration", help="Inspiracja / pomysł")
@click.option("--list-jobs", "list_jobs_flag", is_flag=True, help="Lista zadań produkcyjnych")
@click.option("--status", type=click.Choice(["pending", "in_progress", "completed", "failed"]), help="Filtruj po statusie")
def main(
    prod_type: Optional[str],
    genre: Optional[str],
    inspiration: Optional[str],
    list_jobs_flag: bool,
    status: Optional[str],
):
    """
    NARRA_FORGE - Batch production engine dla narracji wydawniczych.

    Tryby pracy:

    1. INTERAKTYWNY (domyślny):
       narra-forge

    2. BEZPOŚREDNI:
       narra-forge --type novel --genre fantasy --inspiration "..."

    3. LISTA ZADAŃ:
       narra-forge --list-jobs
       narra-forge --list-jobs --status completed
    """

    # Load config
    try:
        config = NarraForgeConfig()
    except Exception as e:
        console.print(f"\n[bold red]✗ Błąd konfiguracji:[/] {e}\n")
        console.print("[dim]Upewnij się, że plik .env istnieje i zawiera OPENAI_API_KEY[/]\n")
        sys.exit(1)

    # List jobs mode
    if list_jobs_flag:
        asyncio.run(list_jobs(config, status))
        return

    # Banner
    print_banner()

    # Interactive or direct mode
    if prod_type and genre:
        # Direct mode
        production_type = ProductionType(prod_type)
        genre_obj = Genre(genre)

        console.print(f"\n[dim]Tryb bezpośredni: {prod_type} / {genre}[/]")

        output = asyncio.run(run_production(
            production_type=production_type,
            genre=genre_obj,
            inspiration=inspiration,
            config=config,
        ))

    else:
        # Interactive mode
        console.print("\n[dim]Tryb interaktywny - skonfiguruj produkcję:[/]")

        production_type = get_production_type()
        genre_obj = get_genre()
        inspiration = get_inspiration()

        # Confirm
        console.print("\n[bold]4. POTWIERDZENIE[/]")
        console.print(f"  Typ: {production_type.value}")
        console.print(f"  Gatunek: {genre_obj.value}")
        if inspiration:
            console.print(f"  Inspiracja: {inspiration[:80]}")

        if not Confirm.ask("\nUruchomić produkcję?", default=True):
            console.print("\n[dim]Anulowano[/]\n")
            return

        output = asyncio.run(run_production(
            production_type=production_type,
            genre=genre_obj,
            inspiration=inspiration,
            config=config,
        ))


if __name__ == "__main__":
    main()
