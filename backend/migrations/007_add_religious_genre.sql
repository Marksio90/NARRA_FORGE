-- Migration: Add religious genre support
-- NarraForge 2.0: Religious/spiritual literature genre

-- Add 'religious' to the genre_type enum
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumlabel = 'religious'
        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'genre_type')
    ) THEN
        ALTER TYPE genre_type ADD VALUE 'religious';
    END IF;
END$$;
