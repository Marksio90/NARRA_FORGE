-- Migration: Add status field to chapters table
-- Date: 2026-01-26
-- Description: Add production state machine status enum for chapter generation workflow

-- Create the ChapterStatus ENUM type if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'chapterstatus') THEN
        CREATE TYPE chapterstatus AS ENUM (
            'planned',
            'drafting',
            'drafted',
            'validating',
            'validated',
            'repair_needed',
            'repairing',
            'finalized',
            'exported'
        );
    END IF;
END$$;

-- Add status column to chapters table with default value 'planned'
ALTER TABLE chapters
ADD COLUMN IF NOT EXISTS status chapterstatus NOT NULL DEFAULT 'planned';

-- Create index for querying by status
CREATE INDEX IF NOT EXISTS idx_chapters_status ON chapters(status);

-- Add comment for documentation
COMMENT ON COLUMN chapters.status IS 'Production state machine: planned -> drafting -> drafted -> validating -> validated/repair_needed -> finalized -> exported';
