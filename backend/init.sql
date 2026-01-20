-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create custom types
CREATE TYPE project_status AS ENUM (
    'initializing',
    'simulating',
    'generating',
    'completed',
    'failed',
    'cancelled'
);

CREATE TYPE genre_type AS ENUM (
    'sci-fi',
    'fantasy',
    'thriller',
    'horror',
    'romance',
    'drama',
    'comedy',
    'mystery'
);

CREATE TYPE character_role AS ENUM (
    'protagonist',
    'antagonist',
    'supporting',
    'minor',
    'episodic'
);

CREATE TYPE model_tier AS ENUM (
    'tier1',  -- GPT-4o-mini
    'tier2',  -- GPT-4o
    'tier3'   -- GPT-4/o1
);

-- Indexes will be created by Alembic migrations
-- This file only sets up extensions and types
