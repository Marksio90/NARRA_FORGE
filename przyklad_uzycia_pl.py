"""
NARRA_FORGE - Kompletny Przykład Użycia Po Polsku

Ten skrypt demonstruje pełne użycie systemu NARRA_FORGE
do generowania narracji wysokiej jakości w języku polskim.
"""
import asyncio
import os
from pathlib import Path

from narra_forge.core.config import get_default_config
from narra_forge.core.orchestrator import NarrativeOrchestrator
from narra_forge.core.types import PipelineStage
from narra_forge.memory.base import SQLiteMemorySystem

# Import wszystkich agentów (etapy 1-10)
from narra_forge.agents.brief_interpreter import BriefInterpreterAgent
from narra_forge.agents.world_architect import WorldArchitectAgent
from narra_forge.agents.character_architect import CharacterArchitectAgent
from narra_forge.agents.structure_designer import StructureDesignerAgent
from narra_forge.agents.segment_planner import SegmentPlannerAgent
from narra_forge.agents.sequential_generator import SequentialGeneratorAgent
from narra_forge.agents.coherence_validator import CoherenceValidatorAgent
from narra_forge.agents.language_stylizer import LanguageStylerAgent
from narra_forge.agents.editorial_reviewer import EditorialReviewerAgent
from narra_forge.agents.output_processor import OutputProcessorAgent

# Import backendów modeli
from narra_forge.models.backend import ModelOrchestrator
from narra_forge.models.openai_backend import OpenAIBackend
from narra_forge.models.anthropic_backend import AnthropicBackend


