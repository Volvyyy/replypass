-- Migration: 20250627000005_persona_analyses_table.sql
-- Description: Add missing persona_analyses table with RLS policies
-- Impact: Completes DB-004 by implementing the final missing table from the design specification
-- Author: Claude Code (2025-06-27)

-- ============================================================================
-- Table: persona_analyses
-- Description: AI-generated personality analysis and linguistic pattern extraction
-- Security: RLS enabled with persona-based access control
-- ============================================================================

CREATE TABLE persona_analyses (
    -- Primary key using UUID v4
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign key to personas table
    persona_id uuid NOT NULL REFERENCES personas(id) ON DELETE CASCADE,
    
    -- AI analysis results
    ai_interpreted_personality text NOT NULL,
    ai_extracted_patterns text NOT NULL,
    analysis_model varchar(50) NOT NULL,
    
    -- Audit timestamp
    created_at timestamptz DEFAULT now() NOT NULL,
    
    -- Constraints
    CONSTRAINT persona_analyses_model_valid CHECK (
        analysis_model IN ('gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-2.5-flash-lite')
    ),
    CONSTRAINT persona_analyses_personality_not_empty CHECK (
        length(trim(ai_interpreted_personality)) > 0
    ),
    CONSTRAINT persona_analyses_patterns_not_empty CHECK (
        length(trim(ai_extracted_patterns)) > 0
    ),
    
    -- Ensure one analysis per persona (can be updated)
    CONSTRAINT persona_analyses_persona_unique UNIQUE (persona_id)
);

-- ============================================================================
-- Indexes for Performance Optimization
-- ============================================================================

-- Basic indexes
CREATE INDEX idx_persona_analyses_persona_id ON persona_analyses(persona_id);
CREATE INDEX idx_persona_analyses_created_at ON persona_analyses(created_at DESC);
CREATE INDEX idx_persona_analyses_model ON persona_analyses(analysis_model);

-- Full-text search index for personality analysis
CREATE INDEX idx_persona_analyses_personality_search ON persona_analyses 
    USING gin(to_tsvector('english', ai_interpreted_personality));

CREATE INDEX idx_persona_analyses_patterns_search ON persona_analyses 
    USING gin(to_tsvector('english', ai_extracted_patterns));

-- ============================================================================
-- Row Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS on the table
ALTER TABLE persona_analyses ENABLE ROW LEVEL SECURITY;

-- Persona analyses RLS policies (inherit from personas -> cases)
CREATE POLICY "Users can manage persona analyses through personas" ON persona_analyses
FOR ALL USING (
    persona_id IN (
        SELECT p.id FROM personas p
        JOIN cases c ON c.id = p.case_id
        WHERE c.user_id = auth.uid()::uuid AND c.deleted_at IS NULL
    )
);

-- Service role full access
CREATE POLICY "Service role can manage all persona analyses" ON persona_analyses
FOR ALL USING (auth.role() = 'service_role');

-- ============================================================================
-- Helper Functions for Persona Analysis
-- ============================================================================

-- Function: Upsert persona analysis (create or update)
CREATE OR REPLACE FUNCTION upsert_persona_analysis(
    p_persona_id uuid,
    p_personality text,
    p_patterns text,
    p_model varchar(50)
)
RETURNS uuid AS $$
DECLARE
    v_analysis_id uuid;
    v_case_access boolean;
BEGIN
    -- Check if user has access to the persona
    SELECT EXISTS (
        SELECT 1 FROM personas p
        JOIN cases c ON c.id = p.case_id
        WHERE p.id = p_persona_id
        AND c.user_id = auth.uid()::uuid
        AND c.deleted_at IS NULL
    ) INTO v_case_access;
    
    IF NOT v_case_access THEN
        RAISE EXCEPTION 'Access denied: Cannot modify persona analysis for this persona';
    END IF;
    
    -- Upsert analysis
    INSERT INTO persona_analyses (persona_id, ai_interpreted_personality, ai_extracted_patterns, analysis_model)
    VALUES (p_persona_id, p_personality, p_patterns, p_model)
    ON CONFLICT (persona_id) 
    DO UPDATE SET
        ai_interpreted_personality = EXCLUDED.ai_interpreted_personality,
        ai_extracted_patterns = EXCLUDED.ai_extracted_patterns,
        analysis_model = EXCLUDED.analysis_model,
        created_at = now()
    RETURNING id INTO v_analysis_id;
    
    RETURN v_analysis_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get persona analysis with case context
