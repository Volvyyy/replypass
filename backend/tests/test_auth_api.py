"""
Test cases for Authentication API endpoints
Tests user registration and authentication workflows
"""

import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app

class TestUserRegistrationAPI:
    """Test user registration API endpoint"""

    def test_user_registration_success(self):
        """Test successful user registration"""
        registration_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "profile": {
                "display_name": "Test User",
                "timezone": "Asia/Tokyo"
            }
        }

        with patch('app.api.auth.get_supabase_client') as mock_supabase:
            # Mock successful Supabase registration
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            mock_client.auth.sign_up.return_value = MagicMock(
                user=MagicMock(
                    id="user-123",
                    email="test@example.com",
                    email_confirmed_at=None
                ),
                session=None  # Email confirmation required
            )
            
            # Mock user profile creation
            mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(
                data=[{
                    "id": "profile-123",
                    "auth_id": "user-123",
                    "email": "test@example.com",
                    "profile": registration_data["profile"]
                }]
            )

            with TestClient(app) as client:
                response = client.post("/api/auth/register", json=registration_data)

            assert response.status_code == 201
            data = response.json()
            assert data["message"] == "Registration successful"
            assert data["user"]["email"] == "test@example.com"
            assert data["user"]["id"] == "user-123"
            assert data["confirmation_required"] is True

    def test_user_registration_password_mismatch(self):
        """Test registration fails when passwords don't match"""
        registration_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "confirm_password": "DifferentPassword123!",
            "profile": {
                "display_name": "Test User"
            }
        }

        response = client.post("/api/auth/register", json=registration_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "password" in data["detail"].lower()

    def test_user_registration_weak_password(self):
        """Test registration fails with weak password"""
        registration_data = {
            "email": "test@example.com",
            "password": "weak",
            "confirm_password": "weak",
            "profile": {
                "display_name": "Test User"
            }
        }

        response = client.post("/api/auth/register", json=registration_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "password" in data["detail"].lower()

    def test_user_registration_invalid_email(self):
        """Test registration fails with invalid email"""
        registration_data = {
            "email": "invalid-email",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "profile": {
                "display_name": "Test User"
            }
        }

        response = client.post("/api/auth/register", json=registration_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "email" in str(data["detail"]).lower()

    def test_user_registration_existing_user(self):
        """Test registration fails for existing user"""
        registration_data = {
            "email": "existing@example.com",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "profile": {
                "display_name": "Test User"
            }
        }

        with patch('app.api.auth.get_supabase_client') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Mock Supabase error for existing user
            from supabase import AuthApiError
            mock_client.auth.sign_up.side_effect = AuthApiError("User already registered")

            response = client.post("/api/auth/register", json=registration_data)

            assert response.status_code == 409
            data = response.json()
            assert "already exists" in data["detail"].lower() or "already registered" in data["detail"].lower()

    def test_user_registration_missing_required_fields(self):
        """Test registration fails with missing required fields"""
        incomplete_data = {
            "email": "test@example.com",
            # Missing password and confirm_password
        }

        response = client.post("/api/auth/register", json=incomplete_data)
        
        assert response.status_code == 422  # Validation error

    def test_user_registration_profile_validation(self):
        """Test profile data validation during registration"""
        registration_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "profile": {
                "display_name": "",  # Empty display name should fail
                "timezone": "Invalid/Timezone"
            }
        }

        response = client.post("/api/auth/register", json=registration_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "display_name" in data["detail"].lower() or "profile" in data["detail"].lower()


class TestUserProfileCreation:
    """Test user profile creation in users table"""

    def test_profile_creation_with_defaults(self):
        """Test profile creation with default values"""
        with patch('app.api.auth.get_supabase_client') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Mock profile creation
            mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(
                data=[{
                    "id": "profile-123",
                    "auth_id": "user-123",
                    "email": "test@example.com",
                    "profile": {
                        "display_name": "Test User",
                        "timezone": "UTC",
                        "language": "ja"
                    }
                }]
            )

            registration_data = {
                "email": "test@example.com",
                "password": "SecurePassword123!",
                "confirm_password": "SecurePassword123!",
                "profile": {
                    "display_name": "Test User"
                    # timezone and language should get defaults
                }
            }

            # Mock successful auth
            mock_client.auth.sign_up.return_value = MagicMock(
                user=MagicMock(id="user-123", email="test@example.com"),
                session=None
            )

            response = client.post("/api/auth/register", json=registration_data)

            assert response.status_code == 201
            
            # Verify profile creation was called with defaults
            mock_client.table.assert_called_with("users")
            insert_call = mock_client.table().insert.call_args[0][0]
            assert insert_call["profile"]["timezone"] == "UTC"
            assert insert_call["profile"]["language"] == "ja"

    def test_profile_creation_failure_rollback(self):
        """Test that user auth creation is rolled back if profile creation fails"""
        with patch('app.api.auth.get_supabase_client') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Mock successful auth creation
            mock_client.auth.sign_up.return_value = MagicMock(
                user=MagicMock(id="user-123", email="test@example.com"),
                session=None
            )
            
            # Mock profile creation failure
            mock_client.table.return_value.insert.return_value.execute.side_effect = Exception("Database error")

            registration_data = {
                "email": "test@example.com",
                "password": "SecurePassword123!",
                "confirm_password": "SecurePassword123!",
                "profile": {
                    "display_name": "Test User"
                }
            }

            response = client.post("/api/auth/register", json=registration_data)

            assert response.status_code == 500
            data = response.json()
            assert "registration failed" in data["detail"].lower()


class TestPasswordValidation:
    """Test password validation logic"""

    def test_password_strength_requirements(self):
        """Test password meets strength requirements"""
        test_cases = [
            ("short", False, "too short"),
            ("nouppercase123!", False, "no uppercase"),
            ("NOLOWERCASE123!", False, "no lowercase"),
            ("NoNumbers!", False, "no numbers"),
            ("NoSpecialChar123", False, "no special characters"),
            ("ValidPassword123!", True, "meets all requirements"),
            ("AnotherGood1@", True, "meets all requirements"),
        ]

        for password, should_pass, description in test_cases:
            registration_data = {
                "email": "test@example.com",
                "password": password,
                "confirm_password": password,
                "profile": {
                    "display_name": "Test User"
                }
            }

            response = client.post("/api/auth/register", json=registration_data)
            
            if should_pass:
                # Should not fail due to password validation
                assert response.status_code != 400 or "password" not in response.json().get("detail", "").lower()
            else:
                # Should fail due to password validation
                assert response.status_code == 400
                assert "password" in response.json()["detail"].lower()


class TestEmailConfirmation:
    """Test email confirmation workflow"""

    def test_email_confirmation_endpoint(self):
        """Test email confirmation endpoint"""
        with patch('app.api.auth.get_supabase_client') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Mock successful email confirmation
            mock_client.auth.verify_otp.return_value = MagicMock(
                user=MagicMock(
                    id="user-123",
                    email="test@example.com",
                    email_confirmed_at="2025-06-27T12:00:00Z"
                ),
                session=MagicMock(access_token="jwt-token")
            )

            response = client.post("/api/auth/confirm", json={
                "email": "test@example.com",
                "token": "123456"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Email confirmed successfully"
            assert data["user"]["email"] == "test@example.com"
            assert "access_token" in data

    def test_email_confirmation_invalid_token(self):
        """Test email confirmation with invalid token"""
        with patch('app.api.auth.get_supabase_client') as mock_supabase:
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            # Mock invalid token error
            from supabase import AuthApiError
            mock_client.auth.verify_otp.side_effect = AuthApiError("Invalid token")

            response = client.post("/api/auth/confirm", json={
                "email": "test@example.com",
                "token": "invalid"
            })

            assert response.status_code == 400
            data = response.json()
            assert "invalid" in data["detail"].lower() or "token" in data["detail"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])