async def main():
    """
    Główna funkcja demonstracyjna.

    Pokazuje kompletny proces od zlecenia do gotowej narracji.
    """

    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║                    NARRA_FORGE                            ║
    ║                                                           ║
    ║        Autonomiczny Wieloświatowy System Generowania      ║
    ║           Narracji Klasy Absolutnej                       ║
    ║                                                           ║
    ║                    [PL VERSION]                           ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # ========================================================================
    # KROK 1: Konfiguracja
    # ========================================================================
    print("\n[1/6] Ładowanie konfiguracji...")

    config = get_default_config()

    # Sprawdź klucz API
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  UWAGA: Brak OPENAI_API_KEY w zmiennych środowiskowych!")
        print("   Ustaw klucz komendą: export OPENAI_API_KEY='twój-klucz'")
        print("   Lub utwórz plik .env z linią: OPENAI_API_KEY=twój-klucz")
        print("\n   Pobierz klucz: https://platform.openai.com/api-keys")
        return

    # ========================================================================
    # KROK 2: Inicjalizacja backendów modeli
    # ========================================================================
    print("[2/6] Inicjalizacja backendów modeli...")

    backends = {}

    # Zainicjalizuj backendy OpenAI (GŁÓWNE)
    for model_name, model_config in config.models.items():
        if model_config.provider == "openai":
            backends[model_name] = OpenAIBackend(model_config.__dict__)
            print(f"  ✓ {model_name}: {model_config.model_name}")

    # Opcjonalnie: Zainicjalizuj backendy Anthropic (backup)
    if os.getenv("ANTHROPIC_API_KEY"):
        for model_name, model_config in config.models.items():
            if model_config.provider == "anthropic":
                backends[model_name] = AnthropicBackend(model_config.__dict__)
                print(f"  ✓ {model_name}: {model_config.model_name} (backup)")

    model_orchestrator = ModelOrchestrator(
        backends=backends,
        default=config.default_model
    )

    # ========================================================================
    # KROK 3: Inicjalizacja orchestratora
    # ========================================================================
    print("[3/6] Inicjalizacja orchestratora narracyjnego...")

    orchestrator = NarrativeOrchestrator(config)
    orchestrator.model_orchestrator = model_orchestrator

    memory_system = orchestrator.memory_system

    # ========================================================================
    # KROK 4: Rejestracja wszystkich agentów (10 etapów)
    # ========================================================================
    print("[4/6] Rejestracja agentów pipeline'u...")

    # Etap 1: Interpretacja zlecenia (analiza - tani model)
    brief_agent = BriefInterpreterAgent(
        name="InterpretatorZlecenia",
        model_orchestrator=model_orchestrator,
        memory_system=memory_system,
        config={"preferred_model": "gpt-3.5-turbo"}  # Tani i wystarczający
    )
    orchestrator.register_agent(PipelineStage.BRIEF_INTERPRETATION, brief_agent)

    # Etap 2: Architektura świata (kreatywność - dobry model)
    world_agent = WorldArchitectAgent(
        name="ArchitektSwiata",
        model_orchestrator=model_orchestrator,
        memory_system=memory_system,
        config={"preferred_model": "gpt-4-turbo", "temperature": 0.8}  # Kreatywny
    )
    orchestrator.register_agent(PipelineStage.WORLD_ARCHITECTURE, world_agent)

    # Etap 3: Architektura postaci (złożoność - najlepszy model)
    character_agent = CharacterArchitectAgent(
        name="ArchitektPostaci",
        model_orchestrator=model_orchestrator,
        memory_system=memory_system,
        config={"preferred_model": "gpt-4", "temperature": 0.8}  # Najlepsza jakość
    )
    orchestrator.register_agent(PipelineStage.CHARACTER_ARCHITECTURE, character_agent)

    # Etap 4: Projektowanie struktury (planowanie - średni model)
    structure_agent = StructureDesignerAgent(
        name="ProjektantStruktury",
        model_orchestrator=model_orchestrator,
        memory_system=memory_system,
        config={"preferred_model": "gpt-4-turbo"}  # Dobry balans
    )
    orchestrator.register_agent(PipelineStage.NARRATIVE_STRUCTURE, structure_agent)

    # Etap 5: Planowanie segmentów (szczegóły - średni model)
    planner_agent = SegmentPlannerAgent(
        name="PlanistaSeg mentow",
        model_orchestrator=model_orchestrator,
        memory_system=memory_system,
        config={"preferred_model": "gpt-4-turbo"}  # Dobry balans
    )
    orchestrator.register_agent(PipelineStage.SEGMENT_PLANNING, planner_agent)

    # Etap 6: Generacja sekwencyjna (pisanie - najlepszy model!)
    generator_agent = SequentialGeneratorAgent(
        name="GeneratorSekwencyjny",
        model_orchestrator=model_orchestrator,
        memory_system=memory_system,
        config={"preferred_model": "gpt-4", "temperature": 0.85}  # Kreatywność max
    )
    orchestrator.register_agent(PipelineStage.SEQUENTIAL_GENERATION, generator_agent)

    # Etap 7: Walidacja koherencji (analiza - tani model)
    validator_agent = CoherenceValidatorAgent(
        name="WalidatorKoherencji",
        model_orchestrator=model_orchestrator,
        memory_system=memory_system,
        config={"preferred_model": "gpt-3.5-turbo", "temperature": 0.3}  # Precyzja
    )
    orchestrator.register_agent(PipelineStage.COHERENCE_CONTROL, validator_agent)

    # Etap 8: Stylizacja językowa (jakość języka - dobry model)
    styler_agent = LanguageStylerAgent(
        name="StylizatorJezyka",
        model_orchestrator=model_orchestrator,
        memory_system=memory_system,
        config={"preferred_model": "gpt-4-turbo", "temperature": 0.7}  # Dobra jakość
    )
    orchestrator.register_agent(PipelineStage.LANGUAGE_STYLIZATION, styler_agent)

    # Etap 9: Redakcja wydawnicza (finalne poprawki - średni model)
    editor_agent = EditorialReviewerAgent(
        name="RedaktorWydawniczy",
        model_orchestrator=model_orchestrator,
        memory_system=memory_system,
        config={"preferred_model": "gpt-4-turbo", "temperature": 0.6}  # Balans
    )
    orchestrator.register_agent(PipelineStage.EDITORIAL_REVIEW, editor_agent)

    # Etap 10: Przetwarzanie wyjścia (formatowanie - tani model)
    output_agent = OutputProcessorAgent(
        name="ProcesorWyjscia",
        model_orchestrator=model_orchestrator,
        memory_system=memory_system,
        config={"preferred_model": "gpt-3.5-turbo"}  # Proste zadanie
    )
    orchestrator.register_agent(PipelineStage.FINAL_OUTPUT, output_agent)

    print("  ✓ Zarejestrowano wszystkie 10 agentów")

    # ========================================================================
    # KROK 5: Definicja zlecenia narracyjnego
    # ========================================================================
    print("\n[5/6] System gotowy do produkcji narracyjnej\n")

    # Przykładowe zlecenie - mroczne science fiction
    zlecenie_narracyjne = """
Stwórz mroczne opowiadanie science fiction osadzone
w umierającym systemie gwiezdnym.

FABUŁA:
Główny bohater to ostatni pilot transportowy w systemie,
który przez dziesięciolecia woził kolonistów i zasoby między
wygasającymi stacjami orbitalnymi. Większość ludzkości już
ewakuowała się lub wymarła.

Podczas rutynowego lotu odkrywa tajemniczy ładunek,
który nie powinien tam być - coś, co może ocalić
pozostałych przy życiu ludzi... albo definitywnie
ich zniszczyć.

Musi podjąć decyzję, którą nikt nie powinien
podejmować w samotności.

WYMAGANIA:
- Forma: opowiadanie (około 5000 słów)
- Ton: mroczny, filozoficzny, z nutą nadziei
- Tematy: samotność, odpowiedzialność, cena przetrwania,
  moralność w skrajnych warunkach
- Styl: introspektywny, ale z momentami napięcia
- Zakończenie: niejednoznaczne, ale znaczące

WAŻNE:
- Głęboka psychologia głównego bohatera
- Realistyczna wizja umierającego systemu
- Nie ma łatwych odpowiedzi
- Decyzja musi mieć wagę
"""

    print("╔═══════════════════════════════════════════════════════════╗")
    print("║ ZLECENIE NARRACYJNE:                                      ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(zlecenie_narracyjne)
    print("\n" + "="*60 + "\n")

    # ========================================================================
    # KROK 6: Uruchomienie produkcji
    # ========================================================================
    print("[6/6] Rozpoczynam produkcję narracji...\n")

    # URUCHOM PIPELINE
    wynik = await orchestrator.produce_narrative(zlecenie_narracyjne)

    # ========================================================================
    # WYNIKI
    # ========================================================================
    print("\n" + "="*60)
    print("="*60)

    if wynik["success"]:
        print("\n✅ PRODUKCJA ZAKOŃCZONA SUKCESEM\n")

        print(f"ID Projektu: {wynik['project_id']}")
        print(f"Czas trwania: {wynik['duration_seconds']:.2f}s")

        # Metadane
        if "metadata" in wynik:
            meta = wynik["metadata"]

            if "brief" in meta:
                brief = meta["brief"]
                print(f"\n📋 BRIEF:")
                print(f"   Forma: {brief.form.value}")
                print(f"   Gatunek: {brief.genre.value}")
                print(f"   Skala świata: {brief.world_scale}")

            if "world" in meta:
                world = meta["world"]
                print(f"\n🌍 ŚWIAT:")
                print(f"   Nazwa: {world.name}")
                print(f"   Temat: {world.existential_theme}")
                print(f"   Konflikt: {world.core_conflict}")

            if "characters" in meta:
                characters = meta["characters"]
                print(f"\n👥 POSTACIE ({len(characters)}):")
                for char in characters:
                    print(f"   - {char.name}")
                    print(f"     Trajektoria: {char.internal_trajectory}")

        # Wyjście
        if "output" in wynik:
            output = wynik["output"]
            if isinstance(output, dict):
                print(f"\n📁 PLIKI WYJŚCIOWE:")
                if "text_file" in output:
                    print(f"   Tekst: {output['text_file']}")
                if "audiobook_file" in output:
                    print(f"   Audiobook: {output['audiobook_file']}")
                if "metadata_file" in output:
                    print(f"   Metadane: {output['metadata_file']}")

                # Statystyki
                if "full_text" in output:
                    text = output["full_text"]
                    words = len(text.split())
                    chars = len(text)
                    print(f"\n📊 STATYSTYKI:")
                    print(f"   Słowa: {words:,}")
                    print(f"   Znaki: {chars:,}")

        print("\n" + "="*60)
        print("System NARRA_FORGE zakończył pracę pomyślnie.")
        print("="*60 + "\n")

    else:
        print("\n❌ PRODUKCJA ZAKOŃCZONA NIEPOWODZENIEM\n")
        print(f"Błąd: {wynik.get('error')}")
        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # Uruchom async main
    print("Uruchamianie NARRA_FORGE...\n")
    asyncio.run(main())
