"""Packaging Service - creates final packages and audio manifests."""

import hashlib
import json
import logging
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class AudioSegment:
    """Audio segment for TTS/audiobook generation."""

    def __init__(
        self,
        segment_id: str,
        text: str,
        sequence_number: int,
        character_voice: str | None = None,
        emotion: str | None = None,
        duration_estimate: float | None = None,
    ) -> None:
        """
        Initialize audio segment.

        Args:
            segment_id: Unique segment identifier
            text: Text content to be spoken
            sequence_number: Order in the audio sequence
            character_voice: Character voice identifier (for dialogue)
            emotion: Emotional tone (neutral, happy, sad, angry, etc.)
            duration_estimate: Estimated duration in seconds (based on word count)
        """
        self.segment_id = segment_id
        self.text = text
        self.sequence_number = sequence_number
        self.character_voice = character_voice
        self.emotion = emotion
        self.duration_estimate = duration_estimate or self._estimate_duration(text)

    @staticmethod
    def _estimate_duration(text: str) -> float:
        """
        Estimate audio duration based on word count.

        Average speaking rate: 150-160 words per minute.
        Using 155 WPM = 2.58 words per second.
        """
        word_count = len(text.split())
        return round(word_count / 2.58, 2)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "segment_id": self.segment_id,
            "text": self.text,
            "sequence_number": self.sequence_number,
            "character_voice": self.character_voice,
            "emotion": self.emotion,
            "duration_estimate": self.duration_estimate,
            "word_count": len(self.text.split()),
        }


class AudioManifest:
    """Audio manifest for TTS/audiobook generation."""

    def __init__(
        self,
        job_id: UUID,
        title: str,
        author: str | None = None,
        narrator: str | None = None,
        language: str = "pl",
        genre: str | None = None,
    ) -> None:
        """
        Initialize audio manifest.

        Args:
            job_id: Job UUID
            title: Book/story title
            author: Author name
            narrator: Narrator name (for audiobook)
            language: Language code (default: "pl")
            genre: Genre (fantasy, sci-fi, etc.)
        """
        self.manifest_id = uuid4()
        self.job_id = job_id
        self.title = title
        self.author = author or "NARRA_FORGE"
        self.narrator = narrator or "AI Narrator"
        self.language = language
        self.genre = genre
        self.segments: list[AudioSegment] = []
        self.created_at = datetime.utcnow()
        self.total_duration: float = 0.0
        self.total_words: int = 0

    def add_segment(self, segment: AudioSegment) -> None:
        """Add audio segment to manifest."""
        self.segments.append(segment)
        self.total_duration += segment.duration_estimate
        self.total_words += len(segment.text.split())

    def add_segments(self, segments: list[AudioSegment]) -> None:
        """Add multiple segments."""
        for segment in segments:
            self.add_segment(segment)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "manifest_id": str(self.manifest_id),
            "job_id": str(self.job_id),
            "title": self.title,
            "author": self.author,
            "narrator": self.narrator,
            "language": self.language,
            "genre": self.genre,
            "segments": [seg.to_dict() for seg in self.segments],
            "metadata": {
                "total_segments": len(self.segments),
                "total_duration_seconds": round(self.total_duration, 2),
                "total_duration_minutes": round(self.total_duration / 60, 2),
                "total_words": self.total_words,
                "average_segment_duration": (
                    round(self.total_duration / len(self.segments), 2)
                    if self.segments
                    else 0.0
                ),
                "estimated_listening_time": self._format_duration(self.total_duration),
            },
            "created_at": self.created_at.isoformat(),
            "version": "1.0",
        }

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration as HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"


