-- Migration: Add simulation_data and estimated_duration_minutes fields to projects table
-- Date: 2026-01-20
-- Description: Store simulation results in the project for persistence across page refreshes

-- Add simulation_data JSONB column to store full simulation response
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS simulation_data JSONB;

-- Add estimated_duration_minutes to store simulation time estimate
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS estimated_duration_minutes INTEGER;

-- Add comment for documentation
COMMENT ON COLUMN projects.simulation_data IS 'Stores the full simulation response including estimated_steps, estimated_total_cost, estimated_duration_minutes, and ai_decisions';
COMMENT ON COLUMN projects.estimated_duration_minutes IS 'Estimated duration in minutes for the generation pipeline (from simulation)';
