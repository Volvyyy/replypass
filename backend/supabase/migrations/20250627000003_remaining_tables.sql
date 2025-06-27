-- Migration: 20250627000003_remaining_tables.sql
-- Description: Remaining application tables with PostgreSQL 17 optimization
-- Impact: Creates generated_replies, reply_suggestions, feedback_logs, subscription_plans, user_subscriptions, usage_logs
-- Author: Claude Code (2025-06-27)

-- ============================================================================
-- Table: generated_replies
-- Description: Reply generation request history with LLM tracking
-- Security: RLS enabled with case-based access control
-- ============================================================================

CREATE TABLE generated_replies (
    -- Primary key using UUID v4
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign keys
    case_id uuid NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    conversation_log_id uuid NOT NULL REFERENCES conversation_logs(id) ON DELETE CASCADE,
    
    -- Generation details
    user_goal text,
    llm_model varchar(50) NOT NULL,
    
    -- Prompt context stored as optimized JSONB
    prompt_context jsonb NOT NULL DEFAULT '{}',
    
    -- Audit timestamp
    created_at timestamptz DEFAULT now() NOT NULL,
    
    -- Constraints
    CONSTRAINT generated_replies_model_valid CHECK (
        llm_model IN ('gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-2.5-flash-lite')
    )
);

-- ============================================================================
-- Table: reply_suggestions
-- Description: Generated reply options with tracking metadata
-- Security: RLS enabled with generated_reply inheritance
-- ============================================================================

CREATE TABLE reply_suggestions (
    -- Primary key using UUID v4
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign key to generated_replies
    generated_reply_id uuid NOT NULL REFERENCES generated_replies(id) ON DELETE CASCADE,
    
    -- Suggestion details
    category varchar(50) NOT NULL,
    suggestion text NOT NULL,
    
    -- Tracking fields
    was_sent boolean DEFAULT false NOT NULL,
    partner_reaction varchar(20),
    sent_at timestamptz,
    
    -- Audit timestamp
    created_at timestamptz DEFAULT now() NOT NULL,
    
    -- Constraints
    CONSTRAINT reply_suggestions_category_valid CHECK (
        category IN ('friendly', 'professional', 'casual', 'empathetic', 'direct', 'apologetic')
    ),
    CONSTRAINT reply_suggestions_reaction_valid CHECK (
        partner_reaction IS NULL OR partner_reaction IN ('positive', 'neutral', 'negative')
    ),
    CONSTRAINT reply_suggestions_sent_logic CHECK (
        (was_sent = true AND sent_at IS NOT NULL) OR 
        (was_sent = false AND sent_at IS NULL AND partner_reaction IS NULL)
    )
);

-- ============================================================================
-- Table: feedback_logs
-- Description: User feedback for reply suggestions
-- Security: RLS enabled with user and suggestion access control
-- ============================================================================

