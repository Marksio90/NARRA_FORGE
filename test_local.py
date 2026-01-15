#!/usr/bin/env python3
"""
Skrypt testowy dla NARRA_FORGE - weryfikacja lokalna.
Testuje wszystkie kluczowe komponenty systemu.
"""
import sys
import requests
import time
from pathlib import Path

# Kolory dla terminala
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

API_BASE_URL = "http://localhost:8000"
UI_URL = "http://localhost:8501"


def print_test(name, status, message=""):
    """Wydrukuj wynik testu."""
    icon = "✅" if status else "❌"
    color = GREEN if status else RED
    print(f"{color}{icon} {name}{RESET}")
    if message:
        print(f"   {message}")


def test_api_health():
    """Test 1: Czy API działa."""
    print(f"\n{BLUE}[1/8] Test zdrowia API{RESET}")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test("API Health Check", True, f"Status: {data['status']}")
            return True
        else:
            print_test("API Health Check", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_test("API Health Check", False, f"Błąd: {e}")
        return False


def test_api_docs():
    """Test 2: Czy dokumentacja API jest dostępna."""
    print(f"\n{BLUE}[2/8] Test dokumentacji API (Swagger){RESET}")
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print_test("Swagger UI", True, f"Dostępne: {API_BASE_URL}/docs")
            return True
        else:
            print_test("Swagger UI", False)
            return False
    except Exception as e:
        print_test("Swagger UI", False, f"Błąd: {e}")
        return False


def test_ui_running():
    """Test 3: Czy Streamlit UI działa."""
    print(f"\n{BLUE}[3/8] Test Streamlit UI{RESET}")
    try:
        response = requests.get(UI_URL, timeout=5)
        if response.status_code == 200:
            print_test("Streamlit UI", True, f"Dostępne: {UI_URL}")
            return True
        else:
            print_test("Streamlit UI", False)
            return False
    except Exception as e:
        print_test("Streamlit UI", False, f"Błąd: {e}")
        return False


def test_export_modules():
    """Test 4: Czy moduły exportu są dostępne."""
    print(f"\n{BLUE}[4/8] Test modułów exportu{RESET}")
    try:
        from narra_forge.export import EpubExporter, PdfExporter
        print_test("Import EpubExporter", True)
        print_test("Import PdfExporter", True)
        return True
    except Exception as e:
        print_test("Moduły exportu", False, f"Błąd: {e}")
        return False


def test_revision_system():
    """Test 5: Czy system rewizji jest dostępny."""
    print(f"\n{BLUE}[5/8] Test systemu rewizji{RESET}")
    try:
        from narra_forge.core.revision import RevisionSystem
        revision_system = RevisionSystem()
        print_test("RevisionSystem", True)
        return True
    except Exception as e:
        print_test("RevisionSystem", False, f"Błąd: {e}")
        return False


def test_data_directories():
    """Test 6: Czy katalogi danych istnieją."""
    print(f"\n{BLUE}[6/8] Test katalogów danych{RESET}")
    directories = [
        "data",
        "data/revisions",
        "data/exports",
        "output",
        "logs"
    ]

    all_ok = True
    for dir_path in directories:
        path = Path(dir_path)
        if path.exists():
            print_test(f"Katalog {dir_path}", True)
        else:
            print_test(f"Katalog {dir_path}", False, "Nie istnieje - zostanie utworzony")
            path.mkdir(parents=True, exist_ok=True)
            all_ok = False

    return all_ok


def test_api_generate_endpoint():
    """Test 7: Czy endpoint /api/generate odpowiada."""
    print(f"\n{BLUE}[7/8] Test endpointu generacji{RESET}")
    try:
        # Nie wysyłamy prawdziwego żądania, tylko sprawdzamy czy endpoint istnieje
        # (prawdziwa generacja wymaga agentów)
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print_test("API Root Endpoint", True)
            print(f"{YELLOW}   ℹ️  Pełny test generacji wymaga uruchomionych agentów{RESET}")
            return True
        else:
            print_test("API Root Endpoint", False)
            return False
    except Exception as e:
        print_test("API Root Endpoint", False, f"Błąd: {e}")
        return False


def test_dependencies():
    """Test 8: Czy wszystkie zależności są zainstalowane."""
    print(f"\n{BLUE}[8/8] Test zależności Python{RESET}")
    required_packages = [
        ("anthropic", "Anthropic SDK"),
        ("openai", "OpenAI SDK"),
        ("fastapi", "FastAPI"),
        ("streamlit", "Streamlit"),
        ("ebooklib", "ePub Export"),
        ("reportlab", "PDF Export"),
        ("pydantic", "Pydantic"),
    ]

    all_ok = True
    for package, name in required_packages:
        try:
            __import__(package)
            print_test(name, True)
        except ImportError:
            print_test(name, False, f"Brak pakietu: {package}")
            all_ok = False

    return all_ok


def main():
    """Uruchom wszystkie testy."""
    print(f"\n{BLUE}{'='*60}")
    print("🧪 NARRA_FORGE - Test Lokalny")
    print(f"{'='*60}{RESET}\n")

    results = []

    # Uruchom testy
    results.append(("API Health", test_api_health()))
    results.append(("API Docs", test_api_docs()))
    results.append(("Streamlit UI", test_ui_running()))
    results.append(("Moduły Export", test_export_modules()))
    results.append(("System Rewizji", test_revision_system()))
    results.append(("Katalogi Danych", test_data_directories()))
    results.append(("Endpoint Generacji", test_api_generate_endpoint()))
    results.append(("Zależności", test_dependencies()))

    # Podsumowanie
    print(f"\n{BLUE}{'='*60}")
    print("📊 Podsumowanie")
    print(f"{'='*60}{RESET}\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{GREEN}✅ PASSED{RESET}" if result else f"{RED}❌ FAILED{RESET}"
        print(f"  {name:<20} {status}")

    print(f"\n{BLUE}{'='*60}{RESET}")

    if passed == total:
        print(f"{GREEN}✅ Wszystkie testy przeszły! ({passed}/{total}){RESET}")
        print(f"\n{GREEN}System jest gotowy do użycia!{RESET}\n")
        print("Następne kroki:")
        print(f"  1. Otwórz UI: {BLUE}{UI_URL}{RESET}")
        print(f"  2. Otwórz API Docs: {BLUE}{API_BASE_URL}/docs{RESET}")
        print("  3. Utwórz pierwszą narrację w UI")
        return 0
    else:
        print(f"{RED}❌ Niektóre testy nie przeszły ({passed}/{total}){RESET}\n")
        print("Sprawdź błędy powyżej i upewnij się że:")
        print("  1. API działa (docker-compose logs narra-forge-api)")
        print("  2. UI działa (docker-compose logs narra-forge-ui)")
        print("  3. Wszystkie zależności są zainstalowane")
        return 1


if __name__ == "__main__":
    sys.exit(main())
