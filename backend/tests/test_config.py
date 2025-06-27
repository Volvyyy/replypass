"""
Test cases for configuration settings
"""

from unittest.mock import patch

import pytest

from app.config import Settings, validate_settings


def test_default_settings():
    """Test default configuration values"""
    # Create settings without loading .env file for testing defaults
    settings = Settings(_env_file=None)

    assert settings.environment == "development"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert settings.log_level == "DEBUG"
    assert settings.debug_mode is False
    assert settings.enable_docs is True


def test_allowed_origins_parsing():
    """Test parsing of allowed origins from string"""
    settings = Settings(allowed_origins="http://localhost:3000,http://localhost:3001")

    assert len(settings.allowed_origins) == 2
    assert "http://localhost:3000" in settings.allowed_origins
    assert "http://localhost:3001" in settings.allowed_origins


def test_allowed_file_types_parsing():
    """Test parsing of allowed file types from string"""
    settings = Settings(allowed_file_types="image/jpeg,image/png,image/webp")

    assert len(settings.allowed_file_types) == 3
    assert "image/jpeg" in settings.allowed_file_types
    assert "image/png" in settings.allowed_file_types
    assert "image/webp" in settings.allowed_file_types


def test_validate_settings_missing_fields(capsys):
    """Test validation function with missing required fields"""
    with patch("app.config.settings") as mock_settings:
        # Mock settings with placeholder values
        mock_settings.supabase_url = "placeholder"
        mock_settings.supabase_service_key = "placeholder"
        mock_settings.supabase_jwt_secret = "placeholder"
        mock_settings.gemini_api_key = "placeholder"
        mock_settings.stripe_secret_key = "placeholder"
        mock_settings.jwt_secret_key = "placeholder"
        mock_settings.environment = "development"
        mock_settings.port = 8000
        mock_settings.debug_mode = False
        mock_settings.enable_docs = True

        validate_settings()

        captured = capsys.readouterr()
        assert "以下の環境変数が設定されていません" in captured.out


def test_validate_settings_complete(capsys):
    """Test validation function with complete settings"""
    with patch("app.config.settings") as mock_settings:
        # Mock settings with real values
        mock_settings.supabase_url = "https://example.supabase.co"
        mock_settings.supabase_service_key = "real-service-key"
        mock_settings.supabase_jwt_secret = "real-jwt-secret"
        mock_settings.gemini_api_key = "real-gemini-key"
        mock_settings.stripe_secret_key = "real-stripe-key"
        mock_settings.jwt_secret_key = "real-jwt-key"
        mock_settings.environment = "development"
        mock_settings.port = 8000
        mock_settings.debug_mode = False
        mock_settings.enable_docs = True

        validate_settings()

        captured = capsys.readouterr()
        assert "環境: development" in captured.out
        assert "ポート: 8000" in captured.out
