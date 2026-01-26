-- Migration: Add status field to chapters table
-- Date: 2026-01-26
-- Description: Add production state machine status enum for chapter generation workflow

-- Create the ChapterStatus ENUM type if it doesn't exist
-- Using UPPERCASE values to match SQLAlchemy enum name serialization
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'chapterstatus') THEN
        CREATE TYPE chapterstatus AS ENUM (
            'PLANNED',
            'DRAFTING',
            'DRAFTED',
            'VALIDATING',
            'VALIDATED',
            'REPAIR_NEEDED',
            'REPAIRING',
            'FINALIZED',
            'EXPORTED'
        );
    END IF;
END$$;

-- Add status column to chapters table (only if table exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'chapters') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'chapters' AND column_name = 'status') THEN
            ALTER TABLE chapters ADD COLUMN status chapterstatus NOT NULL DEFAULT 'PLANNED';
        END IF;
    END IF;
END$$;

-- Create index for querying by status (only if table exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'chapters') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_chapters_status') THEN
            CREATE INDEX idx_chapters_status ON chapters(status);
        END IF;
    END IF;
END$$;
