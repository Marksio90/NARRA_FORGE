"""Unit tests for Packaging Service."""

import json
from uuid import uuid4

import pytest

from services.packaging import AudioManifest, AudioSegment, PackagingService


def test_audio_segment_creation() -> None:
    """Test AudioSegment creation."""
    segment = AudioSegment(
        segment_id="seg_001",
        text="This is a test segment with exactly ten words here now.",
        sequence_number=1,
        character_voice="narrator",
        emotion="neutral",
    )

    assert segment.segment_id == "seg_001"
    assert segment.sequence_number == 1
    assert segment.character_voice == "narrator"
    assert segment.emotion == "neutral"
    assert segment.duration_estimate > 0


def test_audio_segment_duration_estimation() -> None:
    """Test audio duration estimation."""
    # 155 words per minute = 2.58 words per second
    # 26 words / 2.58 = ~10 seconds
    text = " ".join(["word"] * 26)
    segment = AudioSegment(
        segment_id="seg_001",
        text=text,
        sequence_number=1,
    )

    # Should be approximately 10 seconds
    assert 9.0 <= segment.duration_estimate <= 11.0


def test_audio_segment_to_dict() -> None:
    """Test AudioSegment to_dict."""
    segment = AudioSegment(
        segment_id="seg_001",
        text="Test text here",
        sequence_number=1,
        character_voice="narrator",
        emotion="happy",
    )

    data = segment.to_dict()

    assert data["segment_id"] == "seg_001"
    assert data["text"] == "Test text here"
    assert data["sequence_number"] == 1
    assert data["character_voice"] == "narrator"
    assert data["emotion"] == "happy"
    assert "duration_estimate" in data
    assert data["word_count"] == 3


def test_audio_manifest_creation() -> None:
    """Test AudioManifest creation."""
    job_id = uuid4()
    manifest = AudioManifest(
        job_id=job_id,
        title="Test Story",
        author="Test Author",
        narrator="Test Narrator",
        language="pl",
        genre="fantasy",
    )

    assert manifest.job_id == job_id
    assert manifest.title == "Test Story"
    assert manifest.author == "Test Author"
    assert manifest.narrator == "Test Narrator"
    assert manifest.language == "pl"
    assert manifest.genre == "fantasy"
    assert len(manifest.segments) == 0
    assert manifest.total_duration == 0.0
    assert manifest.total_words == 0


def test_audio_manifest_add_segment() -> None:
    """Test adding segment to manifest."""
    manifest = AudioManifest(
        job_id=uuid4(),
        title="Test",
    )

    segment = AudioSegment(
        segment_id="seg_001",
        text="This is a test.",
        sequence_number=1,
    )

    manifest.add_segment(segment)

    assert len(manifest.segments) == 1
    assert manifest.total_words == 4
    assert manifest.total_duration > 0


def test_audio_manifest_add_multiple_segments() -> None:
    """Test adding multiple segments."""
    manifest = AudioManifest(
        job_id=uuid4(),
        title="Test",
    )

    segments = [
        AudioSegment(segment_id=f"seg_{i}", text=f"Segment {i} text", sequence_number=i)
        for i in range(1, 4)
    ]

    manifest.add_segments(segments)

    assert len(manifest.segments) == 3
    assert manifest.total_words == 9  # 3 segments * 3 words each


def test_audio_manifest_to_dict() -> None:
    """Test AudioManifest to_dict."""
    job_id = uuid4()
    manifest = AudioManifest(
        job_id=job_id,
        title="Test Story",
        author="Author",
        genre="fantasy",
    )

    segment = AudioSegment(
        segment_id="seg_001",
        text="Test segment.",
        sequence_number=1,
    )
    manifest.add_segment(segment)

    data = manifest.to_dict()

    assert data["job_id"] == str(job_id)
    assert data["title"] == "Test Story"
    assert data["author"] == "Author"
    assert data["genre"] == "fantasy"
    assert len(data["segments"]) == 1
    assert "metadata" in data
    assert data["metadata"]["total_segments"] == 1
    assert data["metadata"]["total_words"] == 2
    assert "created_at" in data
    assert data["version"] == "1.0"