class PackagingService:
    """Service for packaging final literary products."""

    @staticmethod
    def create_package(
        job_id: UUID,
        artifacts: list[dict[str, Any]],
        metadata: dict[str, Any],
        format: str = "json",
    ) -> dict[str, Any]:
        """
        Create final package from artifacts.

        Args:
            job_id: Job UUID
            artifacts: List of artifact dictionaries
            metadata: Package metadata (title, author, genre, etc.)
            format: Package format (json, markdown, audio_manifest)

        Returns:
            Package dictionary with all content and metadata
        """
        logger.info(
            "Creating package",
            extra={"job_id": str(job_id), "format": format, "artifact_count": len(artifacts)},
        )

        package_id = uuid4()
        created_at = datetime.utcnow()

        # Organize artifacts by type
        organized = PackagingService._organize_artifacts(artifacts)

        # Create package structure
        package = {
            "package_id": str(package_id),
            "job_id": str(job_id),
            "format": format,
            "metadata": {
                "title": metadata.get("title", "Untitled"),
                "author": metadata.get("author", "NARRA_FORGE"),
                "genre": metadata.get("genre", "unknown"),
                "language": metadata.get("language", "pl"),
                "created_at": created_at.isoformat(),
                "version": "1.0",
            },
            "content": organized,
            "statistics": PackagingService._calculate_statistics(organized),
        }

        # Add format-specific content
        if format == "markdown":
            package["rendered"] = PackagingService._render_markdown(organized, metadata)
        elif format == "audio_manifest":
            package["audio_manifest"] = PackagingService._create_audio_manifest_data(
                job_id, organized, metadata
            )

        # Calculate package checksum
        package["checksum"] = PackagingService._calculate_checksum(package)

        logger.info(
            "Package created",
            extra={
                "job_id": str(job_id),
                "package_id": str(package_id),
                "format": format,
                "total_words": package["statistics"]["total_words"],  # type: ignore[index]
            },
        )

        return package

    @staticmethod
    def _organize_artifacts(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
        """Organize artifacts by type."""
        organized: dict[str, Any] = {
            "world": None,
            "characters": [],
            "plot": None,
            "prose_segments": [],
            "qa_reports": [],
            "style_guides": [],
        }

        for artifact in artifacts:
            artifact_type = artifact.get("type")
            data = artifact.get("data", {})

            if artifact_type == "world_spec":
                organized["world"] = data
            elif artifact_type == "character_spec":
                organized["characters"].append(data)
            elif artifact_type == "plot_outline":
                organized["plot"] = data
            elif artifact_type == "prose_segment":
                organized["prose_segments"].append(data)
            elif artifact_type == "qa_report":
                organized["qa_reports"].append(data)
            elif artifact_type == "style_guide":
                organized["style_guides"].append(data)

        # Sort prose segments by sequence
        organized["prose_segments"].sort(
            key=lambda x: x.get("sequence_number", 0)
        )

        return organized

    @staticmethod
    def _calculate_statistics(organized: dict[str, Any]) -> dict[str, Any]:
        """Calculate package statistics."""
        prose_segments = organized.get("prose_segments", [])

        total_words = sum(seg.get("word_count", 0) for seg in prose_segments)
        total_segments = len(prose_segments)

        return {
            "total_words": total_words,
            "total_segments": total_segments,
            "character_count": len(organized.get("characters", [])),
            "qa_checks": len(organized.get("qa_reports", [])),
            "average_segment_length": (
                round(total_words / total_segments, 2) if total_segments > 0 else 0
            ),
        }

    @staticmethod
    def _render_markdown(
        organized: dict[str, Any], metadata: dict[str, Any]
    ) -> str:
        """Render package as markdown."""
        lines = []

        # Title and metadata
        title = metadata.get("title", "Untitled")
        author = metadata.get("author", "NARRA_FORGE")
        genre = metadata.get("genre", "Unknown")

        lines.append(f"# {title}\n")
        lines.append(f"**Author:** {author}\n")
        lines.append(f"**Genre:** {genre}\n")
        lines.append("\n---\n")

        # World
        if world := organized.get("world"):
            lines.append("\n## World\n")
            if world_name := world.get("name"):
                lines.append(f"**{world_name}**\n")
            if summary := world.get("summary"):
                lines.append(f"\n{summary}\n")

        # Characters
        if characters := organized.get("characters"):
            lines.append("\n## Characters\n")
            for char in characters:
                name = char.get("name", "Unknown")
                role = char.get("role", "character")
                lines.append(f"\n### {name} ({role})\n")
                if traits := char.get("traits"):
                    lines.append(f"\n**Traits:** {', '.join(traits)}\n")

        # Prose
        if prose_segments := organized.get("prose_segments"):
            lines.append("\n## Story\n")
            for segment in prose_segments:
                if prose := segment.get("prose"):
                    lines.append(f"\n{prose}\n")

        return "".join(lines)

    @staticmethod
    def _create_audio_manifest_data(
        job_id: UUID, organized: dict[str, Any], metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """Create audio manifest from organized content."""
        title = metadata.get("title", "Untitled")
        author = metadata.get("author", "NARRA_FORGE")
        genre = metadata.get("genre", "unknown")
        language = metadata.get("language", "pl")

        # Create manifest
        manifest = AudioManifest(
            job_id=job_id,
            title=title,
            author=author,
            language=language,
            genre=genre,
        )

        # Add prose segments as audio segments
        prose_segments = organized.get("prose_segments", [])
        for i, segment in enumerate(prose_segments, start=1):
            prose = segment.get("prose", "")
            segment_id = segment.get("segment_id", f"segment_{i}")

            audio_segment = AudioSegment(
                segment_id=segment_id,
                text=prose,
                sequence_number=i,
            )
            manifest.add_segment(audio_segment)

        return manifest.to_dict()

    @staticmethod
    def _calculate_checksum(package: dict[str, Any]) -> str:
        """Calculate SHA256 checksum of package content."""
        # Remove existing checksum field if present
        package_copy = package.copy()
        package_copy.pop("checksum", None)

        # Calculate checksum
        content = json.dumps(package_copy, sort_keys=True).encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def export_package(
        package: dict[str, Any], export_format: str = "json"
    ) -> str | bytes:
        """
        Export package to specified format.

        Args:
            package: Package dictionary
            export_format: Export format (json, markdown)

        Returns:
            Exported content as string or bytes
        """
        if export_format == "json":
            return json.dumps(package, indent=2, ensure_ascii=False)
        elif export_format == "markdown":
            rendered = package.get("rendered", "")
            return str(rendered)  # Ensure string type
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
