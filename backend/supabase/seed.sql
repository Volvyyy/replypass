-- ============================================================================
-- Reply Pass Development Seed Data
-- Description: Sample data for local development and testing
-- Author: Claude Code (2025-06-27)
-- Note: This data is only for development - never use in production
-- ============================================================================

-- Development test users
-- Note: These auth_ids should correspond to test users in Supabase Auth

-- Test User 1: Regular user with basic profile
INSERT INTO users (
    id,
    email,
    auth_id,
    profile
) VALUES (
    '01010101-0101-0101-0101-010101010101',
    'test1@example.com',
    'test-auth-id-001',
    '{
        "display_name": "テストユーザー1",
        "timezone": "Asia/Tokyo",
        "locale": "ja"
    }'::jsonb
) ON CONFLICT (auth_id) DO NOTHING;

-- Test User 2: User with full profile
INSERT INTO users (
    id,
    email,
    auth_id,
    profile
) VALUES (
    '02020202-0202-0202-0202-020202020202',
    'test2@example.com',
    'test-auth-id-002',
    '{
        "display_name": "田中太郎",
        "avatar_url": "https://example.com/avatar2.jpg",
        "timezone": "Asia/Tokyo",
        "locale": "ja"
    }'::jsonb
) ON CONFLICT (auth_id) DO NOTHING;

-- Test User 3: English user
INSERT INTO users (
    id,
    email,
    auth_id,
    profile
) VALUES (
    '03030303-0303-0303-0303-030303030303',
    'john.doe@example.com',
    'test-auth-id-003',
    '{
        "display_name": "John Doe",
        "timezone": "America/New_York",
        "locale": "en"
    }'::jsonb
) ON CONFLICT (auth_id) DO NOTHING;

-- ============================================================================
-- Subscription Plans Seed Data
-- ============================================================================

-- Free Plan
INSERT INTO subscription_plans (
    id,
    name,
    stripe_price_id,
    price_jpy,
    daily_limit,
    features,
    is_active
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Free',
    'price_free_placeholder',
    0,
    5,
    '{
        "models": ["gemini-2.0-flash"],
        "screenshot_ocr": false,
        "advanced_persona": false,
        "feedback_loop": false,
        "support_level": "community"
    }'::jsonb,
    true
) ON CONFLICT (name) DO NOTHING;

-- Pro Plan
INSERT INTO subscription_plans (
    id,
    name,
    stripe_price_id,
    price_jpy,
    daily_limit,
    features,
    is_active
) VALUES (
    '00000000-0000-0000-0000-000000000002',
    'Pro',
    'price_pro_monthly_jpy',
    1280,
    100,
    '{
        "models": ["gemini-2.0-flash", "gemini-2.5-flash"],
        "screenshot_ocr": true,
        "advanced_persona": true,
        "feedback_loop": true,
        "support_level": "email",
        "priority_generation": false
    }'::jsonb,
    true
) ON CONFLICT (name) DO NOTHING;

-- Unlimited Plan
INSERT INTO subscription_plans (
    id,
    name,
    stripe_price_id,
    price_jpy,
    daily_limit,
    features,
    is_active
) VALUES (
    '00000000-0000-0000-0000-000000000003',
    'Unlimited',
    'price_unlimited_monthly_jpy',
    3480,
    1000,
    '{
        "models": ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"],
        "screenshot_ocr": true,
        "advanced_persona": true,
        "feedback_loop": true,
        "support_level": "priority",
        "priority_generation": true,
        "custom_personas": 10,
        "api_access": true
    }'::jsonb,
    true
) ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- Sample User Subscriptions (for testing)
-- ============================================================================

-- Test User 1: Free plan (implicit - no subscription record needed)

-- Test User 2: Pro plan subscription
INSERT INTO user_subscriptions (
    id,
    user_id,
    plan_id,
    stripe_subscription_id,
    status,
    current_period_start,
    current_period_end
) VALUES (
    '10000000-0000-0000-0000-000000000001',
    '02020202-0202-0202-0202-020202020202',
    '00000000-0000-0000-0000-000000000002',
    'sub_test_pro_user2',
    'active',
    CURRENT_DATE,
    CURRENT_DATE + INTERVAL '30 days'
) ON CONFLICT DO NOTHING;

