"""Tests for embedding service."""

import pytest

from services.embeddings import EmbeddingService


def test_validate_summary_ok() -> None:
    """Test that valid summary passes validation."""
    summary = " ".join(["word"] * 100)  # 100 words
    EmbeddingService.validate_summary(summary)  # Should not raise


def test_validate_summary_too_long() -> None:
    """Test that too long summary raises error."""
    summary = " ".join(["word"] * 1000)  # 1000 words (> 500 max)

    with pytest.raises(ValueError, match="Summary too long"):
        EmbeddingService.validate_summary(summary)


def test_validate_summary_prevents_full_text() -> None:
    """Test that validation prevents full text injection."""
    # Simulate full prose (e.g., 2000 words)
    full_text = " ".join(["word"] * 2000)

    with pytest.raises(ValueError, match="Only summaries allowed"):
        EmbeddingService.validate_summary(full_text)
