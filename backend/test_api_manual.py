#!/usr/bin/env python3
"""
Manual API test script for authentication endpoints
"""

import json
import requests
import sys

# API base URL
BASE_URL = "http://localhost:8000/api"

def test_password_validation():
    """Test password validation"""
    print("Testing password validation...")
    
    # Test weak password
    weak_data = {
        "email": "test@example.com",
        "password": "weak",
        "confirm_password": "weak",
        "profile": {"display_name": "Test User"}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=weak_data)
        if response.status_code == 422:
            print("✅ Weak password correctly rejected")
            detail = response.json()["detail"]
            if any("password" in str(error).lower() for error in detail):
                print("✅ Password validation error message correct")
            else:
                print("❌ Password validation error message incorrect")
        else:
            print(f"❌ Expected 422, got {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running - start with: uvicorn app.main:app --reload")
        return False
    
    return True

def test_password_mismatch():
    """Test password mismatch validation"""
    print("\nTesting password mismatch...")
    
    mismatch_data = {
        "email": "test@example.com", 
        "password": "SecurePassword123!",
        "confirm_password": "DifferentPassword123!",
        "profile": {"display_name": "Test User"}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=mismatch_data)
        if response.status_code == 422:
            print("✅ Password mismatch correctly rejected")
        else:
            print(f"❌ Expected 422, got {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running")
        return False
    
    return True

def test_invalid_email():
    """Test invalid email validation"""
    print("\nTesting invalid email...")
    
    invalid_email_data = {
        "email": "invalid-email",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
        "profile": {"display_name": "Test User"}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=invalid_email_data)
        if response.status_code == 422:
            print("✅ Invalid email correctly rejected")
        else:
            print(f"❌ Expected 422, got {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running")
        return False
    
    return True

def test_auth_required():
    """Test authentication requirement"""
    print("\nTesting authentication requirement...")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/profile")
        if response.status_code == 401:
            print("✅ Authentication correctly required")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running")
        return False
    
    return True

def main():
    """Run all manual tests"""
    print("Manual API Tests for Authentication Endpoints\n")
    print("Make sure to start the server first:")
    print("cd backend && uvicorn app.main:app --reload\n")
    
    tests = [
        test_password_validation,
        test_password_mismatch, 
        test_invalid_email,
        test_auth_required
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All authentication API tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())