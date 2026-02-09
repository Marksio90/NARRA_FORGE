-- Migration: Add mirix_vectors table for pgvector-based semantic search
-- Replaces ChromaDB dependency with native PostgreSQL pgvector
-- Date: 2026-02-09

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'mirix_vectors') THEN
        CREATE TABLE mirix_vectors (
            id TEXT PRIMARY KEY,
            collection TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata JSONB DEFAULT '{}',
            embedding vector(1536),
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE INDEX idx_mirix_vectors_collection ON mirix_vectors (collection);

        -- GIN index on metadata for fast JSONB queries
        CREATE INDEX idx_mirix_vectors_metadata ON mirix_vectors USING GIN (metadata);
    END IF;
END$$;

-- HNSW index for approximate nearest-neighbor search (cosine distance)
-- HNSW advantages over IVFFlat:
--   * No training phase needed (works immediately on empty tables)
--   * Better recall accuracy at same speed
--   * Supports real-time inserts without re-indexing
-- m=16: max connections per node (higher=better recall, more memory)
-- ef_construction=64: search width during build (higher=better quality, slower build)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes WHERE indexname = 'idx_mirix_vectors_embedding'
    ) THEN
        CREATE INDEX idx_mirix_vectors_embedding
        ON mirix_vectors USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
    END IF;
END$$;