CREATE OR REPLACE FUNCTION get_persona_analysis_with_context(p_persona_id uuid)
RETURNS TABLE(
    analysis_id uuid,
    personality text,
    patterns text,
    model varchar(50),
    created_at timestamptz,
    case_name varchar(100),
    partner_name varchar(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pa.id,
        pa.ai_interpreted_personality,
        pa.ai_extracted_patterns,
        pa.analysis_model,
        pa.created_at,
        c.name,
        c.partner_name
    FROM persona_analyses pa
    JOIN personas p ON p.id = pa.persona_id
    JOIN cases c ON c.id = p.case_id
    WHERE pa.persona_id = p_persona_id
    AND c.user_id = auth.uid()::uuid
    AND c.deleted_at IS NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- Triggers for Enhanced Security Monitoring
-- ============================================================================

-- Trigger: Audit persona analysis operations
CREATE OR REPLACE FUNCTION audit_persona_analysis_operations()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Log analysis creation
        INSERT INTO usage_logs (user_id, usage_type, metadata)
        VALUES (
            auth.uid()::uuid,
            'persona_analysis',
            jsonb_build_object(
                'operation', 'create',
                'persona_id', NEW.persona_id,
                'model', NEW.analysis_model,
                'personality_length', length(NEW.ai_interpreted_personality),
                'patterns_length', length(NEW.ai_extracted_patterns)
            )
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        -- Log analysis updates
        INSERT INTO usage_logs (user_id, usage_type, metadata)
        VALUES (
            auth.uid()::uuid,
            'persona_analysis',
            jsonb_build_object(
                'operation', 'update',
                'persona_id', NEW.persona_id,
                'model', NEW.analysis_model,
                'previous_model', OLD.analysis_model,
                'personality_changed', NEW.ai_interpreted_personality != OLD.ai_interpreted_personality,
                'patterns_changed', NEW.ai_extracted_patterns != OLD.ai_extracted_patterns
            )
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_persona_analysis_operations_trigger
    AFTER INSERT OR UPDATE ON persona_analyses
    FOR EACH ROW EXECUTE FUNCTION audit_persona_analysis_operations();

-- ============================================================================
-- Table Comments for Documentation
-- ============================================================================

COMMENT ON TABLE persona_analyses IS 'AI-generated personality analysis and linguistic pattern extraction for personas';
COMMENT ON COLUMN persona_analyses.ai_interpreted_personality IS 'AI-generated personality interpretation based on reference texts';
COMMENT ON COLUMN persona_analyses.ai_extracted_patterns IS 'AI-extracted linguistic patterns and communication style indicators';
COMMENT ON COLUMN persona_analyses.analysis_model IS 'LLM model used for analysis (gemini-2.0-flash, gemini-2.5-flash, gemini-2.5-flash-lite)';

-- ============================================================================
-- Grant Permissions
-- ============================================================================

-- Grant necessary permissions for application users
GRANT SELECT, INSERT, UPDATE ON persona_analyses TO authenticated;

-- Grant all permissions to service role
GRANT ALL ON persona_analyses TO service_role;

-- Grant function execution permissions
GRANT EXECUTE ON FUNCTION upsert_persona_analysis TO authenticated;
GRANT EXECUTE ON FUNCTION get_persona_analysis_with_context TO authenticated;
GRANT EXECUTE ON FUNCTION upsert_persona_analysis TO service_role;
GRANT EXECUTE ON FUNCTION get_persona_analysis_with_context TO service_role;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify RLS is enabled and policies are created
DO $$
BEGIN
    -- Check if RLS is enabled
    IF NOT EXISTS (
        SELECT 1 FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relname = 'persona_analyses'
        AND n.nspname = 'public'
        AND c.relrowsecurity = true
    ) THEN
        RAISE EXCEPTION 'RLS is not enabled on persona_analyses table';
    END IF;
    
    -- Check if policies exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'persona_analyses'
        AND policyname = 'Users can manage persona analyses through personas'
    ) THEN
        RAISE EXCEPTION 'User access policy not found on persona_analyses table';
    END IF;
    
    RAISE NOTICE 'persona_analyses table successfully created with RLS policies';
END;
$$;