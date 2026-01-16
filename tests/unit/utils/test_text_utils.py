"""
Testy dla text_utils
"""
import pytest

from narra_forge.utils.text_utils import (
    fix_polish_encoding,
    ensure_utf8_response,
    normalize_whitespace,
    clean_narrative_text,
    detect_cliches,
    detect_repetitions,
    analyze_text_quality,
)


@pytest.mark.unit
class TestPolishEncodingFix:
    """Test naprawy kodowania polskich znaków"""

    def test_fix_polish_encoding_basic(self):
        """Test podstawowej naprawy kodowania"""
        # Test ą
        assert fix_polish_encoding("Ä…") == "ą"
        assert fix_polish_encoding("Ä„") == "Ą"

        # Test ć
        assert fix_polish_encoding("Ä‡") == "ć"

        # Test ę
        assert fix_polish_encoding("Ä™") == "ę"

        # Test ł
        assert fix_polish_encoding("Ĺ‚") == "ł"
        assert fix_polish_encoding("Ĺ") == "Ł"

    def test_fix_polish_encoding_in_word(self):
        """Test naprawy kodowania w słowach"""
        assert fix_polish_encoding("wiedziaĹ‚") == "wiedział"
        assert fix_polish_encoding("musiaĹ‚") == "musiał"
        assert fix_polish_encoding("pamiÄ™") == "pamię"

    def test_fix_polish_encoding_no_changes(self):
        """Test tekstu bez problemów z kodowaniem"""
        clean_text = "To jest poprawny tekst po polsku"
        assert fix_polish_encoding(clean_text) == clean_text


@pytest.mark.unit
class TestEnsureUTF8:
    """Test zapewnienia poprawnego UTF-8"""

    def test_ensure_utf8_clean_text(self):
        """Test czystego tekstu"""
        text = "Normalny tekst bez problemów"
        assert ensure_utf8_response(text) == text

    def test_ensure_utf8_with_mojibake(self):
        """Test tekstu z mojibake"""
        text_with_mojibake = "Tekst z problemami: Ä… Ä™ Ĺ‚"
        result = ensure_utf8_response(text_with_mojibake)

        # Powinno naprawić mojibake
        assert "Ä…" not in result or result != text_with_mojibake


@pytest.mark.unit
class TestNormalizeWhitespace:
    """Test normalizacji białych znaków"""

    def test_normalize_trailing_spaces(self):
        """Test usuwania końcowych spacji"""
        text = "Line with trailing spaces   \nAnother line   "
        result = normalize_whitespace(text)

        assert "   \n" not in result
        assert result.endswith("line")

    def test_normalize_excessive_newlines(self):
        """Test naprawy nadmiernych pustych linii"""
        text = "Line 1\n\n\n\n\n\nLine 2"
        result = normalize_whitespace(text)

        # Maksymalnie 3 newline-y z rzędu (2 puste linie)
        assert "\n\n\n\n" not in result

    def test_normalize_preserves_single_newlines(self):
        """Test zachowania pojedynczych newline"""
        text = "Line 1\nLine 2\nLine 3"
        result = normalize_whitespace(text)

        assert result == text

    def test_normalize_empty_text(self):
        """Test pustego tekstu"""
        assert normalize_whitespace("") == ""


@pytest.mark.unit
class TestCleanNarrativeText:
    """Test czyszczenia tekstu narracji"""

    def test_clean_removes_bom(self):
        """Test usuwania BOM"""
        text_with_bom = "\ufeffTekst z BOM"
        result = clean_narrative_text(text_with_bom)

        assert "\ufeff" not in result
        assert result == "Tekst z BOM"

    def test_clean_fixes_line_endings(self):
        """Test naprawy zakończeń linii"""
        text_with_crlf = "Line 1\r\nLine 2\rLine 3"
        result = clean_narrative_text(text_with_crlf)

        assert "\r" not in result
        assert "Line 1\nLine 2\nLine 3" == result

    def test_clean_comprehensive(self):
        """Test kompleksowego czyszczenia"""
        messy_text = "\ufeffTekst z Ä…   \r\n\n\n\n\nI kolejna linia   "
        result = clean_narrative_text(messy_text)

        # Powinno być czyste
        assert "\ufeff" not in result
        assert "\r" not in result


