-- Migration: Add simulation_data and estimated_duration_minutes fields to projects table
-- Date: 2026-01-20
-- Description: Store simulation results in the project for persistence across page refreshes

-- Add columns only if projects table exists (may not exist on fresh DB before SQLAlchemy init)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'projects') THEN
        -- Add simulation_data JSONB column to store full simulation response
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'projects' AND column_name = 'simulation_data') THEN
            ALTER TABLE projects ADD COLUMN simulation_data JSONB;
        END IF;

        -- Add estimated_duration_minutes to store simulation time estimate
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'projects' AND column_name = 'estimated_duration_minutes') THEN
            ALTER TABLE projects ADD COLUMN estimated_duration_minutes INTEGER;
        END IF;
    END IF;
END$$;
