"""
Test systemu NARRA_FORGE w kontenerze Docker.

Wykonuje podstawowe testy funkcjonalności bez rzeczywistych wywołań API.
"""
import sys
import os
from pathlib import Path

print("="*60)
print("NARRA_FORGE - Test Kontenera Docker")
print("="*60)

# Test 1: Struktura katalogów
print("\n[Test 1] Sprawdzanie struktury katalogów...")
required_dirs = ["narra_forge", "data", "output", "logs"]
for dir_name in required_dirs:
    dir_path = Path(dir_name)
    if dir_path.exists():
        print(f"  ✓ {dir_name}/ istnieje")
    else:
        print(f"  ✗ {dir_name}/ BRAK")
        sys.exit(1)

# Test 2: Import modułów
print("\n[Test 2] Sprawdzanie importów...")
try:
    from narra_forge.core.types import (
        NarrativeForm, Genre, PipelineStage,
        WorldBible, Character, ProjectBrief
    )
    print("  ✓ narra_forge.core.types")

    from narra_forge.core.config import get_default_config
    print("  ✓ narra_forge.core.config")

    from narra_forge.core.orchestrator import NarrativeOrchestrator
    print("  ✓ narra_forge.core.orchestrator")

    from narra_forge.memory.base import SQLiteMemorySystem
    print("  ✓ narra_forge.memory.base")

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
    print("  ✓ Wszystkie 10 agentów")

    from narra_forge.world.world_manager import WorldManager
    print("  ✓ narra_forge.world.world_manager")

except ImportError as e:
    print(f"  ✗ Błąd importu: {e}")
    sys.exit(1)

# Test 3: Konfiguracja
print("\n[Test 3] Sprawdzanie konfiguracji...")
try:
    config = get_default_config()
    print(f"  ✓ Konfiguracja załadowana")
    print(f"  ✓ Domyślny model: {config.default_model}")
    print(f"  ✓ Liczba modeli: {len(config.models)}")
    print(f"  ✓ Min. coherence score: {config.min_coherence_score}")
except Exception as e:
    print(f"  ✗ Błąd konfiguracji: {e}")
    sys.exit(1)

# Test 4: Zmienne środowiskowe
print("\n[Test 4] Sprawdzanie zmiennych środowiskowych...")
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    masked_key = openai_key[:8] + "..." + openai_key[-4:] if len(openai_key) > 12 else "***"
    print(f"  ✓ OPENAI_API_KEY: {masked_key} (GŁÓWNY)")
else:
    print(f"  ⚠ OPENAI_API_KEY: NIE USTAWIONY")
    print(f"    Uwaga: Bez klucza API system nie będzie mógł generować treści")
    print(f"    Pobierz klucz: https://platform.openai.com/api-keys")

anthropic_key = os.getenv("ANTHROPIC_API_KEY")
if anthropic_key:
    masked_key = anthropic_key[:8] + "..." + anthropic_key[-4:] if len(anthropic_key) > 12 else "***"
    print(f"  ✓ ANTHROPIC_API_KEY: {masked_key} (backup)")
else:
    print(f"  ℹ ANTHROPIC_API_KEY: NIE USTAWIONY (opcjonalny)")

# Test 5: System pamięci
print("\n[Test 5] Test systemu pamięci...")
try:
    db_path = Path("./data/test_memory.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)

    memory = SQLiteMemorySystem(db_path)
    print(f"  ✓ SQLiteMemorySystem zainicjalizowany")

    # Test zapisu i odczytu
    from narra_forge.memory.base import MemoryEntry
    from datetime import datetime

    test_entry = MemoryEntry(
        entry_id="test_001",
        memory_type="structural",
        world_id="test_world",
        content={"test": "data"},
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={}
    )

    memory.store(test_entry)
    retrieved = memory.retrieve("test_001")

    if retrieved and retrieved.entry_id == "test_001":
        print(f"  ✓ Zapis i odczyt z pamięci działa")
    else:
        print(f"  ✗ Problem z zapisem/odczytem pamięci")
        sys.exit(1)

    # Cleanup
    if db_path.exists():
        db_path.unlink()

except Exception as e:
    print(f"  ✗ Błąd systemu pamięci: {e}")
    sys.exit(1)

# Test 6: Typy danych
print("\n[Test 6] Test typów danych...")
try:
    # Test WorldBible
    from datetime import datetime
    world = WorldBible(
        world_id="test_world",
        name="Test World",
        created_at=datetime.now(),
        laws_of_reality={"physics": "newtonian"},
        boundaries={"spatial": "planet"},
        anomalies=[],
        core_conflict="Order vs Chaos",
        existential_theme="Meaning of existence",
        archetype_system={},
        timeline=[],
        current_state={}
    )
    print(f"  ✓ WorldBible: {world.name}")

    # Test Character
    character = Character(
        character_id="test_char",
        name="Test Character",
        world_id="test_world",
        internal_trajectory="Growth",
        contradictions=["Brave but afraid"],
        cognitive_limits=["Cannot see truth"],
        evolution_capacity=0.8,
        motivations=["Survive"],
        fears=["Death"],
        blind_spots=["Own weakness"],
        relationships={},
        current_state={}
    )
    print(f"  ✓ Character: {character.name}")

    # Test ProjectBrief
    brief = ProjectBrief(
        form=NarrativeForm.SHORT_STORY,
        genre=Genre.FANTASY,
        world_scale="intimate",
        expansion_potential="one_shot"
    )
    print(f"  ✓ ProjectBrief: {brief.form.value}, {brief.genre.value}")

except Exception as e:
    print(f"  ✗ Błąd typów danych: {e}")
    sys.exit(1)

# Podsumowanie
print("\n" + "="*60)
print("✅ WSZYSTKIE TESTY PRZESZŁY POMYŚLNIE")
print("="*60)

print(f"""
System NARRA_FORGE jest poprawnie zainstalowany i gotowy do użycia.

Struktura:
  ✓ Wszystkie moduły załadowane
  ✓ Wszystkie 10 agentów dostępne
  ✓ System pamięci działa
  ✓ Typy danych poprawne

Konfiguracja:
  ✓ Config załadowany
  ✓ {len(config.models)} modeli skonfigurowanych
  {'✓' if openai_key else '⚠'} OPENAI_API_KEY {'ustawiony (GPT-4 Turbo)' if openai_key else 'BRAK'}

Aby uruchomić pełny przykład z generacją:
  docker-compose run narra-forge python przyklad_uzycia_pl.py

Lub tryb interaktywny:
  docker-compose run narra-forge-dev bash
""")

sys.exit(0)
