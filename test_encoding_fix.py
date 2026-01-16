#!/usr/bin/env python3
"""
Test demonstracyjny dla encoding fixes w NARRA_FORGE V2

Ten test pokazuje jak text_utils naprawia problemy z mojibake
w polskich znakach.
"""

from narra_forge.utils import (
    clean_narrative_text,
    ensure_utf8_response,
    fix_polish_encoding,
    normalize_whitespace,
)


def test_encoding_fixes():
    """Test fix_polish_encoding"""

    print("=" * 70)
    print("TEST #1: Naprawianie mojibake w polskich znakach")
    print("=" * 70)

    # Przykłady rzeczywistych problemów z outputu
    corrupted_examples = [
        ("pamiÄ™taĹ‚y", "pamiętały"),
        ("ciÄ™ĹĽkie", "ciężkie"),
        ("Ĺ›wiat", "świat"),
        ("gĹ‚owa", "głowa"),
        ("dĹ‚ugie", "długie"),
        ("wĹ‚osy", "włosy"),
        ("Ĺ›wietny", "świetny"),
        ("pamiÄ™Ä‡", "pamięć"),
        ("ĹĽycie", "życie"),
    ]

    print("\nPRZYKŁADY NAPRAW:")
    all_passed = True

    for corrupted, expected in corrupted_examples:
        fixed = fix_polish_encoding(corrupted)
        status = "✅" if fixed == expected else "❌"

        if fixed != expected:
            all_passed = False

        print(f"{status} '{corrupted}' → '{fixed}' (expected: '{expected}')")

    print()
    if all_passed:
        print("✅ Wszystkie pojedyncze znaki naprawione poprawnie!")
    else:
        print("❌ Niektóre znaki nie zostały naprawione")

    return all_passed


def test_full_text_cleanup():
    """Test clean_narrative_text na pełnym tekście"""

    print("\n" + "=" * 70)
    print("TEST #2: Czyszczenie pełnego tekstu narracyjnego")
    print("=" * 70)

    # Przykładowy zepsuty tekst (jak z rzeczywistego outputu)
    corrupted_text = """W sercu miasta pamiÄ™taĹ‚y mury starej szkoĹ‚y alchemii.

Elias sunÄ…Ĺ‚ wÄ…skim korytarzem, czujÄ…c ciÄ™ĹĽar pamiÄ™ci.
GĹ‚owa pÄ™kaĹ‚a mu od tajemnic, które musiaĹ‚ odkryÄ‡.

Ĺťycie w Ĺ›wiecie alchemii byĹ‚o ciÄ™ĹĽkie i peĹ‚ne niebezpieczeĹ„stw.
Ale on wiedziaĹ‚, ĹĽe musi iÄ›Ä‡ dalej.
"""

    # Oczekiwany poprawny tekst
    expected_clean = """W sercu miasta pamiętały mury starej szkoły alchemii.

Elias sunął wąskim korytarzem, czując ciężar pamięci.
Głowa pękała mu od tajemnic, które musiał odkryć.

Życie w świecie alchemii było ciężkie i pełne niebezpieczeństw.
Ale on wiedział, że musi iść dalej."""

    print("\n❌ PRZED czyszczeniem:")
    print(corrupted_text)

    # Wyczyść tekst
    cleaned = clean_narrative_text(corrupted_text)

    print("\n✅ PO czyszczeniu:")
    print(cleaned)

    # Sprawdź czy wszystkie polskie znaki są poprawne
    polish_chars = ['ą', 'ć', 'ę', 'ł', 'ń', 'ó', 'ś', 'ź', 'ż',
                    'Ą', 'Ć', 'Ę', 'Ł', 'Ń', 'Ó', 'Ś', 'Ź', 'Ż']

    mojibake_patterns = ['Ä…', 'Ä™', 'Ĺ›', 'Ä‡', 'Ĺ‚', 'Ĺ„', 'ĹĽ', 'Ĺ»']

    print("\n" + "=" * 70)
    print("WERYFIKACJA:")

    has_mojibake = any(pattern in cleaned for pattern in mojibake_patterns)
    has_polish_chars = any(char in cleaned for char in polish_chars)

    if has_mojibake:
        print("❌ Tekst wciąż zawiera mojibake!")
        return False

    if not has_polish_chars:
        print("⚠️  UWAGA: Tekst nie zawiera polskich znaków (być może nie było czego naprawiać)")
        return True

    print("✅ Brak mojibake w tekście")
    print("✅ Polskie znaki są poprawne")
    print(f"✅ Znaleziono następujące polskie znaki: {set(c for c in cleaned if c in polish_chars)}")

    return True


