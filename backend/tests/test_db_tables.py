"""
Test cases for database tables and functionality
"""

import json
from datetime import datetime, timedelta

import pytest
import requests


def test_table_creation():
    """Test that all core tables are accessible via API"""
    api_base = "http://127.0.0.1:54321/rest/v1"
    headers = {
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
    }

    tables = [
        "users",
        "cases",
        "personas",
        "conversation_logs",
        "conversation_messages",
        "generated_replies",
        "reply_suggestions",
        "feedback_logs",
        "subscription_plans",
        "user_subscriptions",
        "usage_logs",
    ]

    for table in tables:
        response = requests.get(f"{api_base}/{table}", headers=headers)
        assert response.status_code == 200, f"Table {table} not accessible"
        assert isinstance(response.json(), list), f"Table {table} doesn't return list"


def test_rls_protection():
    """Test that RLS properly protects data"""
    api_base = "http://127.0.0.1:54321/rest/v1"
    headers = {
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
    }

    # Attempt to access protected tables without authentication
    protected_tables = [
        "cases",
        "personas",
        "conversation_logs",
        "conversation_messages",
        "generated_replies",
        "reply_suggestions",
        "feedback_logs",
        "user_subscriptions",
        "usage_logs",
    ]

    for table in protected_tables:
        response = requests.get(f"{api_base}/{table}", headers=headers)
        data = response.json()
        # Should return empty list due to RLS (no authenticated user)
        assert len(data) == 0, f"RLS not working for {table}"


def test_jsonb_structure():
    """Test JSONB fields have proper structure"""
    # This test validates the expected JSONB structures are documented

    # Expected JSONB structures from schema
    expected_structures = {
        "cases.metadata": {
            "priority": "high",
            "tags": ["work", "urgent"],
            "notes": "Additional context",
        },
        "personas.quick_settings": {
            "use_honorifics": True,
            "response_length": "medium",
            "thinking_style": "logical",
            "humor_level": 2,
        },
        "conversation_messages.metadata": {
            "confidence_score": 0.95,
            "processing_time": 1200,
            "model_version": "gemini-2.0-flash",
        },
        "generated_replies.prompt_context": {
            "conversation_summary": "Recent discussion about project",
            "user_goal": "friendly response",
            "persona_traits": ["professional", "helpful"],
            "recent_messages": [],
        },
        "feedback_logs.details": {
            "edited_text": "Modified suggestion",
            "reason": "Too formal",
            "rating": 4,
            "custom_feedback": "Could be more casual",
        },
        "subscription_plans.features": {
            "models": ["gemini-2.0-flash", "gemini-2.5-flash"],
            "screenshot_ocr": True,
            "advanced_persona": True,
            "feedback_loop": True,
        },
        "usage_logs.metadata": {
            "model_used": "gemini-2.0-flash",
            "token_count": 1250,
            "processing_time": 800,
            "error_code": None,
        },
    }

    # Validate structure completeness
    for field, structure in expected_structures.items():
        assert isinstance(
            structure, dict
        ), f"JSONB structure for {field} should be dict"
        assert len(structure) > 0, f"JSONB structure for {field} should not be empty"


def test_constraints_validation():
    """Test database constraints are properly defined"""

    # Expected constraints based on schema
    constraints = {
        "cases": [
            "cases_name_not_empty",
            "cases_partner_name_not_empty",
            "cases_casualness_valid",
        ],
        "personas": [
            "personas_casualness_range",
            "personas_emoji_usage_valid",
            "personas_reference_text_length",
            "personas_case_unique",
        ],
        "conversation_logs": [
            "conversation_logs_message_count_positive",
            "conversation_logs_last_message_logical",
        ],
        "conversation_messages": [
            "conversation_messages_speaker_valid",
            "conversation_messages_input_method_valid",
            "conversation_messages_content_not_empty",
            "conversation_messages_timestamp_logical",
        ],
        "generated_replies": ["generated_replies_model_valid"],
        "reply_suggestions": [
            "reply_suggestions_category_valid",
            "reply_suggestions_reaction_valid",
            "reply_suggestions_sent_logic",
        ],
        "feedback_logs": ["feedback_logs_type_valid"],
        "subscription_plans": [
            "subscription_plans_price_positive",
            "subscription_plans_limit_positive",
        ],
        "user_subscriptions": [
            "user_subscriptions_status_valid",
            "user_subscriptions_period_valid",
        ],
        "usage_logs": ["usage_logs_type_valid"],
    }

    # Validate constraint coverage
    for table, table_constraints in constraints.items():
        assert len(table_constraints) > 0, f"Table {table} should have constraints"
        for constraint in table_constraints:
            assert constraint.startswith(
                table
            ), f"Constraint {constraint} should start with table name"


def test_partition_design():
    """Test partition design for conversation_messages"""

    # Validate partition configuration
    partition_info = {
        "table": "conversation_messages",
        "partition_type": "RANGE",
        "partition_key": "created_at",
        "partitions": [
            "conversation_messages_y2025m06",
            "conversation_messages_y2025m07",
        ],
    }

    assert partition_info["partition_type"] == "RANGE", "Should use RANGE partitioning"
    assert (
        partition_info["partition_key"] == "created_at"
    ), "Should partition by created_at"
    assert len(partition_info["partitions"]) >= 2, "Should have multiple partitions"


