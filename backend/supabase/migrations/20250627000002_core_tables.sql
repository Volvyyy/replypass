-- Migration: 20250627000002_core_tables.sql
-- Description: Core application tables with PostgreSQL 17 optimization
-- Impact: Creates cases, personas, conversation_logs, conversation_messages with advanced RLS and indexing
-- Author: Claude Code (2025-06-27)

-- ============================================================================
-- Table: cases
-- Description: Conversation contexts and partner information
-- Security: RLS enabled with user isolation and soft delete support
-- ============================================================================

CREATE TABLE cases (
    -- Primary key using UUID v4
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign key to users table
    user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Case identification and partner information
    name varchar(100) NOT NULL,
    partner_name varchar(100) NOT NULL,
    partner_type varchar(50),
    my_position varchar(50),
    conversation_purpose text,
    
    -- Flexible metadata storage with optimized structure
    metadata jsonb DEFAULT '{}' NOT NULL,
    
    -- Audit timestamps
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL,
    
    -- Soft delete support
    deleted_at timestamptz,
    
    -- Constraints
    CONSTRAINT cases_name_not_empty CHECK (length(trim(name)) > 0),
    CONSTRAINT cases_partner_name_not_empty CHECK (length(trim(partner_name)) > 0),
    CONSTRAINT cases_casualness_valid CHECK (
        metadata->>'casualness_level' IS NULL OR 
        (metadata->>'casualness_level')::int BETWEEN 1 AND 5
    )
);

-- ============================================================================
-- Table: personas  
-- Description: User communication style and personality settings
-- Security: RLS enabled with case-based access control
-- ============================================================================

CREATE TABLE personas (
    -- Primary key using UUID v4
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign key to cases table
    case_id uuid NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    
    -- Communication style settings
    casualness_level int DEFAULT 3 NOT NULL,
    emoji_usage varchar(20) DEFAULT 'normal' NOT NULL,
    reference_texts text,
    
    -- Quick settings stored as optimized JSONB
    quick_settings jsonb DEFAULT '{}' NOT NULL,
    
    -- Audit timestamps
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL,
    
    -- Constraints
    CONSTRAINT personas_casualness_range CHECK (casualness_level BETWEEN 1 AND 5),
    CONSTRAINT personas_emoji_usage_valid CHECK (
        emoji_usage IN ('none', 'minimal', 'normal', 'frequent', 'heavy')
    ),
    CONSTRAINT personas_reference_text_length CHECK (
        reference_texts IS NULL OR length(reference_texts) <= 5000
    ),
    
    -- Ensure one persona per case
    CONSTRAINT personas_case_unique UNIQUE (case_id)
);

-- ============================================================================
-- Table: conversation_logs
-- Description: Conversation session management with time-series optimization
-- Security: RLS enabled with case-based inheritance
-- ============================================================================

CREATE TABLE conversation_logs (
    -- Primary key using UUID v4
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign key to cases table
    case_id uuid NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    
    -- Session metadata
    message_count int DEFAULT 0 NOT NULL,
    last_message_at timestamptz,
    
    -- Audit timestamps
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL,
    
    -- Constraints
    CONSTRAINT conversation_logs_message_count_positive CHECK (message_count >= 0),
    CONSTRAINT conversation_logs_last_message_logical CHECK (
        last_message_at IS NULL OR last_message_at >= created_at
    )
);

-- ============================================================================
-- Table: conversation_messages
-- Description: Individual messages with time-series partitioning
-- Security: RLS enabled with conversation log inheritance  
-- Optimization: Monthly partitioning for scalable time-series data
-- ============================================================================