def test_audio_manifest_metadata_calculations() -> None:
    """Test manifest metadata calculations."""
    manifest = AudioManifest(job_id=uuid4(), title="Test")

    # Add 3 segments with 10 words each
    for i in range(1, 4):
        text = " ".join(["word"] * 10)
        segment = AudioSegment(
            segment_id=f"seg_{i}",
            text=text,
            sequence_number=i,
        )
        manifest.add_segment(segment)

    data = manifest.to_dict()
    metadata = data["metadata"]

    assert metadata["total_segments"] == 3
    assert metadata["total_words"] == 30
    assert metadata["total_duration_seconds"] > 0
    assert metadata["total_duration_minutes"] > 0
    assert metadata["average_segment_duration"] > 0
    assert "estimated_listening_time" in metadata


def test_packaging_service_create_package_json() -> None:
    """Test creating JSON package."""
    job_id = uuid4()

    artifacts = [
        {
            "type": "world_spec",
            "data": {
                "name": "Aethermoor",
                "summary": "A magical world",
            },
        },
        {
            "type": "character_spec",
            "data": {
                "name": "Kael",
                "role": "protagonist",
                "traits": ["brave", "loyal"],
            },
        },
        {
            "type": "prose_segment",
            "data": {
                "segment_id": "seg_001",
                "prose": "Kael walked through the forest.",
                "word_count": 5,
                "sequence_number": 1,
            },
        },
    ]

    metadata = {
        "title": "Test Story",
        "author": "Test Author",
        "genre": "fantasy",
        "language": "pl",
    }

    package = PackagingService.create_package(
        job_id=job_id,
        artifacts=artifacts,
        metadata=metadata,
        format="json",
    )

    assert package["job_id"] == str(job_id)
    assert package["format"] == "json"
    assert package["metadata"]["title"] == "Test Story"
    assert package["metadata"]["author"] == "Test Author"
    assert package["metadata"]["genre"] == "fantasy"
    assert "content" in package
    assert "statistics" in package
    assert "checksum" in package


def test_packaging_service_organize_artifacts() -> None:
    """Test artifact organization."""
    artifacts = [
        {"type": "world_spec", "data": {"name": "World1"}},
        {"type": "character_spec", "data": {"name": "Char1"}},
        {"type": "character_spec", "data": {"name": "Char2"}},
        {"type": "plot_outline", "data": {"acts": []}},
        {
            "type": "prose_segment",
            "data": {"prose": "Text1", "sequence_number": 2},
        },
        {
            "type": "prose_segment",
            "data": {"prose": "Text2", "sequence_number": 1},
        },
        {"type": "qa_report", "data": {"passed": True}},
    ]

    organized = PackagingService._organize_artifacts(artifacts)

    assert organized["world"]["name"] == "World1"
    assert len(organized["characters"]) == 2
    assert organized["plot"]["acts"] == []
    assert len(organized["prose_segments"]) == 2
    # Prose segments should be sorted by sequence_number
    assert organized["prose_segments"][0]["sequence_number"] == 1
    assert organized["prose_segments"][1]["sequence_number"] == 2
    assert len(organized["qa_reports"]) == 1


def test_packaging_service_calculate_statistics() -> None:
    """Test statistics calculation."""
    organized = {
        "prose_segments": [
            {"word_count": 100, "sequence_number": 1},
            {"word_count": 150, "sequence_number": 2},
            {"word_count": 50, "sequence_number": 3},
        ],
        "characters": [{"name": "Char1"}, {"name": "Char2"}],
        "qa_reports": [{"passed": True}],
    }

    stats = PackagingService._calculate_statistics(organized)

    assert stats["total_words"] == 300
    assert stats["total_segments"] == 3
    assert stats["character_count"] == 2
    assert stats["qa_checks"] == 1
    assert stats["average_segment_length"] == 100.0