-- Test User 3: Unlimited plan subscription
INSERT INTO user_subscriptions (
    id,
    user_id,
    plan_id,
    stripe_subscription_id,
    status,
    current_period_start,
    current_period_end
) VALUES (
    '10000000-0000-0000-0000-000000000002',
    '03030303-0303-0303-0303-030303030303',
    '00000000-0000-0000-0000-000000000003',
    'sub_test_unlimited_user3',
    'active',
    CURRENT_DATE,
    CURRENT_DATE + INTERVAL '30 days'
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- Sample Cases for Testing
-- ============================================================================

-- Case 1 for Test User 1
INSERT INTO cases (
    id,
    user_id,
    name,
    partner_name,
    partner_type,
    my_position,
    conversation_purpose,
    metadata
) VALUES (
    '20000000-0000-0000-0000-000000000001',
    '01010101-0101-0101-0101-010101010101',
    '上司との進捗報告',
    '山田部長',
    '上司',
    '部下',
    '週次の進捗報告と相談',
    '{
        "casualness_level": 2,
        "priority": "high",
        "tags": ["work", "report"]
    }'::jsonb
) ON CONFLICT DO NOTHING;

-- Case 2 for Test User 2
INSERT INTO cases (
    id,
    user_id,
    name,
    partner_name,
    partner_type,
    my_position,
    conversation_purpose,
    metadata
) VALUES (
    '20000000-0000-0000-0000-000000000002',
    '02020202-0202-0202-0202-020202020202',
    'クライアントとの商談',
    '株式会社ABC 佐藤様',
    'クライアント',
    '営業担当',
    '新規提案の打ち合わせ',
    '{
        "casualness_level": 1,
        "priority": "high",
        "tags": ["sales", "client", "proposal"]
    }'::jsonb
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- Sample Personas
-- ============================================================================

-- Persona for Case 1
INSERT INTO personas (
    id,
    case_id,
    casualness_level,
    emoji_usage,
    reference_texts,
    quick_settings
) VALUES (
    '11111111-1111-1111-1111-111111111111',
    '20000000-0000-0000-0000-000000000001',
    2,
    'minimal',
    'お疲れ様です。進捗報告いたします。
今週は予定通り作業を進めることができました。
来週の予定についてご相談があります。',
    '{
        "use_honorifics": true,
        "response_length": "medium",
        "thinking_style": "structured",
        "humor_level": 1
    }'::jsonb
) ON CONFLICT (case_id) DO NOTHING;

-- Persona for Case 2
INSERT INTO personas (
    id,
    case_id,
    casualness_level,
    emoji_usage,
    reference_texts,
    quick_settings
) VALUES (
    '22222222-2222-2222-2222-222222222222',
    '20000000-0000-0000-0000-000000000002',
    1,
    'none',
    'いつも大変お世話になっております。
先日はお時間をいただき、誠にありがとうございました。
ご提案の件について、社内で検討させていただきました。',
    '{
        "use_honorifics": true,
        "response_length": "long",
        "thinking_style": "logical",
        "humor_level": 0
    }'::jsonb
) ON CONFLICT (case_id) DO NOTHING;

-- ============================================================================
-- Development Verification
-- ============================================================================

-- Verify seed data was inserted correctly
DO $$
DECLARE
    user_count integer;
    plan_count integer;
    case_count integer;
    subscription_count integer;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;
    SELECT COUNT(*) INTO plan_count FROM subscription_plans;
    SELECT COUNT(*) INTO case_count FROM cases;
    SELECT COUNT(*) INTO subscription_count FROM user_subscriptions;
    
    RAISE NOTICE 'Seed completed:';
    RAISE NOTICE '  - % users inserted', user_count;
    RAISE NOTICE '  - % subscription plans inserted', plan_count;
    RAISE NOTICE '  - % cases inserted', case_count;
    RAISE NOTICE '  - % active subscriptions inserted', subscription_count;
    
    -- Log sample data for verification
    IF plan_count > 0 THEN
        RAISE NOTICE 'Subscription plans: %', (
            SELECT string_agg(name || ' (¥' || price_jpy || ')', ', ')
            FROM subscription_plans
            WHERE is_active = true
        );
    END IF;
END $$;