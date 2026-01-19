"""Embedding service for semantic search with pgvector."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from models.schema import Embedding


class EmbeddingService:
    """Service for managing embeddings and semantic search."""

    MAX_SUMMARY_LENGTH = 500  # Maximum words in summary

    @staticmethod
    def validate_summary(summary: str) -> None:
        """Validate that summary is not too long (prevents full text injection)."""
        word_count = len(summary.split())
        if word_count > EmbeddingService.MAX_SUMMARY_LENGTH:
            raise ValueError(
                f"Summary too long: {word_count} words "
                f"(max {EmbeddingService.MAX_SUMMARY_LENGTH}). "
                "Only summaries allowed, not full text."
            )

    @staticmethod
    async def insert_embedding(
        session: AsyncSession,
        artifact_id: uuid.UUID,
        vector: list[float],
        content_type: str,
        content_summary: str,
        metadata: dict[str, Any] | None = None,
    ) -> Embedding:
        """
        Insert new embedding.

        Args:
            session: Database session
            artifact_id: Foreign key to artifacts table
            vector: Embedding vector (e.g., from OpenAI)
            content_type: Type of content (segment_summary, event, motif, character_state)
            content_summary: Summary text (NOT full text, max 500 words)
            metadata: Optional metadata

        Returns:
            Created embedding

        Raises:
            ValueError: If summary is too long
        """
        # Validate summary length
        EmbeddingService.validate_summary(content_summary)

        # Create embedding
        embedding = Embedding(
            id=uuid.uuid4(),
            artifact_id=artifact_id,
            vector=str(vector),  # Store as string temporarily (will use pgvector type later)
            content_type=content_type,
            content_summary=content_summary,
            meta=metadata or {},  # 'meta' attribute maps to 'metadata' column
            created_at=datetime.utcnow(),
        )

        session.add(embedding)
        await session.commit()
        await session.refresh(embedding)

        return embedding

    @staticmethod
    async def similarity_search(
        session: AsyncSession,
        query_vector: list[float],  # noqa: ARG004 - Will be used with pgvector operators
        content_type: str | None = None,
        top_k: int = 5,
    ) -> list[Embedding]:
        """
        Perform similarity search using cosine similarity.

        Args:
            session: Database session
            query_vector: Query embedding vector
            content_type: Optional filter by content type
            top_k: Number of results to return

        Returns:
            List of similar embeddings
        """
        # Build query
        query = select(Embedding)

        if content_type:
            query = query.where(Embedding.content_type == content_type)

        # Execute query (basic version without pgvector operators)
        result = await session.execute(query.limit(top_k))
        embeddings = list(result.scalars().all())

        return embeddings

    @staticmethod
    async def delete_embeddings_by_artifact(session: AsyncSession, artifact_id: uuid.UUID) -> None:
        """Delete all embeddings for a given artifact."""
        await session.execute(
            text("DELETE FROM embeddings WHERE artifact_id = :artifact_id").bindparams(
                artifact_id=artifact_id
            )
        )
        await session.commit()
