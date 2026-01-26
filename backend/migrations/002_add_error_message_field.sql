-- Migration: Add error_message field to projects table
-- Date: 2026-01-21
-- Description: Store detailed error messages when generation fails

-- Add column only if projects table exists (may not exist on fresh DB before SQLAlchemy init)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'projects') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'projects' AND column_name = 'error_message') THEN
            ALTER TABLE projects ADD COLUMN error_message TEXT;
        END IF;
    END IF;
END$$;
