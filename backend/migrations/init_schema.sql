-- Jobs table
CREATE TABLE jobs (
    id UUID PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    inspiration TEXT,
    constraints JSON NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP
);

-- Artifacts table
CREATE TABLE artifacts (
    id UUID PRIMARY KEY,
    job_id UUID NOT NULL,
    type VARCHAR(50) NOT NULL,
    version INTEGER NOT NULL,
    data JSON NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Worlds table
CREATE TABLE worlds (
    id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    rules JSON NOT NULL,
    geography JSON NOT NULL,
    history JSON NOT NULL,
    themes JSON NOT NULL,
    version INTEGER NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Characters table
CREATE TABLE characters (
    id UUID PRIMARY KEY,
    world_id UUID NOT NULL,
    name VARCHAR(200) NOT NULL,
    trajectory JSON NOT NULL,
    relationships JSON NOT NULL,
    constraints JSON NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

-- Timelines table
CREATE TABLE timelines (
    id UUID PRIMARY KEY,
    world_id UUID NOT NULL,
    nodes JSON NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE
);

-- QA Reports table
CREATE TABLE qa_reports (
    id UUID PRIMARY KEY,
    job_id UUID NOT NULL,
    logic_score FLOAT NOT NULL,
    psychology_score FLOAT NOT NULL,
    timeline_score FLOAT NOT NULL,
    critical_errors JSON NOT NULL,
    warnings JSON NOT NULL,
    passed BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Cost Snapshots table
CREATE TABLE cost_snapshots (
    id UUID PRIMARY KEY,
    job_id UUID NOT NULL,
    stage VARCHAR(100) NOT NULL,
    tokens_used INTEGER NOT NULL,
    cost_usd FLOAT NOT NULL,
    model VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_artifacts_job_id ON artifacts(job_id);
CREATE INDEX idx_characters_world_id ON characters(world_id);
CREATE INDEX idx_timelines_world_id ON timelines(world_id);
CREATE INDEX idx_qa_reports_job_id ON qa_reports(job_id);
CREATE INDEX idx_cost_snapshots_job_id ON cost_snapshots(job_id);

-- Update alembic_version
INSERT INTO alembic_version (version_num) VALUES ('af4b3ea397a4');
