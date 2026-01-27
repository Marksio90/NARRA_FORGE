-- Migration: Add series support for multi-book sagas
-- Date: 2026-01-27
-- Description: Add series table and related tables for tracking multi-book continuity

-- Create series table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'series') THEN
        CREATE TABLE series (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

            -- Basic info
            name VARCHAR(255) NOT NULL,
            description TEXT,
            genre VARCHAR(50) NOT NULL,
            language VARCHAR(20) NOT NULL DEFAULT 'polski',

            -- Series planning
            planned_books INTEGER NOT NULL DEFAULT 3,
            completed_books INTEGER NOT NULL DEFAULT 0,

            -- Shared universe
            shared_world_bible_id INTEGER REFERENCES world_bibles(id) ON DELETE SET NULL,

            -- Series arc
            series_arc TEXT,

            -- JSONB fields for flexible data
            timeline JSONB DEFAULT '[]'::jsonb,
            recurring_characters JSONB DEFAULT '[]'::jsonb,
            plot_threads JSONB DEFAULT '[]'::jsonb,
            shared_elements JSONB DEFAULT '{}'::jsonb,

            -- Status
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            is_complete BOOLEAN NOT NULL DEFAULT FALSE,

            -- Timestamps
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        );
    END IF;
END$$;

-- Create indexes for series table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'series') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_series_user_id') THEN
            CREATE INDEX idx_series_user_id ON series(user_id);
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_series_genre') THEN
            CREATE INDEX idx_series_genre ON series(genre);
        END IF;
    END IF;
END$$;

-- Create series_character_arcs table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'series_character_arcs') THEN
        CREATE TABLE series_character_arcs (
            id SERIAL PRIMARY KEY,
            series_id INTEGER NOT NULL REFERENCES series(id) ON DELETE CASCADE,
            character_name VARCHAR(255) NOT NULL,

            -- Arc tracking
            starting_state TEXT,
            current_state TEXT,
            target_end_state TEXT,

            -- Appearances
            first_appearance_book INTEGER NOT NULL,
            last_appearance_book INTEGER,

            -- JSONB fields
            key_moments JSONB DEFAULT '[]'::jsonb,
            relationships JSONB DEFAULT '{}'::jsonb,

            -- Status
            is_alive BOOLEAN NOT NULL DEFAULT TRUE,
            is_recurring BOOLEAN NOT NULL DEFAULT TRUE,
            death_book INTEGER,
            death_chapter INTEGER,

            -- Timestamps
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        );
    END IF;
END$$;

-- Create index for series_character_arcs
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'series_character_arcs') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_series_character_arcs_series_id') THEN
            CREATE INDEX idx_series_character_arcs_series_id ON series_character_arcs(series_id);
        END IF;
    END IF;
END$$;

-- Create series_plot_threads table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'series_plot_threads') THEN
        CREATE TABLE series_plot_threads (
            id SERIAL PRIMARY KEY,
            series_id INTEGER NOT NULL REFERENCES series(id) ON DELETE CASCADE,

            -- Thread info
            name VARCHAR(255) NOT NULL,
            description TEXT,
            thread_type VARCHAR(50),

            -- Status
            introduced_in_book INTEGER NOT NULL,
            introduced_in_chapter INTEGER,
            resolved_in_book INTEGER,
            resolved_in_chapter INTEGER,
            is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
            is_main_plot BOOLEAN NOT NULL DEFAULT FALSE,

            -- JSONB fields
            related_characters JSONB DEFAULT '[]'::jsonb,
            key_events JSONB DEFAULT '[]'::jsonb,
            foreshadowing JSONB DEFAULT '[]'::jsonb,

            -- Timestamps
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        );
    END IF;
END$$;

-- Create index for series_plot_threads
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'series_plot_threads') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_series_plot_threads_series_id') THEN
            CREATE INDEX idx_series_plot_threads_series_id ON series_plot_threads(series_id);
        END IF;
    END IF;
END$$;

-- Add series_id column to projects table if not exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'projects') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'projects' AND column_name = 'series_id') THEN
            ALTER TABLE projects ADD COLUMN series_id INTEGER REFERENCES series(id) ON DELETE SET NULL;
        END IF;
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'projects' AND column_name = 'book_number_in_series') THEN
            ALTER TABLE projects ADD COLUMN book_number_in_series INTEGER;
        END IF;
    END IF;
END$$;

-- Create index for projects.series_id
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'projects') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_projects_series_id') THEN
            CREATE INDEX idx_projects_series_id ON projects(series_id);
        END IF;
    END IF;
END$$;
