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

-- IVFFlat index for approximate nearest-neighbor search (cosine distance)
-- Note: requires at least 1 row to exist; safe to run on empty table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes WHERE indexname = 'idx_mirix_vectors_embedding'
    ) THEN
        BEGIN
            CREATE INDEX idx_mirix_vectors_embedding
            ON mirix_vectors USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'ivfflat index creation skipped (table may be empty): %', SQLERRM;
        END;
    END IF;
END$$;
