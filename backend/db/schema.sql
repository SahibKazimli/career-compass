-- Database schema for career compass

CREATE EXTENSION IF NOT EXISTS vector

-- Users table
CREATE TABLE IF NOT EXISTS profiles (
    user_id SERIAL PRIMARY KEY,
    email TEXT,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resumes table
CREATE TABLE IF NOT EXISTS resumes (
    resume_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    raw_text TEXT, 
    parsed_skills TEXT,
    parsed_experience TEXT,
    embedding TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resume chunks with pgvector 
CREATE TABLE IF NOT EXISTS resume_chunks (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,  
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
    skill_gaps TEXT,
    learning_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_resume_chunks_resume_id ON resume_chunks(resume_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_career_paths_title ON career_paths(title);

-- Vector indexes (HNSW for fast similarity search)
CREATE INDEX IF NOT EXISTS idx_resume_chunks_embedding 
    ON resume_chunks USING hnsw (embedding vector_cosine_ops);
    
CREATE INDEX IF NOT EXISTS idx_career_paths_embedding 
    ON career_paths USING hnsw (embedding vector_cosine_ops);