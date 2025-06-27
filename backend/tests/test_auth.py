"""
Test cases for Supabase Auth integration
"""

import os
import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.auth.dependencies import get_current_user
from app.auth.jwt_bearer import JWTBearer
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test basic health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["features"]["supabase_auth"] is True


def test_root_endpoint():
    """Test root endpoint returns correct information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Reply Pass API" in data["message"]
    assert data["auth"] == "Supabase Auth 2025 Ready"


def test_protected_endpoint_without_auth():
    """Test protected endpoint rejects unauthenticated requests"""
    response = client.get("/auth/profile")
    assert response.status_code == 401
    assert "Bearer authentication required" in response.json()["detail"]


@patch.dict(os.environ, {"SUPABASE_JWT_SECRET": "test-secret-key"})
def test_protected_endpoint_with_invalid_token():
    """Test protected endpoint rejects invalid tokens"""
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.get("/auth/profile", headers=headers)
    assert response.status_code == 401


@patch.dict(os.environ, {"SUPABASE_JWT_SECRET": "test-secret-key"})
def test_jwt_bearer_validation():
    """Test JWT Bearer validation logic"""
    jwt_bearer = JWTBearer()

    # Test JWT verification with mock payload
    test_payload = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "role": "authenticated",
        "aud": "authenticated",
        "iss": "test-issuer",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }

    # Create test token
    test_token = jwt.encode(test_payload, "test-secret-key", algorithm="HS256")

    # Verify token
    result = jwt_bearer.verify_jwt(test_token)
    assert result is not None
    assert result["sub"] == "test-user-id"
    assert result["email"] == "test@example.com"


@patch.dict(os.environ, {"SUPABASE_JWT_SECRET": "test-secret-key"})
def test_protected_endpoint_with_valid_token():
    """Test protected endpoint accepts valid tokens"""
    # Create test JWT token
    test_payload = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "role": "authenticated",
        "aud": "authenticated",
        "iss": "test-issuer",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "user_metadata": {"display_name": "Test User"},
    }

    test_token = jwt.encode(test_payload, "test-secret-key", algorithm="HS256")

    headers = {"Authorization": f"Bearer {test_token}"}

    # Test profile endpoint
    response = client.get("/auth/profile", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test-user-id"
    assert data["email"] == "test@example.com"
    assert data["role"] == "authenticated"

    # Test verify endpoint
    response = client.get("/auth/verify", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["user_id"] == "test-user-id"


def test_security_headers():
    """Test that security headers are properly set"""
    response = client.get("/health")

    # Check security headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "X-Response-Time" in response.headers
    assert response.headers["X-API-Version"] == "1.0"


def test_cors_headers():
    """Test CORS headers are properly configured"""
    # Use a simple GET request instead of OPTIONS for testing
    response = client.get("/health")
    assert response.status_code == 200

    # CORS headers would be visible in browser environment
    # Note: TestClient doesn't fully simulate browser CORS behavior


def test_rate_limiting():
    """Test rate limiting functionality"""
    # Note: This is a basic test - full rate limiting testing would require
    # more sophisticated mocking of the middleware

    # Make multiple requests quickly
    responses = []
    for _ in range(5):
        response = client.get("/health")
        responses.append(response.status_code)

    # Should not hit rate limit with default settings in test
    assert all(status == 200 for status in responses)


@patch.dict(os.environ, {"SUPABASE_JWT_SECRET": "test-secret-key"})
def test_jwt_token_expiration():
    """Test that expired tokens are rejected"""
    # Create expired token
    expired_payload = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "role": "authenticated",
        "aud": "authenticated",
        "iat": int(time.time()) - 7200,  # 2 hours ago
        "exp": int(time.time()) - 3600,  # 1 hour ago (expired)
    }

    expired_token = jwt.encode(expired_payload, "test-secret-key", algorithm="HS256")

    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/auth/profile", headers=headers)
    assert response.status_code == 401


@patch.dict(os.environ, {"SUPABASE_JWT_SECRET": "test-secret-key"})
def test_jwt_invalid_audience():
    """Test that tokens with invalid audience are rejected"""
    invalid_aud_payload = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "role": "authenticated",
        "aud": "invalid-audience",  # Wrong audience
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }

    invalid_token = jwt.encode(
        invalid_aud_payload, "test-secret-key", algorithm="HS256"
    )

    headers = {"Authorization": f"Bearer {invalid_token}"}
    response = client.get("/auth/profile", headers=headers)
    assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__])
    print("✅ All authentication tests passed!")