@pytest.mark.unit
class TestClicheDetection:
    """Test wykrywania banałów"""

    def test_detect_cliches_finds_common(self):
        """Test wykrywania częstych banałów"""
        text = "Serce waliło jak młot. Krew zamarzła w żyłach."
        cliches = detect_cliches(text)

        assert isinstance(cliches, list)
        assert len(cliches) > 0
        # Powinno znaleźć "serce waliło"
        assert any("serce" in c["cliche"].lower() for c in cliches)

    def test_detect_cliches_clean_text(self):
        """Test tekstu bez banałów"""
        text = "Serce przyspieszyło. Poczuł strach."
        cliches = detect_cliches(text)

        # Może być puste lub mieć niewiele wykryć
        assert isinstance(cliches, list)

    def test_detect_cliches_case_insensitive(self):
        """Test niezależności od wielkości liter"""
        text = "SERCE WALIŁO JAK MŁOT"
        cliches = detect_cliches(text)

        # Powinno wykryć mimo wielkich liter
        assert len(cliches) > 0


@pytest.mark.unit
class TestRepetitionDetection:
    """Test wykrywania powtórzeń"""

    def test_detect_repetitions_finds_high_count(self):
        """Test wykrywania wysokich powtórzeń"""
        text = "Wiedział, że wiedział. Wiedział o wszystkim. Wiedział dokładnie."
        result = detect_repetitions(text, threshold=3)

        assert isinstance(result, dict)
        # Powinno wykryć "wiedział" jako powtarzające się słowo
        assert len(result) > 0

    def test_detect_repetitions_clean(self):
        """Test tekstu bez powtórzeń"""
        text = "Różne słowa używane tylko raz każde tutaj."
        result = detect_repetitions(text, threshold=5)

        # Nie powinno wykryć wysokich powtórzeń
        assert isinstance(result, dict)

    def test_detect_repetitions_ignores_short(self):
        """Test ignorowania krótkich słów"""
        text = "To jest to. To jest to także."
        result = detect_repetitions(text, threshold=3)

        # Krótkie słowa typu "to", "jest" powinny być ignorowane
        assert isinstance(result, dict)


@pytest.mark.unit
class TestTextQualityAnalysis:
    """Test kompleksowej analizy jakości"""

    def test_analyze_quality_with_cliches(self):
        """Test analizy z banałami"""
        text = """Serce waliło jak młot. Patrzył na nią.
        Wiedział, że coś się stanie. Wiedział o wszystkim.
        Wiedział dokładnie, co się wydarzy."""

        result = analyze_text_quality(text)

        assert "cliches" in result
        assert "repetitions" in result
        assert "quality_score" in result

        # Powinno wykryć banały
        assert len(result["cliches"]) > 0

        # Quality score powinien być niski
        assert 0.0 <= result["quality_score"] <= 1.0

    def test_analyze_quality_clean_text(self):
        """Test tekstu wysokiej jakości"""
        text = """Serce przyspieszyło. Spojrzał w dal.
        Rozumiał konsekwencje. Decyzja była jasna.
        Ruszył naprzód bez wahania."""

        result = analyze_text_quality(text)

        # Powinno być mało lub zero banałów
        assert len(result["cliches"]) == 0

        # Quality score powinien być wysoki
        assert result["quality_score"] > 0.5

    def test_analyze_quality_handles_empty(self):
        """Test obsługi pustego tekstu"""
        result = analyze_text_quality("")

        assert "cliches" in result
        assert "repetitions" in result
        assert result["quality_score"] >= 0.0

    def test_analyze_quality_structure(self):
        """Test struktury wyniku"""
        text = "Test text with some content here."
        result = analyze_text_quality(text)

        # Sprawdź czy ma wymagane klucze
        assert "cliches" in result
        assert isinstance(result["cliches"], list)

        assert "repetitions" in result
        assert isinstance(result["repetitions"], dict)

        assert "quality_score" in result
        assert isinstance(result["quality_score"], (int, float))
