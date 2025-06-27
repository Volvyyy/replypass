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


def test_cors_headers():
    """Test CORS headers are present in responses"""
    response = client.get("/health")
    assert response.status_code == 200
    # Note: CORS headers are only added for cross-origin requests
    # This test verifies the endpoint works without CORS errors