CREATE TABLE feedback_logs (
    -- Primary key using UUID v4
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign keys
    reply_suggestion_id uuid NOT NULL REFERENCES reply_suggestions(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Feedback details
    feedback_type varchar(20) NOT NULL,
    
    -- Flexible details storage with optimized structure
    details jsonb DEFAULT '{}' NOT NULL,
    
    -- Audit timestamp
    created_at timestamptz DEFAULT now() NOT NULL,
    
    -- Constraints
    CONSTRAINT feedback_logs_type_valid CHECK (
        feedback_type IN ('like', 'dislike', 'edit', 'report', 'custom')
    )
);

-- ============================================================================
-- Table: subscription_plans
-- Description: Master table for subscription pricing tiers
-- Security: Public read access, admin write only
-- ============================================================================

CREATE TABLE subscription_plans (
    -- Primary key using UUID v4
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Plan identification
    name varchar(50) NOT NULL UNIQUE,
    stripe_price_id varchar(100) NOT NULL UNIQUE,
    
    -- Pricing and limits
    price_jpy int NOT NULL,
    daily_limit int NOT NULL,
    
    -- Feature configuration stored as optimized JSONB
    features jsonb NOT NULL DEFAULT '{}',
    
    -- Status
    is_active boolean DEFAULT true NOT NULL,
    
    -- Audit timestamps
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL,
    
    -- Constraints
    CONSTRAINT subscription_plans_price_positive CHECK (price_jpy >= 0),
    CONSTRAINT subscription_plans_limit_positive CHECK (daily_limit > 0)
);

-- ============================================================================
-- Table: user_subscriptions
-- Description: Active user subscription tracking
-- Security: RLS enabled with user isolation
-- ============================================================================

CREATE TABLE user_subscriptions (
    -- Primary key using UUID v4
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign keys
    user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id uuid NOT NULL REFERENCES subscription_plans(id),
    
    -- Stripe integration
    stripe_subscription_id varchar(100) UNIQUE,
    
    -- Subscription status
    status varchar(20) NOT NULL,
    current_period_start timestamptz NOT NULL,
    current_period_end timestamptz NOT NULL,
    canceled_at timestamptz,
    
    -- Audit timestamps
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL,
    
    -- Constraints
    CONSTRAINT user_subscriptions_status_valid CHECK (
        status IN ('trialing', 'active', 'canceled', 'incomplete', 'incomplete_expired', 'past_due', 'unpaid')
    ),
    CONSTRAINT user_subscriptions_period_valid CHECK (
        current_period_end > current_period_start
    )
    
    -- Note: Unique active subscription constraint implemented as partial index below
);

-- ============================================================================
-- Table: usage_logs
-- Description: API usage tracking with time-series optimization
-- Security: RLS enabled with user isolation
-- Optimization: BRIN index for efficient time-series queries
-- ============================================================================

CREATE TABLE usage_logs (
    -- Primary key using UUID v4
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign key to users
    user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Usage details
    usage_type varchar(50) NOT NULL,
    
    -- Flexible metadata storage with optimized structure
    metadata jsonb NOT NULL DEFAULT '{}',
    
    -- Audit timestamp (clustering key for BRIN)
    created_at timestamptz DEFAULT now() NOT NULL,
    
    -- Constraints
    CONSTRAINT usage_logs_type_valid CHECK (
        usage_type IN ('reply_generation', 'screenshot_ocr', 'persona_analysis', 'api_call')
    )
);

-- ============================================================================
-- Additional Indexes for Initial Tables (from design document)
-- ============================================================================

-- Note: Users table indexes already created in DB-001

-- Cases table additional index
CREATE INDEX idx_cases_updated_at ON cases(updated_at DESC) WHERE deleted_at IS NULL;

-- ============================================================================
-- Indexes for New Tables (PostgreSQL 17 Optimized)
-- ============================================================================

-- Generated replies indexes
CREATE INDEX idx_generated_replies_case_id ON generated_replies(case_id);
CREATE INDEX idx_generated_replies_created_at ON generated_replies(created_at DESC);
CREATE INDEX idx_generated_replies_model ON generated_replies(llm_model);

-- Reply suggestions indexes
CREATE INDEX idx_reply_suggestions_generated_id ON reply_suggestions(generated_reply_id);
CREATE INDEX idx_reply_suggestions_sent ON reply_suggestions(was_sent) WHERE was_sent = true;
CREATE INDEX idx_reply_suggestions_category ON reply_suggestions(category);

-- Covering index for suggestion retrieval (PostgreSQL 17 feature)
CREATE INDEX idx_reply_suggestions_covering ON reply_suggestions(generated_reply_id, category) 
    INCLUDE (suggestion, was_sent, partner_reaction);

-- Feedback logs indexes
CREATE INDEX idx_feedback_logs_suggestion_id ON feedback_logs(reply_suggestion_id);
CREATE INDEX idx_feedback_logs_user_id ON feedback_logs(user_id);
CREATE INDEX idx_feedback_logs_type ON feedback_logs(feedback_type);

-- Subscription plans index
CREATE INDEX idx_subscription_plans_active ON subscription_plans(is_active) WHERE is_active = true;

-- User subscriptions indexes
CREATE INDEX idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX idx_user_subscriptions_status ON user_subscriptions(status) WHERE status IN ('active', 'trialing');
CREATE INDEX idx_user_subscriptions_period ON user_subscriptions(current_period_end);

-- Unique constraint for active subscriptions (one active subscription per user)
CREATE UNIQUE INDEX idx_user_subscriptions_unique_active ON user_subscriptions(user_id) 
    WHERE status IN ('active', 'trialing');

-- Usage logs indexes with BRIN for time-series optimization
CREATE INDEX idx_usage_logs_created_brin ON usage_logs USING brin(created_at);
CREATE INDEX idx_usage_logs_user_created ON usage_logs(user_id, created_at DESC);
CREATE INDEX idx_usage_logs_type_created ON usage_logs(usage_type, created_at DESC);

-- Specialized composite index for daily usage limit checks
CREATE INDEX idx_usage_daily_check ON usage_logs(user_id, usage_type, created_at) 
    WHERE usage_type = 'reply_generation';

-- JSONB GIN index for metadata search (PostgreSQL 17 optimization)
CREATE INDEX idx_usage_logs_metadata_gin ON usage_logs USING gin (metadata jsonb_path_ops);

-- ============================================================================
-- Row Level Security (RLS) Policies
-- ============================================================================

-- Enable RLS on all new tables
ALTER TABLE generated_replies ENABLE ROW LEVEL SECURITY;
ALTER TABLE reply_suggestions ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscription_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;

-- Generated replies RLS policies (inherit from cases)
CREATE POLICY "Users can manage generated replies through cases" ON generated_replies
FOR ALL USING (
    case_id IN (
        SELECT id FROM cases WHERE user_id = auth.uid()::uuid AND deleted_at IS NULL
    )
);

-- Reply suggestions RLS policies (inherit from generated replies)
CREATE POLICY "Users can manage reply suggestions through generated replies" ON reply_suggestions
FOR ALL USING (
    generated_reply_id IN (
        SELECT gr.id FROM generated_replies gr
        JOIN cases c ON c.id = gr.case_id
        WHERE c.user_id = auth.uid()::uuid AND c.deleted_at IS NULL
    )
);

-- Feedback logs RLS policies
CREATE POLICY "Users can create own feedback" ON feedback_logs
FOR INSERT WITH CHECK (user_id = auth.uid()::uuid);

CREATE POLICY "Users can view own feedback" ON feedback_logs
FOR SELECT USING (user_id = auth.uid()::uuid);

-- Subscription plans RLS policies (public read)
CREATE POLICY "Anyone can view active subscription plans" ON subscription_plans
FOR SELECT USING (is_active = true);

-- Service role can manage plans
CREATE POLICY "Service role can manage subscription plans" ON subscription_plans
FOR ALL USING (auth.role() = 'service_role');

-- User subscriptions RLS policies
CREATE POLICY "Users can view own subscriptions" ON user_subscriptions
FOR SELECT USING (user_id = auth.uid()::uuid);

CREATE POLICY "Service role can manage all subscriptions" ON user_subscriptions
FOR ALL USING (auth.role() = 'service_role');

-- Usage logs RLS policies
CREATE POLICY "Users can view own usage logs" ON usage_logs
FOR SELECT USING (user_id = auth.uid()::uuid);

CREATE POLICY "Service role can manage all usage logs" ON usage_logs
FOR ALL USING (auth.role() = 'service_role');

-- ============================================================================
-- Triggers for Automatic Updates
-- ============================================================================

-- Add updated_at triggers for tables with update tracking
CREATE TRIGGER update_subscription_plans_updated_at 
    BEFORE UPDATE ON subscription_plans 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_subscriptions_updated_at 
    BEFORE UPDATE ON user_subscriptions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Helper Functions for Usage Tracking
-- ============================================================================

-- Function: Check daily usage limit
CREATE OR REPLACE FUNCTION check_daily_usage_limit(p_user_id uuid, p_usage_type varchar)
RETURNS TABLE(used_count bigint, daily_limit int, is_allowed boolean) AS $$
BEGIN
    RETURN QUERY
    WITH user_plan AS (
        SELECT sp.daily_limit
        FROM user_subscriptions us
        JOIN subscription_plans sp ON sp.id = us.plan_id
        WHERE us.user_id = p_user_id 
        AND us.status IN ('active', 'trialing')
        ORDER BY us.created_at DESC
        LIMIT 1
    ),
    usage_count AS (
        SELECT COUNT(*) as count
        FROM usage_logs
        WHERE user_id = p_user_id
        AND usage_type = p_usage_type
        AND created_at >= CURRENT_DATE AT TIME ZONE 'Asia/Tokyo'
    )
    SELECT 
        uc.count,
        COALESCE(up.daily_limit, 5) as daily_limit, -- Default free tier limit
        uc.count < COALESCE(up.daily_limit, 5) as is_allowed
    FROM usage_count uc
    CROSS JOIN (SELECT * FROM user_plan) up;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Log API usage with limit check
CREATE OR REPLACE FUNCTION log_api_usage(
    p_user_id uuid, 
    p_usage_type varchar, 
    p_metadata jsonb DEFAULT '{}'
)
RETURNS jsonb AS $$
DECLARE
    v_limit_check record;
    v_usage_id uuid;
BEGIN
    -- Check daily limit
    SELECT * INTO v_limit_check
    FROM check_daily_usage_limit(p_user_id, p_usage_type);
    
    IF NOT v_limit_check.is_allowed THEN
        RETURN jsonb_build_object(
            'success', false,
            'error', 'daily_limit_exceeded',
            'used_count', v_limit_check.used_count,
            'daily_limit', v_limit_check.daily_limit
        );
    END IF;
    
    -- Log usage
    INSERT INTO usage_logs (user_id, usage_type, metadata)
    VALUES (p_user_id, p_usage_type, p_metadata)
    RETURNING id INTO v_usage_id;
    
    RETURN jsonb_build_object(
        'success', true,
        'usage_id', v_usage_id,
        'used_count', v_limit_check.used_count + 1,
        'daily_limit', v_limit_check.daily_limit
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- Table Comments for Documentation
-- ============================================================================

COMMENT ON TABLE generated_replies IS 'Reply generation request history with LLM model tracking';
COMMENT ON TABLE reply_suggestions IS 'Generated reply options with sending status and partner reactions';
COMMENT ON TABLE feedback_logs IS 'User feedback for improving reply generation quality';
COMMENT ON TABLE subscription_plans IS 'Master table for subscription tiers and features';
COMMENT ON TABLE user_subscriptions IS 'Active user subscription tracking with Stripe integration';
COMMENT ON TABLE usage_logs IS 'API usage tracking optimized for time-series queries with BRIN indexes';

-- Column comments for complex fields
COMMENT ON COLUMN generated_replies.prompt_context IS 'JSONB: {conversation_summary, user_goal, persona_traits, recent_messages}';
COMMENT ON COLUMN feedback_logs.details IS 'JSONB: {edited_text, reason, rating, custom_feedback}';
COMMENT ON COLUMN subscription_plans.features IS 'JSONB: {models[], screenshot_ocr, advanced_persona, feedback_loop}';
COMMENT ON COLUMN usage_logs.metadata IS 'JSONB: {model_used, token_count, processing_time, error_code}';

-- ============================================================================
-- Grant Permissions
-- ============================================================================

-- Grant necessary permissions for application users
GRANT SELECT, INSERT ON generated_replies TO authenticated;
GRANT SELECT, UPDATE ON reply_suggestions TO authenticated;
GRANT SELECT, INSERT ON feedback_logs TO authenticated;
GRANT SELECT ON subscription_plans TO authenticated;
GRANT SELECT ON user_subscriptions TO authenticated;
GRANT SELECT ON usage_logs TO authenticated;

-- Grant all permissions to service role
GRANT ALL ON generated_replies TO service_role;
GRANT ALL ON reply_suggestions TO service_role;
GRANT ALL ON feedback_logs TO service_role;
GRANT ALL ON subscription_plans TO service_role;
GRANT ALL ON user_subscriptions TO service_role;
GRANT ALL ON usage_logs TO service_role;

-- Grant function execution permissions
GRANT EXECUTE ON FUNCTION check_daily_usage_limit TO authenticated;
GRANT EXECUTE ON FUNCTION log_api_usage TO authenticated;
GRANT EXECUTE ON FUNCTION check_daily_usage_limit TO service_role;
GRANT EXECUTE ON FUNCTION log_api_usage TO service_role;