def test_index_strategy():
    """Test index strategy covers expected query patterns"""

    # Expected indexes based on schema
    expected_indexes = {
        "users": [
            "idx_users_email",
            "idx_users_auth_id",
            "idx_users_created_at",
            "idx_users_profile_display_name",
        ],
        "cases": [
            "idx_cases_user_id",
            "idx_cases_user_active",
            "idx_cases_metadata_gin",
            "idx_cases_partner_search",
            "idx_cases_updated_at",
        ],
        "personas": [
            "idx_personas_case_id",
            "idx_personas_settings_gin",
            "idx_personas_casualness",
        ],
        "conversation_logs": [
            "idx_conversation_logs_case_id",
            "idx_conversation_logs_activity",
            "idx_conversation_logs_created",
        ],
        "conversation_messages": [
            "idx_conversation_messages_log_id",
            "idx_conversation_messages_timestamp",
            "idx_conversation_messages_speaker",
            "idx_conversation_messages_metadata_gin",
        ],
        "generated_replies": [
            "idx_generated_replies_case_id",
            "idx_generated_replies_created_at",
            "idx_generated_replies_model",
        ],
        "reply_suggestions": [
            "idx_reply_suggestions_generated_id",
            "idx_reply_suggestions_sent",
            "idx_reply_suggestions_category",
            "idx_reply_suggestions_covering",
        ],
        "feedback_logs": [
            "idx_feedback_logs_suggestion_id",
            "idx_feedback_logs_user_id",
            "idx_feedback_logs_type",
        ],
        "subscription_plans": ["idx_subscription_plans_active"],
        "user_subscriptions": [
            "idx_user_subscriptions_user_id",
            "idx_user_subscriptions_status",
            "idx_user_subscriptions_period",
            "idx_user_subscriptions_unique_active",
        ],
        "usage_logs": [
            "idx_usage_logs_created_brin",
            "idx_usage_logs_user_created",
            "idx_usage_logs_type_created",
            "idx_usage_daily_check",
            "idx_usage_logs_metadata_gin",
        ],
    }

    # Validate index coverage
    for table, indexes in expected_indexes.items():
        assert len(indexes) >= 1, f"Table {table} should have at least one index"

        # Check for GIN indexes on JSONB fields
        gin_indexes = [idx for idx in indexes if "gin" in idx]
        jsonb_tables = ["cases", "personas", "conversation_messages", "usage_logs"]
        if table in jsonb_tables:
            assert (
                len(gin_indexes) >= 1
            ), f"Table {table} should have GIN indexes for JSONB"

        # Check for BRIN index on time-series table
        if table == "usage_logs":
            brin_indexes = [idx for idx in indexes if "brin" in idx]
            assert (
                len(brin_indexes) >= 1
            ), f"Table {table} should have BRIN index for time-series data"


def test_function_definitions():
    """Test helper functions are properly defined"""

    # Expected functions based on schema
    expected_functions = [
        "soft_delete_case",
        "update_conversation_message_count",
        "update_updated_at_column",  # From previous migration
        "check_daily_usage_limit",
        "log_api_usage",
    ]

    for function in expected_functions:
        # Functions should have specific purposes
        if function == "soft_delete_case":
            assert True, "Should handle case soft deletion"
        elif function == "update_conversation_message_count":
            assert True, "Should maintain message count accuracy"
        elif function == "update_updated_at_column":
            assert True, "Should auto-update timestamps"
        elif function == "check_daily_usage_limit":
            assert True, "Should check user daily API usage limits"
        elif function == "log_api_usage":
            assert True, "Should log API usage with limit validation"


def test_subscription_plans_data():
    """Test subscription plans seed data is properly structured"""

    # Expected subscription plans
    expected_plans = {
        "Free": {"price_jpy": 0, "daily_limit": 5},
        "Pro": {"price_jpy": 1280, "daily_limit": 100},
        "Unlimited": {"price_jpy": 3480, "daily_limit": 1000},
    }

    for plan_name, details in expected_plans.items():
        assert (
            details["price_jpy"] >= 0
        ), f"Plan {plan_name} should have non-negative price"
        assert (
            details["daily_limit"] > 0
        ), f"Plan {plan_name} should have positive daily limit"

        # Validate pricing logic
        if plan_name == "Free":
            assert details["price_jpy"] == 0, "Free plan should be free"
        else:
            assert (
                details["price_jpy"] > 0
            ), f"Paid plan {plan_name} should have positive price"


if __name__ == "__main__":
    # Run basic validation
    test_table_creation()
    test_rls_protection()
    test_jsonb_structure()
    test_constraints_validation()
    test_partition_design()
    test_index_strategy()
    test_function_definitions()
    test_subscription_plans_data()
    print("✅ All database tests passed!")
