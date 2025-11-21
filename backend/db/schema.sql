-- Database schema for Career Compass (PostgreSQL + pgvector)

-- Extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resumes table
CREATE TABLE IF NOT EXISTS resumes (
    resume_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    raw_text TEXT,
    parsed_skills TEXT,         -- JSON string (can later switch to JSONB)
    parsed_experience TEXT,     -- JSON string
    embedding TEXT,             -- legacy storage of chunks w/ embeddings if needed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resume chunks with pgvector 
CREATE TABLE IF NOT EXISTS resume_chunks (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER NOT NULL REFERENCES resumes(resume_id) ON DELETE CASCADE,
    section VARCHAR(255),
    content TEXT,
    summary TEXT,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Career paths
CREATE TABLE IF NOT EXISTS career_paths (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    required_skills TEXT,   
    embedding vector(768),
    avg_salary FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recommendations
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    raw_text TEXT,
    career_path_id INTEGER REFERENCES career_paths(id) ON DELETE CASCADE,
    similarity_score FLOAT,
    skill_gaps TEXT,      -- JSON string
    learning_path TEXT,   -- JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Events (multi-agent protocol)
CREATE TABLE IF NOT EXISTS agent_events (
    id SERIAL PRIMARY KEY,
    event_id UUID DEFAULT gen_random_uuid() UNIQUE,
    event_type VARCHAR(120) NOT NULL,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    resume_id INTEGER REFERENCES resumes(resume_id) ON DELETE CASCADE,
    run_id UUID,
    payload JSONB,
    status VARCHAR(32) DEFAULT 'pending',   -- pending | processing | done | failed | dead
    attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id SERIAL PRIMARY KEY,
    run_id UUID DEFAULT gen_random_uuid() UNIQUE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    target_role VARCHAR(255),
    state JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(32) DEFAULT 'in_progress',  -- in_progress | completed | failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Standard indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_resume_chunks_resume_id ON resume_chunks(resume_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_career_paths_title ON career_paths(title);
CREATE INDEX IF NOT EXISTS idx_agent_events_type ON agent_events(event_type);
CREATE INDEX IF NOT EXISTS idx_agent_events_status ON agent_events(status);
CREATE INDEX IF NOT EXISTS idx_agent_events_resume ON agent_events(resume_id);
CREATE INDEX IF NOT EXISTS idx_agent_runs_user ON agent_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_runs_status ON agent_runs(status);

-- Vector indexes (HNSW)
CREATE INDEX IF NOT EXISTS idx_resume_chunks_embedding
    ON resume_chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_career_paths_embedding
    ON career_paths USING hnsw (embedding vector_cosine_ops);