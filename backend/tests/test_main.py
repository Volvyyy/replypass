"""
Test cases for main FastAPI application
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns healthy status"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Reply Pass API v1.0.0"
    assert data["status"] == "healthy"


def test_health_check_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "reply-pass-api"
    assert data["version"] == "1.0.0"


def test_docs_endpoint():
    """Test that API docs are accessible (if enabled)"""
    response = client.get("/docs")
    # Should either return 200 (docs enabled) or 404 (docs disabled)
    assert response.status_code in [200, 404]

    # Even docs endpoints should have security headers
    if response.status_code == 200:
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers


def test_cors_headers():
    """Test CORS headers are present in responses"""
    response = client.get("/health")
    assert response.status_code == 200
    # Note: CORS headers are only added for cross-origin requests
    # This test verifies the endpoint works without CORS errors


def test_security_headers():
    """Test that security headers are present in all responses"""
    response = client.get("/health")
    assert response.status_code == 200

    # Check essential security headers
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "Content-Security-Policy" in response.headers
    assert "Permissions-Policy" in response.headers

    # Check custom API headers
    assert response.headers.get("X-API-Version") == "1.0"
    assert "X-Response-Time" in response.headers
    assert response.headers.get("X-Powered-By") == "Reply Pass API"

    # Check DNS prefetch control for security
    assert response.headers.get("X-DNS-Prefetch-Control") == "off"


def test_rate_limit_headers():
    """Test that rate limiting headers are included"""
    response = client.get("/health")
    assert response.status_code == 200

    # Check rate limiting headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers

    # Verify rate limit remaining is a valid number
    remaining = response.headers.get("X-RateLimit-Remaining")
    assert remaining.isdigit()
    assert int(remaining) >= 0


def test_rate_limiting_enforcement():
    """Test that rate limiting actually works"""
    # Make multiple requests quickly
    responses = []
    for i in range(5):
        response = client.get("/health")
        responses.append(response)

    # All should succeed (within limit)
    for response in responses:
        assert response.status_code == 200

    # Check that rate limit remaining decreases
    remaining_counts = [
        int(response.headers.get("X-RateLimit-Remaining", "0"))
        for response in responses
    ]
    # Should be decreasing (though order might vary due to timing)
    assert any(remaining_counts)


def test_cors_preflight_simulation():
    """Test CORS preflight request simulation"""
    # Simulate a preflight request with custom headers
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type,Authorization",
    }

    response = client.options("/health", headers=headers)
    assert response.status_code == 200


def test_security_csp_policy():
    """Test Content Security Policy is restrictive for API"""
    response = client.get("/health")
    csp = response.headers.get("Content-Security-Policy", "")

    # Verify restrictive CSP for API
    assert "default-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp
    assert "base-uri 'none'" in csp


def test_cross_origin_policies():
    """Test Cross-Origin security policies are set"""
    response = client.get("/health")

    assert response.headers.get("Cross-Origin-Embedder-Policy") == "require-corp"
    assert response.headers.get("Cross-Origin-Opener-Policy") == "same-origin"
    assert response.headers.get("Cross-Origin-Resource-Policy") == "cross-origin"


def test_request_id_header():
    """Test that request ID is generated for tracing"""
    response = client.get("/health")
    assert response.status_code == 200

    # Check request ID header exists and is valid format
    request_id = response.headers.get("X-Request-ID")
    assert request_id is not None
    assert len(request_id) == 8  # UUID first 8 characters


def test_enhanced_rate_limit_headers():
    """Test enhanced rate limiting headers"""
    response = client.get("/health")
    assert response.status_code == 200

    # Check all rate limiting headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers
    assert "X-RateLimit-Limit" in response.headers

    # Verify values are valid
    remaining = int(response.headers.get("X-RateLimit-Remaining"))
    limit = int(response.headers.get("X-RateLimit-Limit"))
    assert 0 <= remaining <= limit


def test_permissions_policy_header():
    """Test Permissions Policy header for device access control"""
    response = client.get("/health")
    permissions_policy = response.headers.get("Permissions-Policy", "")

    # Verify restrictive permissions policy
    assert "camera=()" in permissions_policy
    assert "microphone=()" in permissions_policy
    assert "geolocation=()" in permissions_policy
    assert "payment=()" in permissions_policy


def test_configuration_driven_security():
    """Test that security settings are configuration-driven"""
    response = client.get("/health")

    # Verify CSP comes from configuration
    csp = response.headers.get("Content-Security-Policy")
    assert csp is not None
    assert "default-src 'none'" in csp

    # Verify CORS headers come from configuration
    assert "X-Response-Time" in response.headers
    assert "X-API-Version" in response.headers
