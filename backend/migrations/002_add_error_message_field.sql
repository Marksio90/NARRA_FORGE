-- Migration: Add error_message field to projects table
-- Date: 2026-01-21
-- Description: Store detailed error messages when generation fails

-- Add error_message TEXT column to store error details
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Add comment for documentation
COMMENT ON COLUMN projects.error_message IS 'Stores detailed error message when generation fails (status = failed)';
