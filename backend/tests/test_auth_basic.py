"""
Basic tests for Authentication API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app


def test_user_registration_password_validation():
    """Test password validation during registration"""
    client = TestClient(app)
    weak_password_data = {
        "email": "test@example.com",
        "password": "weak",
        "confirm_password": "weak",
        "profile": {
            "display_name": "Test User"
        }
    }
    
    response = client.post("/api/auth/register", json=weak_password_data)
    assert response.status_code == 422
    detail = str(response.json()["detail"])
    assert "password" in detail.lower()


def test_user_registration_password_mismatch():
    """Test registration fails when passwords don't match"""
    client = TestClient(app)
    mismatch_data = {
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "confirm_password": "DifferentPassword123!",
        "profile": {
            "display_name": "Test User"
        }
    }
    
    response = client.post("/api/auth/register", json=mismatch_data)
    assert response.status_code == 422
    detail = str(response.json()["detail"])
    assert "password" in detail.lower()


def test_user_registration_invalid_email():
    """Test registration fails with invalid email"""
    client = TestClient(app)
    invalid_email_data = {
        "email": "invalid-email",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
        "profile": {
            "display_name": "Test User"
        }
    }
    
    response = client.post("/api/auth/register", json=invalid_email_data)
    assert response.status_code == 422
    detail = str(response.json()["detail"])
    assert "email" in detail.lower()


@patch('app.api.auth.get_supabase_client')
def test_user_registration_success(mock_supabase):
    """Test successful user registration"""
    client = TestClient(app)
    mock_client = MagicMock()
    mock_supabase.return_value = mock_client
    
    mock_client.auth.sign_up.return_value = MagicMock(
        user=MagicMock(
            id="user-123",
            email="test@example.com",
            email_confirmed_at=None,
            created_at="2025-06-27T12:00:00Z"
        ),
        session=None
    )
    
    mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(
        data=[{
            "id": "profile-123",
            "auth_id": "user-123",
            "email": "test@example.com",
            "profile": {"display_name": "Test User", "timezone": "UTC", "language": "ja"}
        }]
    )
    
    registration_data = {
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
        "profile": {
            "display_name": "Test User"
        }
    }
    
    response = client.post("/api/auth/register", json=registration_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert "user" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["confirmation_required"] is True


def test_auth_profile_endpoint_requires_authentication():
    """Test that profile endpoint requires authentication"""
    client = TestClient(app)
    response = client.get("/api/auth/profile")
    assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])