CREATE TABLE conversation_messages (
    -- Primary key using UUID v4 + partition key (PostgreSQL 17 requirement)
    id uuid DEFAULT gen_random_uuid(),
    
    -- Foreign key to conversation_logs table
    conversation_log_id uuid NOT NULL REFERENCES conversation_logs(id) ON DELETE CASCADE,
    
    -- Message content and metadata
    speaker varchar(20) NOT NULL,
    content text NOT NULL,
    input_method varchar(20) DEFAULT 'text' NOT NULL,
    
    -- Optimized JSONB metadata for message context
    metadata jsonb DEFAULT '{}' NOT NULL,
    
    -- Message timing (separate from audit timestamps)
    message_timestamp timestamptz,
    
    -- Audit timestamps (partition key)
    created_at timestamptz DEFAULT now() NOT NULL,
    
    -- Constraints
    CONSTRAINT conversation_messages_speaker_valid CHECK (
        speaker IN ('user', 'partner', 'assistant', 'system')
    ),
    CONSTRAINT conversation_messages_input_method_valid CHECK (
        input_method IN ('text', 'voice', 'screenshot', 'file')
    ),
    CONSTRAINT conversation_messages_content_not_empty CHECK (
        length(trim(content)) > 0
    ),
    CONSTRAINT conversation_messages_timestamp_logical CHECK (
        message_timestamp IS NULL OR message_timestamp <= now()
    ),
    
    -- Composite primary key including partition key
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Create initial partition for current month
CREATE TABLE conversation_messages_y2025m06 PARTITION OF conversation_messages
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');

CREATE TABLE conversation_messages_y2025m07 PARTITION OF conversation_messages
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');

-- ============================================================================
-- Indexes for Performance Optimization (PostgreSQL 17 optimized)
-- ============================================================================

-- Cases table indexes
CREATE INDEX idx_cases_user_id ON cases (user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_cases_user_active ON cases (user_id, created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_cases_metadata_gin ON cases USING gin (metadata jsonb_path_ops);
CREATE INDEX idx_cases_partner_search ON cases USING gin (
    to_tsvector('english', partner_name || ' ' || coalesce(partner_type, ''))
) WHERE deleted_at IS NULL;

-- Personas table indexes  
CREATE INDEX idx_personas_case_id ON personas (case_id);
CREATE INDEX idx_personas_settings_gin ON personas USING gin (quick_settings jsonb_path_ops);
CREATE INDEX idx_personas_casualness ON personas (casualness_level);

-- Conversation logs indexes
CREATE INDEX idx_conversation_logs_case_id ON conversation_logs (case_id);
CREATE INDEX idx_conversation_logs_activity ON conversation_logs (case_id, last_message_at DESC NULLS LAST);
CREATE INDEX idx_conversation_logs_created ON conversation_logs (created_at DESC);

-- Conversation messages indexes (applied to partitions)
CREATE INDEX idx_conversation_messages_log_id ON conversation_messages (conversation_log_id);
CREATE INDEX idx_conversation_messages_timestamp ON conversation_messages (message_timestamp DESC);
CREATE INDEX idx_conversation_messages_speaker ON conversation_messages (speaker, created_at DESC);
CREATE INDEX idx_conversation_messages_metadata_gin ON conversation_messages USING gin (metadata jsonb_path_ops);

-- ============================================================================
-- Row Level Security (RLS) Policies - PostgreSQL 17 Optimized
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE personas ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;

-- Cases RLS policies
CREATE POLICY "Users can manage own cases" ON cases
FOR ALL USING (user_id = auth.uid()::uuid AND deleted_at IS NULL);

CREATE POLICY "Users can view own deleted cases" ON cases
FOR SELECT USING (user_id = auth.uid()::uuid);

-- Service role full access
CREATE POLICY "Service role can manage all cases" ON cases
FOR ALL USING (auth.role() = 'service_role');

-- Personas RLS policies (inherit from cases)
CREATE POLICY "Users can manage personas through cases" ON personas
FOR ALL USING (
    case_id IN (
        SELECT id FROM cases WHERE user_id = auth.uid()::uuid
    )
);

-- Conversation logs RLS policies (inherit from cases)
CREATE POLICY "Users can manage conversation logs through cases" ON conversation_logs
FOR ALL USING (
    case_id IN (
        SELECT id FROM cases WHERE user_id = auth.uid()::uuid AND deleted_at IS NULL
    )
);

-- Conversation messages RLS policies (inherit from conversation logs)
CREATE POLICY "Users can manage messages through conversation logs" ON conversation_messages
FOR ALL USING (
    conversation_log_id IN (
        SELECT cl.id FROM conversation_logs cl
        JOIN cases c ON c.id = cl.case_id
        WHERE c.user_id = auth.uid()::uuid AND c.deleted_at IS NULL
    )
);

-- ============================================================================
-- Triggers for Automatic Updates
-- ============================================================================

-- Add updated_at triggers for relevant tables
CREATE TRIGGER update_cases_updated_at 
    BEFORE UPDATE ON cases 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_personas_updated_at 
    BEFORE UPDATE ON personas 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversation_logs_updated_at 
    BEFORE UPDATE ON conversation_logs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Helper Functions for Application Logic
-- ============================================================================

-- Function: Soft delete a case and all related data
CREATE OR REPLACE FUNCTION soft_delete_case(case_uuid uuid)
RETURNS boolean AS $$
BEGIN
    UPDATE cases 
    SET deleted_at = now(), updated_at = now()
    WHERE id = case_uuid AND user_id = auth.uid()::uuid AND deleted_at IS NULL;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Update conversation message count
CREATE OR REPLACE FUNCTION update_conversation_message_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE conversation_logs 
        SET message_count = message_count + 1,
            last_message_at = COALESCE(NEW.message_timestamp, NEW.created_at),
            updated_at = now()
        WHERE id = NEW.conversation_log_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE conversation_logs 
        SET message_count = GREATEST(message_count - 1, 0),
            updated_at = now()
        WHERE id = OLD.conversation_log_id;
        
        -- Update last_message_at to most recent remaining message
        UPDATE conversation_logs 
        SET last_message_at = (
            SELECT COALESCE(MAX(COALESCE(message_timestamp, created_at)), created_at)
            FROM conversation_messages 
            WHERE conversation_log_id = OLD.conversation_log_id
        )
        WHERE id = OLD.conversation_log_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update message count on conversation_messages changes
CREATE TRIGGER conversation_message_count_trigger
    AFTER INSERT OR DELETE ON conversation_messages
    FOR EACH ROW EXECUTE FUNCTION update_conversation_message_count();

-- ============================================================================
-- Table Comments for Documentation
-- ============================================================================

COMMENT ON TABLE cases IS 'Conversation contexts and partner information with soft delete support';
COMMENT ON TABLE personas IS 'User communication style and personality settings per case';
COMMENT ON TABLE conversation_logs IS 'Conversation session management with message tracking';
COMMENT ON TABLE conversation_messages IS 'Individual messages with time-series partitioning for scalability';

-- Column comments for complex fields
COMMENT ON COLUMN cases.metadata IS 'JSONB field for flexible case-specific data: {priority, tags, notes, etc}';
COMMENT ON COLUMN personas.quick_settings IS 'JSONB field for UI quick settings: {use_honorifics, response_length, thinking_style, humor_level}';
COMMENT ON COLUMN conversation_messages.metadata IS 'JSONB field for message context: {confidence_score, processing_time, model_version}';

-- ============================================================================
-- Grant Permissions
-- ============================================================================

-- Grant necessary permissions for application users
GRANT SELECT, INSERT, UPDATE, DELETE ON cases TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON personas TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON conversation_logs TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON conversation_messages TO authenticated;

-- Grant all permissions to service role
GRANT ALL ON cases TO service_role;
GRANT ALL ON personas TO service_role;
GRANT ALL ON conversation_logs TO service_role;
GRANT ALL ON conversation_messages TO service_role;

-- Grant function execution permissions
GRANT EXECUTE ON FUNCTION soft_delete_case TO authenticated;
GRANT EXECUTE ON FUNCTION soft_delete_case TO service_role;