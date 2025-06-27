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
-- Development Verification
-- ============================================================================

-- Verify seed data was inserted correctly
DO $$
DECLARE
    user_count integer;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;
    RAISE NOTICE 'Seed completed: % users inserted', user_count;
    
    -- Log sample user for verification
    IF user_count > 0 THEN
        RAISE NOTICE 'Sample user: %', (
            SELECT row_to_json(u) FROM (
                SELECT email, profile->>'display_name' as display_name 
                FROM users 
                LIMIT 1
            ) u
        );
    END IF;
END $$;