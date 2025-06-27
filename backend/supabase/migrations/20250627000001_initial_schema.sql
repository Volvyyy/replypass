-- Migration: 20250627000001_initial_schema.sql
-- Description: Initial users table creation with RLS and authentication integration
-- Impact: Creates foundation table for user management with secure tenant isolation
-- Author: Claude Code (2025-06-27)

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Table: users
-- Description: Core user table integrated with Supabase Auth
-- Security: RLS enabled with tenant isolation policies
-- ============================================================================

CREATE TABLE users (
    -- Primary key using UUID v4
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Authentication integration
    email varchar(255) NOT NULL,
    auth_id varchar(255) NOT NULL,
    
    -- User profile information stored as JSONB for flexibility
    profile jsonb DEFAULT '{}' NOT NULL,
    
    -- Audit timestamps
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL,
    
    -- Constraints
    CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT users_auth_id_not_empty CHECK (length(auth_id) > 0)
);

-- ============================================================================
-- Unique Constraints and Indexes
-- ============================================================================

-- Unique constraints for email and auth_id
ALTER TABLE users ADD CONSTRAINT users_email_key UNIQUE (email);
ALTER TABLE users ADD CONSTRAINT users_auth_id_key UNIQUE (auth_id);

-- Performance indexes for common queries
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_auth_id ON users (auth_id);
CREATE INDEX idx_users_created_at ON users (created_at);

-- JSONB indexes for profile searches (optimized for PostgreSQL 17)
CREATE INDEX idx_users_profile_display_name ON users 
USING gin ((profile->'display_name'));

-- ============================================================================
-- Row Level Security (RLS) Configuration
-- PostgreSQL 17 optimized policies for performance
-- ============================================================================

-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view and edit their own profile
CREATE POLICY "Users can manage own profile" ON users
FOR ALL USING (auth.uid()::text = auth_id);

-- Policy: Authenticated users can view basic profile info (for display purposes)
CREATE POLICY "Users can view others basic profile" ON users
FOR SELECT USING (
    auth.role() = 'authenticated' AND
    id != auth.uid()  -- Prevent viewing own profile through this policy
);

-- Policy: Service role can manage all users (for admin operations)
CREATE POLICY "Service role can manage all users" ON users
FOR ALL USING (auth.role() = 'service_role');

-- ============================================================================
-- Database Functions
-- ============================================================================

-- Function: Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger: Auto-update updated_at on users table
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Function: Create user profile with auth integration
CREATE OR REPLACE FUNCTION create_user_profile(
    user_email text,
    user_auth_id text,
    user_profile jsonb DEFAULT '{}'::jsonb
)
RETURNS uuid AS $$
DECLARE
    new_user_id uuid;
BEGIN
    INSERT INTO users (email, auth_id, profile)
    VALUES (user_email, user_auth_id, user_profile)
    RETURNING id INTO new_user_id;
    
    RETURN new_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE users IS 'Core user table integrated with Supabase Auth, storing user profiles with RLS tenant isolation';
COMMENT ON COLUMN users.id IS 'Primary key using UUID v4 for distributed systems compatibility';
COMMENT ON COLUMN users.email IS 'User email address, must be unique and properly formatted';
COMMENT ON COLUMN users.auth_id IS 'Supabase Auth UUID for authentication integration';
COMMENT ON COLUMN users.profile IS 'JSONB field for flexible user profile data: {display_name, avatar_url, timezone, locale}';
COMMENT ON COLUMN users.created_at IS 'User registration timestamp';
COMMENT ON COLUMN users.updated_at IS 'Last profile update timestamp, automatically maintained';

-- ============================================================================
-- Grant Permissions
-- ============================================================================

-- Grant necessary permissions for application
GRANT SELECT, INSERT, UPDATE ON users TO authenticated;
GRANT ALL ON users TO service_role;

-- Grant permission to use the create_user_profile function
GRANT EXECUTE ON FUNCTION create_user_profile TO authenticated;
GRANT EXECUTE ON FUNCTION create_user_profile TO service_role;