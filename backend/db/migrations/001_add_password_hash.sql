-- Migration: Add password_hash column to users table
-- Run this if you have existing data

ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash TEXT;

-- Create index on email for faster auth lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