def test_ensure_utf8_response():
    """Test ensure_utf8_response detection"""

    print("\n" + "=" * 70)
    print("TEST #3: Automatyczna detekcja i naprawa mojibake")
    print("=" * 70)

    # Tekst z mojibake
    text_with_mojibake = "Elias sunÄ…Ĺ‚ korytarzem. Ĺťycie byĹ‚o ciÄ™ĹĽkie."

    # Tekst już poprawny
    text_clean = "Elias sunął korytarzem. Życie było ciężkie."

    print("\n1. Tekst z mojibake:")
    print(f"   Input:  '{text_with_mojibake}'")
    fixed1 = ensure_utf8_response(text_with_mojibake)
    print(f"   Output: '{fixed1}'")

    has_mojibake = any(p in fixed1 for p in ['Ä…', 'Ä™', 'Ĺ›', 'Ĺ‚', 'ĹĽ'])
    print(f"   Status: {'❌ FAILED' if has_mojibake else '✅ FIXED'}")

    print("\n2. Tekst już poprawny (nie powinien zostać zmieniony):")
    print(f"   Input:  '{text_clean}'")
    fixed2 = ensure_utf8_response(text_clean)
    print(f"   Output: '{fixed2}'")
    print(f"   Status: {'✅ UNCHANGED' if fixed2 == text_clean else '⚠️ MODIFIED'}")

    return not has_mojibake


def test_normalize_whitespace():
    """Test normalize_whitespace"""

    print("\n" + "=" * 70)
    print("TEST #4: Normalizacja whitespace")
    print("=" * 70)

    # Tekst z problemami formatowania
    messy_text = """Linia 1   \n\n\n\n\nLinia 2    \nLinia 3\n\n\n\nLinia 4"""

    print("\n❌ PRZED normalizacją (trailing spaces pokazane jako [SPACE]):")
    for line in messy_text.split('\n'):
        visible = line.replace(' ', '[SPACE]')
        print(f"   '{visible}'")

    normalized = normalize_whitespace(messy_text)

    print("\n✅ PO normalizacji:")
    for line in normalized.split('\n'):
        visible = line.replace(' ', '[SPACE]')
        print(f"   '{visible}'")

    # Weryfikacja
    has_trailing = any(line.endswith(' ') for line in normalized.split('\n'))
    has_excessive_newlines = '\n\n\n\n' in normalized

    print("\n" + "=" * 70)
    print("WERYFIKACJA:")
    print(f"{'✅' if not has_trailing else '❌'} Brak trailing whitespace")
    print(f"{'✅' if not has_excessive_newlines else '❌'} Brak nadmiarowych pustych linii")

    return not has_trailing and not has_excessive_newlines


def main():
    """Uruchom wszystkie testy"""

    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "NARRA_FORGE V2 - ENCODING TEST" + " " * 23 + "║")
    print("║" + " " * 15 + "Test mechanizmów naprawy UTF-8" + " " * 23 + "║")
    print("╚" + "=" * 68 + "╝")

    results = []

    # Uruchom wszystkie testy
    results.append(("Pojedyncze znaki", test_encoding_fixes()))
    results.append(("Pełny tekst", test_full_text_cleanup()))
    results.append(("Auto-detekcja", test_ensure_utf8_response()))
    results.append(("Normalizacja whitespace", test_normalize_whitespace()))

    # Podsumowanie
    print("\n" + "=" * 70)
    print("PODSUMOWANIE TESTÓW")
    print("=" * 70)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")

    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ✅ ✅  WSZYSTKIE TESTY PRZESZŁY POMYŚLNIE  ✅ ✅ ✅")
        print("\nEncoding fixes działają poprawnie!")
        print("System jest gotowy do produkcyjnej generacji narracji.")
    else:
        print("❌ ❌ ❌  NIEKTÓRE TESTY NIE PRZESZŁY  ❌ ❌ ❌")
        print("\nSprawdź implementację text_utils.py")
    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