def test_packaging_service_render_markdown() -> None:
    """Test markdown rendering."""
    organized = {
        "world": {
            "name": "Aethermoor",
            "summary": "A magical world of wonder.",
        },
        "characters": [
            {
                "name": "Kael",
                "role": "protagonist",
                "traits": ["brave", "loyal"],
            }
        ],
        "prose_segments": [
            {"prose": "First paragraph.", "sequence_number": 1},
            {"prose": "Second paragraph.", "sequence_number": 2},
        ],
    }

    metadata = {
        "title": "Test Story",
        "author": "Test Author",
        "genre": "fantasy",
    }

    markdown = PackagingService._render_markdown(organized, metadata)

    assert "# Test Story" in markdown
    assert "**Author:** Test Author" in markdown
    assert "**Genre:** fantasy" in markdown
    assert "## World" in markdown
    assert "Aethermoor" in markdown
    assert "## Characters" in markdown
    assert "Kael" in markdown
    assert "## Story" in markdown
    assert "First paragraph." in markdown
    assert "Second paragraph." in markdown


def test_packaging_service_create_audio_manifest() -> None:
    """Test audio manifest creation."""
    job_id = uuid4()

    artifacts = [
        {
            "type": "prose_segment",
            "data": {
                "segment_id": "seg_001",
                "prose": "This is the first segment of our story.",
                "word_count": 8,
                "sequence_number": 1,
            },
        },
        {
            "type": "prose_segment",
            "data": {
                "segment_id": "seg_002",
                "prose": "This is the second segment of our story.",
                "word_count": 8,
                "sequence_number": 2,
            },
        },
    ]

    metadata = {
        "title": "Test Story",
        "author": "Test Author",
        "genre": "fantasy",
        "language": "pl",
    }

    package = PackagingService.create_package(
        job_id=job_id,
        artifacts=artifacts,
        metadata=metadata,
        format="audio_manifest",
    )

    assert "audio_manifest" in package
    manifest = package["audio_manifest"]

    assert manifest["title"] == "Test Story"
    assert manifest["author"] == "Test Author"
    assert manifest["language"] == "pl"
    assert manifest["genre"] == "fantasy"
    assert len(manifest["segments"]) == 2
    assert manifest["metadata"]["total_segments"] == 2
    assert manifest["metadata"]["total_words"] == 16


def test_packaging_service_checksum_calculation() -> None:
    """Test checksum calculation."""
    job_id = uuid4()
    artifacts = [
        {"type": "world_spec", "data": {"name": "World"}},
    ]
    metadata = {"title": "Test"}

    package = PackagingService.create_package(
        job_id=job_id,
        artifacts=artifacts,
        metadata=metadata,
    )

    # Checksum should exist and be SHA256 (64 hex characters)
    assert "checksum" in package
    assert len(package["checksum"]) == 64
    assert all(c in "0123456789abcdef" for c in package["checksum"])


def test_packaging_service_export_json() -> None:
    """Test JSON export."""
    job_id = uuid4()
    artifacts = [{"type": "world_spec", "data": {"name": "World"}}]
    metadata = {"title": "Test"}

    package = PackagingService.create_package(
        job_id=job_id,
        artifacts=artifacts,
        metadata=metadata,
        format="json",
    )

    exported = PackagingService.export_package(package, export_format="json")

    assert isinstance(exported, str)
    # Should be valid JSON
    parsed = json.loads(exported)
    assert parsed["metadata"]["title"] == "Test"


def test_packaging_service_export_markdown() -> None:
    """Test markdown export."""
    job_id = uuid4()
    artifacts = [
        {"type": "world_spec", "data": {"name": "Aethermoor", "summary": "A world"}},
        {
            "type": "prose_segment",
            "data": {"prose": "Story text.", "sequence_number": 1},
        },
    ]
    metadata = {"title": "Test Story", "author": "Author", "genre": "fantasy"}

    package = PackagingService.create_package(
        job_id=job_id,
        artifacts=artifacts,
        metadata=metadata,
        format="markdown",
    )

    exported = PackagingService.export_package(package, export_format="markdown")

    assert isinstance(exported, str)
    assert "# Test Story" in exported
    assert "Story text." in exported


def test_packaging_service_unsupported_export_format() -> None:
    """Test unsupported export format."""
    package = {"metadata": {"title": "Test"}}

    with pytest.raises(ValueError, match="Unsupported export format"):
        PackagingService.export_package(package, export_format="pdf")


def test_audio_manifest_duration_formatting() -> None:
    """Test duration formatting."""
    # Test hours:minutes:seconds format
    assert AudioManifest._format_duration(3661) == "01:01:01"
    assert AudioManifest._format_duration(125) == "02:05"
    assert AudioManifest._format_duration(59) == "00:59"
