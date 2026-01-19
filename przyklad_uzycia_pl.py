"""
NARRA_FORGE - Przykład Użycia (Polski)

Kompletny przykład generowania narracji za pomocą NARRA_FORGE.
"""

import asyncio
import logging
from narra_forge import (
    NarrativeOrchestrator,
    get_default_config,
)

# Konfiguruj logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


async def przyklad_podstawowy():
    """
    Podstawowy przykład: Wygeneruj opowiadanie z prostego zlecenia
    """
    print("=" * 80)
    print("PRZYKŁAD 1: Podstawowe Opowiadanie")
    print("=" * 80)

    # Utwórz config i orchestrator
    config = get_default_config()
    orchestrator = NarrativeOrchestrator(config)

    # Zlecenie użytkownika (dowolny język naturalny!)
    zlecenie = """
    Napisz mroczne opowiadanie fantasy o młodym alchemiku,
    który odkrywa straszną tajemnicę swojego mistrza.

    Forma: opowiadanie (około 5000-8000 słów)
    Ton: mroczny, moralnie złożony
    Setting: średniowieczne miasto z magią
    """

    # GENERUJ!
    print(f"\n📝 Zlecenie:\n{zlecenie}\n")
    print("🚀 Rozpoczynam produkcję narracji...\n")

    wynik = await orchestrator.produce_narrative(zlecenie)

    # Wyniki
    if wynik.success:
        print("\n✅ SUKCES! Narracja wygenerowana!")
        print(f"📊 Statystyki:")
        print(f"   - Liczba słów: {wynik.total_word_count:,}")
        print(f"   - Liczba rozdziałów: {wynik.total_chapters}")
        print(f"   - Czas generacji: {wynik.generation_time_seconds:.1f}s")
        print(f"   - Wynik koherencji: {wynik.quality_score:.2%}")
        print(f"\n📁 Pliki:")
        for nazwa, sciezka in wynik.output_files.items():
            print(f"   - {nazwa}: {sciezka}")

        print(f"\n📖 Początek tekstu (pierwsze 500 znaków):")
        print("-" * 80)
        print(wynik.full_text[:500] + "...")
        print("-" * 80)

    else:
        print("\n❌ BŁĄD! Generacja nie powiodła się:")
        for blad in wynik.errors:
            print(f"   - {blad}")


async def przyklad_nowela():
    """
    Przykład 2: Dłuższa forma - nowela
    """
    print("\n" + "=" * 80)
    print("PRZYKŁAD 2: Nowela Sci-Fi")
    print("=" * 80)

    config = get_default_config()
    orchestrator = NarrativeOrchestrator(config)

    zlecenie = """
    Nowela science fiction o samotnej stacji kosmicznej,
    gdzie AI zaczyna rozwijać świadomość.

    Długość: nowela (20,000-30,000 słów)
    Ton: filozoficzny, refleksyjny
    Temat: Czym jest świadomość? Czy AI może być "żywe"?
    """

    print(f"\n📝 Zlecenie:\n{zlecenie}\n")
    print("🚀 Rozpoczynam produkcję noweli...\n")

    wynik = await orchestrator.produce_narrative(zlecenie)

    if wynik.success:
        print("\n✅ Nowela gotowa!")
        print(f"📊 {wynik.total_word_count:,} słów w {wynik.total_chapters} rozdziałach")
        print(f"📁 Tekst: {wynik.output_files['text_file']}")
    else:
        print(f"\n❌ Błąd: {wynik.errors}")


async def przyklad_thriller():
    """
    Przykład 3: Thriller psychologiczny
    """
    print("\n" + "=" * 80)
    print("PRZYKŁAD 3: Thriller Psychologiczny")
    print("=" * 80)

    config = get_default_config()
    orchestrator = NarrativeOrchestrator(config)

    zlecenie = """
    Thriller psychologiczny o detektywie ścigającym seryjnego mordercę,
    który okazuje się być jego dawnym partnerem.

    Forma: opowiadanie (10,000 słów)
    Ton: suspenseful, dark
    Setting: współczesne Warszawa
    POV: pierwsza osoba (perspektywa detektywa)
    """

    print(f"\n📝 Zlecenie:\n{zlecenie}\n")

    wynik = await orchestrator.produce_narrative(zlecenie)

    if wynik.success:
        print("\n✅ Thriller gotowy!")
        print(f"🌍 Świat: {wynik.world.name}")
        print(f"👥 Postacie: {[c.name for c in wynik.characters]}")
        print(f"📖 Wynik koherencji: {wynik.coherence_report.overall_score:.2%}")


async def przyklad_uniwersalne_api():
    """
    Przykład 4: UNIWERSALNE API - system dostosowuje się automatycznie
    """
    print("\n" + "=" * 80)
    print("PRZYKŁAD 4: UNIWERSALNE API - Różne Formaty")
    print("=" * 80)

    config = get_default_config()
    orchestrator = NarrativeOrchestrator(config)

    # Test 1: Flash fiction
    print("\n📝 Test 1: Flash Fiction (ultra krótka forma)")
    wynik1 = await orchestrator.produce_narrative(
        "Krótkie opowiadanie (500 słów) o ostatnim dniu na Ziemi. Poetycki ton."
    )
    print(f"   ✅ Wygenerowano: {wynik1.total_word_count} słów")

    # Test 2: Auto-detekcja gatunku
    print("\n📝 Test 2: Auto-detekcja (system sam określi gatunek i formę)")
    wynik2 = await orchestrator.produce_narrative(
        "Historia o dziewczynie, która odkrywa, że może podróżować w czasie poprzez sny."
    )
    print(f"   ✅ Wykryto: {wynik2.brief.genre.value} / {wynik2.brief.form.value}")
    print(f"   ✅ Wygenerowano: {wynik2.total_word_count} słów")

    # Test 3: Hybrid gatunek
    print("\n📝 Test 3: Hybrydowy gatunek (fantasy + romance)")
    wynik3 = await orchestrator.produce_narrative(
        """
        Nowela romantyczna z elementami fantasy.
        Czarodziejka zakochuje się w śmiertelniku, ale ich związek jest zabroniony.
        Długość: 20,000 słów.
        """
    )
    print(f"   ✅ Wygenerowano: {wynik3.total_word_count} słów")


async def main():
    """
    Główna funkcja - uruchom wszystkie przykłady
    """
    print("\n")
    print("🚀" * 40)
    print("NARRA_FORGE - Przykłady Użycia")
    print("Autonomiczny Wieloświatowy System Generowania Narracji")
    print("🚀" * 40)

    # Sprawdź, czy klucz API jest ustawiony
    import os
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️ UWAGA: Brak klucza API!")
        print("Ustaw OPENAI_API_KEY lub ANTHROPIC_API_KEY w .env lub export")
        print("Przykład: export OPENAI_API_KEY='sk-proj-...'")
        return

    # Uruchom przykłady (możesz zakomentować niepotrzebne)
    try:
        # await przyklad_podstawowy()
        # await przyklad_nowela()
        # await przyklad_thriller()
        await przyklad_uniwersalne_api()

    except KeyboardInterrupt:
        print("\n\n⏸️ Przerwano przez użytkownika")
    except Exception as e:
        print(f"\n\n❌ Błąd: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("✅ Przykłady zakończone!")
    print("=" * 80)


if __name__ == "__main__":
    # Uruchom async main
    asyncio.run(main())
